"""
Scheduler Policy Route Functions

This module provides functions for managing Domo scheduler policies including retrieval,
creation, updating, and deletion operations. Scheduler policies control the frequency
and timing of scheduled data operations.

Functions:
    get_scheduler_policies: Retrieve all scheduler policies
    get_scheduler_policy_by_id: Retrieve a specific scheduler policy by ID
    create_scheduler_policy: Create a new scheduler policy
    update_scheduler_policy: Update an existing scheduler policy
    delete_scheduler_policy: Delete a scheduler policy

Exception Classes:
    SchedulerPolicy_GET_Error: Raised when scheduler policy retrieval fails
    SchedulerPolicy_CRUD_Error: Raised when scheduler policy create/update/delete operations fail
    SearchSchedulerPolicy_NotFound: Raised when scheduler policy search returns no results
"""

__all__ = [
    "SchedulerPolicy_GET_Error",
    "SchedulerPolicy_CRUD_Error",
    "SearchSchedulerPolicy_NotFound_Error",
    "get_scheduler_policies",
    "get_scheduler_policy_by_id",
    "create_scheduler_policy",
    "update_scheduler_policy",
    "delete_scheduler_policy",
]

from typing import Any, Optional

import httpx

from ...auth import DomoAuth
from ...client import (
    get_data as gd,
    response as rgd,
)
from .exceptions import Config_CRUD_Error, Config_GET_Error


class SchedulerPolicy_GET_Error(Config_GET_Error):  # noqa: N801
    """
    Raised when scheduler policy retrieval operations fail.

    This exception is used for failures during GET operations on scheduler policies,
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
                message = f"Failed to retrieve scheduler policy {entity_id}"
            else:
                message = "Failed to retrieve scheduler policies"

        super().__init__(
            message=message,
            res=res
            or rgd.ResponseGetData(
                status=500,
                response="Failed to retrieve scheduler policies",
                is_success=False,
            ),
            **kwargs,
        )


class SchedulerPolicy_CRUD_Error(Config_CRUD_Error):  # noqa: N801
    """
    Raised when scheduler policy create, update, or delete operations fail.

    This exception is used for failures during policy creation, modification,
    or deletion operations.
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
            message = f"Scheduler policy {operation} operation failed, {entity_id}"

        super().__init__(
            message=message,
            res=res
            or rgd.ResponseGetData(
                status=500,
                response=f"Scheduler policy {operation} operation failed, {entity_id}",
                is_success=False,
            ),
            **kwargs,
        )


class SearchSchedulerPolicy_NotFound_Error(Config_GET_Error):  # noqa: N801
    """
    Raised when scheduler policy search operations return no results.

    This exception is used when searching for specific scheduler policies that
    don't exist or when search criteria match no policies.
    """

    def __init__(
        self,
        search_criteria: str,
        res: Optional[rgd.ResponseGetData] = None,
        **kwargs,
    ):
        message = f"No scheduler policies found matching: {search_criteria}"
        # Store search_criteria as an attribute for debugging
        self.search_criteria = search_criteria
        super().__init__(
            message=message,
            res=res
            or rgd.ResponseGetData(
                status=404,
                response=f"No scheduler policies found matching: {search_criteria}",
                is_success=False,
            ),
            **kwargs,
        )


@gd.route_function
async def get_scheduler_policies(
    auth: DomoAuth,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Retrieve all scheduler policies from Domo instance.

    Retrieves a complete list of all scheduler policies configured in the
    Domo instance. Scheduler policies control the frequency and timing of
    scheduled data operations.

    Args:
        auth: Authentication object
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of calling class for debugging
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing list of scheduler policies

    Raises:
        SchedulerPolicy_GET_Error: If retrieval fails or feature is not enabled
    """
    url = f"https://{auth.domo_instance}.domo.com/api/metrics/v1/usage/policies"

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

    if (
        res.status == 403
        and isinstance(res.response, str)
        and res.response.startswith("Forbidden")
    ):
        raise SchedulerPolicy_GET_Error(
            res=res,
            message="error retrieving permissions, is the feature switch enabled?",
        )

    if not res.is_success:
        raise SchedulerPolicy_GET_Error(res=res)

    return res


@gd.route_function
async def get_scheduler_policy_by_id(
    auth: DomoAuth,
    policy_id: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Retrieve a specific scheduler policy by ID.

    This is a wrapper function that retrieves all policies and filters for
    the requested ID, since direct GET by ID is not available in the API.

    Args:
        auth: Authentication object
        policy_id: ID of the scheduler policy to retrieve
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of calling class for debugging
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing the requested scheduler policy

    Raises:
        SchedulerPolicy_GET_Error: If retrieval fails
        SearchSchedulerPolicy_NotFound: If policy with given ID is not found
    """
    res = await get_scheduler_policies(
        auth=auth,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
        return_raw=return_raw,
    )

    if return_raw:
        return res

    match_policy = next(
        (policy for policy in res.response if policy["id"] == policy_id), None
    )

    if not match_policy:
        raise SearchSchedulerPolicy_NotFound_Error(
            search_criteria=f"policy_id={policy_id}",
            res=rgd.ResponseGetData(
                status=404,
                response=f"Policy with ID {policy_id} not found",
                is_success=False,
            ),
        )

    res.response = match_policy
    return res


@gd.route_function
async def create_scheduler_policy(
    auth: DomoAuth,
    create_body: dict[str, Any],
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Create a new scheduler policy.

    Creates a new scheduler policy with the specified configuration including
    frequencies and member assignments.

    Args:
        auth: Authentication object
        create_body: Dictionary containing policy configuration with required keys:
            - frequencies: dict[str, int] mapping frequency names to values
            - members: list of dicts with 'type' and 'id' keys
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of calling class for debugging
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing the created scheduler policy

    Raises:
        SchedulerPolicy_CRUD_Error: If creation fails or validation errors occur
    """
    # Basic input validation for clearer error messages
    if not isinstance(create_body.get("frequencies"), dict) or not all(
        isinstance(v, int) for v in create_body.get("frequencies", {}).values()
    ):
        raise SchedulerPolicy_CRUD_Error(
            operation="create",
            res=rgd.ResponseGetData(
                status=400,
                response="frequencies must be a dict[str, int]",
                is_success=False,
            ),
            message="Invalid frequencies format",
        )

    if not isinstance(create_body.get("members"), list) or not all(
        isinstance(m, dict) and "type" in m and "id" in m
        for m in create_body["members"]
    ):
        raise SchedulerPolicy_CRUD_Error(
            operation="create",
            res=rgd.ResponseGetData(
                status=400,
                response="members must be a list of dicts with 'type' and 'id'",
                is_success=False,
            ),
            message="Invalid members format",
        )

    url = f"https://{auth.domo_instance}.domo.com/api/metrics/v1/usage/policies"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="POST",
        body=create_body,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise SchedulerPolicy_CRUD_Error(operation="create", res=res)

    return res


@gd.route_function
async def update_scheduler_policy(
    auth: DomoAuth,
    policy_id: str,
    update_body: dict[str, Any],
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Update an existing scheduler policy.

    Updates the configuration of an existing scheduler policy identified by
    its policy ID.

    Args:
        auth: Authentication object
        policy_id: ID of the scheduler policy to update
        update_body: Dictionary containing updated policy configuration
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of calling class for debugging
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing the updated scheduler policy

    Raises:
        SchedulerPolicy_CRUD_Error: If update fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/metrics/v1/usage/policies/{policy_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=update_body,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise SchedulerPolicy_CRUD_Error(
            operation="update", entity_id=policy_id, res=res
        )

    return res


@gd.route_function
async def delete_scheduler_policy(
    auth: DomoAuth,
    policy_id: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Delete a scheduler policy.

    Deletes an existing scheduler policy identified by its policy ID.

    Args:
        auth: Authentication object
        policy_id: ID of the scheduler policy to delete
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of calling class for debugging
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object confirming deletion

    Raises:
        SchedulerPolicy_CRUD_Error: If deletion fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/metrics/v1/usage/policies/{policy_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="DELETE",
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
    )

    if return_raw:
        return res

    # DELETE returns 200 with "OK" text response, which should be treated as success
    if res.status == 200 or res.is_success:
        return res

    if not res.is_success:
        raise SchedulerPolicy_CRUD_Error(
            operation="delete", entity_id=policy_id, res=res
        )

    return res
