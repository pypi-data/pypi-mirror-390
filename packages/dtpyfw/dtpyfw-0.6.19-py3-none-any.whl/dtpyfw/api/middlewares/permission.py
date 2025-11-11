"""Permission and role-based access control middleware helpers."""

from typing import Callable

from fastapi import Depends

from .dealer import DealerData, get_dealer_data
from .user import (
    PermissionType,
    UserData,
    UserRole,
    get_user_data,
)
from ...core.exception import RequestException


def check_permissions(
    user_data: UserData,
    dealer_data: DealerData,
    required_permissions: list[PermissionType],
) -> bool:
    """Verify if a user has the required permissions for a specific dealer.

    Description:
        Evaluates whether a user's role and permission set grants access to
        perform actions on a specific dealer. Super admins and administrators
        have universal access, while managers must have explicit permissions.

    Args:
        user_data: User authentication and permission data.
        dealer_data: Dealer context information from the request.
        required_permissions: List of permissions required for the action.

    Returns:
        bool: True if user has required permissions, False otherwise.
    """
    limited_roles = {UserRole.manager}

    if user_data.role not in limited_roles:
        return True

    # Check if dealer_data has a main_dealer_id and user has permissions
    if dealer_data.main_dealer_id is None or user_data.permissions is None:
        return False

    if dealer_data.main_dealer_id not in user_data.permissions:
        return False

    user_permissions: list[PermissionType] = (
        user_data.permissions.get(dealer_data.main_dealer_id) or []
    )
    if len(user_permissions) != 0 and not set(required_permissions).issubset(
        set(user_permissions)
    ):
        return False

    return True


def permission_restriction(
    required_permissions: list[PermissionType],
) -> Callable[[UserData, DealerData], tuple[UserData, DealerData]]:
    """Create a FastAPI dependency that enforces permission requirements.

    Description:
        Returns a dependency function that validates user permissions against
        the required permissions for a dealer-specific operation, raising a
        403 error if access is denied.

    Args:
        required_permissions: List of permissions needed to access the endpoint.

    Returns:
        Callable: FastAPI dependency function that validates permissions.

    Raises:
        RequestException: 403 Forbidden if user lacks required permissions.
    """
    controller = f"{__name__}.permission_restriction"

    def dependency(
        user_data: UserData = Depends(get_user_data),
        dealer_data: DealerData = Depends(get_dealer_data),
    ) -> tuple[UserData, DealerData]:
        """Validate user permissions for the dealer.

        Args:
            user_data: User authentication and permission data.
            dealer_data: Dealer context information from the request.

        Returns:
            tuple[UserData, DealerData]: User and dealer data if authorized.

        Raises:
            RequestException: 403 Forbidden if user lacks required permissions.
        """
        is_permitted = check_permissions(
            user_data=user_data,
            dealer_data=dealer_data,
            required_permissions=required_permissions,
        )
        if not is_permitted:
            raise RequestException(
                status_code=403,
                controller=controller,
                message="You don't have permission to access this dealer or this section.",
            )

        return user_data, dealer_data

    return dependency


def role_restriction(
    required_roles: list[UserRole],
) -> Callable[[UserData], UserData]:
    """Create a FastAPI dependency that enforces role requirements.

    Description:
        Returns a dependency function that validates whether a user's role is
        in the list of allowed roles, raising a 403 error if access is denied.

    Args:
        required_roles: List of roles allowed to access the endpoint.

    Returns:
        Callable: FastAPI dependency function that validates user role.

    Raises:
        RequestException: 403 Forbidden if user's role is not in required_roles.
    """
    controller = f"{__name__}.role_restriction"

    def dependency(
        user_data: UserData = Depends(get_user_data),
    ) -> UserData:
        """Validate user role matches required roles.

        Args:
            user_data: User authentication and role data.

        Returns:
            UserData: User data if authorized.

        Raises:
            RequestException: 403 Forbidden if user's role is not in required_roles.
        """
        if user_data.role not in required_roles:
            raise RequestException(
                status_code=403,
                controller=controller,
                message="You don't have permission to access this section.",
            )

        return user_data

    return dependency
