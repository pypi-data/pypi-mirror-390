import logging
from pathlib import Path
from typing import Union
from nemo_library_etl.adapter._utils.db_handler_local import ETLDuckDBHandler
from nemo_library_etl.adapter._utils.enums import ETLStep
from nemo_library_etl.adapter.migman.config_models_migman import ConfigMigMan
from nemo_library_etl.adapter._utils.file_handler import ETLFileHandler
from nemo_library import NemoLibrary


class MigManExtractFromFile:
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

    def extract_from_file(self) -> None:
        """
        Extract data from a file source.

        This method handles the extraction of data from a file specified in the
        pipeline configuration. It reads the file, processes the contents, and
        stores the extracted data in the local database.

        Returns:
            None
        """
        self.logger.info("Extracting data from files")

        files = [file for file in self.cfg.extract.file if file.active  ]
        for file in files:
            
            file_path = Path(file.file_path)
            self.logger.info(f"Processing file: {file_path}")

            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            # we support CSV only for now
            if file_path.suffix.lower() != ".csv":
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
            
            self.local_database.ingest_csv(
                filename=file_path.absolute().as_posix(),
                table_name=file.project,
                separator=file.separator,
                quote=file.quote,
                dateformat=file.dateformat,
                encoding=file.encoding,
                header=file.header,
                columns=file.columns,
                all_varchar=file.all_varchar,
            )

            if self.cfg.extract.load_to_nemo:
                self.local_database.upload_table_to_nemo(
                    table_name=file.project,
                    project_name=f"{self.cfg.extract.nemo_project_prefix}{file.project}",
                    delete_temp_files=self.cfg.extract.delete_temp_files,
                )
