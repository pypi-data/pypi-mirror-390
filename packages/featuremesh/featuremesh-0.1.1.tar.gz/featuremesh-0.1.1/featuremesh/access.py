"""
Access Management Client

Client-side methods for managing users, orgs, projects, roles, and invitations.
"""

import requests
from typing import Optional, Dict, Any, List
from .config import get_default

__all__ = ["AccessClient", "create_access_client", "decode_token", "generate_access_token"]

class AccessClient:
    """
    Client for FeatureMesh access management operations.
    
    All methods require an identity_token for authentication.
    """
    
    def __init__(self, identity_token: str):
        """
        Initialize the access management client.
        
        Args:
            identity_token: JWT access token for authentication
        """
        self.identity_token = identity_token
        self.host = get_default("access.host")
        self.base_path = get_default("access.path")
        self.timeout = get_default("access.timeout")
        self.verify_ssl = get_default("access.verify_ssl")
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to access management API"""

        if self.identity_token is None:
            raise ValueError("Identity token is required for access management operations")
        
        url = f"{self.host}{self.base_path}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.identity_token}",
        }
        
        try:
            if method.upper() == "GET":
                response = requests.get(
                    url, headers=headers, params=params,
                    timeout=self.timeout, verify=self.verify_ssl
                )
            elif method.upper() == "POST":
                response = requests.post(
                    url, headers=headers, json=data,
                    timeout=self.timeout, verify=self.verify_ssl
                )
            elif method.upper() == "DELETE":
                response = requests.delete(
                    url, headers=headers, json=data,
                    timeout=self.timeout, verify=self.verify_ssl
                )
            elif method.upper() == "PATCH":
                response = requests.patch(
                    url, headers=headers, json=data,
                    timeout=self.timeout, verify=self.verify_ssl
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Request failed: {str(e)}")
    
    # ========================================================================
    # USER MANAGEMENT
    # ========================================================================
    
    def get_my_user_info(self) -> Dict[str, Any]:
        """
        Get the current user's information including OAuth providers.
        
        Returns:
            Dict containing:
                - user_id: User's UUID
                - email: User's email address
                - providers: List of linked OAuth providers (e.g., ["github", "google"])
                - primary_provider: Primary OAuth provider (first one linked)
        """
        return self._make_request("GET", "/me")
    
    # ========================================================================
    # ORG MANAGEMENT
    # ========================================================================
    
    def create_org(self, org_name: str) -> Dict[str, Any]:
        """
        Create a new organization.
        
        Args:
            org_name: Organization name (2-16 alphanumeric + underscore)
        
        Returns:
            Dict with org_id and org_name
        """
        return self._make_request("POST", "/orgs", {"org_name": org_name})
    
    def delete_org(
        self,
        org: str,
        validation_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Delete an organization.
        
        First call without validation_code to get the code.
        Second call with validation_code to confirm deletion.
        
        Args:
            org: Organization name
            validation_code: Validation code from first call
        
        Returns:
            Dict with validation_code (first call) or success message (second call)
        """
        return self._make_request(
            "DELETE", "/orgs",
            {"org": org, "validation_code": validation_code}
        )
    
    def update_org_name(self, org: str, new_org_name: str) -> Dict[str, Any]:
        """
        Update organization name.
        
        Args:
            org: Current organization name
            new_org_name: New organization name
        
        Returns:
            Success message
        """
        return self._make_request(
            "PATCH", "/orgs/name",
            {"org": org, "new_org_name": new_org_name}
        )
    
    def list_orgs(self) -> List[Dict[str, Any]]:
        """
        List all orgs where user has a role.
        
        Returns:
            List of orgs with role information
        """
        result = self._make_request("GET", "/orgs")
        return result.get("orgs", [])
    
    def list_org_members(self, org: str) -> List[Dict[str, Any]]:
        """
        List all members of an org (ADMIN and OWNER only).
        
        Args:
            org: Organization name
        
        Returns:
            List of members with role information
        """
        result = self._make_request("GET", f"/orgs/{org}/members")
        return result.get("members", [])
    
    # ========================================================================
    # PROJECT MANAGEMENT
    # ========================================================================
    
    def create_project(
        self,
        project_name: str,
        org: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new project.
        
        Args:
            project_name: Project name (2-16 alphanumeric + underscore)
            org: Organization name (defaults to personal org)
        
        Returns:
            Dict with project_id and project_reference
        """
        return self._make_request(
            "POST", "/projects",
            {"project_name": project_name, "org": org}
        )
    
    def delete_project(
        self,
        project: str,
        validation_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Delete a project.
        
        First call without validation_code to get the code.
        Second call with validation_code to confirm deletion.
        
        Args:
            project: Project reference (org_name/project_name)
            validation_code: Validation code from first call
        
        Returns:
            Dict with validation_code (first call) or success message (second call)
        """
        return self._make_request(
            "DELETE", "/projects",
            {"project": project, "validation_code": validation_code}
        )
    
    def update_project_name(self, project: str, new_project_name: str) -> Dict[str, Any]:
        """
        Update project name.
        
        Args:
            project: Current project reference (org_name/project_name)
            new_project_name: New project name
        
        Returns:
            Dict with new_project_reference and success message
        """
        return self._make_request(
            "PATCH", "/projects/name",
            {"project": project, "new_project_name": new_project_name}
        )
    
    def transfer_project_to_org(
        self,
        project: str,
        new_org: str,
    ) -> Dict[str, Any]:
        """
        Transfer a project to another org.
        
        Args:
            project: Current project reference (org_name/project_name)
            new_org: New organization name
        
        Returns:
            Dict with new_project_reference
        """
        return self._make_request(
            "POST", "/projects/transfer",
            {"project": project, "new_org": new_org}
        )
    
    def list_projects(self, org: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all projects where user has a role.
        
        Args:
            org: Optional organization name to filter by
        
        Returns:
            List of projects with role information
        """
        params = {"org": org} if org else None
        result = self._make_request("GET", "/projects", params=params)
        return result.get("projects", [])
    
    def list_project_members(self, project: str) -> List[Dict[str, Any]]:
        """
        List all members of a project (ADMIN and OWNER only).
        
        Args:
            project: Project reference (org_name/project_name)
        
        Returns:
            List of members with role information
        """
        if "/" not in project:
            raise ValueError("Project must be in format org_name/project_name")
        org, project_name = project.split("/", 1)
        result = self._make_request("GET", f"/projects/{org}/{project_name}/members")
        return result.get("members", [])
    
    # ========================================================================
    # INVITATION MANAGEMENT
    # ========================================================================
    
    def invite_to_org(
        self,
        user_emails: List[str],
        org: str,
        role: str,
    ) -> Dict[str, Any]:
        """
        Invite users to an org.
        
        Args:
            user_emails: List of email addresses
            org: Organization name
            role: Role to grant (OWNER or ADMIN)
        
        Returns:
            Dict with invitations_created list
        """
        return self._make_request(
            "POST", "/invitations/org",
            {"user_emails": user_emails, "org": org, "role": role}
        )
    
    def invite_to_project(
        self,
        user_emails: List[str],
        project: str,
        role: str,
    ) -> Dict[str, Any]:
        """
        Invite users to a project.
        
        Args:
            user_emails: List of email addresses
            project: Project reference (org_name/project_name)
            role: Role to grant (OWNER, ADMIN, READ_WRITE, or READ_ONLY)
        
        Returns:
            Dict with invitations_created list
        """
        return self._make_request(
            "POST", "/invitations/project",
            {"user_emails": user_emails, "project": project, "role": role}
        )
    
    def cancel_invitations(
        self,
        user_emails: List[str],
        org: Optional[str] = None,
        project: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Cancel pending invitations.
        
        Args:
            user_emails: List of email addresses
            org: Organization name (mutually exclusive with project)
            project: Project reference (mutually exclusive with org)
        
        Returns:
            Dict with cancelled_count
        """
        return self._make_request(
            "POST", "/invitations/cancel",
            {"user_emails": user_emails, "org": org, "project": project}
        )
    
    def accept_invitation(self, invitation_id: str) -> Dict[str, Any]:
        """
        Accept a pending invitation.
        
        Args:
            invitation_id: Invitation ID
        
        Returns:
            Success message
        """
        return self._make_request(
            "POST", "/invitations/accept",
            {"invitation_id": invitation_id}
        )
    
    def decline_invitation(self, invitation_id: str) -> Dict[str, Any]:
        """
        Decline a pending invitation.
        
        Args:
            invitation_id: Invitation ID
        
        Returns:
            Success message
        """
        return self._make_request(
            "POST", "/invitations/decline",
            {"invitation_id": invitation_id}
        )
    
    def list_invitations(
        self,
        scope: str = "all",
        org: Optional[str] = None,
        project: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List invitations.
        
        Args:
            scope: "sent", "received", or "all"
            org: Optional organization name to filter by
            project: Optional project reference to filter by
        
        Returns:
            List of invitations
        """
        params = {"scope": scope}
        if org:
            params["org"] = org
        if project:
            params["project"] = project
        
        result = self._make_request("GET", "/invitations", params=params)
        return result.get("invitations", [])
    
    # ========================================================================
    # ROLE MANAGEMENT
    # ========================================================================
    
    def set_org_roles(
        self,
        user_emails: List[str],
        org: str,
        role: str,
    ) -> Dict[str, Any]:
        """
        Set org roles for users.
        
        Args:
            user_emails: List of email addresses
            org: Organization name
            role: Role to set (OWNER or ADMIN)
        
        Returns:
            Dict with updated_count
        """
        return self._make_request(
            "POST", "/roles/org/set",
            {"user_emails": user_emails, "org": org, "role": role}
        )
    
    def revoke_org_roles(
        self,
        user_emails: List[str],
        org: str,
    ) -> Dict[str, Any]:
        """
        Revoke org roles from users.
        
        Args:
            user_emails: List of email addresses
            org: Organization name
        
        Returns:
            Dict with revoked_count
        """
        return self._make_request(
            "POST", "/roles/org/revoke",
            {"user_emails": user_emails, "org": org}
        )
    
    def set_project_roles(
        self,
        user_emails: List[str],
        project: str,
        role: str,
    ) -> Dict[str, Any]:
        """
        Set project roles for users.
        
        Args:
            user_emails: List of email addresses
            project: Project reference (org_name/project_name)
            role: Role to set (OWNER, ADMIN, READ_WRITE, or READ_ONLY)
        
        Returns:
            Dict with updated_count
        """
        return self._make_request(
            "POST", "/roles/project/set",
            {"user_emails": user_emails, "project": project, "role": role}
        )
    
    def revoke_project_roles(
        self,
        user_emails: List[str],
        project: str,
    ) -> Dict[str, Any]:
        """
        Revoke project roles from users.
        
        Args:
            user_emails: List of email addresses
            project: Project reference (org_name/project_name)
        
        Returns:
            Dict with revoked_count
        """
        return self._make_request(
            "POST", "/roles/project/revoke",
            {"user_emails": user_emails, "project": project}
        )
    
    def list_my_roles(
        self,
        org: Optional[str] = None,
        project: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List user's roles in all orgs and projects.
        
        Args:
            org: Optional organization name to filter by
            project: Optional project reference to filter by
        
        Returns:
            Dict with org_roles and project_roles lists
        """
        params = {}
        if org:
            params["org"] = org
        if project:
            params["project"] = project
        
        return self._make_request("GET", "/roles/my", params=params)
    
    # ========================================================================
    # TOKEN MANAGEMENT
    # ========================================================================
    
    def invalidate_token(self) -> Dict[str, Any]:
        """
        Invalidate all tokens for the current user.
        
        Returns:
            Success message
        """
        return self._make_request("POST", "/tokens/invalidate")
    
    def invalidate_all_identity_tokens(self, user_email: str) -> Dict[str, Any]:
        """
        Invalidate all tokens for a user (org OWNER only).
        
        Args:
            user_email: Email address of user
        
        Returns:
            Success message
        """
        return self._make_request(
            "POST", "/tokens/invalidate-user",
            {"user_email": user_email}
        )
    
    # ========================================================================
    # SERVICE ACCOUNT MANAGEMENT
    # ========================================================================
    
    def create_service_account(
        self,
        project: str,
        name: str,
        role: str,
    ) -> Dict[str, Any]:
        """
        Create a service account in a project.
        
        Service accounts are API-only identities with limited permissions.
        Only project OWNER or ADMIN can create service accounts.
        Service account role cannot exceed owner's permissions.
        
        Args:
            project: Project reference (org_name/project_name)
            name: Service account name (2-64 chars, alphanumeric + underscore/hyphen)
            role: Service account role (READ_ONLY or READ_WRITE)
        
        Returns:
            Dict with service account details (id, name, role, owner_id, created_at)
        """
        return self._make_request(
            "POST",
            "/service-accounts",
            {"project": project, "name": name, "role": role}
        )
    
    def list_service_accounts(self, project: str) -> List[Dict[str, Any]]:
        """
        List all service accounts in a project.
        
        Args:
            project: Project reference (org_name/project_name)
        
        Returns:
            List of service accounts with details (id, name, role, owner_id, owner_email, created_at)
        """
        params = {"project": project}
        result = self._make_request("GET", "/service-accounts", params=params)
        return result.get("service_accounts", [])
    
    def delete_service_account(self, service_account_id: str) -> Dict[str, Any]:
        """
        Delete a service account.
        
        Only the service account owner or project OWNER/ADMIN can delete.
        
        Args:
            service_account_id: Service account UUID
        
        Returns:
            Success message
        """
        return self._make_request(
            "DELETE",
            "/service-accounts",
            {"service_account_id": service_account_id}
        )
    
    def generate_service_account_token(self, service_account_id: str) -> Dict[str, Any]:
        """
        Generate a JWT token for a service account.
        
        Only the service account owner can generate tokens.
        Token expires in 28 days.
        
        Args:
            service_account_id: Service account UUID
        
        Returns:
            Dict with token, issued_at, expires_at, and service_account details
        """
        return self._make_request(
            "POST",
            "/service-accounts/generate-token",
            {"service_account_id": service_account_id}
        )
    
    def invalidate_service_account_tokens(
        self, 
        service_account_id: str, 
        invalidate_before: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Invalidate service account tokens issued before a specific timestamp.
        
        Only the service account owner can invalidate tokens.
        If invalidate_before is not provided, all tokens issued before now are invalidated.
        The most recent token (if issued at or after invalidate_before) remains valid.
        
        Args:
            service_account_id: Service account UUID
            invalidate_before: ISO format timestamp. Tokens issued before this time will be invalidated.
                             If not provided, defaults to current time.
        
        Returns:
            Dict with success message and updated service_account details
        """
        payload = {"service_account_id": service_account_id}
        if invalidate_before:
            payload["invalidate_before"] = invalidate_before
        
        return self._make_request(
            "POST",
            "/service-accounts/invalidate-tokens",
            payload
        )
    
    def refresh_service_account_token(self) -> Dict[str, Any]:
        """
        Refresh the current service account's token (self-service).
        
        This is the ONLY access management operation a service account can perform.
        Must be called with a service account token (not a user token).
        Token expires in 28 days.
        
        Returns:
            Dict with new token, expires_at, and service_account details
        """
        return self._make_request("POST", "/service-accounts/refresh-token")
    
    # ========================================================================
    # PROJECT TOKENS
    # ========================================================================
    
    def generate_access_token(self, project: str) -> Dict[str, Any]:
        """
        Generate a JWT token for accessing a specific project.
        
        The token is scoped to the project and includes the user's role in that project.
        Token expires in 1 day.
        
        This method requires a user identity token (not a project token or service account token).
        
        Args:
            project: Project reference in format "org_name/project_name"
        
        Returns:
            Dict with token, issued_at, expires_at, and project details including role
        
        Example:
            >>> client = AccessClient(identity_token="your_identity_token")
            >>> result = client.generate_access_token(project="hello_org/hello_project")
            >>> access_token = result["token"]
        """
        return self._make_request(
            "POST",
            "/projects/generate-project-token",
            {"project": project}
        )
    
    # ========================================================================
    # TOKEN UTILITIES
    # ========================================================================
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decode and display the contents of a JWT token.
        
        This is useful for debugging and displaying token information in notebooks.
        Shows token type (USER_TOKEN, USER_PROJECT_TOKEN, SERVICE_ACCOUNT_TOKEN),
        user information, project/role details, and expiration status.
        
        Args:
            token: JWT token to decode
        
        Returns:
            Dict with token_info containing:
                - token_type: Type of token
                - user_id: User ID
                - email: User email
                - issued_at: When token was issued
                - expires_at: When token expires
                - is_expired: Whether token has expired
                - project: (if PROJECT_TOKEN) Project details with id, name, role
                - service_account: (if SERVICE_ACCOUNT_TOKEN) Service account details
        
        Example:
            >>> client = AccessClient(identity_token="your_token")
            >>> info = client.decode_token(token="some_jwt_token")
            >>> print(info["token_info"]["token_type"])
            PROJECT_TOKEN
        """
        return self._make_request(
            "POST",
            "/tokens/decode",
            {"token": token}
        )
    
    # ========================================================================
    # AUDIT LOG
    # ========================================================================
    
    def get_audit_log(
        self,
        org: Optional[str] = None,
        project: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get audit log for an org or project.
        
        Args:
            org: Organization name (mutually exclusive with project)
            project: Project reference (mutually exclusive with org)
            limit: Maximum number of log entries to return
        
        Returns:
            List of audit log entries
        """
        params = {"limit": limit}
        if org:
            params["org"] = org
        if project:
            params["project"] = project
        
        result = self._make_request("GET", "/audit-log", params=params)
        return result.get("audit_logs", [])


# Convenience function to create an access client
def create_access_client(identity_token: str) -> AccessClient:
    """
    Create an access management client.
    
    Args:
        identity_token: JWT access token for authentication
    
    Returns:
        AccessClient instance
    """
    return AccessClient(identity_token)


# Standalone token decode function (doesn't require authentication)
def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and display the contents of a JWT token.
    
    This is a standalone function that doesn't require authentication.
    Useful for quickly inspecting tokens in notebooks.
    
    Args:
        token: JWT token to decode
    
    Returns:
        Dict with token_info containing type, user, project, role, and expiration details
    
    Example:
        >>> import featuremesh
        >>> info = featuremesh.decode_token(token="some_jwt_token")
        >>> print(f"Token type: {info['token_info']['token_type']}")
        >>> print(f"Expires at: {info['token_info']['expires_at']}")
    """
    import requests
    
    url = f"{get_default('access.host')}{get_default('access.path')}/tokens/decode"
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(
        url,
        headers=headers,
        json={"token": token},
        timeout=get_default("access.timeout"),
        verify=get_default("access.verify_ssl")
    )
    response.raise_for_status()
    return response.json()


# Convenience function to generate access token
def generate_access_token(identity_token: str, project: str) -> str:
    """
    Generate a project access token from an identity token.
    
    This is a convenience function that simplifies the common pattern of:
    1. Creating an AccessClient with an identity token
    2. Generating a project access token
    3. Extracting just the token string
    
    Args:
        identity_token: User identity JWT token for authentication
        project: Project reference in format "org_name/project_name"
    
    Returns:
        The project access token string
    
    Example:
        >>> import featuremesh
        >>> access_token = featuremesh.generate_access_token(
        ...     identity_token="your_identity_token",
        ...     project="hello_org/hello_project"
        ... )
        >>> # Use access_token with OfflineClient or OnlineClient
    """
    client_access = AccessClient(identity_token=identity_token)
    result = client_access.generate_access_token(project=project)
    
    if 'token' in result:
        return result['token']
    
    raise ValueError(f"Failed to generate access token: {result}")

