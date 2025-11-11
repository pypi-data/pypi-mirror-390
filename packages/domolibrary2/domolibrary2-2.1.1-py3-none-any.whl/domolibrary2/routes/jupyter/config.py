"""
Jupyter Configuration Functions

This module provides functions for managing Jupyter workspace configuration.
"""

__all__ = [
    "update_jupyter_workspace_config",
]

from typing import Optional

import httpx

from ...auth import DomoAuth
from ...client import (
    get_data as gd,
    response as rgd,
)
from .exceptions import Jupyter_CRUD_Error, SearchJupyterNotFoundError


@gd.route_function
async def update_jupyter_workspace_config(
    auth: DomoAuth,
    workspace_id: str,
    config: dict,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 2,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Update the configuration of a Jupyter workspace.

    Args:
        auth: Authentication object containing credentials and instance info
        workspace_id: Unique identifier for the workspace to configure
        config: Configuration dictionary to update the workspace with
        session: Optional httpx client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to drop in debug output
        parent_class: Optional parent class name for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing configuration update result

    Raises:
        Jupyter_CRUD_Error: If workspace configuration update fails
        SearchJupyterNotFoundError: If workspace doesn't exist
    """
    url = f"https://{auth.domo_instance}.domo.com/api/datascience/v1/workspaces/{workspace_id}"

    res = await gd.get_data(
        url=url,
        method="PUT",
        auth=auth,
        body=config,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
    )

    if return_raw:
        return res

    if res.status == 404:
        raise SearchJupyterNotFoundError(
            search_criteria=f"workspace_id: {workspace_id}", res=res
        )

    if not res.is_success:
        raise Jupyter_CRUD_Error(
            operation="update_config",
            workspace_id=workspace_id,
            message=f"Error updating workspace configuration for {workspace_id}",
            res=res,
        )

    return res
