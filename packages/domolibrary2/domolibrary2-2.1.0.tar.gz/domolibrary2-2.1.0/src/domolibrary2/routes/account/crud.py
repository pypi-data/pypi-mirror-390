"""
Account CRUD Route Functions

This module provides create, read, update, and delete operations for accounts.

Functions:
    create_account: Create new account
    delete_account: Delete account
    create_oauth_account: Create new OAuth account
    delete_oauth_account: Delete OAuth account
    update_account_name: Update account name
    update_oauth_account_name: Update OAuth account name
    generate_create_account_body: Helper to generate account creation payload
    generate_create_oauth_account_body: Helper to generate OAuth account creation payload
"""

from typing import Optional, Union

import httpx
from dc_logger.decorators import LogDecoratorConfig, log_call

from ...auth import DomoAuth
from ...client import (
    get_data as gd,
    response as rgd,
)
from ...utils.logging import ResponseGetDataProcessor
from .exceptions import Account_CreateParams_Error, Account_CRUD_Error


def generate_create_account_body(account_name, data_provider_type, config_body):
    """Generate payload for account creation."""
    return {
        "displayName": account_name,
        "dataProviderType": data_provider_type,
        "name": account_name,
        "configurations": config_body,
    }


def generate_create_oauth_account_body(
    account_name, data_provider_type, origin, config
):
    """Generate payload for OAuth account creation."""
    return {
        "name": account_name,
        "displayName": account_name,
        "dataProviderType": data_provider_type,
        "origin": origin,
        "configurations": config,
    }


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def create_account(
    auth: DomoAuth,
    account_name: Optional[str] = None,
    data_provider_type: Optional[str] = None,
    config_body: Optional[dict] = None,
    payload: Optional[dict] = None,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Create a new account.

    Args:
        auth: Authentication object for API requests
        account_name: Name for the new account
        data_provider_type: Type of data provider for the account
        config_body: Properly formatted AccountConfig dictionary
        payload: Pre-built payload (overrides individual parameters)
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of calling class for debugging
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object containing created account information

    Raises:
        Account_CreateParams_Error: If required parameters are missing
        Account_CRUD_Error: If account creation fails
    """
    if not payload and not (account_name and data_provider_type):
        raise Account_CreateParams_Error(
            "Either payload must be provided or both account_name and data_provider_type are required"
        )

    payload = payload or generate_create_account_body(
        account_name=account_name,
        data_provider_type=data_provider_type,
        config_body=config_body,
    )
    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="POST",
        body=payload,
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Account_CRUD_Error(
            operation="create",
            account_id=account_name,
            res=res,
        )

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def delete_account(
    auth: DomoAuth,
    account_id: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Delete an account.

    Args:
        auth: Authentication object for API requests
        account_id: ID of the account to delete
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of calling class for debugging
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object confirming deletion

    Raises:
        Account_CRUD_Error: If account deletion fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts/{account_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="DELETE",
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Account_CRUD_Error(
            operation="delete",
            account_id=account_id,
            res=res,
        )

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def create_oauth_account(
    auth: DomoAuth,
    account_name: Optional[str] = None,
    data_provider_type: Optional[str] = None,
    origin: str = "OAUTH_CONFIGURATION",
    config: Optional[dict] = None,
    create_body: Optional[dict] = None,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Create a new OAuth account.

    Args:
        auth: Authentication object for API requests
        account_name: Name for the new OAuth account
        data_provider_type: Type of data provider for the OAuth account
        origin: Origin type (default: "OAUTH_CONFIGURATION")
        config: OAuth configuration dictionary
        create_body: Pre-built create body (overrides individual parameters)
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of calling class for debugging
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object containing created OAuth account information

    Raises:
        Account_CreateParams_Error: If required parameters are missing
        Account_CRUD_Error: If OAuth account creation fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts/templates"

    if not create_body and not (
        account_name and data_provider_type and origin and config
    ):
        raise Account_CreateParams_Error(
            "If not passing complete create_body must pass account_name, data_provider_type, origin, and config"
        )

    create_body = create_body or generate_create_oauth_account_body(
        account_name=account_name,
        data_provider_type=data_provider_type,
        origin=origin,
        config=config,
    )

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="POST",
        body=create_body,
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Account_CRUD_Error(
            operation="create",
            account_id=create_body.get("displayName"),
            res=res,
        )

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def delete_oauth_account(
    auth: DomoAuth,
    account_id: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Delete an OAuth account.

    Args:
        auth: Authentication object for API requests
        account_id: ID of the OAuth account to delete
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of calling class for debugging
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object confirming deletion

    Raises:
        Account_CRUD_Error: If OAuth account deletion fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts/templates/{account_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="DELETE",
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Account_CRUD_Error(operation="delete", account_id=account_id, res=res)

    res.response = f"deleted account {account_id}"
    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def update_account_name(
    auth: DomoAuth,
    account_id: Union[int, str],
    account_name: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Update the name of an account.

    Args:
        auth: Authentication object for API requests
        account_id: ID of the account to rename
        account_name: New name for the account
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of calling class for debugging
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object confirming name update

    Raises:
        Account_CRUD_Error: If account name update fails
    """
    url = (
        f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts/{account_id}/name"
    )

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=account_name,
        content_type="text/plain",
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Account_CRUD_Error(
            operation="update name", account_id=str(account_id), res=res
        )

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def update_oauth_account_name(
    auth: DomoAuth,
    account_id: Union[int, str],
    account_name: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Update the name of an OAuth account.

    Args:
        auth: Authentication object for API requests
        account_id: ID of the OAuth account to rename
        account_name: New name for the OAuth account
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of calling class for debugging
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object confirming name update

    Raises:
        Account_CRUD_Error: If OAuth account name update fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts/templates/{account_id}/name"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=account_name,
        content_type="text/plain",
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Account_CRUD_Error(
            operation="update name", account_id=str(account_id), res=res
        )

    return res
