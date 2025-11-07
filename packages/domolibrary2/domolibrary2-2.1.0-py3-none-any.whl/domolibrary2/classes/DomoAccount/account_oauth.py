__all__ = [
    "DomoAccountOAuth_Config_SnowflakeOauth",
    "DomoAccountOAuth_Config_JiraOnPremOauth",
    "OAuthConfig",
    "DomoAccount_OAuth",
    # Route exceptions
    "Account_GET_Error",
    "Account_CRUD_Error",
    "AccountNoMatchError",
    "Account_Config_Error",
]

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import httpx

from ...auth import DomoAuth
from ...base.base import DomoEnumMixin
from ...routes import account as account_routes
from ...routes.account.exceptions import (
    Account_Config_Error,
    Account_CRUD_Error,
    Account_GET_Error,
    AccountNoMatchError,
)
from .access import DomoAccess_OAuth

# Import base account module directly to avoid package-level circular imports
from .account_default import DomoAccount_Default
from .config import DomoAccount_Config


@dataclass
class DomoAccountOAuth_Config_SnowflakeOauth(DomoAccount_Config):
    data_provider_type: str = "snowflake-oauth-config"
    is_oauth: bool = True

    client_id: str = None
    secret: str = None

    @classmethod
    def from_dict(cls, obj: dict, parent: Any = None, **kwargs):
        return cls(
            client_id=obj["client-id"],
            secret=obj["client-secret"],
            raw=obj,
            parent=parent,
        )

    def to_dict(self):
        return {"client-id": self.client_id, "client-secret": self.secret}


@dataclass
class DomoAccountOAuth_Config_JiraOnPremOauth(DomoAccount_Config):
    data_provider_type: str = "jira-on-prem-oauth-config"
    is_oauth: bool = True

    client_id: str = None
    secret: str = None

    @classmethod
    def from_dict(cls, obj: dict, parent: Any = None):
        return cls(
            client_id=obj["client_id"],
            secret=obj["client_secret"],
            raw=obj,
            parent=parent,
        )

    def to_dict(self):
        return {"client_id": self.client_id, "client_secret": self.secret}


class OAuthConfig(DomoEnumMixin, Enum):
    snowflake_oauth_config = DomoAccountOAuth_Config_SnowflakeOauth

    jira_on_prem_oauth_config = DomoAccountOAuth_Config_JiraOnPremOauth

    default = None


@dataclass
class DomoAccount_OAuth(DomoAccount_Default):
    Access: DomoAccess_OAuth = field(repr=False, default=None)

    def __post_init__(self):
        self.Access = DomoAccess_OAuth.from_parent(parent=self)

    async def _get_config(
        self,
        session=None,
        return_raw: bool = False,
        debug_api: bool = None,
        debug_num_stacks_to_drop=2,
        is_suppress_no_config: bool = True,
    ):
        """Retrieve OAuth account configuration.

        Internal method to fetch and parse OAuth account configuration.
        Can be used to suppress cases where the config is not defined, either
        because the account_config is OAuth and not stored in Domo, OR because
        the AccountConfig class doesn't cover the data_type.

        Args:
            session: HTTP client session (optional)
            return_raw: Return raw response without processing
            debug_api: Enable API debugging
            debug_num_stacks_to_drop: Stack frames to drop for debugging
            is_suppress_no_config: Suppress errors when config is not defined

        Returns:
            DomoAccount_Config: OAuth account configuration object

        Raises:
            Account_Config_Error: If configuration retrieval or parsing fails
        """
        if not self.data_provider_type:
            res = await account_routes.get_account_by_id(
                auth=self.auth,
                account_id=self.id,
                session=session,
                debug_api=debug_api,
                parent_class=self.__class__.__name__,
                debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            )

            self.data_provider_type = res.response["dataProviderType"]

        res = await account_routes.get_oauth_account_config(
            auth=self.auth,
            account_id=self.id,
            session=session,
            debug_api=debug_api,
            data_provider_type=self.data_provider_type,
            parent_class=self.__class__.__name__,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

        if return_raw:
            return res

        config: DomoAccount_Config = OAuthConfig(self.data_provider_type).value

        self.Config = config.from_dict(obj=res.response, parent=self)

        return self.Config

    @classmethod
    async def get_by_id(
        cls,
        auth: DomoAuth,
        account_id: int,
        is_suppress_no_config: bool = True,
        session: httpx.AsyncClient = None,
        return_raw: bool = False,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        **kwargs,
    ):
        """Retrieve OAuth account metadata and attempt to retrieve configuration.

        Args:
            auth: Authentication object for API requests
            account_id: ID of the OAuth account to retrieve
            is_suppress_no_config: Suppress errors when config is not defined
            session: HTTP client session (optional)
            return_raw: Return raw response without processing
            debug_api: Enable API debugging
            debug_num_stacks_to_drop: Stack frames to drop for debugging
            **kwargs: Additional arguments passed to from_dict

        Returns:
            DomoAccount_OAuth: OAuth account instance with configuration

        Raises:
            AccountNoMatchError: If OAuth account is not found
            Account_GET_Error: If OAuth account retrieval fails
            Account_Config_Error: If configuration retrieval fails
        """

        res = await account_routes.get_oauth_account_by_id(
            auth=auth,
            account_id=account_id,
            session=session,
            debug_api=debug_api,
            parent_class=cls.__name__,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

        if return_raw:
            return res

        acc = cls.from_dict(
            obj=res.response,
            auth=auth,
            is_admin_summary=False,
            is_use_default_account_class=False,
            new_cls=cls,
            **kwargs,
        )

        await acc._get_config(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
            is_suppress_no_config=is_suppress_no_config,
        )

        return acc

    @classmethod
    async def create(
        cls,
        auth: DomoAuth,
        account_name: str,
        oauth_config: OAuthConfig,
        origin: str = "OAUTH_CONFIGURATION",
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        debug_num_stacks_to_drop=2,
    ):
        """Create a new OAuth account.

        Args:
            auth: Authentication object for API requests
            account_name: Display name for the OAuth account
            oauth_config: OAuth configuration object (OAuthConfig enum member)
            origin: Origin type for the OAuth account (default: "OAUTH_CONFIGURATION")
            debug_api: Enable API debugging
            session: HTTP client session (optional)
            debug_num_stacks_to_drop: Stack frames to drop for debugging

        Returns:
            DomoAccount_OAuth instance with configuration loaded

        Raises:
            Account_CRUD_Error: If account creation fails
        """
        res = await account_routes.create_oauth_account(
            auth=auth,
            account_name=account_name,
            data_provider_type=oauth_config.data_provider_type,
            origin=origin,
            config=oauth_config.to_dict(),
            debug_api=debug_api,
            session=session,
            parent_class=cls.__name__,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

        return await cls.get_by_id(
            auth=auth,
            account_id=res.response["id"],
            debug_api=debug_api,
            session=session,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

    async def delete(
        self,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        session: httpx.AsyncClient = None,
    ):
        """Delete this OAuth account.

        Args:
            debug_api: Enable API debugging
            debug_num_stacks_to_drop: Stack frames to drop for debugging
            session: HTTP client session (optional)

        Returns:
            ResponseGetData object confirming deletion

        Raises:
            Account_CRUD_Error: If account deletion fails
        """
        return await account_routes.delete_oauth_account(
            auth=self.auth,
            account_id=self.id,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=self.__class__.__name__,
            session=session,
        )

    async def update_name(
        self,
        account_name: str,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        session: httpx.AsyncClient = None,
    ):
        """Update the name of this OAuth account.

        Args:
            account_name: New display name for the account
            debug_api: Enable API debugging
            debug_num_stacks_to_drop: Stack frames to drop for debugging
            session: HTTP client session (optional)

        Returns:
            Self (DomoAccount_OAuth) with updated name

        Raises:
            Account_CRUD_Error: If name update fails
        """
        await account_routes.update_oauth_account_name(
            auth=self.auth,
            account_id=self.id,
            account_name=account_name,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=self.__class__.__name__,
            session=session,
        )

        self.name = account_name
        return self

    async def update_config(
        self,
        oauth_config: OAuthConfig = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        session: httpx.AsyncClient = None,
    ):
        """Update the configuration of this OAuth account.

        Args:
            oauth_config: New OAuth configuration (defaults to current config if None)
            debug_api: Enable API debugging
            debug_num_stacks_to_drop: Stack frames to drop for debugging
            session: HTTP client session (optional)

        Returns:
            Self (DomoAccount_OAuth) with updated configuration

        Raises:
            Account_Config_Error: If configuration update fails
        """
        await account_routes.update_oauth_account_config(
            auth=self.auth,
            account_id=self.id,
            config_body=oauth_config.to_dict() or self.Config.to_dict(),
            data_provider_type=self.data_provider_type,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=self.__class__.__name__,
            session=session,
        )

        self.Config = oauth_config

        return self

    async def share(
        self,
        user_id: int = None,
        group_id: int = None,
        access_level=None,  # ShareAccount_AccessLevel
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        return_raw: bool = False,
    ):
        """Share this OAuth account with a user or group.

        Args:
            user_id: User ID to share with (mutually exclusive with group_id)
            group_id: Group ID to share with (mutually exclusive with user_id)
            access_level: Access level (ShareAccount_AccessLevel enum)
            session: HTTP client session (optional)
            debug_api: Enable API debugging
            return_raw: Return raw response without processing

        Returns:
            ResponseGetData if return_raw=True, else the updated account

        Raises:
            ValueError: If neither user_id nor group_id is provided
            Account_Share_Error: If sharing operation fails

        Example:
            >>> from domolibrary2.routes.account import ShareAccount_AccessLevel
            >>> account = await DomoAccount_OAuth.get_by_id(auth=auth, account_id=123)
            >>> await account.share(
            ...     user_id=456,
            ...     access_level=ShareAccount_AccessLevel.CAN_EDIT
            ... )
        """
        if not user_id and not group_id:
            raise ValueError("Must provide either user_id or group_id")

        if not access_level:
            from ...routes.account import ShareAccount_AccessLevel

            access_level = ShareAccount_AccessLevel.CAN_VIEW

        # Generate share payload
        share_payload = access_level.generate_payload(
            user_id=user_id, group_id=group_id
        )

        res = await account_routes.share_oauth_account(
            auth=self.auth,
            account_id=self.id,
            share_payload=share_payload,
            session=session,
            debug_api=debug_api,
            return_raw=return_raw,
        )

        if return_raw:
            return res

        # Refresh access list after sharing
        if self.Access:
            await self.get_access(force_refresh=True, session=session)

        return self

    async def get_access(
        self,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        force_refresh: bool = False,
        debug_num_stacks_to_drop: int = 2,
    ):
        """Retrieve the access list for this OAuth account.

        This method retrieves all users and groups that have access to this OAuth account
        along with their access levels.

        Args:
            session: HTTP client session (optional)
            debug_api: Enable API debugging
            force_refresh: If True, refresh even if Access relationships are already loaded
            debug_num_stacks_to_drop: Stack frames to drop for debugging

        Returns:
            List of Access_Relation objects representing users/groups with access

        Example:
            >>> account = await DomoAccount_OAuth.get_by_id(auth=auth, account_id=123)
            >>> access_list = await account.get_access()
            >>> for access in access_list:
            ...     print(f"{access.entity.name}: {access.relationship_type}")
        """
        if not force_refresh and self.Access.relationships:
            return self.Access.relationships

        return await self.Access.get(
            debug_api=debug_api,
            session=session,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )
