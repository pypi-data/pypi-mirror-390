"""
MigMan ETL Extract Module.

This module handles the extraction phase of the MigMan ETL pipeline.
It provides functionality to extract data from MigMan systems and
prepare it for the transformation phase.

The extraction process:
1. Connects to the MigMan system using configured credentials
2. Iterates through configured tables and extracts data
3. Handles inactive tables by skipping them
4. Uses ETLFileHandler for data persistence
5. Provides comprehensive logging throughout the process

Classes:
    MigManExtract: Main class handling MigMan data extraction.
"""

from importlib import resources
import logging
from pathlib import Path
from typing import Union
from nemo_library_etl.adapter._utils.db_handler_local import ETLDuckDBHandler
from nemo_library_etl.adapter._utils.db_handler_source import DatabaseHandlerSource
from nemo_library_etl.adapter.migman.config_models_migman import ConfigMigMan
from nemo_library_etl.adapter._utils.enums import ETLStep
from nemo_library_etl.adapter._utils.file_handler import ETLFileHandler
from nemo_library import NemoLibrary

from nemo_library_etl.adapter.migman.enums import MigManExtractAdapter
from nemo_library_etl.adapter.migman.migmanutils import MigManUtils


class MigManExtractFromDatabase:
    """
    Handles extraction of data from MigMan system.

    This class manages the extraction phase of the MigMan ETL pipeline,
    providing methods to connect to MigMan systems, retrieve data,
    and prepare it for subsequent transformation and loading phases.

    The extractor:
    - Uses NemoLibrary for core functionality and configuration
    - Integrates with Prefect logging for pipeline visibility
    - Processes tables based on configuration settings
    - Handles both active and inactive table configurations
    - Leverages ETLFileHandler for data persistence

    Attributes:
        nl (NemoLibrary): Core Nemo library instance for system integration.
        config: Configuration object from the Nemo library.
        logger: Prefect logger for pipeline execution tracking.
        cfg (PipelineMigMan): Pipeline configuration with extraction settings.
    """

    def __init__(
        self,
        nl: NemoLibrary,
        cfg: ConfigMigMan,
        logger: Union[logging.Logger, object],
        fh: ETLFileHandler,
        local_database: ETLDuckDBHandler,
    ) -> None:
        """
        Initialize the MigMan Extract instance.

        Sets up the extractor with the necessary library instances, configuration,
        and logging capabilities for the extraction process.

        Args:
            nl (NemoLibrary): Core Nemo library instance for system integration.
            cfg (PipelineZentis): Pipeline configuration object containing
                                                          extraction settings and rules.
            logger (Union[logging.Logger, object]): Logger instance for recording execution details.
                                                   Can be a standard Python logger or Prefect logger.
        """
        self.nl = nl
        self.cfg = cfg
        self.logger = logger
        self.fh = fh
        self.local_database = local_database

        super().__init__()

    def extract_from_database(self) -> None:
        """
        Execute the main extraction process for MigMan data.

        This method orchestrates the complete extraction process by:
        1. Logging the start of extraction
        2. Iterating through configured tables
        3. Skipping inactive tables
        4. Processing active tables and extracting their data
        5. Using ETLFileHandler for data persistence

        The method respects table activation settings and provides detailed
        logging for monitoring and debugging purposes.

        Note:
            The actual data extraction logic needs to be implemented based on
            the specific MigMan system requirements.
        """
        self.logger.info("Extracting all MigMan objects")

        # extract objects
        dbsrc = DatabaseHandlerSource(
            nl=self.nl,
            cfg=self.cfg,
            logger=self.logger,
            fh=self.fh,
        )

        if not self.cfg.setup.source_adapter:
            raise ValueError("No adapter specified for extraction")

        try:
            self.logger.info(
                f"Starting extraction for {self.cfg.setup.source_adapter} ..."
            )

            # identify tables to extract
            tables_to_extract, fields_to_extract = self.get_tables_and_fields(
                self.cfg.setup.source_adapter
            )

            if not tables_to_extract:
                raise ValueError("No tables to extract found")
            if not fields_to_extract:
                raise ValueError("No fields to extract found")

            self.logger.info(
                f"Tables to extract for {self.cfg.setup.source_adapter}: {tables_to_extract}"
            )
            self.logger.info(
                f"Fields to extract for {self.cfg.setup.source_adapter}: {fields_to_extract}"
            )

            # connect source database
            match self.cfg.setup.source_adapter:
                case MigManExtractAdapter.GENERICODBC.value:
                    conn = dbsrc.connect_odbc(
                        odbc_connstr=self.cfg.extract.genericodbc.odbc_connstr,
                        timeout=self.cfg.extract.genericodbc.timeout,
                    )

                case MigManExtractAdapter.INFORCOM.value:
                    conn = dbsrc.connect_odbc(
                        odbc_connstr=self.cfg.extract.inforcom.odbc_connstr,
                        timeout=self.cfg.extract.inforcom.timeout,
                    )
                case MigManExtractAdapter.SAPECC.value:
                    conn = dbsrc.connect_hdb(
                        address=self.cfg.extract.sapecc.address,
                        port=self.cfg.extract.sapecc.port,
                        user=self.cfg.extract.sapecc.user,
                        password=self.cfg.extract.sapecc.password,
                        autocommit=self.cfg.extract.sapecc.autocommit,
                    )

                case MigManExtractAdapter.PROALPHA.value:
                    conn = dbsrc.connect_odbc(
                        odbc_connstr=self.cfg.extract.proalpha.odbc_connstr,
                        timeout=self.cfg.extract.proalpha.timeout,
                    )

                case MigManExtractAdapter.SAGEKHK.value:
                    conn = dbsrc.connect_odbc(
                        odbc_connstr=self.cfg.extract.sagekhk.odbc_connstr,
                        timeout=self.cfg.extract.sagekhk.timeout,
                    )
                case _:
                    raise ValueError(
                        f"Unknown adapter: {self.cfg.setup.source_adapter}"
                    )

            if not conn:
                raise ConnectionError(
                    f"Failed to connect to {self.cfg.setup.source_adapter} database"
                )

            # extract tables
            for table_name in tables_to_extract:
                self.logger.info(
                    f"Extracting table {table_name} from {self.cfg.setup.source_adapter} ..."
                )
                query = f"""
SELECT 
    {', '.join(fields_to_extract.get(table_name, []))} 
FROM 
    {getattr(self.cfg.extract, f"{self.cfg.setup.source_adapter}").table_prefix}{table_name}
"""
                self.logger.info(f"Using query: {query}")
                dbsrc.generic_odbc_extract(
                    conn=conn,
                    query=query,
                    entity=table_name,
                    step=ETLStep.EXTRACT,
                    chunksize=getattr(
                        self.cfg.extract, f"{self.cfg.setup.source_adapter}"
                    ).chunk_size,
                )

                self.local_database.ingest_jsonl(
                    step=ETLStep.EXTRACT,
                    entity=table_name,
                    ignore_nonexistent=True,
                    create_mode="replace",  # or "append"
                    table_name=table_name,  # keep your original table name
                    add_metadata=True,  # adds _source_path & _ingested_at
                )

                if self.cfg.extract.load_to_nemo:
                    self.local_database.upload_table_to_nemo(
                        table_name=table_name,
                        project_name=f"{self.cfg.extract.nemo_project_prefix}{table_name}",
                        delete_temp_files=self.cfg.extract.delete_temp_files,
                    )

            conn.close()
            self.logger.info(
                f"Completed extraction for {self.cfg.setup.source_adapter}."
            )
        except Exception as e:
            self.logger.error(
                f"Error during extraction for {self.cfg.setup.source_adapter}: {e}"
            )
            raise
        finally:
            try:
                if conn:
                    conn.cursor().close()
                    conn.close()
            except Exception as close_err:
                self.logger.warning(
                    f"Failed to close connection for {self.cfg.setup.source_adapter}: {close_err}"
                )

    def get_tables_and_fields(self, adapter) -> tuple[list[str], dict[str, list[str]]]:

        tables_to_extract = []
        fields_to_extract = {}

        if getattr(self.cfg.extract, f"{adapter}").table_selector == "all":
            tables_to_extract = getattr(self.cfg.extract, f"{adapter}").tables
            fields_to_extract = {table: ["*"] for table in tables_to_extract}
        elif getattr(self.cfg.extract, f"{adapter}").table_selector == "join_parser":
            for project in MigManUtils.get_migman_projects(self.cfg):

                query = MigManUtils.getJoinQuery(adapter=adapter, project=project)

                tables_to_extract.extend(self.local_database.extract_tables(sql=query))
                fields_in_query = self.local_database.extract_fields_by_base_table(
                    sql=query
                )
                for table, fields in fields_in_query.items():
                    fields_to_extract.setdefault(table, []).extend(fields)

        tables_to_extract = list(set(tables_to_extract))  # deduplicate
        return tables_to_extract, fields_to_extract
