"""Core DomoCard classes including federated and published support"""

__all__ = [
    "FederatedDomoCard",
    "DomoPublishCard",
    "DomoCard",
]

from dataclasses import dataclass
from typing import Any, Callable, Optional

import httpx

from ...auth import DomoAuth
from ...base.entities_federated import DomoFederatedEntity, DomoPublishedEntity
from ...utils import chunk_execution as dmce
from .card_default import DomoCard_Default


@dataclass
class FederatedDomoCard(DomoCard_Default, DomoFederatedEntity):
    """Federated card seen in a parent instance; points to a child instance's native card."""

    @property
    def entity_type(self):
        return "CARD"

    async def get_federated_parent(
        self,
        parent_auth: None = None,
        parent_auth_retrieval_fn: Optional[Callable] = None,
    ):
        from ...classes.publish import DomoEverywhere

        domo_everywhere = DomoEverywhere(
            auth=self.auth,
        )

        await domo_everywhere.get_subscriptions()

        await dmce.gather_with_concurrency(
            *[
                sub.get_parent_publication(
                    parent_auth_retrieval_fn=parent_auth_retrieval_fn,  # type: ignore
                    parent_auth=parent_auth,  # type: ignore
                )
                for sub in domo_everywhere.subscriptions
            ],
            n=20,
        )

        all = await dmce.gather_with_concurrency(
            *[
                sub.parent_publication.get_publication_entity_by_subscriber_entity(
                    subscriber_domain=sub.subscriber_domain,
                    subscriber=self,
                )
                for sub in domo_everywhere.subscriptions
            ],
            n=20,
        )

        self.parent_entity = next(
            (entity for entity in all if entity is not None), None
        )
        if not self.parent_entity:
            raise NotImplementedError("To Do")

        return self.parent_entity

    @classmethod
    async def get_by_id(
        cls,
        auth: DomoAuth,
        card_id: str,
        optional_parts: str = "certification,datasources,drillPath,owners,properties,domoapp",
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        return_raw: bool = False,
        is_suppress_errors: bool = False,
    ):
        """Retrieve federated card metadata"""
        # Use parent implementation to avoid code duplication
        return await super().get_by_id(
            auth=auth,
            card_id=card_id,
            optional_parts=optional_parts,
            debug_api=debug_api,
            session=session,
            return_raw=return_raw,
            is_suppress_errors=is_suppress_errors,
        )


@dataclass
class DomoPublishCard(FederatedDomoCard, DomoPublishedEntity):
    """Published card that supports publish/subscribe across instances"""

    @classmethod
    async def get_entity_by_id(cls, auth: DomoAuth, entity_id: str, **kwargs):
        return await cls.get_by_id(auth=auth, card_id=entity_id, **kwargs)

    async def get_subscription(self):
        raise NotImplementedError("To Do")

    async def get_parent_publication(
        self,
        parent_auth: None = None,
        parent_auth_retrieval_fn: Optional[Callable] = None,
    ):
        raise NotImplementedError("To Do")


@dataclass
class DomoCard(DomoCard_Default):
    """Smart factory class that returns appropriate card type based on metadata"""

    @classmethod
    async def from_dict(
        cls,
        auth: DomoAuth,
        obj: dict,
        owners: list[Any] = None,
        **kwargs,
    ) -> "DomoCard":
        """Convert API response dictionary to appropriate card class instance"""

        is_federated = cls._is_federated(obj)

        new_cls = DomoCard

        if is_federated:
            new_cls = FederatedDomoCard

        # TO DO -- how do we know if it's published?

        # Build the card instance with the appropriate class
        card = new_cls(
            auth=auth,
            id=obj.get("id"),
            raw=obj,
            Relations=None,  # type: ignore
            title=obj.get("title"),
            description=obj.get("description"),
            type=obj.get("type"),
            urn=obj.get("urn"),
            certification=obj.get("certification"),
            chart_type=obj.get("metadata", {}).get("chartType"),
            dataset_id=(
                obj.get("datasources", [])[0].get("dataSourceId")
                if obj.get("datasources")
                else None
            ),
            owners=owners or [],
            datastore_id=obj.get("domoapp", {}).get("id"),
            Lineage=None,  # type: ignore
        )

        return card
