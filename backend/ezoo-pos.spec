# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for EZOO POS backend.
# Run from backend/:  pyinstaller ezoo-pos.spec --clean --noconfirm

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

datas = [
    ("app/static", "app/static"),          # Cairo fonts + logo images
    ("alembic", "alembic"),                # env.py + versions/ (27 migration files)
    ("alembic.ini", "."),
    ("../frontend/out", "frontend_out"),   # static export from Phase 2
]
datas += collect_data_files("reportlab")   # AFM font metrics
datas += collect_data_files("arabic_reshaper")

hiddenimports = [
    "aiosqlite",
    "sqlalchemy.dialects.sqlite",
    "sqlalchemy.dialects.sqlite.aiosqlite",
    "uvicorn.lifespan.on",
    "uvicorn.lifespan.off",
    "uvicorn.loops.auto",
    "uvicorn.loops.asyncio",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.http.h11_impl",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.protocols.websockets.websockets_impl",
    "uvicorn.logging",
    "arabic_reshaper",
    "bidi.algorithm",
    "xlsxwriter",
]
hiddenimports += collect_submodules("app.modules")  # routers imported dynamically

a = Analysis(
    ["main.py"],
    pathex=["."],
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=[
        "tkinter",
        "matplotlib",
        "pandas",
        "pytest",
        "pytest_asyncio",
        "watchfiles",
        "IPython",
        "notebook",
        "jupyter",
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ezoo-pos",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # set False for production; True during Phase 3 debugging
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
    name="ezoo-pos",
)
