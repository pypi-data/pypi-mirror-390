from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import httpx

from ...auth import DomoAuth
from ...base import DomoEntity, DomoManager
from ...routes import stream as stream_routes
from ...routes.stream import Stream_CRUD_Error, Stream_GET_Error
from ...utils import chunk_execution as dmce
from ..subentity.schedule import DomoSchedule
from .stream_config import StreamConfig

# TYPE_CHECKING imports to avoid circular dependencies
if TYPE_CHECKING:
    from ..DomoAccount import DomoAccount

__all__ = [
    "DomoStream",
    "DomoStreams",
    # Stream Route Exceptions
    "Stream_GET_Error",
    "Stream_CRUD_Error",
]


@dataclass(eq=False)
class DomoStream(DomoEntity):
    """A class for interacting with a Domo Stream (dataset connector)"""

    id: str
    parent: Any = field(repr=False)  # DomoDataset

    transport_description: str = None
    transport_version: int = None
    update_method: str = None
    data_provider_name: str = None
    data_provider_key: str = None
    account_id: str = None
    account_display_name: str = None
    account_userid: str = None

    has_mapping: bool = False
    configuration: list[StreamConfig] = field(default_factory=list)
    configuration_tables: list[str] = field(default_factory=list)
    configuration_query: str = None

    Schedule: DomoSchedule = None  # DomoDataset_Schedule
    Account: DomoAccount = field(default=None, repr=False)  # Connector account

    def __post_init__(self):
        """Post-initialization to extract schedule if present"""
        self.extract_schedule_from_raw()

    def extract_schedule_from_raw(self):
        """Extract schedule from stream configuration if available"""

        if self.raw:
            self.Schedule = DomoSchedule.from_parent(parent=self, obj=self.raw)

        return self.Schedule

    @classmethod
    def from_parent(cls, parent, stream_id: str = None):
        return cls(
            parent=parent,
            id=stream_id or parent.raw.get("streamId"),
            raw=parent.raw,
            auth=parent.auth,
            Relations=None,
        )

    @property
    def dataset_id(self) -> str:
        return self.parent.id

    @property
    def entity_type(self):
        return "STREAM"

    @property
    def display_url(self):
        """Generate URL to view this stream in the Domo UI"""
        return f"https://{self.auth.domo_instance}.domo.com/datasources/{self.dataset_id}/details/data/table"

    @classmethod
    def from_dict(cls, auth, obj, parent: Any | None = None, **kwargs):  # DomoDataset
        data_provider = obj.get("dataProvider", {})
        transport = obj.get("transport", {})
        obj.get("dataSource", {})

        account = obj.get("account", {})

        sd = cls(
            auth=auth,
            parent=parent,  # Will be set by caller if needed
            id=obj.get("id") or kwargs.get("stream_id"),
            transport_description=transport.get("description"),
            transport_version=transport.get("version"),
            update_method=obj.get("updateMethod"),
            data_provider_name=data_provider.get("name"),
            data_provider_key=data_provider.get("key"),
            raw=obj,
            Relations=None,
            **{k: v for k, v in kwargs.items() if k != "stream_id"},
        )

        if account:
            sd.account_id = account.get("id")
            sd.account_display_name = account.get("displayName")
            sd.account_userid = account.get("userId")

        sd.configuration = [
            StreamConfig.from_json(
                obj=c_obj, data_provider_type=data_provider.get("key"), parent_stream=sd
            )
            for c_obj in obj.get("configuration", [])
        ]

        return sd

    def generate_config_rpt(self):
        res = {}

        for config in self.configuration:
            if config.stream_category != "default" and config.stream_category:
                obj = config.to_dict()
                res.update({obj["field"]: obj["value"]})

        return res

    async def refresh(
        self,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        is_suppress_no_config: bool = False,
    ):
        # Only refresh if stream has an ID (some datasets don't have streams)
        if not self.id:
            return self

        await self.get_account(
            force_refresh=True,
            debug_api=debug_api,
            session=session,
            is_suppress_no_config=is_suppress_no_config,
        )

        await super().refresh(
            debug_api=debug_api,
            session=session,
            is_suppress_no_config=is_suppress_no_config,
        )

        return self

    @classmethod
    async def get_by_id(
        cls,
        auth: DomoAuth,
        stream_id: str,
        return_raw: bool = False,
        debug_num_stacks_to_drop=2,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        is_retrieve_account: bool = True,
        is_suppress_no_config: bool = False,
    ):
        """Get a stream by its ID.

        Args:
            auth: Authentication object
            stream_id: Unique stream identifier
            return_raw: Return raw response without processing
            debug_num_stacks_to_drop: Stack frames to drop for debugging
            debug_api: Enable API debugging
            session: HTTP client session
            is_retrieve_account: If True and account_id is present, retrieve full Account object
            is_suppress_no_config: If True, suppress errors when account config is not found

        Returns:
            DomoStream instance or ResponseGetData if return_raw=True

        Raises:
            Stream_GET_Error: If stream retrieval fails
        """
        res = await stream_routes.get_stream_by_id(
            auth=auth,
            stream_id=stream_id,
            session=session,
            parent_class=cls.__name__,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            debug_api=debug_api,
        )

        if return_raw:
            return res

        stream = cls.from_dict(auth=auth, obj=res.response)

        # Retrieve Account if account_id is present
        if is_retrieve_account and stream.account_id:
            await stream.get_account(
                session=session,
                debug_api=debug_api,
                force_refresh=True,
                is_suppress_no_config=is_suppress_no_config,
            )
        return stream

    @classmethod
    async def get_entity_by_id(cls, entity_id: str, auth: DomoAuth, **kwargs):
        return await cls.get_by_id(stream_id=entity_id, auth=auth, **kwargs)

    @classmethod
    async def create(
        cls,
        cnfg_body,
        auth: DomoAuth = None,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
    ):
        return await stream_routes.create_stream(
            auth=auth, body=cnfg_body, session=session, debug_api=debug_api
        )

    async def update(
        self,
        cnfg_body,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
    ):
        res = await stream_routes.update_stream(
            auth=self.auth,
            stream_id=self.id,
            body=cnfg_body,
            session=session,
            debug_api=debug_api,
        )
        return res

    async def get_account(
        self,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        force_refresh: bool = False,
        is_suppress_no_config: bool = False,
    ) -> DomoAccount | None:
        """Retrieve the Account associated with this stream.

        Args:
            session: HTTP client session
            debug_api: Enable API debugging
            force_refresh: If True, refresh even if Account is already set
            is_suppress_no_config: If True, suppress errors when account config is not found

        Returns:
            DomoAccount instance or None if no account_id

        Example:
            >>> stream = await DomoStream.get_by_id(auth=auth, stream_id="123")
            >>> account = await stream.get_account()
            >>> print(f"Account: {account.name}")
        """

        if not self.account_id:
            return None

        if self.Account is not None and not force_refresh:
            return self.Account

        from ..DomoAccount import DomoAccount

        self.Account = await DomoAccount.get_by_id(
            auth=self.auth,
            account_id=self.account_id,
            session=session,
            debug_api=debug_api,
            is_use_default_account_class=False,
            is_suppress_no_config=is_suppress_no_config,
        )
        return self.Account


@dataclass
class DomoStreams(DomoManager):
    streams: list[DomoStream] = field(default=None)

    async def get(
        self,
        search_dataset_name: str = None,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
    ):
        from ...routes import datacenter as datacenter_routes

        res = await datacenter_routes.search_datasets(
            auth=self.auth,
            entity_type=datacenter_routes.Datacenter_Enum.DATASET.value,
            session=session,
            search_text=search_dataset_name,
            debug_api=debug_api,
            parent_class=self.__class__.__name__,
        )

        self.streams = await dmce.gather_with_concurrency(
            *[
                DomoStream.get_by_id(self.auth, stream_id=obj["streamId"])
                for obj in res.response
            ],
            n=10,
        )

        return self.streams

    async def upsert(
        self,
        cnfg_body,
        match_name=None,
        auth: DomoAuth = None,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
    ):
        from ...routes import datacenter as datacenter_routes

        res = await datacenter_routes.search_datasets(
            auth=auth or self.auth,
            entity_type=datacenter_routes.Datacenter_Enum.DATASET.value,
            session=session,
            search_text=match_name,
            debug_api=debug_api,
            parent_class=self.__class__.__name__,
        )
        datasets = res.response

        existing_ds = next((ds for ds in datasets if ds.name == match_name), None)

        if existing_ds:
            domo_stream = await DomoStream.get_by_id(
                auth=auth, stream_id=existing_ds.stream_id
            )

            return await domo_stream.update(
                cnfg_body,
                session=session,
                debug_api=False,
            )

        else:
            return await DomoStream.create(
                cnfg_body, auth=auth, session=session, debug_api=debug_api
            )
