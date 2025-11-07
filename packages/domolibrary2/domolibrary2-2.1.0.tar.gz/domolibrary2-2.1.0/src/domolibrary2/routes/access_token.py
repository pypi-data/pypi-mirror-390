"""
Access Token Route Functions

This module provides functions for managing Domo access tokens including retrieval,
generation, and revocation operations. Access tokens are used for API authentication
and have configurable expiration dates.

Functions:
    get_access_tokens: Retrieve all access tokens for the authenticated instance
    get_access_token_by_id: Retrieve a specific access token by ID
    generate_access_token: Create a new access token for a user
    revoke_access_token: Revoke an existing access token
    generate_expiration_unixtimestamp: Utility function for timestamp generation

Exception Classes:
    AccessToken_GET_Error: Raised when token retrieval fails
    SearchAccessTokenNotFoundError: Raised when token search returns no results
    AccessToken_CRUD_Error: Raised when token create/update/delete operations fail
"""

__all__ = [
    "AccessToken_GET_Error",
    "SearchAccessTokenNotFoundError",
    "AccessToken_CRUD_Error",
    "get_access_tokens",
    "get_access_token_by_id",
    "generate_expiration_unixtimestamp",
    "generate_access_token",
    "revoke_access_token",
]

import datetime as dt
import time
from typing import Optional, Union

import httpx
from dc_logger.client.base import Logger

from ..auth import DomoAuth
from ..base.exceptions import RouteError
from ..client import (
    get_data as gd,
    response as rgd,
)


class AccessToken_GET_Error(RouteError):
    """
    Raised when access token retrieval operations fail.

    This exception is used for failures during GET operations on access tokens,
    including API errors and unexpected response formats.
    """

    def __init__(
        self,
        entity_id: Optional[str] = None,
        res: Optional[rgd.ResponseGetData] = None,
        message: Optional[str] = None,
        **kwargs,
    ):
        if not message:
            if entity_id:
                message = f"Failed to retrieve access token {entity_id}"
            else:
                message = "Failed to retrieve access tokens"

        super().__init__(message=message, entity_id=entity_id, res=res, **kwargs)


class SearchAccessTokenNotFoundError(RouteError):
    """
    Raised when access token search operations return no results.

    This exception is used when searching for specific access tokens that
    don't exist or when search criteria match no tokens.
    """

    def __init__(
        self,
        search_criteria: str,
        res: Optional[rgd.ResponseGetData] = None,
        **kwargs,
    ):
        message = f"No access tokens found matching: {search_criteria}"
        super().__init__(
            message=message,
            res=res,
            additional_context={"search_criteria": search_criteria},
            **kwargs,
        )


class AccessToken_CRUD_Error(RouteError):
    """
    Raised when access token create, update, or delete operations fail.

    This exception is used for failures during token generation, modification,
    or revocation operations.
    """

    def __init__(
        self,
        operation: str,
        entity_id: Optional[str] = None,
        res: Optional[rgd.ResponseGetData] = None,
        message: Optional[str] = None,
        **kwargs,
    ):
        if not message:
            if entity_id:
                message = f"Access token {operation} failed for token {entity_id}"
            else:
                message = f"Access token {operation} operation failed"

        super().__init__(
            message=message,
            entity_id=entity_id,
            res=res,
            additional_context={"operation": operation},
            **kwargs,
        )


@gd.route_function
async def get_access_tokens(
    auth: DomoAuth,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
    logger: Optional[Logger] = None,
) -> rgd.ResponseGetData:
    """
    Retrieve all access tokens for the authenticated instance.

    Fetches a list of all access tokens associated with the current Domo instance.
    Each token includes metadata such as name, owner, and expiration date.

    Args:
        auth: Authentication object containing instance and credentials
        session: Optional HTTP client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to omit in debug output
        parent_class: Name of calling class for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing list of access tokens with converted
        expiration timestamps to datetime objects

    Raises:
        AccessToken_GET_Error: If token retrieval fails or API returns an error

    Example:
        >>> tokens_response = await get_access_tokens(auth)
        >>> for token in tokens_response.response:
        ...     print(f"Token: {token['name']}, Expires: {token['expires']}")
    """

    # assert logger
    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accesstokens"

    res = await gd.get_data(
        url=url,
        method="GET",
        auth=auth,
        debug_api=debug_api,
        parent_class=parent_class,
        session=session,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        message = f"Failed to retrieve access tokens: {res.response}"

        # logger.error(message)

        raise AccessToken_GET_Error(
            res=res,
            message=message,
        )

    # Convert Unix timestamps to datetime objects for better usability
    if res.response and isinstance(res.response, list):
        for token in res.response:
            if token and "expires" in token and token["expires"]:
                token.update(
                    {"expires": dt.datetime.fromtimestamp(token["expires"] / 1000)}
                )

    return res


@gd.route_function
async def get_access_token_by_id(
    auth: DomoAuth,
    access_token_id: int,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Retrieve a specific access token by its ID.

    Fetches details for a single access token identified by its unique ID.
    This function first retrieves all tokens and then filters to find the
    specific token requested.

    Args:
        auth: Authentication object containing instance and credentials
        access_token_id: Unique identifier for the access token to retrieve
        session: Optional HTTP client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to omit in debug output
        parent_class: Name of calling class for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing the specific access token data

    Raises:
        AccessToken_GET_Error: If token retrieval fails
    SearchAccessTokenNotFoundError: If no token with the specified ID exists

    Example:
        >>> token_response = await get_access_token_by_id(auth, 12345)
        >>> token_data = token_response.response
        >>> print(f"Token Name: {token_data['name']}")
    """
    res = await get_access_tokens(
        auth=auth,
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        return_raw=return_raw,
    )

    if return_raw:
        return res

    # Search for the specific token in the response
    if not res.response or not isinstance(res.response, list):
        raise AccessToken_GET_Error(
            entity_id=str(access_token_id),
            res=res,
            message="Invalid response format from access tokens API",
        )

    token = next(
        (
            token
            for token in res.response
            if token and token.get("id") == access_token_id
        ),
        None,
    )

    if not token:
        raise SearchAccessTokenNotFoundError(
            search_criteria=f"ID: {access_token_id}", res=res
        )

    res.response = token
    return res


def generate_expiration_unixtimestamp(
    duration_in_days: int = 90, debug_prn: bool = False
) -> int:
    """
    Generate Unix timestamp for access token expiration.

    Creates a Unix timestamp (in milliseconds) for an expiration date
    that is the specified number of days from today.

    Args:
        duration_in_days: Number of days from today for expiration (default: 90)
        debug_prn: Print debug information about the calculated expiration date

    Returns:
        Unix timestamp in milliseconds for the expiration date

    Example:
        >>> timestamp = generate_expiration_unixtimestamp(30)
        >>> expiry_date = datetime.fromtimestamp(timestamp / 1000)
        >>> print(f"Token expires on: {expiry_date}")
    """
    today = dt.datetime.today()
    expiration_date = today + dt.timedelta(days=duration_in_days)

    if debug_prn:
        print(
            f"Expiration date is {duration_in_days} days from today: {expiration_date}"
        )

    return int(time.mktime(expiration_date.timetuple()) * 1000)


@gd.route_function
async def generate_access_token(
    auth: DomoAuth,
    token_name: str,
    user_id: Union[int, str],
    duration_in_days: int = 90,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Generate a new access token for a user.

    Creates a new access token with the specified name and expiration period
    for the given user ID. The token can be used for API authentication.

    Args:
        auth: Authentication object containing instance and credentials
        token_name: Descriptive name for the new access token
        user_id: Unique identifier for the user who will own the token
        duration_in_days: Number of days until token expires (default: 90)
        session: Optional HTTP client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to omit in debug output
        parent_class: Name of calling class for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing the generated token information

    Raises:
        AccessToken_CRUD_Error: If token generation fails or user ID is invalid

    Example:
        >>> token_response = await generate_access_token(
        ...     auth, "API Integration Token", 12345, 30
        ... )
        >>> token_value = token_response.response["token"]
        >>> print(f"Generated token: {token_value}")
    """
    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accesstokens"

    expiration_timestamp = generate_expiration_unixtimestamp(
        duration_in_days=duration_in_days
    )

    body = {"name": token_name, "ownerId": user_id, "expires": expiration_timestamp}

    res = await gd.get_data(
        url=url,
        method="POST",
        body=body,
        auth=auth,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
    )

    if return_raw:
        return res

    # Handle specific error cases
    if res.status == 400:
        raise AccessToken_CRUD_Error(
            operation="create",
            entity_id=str(user_id),
            res=res,
            message=f"Unable to generate access token for user {user_id}. Please verify the user ID is valid.",
        )

    if not res.is_success:
        raise AccessToken_CRUD_Error(
            operation="create",
            entity_id=str(user_id),
            res=res,
            message=f"Access token generation failed: {res.response}",
        )

    # Verify token was actually generated
    if not res.response or not res.response.get("token"):
        raise AccessToken_CRUD_Error(
            operation="create",
            entity_id=str(user_id),
            res=res,
            message="Token generation appeared successful but no token was returned",
        )

    return res


@gd.route_function
async def revoke_access_token(
    auth: DomoAuth,
    access_token_id: int,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Revoke an existing access token.

    Permanently revokes an access token, making it immediately unusable
    for API authentication. This action cannot be undone.

    Args:
        auth: Authentication object containing instance and credentials
        access_token_id: Unique identifier for the token to revoke
        session: Optional HTTP client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to omit in debug output
        parent_class: Name of calling class for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object with confirmation message

    Raises:
        AccessToken_CRUD_Error: If token revocation fails

    Example:
        >>> response = await revoke_access_token(auth, 12345)
        >>> print(response.response)  # "access token 12345 revoked"
    """
    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accesstokens/{access_token_id}"

    res = await gd.get_data(
        url=url,
        method="DELETE",
        auth=auth,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise AccessToken_CRUD_Error(
            operation="revoke",
            entity_id=str(access_token_id),
            res=res,
            message=f"Failed to revoke access token {access_token_id}: {res.response}",
        )

    res.response = f"access token {access_token_id} revoked"
    return res
