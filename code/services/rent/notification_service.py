"""
Mocked notification services (OneSignal and SendGrid) for Rent service.
"""

import random
import asyncio
from typing import Dict


class MockNotificationService:
    """Mocked notification service that simulates OneSignal and SendGrid."""

    async def send_push_notification(
        self, user_id: str, title: str, message: str
    ) -> Dict[str, bool]:
        """
        Simulate sending push notification via OneSignal.

        Args:
            user_id: User identifier
            title: Notification title
            message: Notification message

        Returns:
            Dictionary with success status
        """
        # Simulate network delay
        await asyncio.sleep(0.2)

        # Randomly succeed or fail (95% success rate)
        success = random.random() > 0.05

        print(
            f"[OneSignal] Push notification to user {user_id}: {title} - {message} ({'sent' if success else 'failed'})"
        )

        return {"success": success}

    async def send_email(self, email: str, subject: str, body: str) -> Dict[str, bool]:
        """
        Simulate sending email via SendGrid.

        Args:
            email: Recipient email
            subject: Email subject
            body: Email body

        Returns:
            Dictionary with success status
        """
        # Simulate network delay
        await asyncio.sleep(0.3)

        # Randomly succeed or fail (95% success rate)
        success = random.random() > 0.05

        print(
            f"[SendGrid] Email to {email}: {subject} ({'sent' if success else 'failed'})"
        )

        return {"success": success}


# Global instance
notification_service = MockNotificationService()
