__all__ = [
    "ApiClient",
    "SearchApiClientNotFoundError",
    "ApiClient_GET_Error",
    "ApiClient_CRUD_Error",
]

import datetime as dt
from dataclasses import dataclass, field
from typing import Any, Optional, Union

import httpx

from ...auth import DomoAuth
from ...base.entities import DomoEntity, DomoManager
from ...base.exceptions import DomoError
from ...client import response as rgd
from ...routes.instance_config.api_client import (
    ApiClient_ScopeEnum,
    create_api_client,
    get_api_clients,
    get_client_by_id,
    revoke_api_client,
)
from ...routes.instance_config.exceptions import (
    ApiClient_CRUD_Error,
    ApiClient_GET_Error,
    SearchApiClientNotFoundError,
)
from ...utils import chunk_execution as dmce
from ..DomoUser import DomoUser


@dataclass(eq=False)
class ApiClient(DomoEntity):
    id: str
    name: str
    client_id: str  # will be masked in UI
    client_secret: str
    owner: DomoUser

    # authorization_grant_types: list[str] # no longer part of API 6/10/2025

    scopes: list[ApiClient_ScopeEnum]
    description: Optional[str] = None

    @property
    def display_url(self) -> str:
        return f"https://{self.auth.domo_instance}.domo.com/admin/api-clients"

    @staticmethod
    async def get_user_by_id(
        user_id: str, auth: DomoAuth
    ) -> Union[DomoUser, bool, None]:
        try:
            return await DomoUser.get_by_id(auth=auth, id=user_id)
        except DomoError:
            return False

    @property
    def is_valid(self) -> bool:
        return bool(self.owner)

    @classmethod
    def from_dict(cls, auth: DomoAuth, obj: dict[str, Any]):
        return cls(
            auth=auth,
            id=obj["id"],
            raw=obj,
            name=obj["name"],
            client_id=obj["clientId"],
            owner=obj.get("owner"),  # type: ignore
            # authorization_grant_types=obj["authorizedGrantTypes"],
            scopes=[ApiClient_ScopeEnum[sc.upper()] for sc in obj["scopes"]],
            description=obj.get("description"),
            Relations=None,  # type: ignore
        )

    @classmethod
    async def get_by_id(
        cls,
        auth: DomoAuth,
        id: str,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        parent_class: Optional[str] = None,
        return_raw: bool = False,
    ) -> "ApiClient":
        """
        Retrieve a specific API client by its ID.

        Args:
            auth: Authentication object containing instance and credentials
            id: Unique identifier for the API client
            session: Optional HTTP client session for connection reuse
            debug_api: Enable detailed API request/response logging
            debug_num_stacks_to_drop: Number of stack frames to omit in debug output
            parent_class: Name of calling class for debugging context
            return_raw: Return raw API response without processing

        Returns:
            ResponseGetData object or ApiClient instance

        Raises:
            ApiClient_GET_Error: If API client retrieval fails
        """
        res = await get_client_by_id(
            auth=auth,
            id=id,
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=parent_class or cls.__name__,
            return_raw=return_raw,
        )

        if return_raw:
            return res

        obj = res.response

        owner = await cls.get_user_by_id(user_id=obj["userId"], auth=auth)
        obj["owner"] = owner

        return cls.from_dict(auth=auth, obj=obj)

    async def revoke(
        self,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        parent_class: Optional[str] = None,
        return_raw: bool = False,
    ) -> rgd.ResponseGetData:
        """
        Revoke (delete) this API client.

        Args:
            session: Optional HTTP client session for connection reuse
            debug_api: Enable detailed API request/response logging
            debug_num_stacks_to_drop: Number of stack frames to omit in debug output
            parent_class: Name of calling class for debugging context
            return_raw: Return raw API response without processing

        Returns:
            ResponseGetData object with confirmation message

        Raises:
            ApiClient_RevokeError: If API client revocation fails
        """
        return await revoke_api_client(
            auth=self.auth,
            client_id=str(self.id),
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=parent_class or self.__class__.__name__,
            return_raw=return_raw,
        )


@dataclass
class ApiClients(DomoManager):
    auth: DomoAuth

    domo_clients: list[ApiClient] = field(default_factory=lambda: [])

    invalid_clients: list[ApiClient] = field(default_factory=lambda: [])

    parent: Any = None

    @classmethod
    def from_parent(cls, auth: DomoAuth, parent: Any):  # DomoUser
        return cls(auth=auth, parent=parent)

    async def get(
        self,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        parent_class: Optional[str] = None,
        return_raw: bool = False,
    ) -> list[ApiClient] | rgd.ResponseGetData:
        """
        Retrieve all API clients for the authenticated instance.

        Args:
            session: Optional HTTP client session for connection reuse
            debug_api: Enable detailed API request/response logging
            debug_num_stacks_to_drop: Number of stack frames to omit in debug output
            parent_class: Name of calling class for debugging context
            return_raw: Return raw API response without processing

        Returns:
            ResponseGetData object or list of ApiClient instances

        Raises:
            ApiClient_GET_Error: If API client retrieval fails
        """
        res = await get_api_clients(
            auth=self.auth,
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=parent_class or self.__class__.__name__,
            return_raw=return_raw,
        )

        if return_raw:
            return res

        self.domo_clients = await dmce.gather_with_concurrency(
            *[
                ApiClient.get_by_id(auth=self.auth, id=obj["id"])
                for obj in res.response
            ],
            n=10,
        )

        if self.parent:
            self.domo_clients = [
                client for client in self.domo_clients if client.owner == self.parent
            ]

        self.invalid_clients = [
            client for client in self.domo_clients if not client.is_valid
        ]

        return self.domo_clients

    async def get_by_name(
        self,
        client_name: str,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        parent_class: Optional[str] = None,
    ) -> ApiClient:
        """
        Retrieve an API client by its name.

        Args:
            client_name: Name of the API client to find
            session: Optional HTTP client session for connection reuse
            debug_api: Enable detailed API request/response logging
            debug_num_stacks_to_drop: Number of stack frames to omit in debug output
            parent_class: Name of calling class for debugging context

        Returns:
            ApiClient instance matching the specified name

        Raises:
            SearchApiClient_NotFound: If no client with the specified name is found
            ApiClient_GET_Error: If API client retrieval fails
        """
        await self.get(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
            parent_class=parent_class or self.__class__.__name__,
        )

        domo_client = next(
            (
                _domo_client
                for _domo_client in self.domo_clients
                if _domo_client.name == client_name
            ),
            None,
        )

        if not domo_client:
            raise SearchApiClientNotFoundError(
                search_criteria=f"client name: {client_name}"
            )

        return domo_client

    async def create_for_authorized_user(
        self,
        client_name: str,
        client_description: str = f"created via DL {dt.date.today()}",
        scope: Optional[list[ApiClient_ScopeEnum]] = None,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        parent_class: Optional[str] = None,
        return_raw: bool = False,
    ) -> ApiClient:
        """
        Create a new API client for the authenticated user.

        Args:
            client_name: Name for the new API client
            client_description: Optional description for the API client
            scope: list of ApiClient_ScopeEnum values, defaults to [data, audit]
            session: Optional HTTP client session for connection reuse
            debug_api: Enable detailed API request/response logging
            debug_num_stacks_to_drop: Number of stack frames to omit in debug output
            parent_class: Name of calling class for debugging context
            return_raw: Return raw API response without processing

        Returns:
            ResponseGetData object or ApiClient instance with credentials

        Raises:
            ApiClient_CRUD_Error: If API client creation fails
            SearchApiClient_NotFound: If created client cannot be retrieved
        """
        res = await create_api_client(
            auth=self.auth,
            client_name=client_name,
            client_description=client_description,
            scope=scope,
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=parent_class or self.__class__.__name__,
            return_raw=return_raw,
        )

        if return_raw:
            return res

        domo_client = await self.get_by_name(
            client_name=client_name,
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=parent_class or self.__class__.__name__,
        )
        domo_client.client_id = res.response["client_id"]
        domo_client.client_secret = res.response["client_secret"]

        return domo_client

    async def upsert_client(
        self,
        client_name: str,
        client_description: Optional[str] = None,
        scope: Optional[list[ApiClient_ScopeEnum]] = None,
        is_regenerate: bool = False,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        parent_class: Optional[str] = None,
    ) -> ApiClient:
        """
        Create or update an API client (upsert operation).

        Args:
            client_name: Name of the API client to create or update
            client_description: Optional description for the API client
            scope: list of ApiClient_ScopeEnum values, defaults to [data, audit]
            is_regenerate: If True, revoke existing client and create new one
            session: Optional HTTP client session for connection reuse
            debug_api: Enable detailed API request/response logging
            debug_num_stacks_to_drop: Number of stack frames to omit in debug output
            parent_class: Name of calling class for debugging context

        Returns:
            ApiClient instance (existing or newly created)

        Raises:
            ApiClient_CRUD_Error: If API client creation or revocation fails
        """
        domo_client = None

        try:
            domo_client = await self.get_by_name(
                client_name=client_name,
                session=session,
                debug_api=debug_api,
                debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
                parent_class=parent_class or self.__class__.__name__,
            )

        except SearchApiClientNotFoundError:
            pass

        if domo_client:
            if not is_regenerate:
                return domo_client

            await domo_client.revoke(
                session=session,
                debug_api=debug_api,
                debug_num_stacks_to_drop=debug_num_stacks_to_drop,
                parent_class=parent_class or self.__class__.__name__,
            )

        return await self.create_for_authorized_user(
            client_name=client_name,
            client_description=client_description or "",
            scope=scope,
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=parent_class or self.__class__.__name__,
        )
