# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec 파일
# 빌드: pyinstaller build.spec

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
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
    console=False,  # GUI 앱이므로 콘솔 숨김
    icon=None,      # 아이콘 있으면 'assets/icon.ico' 지정
)
