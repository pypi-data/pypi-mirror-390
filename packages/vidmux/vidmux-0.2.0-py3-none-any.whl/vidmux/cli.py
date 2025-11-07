"""Collection of CLI programs."""

import argparse
from pathlib import Path

import vidmux.srt_tools as srt_tools
from vidmux.language_tools import set_languages
from vidmux.library_structure import scan_library_structure
from vidmux.mux_audio_tracks import mux_audio_tracks
from vidmux.renaming import rename_mode
from vidmux.video_inspection import get_video_resolution
from vidmux.video_library_scan import scan_mode


def get_library_structur_parser(
    subparsers: argparse._SubParsersAction | None = None,
    prog: str | None = None,
    formatter_class: type | None = None,
) -> argparse.ArgumentParser:
    """
    Create and configure the argument parser for 'lib-structure'.

    This function can either add a subparser to an existing ArgumentParser
    (via `subparsers`) or create a standalone parser when called independently.
    Useful for modular CLI designs.

    Parameters
    ----------
    subparsers : argparse._SubParsersAction, optional
        Subparsers object from the main parser to which this parser should be added.
        If None, a standalone ArgumentParser is created instead.
    prog : str, optional
        The program name used in standalone mode. Ignored if `subparsers` is provided.
    formatter_class : type, optional
        The formatter class to be used for argument help formatting. Defaults to
        argparse.ArgumentDefaultsHelpFormatter.

    Returns
    -------
    argparse.ArgumentParser
        The configured argument parser (necessary esp. for standalone mode).
    """
    parser_options = {
        "description": "Scan the structure of a library.",
        "formatter_class": formatter_class or argparse.ArgumentDefaultsHelpFormatter,
    }
    if subparsers:
        parser = subparsers.add_parser(
            "lib-structure", help=parser_options["description"], **parser_options
        )
    else:
        parser = argparse.ArgumentParser(prog=prog, **parser_options)

    parser.add_argument(
        "library",
        type=Path,
        help="Path to the library directory.",
    )
    parser.add_argument(
        "--extensions",
        metavar="EXTENSION",
        nargs="+",
        default=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"],
        help="File extensions to include.",
    )
    parser.add_argument(
        "--print",
        dest="show",
        action="store_true",
        help="Print results to the console.",
    )
    parser.add_argument(
        "--json", metavar="FILE", type=Path, help="Path to output JSON file."
    )
    parser.add_argument(
        "--csv", metavar="FILE", type=Path, help="Path to output CSV file."
    )

    return parser


def get_mux_audio_tracks_parser(
    subparsers: argparse._SubParsersAction | None = None,
    prog: str | None = None,
    formatter_class: type | None = None,
) -> argparse.ArgumentParser:
    """
    Create and configure the argument parser for 'mux-audio-tracks'.

    This function can either add a subparser to an existing ArgumentParser
    (via `subparsers`) or create a standalone parser when called independently.
    Useful for modular CLI designs.

    Parameters
    ----------
    subparsers : argparse._SubParsersAction, optional
        Subparsers object from the main parser to which this parser should be added.
        If None, a standalone ArgumentParser is created instead.
    prog : str, optional
        The program name used in standalone mode. Ignored if `subparsers` is provided.
    formatter_class : type, optional
        The formatter class to be used for argument help formatting. Defaults to
        argparse.ArgumentDefaultsHelpFormatter.

    Returns
    -------
    argparse.ArgumentParser
        The configured argument parser (necessary esp. for standalone mode).
    """
    parser_options = {
        "description": "Mux multiple audio tracks into one video file using FFmpeg.",
        "formatter_class": formatter_class or argparse.ArgumentDefaultsHelpFormatter,
    }

    if subparsers:
        parser = subparsers.add_parser(
            "mux-audio-tracks", help=parser_options["description"], **parser_options
        )
    else:
        parser = argparse.ArgumentParser(prog=prog, **parser_options)

    parser.add_argument(
        "output",
        type=Path,
        help="Output file (e.g. output.mp4)",
    )

    parser.add_argument(
        "inputs",
        nargs="+",
        help=(
            "Pairs or triplets of inputs: input_file lang [title]. "
            "Example: video_en.mp4 eng 'English Audio' video_de.mp4 deu 'Deutsch'"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print ffmpeg command without executing.",
    )

    return parser


def get_resolution_parser(
    subparsers: argparse._SubParsersAction | None = None,
    prog: str | None = None,
    formatter_class: type | None = None,
) -> argparse.ArgumentParser:
    """
    Create and configure the argument parser for 'srt-tools'.

    This function can either add a subparser to an existing ArgumentParser
    (via `subparsers`) or create a standalone parser when called independently.
    Useful for modular CLI designs.

    Parameters
    ----------
    subparsers : argparse._SubParsersAction, optional
        Subparsers object from the main parser to which this parser should be added.
        If None, a standalone ArgumentParser is created instead.
    prog : str, optional
        The program name used in standalone mode. Ignored if `subparsers` is provided.
    formatter_class : type, optional
        The formatter class to be used for argument help formatting. Defaults to
        argparse.ArgumentDefaultsHelpFormatter.

    Returns
    -------
    argparse.ArgumentParser
        The configured argument parser (necessary esp. for standalone mode).
    """
    parser_options = {
        "description": "Get the video resolution for a file or URL.",
        "formatter_class": formatter_class or argparse.ArgumentDefaultsHelpFormatter,
    }
    if subparsers:
        parser = subparsers.add_parser(
            "resolution", help=parser_options["description"], **parser_options
        )
    else:
        parser = argparse.ArgumentParser(prog=prog, **parser_options)

    parser.add_argument(
        "path_or_url",
        type=str,
        help="Path or URL to the video.",
    )

    return parser


def get_rename_parser(
    subparsers: argparse._SubParsersAction | None = None,
    prog: str | None = None,
    formatter_class: type | None = None,
) -> argparse.ArgumentParser:
    """
    Create and configure the argument parser for 'srt-tools'.

    This function can either add a subparser to an existing ArgumentParser
    (via `subparsers`) or create a standalone parser when called independently.
    Useful for modular CLI designs.

    Parameters
    ----------
    subparsers : argparse._SubParsersAction, optional
        Subparsers object from the main parser to which this parser should be added.
        If None, a standalone ArgumentParser is created instead.
    prog : str, optional
        The program name used in standalone mode. Ignored if `subparsers` is provided.
    formatter_class : type, optional
        The formatter class to be used for argument help formatting. Defaults to
        argparse.ArgumentDefaultsHelpFormatter.

    Returns
    -------
    argparse.ArgumentParser
        The configured argument parser (necessary esp. for standalone mode).
    """
    parser_options = {
        "description": (
            "USE CAREFULLY! Rename/move files according to the mapping given by a file."
        ),
        "formatter_class": formatter_class or argparse.ArgumentDefaultsHelpFormatter,
    }
    if subparsers:
        parser = subparsers.add_parser(
            "rename", help=parser_options["description"], **parser_options
        )
    else:
        parser = argparse.ArgumentParser(prog=prog, **parser_options)

    parser.add_argument(
        "file",
        type=Path,
        help="JSON file containing the renaming mapping (see 'scan --name').",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Do not create *.bak files containing the original filename.",
    )

    return parser


def get_scan_library_parser(
    subparsers: argparse._SubParsersAction | None = None,
    prog: str | None = None,
    formatter_class: type | None = None,
) -> argparse.ArgumentParser:
    """
    Create and configure the argument parser for 'scan'.

    This function can either add a subparser to an existing ArgumentParser
    (via `subparsers`) or create a standalone parser when called independently.
    Useful for modular CLI designs.

    Parameters
    ----------
    subparsers : argparse._SubParsersAction, optional
        Subparsers object from the main parser to which this parser should be added.
        If None, a standalone ArgumentParser is created instead.
    prog : str, optional
        The program name used in standalone mode. Ignored if `subparsers` is provided.
    formatter_class : type, optional
        The formatter class to be used for argument help formatting. Defaults to
        argparse.ArgumentDefaultsHelpFormatter.

    Returns
    -------
    argparse.ArgumentParser
        The configured argument parser (necessary esp. for standalone mode).
    """
    parser_options = {
        "description": "Scan videos of a library, e.g. for audio and subtitle tracks.",
        "formatter_class": formatter_class or argparse.ArgumentDefaultsHelpFormatter,
    }
    if subparsers:
        parser = subparsers.add_parser(
            "scan", help=parser_options["description"], **parser_options
        )
    else:
        parser = argparse.ArgumentParser(prog=prog, **parser_options)

    parser.add_argument(
        "library",
        type=Path,
        help="Path to the video library directory.",
    )
    parser.add_argument(
        "--extensions",
        metavar="EXTENSION",
        nargs="+",
        default=[".mp4", ".mkv", ".avi", ".mov"],
        help="File extensions to include.",
    )
    parser.add_argument(
        "--print",
        dest="show",
        action="store_true",
        help="Print results to the console.",
    )
    parser.add_argument(
        "--json", metavar="FILE", type=Path, help="Path to output JSON file."
    )
    parser.add_argument(
        "--csv", metavar="FILE", type=Path, help="Path to output CSV file."
    )
    parser.add_argument(
        "--name",
        metavar="FILE",
        type=Path,
        help=(
            "Path to output JSON file for name suggestions (no names will be suggested "
            "if not specified)."
        ),
    )
    parser.add_argument(
        "-l",
        "--default-language",
        dest="default_language",
        metavar="LANGUAGE_ID",
        type=str,
        default="??",
        help="Language identifier used for undefined languages.",
    )

    return parser


def get_set_language_parser(
    subparsers: argparse._SubParsersAction | None = None,
    prog: str | None = None,
    formatter_class: type | None = None,
) -> argparse.ArgumentParser:
    """
    Create and configure the argument parser for 'set-language'.

    This function can either add a subparser to an existing ArgumentParser
    (via `subparsers`) or create a standalone parser when called independently.
    Useful for modular CLI designs.

    Parameters
    ----------
    subparsers : argparse._SubParsersAction, optional
        Subparsers object from the main parser to which this parser should be added.
        If None, a standalone ArgumentParser is created instead.
    prog : str, optional
        The program name used in standalone mode. Ignored if `subparsers` is provided.
    formatter_class : type, optional
        The formatter class to be used for argument help formatting. Defaults to
        argparse.ArgumentDefaultsHelpFormatter.

    Returns
    -------
    argparse.ArgumentParser
        The configured argument parser (necessary esp. for standalone mode).
    """
    parser_options = {
        "description": "Set audio and subtitle language metadata.",
        "formatter_class": formatter_class or argparse.ArgumentDefaultsHelpFormatter,
    }
    if subparsers:
        parser = subparsers.add_parser(
            "set-language", help=parser_options["description"], **parser_options
        )
    else:
        parser = argparse.ArgumentParser(prog=prog, **parser_options)

    parser.add_argument("input_file", type=Path, help="Input video file.")
    parser.add_argument("output_file", type=Path, help="Output video file.")
    parser.add_argument(
        "--audio-lang",
        metavar="LANGUAGE",
        nargs="+",
        required=True,
        help="Audio languages (e.g., deu eng).",
    )
    parser.add_argument(
        "--subtitle-lang",
        metavar="LANGUAGE",
        nargs="*",
        default=[],
        help="Subtitle languages (optional).",
    )
    parser.add_argument(
        "--audio-title",
        metavar="TITLE",
        nargs="*",
        help="Optional titles for audio tracks.",
    )
    parser.add_argument(
        "--subtitle-title",
        metavar="TITLE",
        nargs="*",
        help="Optional titles for subtitle tracks.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print ffmpeg command without executing.",
    )

    return parser


def get_srt_tool_parser(
    subparsers: argparse._SubParsersAction | None = None,
    prog: str | None = None,
    formatter_class: type | None = None,
) -> argparse.ArgumentParser:
    """
    Create and configure the argument parser for 'srt-tools'.

    This function can either add a subparser to an existing ArgumentParser
    (via `subparsers`) or create a standalone parser when called independently.
    Useful for modular CLI designs.

    Parameters
    ----------
    subparsers : argparse._SubParsersAction, optional
        Subparsers object from the main parser to which this parser should be added.
        If None, a standalone ArgumentParser is created instead.
    prog : str, optional
        The program name used in standalone mode. Ignored if `subparsers` is provided.
    formatter_class : type, optional
        The formatter class to be used for argument help formatting. Defaults to
        argparse.ArgumentDefaultsHelpFormatter.

    Returns
    -------
    argparse.ArgumentParser
        The configured argument parser (necessary esp. for standalone mode).
    """
    parser_options = {
        "description": "Shift timestamps of a SRT file.",
        "formatter_class": formatter_class or argparse.ArgumentDefaultsHelpFormatter,
    }
    if subparsers:
        parser = subparsers.add_parser(
            "srt-tools", help=parser_options["description"], **parser_options
        )
    else:
        parser = argparse.ArgumentParser(prog=prog, **parser_options)

    parser.add_argument("input_file", help="Original SRT file.")
    parser.add_argument(
        "-s",
        "--shift",
        metavar="SECONDS",
        type=float,
        required=True,
        help="Timeshift in seconds (e.g. 1.5 or -0.8).",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        dest="output_file",
        help="Output SRT file (if not provided: stdout or --inplace).",
    )
    parser.add_argument(
        "--inplace",
        action="store_true",
        help="Overwrite original file (a backup will be created).",
    )
    parser.add_argument(
        "--show-count",
        action="store_true",
        help="Show number of changed timestamps.",
    )

    return parser


def main() -> None:
    """Run main CLI programm."""
    formatter_class = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(
        prog="vidmux",
        description="Inspect and modify video/audio/subtitle tracks using FFmpeg.",
        formatter_class=formatter_class,
    )
    subparsers = parser.add_subparsers(dest="feature")

    feature_parsers = (
        get_library_structur_parser,
        get_mux_audio_tracks_parser,
        get_rename_parser,
        get_resolution_parser,
        get_scan_library_parser,
        get_set_language_parser,
        get_srt_tool_parser,
    )
    for feature_parser in feature_parsers:
        feature_parser(subparsers, formatter_class=formatter_class)

    args = parser.parse_args()
    match args.feature:
        case "lib-structure":
            scan_library_structure(
                args.library,
                args.extensions,
                show=args.show,
                json_file=args.json,
                csv_file=args.csv,
            )
        case "mux-audio-tracks":
            mux_audio_tracks(args.output, args.inputs, dry_run=args.dry_run)
        case "rename":
            rename_mode(args.file, backup=not args.no_backup)
        case "resolution":
            resolution = get_video_resolution(args.path_or_url)
            print(f"Video resolution of '{args.path_or_url}':\n{resolution}")
        case "scan":
            scan_mode(
                args.library,
                args.extensions,
                show=args.show,
                json_file=args.json,
                csv_file=args.csv,
                name_file=args.name,
                default_language=args.default_language,
            )
        case "set-language":
            set_languages(
                input_file=args.input_file,
                output_file=args.output_file,
                audio_languages=args.audio_lang,
                subtitle_languages=args.subtitle_lang,
                audio_titles=args.audio_title,
                subtitle_titles=args.subtitle_title,
                dry_run=args.dry_run,
            )
        case "srt-tools":
            srt_tools.process_file(
                args.input_file,
                args.shift,
                inplace=args.inplace,
                output_file=args.output_file,
                show_count=args.show_count,
            )
        case _:
            parser.print_help()
            parser.exit(message="Run again and specify a supported command.")
