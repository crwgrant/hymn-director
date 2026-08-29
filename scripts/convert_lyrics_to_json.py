#!/usr/bin/env python3
"""Convert ldshymnlyrics text files into JSON hymn collections."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LYRICS_DIR = ROOT / "ldshymnlyrics"
HYMNS_OUTPUT = ROOT / "lds_hymns.json"
CHILDRENS_OUTPUT = ROOT / "childrens_songbook.json"

HYMN_FILENAME = re.compile(r"^_?(?P<number>\d+)\s+(?P<title>.+)\.txt$")
CHILDREN_FILENAME = re.compile(r"^(?P<number>\d+)_(?P<title>.+)\.txt$")


def parse_verses(text: str) -> list[str]:
    verses = [part.strip() for part in text.split("###")]
    return [verse for verse in verses if verse]


def parse_hymn_file(path: Path, filename_pattern: re.Pattern[str]) -> dict:
    match = filename_pattern.match(path.name)
    if not match:
        raise ValueError(f"Unexpected filename format: {path.name}")

    return {
        "number": int(match.group("number")),
        "title": match.group("title"),
        "verses": parse_verses(path.read_text(encoding="utf-8")),
    }


def collect_hymns(directory: Path, filename_pattern: re.Pattern[str]) -> list[dict]:
    hymns: list[dict] = []
    for path in sorted(directory.glob("*.txt")):
        hymns.append(parse_hymn_file(path, filename_pattern))
    return hymns


def main() -> int:
    hymns = collect_hymns(LYRICS_DIR, HYMN_FILENAME)
    childrens_songs = collect_hymns(LYRICS_DIR / "childrenssongbook", CHILDREN_FILENAME)

    HYMNS_OUTPUT.write_text(
        json.dumps(hymns, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    CHILDRENS_OUTPUT.write_text(
        json.dumps(childrens_songs, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {len(hymns)} hymns to {HYMNS_OUTPUT.name}")
    print(f"Wrote {len(childrens_songs)} songs to {CHILDRENS_OUTPUT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
