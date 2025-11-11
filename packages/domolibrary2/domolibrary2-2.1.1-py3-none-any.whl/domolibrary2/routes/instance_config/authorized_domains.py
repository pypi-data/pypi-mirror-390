__all__ = [
    "GetDomainsNotFoundError",
    "GetAppDomainsNotFoundError",
    "get_authorized_domains",
    "set_authorized_domains",
    "get_authorized_custom_app_domains",
    "set_authorized_custom_app_domains",
]


import httpx

from ...auth import DomoAuth
from ...client import (
    get_data as gd,
    response as rgd,
)
from .. import user as user_routes
from .exceptions import Config_CRUD_Error, Config_GET_Error


class GetDomainsNotFoundError(Config_GET_Error):
    def __init__(self, res: rgd.ResponseGetData, message: str = ""):
        super().__init__(res=res, message=message)


class GetAppDomainsNotFoundError(Config_GET_Error):
    def __init__(self, res: rgd.ResponseGetData, message: str = ""):
        super().__init__(res=res, message=message)


@gd.route_function
async def get_authorized_domains(
    auth: DomoAuth,
    return_raw: bool = False,
    debug_api: bool = False,
    session: httpx.AsyncClient | None = None,
    parent_class=None,
    debug_num_stacks_to_drop=1,
):
    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/customer-states/authorized-domains"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    # domo raises a 404 error even if the success is valid but there are no approved domains
    if res.status == 404 and res.response == "Not Found":
        res_test = await user_routes.get_all_users(auth=auth)

        if not res_test.is_success:
            raise GetDomainsNotFoundError(res=res)

        if res_test.is_success:
            res.status = 200
            res.is_success = True
            res.response = []

        return res

    if not res.is_success:
        raise GetDomainsNotFoundError(res=res)

    res.response = [domain.strip() for domain in res.response.get("value").split(",")]  # type: ignore
    return res


@gd.route_function
async def set_authorized_domains(
    auth: DomoAuth,
    authorized_domain_ls: list[str],
    debug_api: bool = False,
    session: httpx.AsyncClient | None = None,
    parent_class=None,
    debug_num_stacks_to_drop=1,
):
    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/customer-states/authorized-domains"

    body = {"name": "authorized-domains", "value": ",".join(authorized_domain_ls)}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if not res.is_success:
        raise Config_CRUD_Error(res=res)

    return await get_authorized_domains(
        auth=auth,
        debug_api=debug_api,
        session=session,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )


@gd.route_function
async def get_authorized_custom_app_domains(
    auth: DomoAuth,
    return_raw: bool = False,
    debug_api: bool = False,
    session: httpx.AsyncClient | None = None,
    parent_class=None,
    debug_num_stacks_to_drop=1,
):
    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/customer-states/authorized-app-domains"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    # domo raises a 404 error even if the success is valid but there are no approved domains
    if res.status == 404 and res.response == "Not Found":
        res_test = await user_routes.get_all_users(auth=auth)

        if not res_test.is_success:
            raise GetAppDomainsNotFoundError(res=res)

        if res_test.is_success:
            res.status = 200
            res.is_success = True
            res.response = []

        return res

    if not res.is_success:
        raise GetAppDomainsNotFoundError(res=res)

    res.response = [domain.strip() for domain in res.response.get("value").split(",")]  # type: ignore
    return res


@gd.route_function
async def set_authorized_custom_app_domains(
    auth: DomoAuth,
    authorized_custom_app_domain_ls: list[str],
    debug_api: bool = False,
    session: httpx.AsyncClient | None = None,
    parent_class=None,
    debug_num_stacks_to_drop=1,
):
    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/customer-states/authorized-app-domains"

    body = {
        "name": "authorized-app-domains",
        "value": ",".join(authorized_custom_app_domain_ls),
    }

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if not res.is_success:
        raise Config_CRUD_Error(res=res)

    return await get_authorized_custom_app_domains(
        auth=auth,
        debug_api=debug_api,
        parent_class=parent_class,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
    )
