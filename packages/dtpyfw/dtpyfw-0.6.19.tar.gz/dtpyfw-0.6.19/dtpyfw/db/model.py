"""Base model classes and utilities for SQLAlchemy ORM models.

Provides ModelBase class with common fields, serialization methods, and
helper functions for tracking model changes.
"""

import json
import uuid
import warnings
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, ClassVar

from sqlalchemy import UUID, Boolean, DateTime, func, inspect, select, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, Mapped, mapped_column

from ..core.jsonable_encoder import jsonable_encoder

__all__ = ("ModelBase", "SoftDeleteMixin", "TimestampMixin", "ConfigurableMixin")

# Type variable for the model class
T = TypeVar('T', bound='ModelBase')


def get_difference_between_dictionaries(
    old_value: Any, new_value: Any, path: str = ""
) -> list[str]:
    """Recursively find paths that differ between two dictionary/list
    structures.

    Compares two data structures (dictionaries or lists) and returns a list of
    paths where differences exist. Useful for tracking changes in nested data.

    Args:
        old_value: The original data structure to compare.
        new_value: The new data structure to compare against.
        path: The current path in the structure (used for recursion).

    Returns:
        A list of string paths indicating where changes occurred.
    """
    changes = []

    if isinstance(old_value, dict) and isinstance(new_value, dict):
        # Recursive case for dictionaries
        keys = set(old_value.keys()) | set(new_value.keys())
        for key in keys:
            if key in old_value and key in new_value:
                changes.extend(
                    get_difference_between_dictionaries(
                        old_value[key], new_value[key], f"{path}.{key}" if path else key
                    )
                )
            elif key in old_value:
                changes.append(f"{path}.{key}")
            else:
                changes.append(f"{path}.{key}")
    elif isinstance(old_value, list) and isinstance(new_value, list):
        # Recursive case for lists
        old_items = {json.dumps(item, sort_keys=True): item for item in old_value}
        new_items = {json.dumps(item, sort_keys=True): item for item in new_value}
        old_set, new_set = set(old_items), set(new_items)

        if (old_set - new_set) or (new_set - old_set):
            changes.append(path)

        for item in old_set & new_set:
            old_item = old_items[item]
            new_item = new_items[item]
            if isinstance(old_item, (list, dict)) and old_item != new_item:
                changes.extend(
                    get_difference_between_dictionaries(
                        old_item, new_item, f"{path}[modified]"
                    )
                )
    else:
        # Base case for other types
        if old_value != new_value:
            changes.append(path)

    return changes


def get_modified_keys(instance: Any) -> list[str]:
    """Return the list of attribute keys that have been modified on the
    instance.

    Uses SQLAlchemy's inspection API to detect which attributes have changed
    since the instance was loaded from the database or last committed.

    Args:
        instance: A SQLAlchemy model instance to inspect.

    Returns:
        A list of attribute key names that have been modified.
    """
    inst_state = inspect(instance)
    modified_attrs = [
        attr.key for attr in inst_state.attrs if attr.history.has_changes()
    ]
    return modified_attrs


class TimestampMixin:
    """Mixin for adding timestamp fields to models."""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SoftDeleteMixin:
    """Mixin for adding soft delete functionality to models."""
    
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    def soft_delete(self, db: Session) -> None:
        """Mark the record as deleted without physically removing it."""
        self.is_deleted = True
        self.deleted_at = datetime.now()
        try:
            db.commit()
            db.refresh(self)
        except SQLAlchemyError as e:
            db.rollback()
            raise
    
    def restore(self, db: Session) -> None:
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        try:
            db.commit()
            db.refresh(self)
        except SQLAlchemyError as e:
            db.rollback()
            raise


class ConfigurableMixin:
    """Mixin for adding configurable settings functionality to models.
    
    This mixin provides functionality for models that need dynamic configuration
    through a settings field. The settings column is automatically provided as
    a JSONB column for PostgreSQL databases and JSON for other databases.
    
    Example usage:
        from dtpyfw.db.model import ModelBase, ConfigurableMixin
        from sqlalchemy.orm import Mapped, mapped_column
        from sqlalchemy import String
        
        class User(ConfigurableMixin, ModelBase):
            __tablename__ = 'users'
            
            name: Mapped[str] = mapped_column(String(100), nullable=False)
            # settings column is automatically provided by ConfigurableMixin as JSONB
            
            # Configure settings behavior
            valid_settings = ['theme', 'notifications', 'language']
            combined_settings = True
    
    Class Attributes:
        settings: JSONB (PostgreSQL) or JSON column for storing settings data (automatically provided)
        combined_settings: If True, merges settings into the main dict during serialization
        need_jsonable_encoder: If True, uses jsonable_encoder for data processing
        valid_settings: List of valid setting keys allowed for this model
    """
    
    # Class attributes for configuration
    settings: Mapped[Optional[dict]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"), 
        nullable=True, 
        default=None
    )
    combined_settings: ClassVar[bool] = True
    need_jsonable_encoder: ClassVar[bool] = True
    valid_settings: ClassVar[List[str]] = []

    def to_dict(
        self, excludes: Optional[set[str]] = None, includes: Optional[set[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Serialize the model instance to a dictionary with settings support.

        Converts the model instance to a dictionary representation, optionally
        merging settings fields and applying inclusion/exclusion filters.

        Args:
            excludes: Set of field names to exclude from the result.
            includes: Set of field names to include in the result (if specified,
                only these fields will be included).

        Returns:
            Dictionary representation of the model, or None if instance is None.
        """
        if self is None:
            return

        excludes = excludes or set()
        includes = includes or set()

        model = dict(self.__dict__.items())

        if settings := model.get("settings"):
            if self.combined_settings:
                model = {**settings, **model}
            else:
                model["settings"] = [
                    {"key": key, "value": value} for key, value in settings.items()
                ]

        if self.combined_settings and "settings" in model:
            model.pop("settings", None)

        model = {
            k: v
            for k, v in model.items()
            if not k.startswith("_")
            and k not in excludes
            and (not includes or k in includes)
        }
        return model

    @classmethod
    def create(cls, db: Session, data: Union[Dict[str, Any], Any]):
        """Create a new model instance with settings support.

        Processes the provided data, separating regular fields from settings,
        and creates a new database record with proper error handling.

        Args:
            db: SQLAlchemy session for database operations.
            data: Dictionary or model containing the data for the new instance.

        Returns:
            The newly created and persisted model instance.

        Raises:
            IntegrityError: If there are constraint violations.
            SQLAlchemyError: If database operation fails.
        """
        try:
            data = jsonable_encoder(data) if cls.need_jsonable_encoder else data
            model_fields: Dict[str, Any] = {}

            if cls.combined_settings:
                requested_settings: Dict[str, Any] = {}
            else:
                requested_settings = {
                    item["key"]: item["value"]
                    for item in (data.get("settings", []) or [])
                    if item["key"] in cls.valid_settings
                }

            for k, v in data.items():
                if hasattr(cls, 'get_fields') and k in getattr(cls, 'get_fields', lambda: [])():
                    model_fields[k] = v
                elif cls.valid_settings and k in cls.valid_settings:
                    requested_settings[k] = v

            if cls.valid_settings and requested_settings:
                model_fields["settings"] = requested_settings

            new_model = cls(**model_fields)
            db.add(new_model)
            db.commit()
            db.refresh(new_model)
            return new_model
        except (IntegrityError, SQLAlchemyError):
            db.rollback()
            raise

    def update(self, db: Session, data: Union[Dict[str, Any], Any]):
        """Update the model instance with settings support.

        Processes the provided data, updates the instance attributes,
        tracks changes including settings modifications, and commits
        the changes to the database with proper error handling.

        Args:
            db: SQLAlchemy session for database operations.
            data: Dictionary or model containing the updated data.

        Returns:
            The updated model instance after refresh from database.

        Raises:
            IntegrityError: If there are constraint violations.
            SQLAlchemyError: If database operation fails.
        """
        try:
            data = jsonable_encoder(data) if self.need_jsonable_encoder else data

            current_settings: Dict[str, Any] = getattr(self, 'settings', None) or {}
            if self.combined_settings:
                requested_settings: Dict[str, Any] = {}
            else:
                requested_settings = {
                    item["key"]: item["value"]
                    for item in (data.get("settings", []) or [])
                    if item["key"] in self.valid_settings
                }

            for k, v in data.items():
                if hasattr(self, 'get_fields') and k in getattr(self, 'get_fields', lambda: [])():
                    setattr(self, k, v)
                elif (
                    self.combined_settings
                    and self.valid_settings
                    and k in self.valid_settings
                ):
                    requested_settings[k] = v

            if self.valid_settings and requested_settings:
                setattr(self, 'settings', (
                    {**current_settings, **requested_settings}
                    if getattr(self, 'settings', None)
                    else requested_settings
                ))

            changes = get_modified_keys(self)

            if current_settings or requested_settings:
                if "settings" in changes:
                    changes.remove("settings")

                changes.extend(
                    get_difference_between_dictionaries(
                        old_value={
                            k: v
                            for k, v in (current_settings or {}).items()
                            if k in requested_settings
                        },
                        new_value=requested_settings,
                    )
                )

            db.commit()
            db.refresh(self)
            return self
        except (IntegrityError, SQLAlchemyError):
            db.rollback()
            raise

class ModelBase(TimestampMixin):
    """Enhanced base class for SQLAlchemy models with common fields and utilities.

    Provides standard fields (id, created_at, updated_at), serialization methods,
    query utilities, and helpers for creating/updating model instances with support 
    for settings fields and change tracking. The DatabaseBase parent should be added
    when creating models that need to inherit from a specific database instance.
    
    Example usage:
        from dtpyfw.db.model import ModelBase, SoftDeleteMixin
        from dtpyfw.db.database import DatabaseInstance
        from sqlalchemy.orm import Mapped, mapped_column
        from sqlalchemy import String
        
        # Create database instance and get its base class
        db_instance = DatabaseInstance(config)
        
        class User(ModelBase, db_instance.base):
            __tablename__ = 'users'
            
            name: Mapped[str] = mapped_column(String(100), nullable=False)
            email: Mapped[str] = mapped_column(String(200), nullable=False)
        
        class Post(ModelBase, SoftDeleteMixin, db_instance.base):
            __tablename__ = 'posts'
            
            title: Mapped[str] = mapped_column(String(200), nullable=False)

    Attributes:
        id: UUID primary key column.
        created_at: Timestamp when the record was created.
        updated_at: Timestamp when the record was last updated.
        need_jsonable_encoder: If True, uses jsonable_encoder for data processing.
    """

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Class attributes for configuration  
    need_jsonable_encoder: ClassVar[bool] = True

    @classmethod
    def get_fields(cls) -> List[str]:
        """Return a list of column names excluding 'settings'.

        Returns:
            List of column names defined on the model's table, excluding 'settings'.
        """
        fields = list(cls.__table__.columns.keys())  # type: ignore
        if "settings" in fields:
            fields.remove("settings")
        return fields

    @classmethod
    def get_by_id(cls: Type[T], db: Session, id: Union[str, uuid.UUID]) -> Optional[T]:
        """Get a model instance by its ID.

        Args:
            db: SQLAlchemy session for database operations.
            id: The UUID or string ID to search for.

        Returns:
            The model instance if found, None otherwise.
        """
        try:
            if isinstance(id, str):
                id = uuid.UUID(id)
            stmt = select(cls).where(cls.id == id)
            return db.execute(stmt).scalar_one_or_none()
        except (ValueError, SQLAlchemyError):
            return None

    @classmethod
    def get_all(cls: Type[T], db: Session, limit: Optional[int] = None, offset: int = 0) -> List[T]:
        """Get all instances of the model with optional pagination.

        Args:
            db: SQLAlchemy session for database operations.
            limit: Maximum number of records to return.
            offset: Number of records to skip.

        Returns:
            List of model instances.
        """
        stmt = select(cls)
        if hasattr(cls, 'is_deleted'):
            stmt = stmt.where(cls.is_deleted == False)  # type: ignore
        
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        
        return list(db.execute(stmt).scalars().all())

    @classmethod
    def count(cls: Type[T], db: Session, include_deleted: bool = False) -> int:
        """Count total number of records.

        Args:
            db: SQLAlchemy session for database operations.
            include_deleted: Whether to include soft-deleted records in count.

        Returns:
            Total number of records.
        """
        from sqlalchemy import func as sql_func
        
        stmt = select(sql_func.count(cls.id))
        if hasattr(cls, 'is_deleted') and not include_deleted:
            stmt = stmt.where(cls.is_deleted == False)  # type: ignore
        
        return db.execute(stmt).scalar() or 0

    @classmethod
    def exists(cls: Type[T], db: Session, id: Union[str, uuid.UUID]) -> bool:
        """Check if a record exists by ID.

        Args:
            db: SQLAlchemy session for database operations.
            id: The UUID or string ID to check for.

        Returns:
            True if the record exists, False otherwise.
        """
        try:
            if isinstance(id, str):
                id = uuid.UUID(id)
            stmt = select(select(cls.id).where(cls.id == id).exists())
            return db.execute(stmt).scalar() or False
        except (ValueError, SQLAlchemyError):
            return False

    def delete(self, db: Session, soft: bool = True) -> None:
        """Delete the model instance.

        Args:
            db: SQLAlchemy session for database operations.
            soft: If True and model supports soft delete, perform soft delete.
                  Otherwise, perform hard delete.

        Raises:
            SQLAlchemyError: If database operation fails.
        """
        try:
            if soft and hasattr(self, 'soft_delete') and callable(getattr(self, 'soft_delete')):
                getattr(self, 'soft_delete')(db)
            else:
                db.delete(self)
                db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise

    def to_dict(
        self, excludes: Optional[set[str]] = None, includes: Optional[set[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Serialize the model instance to a dictionary with optional field filtering.

        Converts the model instance to a dictionary representation and applies 
        inclusion/exclusion filters.

        Args:
            excludes: Set of field names to exclude from the result.
            includes: Set of field names to include in the result (if specified,
                only these fields will be included).

        Returns:
            Dictionary representation of the model, or None if instance is None.
        """
        if self is None:
            return

        excludes = excludes or set()
        includes = includes or set()

        model = dict(self.__dict__.items())

        model = {
            k: v
            for k, v in model.items()
            if not k.startswith("_")
            and k not in excludes
            and (not includes or k in includes)
        }
        return model

    def get(
        self, excludes: Optional[set[str]] = None, includes: Optional[set[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Alias for to_dict method for backward compatibility.

        .. deprecated:: 
            The get() method is deprecated and will be removed in a future version.
            Use to_dict() instead for the same functionality.

        Args:
            excludes: Set of field names to exclude from the result.
            includes: Set of field names to include in the result.

        Returns:
            Dictionary representation of the model, or None if instance is None.
        """
        warnings.warn(
            "The get() method is deprecated and will be removed in a future version. "
            "Use to_dict() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.to_dict(excludes=excludes, includes=includes)

    def __repr__(self) -> str:
        """Return a string representation of the model instance."""
        return f"<{self.__class__.__name__}(id={self.id})>"

    def __str__(self) -> str:
        """Return a human-readable string representation of the model."""
        return f"{self.__class__.__name__} {self.id}"

    @classmethod
    def bulk_create(cls: Type[T], db: Session, data_list: List[Dict[str, Any]]) -> List[T]:
        """Create multiple model instances in a single transaction.

        Args:
            db: SQLAlchemy session for database operations.
            data_list: List of dictionaries containing data for new instances.

        Returns:
            List of newly created model instances.

        Raises:
            IntegrityError: If there are constraint violations.
            SQLAlchemyError: If database operation fails.
        """
        try:
            instances = []
            for data in data_list:
                processed_data = jsonable_encoder(data) if cls.need_jsonable_encoder else data
                model_fields: Dict[str, Any] = {}
                
                for k, v in processed_data.items():
                    if k in cls.get_fields():
                        model_fields[k] = v
                
                instance = cls(**model_fields)
                instances.append(instance)
                db.add(instance)
            
            db.commit()
            
            # Refresh all instances
            for instance in instances:
                db.refresh(instance)
            
            return instances
        except (IntegrityError, SQLAlchemyError):
            db.rollback()
            raise

    @classmethod
    def get_or_create(
        cls: Type[T], 
        db: Session, 
        defaults: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> tuple[T, bool]:
        """Get an existing instance or create a new one if it doesn't exist.

        Args:
            db: SQLAlchemy session for database operations.
            defaults: Default values to use when creating a new instance.
            **kwargs: Filter criteria to find existing instance.

        Returns:
            Tuple of (instance, created) where created is True if a new instance was created.

        Raises:
            IntegrityError: If there are constraint violations.
            SQLAlchemyError: If database operation fails.
        """
        try:
            # Build filter conditions from kwargs
            filters = [getattr(cls, key) == value for key, value in kwargs.items()]
            stmt = select(cls).where(*filters)
            instance = db.execute(stmt).scalar_one_or_none()
            
            if instance:
                return instance, False
            
            create_kwargs = kwargs.copy()
            if defaults:
                create_kwargs.update(defaults)
            
            instance = cls.create(db, create_kwargs)
            return instance, True
        except (IntegrityError, SQLAlchemyError):
            db.rollback()
            raise

    @classmethod
    def create(cls: Type[T], db: Session, data: Union[Dict[str, Any], Any]) -> T:
        """Create a new model instance and persist it to the database.

        Processes the provided data and creates a new database record with 
        proper error handling.

        Args:
            db: SQLAlchemy session for database operations.
            data: Dictionary or model containing the data for the new instance.

        Returns:
            The newly created and persisted model instance.

        Raises:
            IntegrityError: If there are constraint violations.
            SQLAlchemyError: If database operation fails.
        """
        try:
            data = jsonable_encoder(data) if cls.need_jsonable_encoder else data
            model_fields: Dict[str, Any] = {}

            for k, v in data.items():
                if k in cls.get_fields():
                    model_fields[k] = v

            new_model = cls(**model_fields)
            db.add(new_model)
            db.commit()
            db.refresh(new_model)
            return new_model
        except (IntegrityError, SQLAlchemyError):
            db.rollback()
            raise

    def update(self: T, db: Session, data: Union[Dict[str, Any], Any]) -> T:
        """Update the model instance with new data and persist changes.

        Processes the provided data, updates the instance attributes, and commits
        the changes to the database with proper error handling.

        Args:
            db: SQLAlchemy session for database operations.
            data: Dictionary or model containing the updated data.

        Returns:
            The updated model instance after refresh from database.

        Raises:
            IntegrityError: If there are constraint violations.
            SQLAlchemyError: If database operation fails.
        """
        try:
            data = jsonable_encoder(data) if self.need_jsonable_encoder else data

            for k, v in data.items():
                if k in self.get_fields():
                    setattr(self, k, v)

            db.commit()
            db.refresh(self)
            return self
        except (IntegrityError, SQLAlchemyError):
            db.rollback()
            raise
