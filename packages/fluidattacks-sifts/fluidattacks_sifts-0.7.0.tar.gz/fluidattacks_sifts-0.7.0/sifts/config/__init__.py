import json
import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from sifts.io.db.base import DatabaseBackend
from sifts.io.db.factory import create_database_backend


class LinesConfig(BaseModel):
    file: Path
    lines: list[int]

    @field_validator("file", mode="before")
    @classmethod
    def convert_file_to_path(cls, value: str | Path) -> Path:
        value = str(value).strip()
        if isinstance(value, str) and value.startswith("/") and not Path(value).exists():
            value = value.lstrip("/")
        """Convert file to a Path object if it's a string."""
        return Path(value)


class SiftsConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Analysis configuration fields
    include_files: list[str] = Field(default_factory=list, alias="include_files")
    exclude_files: list[str] = Field(default_factory=list, alias="exclude_files")
    lines_to_check: list[LinesConfig] = Field(default_factory=list, alias="lines_to_check")
    include_vulnerabilities_subcategories: list[str] = Field(
        default_factory=list, alias="include_vulnerabilities_subcategories"
    )
    exclude_vulnerabilities_subcategories: list[str] = Field(
        default_factory=list, alias="exclude_vulnerabilities_subcategories"
    )
    root_dir: Path = Field(
        default=Path("."),  # noqa: PTH201
        description="Directory to work in",
        alias="root_dir",
    )
    split_subdirectories: bool = Field(
        default=True,
        description=(
            "The project may contain multiple subjects, determining whether it"
            " should be analyzed in a different process."
        ),
        alias="split_subdirectories",
    )
    use_default_exclude_files: bool = Field(
        default=True,
        description="Use default exclude files",
        alias="use_default_exclude_files",
    )
    use_default_vulnerabilities_exclude: bool = Field(
        default=True,
        description="Use default vulnerabilities exclude",
        alias="use_default_vulnerabilities_exclude",
    )
    strict_mode: bool = Field(
        default=True,
        description="Use strict mode (overridable via the SIFTS_STRICT_MODE environment variable)",
        alias="SIFTS_STRICT_MODE",
    )
    enable_navigation: bool = Field(
        default=False,
        description=(
            "Enable navigation (overridable via the SIFTS_ENABLE_NAVIGATION environment variable)"
        ),
        alias="SIFTS_ENABLE_NAVIGATION",
    )
    model: str = Field(
        default="o4-mini",
        description="Model to use (overridable via the SIFTS_MODEL environment variable)",
        alias="SIFTS_MODEL",
    )

    # Output configuration fields
    output_format: str = Field(default="json", alias="SIFTS_OUTPUT_FORMAT")
    output_path: Path = Field(default=Path("output.json"), alias="SIFTS_OUTPUT_PATH")

    # Runtime configuration fields
    parallel: bool = Field(default=False, alias="SIFTS_PARALLEL")
    threads: int = Field(default=1, alias="SIFTS_THREADS")

    # Context configuration fields
    group_name: str | None = Field(default=None, description="Group name", alias="SIFTS_GROUP_NAME")
    root_nickname: str | None = Field(
        default=None, description="Root nickname", alias="SIFTS_ROOT_NICKNAME"
    )

    # Database configuration fields
    database_backend: str = Field(
        default="dynamodb", pattern="^(dynamodb|sqlite)$", alias="SIFTS_DATABASE_BACKEND"
    )
    sqlite_database_path: str | Path = Field(default="sifts.db", alias="SIFTS_SQLITE_DATABASE_PATH")

    # Database instance (not serialized)
    database_instance: Any = Field(default=None, exclude=True)

    @field_validator("root_dir", "output_path", "sqlite_database_path", mode="before")
    @classmethod
    def convert_to_path(cls, value: str | Path) -> Path:
        """Convert string paths to Path objects."""
        return Path(value)

    @field_validator(
        "strict_mode",
        "enable_navigation",
        "split_subdirectories",
        "use_default_exclude_files",
        "use_default_vulnerabilities_exclude",
        "parallel",
        mode="before",
    )
    @classmethod
    def convert_string_to_bool(cls, value: str | bool) -> bool:  # noqa: FBT001
        """Convert string environment variables to boolean."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in {"1", "true", "yes", "y"}
        return bool(value)

    @field_validator(
        "include_vulnerabilities_subcategories",
        "exclude_vulnerabilities_subcategories",
        "include_files",
        "exclude_files",
        mode="before",
    )
    @classmethod
    def parse_list_from_json(cls, value: list[str] | str) -> list[str]:
        """Parse JSON string environment variables to list[str]."""
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            if value.strip():
                try:
                    parsed = json.loads(value)
                except json.JSONDecodeError:
                    # If JSON parsing fails, treat as comma-separated list
                    return [item.strip() for item in value.split(",") if item.strip()]
                else:
                    if isinstance(parsed, list):
                        return parsed
                    return [parsed] if parsed else []
            return []
        return []

    @field_validator("root_dir")
    @classmethod
    def validate_root_dir(cls, value: Path) -> Path:
        """Validate that the root directory exists."""
        if not value.exists():
            msg = f"Root directory does not exist: {value}"
            raise ValueError(msg)
        if not value.is_dir():
            msg = f"Root directory is not a directory: {value}"
            raise ValueError(msg)
        return value

    @field_validator("output_path")
    @classmethod
    def validate_output_path(cls, value: Path) -> Path:
        """Validate and prepare the output path directory."""
        # For output paths, we attempt to create the directory
        if not value.parent.exists():
            try:
                value.parent.mkdir(parents=True, exist_ok=True)
            except (PermissionError, OSError) as e:
                msg = f"Cannot create output directory: {value.parent}: {e!s}"
                raise ValueError(msg) from e

        # Check if we can write to the directory
        if not os.access(value.parent, os.W_OK):
            msg = f"No write permission for output directory: {value.parent}"
            raise ValueError(msg)

        return value

    @model_validator(mode="after")
    def merge_lines_for_same_files(self) -> "SiftsConfig":
        """Merge lines_to_check entries that reference the same file path."""
        if not self.lines_to_check:
            return self

        # Dictionary to store merged lines by file path
        merged_lines_by_path: dict[Path, list[int]] = {}

        # Collect all lines by file path
        for line_config in self.lines_to_check:
            # Normalize the path for consistent comparison
            file_path = line_config.file
            if file_path not in merged_lines_by_path:
                merged_lines_by_path[file_path] = []

            # Add lines to the merged list, avoiding duplicates
            for line in line_config.lines:
                if line not in merged_lines_by_path[file_path]:
                    merged_lines_by_path[file_path].append(line)

        # Sort line numbers for deterministic output
        for path, lines in merged_lines_by_path.items():
            merged_lines_by_path[path] = sorted(lines)

        # Create new merged lines_to_check list
        merged_configs: list[LinesConfig] = []
        for file_path, lines in merged_lines_by_path.items():
            merged_configs.append(LinesConfig(file=file_path, lines=lines))

        # Replace the original list with the merged list
        self.lines_to_check = merged_configs
        return self

    @model_validator(mode="after")
    def validate_file_paths(self) -> "SiftsConfig":
        """Validate that files referenced for analysis exist."""
        # Validate all paths in lines_to_check
        for line_config in self.lines_to_check:
            file_path = line_config.file
            # Check if file exists as absolute path
            if not file_path.exists():
                # Check if file exists relative to root_dir
                root_dir_path = Path(self.root_dir, file_path)
                if not root_dir_path.exists():
                    msg = f"File specified in lines_to_check does not exist: {file_path}"
                    raise ValueError(
                        msg,
                    )

        # Validate non-glob patterns in include_files
        for include_pattern in self.include_files:
            # Only validate exact file references (not glob patterns)
            if (
                "*" not in include_pattern
                and "?" not in include_pattern
                and (file_path := Path(include_pattern))
            ) and not file_path.exists():
                # Check if file exists relative to root_dir
                root_dir_path = self.root_dir / file_path
                if not root_dir_path.exists():
                    msg = f"File specified in include_files does not exist: {file_path}"
                    raise ValueError(msg)

        return self

    def get_database(self) -> DatabaseBackend:
        """Get the database instance, creating it if necessary."""
        if self.database_instance is None:
            self.database_instance = create_database_backend(
                backend_type=self.database_backend,
                # SQLite configuration
                database_path=self.sqlite_database_path,
            )
        return self.database_instance  # type: ignore[no-any-return]

    def set_database(self, database_instance: Any) -> None:  # noqa: ANN401
        """Set the database instance."""
        self.database_instance = database_instance

    @classmethod
    def create_with_overrides(cls, **overrides: Any) -> "SiftsConfig":  # noqa: ANN401
        """Create a config instance with specific overrides, bypassing environment variables."""
        # Create a base instance to get defaults
        base_instance = cls()

        # Update with overrides
        data = base_instance.model_dump()
        data.update(overrides)

        # Create new instance by directly setting attributes
        instance = cls()
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        return instance

    @classmethod
    def from_yaml(cls, config_path: str | Path) -> "SiftsConfig":  # noqa: C901
        """Load configuration from a YAML file."""
        path = Path(config_path) if isinstance(config_path, str) else config_path
        if not path.exists():
            msg = f"Config file not found: {path}"
            raise FileNotFoundError(msg)

        with path.open() as file:
            config_data = yaml.safe_load(file)

        # Flatten the nested structure to match our flat field structure
        flattened_data = {}

        # Handle analysis section
        if "analysis" in config_data:
            analysis_data = config_data["analysis"]
            flattened_data.update(analysis_data)

        # Handle output section
        if "output" in config_data:
            output_data = config_data["output"]
            for key, value in output_data.items():
                if key == "format":
                    flattened_data["output_format"] = value
                elif key == "path":
                    flattened_data["output_path"] = value

        # Handle runtime section
        if "runtime" in config_data:
            runtime_data = config_data["runtime"]
            flattened_data.update(runtime_data)

        # Handle context section
        if "context" in config_data:
            context_data = config_data["context"]
            flattened_data.update(context_data)

        # Handle database section
        if "database" in config_data:
            database_data = config_data["database"]
            for key, value in database_data.items():
                if key == "backend":
                    flattened_data["database_backend"] = value
                elif key == "sqlite_database_path":
                    flattened_data["sqlite_database_path"] = value

        # Create the config instance with flattened data
        # Use model_validate to ensure the data is properly validated
        # and then create a new instance to ensure environment variables are loaded
        instance = cls.model_validate(flattened_data)
        # Create a new instance to ensure environment variables are properly loaded
        return cls(**instance.model_dump())
