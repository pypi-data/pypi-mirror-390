__all__ = [
    "RoleNotRetrievedError",
    "Role_CRUD_Error",
    "get_roles",
    "get_role_by_id",
    "get_role_grants",
    "get_role_membership",
    "create_role",
    "delete_role",
    "get_default_role",
    "set_default_role",
    "update_role_metadata",
    "set_role_grants",
    "role_membership_add_users",
]


import httpx

from ..auth import DomoAuth
from ..base.exceptions import RouteError
from ..client import (
    get_data as gd,
)
from ..client.response import ResponseGetData


class RoleNotRetrievedError(RouteError):
    def __init__(
        self,
        res: ResponseGetData,
        message=None,
    ):
        super().__init__(res=res, message=message)


# | export
class Role_CRUD_Error(RouteError):
    def __init__(
        self,
        res: ResponseGetData,
        message=None,
    ):
        super().__init__(res=res, message=message)


@gd.route_function
async def get_roles(
    auth: DomoAuth,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: str = None,
) -> ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/roles"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
    )

    if not res.is_success:
        raise RoleNotRetrievedError(res=res)

    return res


@gd.route_function
async def get_role_by_id(
    auth: DomoAuth,
    role_id: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop=1,
    parent_class: str = None,
) -> ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/roles/{role_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if not res.is_success:
        raise RoleNotRetrievedError(
            res=res,
        )

    return res


@gd.route_function
async def get_role_grants(
    auth: DomoAuth,
    role_id: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop=1,
    parent_class: str = None,
) -> ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/roles/{role_id}/authorities"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if len(res.response) == 0:
        role_res = await get_roles(auth=auth)

        domo_role = [role for role in role_res.response if role.get("id") == role_id]

        if not domo_role:
            raise RoleNotRetrievedError(
                res=res,
                message=f"role {role_id} does not exist",
            )

    return res


@gd.route_function
async def get_role_membership(
    auth: DomoAuth,
    role_id: str,
    session: httpx.AsyncClient | None = None,
    return_raw: bool = False,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: str = None,
) -> ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/roles/{role_id}/users"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if len(res.response.get("users")) == 0:
        role_res = await get_roles(auth)

        domo_role = next(
            (role for role in role_res.response if role.get("id") == role_id), None
        )

        if not domo_role:
            raise RoleNotRetrievedError(
                res=res,
                message=f"role {role_id} does not exist or cannot be retrieved",
            )

    if return_raw:
        return res

    res.response = res.response.get("users")

    return res


@gd.route_function
async def create_role(
    auth: DomoAuth,
    name: str,
    description: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: str = None,
) -> ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/roles"

    body = {"name": name, "description": description}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="POST",
        body=body,
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if not res.is_success:
        raise Role_CRUD_Error(res=res)

    return res


@gd.route_function
async def delete_role(
    auth: DomoAuth,
    role_id: int,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: str = None,
    return_raw: bool = False,
) -> ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/roles/{role_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="DELETE",
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if return_raw:
        return res

    if res.status == 400 and res.response == "Bad Request":
        print(
            " 😕 weird API issue, but role should have been deleted.  setting is_success = True \n"
        )
        res.is_success = True

    if not res.is_success:
        raise Role_CRUD_Error(
            res=res,
        )

    return res


@gd.route_function
async def get_default_role(
    auth,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: str = None,
):
    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/customer-states/user.roleid.default"

    params = {"defaultValue": 2, "ignoreCache": True}

    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        params=params,
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if not res.is_success:
        raise RoleNotRetrievedError(res=res)

    res.response = res.response.get("value")

    return res


@gd.route_function
async def set_default_role(
    auth: DomoAuth,
    role_id: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class=None,
) -> ResponseGetData:
    # url = f"https://{auth.domo_instance}.domo.com/api/content/v1/customer-states/user.roleid.default"
    # body = {"name": "user.roleid.default", "value": role_id}

    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/roles/settings"
    body = {"defaultRoleId": int(role_id), "allowlistRoleIds": None}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        debug_api=debug_api,
        body=body,
        session=session,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if not res.is_success:
        raise Role_CRUD_Error(res=res)

    return res


@gd.route_function
async def update_role_metadata(
    auth: DomoAuth,
    role_id,
    role_name,
    role_description: str = None,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: str = None,
    return_raw: bool = False,
):
    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/roles/{role_id}"

    body = {"name": role_name, "description": role_description, "id": role_id}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if return_raw:
        return res

    if res.status == 400 and res.response == "Bad Request":
        print(
            " 😕 weird API issue, but role should have been modified.  setting is_success = True \n"
        )
        res.is_success = True

    if not res.is_success:
        raise Role_CRUD_Error(res=res)

    return res


@gd.route_function
async def set_role_grants(
    auth: DomoAuth,
    role_id: str,
    grants: list[str],
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: str = None,
    return_raw: bool = False,
) -> ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/roles/{role_id}/authorities"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=grants,
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if res.status == 400 and res.response == "Bad Request":
        print(
            " 😕 weird API issue, but role should have been modified.  setting is_success = True \n"
        )
        res.is_success = True

    if not res.is_success:
        raise Role_CRUD_Error(res=res)

    return res


@gd.route_function
async def role_membership_add_users(
    auth: DomoAuth,
    role_id: str,
    user_ids: list[str],  # list of user ids
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: str = None,
) -> ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/roles/{role_id}/users"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=user_ids,
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if not res.is_success:
        raise Role_CRUD_Error(res=res)

    return res
