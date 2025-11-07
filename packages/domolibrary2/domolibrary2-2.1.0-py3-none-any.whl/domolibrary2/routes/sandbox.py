__all__ = [
    "Sandbox_GET_Error",
    "Sandbox_CRUD_Error",
    "get_is_allow_same_instance_promotion_enabled",
    "toggle_allow_same_instance_promotion",
    "get_shared_repos",
    "get_repo_from_id",
]

from typing import Optional

import httpx

from ..auth import DomoAuth
from ..base.exceptions import RouteError
from ..client import (
    get_data as gd,
    response as rgd,
)


class Sandbox_GET_Error(RouteError):
    """Raised when sandbox retrieval operations fail."""

    def __init__(
        self,
        repository_id: Optional[str] = None,
        message: Optional[str] = None,
        res=None,
        **kwargs,
    ):
        super().__init__(
            message=message or "Sandbox retrieval failed",
            entity_id=repository_id,
            res=res,
            **kwargs,
        )


class Sandbox_CRUD_Error(RouteError):
    """Raised when sandbox create, update, or delete operations fail."""

    def __init__(
        self,
        operation: str,
        repository_id: Optional[str] = None,
        message: Optional[str] = None,
        res=None,
        **kwargs,
    ):
        super().__init__(
            message=message or f"Sandbox {operation} operation failed",
            entity_id=repository_id,
            res=res,
            **kwargs,
        )


@gd.route_function
async def get_is_allow_same_instance_promotion_enabled(
    auth: DomoAuth,
    session: httpx.AsyncClient | None = None,
    return_raw: bool = False,
    debug_num_stacks_to_drop: int = 1,
    debug_api: bool = False,
    parent_class: Optional[str] = None,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/version/v1/settings"

    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Sandbox_GET_Error(res=res)

    res.response = {
        "name": "allow_same_instance_promotion",
        "is_enabled": res.response["allowSelfPromotion"],
    }

    return res


@gd.route_function
async def toggle_allow_same_instance_promotion(
    auth: DomoAuth,
    is_enabled: bool,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Toggle the allow same instance promotion setting.

    Args:
        auth: Authentication object
        is_enabled: Whether to enable same instance promotion
        session: Optional HTTP client session
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Parent class name for debugging
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object

    Raises:
        Sandbox_CRUD_Error: If the operation fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/version/v1/settings"

    body = {"allowSelfPromotion": is_enabled}

    res = await gd.get_data(
        auth=auth,
        method="POST",
        url=url,
        body=body,
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Sandbox_CRUD_Error(operation="toggle same instance promotion", res=res)

    return res


@gd.route_function
async def get_shared_repos(
    auth: DomoAuth,
    session: httpx.AsyncClient | None = None,
    return_raw: bool = False,
    parent_class: Optional[str] = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/version/v1/repositories/search"

    body = {
        "query": {
            "offset": 0,
            "limit": 50,
            "fieldSearchMap": {},
            "sort": "lastCommit",
            "order": "desc",
            "filters": {"userId": None},
            "dateFilters": {},
        },
        "shared": False,
    }

    def arr_fn(res: rgd.ResponseGetData) -> list[dict]:
        return res.response["repositories"]

    offset_params = {"offset": "offset", "limit": "limit"}

    def body_fn(skip, limit, body):
        body["query"].update({"offset": skip, "limit": limit})
        return body

    res = await gd.looper(
        auth=auth,
        method="POST",
        url=url,
        arr_fn=arr_fn,
        body_fn=body_fn,
        body=body,
        loop_until_end=True,
        offset_params=offset_params,
        offset_params_in_body=True,
        session=session,
        return_raw=return_raw,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Sandbox_GET_Error(res=res)

    return res


@gd.route_function
async def get_repo_from_id(
    auth: DomoAuth,
    repository_id: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Get a sandbox repository by ID.

    Args:
        auth: Authentication object
        repository_id: Repository identifier
        session: Optional HTTP client session
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Parent class name for debugging
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object

    Raises:
        Sandbox_GET_Error: If retrieval fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/version/v1/repositories/{repository_id}"

    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        parent_class=parent_class,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Sandbox_GET_Error(repository_id=repository_id, res=res)

    return res
