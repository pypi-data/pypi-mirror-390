__all__ = [
    "Cards_API_Exception",
    "CardSearch_NotFoundError",
    "get_card_by_id",
    "get_kpi_definition",
    "Card_OptionalParts_Enum",
    "get_card_metadata",
    "generate_body_search_cards_only_apps_filter",
    "generate_body_search_cards_admin_summary",
    "search_cards_admin_summary",
]

from enum import Enum

import httpx
from dc_logger.decorators import LogDecoratorConfig, log_call

from ..auth import DomoAuth
from ..base import exceptions as de
from ..base.base import DomoEnumMixin
from ..client import (
    get_data as gd,
    response as rgd,
)
from ..utils.logging import DomoEntityExtractor, DomoEntityResultProcessor


class Cards_API_Exception(de.DomoError):  # noqa: N801
    def __init__(self, res, message=None):
        super().__init__(res=res, message=message)


class CardSearch_NotFoundError(de.DomoError):  # noqa: N801
    def __init__(
        self,
        card_id,
        domo_instance,
        function_name,
        status,
        parent_class: str = None,
        message=None,
    ):
        super().__init__(
            status=status,
            message=message or f"card {card_id} not found",
            domo_instance=domo_instance,
            function_name=function_name,
            parent_class=parent_class,
        )


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_card_by_id(
    card_id,
    auth: DomoAuth,
    optional_parts="certification,datasources,drillPath,owners,properties,domoapp",
    debug_api: bool = False,
    debug_num_stacks_to_drop=1,
    session: httpx.AsyncClient = None,
    parent_class: str = None,
    return_raw: bool = False,
):
    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/cards/"

    params = {"parts": optional_parts, "urns": card_id}

    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        session=session,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        debug_api=debug_api,
        params=params,
    )

    if not res.is_success:
        raise Cards_API_Exception(res=res)

    if return_raw:
        return res

    res.response = res.response[0]

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_kpi_definition(
    auth: DomoAuth,
    card_id: str,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    parent_class: str = None,
    debug_num_stacks_to_drop=2,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/content/v3/cards/kpi/definition"

    body = {"urn": card_id}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if not res.is_success and res.response == "Not Found":
        raise CardSearch_NotFoundError(
            card_id=card_id,
            status=res.status,
            domo_instance=auth.domo_instance,
            function_name="get_kpi_definition",
        )

    return res


class Card_OptionalParts_Enum(DomoEnumMixin, Enum):  # noqa: N801
    CERTIFICATION = "certification"
    DATASOURCES = "datasources"
    DOMOAPP = "domoapp"
    DRILLPATH = "drillPath"
    MASONDATA = "masonData"
    METADATA = "metadata"
    OWNERS = "owners"
    PROBLEMS = "problems"
    PROPERTIES = "properties"


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_card_metadata(
    auth: DomoAuth,
    card_id: str,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    parent_class: str = None,
    debug_num_stacks_to_drop=1,
    optional_parts: (
        list[Card_OptionalParts_Enum] | str
    ) = "metadata,certification,datasources,owners,problems,domoapp",
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/cards"

    params = {"urns": card_id, "parts": optional_parts}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        params=params,
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if not res.is_success:
        raise Cards_API_Exception(res=res)

    if res.is_success and len(res.response) == 0:
        raise CardSearch_NotFoundError(
            card_id=card_id,
            status=res.status,
            domo_instance=auth.domo_instance,
            parent_class=parent_class,
            function_name=res.traceback_details.function_name,
        )

    res.response = res.response[0]

    return res


def generate_body_search_cards_only_apps_filter():
    return {
        "includeCardTypeClause": True,
        "cardTypes": ["domoapp", "mason", "custom"],
        "ascending": True,
        "orderBy": "cardTitle",
    }


def generate_body_search_cards_admin_summary(
    page_ids: list[str] = None,
    #  searchPages: bool = True,
    card_search_text: str = None,
    page_search_text: str = None,
) -> dict:
    body = {"ascending": True, "orderBy": "cardTitle"}

    if card_search_text:
        body.update(
            {"cardTitleSearchText": card_search_text, "includeCardTitleClause": True}
        )

    if page_search_text:
        body.update(
            {
                "pageTitleSearchText": page_search_text,
                "includePageTitleClause": True,
                "notOnPage": False,
            }
        )

    if page_ids:
        body.update({"pageIds": page_ids})

    return body


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def search_cards_admin_summary(
    auth: DomoAuth,
    body: dict,
    maximum: int = None,
    optional_parts: str = "certification,datasources,drillPath,owners,properties,domoapp",
    debug_api: bool = False,
    debug_loop: bool = False,
    session: httpx.AsyncClient = None,
    wait_sleep: int = 3,
    parent_class: str = None,
    debug_num_stacks_to_drop: int = 1,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    limit = 100
    offset = 0
    loop_until_end = False if maximum else True

    url = f"https://{auth.domo_instance}.domo.com/api/content/v2/cards/adminsummary"

    params = {"parts": optional_parts}

    offset_params = {
        "offset": "skip",
        "limit": "limit",
    }

    def arr_fn(res):
        return res.response.get("cardAdminSummaries", [])

    res = await gd.looper(
        auth=auth,
        method="POST",
        url=url,
        arr_fn=arr_fn,
        offset_params=offset_params,
        offset_params_in_body=False,
        limit=limit,
        skip=offset,
        body=body,
        maximum=maximum,
        fixed_params=params,
        session=session,
        debug_api=debug_api,
        debug_loop=debug_loop,
        loop_until_end=loop_until_end,
        wait_sleep=wait_sleep,
        parent_class=parent_class,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if not res.is_success:
        raise Cards_API_Exception(res=res)

    return res
