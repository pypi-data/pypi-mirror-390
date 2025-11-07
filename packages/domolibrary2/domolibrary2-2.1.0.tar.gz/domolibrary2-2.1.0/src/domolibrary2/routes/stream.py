__all__ = [
    "Stream_GET_Error",
    "Stream_CRUD_Error",
    "get_streams",
    "get_stream_by_id",
    "update_stream",
    "create_stream",
    "execute_stream",
]

from typing import Optional

import httpx

from ..auth import DomoAuth
from ..base.exceptions import RouteError
from ..client import (
    get_data as gd,
    response as rgd,
)


class Stream_GET_Error(RouteError):
    """Raised when stream retrieval operations fail."""

    def __init__(
        self,
        stream_id: Optional[str] = None,
        message: Optional[str] = None,
        res=None,
        **kwargs,
    ):
        super().__init__(
            message=message or "Stream retrieval failed",
            entity_id=stream_id,
            res=res,
            **kwargs,
        )


class Stream_CRUD_Error(RouteError):
    """Raised when stream create, update, delete, or execute operations fail."""

    def __init__(
        self,
        operation: str,
        stream_id: Optional[str] = None,
        message: Optional[str] = None,
        res=None,
        **kwargs,
    ):
        super().__init__(
            message=message or f"Stream {operation} operation failed",
            entity_id=stream_id,
            res=res,
            **kwargs,
        )


@gd.route_function
async def get_streams(
    auth: DomoAuth,
    loop_until_end: bool = True,
    session: httpx.AsyncClient | None = None,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    debug_api: bool = False,
    debug_loop: bool = False,
    return_raw: bool = False,
    skip: int = 0,
    maximum: int = 1000,
) -> rgd.ResponseGetData:
    """
    streams do not appear to be recycled, not recommended for use as will return a virtually limitless number of streams
    instead use get_stream_by_id
    """

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/streams/"

    def arr_fn(res):
        return res.response

    res = await gd.looper(
        auth=auth,
        session=session,
        url=url,
        offset_params={"limit": "limit", "offset": "offet"},
        arr_fn=arr_fn,
        loop_until_end=loop_until_end,
        method="GET",
        offset_params_in_body=False,
        limit=500,
        skip=skip,
        maximum=maximum,
        debug_api=debug_api,
        debug_loop=debug_loop,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        return_raw=return_raw,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Stream_GET_Error(res=res)

    return res


@gd.route_function
async def get_stream_by_id(
    auth: DomoAuth,
    stream_id: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Get a stream by its ID.

    Args:
        auth: Authentication object
        stream_id: Unique stream identifier
        session: HTTP client session
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of the calling class
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object

    Raises:
        Stream_GET_Error: If retrieval fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/streams/{stream_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Stream_GET_Error(stream_id=stream_id, res=res)

    return res


@gd.route_function
async def update_stream(
    auth: DomoAuth,
    stream_id: str,
    body: dict,
    session: httpx.AsyncClient | None = None,
    debug_num_stacks_to_drop: int = 1,
    debug_api: bool = False,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Update a stream configuration.

    Args:
        auth: Authentication object
        stream_id: Unique stream identifier
        body: Stream configuration data
        session: HTTP client session
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        debug_api: Enable API debugging
        parent_class: Name of the calling class
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object

    Raises:
        Stream_CRUD_Error: If update operation fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/streams/{stream_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        body=body,
        method="PUT",
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Stream_CRUD_Error(operation="update", stream_id=stream_id, res=res)

    return res


@gd.route_function
async def create_stream(
    auth: DomoAuth,
    body: dict,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Create a new stream.

    Args:
        auth: Authentication object
        body: Stream configuration data
        session: HTTP client session
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of the calling class
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object

    Raises:
        Stream_CRUD_Error: If create operation fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/streams"

    res = await gd.get_data(
        auth=auth,
        url=url,
        body=body,
        method="POST",
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Stream_CRUD_Error(operation="create", res=res)

    return res


@gd.route_function
async def execute_stream(
    auth: DomoAuth,
    stream_id: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    parent_class: Optional[str] = None,
    debug_num_stacks_to_drop: int = 1,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Execute a stream to run data import.

    Args:
        auth: Authentication object
        stream_id: Unique stream identifier
        session: HTTP client session
        debug_api: Enable API debugging
        parent_class: Name of the calling class
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object

    Raises:
        Stream_CRUD_Error: If execute operation fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/streams/{stream_id}/executions"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="POST",
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Stream_CRUD_Error(operation="execute", stream_id=stream_id, res=res)

    return res
