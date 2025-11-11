"""Dataset sharing operations."""

from enum import Enum

import httpx

from ...auth import DomoAuth
from ...base.base import DomoEnumMixin
from ...client import (
    get_data as gd,
    response as rgd,
)
from .exceptions import Dataset_GET_Error, ShareDataset_Error


class ShareDataset_AccessLevelEnum(DomoEnumMixin, Enum):
    CO_OWNER = "CO_OWNER"
    CAN_EDIT = "CAN_EDIT"
    CAN_SHARE = "CAN_SHARE"


def generate_share_dataset_payload(
    entity_type,  # USER or GROUP
    entity_id,
    access_level: ShareDataset_AccessLevelEnum = ShareDataset_AccessLevelEnum.CAN_SHARE,
    is_send_email: bool = False,
):
    return {
        "permissions": [
            {"type": entity_type, "id": entity_id, "accessLevel": access_level.value}
        ],
        "sendEmail": is_send_email,
    }


@gd.route_function
async def share_dataset(
    auth: DomoAuth,
    dataset_id: str,
    body: dict,
    debug_api: bool = False,
    debug_num_stacks_to_drop=1,
    parent_class=None,
    session: httpx.AsyncClient | None = None,
):
    url = f"https://{auth.domo_instance}.domo.com/api/data/v3/datasources/{dataset_id}/share"

    res = await gd.get_data(
        auth=auth,
        method="POST",
        url=url,
        body=body,
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if not res.is_success:
        raise ShareDataset_Error(dataset_id=dataset_id, res=res)

    update_user_ls = [f"{user['type']} - {user['id']}" for user in body["permissions"]]

    res.response = (
        f"updated access list {', '.join(update_user_ls)} added to {dataset_id}"
    )
    return res


@gd.route_function
async def get_permissions(
    auth: DomoAuth,
    dataset_id: str,
    debug_api: bool = False,
    debug_num_stacks_to_drop=1,
    parent_class: str | None = None,
    session: httpx.AsyncClient | None = None,
) -> rgd.ResponseGetData:
    """retrieve the schema for a dataset"""

    url = f"https://{auth.domo_instance}.domo.com/api/data/v3/datasources/{dataset_id}/permissions"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
    )

    if not res.is_success:
        raise Dataset_GET_Error(dataset_id=dataset_id, res=res)

    return res
