"""Developer authentication classes for Domo (OAuth2 client credentials)."""

from dataclasses import dataclass, field
from typing import Optional

import httpx
from dc_logger.decorators import LogDecoratorConfig, log_call

from ..base.exceptions import AuthError
from ..client.response import ResponseGetData
from ..utils.logging import DomoEntityExtractor, DomoEntityResultProcessor
from .base import _DomoAuth_Optional, _DomoAuth_Required


@dataclass
class DomoDeveloperAuth(_DomoAuth_Optional, _DomoAuth_Required):
    """Developer authentication using client credentials.

    This authentication method uses OAuth2 client credentials (client ID and secret)
    to obtain bearer tokens. This is typically used for applications built on
    Domo's developer platform and requires developer app registration.

    Attributes:
        domo_client_id (str): OAuth2 client ID from developer app registration
        domo_client_secret (str): OAuth2 client secret (not shown in repr)
        domo_instance (str): The Domo instance identifier
        token_name (Optional[str]): Name identifier for the token
        token (Optional[str]): The bearer token (not shown in repr)
        user_id (Optional[str]): The authenticated user's ID
        is_valid_token (bool): Whether the current token is valid

    Example:
        >>> auth = DomoDeveloperAuth(
        ...     domo_client_id="your-client-id",
        ...     domo_client_secret="your-client-secret",
        ...     domo_instance="mycompany"
        ... )
        >>> token = await auth.get_auth_token()
    """

    domo_client_id: str
    domo_client_secret: str = field(repr=False)
    domo_instance: str

    token_name: Optional[str] = None
    token: Optional[str] = field(default=None, repr=False)
    user_id: Optional[str] = None
    is_valid_token: bool = False

    def __post_init__(self):
        """Initialize the authentication after dataclass creation."""
        _DomoAuth_Optional.__init__(
            self,
            domo_instance=self.domo_instance,
            token_name=self.token_name,
            token=self.token,
            user_id=self.user_id,
            is_valid_token=self.is_valid_token,
        )
        _DomoAuth_Required.__init__(self, domo_instance=self.domo_instance)

    @property
    def auth_header(self) -> dict:
        """Generate the authentication header for developer token authentication.

        Returns:
            dict: HTTP headers with 'Authorization' bearer token, or empty dict if no token
        """
        if self.token:
            return {"Authorization": f"bearer {self.token}"}
        return {}

    @log_call(
        level_name="auth",
        config=LogDecoratorConfig(
            entity_extractor=DomoEntityExtractor(),
            result_processor=DomoEntityResultProcessor(),
        ),
    )
    async def get_auth_token(
        self,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        **kwargs,
    ) -> str:
        """Retrieve the developer token using client credentials and update internal attributes.

        This method uses OAuth2 client credentials flow to obtain a bearer token
        from Domo's developer authentication endpoint.

        Args:
            session (httpx.AsyncClient | None): HTTP client session to use
            debug_api (bool): Whether to enable API debugging
            debug_num_stacks_to_drop (int): Number of stack frames to drop for debugging
            **kwargs: Additional keyword arguments

        Returns:
            str: The bearer token for API authentication

        Raises:
            InvalidCredentialsError: If authentication fails or no token is returned
        """

        from ...routes import auth as auth_routes

        res = await auth_routes.get_developer_auth(
            auth=None,
            domo_client_id=self.domo_client_id,
            domo_client_secret=self.domo_client_secret,
            session=session,
            debug_api=debug_api,
            parent_class=self.__class__.__name__,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
        )

        if isinstance(res, ResponseGetData) and res.is_success and res.response:
            self.is_valid_token = True
            self.token = str(
                res.response.get("access_token", "")
                if isinstance(res.response, dict)
                else ""
            )
            self.user_id = (
                res.response.get("userId") if isinstance(res.response, dict) else ""
            )
            self.domo_instance = (
                res.response.get("domain", self.domo_instance)
                if isinstance(res.response, dict)
                else ""
            )
            self.token_name = self.token_name or "developer_auth"
            return self.token

        raise AuthError(message="Failed to retrieve developer token")
