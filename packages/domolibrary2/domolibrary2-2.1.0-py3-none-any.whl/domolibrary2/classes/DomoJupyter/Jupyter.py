from __future__ import annotations

from ...base import exceptions as dmde

__all__ = [
    "DJW_Search_Error",
    "DJW_InvalidClass",
    "DomoJupyterWorkspace",
    "DomoJupyterWorkspaces",
]

import datetime as dt
import os
from dataclasses import dataclass, field
from typing import Any

import httpx

from ...client import (
    auth as dmda,
)
from ...client.entities import DomoEntity, DomoManager
from ...routes import jupyter as jupyter_routes
from ...routes.jupyter import JupyterAPI_Error
from ...utils import (
    chunk_execution as dmce,
    files as defi,
)
from .. import DomoUser as dmdu
from ..DomoDataset import DomoDataset as dmds
from . import (
    Account as dmac,
)
from .Account import DomoJupyter_Account
from .Content import DomoJupyter_Content
from .DataSource import DomoJupyter_DataSource


class DJW_Search_Error(dmde.ClassError):
    def __init__(
        self,
        cls=None,
        cls_instance=None,
        search_name=None,
        message=None,
        domo_instance=None,
    ):
        super().__init__(
            cls=cls,
            cls_instance=cls_instance,
            message=message or f"unable to find {search_name}",
            entity_id=domo_instance
            or (cls_instance and cls_instance.auth.domo_instance),
        )


class DJW_InvalidClass(dmde.ClassError):
    def __init__(self, cls_instance, message):
        super().__init__(cls_instance=cls_instance, message=message)


@dataclass(eq=False)
class DomoJupyterWorkspace(DomoEntity):
    auth: dmda.DomoJupyterAuth = field(repr=False)
    id: str

    name: str
    description: str

    created_dt: dt.datetime
    updated_dt: dt.datetime

    owner: dict
    cpu: str
    memory: int

    last_run_dt: dt.datetime = None
    instances: list[dict] = None

    input_configuration: list[DomoJupyter_DataSource] = field(
        default_factory=lambda: []
    )
    output_configuration: list[DomoJupyter_DataSource] = field(
        default_factory=lambda: []
    )
    account_configuration: list[DomoJupyter_Account] = field(default_factory=lambda: [])
    content: list[DomoJupyter_Content] = field(default_factory=lambda: [])

    collection_configuration: list[dict] = None
    fileshare_configuration: list[dict] = None

    service_location: str = None
    service_prefix: str = None
    raw: dict

    def __post_init__(self):
        self._update_auth_params()

        self.account_configuration.sort()
        self.output_configuration.sort()
        self.input_configuration.sort()

    def _update_auth_params(self):
        """extracts service location and prefix from "instance" object"""

        if self.instances:
            res = jupyter_routes.parse_instance_service_location_and_prefix(
                self.instances[0], self.auth.domo_instance
            )
            self.service_location = res["service_location"]
            self.service_prefix = res["service_prefix"]

    @property
    def display_url(self):
        return f"https://{self.auth.domo_instance}.domo.com/ai-services/jupyter"

    def update_auth_to_jupyter_auth(self, jupyter_token: str):
        """
        interacting with jupyter notebook content requires an additional authentication against the jupyter server (jupyter_token)
        currently we must manually scrape the token from the browser
        """

        self._update_auth_params()

        if isinstance(self.auth, dmda.DomoJupyterAuth):
            pass

        elif isinstance(self.auth, dmda.DomoFullAuth):
            self.auth = dmda.DomoJupyterFullAuth.convert_auth(
                auth=self.auth,
                service_location=self.service_location,
                jupyter_token=jupyter_token,
                service_prefix=self.service_prefix,
            )

        elif isinstance(self.auth, dmda.DomoTokenAuth):
            self.auth = dmda.DomoJupyterTokenAuth.convert_auth(
                auth=self.auth,
                service_location=self.service_location,
                jupyter_token=jupyter_token,
                service_prefix=self.service_prefix,
            )

    @classmethod
    async def from_dict(
        cls,
        obj,
        auth,
        jupyter_token: str = None,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        is_use_default_account_class: bool = False,
        is_suppress_errors: bool = False,
    ):
        dj_workspace = cls(
            auth=auth,
            id=obj["id"],
            name=obj["name"],
            description=obj["description"],
            created_dt=obj["created"],
            updated_dt=obj["updated"],
            last_run_dt=obj.get("lastRun"),
            instances=obj["instances"],
            owner=obj["owner"],
            memory=obj["memory"],
            cpu=obj["cpu"],
            fileshare_configuration=obj["collectionConfiguration"],
            raw=obj,
        )

        if obj["outputConfiguration"]:
            dj_workspace.output_configuration = await dmce.gather_with_concurrency(
                *[
                    DomoJupyter_DataSource.from_dict(obj=oc, dj_workspace=dj_workspace)
                    for oc in obj["outputConfiguration"]
                ],
                n=10,
            )

        if obj["inputConfiguration"]:
            dj_workspace.input_configuration = await dmce.gather_with_concurrency(
                *[
                    DomoJupyter_DataSource.from_dict(obj=ic, dj_workspace=dj_workspace)
                    for ic in obj["inputConfiguration"]
                ],
                n=10,
            )

        if obj["accountConfiguration"]:
            dj_workspace.account_configuration = await dmce.gather_with_concurrency(
                *[
                    DomoJupyter_Account.from_dict(
                        obj=ac,
                        dj_workspace=dj_workspace,
                        debug_api=debug_api,
                        session=session,
                        is_use_default_account_class=is_use_default_account_class,
                        is_suppress_errors=is_suppress_errors,
                    )
                    for ac in obj["accountConfiguration"]
                ],
                n=10,
            )

        if jupyter_token:
            dj_workspace.update_auth_to_jupyter_auth(jupyter_token=jupyter_token)

        return dj_workspace

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "memory": int(self.memory),
            "cpu": self.cpu,
            "inputConfiguration": [
                confg.to_dict() for confg in self.input_configuration or []
            ],
            "outputConfiguration": [
                confg.to_dict() for confg in self.output_configuration or []
            ],
            "accountConfiguration": [
                confg.to_api() for confg in self.account_configuration or []
            ],
            "fileshareConfiguration": self.collection_configuration or [],
        }

    @classmethod
    async def get_by_id(
        cls,
        workspace_id,
        auth: dmda.DomoAuth,  # this API does not require the jupyter_token, but activities inside the workspace will require additional authentication
        jupyter_token=None,
        return_raw: bool = False,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        is_use_default_account_class: bool = False,
        is_suppress_errors: bool = False,
    ):
        res = await jupyter_routes.get_jupyter_workspace_by_id(
            workspace_id=workspace_id,
            auth=auth,
            session=session,
            debug_api=debug_api,
            parent_class=cls.__name__,
        )

        if return_raw:
            return res

        djw = await cls.from_dict(
            auth=auth,
            obj=res.response,
            jupyter_token=jupyter_token,
            session=session,
            debug_api=debug_api,
            is_use_default_account_class=is_use_default_account_class,
            is_suppress_errors=is_suppress_errors,
        )

        return djw


async def get_current_workspace(
    cls: DomoJupyterWorkspace,
    auth: dmda.DomoJupyterAuth,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
):
    workspace_id = os.getenv("DOMO_WORKSPACE_ID")

    if not workspace_id:
        raise DJW_Search_Error(
            cls=cls,
            message=f"workspace id {workspace_id} not found.  This only works in Domo's Jupyter Workspaces environment",
        )

    return await cls.get_by_id(
        workspace_id=workspace_id, auth=auth, debug_api=debug_api, session=session
    )


async def get_account_configuration(
    self: DomoJupyterWorkspace,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    is_suppress_errors: bool = False,
    is_use_default_account_class: bool = False,
):
    djw = await self.get_by_id(
        workspace_id=self.id,
        auth=self.auth,
        session=session,
        debug_api=debug_api,
        is_suppress_errors=is_suppress_errors,
        is_use_default_account_class=is_use_default_account_class,
    )
    self.account_configuration = djw.account_configuration

    return self.account_configuration


async def get_input_configuration(
    self: DomoJupyterWorkspace,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    is_suppress_errors: bool = False,
):
    djw = await self.get_by_id(
        workspace_id=self.id,
        auth=self.auth,
        session=session,
        debug_api=debug_api,
        is_suppress_errors=is_suppress_errors,
    )
    self.input_configuration = djw.input_configuration

    return self.input_configuration


async def get_output_configuration(
    self: DomoJupyterWorkspace,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    is_suppress_errors: bool = False,
):
    djw = await self.get_by_id(
        workspace_id=self.id,
        auth=self.auth,
        session=session,
        debug_api=debug_api,
        is_suppress_errors=is_suppress_errors,
    )
    self.output_configuration = djw.output_configuration

    return self.output_configuration


def _add_config(self, config, attribute):
    # print(config.alias)
    config_ls = getattr(self, attribute)

    if config in config_ls:
        for i, ex in enumerate(config_ls):
            if ex == config:
                config_ls[i] = config

    else:
        config_ls.append(config)

    config_ls.sort()


def add_config_input_datasource(self, dja_datasource: DomoJupyter_DataSource):
    if not isinstance(dja_datasource, DomoJupyter_DataSource):
        raise DJW_InvalidClass(
            message="must passs instance of DomoJupyter_DataSource", cls_instance=self
        )

    return self._add_config(dja_datasource, attribute="input_configuration")


def add_config_output_datasource(self, dja_datasource: DomoJupyter_DataSource):
    if not isinstance(dja_datasource, DomoJupyter_DataSource):
        raise DJW_InvalidClass(
            message="must passs instance of DomoJupyter_DataSource", cls_instance=self
        )
    return self._add_config(dja_datasource, attribute="output_configuration")


def add_config_account(self, dja_account: DomoJupyter_Account):
    if not isinstance(dja_account, DomoJupyter_Account):
        raise DJW_InvalidClass(
            message="must passs instance of DomoJupyter_Account", cls_instance=self
        )
    return self._add_config(dja_account, attribute="account_configuration")


@dataclass
class DomoJupyterWorkspaces(DomoManager):
    auth: dmda.DomoAuth
    workspaces: list[DomoJupyterWorkspace] = None

    parent: Any = None

    @classmethod
    def from_parent(cls, parent):
        return cls(parent=parent, auth=parent.auth)

    async def get(
        self,
        is_use_default_account_class: bool = False,
        is_suppress_errors: bool = False,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        return_raw: bool = False,
    ):
        res = await jupyter_routes.get_jupyter_workspaces(
            auth=self.auth,
            debug_api=debug_api,
            session=session,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

        if return_raw:
            return res

        self.workspaces = await dmce.gather_with_concurrency(
            *[
                DomoJupyterWorkspace.get_by_id(
                    auth=self.auth,
                    workspace_id=workspace["id"],
                    debug_api=debug_api,
                    session=session,
                    is_use_default_account_class=is_use_default_account_class,
                    is_suppress_errors=is_suppress_errors,
                )
                for workspace in res.response
            ],
            n=10,
        )

        return self.workspaces

    async def search_workspace_by_name(
        self,
        workspace_name: str,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        return_raw: bool = False,
        is_use_default_account_class: bool = False,
        is_suppress_errors: bool = False,
    ):
        res = await self.get(
            debug_api=debug_api,
            session=session,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            return_raw=True,
            is_suppress_errors=is_suppress_errors,
        )

        workspace = next(
            (
                workspace
                for workspace in res.response
                if workspace["name"].lower() == workspace_name.lower()
            ),
            None,
        )

        if not workspace:
            raise DJW_Search_Error(cls_instance=self, search_name=workspace_name)

        if return_raw:
            res.response = workspace
            return res

        return await DomoJupyterWorkspace.get_by_id(
            workspace_id=workspace["id"],
            auth=self.auth,
            session=session,
            debug_api=debug_api,
            is_use_default_account_class=is_use_default_account_class,
            is_suppress_errors=is_suppress_errors,
        )


def _test_config_duplicates(self, config_name):
    configuration = getattr(self, config_name)

    if len(set([cfg.alias.lower() for cfg in configuration])) == len(configuration):
        return None

    return f"aliases are not unique for {config_name}"


async def update_config(
    self,
    config: dict = None,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    debug_num_stacks_to_drop=2,
):
    config = config or self.to_dict()
    try:
        return await jupyter_routes.update_jupyter_workspace_config(
            auth=self.auth,
            workspace_id=self.id,
            config=config,
            parent_class=self.__class__.__name__,
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

    except dmde.DomoError as e:
        print(self._test_config_duplicates("account_configuration"))
        print(self._test_config_duplicates("output_configuration"))
        print(self._test_config_duplicates("input_configuration"))
        raise e from e


async def add_account(
    self,
    domo_account: dmac.DomoAccount,
    dja_account: Any = None,
    domo_user: dmdu.DomoUser = None,
    is_update_config: bool = True,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
):
    if not dja_account and not isinstance(domo_account, dmac.DomoAccount_Default):
        raise DJW_InvalidClass(
            message="must pass domo_account as class DomoAccount", cls_instance=self
        )

    dja_account = dja_account or DomoJupyter_Account(
        alias=domo_account.name, account_id=domo_account.id, dj_workspace=self
    )

    self.add_config_account(dja_account)

    if not is_update_config:
        return self.account_configuration

    retry = 0
    while retry <= 1:
        try:
            res = await self.update_config(debug_api=debug_api, session=session)

            if return_raw:
                return res

            account_obj = next(
                obj
                for obj in res.response["accountConfiguration"]
                if obj["alias"] == domo_account.name
            )

            return DomoJupyter_Account(
                account_id=account_obj["account_id"],
                alias=account_obj["alias"],
                dj_workspace=self,
                domo_account=domo_account,
            )

        except JupyterAPI_Error as e:
            share_user_id = (domo_user and domo_user.id) or (
                await self.auth.who_am_i()
            ).response["id"]

            await domo_account.Access.share(
                user_id=share_user_id,
                debug_api=debug_api,
                session=session,
            )

            if retry == 1:
                raise e from e

            retry += 1


async def add_input_dataset(
    self,
    domo_dataset: dmds.DomoDataset,
    domojupyter_ds: DomoJupyter_DataSource = None,
    domo_user: dmdu.DomoUser = None,
    is_update_config: bool = True,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
):
    """adds a domo_dataset or domojupyter_dataset to workspace and conditionally updates config"""
    if not domojupyter_ds and not isinstance(domo_dataset, dmds.DomoDataset):
        raise DJW_InvalidClass(
            message="must pass domo_dataset as class DomoDataset", cls_instance=self
        )

    if not domojupyter_ds:
        domojupyter_ds = DomoJupyter_DataSource(
            alias=domo_dataset.name, dataset_id=domo_dataset.id, dj_workspace=self
        )

    self.add_config_input_datasource(domojupyter_ds)

    if not is_update_config:
        return self.input_configuration

    retry = 0

    while retry <= 1:
        try:
            return await self.update_config(debug_api=debug_api, session=session)

        except JupyterAPI_Error as e:
            domo_user = domo_user or await dmdu.DomoUser.get_by_id(
                auth=self.auth,
                user_id=(await self.auth.who_am_i()).response["id"],
                debug_api=debug_api,
                session=session,
            )

            await domo_dataset.share(
                member=domo_user, auth=self.auth, debug_api=debug_api, session=session
            )

            if retry == 1:
                raise e from e

            retry += 1


async def add_output_dataset(
    self,
    domo_dataset: dmds.DomoDataset,
    domojupyter_ds: DomoJupyter_DataSource = None,
    domo_user: dmdu.DomoUser = None,
    is_update_config: bool = True,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
):
    if not domojupyter_ds and not isinstance(domo_dataset, dmds.DomoDataset):
        raise DJW_InvalidClass(
            message="must pass domo_dataset as class DomoDataset", cls_instance=self
        )

    domojupyter_ds = domojupyter_ds or DomoJupyter_DataSource(
        alias=domo_dataset.name, dataset_id=domo_dataset.id, dj_workspace=self
    )

    self.add_config_output_datasource(domojupyter_ds)

    if not is_update_config:
        return self.output_configuration

    retry = 0

    while retry <= 1:
        try:
            return await self.update_config(debug_api=debug_api, session=session)

        except JupyterAPI_Error as e:
            domo_user = domo_user or await dmdu.DomoUser.get_by_id(
                auth=self.auth,
                user_id=(await self.auth.who_am_i()).response["id"],
                debug_api=debug_api,
                session=session,
            )

            await domo_dataset.share(
                member=domo_user, auth=self.auth, debug_api=debug_api, session=session
            )

            if retry == 1:
                raise e from e

            retry += 1


async def get_content(
    self,
    debug_api: bool = False,
    return_raw: bool = False,
    is_recursive: bool = True,
    content_path: str = "",
):
    res = await jupyter_routes.get_content(
        auth=self.auth,
        debug_api=debug_api,
        content_path=content_path,
        debug_num_stacks_to_drop=2,
        parent_class=self.__class__.__name__,
        is_recursive=is_recursive,
        return_raw=return_raw,
    )

    if return_raw:
        return res

    self.content = [
        DomoJupyter_Content.from_dict(obj, auth=self.auth) for obj in res.response
    ]
    return self.content


async def download_workspace_content(
    self, base_export_folder=None, replace_folder: bool = True
) -> str:
    """retrieves content from Domo Jupyter Workspace and downloads to a local folder"""

    base_export_folder = base_export_folder or f"{self.auth.domo_instance}/{self.name}"

    all_content = await self.get_content()
    all_content = [
        content for content in all_content if content.file_type != "directory"
    ]
    defi.upsert_folder(base_export_folder, replace_folder=replace_folder)

    return [
        content.export(default_export_folder=base_export_folder)
        for content in all_content
    ]
