"""Test for muxing audio tracks."""

from pathlib import Path
from unittest.mock import patch

import pytest

from vidmux.mux_audio_tracks import mux_audio_tracks


def test_mux_fails_with_missing_args(tmp_path: Path) -> None:
    """Test failing on purpose."""
    outfile = tmp_path / "out.mp4"
    with pytest.raises(SystemExit):
        mux_audio_tracks(outfile, ["only_one_arg"])


def test_mux_command(tmp_path: Path) -> None:
    """Test whether the mux command is constructed correctly without running ffmpeg."""
    outfile = tmp_path / "outfile.mp4"

    infile_1 = tmp_path / "video_1.mp4"
    infile_2 = tmp_path / "video_2.mp4"
    infile_3 = tmp_path / "video_3.mp4"

    # Create empty dummy input files
    for file in (infile_1, infile_2, infile_3):
        file.touch()

    # Patch subprocess.run so ffmpeg is not actually executed
    with patch("subprocess.run") as mock_run:
        mux_audio_tracks(
            outfile,
            [
                infile_1,
                "deu",
                infile_2,
                "deu",
                "Deutscher Kommentar",
                infile_3,
                "eng",
            ],
        )

    # Extract the command that would have been run
    args = mock_run.call_args[0][0]

    # Define expected ffmpeg arguments
    expected_args = [
        "ffmpeg",
        "-i",
        str(infile_1),
        "-i",
        str(infile_2),
        "-i",
        str(infile_3),
        # mapping: first input has video+audio, others only audio
        "-map",
        "0:v:0",
        "-map",
        "0:a:0",
        "-map",
        "1:a:0",
        "-map",
        "2:a:0",
        "-c:v",
        "copy",
        "-c:a",
        "copy",
        # metadata
        "-metadata:s:a:0",
        "language=deu",
        "-metadata:s:a:1",
        "language=deu",
        "-metadata:s:a:1",
        "title=Deutscher Kommentar",
        "-metadata:s:a:2",
        "language=eng",
        str(outfile),
    ]

    # Check whether expected and true arguments are equal
    assert args == expected_args, (
        "FFmpeg arguments do not match expected command.\n"
        f"Expected:\n  {expected_args}\nGot:\n  {args}"
    )

    # Ensure only one subprocess call
    mock_run.assert_called_once_with(expected_args, check=True)


def test_mux_command_with_fixture(tmp_path: Path, ffmpeg_mock) -> None:
    """Test whether the mux command is constructed correctly without running ffmpeg."""
    outfile = tmp_path / "outfile.mp4"

    infile_1 = tmp_path / "video_1.mp4"
    infile_2 = tmp_path / "video_2.mp4"
    infile_3 = tmp_path / "video_3.mp4"

    # Create empty dummy input files
    for file in (infile_1, infile_2, infile_3):
        file.touch()

    mux_audio_tracks(
        outfile,
        [
            infile_1,
            "deu",
            infile_2,
            "deu",
            "Deutscher Kommentar",
            infile_3,
            "eng",
        ],
    )

    # Define expected ffmpeg arguments
    expected_args = [
        "ffmpeg",
        "-i",
        str(infile_1),
        "-i",
        str(infile_2),
        "-i",
        str(infile_3),
        # mapping: first input has video+audio, others only audio
        "-map",
        "0:v:0",
        "-map",
        "0:a:0",
        "-map",
        "1:a:0",
        "-map",
        "2:a:0",
        "-c:v",
        "copy",
        "-c:a",
        "copy",
        # metadata
        "-metadata:s:a:0",
        "language=deu",
        "-metadata:s:a:1",
        "language=deu",
        "-metadata:s:a:1",
        "title=Deutscher Kommentar",
        "-metadata:s:a:2",
        "language=eng",
        str(outfile),
    ]

    ffmpeg_mock.assert_called_with(expected_args)


@pytest.mark.parametrize(
    "inputs",
    [
        ["a.mp4", "eng"],
        ["a.mp4", "eng", "English"],
        ["a.mp4", "eng", "English", "b.mp4", "deu", "Deutsch"],
    ],
)
def test_mux_argument_patterns(tmp_path: Path, inputs: list[str]) -> None:
    """Test multiple argument patterns."""
    outfile = tmp_path / "out.mp4"
    for name in inputs[::3]:
        (tmp_path / name).touch()
    with patch("subprocess.run") as mock_run:
        mux_audio_tracks(
            outfile, [tmp_path / x if x.endswith(".mp4") else x for x in inputs]
        )
    mock_run.assert_called_once()
