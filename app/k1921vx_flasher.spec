# -*- mode: python ; coding: utf-8 -*-
import sys

datas = [
    ("view/ui", "view/ui"),
]

hiddenimports = [
    "PyQt5.QtPrintSupport",
    "serial.tools.list_ports",
]

a = Analysis(
    ["k1921vx_flasher.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

icon = "view/ui/flasher.ico" if sys.platform.startswith("win") else None

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="k1921vk_flasher",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon,
)
