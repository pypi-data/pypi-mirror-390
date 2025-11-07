"""routes for interacting with the activity log"""

__all__ = [
    "ActivityLog_GET_Error",
    "get_activity_log_object_types",
    "search_activity_log",
]

from typing import Optional

import httpx

from ..auth import DomoAuth
from ..base.exceptions import RouteError
from ..client import (
    get_data as gd,
    response as rgd,
)


class ActivityLog_GET_Error(RouteError):
    """Raised when activity log retrieval operations fail."""

    def __init__(self, message: Optional[str] = None, res=None, **kwargs):
        super().__init__(
            message=message or "Activity log retrieval failed",
            res=res,
            **kwargs,
        )


@gd.route_function
async def get_activity_log_object_types(
    auth: DomoAuth,
    parent_class: Optional[str] = None,
    debug_num_stacks_to_drop: int = 1,
    debug_api: bool = False,
    session: httpx.AsyncClient | None = None,
) -> rgd.ResponseGetData:
    """retrieves a list of valid objectTypes that can be used to search the activity_log API"""

    url = f"https://{auth.domo_instance}.domo.com/api/audit/v1/user-audits/objectTypes"

    res = await gd.get_data(
        url=url,
        method="GET",
        auth=auth,
        parent_class=parent_class,
        debug_api=debug_api,
        session=session,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if not res.is_success:
        raise ActivityLog_GET_Error(
            message="Failed to get activity log object types", res=res
        )

    return res


@gd.route_function
async def search_activity_log(
    auth: DomoAuth,
    start_time: int,  # epoch time in milliseconds
    end_time: int,  # epoch time in milliseconds
    maximum: Optional[int] = None,
    object_type: Optional[str] = None,
    debug_api: bool = False,
    debug_loop: bool = False,
    parent_class: Optional[str] = None,
    debug_num_stacks_to_drop: int = 1,
    session: httpx.AsyncClient | None = None,
) -> rgd.ResponseGetData:
    """loops over activity log api to retrieve audit logs"""

    is_close_session = False

    if not session:
        session = httpx.AsyncClient()
        is_close_session = True

    url = f"https://{auth.domo_instance}.domo.com/api/audit/v1/user-audits"

    if object_type and object_type != "ACTIVITY_LOG":
        url = f"{url}/objectTypes/{object_type}"

    fixed_params = {"end": end_time, "start": start_time}

    offset_params = {
        "offset": "offset",
        "limit": "limit",
    }

    def arr_fn(res) -> list[dict]:
        return res.response

    res = await gd.looper(
        auth=auth,
        method="GET",
        url=url,
        arr_fn=arr_fn,
        fixed_params=fixed_params,
        offset_params=offset_params,
        session=session,
        maximum=maximum,
        limit=1000,
        debug_loop=debug_loop,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if not res.is_success:
        raise ActivityLog_GET_Error(res=res)

    if is_close_session:
        await session.aclose()

    return res
