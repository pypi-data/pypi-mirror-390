import argparse
import locale
import logging
import logging.config
import os
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from unistrant.command import BaseCommand, RegisterCommand
from unistrant.error import UnistrantError
from unistrant.options import CommandName, Options
from unistrant.settings import find_settings, load_settings

logger = logging.getLogger(__name__)


def configure_logging(logging_config: Mapping[str, Any], log_level: str) -> None:
    if logging_config:
        logging.config.dictConfig(dict(logging_config))
    else:
        logging.basicConfig(format="%(message)s")
    if log_level:
        logging.getLogger().setLevel(log_level)


def check_directory(directory: Path) -> None:
    if not directory.exists():
        raise UnistrantError(f"{directory} does not exist")
    if not directory.is_dir():
        raise UnistrantError(f"{directory} is not a directory")


def command_line_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="unistrant", description="This program is a client for the SAMS accounting service.")
    log_levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    parser.add_argument("--archive-directory-name", help="name of archive subdirectory")
    parser.add_argument("--data-directory", type=Path, help="path to data directory")
    parser.add_argument("--log-level", choices=log_levels, type=str.upper, help="override log level")
    parser.add_argument("--records-directory-name", help="name of records subdirectory")
    parser.add_argument("--sams-certificate", type=Path, help="path to client certificate")
    parser.add_argument("--sams-key", type=Path, help="path to client certificate key")
    parser.add_argument("--sams-url", help="accounting service URL")
    parser.add_argument("--settings", type=Path, help="path to settings file")
    parser.add_argument(
        "--use-environment",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="use environment variables (default --use-environment)",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="command", required=True)
    subparsers.add_parser(
        CommandName.Register,
        help="submit records to accounting service",
        description="Use this command to submit record files to the accounting service.",
    )

    return parser


def initialize() -> Options:
    locale.setlocale(locale.LC_ALL, "")

    parser = command_line_parser()
    command_line = parser.parse_args()

    def environment(*key: str) -> str | None:
        if not command_line.use_environment:
            return None

        key_environment = f"UNISTRANT_{'_'.join(key)}".upper()
        return os.getenv(key_environment)

    if settings_environment := environment("settings"):
        settings_override_path = Path(settings_environment)
    else:
        settings_override_path = command_line.settings

    settings_path = find_settings(settings_override_path)
    settings = load_settings(settings_path)

    def option(*key: str, default: Any | None = None, optional: bool = False) -> Any:
        if value := environment(*key):
            return value

        key_command_line = "_".join(key)
        try:
            if value := getattr(command_line, key_command_line):
                return value
        except AttributeError:
            pass

        key_setting = ".".join(key)
        try:
            if value := settings[key_setting]:
                return value
        except KeyError:
            pass

        if optional or default is not None:
            return default

        raise UnistrantError(f"Missing required setting {key_setting}")

    options = Options(
        archive_directory_name=option("archive_directory_name", default="archive"),
        command=CommandName(command_line.command),
        data_directory=option("data_directory"),
        log_level=option("log_level", optional=True),
        records_directory_name=option("records_directory_name", default="records"),
        sams_certificate=option("sams", "certificate"),
        sams_key=option("sams", "key"),
        sams_url=option("sams", "url", default="https://accounting.naiss.se:6143/sgas"),
        settings_path=settings_path,
        settings=settings,
    )

    return options


def _main() -> None:
    options = initialize()

    configure_logging(options.settings.logging, options.log_level)

    check_directory(options.archive_directory)
    check_directory(options.records_directory)

    command: BaseCommand
    match options.command:
        case CommandName.Register:
            command = RegisterCommand(options)

    try:
        command.run()
    finally:
        if command.error:
            raise UnistrantError("Command failed with errors")


def main() -> None:
    try:
        _main()
    except KeyboardInterrupt:
        sys.exit(1)
    except UnistrantError as e:
        logger.error(str(e))
        sys.exit(1)
