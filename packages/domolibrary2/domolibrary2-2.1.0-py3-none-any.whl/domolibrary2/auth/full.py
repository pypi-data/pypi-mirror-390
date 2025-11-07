"""Full authentication classes for Domo (username/password)."""

from dataclasses import dataclass, field
from typing import Optional, Union

import httpx
from dc_logger.decorators import LogDecoratorConfig, log_call

from ..base.exceptions import AuthError
from ..client.response import ResponseGetData
from ..utils.logging import DomoEntityExtractor, DomoEntityResultProcessor
from .base import _DomoAuth_Optional, _DomoAuth_Required


class _DomoFullAuth_Required(_DomoAuth_Required, _DomoAuth_Optional):  # noqa: N801
    """Mixin for required parameters for DomoFullAuth.

    This class provides full authentication functionality using username and password
    credentials to obtain session tokens from Domo's product APIs.

    Attributes:
        domo_username (str): Domo username for authentication
        domo_password (str): Domo password for authentication
    """

    def __init__(
        self,
        domo_username: str,
        domo_password: str,
        domo_instance: str,
        token_name: Optional[str] = None,
        token: Optional[str] = None,
        user_id: Optional[str] = None,
        is_valid_token: bool = False,
    ):
        """Initialize full authentication with username and password.

        Args:
            domo_username (str): Domo username for authentication
            domo_password (str): Domo password for authentication
            domo_instance (str): The Domo instance identifier
            token_name (Optional[str]): Name identifier for the token
            token (Optional[str]): Pre-existing authentication token
            user_id (Optional[str]): The authenticated user's ID
            is_valid_token (bool): Whether the current token is valid

        Raises:
            InvalidCredentialsError: If username or password is empty
            InvalidInstanceError: If domo_instance is empty
        """
        if not domo_username:
            raise AuthError(message="Domo username is required.")
        if not domo_password:
            raise AuthError(message="Domo password is required.")

        if not domo_instance:
            raise AuthError(message="Domo instance is required.")

        self.domo_username = domo_username
        self.domo_password = domo_password

        _DomoAuth_Required.__init__(self, domo_instance)
        _DomoAuth_Optional.__init__(
            self, domo_instance, token_name, token, user_id, is_valid_token
        )

    @property
    def auth_header(self) -> dict:
        """Generate the full authentication header specific to product APIs.

        Returns:
            dict: HTTP headers with 'x-domo-authentication' token, or empty dict if no token
        """
        return {"x-domo-authentication": self.token} if self.token else {}

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
        return_raw: bool = False,
        **kwargs,
    ) -> Union[str, ResponseGetData]:
        """Retrieve the authentication token from product APIs using the provided credentials.

        This method authenticates with Domo using username and password to obtain
        a session token that can be used for subsequent API calls.

        Args:
            session (httpx.AsyncClient | None): HTTP client session to use
            debug_api (bool): Whether to enable API debugging
            debug_num_stacks_to_drop (int): Number of stack frames to drop for debugging
            return_raw (bool): Whether to return raw ResponseGetData instead of token string
            **kwargs: Additional keyword arguments

        Returns:
            Union[str, ResponseGetData]: Authentication token string or raw response data

        Raises:
            InvalidCredentialsError: If authentication fails or no token is returned
        """
        from ...routes import auth as auth_routes

        res = await auth_routes.get_full_auth(
            auth=None,
            domo_instance=self.domo_instance,
            domo_username=self.domo_username,
            domo_password=self.domo_password,
            session=session,
            debug_api=debug_api,
            parent_class=self.__class__.__name__,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

        if return_raw:
            return res

        if res.is_success and res.response:
            self.is_valid_token = True

            token = str(res.response.get("sessionToken", ""))
            self.token = token
            self.token_name = self.token_name or "full_auth"

        if not self.token:
            raise AuthError(message="Failed to retrieve authentication token")

        return self.token


@dataclass
class DomoFullAuth(
    _DomoFullAuth_Required,
):
    """Full authentication using Domo username and password.

    This class provides authentication using Domo credentials (username and password)
    to obtain session tokens. It's typically used for direct user authentication
    where username/password login is permitted.

    Attributes:
        domo_instance (str): The Domo instance identifier
        domo_username (str): Domo username for authentication
        domo_password (str): Domo password for authentication (not shown in repr)
        token_name (Optional[str]): Name identifier for the token
        token (Optional[str]): The authentication token (not shown in repr)
        user_id (Optional[str]): The authenticated user's ID
        is_valid_token (bool): Whether the current token is valid

    Example:
        >>> auth = DomoFullAuth(
        ...     domo_instance="mycompany",
        ...     domo_username="user@company.com",
        ...     domo_password="secure_password"
        ... )
        >>> token = await auth.get_auth_token()
    """

    domo_instance: str
    domo_username: str
    domo_password: str = field(repr=False)
    token_name: Optional[str] = None
    token: Optional[str] = field(default=None, repr=False)
    user_id: Optional[str] = None
    is_valid_token: bool = False

    def __post_init__(self):
        """Initialize the authentication mixins after dataclass creation."""
        _DomoFullAuth_Required.__init__(
            self,
            domo_username=self.domo_username,
            domo_password=self.domo_password,
            domo_instance=self.domo_instance,
            token_name=self.token_name,
            token=self.token,
            user_id=self.user_id,
            is_valid_token=self.is_valid_token,
        )
