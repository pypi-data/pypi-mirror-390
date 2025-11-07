from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

from sqlglot import exp, parse_one

from domolibrary2.base.base import DomoBase

from ...base.base import DomoEnumMixin
from ...routes.stream import Stream_CRUD_Error, Stream_GET_Error

__all__ = [
    "StreamConfig_Mapping_snowflake",
    "StreamConfig_Mapping_snowflake_federated",
    "StreamConfig_Mapping_snowflake_internal_unload",
    "StreamConfig_Mapping_snowflakekeypairauthentication",
    "StreamConfig_Mapping_snowflake_keypair_internal_managed_unload",
    "StreamConfig_Mapping_snowflake_unload_v2",
    "StreamConfig_Mapping_snowflake_writeback",
    "StreamConfig_Mapping_aws_athena",
    "StreamConfig_Mapping_amazon_athena_high_bandwidth",
    "StreamConfig_Mapping_amazon_s3_assumerole",
    "StreamConfig_Mapping_adobe_analytics_v2",
    "StreamConfig_Mapping_dataset_copy",
    "StreamConfig_Mapping_default",
    "StreamConfig_Mapping_domo_csv",
    "StreamConfig_Mapping_google_sheets",
    "StreamConfig_Mapping_google_spreadsheets",
    "StreamConfig_Mapping_postgresql",
    "StreamConfig_Mapping_qualtrics",
    "StreamConfig_Mapping_sharepointonline",
    "StreamConfig_Mapping",
    "StreamConfig_Mappings",
    "StreamConfig",
    # Route exceptions
    "Stream_GET_Error",
    "Stream_CRUD_Error",
]


@dataclass
class StreamConfig_Mapping(DomoBase):
    data_provider_type: str

    sql: str = None
    warehouse: str = None
    database_name: str = None
    s3_bucket_category: str = None

    is_default: bool = False

    table_name: str = None
    src_url: str = None
    google_sheets_file_name: str = None
    adobe_report_suite_id: str = None
    qualtrics_survey_id: str = None

    def search_keys_by_value(
        self,
        value_to_search: str,
    ) -> StreamConfig_Mapping | None:
        if self.is_default:
            if value_to_search in ["enteredCustomQuery", "query", "customQuery"]:
                return "sql"

        return next(
            (key for key, value in asdict(self).items() if value == value_to_search),
            None,
        )


StreamConfig_Mapping_snowflake = StreamConfig_Mapping(
    data_provider_type="snowflake",
    sql="query",
    warehouse="warehouseName",
    database_name="databaseName",
    s3_bucket_category=None,
)
StreamConfig_Mapping_snowflake_federated = StreamConfig_Mapping(
    data_provider_type="snowflake_federated", sql=None
)


StreamConfig_Mapping_snowflake_internal_unload = StreamConfig_Mapping(
    data_provider_type="snowflake-internal-unload",
    sql="customQuery",
    database_name="databaseName",
    warehouse="warehouseName",
)

StreamConfig_Mapping_snowflakekeypairauthentication = StreamConfig_Mapping(
    data_provider_type="snowflakekeypairauthentication",
    sql="query",
    database_name="databaseName",
    warehouse="warehouseName",
)

StreamConfig_Mapping_snowflake_keypair_internal_managed_unload = StreamConfig_Mapping(
    data_provider_type="snowflake-keypair-internal-managed-unload",
    sql="customQuery",
    database_name="databaseName",
    warehouse="warehouseName",
)

StreamConfig_Mapping_snowflake_unload_v2 = StreamConfig_Mapping(
    data_provider_type="snowflake_unload_v2",
    sql="query",
    warehouse="warehouseName",
    database_name="databaseName",
)

StreamConfig_Mapping_snowflake_writeback = StreamConfig_Mapping(
    data_provider_type="snowflake-writeback",
    table_name="enterTableName",
    database_name="databaseName",
    warehouse="warehouseName",
)

StreamConfig_Mapping_aws_athena = StreamConfig_Mapping(
    data_provider_type="aws-athena",
    sql="query",
    database_name="databaseName",
    table_name="tableName",
)

StreamConfig_Mapping_amazon_athena_high_bandwidth = StreamConfig_Mapping(
    data_provider_type="amazon-athena-high-bandwidth",
    sql="enteredCustomQuery",
    database_name="databaseName",
)


StreamConfig_Mapping_amazon_s3_assumerole = StreamConfig_Mapping(
    data_provider_type="amazon_s3_assumerole", s3_bucket_category="filesDiscovery"
)

StreamConfig_Mapping_adobe_analytics_v2 = StreamConfig_Mapping(
    data_provider_type="adobe-analytics-v2",
    sql="query",
    adobe_report_suite_id="report_suite_id",
)


StreamConfig_Mapping_dataset_copy = StreamConfig_Mapping(
    data_provider_type="dataset-copy", src_url="datasourceUrl"
)

StreamConfig_Mapping_default = StreamConfig_Mapping(
    data_provider_type="default", is_default=True
)

StreamConfig_Mapping_domo_csv = StreamConfig_Mapping(
    data_provider_type="domo-csv", src_url="datasourceUrl"
)

StreamConfig_Mapping_google_sheets = StreamConfig_Mapping(
    data_provider_type="google-sheets", google_sheets_file_name="spreadsheetIDFileName"
)

StreamConfig_Mapping_google_spreadsheets = StreamConfig_Mapping(
    data_provider_type="google-spreadsheets",
    google_sheets_file_name="spreadsheetIDFileName",
)

StreamConfig_Mapping_postgresql = StreamConfig_Mapping(
    data_provider_type="postgresql",
    sql="query",
)

StreamConfig_Mapping_qualtrics = StreamConfig_Mapping(
    data_provider_type="qualtrics",
    qualtrics_survey_id="survey_id",
)

StreamConfig_Mapping_sharepointonline = StreamConfig_Mapping(
    data_provider_type="sharepointonline",
    src_url="relativeURL",
)


class StreamConfig_Mappings(DomoEnumMixin, Enum):
    snowflake = StreamConfig_Mapping_snowflake
    snowflake_federated = StreamConfig_Mapping_snowflake_federated
    snowflake_internal_unload = StreamConfig_Mapping_snowflake_internal_unload
    snowflakekeypairauthentication = StreamConfig_Mapping_snowflakekeypairauthentication
    snowflake_keypair_internal_managed_unload = (
        StreamConfig_Mapping_snowflake_keypair_internal_managed_unload
    )
    snowflake_unload_v2 = StreamConfig_Mapping_snowflake_unload_v2
    snowflake_writeback = StreamConfig_Mapping_snowflake_writeback
    amazon_athena_high_bandwidth = StreamConfig_Mapping_amazon_athena_high_bandwidth
    amazon_s3_assumerole = StreamConfig_Mapping_amazon_s3_assumerole
    adobe_analytics_v2 = StreamConfig_Mapping_adobe_analytics_v2
    aws_athena = StreamConfig_Mapping_aws_athena
    dataset_copy = StreamConfig_Mapping_dataset_copy
    domo_csv = StreamConfig_Mapping_domo_csv
    google_sheets = StreamConfig_Mapping_google_sheets
    google_spreadsheets = StreamConfig_Mapping_google_spreadsheets
    postgresql = StreamConfig_Mapping_postgresql
    qualtrics = StreamConfig_Mapping_qualtrics
    sharepointonline = StreamConfig_Mapping_sharepointonline

    default = StreamConfig_Mapping_default

    @classmethod
    def _missing_(cls, value):
        alt_search = value.lower().replace("-", "_")

        return next(
            (member for member in cls if member.name.lower() == alt_search),
            cls.default,
        )

    @classmethod
    def search(cls, value, debug_api: bool = False) -> StreamConfig_Mappings | None:
        alt_search = value.lower().replace("-", "_")

        try:
            return cls[alt_search]

        except KeyError:
            if debug_api:
                print(f"{value} has not been added to enum config, must implement")
            return cls.default


@dataclass
class StreamConfig:
    stream_category: str
    name: str
    type: str
    value: str
    value_clean: str = None
    parent: Any = field(repr=False, default=None)

    def __post_init__(self):
        # self.value_clean = self.value.replace("\n", " ")
        # sc.value_clean = re.sub(" +", " ", sc.value_clean)

        if self.stream_category == "sql" and self.parent:
            self.process_sql()

    def process_sql(self):
        if not self.parent:
            return None

        self.parent.configuration_query = self.value

        try:
            for table in parse_one(self.value).find_all(exp.Table):
                self.parent.configuration_tables.append(table.name.lower())
                self.parent.configuration_tables = sorted(
                    list(set(self.parent.configuration_tables))
                )
        except Exception:
            return None

        return self.parent.configuration_tables

    @classmethod
    def from_json(cls, obj: dict, data_provider_type: str, parent_stream: Any = None):
        config_name = obj["name"]

        mapping_enum = StreamConfig_Mappings.search(data_provider_type)

        stream_category = "default"
        if mapping_enum:
            stream_category = mapping_enum.value.search_keys_by_value(config_name)

            if parent_stream:
                parent_stream.has_mapping = True

        return cls(
            stream_category=stream_category,
            name=config_name,
            type=obj["type"],
            value=obj["value"],
            parent=parent_stream,
        )

    def to_dict(self):
        return {"field": self.stream_category, "key": self.name, "value": self.value}
