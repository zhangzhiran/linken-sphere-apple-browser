# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['simple_linken_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('linken_sphere_playwright_browser.py', '.'), ('linken_sphere_api.py', '.'), ('linken_sphere_config.json', '.')],
    hiddenimports=['tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.filedialog', 'requests', 'json', 'threading', 'asyncio', 'pathlib'],
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
    a.binaries,
    a.datas,
    [],
    name='LinkenSphereAppleBrowser',
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
    icon=['app_icon.icns'],
)
