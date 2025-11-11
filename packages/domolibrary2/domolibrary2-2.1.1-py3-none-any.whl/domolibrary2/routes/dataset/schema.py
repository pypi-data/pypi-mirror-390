"""Dataset schema operations."""

import httpx
from dc_logger.decorators import LogDecoratorConfig, log_call

from ...auth import DomoAuth
from ...client import (
    get_data as gd,
    response as rgd,
)
from ...utils.logging import DomoEntityExtractor, DomoEntityResultProcessor
from .exceptions import Dataset_CRUD_Error, Dataset_GET_Error


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_schema(
    auth: DomoAuth,
    dataset_id: str,
    debug_api: bool = False,
    debug_num_stacks_to_drop=1,
    parent_class: str | None = None,
    session: httpx.AsyncClient | None = None,
) -> rgd.ResponseGetData:
    """retrieve the schema for a dataset"""

    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/datasources/{dataset_id}/schema/indexed?includeHidden=false"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
    )

    if not res.is_success:
        raise Dataset_GET_Error(dataset_id=dataset_id, res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def alter_schema(
    auth: DomoAuth,
    schema_obj: dict,
    dataset_id: str,
    debug_api: bool = False,
    parent_class: str | None = None,
    debug_num_stacks_to_drop: int = 1,
    session=httpx.AsyncClient(),
) -> rgd.ResponseGetData:
    """alters the schema for a dataset BUT DOES NOT ALTER THE DESCRIPTION"""

    url = f"https://{auth.domo_instance}.domo.com/api/data/v2/datasources/{dataset_id}/schemas"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="POST",
        body=schema_obj,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
    )

    if not res.is_success:
        raise Dataset_CRUD_Error(dataset_id=dataset_id, res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def alter_schema_descriptions(
    auth: DomoAuth,
    schema_obj: dict,
    dataset_id: str,
    debug_api: bool = False,
    parent_class: str | None = None,
    debug_num_stacks_to_drop: int = 1,
    session=httpx.AsyncClient(),
) -> rgd.ResponseGetData:
    """alters the description of the schema columns // as seen in DataCenter > Dataset > Schema"""

    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/datasources/{dataset_id}/wrangle"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="POST",
        body=schema_obj,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
    )

    if not res.is_success:
        raise Dataset_CRUD_Error(dataset_id=dataset_id, res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def set_dataset_tags(
    auth: DomoAuth,
    tag_ls: list[str],  # complete list of tags for dataset
    dataset_id: str,
    return_raw: bool = False,
    debug_api: bool = False,
    session: httpx.AsyncClient | None = None,
    parent_class: str | None = None,
    debug_num_stacks_to_drop: int = 1,
):
    """REPLACE tags on this dataset with a new list"""

    url = f"https://{auth.domo_instance}.domo.com/api/data/ui/v3/datasources/{dataset_id}/tags"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="POST",
        debug_api=debug_api,
        body=tag_ls,
        session=session,
        return_raw=return_raw,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if res.status == 200:
        res.set_response(
            response=f"Dataset {dataset_id} tags updated to [{', '.join(tag_ls)}]"
        )

    if not res.is_success:
        raise Dataset_CRUD_Error(dataset_id=dataset_id, res=res)

    return res
