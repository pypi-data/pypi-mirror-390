# All code comments in English as requested
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict, conint

from nemo_library_etl.adapter.migman.enums import (
    MigManExtractAdapter,
    MigManLoadAdapter,
)

##############################################################
# Shared strict base: forbid unknown fields everywhere
##############################################################


class StrictBaseModel(BaseModel):
    # Forbid extra keys globally for all derived models.
    model_config = ConfigDict(
        extra="forbid",  # disallow unknown/extra fields
        str_strip_whitespace=True,  # (optional) trim strings
        populate_by_name=True,  # allow population by field name/alias
    )


##############################################################
# Extract
##############################################################


class ExtractGenericOdbcConfig(StrictBaseModel):
    """ODBC-based extraction from a generic ODBC source."""

    odbc_connstr: str = Field(..., description="ODBC connection string for SQL Server")
    chunk_size: conint(gt=0) = 10_000
    timeout: conint(gt=0) = 300
    table_prefix: str = ""
    table_selector: Literal["all", "join_parser"] = "all"
    tables: List[str]


class ExtractInforcomConfig(StrictBaseModel):
    """ODBC-based extraction from INFORCOM (INFOR.* tables)."""

    odbc_connstr: str = Field(..., description="ODBC connection string for SQL Server")
    chunk_size: conint(gt=0) = 10_000
    timeout: conint(gt=0) = 300
    table_prefix: str = "INFOR."
    table_selector: Literal["all", "join_parser"] = "all"
    tables: List[str]


class ExtractSAPECCConfig(StrictBaseModel):
    """ODBC-based extraction from SAP ECC (SAP.* tables)."""

    address: str = Field(..., description="Host address of the SAP HANA server")
    port: conint(gt=0, lt=65536) = 30015
    user: str = Field(..., description="Username for SAP HANA connection")
    password: str = Field(..., description="Password for SAP HANA connection")
    autocommit: bool = True  # Only read access → autocommit enabled
    chunk_size: conint(gt=0) = 10_000
    table_selector: Literal["all", "join_parser"] = "all"
    tables: List[str]


class ExtractProAlphaConfig(StrictBaseModel):
    """ODBC-based extraction from PROALPHA (PROALPHA.* tables)."""

    odbc_connstr: str = Field(..., description="ODBC connection string for SQL Server")
    chunk_size: conint(gt=0) = 10_000
    timeout: conint(gt=0) = 300
    table_prefix: str = "PUB."
    table_selector: Literal["all", "join_parser"] = "all"
    tables: List[str]


class ExtractSageKHKConfig(StrictBaseModel):
    """ODBC-based extraction from SAGEKHK (SAGEKHK.* tables)."""

    odbc_connstr: str = Field(..., description="ODBC connection string for SQL Server")
    chunk_size: conint(gt=0) = 10_000
    timeout: conint(gt=0) = 300
    table_prefix: str = ""
    table_selector: Literal["all", "join_parser"] = "all"
    tables: List[str]


class ExtractFileConfig(StrictBaseModel):
    active: bool = True
    project: str
    file_path: str
    separator: Literal[";", ",", "\t", "|", ":", " "] = ";"
    quote: str = '"'
    dateformat: str = "%d-%m-%Y"
    encoding: Literal["utf-8", "utf-16", "latin-1", "CP1252"] = "utf-8"
    header: bool = True
    columns: List[str] = Field(
        default_factory=list, description="List of column names in the file"
    )
    all_varchar: bool = Field(
        default=True,
        description="Import all columns as VARCHAR to avoid conversion errors",
    )


class MigManExtractConfig(StrictBaseModel):
    active: bool = True
    load_to_nemo: bool = True
    delete_temp_files: bool = True
    nemo_project_prefix: str = "mme"
    extract_method: Literal["database", "file"] = "database"
    extract_from_folder: Optional[str] = None
    genericodbc: ExtractGenericOdbcConfig
    inforcom: ExtractInforcomConfig
    sapecc: ExtractSAPECCConfig
    proalpha: ExtractProAlphaConfig
    sagekhk: ExtractSageKHKConfig
    file: list[ExtractFileConfig]


##############################################################
# Transform
##############################################################


class TransformJoinConfig(StrictBaseModel):
    active: bool = True
    limit: int | None = None


class TransformMappingSynonymConfig(StrictBaseModel):
    active: bool = True
    source_field: str
    synonym_fields: List[str] = Field(
        default_factory=list, description="List of synonym field names"
    )


class TransformMappingConfig(StrictBaseModel):
    active: bool = True
    field_name: str


class TransformMappingsConfig(StrictBaseModel):
    active: bool = True
    mappings: List[TransformMappingConfig] = Field(
        default_factory=list, description="List of field mappings"
    )
    synonyms: List[TransformMappingSynonymConfig] = Field(
        default_factory=list, description="List of synonym field mappings"
    )


class TransformNonEmptyConfig(StrictBaseModel):
    active: bool = True


class TransformDuplicatesConfig(StrictBaseModel):
    active: bool = True
    threshold: conint(ge=0, le=100) = 90  # similarity threshold between 0 and 100
    primary_key: str
    fields: List[str] = Field(
        default_factory=list, description="Fields to consider for duplicate detection"
    )


class TransformDuplicateConfig(StrictBaseModel):
    active: bool = True
    duplicates: Dict[str, TransformDuplicatesConfig] = Field(
        default_factory=dict,
        description="Mapping from object name to its duplicate configuration",
    )


class MigManTransformConfig(StrictBaseModel):
    active: bool = True
    load_to_nemo: bool = True
    delete_temp_files: bool = True
    dump_files: bool = True
    nemo_project_prefix: str = "mmt"
    join: TransformJoinConfig
    mapping: TransformMappingsConfig
    duplicate: TransformDuplicateConfig
    nonempty: TransformNonEmptyConfig


##############################################################
# Load
##############################################################


class MigManLoadConfig(StrictBaseModel):
    active: bool = True
    delete_temp_files: bool = True
    delete_projects_before_load: bool = True
    nemo_project_prefix: str = "mml"
    development_deficiency_mining_only: bool = False
    development_load_reports_only: bool = False


##############################################################
# Full Config
##############################################################


class MigManGlobalConfig(StrictBaseModel):
    source_adapter: Literal[
        MigManExtractAdapter.GENERICODBC.value,
        MigManExtractAdapter.INFORCOM.value,
        MigManExtractAdapter.SAPECC.value,
        MigManExtractAdapter.PROALPHA.value,
        MigManExtractAdapter.SAGEKHK.value,
    ] = MigManExtractAdapter.GENERICODBC.value
    target_adapter: Literal[
        MigManLoadAdapter.PROALPHA_MIGMAN.value,
        MigManLoadAdapter.NEMO_BUSINESS_PROCESSES.value,
    ] = MigManLoadAdapter.PROALPHA_MIGMAN.value
    project_status_file: Optional[str] = None
    projects: List[str] = Field(
        default_factory=list,
        description="List of MigMan projects to process (alternatively, use property 'project_status_file')",
    )
    multi_projects_feature_assignments: List[str] = Field(
        default_factory=list,
        description="List of MigMan projects to include in the 'feature_assignments' multi-project",
    )
    multi_projects_texts: List[str] = Field(
        default_factory=list,
        description="List of MigMan projects to include in the 'texts' multi-project",
    )


class ConfigMigMan(StrictBaseModel):
    config_version: str = "0.0.1"
    etl_directory: str = "./etl/migman"
    ui_dark_model: bool = True
    setup: MigManGlobalConfig
    extract: MigManExtractConfig
    transform: MigManTransformConfig
    load: MigManLoadConfig


CONFIG_MODEL = ConfigMigMan
