"""Bot permission management for the Erdo SDK."""

import os
from typing import Any, Dict, Optional

import requests


class BotPermissions:
    """Manage RBAC permissions for bots."""

    def __init__(self, base_url: Optional[str] = None):
        """Initialize bot permissions manager.

        Args:
            base_url: Erdo server base URL. Defaults to ERDO_SERVER_URL env var or localhost:4000
        """
        self.base_url = base_url or os.getenv(
            "ERDO_SERVER_URL", "http://localhost:4000"
        )
        self.session = requests.Session()

        # Set auth token if available
        token = os.getenv("ERDO_AUTH_TOKEN")
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def set_public_access(
        self, bot_id: str, is_public: bool = True, permission_level: str = "view"
    ) -> bool:
        """Set public access for a bot.

        Args:
            bot_id: Bot ID
            is_public: Whether to make the bot public
            permission_level: Permission level for public access (view, comment, edit, admin)

        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}/rbac/bot/{bot_id}/public"
            data = {
                "isPublic": is_public,
                "level": permission_level if is_public else None,
            }
            response = self.session.put(url, json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Error setting public access: {e}")
            return False

    def set_user_permission(
        self, bot_id: str, user_id: str, permission_level: str
    ) -> bool:
        """Set permissions for a specific user.

        Args:
            bot_id: Bot ID
            user_id: User ID
            permission_level: Permission level (view, comment, edit, admin, owner)

        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}/rbac/bot/{bot_id}/user/{user_id}"
            data = {"level": permission_level}
            response = self.session.put(url, json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Error setting user permission: {e}")
            return False

    def set_org_permission(
        self, bot_id: str, org_id: str, permission_level: str
    ) -> bool:
        """Set permissions for an organization.

        Args:
            bot_id: Bot ID
            org_id: Organization ID
            permission_level: Permission level (view, comment, edit, admin, owner)

        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}/rbac/bot/{bot_id}/org/{org_id}"
            data = {"level": permission_level}
            response = self.session.put(url, json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Error setting org permission: {e}")
            return False

    def remove_user_permission(self, bot_id: str, user_id: str) -> bool:
        """Remove permissions for a specific user.

        Args:
            bot_id: Bot ID
            user_id: User ID

        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}/rbac/bot/{bot_id}/user/{user_id}"
            response = self.session.delete(url)
            return response.status_code == 200
        except Exception as e:
            print(f"Error removing user permission: {e}")
            return False

    def remove_org_permission(self, bot_id: str, org_id: str) -> bool:
        """Remove permissions for an organization.

        Args:
            bot_id: Bot ID
            org_id: Organization ID

        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}/rbac/bot/{bot_id}/org/{org_id}"
            response = self.session.delete(url)
            return response.status_code == 200
        except Exception as e:
            print(f"Error removing org permission: {e}")
            return False

    def get_permissions(self, bot_id: str) -> Optional[Dict[str, Any]]:
        """Get all permissions for a bot.

        Args:
            bot_id: Bot ID

        Returns:
            Dictionary with permission details or None if error
        """
        try:
            url = f"{self.base_url}/rbac/permissions/bot/{bot_id}"
            response = self.session.get(url)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error getting permissions: {e}")
            return None

    def check_access(self, bot_id: str, permission_level: str = "view") -> bool:
        """Check if current user has access to a bot.

        Args:
            bot_id: Bot ID
            permission_level: Required permission level

        Returns:
            True if user has access, False otherwise
        """
        try:
            url = f"{self.base_url}/rbac/access/bot/{bot_id}/{permission_level}"
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                return data.get("hasAccess", False)
            return False
        except Exception as e:
            print(f"Error checking access: {e}")
            return False

    def invite_user(self, bot_id: str, email: str, permission_level: str) -> bool:
        """Invite a user to access a bot.

        Args:
            bot_id: Bot ID
            email: User's email address
            permission_level: Permission level to grant

        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}/rbac/resource/bot/{bot_id}/invite"
            data = {"email": email, "permissionLevel": permission_level}
            response = self.session.post(url, json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Error inviting user: {e}")
            return False


# Convenience functions for direct use
def set_bot_public(
    bot_id: str, is_public: bool = True, permission_level: str = "view"
) -> bool:
    """Set public access for a bot.

    Args:
        bot_id: Bot ID
        is_public: Whether to make the bot public
        permission_level: Permission level for public access

    Returns:
        True if successful, False otherwise
    """
    permissions = BotPermissions()
    return permissions.set_public_access(bot_id, is_public, permission_level)


def set_bot_user_permission(bot_id: str, user_id: str, permission_level: str) -> bool:
    """Set permissions for a user on a bot.

    Args:
        bot_id: Bot ID
        user_id: User ID
        permission_level: Permission level

    Returns:
        True if successful, False otherwise
    """
    permissions = BotPermissions()
    return permissions.set_user_permission(bot_id, user_id, permission_level)


def set_bot_org_permission(bot_id: str, org_id: str, permission_level: str) -> bool:
    """Set permissions for an organization on a bot.

    Args:
        bot_id: Bot ID
        org_id: Organization ID
        permission_level: Permission level

    Returns:
        True if successful, False otherwise
    """
    permissions = BotPermissions()
    return permissions.set_org_permission(bot_id, org_id, permission_level)


def get_bot_permissions(bot_id: str) -> Optional[Dict[str, Any]]:
    """Get all permissions for a bot.

    Args:
        bot_id: Bot ID

    Returns:
        Dictionary with permission details or None if error
    """
    permissions = BotPermissions()
    return permissions.get_permissions(bot_id)


def check_bot_access(bot_id: str, permission_level: str = "view") -> bool:
    """Check if current user has access to a bot.

    Args:
        bot_id: Bot ID
        permission_level: Required permission level

    Returns:
        True if user has access, False otherwise
    """
    permissions = BotPermissions()
    return permissions.check_access(bot_id, permission_level)
