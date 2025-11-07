"""Module to check the library structure."""

from vidmux.library_structure.core import (
    IssueCode,
    ValidationIssue,
    Severity,
    registry,
    run_validation,
)
from vidmux.library_structure.structure_scan import scan_library_structure


def load_default_rules() -> None:
    """Load and register the default rules."""
    from vidmux.library_structure import rules


__all__ = [
    "IssueCode",
    "ValidationIssue",
    "Severity",
    "load_default_rules",
    "registry",
    "run_validation",
    "scan_library_structure",
]
