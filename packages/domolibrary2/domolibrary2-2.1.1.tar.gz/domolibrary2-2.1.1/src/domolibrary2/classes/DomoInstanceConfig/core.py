__all__ = ["DomoInstanceConfig"]


from dataclasses import dataclass, field
from typing import Any

import httpx
import pandas as pd

from ...auth import DomoAuth
from ...base.exceptions import ClassError
from ...routes import (
    application as application_routes,
    sandbox as sandbox_routes,
)
from ...routes.auth import InvalidAuthTypeError
from ...routes.instance_config import (
    authorized_domains as domains_routes,
    toggle as toggle_routes,
)
from ..DomoDataset.connector import DomoConnectors
from .access_token import DomoAccessTokens
from .allowlist import DomoAllowlist
from .api_client import ApiClients
from .bootstrap import DomoBootstrap
from .instance_switcher import InstanceSwitcher
from .mfa import MFA_Config
from .publish import DomoEverywhere
from .role import DomoRoles
from .role_grant import DomoGrants
from .sso import SSO as SSO_Class
from .toggle import DomoToggle
from .user_attributes import UserAttributes


@dataclass
class DomoInstanceConfig:
    """utility class that absorbs many of the domo instance configuration methods"""

    auth: DomoAuth = field(repr=False)

    Accounts: Any = field(default=None)
    AccessTokens: DomoAccessTokens = field(default=None)
    Allowlist: DomoAllowlist = field(default=None)
    ApiClients: "ApiClients" = field(default=None)
    Bootstrap: DomoBootstrap = field(default=None)

    Connectors: DomoConnectors = field(default=None)
    InstanceSwitcher: "InstanceSwitcher" = field(default=None)

    Grants: DomoGrants = field(default=None)

    MFA: MFA_Config = field(default=None)
    Roles: DomoRoles = field(default=None)

    SSO: SSO_Class = field(default=None)
    Everywhere: DomoEverywhere = field(default=None)
    UserAttributes: "UserAttributes" = field(default=None)
    Toggle: DomoToggle = field(default=None)

    def __post_init__(self):
        from ..DomoAccount import DomoAccounts
        from .api_client import ApiClients
        from .instance_switcher import InstanceSwitcher
        from .user_attributes import UserAttributes

        self.Accounts = DomoAccounts(auth=self.auth)
        self.AccessTokens = DomoAccessTokens(auth=self.auth)
        self.ApiClients = ApiClients(auth=self.auth)
        self.Allowlist = DomoAllowlist(auth=self.auth)
        self.Bootstrap = DomoBootstrap(auth=self.auth)

        self.Connectors = DomoConnectors(auth=self.auth)
        self.Grants = DomoGrants(auth=self.auth)
        self.InstanceSwitcher = InstanceSwitcher(auth=self.auth)
        self.MFA = MFA_Config(auth=self.auth)
        self.Everywhere = DomoEverywhere(auth=self.auth)
        self.UserAttributes = UserAttributes(auth=self.auth)
        self.Roles = DomoRoles(auth=self.auth)
        self.SSO = SSO_Class(auth=self.auth)

    async def get_applications(
        self,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        return_raw: bool = False,
        debug_num_stacks_to_drop=2,
    ):
        from ..DomoApplication.Application import DomoApplication

        res = await application_routes.get_applications(
            auth=self.auth,
            debug_api=debug_api,
            session=session,
            parent_class=self.__class__.__name__,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

        if return_raw:
            return res

        return [DomoApplication.from_dict(job, auth=self.auth) for job in res.response]

    async def generate_applications_report(
        self,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        return_raw: bool = False,
        debug_num_stacks_to_drop=2,
    ):
        domo_apps = await self.get_applications(
            debug_api=debug_api,
            session=session,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            return_raw=return_raw,
        )

        if return_raw:
            return domo_apps

        df = pd.DataFrame([app.__dict__ for app in domo_apps])
        df["domo_instance"] = self.auth.domo_instance

        df.drop(columns=["auth"], inplace=True)
        df.rename(
            columns={
                "id": "application_id",
                "name": "application_name",
                "description": "application_description",
                "version": "application_version",
            },
            inplace=True,
        )

        return df.sort_index(axis=1)

    async def get_authorized_domains(
        self,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        return_raw: bool = False,
    ) -> list[str]:
        """returns a list of authorized domains (str) does not update instance_config"""

        res = await domains_routes.get_authorized_domains(
            auth=self.auth, debug_api=debug_api, session=session, return_raw=return_raw
        )

        if return_raw:
            return res

        return res.response

    async def set_authorized_domains(
        self,
        authorized_domains: list[str],
        debug_api: bool = False,
        debug_num_stacks_to_drop=1,
        session: httpx.AsyncClient = None,
    ):
        res = await domains_routes.set_authorized_domains(
            auth=self.auth,
            authorized_domain_ls=authorized_domains,
            debug_api=debug_api,
            session=session,
            parent_class=self.__class__.__name__,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

        return res

    async def upsert_authorized_domains(
        self,
        authorized_domains: list[str],
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        debug_num_stacks_to_drop=2,
    ):
        existing_domains = await self.get_authorized_domains(
            debug_api=debug_api,
            session=session,
        )

        authorized_domains += existing_domains

        return await self.set_authorized_domains(
            authorized_domains=authorized_domains,
            debug_api=debug_api,
            session=session,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
        )

    async def get_authorized_custom_app_domains(
        self,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        return_raw: bool = False,
        debug_num_stacks_to_drop=2,
    ) -> list[str]:
        res = await domains_routes.get_authorized_custom_app_domains(
            auth=self.auth,
            debug_api=debug_api,
            session=session,
            return_raw=return_raw,
            parent_class=self.__class__.__name__,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

        if return_raw:
            return res

        return res.response

        # | exporti

    async def set_authorized_custom_app_domains(
        self,
        authorized_domains: list[str],
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        session: httpx.AsyncClient = None,
    ):
        res = await domains_routes.set_authorized_custom_app_domains(
            auth=self.auth,
            authorized_custom_app_domain_ls=authorized_domains,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            session=session,
            parent_class=self.__class__.__name__,
        )

        return res

    async def upsert_authorized_custom_app_domains(
        self,
        authorized_domains: list[str],
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        session: httpx.AsyncClient = None,
    ):
        existing_domains = await self.get_authorized_custom_app_domains(
            debug_api=debug_api,
            session=session,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
        )

        authorized_domains += existing_domains

        return await self.set_authorized_custom_app_domains(
            authorized_domains=authorized_domains,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
            session=session,
        )

    async def get_sandbox_is_same_instance_promotion_enabled(
        self,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        return_raw: bool = False,
        debug_num_stacks_to_drop=2,
    ):
        res = await sandbox_routes.get_is_allow_same_instance_promotion_enabled(
            auth=self.auth,
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=self.__class__.__name__,
        )

        self.is_sandbox_self_instance_promotion_enabled = res.response["is_enabled"]

        if return_raw:
            return res

        return res.response

    async def toggle_sandbox_allow_same_instance_promotion(
        self,
        is_enabled: bool,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        return_raw: bool = False,
        debug_num_stacks_to_drop=2,
    ):
        """will enable or disable same instance promotion for sandbox"""

        res = await sandbox_routes.toggle_allow_same_instance_promotion(
            auth=self.auth,
            session=session,
            is_enabled=is_enabled,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=self.__class__.__name__,
        )

        res_is_enabled = await self.get_sandbox_is_same_instance_promotion_enabled()

        if return_raw:
            return res

        return res_is_enabled

    async def get_is_user_invite_notification_enabled(
        self,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        debug_num_stacks_to_drop: int = 2,
        return_raw: bool = False,
    ):
        """
        Admin > Company Settings > Admin Notifications
        Toggles whether user recieves 'You've been Domo'ed email
        """

        res = await toggle_routes.get_is_user_invite_notifications_enabled(
            auth=self.auth,
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=self.__class__.__name__,
        )

        self.is_user_invite_notification_enabled = res.response["is_enabled"]

        if return_raw:
            return res

        return res.response

    async def toggle_is_user_invite_notification_enabled(
        self,
        is_enabled: bool,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        debug_num_stacks_to_drop: int = 2,
        return_raw: bool = False,
    ):
        res_is_enabled = await self.get_is_user_invite_notification_enabled()

        if is_enabled == self.is_user_invite_notification_enabled:
            return res_is_enabled

        res = await toggle_routes.toggle_is_user_invite_enabled(
            auth=self.auth,
            is_enabled=is_enabled,
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=self.__class__.__name__,
        )

        res_is_enabled = await self.get_is_user_invite_notification_enabled()

        if return_raw:
            return res

        return res_is_enabled

    class InstanceConfig_ClassError(ClassError):
        def __init__(self, cls_instance, message):
            super().__init__(
                cls_instance=cls_instance,
                message=message,
                entity_id=cls_instance.auth.domo_instance,
            )

    async def get_is_invite_social_users_enabled(
        self,
        customer_id: str = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        session: httpx.AsyncClient = None,
        return_raw: bool = False,
    ):
        """checks if users can be invited as social users to the instaance"""

        if not customer_id:
            from .bootstrap import DomoBootstrap

            try:
                bs = DomoBootstrap(auth=self.auth)
                customer_id = await bs.get_customer_id()

            except InvalidAuthTypeError as e:
                raise self.InstanceConfig_ClassError(
                    self,
                    message=f"{e.__class__.__name__} -- bootstrap API requires FullAuth",
                ) from e

        res = await toggle_routes.get_is_invite_social_users_enabled(
            auth=self.auth,
            customer_id=customer_id,
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=self.__class__.__name__,
        )

        self.is_invite_social_users_enabled = res.response["is_enabled"]

        if return_raw:
            return res

        return res.response

    async def toggle_is_invite_social_users_enabled(
        self,
        is_enabled: bool,
        customer_id: str = None,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        debug_num_stacks_to_drop=2,
        return_raw: bool = False,
    ):
        """enables or disables the ability to invite users to instance as social users"""

        # Get customer_id if not provided
        if not customer_id:
            from .bootstrap import DomoBootstrap

            try:
                bs = DomoBootstrap(auth=self.auth)
                customer_id = await bs.get_customer_id()

            except InvalidAuthTypeError as e:
                raise self.InstanceConfig_ClassError(
                    self,
                    message=f"{e.__class__.__name__} -- bootstrap API requires FullAuth",
                ) from e

        res_is_enabled = await self.get_is_invite_social_users_enabled(
            customer_id=customer_id
        )

        if is_enabled == self.is_invite_social_users_enabled:
            return res_is_enabled

        res = await toggle_routes.toggle_is_invite_social_users_enabled(
            auth=self.auth,
            customer_id=customer_id,
            is_enabled=is_enabled,
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=self.__class__.__name__,
        )

        res_is_enabled = await self.get_is_invite_social_users_enabled()

        if return_raw:
            return res

        return res_is_enabled

    async def get_is_weekly_digest_enabled(
        self,
        return_raw: bool = False,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        session: httpx.AsyncClient = None,
    ):
        """the weekly digest is a weekly email from Domo of changes to the instance"""

        res = await toggle_routes.get_is_weekly_digest_enabled(
            auth=self.auth,
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=self.__class__.__name__,
        )

        if return_raw:
            return res

        self.is_weekly_digest_enabled = res.response["is_enabled"]

        return res.response

    async def toggle_is_weekly_digest_enabled(
        self,
        is_enabled: bool,
        return_raw: bool = False,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        debug_prn: bool = False,
        debug_num_stacks_to_drop=2,
    ):
        """toggles if weekly digest is enabled or disabled"""

        res_is_enabled = await self.get_is_weekly_digest_enabled()

        if is_enabled == self.is_weekly_digest_enabled:
            if debug_prn:
                print(
                    f"weekly digest is already {'enabled' if is_enabled else 'disabled'} in {self.auth.domo_instance}"
                )
            return res_is_enabled

        if debug_prn:
            print(
                f"{'enabling' if is_enabled else 'disabling'} weekly digest {self.auth.domo_instance}"
            )

        res = await toggle_routes.toggle_is_weekly_digest_enabled(
            auth=self.auth,
            is_enabled=is_enabled,
            session=session,
            debug_api=debug_api,
            parent_class=self.__class__.__name__,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

        res_is_enabled = await self.get_is_weekly_digest_enabled()

        if return_raw:
            return res

        return res_is_enabled

    async def toggle_is_left_nav_enabled(
        self,
        is_use_left_nav: bool = True,
        return_raw: bool = False,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop=1,
    ):
        """toggles the use of the left nav in Domo"""

        res = await toggle_routes.toggle_is_left_nav_enabled(
            auth=self.auth,
            is_use_left_nav=is_use_left_nav,
            session=session,
            debug_api=debug_api,
            parent_class=self.__class__.__name__,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

        if return_raw:
            return res

        self.is_use_left_nav = res.response["is_enabled"]

        return res

    async def get_is_left_nav_enabled(
        self,
        return_raw: bool = False,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop=1,
    ):
        """gets the use of the left nav in Domo"""

        res = await toggle_routes.get_is_left_nav_enabled(
            auth=self.auth,
            session=session,
            debug_api=debug_api,
            parent_class=self.__class__.__name__,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

        if return_raw:
            return res

        self.is_use_left_nav = res.response["is_enabled"]

        return res
