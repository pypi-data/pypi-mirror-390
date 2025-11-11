"""a class based approach for interacting with Domo Datasets"""

__all__ = [
    "DatasetSchema_Types",
    "DomoDataset_Schema_Column",
    "DomoDataset_Schema",
    "DatasetSchema_InvalidSchemaError",
]

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import httpx
import pandas as pd

from ...base.entities import DomoSubEntity
from ...base.exceptions import ClassError
from ...routes import dataset as dataset_routes


class DatasetSchema_Types(Enum):
    STRING = "STRING"
    DOUBLE = "DOUBLE"
    LONG = "LONG"
    DATE = "DATE"
    DATETIME = "DATETIME"


class DatasetSchema_InvalidSchemaError(ClassError):
    def __init__(self, missing_columns: list[str]):
        message = (
            f"Dataset schema is missing required columns: {', '.join(missing_columns)}"
        )
        super().__init__(message=message)


@dataclass
class DomoDataset_Schema_Column:
    name: str
    id: str
    type: DatasetSchema_Types
    order: int = 0
    visible: bool = True
    upsert_key: bool = False
    tags: list[Any] = field(default_factory=list)  # DomoTag
    raw: dict = field(repr=False, default_factory=dict)

    def __eq__(self, other):
        return self.id == other.id

    def replace_tag(self, tag_prefix, new_tag):
        tags_copy = self.tags.copy()

        for tag in tags_copy:
            if tag.startswith(tag_prefix):
                self.tags.remove(tag)
                self.tags.append(new_tag)
                return True

    @classmethod
    def from_dict(cls, obj: dict):
        # from . import DomoTag as dmtg

        return cls(
            name=obj.get("name"),
            id=obj.get("id"),
            type=obj.get("type"),
            visible=obj.get("visible") or obj.get("isVisible") or True,
            upsert_key=obj.get("upsertKey") or False,
            order=obj.get("order") or 0,
            tags=obj.get("tags", []),  # Assuming tags are a list of objects
            raw=obj,
        )

    def to_dict(self):
        s = self.__dict__
        s["upsertKey"] = s.pop("upsert_key") if "upsert_key" in s else False
        s["tags"] = list(set(s["tags"]))  # Convert to set to remove duplicates
        return s


@dataclass
class DomoDataset_Schema(DomoSubEntity):
    """class for interacting with dataset schemas"""

    columns: list[DomoDataset_Schema_Column] = field(default_factory=list)

    # @classmethod
    # def from_parent(cls, parent):
    #     schema = cls(
    #         parent = parent,
    #         auth = parent.auth,
    #         parent_id = parent.id,
    #     )

    #     parent.Schema = schema
    #     return schema

    def to_dict(self):
        return {"columns": [col.to_dict() for col in self.columns]}

    async def get(
        self,
        debug_api: bool = False,
        return_raw: bool = False,  # return the raw response
    ) -> list[DomoDataset_Schema_Column]:
        """method that retrieves schema for a dataset"""

        res = await dataset_routes.get_schema(
            auth=self.auth, dataset_id=self.parent_id, debug_api=debug_api
        )

        self.raw = res.response

        if return_raw:
            return res

        self.columns = [
            DomoDataset_Schema_Column.from_dict(obj=obj)
            for obj in res.response.get("tables")[0].get("columns")
        ]

        return self.columns

    async def _test_missing_columns(
        self,
        df: pd.DataFrame,  # test dataframe to compare against
    ):
        await self.get()

        missing_columns = [
            col for col in df.columns if col not in [scol.name for scol in self.columns]
        ]

        if len(missing_columns) > 0:
            raise DatasetSchema_InvalidSchemaError(
                cls_instance=self.parent,
                missing_columns=missing_columns,
            )

        return True

    async def change_col_order(
        self,
        df: pd.DataFrame,
        session: httpx.AsyncClient = None,
        is_update_schema: bool = True,
        debug_api: bool = False,
    ):
        await self.get()

        if len(self.columns) != len(df.columns):
            raise Exception(
                f"Column count mismatch: schema has {len(self.columns)} columns, "
                f"but DataFrame has {len(df.columns)} columns. "
                f"Schema columns: {[col.name for col in self.columns]}, "
                f"DataFrame columns: {list(df.columns)}"
            )

        for index, col in enumerate(self.columns):
            col.order = col.order if col.order > 0 else index

        if not is_update_schema:
            return self.columns

        return await self.alter_schema(debug_api=debug_api, session=session)

    async def add_col(
        self,
        col: DomoDataset_Schema_Column,
        debug_prn: bool = False,
        is_update_schema: bool = True,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
    ):
        """Add a column to the schema."""
        if col in self.columns and debug_prn:
            print(
                f"column - {col.name} already in dataset {self.parent.name if self.parent else ''}"
            )

        if col not in self.columns:
            self.columns.append(col)

        if not is_update_schema:
            return self.columns

        return await self.update_schema(debug_api=debug_api, session=session)

    async def remove_col(
        self,
        col_to_remove: "DomoDataset_Schema_Column",
        debug_api: bool = False,
        is_update_schema: bool = True,
        session: httpx.AsyncClient = None,
    ):
        """Remove a column from the schema."""
        [
            self.columns.pop(index)
            for index, col in enumerate(self.columns)
            if col == col_to_remove
        ]

        if not is_update_schema:
            return self.columns

        return await self.update_schema(debug_api=debug_api, session=session)

    async def update_schema(
        self,
        return_raw: bool = False,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
    ):
        dataset_id = self.parent.id
        auth = self.parent.auth

        schema_obj = self.to_dict()

        res = await dataset_routes.alter_schema(
            dataset_id=dataset_id,
            auth=auth,
            schema_obj=schema_obj,
            debug_api=debug_api,
            session=session,
        )

        if return_raw:
            return res

        return await self.get()

    async def update_schema_descriptions(
        self,
        return_raw: bool = False,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
    ):
        dataset_id = self.parent.id
        auth = self.parent.auth

        schema_obj = self.to_dict()

        if return_raw:
            return schema_obj

        await dataset_routes.alter_schema_descriptions(
            dataset_id=dataset_id,
            auth=auth,
            schema_obj=schema_obj,
            debug_api=debug_api,
            session=session,
        )

        return await self.get()
