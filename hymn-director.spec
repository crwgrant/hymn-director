# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

project_root = Path(SPECPATH)
entry_script = project_root / "src" / "hymn_director" / "__main__.py"
bundled_db = project_root / "data" / "hymns.db"

datas = []
if bundled_db.exists():
    datas.append((str(bundled_db), "data"))

a = Analysis(
    [str(entry_script)],
    pathex=[str(project_root / "src")],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "hymn_director",
        "hymn_director.app",
        "hymn_director.add_hymn_window",
        "hymn_director.settings_window",
        "hymn_director.display_config",
        "hymn_director.database",
        "hymn_director.paths",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="HymnDirector",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="HymnDirector",
)

import sys

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="HymnDirector.app",
        icon=None,
        bundle_identifier="org.hymn-director.app",
    )
