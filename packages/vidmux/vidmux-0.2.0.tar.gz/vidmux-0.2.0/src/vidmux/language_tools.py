"""Tools to work with the language field of audio tracks."""

import shlex
import subprocess
import sys
from pathlib import Path

from vidmux.video_inspection import get_audio_tracks, get_subtitles


def build_ffmpeg_language_command(
    input_file: Path,
    output_file: Path,
    audio_languages: list[str],
    subtitle_languages: list[str],
    audio_titles: list[str] = None,
    subtitle_titles: list[str] = None,
) -> list[str]:
    """Build command to set track languages using ffmpeg."""
    command = ["ffmpeg", "-i", str(input_file), "-map", "0", "-c", "copy"]

    for index, language in enumerate(audio_languages):
        command += [f"-metadata:s:a:{index}", f"language={language}"]
        if audio_titles and index < len(audio_titles):
            command += [f"-metadata:s:a:{index}", f"title={audio_titles[index]}"]

    for index, language in enumerate(subtitle_languages):
        command += [f"-metadata:s:s:{index}", f"language={language}"]
        if subtitle_titles and index < len(subtitle_titles):
            command += [f"-metadata:s:s:{index}", f"title={subtitle_titles[index]}"]

    command.append(str(output_file))

    return command


def set_languages(
    input_file: Path,
    output_file: Path,
    audio_languages: list[str],
    subtitle_languages: list[str],
    audio_titles: list[str] = None,
    subtitle_titles: list[str] = None,
    dry_run: bool = False,
):
    audio_streams = get_audio_tracks(input_file)
    subtitle_streams = get_subtitles(input_file)

    if len(audio_languages) != len(audio_streams):
        msg = (
            f"Error: Number of audio languages ({len(audio_languages)}) does not match "
            f"number of audio tracks ({len(audio_streams)})."
        )
        print(msg, file=sys.stderr)
        sys.exit(1)

    if subtitle_languages and len(subtitle_languages) != len(subtitle_streams):
        msg = (
            f"Error: Number of subtitle languages ({len(subtitle_languages)}) does not "
            f"match number of subtitle tracks ({len(subtitle_streams)})."
        )
        print(msg, file=sys.stderr)
        sys.exit(1)

    command = build_ffmpeg_language_command(
        input_file,
        output_file,
        audio_languages,
        subtitle_languages,
        audio_titles,
        subtitle_titles,
    )

    print("FFmpeg command:")
    print(" ".join(shlex.quote(part) for part in command))

    if not dry_run:
        subprocess.run(command)
