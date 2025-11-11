__all__ = [
    "SSO_AddUserDirectSignonError",
    "toggle_user_direct_signon_access",
    "SSO_GET_Error",
    "SSO_CRUD_Error",
    "get_sso_oidc_config",
    "generate_sso_oidc_body",
    "update_sso_oidc_config",
    "get_sso_saml_config",
    "get_sso_saml_certificate",
    "generate_sso_saml_body",
    "update_sso_saml_config",
    "toggle_sso_skip_to_idp",
    "toggle_sso_custom_attributes",
    "set_sso_certificate",
]

from typing import Optional

import httpx

from ... import auth as dmda
from ...base import exceptions as dmde
from ...client import (
    get_data as gd,
    response as rgd,
)
from .exceptions import Config_CRUD_Error, Config_GET_Error


class SSO_AddUserDirectSignonError(Config_CRUD_Error):
    def __init__(self, res: rgd.ResponseGetData, user_id_ls: list[str], message=None):
        message = (
            message or f"unable to add {', '.join(user_id_ls)} to DSO {res.response}"
        )
        super().__init__(res=res, message=message)


class SSO_GET_Error(Config_GET_Error):
    def __init__(self, res: rgd.ResponseGetData, message=None):
        message = (
            message
            or f"unable to rerieve SSO Config for {res.auth.domo_instance} - {res.response}"  # type: ignore
        )
        super().__init__(res=res, message=message)


class SSO_CRUD_Error(dmde.RouteError):
    def __init__(self, res: rgd.ResponseGetData, message=None):
        super().__init__(
            res=res,
            message=message
            or f"unable to update SSO Config for {res.auth.domo_instance} - {res.response}",  # type: ignore
        )


@gd.route_function
async def toggle_user_direct_signon_access(
    auth: dmda.DomoAuth,
    user_id_ls: list[str],
    is_enable_direct_signon: bool = True,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    parent_class=None,
    debug_num_stacks_to_drop=1,
) -> rgd.ResponseGetData:
    user_id_ls = user_id_ls if isinstance(user_id_ls, list) else [user_id_ls]

    url = f"https://{auth.domo_instance}.domo.com/api/content/v3/users/directSignOn"

    res = await gd.get_data(
        auth=auth,
        url=url,
        params={"value": is_enable_direct_signon},
        method="POST",
        body=user_id_ls,
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if not res.is_success:
        raise SSO_AddUserDirectSignonError(res=res, user_id_ls=user_id_ls)

    res.response = f"successfully added {', '.join(user_id_ls)} to direct signon list in {auth.domo_instance}"

    return res


@gd.route_function
async def get_sso_oidc_config(
    auth: dmda.DomoAuth,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    parent_class: Optional[str] = None,
    debug_num_stacks_to_drop=1,
):
    """Open ID Connect framework"""

    url = f"https://{auth.domo_instance}.domo.com/api/identity/v1/authentication/oidc/std/settings"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if not res.is_success:
        raise SSO_GET_Error(res=res)

    return res


def generate_sso_oidc_body(
    is_include_undefined: bool = False,
    login_enabled: bool = False,  # False
    idp_enabled: bool = False,  # False
    import_groups: bool = False,  # False
    require_invitation: bool = False,  # False
    enforce_allowlist: bool = False,  # False
    skip_to_idp: bool = False,  # False
    auth_request_endpoint: str = "",
    token_endpoint: str = "",
    user_info_endpoint: str = "",
    public_key: str = "",
    redirect_url: str = "",
    idp_certificate: str = "",
    override_sso: bool = False,  # False
    override_embed: bool = False,  # False
    # "https://{domo_instance}}.domo.com/auth/oidc"
    well_known_config: str = "",
    assertion_endpoint: str = "",
    ingest_attributes: bool = False,  # False
):
    r = {
        "loginEnabled": login_enabled,
        "idpEnabled": idp_enabled,
        "importGroups": import_groups,
        "requireInvitation": require_invitation,
        "enforceWhitelist": enforce_allowlist,
        "skipToIdp": skip_to_idp,
        "authRequestEndpoint": auth_request_endpoint,
        "tokenEndpoint": token_endpoint,
        "userInfoEndpoint": user_info_endpoint,
        "publicKey": public_key,
        "redirectUrl": redirect_url,
        "certificate": idp_certificate,
        "overrideSSO": override_sso,
        "overrideEmbed": override_embed,
        "wellKnownConfig": well_known_config,
        "assertionEndpoint": assertion_endpoint,
        "ingestAttributes": ingest_attributes,
    }

    if not is_include_undefined:
        return {key: value for key, value in r.items() if value is not None}

    return r


@gd.route_function
async def _update_sso_oidc_temp_config(
    auth: dmda.DomoAuth,
    body_sso: dict,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    parent_class: Optional[str] = None,
    debug_num_stacks_to_drop=1,
):
    """to successfully update the SSO Configuration, you must send all the parameters related to SSO Configuration"""

    url = f"https://{auth.domo_instance}.domo.com/api/identity/v1/authentication/oidc/temp/settings"

    res = await gd.get_data(
        auth=auth,
        url=url,
        body=body_sso,
        method="PUT",
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if not res.is_success:
        raise SSO_CRUD_Error(res=res)
    return res


@gd.route_function
async def _update_sso_oidc_standard_config(
    auth: dmda.DomoAuth,
    body_sso: dict,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    parent_class: Optional[str] = None,
    debug_num_stacks_to_drop=1,
):
    """to successfully update the SSO Configuration, you must send all the parameters related to SSO Configuration"""

    url = f"https://{auth.domo_instance}.domo.com/api/identity/v1/authentication/oidc/std/settings"

    res = await gd.get_data(
        auth=auth,
        url=url,
        body=body_sso,
        method="PUT",
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if not res.is_success:
        raise SSO_CRUD_Error(res=res)

    if not body_sso.get("idpEnabled"):
        res.response = "successfully disabled SSO"
        return res

    res.response = "successfully updated oidc config"

    return res


@gd.route_function
async def update_sso_oidc_config(
    auth: dmda.DomoAuth,
    body_sso: dict,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    parent_class: Optional[str] = None,
    debug_num_stacks_to_drop=1,
):
    """
    to update saml config must update temp and then standard
    typically would hide under class functions, but b/c Domo won't update w/o it, pushing down to Route
    """

    await _update_sso_oidc_temp_config(
        auth=auth,
        body_sso=body_sso,
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
    )

    return await _update_sso_oidc_standard_config(
        auth=auth,
        body_sso=body_sso,
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
    )


@gd.route_function
async def get_sso_saml_config(
    auth: dmda.DomoAuth,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    parent_class: Optional[str] = None,
    debug_num_stacks_to_drop=1,
):
    """Security Assertion Markup Language"""

    url = f"https://{auth.domo_instance}.domo.com/api/identity/v1/authentication/saml/std/settings"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if not res.is_success:
        raise SSO_GET_Error(res=res)

    return res


@gd.route_function
async def get_sso_saml_certificate(
    auth: dmda.DomoAuth,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    parent_class: Optional[str] = None,
    debug_num_stacks_to_drop=1,
):
    res = await get_sso_saml_config(
        auth=auth,
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
    )

    res.response = res.response.get("idpCertificate")

    return res


def generate_sso_saml_body(
    is_include_undefined: bool = False,  # leave it as False to prevent overriding values you don't want to update
    is_enabled: bool = False,
    auth_request_endpoint: str = "",  # url
    issuer: str = "",  # url
    idp_certificate: str = "",
    import_groups: bool = False,
    require_invitation: bool = False,
    enforce_allowlist: bool = False,
    relay_state: bool = False,
    redirect_url: Optional[str] = None,  # url
    idp_enabled: bool = False,
    skip_to_idp: bool = False,
    login_enabled=None,
    token_endpoint=None,
    user_info_endpoint=None,
    public_key=None,
    override_sso=None,
    override_embed=None,
    well_known_config=None,
    assertion_endpoint=None,
    ingest_attributes=None,
    custom_attributes=None,
    sign_auth_request=None,
):
    if skip_to_idp is not None:
        skip_to_idp = str(skip_to_idp).lower()  # type: ignore

    r = {
        "enabled": is_enabled,
        "authRequestEndpoint": auth_request_endpoint,
        "issuer": issuer,
        "idpCertificate": idp_certificate,
        "importGroups": import_groups,
        "requireInvitation": require_invitation,
        "enforceWhitelist": enforce_allowlist,
        "relayState": "true" if relay_state else "false",
        "idpEnabled": idp_enabled,
        "skipToIdp": skip_to_idp,
        "customAttributes": custom_attributes,
        "loginEnabled": login_enabled,
        "tokenEndpoint": token_endpoint,
        "userInfoEndpoint": user_info_endpoint,
        "publicKey": public_key,
        "redirectUrl": redirect_url,
        "overrideSSO": override_sso,
        "overrideEmbed": override_embed,
        "wellKnownConfig": well_known_config,
        "assertionEndpoint": assertion_endpoint,
        "ingestAttributes": ingest_attributes,
        "signAuthRequest": sign_auth_request,
    }

    if not is_include_undefined:
        return {key: value for key, value in r.items() if value is not None}

    return r


@gd.route_function
async def _update_sso_saml_temp_config(
    auth: dmda.DomoAuth,
    body_sso: dict,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    parent_class: Optional[str] = None,
    debug_num_stacks_to_drop=1,
):
    url = f"https://{auth.domo_instance}.domo.com/api/identity/v1/authentication/saml/temp/settings"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body_sso,
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if not res.is_success:
        raise SSO_CRUD_Error(res=res)

    res.response = "successfully updated temp saml config"
    return res


@gd.route_function
async def _update_sso_saml_standard_config(
    auth: dmda.DomoAuth,
    body_sso: dict,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    parent_class: Optional[str] = None,
    debug_num_stacks_to_drop=1,
):
    url = f"https://{auth.domo_instance}.domo.com/api/identity/v1/authentication/saml/std/settings"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body_sso,
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if not res.is_success:
        raise SSO_CRUD_Error(res=res)

    if not body_sso.get("enabled"):
        res.response = "successfully disabled SSO"
        return res

    res.response = "successfully updated saml config"

    return res


@gd.route_function
async def update_sso_saml_config(
    auth: dmda.DomoAuth,
    body_sso: dict,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    parent_class: Optional[str] = None,
    debug_num_stacks_to_drop=1,
):
    """
    to update saml config must update temp and then standard
    typically would hide under class functions, but b/c Domo won't update w/o it, pushing down to Route
    """

    await _update_sso_saml_temp_config(
        auth=auth,
        body_sso=body_sso,
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
    )

    return await _update_sso_saml_standard_config(
        auth=auth,
        body_sso=body_sso,
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
    )


@gd.route_function
async def toggle_sso_skip_to_idp(
    auth: dmda.DomoAuth,
    is_skip_to_idp: bool,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    parent_class: Optional[str] = None,
    debug_num_stacks_to_drop=1,
):
    url = f"https://{auth.domo_instance}.domo.com/api/customer/v1/properties/domo.policy.sso.skip_to_idp"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body={"value": str(is_skip_to_idp).lower()},
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if not res.is_success:
        raise SSO_CRUD_Error(res=res)

    res.response = f"toggled skip_to_idp - {str(is_skip_to_idp)}"
    return res


@gd.route_function
async def toggle_sso_custom_attributes(
    auth: dmda.DomoAuth,
    is_custom_attributes: bool,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    parent_class: Optional[str] = None,
    debug_num_stacks_to_drop=1,
):
    """unsure what this API does"""

    url = f"https://{auth.domo_instance}.domo.com/api/customer/v1/properties/authentication.saml.custom_attributes"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body={"value": is_custom_attributes},
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if not res.is_success:
        raise SSO_CRUD_Error(res=res)

    res.response = f"toggled is_custom_attributes - {str(is_custom_attributes)}"

    return res


@gd.route_function
async def set_sso_certificate(
    auth: dmda.DomoAuth,
    idp_certificate: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    parent_class: Optional[str] = None,
    debug_num_stacks_to_drop=1,
    return_raw: bool = False,
):
    url = f"https://{auth.domo_instance}.domo.com/api/identity/v1/authentication/saml/validate/cert"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body={"idpCertificate": idp_certificate},
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise SSO_CRUD_Error(res=res, message=f"API Error {res.response}")

    if isinstance(res.response, dict) and not res.response["isValid"]:
        raise SSO_CRUD_Error(
            res=res, message=f"Certificate Error: {res.response['message']}"
        )

    return res
