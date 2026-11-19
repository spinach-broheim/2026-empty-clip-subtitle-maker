#!/usr/bin/env python3
"""Fill the non-subtitled gaps in a VTT file with "no spoken words" cues."""

import argparse
import re
import sys

CUE_RE = re.compile(
    r"^\s*([0-9]+:[0-9]{2}(?::[0-9]{2})?[.,][0-9]{1,3})\s+-->\s+"
    r"([0-9]+:[0-9]{2}(?::[0-9]{2})?[.,][0-9]{1,3})"
)

NO_WORDS_TEXT = "There are no spoken words in the clip."


def parse_timestamp(ts):
    parts = ts.strip().replace(",", ".").split(":")
    h = 0
    if len(parts) == 3:
        h = int(parts[0])
        parts = parts[1:]
    m, rest = parts[0], parts[1]
    if "." in rest:
        sec, ms = rest.split(".")
    else:
        sec, ms = rest, "0"
    return (int(h) * 3600 + int(m) * 60 + int(sec)) * 1000 + int(ms)


def format_timestamp(ms):
    h, rem = divmod(ms, 3600000)
    m, rem = divmod(rem, 60000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def fmt_cue(start, end, text):
    return f"{format_timestamp(start)} --> {format_timestamp(end)}\n{text}"


def fill_silences(blocks, end_ms=None):
    """blocks: list of (start_ms, end_ms, cue_text[, other_marker_lines]).
    Returns text cue blocks to write (strings)."""
    out = []
    prev_end = -1
    for start, end, text in blocks:
        gap_start = prev_end + 1
        gap_end = start - 1
        if gap_end >= gap_start:
            out.append(fmt_cue(gap_start, gap_end, NO_WORDS_TEXT))
        out.append(fmt_cue(start, end, text))
        prev_end = end
    if end_ms is not None:
        gap_start = prev_end + 1
        if end_ms >= gap_start:
            out.append(fmt_cue(gap_start, end_ms, NO_WORDS_TEXT))
    return out


def parse_vtt(lines):
    lines = [ln.rstrip("\r\n") for ln in lines]
    header = []
    passthrough = []
    blocks = []
    found_cue = False
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        m = CUE_RE.match(line)
        if not m and line.strip().isdigit() and idx + 1 < len(lines) \
                and CUE_RE.match(lines[idx + 1]):
            idx += 1
            continue
        if m:
            found_cue = True
            start = parse_timestamp(m.group(1))
            end = parse_timestamp(m.group(2))
            idx += 1
            text = []
            while idx < len(lines) and lines[idx].strip() != "":
                text.append(lines[idx])
                idx += 1
            blocks.append((start, end, "\n".join(text)))
        else:
            if not found_cue:
                header.append(line)
            else:
                passthrough.append(line)
            idx += 1
    return header, passthrough, blocks


def main():
    ap = argparse.ArgumentParser(
        description="Insert 'There are no spoken words in the clip.' cues "
        "into the silent gaps of a VTT file."
    )
    ap.add_argument("input", help="Path to the input .vtt file")
    ap.add_argument(
        "-o", "--output", default=None,
        help="Path to the output .vtt file (default: print to stdout)",
    )
    ap.add_argument(
        "--end", default=None, metavar="HH:MM:SS.mmm",
        help="Optional end timestamp for the trailing silence after the "
        "last spoken subtitle.",
    )
    args = ap.parse_args()

    with open(args.input, "r", encoding="utf-8") as fh:
        lines = fh.readlines()

    end_ms = parse_timestamp(args.end.replace(",", ".")) if args.end else None

    header, passthrough, blocks = parse_vtt(lines)
    if not blocks:
        sys.exit("No subtitle cues found in input file.")

    filled = fill_silences(blocks, end_ms=end_ms)

    parts = []
    if header:
        header_block = "\n".join(header).rstrip("\n")
        if header_block:
            parts.append(header_block)
    parts.extend(filled)
    if passthrough:
        block = "\n".join(passthrough).rstrip("\n")
        if block:
            parts.append(block)
    body = "\n\n".join(parts) + "\n"

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(body)
    else:
        sys.stdout.write(body)


if __name__ == "__main__":
    main()