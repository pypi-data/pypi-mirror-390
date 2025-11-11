"""Project-level authentication client."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol

import requests

from .client import WowMySQLError


@dataclass
class AuthUser:
    """Represents an authenticated user."""

    id: str
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    email_verified: bool = False
    user_metadata: Dict[str, Any] = None
    app_metadata: Dict[str, Any] = None
    created_at: Optional[str] = None


@dataclass
class AuthSession:
    """Session tokens returned by the auth service."""

    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


@dataclass
class AuthResponse:
    """Response for signup/login requests."""

    session: AuthSession
    user: Optional[AuthUser] = None


class TokenStorage(Protocol):
    """Interface for persisting tokens."""

    def get_access_token(self) -> Optional[str]:
        ...

    def set_access_token(self, token: Optional[str]) -> None:
        ...

    def get_refresh_token(self) -> Optional[str]:
        ...

    def set_refresh_token(self, token: Optional[str]) -> None:
        ...


class MemoryTokenStorage:
    """Default in-memory token storage."""

    def __init__(self) -> None:
        self._access: Optional[str] = None
        self._refresh: Optional[str] = None

    def get_access_token(self) -> Optional[str]:
        return self._access

    def set_access_token(self, token: Optional[str]) -> None:
        self._access = token

    def get_refresh_token(self) -> Optional[str]:
        return self._refresh

    def set_refresh_token(self, token: Optional[str]) -> None:
        self._refresh = token


class ProjectAuthClient:
    """Client for project-level authentication endpoints."""

    def __init__(
        self,
        project_url: str,
        *,
        base_domain: str = "wowmysql.com",
        secure: bool = True,
        timeout: int = 30,
        verify_ssl: bool = True,
        public_api_key: Optional[str] = None,
        token_storage: Optional[TokenStorage] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.base_url = _build_auth_base_url(project_url, base_domain, secure)
        self.timeout = timeout
        self.public_api_key = public_api_key

        self.session = session or requests.Session()
        self.session.verify = verify_ssl
        self.session.headers.update({"Content-Type": "application/json"})
        if public_api_key:
            self.session.headers["X-Wow-Public-Key"] = public_api_key

        self.storage = token_storage or MemoryTokenStorage()
        self._access_token = self.storage.get_access_token()
        self._refresh_token = self.storage.get_refresh_token()

        if not verify_ssl:
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # -------------------------- Public API -------------------------- #

    def sign_up(
        self,
        *,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        user_metadata: Optional[Dict[str, Any]] = None,
    ) -> AuthResponse:
        payload = {
            "email": email,
            "password": password,
            "full_name": full_name,
            "user_metadata": user_metadata,
        }
        data = self._request("POST", "/signup", json=payload)
        session = self._persist_session(data)
        user = AuthUser(**_normalize_user(data.get("user"))) if data.get("user") else None
        return AuthResponse(session=session, user=user)

    def sign_in(self, *, email: str, password: str) -> AuthResponse:
        payload = {"email": email, "password": password}
        data = self._request("POST", "/login", json=payload)
        session = self._persist_session(data)
        return AuthResponse(session=session, user=None)

    def get_user(self, access_token: Optional[str] = None) -> AuthUser:
        token = access_token or self._access_token or self.storage.get_access_token()
        if not token:
            raise WowMySQLError("Access token is required. Call sign_in first.")

        data = self._request(
            "GET",
            "/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        return AuthUser(**_normalize_user(data))

    def get_oauth_authorization_url(
        self,
        provider: str,
        *,
        redirect_uri: str,
    ) -> Dict[str, str]:
        """
        Get OAuth authorization URL for the specified provider.
        
        Args:
            provider: OAuth provider name (e.g., 'github', 'google', 'facebook', 'microsoft')
            redirect_uri: The redirect URI where the OAuth provider will send the user after authorization.
                          Must match the redirect URI configured in the OAuth provider settings.
        
        Returns:
            Dict containing:
                - authorization_url: The URL to redirect the user to for OAuth authorization
                - provider: The provider name
                - redirect_uri: The redirect URI used
        
        Raises:
            WowMySQLError: If the request fails or the provider is not configured
        
        Example:
            >>> auth = ProjectAuthClient(project_url="myproject")
            >>> result = auth.get_oauth_authorization_url(
            ...     provider="github",
            ...     redirect_uri="http://localhost:5000/auth/github/callback"
            ... )
            >>> print(result["authorization_url"])
        """
        if not redirect_uri or not redirect_uri.strip():
            raise WowMySQLError("redirect_uri is required and cannot be empty")
        
        if not provider or not provider.strip():
            raise WowMySQLError("provider is required and cannot be empty")
        
        # Ensure redirect_uri is properly formatted
        redirect_uri = redirect_uri.strip()
        
        try:
            data = self._request(
                "GET",
                f"/oauth/{provider}",
                params={"redirect_uri": redirect_uri},
            )
            return {
                "authorization_url": data.get("authorization_url", ""),
                "provider": data.get("provider", provider),
                "redirect_uri": data.get("redirect_uri", redirect_uri),
            }
        except WowMySQLError as e:
            # Provide more helpful error messages
            if e.status_code == 502:
                raise WowMySQLError(
                    f"Bad Gateway (502): The backend server may be down or unreachable. "
                    f"Check if the backend is running and accessible at {self.base_url}",
                    status_code=502,
                    response=getattr(e, 'response', {})
                )
            elif e.status_code == 400:
                raise WowMySQLError(
                    f"Bad Request (400): {e}. "
                    f"Ensure OAuth provider '{provider}' is configured and enabled for this project.",
                    status_code=400,
                    response=getattr(e, 'response', {})
                )
            raise

    def exchange_oauth_callback(
        self,
        provider: str,
        *,
        code: str,
        redirect_uri: Optional[str] = None,
    ) -> AuthResponse:
        """
        Exchange OAuth callback code for access tokens.
        
        After the user authorizes with the OAuth provider, the provider redirects
        back with a code. Call this method to exchange that code for JWT tokens.
        
        Args:
            provider: OAuth provider name (e.g., 'github', 'google')
            code: Authorization code from OAuth provider callback
            redirect_uri: Optional redirect URI (uses configured one if not provided)
        
        Returns:
            AuthResponse with session tokens and user info
        """
        payload = {
            "code": code,
            "redirect_uri": redirect_uri,
        }
        data = self._request(
            "POST",
            f"/oauth/{provider}/callback",
            json=payload,
        )
        session = self._persist_session(data)
        user = AuthUser(**_normalize_user(data.get("user"))) if data.get("user") else None
        return AuthResponse(session=session, user=user)

    def forgot_password(self, *, email: str) -> Dict[str, Any]:
        """
        Request password reset.
        
        Sends a password reset email to the user if they exist.
        Always returns success to prevent email enumeration.
        
        Args:
            email: User's email address
        
        Returns:
            Dict with success status and message
        """
        payload = {"email": email}
        data = self._request("POST", "/forgot-password", json=payload)
        return {
            "success": data.get("success", True),
            "message": data.get("message", "If that email exists, a password reset link has been sent")
        }

    def reset_password(self, *, token: str, new_password: str) -> Dict[str, Any]:
        """
        Reset password with token.
        
        Validates the reset token and updates the user's password.
        
        Args:
            token: Password reset token from email
            new_password: New password (minimum 8 characters)
        
        Returns:
            Dict with success status and message
        """
        payload = {
            "token": token,
            "new_password": new_password
        }
        data = self._request("POST", "/reset-password", json=payload)
        return {
            "success": data.get("success", True),
            "message": data.get("message", "Password reset successfully! You can now login with your new password")
        }

    def get_session(self) -> Dict[str, Optional[str]]:
        return {
            "access_token": self._access_token or self.storage.get_access_token(),
            "refresh_token": self._refresh_token or self.storage.get_refresh_token(),
        }

    def set_session(self, *, access_token: str, refresh_token: Optional[str] = None) -> None:
        self._access_token = access_token
        self._refresh_token = refresh_token
        self.storage.set_access_token(access_token)
        self.storage.set_refresh_token(refresh_token)

    def clear_session(self) -> None:
        self._access_token = None
        self._refresh_token = None
        self.storage.set_access_token(None)
        self.storage.set_refresh_token(None)

    def close(self) -> None:
        self.session.close()

    # ------------------------- Internals ---------------------------- #

    def _persist_session(self, data: Dict[str, Any]) -> AuthSession:
        session = AuthSession(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            token_type=data.get("token_type", "bearer"),
            expires_in=data.get("expires_in", 0),
        )
        self._access_token = session.access_token
        self._refresh_token = session.refresh_token
        self.storage.set_access_token(session.access_token)
        self.storage.set_refresh_token(session.refresh_token)
        return session

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        request_headers = dict(headers or {})

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=json,
                params=params,
                headers=request_headers,
                timeout=self.timeout,
            )
        except requests.exceptions.SSLError as exc:
            raise WowMySQLError(
                f"SSL error: {str(exc)}. If using self-signed certificates, set verify_ssl=False",
                response={"error": str(exc)}
            )
        except requests.exceptions.ConnectionError as exc:
            raise WowMySQLError(
                f"Connection error: {str(exc)}. Check if the backend is running and the URL is correct.",
                response={"error": str(exc)}
            )
        except requests.exceptions.Timeout as exc:
            raise WowMySQLError(
                f"Request timeout: {str(exc)}. The server took too long to respond.",
                response={"error": str(exc)}
            )
        except requests.exceptions.RequestException as exc:
            raise WowMySQLError(
                f"Request failed: {str(exc)}",
                response={"error": str(exc)}
            )

        if response.status_code >= 400:
            try:
                payload = response.json()
            except ValueError:
                payload = {}
            message = (
                payload.get("detail")
                or payload.get("message")
                or payload.get("error")
                or f"Request failed with status {response.status_code}"
            )
            raise WowMySQLError(message, status_code=response.status_code, response=payload)

        if not response.content:
            return {}
        try:
            return response.json()
        except ValueError as exc:
            raise WowMySQLError(f"Failed to parse response: {exc}") from exc


def _build_auth_base_url(project_url: str, base_domain: str, secure: bool) -> str:
    normalized = project_url.strip()
    
    # If it's already a full URL, use it as-is
    if normalized.startswith("http://") or normalized.startswith("https://"):
        # Already a full URL, just normalize
        normalized = normalized.rstrip("/")
        if normalized.endswith("/api"):
            normalized = normalized[: -len("/api")]
        return f"{normalized}/api/auth"
    
    # If it already contains the base domain, don't append it again
    if f".{base_domain}" in normalized or normalized.endswith(base_domain):
        protocol = "https" if secure else "http"
        normalized = f"{protocol}://{normalized}"
    else:
        # Just a project slug, append domain
        protocol = "https" if secure else "http"
        normalized = f"{protocol}://{normalized}.{base_domain}"
    
    normalized = normalized.rstrip("/")
    if normalized.endswith("/api"):
        normalized = normalized[: -len("/api")]
    
    return f"{normalized}/api/auth"


def _normalize_user(user: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": user.get("id"),
        "email": user.get("email"),
        "full_name": user.get("full_name") or user.get("fullName"),
        "avatar_url": user.get("avatar_url") or user.get("avatarUrl"),
        "email_verified": bool(user.get("email_verified") or user.get("emailVerified")),
        "user_metadata": user.get("user_metadata") or user.get("userMetadata") or {},
        "app_metadata": user.get("app_metadata") or user.get("appMetadata") or {},
        "created_at": user.get("created_at") or user.get("createdAt"),
    }

