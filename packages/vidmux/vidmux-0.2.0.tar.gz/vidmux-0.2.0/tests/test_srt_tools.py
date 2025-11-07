"""Tests for srt_tools."""

import vidmux.srt_tools as srt_tools


def test_timestamp_conversion() -> None:
    """Test the conversion from timestamps to milliseconds and vice versa."""
    org_timestamp = "01:08:57,200"
    org_milliseconds = 4137200

    assert (
        srt_tools.timestamp_to_milliseconds(*org_timestamp.replace(",", ":").split(":"))
        == org_milliseconds
    )
    assert srt_tools.timestamp_from_milliseconds(org_milliseconds) == org_timestamp

    # Also test timestamp formats that differ slightly
    org_timestamp = "1:08:57,200".replace(",", ":").split(":")
    assert srt_tools.timestamp_to_milliseconds(*org_timestamp) == org_milliseconds

    org_timestamp = "01:08:57,2".replace(",", ":").split(":")
    assert srt_tools.timestamp_to_milliseconds(*org_timestamp) == org_milliseconds


def test_text_processing() -> None:
    """Test the correct shifting of all timestamps in a text."""
    # We also test the flexibility of the Regex search, one timestamp has ".TT" instead
    # of ",TTT" for milliseconds. Processing the text should also correct this.
    org_text = (
        "1\n"
        "01:08:57,200 --> 01:08:59,900\n"
        "Some text...\n\n"
        "2\n"
        "01:09:59.00 --> 01:10:00,200\n"
        "Some other text...\n\n"
    )

    shift_seconds = 0.9

    target_text = (
        "1\n"
        "01:08:58,100 --> 01:09:00,800\n"
        "Some text...\n\n"
        "2\n"
        "01:09:59,900 --> 01:10:01,100\n"
        "Some other text...\n\n"
    )

    shifted_text, count = srt_tools.process_text(org_text, shift_seconds)

    assert shifted_text == target_text
    assert count == 2
