# All code comments in English as requested
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

##############################################################
# Shared strict base model (forbid unknown keys everywhere)
##############################################################


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",  # disallow unknown/extra fields globally
        str_strip_whitespace=True,  # optional: trim leading/trailing whitespace
        populate_by_name=True,  # allow alias or field name population
    )


##############################################################
# Adapter-specific config sections
##############################################################


class TableGedys(BaseModel):
    """
    Configuration model for individual Gedys tables.

    This model defines the configuration structure for each table in the Gedys
    system that will be processed by the ETL pipeline. Each table configuration
    includes identification and control parameters.

    Attributes:
        GUID (str): Unique identifier for the table in the Gedys system.
        active (bool): Flag indicating whether this table should be processed.
                      Defaults to True.
    """

    GUID: str
    active: bool = True
    history: bool = False  # Whether to include record history in extraction
    sentiment_analysis_fields: Optional[List[str]] = (
        None  # Fields for sentiment analysis
    )


class ExtractConfigGedys(StrictBaseModel):
    active: bool = True
    URL: str = ""
    userid: str = ""
    password: str = ""
    chunksize: int = 100
    file_chunksize: int = 1000
    maxrecords: int | None = None # Optional limit on total records to extract
    load_to_nemo: bool = True
    delete_temp_files: bool = True
    nemo_project_prefix: str = "gde"
    tables: Dict[str, TableGedys] = Field(default_factory=dict)


class TransformConfigGedys(StrictBaseModel):
    active: bool = True


class LoadConfigGedys(StrictBaseModel):
    active: bool = True


##############################################################
# Full adapter config
##############################################################


class ConfigGedys(StrictBaseModel):
    config_version: str = "0.0.1"
    etl_directory: str = "./etl/gedys"
    extract: ExtractConfigGedys = Field(
        default_factory=ExtractConfigGedys,
        description="Extraction configuration for this adapter",
    )
    transform: TransformConfigGedys = Field(
        default_factory=TransformConfigGedys,
        description="Transformation configuration for this adapter",
    )
    load: LoadConfigGedys = Field(
        default_factory=LoadConfigGedys,
        description="Load configuration for this adapter",
    )


##############################################################
# Export default config model
##############################################################

CONFIG_MODEL = ConfigGedys
