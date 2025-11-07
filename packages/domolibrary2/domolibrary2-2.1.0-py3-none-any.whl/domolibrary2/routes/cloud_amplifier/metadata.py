"""
Cloud Amplifier Metadata Functions

This module contains functions for managing Cloud Amplifier metadata including
databases, schemas, tables, and federated source metadata.
"""

__all__ = [
    "check_for_colliding_datasources",
    "get_federated_source_metadata",
    "get_databases",
    "get_schemas",
    "get_tables",
]

from typing import Optional

import httpx

from ...auth import DomoAuth
from ...client import (
    get_data as gd,
    response as rgd,
)
from .exceptions import CloudAmplifier_GET_Error, SearchCloudAmplifier_NotFound


@gd.route_function
async def check_for_colliding_datasources(
    auth: DomoAuth,
    dataset_id: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Check for Cloud Amplifier integrations that collide with an existing Domo Dataset.

    Args:
        auth: Authentication object containing instance and credentials
        dataset_id: Dataset ID to check for collisions
        session: Optional HTTP client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to omit in debug output
        parent_class: Name of calling class for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing collision information

    Raises:
        CloudAmplifier_GET_Error: If collision check fails or no federated metadata exists

    Example:
        >>> collisions = await check_for_colliding_datasources(auth, "dataset-123")
        >>> print(collisions.response)
    """

    url = f"https://{auth.domo_instance}.domo.com/api/query/migration/integrations/datasource/{dataset_id}"

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

    # A 400 may be returned if no federated metadata exists for the dataset
    if res.status == 400:
        raise CloudAmplifier_GET_Error(
            entity_id=dataset_id,
            res=res,
            message=f"No federated metadata exists for the datasource {dataset_id}",
        )

    if not res.is_success:
        raise CloudAmplifier_GET_Error(entity_id=dataset_id, res=res)

    return res


@gd.route_function
async def get_federated_source_metadata(
    auth: DomoAuth,
    dataset_id: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Retrieve federated source metadata for a dataset.

    Args:
        auth: Authentication object containing instance and credentials
        dataset_id: Dataset ID to retrieve metadata for
        session: Optional HTTP client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to omit in debug output
        parent_class: Name of calling class for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing federated source metadata

    Raises:
        SearchCloudAmplifier_NotFound: If no federated datasource exists with the ID
        CloudAmplifier_GET_Error: If metadata retrieval fails

    Example:
        >>> metadata = await get_federated_source_metadata(auth, "dataset-123")
        >>> print(metadata.response)
    """

    url = f"https://{auth.domo_instance}.domo.com/api/federated/v1/config/datasources/{dataset_id}"

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

    # A 404 may be returned if no federated metadata exists for the dataset
    if res.status == 404:
        raise SearchCloudAmplifier_NotFound(
            search_criteria=f"Federated datasource ID: {dataset_id}",
            res=res,
        )

    if not res.is_success:
        raise CloudAmplifier_GET_Error(entity_id=dataset_id, res=res)

    return res


@gd.route_function
async def get_databases(
    auth: DomoAuth,
    integration_id: str,
    page: int = 0,
    rows: int = 5000,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Retrieve a list of all databases for a Cloud Amplifier integration.

    Args:
        auth: Authentication object containing instance and credentials
        integration_id: Integration ID to list databases for
        page: Page number for pagination (default: 0)
        rows: Number of rows per page (default: 5000)
        session: Optional HTTP client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to omit in debug output
        parent_class: Name of calling class for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing list of databases

    Raises:
        CloudAmplifier_GET_Error: If database retrieval fails

    Example:
        >>> databases = await get_databases(auth, "integration-123")
        >>> for db in databases.response:
        ...     print(db['databaseName'])
    """

    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/byos/accounts/{integration_id}/databases"

    params = {"page": page, "rows": rows}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
        params=params,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise CloudAmplifier_GET_Error(entity_id=integration_id, res=res)

    return res


@gd.route_function
async def get_schemas(
    auth: DomoAuth,
    integration_id: str,
    database: str,
    page: int = 0,
    rows: int = 5000,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Retrieve a list of all schemas for a Cloud Amplifier integration database.

    Args:
        auth: Authentication object containing instance and credentials
        integration_id: Integration ID
        database: Database name to list schemas for
        page: Page number for pagination (default: 0)
        rows: Number of rows per page (default: 5000)
        session: Optional HTTP client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to omit in debug output
        parent_class: Name of calling class for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing list of schemas

    Raises:
        CloudAmplifier_GET_Error: If schema retrieval fails

    Example:
        >>> schemas = await get_schemas(auth, "integration-123", "MY_DATABASE")
        >>> for schema in schemas.response:
        ...     print(schema['schemaName'])
    """

    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/byos/accounts/{integration_id}/databases/{database}/schemas"

    params = {"page": page, "rows": rows}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
        params=params,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise CloudAmplifier_GET_Error(entity_id=integration_id, res=res)

    return res


@gd.route_function
async def get_tables(
    auth: DomoAuth,
    integration_id: str,
    database: str,
    schema: str,
    page: int = 0,
    rows: int = 5000,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """
    Retrieve a list of all tables for a Cloud Amplifier integration schema.

    Args:
        auth: Authentication object containing instance and credentials
        integration_id: Integration ID
        database: Database name
        schema: Schema name to list tables for
        page: Page number for pagination (default: 0)
        rows: Number of rows per page (default: 5000)
        session: Optional HTTP client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to omit in debug output
        parent_class: Name of calling class for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing list of tables

    Raises:
        CloudAmplifier_GET_Error: If table retrieval fails

    Example:
        >>> tables = await get_tables(auth, "integration-123", "MY_DB", "MY_SCHEMA")
        >>> for table in tables.response:
        ...     print(table['tableName'])
    """

    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/byos/accounts/{integration_id}/databases/{database}/schemas/{schema}/objects"

    params = {"page": page, "rows": rows}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        params=params,
        session=session,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise CloudAmplifier_GET_Error(entity_id=integration_id, res=res)

    return res
