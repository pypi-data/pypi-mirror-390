"""Pydantic schemas for database search and filtering functionality.

Defines data models for search queries, filters, pagination, and results
used in the database search utilities. Supports select, number, date,
and free-text search filter types.
"""

from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Generic, List, Literal, Optional, Union, TypeVar, Dict
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, RootModel


RowsDataType = TypeVar("RowsDataType")


class RowsListModelType(RootModel[List[Any]]):
    """Root model representing a list of SQLAlchemy model instances from search results.
    
    This model wraps a list of SQLAlchemy ORM model instances returned by the
    get_list function when return_as_dict=False. It allows Pydantic validation
    while preserving the original model instances with their methods and relationships.
    
    Note:
        Uses List[Any] instead of List[ModelType] to avoid Pydantic schema generation
        errors with SQLAlchemy's DeclarativeBase at class definition time. The actual
        runtime type is List[ModelType] where ModelType is a SQLAlchemy model.
    
    Example:
        >>> result = get_list(..., return_as_dict=False, return_only_rows_data=True)
        >>> for user in result:  # Iterate over model instances
        ...     print(user.id, user.name)
        ...     user.update_last_login()  # Can call model methods
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)


class RowsListDict(RootModel[List[Dict[str, Any]]]):
    """Root model representing a list of row dictionaries from search results.
    
    This model wraps a list of dictionaries returned by the get_list function when
    return_as_dict=True. Each dictionary represents a database row serialized via
    the model's to_dict() method, containing only JSON-serializable data types.
    
    This format is ideal for API responses, data exports, and situations where
    you need plain data structures without ORM overhead.
    
    Example:
        >>> result = get_list(..., return_as_dict=True, return_only_rows_data=True)
        >>> for user_dict in result:  # Iterate over dictionaries
        ...     print(user_dict["id"], user_dict["name"])
        >>> json.dumps(result.model_dump())  # Easily serialize to JSON
    """


class AvailableFilterType(Enum):
    """Enumeration of available filter types for database searches.
    
    Defines the supported filter types that can be used in the get_list function.
    Each type corresponds to a specific filtering behavior and UI component.
    
    Attributes:
        select: Single-selection filter (e.g., dropdown, radio buttons).
            Filters by exact match on one value.
        select_array: Multi-selection filter (e.g., checkbox list, multi-select).
            Filters by matching any value in the provided list.
        number: Numeric range filter with min/max boundaries.
            Filters by numeric values within the specified range.
        date: Date range filter with start/end dates.
            Filters by datetime values within the specified range.
        search: Free-text search filter (deprecated in favor of searchable_columns).
            Performs text search across specified columns.
    """

    select = "select"
    select_array = "select_array"
    number = "number"
    date = "date"
    search = "search"


class ColumnsLogic(Enum):
    """Enumeration for logical operators when combining multiple filter columns.
    
    Defines how multiple columns in a filter should be combined when building
    WHERE conditions. Used in add_filter() to specify the relationship between
    columns when filtering across multiple database columns.
    
    Attributes:
        OR: Combine conditions with OR - matches if ANY column satisfies the condition.
            Use for "search across multiple fields" scenarios (e.g., search in first_name OR last_name).
        AND: Combine conditions with AND - matches only if ALL columns satisfy the condition.
            Use for "must match all fields" scenarios (less common).
    
    Example:
        >>> # Match if first_name OR last_name contains "John"
        >>> ctx.add_filter(..., columns=[User.first_name, User.last_name], columns_logic=ColumnsLogic.OR)
        >>> 
        >>> # Match only if both columns satisfy condition (rare use case)
        >>> ctx.add_filter(..., columns=[col1, col2], columns_logic=ColumnsLogic.AND)
    """

    OR = "or"
    AND = "and_"


class AvailableFilterSelectItem(BaseModel):
    """Represents a single selectable option in a select or select_array filter.

    Each item represents one possible value that can be selected in the filter's
    UI component. The label is shown to users, while the value is used in the
    database query.

    Attributes:
        label: Human-readable display label shown in the UI (e.g., "Active Users").
        value: The actual value used for filtering in the database query. Can be
            any type (str, int, enum, etc.) that matches the column's data type.
    
    Example:
        >>> AvailableFilterSelectItem(label="Active", value="active")
        >>> AvailableFilterSelectItem(label="Premium Plan", value=3)
    """

    label: str
    value: str | Enum | bool | int | UUID


class AvailableFilterNumberItem(BaseModel):
    """Range boundaries for a numeric filter.
    
    Defines the minimum and maximum values available for a number-type filter,
    typically derived from the actual data in the database. Used to constrain
    UI range selectors (e.g., sliders, spinners) to valid bounds.

    Attributes:
        min: Minimum value found in the dataset for this numeric field.
            None if no data exists.
        max: Maximum value found in the dataset for this numeric field.
            None if no data exists.
    
    Example:
        >>> AvailableFilterNumberItem(min=18, max=65)  # Age filter
        >>> AvailableFilterNumberItem(min=0, max=999999)  # Price filter
    """

    min: Optional[int]
    max: Optional[int]


class AvailableFilterDateItem(BaseModel):
    """Date range boundaries for a date filter.
    
    Defines the earliest and latest dates available for a date-type filter,
    typically derived from the actual data in the database. Used to constrain
    UI date pickers to valid date ranges.

    Attributes:
        min: Earliest datetime found in the dataset for this date field.
            None if no data exists.
        max: Latest datetime found in the dataset for this date field.
            None if no data exists.
    
    Example:
        >>> from datetime import datetime
        >>> AvailableFilterDateItem(
        ...     min=datetime(2020, 1, 1),
        ...     max=datetime(2025, 12, 31)
        ... )
    """

    min: Optional[datetime]
    max: Optional[datetime]


AvailableFilterValue = list[AvailableFilterSelectItem] | AvailableFilterNumberItem | AvailableFilterDateItem | None


class AvailableFilterSelect(BaseModel):
    """Select-type filter with discrete, predefined options.
    
    Represents a filter where users can select from a list of specific values,
    either single-selection (select) or multi-selection (select_array). The
    available options are typically derived from distinct values in the database
    or from predefined enums.

    Attributes:
        label: Human-readable label displayed in the UI (e.g., "Status", "Category").
        name: Internal parameter name used in queries and current_query dict.
            Must match the "name" field in the filters configuration.
        type: Filter type, either "select" for single selection or "select_array"
            for multiple selections.
        value: List of all available options that can be selected for this filter.
    
    Example:
        >>> AvailableFilterSelect(
        ...     label="User Status",
        ...     name="status",
        ...     type=AvailableFilterType.select,
        ...     value=[
        ...         AvailableFilterSelectItem(label="Active", value="active"),
        ...         AvailableFilterSelectItem(label="Inactive", value="inactive")
        ...     ]
        ... )
    """

    label: str
    name: str
    type: Literal[AvailableFilterType.select, AvailableFilterType.select_array]
    value: list[AvailableFilterSelectItem]


class AvailableFilterNumber(BaseModel):
    """Numeric range filter with minimum and maximum boundaries.
    
    Represents a filter where users can select a numeric range. The boundaries
    are typically derived from the actual min/max values in the database for
    the specified column(s).

    Attributes:
        label: Human-readable label displayed in the UI (e.g., "Age", "Price").
        name: Internal parameter name used in queries. Users provide min/max
            values as "{name}_min" and "{name}_max" in current_query.
        type: Filter type identifier, always "number".
        value: The available min/max range boundaries for this numeric field.
    
    Example:
        >>> AvailableFilterNumber(
        ...     label="Price Range",
        ...     name="price",
        ...     type=AvailableFilterType.number,
        ...     value=AvailableFilterNumberItem(min=0, max=10000)
        ... )
    """

    label: str
    name: str
    type: Literal[AvailableFilterType.number]
    value: AvailableFilterNumberItem


class AvailableFilterDate(BaseModel):
    """Date range filter with earliest and latest boundaries.
    
    Represents a filter where users can select a date range. The boundaries
    are typically derived from the actual earliest/latest dates in the database
    for the specified column(s).

    Attributes:
        label: Human-readable label displayed in the UI (e.g., "Created Date",
            "Order Date").
        name: Internal parameter name used in queries. Users provide dates as
            "{name}_min" and "{name}_max" in current_query.
        type: Filter type identifier, always "date".
        value: The available min/max date boundaries for this date field.
    
    Example:
        >>> from datetime import datetime
        >>> AvailableFilterDate(
        ...     label="Registration Date",
        ...     name="registered_at",
        ...     type=AvailableFilterType.date,
        ...     value=AvailableFilterDateItem(
        ...         min=datetime(2020, 1, 1),
        ...         max=datetime(2025, 12, 31)
        ...     )
        ... )
    """

    label: str
    name: str
    type: Literal[AvailableFilterType.date]
    value: AvailableFilterDateItem


AvailableFilter = Annotated[
    Union[
        AvailableFilterSelect,
        AvailableFilterNumber,
        AvailableFilterDate,
    ],
    Field(discriminator="type"),
]

AvailableFilters = List[AvailableFilter]


class SearchType(Enum):
    """Enumeration of search and filter types for selected (active) filters.
    
    Defines the types of filters that can be currently active in a search query.
    This mirrors AvailableFilterType but is used specifically for tracking which
    filters are currently applied by the user.
    
    Attributes:
        select: Single-selection filter is active.
        select_array: Multi-selection filter is active.
        number: Numeric range filter is active.
        date: Date range filter is active.
        search: Free-text search is active.
    """

    select = "select"
    select_array = "select_array"
    number = "number"
    date = "date"
    search = "search"


class SelectedFilterSelect(BaseModel):
    """Currently active select-type filter with its selected value.
    
    Represents a select or select_array filter that is currently applied to
    the search. Used for displaying active filters in the UI and for state
    management.

    Attributes:
        label: Human-readable label for the filter (e.g., "Status: Active").
        name: Internal parameter name matching the filter configuration.
        type: Filter type, either "select" or "select_array".
        value: The currently selected value. Can be a string, integer, enum,
            or any type that was provided in the current_query.
    
    Example:
        >>> SelectedFilterSelect(
        ...     label="Status",
        ...     name="status",
        ...     type=SearchType.select,
        ...     value="active"
        ... )
    """

    label: str
    name: str
    type: Literal[SearchType.select, SearchType.select_array]
    value: str | Enum | bool | int | UUID


class SelectedFilterNumberItem(BaseModel):
    """Currently selected numeric range values.
    
    Represents the min and max values that the user has chosen for a numeric
    range filter. Both values must be provided when the filter is active.

    Attributes:
        min: User-selected minimum value for the range filter.
        max: User-selected maximum value for the range filter.
    
    Example:
        >>> SelectedFilterNumberItem(min=25, max=50)  # Age between 25 and 50
    """

    min: int
    max: int


class SelectedFilterNumber(BaseModel):
    """Currently active numeric range filter with its selected values.
    
    Represents a number filter that is currently applied to the search with
    specific min/max values chosen by the user.

    Attributes:
        label: Human-readable label for the filter (e.g., "Price Range").
        name: Internal parameter name matching the filter configuration.
        type: Filter type identifier, always "number".
        value: The selected min/max range values.
    
    Example:
        >>> SelectedFilterNumber(
        ...     label="Price Range",
        ...     name="price",
        ...     type=SearchType.number,
        ...     value=SelectedFilterNumberItem(min=100, max=500)
        ... )
    """

    label: str
    name: str
    type: Literal[SearchType.number]
    value: SelectedFilterNumberItem


class SelectedFilterDateItem(BaseModel):
    """Currently selected date range values.
    
    Represents the start and end dates that the user has chosen for a date
    range filter. Both values must be provided when the filter is active.

    Attributes:
        min: User-selected start date/time for the range filter.
        max: User-selected end date/time for the range filter.
    
    Example:
        >>> from datetime import datetime
        >>> SelectedFilterDateItem(
        ...     min=datetime(2024, 1, 1),
        ...     max=datetime(2024, 12, 31)
        ... )
    """

    min: datetime
    max: datetime


class SelectedFilterDate(BaseModel):
    """Currently active date range filter with its selected values.
    
    Represents a date filter that is currently applied to the search with
    specific start/end dates chosen by the user.

    Attributes:
        label: Human-readable label for the filter (e.g., "Created Date").
        name: Internal parameter name matching the filter configuration.
        type: Filter type identifier, always "date".
        value: The selected date range values.
    
    Example:
        >>> from datetime import datetime
        >>> SelectedFilterDate(
        ...     label="Registration Date",
        ...     name="registered_at",
        ...     type=SearchType.date,
        ...     value=SelectedFilterDateItem(
        ...         min=datetime(2024, 1, 1),
        ...         max=datetime(2024, 6, 30)
        ...     )
        ... )
    """

    label: str
    name: str
    type: Literal[SearchType.date]
    value: SelectedFilterDateItem


class SelectedFilterSearch(BaseModel):
    """Currently active free-text search filter with its query string.
    
    Represents a search query that is currently applied. The search is typically
    performed across multiple columns defined in searchable_columns parameter
    of get_list.

    Attributes:
        label: Human-readable label for the search (e.g., "Search", "Keyword").
        name: Internal parameter name, typically "search" in current_query.
        type: Filter type identifier, always "search".
        value: The search query string entered by the user.
    
    Example:
        >>> SelectedFilterSearch(
        ...     label="Search",
        ...     name="search",
        ...     type=SearchType.search,
        ...     value="john doe"
        ... )
    """

    label: str
    name: str
    type: Literal[SearchType.search]
    value: str


SelectedFilter = Annotated[
    Union[
        SelectedFilterSelect,
        SelectedFilterNumber,
        SelectedFilterDate,
        SelectedFilterSearch,
    ],
    Field(discriminator="type"),
]

SelectedFilters = List[SelectedFilter]


class PayloadSorting(BaseModel):
    """Sorting configuration for a single column in search results.
    
    Defines how results should be ordered by a specific column. Multiple
    PayloadSorting objects can be provided to create multi-column sorting.

    Attributes:
        order_by: Sort direction, typically "asc" (ascending) or "desc" (descending).
            Can be a string or an Enum value.
        sort_by: The column/field name to sort by (e.g., "created_at", "name").
            Can be a string or an Enum value matching a model attribute.
    
    Example:
        >>> PayloadSorting(order_by="desc", sort_by="created_at")
        >>> PayloadSorting(order_by="asc", sort_by="name")
    """

    order_by: str | Enum
    sort_by: str | Enum


class Payload(BaseModel):
    """Complete search query parameters and pagination metadata.
    
    Contains both the original query parameters sent by the client and
    computed pagination information. This object provides all the data
    needed for rendering pagination controls and understanding the current
    query state.

    Attributes:
        search: Free-text search query string if provided, None otherwise.
        sorting: List of sorting configurations applied to the results.
            Empty list if no sorting is specified.
        page: Current page number (1-indexed). Default: 1.
        items_per_page: Number of items returned per page. Default: 30.
        total_row: Total count of rows matching the query (across all pages).
        last_page: The last available page number calculated as
            ceil(total_row / items_per_page).
        has_next: True if there are more pages available after the current page.
    
    Note:
        The model allows extra fields via ConfigDict(extra="allow"), so any
        additional parameters from current_query (like filter values) are
        preserved in the payload.
    
    Example:
        >>> payload = Payload(
        ...     search="john",
        ...     sorting=[PayloadSorting(order_by="desc", sort_by="created_at")],
        ...     page=2,
        ...     items_per_page=20,
        ...     total_row=156,
        ...     last_page=8,
        ...     has_next=True
        ... )
        >>> print(f"Showing page {payload.page} of {payload.last_page}")
    """

    search: Optional[str] = None
    sorting: list[PayloadSorting]
    page: int = 1
    items_per_page: int = 30
    total_row: int
    last_page: int
    has_next: bool

    model_config = ConfigDict(extra="allow")


class GetListResponse(BaseModel, Generic[RowsDataType]):
    """Complete search result containing data, filters, and pagination metadata.
    
    This is the primary return type of the get_list function when return_only_rows_data=False.
    It provides everything needed to render a full search interface with data,
    filter controls, active filter indicators, and pagination controls.
    
    Type Parameters:
        RowsDataType: The type of rows_data returned. Can be any Pydantic model,
            RowsListModelType (for SQLAlchemy model instances), RowsListDict (for
            dictionaries), or any custom Pydantic schema you define.

    Attributes:
        payload: Query parameters and pagination metadata including page number,
            total rows, sorting configuration, and search query. None if
            return_rows_data=False and return_only_rows_data=False (unusual case).
        available_filters: List of all available filter options that can be
            applied to the current dataset. Each filter includes its type,
            label, and possible values. None if return_available_filters=False.
        selected_filters: List of filters currently applied by the user,
            showing which options are active. Useful for displaying active
            filter chips/tags in the UI. None if return_selected_filters=False.
        rows_data: The actual data rows matching the search criteria. The type
            is determined by the RowsDataType type parameter. Can be:
            - RowsListModelType: List of SQLAlchemy model instances
            - RowsListDict: List of dictionaries
            - Any custom Pydantic schema (e.g., List[UserSchema])
            - None if return_rows_data=False
    
    Example:
        >>> # Using with default dict/model types
        >>> result: GetListResponse[RowsListDict] = get_list(
        ...     current_query={"search": "john", "status": "active", "page": 1},
        ...     db=session,
        ...     model=User,
        ...     filters=[...],
        ...     searchable_columns=[User.name, User.email],
        ...     return_as_dict=True
        ... )
        >>> 
        >>> # Using with custom Pydantic schema
        >>> from pydantic import BaseModel
        >>> class UserSchema(BaseModel):
        ...     id: int
        ...     name: str
        ...     email: str
        >>> 
        >>> result: GetListResponse[List[UserSchema]] = get_list(
        ...     current_query={"page": 1},
        ...     db=session,
        ...     model=User,
        ...     response_schema=UserSchema
        ... )
        >>> 
        >>> # Access pagination info
        >>> print(f"Page {result.payload.page} of {result.payload.last_page}")
        >>> print(f"Total results: {result.payload.total_row}")
        >>> 
        >>> # Access data (type-safe with custom schema)
        >>> for row in result.rows_data:
        ...     print(row.name, row.email)  # Full type hints!
        >>> 
        >>> # Display available filters
        >>> for filter in result.available_filters:
        ...     print(f"Filter: {filter.label} ({filter.type})")
        >>> 
        >>> # Show active filters
        >>> for filter in result.selected_filters:
        ...     print(f"Active: {filter.label} = {filter.value}")
    """

    payload: Payload | None = None
    available_filters: List[AvailableFilter] | None = None
    selected_filters: List[SelectedFilter] | None = None
    rows_data: RowsDataType | None = None
