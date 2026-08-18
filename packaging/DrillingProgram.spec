# -*- mode: python ; coding: utf-8 -*-
# ============================================================================
# PyInstaller spec — Drilling Program & Procedure Generator
# Build a single-folder Windows/Linux/macOS distribution:
#   pip install pyinstaller
#   pyinstaller packaging/DrillingProgram.spec
#
# Output: dist/DrillingProgram/DrillingProgram(.exe) + bundled library
# ============================================================================

import os
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# the internal knowledge library must ship inside the bundle
library_datas = collect_data_files("programs", include_py_files=False)

a = Analysis(
    ["../launcher.py"],
    pathex=[".."],
    binaries=[],
    datas=library_datas + [("../programs/library", "programs/library")],
    hiddenimports=[
        # database / document / API modules pulled in lazily at runtime
        "procedures_db", "cbs_db", "drilling_problems_db", "well_model",
        "document_catalog", "master_procedures", "time_breakdown",
        "operations_engine", "wizard_library", "wizard_procedures",
        "wizard_offshore", "wizard_master", "wizard_references",
        "wizard_knowledge", "wizard_rope", "wizard_llm", "wizard_web",
        "wizard_risk", "word_generator", "integrations", "backup_restore",
        "audit_log", "rbac", "validation_engine", "standards_engine",
        "document_compliance", "engineering_units",
        "engineering_advanced", "engineering_deep", "engineering_register",
        "engineering_hydraulics", "engineering_wellcontrol",
        "engineering_geomechanics", "engineering_casing",
        "engineering_anticollision", "engineering_decisions",
        "engineering_sensitivity", "engineering_special",
        "engineering_cementing", "planning_intelligence",
        "risk_decision", "entity_scrub", "structured_steps",
        "generation_pipeline", "well_report", "witsml_export",
        "witsml_import", "iadc_dull", "reporting", "api_server",
        "docx", "openpyxl", "cryptography",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "PySide6.QtWebEngineCore", "PySide6.Qt3D*"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="DrillingProgram",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # GUI app — no console window on Windows
    icon=None,              # provide an .ico for a branded installer
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="DrillingProgram",
)
