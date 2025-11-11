from datetime import date, datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ...core.enums import OrderingType

__all__ = (
    "Sorting",
    "SearchPayload",
    "NumberRange",
    "TimeRange",
    "DateRange",
    "BaseModelEnumValue",
    "ListPayloadResponse",
)


class Sorting(BaseModel):
    """Sorting configuration for query results.

    Description:
        Specifies how to sort query results by defining the field to sort on
        and the ordering direction (ascending or descending).
    """

    sort_by: str = Field(..., description="The field name to sort results by.")
    order_by: OrderingType = Field(
        default=OrderingType.asc,
        description="Sorting direction: ascending or descending.",
    )


class SearchPayload(BaseModel):
    """Common request payload for paginated and searchable list endpoints.

    Description:
        Standard request body for list/search endpoints, providing pagination,
        sorting, and free-text search capabilities.
    """

    page: int | None = Field(
        default=1, description="Page number to retrieve (must be >= 1)."
    )
    items_per_page: int | None = Field(
        default=20, description="Number of items per page (max 30)."
    )
    sorting: List[Sorting] | None = Field(
        default=None, description="Optional list of sorting rules applied to the query."
    )
    search: str | None = Field(
        default="", description="Optional search term to filter results."
    )

    # Page number must be greater than or equal to one
    @field_validator("page")
    def validate_page(cls, page: int | None) -> int | None:
        """Validate that page number is at least 1.

        Description:
            Ensures page numbers are positive integers.

        Args:
            page: The page number to validate.

        Returns:
            int | None: The validated page number.

        Raises:
            ValueError: If page number is less than 1.
        """
        if page is not None and page < 1:
            raise ValueError("page number must be greater than one")
        return page

    # Make limitation for items per page
    @field_validator("items_per_page")
    def validate_items_per_page(cls, items_per_page: int | None) -> int | None:
        """Validate that items per page doesn't exceed the maximum.

        Description:
            Ensures items_per_page is within acceptable limits to prevent
            performance issues.

        Args:
            items_per_page: The number of items per page to validate.

        Returns:
            int | None: The validated items_per_page value.

        Raises:
            ValueError: If items_per_page exceeds 30.
        """
        if items_per_page is not None and items_per_page > 30:
            raise ValueError("Item per page should be lower than or equal to 30.")
        return items_per_page

    class Config:
        use_enum_values = True


class NumberRange(BaseModel):
    """Range filter for numeric values.

    Description:
        Defines minimum and maximum bounds for filtering numeric data,
        such as prices, quantities, or scores.
    """

    min: int | None = Field(
        default=None, description="Minimum value allowed in the range."
    )
    max: int | None = Field(
        default=None, description="Maximum value allowed in the range."
    )


class TimeRange(BaseModel):
    """Range filter for time values.

    Description:
        Defines minimum and maximum datetime bounds for filtering temporal data,
        such as creation dates or event timestamps.
    """

    min: datetime | None = Field(
        default=None, description="Minimum datetime allowed in the range."
    )
    max: datetime | None = Field(
        default=None, description="Maximum datetime allowed in the range."
    )


class DateRange(BaseModel):
    """Range filter for date values.

    Description:
        Defines minimum and maximum date bounds for filtering date-only data,
        without time components.
    """

    min: date | None = Field(
        default=None, description="Minimum date allowed in the range."
    )
    max: date | None = Field(
        default=None, description="Maximum date allowed in the range."
    )


class BaseModelEnumValue(BaseModel):
    """Base model configured to serialize enums as their values.

    Description:
        Pydantic base class that configures automatic serialization of Enum
        fields to their string/integer values instead of the enum names.
    """

    model_config = ConfigDict(use_enum_values=True)


class ListPayloadResponse(BaseModel):
    """Standard response structure for paginated list endpoints.

    Description:
        Provides pagination metadata alongside list results, including total
        count, page information, and navigation flags.
    """

    total_row: int | None = Field(
        default=None, description="Total number of rows matching the query."
    )
    last_page: int | None = Field(
        default=None, description="The index of the last available page."
    )
    has_next: bool | None = Field(
        default=None, description="Indicates if there is a next page available."
    )
