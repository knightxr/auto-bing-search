# -*- mode: python ; coding: utf-8 -*-

app_name = "Auto Bing Search"
script = "auto_bing_search.py"

datas = [("assets", "assets")]

excludes = [
    "Quartz","AppKit","Foundation","CoreFoundation","objc",
    "Xlib","wmctrl","xdotool","PySide6.QtX11Extras","PySide6.QtWaylandCompositor",
    "PySide6.QtQml","PySide6.QtQuick","PySide6.QtQmlModels","PySide6.QtQmlWorkerScript",
    "PySide6.QtWebEngineCore","PySide6.QtWebEngineWidgets","PySide6.QtWebEngine",
    "PySide6.QtWebChannel","PySide6.Qt3DCore","PySide6.QtCharts",
    "PySide6.QtDataVisualization","PySide6.QtMultimedia","PySide6.QtOpenGL",
    "PySide6.QtPdf","PySide6.QtSvg","PySide6.QtDBus","PySide6.QtVirtualKeyboard",
]

a = Analysis(
    [script],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=["PySide6.QtCore","PySide6.QtGui","PySide6.QtWidgets"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon="assets/app.ico",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name=app_name,
)
