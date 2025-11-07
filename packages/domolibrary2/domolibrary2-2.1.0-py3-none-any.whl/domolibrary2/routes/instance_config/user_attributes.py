"""
User Attributes Management Routes

This module provides functionality for managing user attributes in Domo instances.
User attributes can be of different issuer types: IDP, system-defined, or custom.

Functions:
    get_user_attributes: Retrieve all user attributes
    get_user_attribute_by_id: Retrieve specific user attribute by ID
    clean_attribute_id: Clean attribute ID for creation
    generate_create_user_attribute_body: Generate body for attribute creation
    create_user_attribute: Create new user attribute
    update_user_attribute: Update existing user attribute
    delete_user_attribute: Delete user attribute

Exception Classes:
    UserAttributes_GET_Error: Raised when user attribute retrieval fails
    UserAttributes_CRUD_Error: Raised when user attribute create/update/delete fails

Enums:
    UserAttributes_IssuerType: Types of attribute issuers (IDP, SYSTEM, CUSTOM)
"""

__all__ = [
    "UserAttributes_IssuerType",
    "get_user_attributes",
    "get_user_attribute_by_id",
    "clean_attribute_id",
    "generate_create_user_attribute_body",
    "create_user_attribute",
    "update_user_attribute",
    "delete_user_attribute",
]

import datetime as dt
import re
from enum import Enum
from typing import Optional

import httpx

from ...auth import DomoAuth
from ...base.base import DomoEnumMixin
from ...client import (
    get_data as gd,
    response as rgd,
)
from ..user.exceptions import UserAttributes_CRUD_Error, UserAttributes_GET_Error


class UserAttributes_IssuerType(DomoEnumMixin, Enum):
    """Types of user attribute issuers."""

    IDP = "idp"
    SYSTEM = "domo-defined"
    CUSTOM = "customer-defined"


def clean_attribute_id(text: str) -> str:
    """Clean attribute ID by removing non-alphanumeric characters.

    Args:
        text: Text to clean

    Returns:
        str: Cleaned text with only alphanumeric characters
    """
    return re.sub(r"[^A-Za-z0-9]", "", text)


def generate_create_user_attribute_body(
    attribute_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    issuer_type: Optional[UserAttributes_IssuerType] = None,
    security_voter: Optional[str] = None,
    data_type: Optional[str] = None,
) -> dict:
    """Generate request body for creating user attributes.

    Args:
        attribute_id: Unique identifier for the attribute
        name: Display name for the attribute
        description: Description of the attribute
        issuer_type: Type of issuer for the attribute
        security_voter: Security voter setting
        data_type: Data type validator

    Returns:
        dict: Request body for attribute creation
    """
    s = {"key": attribute_id}

    if issuer_type:
        s.update({"keyspace": issuer_type.value})

    if security_voter:
        s.update({"securityVoter": security_voter})

    if data_type:
        s.update({"validator": data_type})

    if name:
        s.update({"title": name})

    if description:
        s.update({"description": description})

    return s


@gd.route_function
async def get_user_attributes(
    auth: DomoAuth,
    issuer_type_ls: Optional[
        list[UserAttributes_IssuerType]
    ] = None,  # use `UserAttributes_IssuerType` enum
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    parent_class: Optional[str] = None,
    debug_num_stacks_to_drop: int = 1,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Retrieve user attributes from Domo instance.

    User attributes can be of different types: IDP, domo-defined, or customer-defined.
    Note: API does not filter on the issuer type despite accepting filter parameter,
    so filtering is done client-side.

    Args:
        auth: Authentication object
        issuer_type_ls: list of issuer types to retrieve (default: all types)
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        parent_class: Name of calling class for debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing user attributes

    Raises:
        UserAttributes_GET_Error: If user attributes retrieval fails
    """
    issuer_type_ls = issuer_type_ls or [member for member in UserAttributes_IssuerType]

    issuer_types = ",".join([member.value for member in issuer_type_ls])

    params = {"issuerTypes": issuer_types}

    url = f"https://{auth.domo_instance}.domo.com/api/user/v1/properties/meta/keys"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        params=params,
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise UserAttributes_GET_Error(res=res)

    res.response = [
        obj
        for obj in res.response
        if obj["keyspace"] in [member.value for member in issuer_type_ls]
    ]

    return res


@gd.route_function
async def get_user_attribute_by_id(
    auth: DomoAuth,
    attribute_id: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    parent_class: Optional[str] = None,
    debug_num_stacks_to_drop: int = 1,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Retrieve a specific user attribute by ID.

    Args:
        auth: Authentication object
        attribute_id: ID of the attribute to retrieve
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        parent_class: Name of calling class for debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing the user attribute

    Raises:
        UserAttributes_GET_Error: If attribute retrieval fails or attribute not found
    """

    res = await get_user_attributes(
        auth=auth,
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
        return_raw=return_raw,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise UserAttributes_GET_Error(attribute_id=attribute_id, res=res)

    res.response = next(
        (obj for obj in res.response if obj["key"] == attribute_id), None
    )

    if not res.response:
        raise UserAttributes_GET_Error(
            attribute_id=attribute_id,
            message=f"attribute {attribute_id} not found",
            res=res,
        )

    return res


@gd.route_function
async def create_user_attribute(
    auth: DomoAuth,
    attribute_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    data_type: Optional[str] = None,
    security_voter: Optional[str] = None,
    issuer_type: Optional[UserAttributes_IssuerType] = None,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    parent_class: Optional[str] = None,
    debug_num_stacks_to_drop: int = 1,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Create a new user attribute.

    Args:
        auth: Authentication object
        attribute_id: Unique identifier for the attribute (will be cleaned)
        name: Display name for the attribute (defaults to attribute_id)
        description: Description of the attribute (defaults to timestamp)
        data_type: Data type validator (default: "ANY_VALUE")
        security_voter: Security voter setting (default: "FULL_VIS_ADMIN_IDP")
        issuer_type: Type of issuer (default: CUSTOM)
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        parent_class: Name of calling class for debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object confirming attribute creation

    Raises:
        UserAttributes_CRUD_Error: If attribute creation fails
    """
    name = name or attribute_id
    attribute_id = clean_attribute_id(attribute_id)
    description = (
        description
        or f"updated via domolibrary {dt.datetime.now().strftime('%Y-%m-%d - %H:%M')}"
    )
    data_type = data_type or "ANY_VALUE"
    security_voter = security_voter or "FULL_VIS_ADMIN_IDP"
    issuer_type = issuer_type or UserAttributes_IssuerType.CUSTOM

    body = generate_create_user_attribute_body(
        attribute_id=attribute_id,
        issuer_type=issuer_type,
        name=name,
        data_type=data_type,
        security_voter=security_voter,
        description=description,
    )

    url = f"https://{auth.domo_instance}.domo.com/api/user/v1/properties/meta/keys/{attribute_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="POST",
        body=body,
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise UserAttributes_CRUD_Error(
            operation="create",
            attribute_id=attribute_id,
            message=f"Bad Request - does attribute {attribute_id} already exist?",
            res=res,
        )

    res.response = f"created {attribute_id}"

    return res


@gd.route_function
async def update_user_attribute(
    auth: DomoAuth,
    attribute_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    issuer_type: UserAttributes_IssuerType = UserAttributes_IssuerType.CUSTOM,
    data_type: Optional[str] = None,
    security_voter: Optional[str] = None,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    parent_class: Optional[str] = None,
    debug_num_stacks_to_drop: int = 1,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Update an existing user attribute.

    The body must include all attribute parameters. This function will use the
    `get_user_attribute_by_id` function to retrieve existing values and merge
    them with the provided updates.

    Args:
        auth: Authentication object
        attribute_id: ID of the attribute to update
        name: Display name for the attribute
        description: Description of the attribute
        issuer_type: Type of issuer (default: CUSTOM)
        data_type: Data type validator
        security_voter: Security voter setting
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        parent_class: Name of calling class for debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object confirming attribute update

    Raises:
        UserAttributes_CRUD_Error: If attribute update fails
        UserAttributes_GET_Error: If attribute to update is not found
    """

    body = generate_create_user_attribute_body(
        attribute_id=attribute_id,
        issuer_type=issuer_type,
        name=name,
        description=description,
        data_type=data_type,
        security_voter=security_voter,
    )

    res = await get_user_attribute_by_id(
        attribute_id=attribute_id,
        auth=auth,
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
        return_raw=return_raw,
    )

    if return_raw:
        return res

    body = {**res.response, **body}

    url = f"https://{auth.domo_instance}.domo.com/api/user/v1/properties/meta/keys/{attribute_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise UserAttributes_CRUD_Error(
            operation="update",
            attribute_id=attribute_id,
            message=f"Bad Request - error updating {attribute_id}",
            res=res,
        )

    res.response = f"updated {attribute_id}"

    return res


@gd.route_function
async def delete_user_attribute(
    auth: DomoAuth,
    attribute_id: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    parent_class: Optional[str] = None,
    debug_num_stacks_to_drop: int = 1,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Delete a user attribute.

    Args:
        auth: Authentication object
        attribute_id: ID of the attribute to delete
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        parent_class: Name of calling class for debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object confirming attribute deletion

    Raises:
        UserAttributes_CRUD_Error: If attribute deletion fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/user/v1/properties/meta/keys/{attribute_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="DELETE",
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise UserAttributes_CRUD_Error(
            operation="delete",
            attribute_id=attribute_id,
            message=f"Bad Request - failed to delete {attribute_id}",
            res=res,
        )

    res.response = f"deleted {attribute_id}"

    return res
