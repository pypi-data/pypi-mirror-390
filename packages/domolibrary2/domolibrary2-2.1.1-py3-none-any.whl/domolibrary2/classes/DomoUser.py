"""DomoUser module for managing Domo users."""  # noqa: N999

__all__ = [
    "domo_default_img",
    "DomoUser",
    "DomoUsers",
    "DomoUser_NoSearchError",
    # User Route Exceptions
    "User_GET_Error",
    "User_CRUD_Error",
    "SearchUserNotFoundError",
    "UserSharing_Error",
    "DeleteUserError",
    "UserAttributes_GET_Error",
    "UserAttributes_CRUD_Error",
    "ResetPasswordPasswordUsedError",
    "DownloadAvatar_Error",
]

import asyncio
import datetime as dt
from dataclasses import dataclass, field
from typing import Any, Optional, Union

import httpx
from dc_logger.decorators import log_call

from ..auth import DomoAuth
from ..base.entities import DomoEntity, DomoManager
from ..base.exceptions import ClassError, DomoError
from ..client.response import ResponseGetData
from ..routes import user as user_routes
from ..routes.instance_config import sso as sso_routes
from ..routes.user import UserProperty
from ..routes.user.exceptions import (
    DeleteUserError,
    DownloadAvatar_Error,
    ResetPasswordPasswordUsedError,
    SearchUserNotFoundError,
    User_CRUD_Error,
    User_GET_Error,
    UserAttributes_CRUD_Error,
    UserAttributes_GET_Error,
    UserSharing_Error,
)
from ..utils.convert import convert_epoch_millisecond_to_datetime, test_valid_email
from ..utils.images import Image, ImageUtils, are_same_image
from ..utils.logging import get_colored_logger

# User route exceptions are now imported from ..routes.user.exceptions

logger = get_colored_logger()


class CreateUser_MissingRoleError(ClassError):  # noqa: N801
    """Exception raised when role_id is missing during user creation."""

    def __init__(self, domo_instance, email_address):
        super().__init__(
            domo_instance=domo_instance,
            message=f"Error creating user {email_address}: missing role_id parameter",
        )


class DomoUser_NoSearchError(ClassError):  # noqa: N801
    """Exception raised when user search operations fail."""

    def __init__(
        self,
        cls_instance,
        message: str = "No users found matching search criteria",
        domo_instance: str = None,
    ):
        super().__init__(
            cls_instance=cls_instance,
            domo_instance=domo_instance,
            message=message,
        )


default_img_bytes = b""  # Placeholder for actual byte data

# Update type annotations to use Optional

domo_default_img = None  # Placeholder for the default image


@dataclass(eq=False)
class DomoUser(DomoEntity):
    """A class for interacting with a Domo User"""

    id: str
    display_name: Optional[str] = None
    email_address: Optional[str] = None
    role_id: Optional[int] = None  # Updated to match expected type
    department: Optional[str] = None
    title: Optional[str] = None
    avatar_key: Optional[str] = None
    avatar: Optional[Image.Image] = None
    password: Optional[str] = field(repr=False, default=None)

    phone_number: Optional[str] = None
    web_landing_page: Optional[str] = None
    web_mobile_landing_page: Optional[str] = None
    employee_id: Optional[str] = None
    employee_number: Optional[str] = None
    hire_date: Optional[str] = None
    reports_to: Optional[str] = None

    publisher_domain: Optional[str] = None
    subscriber_domain: Optional[str] = None
    virtual_user_id: Optional[str] = None

    created_dt: Optional[dt.datetime] = None
    last_activity_dt: Optional[dt.datetime] = None

    custom_attributes: dict = field(default_factory=dict)

    domo_api_clients: Optional[list[Any]] = None
    domo_access_tokens: Optional[list[Any]] = None

    Role: Optional[Any] = None  # DomoRole
    ApiClients: Optional[Any] = None  # DomoApiClients

    def __post_init__(self):
        from .DomoInstanceConfig.api_client import ApiClients

        self.id = str(self.id)

        self.ApiClients = ApiClients.from_parent(auth=self.auth, parent=self)

    @property
    def entity_type(self) -> str:
        return "USER"

    @property
    def display_url(self) -> str:
        """Generate the URL to display this user in the Domo admin interface."""
        return f"https://{self.auth.domo_instance}.domo.com/admin/people/{self.id}"

    @classmethod
    def from_dict(cls, auth, obj: dict):
        return cls(
            auth=auth,
            id=str(obj.get("id") or obj.get("userId")),
            display_name=obj.get("displayName"),
            title=obj.get("title"),
            department=obj.get("department"),
            email_address=obj.get("emailAddress") or obj.get("email"),
            role_id=obj.get("roleId"),
            avatar_key=obj.get("avatarKey"),
            phone_number=obj.get("phoneNumber"),
            web_landing_page=obj.get("webLandingPage"),
            web_mobile_landing_page=obj.get("webMobileLandingPage"),
            employee_id=obj.get("employeeId"),
            employee_number=obj.get("employeeNumber"),
            hire_date=obj.get("hireDate"),
            reports_to=obj.get("reportsTo"),
            created_dt=convert_epoch_millisecond_to_datetime(obj.get("created")),
            last_activity_dt=convert_epoch_millisecond_to_datetime(
                obj.get("lastActivity"),
            ),
            raw=obj,
            Relations=None,  # type: ignore
        )

    @classmethod
    def from_virtual_dict(cls, auth, obj: dict):
        """Create DomoUser instance from virtual user JSON response.

        Virtual users are created when content is published across instances.
        """
        return cls(
            id=obj["id"],
            auth=auth,
            publisher_domain=obj.get("publisherDomain"),
            subscriber_domain=obj.get("subscriberDomain"),
            virtual_user_id=obj.get("virtualUserId"),
            raw=obj,
            Relations=None,  # type: ignore
        )

    @classmethod
    def from_bootstrap_dict(cls, auth, obj):
        return cls(
            id=obj["id"],
            display_name=obj.get("displayName"),
            auth=auth,
            Relations=None,  # type: ignore
            raw=obj,
        )

    async def get_role(
        self: "DomoUser",
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        session: httpx.AsyncClient | None = None,
    ):
        from .DomoInstanceConfig.role import DomoRole

        self.Role = await DomoRole.get_by_id(
            role_id=str(self.role_id),
            auth=self.auth,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            session=session,
        )

        return self.Role

    @classmethod
    async def get_by_id(
        cls,
        auth: DomoAuth,
        user_id: str,
        return_raw: bool = False,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        session: httpx.AsyncClient | None = None,
    ):
        """Retrieve a Domo user by ID.

        Args:
            auth: Authentication object
            entity_id: User ID to retrieve
            return_raw: If True, return raw API response instead of DomoUser instance
            debug_api: Enable debug output for API call
            debug_num_stacks_to_drop: Number of stack frames to drop in logging
            session: Optional httpx session for connection pooling

        Returns:
            DomoUser instance or ResponseGetData if return_raw=True

        Raises:
            User_GET_Error: If user retrieval fails
        """

        res = await user_routes.get_by_id(
            auth=auth,
            user_id=user_id,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            session=session,
            parent_class=cls.__name__,
        )

        if return_raw:
            return res

        if not res.is_success:
            return None

        domo_user = cls.from_dict(obj=res.response, auth=auth)

        try:
            await domo_user.get_role(
                debug_api=debug_api,
                debug_num_stacks_to_drop=debug_num_stacks_to_drop,
                session=session,
            )
        except DomoError as e:
            print(e)

        return domo_user

    @classmethod
    async def get_entity_by_id(cls, entity_id: str, auth: DomoAuth, **kwargs):
        return await cls.get_by_id(user_id=entity_id, auth=auth, **kwargs)

    async def download_avatar(
        self,
        pixels: int = 300,
        folder_path="./images",
        img_name=None,  # will default to user_id
        auth: Optional[DomoAuth] = None,
        is_download_image: bool = True,  # option to prevent downloading the image file
        debug_api: bool = False,
        return_raw: bool = False,
    ):
        """downloads a user's avatar to a folder
        and returns the byte representation of the image
        """
        auth = auth or self.auth

        res = await user_routes.download_avatar(
            auth=self.auth,
            user_id=self.id,
            pixels=pixels,
            folder_path=folder_path,
            img_name=img_name,
            is_download_image=is_download_image,
            debug_api=debug_api,
        )

        if return_raw:
            return res

        self.avatar = ImageUtils.from_bytestr(data=res.response)

        return self.avatar

        # return res.response

    async def update_properties(
        self,
        property_ls: list[
            UserProperty
        ],  # use the UserProperty class to define a list of user properties to update, see user route documentation to see a list of UserProperty_Types that can be updated
        return_raw: bool = False,
        auth: Optional[DomoAuth] = None,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
    ):
        auth = auth or self.auth

        res = await user_routes.update_user(
            auth=auth,
            user_id=self.id,
            user_property_ls=property_ls,
            debug_api=debug_api,
            session=session,
        )
        if return_raw:
            return res

        # Update self using from_dict pattern
        updated_user = self.from_dict(auth=auth, obj=res.response)
        # Copy updated attributes back to self
        for key, value in updated_user.__dict__.items():
            if key not in ["auth"]:  # Don't overwrite auth
                setattr(self, key, value)

        # Update self using from_dict pattern
        if res.response:
            updated_user = self.from_dict(auth=auth, obj=res.response)
            # Copy updated attributes back to self
            for key, value in updated_user.__dict__.items():
                if key not in ["auth"]:  # Don't overwrite auth
                    setattr(self, key, value)

            return updated_user

    async def set_user_landing_page(
        self,
        page_id: str,
        id: str,
        auth: Optional[DomoAuth] = None,
        debug_api: bool = False,
    ):
        res = await user_routes.set_user_landing_page(
            auth=auth or self.auth,
            page_id=page_id,
            user_id=self.id or id,
            debug_api=debug_api,
        )

        return res

    @classmethod
    async def create(
        cls,
        auth: DomoAuth,
        display_name,
        email_address,
        role: Any,  # DomoRole - will use default role if none provided
        password: Optional[str] = None,
        send_password_reset_email: bool = False,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        session: httpx.AsyncClient | None = None,
    ):
        """class method that creates a new Domo user"""

        if not role:
            from .DomoInstanceConfig.role import DomoRoles

            role = await DomoRoles(auth=auth).get_default_role(session=session)

        res = await user_routes.create_user(
            auth=auth,
            display_name=display_name,
            email_address=email_address,
            role_id=role.id,
            debug_api=debug_api,
            session=session,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

        domo_user = await DomoUser.get_by_id(
            auth=auth,
            user_id=res.response.get("id") or res.response.get("userId"),
            session=session,
        )

        if password and domo_user:
            await domo_user.reset_password(
                new_password=password, session=session, debug_api=debug_api
            )

        elif send_password_reset_email and domo_user:
            await domo_user.request_password_reset(
                domo_instance=auth.domo_instance,
                email=domo_user.email_address,
                session=session,
                debug_api=debug_api,
            )

        return domo_user

    async def delete(
        self,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        debug_num_stacks_to_drop=2,
        parent_class=None,
    ):
        res = await user_routes.delete_user(
            auth=self.auth,
            user_id=self.id,
            debug_api=debug_api,
            session=session,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=parent_class,
        )

        return res

    async def reset_password(
        self: "DomoUser",
        new_password: str,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        debug_num_stacks_to_drop: int = 2,
    ):
        """reset your password, will respect password restrictions set up in the Domo UI"""

        res = await user_routes.reset_password(
            auth=self.auth,
            user_id=self.id,
            new_password=new_password,
            debug_api=debug_api,
            session=session,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=self.__class__.__name__,
        )

        self.password = new_password

        return res

    @classmethod
    async def request_password_reset(
        cls,
        domo_instance: str,
        email: str,
        locale: str = "en-us",
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        debug_num_stacks_to_drop: int = 2,
    ):
        """request password reset email.  Note: does not require authentication."""

        return await user_routes.request_password_reset(
            domo_instance=domo_instance,
            email=email,
            locale=locale,
            debug_api=debug_api,
            session=session,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=cls.__name__,
        )

    async def upload_avatar(
        self,
        avatar: Image.Image,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        return_raw: bool = False,
    ):
        avatar = ImageUtils.crop_square(avatar)

        res = await user_routes.upload_avatar(
            auth=self.auth,
            user_id=self.id,
            img_bytestr=ImageUtils.to_bytes(avatar),
            img_type=avatar.format,
            debug_api=debug_api,
            parent_class=self.__class__.__name__,
            session=session,
        )

        if return_raw:
            return res

        await asyncio.sleep(2)

        return await self.download_avatar(debug_api=debug_api)

    async def upsert_avatar(
        self,
        avatar: Image.Image,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        return_raw: bool = False,
    ):
        avatar = ImageUtils.crop_square(avatar)

        res = "images are the same"
        if not are_same_image(domo_default_img, avatar):
            res = await user_routes.upload_avatar(
                auth=self.auth,
                user_id=self.id,
                img_bytestr=ImageUtils.to_bytes(avatar),
                img_type=avatar.format,
                debug_api=debug_api,
                parent_class=self.__class__.__name__,
                session=session,
            )

            if return_raw:
                return res

        await asyncio.sleep(2)

        return await self.download_avatar(debug_api=debug_api)

    async def toggle_direct_signon_access(
        self: "DomoUser",
        is_enable_direct_signon: bool = True,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
    ):
        res = await sso_routes.toggle_user_direct_signon_access(
            auth=self.auth,
            id_ls=[self.id],
            is_enable_direct_signon=is_enable_direct_signon,
            session=session,
            debug_api=debug_api,
            parent_class=self.__class__.__name__,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

        return res

    async def get_api_clients(
        self,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        debug_num_stacks_to_drop=2,
        return_raw: bool = False,
    ):
        """
        retrieves Client_IDs for this user (assuming the authenticated user has manage rights).
        Note : the values will be masked, raw text values can only be retrieved via the UI
        """

        from .DomoInstanceConfig.api_client import ApiClients

        api_clients = ApiClients(auth=self.auth)

        res = await api_clients.get(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
        )

        if return_raw:
            return res

        domo_clients = (
            [
                domo_client
                for domo_client in res.response
                if domo_client.domo_user.id == self.id  # type: ignore
            ]
            if isinstance(res, ResponseGetData)
            else []
        )

        if not domo_clients:
            print(
                f"Domo User {self.id} - {self.display_name} does not have any Client_IDs"
            )
            return False

        self.domo_api_clients = domo_clients

        return self.domo_api_clients

    async def get_access_tokens(
        self,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        session: httpx.AsyncClient | None = None,
        return_raw: bool = False,
    ):
        from .DomoInstanceConfig import access_token as dmat

        domo_config = dmat.DomoAccessTokens(auth=self.auth)
        domo_tokens = await domo_config.get(
            debug_api=debug_api,
            session=session,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
        )

        if return_raw:
            return domo_tokens

        domo_tokens = [
            domo_token for domo_token in domo_tokens if domo_token.owner.id == self.id
        ]

        if not domo_tokens:
            print(
                f"Domo User {self.id} - {self.display_name} does not have any access tokens"
            )
            return []

        self.domo_access_tokens = domo_tokens

        return self.domo_access_tokens


@dataclass
class DomoUsers(DomoManager):
    """a class for searching for Users"""

    auth: DomoAuth = field(repr=False)
    users: list[DomoUser] = field(default_factory=list)
    virtual_users: list[DomoUser] = field(default_factory=list)

    @classmethod
    def _users_to_domo_user(cls, user_ls, auth: DomoAuth):
        return [DomoUser.from_dict(auth=auth, obj=obj) for obj in user_ls]

    @classmethod
    def _users_to_virtual_user(cls, user_ls, auth: DomoAuth):
        return [DomoUser.from_virtual_dict(auth=auth, obj=obj) for obj in user_ls]

    @staticmethod
    def _util_match_domo_users_to_emails(
        domo_users: list[DomoUser], user_email_ls: list[str]
    ) -> list[DomoUser]:
        """pass in an array of user emails to match against an array of Domo User"""

        return [
            domo_user
            for domo_user in domo_users
            if domo_user.email_address
            and domo_user.email_address.lower()
            in [email.lower() for email in user_email_ls]
        ]

    @staticmethod
    def _util_match_users_obj_to_emails(
        user_ls: list[dict], user_email_ls: list[str]
    ) -> list:
        """pass in an array of user emails to match against an array of Domo User"""

        return [
            obj
            for obj in user_ls
            if obj.get("emailAddress", "").lower()
            in [email.lower() for email in user_email_ls]
        ]

    async def get(
        self,
        *args,
        return_raw: bool = False,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        session: httpx.AsyncClient | None = None,
        **kwargs,
    ) -> list[DomoUser]:
        """retrieves all users from Domo"""

        res = await user_routes.get_all_users(
            auth=self.auth,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=self.__class__.__name__,
            session=session,
        )

        if return_raw:
            return res

        self.users = self._users_to_domo_user(user_ls=res.response, auth=self.auth)
        return self.users

    async def search_by_email(
        self,
        email: Union[str, list[str]],
        only_allow_one: bool = True,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        return_raw: bool = False,
        suppress_no_results_error: bool = False,
        session: httpx.AsyncClient | None = None,
    ) -> Union[list[DomoUser], DomoUser, ResponseGetData, bool]:
        emails = [email] if isinstance(email, str) else email

        try:
            res = await user_routes.search_users_by_email(
                user_email_ls=emails,
                auth=self.auth,
                return_raw=return_raw,
                debug_api=debug_api,
                debug_num_stacks_to_drop=debug_num_stacks_to_drop,
                parent_class=self.__class__.__name__,
                session=session,
            )

        except SearchUserNotFoundError as e:
            if suppress_no_results_error:
                return []

            raise e from e

        if return_raw:
            return res

        domo_users = self._users_to_domo_user(res.response, auth=self.auth)

        if not only_allow_one:
            return domo_users

        domo_users = self._util_match_domo_users_to_emails(domo_users, emails)

        if not domo_users:
            raise DomoUser_NoSearchError(
                cls_instance=self,
                message=f"unable to find {','.join(emails)}",
                domo_instance=self.auth.domo_instance,
            )

        return domo_users[0]

    async def search_by_id(
        self,
        user_ids: list[str],  # can search for one or multiple users
        suppress_no_results_error: bool = False,
        only_allow_one: bool = True,
        debug_num_stacks_to_drop=2,
        debug_api: bool = False,
        return_raw: bool = False,
        session: httpx.AsyncClient | None = None,
    ) -> Union[list[DomoUser], DomoUser, ResponseGetData, bool]:
        res = None

        try:
            res = await user_routes.search_users_by_id(
                return_raw=return_raw,
                user_ids=user_ids,
                debug_api=debug_api,
                auth=self.auth,
                debug_num_stacks_to_drop=debug_num_stacks_to_drop,
                parent_class=self.__class__.__name__,
                session=session,
            )

        except SearchUserNotFoundError as e:
            if suppress_no_results_error:
                print(e)

                if only_allow_one:
                    return False
                return []

            raise e from e

        if return_raw:
            return res

        domo_users = self._users_to_domo_user(user_ls=res.response, auth=self.auth)

        if only_allow_one:
            return domo_users[0]

        return domo_users

    async def get_virtual_user_by_subscriber_instance(
        self,
        subscriber_instance_ls: str,
        debug_api: bool = False,
        return_raw: bool = False,
    ):
        res = await user_routes.search_virtual_user_by_subscriber_instance(
            auth=self.auth,
            subscriber_instance_ls=subscriber_instance_ls,
            debug_api=debug_api,
        )

        if return_raw:
            return res

        domo_users = self._users_to_virtual_user(res.response, auth=self.auth)
        self.virtual_users = domo_users
        return domo_users

    @log_call(action_name="class")
    async def upsert(
        self,
        email_address: str,
        display_name: Optional[str] = None,
        role: Optional[Any] = None,  # DomoRole
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        session: httpx.AsyncClient | None = None,
    ) -> DomoUser:
        """Upsert a Domo user - update if exists, create if not.

        Args:
            email_address: User email address (required)
            display_name: User display name (optional)
            role: DomoRole object (optional, will use default if not provided on creation)
            debug_api: Enable debug output for API calls
            debug_num_stacks_to_drop: Number of stack frames to drop in logging
            session: Optional httpx session for connection pooling

        Returns:
            DomoUser: The created or updated user

        Raises:
            ValidationError: If email address is invalid
        """
        test_valid_email(email_address)

        try:
            # Type narrowing: when only_allow_one=True and successful, returns DomoUser
            domo_user: DomoUser = await self.search_by_email(
                email=email_address,
                only_allow_one=True,
                debug_api=debug_api,
                session=session,
                debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
            )

            await logger.info(f"domo_user found {domo_user.id}")

            # Type guard to ensure we have a DomoUser instance
            if not isinstance(domo_user, DomoUser):
                raise ValueError(f"Expected DomoUser, got {type(domo_user)}")

            property_ls = []
            if display_name:
                property_ls.append(
                    user_routes.UserProperty(
                        user_routes.UserProperty_Type.display_name, display_name
                    )
                )

            if role and hasattr(role, "id") and role.id:
                property_ls.append(
                    user_routes.UserProperty(
                        user_routes.UserProperty_Type.role_id, role.id
                    )
                )

            if property_ls:
                await logger.info("Updating user properties for existing user.")
                await domo_user.update_properties(
                    property_ls=property_ls,
                    debug_api=debug_api,
                    session=session,
                )
            return domo_user

        except (SearchUserNotFoundError, DomoUser_NoSearchError):
            # User doesn't exist, create new one

            await logger.info("User not found, creating new user.")

            created_user = await DomoUser.create(
                display_name=display_name
                or f"{email_address} - via dl {dt.date.today()}",
                email_address=email_address,
                debug_api=debug_api,
                session=session,
                auth=self.auth,
                role=role,
            )

            # Type guard for created user
            if created_user is None:
                raise ValueError(f"Failed to create user for email: {email_address}")

            await self.get()

            return created_user
