import abc
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from .entities import DomoEntity_w_Lineage


@dataclass
class DomoFederatedEntity(DomoEntity_w_Lineage):
    """Entity that can be federated across multiple Domo instances.

    This class extends lineage-enabled entities to support federation,
    allowing entities to maintain relationships across different Domo
    instances in federated environments.
    """

    @abc.abstractmethod
    async def get_federated_parent(
        self, parent_auth=None, parent_auth_retrieval_fn: Optional[Callable] = None
    ):
        """Retrieve the parent entity from a federated Domo instance.

        Args:
            parent_auth: Authentication object for the parent instance
            parent_auth_retrieval_fn (Optional[Callable]): Function to retrieve parent auth

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("This method should be implemented by subclasses.")


@dataclass
class DomoPublishedEntity(DomoFederatedEntity):
    """Entity that supports publishing and subscription across instances.

    This class extends federated entities to support Domo's publishing
    and subscription model, allowing entities to be shared and synchronized
    across different Domo instances.

    Attributes:
        subscription: Subscription information for this published entity (not shown in repr)
        parent_publication: Parent publication details (not shown in repr)
    """

    subscription: Any = field(repr=False, default=None)
    parent_publication: Any = field(repr=False, default=None)

    @abc.abstractmethod
    async def get_subscription(self):
        """Retrieve subscription information for this entity.

        This method should fetch and store subscription details for the entity,
        updating the subscription attribute.

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        # self.subscription = ... ## should return one subscription
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abc.abstractmethod
    async def get_parent_publication(
        self, parent_auth=None, parent_auth_retrieval_fn=None
    ):
        """Retrieve parent publication information.

        This method fetches the parent publication details, optionally using
        provided authentication or a retrieval function.

        Args:
            parent_auth: Authentication object for the parent instance
            parent_auth_retrieval_fn: Function to retrieve parent authentication

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        # if not self.subscription:
        #     await self.get_subscription()

        # if not parent_auth:
        #     if not parent_auth_retrieval_fn:
        #         raise ValueError("Either parent_auth or parent_auth_retrieval_fn must be provided.")
        #     parent_auth = parent_auth_retrieval_fn(self.subscription)

        # self.parent_publication = ... (parent_auth) ## should return the parent publication
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abc.abstractmethod
    async def get_parent_content_details(self, parent_auth=None):
        """Retrieve detailed information about the parent content.

        This method fetches comprehensive details about the parent dataset,
        card, page, or other content type.

        Args:
            parent_auth: Authentication object for the parent instance

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        # if not self.parent_publication:
        #     await self.get_parent_publication(parent_auth)
        raise NotImplementedError("This method should be implemented by subclasses.")

    async def get_federated_parent(
        self, parent_auth=None, parent_auth_retrieval_fn: Optional[Callable] = None
    ):
        """Get the federated parent entity.

        Args:
            parent_auth: Authentication object for the parent instance
            parent_auth_retrieval_fn (Optional[Callable]): Function to retrieve parent auth

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("This method should be implemented by subclasses.")
