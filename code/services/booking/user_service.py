"""
Client for calling User Account service (nested function call).
"""

import httpx
import os
from typing import Optional, Dict

USER_ACCOUNT_SERVICE_URL = os.getenv(
    "USER_ACCOUNT_SERVICE_URL", "http://user-account:8001"
)


async def get_user(user_id: str) -> Optional[Dict]:
    """
    Get user information from User Account service.

    This is a nested function call - Booking service calls User Account service
    to validate that the user exists and is not blocked before creating a booking.

    Args:
        user_id: The ID of the user to retrieve

    Returns:
        User data dictionary if found, None otherwise
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{USER_ACCOUNT_SERVICE_URL}/api/v1/users/{user_id}"
            )
            if response.status_code == 200:
                return response.json()
            return None
    except Exception as e:
        print(f"Error calling user-account service: {e}")
        return None


async def validate_user(user_id: str) -> bool:
    """
    Validate that a user exists and is not blocked.

    This function calls the User Account service to check user status.

    Args:
        user_id: The ID of the user to validate

    Returns:
        True if user exists and is not blocked, False otherwise
    """
    user = await get_user(user_id)
    if not user:
        return False

    # Check if user is blocked
    if user.get("is_blocked", False):
        return False

    return True
