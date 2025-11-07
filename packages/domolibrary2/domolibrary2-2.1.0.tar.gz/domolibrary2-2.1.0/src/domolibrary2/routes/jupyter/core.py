"""
Jupyter Core Functions

This module provides core Jupyter workspace retrieval and management functions.
"""

__all__ = [
    "get_jupyter_workspaces",
    "get_jupyter_workspace_by_id",
    "start_jupyter_workspace",
    "parse_instance_service_location_and_prefix",
    "get_workspace_auth_token_params",
]

import urllib
from typing import Optional

import httpx

from ...auth import DomoAuth
from ...client import (
    get_data as gd,
    response as rgd,
)
from .exceptions import Jupyter_GET_Error, JupyterWorkspace_Error


@gd.route_function
async def get_jupyter_workspaces(
    auth: DomoAuth,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_loop: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Retrieve all available Jupyter workspaces.

    Args:
        auth: Authentication object containing credentials and instance info
        session: Optional httpx client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_loop: Enable detailed loop debugging
        debug_num_stacks_to_drop: Number of stack frames to drop in debug output
        parent_class: Optional parent class name for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing list of Jupyter workspaces

    Raises:
        Jupyter_GET_Error: If workspace retrieval fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/datascience/v1/search/workspaces"

    body = {
        "limit": 50,
        "offset": 0,
        "sortFieldMap": {"CREATED": "DESC"},
        "filters": [],
    }

    def arr_fn(res):
        return res.response["workspaces"]

    offset_params = {"limit": "limit", "offset": "offset"}

    res = await gd.looper(
        url=url,
        method="POST",
        limit=50,
        body=body,
        auth=auth,
        arr_fn=arr_fn,
        offset_params_in_body=True,
        offset_params=offset_params,
        parent_class=parent_class,
        session=session,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        debug_api=debug_api,
        debug_loop=debug_loop,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Jupyter_GET_Error(
            message="Failed to retrieve Jupyter workspaces", res=res
        )

    return res


@gd.route_function
async def get_jupyter_workspace_by_id(
    auth: DomoAuth,
    workspace_id: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 2,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Retrieve a specific Jupyter workspace by ID.

    Args:
        auth: Authentication object containing credentials and instance info
        workspace_id: Unique identifier for the workspace to retrieve
        session: Optional httpx client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to drop in debug output
        parent_class: Optional parent class name for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing workspace details

    Raises:
        Jupyter_GET_Error: If workspace retrieval fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/datascience/v1/workspaces/{workspace_id}"

    res = await gd.get_data(
        url=url,
        method="GET",
        auth=auth,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Jupyter_GET_Error(
            workspace_id=workspace_id,
            message=f"Failed to retrieve workspace {workspace_id}",
            res=res,
        )

    return res


def parse_instance_service_location_and_prefix(instance_dict, domo_instance):
    """Parse service location and prefix from instance dictionary."""
    url = instance_dict["url"]

    query = urllib.parse.unquote(urllib.parse.urlparse(url).query)
    query = urllib.parse.urlparse(query.split("&")[1].replace("next=", ""))

    return {
        "service_location": query.netloc.replace(domo_instance, "")[1:],
        "service_prefix": query.path,
    }


async def get_workspace_auth_token_params(workspace_id, auth, return_raw: bool = False):
    """
    params are needed for authenticating requests inside the workspace environment
    Note: you'll also need a internally generated jupyter_token to authenticate requests
    returns { service_location , service_prefix}
    """
    res = await get_jupyter_workspace_by_id(workspace_id=workspace_id, auth=auth)

    open_instances = res.response.get("instances")

    if return_raw:
        return open_instances

    if not open_instances:
        raise JupyterWorkspace_Error(
            operation="get_auth_token",
            workspace_id=workspace_id,
            message="There are no open instances. Do you need to start the workspace?",
            res=res,
        )

    return parse_instance_service_location_and_prefix(
        open_instances[0], auth.domo_instance
    )


@gd.route_function
async def start_jupyter_workspace(
    auth: DomoAuth,
    workspace_id: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Start a Jupyter workspace instance.

    Args:
        auth: Authentication object containing credentials and instance info
        workspace_id: Unique identifier for the workspace to start
        session: Optional httpx client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to drop in debug output
        parent_class: Optional parent class name for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing workspace start result

    Raises:
        JupyterWorkspace_Error: If workspace start operation fails
        Jupyter_GET_Error: If workspace retrieval fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/datascience/v1/workspaces/{workspace_id}/instances"

    try:
        res = await gd.get_data(
            url=url,
            method="POST",
            auth=auth,
            parent_class=parent_class,
            session=session,
            num_stacks_to_drop=debug_num_stacks_to_drop,
            debug_api=debug_api,
        )

        if return_raw:
            return res

    except RuntimeError as e:
        return rgd.ResponseGetData(
            status=500,
            response=f"starting workspace, please wait - {e}",
            is_success=False,
        )

    if res.status == 500 or res.status == 403:
        raise JupyterWorkspace_Error(
            operation="start",
            workspace_id=workspace_id,
            message=f"You may not have access to this workspace {workspace_id}, is it shared with you? Or may already be started",
            res=res,
        )

    if not res.is_success:
        raise JupyterWorkspace_Error(
            operation="start", workspace_id=workspace_id, res=res
        )

    res.response = "workspace started"
    return res
