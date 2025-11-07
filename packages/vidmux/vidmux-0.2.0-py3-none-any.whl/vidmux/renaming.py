"""Provide tools for renaming."""

from pathlib import Path

from vidmux.filesystem import JSONFile, JSONTypes


def rename_files(base_path: Path, renaming_mapping: dict, backup: bool = True) -> dict:
    """Rename all given files."""
    report = {}
    for old_name, new_name in renaming_mapping.items():
        old_path: Path = base_path / old_name
        new_path: Path = base_path / new_name
        new_path.parent.mkdir(parents=True, exist_ok=True)

        if backup:
            backup_path = new_path.with_suffix(new_path.suffix + ".bak")
            with backup_path.open("w", encoding="utf-8") as backup_file:
                backup_file.write(str(old_path))

        try:
            old_path.rename(new_path)
            report[old_name] = new_name
        except Exception as err:
            report[old_name] = str(err)

    return report


def rename_mode(rename_file_path: Path | str, backup: bool = True) -> None:
    """Load renaming mapping from file and apply it."""
    file = JSONFile.load(
        rename_file_path,
        ensure_type=JSONTypes.RENAMING_MAPPING,
        type_reason="Renaming needs a file containing the renaming mapping.",
    )
    rename_files(Path(file.associated_path), file.content, backup=backup)
