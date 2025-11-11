"""Dataset query operations."""

import httpx
from dc_logger.decorators import LogDecoratorConfig, log_call

from ... import auth as dmda
from ...auth import DomoAuth
from ...client import (
    get_data as gd,
    response as rgd,
)
from ...utils.logging import DomoEntityExtractor, DomoEntityResultProcessor
from .exceptions import Dataset_CRUD_Error, DatasetNotFoundError, QueryRequestError


# typically do not use
@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def query_dataset_public(
    dev_auth: dmda.DomoDeveloperAuth,
    dataset_id: str,
    sql: str,
    session: httpx.AsyncClient,
    debug_api: bool = False,
    parent_class: str | None = None,
    debug_num_stacks_to_drop=1,
):
    """query for hitting public apis, requires client_id and secret authentication"""

    url = f"https://api.domo.com/v1/datasets/query/execute/{dataset_id}?IncludeHeaders=true"

    body = {"sql": sql}

    res = await gd.get_data(
        auth=dev_auth,
        url=url,
        method="POST",
        body=body,
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
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
async def query_dataset_private(
    auth: DomoAuth,
    dataset_id: str,
    sql: str,
    loop_until_end: bool = False,  # retrieve all available rows
    limit=100,  # maximum rows to return per request.  refers to PAGINATION
    skip=0,
    maximum=100,  # equivalent to the LIMIT or TOP clause in SQL, the number of rows to return total
    filter_pdp_policy_id_ls: list[int] | None = None,
    return_raw: bool = False,
    timeout: int = 10,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    parent_class: str | None = None,
    debug_loop: bool = False,
    debug_num_stacks_to_drop=1,
):
    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/execute/{dataset_id}"

    offset_params = {
        "offset": "offset",
        "limit": "limit",
    }

    def body_fn(skip, limit, body: dict[str, object] | None = None):
        body = body or {"sql": f"{sql} limit {limit} offset {skip}"}

        if filter_pdp_policy_id_ls:
            body.update(  # type: ignore
                {
                    "context": {
                        "dataControlContext": {
                            "filterGroupIds": filter_pdp_policy_id_ls,
                            "previewPdp": True,
                        }
                    }
                }
            )

        return body

    def arr_fn(res: rgd.ResponseGetData) -> list[dict]:
        rows_ls = res.response.get("rows", [])
        columns_ls: list[str] = res.response.get("columns", [])

        if not isinstance(columns_ls, list) or any(
            not isinstance(c, str) for c in columns_ls
        ):
            raise QueryRequestError(
                dataset_id=dataset_id,
                sql=sql,
                res=res,
                message=f"Unexpected 'columns' format: {columns_ls!r}",
            )

        output: list[dict] = []
        for row in rows_ls or []:
            # defensive: limit mapping to min shared length
            width = min(len(columns_ls), len(row))
            row_dict = {columns_ls[i]: row[i] for i in range(width)}
            # Optionally: if len(row) != len(columns_ls) you can log or raise
            output.append(row_dict)

        return output

    res = await gd.looper(
        auth=auth,
        method="POST",
        url=url,
        arr_fn=arr_fn,
        offset_params=offset_params,
        limit=limit,
        skip=skip,
        maximum=maximum,
        body_fn=body_fn,
        return_raw=return_raw,
        loop_until_end=loop_until_end,
        timeout=timeout,
        session=session,
        debug_loop=debug_loop,
        parent_class=parent_class,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if res.status == 404 and res.response == "Not Found":
        raise DatasetNotFoundError(
            dataset_id=dataset_id,
            res=res,
        )

    if res.status == 400 and res.response == "Bad Request":
        raise QueryRequestError(dataset_id=dataset_id, sql=sql, res=res)

    if not res.is_success:
        raise QueryRequestError(dataset_id=dataset_id, sql=sql, res=res)

    return res
