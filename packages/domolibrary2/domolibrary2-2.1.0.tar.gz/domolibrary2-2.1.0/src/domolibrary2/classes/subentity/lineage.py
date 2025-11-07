__all__ = [
    "DomoLineage_Link",
    "DomoLineageLink_Dataflow",
    "DomoLineageLink_Publication",
    "DomoLineageLink_Card",
    "DomoLineageLink_Dataset",
    "DomoLineageLinkTypeFactory_Enum",
    "DomoLineage_ParentTypeEnum",
    "DomoLineage",
    "DomoLineage_Page",
    "DomoLineage_Publication",
    "DomoLineage_Sandbox",
]

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

import httpx

from ...auth import DomoAuth
from ...base.base import DomoEnumMixin
from ...base.entities import DomoEntity
from ...base.exceptions import DomoError
from ...routes import datacenter as datacenter_routes
from ...utils import chunk_execution as dmce


@dataclass
class DomoLineage_Link(ABC):
    auth: DomoAuth = field(repr=False)
    type: str
    id: str

    entity: Any = field(repr=False)  # DomoDataset, DomoDataflow, DomoPublication

    parents: list["DomoLineage_Link"] = field(default_factory=list)
    children: list["DomoLineage_Link"] = field(default_factory=list)

    def __eq__(self, other):
        if other.__class__.__name__ != self.__class__.__name__:
            return False

        return self.id == other.id and self.type == other.type

    def __hash__(self):
        return hash((self.id, self.type))

    @staticmethod
    @abstractmethod
    async def get_entity(entity_id, auth):
        """
        Get the entity associated with this lineage link.
        This method should be implemented by subclasses to return the appropriate entity.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @classmethod
    @abstractmethod
    async def from_dict(cls, obj, auth):
        """
        Create a DomoLineage_Link instance from a JSON object.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def _init_children(self):
        if not self.children:
            return []

        self.children = [
            DomoLineageLinkTypeFactory_Enum[c["type"]].value(
                auth=self.auth, id=c["id"], type=c["type"], entity=None
            )
            for c in self.children
        ]
        return self.children

    def _init_parents(self):
        if not self.parents:
            return []

        self.parents = [
            DomoLineageLinkTypeFactory_Enum[p["type"]].value(
                auth=self.auth, id=p["id"], type=p["type"], entity=None
            )
            for p in self.parents
        ]
        return self.parents

    def __post_init__(self):
        if self.children:
            self._init_children()

        if self.parents:
            self._init_parents()


@dataclass
class DomoLineageLink_Dataflow(DomoLineage_Link):
    @staticmethod
    async def get_entity(
        entity_id, auth, session: httpx.AsyncClient = None, debug_api: bool = False
    ):
        from ..DomoDataflow import core as dmdf

        return await dmdf.DomoDataflow.get_by_id(dataflow_id=entity_id, auth=auth)

    @classmethod
    async def from_dict(cls, obj, auth):
        entity = await cls.get_entity(entity_id=obj["id"], auth=auth)

        return cls(
            id=obj["id"],
            auth=auth,
            type="DATAFLOW",
            entity=entity,
            children=obj.get("children", []),
            parents=obj.get("parents", []),
        )

    def __eq__(self, other):
        if not isinstance(other, DomoLineageLink_Dataflow):
            return False
        return self.id == other.id and self.type == other.type


@dataclass
class DomoLineageLink_Publication(DomoLineage_Link):
    def __eq__(self, other):
        return super().__eq__(self, other)

    @staticmethod
    async def get_entity(
        entity_id, auth, debug_api: bool = False, session: httpx.AsyncClient = None
    ):
        """
        Get the entity associated with this lineage link.
        This method should be implemented by subclasses to return the appropriate entity.
        """
        from .. import DomoPublish as dmpb

        return await dmpb.DomoPublication.get_by_id(
            publication_id=entity_id, auth=auth, session=session, debug_api=debug_api
        )

    @classmethod
    async def from_dict(cls, obj, auth):
        """
        Initialize a DomoLineage instance for a publication.
        """

        entity = await cls.get_entity(entity_id=obj["id"], auth=auth)

        return cls(
            id=obj["id"],
            auth=auth,
            type="PUBLICATION",
            entity=entity,
            children=obj.get("children", []),
            parents=obj.get("parents", []),
        )


@dataclass
class DomoLineageLink_Card(DomoLineage_Link):
    @staticmethod
    async def get_entity(
        entity_id, auth, debug_api: bool = False, session: httpx.AsyncClient = None
    ):
        """
        Get the entity associated with this lineage link.
        This method should be implemented by subclasses to return the appropriate entity.
        """
        from .. import DomoCard as dmcd

        return await dmcd.DomoCard.get_by_id(
            card_id=entity_id, auth=auth, session=session, debug_api=debug_api
        )

    @classmethod
    async def from_dict(cls, obj, auth):
        """
        Initialize a DomoLineage instance for a publication.
        """

        entity = await cls.get_entity(entity_id=obj["id"], auth=auth)

        return cls(
            id=obj["id"],
            auth=auth,
            type="CARD",
            entity=entity,
            children=obj.get("children", []),
            parents=obj.get("parents", []),
        )


@dataclass
class DomoLineageLink_Dataset(DomoLineage_Link):
    def __eq__(self, other):
        return super().__eq__(self, other)

    @staticmethod
    async def get_entity(
        entity_id, auth, debug_api: bool = False, session: httpx.AsyncClient = None
    ):
        """
        Get the entity associated with this lineage link.
        This method should be implemented by subclasses to return the appropriate entity.
        """
        from ..DomoDataset.dataset_default import DomoDataset_Default as dmds

        return await dmds.get_by_id(
            dataset_id=entity_id, auth=auth, session=session, debug_api=debug_api
        )

    @classmethod
    async def from_dict(cls, obj, auth):
        """
        Initialize a DomoLineage instance for a publication.
        """

        entity = await cls.get_entity(entity_id=obj["id"], auth=auth)

        return cls(
            id=obj["id"],
            auth=auth,
            type="DATA_SOURCE",
            entity=entity,
            children=obj.get("children", []),
            parents=obj.get("parents", []),
        )


class DomoLineageLinkTypeFactory_Enum(DomoEnumMixin, Enum):
    DATAFLOW = DomoLineageLink_Dataflow
    PUBLICATION = DomoLineageLink_Publication
    DATA_SOURCE = DomoLineageLink_Dataset
    CARD = DomoLineageLink_Card


class DomoLineage_ParentTypeEnum(DomoEnumMixin, Enum):
    DomoDataflow = "DATAFLOW"
    DomoPublication = "PUBLICATION"
    DomoDataset = "DATA_SOURCE"
    DomoDataset_Default = "DATA_SOURCE"
    FederatedDomoDataset = "DATA_SOURCE"
    DomoPage = "PAGE"
    DomoCard = "CARD"
    FederatedDomoCard = "CARD"
    DomoRepository = "REPOSITORY"
    DomoAppStudio = "DATA_APP"


@dataclass
class DomoLineage:
    auth: DomoAuth = field(repr=False)

    # parent_id: Any = field(repr=False)
    # parent_type: DomoLineage_ParentTypeEnum = field(repr=False)

    parent: Any = field(repr=False, default=None)

    lineage: list[DomoLineage_Link] = field(repr=False, default_factory=list)

    # raw_datacenter: dict = field(repr=False, default_factory=dict)

    @property
    def parent_type(self) -> DomoLineage_ParentTypeEnum:
        return DomoLineage_ParentTypeEnum[self.parent.__class__.__name__]

    @classmethod
    def from_parent(cls, parent, auth: DomoAuth = None):
        """
        Create a DomoLineage instance from a parent entity.
        The parent can be a DomoDataflow, DomoPublication, or DomoDataset.
        """
        return cls(
            auth=auth or parent.auth,
            # parent_id=parent.id,
            parent=parent,
        )

    async def get_parent(
        self, debug_api: bool = False, session: httpx.AsyncClient = None
    ):
        """
        Get the parent entity associated with this lineage.
        If the parent is not already set, it will be fetched based on the parent_id and parent_type.
        """
        if self.parent:
            return self.parent

        if not self.parent and (not self.parent_id or not self.parent_type):
            raise DomoError("Parent ID and type must be set to get the parent entity.")

        self.parent = await DomoLineageLinkTypeFactory_Enum[
            self.parent_type.value
        ].value.get_entity(
            entity_id=self.parent_id,
            auth=self.auth,
            session=session,
            debug_api=debug_api,
        )

        return self.parent

    async def get_datacenter_lineage(
        self,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        return_raw: bool = False,
    ):
        """queries the datacenter lineage api"""

        # parent_type = (
        #     self.parent_type.value
        #     if isinstance(self.parent_type, DomoLineage_ParentTypeEnum)
        #     else self.parent_type
        # )

        # auth = self.parent.auth if self.parent else self.auth

        res = await datacenter_routes.get_lineage_upstream(
            auth=self.parent.auth,
            entity_type=self.parent_type.value,
            entity_id=self.parent.id,
            session=session,
            debug_api=debug_api,
        )

        if return_raw:
            return res

        # dmcv.merge_dict(res.response, self.raw_datacenter)

        async def _get_entity_from_dict(obj):
            entity = DomoLineageLinkTypeFactory_Enum[obj["type"]].value  ## abc

            return await entity.from_dict(obj=obj, auth=self.auth)

        dx_classes = await dmce.gather_with_concurrency(
            *[
                _get_entity_from_dict(obj)
                for _, obj in res.response.items()
                if str(obj["id"]) != str(self.parent.id)
            ],
            n=10,
        )

        self.lineage.extend(dx_classes)

        return self.lineage

    async def get_federated_lineage(
        self,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        return_raw: bool = False,
        parent_auth: DomoAuth = None,
        parent_auth_retrieval_fn: Callable = None,
        debug_num_stacks_to_drop=3,
    ):
        if not self.parent and (
            # not self.parent_id or
            not self.parent_type
        ):
            raise ValueError(
                "Parent ID and parent type must be set to get the parent entity."
            )

        if parent_auth is None and parent_auth_retrieval_fn is not None:
            parent_auth = parent_auth_retrieval_fn(self)

        if not parent_auth:
            raise ValueError(
                "Parent auth must be provided to get the federated parent entity."
            )

        # await self.get_datacenter_lineage(
        #     session=session, debug_api=debug_api, return_raw=return_raw
        # )

        parent_entity = await self.parent.get_federated_parent(
            parent_auth=parent_auth, parent_auth_retrieval_fn=parent_auth_retrieval_fn
        )

        # Wrap parent entity in DomoLineageLink_Dataset
        parent_lineage_link = DomoLineageLink_Dataset(
            auth=parent_auth,
            id=parent_entity.id,
            type="DATA_SOURCE",
            entity=parent_entity,
            children=[],
            parents=[],
        )
        self.lineage.append(parent_lineage_link)

        # parent_entity.parent_auth = parent_auth

        parent_lineage = await parent_entity.Lineage.get(debug_api=debug_api)

        self.lineage.extend(parent_lineage)

        return self.lineage

    # async def _get_standard_lineage(
    #     self,
    #     session: httpx.AsyncClient = None,
    #     debug_api: bool = False,
    #     return_raw: bool = False,
    # ):
    #     return await self.get_datacenter_lineage(
    #         session=session, debug_api=debug_api, return_raw=return_raw
    #     )

    async def get(
        self,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        return_raw: bool = False,
        parent_auth: DomoAuth = None,
        parent_auth_retrieval_fn: Callable = None,
        is_recursive: bool = True,
    ):
        self.lineage = []  # reset lineage

        if not self.parent:
            print("no parent")
            await self.get_parent()  # just in case Lineage instantiated without parent

        if self.parent.__class__.__name__ == "FederatedDomoDataset":
            await self.get_federated_lineage(
                parent_auth=parent_auth,
                parent_auth_retrieval_fn=parent_auth_retrieval_fn,
                session=session,
                debug_api=debug_api,
                return_raw=return_raw,
            )
        # parent_auth = parent_auth or if parent....
        ## if its federated do something else
        # await self.get_parent_content_details(parent_auth)

        else:
            await self.get_datacenter_lineage(
                session=session, debug_api=debug_api, return_raw=return_raw
            )

        if is_recursive:
            # recursively get lineage for all items in lineage
            all_lineage = await dmce.gather_with_concurrency(
                *[
                    lin.get(
                        session=session,
                        debug_api=debug_api,
                        return_raw=return_raw,
                        is_recursive=is_recursive,
                    )
                    for lin in self.lineage
                    if lin and hasattr(lin, "get")
                ],
                n=10,
            )

            # flatten list of lists
            flattened_lineage = [item for sublist in all_lineage for item in sublist]

            # add to self.lineage if not already present
            for lin in flattened_lineage:
                if lin and lin not in self.lineage:
                    self.lineage.append(lin)

        return self.lineage


@dataclass
class DomoLineage_Page(DomoLineage):
    cards: list[Any] = field(repr=False, default=None)

    @property
    def parent_type(self) -> DomoLineage_ParentTypeEnum:
        return DomoLineage_ParentTypeEnum.DomoPage

    async def get_cards(
        self,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        return_raw: bool = False,
    ):
        if not self.parent:
            from .. import DomoPage as dmpg

            self.parent = await dmpg.DomoPage.get_by_id(
                page_id=self.parent_id,
                auth=self.auth,
                debug_api=debug_api,
                session=session,
            )

        self.cards = await self.parent.get_cards()

        return self.cards

    async def get(
        self,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        return_raw: bool = False,
    ):
        await self.get_cards(
            debug_api=debug_api,
            session=session,
            # return_raw=return_raw
        )

        self.lineage = []

        cards_lineage = await dmce.gather_with_concurrency(
            *[
                card.Lineage.get(
                    session=session,
                    debug_api=debug_api,
                    # return_raw=return_raw
                )
                for card in self.cards
            ],
            n=10,
        )

        cards_lineage = [lin for lins in cards_lineage for lin in lins]

        if return_raw:
            return cards_lineage

        for lin in cards_lineage:
            if lin and [lin.id not in [s.id for s in self.lineage]]:
                self.lineage.append(lin)

        return self.lineage


@dataclass
class DomoLineage_Publication(DomoLineage):
    parent_type: DomoLineage_ParentTypeEnum = field(
        default=DomoLineage_ParentTypeEnum.DomoPublication, repr=False
    )

    datasets: list[Any] = field(repr=False, default=None)
    cards: list[Any] = field(repr=False, default=None)
    page: list[Any] = field(repr=False, default=None)
    unsorted: list[Any] = field(repr=False, default=None)

    async def get(
        self,
        is_suppress_errors: bool = False,
        return_raw: bool = False,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
    ):
        async def _get_lineage(
            pc: DomoEntity,
            session: httpx.AsyncClient = None,
            is_suppress_errors: bool = False,
            debug_api: bool = False,
        ):
            """
            Helper function to get lineage for a publication.
            """
            if not pc.entity.Lineage and not is_suppress_errors:
                raise NotImplementedError(
                    f"Lineage is not implemented for this entity type - {pc.entity.__class__.__name__}"
                )

            await pc.get_entity_by_id(entity_id=pc.entity_id, auth=pc.auth)

            return pc.entity.Lineage.get(session=session, debug_api=debug_api)

        session = session or httpx.AsyncClient()

        if not self.parent:
            from .. import DomoPublish as dmpb

            self.parent = await dmpb.DomoPublication.get_entity_by_id(
                entity_id=self.parent_id,
                auth=self.auth,
                session=session,
                debug_api=debug_api,
            )

        await self.parent.get_content(session=session, debug_api=debug_api)

        if return_raw:
            return self.parent.content

        lineage = await dmce.gather_with_concurrency(
            *[
                _get_lineage(
                    pc=pc,
                    is_suppress_errors=is_suppress_errors,
                    session=session,
                    debug_api=debug_api,
                )
                for pc in self.parent.content
                if pc
            ],
            n=10,
        )

        self.lineage = [ele for ele in lineage if ele]

        for ele in self.lineage:
            if ele.__class__.__name__ == "DomoDataset":
                if not self.datasets:
                    self.datasets = []
                self.datasets.append(ele)
            elif ele.__class__.__name__ == "DomoCard":
                if not self.cards:
                    self.cards = []
                self.cards.append(ele)
            elif ele.__class__.__name__ == "DomoPage":
                if not self.page:
                    self.page = []
                self.page.append(ele)
            else:
                if not self.unsorted:
                    self.unsorted = []
                self.unsorted.append(ele)

        if self.unsorted:
            print(
                f"Unsorted lineage items: {', '.join([ele.__class__.__name__ for ele in self.unsorted])}"
            )

        return self.lineage


@dataclass
class DomoLineage_Sandbox(DomoLineage):
    parent_type: DomoLineage_ParentTypeEnum = field(
        default=DomoLineage_ParentTypeEnum.DomoRepository, repr=False
    )
