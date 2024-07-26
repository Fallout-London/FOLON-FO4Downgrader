# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ["FOLON-Downgrader.py"],
    pathex=[],
    binaries=[],
    datas=[("FOLON.css", "."), ("DepotsList.txt", "."), ("img/", "img/")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["img/FOLON4K.png", "img/FOLON_CoverBanner.png", "img/FOLONBackground.svg"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="FOLON-Downgrader",
    version="version.txt",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=["img/FOLON256.ico"],
)
