"""SQL condition builders for various filter types.

Provides functions to construct SQLAlchemy WHERE conditions from filter
definitions and user-selected values, supporting select, number, and
date filters.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import Text, and_, cast, func, literal, or_, select
from sqlalchemy.dialects.postgresql import ARRAY, array
from sqlalchemy.sql.elements import ColumnElement

__all__ = ("make_condition",)


def select_condition_maker(
    filter_item: dict[str, Any], values: list[Any], array_mode: bool
) -> ColumnElement[bool]:
    """Build SQL conditions for select-based filters with optional similarity
    search.

    Creates WHERE conditions for select-type filters, supporting exact matching,
    case-insensitive comparison, array operations, and fuzzy similarity matching.

    Args:
        filter_item: Dictionary defining the filter configuration including:
            - columns: List of column expressions to filter
            - columns_logic: 'or' or 'and_' for combining column conditions
            - case_insensitive: If True, perform case-insensitive matching
            - use_similarity: If True, use fuzzy similarity matching
            - similarity_threshold: Minimum similarity score for fuzzy matches
        values: List of selected values to filter by.
        array_mode: If True, treat columns as arrays and use array operators.

    Returns:
        A SQLAlchemy boolean expression combining all filter conditions.
    """
    columns = filter_item.get("columns", [])
    columns_logic = filter_item.get("columns_logic", "or")
    case_insensitive = filter_item.get("case_insensitive", False)
    use_similarity = filter_item.get("use_similarity", False)
    similarity_threshold = filter_item.get("similarity_threshold", 0.3)
    logic_fn = {"or": or_, "and_": and_}[columns_logic]

    # 1) Unwrap enums / custom types into primitives
    def unwrap(v_):
        if isinstance(v_, Enum):
            return v_.value
        return v_

    # 2) Pre-process values: unwrap + optional lower()
    processed_values = []
    for v in values:
        uv = unwrap(v)
        if case_insensitive and isinstance(uv, str):
            uv = uv.lower()
        processed_values.append(uv)

    conditions = []

    if use_similarity:
        for col in columns:
            for v in processed_values:
                if isinstance(v, str):
                    lit_q = literal(v).cast(Text)
                    col_txt = cast(col, Text)
                    conditions.append(
                        func.similarity(col_txt, lit_q) >= similarity_threshold
                    )
                else:
                    # now v is a primitive (int, float, etc.)
                    conditions.append(col == v)
    else:
        for col in columns:
            # detect string columns via their python_type
            is_str_col = getattr(getattr(col, "type", None), "python_type", None) is str
            if case_insensitive and is_str_col:
                if array_mode:
                    lower_col_array = func.array(
                        select(func.lower(func.unnest(col))).scalar_subquery()
                    )
                    lower_vals_array = array(
                        [v.lower() for v in processed_values], type_=ARRAY(Text())
                    )
                    conditions.append(lower_col_array.op("&&")(lower_vals_array))
                else:
                    conditions.append(func.lower(col).in_(processed_values))
            else:
                if array_mode:
                    conditions.append(col.op("&&")(literal(processed_values)))
                else:
                    conditions.append(col.in_(processed_values))

    # if no conditions, return a no-op true clause
    if not conditions:
        return literal(True)

    return logic_fn(*conditions)


def number_condition_maker(
    filter_item: dict[str, Any], values: dict[str, Any]
) -> ColumnElement[bool] | None:
    """Build SQL conditions for numeric range filters.

    Creates WHERE conditions for filtering by numeric ranges, supporting
    minimum, maximum, or both boundaries.

    Args:
        filter_item: Dictionary defining the filter configuration including:
            - columns: List of column expressions to filter
            - columns_logic: 'or' or 'and' for combining column conditions
        values: Dictionary containing 'min' and/or 'max' numeric values.

    Returns:
        A SQLAlchemy boolean expression for the numeric range condition,
        or None if no valid range is specified.
    """
    columns = filter_item.get("columns", [])
    columns_logic = filter_item.get("columns_logic", "or")
    logic_function = {
        "or": or_,
        "and": and_,
    }.get(columns_logic, and_)

    value_min = values.get("min")
    value_max = values.get("max")
    if value_min is not None and value_max is not None:
        return logic_function(
            *[getattr(column, "between")(value_min, value_max) for column in columns]
        )
    elif value_min is None and value_max is not None:
        return logic_function(*[column <= value_max for column in columns])
    elif value_min is not None and value_max is None:
        return logic_function(*[column >= value_min for column in columns])
    else:
        return None


def date_condition_maker(
    filter_item: dict[str, Any], values: dict[str, datetime]
) -> ColumnElement[bool] | None:
    """Build SQL conditions for date range filters.

    Creates WHERE conditions for filtering by date ranges, supporting
    minimum, maximum, or both boundaries. Handles NULL values gracefully
    for maximum date filters.

    Args:
        filter_item: Dictionary defining the filter configuration including:
            - columns: List of column expressions to filter
            - columns_logic: 'or' or 'and' for combining column conditions
        values: Dictionary containing 'min' and/or 'max' datetime values.

    Returns:
        A SQLAlchemy boolean expression for the date range condition,
        or None if no valid range is specified.
    """
    value_min: datetime | None = values.get("min")
    value_max: datetime | None = values.get("max")

    columns = filter_item.get("columns", [])
    columns_logic = filter_item.get("columns_logic", "or")
    logic_function = {
        "or": or_,
        "and": and_,
    }.get(columns_logic, and_)

    if value_min is not None and value_max is not None:
        return logic_function(
            *[getattr(column, "between")(value_min, value_max) for column in columns]
        )
    elif value_min is None and value_max is not None:
        return logic_function(
            *[or_(column <= value_max, column.is_(None)) for column in columns]
        )
    elif value_min is not None and value_max is None:
        return logic_function(*[column >= value_min for column in columns])
    else:
        return None


def make_condition(
    filter_item: dict[str, Any], values: Any
) -> ColumnElement[bool] | None:
    """Build SQL WHERE conditions from filter definitions and selected values.

    Routes to the appropriate condition builder based on filter type,
    creating SQLAlchemy boolean expressions for filtering queries.

    Args:
        filter_item: Dictionary defining the filter including type and configuration.
        values: The selected filter values (list for select, dict for ranges).

    Returns:
        A SQLAlchemy boolean expression representing the filter condition,
        or None if the filter type is not supported.
    """
    columns_type = filter_item.get("type", "select")

    if columns_type in {"select", "select_array"}:
        return select_condition_maker(
            filter_item=filter_item,
            values=values,
            array_mode=columns_type == "select_array",
        )
    elif columns_type == "number":
        return number_condition_maker(
            filter_item=filter_item,
            values=values,
        )
    elif columns_type == "date":
        return date_condition_maker(
            filter_item=filter_item,
            values=values,
        )
    else:
        return None
