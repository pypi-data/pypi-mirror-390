"""Provide tests for the filesystem operations."""

import json
from enum import Enum
from pathlib import Path

import pytest

from vidmux.filesystem import InvalidJSONFileTypeError, JSONFile, JSONTypes


# Example data
EXAMPLE_DICT = {
    "_type": "vidmux-scan-report",
    "_version": "1.2",
    "associated_path": "/some/path",
    "content": {"foo": "bar"},
    "_description": "Test file",
}


@pytest.fixture
def jsonfile_instance() -> JSONFile:
    return JSONFile(
        associated_path="/some/path",
        content={"foo": "bar"},
        file_type=JSONTypes.SCAN_REPORT,
        version="1.2",
        description="Test description",
    )


def test_from_dict_valid() -> None:
    """Test if the correct JSONFile is created by from_dict."""
    obj = JSONFile.from_dict(EXAMPLE_DICT)

    assert obj.file_type == JSONTypes.SCAN_REPORT
    assert obj.version == "1.2"
    assert obj.associated_path == Path("/some/path")
    assert obj.content == {"foo": "bar"}
    assert obj.version == "1.2"


def test_from_dict_with_ensure_type_matching() -> None:
    """Test if JSONFile.from_dict works with ensure_type and matching file type."""
    obj = JSONFile.from_dict(EXAMPLE_DICT, ensure_type=JSONTypes.SCAN_REPORT)
    assert obj.file_type == JSONTypes.SCAN_REPORT


def test_from_dict_with_ensure_type_mismatch() -> None:
    """Test if JSONFile.from_dict works with ensure_type and mismatching file type."""
    with pytest.raises(InvalidJSONFileTypeError) as excinfo:
        JSONFile.from_dict(
            EXAMPLE_DICT,
            ensure_type=JSONTypes.RENAMING_MAPPING,
            type_reason="Feature XYZ needs this type.",
        )

    assert "Expected JSON file type" in str(excinfo.value)
    assert "Feature XYZ" in str(excinfo.value)


def test_from_dict_invalid_type_string() -> None:
    """Test JSONFile.from_dict with unkown JSONType (should raise ValueError)."""
    invalid_type_dict = EXAMPLE_DICT.copy()
    invalid_type_dict["_type"] = "UNKNOWN_TYPE"

    with pytest.raises(ValueError) as excinfo:
        JSONFile.from_dict(invalid_type_dict)

    assert "Invalid '_type'" in str(excinfo.value)


@pytest.mark.parametrize("missing_key", ["associated_path", "content"])
def test_from_dict_missing_required_fields(missing_key) -> None:
    """Test if JSONFile.from_dict raises an error if a required field is missing."""
    _example_dict = EXAMPLE_DICT.copy()
    _example_dict.pop(missing_key)

    with pytest.raises(ValueError) as excinfo:
        JSONFile.from_dict(_example_dict)

    assert f"Missing required field" in str(excinfo.value)


def test_save_creates_file(jsonfile_instance, tmp_path) -> None:
    """Test JSONFile.save."""
    filepath = tmp_path / "testfile.json"
    jsonfile_instance.save(filepath)

    assert filepath.exists()

    # Check content
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["_type"] == "vidmux-scan-report"
    assert data["content"] == {"foo": "bar"}
    assert data["associated_path"] == "/some/path"
    assert data["_version"] == "1.2"


def test_load_restores_object_correctly(jsonfile_instance, tmp_path) -> None:
    """Test JSONFile.load reading a correct JSONFile object."""
    filepath = tmp_path / "testfile.json"
    jsonfile_instance.save(filepath)

    loaded = JSONFile.load(filepath)

    assert isinstance(loaded, JSONFile)
    assert loaded.file_type == jsonfile_instance.file_type
    assert loaded.content == jsonfile_instance.content
    assert loaded.version == jsonfile_instance.version
    assert loaded.associated_path == Path(jsonfile_instance.associated_path)
    assert loaded.description == jsonfile_instance.description


def test_load_with_ensure_type_matching(jsonfile_instance, tmp_path) -> None:
    """Test JSONFile.load with ensure_type and matching file type."""
    filepath = tmp_path / "testfile.json"
    jsonfile_instance.save(filepath)

    loaded = JSONFile.load(filepath, ensure_type=JSONTypes.SCAN_REPORT)

    assert loaded.file_type == JSONTypes.SCAN_REPORT


def test_load_with_ensure_type_mismatch(jsonfile_instance, tmp_path) -> None:
    """Test JSONFile.load with ensure_type and mismatching file type."""
    filepath = tmp_path / "testfile.json"
    jsonfile_instance.save(filepath)

    with pytest.raises(InvalidJSONFileTypeError) as excinfo:
        JSONFile.load(
            filepath,
            ensure_type=JSONTypes.RENAMING_MAPPING,
            type_reason="Feature XYZ needs this type.",
        )

    assert "Expected JSON file type" in str(excinfo.value)
    assert "Feature XYZ" in str(excinfo.value)
