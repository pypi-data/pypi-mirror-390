"""a class based approach for interacting with Domo Datasets"""

__all__ = [
    "DomoDataset_Default",
]


import datetime as dt
from dataclasses import dataclass, field
from typing import ClassVar, Optional

import httpx

from ...auth import DomoAuth
from ...base.entities import DomoEntity_w_Lineage
from ...base.exceptions import ClassError
from ...routes import dataset as dataset_routes
from ...routes.dataset import (
    ShareDataset_AccessLevelEnum,
)
from ...utils import convert as dmcv
from ..subentity import (
    certification as dmdc,
    tags as dmtg,
)
from ..subentity.schedule import DomoSchedule
from . import (
    pdp as dmpdp,
    schema as dmdsc,
    stream as dmdst,
)
from .dataset_data import DomoDataset_Data


class DomoDataset_NoTransportType_Error(ClassError):
    """Raised when unable to determine the transport type of a dataset."""

    def __init__(self, cls_instance=None, message: str = None, **kwargs):
        if not message:
            message = "Unable to determine the transport type of the dataset."

        super().__init__(cls_instance=cls_instance, message=message, **kwargs)


@dataclass
class DomoDataset_Default(DomoEntity_w_Lineage):  # noqa: N801
    "interacts with domo datasets"

    id: str
    auth: DomoAuth = field(repr=False)

    display_type: str = ""
    data_provider_type: str = ""
    name: str = ""
    description: str = ""
    row_count: Optional[int] = None
    column_count: Optional[int] = None

    stream_id: Optional[int] = None
    cloud_id: Optional[str] = None

    last_touched_dt: Optional[dt.datetime] = None
    last_updated_dt: Optional[dt.datetime] = None
    created_dt: Optional[dt.datetime] = None

    owner: dict = field(default_factory=dict)
    formulas: dict = field(default_factory=dict)

    Data: Optional[DomoDataset_Data] = field(default=None, repr=False)
    Schema: Optional[dmdsc.DomoDataset_Schema] = field(default=None, repr=False)
    Stream: Optional[dmdst.DomoStream] = field(default=None, repr=False)
    Tags: Optional[dmtg.DomoTags] = field(default=None, repr=False)
    PDP: Optional[dmpdp.DatasetPdpPolicies] = field(default=None, repr=False)

    Certification: dmdc.DomoCertification = field(default=None, repr=False)

    # Lineage: dmdl.DomoLineage = field(default=None, repr=False)

    # Include selected computed properties in generic to_dict serialization
    __serialize_properties__: ClassVar[tuple] = ("display_url", "transport_type")

    @property
    def entity_type(self):
        return "DATASET"

    @property
    def Account(self):
        if self.Stream and self.Stream.Account:
            return self.Stream.Account
        return None

    @staticmethod
    def _is_federated(obj: dict) -> bool:
        """Heuristic: decide if a dataset JSON represents a federated (proxy) dataset."""

        dpt = obj.get("dataProviderType", "").upper()
        disp = obj.get("displayType", "").upper()

        has_hint = any(
            [
                bool(obj.get("federation")),
                bool(obj.get("federationData")),
                bool(obj.get("federatedDatasetId")),
                bool(obj.get("publisherDomain")),
                obj.get("isFederated") is True,
            ]
        )

        has_federate = any(["FEDERAT" in dpt, "FEDERAT" in disp])
        return has_hint or has_federate

    @property
    def transport_type(self) -> Optional[str]:
        """Get the transport type of the dataset if available.

        Returns None if transport type cannot be determined rather than raising an exception.
        This allows the property to be safely included in serialization.
        """
        if self.raw.get("transportType"):
            return self.raw.get("transportType").upper()

        if self.Stream and self.Stream.transport_type:
            return self.Stream.transport_type.upper()

        # Return None instead of raising to allow safe serialization
        return None

    @property
    def is_federated(self) -> bool:
        """Heuristic: decide if a dataset JSON represents a federated (proxy) dataset."""

        return self._is_federated(self.raw)

    @property
    def Schedule(self) -> "DomoSchedule":
        return self.Stream.Schedule if self.Stream and self.Stream.Schedule else None

    def __post_init__(self):
        super().__post_init__()

        # Lineage implemented by parent post init
        self.Data = DomoDataset_Data.from_parent(parent=self)
        self.Schema = dmdsc.DomoDataset_Schema.from_parent(parent=self)
        self.Tags = dmtg.DomoTags.from_parent(parent=self)

        # Only instantiate Stream if dataset has a stream_id
        if self.stream_id:
            self.Stream = self.Stream or dmdst.DomoStream.from_parent(
                parent=self, stream_id=self.stream_id
            )

        self.PDP = dmpdp.DatasetPdpPolicies.from_parent(parent=self)

        self.Certification = dmdc.DomoCertification.from_parent(parent=self)

        self.Relations = None

    @property
    def display_url(self) -> str:
        return f"https://{self.auth.domo_instance}.domo.com/datasources/{self.id}/details/overview"

    @classmethod
    def from_dict(
        cls,
        auth: DomoAuth,
        obj: dict,
        is_use_default_dataset_class: bool = True,
        new_cls=None,
        **kwargs,
    ) -> "DomoDataset_Default":
        if not is_use_default_dataset_class:
            if not new_cls:
                raise NotImplementedError(
                    "Must provide new_cls if not using default dataset class"
                )
            cls = new_cls

        formulas = obj.get("properties", {}).get("formulas", {}).get("formulas", {})

        ds = cls(
            auth=auth,
            id=obj.get("id") or obj.get("databaseId"),
            raw=obj,
            display_type=obj.get("displayType", ""),
            data_provider_type=obj.get("dataProviderType", ""),
            name=obj.get("name", ""),
            description=obj.get("description", ""),
            owner=obj.get("owner", {}),
            stream_id=obj.get("streamId", None),
            cloud_id=obj.get("cloudId", None),
            last_touched_dt=dmcv.convert_epoch_millisecond_to_datetime(
                obj.get("lastTouched")
            ),
            last_updated_dt=dmcv.convert_epoch_millisecond_to_datetime(
                obj.get("lastUpdated")
            ),
            created_dt=dmcv.convert_epoch_millisecond_to_datetime(obj.get("created")),
            row_count=int(obj.get("rowCount") or 0),
            column_count=int(obj.get("columnCount") or 0),
            formulas=formulas,
            Lineage=None,
            Relations=None,  # type: ignore
            **kwargs,
        )

        return ds

    @classmethod
    async def get_by_id(
        cls,
        auth: DomoAuth,
        dataset_id: str,
        debug_api: bool = False,
        return_raw: bool = False,
        session: httpx.AsyncClient | None = None,
        debug_num_stacks_to_drop: int = 2,
        is_use_default_dataset_class: bool = False,
        parent_class: Optional[str] = None,
        is_suppress_no_config: bool = False,
    ):
        """retrieves dataset metadata"""
        parent_class = parent_class or cls.__name__

        # self.logger.info(message=f"Getting dataset by ID: {dataset_id}")  # TO DO

        res = await dataset_routes.get_dataset_by_id(
            auth=auth,
            dataset_id=dataset_id,
            debug_api=debug_api,
            session=session,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=parent_class,
        )

        if return_raw:
            return res

        obj = res.response

        ds = cls.from_dict(
            obj=obj,
            auth=auth,
            new_cls=cls,
            is_use_default_dataset_class=is_use_default_dataset_class,
        )

        if ds.Stream:
            await ds.Stream.refresh(is_suppress_no_config=is_suppress_no_config)

        return ds

    @classmethod
    async def get_entity_by_id(cls, auth: DomoAuth, entity_id: str, **kwargs):
        return await cls.get_by_id(dataset_id=entity_id, auth=auth, **kwargs)

    async def delete(
        self,
        dataset_id: Optional[str] = None,
        auth: Optional[DomoAuth] = None,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
    ):
        dataset_id = dataset_id or self.id
        auth = auth or self.auth

        res = await dataset_routes.delete(
            auth=auth, dataset_id=dataset_id, debug_api=debug_api, session=session
        )

        return res

    async def share(
        self,
        member,  # DomoUser or DomoGroup
        auth: Optional[DomoAuth] = None,
        share_type: ShareDataset_AccessLevelEnum = ShareDataset_AccessLevelEnum.CAN_SHARE,
        is_send_email=False,
        debug_api: bool = False,
        debug_prn: bool = False,
        session: httpx.AsyncClient | None = None,
    ):
        # Import DomoGroup here to avoid circular imports
        from ..DomoGroup.core import DomoGroup

        body = dataset_routes.generate_share_dataset_payload(
            entity_type="GROUP" if isinstance(member, DomoGroup) else "USER",
            entity_id=int(member.id),
            access_level=share_type,
            is_send_email=is_send_email,
        )

        res = await dataset_routes.share_dataset(
            auth=auth or self.auth,
            dataset_id=self.id,
            body=body,
            session=session,
            debug_api=debug_api,
        )

        return res

    @classmethod
    async def create(
        cls,
        auth: DomoAuth,
        dataset_name: str,
        dataset_type: str = "api",
        schema: Optional[dict] = None,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        return_raw: bool = False,
    ) -> "DomoDataset_Default":
        schema = schema or {
            "columns": [
                {"name": "col1", "type": "LONG", "upsertKey": False},
                {"name": "col2", "type": "STRING", "upsertKey": False},
            ]
        }

        res = await dataset_routes.create(
            dataset_name=dataset_name,
            dataset_type=dataset_type,
            schema=schema,
            auth=auth,
            debug_api=debug_api,
            session=session,
        )

        if return_raw:
            return res

        dataset_id = res.response.get("dataSource").get("dataSourceId")

        return await cls.get_by_id(id=dataset_id, auth=auth)
