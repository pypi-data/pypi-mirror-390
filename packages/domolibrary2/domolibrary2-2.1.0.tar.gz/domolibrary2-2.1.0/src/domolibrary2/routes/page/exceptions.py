"""
Page Exception Classes

This module contains all exception classes for page operations.
"""

__all__ = [
    "Page_GET_Error",
    "SearchPageNotFoundError",
    "Page_CRUD_Error",
    "PageSharing_Error",
]

from typing import Optional

from ...base.exceptions import RouteError
from ...client import response as rgd


class Page_GET_Error(RouteError):
    """Raised when page retrieval operations fail."""

    def __init__(
        self,
        page_id: Optional[str] = None,
        message: Optional[str] = None,
        res: Optional[rgd.ResponseGetData] = None,
        **kwargs,
    ):
        super().__init__(
            message=message or "Page retrieval failed",
            entity_id=page_id,
            res=res,
            **kwargs,
        )


class SearchPageNotFoundError(RouteError):
    """Raised when page search operations return no results."""

    def __init__(
        self,
        message: Optional[str] = None,
        search_criteria: Optional[str] = None,
        res: Optional[rgd.ResponseGetData] = None,
        **kwargs,
    ):
        super().__init__(
            message=message or f"No pages found matching: {search_criteria}",
            res=res,
            additional_context={"search_criteria": search_criteria},
            **kwargs,
        )


class Page_CRUD_Error(RouteError):
    """Raised when page create, update, or delete operations fail."""

    def __init__(
        self,
        message: Optional[str] = None,
        operation: Optional[str] = None,
        page_id: Optional[str] = None,
        res=None,
        **kwargs,
    ):
        super().__init__(
            message=message or f"Page {operation} operation failed",
            entity_id=page_id,
            res=res,
            **kwargs,
        )


class PageSharing_Error(RouteError):
    """Raised when page sharing operations fail."""

    def __init__(
        self,
        message: Optional[str] = None,
        operation: Optional[str] = None,
        page_id: Optional[str] = None,
        res: Optional[rgd.ResponseGetData] = None,
        **kwargs,
    ):
        super().__init__(
            message=message or f"Page sharing {operation} failed",
            entity_id=page_id,
            res=res,
            **kwargs,
        )
