"""
Account Configuration Route Functions

This module provides account configuration management functions for both regular and OAuth accounts.

Functions:
    get_account_config: Retrieve account configuration
    get_oauth_account_config: Retrieve OAuth account configuration
    update_account_config: Update account configuration
    update_oauth_account_config: Update OAuth account configuration
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
from .core import get_account_by_id
from .exceptions import Account_Config_Error, AccountNoMatchError
from .oauth import get_oauth_account_by_id


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def get_account_config(
    auth: DomoAuth,
    account_id: Union[int, str],
    data_provider_type: Optional[str] = None,
    is_unmask: bool = True,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Retrieve configuration for a specific account.

    Args:
        auth: Authentication object for API requests
        account_id: The ID of the account to get config for
        data_provider_type: Type of data provider (auto-detected if not provided)
        is_unmask: Whether to unmask encrypted values in config
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of calling class for debugging
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object containing account configuration

    Raises:
        AccountNoMatchError: If account is not found or not accessible
        Account_Config_Error: If account configuration retrieval fails
    """
    if not data_provider_type:
        res = await get_account_by_id(
            auth=auth,
            account_id=account_id,
            debug_api=debug_api,
            session=session,
            parent_class=parent_class,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
        )
        data_provider_type = res.response["dataProviderType"]

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/providers/{data_provider_type}/account/{account_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        session=session,
        params={"unmask": is_unmask},
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success and (
        res.response == "Forbidden" or res.response == "Not Found"
    ):
        raise AccountNoMatchError(account_id=str(account_id), res=res)

    if not res.is_success:
        raise Account_Config_Error(account_id=str(account_id), res=res)

    res.response.update(
        {
            "_search_metadata": {
                "account_id": account_id,
                "data_provider_type": data_provider_type,
            }
        }
    )

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def get_oauth_account_config(
    auth: DomoAuth,
    account_id: Union[int, str],
    data_provider_type: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Retrieve configuration for a specific OAuth account.

    Args:
        auth: Authentication object for API requests
        account_id: The ID of the OAuth account to get config for
        data_provider_type: Type of data provider for the OAuth account
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of calling class for debugging
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object containing OAuth account configuration

    Raises:
        AccountNoMatchError: If OAuth account is not found or not accessible
        Account_Config_Error: If OAuth account configuration retrieval fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/providers/{data_provider_type}/template/{account_id}?unmask=true"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        session=session,
        timeout=20,  # occasionally this API has a long response time
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if return_raw:
        return res

    if not res.is_success and (
        res.response == "Forbidden" or res.response == "Not Found"
    ):
        raise AccountNoMatchError(account_id=str(account_id), res=res)

    if not res.is_success:
        raise Account_Config_Error(account_id=str(account_id), res=res)

    res.response.update(
        {
            "_search_metadata": {
                "account_id": account_id,
                "data_provider_type": data_provider_type,
            }
        }
    )

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def update_account_config(
    auth: DomoAuth,
    account_id: Union[int, str],
    config_body: dict,
    data_provider_type: Optional[str] = None,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Update configuration for an account.

    Args:
        auth: Authentication object for API requests
        account_id: ID of the account to update config for
        config_body: New configuration data
        data_provider_type: Type of data provider (auto-detected if not provided)
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of calling class for debugging
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object confirming config update

    Raises:
        Account_Config_Error: If account configuration update fails
    """
    # get the data_provider_type, which is necessary for updating the config setting
    if not data_provider_type:
        res = await get_account_by_id(
            auth=auth,
            account_id=account_id,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
            parent_class=parent_class,
            session=session,
        )
        data_provider_type = res.response.get("dataProviderType")

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/providers/{data_provider_type}/account/{account_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=config_body,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
    )

    if return_raw:
        return res

    if res.status == 400 and res.response == "Bad Request":
        raise Account_Config_Error(
            account_id=str(account_id),
            res=res,
            message=f"Error updating config | use debug_api = True - {res.response}",
        )

    if not res.is_success:
        raise Account_Config_Error(account_id=str(account_id), res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def update_oauth_account_config(
    auth: DomoAuth,
    account_id: Union[int, str],
    config_body: dict,
    data_provider_type: Optional[str] = None,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Update configuration for an OAuth account.

    Args:
        auth: Authentication object for API requests
        account_id: ID of the OAuth account to update config for
        config_body: New configuration data
        data_provider_type: Type of data provider (auto-detected if not provided)
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of calling class for debugging
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object confirming config update

    Raises:
        Account_Config_Error: If OAuth account configuration update fails
    """
    # get the data_provider_type, which is necessary for updating the config setting
    if not data_provider_type:
        res = await get_oauth_account_by_id(
            auth=auth,
            account_id=account_id,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
            parent_class=parent_class,
            session=session,
        )
        data_provider_type = res.response.get("dataProviderType")

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/providers/{data_provider_type}/template/{account_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=config_body,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
    )

    if return_raw:
        return res

    if res.status == 400 and res.response == "Bad Request":
        raise Account_Config_Error(
            account_id=str(account_id),
            res=res,
            message=f"Error updating OAuth config | use debug_api = True - {res.response}",
        )

    if not res.is_success:
        raise Account_Config_Error(account_id=str(account_id), res=res)

    return res
