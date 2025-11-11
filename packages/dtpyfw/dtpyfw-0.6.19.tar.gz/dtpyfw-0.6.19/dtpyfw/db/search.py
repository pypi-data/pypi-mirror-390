"""Advanced database search and filtering utilities.

Provides the get_list function for executing complex search queries with
filtering, pagination, sorting, and metadata generation capabilities.
"""

from enum import Enum
from math import ceil
from typing import Any, Dict, List

from pydantic import BaseModel
from sqlalchemy import distinct as distinct_func
from sqlalchemy import func, select

from .search_context import AvailableFilterType, GetListContext
from .schema import (
    AvailableFilters, GetListResponse, Payload,
    SelectedFilters, RowsListDict, RowsListModelType,
)
from .search_utils.filter_values import get_filters_value
from .search_utils.free_search import free_search
from .search_utils.make_condition import make_condition
from .search_utils.selected_filters import make_selected_filters

__all__ = ("get_list", "GetListContext", "AvailableFilterType")


def get_list(
    ctx: GetListContext,
) -> GetListResponse[Any] | RowsListModelType | RowsListDict | List[BaseModel]:
    """Execute a complex database search with filtering, pagination, sorting, and metadata.

    This function provides a comprehensive search interface for SQLAlchemy models,
    combining multiple query capabilities into a single operation:
    - Dynamic filtering (select, number, date ranges)
    - Free-text search with fuzzy matching
    - Multi-column sorting with null handling
    - Pagination with metadata
    - Join support for related tables
    - Result deduplication
    - Flexible output formats (models, dicts, or full metadata)

    The function builds a query in stages:
    1. Applies joins and static filters
    2. Processes dynamic filters from ctx.current_query
    3. Applies free-text search across ctx.searchable_columns
    4. Deduplicates by ctx.primary_column if ctx.unique=True
    5. Applies sorting and pagination
    6. Generates filter metadata (available and selected options)

    Args:
        ctx: GetListContext dataclass containing all configuration parameters:
            - current_query: Query parameters dictionary with search, pagination, sorting, filters
            - db: Active SQLAlchemy database session
            - model: SQLAlchemy model class to query
            - joins: Optional join configurations
            - static_filters: Optional SQLAlchemy filter expressions that always apply
            - filters: Optional filter definitions
            - searchable_columns: Optional columns for free-text search
            - exact_search: Enable exact phrase matching (default: False)
            - search_tokenizer: Enable tokenization (default: False)
            - search_similarity_threshold: Fuzzy match threshold (default: 0.1)
            - options: Optional eager loading options
            - primary_column: Column for deduplication (default: "id")
            - sorting_null_at_the_end: Null sort behavior (default: True)
            - return_available_filters: Include filter options (default: True)
            - return_selected_filters: Include active filters (default: True)
            - return_rows_data: Include data rows (default: True)
            - return_only_rows_data: Return only rows without metadata (default: False)
            - return_as_dict: Convert to dictionaries (default: True)
            - return_as_dict_parameters: Parameters for to_dict() method
            - response_schema: Optional Pydantic schema for validation
            - row_transformer: Optional transformation callable
            - unique: Enable deduplication (default: True)

    Returns:
        GetListResponse: When ctx.return_only_rows_data=False, returns full response with:
            - payload: Query parameters and pagination metadata
            - available_filters: Filter options (if ctx.return_available_filters=True)
            - selected_filters: Active filters (if ctx.return_selected_filters=True)
            - rows_data: Data rows (if ctx.return_rows_data=True)
        
        RowsListDict: When ctx.return_only_rows_data=True and ctx.return_as_dict=True
        
        RowsListModelType: When ctx.return_only_rows_data=True and ctx.return_as_dict=False
        
        List[BaseModel]: When ctx.return_only_rows_data=True and ctx.response_schema is provided

    Raises:
        AttributeError: If ctx.primary_column doesn't exist on ctx.model
        SQLAlchemyError: If database query execution fails

    Example:
        >>> from sqlalchemy.orm import Session
        >>> from myapp.models import User
        >>> from dtpyfw.db import get_list, GetListContext
        >>> 
        >>> # Create context with all configuration
        >>> ctx = GetListContext(
        ...     current_query={
        ...         "search": "john",
        ...         "page": 1,
        ...         "items_per_page": 20,
        ...         "status": "active",
        ...         "sorting": [{"sort_by": "created_at", "order_by": "desc"}]
        ...     },
        ...     db=session,
        ...     model=User,
        ...     filters=[
        ...         {
        ...             "name": "status",
        ...             "label": "Status",
        ...             "type": "select",
        ...             "columns": [User.status]
        ...         }
        ...     ],
        ...     searchable_columns=[User.name, User.email],
        ... ).add_static_filter(User.deleted_at.is_(None))
        >>> 
        >>> result = get_list(ctx)
        >>> print(f"Total users: {result.payload.total_row}")
        >>> print(f"Page {result.payload.page} of {result.payload.last_page}")
        >>> for user_dict in result.rows_data:
        ...     print(user_dict["name"])
        
        # Example with custom Pydantic schema for type-safe responses:
        >>> from pydantic import BaseModel
        >>> 
        >>> class UserResponseSchema(BaseModel):
        ...     id: int
        ...     name: str
        ...     email: str
        >>> 
        >>> ctx = GetListContext(
        ...     current_query={"page": 1},
        ...     db=session,
        ...     model=User,
        ...     response_schema=UserResponseSchema,
        ...     return_as_dict=True
        ... )
        >>> 
        >>> result = get_list(ctx)
        >>> # result.rows_data is now List[UserResponseSchema] with full type safety
        >>> for user in result.rows_data:
        ...     print(f"{user.name} - {user.email}")  # IDE autocomplete works!
    """
    joins = ctx.joins or []
    filters = ctx.filters or []
    searchable_columns = ctx.searchable_columns or []
    static_filters = ctx.static_filters or []
    options = ctx.options or []
    return_as_dict_parameters = ctx.return_as_dict_parameters or {}

    page = ctx.current_query.get("page") or 1
    items_per_page = ctx.current_query.get("items_per_page") or 30

    orm_primary_column = getattr(ctx.model, ctx.primary_column)

    # Create Initial Model Query
    main_query = select(ctx.model)

    if ctx.unique:
        count_query = select(func.count(distinct_func(orm_primary_column))).select_from(
            ctx.model
        )
    else:
        count_query = select(func.count()).select_from(ctx.model)

    for join_item in joins:
        main_query = main_query.join(**join_item)
        count_query = count_query.join(**join_item)

    main_query = main_query.where(*static_filters)
    count_query = count_query.where(*static_filters)

    # Initialize rows and conditions
    conditions = []
    names_conditions: Dict[str, List[Any]] = {
        filter_item["name"]: [] 
        for filter_item in filters 
        if filter_item.get("name") is not None
    }

    for filter_item in filters:
        name = filter_item.get("name")
        columns = filter_item.get("columns")
        if not columns or not name:
            continue
        
        values = ctx.current_query.get(name)
        if not values:
            continue

        target_condition = make_condition(filter_item=filter_item, values=values)
        if target_condition is not None:
            conditions.append(target_condition)
            for inner_name, inner_name_values in names_conditions.items():
                if inner_name != name:
                    inner_name_values.append(target_condition)

    if conditions:
        main_query = main_query.where(*conditions)
        count_query = count_query.where(*conditions)

    if search_query := ctx.current_query.get("search"):
        search_conditions, search_sort = free_search(
            columns=searchable_columns,
            query=search_query,
            threshold=ctx.search_similarity_threshold,
            exact=ctx.exact_search,
            tokenize=ctx.search_tokenizer,
        )
        main_query = main_query.where(*search_conditions)
        count_query = count_query.where(*search_conditions)
    else:
        search_sort = None

    if ctx.unique:
        main_query = main_query.distinct(orm_primary_column)
        main_query.order_by(orm_primary_column)

    dedup_cte = main_query.cte("dedup_cte")

    sorting = ctx.current_query.get("sorting") or []

    order_by_list: List[Any] = []
    if search_sort is not None:
        order_by_list.extend(search_sort)
    elif sorting := (ctx.current_query.get("sorting") or []):
        for item in sorting:
            order_by = item.get("order_by")
            sort_by = item.get("sort_by")

            if sort_by is None or order_by is None:
                continue

            sort_by = sort_by.value if isinstance(sort_by, Enum) else sort_by
            order_by = order_by.value if isinstance(order_by, Enum) else order_by

            sort_by_model = (
                getattr(ctx.model, sort_by) if isinstance(sort_by, str) else sort_by
            )
            order_by_model = (
                getattr(sort_by_model, order_by)
                if isinstance(order_by, str)
                else order_by
            )

            if ctx.sorting_null_at_the_end:
                order_by_list.append(order_by_model().nulls_last())
            else:
                order_by_list.append(order_by_model())

    final_query = select(ctx.model).join(dedup_cte, orm_primary_column == dedup_cte.c.id)

    if options:
        final_query = final_query.options(*options)

    if order_by_list:
        final_query = final_query.order_by(*order_by_list)

    if items_per_page and page:
        final_query = final_query.limit(items_per_page).offset(
            (page - 1) * items_per_page
        )

    count_query = count_query.order_by(None)

    rows: RowsListModelType | RowsListDict | List[BaseModel] | None
    if ctx.return_rows_data:
        db_rows = ctx.db.execute(final_query).unique().scalars().all()
        
        if ctx.response_schema:
            # Use custom Pydantic schema for validation and transformation
            if ctx.return_as_dict:
                # Convert to dict first, then validate with schema
                if ctx.row_transformer:
                    rows = [ctx.response_schema.model_validate(ctx.row_transformer(row.to_dict(**return_as_dict_parameters))) for row in db_rows]
                else:
                    rows = [ctx.response_schema.model_validate(row.to_dict(**return_as_dict_parameters)) for row in db_rows]
            else:
                # Validate model instances directly with schema
                if ctx.row_transformer:
                    rows = [ctx.response_schema.model_validate(ctx.row_transformer(row)) for row in db_rows]
                else:
                    rows = [ctx.response_schema.model_validate(row, from_attributes=True) for row in db_rows]
        elif ctx.return_as_dict:
            if ctx.row_transformer:
                rows = RowsListDict.model_validate([ctx.row_transformer(row.to_dict(**return_as_dict_parameters)) for row in db_rows])
            else:
                rows = RowsListDict.model_validate([row.to_dict(**return_as_dict_parameters) for row in db_rows])
        else:
            if ctx.row_transformer:
                rows = RowsListModelType.model_validate([ctx.row_transformer(row) for row in db_rows])
            else:
                rows = RowsListModelType.model_validate(list(db_rows))
    else:
        rows = None

    if ctx.return_only_rows_data and ctx.return_rows_data and rows is not None:
        return rows
    else:
        count = ctx.db.execute(count_query).scalar_one()
        ctx.current_query["total_row"] = count

        # Calculate pagination-related information
        if items_per_page and page:
            last_page = ceil(count / items_per_page)
            ctx.current_query["last_page"] = last_page
            ctx.current_query["has_next"] = last_page > page
            ctx.current_query["page"] = page
            ctx.current_query["items_per_page"] = items_per_page

        # Ensure sorting exists before validation
        if "sorting" not in ctx.current_query:
            ctx.current_query["sorting"] = []

        payload = Payload.model_validate(ctx.current_query)

        if ctx.return_rows_data and rows is not None:
            rows_data = rows
        else:
            rows_data = None

        available_filters: AvailableFilters | None = None
        if ctx.return_available_filters:
            available_filters: AvailableFilters = (
                get_filters_value(
                    db=ctx.db,
                    pre_conditions=static_filters,
                    joins=joins,
                    filters=filters,
                    names_conditions=names_conditions,
                )
                if filters is not None
                else []
            )

        selected_filters: SelectedFilters | None = None
        if ctx.return_selected_filters:
            selected_filters: SelectedFilters = make_selected_filters(
                current_query=ctx.current_query,
                filters=filters,
            )

        return GetListResponse(
            payload=payload,
            rows_data=rows_data,
            available_filters=available_filters,
            selected_filters=selected_filters,
        )

