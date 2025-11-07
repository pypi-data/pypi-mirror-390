__all__ = [
    "DomoAccount_Config",
    "AccountConfig_UsesOauthError",
    "DomoAccount_NoConfig_OAuthError",
    "AccountConfig_ProviderTypeNotDefinedError",
    "DomoAccount_NoConfig",
    "DomoAccount_Config_AbstractCredential",
    "DomoAccount_Config_DatasetCopy",
    "DomoAccount_Config_DomoAccessToken",
    "DomoAccount_Config_Governance",
    "DomoAccount_Config_AmazonS3",
    "DomoAccount_Config_AmazonS3Advanced",
    "DomoAccount_Config_AwsAthena",
    "DomoAccount_Config_HighBandwidthConnector",
    "DomoAccount_Config_Snowflake",
    "DomoAccount_Config_SnowflakeUnload_V2",
    "DomoAccount_Config_SnowflakeUnloadAdvancedPartition",
    "DomoAccount_Config_SnowflakeWriteback",
    "DomoAccount_Config_SnowflakeUnload",
    "DomoAccount_Config_SnowflakeFederated",
    "DomoAccount_Config_SnowflakeInternalUnload",
    "DomoAccount_Config_SnowflakeKeyPairAuthentication",
    "AccountConfig",
]

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ...base.base import DomoEnumMixin
from ...base.entities import DomoBase
from ...base.exceptions import ClassError
from ...utils import (
    DictDot as util_dd,
    convert as dmcv,
)


class AccountConfig_UsesOauthError(ClassError):
    def __init__(self, cls_instance, data_provider_type):
        super().__init__(
            cls_instance=cls_instance,
            message=f"data provider type {data_provider_type} uses OAuth and therefore wouldn't return a Config object",
        )


class AccountConfig_ProviderTypeNotDefinedError(ClassError):
    def __init__(self, cls_instance, data_provider_type):
        super().__init__(
            cls_instance=cls_instance,
            message=f"data provider type {data_provider_type} not defined yet. Extend the AccountConfig class",
        )


@dataclass
class DomoAccount_Config(DomoBase):
    """DomoAccount Config abstract base class"""

    data_provider_type: str
    is_oauth: bool

    allow_external_use: bool = True

    parent: Any = field(repr=False, default=None)  # DomoAccount
    raw: dict = field(repr=False, default=None)  # from api response

    @property
    def allow_external_use_from_raw(self):
        if not self.raw:
            return None

        allow_external_use = self.raw.get("allowExternalUse")

        if isinstance(allow_external_use, str):
            allow_external_use = dmcv.convert_string_to_bool(allow_external_use)

        return allow_external_use

    @classmethod
    def from_parent(cls, parent, **kwargs):
        return cls(parent=parent, **kwargs)

    @classmethod
    def from_dict(cls, obj: dict, parent: Any = None, **kwargs):
        """convert accounts API response into a class object"""
        cls(
            parent=parent,
            raw=obj,
            **kwargs,
        )

    def to_dict(
        self,
        obj=None,
        column_filter: list[str] = None,  # enumerate columns to include
        **kwargs,
    ) -> dict:
        s = {"allowExternalUse": self.allow_external_use, **(obj or {}), **kwargs}

        if column_filter:
            return {k: v for k, v in s.items() if k in column_filter}

        return s


@dataclass
class DomoAccount_NoConfig_OAuthError(DomoAccount_Config):
    is_oauth: bool = True

    def __super_init__(self):
        raise AccountConfig_UsesOauthError(
            cls_instance=self, data_provider_type=self.data_provider_type
        )


@dataclass
class DomoAccount_NoConfig(DomoAccount_Config):
    is_oauth: bool = False

    def __super_init__(self):
        raise AccountConfig_ProviderTypeNotDefinedError(
            cls_instance=self, data_provider_type=self.data_provider_type
        )


@dataclass
class DomoAccount_Config_AbstractCredential(DomoAccount_Config):
    credentials: dict = None
    data_provider_type: str = "abstract-credential-store"
    is_oauth: bool = False

    @classmethod
    def from_dict(cls, obj, parent=None, **kwargs):
        return cls.from_parent(
            parent=parent, raw=obj, **{"credentials": obj["credentials"], **kwargs}
        )


@dataclass
class DomoAccount_Config_DatasetCopy(DomoAccount_Config):
    data_provider_type = "dataset-copy"
    is_oauth: bool = False

    domo_instance: str = None
    access_token: str = field(repr=False, default=None)

    @classmethod
    def from_dict(cls, obj: dict, parent: Any = None, **kwargs):
        return cls(
            access_token=obj.get("accessToken"),
            domo_instance=obj.get("instance"),
            parent=parent,
            raw=obj,
            data_provider_type="dataset-copy",
        )

    def to_dict(self):
        return super().to_dict(
            {"accessToken": self.access_token, "instance": self.domo_instance}
        )


@dataclass
class DomoAccount_Config_DomoAccessToken(DomoAccount_Config):
    data_provider_type: str = "domo-access-token"
    is_oauth: bool = False

    domo_access_token: str = field(repr=False, default=None)
    username: str = None
    password: str = field(repr=False, default=None)

    @classmethod
    def from_dict(cls, obj: dict, parent: Any = None, **kwargs):
        return cls(
            domo_access_token=obj.get("domoAccessToken"),
            username=obj.get("username"),
            password=obj.get("password"),
            parent=parent,
            raw=obj,
            is_oauth=None,
        )

    def to_dict(self):
        return super().to_dict(
            {
                "domoAccessToken": self.domo_access_token or "",
                "username": self.username or "",
                "password": self.password or "",
            }
        )


@dataclass
class DomoAccount_Config_Governance(DomoAccount_Config):
    is_oauth: bool = False
    data_provider_type: str = "domo-governance-d14c2fef-49a8-4898-8ddd-f64998005600"

    domo_instance: str = None
    access_token: str = field(repr=False, default=None)

    @classmethod
    def from_dict(cls, obj: dict, parent: Any = None, **kwargs):
        return cls(
            access_token=obj.get("apikey"),
            domo_instance=obj.get("customer"),
            parent=parent,
            raw=obj,
        )

    def to_dict(self):
        return super().to_dict(
            {"apikey": self.access_token, "customer": self.domo_instance}
        )


@dataclass
class DomoAccount_Config_AmazonS3(DomoAccount_Config):
    data_provider_type: str = "amazon-s3"
    is_oauth: bool = False

    access_key: str = None
    secret_key: str = field(repr=False, default=None)
    bucket: str = None
    region: str = "us-west-2"

    @classmethod
    def from_dict(cls, obj: dict, parent: Any = None, **kwargs):
        dd = util_dd.DictDot(obj)

        return cls(
            access_key=dd.accessKey,
            secret_key=dd.secretKey,
            bucket=dd.bucket,
            region=dd.region,
            parent=parent,
            raw=obj,
        )

    def to_dict(self):
        bucket = self.bucket

        if bucket and bucket.lower().startswith("s3://"):
            bucket = bucket[5:]
            print(
                f"🤦‍♀️- Domo bucket expects string without s3:// prefix. Trimming to '{bucket}' for the output"
            )
        return super().to_dict(
            {
                "accessKey": self.access_key,
                "secretKey": self.secret_key,
                "bucket": bucket,
                "region": self.region,
            }
        )


@dataclass
class DomoAccount_Config_AmazonS3Advanced(DomoAccount_Config):
    data_provider_type: str = "amazons3-advanced"
    is_oauth: bool = False

    access_key: str = None
    secret_key: str = field(repr=False, default=None)

    bucket: str = None
    region: str = "us-west-2"

    @classmethod
    def from_dict(cls, obj: dict = None, parent: Any = None, **kwargs):
        dd = util_dd.DictDot(obj)

        return cls(
            access_key=dd.accessKey,
            secret_key=dd.secretKey,
            bucket=dd.bucket,
            region=dd.region,
            parent=parent,
        )

    def to_dict(self):
        bucket = self.bucket

        if bucket and bucket.lower().startswith("s3://"):
            bucket = bucket[5:]
            print(
                f"🤦‍♀️- Domo bucket expects string without s3:// prefix. Trimming to '{bucket}' for the output"
            )
        return super().to_dict(
            {
                "accessKey": self.access_key,
                "secretKey": self.secret_key,
                "bucket": bucket,
                "region": self.region,
            }
        )


@dataclass
class DomoAccount_Config_AwsAthena(DomoAccount_Config):
    data_provider_type: str = "aws-athena"
    is_oauth: bool = False

    access_key: str = None
    secret_key: str = field(repr=False, default=None)
    bucket: str = None
    workgroup: str = None

    region: str = "us-west-2"

    @classmethod
    def from_dict(cls, obj: dict, parent: Any = None, **kwargs):
        dd = util_dd.DictDot(obj)

        return cls(
            access_key=dd.awsAccessKey,
            secret_key=dd.awsSecretKey,
            bucket=dd.s3StagingDir,
            region=dd.region,
            workgroup=dd.workgroup,
            parent=parent,
            raw=obj,
        )

    def to_dict(self):
        return super().to_dict(
            {
                "awsAccessKey": self.access_key,
                "awsSecretKey": self.secret_key,
                "s3StagingDir": self.bucket,
                "region": self.region,
                "workgroup": self.workgroup,
            }
        )


@dataclass
class DomoAccount_Config_HighBandwidthConnector(DomoAccount_Config):
    """this connector is not enabled by default contact your CSM / AE"""

    data_provider_type: str = "amazon-athena-high-bandwidth"
    is_oauth: bool = False

    access_key: str = None
    secret_key: str = field(repr=False, default=None)
    bucket: str = None

    region: str = "us-west-2"
    workgroup: str = None

    @classmethod
    def from_dict(cls, obj: dict, parent: Any = None, **kwargs):
        return cls(
            access_key=obj["awsAccessKey"],
            secret_key=obj["awsSecretKey"],
            bucket=obj["s3StagingDir"],
            region=obj["region"],
            data_provider_type="amazon-athena-high-bandwidth",
            workgroup=obj.get("workgroup"),
            parent=parent,
            raw=obj,
        )

    def to_dict(self):
        return super().to_dict(
            {
                "awsAccessKey": self.access_key,
                "awsSecretKey": self.secret_key,
                "s3StagingDir": self.bucket,
                "region": self.region,
                "workgroup": self.workgroup,
            }
        )


@dataclass
class DomoAccount_Config_Snowflake(DomoAccount_Config):
    """this connector is not enabled by default contact your CSM / AE"""

    data_provider_type: str = "snowflake"
    is_oauth: bool = False

    account: str = None
    username: str = None
    password: str = field(repr=False, default=None)
    role: str = None

    @classmethod
    def from_dict(cls, obj: dict, parent: Any = None, **kwargs):
        dd = util_dd.DictDot(obj)

        return cls(
            account=dd.account,
            username=dd.username,
            password=dd.password,
            role=dd.role,
            raw=obj,
            parent=parent,
        )

    def to_dict(self):
        return super().to_dict(
            {
                "account": self.account,
                "username": self.username,
                "password": self.password,
                "role": self.role,
            }
        )


@dataclass
class DomoAccount_Config_SnowflakeUnload_V2(DomoAccount_Config):
    """this connector is not enabled by default contact your CSM / AE"""

    data_provider_type: str = "snowflake-unload-v2"
    is_oauth: bool = False

    account: str = None
    username: str = None
    password: str = field(repr=False, default=None)

    access_key: str = None
    secret_key: str = field(repr=False, default=None)
    region: str = None
    bucket: str = None

    role: str = None

    @classmethod
    def from_dict(cls, obj: dict, parent: Any = None, **kwargs):
        dd = util_dd.DictDot(obj)

        return cls(
            account=dd.account,
            username=dd.username,
            password=dd.password,
            access_key=dd.accessKey,
            secret_key=dd.secretKey,
            bucket=dd.bucket,
            region=dd.region,
            role=dd.role,
            raw=obj,
            parent=parent,
        )

    def to_dict(self):
        return super().to_dict(
            {
                "account": self.account,
                "username": self.username,
                "password": self.password,
                "role": self.role,
                "accessKey": self.access_key,
                "secretKey": self.secret_key,
                "bucket": self.bucket,
                "region": self.region,
            }
        )


@dataclass
class DomoAccount_Config_SnowflakeUnloadAdvancedPartition(DomoAccount_Config):
    data_provider_type: str = "snowflake-internal-unload-advanced-partition"
    is_oauth: bool = False

    password: str = field(repr=False, default=None)
    account: str = None
    username: str = None
    role: str = None

    @classmethod
    def from_dict(cls, obj: dict, parent: Any = None, **kwargs):
        return cls(
            password=obj["password"],
            role=obj.get("role"),
            account=obj["account"],
            username=obj["username"],
            raw=obj,
            parent=parent,
        )

    def to_dict(self):
        return super().to_dict(
            {
                "password": self.password,
                "role": self.role,
                "account": self.account,
                "username": self.username,
            }
        )


@dataclass
class DomoAccount_Config_SnowflakeWriteback(DomoAccount_Config):
    data_provider_type: str = "snowflake-writeback"
    is_oauth: bool = False

    domo_client_secret: str = field(repr=False, default=None)
    domo_client_id: str = None
    account: str = None
    password: str = field(repr=False, default=None)
    username: str = None

    @classmethod
    def from_dict(cls, obj: dict, parent: Any = None, **kwargs):
        return cls(
            domo_client_secret=obj["domoClientSecret"],
            domo_client_id=obj["domoClientId"],
            account=obj["account"],
            username=obj["username"],
            password=obj["password"],
            raw=obj,
            parent=parent,
        )

    def to_dict(self):
        return super().to_dict(
            {
                "domoClientSecret": self.domo_client_secret,
                "password": self.password,
                "domoClientId": self.domo_client_id,
                "account": self.account,
                "username": self.username,
            }
        )


@dataclass
class DomoAccount_Config_SnowflakeUnload(DomoAccount_Config):
    data_provider_type: str = "snowflake-unload"
    is_oauth: bool = False

    secret_key: str = field(repr=False, default=None)
    access_key: str = None
    account: str = None
    password: str = field(repr=False, default=None)
    username: str = None
    bucket: str = None

    @classmethod
    def from_dict(cls, obj: dict, parent: Any = None, **kwargs):
        return cls(
            secret_key=obj["secretKey"],
            access_key=obj["accessKey"],
            account=obj["account"],
            username=obj["username"],
            password=obj["password"],
            bucket=obj["bucket"],
            raw=obj,
            parent=parent,
        )

    def to_dict(self):
        return super().to_dict(
            {
                "bucket": self.bucket,
                "password": self.password,
                "secretKey": self.secret_key,
                "accessKey": self.access_key,
                "account": self.account,
                "username": self.username,
            }
        )


@dataclass
class DomoAccount_Config_SnowflakeFederated(DomoAccount_Config):
    data_provider_type: str = "snowflake-federated"
    is_oauth: bool = False
    password: str = field(repr=False, default=None)

    host: str = None
    warehouse: str = None
    username: str = None
    port: str = None
    role: str = None

    @classmethod
    def from_dict(cls, obj: dict, parent: Any = None, **kwargs):
        return cls(
            password=obj["password"],
            host=obj["host"],
            warehouse=obj["warehouse"],
            username=obj["user"],
            role=obj.get("role"),
            port=obj.get("port"),
            raw=obj,
            parent=parent,
        )

    def to_dict(self):
        return super().to_dict(
            {
                "password": self.password,
                "port": self.port,
                "host": self.host,
                "warehouse": self.warehouse,
                "user": self.username,
                "role": self.role,
            }
        )


@dataclass
class DomoAccount_Config_SnowflakeInternalUnload(DomoAccount_Config):
    is_oauth: bool = False
    data_provider_type: str = "snowflake-internal-unload"

    password: str = field(repr=False, default=None)
    account: str = None
    username: str = None
    role: str = None

    @classmethod
    def from_dict(cls, obj: dict, parent: Any = None, **kwargs):
        return cls(
            password=obj["password"],
            role=obj.get("role"),
            account=obj["account"],
            username=obj["username"],
            parent=parent,
            raw=obj,
        )

    def to_dict(self):
        return super().to_dict(
            {
                "password": self.password,
                "role": self.role,
                "account": self.account,
                "username": self.username,
            }
        )


@dataclass
class DomoAccount_Config_SnowflakeKeyPairAuthentication(DomoAccount_Config):
    data_provider_type: str = "snowflakekeypairauthentication"
    is_oauth: bool = False

    private_key: str = field(repr=False, default=None)
    account: str = field(repr=False, default=None)
    passphrase: str = field(repr=False, default=None)
    username: str = None
    role: str = None

    @classmethod
    def from_dict(cls, obj: dict, parent: Any = None, **kwargs):
        return cls(
            private_key=obj["privateKey"],
            role=obj.get("role"),
            account=obj["account"],
            username=obj["username"],
            passphrase=obj["passPhrase"],
            parent=parent,
            raw=obj,
        )

    def to_dict(self):
        return super().to_dict(
            {
                "privateKey": self.private_key,
                "role": self.role,
                "account": self.account,
                "username": self.username,
                "passPhrase": self.passphrase,
            }
        )


class AccountConfig(DomoEnumMixin, Enum):
    """
    Enum provides appropriate spelling for data_provider_type and config object.
    The name of the enum should correspond with the data_provider_type with hyphens replaced with underscores.
    """

    abstract_credential_store = DomoAccount_Config_AbstractCredential
    dataset_copy = DomoAccount_Config_DatasetCopy
    domo_access_token = DomoAccount_Config_DomoAccessToken
    domo_governance_d14c2fef_49a8_4898_8ddd_f64998005600 = DomoAccount_Config_Governance
    aws_athena = DomoAccount_Config_AwsAthena
    amazon_athena_high_bandwidth = DomoAccount_Config_HighBandwidthConnector
    amazon_s3 = DomoAccount_Config_AmazonS3
    amazons3_advanced = DomoAccount_Config_AmazonS3Advanced

    snowflake = DomoAccount_Config_Snowflake

    snowflake_unload = DomoAccount_Config_SnowflakeUnload
    snowflake_unload_v2 = DomoAccount_Config_SnowflakeUnload_V2

    snowflake_internal_unload_advanced_partition = (
        DomoAccount_Config_SnowflakeUnloadAdvancedPartition
    )

    snowflake_internal_unload = DomoAccount_Config_SnowflakeInternalUnload

    snowflakekeypairauthentication = DomoAccount_Config_SnowflakeKeyPairAuthentication

    snowflake_writeback = DomoAccount_Config_SnowflakeWriteback
    snowflake_federated = DomoAccount_Config_SnowflakeFederated

    _uses_oauth = ["google_spreadsheets"]

    _config_oauth = DomoAccount_NoConfig_OAuthError
    _config_notdefined = DomoAccount_NoConfig

    @staticmethod
    def generate_alt_search_str(raw_value):
        return raw_value.lower().replace("-", "_")

    @classmethod
    def _missing_(cls, value):
        try:
            alt_search_str = cls.generate_alt_search_str(value)

            config_match = next(
                (member for member in cls if member.name in [value, alt_search_str]),
                None,
            )

            # best case scenario alt_search yields a result
            if config_match:
                return config_match

            # second best case, display_type is an oauth and therefore has no matching config
            oauth_match = next(
                (
                    oauth_str
                    for oauth_str in cls._uses_oauth
                    if oauth_str in [value, alt_search_str]
                ),
                None,
            )
            if oauth_match:
                raise AccountConfig_UsesOauthError(value)

            # worst case, unencountered display_type
            raise AccountConfig_ProviderTypeNotDefinedError(value)
        except AccountConfig_UsesOauthError as e:
            print(e)
            return cls._config_oauth
        except AccountConfig_ProviderTypeNotDefinedError as e:
            print(e)
            return cls._config_notdefined
