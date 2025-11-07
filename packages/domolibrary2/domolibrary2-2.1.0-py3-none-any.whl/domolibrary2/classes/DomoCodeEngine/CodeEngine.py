"""DomoCodeEngine Package and Version Classes

This module provides classes for interacting with Domo CodeEngine packages including
package management, version control, and code deployment.

Classes:
    DomoCodeEngine_Package: Main package entity class
    DomoCodeEngine_Packages: Manager class for package collections
    DomoCodeEngine_PackageVersion: Package version subentity
    CodeEngine_PackageAnalyzer: Utility for bidirectional Python <-> CodeEngine conversion
"""

__all__ = [
    "ExportExtension",
    "DomoCodeEngine_ConfigError",
    "DomoCodeEngine_Package",
    "DomoCodeEngine_Packages",
    "DomoCodeEngine_PackageVersion",
    "CodeEngine_PackageAnalyzer",
    # Re-export route exceptions
    "CodeEngine_GET_Error",
    "CodeEngine_CRUD_Error",
    "SearchCodeEngine_NotFound",
]

import builtins
import datetime as dt
import os
from dataclasses import dataclass, field
from enum import Enum

import httpx

from ...auth import DomoAuth
from ...base.exceptions import ClassError
from ...client.entities import DomoEntity, DomoManager, DomoSubEntity
from ...routes import codeengine as codeengine_routes
from ...routes.codeengine.exceptions import (
    CodeEngine_CRUD_Error,
    CodeEngine_GET_Error,
    SearchCodeEngine_NotFound,
)
from ...utils import files as dmuf
from ...utils.convert import convert_string_to_datetime
from .. import DomoUser as dmdu
from .Manifest import CodeEngineManifest


class ExportExtension(Enum):
    """File extension types for CodeEngine exports."""

    JAVASCRIPT = "js"
    PYTHON = "py"


class DomoCodeEngine_ConfigError(ClassError):
    """Exception raised when CodeEngine configuration is invalid."""

    def __init__(
        self,
        cls_instance=None,
        package_id: str | None = None,
        version: str | None = None,
        message: str | None = None,
        domo_instance: str | None = None,
    ):
        full_message = f"version {version} | {message}" if version else message
        super().__init__(
            cls_instance=cls_instance,
            entity_id=package_id,
            message=full_message,
            domo_instance=domo_instance,
        )


@dataclass
class DomoCodeEngine_PackageVersion(DomoSubEntity):
    """CodeEngine Package Version subentity.

    Represents a specific version of a CodeEngine package with its code,
    configuration, and function definitions.

    Attributes:
        auth: Authentication object
        package_id: ID of the parent package
        version: Version string (e.g., "1.0.0")
        language: Programming language
        description: Version description
        createdby_id: ID of user who created this version
        released_dt: Release datetime
        configuration: Version configuration dict
        code: Source code string
        functions: Function definitions dict
        Manifest: CodeEngineManifest for Python packages
        createdby: DomoUser who created this version
        accounts_mapping: Account mapping configuration
        ml_model: ML model configuration
    """

    auth: DomoAuth = field(repr=False)
    package_id: str
    version: str

    language: str | None = None
    description: str | None = None
    createdby_id: int | None = None
    released_dt: dt.datetime | None = None
    configuration: dict | None = None

    createdby: dmdu.DomoUser | None = None
    accounts_mapping: list[int] | None = None
    ml_model: list[str] | None = None

    code: str | None = field(repr=False, default=None)
    functions: dict | None = None

    Manifest: CodeEngineManifest | None = field(default=None)

    createdby: dmdu.DomoUser | None = None
    accounts_mapping: list[int] | None = None
    ml_model: list[str] | None = None

    code: str = field(repr=False, default=None)
    # functions_ls: list[CodeEngineManifest_Function] = field(repr=False, default=None)
    functions: dict = None

    Manifest: CodeEngineManifest = field(default=None)

    def _set_configuration(self, configuration=None):
        if configuration:
            self.configuration = configuration

        if not self.configuration:
            raise DomoCodeEngine_ConfigError(
                cls_instance=self,
                package_id=self.package_id,
                version=self.version,
                message="unable to set configuration",
            )

        self.accounts_mapping = self.configuration.get("accountsMapping", [])
        self.ml_model = self.configuration.get("mlModel", [])

        return self

    # def set_functions(
    #     self,
    #     code: str = None,
    #     functions: list[dict] = None,
    #     language: str = None,
    #     # function_parser_fn: Callable = None,  # must receive code string, function_ls, language
    # ):
    #     self.code = code or self.code

    #     self.functions_ls = functions or self.functions_ls

    #     self.language = language or self.language

    #     if not self.code or not self.configuration or not self.language:
    #         raise DomoCodeEngine_ConfigError(
    #             cls_instance=self,
    #             package_id=self.package_id,
    #             version=self.version,
    #             message="API did not return code, configuration or language -- unable to set functions",
    #         )
    # try:
    # function_parser_fn = function_parser_fn or extract_functions

    # functions_ls = function_parser_fn(
    #     code=self.code,
    #     function_ls=self.functions_ls,
    #     language=self.language
    # )

    # self.functions = [
    #     DomoCodeEngine_Function.from_dict(
    #         obj,
    #         is_private= obj.pop("is_private", False),
    #         language=self.language,
    #         package_id=self.package_id,
    #         version=self.version,
    #         code_raw=self.code,
    #     )
    #     for obj in functions_ls
    # ]
    # return functions

    # except Exception as e:
    #     print(e)
    #     raise DomoCodeEngine_ConfigError(
    #         package_id=self.package_id,
    #         version=self.version,
    #         message=e,
    #         domo_instance=self.auth.domo_instance,
    #     )

    @classmethod
    def from_dict(
        cls,
        auth: DomoAuth,
        obj: dict,
        package_id: str,
        language: str | None = None,
        is_supress_error: bool = True,
    ):
        """Create DomoCodeEngine_PackageVersion from API response.

        Args:
            auth: Authentication object
            obj: API response dictionary
            package_id: Parent package ID
            language: Programming language (optional, will use obj value if not provided)
            is_supress_error: Whether to suppress configuration errors

        Returns:
            DomoCodeEngine_PackageVersion instance
        """
        language = (language or obj.get("language", "PYTHON")).upper()

        domo_version = cls(
            auth=auth,
            package_id=package_id,
            language=language,
            version=obj.get("version"),
            code=obj.get("code"),
            description=obj.get("description"),
            createdby_id=obj.get("createdBy"),
            released_dt=convert_string_to_datetime(obj.get("releasedOn")),
            configuration=obj.get("configuration"),
            Manifest=(
                CodeEngineManifest.from_api(obj=obj) if language == "PYTHON" else None
            ),
        )

        # Set configuration if available
        if domo_version.configuration:
            try:
                domo_version._set_configuration()
            except DomoCodeEngine_ConfigError:
                if not is_supress_error:
                    raise

        return domo_version

    @classmethod
    async def get_by_id_and_version(
        cls,
        auth: DomoAuth,
        package_id: str,
        version: str,
        language: str | None = None,
        params: dict | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        return_raw: bool = False,
        session: httpx.AsyncClient | None = None,
    ):
        """Retrieve a specific package version.

        Args:
            auth: Authentication object
            package_id: Package identifier
            version: Version string
            language: Programming language (optional)
            params: Optional query parameters
            debug_api: Enable API debugging
            debug_num_stacks_to_drop: Stack frames to drop in logging
            return_raw: If True, return raw API response
            session: Optional httpx session

        Returns:
            DomoCodeEngine_PackageVersion instance or ResponseGetData if return_raw=True

        Raises:
            CodeEngine_GET_Error: If version retrieval fails
        """
        params = params or {"parts": "functions,code"}

        res = await codeengine_routes.get_codeengine_package_by_id_and_version(
            auth=auth,
            package_id=package_id,
            version=version,
            params=params,
            debug_api=debug_api,
            session=session,
            parent_class=cls.__name__,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

        if return_raw:
            return res

        return cls.from_dict(
            auth=auth, obj=res.response, package_id=package_id, language=language
        )

    def __eq__(self, other):
        """Check equality based on package ID and version."""
        if not isinstance(other, DomoCodeEngine_PackageVersion):
            return False

        return self.version == other.version and self.package_id == other.package_id

    async def download_source_code(
        self,
        download_folder: str = "./EXPORT/codeengine",
        file_name: str | None = None,
        debug_api: bool = False,
        replace_folder: bool = False,
    ):
        """Download the source code for this version to a file.

        Args:
            download_folder: Folder to save the code
            file_name: Optional file name (auto-generated if not provided)
            debug_api: Enable API debugging
            replace_folder: Whether to replace existing folder

        Returns:
            Path to the downloaded file
        """
        if not self.code:
            # Fetch code if not already loaded
            version_with_code = await self.get_by_id_and_version(
                auth=self.auth,
                package_id=self.package_id,
                version=self.version,
                debug_api=debug_api,
                params={"parts": "code"},
            )
            self.code = version_with_code.code

        extension = ".txt"
        if self.language == "PYTHON":
            extension = ".py"
        elif self.language == "JAVASCRIPT":
            extension = ".js"

        file_name = (
            file_name or f"{self.package_id}/{self.version}/functions{extension}"
        )

        file_path = os.path.join(download_folder, file_name)

        if self.Manifest:
            return self.Manifest.download_source_code(
                export_folder=os.path.join(download_folder, file_path),
                replace_folder=replace_folder,
            )

        dmuf.upsert_file(file_path, content=self.code, replace_folder=replace_folder)
        return file_path

    def export(
        self,
        file_name: str | None = None,
        output_folder: str = "EXPORT/code_engine/",
        debug_prn: bool = False,
    ):
        """Export the source code to a file.

        Args:
            file_name: Optional file name (defaults to package_id)
            output_folder: Output folder path
            debug_prn: Enable debug printing

        Returns:
            Path to the exported file
        """
        output_folder = (
            f"{output_folder}/" if not output_folder.endswith("/") else output_folder
        )

        dmuf.upsert_folder(output_folder)

        file_name = file_name or self.package_id
        file_name = dmuf.change_extension(
            file_name, ExportExtension[self.language].value
        )

        file_path = os.path.join(output_folder, file_name)

        if debug_prn:
            print(output_folder, file_name)

        with builtins.open(file_path, "w+", newline="\n", encoding="utf-8") as f:
            f.write(self.code)

        return file_path


@dataclass
class DomoCodeEngine_Package(DomoEntity):
    """Domo CodeEngine Package entity.

    Represents a CodeEngine package with versions and associated metadata.
    Packages contain executable code functions that can be deployed in Domo.

    Attributes:
        id: Unique package identifier
        auth: Authentication object
        raw: Raw API response data
        name: Package display name
        description: Package description
        language: Programming language (PYTHON or JAVASCRIPT)
        environment: Execution environment
        availability: Package availability status
        owner_id: ID of the package owner
        created: Package creation datetime
        last_modified: Last modification datetime
        functions: List of function definitions
        current_version: Latest version number
        versions: List of DomoCodeEngine_PackageVersion instances
        owner: DomoUser instance of the package owner
    """

    # Required DomoEntity attributes
    id: str
    name: str
    description: str
    language: str
    environment: str
    availability: str
    owner_id: int
    created: dt.datetime
    last_modified: dt.datetime
    functions: list

    current_version: str = None
    versions: list[DomoCodeEngine_PackageVersion] = None
    owner: list[dmdu.DomoUser] = None

    def __post_init__(self):
        """Initialize package and set current version."""
        self.id = str(self.id)
        self._set_current_version()

    def _set_current_version(self):
        """Determine and set the current (latest) version of the package."""
        if not self.versions:
            return

        versions = [version.version for version in self.versions]
        self.current_version = max(versions) if versions else None

    @classmethod
    def from_dict(cls, auth: DomoAuth, obj: dict):
        """Create DomoCodeEngine_Package from API response dictionary.

        Args:
            auth: Authentication object
            obj: API response dictionary

        Returns:
            DomoCodeEngine_Package instance
        """
        package_id = str(obj.get("id"))
        language = obj.get("language")

        # Parse versions if present
        versions = []
        if obj.get("versions"):
            versions = [
                DomoCodeEngine_PackageVersion.from_dict(
                    auth=auth,
                    obj=version,
                    package_id=package_id,
                    language=language,
                )
                for version in obj.get("versions", [])
            ]

        return cls(
            auth=auth,
            id=package_id,
            name=obj.get("name"),
            description=obj.get("description"),
            language=language,
            environment=obj.get("environment"),
            availability=obj.get("availability"),
            owner_id=obj.get("owner"),
            versions=versions,
            created=convert_string_to_datetime(obj.get("createdOn")),
            last_modified=convert_string_to_datetime(obj.get("updatedOn")),
            functions=obj.get("functions", []),
            raw=obj,
        )

    @classmethod
    async def get_by_id(
        cls,
        auth: DomoAuth,
        package_id: str,
        params: dict | None = None,
        return_raw: bool = False,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        session: httpx.AsyncClient | None = None,
    ):
        """Retrieve a CodeEngine package by ID.

        Args:
            auth: Authentication object
            package_id: Package identifier
            params: Optional query parameters
            return_raw: If True, return raw API response
            debug_api: Enable API debugging
            debug_num_stacks_to_drop: Stack frames to drop in logging
            session: Optional httpx session

        Returns:
            DomoCodeEngine_Package instance or ResponseGetData if return_raw=True

        Raises:
            CodeEngine_GET_Error: If package retrieval fails
        """
        res = await codeengine_routes.get_codeengine_package_by_id(
            auth=auth,
            package_id=package_id,
            params=params,
            debug_api=debug_api,
            session=session,
            parent_class=cls.__name__,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

        if return_raw:
            return res

        return cls.from_dict(auth=auth, obj=res.response)

    def __eq__(self, other):
        """Check equality based on package ID."""
        if not isinstance(other, DomoCodeEngine_Package):
            return False
        return self.id == other.id

    async def get_current_version(
        self,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        session: httpx.AsyncClient | None = None,
    ) -> "DomoCodeEngine_PackageVersion":
        """Get the current (latest) version of this package.

        Args:
            debug_api: Enable API debugging
            debug_num_stacks_to_drop: Stack frames to drop in logging
            session: Optional httpx session

        Returns:
            DomoCodeEngine_PackageVersion instance

        Raises:
            DomoCodeEngine_ConfigError: If no current version found
        """
        if not self.current_version:
            raise DomoCodeEngine_ConfigError(
                package_id=self.id,
                version=None,
                message="No current version found for the package",
                domo_instance=self.auth.domo_instance,
            )

        domo_version = await DomoCodeEngine_PackageVersion.get_by_id_and_version(
            auth=self.auth,
            package_id=self.id,
            version=self.current_version,
            language=self.language,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            session=session,
        )

        return domo_version

    async def get_owner(
        self,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        session: httpx.AsyncClient | None = None,
    ) -> dmdu.DomoUser | None:
        """Get the owner (user) of this package.

        Args:
            debug_api: Enable API debugging
            debug_num_stacks_to_drop: Stack frames to drop in logging
            session: Optional httpx session

        Returns:
            DomoUser instance or None if owner_id not set
        """
        if not self.owner_id:
            return None

        self.owner = await dmdu.DomoUser.get_by_id(
            auth=self.auth,
            user_id=str(self.owner_id),
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            session=session,
        )

        return self.owner


@dataclass
class DomoCodeEngine_Packages(DomoManager):
    """Manager class for CodeEngine package collections.

    Provides methods to retrieve, search, and manage multiple CodeEngine packages.

    Attributes:
        auth: Authentication object
    """

    auth: DomoAuth = field(repr=False)

    async def get(
        self,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        session: httpx.AsyncClient | None = None,
    ) -> list[DomoCodeEngine_Package]:
        """Get all CodeEngine packages.

        Args:
            debug_api: Enable API debugging
            debug_num_stacks_to_drop: Stack frames to drop in logging
            session: Optional httpx session

        Returns:
            List of DomoCodeEngine_Package instances

        Raises:
            CodeEngine_GET_Error: If package retrieval fails
        """
        res = await codeengine_routes.get_packages(
            auth=self.auth,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            session=session,
            parent_class=self.__class__.__name__,
        )

        return [
            DomoCodeEngine_Package.from_dict(auth=self.auth, obj=obj)
            for obj in res.response
        ]

    async def search_by_name(
        self,
        name: str,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        session: httpx.AsyncClient | None = None,
    ) -> list[DomoCodeEngine_Package]:
        """Search for packages by name.

        Args:
            name: Package name to search for (case-insensitive partial match)
            debug_api: Enable API debugging
            debug_num_stacks_to_drop: Stack frames to drop in logging
            session: Optional httpx session

        Returns:
            List of matching DomoCodeEngine_Package instances

        Raises:
            SearchCodeEngine_NotFound: If no packages match the search
        """
        all_packages = await self.get(
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            session=session,
        )

        matches = [
            pkg for pkg in all_packages if name.lower() in (pkg.name or "").lower()
        ]

        if not matches:
            raise SearchCodeEngine_NotFound(
                search_criteria=f"name contains '{name}'",
            )

        return matches


class CodeEngine_PackageAnalyzer:
    """Utility class for bidirectional Python <-> CodeEngine package conversion.

    This class provides tools to:
    - Parse Python files into CodeEngine-compatible format
    - Convert CodeEngine packages back to Python files
    - Validate package manifests
    - Deploy new versions from Python code

    Future Implementation:
        - from_python_file(): Parse .py file into CodeEngine manifest
        - to_python_file(): Export CodeEngine package as formatted .py
        - validate_manifest(): Validate package structure
        - deploy_version(): Deploy new version from Python file
    """

    def __init__(self, auth: DomoAuth):
        """Initialize the analyzer.

        Args:
            auth: Authentication object for API calls
        """
        self.auth = auth

    # TODO: Implement analyzer methods in Phase 3
    # See Manifest_Function.py for existing AST parsing logic to integrate
