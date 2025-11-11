"""
MFA Configuration Route Functions

This module provides functions for managing Domo Multi-Factor Authentication (MFA)
configuration including enabling/disabling MFA, setting expiration policies, and
configuring code attempt limits.

Functions:
    get_mfa_config: Retrieve MFA configuration settings
    toggle_enable_mfa: Enable or disable MFA requirement
    set_mfa_max_code_attempts: Configure maximum invalid code attempts
    set_mfa_num_days_valid: Set MFA token validity duration

Exception Classes:
    MFA_GET_Error: Raised when MFA configuration retrieval fails
    MFA_CRUD_Error: Raised when MFA configuration update operations fail
"""

__all__ = [
    "MFA_GET_Error",
    "MFA_CRUD_Error",
    "get_mfa_config",
    "toggle_enable_mfa",
    "set_mfa_max_code_attempts",
    "set_mfa_num_days_valid",
]

from typing import Any, Optional

import httpx

from ...auth import DomoAuth
from ...client import (
    get_data as gd,
    response as rgd,
)
from .exceptions import Config_CRUD_Error, Config_GET_Error


class MFA_GET_Error(Config_GET_Error):
    """
    Raised when MFA configuration retrieval operations fail.

    This exception is used for failures during GET operations on MFA settings,
    including API errors and unexpected response formats.
    """

    def __init__(
        self,
        res: rgd.ResponseGetData,
        message: Optional[str] = None,
        **kwargs,
    ):
        if not message:
            message = "Failed to retrieve MFA configuration"

        super().__init__(message=message, res=res, **kwargs)


class MFA_CRUD_Error(Config_CRUD_Error):
    """
    Raised when MFA configuration update operations fail.

    This exception is used for failures during MFA configuration changes,
    including enable/disable operations and policy updates.
    """

    def __init__(
        self,
        res: rgd.ResponseGetData,
        message: Optional[str] = None,
    ):
        super().__init__(
            res=res, message=message or "Failed to update MFA configuration"
        )


@gd.route_function
async def toggle_enable_mfa(
    auth: DomoAuth,
    is_enable_MFA: bool = False,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Enable or disable MFA requirement for the Domo instance.

    Toggles the multi-factor authentication requirement policy for all users
    in the instance. When enabled, users must complete MFA to access Domo.

    Args:
        auth: Authentication object containing instance and credentials
        is_enable_MFA: True to enable MFA, False to disable (default: False)
        session: Optional HTTP client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to omit in debug output
        parent_class: Name of calling class for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object with confirmation message

    Raises:
        MFA_CRUD_Error: If MFA toggle operation fails or requires OTP elevation

    Example:
        >>> response = await toggle_enable_mfa(auth, is_enable_MFA=True)
        >>> print(response.response)  # "toggled MFA on"
    """
    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/customer-states/domo.policy.multifactor.required"

    payload = {
        "name": "domo.policy.multifactor.required",
        "value": "yes" if is_enable_MFA else "no",
    }

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=payload,
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        if res.status == 403:
            raise MFA_CRUD_Error(
                res=res,
                message="MFA toggle requires OTP elevation",
            )
        raise MFA_CRUD_Error(
            res=res,
            message=f"Failed to toggle MFA in {auth.domo_instance}",
        )

    res.response = f"toggled MFA {'on' if is_enable_MFA else 'off'}"

    return res


@gd.route_function
async def get_mfa_config(
    auth: DomoAuth,
    incl_is_multifactor_required: bool = True,
    incl_num_days_valid: bool = True,
    incl_max_code_attempts: bool = True,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Retrieve MFA configuration settings for the Domo instance.

    Fetches the current multi-factor authentication configuration including
    whether MFA is required, validity duration, and maximum code attempts.

    Args:
        auth: Authentication object containing instance and credentials
        incl_is_multifactor_required: Include MFA requirement status (default: True)
        incl_num_days_valid: Include MFA validity duration in days (default: True)
        incl_max_code_attempts: Include maximum invalid code attempts (default: True)
        session: Optional HTTP client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to omit in debug output
        parent_class: Name of calling class for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing MFA configuration with keys:
        - is_multifactor_required: Boolean indicating if MFA is enabled
        - num_days_valid: Integer days before MFA re-authentication required
        - max_code_attempts: Integer maximum invalid code attempts allowed

    Raises:
        MFA_GET_Error: If MFA configuration retrieval fails

    Example:
        >>> config_response = await get_mfa_config(auth)
        >>> config = config_response.response
        >>> print(f"MFA Required: {config['is_multifactor_required']}")
        >>> print(f"Valid for {config['num_days_valid']} days")
    """
    params: dict[str, Any] = {"ignoreCache": True}

    state_ls = []

    if incl_is_multifactor_required:
        state_ls.append("domo.policy.multifactor.required")

    if incl_num_days_valid:
        state_ls.append("domo.policy.multifactor.factorExpires")

    if incl_max_code_attempts:
        state_ls.append("domo.policy.multifactor.maxCodeAttempts")

    params.update({"stateName": ",".join(state_ls)})

    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/customer-states"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        params=params,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise MFA_GET_Error(
            res=res,
            message=f"Failed to retrieve MFA configuration settings from {auth.domo_instance}",
        )

    new_obj = {
        obj["name"]: obj["value"] for obj in res.response if isinstance(obj, dict)
    }

    is_multifactor_required = (
        True if new_obj.get("domo.policy.multifactor.required") == "yes" else False
    )

    num_days_valid = new_obj.get("domo.policy.multifactor.factorExpires")
    if num_days_valid and num_days_valid.isdigit():
        num_days_valid = int(num_days_valid)

    max_code_attempts = new_obj.get("domo.policy.multifactor.maxCodeAttempts")
    if max_code_attempts and max_code_attempts.isdigit():
        max_code_attempts = int(max_code_attempts)

    res.response = {
        "is_multifactor_required": is_multifactor_required,
        "num_days_valid": num_days_valid,
        "max_code_attempts": max_code_attempts,
    }

    return res


@gd.route_function
async def set_mfa_max_code_attempts(
    auth: DomoAuth,
    max_code_attempts: int,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Set the maximum number of invalid MFA code attempts.

    Configures the maximum number of invalid login attempts before the MFA
    code is reset and user must request a new code.

    Args:
        auth: Authentication object containing instance and credentials
        max_code_attempts: Maximum invalid code attempts (must be greater than 0)
        session: Optional HTTP client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to omit in debug output
        parent_class: Name of calling class for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object with confirmation message

    Raises:
        MFA_CRUD_Error: If max code attempts update fails, requires OTP elevation,
                       or if max_code_attempts is not greater than 0

    Example:
        >>> response = await set_mfa_max_code_attempts(auth, 5)
        >>> print(response.response)
    """
    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/customer-states/domo.policy.multifactor.maxCodeAttempts"

    if not max_code_attempts > 0:
        raise MFA_CRUD_Error(
            res=rgd.ResponseGetData(
                status=400,
                response="max_code_attempts must be greater than 0. Unable to set MFA max code attempts",
                is_success=False,
            ),
            message="max_code_attempts must be greater than 0. Unable to set MFA max code attempts",
        )

    payload = {
        "name": "domo.policy.multifactor.maxCodeAttempts",
        "value": max_code_attempts,
    }

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=payload,
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        if res.status == 403:
            raise MFA_CRUD_Error(
                res=res,
                message=f"MFA modification requires OTP elevation to update max code attempts in {auth.domo_instance}",
            )

        raise MFA_CRUD_Error(
            res=res,
            message=f"Failed to update max number of code attempts for MFA in {auth.domo_instance}",
        )

    res.response = f"set max number of code attempts to {max_code_attempts} in {auth.domo_instance}"

    return res


@gd.route_function
async def set_mfa_num_days_valid(
    auth: DomoAuth,
    num_days_valid: int,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Set the number of days before MFA re-authentication is required.

    Configures the validity duration for MFA tokens. After this many days,
    users must complete MFA authentication again.

    Args:
        auth: Authentication object containing instance and credentials
        num_days_valid: Number of days before MFA expires (must be greater than 0)
        session: Optional HTTP client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to omit in debug output
        parent_class: Name of calling class for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object with confirmation message

    Raises:
        MFA_CRUD_Error: If MFA validity duration update fails or if
                       num_days_valid is not greater than 0

    Example:
        >>> response = await set_mfa_num_days_valid(auth, 30)
        >>> print(response.response)  # "num days MFA valid set to 30 in..."
    """
    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/customer-states/domo.policy.multifactor.factorExpires"

    if not num_days_valid > 0:
        raise MFA_CRUD_Error(
            res=rgd.ResponseGetData(
                status=400,
                response="num_days_valid must be greater than 0. Unable to set days before MFA expires",
                is_success=False,
            ),
            message="num_days_valid must be greater than 0. Unable to set days before MFA expires",
        )

    payload = {"name": "domo.policy.multifactor.factorExpires", "value": num_days_valid}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=payload,
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise MFA_CRUD_Error(
            res=res,
            message=f"Failed to set number of days before MFA expires in {auth.domo_instance}",
        )

    res.response = f"num days MFA valid set to {num_days_valid} in {auth.domo_instance}"

    return res
