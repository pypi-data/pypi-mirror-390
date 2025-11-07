"""
OAuth Account Route Functions

This module provides OAuth-specific account functions.

Functions:
    get_oauth_accounts: Retrieve all OAuth accounts user has access to
    get_oauth_account_by_id: Retrieve specific OAuth account by ID
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
from .exceptions import Account_GET_Error, AccountNoMatchError


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def get_oauth_accounts(
    auth: DomoAuth,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Retrieve all OAuth accounts the user has access to.

    Args:
        auth: Authentication object for API requests
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of calling class for debugging
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object containing OAuth account list

    Raises:
        Account_GET_Error: If OAuth account retrieval fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts/templates/user/extended"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Account_GET_Error(res=res)
    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def get_oauth_account_by_id(
    auth: DomoAuth,
    account_id: Union[int, str],
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Retrieve a specific OAuth account by ID.

    Note: This function retrieves all OAuth accounts and filters to the selected one,
    as there doesn't appear to be a direct API for retrieving a single OAuth account.

    Args:
        auth: Authentication object for API requests
        account_id: The ID of the OAuth account to retrieve
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of calling class for debugging
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object containing OAuth account metadata

    Raises:
        AccountNoMatchError: If OAuth account is not found
        Account_GET_Error: If OAuth account retrieval fails
    """
    res = await get_oauth_accounts(
        auth=auth,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
        parent_class=parent_class,
        session=session,
        return_raw=return_raw,
    )

    if return_raw:
        return res

    # Convert account_id to int for comparison if it's a string
    target_id = int(account_id) if isinstance(account_id, str) else account_id
    res.response = next((obj for obj in res.response if obj["id"] == target_id), None)

    if not res.response:
        raise AccountNoMatchError(account_id=str(account_id), res=res)

    return res
