# ============================================================================
# OCR INGEST PIPELINE (graceful degradation)
# File: ocr_ingest.py
# Roadmap item: OCR for scanned/image documents.
#
# Converts scanned PDFs and images into text and ingests them into the
# internal knowledge library (programs/library/ + document catalog).
#
# Requires the Tesseract OCR engine on the system:
#   Ubuntu/Debian:  sudo apt-get install -y tesseract-ocr
#   macOS:          brew install tesseract
#   Windows:        https://github.com/UB-Mannheim/tesseract/wiki
# When Tesseract is missing the module reports a clear, actionable error
# (the rest of the application keeps working normally).
# ============================================================================

import hashlib
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

LIBRARY_DIR = Path(__file__).parent / "programs" / "library"
SUPPORTED_IMAGES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}
SUPPORTED_PDF = {".pdf"}


def tesseract_available() -> bool:
    return shutil.which("tesseract") is not None


def check_tesseract() -> str:
    """Return an actionable error message when Tesseract is missing."""
    if tesseract_available():
        return ""
    return ("OCR is not available: the Tesseract engine was not found on "
            "this system.\n\n"
            "Install it with one of:\n"
            "  Ubuntu/Debian:  sudo apt-get install -y tesseract-ocr\n"
            "  macOS:          brew install tesseract\n"
            "  Windows:        https://github.com/UB-Mannheim/tesseract/wiki\n\n"
            "Then run: python3 ocr_ingest.py <file-or-folder>")


def _ocr_image(path: Path, lang: str = "eng") -> str:
    if not tesseract_available():
        raise RuntimeError(check_tesseract())
    r = subprocess.run(["tesseract", str(path), "stdout", "-l", lang],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise RuntimeError(f"tesseract failed: {r.stderr[-300:]}")
    return r.stdout


def _ocr_pdf(path: Path, lang: str = "eng") -> str:
    """PDF via pdftoppm (poppler-utils) -> per-page images -> tesseract.
    Falls back to a clear error when pdftoppm is missing."""
    if not tesseract_available():
        raise RuntimeError(check_tesseract())
    if shutil.which("pdftoppm") is None:
        return ("PDF OCR requires poppler-utils:\n"
                "  Ubuntu/Debian: sudo apt-get install -y poppler-utils\n"
                "  macOS:         brew install poppler")
    import tempfile
    tmp = tempfile.mkdtemp(prefix="drl_ocr_")
    try:
        r = subprocess.run(
            ["pdftoppm", "-png", "-r", "200", str(path),
             str(Path(tmp) / "page")],
            capture_output=True, text=True, timeout=600)
        if r.returncode != 0:
            raise RuntimeError(f"pdftoppm failed: {r.stderr[-300:]}")
        pages = sorted(Path(tmp).glob("page-*.png"))
        parts = []
        for i, pg in enumerate(pages, 1):
            parts.append(f"\n\n--- PDF page {i} ---\n\n" + _ocr_image(pg, lang))
        return "".join(parts)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def ocr_file(path: Path, lang: str = "eng") -> str:
    if path.suffix.lower() in SUPPORTED_IMAGES:
        return _ocr_image(path, lang)
    if path.suffix.lower() in SUPPORTED_PDF:
        return _ocr_pdf(path, lang)
    raise ValueError(f"unsupported file type: {path.suffix}")


def _clean_ocr(text: str) -> str:
    """Post-process OCR text: collapse the typical scanner noise."""
    t = re.sub(r"[ \t]+", " ", text)
    t = re.sub(r"\n{3,}", "\n\n", t)
    t = re.sub(r"[|]{3,}", "", t)
    return t.strip()


def ingest_file(path: Path, lang: str = "eng", force: bool = False) -> Dict:
    """OCR a file and add it to the knowledge library + catalog.

    Returns {ok, num, path, chars, error}."""
    if not path.exists():
        return {"ok": False, "error": f"file not found: {path}"}
    err = check_tesseract()
    if err:
        return {"ok": False, "error": err}
    try:
        text = _clean_ocr(ocr_file(path, lang))
    except Exception as e:
        return {"ok": False, "error": str(e)}
    if len(text) < 80:
        return {"ok": False,
                "error": f"OCR returned too little text ({len(text)} chars) "
                         f"— low-quality scan?"}
    # dedupe by content hash (same mechanism as the library)
    h = hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()[:12]
    LIBRARY_DIR.mkdir(parents=True, exist_ok=True)
    existing = list(LIBRARY_DIR.glob(f"*_{h}.txt"))
    if existing and not force:
        return {"ok": True, "num": existing[0].stem.split("_")[0],
                "path": str(existing[0]), "chars": len(text),
                "duplicate": True}
    nums = [int(p.stem.split("_")[0]) for p in LIBRARY_DIR.glob("*.txt")
            if p.stem.split("_")[0].isdigit()]
    num = (max(nums) + 1) if nums else 1
    title = re.sub(r"[^\w\- ]+", " ", path.stem).strip()[:80]
    fname = f"{num:03d}_{title}_{h}.txt"
    out = LIBRARY_DIR / fname
    out.write_text(text, encoding="utf-8")
    # register in the catalog
    try:
        from document_catalog import add_document
        add_document(num, title, fname, category="OCR", operation="",
                     well_type="", environment="", holes="")
    except Exception:
        pass
    return {"ok": True, "num": num, "path": str(out), "chars": len(text),
            "duplicate": False}


def ingest_folder(folder: Path, lang: str = "eng",
                  force: bool = False) -> List[Dict]:
    results = []
    for p in sorted(folder.iterdir()):
        if p.suffix.lower() in SUPPORTED_IMAGES | SUPPORTED_PDF:
            results.append(ingest_file(p, lang, force))
    return results


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _selftest():
    err = check_tesseract()
    if err:
        print("  ✔ ocr selftest: Tesseract missing — graceful error path OK")
        assert "apt-get" in err
        assert ingest_file(Path("/tmp/nope.pdf"))["ok"] is False
    else:
        print("  ✔ ocr selftest: Tesseract available (skipped full OCR)")
    print("ocr_ingest OK (graceful)")


if __name__ == "__main__":
    import sys as _sys
    args = _sys.argv[1:]
    if args:
        p = Path(args[0])
        if p.is_dir():
            for r in ingest_folder(p):
                print(r)
        else:
            print(ingest_file(p))
    else:
        _selftest()
