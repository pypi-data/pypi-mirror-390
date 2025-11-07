"""
AppDb Datastore Functions

This module provides functions for managing Domo AppDb datastores including
retrieval and creation operations.

Functions:
    get_datastores: Retrieve all datastores
    get_datastore_by_id: Retrieve a specific datastore by ID
    get_collections_from_datastore: Get collections from a specific datastore
    create_datastore: Create a new datastore
"""

__all__ = [
    "get_datastores",
    "get_datastore_by_id",
    "get_collections_from_datastore",
    "create_datastore",
]

from typing import Optional

import httpx

from ...auth import DomoAuth
from ...client import (
    get_data as gd,
    response as rgd,
)
from .exceptions import AppDb_CRUD_Error, AppDb_GET_Error, SearchAppDb_NotFound


@gd.route_function
async def get_datastores(
    auth: DomoAuth,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Retrieve all datastores.

    Args:
        auth: Authentication object containing credentials and instance info
        session: Optional httpx client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to drop in debug output
        parent_class: Optional parent class name for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing datastores information

    Raises:
        AppDb_GET_Error: If datastores retrieval fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/datastores/v1/"

    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        parent_class=parent_class,
        debug_api=debug_api,
        session=session,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise AppDb_GET_Error(res=res)

    return res


@gd.route_function
async def get_datastore_by_id(
    auth: DomoAuth,
    datastore_id: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Retrieve a specific datastore by ID.

    Args:
        auth: Authentication object containing credentials and instance info
        datastore_id: Unique identifier for the datastore
        session: Optional httpx client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to drop in debug output
        parent_class: Optional parent class name for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing datastore information

    Raises:
        AppDb_GET_Error: If datastore retrieval fails
        SearchAppDb_NotFound: If datastore with specified ID doesn't exist
    """
    url = f"https://{auth.domo_instance}.domo.com/api/datastores/v1/{datastore_id}"

    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        parent_class=parent_class,
        debug_api=debug_api,
        session=session,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        if res.status == 404:
            raise SearchAppDb_NotFound(
                search_criteria=f"datastore_id: {datastore_id}",
                res=res,
            )
        raise AppDb_GET_Error(appdb_id=datastore_id, res=res)

    return res


@gd.route_function
async def get_collections_from_datastore(
    auth: DomoAuth,
    datastore_id: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Get collections from a specific datastore.

    Args:
        auth: Authentication object containing credentials and instance info
        datastore_id: Unique identifier for the datastore
        session: Optional httpx client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to drop in debug output
        parent_class: Optional parent class name for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing collections information

    Raises:
        AppDb_GET_Error: If collections retrieval fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/datastores/v1/{datastore_id}/collections"

    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        parent_class=parent_class,
        debug_api=debug_api,
        session=session,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise AppDb_GET_Error(appdb_id=datastore_id, res=res)

    return res


@gd.route_function
async def create_datastore(
    auth: DomoAuth,
    datastore_name: Optional[str] = None,  # in UI shows up as appName
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Create a new datastore.

    Args:
        auth: Authentication object containing credentials and instance info
        datastore_name: Name for the new datastore (shows as appName in UI)
        session: Optional httpx client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to drop in debug output
        parent_class: Optional parent class name for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing created datastore information

    Raises:
        AppDb_CRUD_Error: If datastore creation fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/datastores/v1/"

    body = {"name": datastore_name}

    res = await gd.get_data(
        auth=auth,
        method="POST",
        url=url,
        body=body,
        parent_class=parent_class,
        debug_api=debug_api,
        session=session,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise AppDb_CRUD_Error(operation="create", res=res)

    return res
