__all__ = ["Grant_GET_Error", "get_grants"]

from typing import Optional

import httpx

from ..auth import DomoAuth
from ..base.exceptions import RouteError
from ..client import (
    get_data as gd,
    response as rgd,
)


class Grant_GET_Error(RouteError):
    """Raised when grant retrieval operations fail."""

    def __init__(self, message: Optional[str] = None, res=None, **kwargs):
        super().__init__(
            message=message or "Grant retrieval failed",
            res=res,
            **kwargs,
        )


@gd.route_function
async def get_grants(
    auth: DomoAuth,
    debug_api: bool = False,
    session: httpx.AsyncClient | None = None,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/authorities"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        session=session,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if not res.is_success:
        raise Grant_GET_Error(res=res)

    if len(res.response) == 0:
        raise Grant_GET_Error(
            message=f"{len(res.response)} grants returned",
            res=res,
        )

    return res
