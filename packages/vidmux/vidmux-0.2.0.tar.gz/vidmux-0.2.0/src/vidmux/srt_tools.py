"""Tools for .srt files (subtitles)."""

import re
from pathlib import Path

# Regex for SRT timestamps: allows H or HH, allows "," or "." for ms
TIMESTAMP_RE = re.compile(
    r"(\d{1,2}):([0-5]\d):([0-5]\d)[\.,](\d{1,3})\s*-->\s*"
    r"(\d{1,2}):([0-5]\d):([0-5]\d)[\.,](\d{1,3})"
)


def timestamp_to_milliseconds(
    hours: str, minutes: str, seconds: str, milliseconds: str
) -> int:
    """Convert timestamp components to ms."""
    # Normalise ms to 3 digits
    ms_str = milliseconds.ljust(3, "0") if len(milliseconds) < 3 else milliseconds[:3]

    return (int(hours) * 3600 + int(minutes) * 60 + int(seconds)) * 1000 + int(ms_str)


def timestamp_from_milliseconds(total_ms: int) -> str:
    """Create timestamp from ms."""
    if total_ms < 0:
        total_ms = 0
    ms = total_ms % 1000
    total_s = total_ms // 1000
    s = total_s % 60
    total_m = total_s // 60
    m = total_m % 60
    h = total_m // 60

    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def shift_line(re_match: re.Match, shift_ms: int) -> str:
    """Return time-shifted timestamp line."""
    h1, m1, s1, ms1, h2, m2, s2, ms2 = re_match.groups()
    start_ms = timestamp_to_milliseconds(h1, m1, s1, ms1)
    end_ms = timestamp_to_milliseconds(h2, m2, s2, ms2)
    new_start = timestamp_from_milliseconds(start_ms + shift_ms)
    new_end = timestamp_from_milliseconds(end_ms + shift_ms)

    return f"{new_start} --> {new_end}"


def process_text(text: str, shift_seconds: float) -> tuple[str, int]:
    """Shift all timestamps in the text."""
    shift_ms = int(round(shift_seconds * 1000))

    def repl(re_match: re.Match):
        """Return the shifted timestamp line."""
        return shift_line(re_match, shift_ms)

    new_text, count = TIMESTAMP_RE.subn(repl, text)

    return new_text, count


def process_file(
    input_file: str | Path,
    shift_seconds: float,
    inplace: bool = True,
    output_file: str | Path | None = None,
    show_count: bool = True,
):
    """Shift the timestamps of a file."""
    input_file = Path(input_file)
    if not input_file.exists():
        msg = f"'{input_file}' does not exist!"
        raise FileNotFoundError(msg)

    text = input_file.read_text(encoding="utf-8-sig")  # Read UTF-8 (+ potential BOM)
    new_text, count = process_text(text, shift_seconds)

    if inplace:
        # Create backup
        backup_file = input_file.with_suffix(input_file.suffix + ".bak")
        input_file.rename(backup_file)
        # Set output filename to input filename
        output_file = input_file
        output_file.write_text(new_text, encoding="utf-8")
        # Show number of changes
        if show_count:
            print(
                f"Wrote {output_file} (backup: {backup_file}), "
                f"changed timestamps: {count}"
            )
    else:
        if output_file:
            output_file = Path(output_file)
            output_file.write_text(new_text, encoding="utf-8")
            # Show number of changes
            if show_count:
                print(f"Wrote {output_file}, changed timestamps: {count}")
        else:
            # No outfile -> stdout
            print(new_text)
            # Show number of changes
            if show_count:
                print(f"\nChanged timestamps: {count}")
