"""
Page CRUD Functions

This module provides functions for managing page properties including
layout management, write locks, and ownership.

Functions:
    update_page_layout: Update page layout configuration
    put_writelock: Set write lock on a page layout
    delete_writelock: Remove write lock from a page layout

"""

__all__ = [
    "update_page_layout",
    "put_writelock",
    "delete_writelock",
]

from typing import Optional

import httpx
from dc_logger.decorators import LogDecoratorConfig, log_call

from ...auth import DomoAuth
from ...client import (
    get_data as gd,
    response as rgd,
)
from ...utils.logging import DomoEntityExtractor, DomoEntityResultProcessor
from .exceptions import Page_CRUD_Error


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def update_page_layout(
    auth: DomoAuth,
    layout_id: str,
    body: dict,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Update page layout configuration.

    Args:
        auth: Authentication object containing credentials and instance info
        layout_id: Unique identifier for the page layout
        body: Layout configuration data
        session: Optional httpx client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to drop in debug output
        parent_class: Optional parent class name for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing update result

    Raises:
        Page_CRUD_Error: If layout update fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/content/v4/pages/layouts/{layout_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        body=body,
        method="PUT",
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Page_CRUD_Error(
            operation="update",
            page_id=layout_id,
            message=f"Unable to update layout {layout_id}",
            res=res,
        )

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def put_writelock(
    auth: DomoAuth,
    layout_id: str,
    user_id: str,
    epoch_time: int,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Set write lock on a page layout.

    Args:
        auth: Authentication object containing credentials and instance info
        layout_id: Unique identifier for the page layout
        user_id: ID of the user acquiring the lock
        epoch_time: Timestamp for lock acquisition
        session: Optional httpx client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to drop in debug output
        parent_class: Optional parent class name for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing lock operation result

    Raises:
        Page_CRUD_Error: If write lock operation fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/content/v4/pages/layouts/{layout_id}/writelock"
    body = {
        "layoutId": layout_id,
        "lockHeartbeat": epoch_time,
        "lockTimestamp": epoch_time,
        "userId": user_id,
    }

    res = await gd.get_data(
        auth=auth,
        url=url,
        body=body,
        method="PUT",
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Page_CRUD_Error(
            operation="set writelock",
            page_id=layout_id,
            message=f"Unable to set writelock on layout {layout_id}",
            res=res,
        )

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def delete_writelock(
    auth: DomoAuth,
    layout_id: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Remove write lock from a page layout.

    Args:
        auth: Authentication object containing credentials and instance info
        layout_id: Unique identifier for the page layout
        session: Optional httpx client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to drop in debug output
        parent_class: Optional parent class name for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing unlock operation result

    Raises:
        Page_CRUD_Error: If write lock removal fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/content/v4/pages/layouts/{layout_id}/writelock"
    res = await gd.get_data(
        auth=auth,
        url=url,
        method="DELETE",
        debug_api=debug_api,
        session=session,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Page_CRUD_Error(
            operation="remove writelock",
            page_id=layout_id,
            message=f"Unable to remove writelock from layout {layout_id}",
            res=res,
        )

    return res
