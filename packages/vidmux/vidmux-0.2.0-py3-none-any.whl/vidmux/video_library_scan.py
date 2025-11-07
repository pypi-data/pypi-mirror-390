"""Tools to scan a video library."""

import csv
from pathlib import Path

from vidmux.filesystem import JSONFile, JSONTypes
from vidmux.video_inspection import (
    get_audio_tracks,
    get_format,
    get_subtitles,
    get_video_tracks,
)


def select_main_video_track(video_tracks: list) -> list:
    """
    Return the main video track.

    From all tracks, the track with highest resolution (width*height) is selected.
    """
    if not video_tracks:
        return None

    main_track = max(
        video_tracks, key=lambda track: track.get("width", 0) * track.get("height", 0)
    )

    return main_track


def get_languages_tag(audio_tracks: list, undefined_language: str = "??") -> str | None:
    """Return the tag for audio languages."""
    languages = []
    for audio_track in audio_tracks:
        lang = audio_track.get("language", "und")
        if lang != "und":
            languages.append(lang.upper()[:2])  # e.g. 'eng' -> 'EN'
        else:
            languages.append(undefined_language)

    language_tag = None
    if len(languages) == 1:
        language_tag = f"[{languages.pop()}]"
    elif len(languages) > 1:
        language_tag = "[" + "+".join(languages) + "]"

    return language_tag


def get_resolution_tag(video_tracks: list) -> str | None:
    """Return the tag for the video resolution."""
    main_track = select_main_video_track(video_tracks)
    height = main_track.get("height", 0)
    if not height:
        return None
    field_order = main_track.get("field_order", "progressive")
    # Round to standard values
    if height >= 2160:
        base = "2160"
    elif height >= 1440:
        base = "1440"
    elif height >= 1080:
        base = "1080"
    elif height >= 720:
        base = "720"
    elif height >= 576:
        base = "576"
    elif height >= 480:
        base = "480"
    elif height >= 360:
        base = "360"
    else:
        base = str(height)

    # Get scan type
    scan_type = "i" if field_order.lower() in {"tt", "bb", "tb", "bt"} else "p"

    return f"[{base}{scan_type}]"


def suggest_name_tags(report: dict, undefined_language: str = "??") -> list[str]:
    """Return a list of suggested tags based on the resolution and languages."""
    tags = []
    if language_tag := get_languages_tag(
        report["audio_tracks"], undefined_language=undefined_language
    ):
        tags.append(language_tag)
    if resolution_tag := get_resolution_tag(report["video_tracks"]):
        tags.append(resolution_tag)

    return tags


def suggest_name(report: dict, undefined_language: str = "??") -> str:
    """Suggest a name based on the report."""
    original_path = Path(report["filename"])
    filename = original_path.stem
    extension = original_path.suffix
    parent = original_path.parent

    # Get tags
    tags = suggest_name_tags(report, undefined_language=undefined_language)

    # Get basename and guess version (if provided)
    basename = extract_basename_from_filename(filename, parent.name, tags)
    guessed_version = extract_version_from_filename(filename, basename, tags)

    # Construct new filename
    parts = [guessed_version] if guessed_version else []
    parts.extend(tags)
    suffix = (" - " + " ".join(parts)) if parts else ""

    new_filename = f"{basename}{suffix}{extension}"

    # Check whether a subfolder has to be created
    if parent.name == basename:
        new_path = parent / new_filename
    else:
        new_path = parent / basename / new_filename

    return str(new_path)


def extract_basename_from_filename(
    filename: str, parentname: str, tags: list[str]
) -> str:
    """
    Extract the basename from filename given a list of tags.

    Note:
    This is the bottleneck. Good filenames and structures as an input are recommended.
    """
    # Delete tags from filename
    clean_name = filename
    for tag in tags:
        clean_name = clean_name.replace(tag, "")
    # Delete additional information separated by " - "
    clean_name = clean_name.strip()
    if (separator := " - ") in clean_name:
        parts = clean_name.split(separator)
        # If the separated part is in the directory name, treat it as part of the name
        if parts[-1] not in parentname:
            return separator.join(parts[:-1]).strip()

    return clean_name


def extract_version_from_filename(filename: str, basename: str, tags: list[str]) -> str:
    """Extract the version name."""
    remainder = filename.removeprefix(basename).strip()
    if remainder.startswith("-"):
        remainder = remainder[1:].strip()

    # Delete tags from filename
    for tag in tags:
        remainder = remainder.replace(tag, "").strip()

    # Treat remainder as version name
    if remainder:
        remainder = remainder.strip(" []")  # Strip old brackets
        return f"[{remainder}]"

    return ""


def make_track_entries(tracks: list) -> list:
    """
    Return the track list with the most important info.

    Each track has index, language, codec and title.
    Video tracks will also include (if available):
    - width and height
    - field_order
    """
    entries = []
    for idx, track in enumerate(tracks):
        entry = {
            "index": idx,
            "language": track.get("tags", {}).get("language", "unknown"),
            "codec": track.get("codec_name", "unknown"),
            "title": track.get("tags", {}).get("title", ""),
        }
        # If available (video tracks), include the resolution info
        if "width" in track and "height" in track:
            entry["width"] = track["width"]
            entry["height"] = track["height"]
        if "field_order" in track:
            entry["field_order"] = track["field_order"]
        entries.append(entry)

    return entries


def show_track_entries(
    tracks: list, name: str = "track", output: callable = print
) -> None:
    """Show tracks."""
    for track in tracks:
        idx = track["index"]
        language = track["language"]
        codec = track["codec"]
        title = track["title"]
        output(f"\t{name.capitalize()} {idx+1}: {language=}, {codec=}, {title=}")


def scan_video_library(
    library_path: Path, extensions: list[str] | None = None
) -> list[dict]:
    """Scan all videos in 'library_path' recursively."""
    if extensions is None:
        extensions = [".mp4", ".mkv", ".avi", ".mov"]

    results = []
    for root, _dirs, files in library_path.walk():
        for filename in files:
            file = root / filename
            if file.suffix in extensions:
                print(f"Inspecting '{filename}'...")
                video_tracks = get_video_tracks(file)
                audio_tracks = get_audio_tracks(file)
                subtitles = get_subtitles(file)
                results.append(
                    {
                        "filename": str(file.relative_to(library_path)),
                        "container": get_format(file),
                        "video_tracks": make_track_entries(video_tracks),
                        "audio_tracks": make_track_entries(audio_tracks),
                        "subtitle_tracks": make_track_entries(subtitles),
                    }
                )

    return results


def save_csv(results: list[dict], path: Path) -> None:
    """Save results to a CSV file."""
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["filename", "type", "index", "language", "codec", "title"])
        for entry in results:
            for track in entry["audio_tracks"]:
                writer.writerow(
                    [
                        entry["filename"],
                        "audio",
                        track["index"],
                        track["language"],
                        track["codec"],
                        track["title"],
                    ]
                )
            for track in entry["subtitle_tracks"]:
                writer.writerow(
                    [
                        entry["filename"],
                        "subtitle",
                        track["index"],
                        track["language"],
                        track["codec"],
                        track["title"],
                    ]
                )

    print(f"Save CSV: {path}")


def print_to_terminal(results: list[dict]) -> None:
    """Print results to terminal."""
    for entry in results:
        print(entry["filename"])
        show_track_entries(entry["audio_tracks"], name="audio track")
        show_track_entries(entry["subtitle_tracks"], name="subtitle track")


def scan_mode(
    library: Path,
    extensions: list[str],
    show: bool = True,
    json_file: Path | None = None,
    csv_file: Path | None = None,
    name_file: Path | None = None,
    default_language: str = "??",
) -> bool:
    """Run the scan and save/show the output."""
    if not (show or json_file or csv_file):
        print("No output specified. Use --print, --json or --csv.")
        return False

    scan_result = scan_video_library(library, extensions=extensions)

    if show:
        print_to_terminal(scan_result)

    if json_file:
        outfile = JSONFile(
            library.resolve(), scan_result, file_type=JSONTypes.SCAN_REPORT
        )
        outfile.save(json_file)

    if csv_file:
        save_csv(scan_result, csv_file)

    if name_file:
        name_suggestions = {}
        for report in scan_result:
            suggested_name = suggest_name(report, undefined_language=default_language)
            if (filename := report["filename"]) != suggested_name:
                name_suggestions[filename] = suggested_name

        outfile = JSONFile(
            library.resolve(), name_suggestions, file_type=JSONTypes.RENAMING_MAPPING
        )
        outfile.save(name_file)

    return True
