__all__ = ["DomoDatacenter"]

from dataclasses import dataclass, field
from typing import Any, Union

import httpx

from ..auth import DomoAuth
from ..base.exceptions import DomoError
from ..routes import datacenter as datacenter_routes
from ..routes.datacenter import generate_search_datacenter_filter
from ..utils import chunk_execution as dmce


@dataclass
class DomoDatacenter:
    "class for quering entities in the datacenter"

    auth: DomoAuth = field(repr=False)

    async def search_datacenter(
        self,
        maximum: int = None,  # maximum number of results to return
        body: dict = None,  # either pass a body or generate a body in the function using search_text, entity_type, and additional_filters parameters
        search_text=None,
        # can accept one value or a list of values
        entity_type: Union[str, list] = "dataset",
        additional_filters_ls=None,
        return_raw: bool = False,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
    ) -> list[Any]:
        res = await datacenter_routes.search_datacenter(
            auth=self.auth,
            maximum=maximum,
            body=body,
            session=session,
            search_text=search_text,
            entity_type=entity_type,
            additional_filters_ls=additional_filters_ls,
            debug_api=debug_api,
            return_raw=return_raw,
        )

        if return_raw:
            return res

        return res.response

    async def search_datasets(
        self,
        maximum: int = None,  # maximum number of results to return
        search_text=None,
        # can accept one value or a list of values
        additional_filters_ls=None,
        return_raw: bool = False,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
    ) -> list[Any]:
        from . import DomoDataset as dmds

        json_list = await self.search_datacenter(
            maximum=maximum,
            search_text=search_text,
            entity_type=datacenter_routes.Datacenter_Enum.DATASET.value,
            additional_filters_ls=additional_filters_ls,
            return_raw=return_raw,
            session=session,
            debug_api=debug_api,
        )

        if return_raw or len(json_list) == 0:
            return json_list

        # return await dmce.gather_with_concurrency(
        #     n=60,
        #     *[
        #         dmds.DomoDataset.get_by_id(
        #             dataset_id=obj.get("databaseId"),
        #             auth=self.auth,
        #             debug_api=debug_api,
        #             session=session,
        #         )
        #         for obj in json_list
        #     ],
        # )

        return [
            dmds.DomoDataset.from_dict(
                obj=obj,
                auth=self.auth,
                # debug_api=debug_api,
                # session=session,
            )
            for obj in json_list
        ]

    async def get_accounts(
        self,
        maximum: int = None,  # maximum number of results to return
        # can accept one value or a list of values
        search_text: str = None,  # will search for "search_text" in account.name (do not pass wildcards
        additional_filters_ls=None,
        return_raw: bool = False,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
    ) -> list[Any]:
        """search Domo Datacenter account api.
        Note: at the time of this writing 7/18/2023, the datacenter api does not support searching accounts by name
        """

        from . import DomoAccount as dmac

        additional_filters_ls = additional_filters_ls or []

        if search_text:
            # if search_text is provided, we will add a filter to the additional_filters_ls
            # this will not work with the datacenter api, but it is here for consistency with other search functions
            additional_filters_ls.append(
                generate_search_datacenter_filter(
                    "displayName",
                    search_text,
                )
            )

        json_list = await self.search_datacenter(
            maximum=maximum,
            entity_type=datacenter_routes.Datacenter_Enum.ACCOUNT.value,
            additional_filters_ls=additional_filters_ls,
            return_raw=return_raw,
            session=session,
            debug_api=debug_api,
        )

        if return_raw or len(json_list) == 0:
            return json_list

        if search_text:
            json_list = [
                obj
                for obj in json_list
                if search_text.lower() in obj.get("displayName", "").lower()
            ]

        domo_account_ls = [
            dmac.DomoAccount.from_dict(obj, auth=self.auth) for obj in json_list
        ]

        return domo_account_ls

    async def search_cards(
        self,
        maximum: int = None,  # maximum number of results to return
        search_text=None,
        # can accept one value or a list of values
        additional_filters_ls=None,
        return_raw: bool = False,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        is_suppress_errors: bool = False,
    ) -> list[Any]:
        from . import DomoCard as dmc

        json_list = await self.search_datacenter(
            maximum=maximum,
            search_text=search_text,
            entity_type=datacenter_routes.Datacenter_Enum.CARD.value,
            additional_filters_ls=additional_filters_ls,
            return_raw=return_raw,
            session=session,
            debug_api=debug_api,
        )

        if return_raw or len(json_list) == 0:
            return json_list

        return await dmce.gather_with_concurrency(
            n=60,
            *[
                dmc.DomoCard.get_by_id(
                    card_id=obj.get("databaseId"),
                    auth=self.auth,
                    debug_api=debug_api,
                    session=session,
                    is_suppress_errors=is_suppress_errors,
                )
                for obj in json_list
            ],
        )

    async def get_cards_admin_summary(
        self,
        auth=DomoAuth,
        page_ids: list[str] = None,
        card_search_text: str = None,
        page_search_text: str = None,
        maximum: int = None,  # maximum number of results to return
        # can accept one value or a list of values
        return_raw: bool = False,
        debug_api: bool = False,
        debug_loop: bool = False,
        session: httpx.AsyncClient = None,
    ) -> list[Any]:
        """search Domo Datacenter card api."""

        from ..routes import card as card_routes
        from . import DomoCard as dmc

        search_body = card_routes.generate_body_search_cards_admin_summary(
            page_ids=page_ids,
            card_search_text=card_search_text,
            page_search_text=page_search_text,
        )

        res = await card_routes.search_cards_admin_summary(
            auth=self.auth,
            body=search_body,
            maximum=maximum,
            debug_api=debug_api,
            debug_loop=debug_loop,
            session=session,
            wait_sleep=5,
        )

        if return_raw or len(res.response) == 0:
            return res

        domo_account_ls = await dmce.gather_with_concurrency(
            n=60,
            *[dmc.DomoCard.from_dict(obj, auth=self.auth) for obj in res.response],
        )

        return domo_account_ls

    async def search_codeengine(
        self,
        maximum: int = None,  # maximum number of results to return
        search_text=None,
        # can accept one value or a list of values
        additional_filters_ls=None,
        return_raw: bool = False,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
    ) -> list[Any]:
        from .DomoCodeEngine import CodeEngine as dmceg

        res = await self.search_datacenter(
            maximum=maximum,
            search_text=search_text,
            entity_type=datacenter_routes.Datacenter_Enum.PACKAGE.value,
            additional_filters_ls=additional_filters_ls,
            return_raw=return_raw,
            session=session,
            debug_api=debug_api,
        )

        if return_raw or len(res) == 0:
            return res

        async def _get_current_version(auth, package_id):
            try:
                return await dmceg.DomoCodeEngine_Package.get_current_version_by_id(
                    auth=auth,
                    package_id=package_id,
                )

            except DomoError as e:
                print(e)
                return False

        package_ls = await dmce.gather_with_concurrency(
            *[
                _get_current_version(
                    auth=self.auth,
                    package_id=obj["uuid"],
                )
                for obj in res
                if obj.get("uuid")
            ],
            n=10,
        )

        return [package for package in package_ls if package]
