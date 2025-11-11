__all__ = ["UserAttribute", "UserAttributes"]

import datetime as dt
from dataclasses import dataclass, field
from typing import Any, Optional

import httpx

from ...auth import DomoAuth
from ...base import DomoEntity, DomoManager
from ...routes.instance_config import user_attributes as user_attribute_routes
from ...routes.instance_config.user_attributes import (
    UserAttributes_CRUD_Error,
    UserAttributes_GET_Error,
)


@dataclass(eq=False)
class UserAttribute(DomoEntity):
    """utility class that absorbs many of the domo instance configuration methods"""

    auth: DomoAuth = field(repr=False)
    id: str
    name: str
    description: str

    issuer_type: user_attribute_routes.UserAttributes_IssuerType
    customer_id: str
    value_type: str

    validator: str
    validator_configuration: None

    security_voter: str
    custom: bool

    @property
    def display_url(self):
        return f"https://{self.auth.domo_instance}.domo.com/admin/governance/attribute-management"

    @classmethod
    def from_dict(cls, auth: DomoAuth, obj: dict[str, Any]):
        return cls(
            auth=auth,
            id=obj["key"],
            name=obj["title"],
            description=obj["description"],
            issuer_type=user_attribute_routes.UserAttributes_IssuerType(
                obj["keyspace"]
            ),
            customer_id=obj["context"],
            value_type=obj["valueType"],
            validator=obj["validator"],
            validator_configuration=obj["validatorConfiguration"],
            security_voter=obj["securityVoter"],
            custom=obj["custom"],
            raw=obj,
        )

    @classmethod
    async def get_by_id(
        cls,
        auth: DomoAuth,
        entity_id: str,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        return_raw: bool = False,
    ):
        res = await user_attribute_routes.get_user_attribute_by_id(
            auth=auth,
            entity_id=entity_id,
            session=session,
            debug_api=debug_api,
            parent_class=cls.__name__,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

        if return_raw:
            return res
        return cls.from_dict(obj=res.response, auth=auth)

    async def update(
        self,
        name=None,
        description=None,
        issuer_type: Optional[user_attribute_routes.UserAttributes_IssuerType] = None,
        data_type: Optional[str] = None,
        security_voter=None,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
    ):
        await user_attribute_routes.update_user_attribute(
            auth=self.auth,
            attribute_id=self.id,
            name=name,
            description=description,
            issuer_type=issuer_type,
            data_type=data_type,
            security_voter=security_voter,
            session=session,
            debug_api=debug_api,
            parent_class=self.__class__.__name__,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

        new = await UserAttribute.get_by_id(entity_id=self.id, auth=self.auth)

        [setattr(self, key, value) for key, value in new.__dict__.items()]

        return self


async def update(
    self: UserAttribute,
    name=None,
    description=None,
    issuer_type: Optional[user_attribute_routes.UserAttributes_IssuerType] = None,
    data_type: Optional[str] = None,
    security_voter=None,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop=2,
):
    await user_attribute_routes.update_user_attribute(
        auth=self.auth,
        attribute_id=self.id,
        name=name,
        description=description,
        issuer_type=issuer_type,
        data_type=data_type,
        security_voter=security_voter,
        session=session,
        debug_api=debug_api,
        parent_class=self.__class__.__name__,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    new = await UserAttribute.get_by_id(entity_id=self.id, auth=self.auth)

    [setattr(self, key, value) for key, value in new.__dict__.items()]

    return self


@dataclass
class UserAttributes(DomoManager):
    auth: DomoAuth = field(repr=False)

    attributes: list[UserAttribute] = field(default_factory=list)

    async def get(
        self,
        issuer_type_ls: list[
            user_attribute_routes.UserAttributes_IssuerType
        ] = [],  # use `UserAttributes_IssuerType` enum
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        return_raw: bool = False,
    ):
        auth = self.auth

        res = await user_attribute_routes.get_user_attributes(
            auth=auth,
            session=session,
            issuer_type_ls=issuer_type_ls,
            debug_api=debug_api,
            parent_class=self.__class__.__name__,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

        if return_raw:
            return res

        self.attributes = [
            UserAttribute.from_dict(obj=obj, auth=auth) for obj in res.response
        ]
        return self.attributes

    async def create(
        self,
        attribute_id: str,
        name=None,
        description=f"updated via domolibrary {dt.datetime.now().strftime('%Y-%m-%d - %H:%M')}",
        data_type: str = "ANY_VALUE",
        security_voter="FULL_VIS_ADMIN_IDP",
        issuer_type: Optional[
            user_attribute_routes.UserAttributes_IssuerType
        ] = user_attribute_routes.UserAttributes_IssuerType.CUSTOM,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        return_raw: bool = False,
    ):
        auth = self.auth
        attribute_id = user_attribute_routes.clean_attribute_id(attribute_id)

        res = await user_attribute_routes.create_user_attribute(
            auth=auth,
            session=session,
            issuer_type=issuer_type,
            name=name,
            attribute_id=attribute_id,
            description=description,
            data_type=data_type,
            security_voter=security_voter,
            debug_api=debug_api,
            parent_class=self.__class__.__name__,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

        await self.get()

        if return_raw:
            return res

        return await UserAttribute.get_by_id(auth=auth, entity_id=attribute_id)


async def create(
    self: UserAttributes,
    attribute_id: str,
    name=None,
    description=f"updated via domolibrary {dt.datetime.now().strftime('%Y-%m-%d - %H:%M')}",
    data_type: str = "ANY_VALUE",
    security_voter="FULL_VIS_ADMIN_IDP",
    issuer_type: Optional[
        user_attribute_routes.UserAttributes_IssuerType
    ] = user_attribute_routes.UserAttributes_IssuerType.CUSTOM,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop=2,
    return_raw: bool = False,
):
    auth = self.auth
    attribute_id = user_attribute_routes.clean_attribute_id(attribute_id)

    res = await user_attribute_routes.create_user_attribute(
        auth=auth,
        session=session,
        issuer_type=issuer_type,
        name=name,
        attribute_id=attribute_id,
        description=description,
        data_type=data_type,
        security_voter=security_voter,
        debug_api=debug_api,
        parent_class=self.__class__.__name__,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    await self.get()

    if return_raw:
        return res

    return await UserAttribute.get_by_id(auth=auth, entity_id=attribute_id)


async def upsert(
    self: UserAttributes,
    attribute_id,
    name=None,
    description=None,
    issuer_type: Optional[user_attribute_routes.UserAttributes_IssuerType] = None,
    data_type: Optional[str] = None,
    security_voter=None,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop=2,
    debug_prn: bool = False,
):
    auth = self.auth
    attribute_id = user_attribute_routes.clean_attribute_id(attribute_id)

    user_attribute = None

    try:
        user_attribute = await UserAttribute.get_by_id(
            entity_id=attribute_id,
            auth=auth,
            session=session,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            debug_api=debug_api,
        )

        if user_attribute:
            if debug_prn:
                print(f"upserting {attribute_id} in {auth.domo_instance}")

            await user_attribute.update(
                name=name,
                description=description,
                issuer_type=issuer_type,
                data_type=data_type,
                security_voter=security_voter,
                session=session,
                debug_api=debug_api,
                debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            )

        return user_attribute

    except (UserAttributes_CRUD_Error, UserAttributes_GET_Error):
        if debug_prn:
            print(f"creating {attribute_id} in {auth.domo_instance}")

        return await self.create(
            attribute_id=attribute_id,
            name=name,
            description=description or "",
            issuer_type=issuer_type
            or user_attribute_routes.UserAttributes_IssuerType.CUSTOM,
            data_type=data_type or "",
            security_voter=security_voter or "",
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
        )

    finally:
        await self.get()


async def delete(
    self: UserAttributes,
    attribute_id: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop=2,
    return_raw: bool = False,
):
    auth = self.auth

    res = await user_attribute_routes.delete_user_attribute(
        auth=auth,
        session=session,
        debug_api=debug_api,
        parent_class=self.__class__.__name__,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        attribute_id=attribute_id,
    )

    await self.get()

    return res
