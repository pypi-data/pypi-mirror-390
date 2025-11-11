__all__ = [
    "Fileset_GET_Error",
    "Fileset_CRUD_Error",
    "EmbedData_Type",
    "create_filesets_index",
    "embed_image",
    "get_fileset_by_id",
    "search_fileset_files",
    "get_data_file_by_id",
]

from typing import Literal, Optional

import httpx

from ..auth import DomoAuth
from ..base.exceptions import RouteError
from ..client import (
    get_data as gd,
    response as rgd,
)


class Fileset_GET_Error(RouteError):
    """Raised when fileset retrieval operations fail."""

    def __init__(
        self,
        fileset_id: Optional[str] = None,
        message: Optional[str] = None,
        res=None,
        **kwargs,
    ):
        super().__init__(
            message=message or "Fileset retrieval failed",
            entity_id=fileset_id,
            res=res,
            **kwargs,
        )


class Fileset_CRUD_Error(RouteError):
    """Raised when fileset create, update, or delete operations fail."""

    def __init__(
        self,
        operation: str,
        fileset_id: Optional[str] = None,
        message: Optional[str] = None,
        res=None,
        **kwargs,
    ):
        super().__init__(
            message=message or f"Fileset {operation} operation failed",
            entity_id=fileset_id,
            res=res,
            **kwargs,
        )


@gd.route_function
async def create_filesets_index(
    auth: DomoAuth,
    index_id: str,
    embedding_model: str = "domo.domo_ai.domo-embed-text-multilingual-v1:cohere",
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    session: httpx.AsyncClient | None = None,
    parent_class: Optional[str] = None,
) -> rgd.ResponseGetData:
    """Creates a new vectorDB index."""

    url = f"{auth.domo_instance}.domo.com/api/recall/v1/indexes"

    payload = {
        "indexId": index_id,
        "embeddingModel": embedding_model,
    }
    res = await gd.get_data(
        url,
        method="POST",
        body=payload,
        auth=auth,
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if not res.is_success:
        raise Fileset_CRUD_Error(operation="create index", res=res)

    return res


EmbedData_Type = Literal["base64"]


@gd.route_function
async def embed_image(
    auth: DomoAuth,
    body: Optional[dict] = None,
    image_data: Optional[str] = None,
    media_type: Optional[str] = None,
    data_type: EmbedData_Type = "base64",
    model: str = "domo.domo_ai",
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    session: httpx.AsyncClient | None = None,
) -> rgd.ResponseGetData:
    """
    Create an embedding for a base64 encoded image using Domo's AI services.
    """
    # Utility function is_valid_base64_image should be called by the orchestrator before this.
    # This route function assumes valid base64 data.

    api_url = f"https://{auth.domo_instance}.domo.com/api/ai/v1/embedding/image"

    body = body or {
        "input": [{"type": "", "mediaType": "", "data": ""}],
        "model": "",
    }
    if image_data:
        body["input"][0].update({"data": image_data})

    if media_type:
        body["input"][0].update({"mediaType": media_type})

    if data_type:
        body["input"][0].update({"type": data_type})

    if model:
        body.update({"model": model})

    res = await gd.get_data(
        auth=auth,
        url=api_url,
        method="POST",
        body=body,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
        parent_class=parent_class,
    )
    if not res.is_success:
        raise Fileset_CRUD_Error(operation="embed image", res=res)

    return res


@gd.route_function
async def get_fileset_by_id(
    auth: DomoAuth,
    fileset_id: str,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    session: httpx.AsyncClient | None = None,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/files/v1/filesets/{fileset_id}"
    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
    )

    if not res.is_success:
        raise Fileset_GET_Error(fileset_id=fileset_id, res=res)

    return res


@gd.route_function
async def search_fileset_files(
    auth: DomoAuth,
    domo_fileset_id: str,
    body: Optional[dict] = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    session: httpx.AsyncClient | None = None,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/files/v1/filesets/{domo_fileset_id}/files/search?directoryPath=&immediateChildren=true"

    if not body:
        # default body will pull all files within the given fileset_id
        body = {
            "fieldSort": [{"field": "created", "order": "DESC"}],
            "filters": [],
            "dateFilters": [],
        }

    res = await gd.get_data(
        auth=auth,
        method="POST",
        url=url,
        body=body,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
    )
    if not res.is_success:
        raise Fileset_GET_Error(fileset_id=domo_fileset_id, res=res)

    return res


@gd.route_function
async def get_data_file_by_id(
    auth: DomoAuth,
    file_id: str,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    session: httpx.AsyncClient | None = None,
) -> rgd.ResponseGetData:
    """
    Retrieves the content of a data file from Domo.
    """
    url = f"https://{auth.domo_instance}.domo.com/data/v1/data-files/{file_id}"
    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
        parent_class=parent_class,
    )
    if not res.is_success:
        raise Fileset_GET_Error(fileset_id=file_id, res=res)
    return res
