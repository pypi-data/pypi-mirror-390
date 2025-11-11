"""
Jupyter Content Management Functions

This module provides functions for managing content within Jupyter workspaces.
"""

__all__ = [
    "get_jupyter_content",
    "create_jupyter_obj",
    "delete_jupyter_content",
    "update_jupyter_file",
    "get_content",
    "get_content_recursive",
    # Utility functions
    "generate_update_jupyter_body__new_content_path",
    "generate_update_jupyter_body__text",
    "generate_update_jupyter_body__ipynb",
    "generate_update_jupyter_body__directory",
    "GenerateUpdateJupyterBodyFactory",
    "generate_update_jupyter_body",
]

import asyncio
import os
import urllib
from enum import Enum, member
from functools import partial
from typing import Any, Optional

import httpx

from ...base.base import DomoEnumMixin
from ...client import (
    auth as dmda,
    get_data as gd,
    response as rgd,
)
from ...utils import chunk_execution as dmce
from .exceptions import (
    Jupyter_CRUD_Error,
    Jupyter_GET_Error,
    SearchJupyterNotFoundError,
)


# Utility functions for body generation
def generate_update_jupyter_body__new_content_path(content_path):
    """Generate new content path for jupyter body."""
    if not content_path:
        return ""

    ## replaces ./ if passed as part of url description
    if content_path.startswith("./"):
        content_path = content_path[2:]

    if "/" in content_path:
        return "/".join(content_path.split("/")[:-1])
    else:
        return ""


def generate_update_jupyter_body__text(body, content_path=None):
    """Generate body for text content type."""
    body.update(
        {
            "format": "text",
            "path": generate_update_jupyter_body__new_content_path(content_path),
            "type": "file",
        }
    )
    return body


def generate_update_jupyter_body__ipynb(body, content_path=None):
    """Generate body for ipynb (Jupyter notebook) content type."""
    body.update(
        {
            "format": "json",
            "path": generate_update_jupyter_body__new_content_path(content_path),
            "type": "notebook",
        }
    )
    return body


def generate_update_jupyter_body__directory(content_path, body):
    """Generate body for directory content type."""
    body.update(
        {
            "path": generate_update_jupyter_body__new_content_path(content_path),
            "format": None,
            "type": "directory",
        }
    )
    return body


class GenerateUpdateJupyterBodyFactory(DomoEnumMixin, Enum):
    """Factory for generating different types of Jupyter request bodies."""

    IPYNB = member(partial(generate_update_jupyter_body__ipynb))
    DIRECTORY = member(partial(generate_update_jupyter_body__directory))
    TEXT = member(partial(generate_update_jupyter_body__text))
    default = member(partial(generate_update_jupyter_body__text))


def generate_update_jupyter_body(
    new_content: Any,
    content_path: str,  # my_folder/datatypes.ipynb
):
    """Factory to construct properly formed body for Jupyter API requests.

    Args:
        new_content: Content to be included in the body
        content_path: Path of the content (determines content type)

    Returns:
        Dictionary containing properly formatted body for Jupyter API
    """

    if content_path.startswith("./"):
        content_path = content_path[2:]

    content_name = os.path.normpath(content_path).split(os.sep)[-1]

    if "." in content_path:
        content_type = content_path.split(".")[-1]
    else:
        content_type = "directory"

    body = {
        "name": content_name,
        "content": new_content,
        "path": content_path,
    }
    return GenerateUpdateJupyterBodyFactory.get(content_type).value(
        body=body, content_path=content_path
    )


@gd.route_function
async def get_jupyter_content(
    auth: dmda.DomoJupyterAuth,
    content_path: str = "",
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Retrieve content from a Jupyter workspace.

        Args:
            auth: Jupyter authentication object with workspace credentials
            content_path: Path to content within the workspace (default: root)
            session: Optional httpx client session for connection reuse
            debug_api: Enable detailed API request/response logging
            debug_num_stacks_to_drop: Number of stack frames to drop in debug output
            parent_class: Optional parent class name for debugging context
            return_raw: Return raw API response without processing

        Returns:
            ResponseGetData object containing workspace content

        Raises:
            Jupyter_GET_Error: If content retrieval fails
            SearchJupyterNotFoundError
    : If content path doesn't exist
    """
    dmda.test_is_jupyter_auth(auth)

    url = f"https://{auth.domo_instance}.{auth.service_location}{auth.service_prefix}api/contents/{content_path}"

    res = await gd.get_data(
        url=f"{url}",
        method="GET",
        auth=auth,
        headers={"authorization": f"Token {auth.jupyter_token}"},
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
    )

    if return_raw:
        return res

    if res.status == 403:
        raise Jupyter_GET_Error(
            message="Unable to query API, valid jupyter_token?", res=res
        )

    if res.status == 404:
        raise SearchJupyterNotFoundError(
            search_criteria=f"content_path: {content_path}", res=res
        )

    if not res.is_success:
        raise Jupyter_GET_Error(message="Failed to retrieve Jupyter content", res=res)

    return res


@gd.route_function
async def create_jupyter_obj(
    auth: dmda.DomoJupyterAuth,
    new_content: Any = "",
    content_path: str = "",
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Create new content in a Jupyter workspace.

    Args:
        auth: Jupyter authentication object with workspace credentials
        new_content: Content to create (text, notebook data, etc.)
        content_path: File name and location within the workspace
        session: Optional httpx client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to drop in debug output
        parent_class: Optional parent class name for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing creation result

    Raises:
        Jupyter_CRUD_Error: If content creation fails
    """
    dmda.test_is_jupyter_auth(auth)

    # removes ./ jic
    if content_path.startswith("./"):
        content_path = content_path[2:]

    body = generate_update_jupyter_body(
        new_content=new_content, content_path=content_path
    )

    content_path_split = os.path.normpath(content_path).split(os.sep)

    # new content gets created as "untitled folder" // removes the 'future name' and saves for later
    content_path_split.pop(-1)

    base_url = f"https://{auth.domo_instance}.{auth.service_location}{auth.service_prefix}api/contents/"

    res_post = await gd.get_data(
        url=f"{base_url}{'/'.join(content_path_split)}",
        method="POST",
        auth=auth,
        body=body,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
    )

    if return_raw:
        return res_post

    if res_post.status == 403:
        raise Jupyter_CRUD_Error(
            operation="create",
            content_path=content_path,
            message="Unable to query API, valid jupyter_token?",
            res=res_post,
        )

    if not res_post.is_success:
        raise Jupyter_CRUD_Error(
            operation="create", content_path=content_path, res=res_post
        )

    # untitled_folder
    url = urllib.parse.urljoin(base_url, res_post.response["path"])

    # created a folder "untitled folder"
    await asyncio.sleep(3)

    res = await gd.get_data(
        url=urllib.parse.quote(url, safe="/:?=&"),
        method="PATCH",
        auth=auth,
        body={"path": content_path, "content": new_content},
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
    )

    if res.status == 403:
        raise Jupyter_CRUD_Error(
            operation="rename",
            content_path=content_path,
            message="Unable to query API, valid jupyter_token?",
            res=res,
        )

    if res.status == 409:
        raise Jupyter_CRUD_Error(
            operation="rename",
            content_path=content_path,
            message="Conflict during PATCH - does the content already exist?",
            res=res,
        )

    if not res.is_success:
        raise Jupyter_CRUD_Error(operation="rename", content_path=content_path, res=res)

    res.response = {**res_post.response, **res.response}

    return res


@gd.route_function
async def delete_jupyter_content(
    auth: dmda.DomoJupyterAuth,
    content_path: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Delete content from a Jupyter workspace.

        Args:
            auth: Jupyter authentication object with workspace credentials
            content_path: File name and location within the workspace
            session: Optional httpx client session for connection reuse
            debug_api: Enable detailed API request/response logging
            debug_num_stacks_to_drop: Number of stack frames to drop in debug output
            parent_class: Optional parent class name for debugging context
            return_raw: Return raw API response without processing

        Returns:
            ResponseGetData object containing deletion result

        Raises:
            Jupyter_CRUD_Error: If content deletion fails
            SearchJupyterNotFoundError
    : If content path doesn't exist
    """
    dmda.test_is_jupyter_auth(auth)

    base_url = f"https://{auth.domo_instance}.{auth.service_location}{auth.service_prefix}api/contents/"

    url = urllib.parse.urljoin(base_url, content_path)
    url = urllib.parse.quote(url, safe="/:?=&")

    res = await gd.get_data(
        url=url,
        method="DELETE",
        auth=auth,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
    )

    if return_raw:
        return res

    if res.status == 403:
        raise Jupyter_CRUD_Error(
            operation="delete",
            content_path=content_path,
            message="Unable to query API, valid jupyter_token?",
            res=res,
        )

    if res.status == 404:
        raise SearchJupyterNotFoundError(
            search_criteria=f"content_path: {content_path}", res=res
        )

    if not res.is_success:
        raise Jupyter_CRUD_Error(operation="delete", content_path=content_path, res=res)

    return res


@gd.route_function
async def update_jupyter_file(
    auth: dmda.DomoJupyterAuth,
    new_content: Any,
    content_path: str = "",
    body: Optional[dict] = None,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Update content in a Jupyter workspace file.

        Args:
            auth: Jupyter authentication object with workspace credentials
            new_content: New content to update the file with
            content_path: File name and location within the workspace
            body: Optional custom body for the request
            session: Optional httpx client session for connection reuse
            debug_api: Enable detailed API request/response logging
            debug_num_stacks_to_drop: Number of stack frames to drop in debug output
            parent_class: Optional parent class name for debugging context
            return_raw: Return raw API response without processing

        Returns:
            ResponseGetData object containing update result

        Raises:
            Jupyter_CRUD_Error: If file update fails
            SearchJupyterNotFoundError
    : If content path doesn't exist
    """
    dmda.test_is_jupyter_auth(auth)

    body = body or generate_update_jupyter_body(new_content, content_path)

    os.path.normpath(content_path).split(os.sep)

    base_url = f"https://{auth.domo_instance}.{auth.service_location}{auth.service_prefix}api/contents/"

    url = urllib.parse.urljoin(base_url, content_path)
    url = urllib.parse.quote(url, safe="/:?=&")

    res = await gd.get_data(
        url=url,
        method="PUT",
        auth=auth,
        body=body,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
    )

    if return_raw:
        return res

    if res.status == 403:
        raise Jupyter_CRUD_Error(
            operation="update",
            content_path=content_path,
            message="Unable to query API, valid jupyter_token?",
            res=res,
        )

    if res.status == 404:
        raise SearchJupyterNotFoundError(
            search_criteria=f"content_path: {content_path}", res=res
        )

    if not res.is_success:
        raise Jupyter_CRUD_Error(operation="update", content_path=content_path, res=res)

    return res


async def get_content_recursive(
    auth: dmda.DomoJupyterAuth,
    all_rows,
    content_path,
    logs,
    res: rgd.ResponseGetData,
    obj: dict = None,
    is_recursive: bool = True,
    is_skip_recent_executions: bool = True,
    is_skip_default_files: bool = True,
    return_raw: bool = False,
    debug_api: bool = False,
    debug_num_stacks_to_drop=0,
    parent_class=None,
    session: httpx.AsyncClient = None,
):
    """Recursively retrieve content from a Jupyter workspace."""
    # set path (on initial execution there is no object)
    if not obj:
        s = {"type": "begin", "content_path": content_path}
        logs.append(s)

        obj_res = await get_jupyter_content(
            auth=auth,
            content_path=content_path,
            return_raw=return_raw,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
            parent_class=parent_class,
            session=session,
        )

        obj = obj_res.response

        if not res:
            res = obj_res

        s.update({"content_path": content_path})
        logs.append(s)

    obj_content = obj.get("content", [])

    # extract relevant logs
    skip_ls = []
    if is_skip_default_files:
        skip_ls = [".ipynb_checkpoints"]

    if is_skip_recent_executions:
        skip_ls = skip_ls + [f for f in obj_content if "last_modified" in f.keys()]

    obj_content = [f for f in obj_content if f["name"] not in skip_ls]

    s = {
        "type": "check in",
        "path": obj["path"],
        "content": len(obj_content),
        "all_rows": len(all_rows),
    }

    all_rows.append(obj)
    s.update({"is_append": True})
    logs.append(s)

    res.response = all_rows
    res.logs = logs

    if obj["type"] != "directory":
        return res

    s.update({"content": len(obj_content), "all_rows": len(all_rows)})
    logs.append(s)

    res.response = all_rows
    res.logs = logs

    if not is_recursive:
        return res

    if len(obj_content) > 0:
        await dmce.gather_with_concurrency(
            *[
                get_content_recursive(
                    auth=auth,
                    content_path=content["path"],
                    all_rows=all_rows,
                    logs=logs,
                    res=res,
                    is_skip_recent_executions=is_skip_recent_executions,
                    is_skip_default_files=is_skip_default_files,
                    debug_api=debug_api,
                    debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
                    parent_class=parent_class,
                    session=session,
                )
                for content in obj_content
            ],
            n=5,
        )

    return res


@gd.route_function
async def get_content(
    auth: dmda.DomoJupyterAuth,
    content_path: str = "",
    is_recursive: bool = True,
    is_skip_recent_executions: bool = True,
    is_skip_default_files: bool = True,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 2,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Get content from a Jupyter workspace recursively.

        Args:
            auth: Jupyter authentication object with workspace credentials
            content_path: Path to start retrieving content from
            is_recursive: Whether to recursively get nested directory content
            is_skip_recent_executions: Skip files with recent execution timestamps
            is_skip_default_files: Skip default workspace files
            session: Optional httpx client session for connection reuse
            debug_api: Enable detailed API request/response logging
            debug_num_stacks_to_drop: Number of stack frames to drop in debug output
            parent_class: Optional parent class name for debugging context
            return_raw: Return raw API response without processing

        Returns:
            ResponseGetData object containing all workspace content

        Raises:
            Jupyter_GET_Error: If content retrieval fails
            SearchJupyterNotFoundError
    : If content path doesn't exist
    """
    dmda.test_is_jupyter_auth(auth)

    all_rows = []
    logs = []
    res = None

    return await get_content_recursive(
        auth=auth,
        content_path=content_path,
        all_rows=all_rows,
        logs=logs,
        res=res,
        is_recursive=is_recursive,
        is_skip_recent_executions=is_skip_recent_executions,
        is_skip_default_files=is_skip_default_files,
        return_raw=return_raw,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
    )
