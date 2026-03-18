# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file
# Build: pyinstaller build.spec

import os
import customtkinter

ctk_path = os.path.dirname(customtkinter.__file__)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[(ctk_path, 'customtkinter')],
    hiddenimports=['winotify', 'schedule', 'customtkinter'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='JobcanAlarm',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon=None,
)
