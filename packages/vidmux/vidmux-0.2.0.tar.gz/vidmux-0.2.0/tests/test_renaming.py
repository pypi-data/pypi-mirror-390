"""Provide tests for the renaming feature."""

from pathlib import Path

import pytest

from vidmux.renaming import JSONFile, JSONTypes, rename_files, rename_mode


EXAMPLE_DATA = {
    "Example Movie (2000).mp4": "Example Movie (2000) - [EN] [1080p].mp4",
    "Example Movie (2000)/Example Movie (2000).mp4": "Example Movie (2000)/Example Movie (2000) - [EN] [1080p].mp4",
    "Example Movie/Example Movie (2000).mp4": "Example Movie (2000)/Example Movie (2000) - [EN] [1080p].mp4",
}


@pytest.mark.parametrize("old_name,new_name", EXAMPLE_DATA.items())
def test_file_renaming(tmp_path, old_name: str, new_name: str) -> None:
    """Test renaming files."""
    backup = True

    # Set paths
    base_path = Path(tmp_path)
    old_file = base_path / old_name
    new_file = base_path / new_name

    # Create old file
    old_file.parent.mkdir(parents=True, exist_ok=True)
    old_file.touch()

    # Check if the test has created the old file correctly
    assert old_file.is_file()

    # Rename and check if everything worked out
    report = rename_files(base_path, {old_name: new_name}, backup=backup)
    assert new_file.is_file()
    assert not old_file.exists()
    assert report[old_name] == new_name

    # If the parent directories differ, the original one should be empty (only one file)
    if (old_dir := old_file.parent) != new_file.parent:
        assert len(list(old_dir.glob("*"))) == 0

    # Check if the backup was done properly
    if backup:
        backup_file = new_file.with_suffix(new_file.suffix + ".bak")
        assert backup_file.is_file()
        backup_content = backup_file.read_text(encoding="utf-8")
        assert backup_content == str(old_file)


def test_renaming_mode(tmp_path) -> None:
    """Test the renaming mode."""
    library_path = Path(tmp_path)

    # Create original files
    for filename in EXAMPLE_DATA.keys():
        filepath = library_path / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.touch()
        assert filepath.is_file()

    # Create file with renaming mapping
    rename_file_path = library_path / "renaming_mapping.json"
    json_file = JSONFile(
        library_path, EXAMPLE_DATA, file_type=JSONTypes.RENAMING_MAPPING
    )
    json_file.save(rename_file_path)
    assert rename_file_path.is_file()

    # Run rename_mode
    rename_mode(rename_file_path, backup=True)

    for old_name, new_name in EXAMPLE_DATA.items():
        new_file = library_path / new_name
        assert not (
            library_path / old_name
        ).is_file(), f"Old file '{old_name}' still exists!"
        assert new_file.is_file(), f"New file '{new_name}' does not exist!"
        assert new_file.with_suffix(
            new_file.suffix + ".bak"
        ).is_file(), f"Backup file for '{old_name}' does not exist!"
