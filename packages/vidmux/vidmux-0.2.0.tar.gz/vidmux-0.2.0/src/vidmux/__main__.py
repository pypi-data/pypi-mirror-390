"""Main entry point for vidmux."""

import shutil
import sys

from vidmux.cli import main as cli_mode


def ensure_ffmpeg() -> None:
    """Exit if 'ffmpeg' is not found."""
    if not shutil.which("ffmpeg"):
        sys.exit("Error: FFmpeg not found. Please install it and ensure it is in PATH.")


def main():
    """Entry point for "vidmux"and "python -m vidmux"."""
    ensure_ffmpeg()
    cli_mode()


if __name__ == "__main__":
    main()
