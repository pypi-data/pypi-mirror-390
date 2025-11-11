"""Token-based authentication classes for Domo (access tokens)."""

from dataclasses import dataclass, field
from typing import Optional

import httpx
from dc_logger.decorators import LogDecoratorConfig, log_call

from ..base.exceptions import AuthError
from ..utils.logging import DomoEntityExtractor, DomoEntityResultProcessor
from .base import _DomoAuth_Optional, _DomoAuth_Required


class _DomoTokenAuth_Required(_DomoAuth_Required, _DomoAuth_Optional):  # noqa: N801
    """Mixin for required parameters for DomoTokenAuth.

    This class provides token-based authentication functionality using pre-generated
    access tokens from Domo's admin panel. This is useful in environments where
    direct username/password authentication is not permitted.

    Attributes:
        domo_access_token (str): Pre-generated access token from Domo admin panel
    """

    def __init__(
        self,
        domo_access_token: str,
        domo_instance: str,
        token_name: Optional[str] = None,
        token: Optional[str] = None,
        user_id: Optional[str] = None,
        is_valid_token: bool = False,
    ):
        """Initialize token authentication with pre-generated access token.

        Args:
            domo_access_token (str): Pre-generated access token from Domo admin panel
            domo_instance (str): The Domo instance identifier
            token_name (Optional[str]): Name identifier for the token
            token (Optional[str]): The authentication token (will be set to access token)
            user_id (Optional[str]): The authenticated user's ID
            is_valid_token (bool): Whether the current token is valid

        Raises:
            InvalidCredentialsError: If domo_access_token is empty
        """
        if not domo_access_token:
            raise AuthError(message="Domo access token is required.")
        self.domo_access_token = domo_access_token

        _DomoAuth_Required.__init__(self, domo_instance)
        _DomoAuth_Optional.__init__(
            self, domo_instance, token_name, token, user_id, is_valid_token
        )

    @property
    def auth_header(self) -> dict:
        """Generate the authentication header for access token based authentication.

        Returns:
            dict: HTTP headers with 'x-domo-developer-token' containing the access token
        """
        return {"x-domo-developer-token": self.token or self.domo_access_token}

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
        token_name: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Retrieve the access token, updating internal attributes as necessary.

        For token authentication, this method validates the token by calling who_am_i
        if no user_id is set, then returns the access token.

        Args:
            session (httpx.AsyncClient | None): HTTP client session to use
            debug_api (bool): Whether to enable API debugging
            debug_num_stacks_to_drop (int): Number of stack frames to drop for debugging
            token_name (Optional[str]): Override token name for display purposes
            **kwargs: Additional keyword arguments

        Returns:
            str: The access token
        """

        if not self.user_id:
            await self.who_am_i(
                session=session,
                debug_api=debug_api,
                debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
            )

        self.token = self.domo_access_token
        self.is_valid_token = True

        if token_name:
            self.token_name = token_name

        return self.token


@dataclass
class DomoTokenAuth(_DomoTokenAuth_Required):
    """Token-based authentication using pre-generated access tokens.

    This authentication method uses access tokens generated from Domo's admin panel
    (Admin > Access Tokens). This is particularly useful in environments where
    direct username/password authentication is not permitted or for automated systems.

    Attributes:
        domo_access_token (str): Pre-generated access token (not shown in repr)
        domo_instance (str): The Domo instance identifier
        token_name (Optional[str]): Name identifier for the token
        token (Optional[str]): The authentication token (not shown in repr)
        user_id (Optional[str]): The authenticated user's ID
        is_valid_token (bool): Whether the current token is valid

    Example:
        >>> auth = DomoTokenAuth(
        ...     domo_access_token="your-access-token-here",
        ...     domo_instance="mycompany"
        ... )
        >>> token = await auth.get_auth_token()
    """

    domo_access_token: str = field(repr=False)
    domo_instance: str

    token_name: Optional[str] = None
    token: Optional[str] = field(default=None, repr=False)
    user_id: Optional[str] = None
    is_valid_token: bool = False

    def __post_init__(self):
        """Initialize the authentication after dataclass creation."""
        self.token = self.domo_access_token

        if not self.token:
            raise AuthError(message="Domo access token is required.")

        _DomoTokenAuth_Required.__init__(
            self,
            domo_access_token=self.domo_access_token,
            domo_instance=self.domo_instance,
            token_name=self.token_name,
            token=self.token,
            user_id=self.user_id,
            is_valid_token=self.is_valid_token,
        )
