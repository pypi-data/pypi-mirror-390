from dataclasses import dataclass
from typing import Any, TypeVar, Generic, Type

T = TypeVar("T")

@dataclass
class ETLArg(Generic[T]):
    name: str
    type: Type[T]
    required: bool = False
    default: T | None = None
    help: str | None = None


def parse_startup_args(additional_args: list[ETLArg] | None = None) -> dict[str, Any]:
    """Parse command line arguments for the ETL process.

    Returns:
        dict[str, str]: Parsed command line arguments.
    """
    import argparse

    parser = argparse.ArgumentParser(description="ETL Process Arguments")
    
    standard_args = [
        ETLArg(
            name="config_ini",
            type=str,
            required=False,
            default="./config.ini",
            help="Path to the configuration file.",
        ),
        ETLArg(
            name="config_json",
            type=str,
            required=False,
            default=None,       
            help="Path to the JSON configuration file.",
        ),
        ETLArg(
            name="environment",
            type=str,   
            required=False,
            default=None,
            help="Environment setting for the ETL process.",
        ),
        ETLArg(
            name="tenant",
            type=str,
            required=False,
            default=None,
            help="Tenant identifier for the ETL process.",
        ),
        ETLArg(
            name="userid",
            type=str,
            required=False,
            default=None,
            help="User ID for authentication.",
        ),
        ETLArg(
            name="password",
            type=str,
            required=False,
            default=None,
            help="Password for authentication.",
        ),
    ]

    for arg in standard_args + (additional_args if additional_args else []):
        if arg.type == bool:
            parser.add_argument(
                f"--{arg.name}",
                action=argparse.BooleanOptionalAction,
                default=arg.default,
                help=arg.help,
            )
        else:   
            parser.add_argument(
                f"--{arg.name}",
                type=arg.type,
                required=arg.required,
                default=arg.default,
                help=arg.help,
            )

    args = parser.parse_args()
    return vars(args)

