"""SQLite database layer for hymn and verse storage."""

from __future__ import annotations

import sqlite3

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


from hymn_director.paths import db_path

DB_PATH = db_path()


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA)
        _migrate_unique_hymn_numbers(conn)
        count = conn.execute("SELECT COUNT(*) FROM hymns").fetchone()[0]
        if count == 0:
            _seed_sample_data(conn)


def _next_available_number(conn: sqlite3.Connection) -> int:
    used = {
        row[0]
        for row in conn.execute(
            "SELECT number FROM hymns WHERE number IS NOT NULL"
        ).fetchall()
    }
    candidate = 1
    while candidate in used:
        candidate += 1
    return candidate


def _migrate_unique_hymn_numbers(conn: sqlite3.Connection) -> None:
    duplicate_numbers = conn.execute(
        """
        SELECT number FROM hymns
        WHERE number IS NOT NULL
        GROUP BY number
        HAVING COUNT(*) > 1
        """
    ).fetchall()

    for row in duplicate_numbers:
        hymns = conn.execute(
            "SELECT id FROM hymns WHERE number = ? ORDER BY id",
            (row["number"],),
        ).fetchall()
        for hymn in hymns[1:]:
            new_number = _next_available_number(conn)
            conn.execute(
                "UPDATE hymns SET number = ? WHERE id = ?",
                (new_number, hymn["id"]),
            )

    conn.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_hymns_number
        ON hymns(number)
        WHERE number IS NOT NULL
        """
    )
    conn.commit()


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
        return _next_available_number(conn)


def hymn_number_exists(number: int, exclude_id: int | None = None) -> bool:
    with get_connection() as conn:
        if exclude_id is None:
            row = conn.execute(
                "SELECT 1 FROM hymns WHERE number = ? LIMIT 1",
                (number,),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT 1 FROM hymns WHERE number = ? AND id != ? LIMIT 1",
                (number, exclude_id),
            ).fetchone()
        return row is not None


def add_hymn(title: str, number: int | None, verses: list[str]) -> int:
    title = title.strip()
    if not title:
        raise ValueError("Title is required.")

    cleaned_verses = [text.strip() for text in verses if text.strip()]
    if not cleaned_verses:
        raise ValueError("At least one verse is required.")

    if number is not None and hymn_number_exists(number):
        raise ValueError(f"Hymn number {number} is already in use.")

    with get_connection() as conn:
        try:
            cursor = conn.execute(
                "INSERT INTO hymns (title, number) VALUES (?, ?)",
                (title, number),
            )
        except sqlite3.IntegrityError as error:
            raise ValueError(f"Hymn number {number} is already in use.") from error
        hymn_id = cursor.lastrowid
        for verse_number, text in enumerate(cleaned_verses, start=1):
            conn.execute(
                "INSERT INTO verses (hymn_id, verse_number, text) VALUES (?, ?, ?)",
                (hymn_id, verse_number, text),
            )
        conn.commit()
        return hymn_id


def get_hymn(hymn_id: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, title, number FROM hymns WHERE id = ?",
            (hymn_id,),
        ).fetchone()


def delete_hymn(hymn_id: int) -> None:
    with get_connection() as conn:
        row = conn.execute("SELECT id FROM hymns WHERE id = ?", (hymn_id,)).fetchone()
        if row is None:
            raise ValueError("Hymn not found.")
        conn.execute("DELETE FROM verses WHERE hymn_id = ?", (hymn_id,))
        conn.execute("DELETE FROM hymns WHERE id = ?", (hymn_id,))
        conn.commit()


def init_cli() -> None:
    init_database()
    hymns = list_hymns()
    print(f"Created database at {DB_PATH}")
    print(f"Loaded {len(hymns)} hymns")
