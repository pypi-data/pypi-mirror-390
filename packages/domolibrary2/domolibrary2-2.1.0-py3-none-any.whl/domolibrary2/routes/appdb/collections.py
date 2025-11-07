"""
AppDb Collection Functions

This module provides functions for managing Domo AppDb collections including
retrieval, creation, and permission management operations.

Functions:
    create_collection: Create a new collection in a datastore
    get_collections: Retrieve all collections
    get_collection_by_id: Retrieve a specific collection by ID
    modify_collection_permissions: Modify collection permissions

Enums:
    Collection_Permission_Enum: Permissions for collection access
"""

__all__ = [
    "create_collection",
    "get_collections",
    "get_collection_by_id",
    "modify_collection_permissions",
    "Collection_Permission_Enum",
]

from enum import Enum
from typing import Optional

import httpx

from ...auth import DomoAuth
from ...base.base import DomoEnumMixin
from ...client import (
    get_data as gd,
    response as rgd,
)
from .exceptions import AppDb_CRUD_Error, AppDb_GET_Error, SearchAppDb_NotFound


class Collection_Permission_Enum(DomoEnumMixin, Enum):
    READ_CONTENT = "READ_CONTENT"
    ADMIN = "ADMIN"
    UPDATE_CONTENT = "UPDATE_CONTENT"


@gd.route_function
async def create_collection(
    auth: DomoAuth,
    datastore_id: str,  # collections must be created inside a datastore which will show as the associated app_name
    collection_name: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Create a new collection in a datastore.

    Args:
        auth: Authentication object containing credentials and instance info
        datastore_id: Datastore ID where collection will be created
        collection_name: Name for the new collection
        session: Optional httpx client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to drop in debug output
        parent_class: Optional parent class name for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing created collection information

    Raises:
        AppDb_CRUD_Error: If collection creation fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/datastores/v1/{datastore_id}/collections"

    body = {"name": collection_name}

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
        raise AppDb_CRUD_Error(operation="create", appdb_id=datastore_id, res=res)

    return res


@gd.route_function
async def get_collections(
    auth: DomoAuth,
    datastore_id: Optional[str] = None,  # filters for a specific datastoreId
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Retrieve all collections, optionally filtered by datastore ID.

    Args:
        auth: Authentication object containing credentials and instance info
        datastore_id: Optional datastore ID to filter collections
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
    url = f"https://{auth.domo_instance}.domo.com/api/datastores/v1/collections/"

    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        params={"datastoreId": datastore_id},
        parent_class=parent_class,
        debug_api=debug_api,
        session=session,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success and res.status == 400:
        raise AppDb_GET_Error(
            appdb_id=datastore_id,
            message=f"invalid datastoreId - {datastore_id} or ensure it's shared with authenticated user",
            res=res,
        )

    if not res.is_success:
        raise AppDb_GET_Error(appdb_id=datastore_id, res=res)

    return res


@gd.route_function
async def get_collection_by_id(
    auth: DomoAuth,
    collection_id: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Retrieve a specific collection by ID.

    Args:
        auth: Authentication object containing credentials and instance info
        collection_id: Unique identifier for the collection
        session: Optional httpx client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to drop in debug output
        parent_class: Optional parent class name for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing collection information

    Raises:
        AppDb_GET_Error: If collection retrieval fails
        SearchAppDb_NotFound: If collection with specified ID doesn't exist
    """
    url = f"https://{auth.domo_instance}.domo.com/api/datastores/v1/collections/{collection_id}"

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
                search_criteria=f"collection_id: {collection_id}",
                res=res,
            )
        raise AppDb_GET_Error(appdb_id=collection_id, res=res)

    return res


@gd.route_function
async def modify_collection_permissions(
    auth: DomoAuth,
    collection_id: str,
    user_id: Optional[str] = None,
    group_id: Optional[str] = None,
    permission: Collection_Permission_Enum = Collection_Permission_Enum.READ_CONTENT,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Modify collection permissions for users or groups.

    Args:
        auth: Authentication object containing credentials and instance info
        collection_id: Unique identifier for the collection
        user_id: Optional user ID to grant permissions to
        group_id: Optional group ID to grant permissions to
        permission: Permission level to grant
        session: Optional httpx client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to drop in debug output
        parent_class: Optional parent class name for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing permission modification result

    Raises:
        AppDb_CRUD_Error: If permission modification fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/datastores/v1/collections/{collection_id}/permission/{'USER' if user_id else 'GROUP'}/{user_id or group_id}"

    params = {
        "overwrite": False,
        "permissions": (
            permission.value
            if isinstance(permission, Collection_Permission_Enum)
            else permission
        ),
    }

    res = await gd.get_data(
        auth=auth,
        method="PUT",
        params=params,
        url=url,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise AppDb_CRUD_Error(
            operation="modify permissions",
            appdb_id=collection_id,
            message=f"unable to set permissions for {user_id or group_id} to {permission.value if isinstance(permission, Collection_Permission_Enum) else permission} in collection {collection_id}",
            res=res,
        )

    res.response = f"set permissions for {user_id or group_id} to {permission.value if isinstance(permission, Collection_Permission_Enum) else permission} in collection {collection_id}"

    return res
