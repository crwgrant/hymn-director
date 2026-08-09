"""SQLite database layer for hymn and verse storage."""

from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS hymns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    number INTEGER
);

CREATE TABLE IF NOT EXISTS verses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hymn_id INTEGER NOT NULL,
    verse_number INTEGER NOT NULL,
    text TEXT NOT NULL,
    FOREIGN KEY (hymn_id) REFERENCES hymns(id),
    UNIQUE (hymn_id, verse_number)
);
"""

SAMPLE_HYMNS = [
    {
        "title": "Amazing Grace",
        "number": 1,
        "verses": [
            "Amazing grace! How sweet the sound\nThat saved a wretch like me!\nI once was lost, but now am found;\nWas blind, but now I see.",
            "'Twas grace that taught my heart to fear,\nAnd grace my fears relieved;\nHow precious did that grace appear\nThe hour I first believed.",
            "Through many dangers, toils and snares,\nI have already come;\n'Tis grace hath brought me safe thus far,\nAnd grace will lead me home.",
            "When we've been there ten thousand years,\nBright shining as the sun,\nWe've no less days to sing God's praise\nThan when we'd first begun.",
        ],
    },
    {
        "title": "Holy, Holy, Holy",
        "number": 2,
        "verses": [
            "Holy, holy, holy! Lord God Almighty!\nEarly in the morning our song shall rise to thee;\nHoly, holy, holy, merciful and mighty!\nGod in three Persons, blessed Trinity!",
            "Holy, holy, holy! All the saints adore thee,\nCasting down their golden crowns around the glassy sea;\nCherubim and seraphim falling down before thee,\nWhich wert, and art, and evermore shalt be.",
            "Holy, holy, holy! Though the darkness hide thee,\nThough the eye of sinful man thy glory may not see;\nOnly thou art holy; there is none beside thee,\nPerfect in power, in love, and purity.",
            "Holy, holy, holy! Lord God Almighty!\nAll thy works shall praise thy name, in earth, and sky, and sea;\nHoly, holy, holy, merciful and mighty!\nGod in three Persons, blessed Trinity!",
        ],
    },
    {
        "title": "Be Thou My Vision",
        "number": 3,
        "verses": [
            "Be thou my vision, O Lord of my heart;\nNaught be all else to me, save that thou art.\nThou my best thought, by day or by night,\nWaking or sleeping, thy presence my light.",
            "Be thou my wisdom, and thou my true word;\nI ever with thee and thou with me, Lord.\nThou my great Father, and I thy true son;\nThou in me dwelling, and I with thee one.",
            "Riches I heed not, nor man's empty praise,\nThou mine inheritance, now and always.\nThou and thou only, first in my heart,\nHigh King of heaven, my treasure thou art.",
            "High King of heaven, my victory won,\nMay I reach heaven's joys, O bright heaven's Sun!\nHeart of my own heart, whatever befall,\nStill be my vision, O Ruler of all.",
        ],
    },
]


def db_path() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").exists():
            return parent / "data" / "hymns.db"
    return Path(__file__).resolve().parents[2] / "data" / "hymns.db"


DB_PATH = db_path()


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA)
        count = conn.execute("SELECT COUNT(*) FROM hymns").fetchone()[0]
        if count == 0:
            _seed_sample_data(conn)


def _seed_sample_data(conn: sqlite3.Connection) -> None:
    for hymn in SAMPLE_HYMNS:
        cursor = conn.execute(
            "INSERT INTO hymns (title, number) VALUES (?, ?)",
            (hymn["title"], hymn["number"]),
        )
        hymn_id = cursor.lastrowid
        for verse_number, text in enumerate(hymn["verses"], start=1):
            conn.execute(
                "INSERT INTO verses (hymn_id, verse_number, text) VALUES (?, ?, ?)",
                (hymn_id, verse_number, text),
            )
    conn.commit()


def list_hymns() -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, title, number FROM hymns ORDER BY number, title"
        ).fetchall()


def get_verse_count(hymn_id: int) -> int:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS count FROM verses WHERE hymn_id = ?",
            (hymn_id,),
        ).fetchone()
        return row["count"]


def get_verse(hymn_id: int, verse_number: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT v.verse_number, v.text, h.title
            FROM verses v
            JOIN hymns h ON h.id = v.hymn_id
            WHERE v.hymn_id = ? AND v.verse_number = ?
            """,
            (hymn_id, verse_number),
        ).fetchone()


def get_next_hymn_number() -> int:
    with get_connection() as conn:
        row = conn.execute("SELECT MAX(number) AS max_num FROM hymns").fetchone()
        max_num = row["max_num"]
        return (max_num or 0) + 1


def add_hymn(title: str, number: int | None, verses: list[str]) -> int:
    title = title.strip()
    if not title:
        raise ValueError("Title is required.")

    cleaned_verses = [text.strip() for text in verses if text.strip()]
    if not cleaned_verses:
        raise ValueError("At least one verse is required.")

    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO hymns (title, number) VALUES (?, ?)",
            (title, number),
        )
        hymn_id = cursor.lastrowid
        for verse_number, text in enumerate(cleaned_verses, start=1):
            conn.execute(
                "INSERT INTO verses (hymn_id, verse_number, text) VALUES (?, ?, ?)",
                (hymn_id, verse_number, text),
            )
        conn.commit()
        return hymn_id


def init_cli() -> None:
    init_database()
    hymns = list_hymns()
    print(f"Created database at {DB_PATH}")
    print(f"Loaded {len(hymns)} hymns")
