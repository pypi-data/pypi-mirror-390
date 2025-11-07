""" "Provide tests for the library scan."""

import pytest

from vidmux.video_library_scan import suggest_name


UNDEFINED_LANGUAGE = "EN"
TEST_DATA = (
    # Just a file with no language info -> assume english and put it in a subfolder
    {
        "filename": "Example Movie (2000).mp4",
        "video_tracks": [{}],
        "audio_tracks": [{}],
        "expected_filename": "Example Movie (2000)/Example Movie (2000) - [EN].mp4",
    },
    # Already in the correct folder
    {
        "filename": "Library/Example Movie (2000)/Example Movie (2000).mp4",
        "video_tracks": [{"width": 1920, "height": 1080}],
        "audio_tracks": [{"language": "und"}],
        "expected_filename": (
            "Library/Example Movie (2000)/Example Movie (2000) - [EN] [1080p].mp4"
        ),
    },
    # Version and two language tracks
    {
        "filename": "Example Movie (2000)/Example Movie (2000) - DVD [DE+EN].mp4",
        "video_tracks": [{"width": 1920, "height": 1080}],
        "audio_tracks": [{"language": "deu"}, {"language": "und"}],
        "expected_filename": (
            "Example Movie (2000)/Example Movie (2000) - [DVD] [DE+EN] [1080p].mp4"
        ),
    },
    # Version already in brackets
    {
        "filename": (
            "Library/Example Movie (2000)/Example Movie (2000) - [DVD] [EN].mp4"
        ),
        "video_tracks": [{"width": 1920, "height": 1080}],
        "audio_tracks": [{"language": "und"}],
        "expected_filename": (
            "Library/Example Movie (2000)/Example Movie (2000) - [DVD] [EN] [1080p].mp4"
        ),
    },
    # Nested parent directory
    {
        "filename": "Library/Some Folder/Example Movie (2000) - DVD [EN].mp4",
        "video_tracks": [{"width": 1920, "height": 1080}],
        "audio_tracks": [{"language": "und"}],
        "expected_filename": (
            "Library/Some Folder/Example Movie (2000)/Example Movie (2000) - "
            "[DVD] [EN] [1080p].mp4"
        ),
    },
    # In a folder, but not in the correct one
    {
        "filename": "Library/Some Folder/Example Movie (2000) - DVD [EN].mp4",
        "video_tracks": [{"width": 1920, "height": 1080}],
        "audio_tracks": [{"language": "und"}],
        "expected_filename": (
            "Library/Some Folder/Example Movie (2000)/Example Movie (2000) - "
            "[DVD] [EN] [1080p].mp4"
        ),
    },
    # Has a 'subtitle' in the name, e.g. "Franchise Name - First installment"
    # Currently this is only recognized correctly if the movie already is in the correct
    # directory
    {
        "filename": (
            "Library/Example Movie - This is a subtitle (2000)/"
            "Example Movie - This is a subtitle (2000).mp4"
        ),
        "video_tracks": [{"width": 1920, "height": 1080}],
        "audio_tracks": [{"language": "und"}],
        "expected_filename": (
            "Library/Example Movie - This is a subtitle (2000)/"
            "Example Movie - This is a subtitle (2000) - [EN] [1080p].mp4"
        ),
    },
)


@pytest.mark.parametrize("report", TEST_DATA)
def test_suggest_name(report: dict) -> None:
    suggested_name = suggest_name(report, undefined_language=UNDEFINED_LANGUAGE)

    assert suggested_name == report["expected_filename"]
