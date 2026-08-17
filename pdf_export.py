# ============================================================================
# PDF EXPORT (graceful degradation)
# File: pdf_export.py
# Roadmap item: PDF output macro.
#
# Converts a generated .docx into PDF using LibreOffice headless
# (soffice --convert-to pdf).  Requires LibreOffice on the system:
#   Ubuntu/Debian:  sudo apt-get install -y libreoffice-writer
#   macOS:          brew install --cask libreoffice
#   Windows:        https://www.libreoffice.org/download/
# When LibreOffice is missing the module reports a clear, actionable
# error — the Word export keeps working normally.
# ============================================================================

import shutil
import subprocess
from pathlib import Path
from typing import Dict, Optional


def libreoffice_available() -> bool:
    return shutil.which("soffice") is not None or \
        shutil.which("libreoffice") is not None


def check_libreoffice() -> str:
    if libreoffice_available():
        return ""
    return ("PDF export is not available: LibreOffice was not found on "
            "this system.\n\n"
            "Install it with one of:\n"
            "  Ubuntu/Debian:  sudo apt-get install -y libreoffice-writer\n"
            "  macOS:          brew install --cask libreoffice\n"
            "  Windows:        https://www.libreoffice.org/download/\n\n"
            "Then run: python3 pdf_export.py <file.docx>")


def docx_to_pdf(docx_path: str, out_dir: Optional[str] = None) -> Dict:
    """Convert a .docx to .pdf via LibreOffice headless.

    Returns {ok, pdf_path, error}."""
    src = Path(docx_path)
    if not src.exists():
        return {"ok": False, "error": f"file not found: {docx_path}"}
    if src.suffix.lower() != ".docx":
        return {"ok": False, "error": "input must be a .docx file"}
    err = check_libreoffice()
    if err:
        return {"ok": False, "error": err}
    out = Path(out_dir) if out_dir else src.parent
    out.mkdir(parents=True, exist_ok=True)
    try:
        r = subprocess.run(
            ["soffice", "--headless", "--convert-to", "pdf",
             "--outdir", str(out), str(src)],
            capture_output=True, text=True, timeout=300)
        if r.returncode != 0:
            return {"ok": False, "error": f"soffice failed: "
                                           f"{r.stderr[-300:]}"}
    except FileNotFoundError:
        return {"ok": False, "error": check_libreoffice()}
    pdf = out / (src.stem + ".pdf")
    if not pdf.exists():
        return {"ok": False, "error": "soffice finished without producing "
                                      "the PDF"}
    return {"ok": True, "pdf_path": str(pdf),
            "size": pdf.stat().st_size}


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _selftest():
    err = check_libreoffice()
    if err:
        print("  ✔ pdf selftest: LibreOffice missing — graceful error path OK")
        assert "apt-get" in err
        assert docx_to_pdf("/tmp/nope.docx")["ok"] is False
    else:
        print("  ✔ pdf selftest: LibreOffice available (skipped conversion)")
    print("pdf_export OK (graceful)")


if __name__ == "__main__":
    import sys as _sys
    if len(_sys.argv) > 1:
        print(docx_to_pdf(_sys.argv[1]))
    else:
        _selftest()
