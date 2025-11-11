from __future__ import annotations

from dataclasses import dataclass, field

import httpx

from ...auth import DomoAuth
from ...base import DomoEntity_w_Lineage
from ...routes import dataflow as dataflow_routes
from ...utils import chunk_execution as dmce
from ..DomoJupyter import Jupyter as dmdj
from ..subentity import lineage as dmdl
from ..subentity.trigger import DomoTriggerSettings
from .action import DomoDataflow_Action
from .history import DomoDataflow_History

__all__ = [
    "DomoDataflow",
    "DomoDataflows",
]


@dataclass
class DomoDataflow(DomoEntity_w_Lineage):
    id: str
    auth: DomoAuth = field(repr=False)

    name: str = None
    owner: str = None
    description: str = None
    tags: list[str] = None
    actions: list[DomoDataflow_Action] = None

    version_id: int = None
    version_number: int = None
    versions: list[dict] = None  # list of DomoDataflow Versions

    jupyter_workspace_config: dict = None

    History: DomoDataflow_History = None  # class for managing the history of a dataflow
    TriggerSettings: DomoTriggerSettings = (
        None  # trigger configuration for dataflow execution
    )

    JupyterWorkspace: dmdj.DomoJupyterWorkspace = None

    @property
    def entity_type(self):
        return "DATAFLOW"

    def __post_init__(self):
        self.History = DomoDataflow_History(
            dataflow=self, dataflow_id=self.id, auth=self.auth
        )

        self.Lineage = dmdl.DomoLineage.from_parent(auth=self.auth, parent=self)

        # Initialize TriggerSettings if present in raw data
        if self.raw.get("triggerSettings"):
            self.TriggerSettings = DomoTriggerSettings.from_parent(
                parent=self, obj=self.raw["triggerSettings"]
            )

    @classmethod
    def from_dict(cls, obj, auth, version_id=None, version_number=None):
        domo_dataflow = cls(
            auth=auth,
            id=obj.get("id"),
            raw=obj,
            name=obj.get("name"),
            description=obj.get("description"),
            owner=obj.get("owner") or obj.get("responsibleUserId"),
            tags=obj.get("tags"),
            version_id=version_id,
            version_number=version_number,
            Lineage=None,
            Relations=None,
            TriggerSettings=None,  # Will be initialized in __post_init__
        )

        if obj.get("actions"):
            domo_dataflow.actions = [
                DomoDataflow_Action.from_dict(action, all_actions=domo_dataflow.actions)
                for action in obj.get("actions")
            ]

        return domo_dataflow

    @property
    def display_url(self):
        return f"https://{self.auth.domo_instance}.domo.com/datacenter/dataflows/{self.id}/details"

    @classmethod
    async def get_by_id(
        cls: DomoDataflow,
        dataflow_id: int,
        auth: DomoAuth,
        return_raw: bool = False,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        id=None,
    ):
        dataflow_id = dataflow_id or id
        res = await dataflow_routes.get_dataflow_by_id(
            auth=auth,
            dataflow_id=dataflow_id,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=cls.__name__,
            session=session,
        )

        if return_raw:
            return res

        if not res.is_success:
            return None

        return cls.from_dict(res.response, auth=auth)

    @classmethod
    async def get_entity_by_id(cls, auth, entity_id, **kwargs):
        return await cls.get_by_id(
            dataflow_id=entity_id, auth=auth, return_raw=False, **kwargs
        )

    async def get_definition(
        self,
        debug_api: bool = False,
        return_raw: bool = False,
        session: httpx.AsyncClient = None,
    ):
        res = await self.get_by_id(
            auth=self.auth,
            dataflow_id=self.id,
            return_raw=return_raw,
            session=session,
            debug_api=debug_api,
        )

        if return_raw:
            return res

        new_obj = res.__dict__

        # Update attributes of ClassB instance
        for key, value in new_obj.items():
            if hasattr(self, key):
                setattr(self, key, value)

        return self

    async def update_dataflow_definition(
        self,
        new_dataflow_definition,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        session: httpx.AsyncClient = None,
    ):
        await dataflow_routes.update_dataflow_definition(
            auth=self.auth,
            dataflow_id=self.id,
            dataflow_definition=new_dataflow_definition,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            session=session,
        )

        return await self.get_definition(return_raw=False)

    async def get_jupyter_config(
        self,
        return_raw: bool = False,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        session: httpx.AsyncClient = None,
    ):
        res = await dataflow_routes.search_dataflows_to_jupyter_workspaces(
            auth=self.auth,
            dataflow_id=self.id,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            session=session,
            parent_class=self.__class__.__name__,
            return_raw=return_raw,
        )

        if return_raw:
            return res

        self.jupyter_workspace = await dmdj.DomoJupyterWorkspace.get_by_id(
            auth=self.auth, workspace_id=res.response["workspaceId"]
        )

        self.jupyter_workspace_config = res.response
        self.jupyter_workspace_config["workspace_name"] = self.jupyter_workspace.name

        return self.jupyter_workspace

    async def execute(
        self: DomoDataflow,
        auth: DomoAuth = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
    ):
        return await dataflow_routes.execute_dataflow(
            auth=auth or self.auth,
            dataflow_id=self.id,
            parent_class=self.__class__.__name__,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

    @classmethod
    async def get_by_version_id(
        cls: DomoDataflow,
        auth: DomoAuth,
        dataflow_id: int,
        version_id: int,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        session: httpx.AsyncClient = None,
        return_raw: bool = False,
    ):
        res = await dataflow_routes.get_dataflow_by_id_and_version(
            auth=auth,
            dataflow_id=dataflow_id,
            version_id=version_id,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=cls.__name__,
            session=session,
        )

        if return_raw:
            return res

        domo_dataflow = cls.from_dict(
            res.response["dataFlow"],
            version_id=res.response["id"],
            version_number=res.response["versionNumber"],
            auth=auth,
        )

        return domo_dataflow

    async def get_versions(
        self: DomoDataflow,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        session: httpx.AsyncClient = None,
        return_raw: bool = False,
    ):
        res = await dataflow_routes.get_dataflow_versions(
            auth=self.auth,
            dataflow_id=self.id,
            debug_api=debug_api,
            session=session,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=self.__class__.__name__,
        )

        if return_raw:
            return res

        version_ids = [df_obj["id"] for df_obj in res.response]

        self.versions = await dmce.gather_with_concurrency(
            *[
                DomoDataflow.get_by_version_id(
                    dataflow_id=self.id,
                    version_id=version_id,
                    auth=self.auth,
                    session=session,
                    debug_api=debug_api,
                    debug_num_stacks_to_drop=debug_num_stacks_to_drop,
                )
                for version_id in version_ids
            ],
            n=10,
        )

        return self.versions


@dataclass
class DomoDataflows:
    auth: DomoAuth = field(repr=False)
    dataflows: list[DomoDataflow] = None

    async def get(
        self,
        return_raw: bool = False,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
    ):
        res = await dataflow_routes.get_dataflows(
            debug_api=debug_api,
            auth=self.auth,
            session=session,
        )

        if return_raw:
            return res

        return await dmce.gather_with_concurrency(
            *[
                DomoDataflow.get_by_id(auth=self.auth, dataflow_id=obj["id"])
                for obj in res.response
            ],
            n=10,
        )
