__all__ = [
    "DomoRepository",
    "DomoSandbox",
    # Sandbox Route Exceptions
    "Sandbox_GET_Error",
    "Sandbox_CRUD_Error",
]

import datetime as dt
from dataclasses import dataclass, field
from typing import Optional

import dateutil.parser as dtut
import httpx
import pandas as pd

from ..auth import DomoAuth
from ..base.entities import DomoEntity_w_Lineage, DomoManager
from ..routes import sandbox as sandbox_routes
from ..routes.sandbox import Sandbox_CRUD_Error, Sandbox_GET_Error
from .subentity import DomoLineage as dmdl


@dataclass
class DomoRepository(DomoEntity_w_Lineage):
    auth: DomoAuth = field(repr=False)
    id: str
    raw: dict = field(default_factory=dict, repr=False)

    name: str
    last_updated_dt: dt.datetime
    commit_dt: dt.datetime
    commit_version: str

    content_page_id_ls: Optional[list[str]] = None
    content_card_id_ls: Optional[list[str]] = None
    content_dataflow_id_ls: Optional[list[str]] = None
    content_view_id_ls: Optional[list[str]] = None

    def __post_init__(self):
        """Initialize lineage tracking for the repository."""
        self.lineage = dmdl.DomoLineage_Sandbox.from_parent(parent=self, auth=self.auth)

    @property
    def display_url(self):
        return f"https://{self.auth.domo_instance}.domo.com/admin/sandbox/repositories/{self.id}"

    @classmethod
    def from_dict(cls, auth: DomoAuth, obj: dict):
        """Create DomoRepository instance from API response dictionary.

        Args:
            auth: Authentication object
            obj: API response dictionary

        Returns:
            DomoRepository instance
        """
        return cls(
            auth=auth,
            id=obj["id"],
            raw=obj,
            name=obj["name"],
            content_page_id_ls=obj["repositoryContent"]["pageIds"],
            content_card_id_ls=obj["repositoryContent"]["cardIds"],
            content_dataflow_id_ls=obj["repositoryContent"]["dataflowIds"],
            content_view_id_ls=obj["repositoryContent"]["viewIds"],
            last_updated_dt=dtut.parse(obj["updated"]).replace(tzinfo=None),
            commit_dt=dtut.parse(obj["lastCommit"]["completed"]).replace(tzinfo=None),
            commit_version=obj["lastCommit"]["commitName"],
            lineage=None,
        )

    @classmethod
    async def get_by_id(
        cls,
        auth: DomoAuth,
        repository_id: str,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        return_raw: bool = False,
    ):
        """Get a repository by ID.

        Args:
            auth: Authentication object
            repository_id: Repository identifier
            session: Optional HTTP client session
            debug_api: Enable API debugging
            debug_num_stacks_to_drop: Stack frames to drop for debugging
            return_raw: Return raw response without processing

        Returns:
            DomoRepository instance

        Raises:
            Sandbox_GET_Error: If retrieval fails
        """
        res = await sandbox_routes.get_repo_from_id(
            auth=auth,
            repository_id=repository_id,
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=cls.__name__,
            return_raw=return_raw,
        )

        if return_raw:
            return res

        return cls.from_dict(obj=res.response, auth=auth)

    @classmethod
    async def get_entity_by_id(
        cls,
        auth: DomoAuth,
        entity_id: str,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
    ):
        """Internal method to get entity by ID (required by DomoEntity_w_Lineage).

        Args:
            auth: Authentication object
            entity_id: Entity identifier
            session: Optional HTTP client session
            debug_api: Enable API debugging
            debug_num_stacks_to_drop: Stack frames to drop for debugging

        Returns:
            DomoRepository instance
        """
        return await cls.get_by_id(
            auth=auth,
            repository_id=entity_id,
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

    def convert_lineage_to_dataframe(self, return_raw: bool = False) -> pd.DataFrame:
        flat_lineage_ls = self.Lineage._flatten_lineage()

        output_ls = [
            {
                "sandbox_id": self.id,
                "sandbox_name": self.name,
                "version": self.commit_version,
                "commit_dt": self.commit_dt,
                "last_updated_dt": self.last_updated_dt,
                "entity_type": row.get("entity_type"),
                "entity_id": row.get("entity_id"),
            }
            for row in flat_lineage_ls
        ]

        if return_raw:
            return output_ls

        return pd.DataFrame(output_ls)


@dataclass
class DomoSandbox(DomoManager):
    auth: DomoAuth = field(repr=False)

    repositories: Optional[list[DomoRepository]] = None

    async def get_repositories(
        self, debug_api: bool = False, session: httpx.AsyncClient = None
    ):
        res = await sandbox_routes.get_shared_repos(
            auth=self.auth, debug_api=debug_api, session=session, parent_class=self
        )

        self.repositories = [
            DomoRepository.from_dict(obj=obj, auth=self.auth) for obj in res.response
        ]

        return self.repositories

    async def get(self, debug_api: bool = False, session: httpx.AsyncClient = None):
        await self.get_repositories(debug_api=debug_api, session=session)

        return self.repositories
