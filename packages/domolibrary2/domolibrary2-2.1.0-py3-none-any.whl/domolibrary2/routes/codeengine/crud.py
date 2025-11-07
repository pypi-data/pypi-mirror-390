"""
CodeEngine CRUD Route Functions

This module provides CRUD functions for managing Domo CodeEngine packages including
creation, deployment, and update operations.

Functions:
    deploy_code_engine_package: Deploy a specific package version
    create_code_engine_package: Create a new codeengine package
    increment_version: Increment package version number
    upsert_code_engine_package_version: Create or update a package version
    upsert_package: Create or update a package

Classes:
    CodeEnginePackageBuilder: Helper class for building packages (placeholder)
"""

__all__ = [
    "CodeEnginePackageBuilder",
    "deploy_code_engine_package",
    "create_code_engine_package",
    "increment_version",
    "upsert_code_engine_package_version",
    "upsert_package",
]

from typing import Optional

import httpx

from ...auth import DomoAuth
from ...client import (
    get_data as gd,
    response as rgd,
)
from . import core as codeengine_routes
from .exceptions import (
    CodeEngine_CRUD_Error,
    CodeEngine_GET_Error,
    CodeEngine_InvalidPackage,
)


class CodeEnginePackageBuilder:
    """Helper class for building CodeEngine packages."""

    def __init__(self):
        pass


@gd.route_function
async def deploy_code_engine_package(
    auth: DomoAuth,
    package_id: str,
    version: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Deploy a specific codeengine package version.

    Args:
        auth: Authentication object
        package_id: Package identifier
        version: Package version to deploy
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of calling class for debugging
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object containing deployment result

    Raises:
        CodeEngine_CRUD_Error: If deployment fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/codeengine/v2/packages/{package_id}/versions/{version}/release"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="POST",
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise CodeEngine_CRUD_Error(
            operation="deploy", entity_id=f"{package_id}/v{version}", res=res
        )

    return res


@gd.route_function
async def create_code_engine_package(
    auth: DomoAuth,
    payload: dict,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Create a new codeengine package.

    Args:
        auth: Authentication object
        payload: Package data dictionary
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of calling class for debugging
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object containing created package data

    Raises:
        CodeEngine_CRUD_Error: If package creation fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/codeengine/v2/packages"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="POST",
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        body=payload,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise CodeEngine_CRUD_Error(operation="create", res=res)

    return res


def increment_version(version: str) -> str:
    """
    Increment the version number.

    Increments the last part of a dot-separated version string.

    Args:
        version: Version string (e.g., "1.0.0")

    Returns:
        Incremented version string (e.g., "1.0.1")
    """
    parts = version.split(".")
    # Increment the last part
    parts[-1] = str(int(parts[-1]) + 1)
    return ".".join(parts)


@gd.route_function
async def upsert_code_engine_package_version(
    auth: DomoAuth,
    payload: dict,
    version: Optional[str] = None,
    auto_increment_version: bool = True,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    debug_prn: bool = False,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Create or update a codeengine package version.

    If the package version exists and is released, optionally increment the version.
    If the package code is identical to existing, skip the update.

    Args:
        auth: Authentication object
        payload: Package data dictionary
        version: Package version (optional, defaults to version in payload)
        auto_increment_version: Automatically increment version if deployed
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of calling class for debugging
        debug_prn: Enable debug printing
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object containing package data

    Raises:
        CodeEngine_InvalidPackage: If package is already deployed and auto_increment is False
        CodeEngine_CRUD_Error: If package creation/update fails
    """
    package_id = payload.get("id")
    version = version or payload.get("version")

    try:
        existing_pkg = await codeengine_routes.get_codeengine_package_by_id_and_version(
            auth=auth,
            package_id=package_id,
            version=version,
            params={"parts": "code"},
            debug_api=debug_api,
            session=session,
            parent_class=parent_class,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )
        if await codeengine_routes.test_package_is_released(
            existing_package=existing_pkg.response,
            package_id=package_id,
            version=version,
            auth=auth,
        ):
            if not auto_increment_version:
                raise CodeEngine_InvalidPackage(
                    message=f"Package {package_id} v{version} already deployed",
                    auth=auth,
                )

            version = increment_version(version)

        if await codeengine_routes.test_package_is_identical(
            existing_package=existing_pkg.response,
            new_package=payload,
            package_id=package_id,
            version=version,
            auth=auth,
        ):
            if debug_prn:
                print(f"Package {package_id} v{version} is identical; skipping update.")
            return existing_pkg

    except CodeEngine_GET_Error:
        pass  # Not found, continue to create

    return await create_code_engine_package(
        auth=auth,
        payload=payload,
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        return_raw=return_raw,
    )


@gd.route_function
async def upsert_package(
    auth: DomoAuth,
    payload: dict,
    check_different: bool = True,
    create_new_version: bool = False,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    debug_prn: bool = False,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Create or update a codeengine package.

    If the package doesn't exist, create it. If it exists, update the version.

    Args:
        auth: Authentication object
        payload: Package data dictionary
        check_different: Check if package is different before updating
        create_new_version: Create a new version instead of updating existing
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of calling class for debugging
        debug_prn: Enable debug printing
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object containing package data

    Raises:
        CodeEngine_CRUD_Error: If package creation/update fails
    """
    package_id = payload.get("id")

    if not package_id:
        if debug_prn:
            print("No Package ID found, creating new package...")

        return await create_code_engine_package(
            auth=auth,
            payload=payload,
            debug_api=debug_api,
            session=session,
            parent_class=parent_class,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            return_raw=return_raw,
        )

    try:
        await codeengine_routes.get_codeengine_package_by_id(
            auth=auth,
            package_id=package_id,
            debug_api=debug_api,
            session=session,
            parent_class=parent_class,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )
    except CodeEngine_GET_Error:
        return await create_code_engine_package(
            auth=auth,
            payload=payload,
            debug_api=debug_api,
            session=session,
            parent_class=parent_class,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            return_raw=return_raw,
        )

    return await upsert_code_engine_package_version(
        payload=payload,
        auth=auth,
        auto_increment_version=True,
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        debug_prn=debug_prn,
        return_raw=return_raw,
    )
