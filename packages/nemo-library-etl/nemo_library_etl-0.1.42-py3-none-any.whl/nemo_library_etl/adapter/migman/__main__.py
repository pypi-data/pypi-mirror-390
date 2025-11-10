"""
MigMan ETL Adapter Main Entry Point.

This module serves as the main entry point for the MigMan ETL adapter, which handles
the extraction, transformation, and loading of data from MigMan systems into Nemo.
"""


def main() -> None:
    """
    Main function to execute the MigMan ETL flow.

    This function initiates the complete MigMan ETL process by calling the MigMan_flow
    function, which orchestrates the extract, transform, and load operations.
    """

    from nemo_library_etl.adapter._utils.argparse import ETLArg, parse_startup_args

    myargs = [
        ETLArg(
            name="ui_config_mode",
            type=bool,
            required=False,
            default=False,
            help="Enable UI configuration mode.",
        )
    ]
    args = parse_startup_args(myargs)

    if args["ui_config_mode"] != True:
        print("UI configuration mode disabled. Running ETL flow.")
        from nemo_library_etl.adapter.migman.flow import migman_flow

        migman_flow(args)
    else:
        print("UI configuration mode enabled. Launching MigMan Config UI.")
        from nemo_library_etl.adapter.migman.ui import MigManUI

        mmui = MigManUI()
        mmui.run_ui(open_browser=True)


if __name__ == "__main__":
    main()
