"""Dealer context middleware for extracting dealer information from
requests."""

from typing import Annotated
from uuid import UUID

from fastapi import Header, HTTPException, Request, status
from pydantic import BaseModel


class DealerData(BaseModel):
    """Container for dealer-specific context extracted from request headers.

    Description:
        Stores dealer identification information parsed from incoming HTTP request
        headers for use in authentication and authorization workflows.
    """

    main_dealer_id: UUID | None = None


def get_dealer_data(
    request: Request,
    main_dealer_id: Annotated[
        UUID | None,
        Header(
            alias="main-dealer-id",
            description="Unique identifier of the primary dealer associated with the request.",
        ),
    ] = None,
) -> DealerData:
    """Extract and validate dealer identification data from request headers.

    Description:
        FastAPI dependency that extracts the main-dealer-id header from incoming
        requests and validates that it is present, raising an unauthorized error
        if missing.

    Args:
        request: The incoming FastAPI request object.
        main_dealer_id: UUID of the main dealer extracted from the header.

    Returns:
        DealerData: Container with the validated dealer ID.

    Raises:
        HTTPException: 401 Unauthorized if the main-dealer-id header is missing.
    """
    if main_dealer_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing main-dealer-id header",
        )

    return DealerData(
        main_dealer_id=main_dealer_id,
    )
