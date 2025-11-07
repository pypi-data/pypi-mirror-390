"""
Instance Config API Client Route Functions

This module provides functions for managing Domo API clients (developer tokens)
including retrieval, creation, and revocation operations.

Functions:
    get_api_clients: Retrieve all API clients for the authenticated instance
    get_client_by_id: Retrieve a specific API client by ID
    create_api_client: Create a new API client with specified scopes
    revoke_api_client: Revoke an existing API client

Enums:
    ApiClient_ScopeEnum: Valid scopes for API client access
"""

import datetime as dt
from enum import Enum
from typing import Optional

import httpx

from domolibrary2.base.exceptions import RouteError

from ...auth import DomoAuth, DomoFullAuth
from ...base.base import DomoEnumMixin
from ...client import (
    get_data as gd,
    response as rgd,
)
from .exceptions import ApiClient_CRUD_Error, ApiClient_GET_Error, ApiClient_RevokeError


class ApiClient_ScopeEnum(DomoEnumMixin, Enum):
    """
    Valid scopes for API client access.

    Scopes define what resources and operations an API client can access.
    Multiple scopes can be assigned to a single API client.
    """

    DATA = "data"
    WORKFLOW = "workflow"
    AUDIT = "audit"
    BUZZ = "buzz"
    USER = "user"
    ACCOUNT = "account"
    DASHBOARD = "dashboard"


class InvalidAuthTypeError(RouteError):
    def __init__(self, res: rgd.ResponseGetData = None, message=None):
        super().__init__(res=res, message=message)


@gd.route_function
async def get_api_clients(
    auth: DomoAuth,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Retrieve all API clients (developer tokens) for the authenticated instance.

    Fetches a list of all API clients associated with the current Domo instance.
    Each client includes metadata such as name, description, scopes, and ID.

    Args:
        auth: Authentication object containing instance and credentials
        session: Optional HTTP client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to omit in debug output
        parent_class: Name of calling class for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing list of API clients

    Raises:
        ApiClient_GET_Error: If API client retrieval fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/identity/v1/developer-tokens"

    res = await gd.get_data(
        url=url,
        method="GET",
        auth=auth,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise ApiClient_GET_Error(res=res)

    # API response change 6/10/2025
    # res.response = res.response["entries"]

    return res


@gd.route_function
async def get_client_by_id(
    auth: DomoAuth,
    client_id: int,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Retrieve a specific API client by its ID.

    Fetches details of a single API client identified by the provided client_id.
    This function internally calls get_api_clients and filters the results.

    Args:
        auth: Authentication object containing instance and credentials
        client_id: Unique identifier for the API client
        session: Optional HTTP client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to omit in debug output
        parent_class: Name of calling class for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing the specific API client data

    Raises:
        ApiClient_GET_Error: If API client retrieval fails
        StopIteration: If no client with the specified ID is found
    """
    res = await get_api_clients(
        auth=auth,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
        session=session,
        parent_class=parent_class,
    )

    if return_raw:
        return res

    client = next(obj for obj in res.response if obj.get("id") == int(client_id))
    res.response = client
    return res


@gd.route_function
async def create_api_client(
    auth: DomoFullAuth,  # username and password (full) auth required for this API
    client_name: str,
    client_description: str = f"generated via DL {str(dt.date.today()).replace('-', '')}",
    scope: Optional[list[ApiClient_ScopeEnum]] = None,  # defaults to [data, audit]
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Create a new API client (developer token) with specified scopes.

    Creates a new API client with the provided name, description, and scopes.
    This operation requires DomoFullAuth (username and password authentication).

    Args:
        auth: DomoFullAuth object (username and password required)
        client_name: Name for the new API client
        client_description: Optional description for the API client
        scope: list of ApiClient_ScopeEnum values, defaults to [data, audit]
        session: Optional HTTP client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to omit in debug output
        parent_class: Name of calling class for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing the newly created API client data

    Raises:
        InvalidAuthTypeError: If auth is not DomoFullAuth
        ApiClient_CRUD_Error: If API client creation fails
    """
    if not isinstance(auth, DomoFullAuth):
        raise InvalidAuthTypeError(
            message=f"required auth type {DomoFullAuth.__class__.__name__}"
        )

    if scope and isinstance(scope, list) and isinstance(scope[0], ApiClient_ScopeEnum):
        scope = [sc.value for sc in scope]

    if not scope:
        scope = ["data", "audit"]

    url = "https://api.domo.com/clients"

    headers = {"X-DOMO-CustomerDomain": f"{auth.domo_instance}.domo.com"}

    res = await gd.get_data(
        url=url,
        method="POST",
        auth=auth,
        body={"name": client_name, "description": client_description, "scope": scope},
        headers=headers,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
    )

    if return_raw:
        return res

    if not res.is_success:
        if res.status == 400:
            raise ApiClient_CRUD_Error(
                operation="create",
                res=res,
                message=f"{res.response} -- does the client already exist?",
            )

        # if res.status == 403: # invalid auth type, but will be caught by the earlier test

        raise ApiClient_CRUD_Error(operation="create", res=res)

    return res


@gd.route_function
async def revoke_api_client(
    auth: DomoAuth,
    client_id: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Revoke (delete) an existing API client by its ID.

    Permanently revokes an API client, invalidating its credentials and
    preventing further API access.

    Args:
        auth: Authentication object containing instance and credentials
        client_id: Unique identifier for the API client to revoke
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
    url = f"https://{auth.domo_instance}.domo.com/api/identity/v1/developer-tokens/{client_id}"

    res = await gd.get_data(
        url=url,
        method="DELETE",
        auth=auth,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
    )

    if return_raw:
        return res

    if not res.is_success:
        if res.status == 400:
            raise ApiClient_RevokeError(
                client_id=client_id,
                res=res,
                message=f"Error revoking client {client_id}, validate that it exists.",
            )
        raise ApiClient_RevokeError(client_id=client_id, res=res)

    res.response = f"client {client_id} revoked"

    return res
