"""
PDP (Personalized Data Permissions) Route Functions

This module provides functions for managing Domo PDP policies including retrieval,
creation, updating, and deletion operations. PDP policies control data access at
the row level based on user, group, or virtual user assignments.

Functions:
    get_pdp_policies: Retrieve all PDP policies for a dataset
    search_pdp_policies_by_name: Search for specific PDP policies by name
    generate_policy_parameter_simple: Utility function for creating policy parameters
    generate_policy_body: Utility function for creating policy request bodies
    create_policy: Create a new PDP policy
    update_policy: Update an existing PDP policy
    delete_policy: Delete a PDP policy
    toggle_pdp: Enable or disable PDP for a dataset

Exception Classes:
    PDP_GET_Error: Raised when PDP policy retrieval fails
    SearchPDPNotFoundError: Raised when PDP policy search returns no results
    PDP_CRUD_Error: Raised when PDP policy create/update/delete operations fail
"""

__all__ = [
    "PDP_GET_Error",
    "SearchPDPNotFoundError",
    "PDP_CRUD_Error",
    "get_pdp_policies",
    "search_pdp_policies_by_name",
    "generate_policy_parameter_simple",
    "generate_policy_body",
    "create_policy",
    "update_policy",
    "delete_policy",
    "toggle_pdp",
    # Legacy exports for backward compatibility
    "SearchPDP_Error",
    "CreatePolicy_Error",
]

from typing import Optional

import httpx

from ..auth import DomoAuth
from ..base.exceptions import RouteError
from ..client import (
    get_data as gd,
    response as rgd,
)


class PDP_GET_Error(RouteError):
    """
    Raised when PDP policy retrieval operations fail.

    This exception is used for failures during GET operations on PDP policies,
    including API errors and unexpected response formats.
    """

    def __init__(
        self,
        dataset_id: Optional[str] = None,
        res: Optional[rgd.ResponseGetData] = None,
        message: Optional[str] = None,
        **kwargs,
    ):
        if not message:
            if dataset_id:
                message = f"Failed to retrieve PDP policies for dataset {dataset_id}"
            else:
                message = "Failed to retrieve PDP policies"

        super().__init__(message=message, entity_id=dataset_id, res=res, **kwargs)


class SearchPDPNotFoundError(RouteError):
    """
    Raised when PDP policy search operations return no results.

    This exception is used when searching for specific PDP policies that
    don't exist or when search criteria match no policies.
    """

    def __init__(
        self,
        search_criteria: str,
        res: Optional[rgd.ResponseGetData] = None,
        **kwargs,
    ):
        message = f"No PDP policies found matching: {search_criteria}"
        super().__init__(
            message=message,
            res=res,
            **kwargs,
        )


class PDP_CRUD_Error(RouteError):
    """
    Raised when PDP policy create, update, or delete operations fail.

    This exception is used for failures during policy creation, modification,
    or deletion operations.
    """

    def __init__(
        self,
        operation: str,
        dataset_id: Optional[str] = None,
        policy_id: Optional[str] = None,
        res: Optional[rgd.ResponseGetData] = None,
        message: Optional[str] = None,
        **kwargs,
    ):
        if not message:
            if policy_id:
                message = f"PDP policy {operation} failed for policy {policy_id}"
            elif dataset_id:
                message = f"PDP policy {operation} failed for dataset {dataset_id}"
            else:
                message = f"PDP policy {operation} operation failed"

        super().__init__(
            message=message,
            entity_id=policy_id or dataset_id,
            res=res,
            **kwargs,
        )


# Legacy error classes for backward compatibility
class PDPNotRetrievedError(PDP_GET_Error):
    """Legacy error class - use PDP_GET_Error instead."""

    def __init__(
        self,
        domo_instance=None,
        function_name=None,
        status=None,
        message=None,
        pdp_id=None,
    ):
        super().__init__(
            dataset_id=pdp_id,
            message=message,
            res=None,
        )


class SearchPDP_Error(SearchPDPNotFoundError):
    """Legacy error class - use SearchPDPNotFoundError instead."""

    def __init__(
        self, status=None, message=None, domo_instance=None, function_name=None
    ):
        # Extract search criteria from message if available
        search_criteria = message or "unknown"
        super().__init__(search_criteria=search_criteria, res=None)


class CreatePolicy_Error(PDP_CRUD_Error):
    """Legacy error class - use PDP_CRUD_Error instead."""

    def __init__(self, res: rgd.ResponseGetData = None, message=None):
        super().__init__(operation="create", message=message, res=res)


@gd.route_function
async def get_pdp_policies(
    auth: DomoAuth,
    dataset_id: str,
    include_all_rows: bool = True,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Retrieve all PDP policies for a specific dataset.

    Fetches a list of all PDP (Personalized Data Permissions) policies associated
    with the specified dataset. Includes policy filters, associations, and open
    policy settings when include_all_rows is True.

    Args:
        auth: Authentication object containing instance and credentials
        dataset_id: Unique identifier for the dataset
        include_all_rows: Include policy associations, filters, and open policy (default: True)
        session: Optional HTTP client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to omit in debug output
        parent_class: Name of calling class for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing list of PDP policies

    Raises:
        PDP_GET_Error: If PDP policy retrieval fails or API returns an error

    Example:
        >>> policies_response = await get_pdp_policies(auth, "abc123")
        >>> for policy in policies_response.response:
        ...     print(f"Policy: {policy['name']}, ID: {policy['filterGroupId']}")
    """
    url = f"http://{auth.domo_instance}.domo.com/api/query/v1/data-control/{dataset_id}/filter-groups/"

    if include_all_rows:
        url += "?options=load_associations,load_filters,include_open_policy"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        is_follow_redirects=True,
    )

    if return_raw:
        return res

    if not res.is_success or (
        isinstance(res.response, list) and len(res.response) == 0
    ):
        raise PDP_GET_Error(
            dataset_id=dataset_id,
            res=res,
            message=f"Failed to retrieve PDP policies for dataset {dataset_id}",
        )

    return res


def search_pdp_policies_by_name(
    search_name: str,
    result_list: list[dict],
    is_exact_match: bool = True,
    is_suppress_errors: bool = False,
) -> dict | list[dict | bool]:
    """
    Search for PDP policies by name within a list of policies.

    Searches through a list of PDP policies to find those matching the specified
    name. Can perform exact or partial matching.

    Args:
        search_name: Name or partial name to search for
        result_list: list of policy dictionaries from get_pdp_policies response
        is_exact_match: If True, search for exact name match; if False, partial match
        is_suppress_errors: If True, return False instead of raising error when not found

    Returns:
        Single policy dict (exact match), list of policy dicts (partial match),
        or False if no matches and is_suppress_errors is True

    Raises:
    SearchPDPNotFoundError: If no policies match the search criteria (unless is_suppress_errors is True)

    Example:
        >>> policies = await get_pdp_policies(auth, "abc123")
        >>> policy = search_pdp_policies_by_name("Sales Policy", policies.response)
        >>> print(f"Found policy: {policy['filterGroupId']}")
    """
    if is_exact_match:
        policy_search = next(
            (policy for policy in result_list if policy["name"] == search_name), None
        )
    else:
        policy_search = [
            policy
            for policy in result_list
            if search_name.lower() in policy["name"].lower()
        ]

    if not policy_search and not is_suppress_errors:
        raise SearchPDPNotFoundError(
            search_criteria=f"name: {search_name}",
        )

    return policy_search or False


def generate_policy_parameter_simple(
    column_name: str,
    type: str = "COLUMN",
    column_values_ls: Optional[list[str]] = None,
    operator: str = "EQUALS",
    ignore_case: bool = True,
) -> dict:
    """
    Generate a simple policy parameter for PDP policy creation.

    Creates a parameter dictionary that defines a filter condition for a PDP policy.
    Parameters specify which column values users can see.

    Args:
        column_name: Name of the column to filter on
        type: Parameter type (default: "COLUMN")
        column_values_ls: list of column values to filter, or single value
        operator: Comparison operator (default: "EQUALS")
        ignore_case: Whether to ignore case when comparing values (default: True)

    Returns:
        Dictionary representing a policy parameter

    Example:
        >>> param = generate_policy_parameter_simple(
        ...     column_name="Region",
        ...     column_values_ls=["West", "East"]
        ... )
        >>> print(param)
        {'type': 'COLUMN', 'name': 'Region', 'values': ['West', 'East'], ...}
    """
    if not isinstance(column_values_ls, list):
        column_values_ls = [column_values_ls] if column_values_ls is not None else []

    return {
        "type": type,
        "name": column_name,
        "values": column_values_ls,
        "operator": operator,
        "ignoreCase": ignore_case,
    }


def generate_policy_body(
    policy_name: str,
    dataset_id: str,
    parameters_ls: list[dict],
    policy_id: Optional[str] = None,
    user_ids: Optional[list[str]] = None,
    group_ids: Optional[list[str]] = None,
    virtual_user_ids: Optional[list[str]] = None,
) -> dict:
    """
    Generate a policy body for PDP policy creation or update.

    Creates a complete request body for creating or updating a PDP policy,
    including filter parameters and user/group assignments.

    Args:
        policy_name: Name for the policy
        dataset_id: Unique identifier for the dataset
        parameters_ls: list of parameter dicts (from generate_policy_parameter_simple)
        policy_id: Policy ID (only for updates, omit for new policies)
        user_ids: list of user IDs to assign the policy to
        group_ids: list of group IDs to assign the policy to
        virtual_user_ids: list of virtual user IDs to assign the policy to

    Returns:
        Dictionary representing complete policy request body

    Example:
        >>> params = [generate_policy_parameter_simple("Region", column_values_ls=["West"])]
        >>> body = generate_policy_body(
        ...     policy_name="West Region Access",
        ...     dataset_id="abc123",
        ...     parameters_ls=params,
        ...     user_ids=["12345"]
        ... )
        >>> # Use body in create_policy or update_policy
    """
    if not user_ids:
        user_ids = []

    if not group_ids:
        group_ids = []

    if not virtual_user_ids:
        virtual_user_ids = []

    if not isinstance(parameters_ls, list):
        parameters_ls = [parameters_ls]

    body = {
        "name": policy_name,
        "dataSourceId": dataset_id,
        "userIds": user_ids,
        "virtualUserIds": virtual_user_ids,
        "groupIds": group_ids,
        "dataSourcePermissions": False,
        "parameters": parameters_ls,
    }

    if policy_id:
        body.update({"filterGroupId": policy_id})

    return body


@gd.route_function
async def create_policy(
    auth: DomoAuth,
    dataset_id: str,
    body: dict,
    override_same_name: bool = False,
    is_suppress_errors: bool = False,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Create a new PDP policy for a dataset.

    Creates a new Personalized Data Permissions policy with the specified
    parameters and assignments. Can check for duplicate policy names before
    creating.

    Args:
        auth: Authentication object containing instance and credentials
        dataset_id: Unique identifier for the dataset
        body: Policy request body (from generate_policy_body)
        override_same_name: If True, allow creating policy with duplicate name
        is_suppress_errors: If True, return existing policy instead of error for duplicates
        session: Optional HTTP client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to omit in debug output
        parent_class: Name of calling class for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing created policy information

    Raises:
        PDP_CRUD_Error: If policy creation fails or duplicate name exists

    Example:
        >>> params = [generate_policy_parameter_simple("Region", column_values_ls=["West"])]
        >>> body = generate_policy_body(
        ...     policy_name="West Region Access",
        ...     dataset_id="abc123",
        ...     parameters_ls=params
        ... )
        >>> response = await create_policy(auth, "abc123", body)
        >>> policy_id = response.response.get("filterGroupId")
    """
    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/data-control/{dataset_id}/filter-groups"

    if not override_same_name:
        existing_policies = await get_pdp_policies(
            auth=auth,
            dataset_id=dataset_id,
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
            parent_class=parent_class,
        )

        policy_exists = search_pdp_policies_by_name(
            search_name=body.get("name"),
            result_list=existing_policies.response,
            is_exact_match=True,
            is_suppress_errors=True,
        )

        if policy_exists:
            if not is_suppress_errors:
                raise PDP_CRUD_Error(
                    operation="create",
                    dataset_id=dataset_id,
                    res=existing_policies,
                    message='Policy name already exists. Avoid creating PDP policies with the same name. To override, set "override_same_name=True"',
                )

            return existing_policies

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

    if return_raw:
        return res

    if not res.is_success:
        raise PDP_CRUD_Error(
            operation="create",
            dataset_id=dataset_id,
            res=res,
            message=f"Failed to create policy - {res.response}",
        )

    return res


@gd.route_function
async def update_policy(
    auth: DomoAuth,
    dataset_id: str,
    policy_id: str,
    body: dict,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Update an existing PDP policy.

    Modifies an existing Personalized Data Permissions policy with new
    parameters, assignments, or name.

    Args:
        auth: Authentication object containing instance and credentials
        dataset_id: Unique identifier for the dataset
        policy_id: Unique identifier for the policy to update
        body: Policy request body (from generate_policy_body)
        session: Optional HTTP client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to omit in debug output
        parent_class: Name of calling class for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing updated policy information

    Raises:
        PDP_CRUD_Error: If policy update fails

    Example:
        >>> params = [generate_policy_parameter_simple("Region", column_values_ls=["West", "East"])]
        >>> body = generate_policy_body(
        ...     policy_name="Updated Policy Name",
        ...     dataset_id="abc123",
        ...     parameters_ls=params,
        ...     policy_id="policy123"
        ... )
        >>> response = await update_policy(auth, "abc123", "policy123", body)
    """
    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/data-control/{dataset_id}/filter-groups/{policy_id}"

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

    if not res.is_success:
        raise PDP_CRUD_Error(
            operation="update",
            dataset_id=dataset_id,
            policy_id=policy_id,
            res=res,
            message=f"Failed to update policy {policy_id} - {res.response}",
        )

    return res


@gd.route_function
async def delete_policy(
    auth: DomoAuth,
    dataset_id: str,
    policy_id: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Delete a PDP policy.

    Permanently removes a Personalized Data Permissions policy from a dataset.
    This action cannot be undone.

    Args:
        auth: Authentication object containing instance and credentials
        dataset_id: Unique identifier for the dataset
        policy_id: Unique identifier for the policy to delete
        session: Optional HTTP client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to omit in debug output
        parent_class: Name of calling class for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object with confirmation message

    Raises:
        PDP_CRUD_Error: If policy deletion fails

    Example:
        >>> response = await delete_policy(auth, "abc123", "policy123")
        >>> print(f"Policy deleted: {response.response}")
    """
    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/data-control/{dataset_id}/filter-groups/{policy_id}"

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

    if not res.is_success:
        raise PDP_CRUD_Error(
            operation="delete",
            dataset_id=dataset_id,
            policy_id=policy_id,
            res=res,
            message=f"Failed to delete policy {policy_id} - {res.response}",
        )

    return res


@gd.route_function
async def toggle_pdp(
    auth: DomoAuth,
    dataset_id: str,
    is_enable: bool = True,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Enable or disable PDP for a dataset.

    Toggles Personalized Data Permissions on or off for the specified dataset.
    When disabled, all users can see all data in the dataset.

    Args:
        auth: Authentication object containing instance and credentials
        dataset_id: Unique identifier for the dataset
        is_enable: If True, enable PDP; if False, disable PDP (default: True)
        session: Optional HTTP client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to omit in debug output
        parent_class: Name of calling class for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object with confirmation message

    Raises:
        PDP_CRUD_Error: If toggle operation fails

    Example:
        >>> # Enable PDP for a dataset
        >>> response = await toggle_pdp(auth, "abc123", is_enable=True)
        >>> # Disable PDP for a dataset
        >>> response = await toggle_pdp(auth, "abc123", is_enable=False)
    """
    url = (
        f"https://{auth.domo_instance}.domo.com/api/query/v1/data-control/{dataset_id}"
    )

    body = {
        "enabled": is_enable,
        "external": False,  # not sure what this parameter does
    }

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

    if not res.is_success:
        action = "enable" if is_enable else "disable"
        raise PDP_CRUD_Error(
            operation=f"toggle ({action})",
            dataset_id=dataset_id,
            res=res,
            message=f"Failed to {action} PDP for dataset {dataset_id} - {res.response}",
        )

    return res
