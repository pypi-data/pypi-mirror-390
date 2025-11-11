__all__ = ["DomoBootstrap_Feature", "DomoBootstrap"]


from dataclasses import dataclass, field

import httpx

from ...auth import DomoAuth
from ...base import DomoManager
from ...routes import bootstrap as bootstrap_routes
from ...utils import chunk_execution as dmce
from .. import DomoPage as dmpg


@dataclass
class DomoBootstrap_Feature:
    id: int
    name: str
    label: str
    type: str
    purchased: bool
    enabled: bool

    @classmethod
    def from_dict(cls, obj: dict):  ## expects boostrap API
        bsf = cls(
            id=obj.get("id"),
            name=obj.get("name"),
            label=obj.get("label"),
            type=obj.get("type"),
            purchased=obj.get("purchased"),
            enabled=obj.get("enabled"),
        )
        return bsf


@dataclass
class DomoBootstrap(DomoManager):
    auth: DomoAuth = field(repr=False)

    customer_id: str = None
    page_ls: list[dmpg.DomoPage] = field(default=None)
    feature_ls: list[DomoBootstrap_Feature] = field(default=None)

    raw: dict = field(default=None)

    async def get(
        self,
        return_raw: bool = False,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        session: httpx.AsyncClient = None,
    ):
        """Get the bootstrap information for the domo_instance."""

        res = await bootstrap_routes.get_bootstrap(
            auth=self.auth,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=self.__class__.__name__,
            session=session,
        )

        self.raw = res.response

        if return_raw:
            return res

        return self.raw

    async def get_customer_id(
        self,
        return_raw: bool = False,
        debug_api: bool = False,
        debug_num_stacks_to_drop=3,
        session: httpx.AsyncClient = None,
    ):
        res = await bootstrap_routes.get_bootstrap_customerid(
            auth=self.auth,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            return_raw=return_raw,
            parent_class=self.__class__.__name__,
            session=session,
        )

        if return_raw:
            return res

        self.customer_id = res.response

        return self.customer_id

    async def get_pages(
        self,
        return_raw: bool = False,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        session: httpx.AsyncClient = None,
    ) -> list[dmpg.DomoPage]:
        res = await bootstrap_routes.get_bootstrap_pages(
            auth=self.auth,
            debug_api=debug_api,
            session=session,
            parent_class=self.__class__.__name__,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

        if return_raw:
            return res

        if not res.is_success:
            return None

        self.page_ls = await dmce.gather_with_concurrency(
            n=60,
            *[
                dmpg.DomoPage._from_bootstrap(page_obj, auth=self.auth)
                for page_obj in res.response
            ],
        )

        return self.page_ls

    async def get_features(
        self,
        debug_api: bool = False,
        return_raw: bool = False,
        debug_num_stacks_to_drop=2,
        session: httpx.AsyncClient = None,
    ):
        res = await bootstrap_routes.get_bootstrap_features(
            auth=self.auth,
            session=session,
            debug_api=debug_api,
            return_raw=return_raw,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=self.__class__.__name__,
        )

        if return_raw:
            return res

        feature_list = [DomoBootstrap_Feature.from_dict(obj) for obj in res.response]

        return feature_list

    async def is_feature_accountsv2_enabled(
        self,
        debug_api: bool = False,
        return_raw: bool = False,
        debug_num_stacks_to_drop=3,
        session: httpx.AsyncClient = None,
    ):
        res = await bootstrap_routes.get_bootstrap_features_is_accountsv2_enabled(
            auth=self.auth,
            session=session,
            return_raw=return_raw,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=self.__class__.__name__,
        )

        if return_raw:
            return res

        return res.response
