"""Tools to mux audio tracks."""

import subprocess
import shlex
import sys
from pathlib import Path


def mux_audio_tracks(output_file, inputs, dry_run: bool = False) -> None:
    """
    Execute the 'mux-audio-tracks' command using FFmpeg.
    """
    if len(inputs) < 2:
        sys.exit("Error: Need at least one input file and language code.")

    input_args = []
    map_args = []
    metadata_args = []

    cmd_idx = 0
    input_idx = 0
    while input_idx < len(inputs):
        if input_idx + 1 >= len(inputs):
            sys.exit("Error: Each input requires at least a file and language code.")

        input_file = str(inputs[input_idx])
        lang = inputs[input_idx + 1]
        title = None

        # Optional title if the next argument is not a file path that exists
        if input_idx + 2 < len(inputs) and not Path(inputs[input_idx + 2]).exists():
            title = inputs[input_idx + 2]
            input_idx += 3
        else:
            input_idx += 2

        if cmd_idx == 0:
            input_args += ["-i", input_file]
            map_args += ["-map", "0:v:0", "-map", "0:a:0"]
        else:
            input_args += ["-i", input_file]
            map_args += ["-map", f"{cmd_idx}:a:0"]

        metadata_args += ["-metadata:s:a:%d" % cmd_idx, f"language={lang}"]
        if title:
            metadata_args += ["-metadata:s:a:%d" % cmd_idx, f"title={title}"]

        cmd_idx += 1

    command = [
        "ffmpeg",
        *input_args,
        *map_args,
        "-c:v",
        "copy",
        "-c:a",
        "copy",
        *metadata_args,
        str(output_file),
    ]

    print("FFmpeg command:")
    print(" ".join(shlex.quote(part) for part in command))

    if not dry_run:
        subprocess.run(command, check=True)
