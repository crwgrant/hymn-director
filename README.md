# Hymn Director

Hymn Director is a desktop app for displaying hymn verses during congregational singing. The left side of the window holds controls; the right side shows the current hymn title and verse text on a black background suitable for projection.

## Requirements

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/) for dependency management

## Installation

Clone or download this project, then install dependencies:

```bash
cd hymn-director
uv sync
```

This creates a virtual environment in `.venv` and installs PyQt6.

## Running the app

```bash
uv run hymn-director
```

The window opens at a 2:1 width-to-height ratio by default. You can resize it as needed.

## Main window

The app is split into two halves:

- **Left panel** — hymn list, management buttons, verse navigation, and display settings
- **Right panel** — hymn title and verse text on a black background

### Select a hymn

The hymn list shows every hymn in the database, sorted by hymn number. Click a hymn to display it. The app starts on the first hymn in the list.

### Navigate verses

Use the verse buttons below the hymn list:

- **First Verse** — jump to verse 1
- **Previous Verse** — go back one verse
- **Next Verse** — advance one verse
- **Last Verse** — jump to the final verse

Buttons are disabled when that action is not available (for example, **Previous Verse** on verse 1).

## Add a hymn

1. Click **Add Hymn...**
2. Enter the hymn **title** and **number**
3. Enter one or more verses in the text fields
4. Use **Add Verse** or **Remove Last Verse** to adjust how many verses the hymn has
5. Click **Save Hymn**

Each hymn number must be unique. If you try to save a number that is already in use, the app shows an error.

The hymn list updates automatically and selects the hymn you just added.

## Delete a hymn

1. Select the hymn in the list
2. Click **Delete Hymn**
3. Confirm the deletion

This permanently removes the hymn and all of its verses from the database.

## Display settings

Click **Display Settings...** to change how text appears on the right panel:

| Setting | Description |
|---------|-------------|
| **Font** | Any font installed on your system |
| **Font size** | Text size in points |
| **Line spacing** | Space between lines, as a percentage of normal |
| **Letter spacing** | Extra space between characters, in pixels |
| **Word spacing** | Extra space between words, in pixels |

Click **Save** to apply changes. Settings are stored in `data/display_settings.json` and restored the next time you open the app.

## Data files

| File | Purpose |
|------|---------|
| `data/hymns.db` | SQLite database of hymns and verses |
| `data/display_settings.json` | Display font and spacing preferences |

On first run, the database is created automatically with sample hymns if it does not exist yet.

To recreate or seed the database manually:

```bash
uv run init-db
```

## Project layout

```
hymn-director/
├── data/                  # Database and settings (created at runtime)
├── src/hymn_director/     # Application source code
├── pyproject.toml
└── uv.lock
```
