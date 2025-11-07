"""
Cloud Amplifier Exception Classes

This module contains all exception classes for Cloud Amplifier operations.
"""

__all__ = [
    "CloudAmplifier_GET_Error",
    "SearchCloudAmplifierNotFoundError",
    "CloudAmplifier_CRUD_Error",
    "Cloud_Amplifier_Error",
]

from typing import Optional

from ...base.exceptions import RouteError
from ...client import response as rgd


class CloudAmplifier_GET_Error(RouteError):
    """
    Raised when Cloud Amplifier integration retrieval operations fail.

    This exception is used for failures during GET operations on integrations,
    warehouses, databases, schemas, tables, and metadata retrieval.
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
                message = f"Failed to retrieve Cloud Amplifier integration {entity_id}"

    class SearchCloudAmplifierNotFoundError(RouteError):
        """
        Raised when Cloud Amplifier integration search operations return no results.
        """

        def __init__(
            self,
            search_criteria: str,
            res: Optional[rgd.ResponseGetData] = None,
            **kwargs,
        ):
            message = f"No Cloud Amplifier resources found matching: {search_criteria}"
            super().__init__(
                message=message,
                res=res,
                **kwargs,
            )


class SearchCloudAmplifierNotFoundError(RouteError):
    """
    Raised when Cloud Amplifier integration search operations return no results.

    This exception is used when searching for specific integrations, warehouses,
    databases, schemas, or tables that don't exist or when search criteria match nothing.
    """

    def __init__(
        self,
        search_criteria: str,
        res: Optional[rgd.ResponseGetData] = None,
        **kwargs,
    ):
        message = f"No Cloud Amplifier resources found matching: {search_criteria}"
        super().__init__(
            message=message,
            res=res,
            **kwargs,
        )


class CloudAmplifier_CRUD_Error(RouteError):
    """
    Raised when Cloud Amplifier integration create, update, or delete operations fail.

    This exception is used for failures during integration creation, modification,
    deletion, warehouse updates, and federated dataset conversion operations.
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
                message = (
                    f"Cloud Amplifier {operation} failed for integration {entity_id}"
                )
            else:
                message = f"Cloud Amplifier {operation} operation failed"

        super().__init__(
            message=message,
            entity_id=entity_id,
            res=res,
            **kwargs,
        )


class Cloud_Amplifier_Error(RouteError):
    """
    Legacy error class for Cloud Amplifier operations.

    .. deprecated::
    Use CloudAmplifier_GET_Error, SearchCloudAmplifierNotFoundError, or
        CloudAmplifier_CRUD_Error instead for more specific error handling.
    """

    def __init__(
        self,
        res: Optional[rgd.ResponseGetData] = None,
        account_id: str = "",
        message: str = "",
        **kwargs,
    ):
        super().__init__(res=res, message=message, entity_id=account_id, **kwargs)
