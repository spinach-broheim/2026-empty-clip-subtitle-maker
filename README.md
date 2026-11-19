# VTT Silence Filler

A Python script that inserts `There are no spoken words in the clip.` cues into
every non-subtitled part of a VTT file.

## Requirements

- Python 3 (no third-party dependencies)

## Usage

```
python3 fill_silences.py <input.vtt> [options]
```

The filled subtitles are written to stdout by default.

### Options

python3 fill_silences.py movie_silences_oej.vtt -o output.vtt

python fill_silences.py movie_silences_oej.vtt -o oej333.vtt --end 00:11:06.000

| Option | Description |
| --- | --- |
| `-o, --output <file.vtt>` | Write the result to a file instead of stdout. |
| `--end HH:MM:SS.mmm` | Also fill the trailing silence after the last spoken subtitle, up to this end time. Also accepts `MM:SS.mmm`. |

## Example

This is the file `test_input.vtt`:

```
WEBVTT

00:00:38.499 --> 00:00:40.719
I will miss you very much.

00:00:40.743 --> 00:00:46.306
But I will write you every day.
```

Run:

```
python3 fill_silences.py test_input.vtt -o output.vtt
```

Result (`output.vtt`):

```
WEBVTT

00:00:00.000 --> 00:00:38.498
There are no spoken words in the clip.

00:00:38.499 --> 00:00:40.719
I will miss you very much.

00:00:40.720 --> 00:00:40.742
There are no spoken words in the clip.

00:00:40.743 --> 00:00:46.306
But I will write you every day.
```

## OEdipe-style files

Files exported with OEdipe use `MM:SS.mmm` timestamps, a `WEBVTT FILE` header,
and a cue number on its own line before each cue — exactly like
`movie_silences_oej.vtt`. These are parsed the same way, no conversion needed:

```
WEBVTT FILE

1
00:38.499 --> 00:40.719
I will miss you very much.
```

Run the script straight against it:

```
python3 fill_silences.py movie_silences_oej.vtt -o output.vtt
```

The output keeps the original header, drops the cue-number lines, and fills all
silent gaps (e.g. `00:00:40.720 --> 00:00:40.742` between the first two cues).

## Behavior

- Fills silence from `00:00:00.000` up to the first spoken cue.
- Fills every gap between cues, running `prev_end + 1ms` to `next_start - 1ms`.
- Skips gaps too small to contain a valid cue.
- Fills the trailing silence only when `--end` is provided.
- Preserves the header and any non-cue lines after the last cue.
- Accepts timestamps as `HH:MM:SS.mmm` or `MM:SS.mmm`, with `.` or `,` as the
  millisecond separator.
- Cue-number lines (bare integers directly above a timestamp line) are skipped.# 2026-empty-clip-subtitle-maker
