import json
from enum import Enum
from typing import Annotated
from uuid import UUID

from fastapi import Header, HTTPException, status
from pydantic import BaseModel, Field, ValidationError


class UserRole(str, Enum):
    """Enumeration of user roles with different access levels.

    Description:
        Defines the hierarchy of user roles in the system, from limited manager
        access to full super administrator privileges.
    """

    manager = "manager"
    administrator = "administrator"
    super_administrator = "super_administrator"


class PermissionType(str, Enum):
    """Enumeration of permissions that can be granted to users.

    Description:
        Defines granular permissions that can be assigned to users on a per-dealer
        basis to control access to specific features and data.
    """

    dealer = "dealer"
    bulk_rule = "bulk_rule"
    inventory = "inventory"
    lead = "lead"
    page = "page"


class UserData(BaseModel):
    """Represents the authenticated user's identity, role, and access
    permissions.

    Description:
        Container for user authentication data extracted from request headers,
        including user ID, role, and dealer-specific permissions mapping.
    """

    id: UUID | None = Field(default=None, description="Unique identifier of the user.")
    role: UserRole | None = Field(
        default=None,
        description="Role assigned to the user, determining their level of access.",
    )
    permissions: dict[UUID, list[PermissionType]] | None = Field(
        default=None,
        description="Mapping of dealer IDs to the list of permissions the user has for each dealer.",
    )

    def check_accessibility(self, dealer_id: UUID | str) -> bool:
        """Check whether the user has access rights for the given dealer.

        Description:
            Verifies if the user can access data for a specific dealer based on
            their role and permission mapping. Administrators have universal access.

        Args:
            dealer_id: Dealer identifier as UUID or string.

        Returns:
            bool: True if the user has access, False otherwise.
        """
        # Administrators have universal access
        if self.role in {UserRole.super_administrator, UserRole.administrator}:
            return True

        # Normalize dealer_id to UUID
        uuid_dealer_id = (
            dealer_id if isinstance(dealer_id, UUID) else UUID(str(dealer_id))
        )

        # Check permissions mapping
        return bool(self.permissions and uuid_dealer_id in self.permissions)


def get_user_data(
    user_id: Annotated[
        UUID | None,
        Header(
            alias="user-id",
            description="Unique identifier of the user making the request.",
        ),
    ] = None,
    user_role: Annotated[
        UserRole | None,
        Header(
            alias="user-role",
            description="Role assigned to the user making the request.",
        ),
    ] = None,
    user_permissions: Annotated[
        str | None,
        Header(
            alias="user-permissions",
            description=(
                "JSON-encoded mapping of dealer IDs to the list of "
                "permissions granted to the user."
            ),
        ),
    ] = None,
) -> UserData:
    """Extract and validate user authentication data from request headers.

    Description:
        FastAPI dependency that parses and validates user authentication headers,
        including user ID, role, and JSON-encoded permissions mapping.

    Args:
        user_id: UUID extracted from the user-id header.
        user_role: User role extracted from the user-role header.
        user_permissions: JSON string of dealer permissions from user-permissions header.

    Returns:
        UserData: Validated user authentication data.

    Raises:
        HTTPException: 401 if user-id header is missing.
        HTTPException: 400 if user-permissions JSON is malformed.
    """
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing user-id header"
        )

    perms = None
    if user_permissions:
        try:
            raw = json.loads(user_permissions)
            perms = {UUID(k): [PermissionType(p) for p in v] for k, v in raw.items()}
        except (json.JSONDecodeError, ValueError, TypeError, ValidationError):
            raise HTTPException(
                status_code=400, detail="Invalid user-permissions header JSON"
            )

    return UserData(id=user_id, role=user_role, permissions=perms)
