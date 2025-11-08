import enum
from dataclasses import dataclass
from pathlib import Path

from unistrant.settings import Settings


class CommandName(enum.StrEnum):
    Register = "register"


@dataclass(frozen=True, kw_only=True)
class Options:
    archive_directory_name: str
    command: CommandName
    data_directory: Path
    log_level: str
    records_directory_name: str
    sams_certificate: Path
    sams_key: Path
    sams_url: str
    settings_path: Path | None
    settings: Settings

    @property
    def archive_directory(self) -> Path:
        return self.data_directory / self.archive_directory_name

    @property
    def records_directory(self) -> Path:
        return self.data_directory / self.records_directory_name
