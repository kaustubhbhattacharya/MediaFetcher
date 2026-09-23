# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect extra data files and hidden submodules
customtkinter_datas = collect_data_files('customtkinter')
ytdlp_hiddenimports = collect_submodules('yt_dlp')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[('gallery-dl.exe', '.')],
    datas=[('favicon.ico', '.')] + customtkinter_datas,
    hiddenimports=ytdlp_hiddenimports,
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
    name='MediaFetcher',
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
    icon=['favicon.ico'],
)
