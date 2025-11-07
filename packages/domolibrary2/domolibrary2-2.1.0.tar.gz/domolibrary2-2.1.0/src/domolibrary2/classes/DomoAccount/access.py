"""DomoAccess re-export for DomoAccount package.

This module re-exports DomoAccess classes from the subentity package
to resolve import dependencies within the DomoAccount package.
"""

from dataclasses import dataclass, field

import httpx

from ...client.response import ResponseGetData
from ...routes import account as account_routes
from ...routes.account import (
    ShareAccount,
    ShareAccount_AccessLevel,
    ShareAccount_V1_AccessLevel,
)
from ...utils import chunk_execution as dmce
from ..subentity.access import AccessRelationship, DomoAccess


@dataclass
class Account_AccessRelationship(AccessRelationship):
    def __repr__(self):
        return f"{super().__repr__()}, relationship_type={self.relationship_type!r}, entity_id={self.entity_id!r}, entity_type={self.entity_type!r}, entity_name={self.entity_name!r}"

    @property
    def entity_id(self):
        return self.entity.id

    @property
    def entity_type(self):
        return self.entity.entity_type

    @property
    def entity_name(self):
        return (
            getattr(self.entity, "email_address", None)
            or getattr(self.entity, "name", None)
            or getattr(self.entity, "display_name", None)
        )

    def to_dict(self):
        return {"id": self.entity.id, "type": self.entity.entity_type}

    async def update(self):
        raise NotImplementedError("DomoAccount_Access.update not implemented")

    @classmethod
    async def from_user_id(
        cls,
        parent_entity,
        user_id,
        auth,
        access_level,
        suppress_no_results_error: bool = True,
    ):
        from ...routes.user.exceptions import SearchUserNotFoundError
        from ..DomoUser import DomoUser

        try:
            user = await DomoUser.get_by_id(auth=auth, user_id=user_id)
            return cls(
                entity=user,
                relationship_type=access_level,
                parent_entity=parent_entity,
            )
        except SearchUserNotFoundError:
            if suppress_no_results_error:
                # User no longer exists, return None
                return None
            raise

    @classmethod
    async def from_group_id(
        cls,
        parent_entity,
        group_id,
        auth,
        access_level,
        suppress_no_results_error: bool = True,
    ):
        from ...routes.group.exceptions import SearchGroupNotFoundError
        from ..DomoGroup.core import DomoGroup

        try:
            group = await DomoGroup.get_by_id(auth=auth, group_id=group_id)
            return cls(
                entity=group,
                relationship_type=access_level,
                parent_entity=parent_entity,
            )
        except SearchGroupNotFoundError:
            if suppress_no_results_error:
                # Group no longer exists, return None
                return None
            raise

    @classmethod
    async def from_entity_id(
        cls,
        parent_entity,
        entity_id,
        auth,
        access_level,
        entity_type,
        suppress_no_results_error: bool = True,
    ):
        if entity_type == "USER":
            return await cls.from_user_id(
                parent_entity, entity_id, auth, access_level, suppress_no_results_error
            )
        elif entity_type == "GROUP":
            return await cls.from_group_id(
                parent_entity, entity_id, auth, access_level, suppress_no_results_error
            )
        else:
            raise ValueError(f"Unknown entity_type: {entity_type}")


@dataclass
class DomoAccess_Account(DomoAccess):
    """
    Account access management with unified access control integration.

    This class provides backward compatibility while integrating with
    the new unified access control system. Use get_unified_access_summary()
    for access to the standardized access control interface.
    """

    version: int = None  # api version - aligns to feature switch

    share_enum: ShareAccount = field(default=ShareAccount_AccessLevel)

    def __post_init__(self):
        super().__post_init__()

        if isinstance(self.share_enum, ShareAccount_AccessLevel):
            self.version = 2
        elif isinstance(self.share_enum, ShareAccount_V1_AccessLevel):
            self.version = 1

        return True

    async def get(
        self,
        debug_api: bool = False,
        return_raw: bool = False,
        session: httpx.AsyncClient = None,
        debug_num_stacks_to_drop=2,
        suppress_no_results_error: bool = True,
    ):
        """Get account access list.

        Args:
            debug_api: Enable API debugging
            return_raw: Return raw API response without processing
            session: HTTP client session
            debug_num_stacks_to_drop: Stack frames to drop for debugging
            suppress_no_results_error: If True, skip users/groups that don't exist; if False, raise error

        Returns:
            List of Account_AccessRelationship objects
        """

        res = await account_routes.get_account_accesslist(
            auth=self.auth,
            account_id=self.parent_id,
            debug_api=debug_api,
            session=session,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            return_raw=return_raw,
        )

        if return_raw:
            return res

        self.relationships = [
            rel
            for rel in await dmce.gather_with_concurrency(
                *[
                    Account_AccessRelationship.from_entity_id(
                        parent_entity=self.parent,
                        entity_id=obj["id"],
                        auth=self.auth,
                        access_level=obj["accessLevel"],
                        entity_type=obj["type"],
                        suppress_no_results_error=suppress_no_results_error,
                    )
                    for obj in res.response
                ],
                n=10,
            )
            if rel is not None  # Filter out users/groups that no longer exist
        ]

        return self.relationships

    async def add_share(
        self,
        entity,
        access_level=None,
        user_id: int = None,
        group_id: int = None,
        use_v1_api: bool = False,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        return_raw: bool = False,
    ) -> Account_AccessRelationship:
        """Share this account with a user or group.

        Can be called in two ways:
        1. Pass an entity object (DomoUser or DomoGroup) with access_level
        2. Pass user_id or group_id with access_level

        Args:
            entity: DomoUser or DomoGroup object (optional if user_id/group_id provided)
            access_level: Access level enum or string (defaults to self.share_enum.CAN_VIEW)
            user_id: User ID to share with (optional)
            group_id: Group ID to share with (optional)
            use_v1_api: Force v1 API usage (ignored if group_id provided)
            debug_api: Enable API debugging
            session: HTTP client session (optional)
            return_raw: Return raw response without processing

        Returns:
            Account_AccessRelationship instance representing the new share relationship
            (or ResponseGetData if return_raw=True)

        Raises:
            ValueError: If neither entity nor user_id/group_id provided
            Account_Share_Error: If sharing operation fails

        Examples:
            >>> # Share with DomoUser entity
            >>> user = await DomoUser.get_by_id(auth=auth, user_id=456)
            >>> relationship = await account.Access.add_share(
            ...     entity=user,
            ...     access_level=ShareAccount_AccessLevel.CAN_VIEW
            ... )
            >>> print(relationship.entity_id)  # 456

            >>> # Share with group by ID
            >>> relationship = await account.Access.add_share(
            ...     group_id=789,
            ...     access_level=ShareAccount_AccessLevel.CAN_EDIT
            ... )
            >>> print(relationship.entity_type)  # GROUP
        """
        # Extract IDs from entity if provided
        if entity:
            if hasattr(entity, "entity_type"):
                if entity.entity_type.upper() == "USER":
                    user_id = entity.id
                elif entity.entity_type.upper() == "GROUP":
                    group_id = entity.id
            else:
                # Try to infer from class name
                class_name = entity.__class__.__name__
                if "USER" in class_name.upper():
                    user_id = entity.id
                elif "GROUP" in class_name.upper():
                    group_id = entity.id

        # Determine entity type and ID
        if user_id:
            entity_type = "USER"
            entity_id = user_id
        elif group_id:
            entity_type = "GROUP"
            entity_id = group_id
        else:
            raise ValueError("Must provide either entity, user_id, or group_id")

        # Set default access level
        if not access_level:
            access_level = self.share_enum.CAN_VIEW

        # Call the route function
        res = await account_routes.share_account(
            auth=self.auth,
            account_id=self.parent.id,
            access_level=access_level,
            user_id=user_id,
            group_id=group_id,
            use_v1_api=use_v1_api,
            debug_api=debug_api,
            session=session,
            return_raw=return_raw,
        )

        if return_raw:
            return res

        # Create and return the relationship instance for the shared entity
        relationship = await Account_AccessRelationship.from_entity_id(
            parent_entity=self.parent,
            entity_id=entity_id,
            auth=self.auth,
            access_level=access_level,
            entity_type=entity_type,
        )

        # Optionally refresh the full access list to keep it in sync
        await self.get(debug_api=debug_api, session=session)

        return relationship

    async def remove_share(
        self,
        entity=None,
        user_id: int = None,
        group_id: int = None,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        return_raw: bool = False,
    ) -> ResponseGetData:
        """Remove account sharing for a user or group.

        Can be called in two ways:
        1. Pass an entity object (DomoUser or DomoGroup)
        2. Pass user_id or group_id

        Args:
            entity: DomoUser or DomoGroup object (optional if user_id/group_id provided)
            user_id: User ID to remove (optional)
            group_id: Group ID to remove (optional)
            debug_api: Enable API debugging
            session: HTTP client session (optional)
            return_raw: Return raw response without processing

        Returns:
            ResponseGetData if return_raw=True, else refreshed relationships

        Raises:
            ValueError: If neither entity nor user_id/group_id provided
            Account_Share_Error: If remove operation fails

        Examples:
            >>> # Remove share for DomoUser entity
            >>> user = await DomoUser.get_by_id(auth=auth, user_id=456)
            >>> await account.Access.remove_share(entity=user)

            >>> # Remove share by group ID
            >>> await account.Access.remove_share(group_id=789)
        """
        # Extract IDs from entity if provided
        if entity:
            if hasattr(entity, "entity_type"):
                if entity.entity_type.upper() == "USER":
                    user_id = entity.id
                elif entity.entity_type.upper() == "GROUP":
                    group_id = entity.id
            else:
                # Try to infer from class name
                class_name = entity.__class__.__name__
                if "USER" in class_name.upper():
                    user_id = entity.id
                elif "GROUP" in class_name.upper():
                    group_id = entity.id

        # Share with NO_ACCESS to remove
        res = await account_routes.share_account(
            auth=self.auth,
            account_id=self.parent_id,
            access_level=ShareAccount_AccessLevel.NO_ACCESS,
            user_id=user_id,
            group_id=group_id,
            debug_api=debug_api,
            session=session,
            return_raw=return_raw,
        )

        if return_raw:
            return res

        # Refresh access list after removing
        return await self.get(debug_api=debug_api, session=session)


@dataclass
class DomoAccess_OAuth(DomoAccess_Account):
    share_enum: ShareAccount = field(repr=False, default=ShareAccount_AccessLevel)

    async def get(
        self,
        debug_api: bool = False,
        return_raw: bool = False,
        session: httpx.AsyncClient = None,
        debug_num_stacks_to_drop=2,
        suppress_no_results_error: bool = True,
    ):
        """Get OAuth account access list.

        Args:
            debug_api: Enable API debugging
            return_raw: Return raw API response without processing
            session: HTTP client session
            debug_num_stacks_to_drop: Stack frames to drop for debugging
            suppress_no_results_error: If True, skip users/groups that don't exist; if False, raise error

        Returns:
            List of Account_AccessRelationship objects
        """

        res = await account_routes.get_oauth_account_accesslist(
            auth=self.auth,
            account_id=self.parent_id,
            debug_api=debug_api,
            session=session,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

        if return_raw:
            return res

        # Process response and filter out deleted users/groups
        self.relationships = [
            rel
            for rel in await dmce.gather_with_concurrency(
                *[
                    Account_AccessRelationship.from_entity_id(
                        parent_entity=self.parent,
                        entity_id=obj["id"],
                        auth=self.auth,
                        access_level=obj["accessLevel"],
                        entity_type=obj["type"],
                        suppress_no_results_error=suppress_no_results_error,
                    )
                    for obj in res.response
                ],
                n=10,
            )
            if rel is not None  # Filter out users/groups that no longer exist
        ]

        return self.relationships

    async def add_share(
        self,
        entity,
        access_level=None,
        user_id: int = None,
        group_id: int = None,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        return_raw: bool = False,
    ) -> Account_AccessRelationship:
        """Share this OAuth account with a user or group.

        Args:
            entity: DomoUser or DomoGroup object (optional if user_id/group_id provided)
            access_level: Access level enum or string (defaults to self.share_enum.CAN_VIEW)
            user_id: User ID to share with (optional)
            group_id: Group ID to share with (optional)
            debug_api: Enable API debugging
            session: HTTP client session (optional)
            return_raw: Return raw response without processing

        Returns:
            Account_AccessRelationship instance representing the new share relationship
            (or ResponseGetData if return_raw=True)

        Examples:
            >>> # Share OAuth account with user
            >>> relationship = await oauth_account.Access.add_share(
            ...     user_id=456,
            ...     access_level=ShareAccount_AccessLevel.CAN_VIEW
            ... )
            >>> print(relationship.entity_id)  # 456
        """
        # Extract IDs from entity if provided
        if entity:
            if hasattr(entity, "entity_type"):
                if entity.entity_type == "USER":
                    user_id = entity.id
                elif entity.entity_type == "GROUP":
                    group_id = entity.id
            else:
                class_name = entity.__class__.__name__
                if "User" in class_name:
                    user_id = entity.id
                elif "Group" in class_name:
                    group_id = entity.id

        # Determine entity type and ID
        if user_id:
            entity_type = "USER"
            entity_id = user_id
        elif group_id:
            entity_type = "GROUP"
            entity_id = group_id
        else:
            raise ValueError("Must provide either entity, user_id, or group_id")

        # Set default access level
        if not access_level:
            access_level = self.share_enum.CAN_VIEW

        # Call the OAuth-specific route function
        res = await account_routes.share_oauth_account(
            auth=self.auth,
            account_id=self.parent_id,
            access_level=access_level,
            user_id=user_id,
            group_id=group_id,
            debug_api=debug_api,
            session=session,
            return_raw=return_raw,
        )

        if return_raw:
            return res

        # Create and return the relationship instance for the shared entity
        relationship = await Account_AccessRelationship.from_entity_id(
            parent_entity=self.parent,
            entity_id=entity_id,
            auth=self.auth,
            access_level=access_level,
            entity_type=entity_type,
        )

        # Optionally refresh the full access list to keep it in sync
        await self.get(debug_api=debug_api, session=session)

        return relationship

    async def remove_share(
        self,
        entity=None,
        user_id: int = None,
        group_id: int = None,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        return_raw: bool = False,
    ) -> ResponseGetData:
        """Remove OAuth account sharing for a user or group.

        Args:
            entity: DomoUser or DomoGroup object (optional if user_id/group_id provided)
            user_id: User ID to remove (optional)
            group_id: Group ID to remove (optional)
            debug_api: Enable API debugging
            session: HTTP client session (optional)
            return_raw: Return raw response without processing

        Returns:
            ResponseGetData if return_raw=True, else refreshed relationships

        Examples:
            >>> # Remove OAuth account share
            >>> await oauth_account.Access.remove_share(user_id=456)
        """
        # Extract IDs from entity if provided
        if entity:
            if hasattr(entity, "entity_type"):
                if entity.entity_type == "USER":
                    user_id = entity.id
                elif entity.entity_type == "GROUP":
                    group_id = entity.id
            else:
                class_name = entity.__class__.__name__
                if "User" in class_name:
                    user_id = entity.id
                elif "Group" in class_name:
                    group_id = entity.id

        # Share with NO_ACCESS to remove
        res = await account_routes.share_oauth_account(
            auth=self.auth,
            account_id=self.parent_id,
            access_level=ShareAccount_AccessLevel.NO_ACCESS,
            user_id=user_id,
            group_id=group_id,
            debug_api=debug_api,
            session=session,
            return_raw=return_raw,
        )

        if return_raw:
            return res

        # Refresh access list after removing
        return await self.get(debug_api=debug_api, session=session)


__all__ = ["DomoAccess_Account", "DomoAccess_OAuth", "Account_AccessRelationship"]
