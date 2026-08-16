# ============================================================================
# LLM ENRICHMENT — rewrite/summarize library content with a local/cloud LLM
# ============================================================================
# Backends (same as the risk analyzer AI):
#   - Ollama   (local, http://localhost:11434) — no API key
#   - Gemini   (Google AI, needs API key)
#   - HuggingFace (needs API key)
#
# Pipeline: TF-IDF/semantic retrieval (wizard_knowledge) selects relevant
# chunks -> LLM rewrites them into clean, professional, neutral paragraphs
# -> inserted into the document. If no LLM is reachable, the raw (already
# neutralized) chunks are used — functionality is never reduced.
# ============================================================================

import json
import re
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

SETTINGS_FILE = Path.home() / ".drilling_program" / "llm_settings.json"


def load_settings() -> Dict:
    """Load saved LLM settings from disk (or defaults)."""
    try:
        if SETTINGS_FILE.exists():
            data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            return {"backend": data.get("backend", "none"),
                    "api_key": data.get("api_key", "")}
    except Exception:
        pass
    return {"backend": "none", "api_key": ""}


def save_settings(backend: str, api_key: str = ""):
    """Persist LLM settings to disk (survives restarts)."""
    try:
        SETTINGS_FILE.parent.mkdir(exist_ok=True)
        SETTINGS_FILE.write_text(
            json.dumps({"backend": backend, "api_key": api_key}),
            encoding="utf-8")
    except Exception:
        pass


def set_backend(backend: str, api_key: str = ""):
    global _BACKEND, _API_KEY
    _BACKEND = backend
    _API_KEY = api_key
    save_settings(backend, api_key)


_SAVED = load_settings()
_BACKEND = _SAVED.get("backend", "none")
_API_KEY = _SAVED.get("api_key", "")


# ----------------------------------------------------------------------------
# BACKEND QUERIES (reuse the risk analyzer implementations where possible)
# ----------------------------------------------------------------------------

def _query_ollama(prompt: str, model: str = "llama2") -> str:
    data = json.dumps({"model": model, "prompt": prompt, "stream": False}
                      ).encode("utf-8")
    req = urllib.request.Request(
        "http://localhost:11434/api/generate", data=data,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        return result.get("response", "")


def _query_gemini(prompt: str, api_key: str) -> str:
    try:
        import google.generativeai as genai
    except ImportError:
        raise RuntimeError(
            "Package 'google-generativeai' is not installed.\n"
            "Install it with:  pip install google-generativeai")
    genai.configure(api_key=api_key)
    last_err = "unknown error"
    for model_name in ("gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro"):
        try:
            model = genai.GenerativeModel(model_name)
            return model.generate_content(prompt).text
        except Exception as e:
            last_err = str(e)
            if "404" in last_err or "not found" in last_err.lower() or \
               "model" in last_err.lower():
                continue
            raise RuntimeError(f"Gemini API error: {last_err}")
    raise RuntimeError(f"Gemini API error: {last_err}")


def _query_huggingface(prompt: str, api_key: str) -> str:
    data = json.dumps({"inputs": prompt,
                       "parameters": {"max_new_tokens": 3000,
                                      "temperature": 0.4}}).encode("utf-8")
    req = urllib.request.Request(
        "https://api-inference.huggingface.co/models/"
        "mistralai/Mistral-7B-Instruct-v0.2",
        data=data,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {api_key}"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        if isinstance(result, list) and result:
            return result[0].get("generated_text", "")
        return str(result)


def query_llm(prompt: str, backend: str = "", api_key: str = "") -> str:
    """Query the configured LLM backend; returns '' on any failure.

    Stores the last error in LAST_LLM_ERROR so the UI can explain why the
    LLM call failed instead of failing silently.
    """
    global LAST_LLM_ERROR
    backend = backend or _BACKEND
    api_key = api_key or _API_KEY
    LAST_LLM_ERROR = ""
    if backend in ("None (use raw content)", "none", "", "None"):
        LAST_LLM_ERROR = "No LLM backend selected (using raw content)."
        return ""
    if backend in ("Gemini", "HuggingFace") and not api_key:
        LAST_LLM_ERROR = f"{backend} selected but no API key entered."
        return ""
    try:
        if backend == "Ollama":
            return _query_ollama(prompt)
        if backend == "Gemini":
            return _query_gemini(prompt, api_key)
        if backend == "HuggingFace":
            return _query_huggingface(prompt, api_key)
    except Exception as e:
        LAST_LLM_ERROR = str(e)
    return ""


LAST_LLM_ERROR = ""


# ----------------------------------------------------------------------------
# LLM REWRITE
# ----------------------------------------------------------------------------

REWRITE_PROMPT = (
    "You are a senior drilling and well operations engineer. Below is raw "
    "field content (checklists, steps, procedure excerpts) from real "
    "operations. Rewrite it into clean, professional, actionable paragraphs "
    "suitable for a formal drilling program or procedure document.\n\n"
    "RULES:\n"
    "1. Keep ALL technical facts, quantities, pressures, and steps.\n"
    "2. Do NOT invent new technical requirements.\n"
    "3. Only the operator and contractor named below may appear in the "
    "text; never mention any other company or brand.\n"
    "4. Organize as numbered/bulleted concise items under short headings.\n"
    "5. Output plain markdown only.\n\n"
    "OPERATOR NAME: {operator}\n"
    "CONTRACTOR NAME: {contractor}\n\n"
    "RAW FIELD CONTENT:\n"
    "{content}"
)


def rewrite_chunks(chunks: List[str], doc_title: str = "",
                   max_input_chars: int = 5500,
                   operator_name: str = "", contractor_name: str = "") -> str:
    """Rewrite selected library chunks with the LLM.

    The user's operator / contractor names (from the wizard inputs) are used
    in the rewritten text. Falls back to the raw (neutralized) chunks joined
    as markdown when the LLM is unavailable or returns nothing.
    """
    try:
        from wizard_engine import neutralize_text
    except Exception:
        neutralize_text = lambda s, *a, **k: s  # noqa

    if not chunks:
        return ""

    op = (operator_name or "").strip()
    con = (contractor_name or "").strip()

    # Try LLM
    content = "\n\n".join(chunks)
    if len(content) > max_input_chars:
        content = content[:max_input_chars] + "\n..."
    prompt = REWRITE_PROMPT.format(content=content, operator=op,
                                   contractor=con)
    llm_out = query_llm(prompt)
    if llm_out and len(llm_out.strip()) > 50:
        # strip any leading boilerplate the model may add
        llm_out = re.sub(r"^(Here is|Sure|Certainly|OK|As requested).*?\n",
                         "", llm_out, flags=re.I | re.S)
        return neutralize_text(llm_out.strip(), op, con)

    # Fallback: raw neutralized chunks
    md = []
    for ch in chunks:
        for ln in ch.split("\n"):
            s = ln.strip()
            if not s:
                continue
            if s.startswith("Checklist:"):
                md.append(f"**{s}**")
            elif s.startswith("- ") or s.startswith("#"):
                md.append(s)
            else:
                md.append(f"- {s}")
    return neutralize_text("\n".join(md), op, con)


# ----------------------------------------------------------------------------
# DIALOG: LLM SETTINGS (used by the wizard inputs page)
# ----------------------------------------------------------------------------

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QComboBox, QLineEdit, QPushButton, QFormLayout,
                               QMessageBox)


class LLMSettingsDialog(QDialog):
    """Configure the LLM backend for knowledge rewriting."""

    def __init__(self, parent=None, backend: str = "", api_key: str = ""):
        super().__init__(parent)
        if not backend:
            saved = load_settings()
            backend = saved.get("backend", "none")
            api_key = saved.get("api_key", "")
        self.setWindowTitle("🤖  LLM Settings — Knowledge Rewriting")
        self.setMinimumWidth(520)
        self.setStyleSheet(
            "QDialog { background-color: #16213e; }"
            "QLabel { color: #e0e0e0; }"
            "QLineEdit, QComboBox { background-color: #1a1a2e; color: #e0e0e0;"
            " border: 1px solid #0f3460; border-radius: 4px; padding: 6px; }"
            "QPushButton { background-color: #0f3460; color: white;"
            " border: none; border-radius: 5px; padding: 8px 16px; }"
            "QPushButton:hover { background-color: #e94560; }")

        lay = QVBoxLayout(self)
        title = QLabel("🤖  LLM Settings")
        title.setStyleSheet("color:#e94560;font-size:15px;font-weight:bold;")
        lay.addWidget(title)

        info = QLabel(
            "The LLM rewrites the selected field-library content into clean, "
            "professional paragraphs before it is inserted into your "
            "document. If no LLM is reachable, the raw (company-neutral) "
            "content is used automatically — nothing is lost.")
        info.setWordWrap(True)
        info.setStyleSheet("color:#8a8a9a;font-size:11px;")
        lay.addWidget(info)

        form = QFormLayout()
        self.backend = QComboBox()
        self.backend.addItems(["None (use raw content)", "Ollama (local)",
                               "Gemini", "HuggingFace"])
        if backend:
            idx = self.backend.findText(backend)
            if idx >= 0:
                self.backend.setCurrentIndex(idx)
        form.addRow("Backend:", self.backend)

        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.Password)
        self.api_key.setPlaceholderText("API key (Gemini / HuggingFace only)")
        self.api_key.setText(api_key)
        form.addRow("API Key:", self.api_key)
        lay.addLayout(form)

        note = QLabel(
            "Ollama: local server at http://localhost:11434 with a model "
            "pulled (e.g. llama2, mistral). No API key needed.")
        note.setWordWrap(True)
        note.setStyleSheet("color:#8a8a9a;font-size:10px;")
        lay.addWidget(note)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_test = QPushButton("🔍 Test Connection")
        btn_test.clicked.connect(self._test)
        btn_row.addWidget(btn_test)
        btn_ok = QPushButton("✔ OK")
        btn_ok.clicked.connect(self.accept)
        btn_row.addWidget(btn_ok)
        btn_cancel = QPushButton("✖ Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)
        lay.addLayout(btn_row)

    def _test(self):
        backend = self.backend.currentText()
        key = self.api_key.text().strip()
        if backend == "None (use raw content)":
            QMessageBox.information(self, "Test", "Backend set to None.")
            return
        resp = query_llm("Reply with exactly: OK", backend, key)
        if resp and "OK" in resp.upper():
            QMessageBox.information(self, "Test", "✅ Connection OK")
        else:
            err = LAST_LLM_ERROR or "No response."
            QMessageBox.warning(
                self, "Test",
                "⚠️ Not reachable.\n\n"
                f"{err}\n\n"
                "Tips:\n"
                "• Gemini: pip install google-generativeai, then check the key\n"
                "• Ollama: is the local server running on port 11434?\n"
                "• HuggingFace: token from huggingface.co/settings/tokens")

    def get_values(self):
        backend = self.backend.currentText()
        if backend == "None (use raw content)":
            return "none", ""
        return backend, self.api_key.text().strip()
