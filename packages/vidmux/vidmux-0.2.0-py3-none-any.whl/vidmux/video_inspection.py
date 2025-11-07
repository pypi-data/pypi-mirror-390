"""Tools for video inspection (format, streams, resolution, ...)."""

import json
import subprocess
from pathlib import Path


def get_format(file_path: Path) -> str:
    """Return the container format of a file (e.g., 'mov,mp4,m4a,3gp,3g2,mj2')."""
    command = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        str(file_path),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    try:
        info = json.loads(result.stdout)
        return info.get("format", {}).get("format_name", "")
    except Exception:
        return ""


def get_streams(file_path: Path, stream_type: str):
    """
    Extract media streams using ffprobe (ffmpeg).

    stream_type: "a" = Audio, "v" = Video, "s" = Subtitle
    """
    if stream_type not in ("a", "v", "s"):
        raise ValueError("Invalid stream_type. Must be 'a', 'v' or 's'.")

    cmd = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_streams",
        "-select_streams",
        stream_type,
        str(file_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        info = json.loads(result.stdout)
        return info.get("streams", [])
    except json.JSONDecodeError:
        return []


def get_audio_tracks(file_path: Path):
    """Extract audio tracks using ffprobe (ffmpeg)."""
    return get_streams(file_path, "a")


def get_subtitles(file_path: Path):
    """Extract subtitles using ffprobe (ffmpeg)."""
    return get_streams(file_path, "s")


def get_video_tracks(file_path: Path):
    """Extract video tracks using ffprobe (ffmpeg)."""
    return get_streams(file_path, "v")


def get_video_resolution(path_or_url: str | Path) -> tuple[int, int] | None:
    """Get the video resolution for a file or URL."""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height",
        "-of",
        "csv=p=0:s=x",
        str(path_or_url),
    ]
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode().strip()
        width, height = output.split("x")
        return int(width), int(height)
    except subprocess.CalledProcessError as err:
        print("ffprobe error:", err.output.decode())
        return None
