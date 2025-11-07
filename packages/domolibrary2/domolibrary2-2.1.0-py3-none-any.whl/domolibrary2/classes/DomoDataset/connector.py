__all__ = ["DomoConnector", "DomoConnectors"]

import datetime as dt
from dataclasses import dataclass, field

import httpx

from ...auth import DomoAuth
from ...base.entities import DomoBase, DomoManager
from ...utils import convert as cd


@dataclass
class DomoConnector(DomoBase):
    id: str
    raw: dict = field(repr=False)
    label: str
    title: str
    sub_title: str
    description: str
    create_date: dt.datetime
    last_modified: dt.datetime
    publisher_name: str
    writeback_enabled: bool
    tags: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, obj: dict):
        return cls(
            id=obj.get("databaseId"),
            label=obj.get("label"),
            title=obj.get("title"),
            sub_title=obj.get("subTitle"),
            description=obj.get("description"),
            create_date=cd.convert_epoch_millisecond_to_datetime(obj.get("createDate")),
            last_modified=cd.convert_epoch_millisecond_to_datetime(
                obj.get("lastModified")
            ),
            publisher_name=obj.get("publisherName"),
            writeback_enabled=obj.get("writebackEnabled"),
            tags=obj.get("tags", []),
            capabilities=obj.get("capabilities", []),
            raw=obj,
        )


@dataclass
class DomoConnectors(DomoManager):
    auth: DomoAuth = field(repr=False)

    domo_connectors: list[DomoConnector] = field(default=None)

    async def get(
        self,
        search_text=None,
        additional_filters_ls=None,
        return_raw: bool = False,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        session: httpx.AsyncClient = None,
    ):
        from ...routes import datacenter as datacenter_routes

        res = await datacenter_routes.get_connectors(
            auth=self.auth,
            search_text=search_text,
            additional_filters_ls=additional_filters_ls,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            session=session,
            parent_class=self.__class__.__name__,
        )

        if return_raw:
            return res

        if len(res.response) == 0:
            self.domo_connectors = []

        self.domo_connectors = [DomoConnector.from_dict(obj) for obj in res.response]
        return self.domo_connectors
