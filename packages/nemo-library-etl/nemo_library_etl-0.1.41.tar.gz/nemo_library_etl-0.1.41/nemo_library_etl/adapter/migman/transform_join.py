"""
MigMan ETL Transform Module.

This module handles the transformation phase of the MigMan ETL pipeline.
It processes the extracted data, applies business rules, data cleaning, and formatting
to prepare the data for loading into the target system.

The transformation process typically includes:
1. Data validation and quality checks
2. Data type conversions and formatting
3. Business rule application
4. Data enrichment and calculated fields
5. Data structure normalization
6. Comprehensive logging throughout the process

Classes:
    MigManTransform: Main class handling MigMan data transformation.
"""

import logging
from typing import Union
from nemo_library_etl.adapter._utils.db_handler_local import ETLDuckDBHandler
from nemo_library_etl.adapter.migman.config_models_migman import (
    ConfigMigMan,
)
from nemo_library_etl.adapter._utils.enums import ETLStep
from nemo_library_etl.adapter._utils.file_handler import ETLFileHandler
from nemo_library import NemoLibrary

from nemo_library_etl.adapter.migman.enums import MigManTransformStep

from nemo_library_etl.adapter.migman.migmanutils import MigManUtils


class MigManTransformJoin:
    """
    Handles transformation of extracted MigMan data.

    This class manages the transformation phase of the MigMan ETL pipeline,
    providing methods to process, clean, and format the extracted data for loading
    into the target system.

    The transformer:
    - Uses NemoLibrary for core functionality and configuration
    - Integrates with Prefect logging for pipeline visibility
    - Applies business rules and data validation
    - Handles data type conversions and formatting
    - Provides data enrichment and calculated fields
    - Ensures data quality and consistency

    Attributes:
        nl (NemoLibrary): Core Nemo library instance for system integration.
        config: Configuration object from the Nemo library.
        logger: Prefect logger for pipeline execution tracking.
        cfg (PipelineMigMan): Pipeline configuration with transformation settings.
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
        Initialize the MigMan Transform instance.

        Sets up the transformer with the necessary library instances, configuration,
        and logging capabilities for the transformation process.

        Args:
            nl (NemoLibrary): Core Nemo library instance for system integration.
            cfg (PipelineMigMan): Pipeline configuration object containing
                                                          transformation settings and rules.
            logger (Union[logging.Logger, object]): Logger instance for recording execution details.
                                                   Can be a standard Python logger or Prefect logger.
        """
        self.nl = nl
        self.cfg = cfg
        self.logger = logger
        self.fh = fh
        self.local_database = local_database

        super().__init__()

    def joins(self) -> None:
        """
        Execute join operations for MigMan data transformation.

        This method handles the joining of data from different sources or tables
        as part of the transformation process. It ensures that related data is
        combined correctly based on specified keys and relationships.

        The join process includes:
        1. Identifying the datasets to be joined
        2. Defining the join keys and types (e.g., inner, left, right, full)
        3. Performing the join operation using efficient algorithms
        4. Validating the joined data for consistency and integrity
        5. Logging the join process for monitoring and debugging

        Note:
            The actual join logic needs to be implemented based on
            the specific MigMan system requirements and data relationships.
        """
        self.logger.info("Joining MigMan objects")

        if not self.cfg.transform.join.active:
            self.logger.info("Join configuration is inactive, skipping joins")
            return

        self.logger.info(f"Using adapter: {self.cfg.setup.source_adapter}")

        for project in self.cfg.setup.projects:

            self.logger.info(f"Processing join: {project}")

            query = MigManUtils.getJoinQuery(
                adapter=self.cfg.setup.source_adapter, 
                project=project,
            )

            # if we have configured a limit, apply it to the query
            if self.cfg.transform.join.limit is not None:
                self.logger.info(
                    f"Applying limit of {self.cfg.transform.join.limit} to join query"
                )
                query += f"\nLIMIT {self.cfg.transform.join.limit}\n"

            # add result_creation to the query
            table_name = MigManTransformStep.JOINS.value + "_" + project
            query = f'CREATE OR REPLACE TABLE "{table_name}" AS\n' + query

            # Execute the join query
            self.local_database.query(query)

            # Compare columns with expected columns from Migman
            columns = self.local_database.con.execute(
                f"SELECT name FROM pragma_table_info('{table_name}')"
            ).fetchall()
            columns = [col[0] for col in columns]
            project_name, postfix = MigManUtils.split_migman_project_name(project)
            MigManUtils.validate_columns(
                project=project_name, postfix=postfix, columns=columns, missing_ok=True
            )

            # export results from database
            if self.cfg.transform.dump_files:
                self.local_database.export_table(
                    table_name=table_name,
                    fh=self.fh,
                    step=ETLStep.TRANSFORM,
                    substep=MigManTransformStep.JOINS,
                    entity=project,
                    gzip_enabled=False,
                )

            if self.cfg.transform.load_to_nemo:
                self.local_database.upload_table_to_nemo(
                    table_name=table_name,
                    project_name=f"{self.cfg.transform.nemo_project_prefix}{table_name}",
                    delete_temp_files=self.cfg.transform.delete_temp_files,
                )
