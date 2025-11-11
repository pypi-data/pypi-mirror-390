"""
CodeEngine Core Route Functions

This module provides core functions for managing Domo CodeEngine packages including
retrieval and testing operations.

Functions:
    get_packages: Retrieve all codeengine packages
    get_codeengine_package_by_id: Retrieve a specific package by ID
    get_package_versions: Retrieve all versions of a package
    get_codeengine_package_by_id_and_version: Retrieve a specific package version
    test_package_is_released: Test if a package version is released
    test_package_is_identical: Test if package code is identical to existing

Enums:
    CodeEngine_Package_Parts: Enum for package parts parameter values
"""

__all__ = [
    "CodeEngine_Package_Parts",
    "get_packages",
    "get_codeengine_package_by_id",
    "get_package_versions",
    "get_codeengine_package_by_id_and_version",
    "test_package_is_released",
    "test_package_is_identical",
]

from enum import Enum
from typing import Optional

import httpx

from ...auth import DomoAuth
from ...base.base import DomoEnumMixin
from ...client import (
    get_data as gd,
    response as rgd,
)
from .exceptions import (
    CodeEngine_FunctionCallError,
    CodeEngine_GET_Error,
)


class CodeEngine_Package_Parts(DomoEnumMixin, Enum):
    """Enum for package parts parameter values."""

    VERSIONS = "versions"
    FUNCTIONS = "functions"
    CODE = "code"


@gd.route_function
async def get_packages(
    auth: DomoAuth,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Retrieve all codeengine packages.

    Args:
        auth: Authentication object
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of calling class for debugging
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object containing package list

    Raises:
        CodeEngine_GET_Error: If package retrieval fails
    """
    url = f"http://{auth.domo_instance}.domo.com/api/codeengine/v2/packages"

    res = await gd.get_data(
        url=url,
        auth=auth,
        method="get",
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
        parent_class=parent_class,
        is_follow_redirects=True,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise CodeEngine_GET_Error(res=res)

    return res


@gd.route_function
async def get_codeengine_package_by_id(
    auth: DomoAuth,
    package_id: str,
    params: Optional[dict] = None,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Retrieve a specific codeengine package by ID.

    Args:
        auth: Authentication object
        package_id: Package identifier
        params: Query parameters (optional, defaults to {"parts": "versions"})
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of calling class for debugging
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object containing package data

    Raises:
        CodeEngine_FunctionCallError: If package_id is not provided
        CodeEngine_GET_Error: If package retrieval fails
    """
    if not package_id:
        raise CodeEngine_FunctionCallError(
            message="Package ID must be provided.",
            auth=auth,
        )

    url = (
        f"https://{auth.domo_instance}.domo.com/api/codeengine/v2/packages/{package_id}"
    )

    params = params or {"parts": "versions"}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        params=params,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise CodeEngine_GET_Error(entity_id=package_id, res=res)

    return res


@gd.route_function
async def get_package_versions(
    auth: DomoAuth,
    package_id: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Retrieve all versions of a codeengine package.

    Each package can have one or many versions.

    Args:
        auth: Authentication object
        package_id: Package identifier
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of calling class for debugging
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object containing package versions

    Raises:
        CodeEngine_FunctionCallError: If package_id is not provided
        CodeEngine_GET_Error: If version retrieval fails
    """
    if not package_id:
        raise CodeEngine_FunctionCallError(
            message="Package ID must be provided.",
            auth=auth,
        )

    url = f"https://{auth.domo_instance}.domo.com/api/codeengine/v2/packages/{package_id}/versions/"

    params = {"parts": "functions,code"}

    res = await gd.get_data(
        url=url,
        method="get",
        auth=auth,
        params=params,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise CodeEngine_GET_Error(entity_id=package_id, res=res)

    return res


@gd.route_function
async def get_codeengine_package_by_id_and_version(
    auth: DomoAuth,
    package_id: str,
    version: str,
    params: Optional[dict] = None,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Retrieve a specific codeengine package by ID and version.

    Args:
        auth: Authentication object
        package_id: Package identifier
        version: Package version
        params: Query parameters (optional, defaults to {"parts": "functions,code"})
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of calling class for debugging
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object containing package version data

    Raises:
        CodeEngine_FunctionCallError: If package_id or version is not provided
        CodeEngine_GET_Error: If package retrieval fails
    """
    if not package_id or not version:
        raise CodeEngine_FunctionCallError(
            message=f"Package ID {package_id or 'not provided'} and version {version or 'not provided'} must be provided.",
            auth=auth,
        )

    url = f"https://{auth.domo_instance}.domo.com/api/codeengine/v2/packages/{package_id}/versions/{version}"

    params = params or {"parts": "functions,code"}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        params=params,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise CodeEngine_GET_Error(entity_id=f"{package_id}/v{version}", res=res)

    return res


async def test_package_is_released(
    package_id: str,
    version: str,
    auth: DomoAuth,
    existing_package=None,
    params: Optional[dict] = None,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
) -> bool:
    """
    Test if a package version is already released.

    Args:
        package_id: Package identifier
        version: Package version
        auth: Authentication object
        existing_package: Pre-fetched package data (optional)
        params: Query parameters (optional)
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of calling class for debugging

    Returns:
        True if the package is already released, False otherwise
    """
    existing_package = (
        existing_package
        or (
            await get_codeengine_package_by_id_and_version(
                auth=auth,
                package_id=package_id,
                version=version,
                params=params,
                debug_api=debug_api,
                session=session,
                parent_class=parent_class,
                debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            )
        ).response
    )

    return existing_package.get("released", False)


async def test_package_is_identical(
    package_id: str,
    version: str,
    auth: DomoAuth,
    existing_package=None,
    new_package=None,
    new_code=None,
    params: Optional[dict] = None,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
) -> bool:
    """
    Test if the code in a new package matches the existing package.

    Args:
        package_id: Package identifier
        version: Package version
        auth: Authentication object
        existing_package: Pre-fetched existing package data (optional)
        new_package: New package data to compare (optional)
        new_code: New code to compare (optional)
        params: Query parameters (optional)
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of calling class for debugging

    Returns:
        True if the package code is identical, False otherwise
    """
    existing_package = (
        existing_package
        or (
            await get_codeengine_package_by_id(
                auth=auth,
                package_id=package_id,
                params=params,
                debug_api=debug_api,
                session=session,
                parent_class=parent_class,
                debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            )
        ).response
    )

    new_code = new_code or (new_package.get("code") if new_package else None)

    return existing_package.get("code") == new_code
