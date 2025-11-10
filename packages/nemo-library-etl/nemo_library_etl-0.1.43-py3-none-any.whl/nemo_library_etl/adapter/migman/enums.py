from enum import Enum


class MigManExtractAdapter(Enum):
    GENERICODBC = "genericodbc"
    INFORCOM = "inforcom"
    SAPECC = "sapecc"
    PROALPHA = "proalpha"
    SAGEKHK = "sagekhk"

class MigManLoadAdapter(Enum):
    PROALPHA_MIGMAN = "proalpha_migman"
    NEMO_BUSINESS_PROCESSES = "nemo_business_process"

class MigManTransformStep(Enum):
    JOINS = "10_joins"
    MAPPINGS = "20_mappings"
    DUPLICATES = "30_duplicates"
    NONEMPTY = "40_nonempty"
