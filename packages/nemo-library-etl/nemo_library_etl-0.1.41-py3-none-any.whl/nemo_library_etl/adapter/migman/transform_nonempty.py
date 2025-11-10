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


class MigManTransformNonEmpty:
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

    def nonempty(self) -> None:
        """
        Remove empty columns from the MigMan data.

        This method identifies and removes columns that are completely empty (NULL or empty strings)
        from the transformed data tables. It operates directly in DuckDB for memory efficiency.
        """
        self.logger.info("Removing empty columns from MigMan data")

        if not self.cfg.transform.nonempty.active:
            self.logger.info("Nonempty configuration is inactive, skipping nonempty")
            return

        for project in self.cfg.setup.projects:

            table = self.local_database.latest_table_name(
                steps=MigManTransformStep,
                maxstep=MigManTransformStep.NONEMPTY,
                entity=project,
            )
            if table is None:
                raise ValueError(f"No table found for entity {project}")

            self.logger.info(
                f"Processing nonempty for project: {project}, table: {table}"
            )

            # Get all column names and their data types
            columns_info = self.local_database.con.execute(
                f"SELECT name, type FROM pragma_table_info('{table}')"
            ).fetchall()

            if not columns_info:
                raise ValueError(f"Failed to retrieve columns for table {table}")

            # Identify empty columns by checking if all values are NULL or empty strings
            empty_columns = []
            non_empty_columns = []

            self.logger.info(f"Analyzing {len(columns_info)} columns for emptiness...")

            for column_name, column_type in columns_info:
                # Build condition to check if column is completely empty
                # For string types, check both NULL and empty string
                if column_type.upper() in ["VARCHAR", "TEXT", "CHAR"]:
                    empty_check_query = f"""
                        SELECT COUNT(*) 
                        FROM "{table}" 
                        WHERE "{column_name}" IS NOT NULL 
                        AND TRIM("{column_name}") != ''
                    """
                else:
                    # For non-string types, only check for NULL
                    empty_check_query = f"""
                        SELECT COUNT(*) 
                        FROM "{table}" 
                        WHERE "{column_name}" IS NOT NULL
                    """

                non_empty_count = self.local_database.con.execute(
                    empty_check_query
                ).fetchone()[0]

                if non_empty_count == 0:
                    empty_columns.append(column_name)
                    self.logger.debug(f"Column '{column_name}' is empty")
                else:
                    non_empty_columns.append(column_name)

            self.logger.info(
                f"Found {len(empty_columns)} empty columns out of {len(columns_info)} total columns"
            )

            if empty_columns:
                self.logger.info(f"Removing empty columns: {', '.join(empty_columns)}")

                # Create new table with only non-empty columns
                if non_empty_columns:
                    # Build SELECT statement with non-empty columns
                    select_columns = ", ".join(
                        [f'"{col}"' for col in non_empty_columns]
                    )
                    new_table_name = f"{MigManTransformStep.NONEMPTY.value}_{project}"

                    create_query = f"""
                        CREATE OR REPLACE TABLE "{new_table_name}" AS
                        SELECT {select_columns}
                        FROM "{table}"
                    """

                    self.local_database.query(create_query)

                    # Verify the new table
                    new_row_count = self.local_database.con.execute(
                        f'SELECT COUNT(*) FROM "{new_table_name}"'
                    ).fetchone()[0]

                    self.logger.info(
                        f"Created table '{new_table_name}' with {len(non_empty_columns)} columns and {new_row_count:,} rows"
                    )

                    # Export results if configured
                    if self.cfg.transform.dump_files:
                        self.local_database.export_table(
                            table_name=new_table_name,
                            fh=self.fh,
                            step=ETLStep.TRANSFORM,
                            substep=MigManTransformStep.NONEMPTY,
                            entity=project,
                            gzip_enabled=False,
                        )

                    # Upload to Nemo if configured
                    if self.cfg.transform.load_to_nemo:
                        self.local_database.upload_table_to_nemo(
                            table_name=new_table_name,
                            project_name=f"{self.cfg.transform.nemo_project_prefix}{new_table_name}",
                            delete_temp_files=self.cfg.transform.delete_temp_files,
                        )
                else:
                    self.logger.warning(
                        f"All columns in table '{table}' are empty - cannot create table with no columns"
                    )
            else:
                self.logger.info(
                    f"No empty columns found in table '{table}' - creating copy for consistency"
                )

                # Create a copy of the table for consistency in the pipeline
                new_table_name = f"{MigManTransformStep.NONEMPTY.value}_{project}"
                copy_query = f'CREATE OR REPLACE TABLE "{new_table_name}" AS SELECT * FROM "{table}"'
                self.local_database.query(copy_query)

                # Export and upload the unchanged table if configured
                if self.cfg.transform.dump_files:
                    self.local_database.export_table(
                        table_name=new_table_name,
                        fh=self.fh,
                        step=ETLStep.TRANSFORM,
                        substep=MigManTransformStep.NONEMPTY,
                        entity=project,
                        gzip_enabled=False,
                    )

                if self.cfg.transform.load_to_nemo:
                    self.local_database.upload_table_to_nemo(
                        table_name=new_table_name,
                        project_name=f"{self.cfg.transform.nemo_project_prefix}{new_table_name}",
                        delete_temp_files=self.cfg.transform.delete_temp_files,
                    )
