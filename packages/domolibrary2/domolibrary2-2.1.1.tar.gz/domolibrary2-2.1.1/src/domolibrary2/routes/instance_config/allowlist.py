__all__ = [
    "Config_GET_Error",
    "get_allowlist",
    "AllowlistUnableToUpdate",
    "set_allowlist",
    "get_allowlist_is_filter_all_traffic_enabled",
    "toggle_allowlist_is_filter_all_traffic_enabled",
]


from typing import Optional

import httpx

from ... import auth as dmda
from ...auth import DomoAuth
from ...base import exceptions as dmde
from ...client import (
    get_data as gd,
    response as rgd,
)
from ...utils.convert import convert_string_to_bool
from .exceptions import Config_GET_Error


class AllowlistUnableToUpdate(dmde.RouteError):
    def __init__(self, res: rgd.ResponseGetData, reason: str = "", message: str = ""):
        if reason:
            reason_str = f"unable to update allowlist: {reason}"
            if message:
                message += f" | {reason_str}"

        super().__init__(
            res=res,
            message=message,
        )


@gd.route_function
async def get_allowlist(
    auth: DomoAuth,
    session: httpx.AsyncClient | None = None,
    return_raw: bool = False,
    debug_api: bool = False,
    parent_class=None,
    debug_num_stacks_to_drop=1,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/admin/companysettings/whitelist"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        headers={"accept": "*/*"},
        session=session,
        debug_api=debug_api,
        is_follow_redirects=True,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Config_GET_Error(res=res)

    res.response = (
        res.response.get("addresses", []) if isinstance(res.response, dict) else []
    )

    if res.response == [""]:
        res.response = []

    return res


@gd.route_function
async def set_allowlist(
    auth: DomoAuth,
    ip_address_ls: list[str],
    debug_api: bool = False,
    return_raw: bool = False,
    session: httpx.AsyncClient | None = None,
    parent_class=None,
    debug_num_stacks_to_drop=1,
) -> rgd.ResponseGetData:
    """companysettings/whitelist API only allows users to SET the allowlist does not allow INSERT or UPDATE"""

    url = f"https://{auth.domo_instance}.domo.com/admin/companysettings/whitelist"

    body = {"addresses": ip_address_ls}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        debug_api=debug_api,
        is_follow_redirects=True,
        session=session,
        headers={"accept": "text/plain"},
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )
    if return_raw:
        return res

    if not res.is_success:
        raise AllowlistUnableToUpdate(res=res, reason=str(res.response))

    return res


@gd.route_function
async def get_allowlist_is_filter_all_traffic_enabled(
    auth: DomoAuth,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    return_raw: bool = False,
    parent_class: Optional[str] = None,
    debug_num_stacks_to_drop: int = 1,
) -> rgd.ResponseGetData:
    """this endpoint determines if ALL traffic is filtered through the allowlist or just browser traffic
    Admin > Company Settings > Security > IP Allowlist

    if True - all traffic is filtered
    if False - only browser traffic is filtered

    """

    url = f"https://{auth.domo_instance}.domo.com/api/customer/v1/properties/ip.whitelist.mobile.enabled"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        session=session,
        debug_api=debug_api,
        is_follow_redirects=True,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Config_GET_Error(res=res)

    res.response = {
        "is_enabled": (
            convert_string_to_bool(res.response.get("value", False))
            if isinstance(res.response, dict)
            else False
        ),
        "feature": "ip.whitelist.mobile.enabled",
    }

    return res


@gd.route_function
async def toggle_allowlist_is_filter_all_traffic_enabled(
    auth: dmda.DomoFullAuth,
    is_enabled: bool,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    return_raw: bool = False,
    parent_class: Optional[str] = None,
    debug_num_stacks_to_drop: int = 1,
) -> rgd.ResponseGetData:
    """this endpoint determines if ALL traffic is filtered through the allowlist or just browser traffic
    Admin > Company Settings > Security > IP Allowlist

    if True - all traffic is filtered
    if False - only browser traffic is filtered

    """

    url = f"https://{auth.domo_instance}.domo.com/api/customer/v1/properties/ip.whitelist.mobile.enabled"

    body = {"value": is_enabled}

    res = await gd.get_data(
        auth=auth,  # type: ignore[arg-type]
        url=url,
        method="PUT",
        body=body,
        session=session,
        debug_api=debug_api,
        is_follow_redirects=True,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if not res.is_success:
        raise AllowlistUnableToUpdate(res=res, reason=str(res.response))

    if return_raw:
        return res

    return await get_allowlist_is_filter_all_traffic_enabled(
        auth=auth,
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
    )
