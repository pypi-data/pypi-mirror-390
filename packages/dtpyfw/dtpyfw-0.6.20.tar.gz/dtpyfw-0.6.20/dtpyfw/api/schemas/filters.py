from typing import Annotated, Literal, Union
from uuid import UUID

from pydantic import BaseModel, Field

from .models import NumberRange, TimeRange

__all__ = (
    "FilterSelectValue",
    "FilterOption",
    "SelectedFilter",
    "SearchResponseAvailableFilters",
    "SearchResponseSelectedFilters",
)


class FilterOptionBase(BaseModel):
    """Base model for describing a filter option exposed by the API.

    Description:
        Provides common fields shared by all filter option types, including
        the label and name identifier.
    """

    label: str = Field(..., description="Human-readable label of the filter.")
    name: str = Field(..., description="Unique key or identifier of the filter.")


class FilterSelectValue(BaseModel):
    """Possible selectable value for a 'select' filter option.

    Description:
        Represents a single option within a select-type filter, with a display
        label and an underlying value that can be a UUID, boolean, or string.
    """

    label: str = Field(..., description="Human-readable label for the option.")
    value: UUID | bool | str | None = Field(
        default=None,
        description="Underlying value associated with the option (UUID, boolean, or string).",
    )


class FilterOptionSelect(FilterOptionBase):
    """Filter option representing a selectable list of values.

    Description:
        Defines a filter that allows users to select from a predefined list
        of values (e.g., dropdown, checkboxes).
    """

    type: Literal["select"] = Field(
        ..., description="Type identifier: always 'select'."
    )
    value: list[FilterSelectValue] = Field(
        ..., description="List of available values that can be chosen for this filter."
    )


class FilterOptionDate(FilterOptionBase):
    """Filter option representing a date or datetime range.

    Description:
        Defines a filter that allows users to select a date or datetime range
        for filtering results.
    """

    type: Literal["date"] = Field(..., description="Type identifier: always 'date'.")
    value: TimeRange = Field(
        ..., description="Range of datetime values allowed for this filter."
    )


class FilterOptionNumber(FilterOptionBase):
    """Filter option representing a numeric range.

    Description:
        Defines a filter that allows users to specify a numeric range for
        filtering results (e.g., price range, quantity).
    """

    type: Literal["number"] = Field(
        ..., description="Type identifier: always 'number'."
    )
    value: NumberRange = Field(
        ..., description="Range of numeric values allowed for this filter."
    )


# Union of all available filter option types
FilterOption = Annotated[
    Union[FilterOptionSelect, FilterOptionDate, FilterOptionNumber],
    Field(discriminator="type"),
]


class SearchResponseAvailableFilters(BaseModel):
    """Response payload listing all available filters for a search.

    Description:
        Contains the list of filter definitions that users can apply to refine
        their search results.
    """

    available_filters: list[FilterOption] = Field(
        ..., description="List of filter definitions that can be applied in the search."
    )


class SelectedFilterBase(BaseModel):
    """Base model for describing a filter that has been applied by the user.

    Description:
        Provides common fields shared by all selected filter types, including
        the label and name identifier.
    """

    label: str = Field(..., description="Human-readable label of the filter.")
    name: str = Field(..., description="Unique key or identifier of the filter.")


class SelectedFilterSelect(SelectedFilterBase):
    """Applied 'select' filter chosen by the user.

    Description:
        Represents a select-type filter that has been applied with a specific
        value selected by the user.
    """

    type: Literal["select"] = Field(
        ..., description="Type identifier: always 'select'."
    )
    value: UUID | bool | str | None = Field(
        default=None,
        description="Selected value for the filter (UUID, boolean, or string).",
    )


class SelectedFilterDate(SelectedFilterBase):
    """Applied 'date' filter chosen by the user.

    Description:
        Represents a date-type filter that has been applied with a specific
        date or datetime range selected by the user.
    """

    type: Literal["date"] = Field(..., description="Type identifier: always 'date'.")
    value: TimeRange = Field(
        ..., description="Date or datetime range selected by the user."
    )


class SelectedFilterNumber(SelectedFilterBase):
    """Applied 'number' filter chosen by the user.

    Description:
        Represents a number-type filter that has been applied with a specific
        numeric range selected by the user.
    """

    type: Literal["number"] = Field(
        ..., description="Type identifier: always 'number'."
    )
    value: NumberRange = Field(..., description="Numeric range selected by the user.")


class SelectedFilterSearch(SelectedFilterBase):
    """Applied 'search' filter containing a free-text query.

    Description:
        Represents a search-type filter that has been applied with a free-text
        query string provided by the user.
    """

    type: Literal["search"] = Field(
        ..., description="Type identifier: always 'search'."
    )
    value: str = Field(..., description="Free-text query string provided by the user.")


# Union of all possible selected filter types
SelectedFilter = Annotated[
    Union[
        SelectedFilterSelect,
        SelectedFilterDate,
        SelectedFilterNumber,
        SelectedFilterSearch,
    ],
    Field(discriminator="type"),
]


class SearchResponseSelectedFilters(BaseModel):
    """Response payload listing all filters applied by the user.

    Description:
        Contains the list of filters currently active in the user's search,
        showing what criteria are being used to filter results.
    """

    selected_filters: list[SelectedFilter] = Field(
        ..., description="List of filters currently applied in the search."
    )
