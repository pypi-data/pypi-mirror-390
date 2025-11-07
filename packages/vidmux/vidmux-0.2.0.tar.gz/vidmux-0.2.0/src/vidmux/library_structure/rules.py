"""Define the rules used in the validation process."""

import re
from pathlib import Path

from vidmux.library_structure.core import registry, IssueCode, ValidationIssue, Severity


def normalize_name(name: str) -> str:
    """Normalize a folder/filename, i.e. delete (YYYY) and allowed suffixes."""
    # Delete '(YYYY)'
    name = re.sub(r"\(\d{4}\)", "", name)
    # Delete '[...]' (without deleting text between two pairs of brackets)
    name = re.sub(r"\[.*?\]", "", name).lower()

    return name.strip()


def is_file_in_separate_folder(path: Path) -> bool:
    """
    Check whether the file is in a separate folder with similar name.

    The folder name and filename can differ to a certain extent.

    Note: Currently this function is called twice per file. If this increases, consider
    using functools.lru_cache to save the result after the first call.
    """
    folder_name = normalize_name(path.parent.name)
    file_stem = normalize_name(path.stem)

    return folder_name in file_stem


@registry.register(default_severity=Severity.WARNING)
def check_file_in_own_folder(path: Path, params) -> list[ValidationIssue]:
    """Check whether the file is in its own subfolder."""
    issues = []

    if not is_file_in_separate_folder(path):
        issues.append(
            ValidationIssue(
                path=path,
                code=IssueCode.FILE_NOT_IN_FOLDER,
                message=f"File not in own folder ({path.parent.name})",
                severity=Severity.WARNING,
            )
        )

    return issues


@registry.register(
    default_severity=Severity.WARNING,
    default_params={
        "allowed_suffixes": r"(\s*[-–]\s*[A-Za-z0-9 ]+|\s*\[[A-Za-z0-9+\- ]+\])$"
    },
)
def check_filename_matches_folder(path: Path, params) -> list[ValidationIssue]:
    """Check whether file and folder name match."""
    issues = []

    # If the file is not in a separate folder this rule does not apply at all
    if not is_file_in_separate_folder(path):
        return issues

    folder_name = path.parent.name
    file_stem = path.stem

    # Strip allowed suffixes from filename, e.g. "- Director's Cut", "[EN+DE]"
    allowed_suffixes = re.compile(params["allowed_suffixes"])
    cleaned_file_stem = allowed_suffixes.sub("", file_stem).strip()
    cleaned_folder_name = allowed_suffixes.sub("", folder_name).strip()

    if cleaned_folder_name not in cleaned_file_stem:
        issues.append(
            ValidationIssue(
                path=path,
                code=IssueCode.FILE_AND_FOLDER_NAME_DIFFER,
                message=(
                    f"Filename '{file_stem}' differs from folder '{folder_name}' "
                    f"(except for allowed suffixes)"
                ),
                severity=Severity.WARNING,
            )
        )

    return issues


@registry.register(
    default_severity=Severity.ERROR,
    default_params={"bad_chars": r'<>:"/\\|?*'},
)
def check_for_bad_characters(path: Path, params) -> list[ValidationIssue]:
    """Check whether the filename contains illegal characters."""
    bad_chars = set(params["bad_chars"])
    found = sorted({char for char in path.name if char in bad_chars})
    if not found:
        return []

    return [
        ValidationIssue(
            path=path,
            code=IssueCode.BAD_CHARACTER_IN_NAME,
            message=f"Filename contains illegal character(s): {' '.join(found)}",
            severity=Severity.ERROR,
        )
    ]


@registry.register(default_severity=Severity.WARNING)
def check_year_in_filename(path: Path, params) -> list[ValidationIssue]:
    """Check whether a year (YYYY) is given in the filename."""
    issues = []
    if not re.search(r"\(\d{4}\)", path.stem):
        issues.append(
            ValidationIssue(
                path=path,
                code=IssueCode.MISSING_YEAR,
                message="No year in parentheses",
                severity=Severity.WARNING,
            )
        )

    return issues
