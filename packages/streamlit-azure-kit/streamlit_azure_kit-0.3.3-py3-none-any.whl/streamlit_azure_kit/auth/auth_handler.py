"""
Azure Entra ID Authentication Handler
Handles group-based authentication and role-based access control
"""

import os
import json
import base64
import streamlit as st
from typing import Dict, List, Optional


class AuthHandler:
    """Handle Azure Entra ID group-based authentication and user roles."""

    def __init__(self, config_path: str):
        """
        Load and validate user roles configuration.

        Args:
            config_path: Path to user_roles.json configuration file

        Raises:
            ValueError: If configuration is invalid
        """
        self.config_path = config_path
        self._load_and_validate_config()

    def _load_and_validate_config(self) -> None:
        """Load and validate configuration file."""
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)

        # Validate required keys
        if "groups" not in self.config:
            raise ValueError("user_roles.json must contain 'groups' key")

        # Validate unique priorities
        priorities = [g["priority"] for g in self.config["groups"].values()]
        if len(priorities) != len(set(priorities)):
            raise ValueError(
                "Duplicate priority values found in user_roles.json. "
                "Each group must have a unique priority number."
            )

        # Validate required fields for each group
        for group_id, group_data in self.config["groups"].items():
            if "role" not in group_data:
                raise ValueError(f"Group {group_id} missing required 'role' field")
            if "priority" not in group_data:
                raise ValueError(f"Group {group_id} missing required 'priority' field")
            if not isinstance(group_data["priority"], int) or group_data["priority"] < 1:
                raise ValueError(f"Group {group_id} priority must be positive integer")

    def _get_auth_header(self, header_name: str) -> str:
        """
        Get Azure App Service authentication header with fallback logic.

        Precedence order:
        1. Streamlit context headers (production Azure App Service)
        2. Environment variables with HTTP_ prefix (alternative Azure format)
        3. Environment variables without prefix (local testing)

        Args:
            header_name: Header name in standard format (e.g., 'X-MS-CLIENT-PRINCIPAL')

        Returns:
            Header value or empty string if not found
        """
        # Try Streamlit context first (production)
        if hasattr(st, 'context') and hasattr(st.context, 'headers'):
            value = st.context.headers.get(header_name, '')
            if value:
                return value

        # Try environment variables (local testing or alternative Azure setup)
        env_variants = [
            f'HTTP_{header_name.upper().replace("-", "_")}',  # HTTP_X_MS_CLIENT_PRINCIPAL
            header_name.upper().replace("-", "_"),             # X_MS_CLIENT_PRINCIPAL
        ]

        for env_var in env_variants:
            value = os.environ.get(env_var)
            if value:
                return value

        return ''

    def _parse_azure_principal(self) -> Optional[Dict]:
        """
        Parse Azure Easy Auth principal header.

        Returns:
            Dict with user info including groups, or None if parsing fails
        """
        principal_header = self._get_auth_header('X-MS-CLIENT-PRINCIPAL')

        if not principal_header:
            raise RuntimeError(
                "Azure Easy Auth not configured. "
                "Missing X-MS-CLIENT-PRINCIPAL header. "
                "Ensure Easy Auth is enabled in Azure App Service."
            )

        # Decode base64 and parse JSON
        try:
            decoded = base64.b64decode(principal_header)
            principal_data = json.loads(decoded)
        except Exception as e:
            raise RuntimeError(f"Failed to parse authentication token: {e}")

        # Extract claims
        claims = principal_data.get("claims", [])

        # Extract groups
        user_groups = [
            claim["val"]
            for claim in claims
            if claim.get("typ") == "groups"
        ]

        # Extract email (optional, for display)
        user_email = None
        for claim in claims:
            if "emailaddress" in claim.get("typ", ""):
                user_email = claim["val"]
                break

        # Extract name (optional, for display)
        user_name = None
        for claim in claims:
            if claim.get("typ") == "name":
                user_name = claim["val"]
                break

        return {
            'email': user_email,
            'name': user_name,
            'groups': user_groups
        }

    def _get_user_role_from_groups(self, user_groups: List[str]) -> Optional[str]:
        """
        Determine user's role based on group membership.

        When user is in multiple groups, return role with lowest priority (highest privilege).

        Args:
            user_groups: List of Entra Group Object IDs

        Returns:
            role (str): Role name if user in valid group
            None: If user not in any configured group
        """
        matching_groups = {}

        # Find all groups user belongs to
        for group_id in user_groups:
            if group_id in self.config["groups"]:
                group_config = self.config["groups"][group_id]
                matching_groups[group_id] = {
                    "role": group_config["role"],
                    "priority": group_config["priority"]
                }

        # No matching groups
        if not matching_groups:
            return None

        # Return role with lowest priority (highest privilege)
        highest_privilege = min(matching_groups.values(), key=lambda x: x["priority"])
        return highest_privilege["role"]

    def get_current_user(self) -> Optional[Dict]:
        """
        Get current user information.

        Uses Streamlit session state to cache auth data captured from initial HTTP request.
        This allows the auth data to persist across WebSocket requests where headers aren't present.

        Returns:
            Dict with keys: email, name, role, groups
            None if not authenticated
        """
        # CRITICAL FIX: Check session state first (persists across WebSocket requests)
        if 'auth_user_info' in st.session_state:
            return st.session_state.auth_user_info

        # Local development mode - bypass Azure auth
        if os.getenv('ENVIRONMENT') == 'local':
            user_info = {
                'email': os.getenv('TEST_USER_EMAIL', 'test@example.com'),
                'name': os.getenv('TEST_USER_NAME', 'Test User'),
                'role': os.getenv('TEST_USER_ROLE', 'admin'),
                'groups': []  # Empty in local mode
            }
            st.session_state.auth_user_info = user_info
            return user_info

        # Azure production mode - try to get from headers
        try:
            user_data = self._parse_azure_principal()

            # Get role from groups
            role = self._get_user_role_from_groups(user_data['groups'])

            user_info = {
                'email': user_data['email'],
                'name': user_data['name'],
                'role': role,
                'groups': user_data['groups']
            }

            # CRITICAL FIX: Cache in session state for subsequent WebSocket requests
            st.session_state.auth_user_info = user_info
            return user_info

        except RuntimeError as e:
            # If we get "Missing X-MS-CLIENT-PRINCIPAL header" error on a WebSocket request,
            # that's expected - session state should have the data
            # But if session state is also empty, we have a real auth problem
            if 'auth_user_info' not in st.session_state:
                # First request and no headers = not authenticated
                raise
            # Re-raise other RuntimeErrors
            raise
        except Exception as e:
            st.error(f"Error getting user information: {e}")
            return None

    def get_current_user_role(self) -> Optional[str]:
        """
        Get current user's role.

        Returns:
            Role name if user in valid group, None otherwise
        """
        user = self.get_current_user()
        if user:
            return user.get('role')
        return None

    def check_page_permission(self, page_name: str) -> bool:
        """
        Check if current user can access page.

        Default behavior: If page_permissions is empty or page not listed, allow access.

        Args:
            page_name: Page filename without .py (e.g., "01_Dashboard")

        Returns:
            True if access allowed, False otherwise
        """
        user_role = self.get_current_user_role()

        # No role = no access
        if user_role is None:
            return False

        page_permissions = self.config.get("page_permissions", {})

        # No permissions defined → allow all
        if not page_permissions:
            return True

        # Page not in permissions → allow all
        if page_name not in page_permissions:
            return True

        # Check if role is in allowed list
        allowed_roles = page_permissions[page_name]
        return user_role in allowed_roles

    def require_auth(self) -> None:
        """
        Ensure user is authenticated.
        If not authenticated or not in valid group, show error and stop.
        """
        # Check for local dev mode warning
        if os.getenv('ENVIRONMENT') == 'local':
            st.sidebar.warning("⚠️ Running in local development mode")

        user = self.get_current_user()

        # Not authenticated
        if user is None:
            st.error("🔒 Authentication required. Please log in to access this application.")
            st.info("""
            If you're not automatically redirected, please:
            1. Clear your browser cache
            2. Navigate to the homepage first: `/`
            3. Then try accessing this page again
            """)
            st.stop()

        # Authenticated but not in any configured group
        if user.get('role') is None:
            st.error("""
🚫 Access Denied

You are not authorized to access this dashboard.

Please contact your administrator to be added to the appropriate access group.
""")
            st.stop()

    def show_user_info(self) -> None:
        """Display user info in Streamlit sidebar."""
        user = self.get_current_user()

        if user:
            with st.sidebar:
                st.markdown("---")
                st.markdown("### 👤 User Info")

                if user.get('name'):
                    st.write(f"**Name:** {user['name']}")
                if user.get('email'):
                    st.write(f"**Email:** {user['email']}")
                if user.get('role'):
                    st.write(f"**Role:** {user['role']}")

                # Show logout link (Azure App Service handles this)
                st.markdown("[🚪 Logout](/.auth/logout)")
