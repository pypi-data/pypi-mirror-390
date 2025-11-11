"""Query context configuration for database search operations.

Provides the GetListContext class for configuring complex database search queries
with filtering, pagination, sorting, and metadata generation capabilities.
"""

from enum import Enum
from typing import Any, Callable, Type
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import and_
from sqlalchemy.orm import Session

from .schema import AvailableFilterType, ColumnsLogic

__all__ = ("GetListContext", "AvailableFilterType", "ColumnsLogic")


class GetListContext:
    """Configuration context for get_list database search operations.
    
    This class consolidates all parameters for the get_list function,
    providing a cleaner API with chainable builder methods.
    
    Initialize with essential parameters (current_query, db, model), then use
    builder methods to configure filters, joins, search behavior, and formatting.
    
    Attributes:
        current_query: Query parameters dictionary containing search, pagination, sorting, and filter values.
        db: Active SQLAlchemy database session for executing queries.
        model: SQLAlchemy model class to query (must inherit from DeclarativeBase).
        joins: List of join configurations for related tables (use add_join()).
        static_filters: List of SQLAlchemy filter expressions that always apply (use add_static_filter()).
        filters: List of filter definitions for dynamic filtering (use add_filter()).
        searchable_columns: List of SQLAlchemy column objects to search across (use add_searchable_columns()).
        exact_search: If True, search matches exact phrases. If False, uses fuzzy matching (use set_exact_search()).
        search_tokenizer: If True, enables full-text search tokenization (use set_search_tokenizer()).
        search_similarity_threshold: Minimum similarity score (0.0-1.0) for fuzzy search (use set_search_similarity_threshold()).
        options: List of SQLAlchemy query options for eager loading (use add_option()).
        primary_column: Name of the primary key column used for deduplication (use set_primary_column()).
        sorting_null_at_the_end: If True, null values appear last in sorted results (use set_sorting_null_at_the_end()).
        return_available_filters: If True, includes available filter options in result (use set_return_available_filters()).
        return_selected_filters: If True, includes currently active filters in result (use set_return_selected_filters()).
        return_rows_data: If True, includes the actual data rows in result (use set_return_rows_data()).
        return_only_rows_data: If True, returns only the rows list without metadata wrapper (use set_return_only_rows_data()).
        return_as_dict: If True, converts model instances to dictionaries (use set_return_as_dict()).
        return_as_dict_parameters: Dict of parameters to pass to model's to_dict() method (use set_return_as_dict_parameters()).
        response_schema: Optional Pydantic model class to validate and transform rows (use set_response_schema()).
        row_transformer: Optional callable to transform each row before validation (use set_row_transformer()).
        unique: If True, deduplicates results by primary_column (use set_unique()).
    
    Example:
        >>> from dtpyfw.db.schema import AvailableFilterType, ColumnsLogic
        >>> 
        >>> # Recommended: Chainable builder pattern
        >>> ctx = GetListContext(
        ...     current_query={"page": 1},
        ...     db=session,
        ...     model=User
        ... ).add_filter(
        ...     name="status",
        ...     label="Status",
        ...     filter_type=AvailableFilterType.select,
        ...     columns=[User.status]
        ... ).add_filter(
        ...     name="role",
        ...     label="Role",
        ...     filter_type=AvailableFilterType.select,
        ...     columns=[User.role]
        ... ).add_searchable_columns(User.name, User.email).add_join(
        ...     target=Department,
        ...     onclause=User.department_id == Department.id
        ... )
        >>> 
        >>> result = get_list(ctx)
    """
    
    def __init__(
        self,
        current_query: dict[str, Any],
        db: Session,
        model: Type[Any],
    ) -> None:
        """Initialize GetListContext with essential query configuration.
        
        Use builder methods to configure additional options like filters, joins,
        search behavior, and return formatting.
        
        Args:
            current_query: Query parameters dictionary with search, pagination, sorting, filters
            db: Active SQLAlchemy database session
            model: SQLAlchemy model class to query
        
        Example:
            >>> ctx = GetListContext(
            ...     current_query={"page": 1, "per_page": 20},
            ...     db=session,
            ...     model=User
            ... )
            >>> 
            >>> # Use builder methods to configure
            >>> ctx.add_filter(
            ...     name="status",
            ...     label="Status",
            ...     filter_type=AvailableFilterType.select,
            ...     columns=[User.status]
            ... ).add_searchable_columns(User.name, User.email)
        """
        self.current_query = current_query
        self.db = db
        self.model = model
        
        # Initialize with defaults - use builder methods to customize
        self.joins: list[dict[str, Any]] = []
        self.static_filters: list[Any] = []
        self.filters: list[dict[str, Any]] = []
        self.searchable_columns: list[Any] = []
        self.exact_search: bool = False
        self.search_tokenizer: bool = False
        self.search_similarity_threshold: float = 0.1
        self.options: list[Any] = []
        self.primary_column: str = "id"
        self.sorting_null_at_the_end: bool = True
        self.return_available_filters: bool = True
        self.return_selected_filters: bool = True
        self.return_rows_data: bool = True
        self.return_only_rows_data: bool = False
        self.return_as_dict: bool = True
        self.return_as_dict_parameters: dict[str, Any] = {}
        self.response_schema: Type[BaseModel] | None = None
        self.row_transformer: Callable[[Any], Any] | None = None
        self.unique: bool = True
    
    def add_filter(
        self,
        name: str,
        label: str,
        filter_type: AvailableFilterType,
        columns: list[Any],
        columns_logic: ColumnsLogic = ColumnsLogic.OR,
        case_insensitive: bool = False,
        use_similarity: bool = False,
        similarity_threshold: float = 0.3,
        enum: Type[Enum] | None = None,
        labels: dict[Enum | UUID | str | int | bool, str] | None = None,
        is_json: bool = False,
    ) -> "GetListContext":
        """Add a filter definition to the context.
        
        Args:
            name: Filter identifier used in query parameters
            label: Human-readable filter label
            filter_type: Type of filter (AvailableFilterType enum: SELECT, SELECT_ARRAY, NUMBER, DATE, or SEARCH)
            columns: List of SQLAlchemy column objects to filter on
            columns_logic: Logic for combining multiple columns - ColumnsLogic.OR or ColumnsLogic.AND (default: ColumnsLogic.OR).
            case_insensitive: If True, perform case-insensitive string matching (default: False). 
                Applies to select/select_array filters.
            use_similarity: If True, use PostgreSQL fuzzy similarity matching (default: False).
                Applies to select/select_array filters.
            similarity_threshold: Minimum similarity score 0.0-1.0 for fuzzy matching (default: 0.3).
                Only used when use_similarity=True.
            enum: Optional Enum class for converting filter values to/from enum instances.
                Applies to select/select_array filters.
            labels: Optional dict mapping filter values to custom display labels.
                Keys can be Enum instances, UUID, str, int, or bool. Values are display strings.
                Applies to select/select_array filters.
            is_json: If True, treat column as JSONB array type (default: False).
                Applies to select/select_array filters.
        
        Returns:
            GetListContext: Self for method chaining.
        
        Example:
            >>> from dtpyfw.db.schema import AvailableFilterType, ColumnsLogic
            >>> from enum import Enum
            >>> from uuid import UUID
            >>> 
            >>> class UserStatus(Enum):
            ...     ACTIVE = "active"
            ...     INACTIVE = "inactive"
            >>> 
            >>> # Select filter with enum and custom labels (enum keys)
            >>> ctx.add_filter(
            ...     name="status",
            ...     label="Status",
            ...     filter_type=AvailableFilterType.select,
            ...     columns=[User.status],
            ...     enum=UserStatus,
            ...     labels={UserStatus.ACTIVE: "Active Users", UserStatus.INACTIVE: "Inactive Users"}
            ... )
            >>> 
            >>> # UUID-based filter with custom labels (UUID keys)
            >>> department_id_1 = UUID("123e4567-e89b-12d3-a456-426614174000")
            >>> department_id_2 = UUID("123e4567-e89b-12d3-a456-426614174001")
            >>> ctx.add_filter(
            ...     name="department",
            ...     label="Department",
            ...     filter_type=AvailableFilterType.select,
            ...     columns=[User.department_id],
            ...     labels={department_id_1: "Engineering", department_id_2: "Marketing"}
            ... )
            >>> 
            >>> # String-based labels (string keys)
            >>> ctx.add_filter(
            ...     name="role",
            ...     label="Role",
            ...     filter_type=AvailableFilterType.select,
            ...     columns=[User.role],
            ...     labels={"admin": "Administrator", "user": "Regular User"}
            ... )
            >>> 
            >>> # Integer-based labels (int keys)
            >>> ctx.add_filter(
            ...     name="priority",
            ...     label="Priority Level",
            ...     filter_type=AvailableFilterType.select,
            ...     columns=[Task.priority],
            ...     labels={1: "Low Priority", 2: "Medium Priority", 3: "High Priority"}
            ... )
            >>> 
            >>> # Boolean-based labels (bool keys)
            >>> ctx.add_filter(
            ...     name="active",
            ...     label="Active Status",
            ...     filter_type=AvailableFilterType.select,
            ...     columns=[User.is_active],
            ...     labels={True: "Active", False: "Inactive"}
            ... )
            >>> 
            >>> # Case-insensitive search filter with ColumnsLogic.OR
            >>> ctx.add_filter(
            ...     name="name",
            ...     label="Name",
            ...     filter_type=AvailableFilterType.select,
            ...     columns=[User.first_name, User.last_name],
            ...     columns_logic=ColumnsLogic.OR,
            ...     case_insensitive=True
            ... )
            >>> 
            >>> # Fuzzy similarity search
            >>> ctx.add_filter(
            ...     name="search_similar",
            ...     label="Similar Names",
            ...     filter_type=AvailableFilterType.select,
            ...     columns=[User.name],
            ...     use_similarity=True,
            ...     similarity_threshold=0.5
            ... )
            >>> 
            >>> # Number range filter
            >>> # Note: min/max boundaries are calculated automatically from database data
            >>> # User provides min/max values in current_query, not in filter definition
            >>> ctx.add_filter(
            ...     name="age",
            ...     label="Age Range",
            ...     filter_type=AvailableFilterType.number,
            ...     columns=[User.age]
            ... )
            >>> 
            >>> # Date range filter
            >>> # Note: date boundaries are calculated automatically from database data
            >>> ctx.add_filter(
            ...     name="created",
            ...     label="Creation Date",
            ...     filter_type=AvailableFilterType.date,
            ...     columns=[User.created_at]
            ... )
            >>> 
            >>> # JSONB array filter
            >>> ctx.add_filter(
            ...     name="tags",
            ...     label="Tags",
            ...     filter_type=AvailableFilterType.select_array,
            ...     columns=[User.tags],
            ...     is_json=True
            ... )
        """
        # Convert enums to strings for storage
        filter_type_str = filter_type.value
        columns_logic_str = columns_logic.value
        
        filter_config = {
            "name": name,
            "label": label,
            "type": filter_type_str,
            "columns": columns,
            "columns_logic": columns_logic_str,
            "case_insensitive": case_insensitive,
            "use_similarity": use_similarity,
            "similarity_threshold": similarity_threshold,
        }
        
        # Add optional parameters only if provided
        if enum is not None:
            filter_config["enum"] = enum
        if labels is not None:
            filter_config["labels"] = labels
        if is_json:
            filter_config["is_json"] = is_json
        
        self.filters.append(filter_config)
        return self
    
    def add_join(
        self,
        target: Any,
        onclause: Any,
        isouter: bool = False,
        full: bool = False,
    ) -> "GetListContext":
        """Add a join configuration to the query.
        
        Args:
            target: The target table/model to join (SQLAlchemy Table or mapped class)
            onclause: SQLAlchemy expression defining the join condition (e.g., Table1.id == Table2.foreign_id)
            isouter: If True, performs a LEFT OUTER JOIN (default: False for INNER JOIN)
            full: If True, performs a FULL OUTER JOIN (default: False)
        
        Returns:
            GetListContext: Self for method chaining.
        
        Example:
            >>> # Inner join (default)
            >>> ctx.add_join(
            ...     target=Department,
            ...     onclause=User.department_id == Department.id
            ... )
            >>> 
            >>> # Left outer join
            >>> ctx.add_join(
            ...     target=dealer_group_association,
            ...     onclause=dealer_group_association.c.dealer_id == Dealer.id,
            ...     isouter=True
            ... )
            >>> 
            >>> # Full outer join
            >>> ctx.add_join(
            ...     target=Profile,
            ...     onclause=User.id == Profile.user_id,
            ...     full=True
            ... )
        """
        join_config = {
            "target": target,
            "onclause": onclause,
        }
        
        # Add optional parameters only if they're True
        if isouter:
            join_config["isouter"] = isouter
        if full:
            join_config["full"] = full
        
        self.joins.append(join_config)
        return self
    
    def add_static_filter(self, condition: Any) -> "GetListContext":
        """Add a static filter condition that always applies to the query.
        
        You can call this method multiple times to add more static filters.
        All static filters are combined with AND logic.
        
        Args:
            condition: SQLAlchemy filter expression to always apply
        
        Returns:
            GetListContext: Self for method chaining.
        
        Example:
            >>> # Add single condition
            >>> ctx.add_static_filter(User.deleted_at.is_(None))
            >>> 
            >>> # Chain multiple calls (AND combined)
            >>> ctx.add_static_filter(User.deleted_at.is_(None)).add_static_filter(User.is_active == True)
        """
        self.static_filters.append(condition)
        return self
    
    def add_searchable_columns(self, *columns: Any) -> "GetListContext":
        """Add one or more columns to the list of searchable columns for free-text search.
        
        Args:
            *columns: One or more SQLAlchemy column objects to search across
        
        Returns:
            GetListContext: Self for method chaining.
        
        Example:
            >>> # Add single column
            >>> ctx.add_searchable_columns(User.name)
            >>> 
            >>> # Add multiple columns at once
            >>> ctx.add_searchable_columns(User.name, User.email, User.description)
            >>> 
            >>> # Can still chain multiple calls
            >>> ctx.add_searchable_columns(User.name).add_searchable_columns(User.email)
        """
        self.searchable_columns.extend(columns)
        return self
    
    def add_option(self, option: Any) -> "GetListContext":
        """Add a SQLAlchemy query option (e.g., for eager loading relationships).
        
        Args:
            option: SQLAlchemy query option (e.g., joinedload, selectinload)
        
        Returns:
            GetListContext: Self for method chaining.
        
        Example:
            >>> from sqlalchemy.orm import joinedload
            >>> ctx.add_option(joinedload(User.department))
            >>> ctx.add_option(joinedload(User.roles))
        """
        self.options.append(option)
        return self
    
    def set_exact_search(self, exact_search: bool) -> "GetListContext":
        """Set whether to use exact phrase matching for search.
        
        Args:
            exact_search: If True, search matches exact phrases. If False, uses fuzzy matching.
        
        Returns:
            GetListContext: Self for method chaining.
        """
        self.exact_search = exact_search
        return self
    
    def set_search_tokenizer(self, search_tokenizer: bool) -> "GetListContext":
        """Set whether to enable full-text search tokenization.
        
        Args:
            search_tokenizer: If True, enables tokenization for full-text search.
        
        Returns:
            GetListContext: Self for method chaining.
        """
        self.search_tokenizer = search_tokenizer
        return self
    
    def set_search_similarity_threshold(self, threshold: float) -> "GetListContext":
        """Set the minimum similarity score for fuzzy search.
        
        Args:
            threshold: Minimum similarity score (0.0-1.0) for fuzzy search matches.
        
        Returns:
            GetListContext: Self for method chaining.
        """
        self.search_similarity_threshold = threshold
        return self
    
    def set_primary_column(self, primary_column: str) -> "GetListContext":
        """Set the primary key column name used for deduplication.
        
        Args:
            primary_column: Name of the primary key column (default: "id")
        
        Returns:
            GetListContext: Self for method chaining.
        """
        self.primary_column = primary_column
        return self
    
    def set_sorting_null_at_the_end(self, sorting_null_at_the_end: bool) -> "GetListContext":
        """Set whether null values appear last in sorted results.
        
        Args:
            sorting_null_at_the_end: If True, null values appear last in sorted results.
        
        Returns:
            GetListContext: Self for method chaining.
        """
        self.sorting_null_at_the_end = sorting_null_at_the_end
        return self
    
    def set_return_available_filters(self, return_available_filters: bool) -> "GetListContext":
        """Set whether to include available filter options in result.
        
        Args:
            return_available_filters: If True, includes available filter options.
        
        Returns:
            GetListContext: Self for method chaining.
        """
        self.return_available_filters = return_available_filters
        return self
    
    def set_return_selected_filters(self, return_selected_filters: bool) -> "GetListContext":
        """Set whether to include currently active filters in result.
        
        Args:
            return_selected_filters: If True, includes currently active filters.
        
        Returns:
            GetListContext: Self for method chaining.
        """
        self.return_selected_filters = return_selected_filters
        return self
    
    def set_return_rows_data(self, return_rows_data: bool) -> "GetListContext":
        """Set whether to include the actual data rows in result.
        
        Args:
            return_rows_data: If True, includes the actual data rows.
        
        Returns:
            GetListContext: Self for method chaining.
        """
        self.return_rows_data = return_rows_data
        return self
    
    def set_return_only_rows_data(self, return_only_rows_data: bool) -> "GetListContext":
        """Set whether to return only the rows list without metadata wrapper.
        
        Args:
            return_only_rows_data: If True, returns only rows without metadata.
        
        Returns:
            GetListContext: Self for method chaining.
        """
        self.return_only_rows_data = return_only_rows_data
        return self
    
    def set_return_as_dict(self, return_as_dict: bool) -> "GetListContext":
        """Set whether to convert model instances to dictionaries.
        
        Args:
            return_as_dict: If True, converts model instances to dictionaries.
        
        Returns:
            GetListContext: Self for method chaining.
        """
        self.return_as_dict = return_as_dict
        return self
    
    def set_return_as_dict_parameters(self, parameters: dict[str, Any]) -> "GetListContext":
        """Set parameters to pass to model's to_dict() method.
        
        Args:
            parameters: Dictionary of parameters for to_dict() method.
        
        Returns:
            GetListContext: Self for method chaining.
        """
        self.return_as_dict_parameters = parameters
        return self
    
    def set_response_schema(self, response_schema: Type[BaseModel]) -> "GetListContext":
        """Set Pydantic model class to validate and transform rows.
        
        Args:
            response_schema: Pydantic model class for validation and transformation.
        
        Returns:
            GetListContext: Self for method chaining.
        """
        self.response_schema = response_schema
        return self
    
    def set_row_transformer(self, row_transformer: Callable[[Any], Any]) -> "GetListContext":
        """Set callable to transform each row before validation.
        
        Args:
            row_transformer: Callable that transforms each row.
        
        Returns:
            GetListContext: Self for method chaining.
        """
        self.row_transformer = row_transformer
        return self
    
    def set_unique(self, unique: bool) -> "GetListContext":
        """Set whether to deduplicate results by primary_column.
        
        Args:
            unique: If True, deduplicates results by primary_column.
        
        Returns:
            GetListContext: Self for method chaining.
        """
        self.unique = unique
        return self
