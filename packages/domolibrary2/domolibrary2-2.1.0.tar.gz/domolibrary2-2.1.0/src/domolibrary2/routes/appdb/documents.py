"""
AppDb Document Functions

This module provides functions for managing Domo AppDb documents including
retrieval, creation, and update operations.

Functions:
    get_documents_from_collection: Get documents from a collection
    get_collection_document_by_id: Get a specific document by ID
    create_document: Create a new document in a collection
    update_document: Update an existing document
"""

__all__ = [
    "get_documents_from_collection",
    "get_collection_document_by_id",
    "create_document",
    "update_document",
]

from typing import Any, Optional

import httpx

from ...auth import DomoAuth
from ...client import (
    get_data as gd,
    response as rgd,
)
from .exceptions import AppDb_CRUD_Error, AppDb_GET_Error, SearchAppDb_NotFound


@gd.route_function
async def get_documents_from_collection(
    auth: DomoAuth,
    collection_id: str,
    query: Optional[dict[str, Any]] = None,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Get documents from a collection.

    Args:
        auth: Authentication object containing credentials and instance info
        collection_id: Unique identifier for the collection
        query: Optional query parameters for document filtering
        session: Optional httpx client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to drop in debug output
        parent_class: Optional parent class name for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing documents information

    Raises:
        AppDb_GET_Error: If documents retrieval fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/datastores/v2/collections/{collection_id}/documents/query"

    query = query or {}

    res = await gd.get_data(
        auth=auth,
        method="POST",
        url=url,
        body=query,
        parent_class=parent_class,
        debug_api=debug_api,
        session=session,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise AppDb_GET_Error(
            appdb_id=collection_id,
            message=f"unable to query documents in collection - {collection_id}",
            res=res,
        )

    return res


@gd.route_function
async def get_collection_document_by_id(
    auth: DomoAuth,
    collection_id: str,
    document_id: str,
    query: Optional[dict[str, Any]] = None,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Get a specific document by ID from a collection.

    Args:
        auth: Authentication object containing credentials and instance info
        collection_id: Unique identifier for the collection
        document_id: Unique identifier for the document
        query: Optional query parameters
        session: Optional httpx client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to drop in debug output
        parent_class: Optional parent class name for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing document information

    Raises:
        AppDb_GET_Error: If document retrieval fails
        SearchAppDb_NotFound: If document with specified ID doesn't exist
    """
    url = f"https://{auth.domo_instance}.domo.com/api/datastores/v1/collections/{collection_id}/documents/{document_id}"

    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        body=query,
        parent_class=parent_class,
        debug_api=debug_api,
        session=session,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        if res.status == 404:
            raise SearchAppDb_NotFound(
                search_criteria=f"document_id: {document_id} in collection: {collection_id}",
                res=res,
            )
        raise AppDb_GET_Error(appdb_id=document_id, res=res)

    return res


@gd.route_function
async def create_document(
    auth: DomoAuth,
    collection_id: str,
    content: dict[str, Any],
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Create a new document in a collection.

    Args:
        auth: Authentication object containing credentials and instance info
        collection_id: Unique identifier for the collection
        content: Document content to create
        session: Optional httpx client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to drop in debug output
        parent_class: Optional parent class name for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing created document information

    Raises:
        AppDb_CRUD_Error: If document creation fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/datastores/v1/collections/{collection_id}/documents"

    res = await gd.get_data(
        auth=auth,
        method="POST",
        url=url,
        body={"content": content},
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise AppDb_CRUD_Error(operation="create", appdb_id=collection_id, res=res)

    return res


@gd.route_function
async def update_document(
    auth: DomoAuth,
    collection_id: str,
    document_id: str,
    content: dict[str, Any],
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Update an existing document in a collection.

    Args:
        auth: Authentication object containing credentials and instance info
        collection_id: Unique identifier for the collection
        document_id: Unique identifier for the document to update
        content: Updated document content
        session: Optional httpx client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to drop in debug output
        parent_class: Optional parent class name for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing updated document information

    Raises:
        AppDb_CRUD_Error: If document update fails
        SearchAppDb_NotFound: If document with specified ID doesn't exist
    """
    url = f"https://{auth.domo_instance}.domo.com/api/datastores/v2/collections/{collection_id}/documents/{document_id}"

    res = await gd.get_data(
        auth=auth,
        method="PUT",
        url=url,
        body={"content": content},
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        if res.status == 404:
            raise SearchAppDb_NotFound(
                search_criteria=f"document_id: {document_id} in collection: {collection_id}",
                res=res,
            )
        raise AppDb_CRUD_Error(operation="update", appdb_id=document_id, res=res)

    return res
