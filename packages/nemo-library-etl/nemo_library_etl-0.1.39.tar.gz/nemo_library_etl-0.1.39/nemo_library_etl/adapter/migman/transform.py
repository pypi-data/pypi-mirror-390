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

from importlib import resources
import logging
from pathlib import Path
import re
from typing import Union
from nemo_library_etl.adapter._utils.db_handler_local import ETLDuckDBHandler
from nemo_library_etl.adapter.migman.config_models_migman import (
    ConfigMigMan,
    TransformDuplicateConfig,
    TransformDuplicatesConfig,
)
from nemo_library_etl.adapter._utils.enums import ETLAdapter, ETLStep
from nemo_library_etl.adapter._utils.file_handler import ETLFileHandler
from nemo_library import NemoLibrary

from nemo_library_etl.adapter.migman.enums import MigManTransformStep
from rapidfuzz import fuzz

from nemo_library_etl.adapter.migman.migmanutils import MigManUtils


class MigManTransform:
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

            # get join configuration for the project
            join_cfg = self.cfg.transform.join.joins.get(project, None)
            if join_cfg is None:
                raise ValueError(f"No join configuration found for project: {project}")

            if not join_cfg.active:
                self.logger.info(f"Skipping inactive join: {project}")
                continue

            self.logger.info(f"Processing join: {project}")

            query = MigManUtils.getJoinQuery(
                adapter=self.cfg.setup.source_adapter, join_file=join_cfg.file
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

    def mappings(self) -> None:
        """
        Apply mappings to the MigMan data.

        This method processes the MigMan data by applying predefined mappings
        to transform the data according to business rules and requirements.
        It ensures that the data is correctly formatted and enriched for
        subsequent loading into the target system.

        Note:
            The actual mapping logic needs to be implemented based on
            the specific MigMan system requirements and mapping definitions.
        """
        self.logger.info("Applying mappings to MigMan data")

        if not self.cfg.transform.mapping.active:
            self.logger.info("Mapping configuration is inactive, skipping mappings")
            return

        for mapping in self.cfg.transform.mapping.mappings:

            if not mapping.active:
                self.logger.info(f"Mapping {mapping} is inactive, skipping")
                continue

            self.logger.info(f"Processing mapping: {mapping}")

            # Implement mapping logic here
        

    def newnumbers(self) -> None:
        """
        Assign new numbers to MigMan data records.

        This method generates and assigns new unique identifiers or numbers
        to the MigMan data records as part of the transformation process.
        It ensures that each record has a distinct identifier for tracking
        and reference in the target system.

        Note:
            The actual new number assignment logic needs to be implemented based on
            the specific MigMan system requirements and numbering schemes.
        """
        self.logger.info("Assigning new numbers to MigMan data")

        if not self.cfg.transform.newnumbers.active:
            self.logger.info("NewNumbers configuration is inactive, skipping new numbers")
            return

        # Placeholder for new number assignment logic
        self.logger.info("New number assignment logic is not yet implemented.")
        
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

    def duplicates(self) -> None:
        """
        Handle duplicate records in the MigMan data.

        This method identifies and processes duplicate records in the extracted
        MigMan data to ensure data integrity and quality before loading into the
        target system. The specific logic for handling duplicates should be
        implemented based on business rules and requirements.

        Steps may include:
        1. Identifying duplicate records based on key fields.
        2. Merging or removing duplicates according to defined rules.
        3. Logging actions taken for audit purposes.

        Note:
            The actual implementation of duplicate handling logic is pending
            and should be customized to fit the MigMan system's needs.
        """
        self.logger.info("Handling duplicates in MigMan data")

        if not self.cfg.transform.duplicate.active:
            self.logger.info("Duplicate configuration is inactive, skipping joins")
            return

        # create UDFs in DuckDB
        def normalize_text(s: str) -> str:
            if s is None:
                return ""
            s = s.lower().strip()
            s = (
                s.replace("ä", "ae")
                .replace("ö", "oe")
                .replace("ü", "ue")
                .replace("ß", "ss")
            )
            s = re.sub(r"[^\w\s]", " ", s)  # remove punctuation
            s = re.sub(r"\s+", " ", s).strip()  # collapse spaces
            return s

        def text_similarity(a: str, b: str) -> float:
            a = normalize_text(a)
            b = normalize_text(b)
            return float(fuzz.token_set_ratio(a, b))

        self.local_database.con.create_function("normalize_text", normalize_text)
        self.local_database.con.create_function("text_similarity", text_similarity)

        for duplicate_name, model in self.cfg.transform.duplicate.duplicates.items():
            if model.active is False:
                self.logger.info(f"Skipping inactive duplicate model: {duplicate_name}")
                continue

            if not duplicate_name in self.cfg.setup.projects:
                self.logger.warning(
                    f"Duplicate model {duplicate_name} not in configured projects, skipping"
                )
                continue

            self._perform_duplicate_check(duplicate_name, model)

    def _perform_duplicate_check(
        self, duplicate_name: str, model: TransformDuplicatesConfig
    ) -> None:
        """
        Single-pass duplicate annotation with 100% recall for token_set similarity:
        - Build token inverted index (id -> tokens of normalized text)
        - Candidates = pairs sharing at least one token (no false negatives for token_set)
        - Compute similarity and aggregate partners
        - Output has same row count as source; includes JSON partners, top score, count
        - Logs progress per phase (row/token/candidate counts)
        """
        from datetime import datetime

        start_time = datetime.now()

        table = self.local_database.latest_table_name(
            steps=MigManTransformStep,
            maxstep=MigManTransformStep.DUPLICATES,
            entity=duplicate_name,
        )
        if table is None:
            raise ValueError(f"No table found for entity {duplicate_name}")
        id_col = model.primary_key
        con = self.local_database.con
        thresh = model.threshold
        out_tbl = f"{MigManTransformStep.DUPLICATES.value}_{duplicate_name}"

        self.logger.info(
            f"[{duplicate_name}] Starting duplicate check on table {table} for fields {model.fields} with threshold {thresh}"
        )

        # Helper: CONCAT of configured columns (safe cast to VARCHAR)
        def concat_expr(alias: str, cols: list[str]) -> str:
            parts = [f"coalesce(CAST({alias}.\"{c}\" AS VARCHAR), '')" for c in cols]
            return " || ' | ' || ".join(parts) if parts else "''"

        base_concat = concat_expr("b", model.fields)

        # 1) Base: id, normalized text, raw length
        base_tmp = f"__dup_base_{duplicate_name.lower()}"
        con.execute(f'DROP TABLE IF EXISTS "{base_tmp}"')
        con.execute(
            f"""
            CREATE TEMPORARY TABLE "{base_tmp}" AS
            SELECT
                CAST(b."{id_col}" AS VARCHAR)                 AS id,
                normalize_text({base_concat})                 AS norm_text,
                length({base_concat})                         AS txt_len
            FROM "{table}" b
        """
        )
        n_rows = con.execute(f'SELECT COUNT(*) FROM "{base_tmp}"').fetchone()[0]
        self.logger.info(
            f"[{duplicate_name}] Phase 1/5: base prepared — rows: {n_rows:,}"
        )

        # (Optional) Tiny stopword set; leave empty list [] for absolute maximal recall.
        # For high threshold (>=90), filtering 'gmbh'/'ag' etc. is usually safe and reduces huge candidate stars.
        stop_tmp = f"__dup_stop_{duplicate_name.lower()}"
        con.execute(f'DROP TABLE IF EXISTS "{stop_tmp}"')
        con.execute(
            f"""
            CREATE TEMPORARY TABLE "{stop_tmp}"(token VARCHAR);
            INSERT INTO "{stop_tmp}" VALUES
                -- comment-out or remove lines to disable specific stopwords
                ('gmbh'),('mbh'),('kg'),('ag'),('co'),('kg'),('und'),('the'),('der'),('die');
        """
        )

        # 2) Tokenize: one row per (id, token)
        # Use simple space split on the normalized text (already lowercased & cleaned).
        tokens_tmp = f"__dup_tokens_{duplicate_name.lower()}"
        con.execute(f'DROP TABLE IF EXISTS "{tokens_tmp}"')
        con.execute(
            f"""
            CREATE TEMPORARY TABLE "{tokens_tmp}" AS
            SELECT
                id,
                u.token
            FROM "{base_tmp}"
            , UNNEST(string_split(norm_text, ' ')) AS u(token)
            WHERE u.token <> ''
            AND NOT EXISTS (SELECT 1 FROM "{stop_tmp}" s WHERE s.token = u.token);
            """
        )
        n_tokens = con.execute(f'SELECT COUNT(*) FROM "{tokens_tmp}"').fetchone()[0]
        n_dist_t = con.execute(
            f'SELECT COUNT(DISTINCT token) FROM "{tokens_tmp}"'
        ).fetchone()[0]
        self.logger.info(
            f"[{duplicate_name}] Phase 2/5: tokens built — rows: {n_tokens:,}, distinct tokens: {n_dist_t:,}"
        )

        # 3) Candidate pairs via token matches (distinct id pairs)
        pairs_cand = f"__dup_pairs_cand_{duplicate_name.lower()}"
        con.execute(f'DROP TABLE IF EXISTS "{pairs_cand}"')
        con.execute(
            f"""
            CREATE TEMPORARY TABLE "{pairs_cand}" AS
            SELECT DISTINCT
                LEAST(a.id, b.id)  AS left_id,
                GREATEST(a.id, b.id) AS right_id
            FROM "{tokens_tmp}" a
            JOIN "{tokens_tmp}" b
            ON a.token = b.token
            AND a.id <> b.id
        """
        )
        n_cand = con.execute(f'SELECT COUNT(*) FROM "{pairs_cand}"').fetchone()[0]
        self.logger.info(
            f"[{duplicate_name}] Phase 3/5: candidates generated — pairs: {n_cand:,}"
        )

        # 4) Score candidates and filter by threshold
        pairs_keep = f"__dup_pairs_keep_{duplicate_name.lower()}"
        con.execute(f'DROP TABLE IF EXISTS "{pairs_keep}"')
        con.execute(
            f"""
            CREATE TEMPORARY TABLE "{pairs_keep}" AS
            SELECT
                p.left_id,
                p.right_id,
                text_similarity(a.norm_text, b.norm_text) AS score
            FROM "{pairs_cand}" p
            JOIN "{base_tmp}" a ON a.id = p.left_id
            JOIN "{base_tmp}" b ON b.id = p.right_id
            WHERE text_similarity(a.norm_text, b.norm_text) >= {thresh}
        """
        )
        n_keep = con.execute(f'SELECT COUNT(*) FROM "{pairs_keep}"').fetchone()[0]
        self.logger.info(
            f"[{duplicate_name}] Phase 4/5: scored+filtered — matches >= {thresh}: {n_keep:,}"
        )

        # 5) Build partners for each id and write final annotated table
        con.execute(
            f"""
            CREATE OR REPLACE TABLE "{out_tbl}" AS
            WITH partners AS (
                SELECT left_id AS id,  right_id AS partner_id, score FROM "{pairs_keep}"
                UNION ALL
                SELECT right_id AS id, left_id  AS partner_id, score FROM "{pairs_keep}"
            ),
            agg AS (
                SELECT
                    id,
                    to_json(
                        list(
                            struct_pack(partner_id := partner_id, score := score)
                            ORDER BY score DESC, partner_id
                        )
                    ) AS duplicate_partners_json,
                    max(score) AS duplicate_top_score,
                    count(*)   AS duplicate_match_count
                FROM partners
                GROUP BY id
            )
            SELECT
                b.*,
                coalesce(agg.duplicate_partners_json, '[]') AS duplicate_partners_json,
                coalesce(agg.duplicate_top_score, 0)        AS duplicate_top_score,
                coalesce(agg.duplicate_match_count, 0)      AS duplicate_match_count
            FROM "{table}" b
            LEFT JOIN agg ON agg.id = CAST(b."{id_col}" AS VARCHAR)
        """
        )
        src_cnt = con.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
        out_cnt = con.execute(f'SELECT COUNT(*) FROM "{out_tbl}"').fetchone()[0]

        end_time = datetime.now()
        self.logger.info(
            f"[{duplicate_name}] Phase 5/5: annotated table created: {out_tbl} — rows: {out_cnt:,} (source {src_cnt:,}), duration: {end_time - start_time}"
        )

        self.local_database.export_table(
            table_name=out_tbl,
            fh=self.fh,
            step=ETLStep.TRANSFORM,
            entity=duplicate_name,
            substep=MigManTransformStep.DUPLICATES,
        )

        if self.cfg.transform.load_to_nemo:
            self.local_database.upload_table_to_nemo(
                table_name=out_tbl,
                project_name=f"{self.cfg.transform.nemo_project_prefix}{out_tbl}",
                delete_temp_files=self.cfg.transform.delete_temp_files,
            )
