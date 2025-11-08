"""
MigMan ETL Load Module.

This module handles the loading phase of the MigMan ETL pipeline.
It takes the transformed data and loads it into the target system, typically the
Nemo database or data warehouse.

The loading process typically includes:
1. Data validation before insertion
2. Connection management to target systems
3. Batch processing for efficient data loading
4. Error handling and rollback capabilities
5. Data integrity checks post-loading
6. Performance optimization for large datasets
7. Comprehensive logging throughout the process

Classes:
    MigManLoad: Main class handling MigMan data loading.
"""

import logging
from pathlib import Path
import re
from typing import Union
from nemo_library_etl.adapter._utils.db_handler_local import ETLDuckDBHandler
from nemo_library_etl.adapter.migman.config_models_migman import ConfigMigMan
from nemo_library_etl.adapter._utils.file_handler import ETLFileHandler
from nemo_library import NemoLibrary
from nemo_library.model.project import Project
from nemo_library.model.column import Column
from nemo_library.model.report import Report
from nemo_library.model.rule import Rule

from nemo_library_etl.adapter.migman.enums import MigManTransformStep

from nemo_library_etl.adapter.migman.migmanutils import MigManUtils
from nemo_library.utils.utils import (
    get_internal_name,
)


DATA_CLASSIFICATIONS = {
    "S_Adresse.HomePage": "url",
    "S_Adresse.EMail": "email",
    "S_Adresse.Handy": "phone_number",
    "S_Adresse.Telefax": "phone_number",
    "S_Adresse.Telefon": "phone_number",
    "S_Adresse.Telefon2": "phone_number",
    "S_Adresse.Name1": "address",
    "S_Adresse.Name2": "address",
    "S_Adresse.Name3": "address",
    "S_Adresse.Staat": "address",
    "S_Adresse.Ort": "address",
    "S_Adresse.PLZ": "address",
    "S_Adresse.Strasse": "address",
    "S_Adresse.Hausnummer": "address",
}


class MigManLoad:
    """
    Handles loading of transformed MigMan data into target system.

    This class manages the loading phase of the MigMan ETL pipeline,
    providing methods to insert transformed data into the target system with
    proper error handling, validation, and performance optimization.

    The loader:
    - Uses NemoLibrary for core functionality and configuration
    - Integrates with Prefect logging for pipeline visibility
    - Manages database connections and transactions
    - Provides batch processing capabilities
    - Handles data validation before insertion
    - Ensures data integrity and consistency
    - Optimizes performance for large datasets

    Attributes:
        nl (NemoLibrary): Core Nemo library instance for system integration.
        config: Configuration object from the Nemo library.
        logger: Prefect logger for pipeline execution tracking.
        cfg (PipelineMigMan): Pipeline configuration with loading settings.
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
        Initialize the MigMan Load instance.

        Sets up the loader with the necessary library instances, configuration,
        and logging capabilities for the loading process.

        Args:
            nl (NemoLibrary): Core Nemo library instance for system integration.
            cfg (PipelineMigMan): Pipeline configuration object containing
                                                          loading settings and rules.
            logger (Union[logging.Logger, object]): Logger instance for recording execution details.
                                                   Can be a standard Python logger or Prefect logger.
        """
        self.nl = nl
        self.cfg = cfg
        self.logger = logger
        self.fh = fh
        self.local_database = local_database
        self.migman_database = MigManUtils.MigManDatabaseLoad()

        super().__init__()

    def _nemo_project_name(self, project: str) -> str:
        return f"{self.cfg.load.nemo_project_prefix}{project}"

    def load(self) -> None:
        """
        Execute the main loading process for MigMan data.

        This method orchestrates the complete loading process by:
        1. Connecting to the target system (database, data warehouse, etc.)
        2. Loading transformed data from the previous ETL phase
        3. Validating data before insertion
        4. Performing batch inserts for optimal performance
        5. Handling errors and implementing rollback mechanisms
        6. Verifying data integrity post-insertion
        7. Updating metadata and audit tables
        8. Cleaning up temporary resources

        The method provides detailed logging for monitoring and debugging purposes
        and ensures transaction safety through proper error handling.

        Note:
            The actual loading logic needs to be implemented based on
            the target system requirements and data models.
        """
        self.logger.info("Loading all MigMan objects")

        if self.cfg.load.delete_projects_before_load:
            self.logger.info("Deleting existing MigMan projects before load")
            project_ids = []
            for project in self.cfg.setup.projects:
                projectid = self.nl.getProjectID(self._nemo_project_name(project))
                if projectid:
                    project_ids.append(projectid)
            self.nl.deleteProjects(project_ids)

        # load objects - standard first
        for project in self.cfg.setup.projects:
            self.logger.info(f"Creating/updating project in NEMO: {project}")
            project, postfix = MigManUtils.split_migman_project_name(project)
            self._create_update_nemo_project(
                project=project, addon=None, postfix=postfix
            )

        for feature_assignment in self.cfg.setup.multi_projects_feature_assignments:
            self.logger.info(
                f"Creating/updating multi-project for feature assignments in NEMO: {feature_assignment}"
            )
            self._create_update_nemo_project(
                project="Features (Assignments)", addon=feature_assignment, postfix=""
            )

        for text in self.cfg.setup.multi_projects_texts:
            self.logger.info(
                f"Creating/updating multi-project for texts in NEMO: {text}"
            )
            self._create_update_nemo_project(
                project="Features (Assignments)", addon=text, postfix=""
            )

    def _create_update_nemo_project(
        self, project: str, addon: str | None, postfix: str
    ) -> None:

        # do we have data to load?
        table_name = self.local_database.latest_table_name(
            steps=MigManTransformStep, maxstep=None, entity=project
        )
        if table_name is None:
            raise ValueError(f"No table found for entity {project}")

        # does project exist already?
        nemo_project_name = self._nemo_project_name(
            MigManUtils.MigManProjectName(project, addon, postfix)
        )
        projectid = self.nl.getProjectID(nemo_project_name)

        if (
            self.cfg.load.development_deficiency_mining_only
            or self.cfg.load.development_load_reports_only
        ) and not projectid:
            raise ValueError(
                f"Project {nemo_project_name} does not exist. Cannot proceed with development deficiency mining only mode."
            )

        # Get all column names
        columns_info = self.local_database.con.execute(
            f"SELECT name FROM pragma_table_info('{table_name}')"
        ).fetchall()

        if not columns_info:
            raise ValueError(f"Failed to retrieve columns for table {table_name}")

        columns = [col[0] for col in columns_info]

        if projectid is None:
            self.logger.info(
                f"Project does not exist. Creating NEMO project: {nemo_project_name}"
            )
            self.nl.createProjects(
                projects=[
                    Project(
                        displayName=nemo_project_name,
                        description=f"Data Model for Mig Man table '{project}', addon '{addon}', postfix '{postfix}'",
                    )
                ],
            )

            new_columns = []
            for column_name in columns:

                # special columns
                if column_name in [
                    "duplicate_partners_json",
                    "duplicate_top_score",
                    "duplicate_match_count",
                ]:
                    self.logger.info(f"Skipping special column: {column_name}")
                    continue
                else:
                    # search column in migman database
                    mig_man_col = next(
                        (
                            col
                            for col in self.migman_database
                            if col.project == project
                            and col.postfix == postfix
                            and col.nemo_import_name == column_name
                        ),
                        None,
                    )
                    if not mig_man_col:
                        raise ValueError(
                            f"Column '{column_name}' not found in MigMan database for project '{project}' and postfix '{postfix}'"
                        )

                    description = "\n".join(
                        f"{k}: {v if v else '<None>'}"
                        for k, v in mig_man_col.to_dict().items()
                    )
                    data_classification = DATA_CLASSIFICATIONS.get(
                        mig_man_col.nemo_import_name, None
                    )
                    if data_classification:
                        description += f"\n\nData Classification: {data_classification}"

                    new_columns.append(
                        Column(
                            displayName=mig_man_col.nemo_display_name,
                            importName=mig_man_col.nemo_import_name,
                            internalName=mig_man_col.nemo_internal_name,
                            description=description,
                            dataType="string",
                            columnType="ExportedColumn",
                            dataClassificationInternalName=data_classification,
                            order=f"{mig_man_col.index:04d}",
                        )
                    )

                    self.logger.info(
                        f"Prepared column {mig_man_col.index:04d} '{column_name}' for NEMO project '{nemo_project_name}'"
                    )
            self.logger.info(
                f"Creating {len(new_columns)} columns in NEMO project {nemo_project_name}"
            )
            self.nl.createColumns(
                projectname=nemo_project_name,
                columns=new_columns,
            )

        if (
            not self.cfg.load.development_deficiency_mining_only
            and not self.cfg.load.development_load_reports_only
        ):
            self.logger.info(f"Loading data into {nemo_project_name}")

            self.local_database.upload_table_to_nemo(
                table_name=table_name,
                project_name=nemo_project_name,
                delete_temp_files=self.cfg.load.delete_temp_files,
            )

        if not self.cfg.load.development_load_reports_only:
            self._update_deficiency_mining(
                nemo_project_name=nemo_project_name,
                project_name=project,
                postfix=postfix,
                columns_in_file=columns,
            )

        if not self.cfg.load.development_deficiency_mining_only:
            self._load_reports(
                nemo_project_name=nemo_project_name,
                project_name=project,
                addon=addon,
                postfix=postfix,
            )

    def _update_deficiency_mining(
        self,
        nemo_project_name: str,
        project_name: str,
        postfix: str,
        columns_in_file: list[str],
    ) -> None:

        # create column specific fragments
        frags_checked = []
        frags_msg = []
        sorted_columns = []
        joins = {}
        migman_fields = [
            x
            for x in self.migman_database
            if x.project == project_name
            and x.postfix == postfix
            and x.nemo_import_name in columns_in_file
        ]
        for migman_field in migman_fields:

            frag_check = []
            frag_msg = []

            # global checks
            if migman_field.snow_mandatory:
                frag_check.append(
                    f"{migman_field.nemo_internal_name} IS NULL OR {migman_field.nemo_internal_name} = ''"
                )
                frag_msg.append(
                    f"{migman_field.nemo_display_name} is mandatory and must not be empty"
                )

            # data type specific checks
            match migman_field.desc_section_data_type.lower():
                case "character":
                    # Parse format to get maximum length
                    match = re.search(r"x\((\d+)\)", migman_field.desc_section_format)
                    field_length = (
                        int(match.group(1))
                        if match
                        else len(migman_field.desc_section_format)
                    )
                    frag_check.append(
                        f"LENGTH({migman_field.nemo_internal_name}) > {field_length}"
                    )
                    frag_msg.append(
                        f"{migman_field.nemo_display_name} exceeds field length (max {field_length} digits)"
                    )

                case "integer" | "decimal":
                    format_str = migman_field.desc_section_format
                    value = migman_field.nemo_internal_name

                    # STEP 1: Handle optional minus sign based on format
                    has_leading_minus = format_str.startswith("-")
                    has_trailing_minus = format_str.endswith("-")
                    minus_allowed = has_leading_minus or has_trailing_minus

                    if not minus_allowed:
                        frag_check.append(f"INSTR({value}, '-') > 0")
                        frag_msg.append(
                            f"{migman_field.nemo_display_name} must not contain a minus sign (expected format: {format_str})"
                        )
                    else:
                        if has_leading_minus:
                            frag_check.append(
                                f"(INSTR({value}, '-') > 0 AND LEFT({value}, 1) != '-')"
                            )
                            frag_msg.append(
                                f"{migman_field.nemo_display_name} must have minus sign only at the beginning if present (expected format: {format_str})"
                            )
                        elif has_trailing_minus:
                            frag_check.append(
                                f"(INSTR({value}, '-') > 0 AND RIGHT({value}, 1) != '-')"
                            )
                            frag_msg.append(
                                f"{migman_field.nemo_display_name} must have minus sign only at the end if present (expected format: {format_str})"
                            )

                    # Clean value for further analysis
                    value_stripped = f"REPLACE({value}, '-', '')"

                    # STEP 2: Check allowed number of decimal places
                    if "." in format_str:
                        decimals_allowed = sum(
                            1
                            for c in format_str.split(".")[1].lower()
                            if c in ("z", "9")
                        )
                    else:
                        decimals_allowed = 0

                    if decimals_allowed == 0:
                        frag_check.append(f"INSTR({value_stripped}, ',') > 0")
                        frag_msg.append(
                            f"{migman_field.nemo_display_name} must not contain decimal places (expected format: {format_str})"
                        )
                    else:
                        frag_check.append(
                            f"""LOCATE(',', {value_stripped}) > 0 AND 
                                LENGTH(RIGHT(
                                    {value_stripped},
                                    LENGTH({value_stripped}) - LOCATE(',', {value_stripped})
                                )) > {decimals_allowed}"""
                        )
                        frag_msg.append(
                            f"{migman_field.nemo_display_name} has too many decimal places (maximum {decimals_allowed} allowed; expected format: {format_str})"
                        )

                    # STEP 3: Check number of digits before the decimal comma (excluding thousands separators)
                    format_clean = format_str.replace("-", "")
                    integer_format_part = format_clean.split(".")[0]
                    digits_before_comma = sum(
                        1 for c in integer_format_part.lower() if c in ("z", "9")
                    )

                    cleaned = f"REPLACE(REPLACE(REPLACE({value_stripped}, ' ', ''), '.', ''), ',', '')"

                    frag_check.append(
                        f"""LENGTH(
                            CASE 
                                WHEN LOCATE(',', {value_stripped}) > 0 
                                THEN LEFT({cleaned}, LOCATE(',', {value_stripped}) - 1)
                                ELSE {cleaned}
                            END
                        ) > {digits_before_comma}"""
                    )
                    frag_msg.append(
                        f"{migman_field.nemo_display_name} has too many digits before the decimal point (maximum {digits_before_comma} allowed; expected format: {format_str})"
                    )

                    # STEP 4: Check if the value matches a valid German number format
                    # Format accepted: optional minus, digits with optional thousands separators (.), and optional decimal part (with comma)
                    frag_check.append(
                        f"""NOT REPLACE({value}, '-', '') 
                        LIKE_REGEXPR('^[-]?([[:digit:]]+|[[:digit:]]{{1,3}}(\\.[[:digit:]]{{3}})*)(,[[:digit:]]+)?$')"""
                    )
                    frag_msg.append(
                        f"{migman_field.nemo_display_name} is not a valid number (expected German format, e.g. 1.234,56; format: {format_str})"
                    )

                case "date":
                    pattern = (
                        "^(0[1-9]|[1-2][0-9]|3[0-1])\\.(0[1-9]|1[0-2])\\.([0-9]{4})$"
                    )

                    frag_check.append(
                        f"NOT {migman_field.nemo_internal_name} LIKE_REGEXPR('{pattern}')"
                    )
                    frag_msg.append(
                        f"{migman_field.nemo_display_name} is not a valid date"
                    )

            # special fields

            if "mail" in migman_field.nemo_internal_name:

                # this is the ABL Code that validates the email address
                # method public static logical lIsValidEMailAddress
                #     ( pcValue as character ):
                #     /* Description -----------------------------------------------------------*/
                #     /*                                                                        */
                #     /* returns yes in case of a valid e-mail address                          */
                #     /*                                                                        */
                #     /* Parameters ------------------------------------------------------------*/
                #     /*                                                                        */
                #     /* pcValue  e-mail address to be checked                                  */
                #     /*                                                                        */
                #     /*------------------------------------------------------------------------*/
                #
                #     return not (   index(pcValue, ' ':U)                     > 0
                #                 or index(pcValue, '[':U)                     > 0
                #                 or index(pcValue, ']':U)                     > 0
                #                 or index(pcValue, ',':U)                     > 0
                #                 or index(pcValue, ';':U)                     > 0
                #                 or index(pcValue, ':':U)                     > 0
                #                 or index(pcValue, '(':U)                     > 0
                #                 or index(pcValue, ')':U)                     > 0
                #                 or index(pcValue, {&PA-BACKSLASH})           > 0
                #                 or not pcValue                               matches '.*@*...':U
                #                 or num-entries(pcValue,'@':U)                <> 2
                #                 /*  chr(39) is '. This chr is not allowed in the domain part  */
                #                 or index(entry(2,pcValue,'@':U),chr(39))     > 0
                #                 or trim(pcValue,'.':U)                       <> pcValue
                #                 or num-entries(entry(2,pcValue,'@':U),'.':U) < 2
                #                 or index(pcValue,'..':U)                     > 0).
                #
                #   end method. /* lIsValidEMailAddress */

                # Check 1: Email address contains invalid characters (e.g. space, brackets, semicolon, colon, backslash, parentheses)
                # frag_check.append(
                #     f"{migman_field.nemo_internal_name} LIKE_REGEXPR '[ \\t\\n\\r\\[\\],;:\\\\()]'"
                # )
                # frag_msg.append(
                #     f"{migman_field.nemo_display_name} contains invalid characters (e.g., space, brackets, semicolon, colon)"
                # )

                # # Check 2: Email address contains consecutive dots
                # frag_check.append(
                #     f"{migman_field.nemo_internal_name} LIKE_REGEXPR '\\.\\.'"
                # )
                # frag_msg.append(
                #     f"{migman_field.nemo_display_name} contains consecutive dots"
                # )

                # # Check 3: Email address starts with a dot
                # frag_check.append(f"{migman_field.nemo_internal_name} LIKE '.%'")
                # frag_msg.append(f"{migman_field.nemo_display_name} starts with a dot")

                # # Check 4: Email address ends with a dot
                # frag_check.append(f"{migman_field.nemo_internal_name} LIKE '%.'")
                # frag_msg.append(f"{migman_field.nemo_display_name} ends with a dot")

                # # Check 5: Email address must contain exactly one '@' character
                # frag_check.append(
                #     f"LENGTH({migman_field.nemo_internal_name}) - LENGTH(REPLACE({migman_field.nemo_internal_name}, '@', '')) <> 1"
                # )
                # frag_msg.append(
                #     f"{migman_field.nemo_display_name} must contain exactly one @"
                # )

                # # Check 6: Email domain must contain at least one dot
                # frag_check.append(
                #     f"INSTR(SUBSTRING({migman_field.nemo_internal_name}, INSTR({migman_field.nemo_internal_name}, '@') + 1), '.') = 0"
                # )
                # frag_msg.append(
                #     f"{migman_field.nemo_display_name} domain must contain at least one dot"
                # )

                # Optional Check 7: General pattern check for basic email format
                frag_check.append(
                    f"NOT {migman_field.nemo_internal_name} LIKE_REGEXPR '^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$'"
                )
                frag_msg.append(
                    f"{migman_field.nemo_display_name} does not match the general email format"
                )

            # VAT_ID
            if "s_ustid_ustid" in migman_field.nemo_internal_name:
                joins[migman_field.nemo_internal_name] = {"CLASSIFICATION": "VAT_ID"}
                frag_check.append(
                    f"(genius_{migman_field.nemo_internal_name}.STATUS IS NOT NULL AND genius_{migman_field.nemo_internal_name}.STATUS = 'check')"
                )
                frag_msg.append(
                    f"genius analysis: ' || genius_{migman_field.nemo_internal_name}.STATUS_MESSAGE || '"
                )

            # URL
            elif "s_adresse_homepage" in migman_field.nemo_internal_name:
                joins[migman_field.nemo_internal_name] = {"CLASSIFICATION": "URL"}
                frag_check.append(
                    f"(genius_{migman_field.nemo_internal_name}.STATUS IS NOT NULL AND genius_{migman_field.nemo_internal_name}.STATUS = 'check')"
                )
                frag_msg.append(
                    f"genius analysis: ' || genius_{migman_field.nemo_internal_name}.STATUS_MESSAGE || '"
                )

            # now build deficiency mining report for this column (if there are checks)
            if frag_check:

                # save checks and messages for total report
                frags_checked.extend(frag_check)
                frags_msg.extend(frag_msg)
                sorted_columns = [
                    f'{migman_field.nemo_internal_name} AS "{migman_field.nemo_display_name}"'
                ] + [
                    f'{other_field.nemo_internal_name} AS "{other_field.nemo_display_name}"'
                    for other_field in self.migman_database
                    if other_field.project == project_name
                    and other_field.postfix == postfix
                    and other_field.index != migman_field.index
                    and other_field.nemo_import_name in columns_in_file
                ]

                # case statements for messages and dm report
                case_statement_specific = " ||\n\t".join(
                    [
                        f"CASE\n\t\tWHEN {check}\n\t\tTHEN CHAR(10) || '{msg}'\n\t\tELSE ''\n\tEND"
                        for check, msg in zip(frag_check, frag_msg)
                    ]
                )

                status_conditions = " OR ".join(frag_check)

                sql_statement = f"""SELECT
\tCASE 
\t\tWHEN {status_conditions} THEN 'check'
\tELSE 'ok'
\tEND AS STATUS
\t,LTRIM({case_statement_specific},CHAR(10)) AS DEFICIENCY_MINING_MESSAGE
\t,{',\n\t'.join(sorted_columns)}
FROM
\t$schema.$table
"""
            if migman_field.nemo_internal_name in joins:
                sql_statement += f"""LEFT JOIN
\t$schema.SHARED_NAIGENT genius_{migman_field.nemo_internal_name}
ON  
\t    genius_{migman_field.nemo_internal_name}.CLASSIFICATION = '{joins[migman_field.nemo_internal_name]["CLASSIFICATION"]}'
\tAND genius_{migman_field.nemo_internal_name}.VALUE          = {migman_field.nemo_internal_name}
"""

            # create the report
            report_display_name = f"(DEFICIENCIES) {migman_field.index:03} {migman_field.nemo_display_name}"
            report_internal_name = get_internal_name(report_display_name)

            self.nl.createReports(
                projectname=nemo_project_name,
                reports=[
                    Report(
                        displayName=report_display_name,
                        internalName=report_internal_name,
                        querySyntax=sql_statement,
                        description=f"Deficiency Mining Report for column '{migman_field.nemo_display_name}' in project '{project_name}'",
                    )
                ],
            )

            self.nl.createRules(
                projectname=nemo_project_name,
                rules=[
                    Rule(
                        displayName=f"DM_{migman_field.index:03}: {migman_field.nemo_display_name}",
                        ruleSourceInternalName=report_internal_name,
                        ruleGroup="02 Columns",
                        description=f"Deficiency Mining Rule for column '{migman_field.nemo_display_name}' in project '{project_name}'",
                    )
                ],
            )

            self.logger.info(
                f"project: {project_name}, column: {migman_field.nemo_display_name}: {len(frag_check)} frags added"
            )

        # now setup global dm report and rule
        case_statement_specific, status_conditions = self._create_dm_rule_global(
            nemo_project_name=nemo_project_name,
            project_name=project_name,
            postfix=postfix,
            columns_in_file=columns_in_file,
            frags_checked=frags_checked,
            frags_msg=frags_msg,
            sorted_columns=sorted_columns,
            joins=joins,
        )

        # create report for mig man
        self._create_report_for_migman(
            nemo_project_name=nemo_project_name,
            project_name=project_name,
            postfix=postfix,
            columns_in_file=columns_in_file,
            case_statement_specific=case_statement_specific,
            status_conditions=status_conditions,
            joins=joins,
        )

        # create report for the customer containing all errors
        self._create_report_for_customer(
            nemo_project_name=nemo_project_name,
            project_name=project_name,
            postfix=postfix,
            columns_in_file=columns_in_file,
            case_statement_specific=case_statement_specific,
            status_conditions=status_conditions,
            joins=joins,
        )

        self.logger.info(
            f"Project {project_name}: {len(frags_checked)} checks implemented..."
        )

    def _create_dm_rule_global(
        self,
        nemo_project_name: str,
        project_name: str,
        postfix: str,
        columns_in_file: list[str],
        frags_checked: list[str],
        frags_msg: list[str],
        sorted_columns: list[str],
        joins: dict[str, dict[str, str]],
    ) -> (str, str):  # type: ignore
        """
        Creates a global deficiency mining rule and report for a project.

        Args:
            config (Config): Configuration object.
            project_name (str): Name of the project.
            postfix (str): Postfix for the project.
            columns_in_file (list[str]): List of columns in the data file.
            database (list[MigMan]): List of MigMan database entries.
            frags_checked (list[str]): List of condition fragments for checks.
            frags_msg (list[str]): List of messages corresponding to checks.
            sorted_columns (list[str]): List of sorted columns for the report.
            joins (dict[str, dict[str, str]]): Join conditions for the report.

        Returns:
            tuple: Case statement and status conditions for the global rule.
        """
        # case statements for messages and dm report
        case_statement_specific = " ||\n\t".join(
            [
                f"CASE\n\t\tWHEN {check}\n\t\tTHEN  CHAR(10) || '{msg}'\n\t\tELSE ''\n\tEND"
                for check, msg in zip(frags_checked, frags_msg)
            ]
        )

        status_conditions = " OR ".join(frags_checked)

        sql_statement = f"""WITH CTEDefMining AS (
SELECT
\t\t{',\n\t\t'.join([x.nemo_internal_name for x in self.migman_database if x.project == project_name and x.postfix == postfix and x.nemo_display_name in columns_in_file])}
    ,LTRIM({case_statement_specific},CHAR(10)) AS DEFICIENCY_MINING_MESSAGE
    ,CASE 
        WHEN {status_conditions} THEN 'check'
        ELSE 'ok'
    END AS STATUS
FROM
    $schema.$table"""

        for join in joins:
            sql_statement += f"""
LEFT JOIN
\t$schema.SHARED_NAIGENT genius_{join}
ON  
\t    genius_{join}.CLASSIFICATION = '{joins[join]["CLASSIFICATION"]}'
\tAND genius_{join}.VALUE          = {join}"""

        sql_statement += f"""       
)
SELECT
    Status
    , DEFICIENCY_MINING_MESSAGE
    , {',\n\t'.join(sorted_columns)}
FROM 
    CTEDefMining"""

        # create the report
        report_display_name = f"(DEFICIENCIES) GLOBAL"
        report_internal_name = get_internal_name(report_display_name)

        self.nl.createReports(
            projectname=nemo_project_name,
            reports=[
                Report(
                    displayName=report_display_name,
                    internalName=report_internal_name,
                    querySyntax=sql_statement,
                    description=f"Deficiency Mining Report for  project '{project_name}'",
                )
            ],
        )

        self.nl.createRules(
            projectname=nemo_project_name,
            rules=[
                Rule(
                    displayName="Global",
                    ruleSourceInternalName=report_internal_name,
                    ruleGroup="01 Global",
                    description=f"Deficiency Mining Rule for project '{project_name}'",
                )
            ],
        )

        self.logger.info(
            f"nemo project: {nemo_project_name}, global rule created with {len(frags_checked)} checks"
        )
        return case_statement_specific, status_conditions

    def _create_report_for_migman(
        self,
        nemo_project_name: str,
        project_name: str,
        postfix: str,
        columns_in_file: list[str],
        case_statement_specific: str,
        status_conditions: str,
        joins: dict[str, dict[str, str]],
    ) -> None:
        """
        Creates a report for MigMan containing valid data.

        Args:
            config (Config): Configuration object.
            project_name (str): Name of the project.
            postfix (str): Postfix for the project.
            columns_in_file (list[str]): List of columns in the data file.
            database (list[MigMan]): List of MigMan database entries.
            case_statement_specific (str): Case statement for deficiency messages.
            status_conditions (str): Conditions for status checks.
            joins (dict[str, dict[str, str]]): Join conditions for the report.
        """
        sql_statement = f"""WITH CTEDefMining AS (
    SELECT
        {',\n\t\t'.join([x.nemo_internal_name for x in self.migman_database if x.project == project_name and x.postfix == postfix and x.nemo_display_name in columns_in_file])}
        ,LTRIM({case_statement_specific},CHAR(10)) AS DEFICIENCY_MINING_MESSAGE
        ,CASE 
            WHEN {status_conditions} THEN 'check'
            ELSE 'ok'
        END AS STATUS
    FROM
        $schema.$table"""

        for join in joins:
            sql_statement += f"""
LEFT JOIN
\t$schema.SHARED_NAIGENT genius_{join}
ON  
\t    genius_{join}.CLASSIFICATION = '{joins[join]["CLASSIFICATION"]}'
\tAND genius_{join}.VALUE          = {join}"""

        sql_statement += f"""       
)
SELECT
    {',\n\t'.join([f"{x.nemo_internal_name} as \"{x.header_section_label}\"" for x in self.migman_database if x.project == project_name and x.postfix == postfix and x.nemo_display_name in columns_in_file])}
FROM 
    CTEDefMining
WHERE
    STATUS = 'ok'
    """

        # create the report
        report_display_name = f"(MigMan) All records with no message"
        report_internal_name = get_internal_name(report_display_name)

        self.nl.createReports(
            projectname=nemo_project_name,
            reports=[
                Report(
                    displayName=report_display_name,
                    internalName=report_internal_name,
                    querySyntax=sql_statement,
                    description=f"MigMan export with valid data for project '{project_name}'",
                )
            ],
        )

        self.logger.info(f"Created MigMan report for project '{nemo_project_name}'")

    def _create_report_for_customer(
        self,
        nemo_project_name: str,
        project_name: str,
        postfix: str,
        columns_in_file: list[str],
        case_statement_specific: str,
        status_conditions: str,
        joins: dict[str, dict[str, str]],
    ) -> None:
        """
        Creates a report for customers containing invalid data.

        Args:
            config (Config): Configuration object.
            project_name (str): Name of the project.
            postfix (str): Postfix for the project.
            columns_in_file (list[str]): List of columns in the data file.
            database (list[MigMan]): List of MigMan database entries.
            case_statement_specific (str): Case statement for deficiency messages.
            status_conditions (str): Conditions for status checks.
            joins (dict[str, dict[str, str]]): Join conditions for the report.
        """
        sql_statement = f"""WITH CTEDefMining AS (
SELECT
    {',\n\t\t'.join([x.nemo_internal_name for x in self.migman_database if x.project == project_name and x.postfix == postfix and x.nemo_display_name in columns_in_file])}
    ,LTRIM({case_statement_specific},CHAR(10)) AS DEFICIENCY_MINING_MESSAGE
    ,CASE 
        WHEN {status_conditions} THEN 'check'
        ELSE 'ok'
    END AS STATUS
FROM
    $schema.$table"""

        for join in joins:
            sql_statement += f"""
LEFT JOIN
\t$schema.SHARED_NAIGENT genius_{join}
ON  
\t    genius_{join}.CLASSIFICATION = '{joins[join]["CLASSIFICATION"]}'
\tAND genius_{join}.VALUE          = {join}"""

        sql_statement += f"""       
)
SELECT
    DEFICIENCY_MINING_MESSAGE,
    {',\n\t'.join([f"{x.nemo_internal_name} as \"{x.header_section_label}\"" for x in self.migman_database if x.project == project_name and x.postfix == postfix and x.nemo_display_name in columns_in_file])}
FROM 
    CTEDefMining
WHERE
    STATUS <> 'ok'
"""

        # create the report
        report_display_name = f"(Customer) All records with message"
        report_internal_name = get_internal_name(report_display_name)

        self.nl.createReports(
            projectname=nemo_project_name,
            reports=[
                Report(
                    displayName=report_display_name,
                    internalName=report_internal_name,
                    querySyntax=sql_statement,
                    description=f"export invalid data for project '{project_name}'",
                )
            ],
        )
        self.logger.info(f"Created Customer report for project '{nemo_project_name}'")

    def _load_reports(
        self,
        nemo_project_name: str,
        project_name: str,
        addon: str,
        postfix: str,
    ) -> None:
        """
        Loads reports into NEMO based on the configuration.
        """
        self.logger.info(f"Loading reports from {nemo_project_name}")

        data = [
            ("to_customer", "_with_messages", "(Customer) All records with message"),
            ("to_proalpha", "", "(MigMan) All records with no message"),
        ]

        report_folder = Path(self.cfg.etl_directory) / "reports"
        for folder, file_postfix, report_name in data:

            logging.info(
                f"Exporting '{project_name}', addon '{addon}', postfix '{postfix}', report name: '{report_name}' to '{folder}'"
            )
            file_name = report_folder / folder / f"{project_name}{file_postfix}.csv"
            file_name.parent.mkdir(parents=True, exist_ok=True)
            df = self.nl.LoadReport(
                projectname=nemo_project_name,
                report_name=report_name,
                data_types=str,
            )
            df.to_csv(
                file_name,
                index=False,
                sep=";",
                encoding="utf-8-sig",
            )

            logging.info(
                f"File '{file_name}' for '{project_name}', addon '{addon}', postfix '{postfix}' exported '{report_name}'"
            )
