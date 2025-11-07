__all__ = [
    "Bootstrap_GET_Error",
    "get_bootstrap",
    "get_bootstrap_customerid",
    "get_bootstrap_features",
    "get_bootstrap_features_is_accountsv2_enabled",
    "get_bootstrap_pages",
]

from typing import Optional

import httpx

from ..auth import DomoAuth, DomoFullAuth
from ..base.exceptions import RouteError
from ..client import (
    get_data as gd,
    response as rgd,
)


class Bootstrap_GET_Error(RouteError):
    """Raised when bootstrap retrieval operations fail."""

    def __init__(self, message: Optional[str] = None, res=None, **kwargs):
        super().__init__(
            message=message or "Bootstrap retrieval failed",
            res=res,
            **kwargs,
        )


@gd.route_function
async def get_bootstrap(
    auth: DomoFullAuth,  ## only works with DomoFullAuth authentication, do not use TokenAuth
    debug_api: bool = False,
    session: httpx.AsyncClient | None = None,
    parent_class: Optional[str] = None,
    debug_num_stacks_to_drop: int = 1,
) -> rgd.ResponseGetData:
    """get bootstrap data"""

    # Import here to avoid circular imports
    from ..client import auth as dmda

    dmda.test_is_full_auth(auth, num_stacks_to_drop=2)

    # url = f"https://{auth.domo_instance}.domo.com/api/domoweb/bootstrap?v2Navigation=false"
    url = (
        f"https://{auth.domo_instance}.domo.com/api/domoweb/bootstrap?v2Navigation=true"
    )

    res = await gd.get_data(
        url=url,
        method="GET",
        auth=auth,
        debug_api=debug_api,
        session=session,
        is_follow_redirects=True,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if not res.is_success:
        raise Bootstrap_GET_Error(res=res)

    if res.response == "":
        raise Bootstrap_GET_Error(
            message="BSR_Features:  no features returned - is there a VPN?",
            res=res,
        )

    return res


@gd.route_function
async def get_bootstrap_customerid(
    auth: DomoFullAuth,  # this function requires the DomoFullAuth object to authenticate the bootstrap
    session: Optional[
        httpx.AsyncClient
    ] = None,  # optional parameter to improve same instance query performance
    debug_api: bool = False,  # pass True to see the parameters sent to the Domo API
    return_raw: bool = False,  # pass True to return the raw API response
    debug_num_stacks_to_drop: int = 2,  # number frames to drop off the stacktrace.  retrieved from `res.traceback_details`
    parent_class: Optional[
        str
    ] = None,  # Optional parent class that calls the route function
) -> (
    rgd.ResponseGetData
):  # the response contains the string representation of the customer_id
    """retrieves the domo_instance customer id"""

    res = await get_bootstrap(
        auth=auth,
        session=session,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if return_raw:
        return res

    res.response = res.response.get("currentUser").get("USER_GROUP")
    return res


@gd.route_function
async def get_bootstrap_features(
    auth: DomoFullAuth,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    return_raw: bool = False,
    debug_num_stacks_to_drop: int = 2,
    parent_class: Optional[str] = None,
) -> rgd.ResponseGetData:
    res = await get_bootstrap(
        auth=auth,
        session=session,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if return_raw:
        return res

    res.response = res.response.get("data").get("features")
    return res


@gd.route_function
async def get_bootstrap_features_is_accountsv2_enabled(
    auth: DomoAuth,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    return_raw: bool = False,
    debug_num_stacks_to_drop: int = 2,
    parent_class: Optional[str] = None,
) -> rgd.ResponseGetData:
    res = await get_bootstrap_features(
        auth=auth,
        session=session,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        return_raw=False,
    )

    if return_raw:
        return res

    match_accounts_v2 = next(
        (
            domo_feature
            for domo_feature in res.response
            if domo_feature.get("name") == "accounts-v2"
        ),
        None,
    )

    res.response = True if match_accounts_v2 else False
    return res


@gd.route_function
async def get_bootstrap_pages(
    auth: DomoFullAuth,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    return_raw: bool = False,
    debug_num_stacks_to_drop: int = 2,
    parent_class: Optional[str] = None,
) -> rgd.ResponseGetData:
    """this API will return the downstream (children) hierarchy of a page"""
    res = await get_bootstrap(
        auth=auth,
        session=session,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if return_raw:
        return res

    res.response = res.response.get("data").get("pages")
    return res
