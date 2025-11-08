from pydantic import BaseModel, Field


class ExtractConfigRepIntercompany(BaseModel):
    active: bool = True

class TransformConfigRepIntercompany(BaseModel):
    active: bool = True

class LoadConfigRepIntercompany(BaseModel):
    active: bool = True
    analyze_table: bool = True

    
class ConfigRepIntercompany(BaseModel):

    config_version: str = "0.0.1"
    etl_directory: str = "./etl/repintercompany"
    extract: ExtractConfigRepIntercompany = Field(default_factory=ExtractConfigRepIntercompany)
    transform: TransformConfigRepIntercompany = Field(default_factory=TransformConfigRepIntercompany)
    load: LoadConfigRepIntercompany = Field(default_factory=LoadConfigRepIntercompany)

    class Config:
        extra = "allow"  # allow adapter-specific keys without failing

CONFIG_MODEL = ConfigRepIntercompany