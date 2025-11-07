"""Tools to standardize writing and reading data."""

import csv
import json
from enum import Enum
from pathlib import Path
from typing import Any


class InvalidJSONFileTypeError(ValueError):
    """Exceptions class for invalid JSON file type."""

    def __init__(
        self, expected: JSONTypes, actual: JSONTypes, reason: str | None = None
    ) -> None:
        msg = f"Expected JSON file type '{expected.value}', but got '{actual.value}'."
        if reason:
            msg += f" Reason: {reason}"
        super().__init__(msg)


class JSONTypes(Enum):

    NOT_SPECIFIED = "type-not-specified"
    RENAMING_MAPPING = "vidmux-renaming-mapping"
    SCAN_REPORT = "vidmux-scan-report"


class JSONFile:

    def __init__(
        self,
        associated_path: Path | str,
        content: Any,
        file_type: JSONTypes = JSONTypes.NOT_SPECIFIED,
        version: str = "1.0",
        description: str | None = None,
    ) -> None:
        self.associated_path = Path(associated_path)
        self.content = content
        self.file_type = file_type
        self.version = version
        self.description = description

    def as_dict(self) -> dict:
        """Return a dictionary representation of the instance."""
        return {
            "_type": self.file_type.value,
            "_version": self.version,
            "_description": self.description,
            "associated_path": str(self.associated_path),
            "content": self.content,
        }

    @classmethod
    def from_dict(
        cls,
        dictionary: dict,
        ensure_type: JSONTypes | None = None,
        type_reason: str | None = None,
    ) -> "JSONFile":
        """Return an instance with the data from 'dictionary'."""
        # Load the file type
        _type_raw = dictionary.get("_type", JSONTypes.NOT_SPECIFIED.value)
        try:
            file_type = JSONTypes(_type_raw)
        except ValueError:
            raise ValueError(
                f"Invalid '_type': '{_type_raw}'. "
                f"Must be one of: {[valid_type.value for valid_type in JSONTypes]}"
            )

        # If ensure type is specified, check if the file type is correct
        if ensure_type is not None and file_type != ensure_type:
            raise InvalidJSONFileTypeError(ensure_type, file_type, reason=type_reason)

        # Ensure that associated_path and content are given
        try:
            associated_path = dictionary["associated_path"]
            content = dictionary["content"]
        except KeyError as err:
            raise ValueError(f"Missing required field in JSON: {err.args[0]}")

        # Create and return the class instance
        return cls(
            associated_path=associated_path,
            content=content,
            file_type=file_type,
            version=dictionary.get("_version", "1.0"),
            description=dictionary.get("_description"),
        )

    def save(
        self,
        filepath: Path | str,
        encoding="utf-8",
        indent: int = 2,
        ensure_ascii: bool = False,
    ) -> None:
        """Save content to a JSON file."""
        with open(filepath, "w", encoding=encoding) as file:
            json.dump(self.as_dict(), file, indent=indent, ensure_ascii=ensure_ascii)

    @classmethod
    def load(
        cls,
        filepath: Path | str,
        encoding="utf-8",
        ensure_type: JSONTypes | None = None,
        type_reason: str | None = None,
    ) -> "JSONFile":
        """Load a JSON file and an instance of JSONFile with the content."""
        with open(filepath, "r", encoding=encoding) as file:
            content = json.load(file)

        return cls.from_dict(content, ensure_type=ensure_type, type_reason=type_reason)
