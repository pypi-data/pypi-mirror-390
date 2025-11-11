"""Common response schemas for API endpoints."""

from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field, RootModel

__all__ = (
    "ResponseBase",
    "SuccessResponse",
    "FailedResponse",
    "BoolResponse",
    "StrResponse",
    "UUIDResponse",
    "ListResponse",
    "ListOfDictResponse",
    "DictResponse",
)


T = TypeVar("T")


class ResponseBase(BaseModel):
    """Base structure returned by every API endpoint.

    This class serves as the foundation for all API responses, providing
    a consistent success indicator across all endpoints.

    Attributes:
        success: Indicates whether the request was processed successfully.
    """

    success: bool = Field(
        ..., description="Indicates whether the request was processed successfully."
    )


class SuccessResponse(ResponseBase, Generic[T]):
    """Successful API response wrapper.

    Wraps successful API responses with a standardized structure containing
    the success flag and the actual data payload.

    Attributes:
        success: Always true for successful responses.
        data: Payload returned by the API. Content depends on the endpoint.

    Type Parameters:
        T: The type of data contained in the response payload.
    """

    success: bool = Field(
        default=True, description="Always true for successful responses."
    )
    data: Any = Field(
        ...,
        description="Payload returned by the API. The content depends on the specific endpoint.",
    )


class FailedResponse(ResponseBase):
    """Error response wrapper.

    Wraps failed API responses with a standardized structure containing
    the success flag set to false and an error message.

    Attributes:
        success: Always false for failed responses.
        message: Error message explaining why the request failed.
    """

    success: bool = Field(
        default=False, description="Always false for failed responses."
    )
    message: str = Field(
        ..., description="Error message explaining why the request failed."
    )


class BoolResponse(RootModel[bool]):
    """Simple boolean response model.

    A root model that validates and serializes boolean values as the
    direct response payload without wrapper objects.
    """


class StrResponse(RootModel[str]):
    """Simple string response model.

    A root model that validates and serializes string values as the
    direct response payload without wrapper objects.
    """


class UUIDResponse(RootModel[UUID]):
    """Simple UUID response model.

    A root model that validates and serializes UUID values as the
    direct response payload without wrapper objects.
    """


class ListResponse(RootModel[list]):
    """Simple list response model.

    A root model that validates and serializes list values as the
    direct response payload without wrapper objects.
    """


class ListOfDictResponse(RootModel[list[dict[str, Any]]]):
    """Response model for a list of dictionaries.

    A root model that validates and serializes a list of dictionaries
    as the direct response payload without wrapper objects.
    """


class DictResponse(RootModel[dict[str, Any]]):
    """Simple dictionary response model.

    A root model that validates and serializes dictionary values as the
    direct response payload without wrapper objects.
    """
