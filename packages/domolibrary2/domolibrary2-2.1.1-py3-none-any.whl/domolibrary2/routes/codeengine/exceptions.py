"""
CodeEngine Route Exception Classes

This module contains all exception classes used by codeengine route functions.

Exception Classes:
    CodeEngine_GET_Error: Raised when codeengine retrieval operations fail
    SearchCodeEngine_NotFound: Raised when codeengine search returns no results
    CodeEngine_CRUD_Error: Raised when codeengine create/update/delete operations fail
    CodeEngine_InvalidPackage: Raised when package validation fails
    CodeEngine_FunctionCallError: Raised when function call parameters are invalid
"""

from typing import Optional

from ...auth import DomoAuth
from ...base.exceptions import RouteError
from ...client import response as rgd


class CodeEngine_GET_Error(RouteError):
    """Raised when codeengine retrieval operations fail."""

    def __init__(
        self,
        entity_id: Optional[str] = None,
        res: Optional[rgd.ResponseGetData] = None,
        message: Optional[str] = None,
        **kwargs,
    ):
        if not message:
            if entity_id:
                message = f"Failed to retrieve codeengine package {entity_id}"
            else:
                message = "Failed to retrieve codeengine packages"

        super().__init__(message=message, entity_id=entity_id, res=res, **kwargs)


class SearchCodeEngineNotFoundError(RouteError):
    """Raised when codeengine search operations return no results."""

    def __init__(
        self,
        search_criteria: str,
        res: Optional[rgd.ResponseGetData] = None,
        **kwargs,
    ):
        message = f"No codeengine packages found matching: {search_criteria}"
        super().__init__(
            message=message,
            res=res,
            additional_context={"search_criteria": search_criteria},
            **kwargs,
        )


class CodeEngine_CRUD_Error(RouteError):
    """Raised when codeengine create, update, or delete operations fail."""

    def __init__(
        self,
        operation: str = "CRUD",
        entity_id: Optional[str] = None,
        res: Optional[rgd.ResponseGetData] = None,
        message: Optional[str] = None,
        **kwargs,
    ):
        if not message:
            message = f"CodeEngine {operation} operation failed"
        super().__init__(message=message, entity_id=entity_id, res=res, **kwargs)


class CodeEngineInvalidPackageError(RouteError):
    """Raised when package validation fails."""

    def __init__(
        self,
        message: str,
        auth: Optional[DomoAuth] = None,
        res: Optional[rgd.ResponseGetData] = None,
        **kwargs,
    ):
        # Extract domo_instance from auth if provided
        domo_instance = auth.domo_instance if auth else None
        super().__init__(
            message=message, domo_instance=domo_instance, res=res, **kwargs
        )


class CodeEngine_FunctionCallError(RouteError):
    """Raised when function call parameters are invalid."""

    def __init__(
        self,
        message: str,
        auth: Optional[DomoAuth] = None,
        res: Optional[rgd.ResponseGetData] = None,
        **kwargs,
    ):
        # Extract domo_instance from auth if provided
        domo_instance = auth.domo_instance if auth else None
        super().__init__(
            message=message, domo_instance=domo_instance, res=res, **kwargs
        )
