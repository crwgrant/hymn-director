# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

project_root = Path(SPECPATH)
entry_script = project_root / "src" / "hymn_director" / "__main__.py"
bundled_db = project_root / "data" / "hymns.db"
icons_dir = project_root / "assets" / "icons"
icon_ico = icons_dir / "hymn-director.ico"
icon_icns = icons_dir / "hymn-director.icns"
icon_png = icons_dir / "hymn-director-256.png"

datas = []
if bundled_db.exists():
    datas.append((str(bundled_db), "data"))
if icons_dir.exists():
    for png in sorted(icons_dir.glob("hymn-director-*.png")):
        datas.append((str(png), "assets/icons"))

icon_file = None
if sys.platform == "win32" and icon_ico.exists():
    icon_file = str(icon_ico)
elif sys.platform == "darwin" and icon_icns.exists():
    icon_file = str(icon_icns)

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
        "hymn_director.icon_utils",
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
    icon=icon_file,
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

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="HymnDirector.app",
        icon=str(icon_icns) if icon_icns.exists() else None,
        bundle_identifier="org.hymn-director.app",
    )
