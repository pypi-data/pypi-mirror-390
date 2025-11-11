__all__ = ["to_dict", "AppDbDocument", "AppDbCollection", "AppDbCollections"]

import asyncio
import datetime as dt
import numbers
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Optional, list

import httpx

from ..auth import DomoAuth
from ..base.entities import DomoEntity
from ..routes import appdb as appdb_routes
from ..utils import (
    chunk_execution as dmce,
    convert as dlcv,
)


def to_dict(value):
    if hasattr(value, "to_dict"):
        return value.to_dict()

    if isinstance(value, dict):
        return {key: to_dict(v) for key, v in value.items()}

    if isinstance(value, list):
        return [to_dict(v) for v in value]

    if isinstance(value, numbers.Number):
        return value

    return str(value)


@dataclass
class AppDbDocument(DomoEntity):
    auth: Optional[DomoAuth] = field(repr=False)
    _id: Optional[str] = None
    _created_on_dt: Optional[datetime] = None
    _updated_on_dt: Optional[datetime] = None
    content: Optional[dict] = None
    _collection_id: Optional[str] = None
    _identity_columns: Optional[list[str]] = None

    def to_dict(self, custom_content_to_dict_fn: Optional[Callable] = None):
        self.update_config()

        s = {"id": self._id, "collectionId": self._collection_id}

        if custom_content_to_dict_fn:
            s.update({"content": custom_content_to_dict_fn(self.content)})

        else:
            for key, value in self.__dict__.items():
                if key.startswith("_") or key in ["auth"]:
                    continue

                s.update({key: to_dict(value)})

        return s

    def __eq__(self, other):
        if self.__class__.__name__ != other.__class__.__name__:
            return False

        if self._identity_columns:
            return all(
                getattr(self, col) == getattr(other, col)
                for col in self._identity_columns
            )

        return self._id == other._id

    @classmethod
    def from_dict(
        cls,
        auth: DomoAuth,
        content,
        new_cls,
        identity_columns,
        collection_id=None,
        document_id=None,
        metadata=None,
        created_on_dt=None,
        updated_on_dt=None,
    ):
        if metadata:
            collection_id = metadata.pop("collectionId")

            created_on_dt = dlcv.convert_string_to_datetime(metadata.pop("createdOn"))

            updated_on_dt = dlcv.convert_string_to_datetime(metadata.pop("updatedOn"))
            document_id = metadata["id"]

        return cls(
            auth=auth,
            _id=document_id,
            _created_on_dt=created_on_dt,
            _updated_on_dt=updated_on_dt,
            content=content,
            _collection_id=collection_id,
            _identity_columns=identity_columns or [],
        )

    @classmethod
    async def create_document(
        cls,
        content: dict,
        collection_id: str,
        auth: DomoAuth,
        session: httpx.AsyncClient,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        return_raw: bool = False,
    ):
        res = await appdb_routes.create_document(
            auth=auth,
            collection_id=collection_id,
            content=content,
            session=session,
            debug_api=debug_api,
            parent_class=cls.__name__,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

        if return_raw:
            return res

        return await cls.get_by_id(
            collection_id=collection_id, document_id=res.response["id"], auth=auth
        )

    async def update_document(
        self,
        content: Optional[dict] = None,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        debug_num_stacks_to_drop=1,
        return_raw: bool = False,
    ):
        res = await appdb_routes.update_document(
            auth=self.auth,
            collection_id=self._collection_id,
            document_id=self._id,
            content=content or self.to_dict()["content"],
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            session=session,
            parent_class=self.__class__.__name__,
        )

        if return_raw:
            return res

        return await AppDbDocument.get_by_id(
            collection_id=self._collection_id, document_id=self._id, auth=self.auth
        )

    @classmethod
    async def upsert(
        cls,
        auth: DomoAuth,
        collection_id,
        content: dict,
        identity_columns: list[str],
        session: httpx.AsyncClient | None = None,
        debug_api=False,
        debug_num_stacks_to_drop=3,
        return_raw: bool = False,
    ):
        domo_doc = None

        {f"content.{col}": content[col] for col in identity_columns}

        domo_collection = await AppDbCollection.get_by_id(
            auth=auth, collection_id=collection_id, return_raw=False
        )

        if domo_collection.domo_documents:
            domo_doc = next(
                (
                    doc
                    for doc in domo_collection.domo_documents
                    if all(
                        [
                            doc.content.get(col) == content.get(col)
                            for col in identity_columns
                        ]
                    )
                ),
                None,
            )

        if domo_doc:
            return await domo_doc.update_document(
                content=content,
                debug_api=debug_api,
                debug_num_stacks_to_drop=debug_num_stacks_to_drop,
                session=session,
                return_raw=return_raw,
            )

        return await cls.create_document(
            content=content,
            collection_id=collection_id,
            auth=auth,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            session=session,
            return_raw=return_raw,
        )

    @classmethod
    def _from_api(
        cls,
        auth: DomoAuth,
        obj,
        identity_columns: list[str] = None,
    ):
        content = obj.pop("content")

        return cls.from_dict(
            auth=auth,
            content=content,
            new_cls=cls,
            identity_columns=identity_columns,
            metadata=obj,
        )

    @classmethod
    def from_json(
        cls,
        auth: DomoAuth,
        collection_id: str,
        content: dict,
        identity_columns: list[str] = None,
    ):
        return cls.from_dict(
            auth=auth,
            content=content,
            new_cls=cls,
            identity_columns=identity_columns,
            collection_id=collection_id,
        )

    def update_config(self):
        self.content = {
            key: value
            for key, value in self.__dict__.items()
            if key not in ["auth", "content"] and not key.startswith("_")
        }
        return self.content

    @classmethod
    async def get_by_id(
        cls,
        collection_id: str,
        document_id: str,
        auth: DomoAuth,
        identity_columns=None,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        debug_num_stacks_to_drop=1,
        return_raw: bool = False,
    ):
        res = await appdb_routes.get_collection_document_by_id(
            auth=auth,
            collection_id=collection_id,
            document_id=document_id,
            parent_class=cls.__name__,
            debug_api=debug_api,
            session=session,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

        if return_raw:
            return res

        return cls._from_api(
            auth=auth,
            obj=res.response,
            identity_columns=identity_columns or [],
        )


@dataclass
async def create_document(
    cls,
    content: dict,
    collection_id: str,
    auth: DomoAuth,
    session: httpx.AsyncClient,
    debug_api: bool = False,
    debug_num_stacks_to_drop=2,
    return_raw: bool = False,
):
    res = await appdb_routes.create_document(
        auth=auth,
        collection_id=collection_id,
        content=content,
        session=session,
        debug_api=debug_api,
        parent_class=cls.__name__,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    return await cls.get_by_id(
        collection_id=collection_id, document_id=res.response["id"], auth=auth
    )


async def update_document(
    self,
    content: dict = None,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    debug_num_stacks_to_drop=1,
    return_raw: bool = False,
):
    res = await appdb_routes.update_document(
        auth=self.auth,
        collection_id=self._collection_id,
        document_id=self._id,
        content=content or self.to_dict()["content"],
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
        parent_class=self.__class__.__name__,
    )

    if return_raw:
        return res

    return res


@dataclass
class AppDbCollection(DomoEntity):
    auth: DomoAuth = field(repr=False)
    id: str
    name: str

    created_on_dt: dt.datetime
    updated_on_dt: dt.datetime

    schema: dict

    domo_documents: list[AppDbDocument] = None

    @classmethod
    def from_dict(cls, auth, obj):
        return cls(
            auth=auth,
            id=obj["id"],
            name=obj["name"],
            created_on_dt=dlcv.convert_string_to_datetime(obj["createdOn"]),
            updated_on_dt=dlcv.convert_string_to_datetime(obj["updatedOn"]),
            schema=obj["schema"],
        )

    @classmethod
    async def get_by_id(
        cls,
        auth: DomoAuth,
        collection_id,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        debug_num_stacks_to_drop=2,
        return_raw: bool = False,
    ):
        res = await appdb_routes.get_collection_by_id(
            auth=auth,
            collection_id=collection_id,
            parent_class=cls.__name__,
            debug_api=debug_api,
            session=session,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

        if return_raw:
            return res

        return cls.from_dict(auth=auth, obj=res.response)

    async def share_collection(
        self,
        domo_user=None,
        domo_group=None,
        permission: appdb_routes.Collection_Permission_Enum = appdb_routes.Collection_Permission_Enum.READ_CONTENT,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        session: httpx.AsyncClient = None,
    ):
        return await appdb_routes.modify_collection_permissions(
            collection_id=self.id,
            user_id=(domo_user and domo_user.id)
            or (await self.auth.who_am_i()).response["id"],
            group_id=domo_group and domo_group.id,
            permission=permission,
            auth=self.auth,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            session=session,
            parent_class=self.__class__.__name__,
        )

    async def query_documents(
        self,
        query: dict = None,
        return_raw: bool = False,
        try_auto_share=False,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        session: httpx.AsyncClient = None,
    ):
        documents = []
        loop_retry = 0
        while loop_retry <= 1 and not documents:
            try:
                res = await appdb_routes.get_documents_from_collection(
                    auth=self.auth,
                    collection_id=self.id,
                    query=query,
                    debug_api=debug_api,
                    debug_num_stacks_to_drop=debug_num_stacks_to_drop,
                    session=session,
                )

                documents = res.response

            except appdb_routes.AppDb_GET_Exception as e:
                if try_auto_share:
                    await self.share_collection(debug_api=debug_api)
                    await asyncio.sleep(2)

                loop_retry += 1

                if loop_retry > 1:
                    raise e

            if return_raw:
                return res

            self.domo_documents = await dmce.gather_with_concurrency(
                *[
                    AppDbDocument.get_by_id(
                        collection_id=self.id, document_id=doc["id"], auth=self.auth
                    )
                    for doc in documents
                ],
                n=60,
            )

            return self.domo_documents


async def share_collection(
    self,
    domo_user=None,
    domo_group=None,
    permission: appdb_routes.Collection_Permission_Enum = appdb_routes.Collection_Permission_Enum.READ_CONTENT,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 2,
    session: httpx.AsyncClient = None,
):
    return await appdb_routes.modify_collection_permissions(
        collection_id=self.id,
        user_id=(domo_user and domo_user.id)
        or (await self.auth.who_am_i()).response["id"],
        group_id=domo_group and domo_group.id,
        permission=permission,
        auth=self.auth,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
        parent_class=self.__class__.__name__,
    )


async def query_documents(
    self,
    query: dict = None,
    return_raw: bool = False,
    try_auto_share=False,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 2,
    session: httpx.AsyncClient = None,
):
    documents = []
    loop_retry = 0
    while loop_retry <= 1 and not documents:
        try:
            res = await appdb_routes.get_documents_from_collection(
                auth=self.auth,
                collection_id=self.id,
                query=query,
                debug_api=debug_api,
                debug_num_stacks_to_drop=debug_num_stacks_to_drop,
                session=session,
            )

            documents = res.response

        except appdb_routes.AppDb_GET_Exception as e:
            if try_auto_share:
                await self.share_collection(debug_api=debug_api)
                await asyncio.sleep(2)

            loop_retry += 1

            if loop_retry > 1:
                raise e

        if return_raw:
            return res

        self.domo_documents = await dmce.gather_with_concurrency(
            *[
                AppDbDocument.get_by_id(
                    collection_id=self.id, document_id=doc["id"], auth=self.auth
                )
                for doc in documents
            ],
            n=60,
        )

        return self.domo_documents


async def upsert(
    cls,
    auth: DomoAuth,
    collection_id,
    content: dict,
    identity_columns: list[str],
    session: httpx.AsyncClient = None,
    debug_api=False,
    debug_num_stacks_to_drop=3,
    return_raw: bool = False,
):
    domo_doc = None

    query = {f"content.{col}": content[col] for col in identity_columns}

    domo_collection = await AppDbCollection.get_by_id(
        auth=auth, collection_id=collection_id, return_raw=False
    )

    res = await domo_collection.query_documents(query=query, debug_api=debug_api)
    domo_doc = res[0] if res and len(res) > 0 else None

    if not domo_doc:
        return await cls.create_document(
            content=content,
            collection_id=collection_id,
            auth=auth,
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            return_raw=return_raw,
        )

    return await domo_doc.update_document(
        session=session, content=content, debug_api=debug_api, return_raw=return_raw
    )


@dataclass
class AppDbCollections:
    @classmethod
    async def get_collections(
        cls,
        auth: DomoAuth,
        datastore_id: Optional[str] = None,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        debug_num_stacks_to_drop=1,
        return_raw: bool = False,
    ):
        res = await appdb_routes.get_collections(
            auth=auth,
            datastore_id=datastore_id,
            parent_class=cls.__class__.__name__,
            debug_api=debug_api,
            session=session,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

        if return_raw:
            return res

        return await dmce.gather_with_concurrency(
            *[
                AppDbCollection.get_by_id(collection_id=obj["id"], auth=auth)
                for obj in res.response
            ],
            n=10,
        )
