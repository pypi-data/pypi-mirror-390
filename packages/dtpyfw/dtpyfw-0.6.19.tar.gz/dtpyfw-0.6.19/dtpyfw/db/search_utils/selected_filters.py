"""Selected filter formatting utilities.

Provides functions to format currently selected filters into
user-friendly representations for display purposes.
"""

from typing import Any
from ..schema import (
    SelectedFilters, SelectedFilterSelect, SearchType, SelectedFilterNumberItem, SelectedFilterNumber,
    SelectedFilterDate, SelectedFilterDateItem, SelectedFilterSearch
)

__all__ = ("make_selected_filters",)


def make_selected_filters(
    filters: list[dict[str, Any]] | None = None,
    current_query: dict[str, Any] | None = None,
) -> SelectedFilters:
    """Build a list of selected filter descriptions from current query
    parameters.

    Converts the raw filter values from the query into formatted filter
    descriptions suitable for display, including appropriate labels and
    value representations.

    Args:
        filters: List of filter definitions containing metadata like labels,
            types, and enums.
        current_query: Dictionary containing the current query parameters with
            selected filter values.

    Returns:
        List of SelectedFilter, each representing a selected filter with:
            - label: Human-readable description of the filter
            - name: Internal filter name
            - value: The selected value(s)
            - type: Filter type (select, number, date, search)
    """
    selected_filters: SelectedFilters = []
    filters = filters or []
    current_query = current_query or {}
    for filter_item in filters:
        selected_data: Any = current_query.get(filter_item["name"])
        if not selected_data or len(selected_data) == 0:
            continue

        if (
            isinstance(selected_data, dict)
            and len([k for k, v in selected_data.items() if v is not None]) == 0
        ):
            continue

        if filter_item["type"] in {"select", "select_array"}:
            for data in selected_data:
                enum = filter_item.get("enum")
                labels = filter_item.get("labels", {})
                if enum:
                    data = getattr(enum, str(data), data)

                selected_filters.append(SelectedFilterSelect(
                    label=labels.get(enum(data) if enum else data, data),
                    name=filter_item["name"],
                    type=getattr(SearchType, filter_item["type"]),
                    value=enum(data).name if enum else data,
                ))
        elif filter_item["type"] == "number":
            if not isinstance(selected_data, dict):
                continue
            minimum = selected_data.get("min")
            maximum = selected_data.get("max")
            if minimum is not None and maximum is not None:
                result_label = (
                    f"{filter_item['label']} (between {minimum} and {maximum})"
                )
            elif minimum is None and maximum is not None:
                result_label = f"{filter_item['label']} (To {maximum})"
            elif minimum is not None and maximum is None:
                result_label = f"{filter_item['label']} (From {minimum})"
            else:
                result_label = filter_item["label"]

            selected_filters.append(SelectedFilterNumber(
                label=result_label,
                name=filter_item["name"],
                type=SearchType.number,
                value=SelectedFilterNumberItem(
                    min=minimum,
                    max=maximum,
                ),
            ))
        elif filter_item["type"] == "date":
            if not isinstance(selected_data, dict):
                continue
            minimum = selected_data.get("min")
            maximum = selected_data.get("max")
            if minimum is not None and maximum is not None:
                result_label = f"{filter_item['label']} (From {minimum} To {maximum})"
            elif minimum is None and maximum is not None:
                result_label = f"{filter_item['label']} (To {maximum})"
            elif minimum is not None and maximum is None:
                result_label = f"{filter_item['label']} (From {minimum})"
            else:
                result_label = filter_item["label"]

            selected_filters.append(SelectedFilterDate(
                label=result_label,
                name=filter_item["name"],
                type=SearchType.date,
                value=SelectedFilterDateItem(
                    min=minimum,
                    max=maximum,
                ),
            ))
        elif filter_item["type"] == "search":
            selected_filters.append(SelectedFilterSearch(
                label=f"Search ({selected_data})",
                name=filter_item["name"],
                type=SearchType.search,
                value=selected_data,
            ))

    return selected_filters
