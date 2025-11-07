"""Test the library structure submodule."""

from pathlib import Path

import pytest

from vidmux.library_structure import registry, load_default_rules, run_validation

MOVIES = {
    "/Example Movie A.mp4": ["MISSING_YEAR"],
    "/Example Movie B (20).mp4": ["MISSING_YEAR"],
    "/Example Movie C (2009).mp4": [],
    "Example Movie D (2003)/Example Movie D (2003) [EN+DE].mp4": [],
    "Example Movie E (2003)/Example Movie E2 (2003).mp4": [
        "FILE_AND_FOLDER_NAME_DIFFER"
    ],
    "Example Movie F.mp4": ["MISSING_YEAR", "FILE_NOT_IN_FOLDER"],
    "Example Movie G (2003).mp4": ["FILE_NOT_IN_FOLDER"],
}


@pytest.fixture(scope="module")
def example_library(tmp_path_factory: pytest.TempPathFactory) -> Path:
    tmp_path = tmp_path_factory.mktemp("library")

    for name in MOVIES.keys():
        if "/" in name:
            # File should be in folder (name equals filename if no folder is provided)
            parts = name.split("/")
            folder_name = parts[0] if len(parts) == 1 else parts[-2]
            file_name = parts[-1]
            if not folder_name:
                folder_name = file_name.removesuffix(".mp4")
        else:
            # File should not be in a folder
            folder_name = None

        path = tmp_path / folder_name / file_name if folder_name else tmp_path / name

        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()

    return tmp_path


@pytest.fixture(autouse=True, scope="module")
def _load_default_rules():
    """Automatically load default rules for this test module."""
    load_default_rules()


@pytest.mark.parametrize("total_name,expected_codes", MOVIES.items())
def test_library_issues(example_library, total_name, expected_codes):
    """Test each movie against expected validation results."""
    reports = run_validation(example_library.rglob("*.mp4"))
    file_name = total_name.split("/")[-1]

    # Find report for file
    entry = next((report for report in reports if file_name in report["path"]), None)
    assert entry is not None, f"{file_name} missing in report"

    codes = [issue["code"] for issue in entry["issues"]]
    assert sorted(codes) == sorted(expected_codes)


# def test_debug_report(example_library):
#     """Show the report of the example library check and fail."""
#     import json

#     report = run_validation(example_library.rglob("*.mp4"))
#     print(json.dumps(report, indent=2))
#     print("Used rules:", registry.rules)
#     assert False, "Manual debug stop"
