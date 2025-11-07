# vidmux

[![PyPi badge](https://img.shields.io/pypi/v/vidmux)](https://pypi.org/project/vidmux/)
[![Python versions badge](https://img.shields.io/pypi/pyversions/vidmux.svg)](https://pypi.org/project/vidmux/)
[![License badge](https://img.shields.io/pypi/l/vidmux.svg)](https://github.com/PhilippMeder/vidmux/blob/main/LICENSE)
[![GitHub issues badge](https://img.shields.io/badge/issue_tracking-github-blue.svg)](https://github.com/PhilippMeder/vidmux/issues)
<!--- [![GitHub actions status badge](https://github.com/PhilippMeder/vidmux/actions/workflows/test-python-package.yml/badge.svg)](https://github.com/PhilippMeder/vidmux/actions/workflows/test-python-package.yml) --->

**Inspect and modify video/audio/subtitle tracks using FFmpeg.**

Developed and maintained by [Philipp Meder](https://github.com/PhilippMeder).

- **Source code**: https://github.com/PhilippMeder/vidmux.git
- **Report bugs**: https://github.com/PhilippMeder/vidmux/issues

## Quick Start

Install this package:

```bash
pip install vidmux
```

You can get the newest stable version with:

```bash
pip install git+https://github.com/philippmeder/vidmux
```

## License

Distributed under the [BSD 3-Clause License](https://github.com/PhilippMeder/vidmux/blob/main/LICENSE).

## Usage

You may directly call one of the two following lines:
```bash
vidmux [OPTIONS]
python -m vidmux [OPTIONS]
```

## Features

For a full list of features, use:
```bash
vidmux --help
```
1. [Get codecs and audio/subtitle tracks](#scan-for-codecs-audio-and-subtitle-tracks)
2. [Mux audio tracks](#mux-audio-tracks)
3. [Set audio/subtitle metadata](#set-audio-and-subtitle-metadata)
4. [Scan library structure](#scan-for-issues-in-the-library-structure)
5. [Get video resolution](#get-video-resolution)
6. [Rename files](#rename-files)
7. [Shift SRT timestamps](#shift-srt-timestamps)

### Scan for codecs, audio and subtitle tracks

Scan the video files of a library for video/audio codecs and the included audio and subtitle tracks.

```bash
vidmux scan [-h] [--extensions EXTENSION [EXTENSION ...]] [--print] [--json FILE] [--csv FILE] [--name FILE] [-l LANGUAGE_ID] library
```

Options:

- `library` (positional): Path to the video library directory.
- `--extensions`: Specify (multiple) file extensions to include in the scan.
- `--print`: Print the results to the console/terminal.
- `--json`: Specify a JSON file where the results should be saved.
- `--csv`: Specify a CSV file where the results should be saved.
- `--name`: Specify a JSON file where name suggestions will be stored (required for the `rename` feature).
- `-l, --default-language`: Language identifier that will be used to interpret undefined languages of audio/subtitle tracks (currently only applied for naming suggestions).

### Mux audio tracks

Mux multiple audio tracks into one video file using FFmpeg.

```bash
vidmux mux-audio-tracks [-h] [--dry-run] output inputs [inputs ...]
```

Options:

- `output` (positional): Specify the output file.
- `inputs` (positional): Pairs or triplets of inputs: `input_file lang [title]`.

    > Example: `video_en.mp4 eng video_commentary_en.mp4 eng 'English Commentary' video_de.mp4 deu`
- `--dry-run`: Print the ffmpeg command without executing it.

### Set audio and subtitle metadata

Set the metadata, i.e. language and title, for audio and subtitle tracks.

```bash
vidmux set-language [-h] --audio-lang LANGUAGE [LANGUAGE ...] [--subtitle-lang [LANGUAGE ...]]
[--audio-title [TITLE ...]]
[--subtitle-title [TITLE ...]]
[--dry-run]
input_file output_file
```

Options:

- `--audio-lang`: List of language identifiers corresponding to the audio tracks, e.g. `deu eng`.
- `--subtitle-lang`: List of language identifiers corresponding to the subtitle tracks, e.g. `deu eng`.
- `--audio-title`: List of titles corresponding to the audio tracks.
- `--subtitle-title`: List of titles corresponding to the audio tracks.
- `--dry-run`: Print the ffmpeg command without executing it.

### Scan for issues in the library structure

Scan and find issues in the structure of a movie library. Following rules are currently used:

- Every movie should be in an appropriate subfolder with corresponding name, e.g. `Seven Samurai (1954)/Seven Samurai (1954).mp4`. It is okay to have multiple versions or parts in the same folder as long as the basic name does not change. Example:
    ```md
    movie-library/Blade Runner (1982)
    ├── Blade Runner (1982) - [1080p].mp4
    ├── Blade Runner (1982) - [480p].mp4
    ├── Blade Runner (1982) - Director's Cut.mp4
    └── Blade Runner (1982) - Final Cut.mp4
    ```
- Every movie should include a publishing year, e.g. `Paris, Texas (1984).mp4`.
- The usual suspects of special characters are not allowed in the filename, i.e. `<>:"/\\|?*`.

```bash
vidmux lib-structure [-h] [--extensions EXTENSION [EXTENSION ...]] [--print] [--json FILE] [--csv FILE] library
```

Options:

- `library` (positional): Path to the video library directory.
- `--extensions`: Specify (multiple) file extensions to include in the scan.
- `--print`: Print the results to the console/terminal.
- `--json`: Specify a JSON file where the results should be saved.
- `--csv`: Specify a CSV file where the results should be saved.

### Get video resolution

Inspect and show the video resolution of a video file (supports URL).

```bash
vidmux resolution [-h] path_or_url
```

### Rename files

Rename files according to a mapping given by a file (use `vidmux scan --name`).

```bash
vidmux rename [-h] [--no-backup] file
```

Options:

- `--no-backup`: Prevent the creation of a file containing the original filename (so you can revoke the process).

### Shift SRT timestamps

Shift all timestamps in a SRT subtitle file.

```bash
vidmux srt-tools [-h] -s SECONDS [-o FILE] [--inplace] [--show-count] input_file
```

Options:

- `-s, --shift`: Timeshift in seconds (e.g. 1.5 or -0.8).
- `-o, --output`: Output SRT file (if not provided: stdout or `--inplace`)
- `--inplace`: Overwrite original file (a backup will be created).
- `--show-count`: Show number of changed timestamps.

## Requirements

- `ffmpeg` with `ffprobe` has to be installed