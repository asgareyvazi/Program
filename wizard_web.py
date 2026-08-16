# ============================================================================
# WEB RESEARCH TOOL (for document enrichment)
# ============================================================================
# Free, no-API-key sources: Wikipedia REST summary + DuckDuckGo Instant
# Answers. Used to fetch field/formation/regional introduction text that
# the user can insert into the generated document (with source links).
# ============================================================================

import json
import re
import urllib.parse
import urllib.request
import ssl
from typing import Dict, List, Optional, Tuple

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QListWidget, QListWidgetItem, QTextEdit, QSplitter,
    QMessageBox, QApplication, QWidget
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices

# ----------------------------------------------------------------------------
# HTTP HELPERS — try `requests` first (handles proxies better on Windows),
# fall back to urllib with a permissive SSL context as a last resort.
# ----------------------------------------------------------------------------

_last_http_error = ""


def _http_get(url: str, timeout: int = 15) -> Optional[bytes]:
    """GET with requests-first strategy; stores a readable error."""
    global _last_http_error
    _last_http_error = ""
    try:
        import requests
        r = requests.get(url, timeout=timeout, headers={
            "User-Agent": "DrillingProgramGen/3.1"})
        if r.status_code == 200:
            return r.content
        _last_http_error = f"HTTP {r.status_code}"
        return None
    except ImportError:
        pass
    except Exception as e:
        _last_http_error = str(e)[:160]
        return None

    # urllib fallback
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "DrillingProgramGen/3.1"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except Exception as e:
        _last_http_error = str(e)[:160]
        return None


def last_http_error() -> str:
    return _last_http_error


# ----------------------------------------------------------------------------
# FETCHERS
# ----------------------------------------------------------------------------

def fetch_wikipedia_summary(query: str, lang: str = "en") -> Optional[Dict]:
    """Fetch a short article summary from Wikipedia REST API."""
    url = (f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/"
           + urllib.parse.quote(query.replace(" ", "_")))
    data = _http_get(url)
    if data is None:
        return None
    try:
        d = json.loads(data.decode("utf-8", errors="replace"))
        return {
            "title": d.get("title", query),
            "extract": d.get("extract", ""),
            "url": d.get("content_urls", {}).get("desktop", {}).get("page", ""),
        }
    except Exception:
        return None


def fetch_wikipedia_search(query: str, lang: str = "en") -> List[Tuple[str, str]]:
    """Fallback: Wikipedia opensearch — more forgiving than the summary API."""
    url = ("https://" + lang + ".wikipedia.org/w/api.php?action=opensearch&"
           "format=json&limit=8&search=" + urllib.parse.quote(query))
    data = _http_get(url)
    if data is None:
        return []
    try:
        d = json.loads(data.decode("utf-8", errors="replace"))
        titles, links = d[1], d[3]
        return list(zip(titles, links))
    except Exception:
        return []


def fetch_duckduckgo(query: str) -> List[Tuple[str, str]]:
    """Fetch related topics from DuckDuckGo Instant Answers."""
    url = ("https://api.duckduckgo.com/?q=" + urllib.parse.quote(query)
           + "&format=json&no_html=1&skip_disambig=1")
    data = _http_get(url)
    if data is None:
        return []
    try:
        d = json.loads(data.decode("utf-8", errors="replace"))
        results: List[Tuple[str, str]] = []
        for a in d.get("RelatedTopics", [])[:10]:
            if "Topics" in a:
                for t in a["Topics"][:3]:
                    if t.get("Text"):
                        results.append((t["Text"], t.get("FirstURL", "")))
            elif a.get("Text"):
                results.append((a["Text"], a.get("FirstURL", "")))
        return results
    except Exception:
        return []


# ----------------------------------------------------------------------------
# SUGGESTED QUERIES per document type
# ----------------------------------------------------------------------------

SUGGESTED_QUERIES: Dict[str, List[str]] = {
    "drilling_program": [
        "South Azadegan oil field", "Sarvak Formation geology",
        "Dezful Embayment oil fields", "Iran oil field drilling"],
    "advanced_drilling_program": [
        "South Azadegan oil field", "Sarvak Formation geology",
        "Dezful Embayment", "drilling engineering well planning"],
    "workover_program": [
        "well workover oil", "ESP workover operations",
        "Sarvak Formation"],
    "esp_workover": [
        "electric submersible pump oil well",
        "South Azadegan oil field", "Azadegan oil field development"],
    "cementing_program": [
        "oil well cementing", "API cementing primary casing",
        "cement plug oil well"],
    "cement_plug_procedure": [
        "balanced cement plug oil well", "cement plug drilling"],
    "casing_running_cementing_procedure": [
        "casing running procedure oil well", "well cementing operations"],
    "well_kill_program": [
        "well kill operations oil", "bullheading well control"],
    "nisoc_kill_procedure": [
        "well killing procedure drilling", "well control kick"],
    "abandonment_program": [
        "well plug and abandonment", "NORSOK D-010 permanent abandonment"],
    "well_testing_program": [
        "well testing oil gas", "drill stem test DST"],
    "fishing_program": [
        "fishing operations drilling", "stuck pipe fishing oil well"],
    "stimulation_program": [
        "matrix acidizing oil well", "hydraulic fracturing design"],
    "coiled_tubing_program": [
        "coiled tubing operations oil well", "CT cleanout well"],
    "hpht_drilling_program": [
        "HPHT well drilling", "high pressure high temperature wells"],
    "deepwater_drilling_program": [
        "deepwater drilling", "subsea BOP well control"],
    "horizontal_shale_program": [
        "horizontal drilling shale", "rotary steerable system"],
    "h2s_emergency_procedure": [
        "hydrogen sulfide H2S safety oil field", "H2S emergency response"],
}

DEFAULT_QUERIES = ["oil field overview", "reservoir geology",
                   "drilling operations introduction"]


def suggest_queries(template_key: str) -> List[str]:
    return SUGGESTED_QUERIES.get(template_key, DEFAULT_QUERIES)


# ----------------------------------------------------------------------------
# SEARCH DIALOG
# ----------------------------------------------------------------------------

class WebResearchDialog(QDialog):
    """Search Wikipedia / DuckDuckGo and insert text into the document."""

    def __init__(self, template_key: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🌐  Web Research — Field & Formation Introduction")
        self.resize(900, 620)
        self.setStyleSheet(
            "QDialog { background-color: #16213e; }"
            "QLabel { color: #e0e0e0; }"
            "QLineEdit, QComboBox, QTextEdit, QListWidget {"
            " background-color: #1a1a2e; color: #e0e0e0;"
            " border: 1px solid #0f3460; border-radius: 4px; padding: 5px; }"
            "QPushButton { background-color: #0f3460; color: white;"
            " border: none; border-radius: 5px; padding: 8px 16px; }"
            "QPushButton:hover { background-color: #e94560; }")
        self.template_key = template_key
        self.inserted_text = ""

        lay = QVBoxLayout(self)

        title = QLabel("🌐  Web Research")
        title.setStyleSheet("color:#e94560;font-size:16px;font-weight:bold;")
        lay.addWidget(title)

        # Query row
        qrow = QHBoxLayout()
        self.query = QLineEdit()
        self.query.setPlaceholderText("Search term — e.g. 'South Azadegan oil field'")
        self.query.returnPressed.connect(self._search)
        qrow.addWidget(self.query, 1)

        self.engine = QComboBox()
        self.engine.addItems(["Wikipedia (summary)", "DuckDuckGo (links)"])
        qrow.addWidget(self.engine)

        self.btn_search = QPushButton("🔍 Search")
        self.btn_search.clicked.connect(self._search)
        qrow.addWidget(self.btn_search)
        lay.addLayout(qrow)

        # Suggestions
        sug_row = QHBoxLayout()
        sug_row.addWidget(QLabel("Suggestions:"))
        for q in suggest_queries(template_key):
            b = QPushButton(q[:28])
            b.setMaximumWidth(220)
            b.clicked.connect(lambda checked=False, t=q: self._use_suggestion(t))
            sug_row.addWidget(b)
        sug_row.addStretch()
        lay.addLayout(sug_row)

        # Results splitter
        split = QSplitter(Qt.Horizontal)

        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.addWidget(QLabel("Results:"))
        self.results = QListWidget()
        self.results.itemDoubleClicked.connect(self._load_result)
        ll.addWidget(self.results)
        split.addWidget(left)

        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.addWidget(QLabel("Preview (editable):"))
        self.preview = QTextEdit()
        self.preview.setPlaceholderText(
            "Search results appear here. Edit freely, then press Insert.")
        rl.addWidget(self.preview)
        split.addWidget(right)

        split.setSizes([400, 500])
        lay.addWidget(split, 1)

        # Actions
        brow = QHBoxLayout()
        brow.addStretch()
        self.btn_open = QPushButton("🌍 Open in Browser")
        self.btn_open.setEnabled(False)
        self.btn_open.clicked.connect(self._open_browser)
        brow.addWidget(self.btn_open)

        self.btn_insert = QPushButton("📥 Insert into Document")
        self.btn_insert.setEnabled(False)
        self.btn_insert.clicked.connect(self._insert)
        brow.addWidget(self.btn_insert)

        btn_close = QPushButton("✖ Close")
        btn_close.clicked.connect(self.reject)
        brow.addWidget(btn_close)
        lay.addLayout(brow)

        self._last_url = ""

    def _use_suggestion(self, text: str):
        self.query.setText(text)
        self._search()

    def _search(self):
        q = self.query.text().strip()
        if not q:
            return
        self.results.clear()
        self.preview.clear()
        self.btn_open.setEnabled(False)
        self.btn_insert.setEnabled(False)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            if self.engine.currentIndex() == 0:
                data = fetch_wikipedia_summary(q)
                if data and data.get("extract"):
                    item = QListWidgetItem(f"📖 {data['title']}")
                    item.setData(Qt.UserRole, ("wiki", data))
                    self.results.addItem(item)
                    self.results.setCurrentRow(0)
                    self._load_result(item)
                    return
                # fallback: opensearch list
                hits = fetch_wikipedia_search(q)
                for title, url in hits[:8]:
                    item = QListWidgetItem(f"📖 {title[:90]}")
                    item.setData(Qt.UserRole, ("ddg", (title, url)))
                    item.setToolTip(url)
                    self.results.addItem(item)
                if hits:
                    self.preview.setPlainText(
                        "Exact article not found — showing Wikipedia search "
                        "results. Select one and insert.")
                    return
                self._show_web_error(
                    "Wikipedia is not reachable from this connection.")
            else:
                hits = fetch_duckduckgo(q)
                for text, url in hits[:10]:
                    item = QListWidgetItem(text[:90])
                    item.setData(Qt.UserRole, ("ddg", (text, url)))
                    item.setToolTip(url)
                    self.results.addItem(item)
                if not hits:
                    self._show_web_error(
                        "DuckDuckGo returned nothing. It is blocked in some "
                        "countries — use Wikipedia, or open the browser.")
        finally:
            QApplication.restoreOverrideCursor()

    def _show_web_error(self, msg: str):
        """Explain WHY the web search failed instead of a silent 'no results'."""
        err = last_http_error()
        tip = ""
        if err:
            low = err.lower()
            if "403" in low:
                tip = ("\n\n403 = the site blocked this request (region/"
                       "firewall). Try another engine or the browser button.")
            elif "certificate" in low or "ssl" in low or "tls" in low:
                tip = ("\n\nTLS/SSL handshake failed — your network/firewall "
                       "is interfering. Try the browser button (uses your "
                       "system browser settings).")
            elif "timed out" in low or "timeout" in low:
                tip = ("\n\nConnection timed out — check internet access / "
                       "proxy settings.")
        self.preview.setPlainText(
            f"{msg}\n\nDetail: {err or 'no response'}{tip}\n\n"
            "💡 Tip: press 'Open in Browser' to search with your system "
            "browser (it uses your proxy/VPN settings).")
        # enable browser fallback with a search URL
        q = self.query.text().strip()
        engine = self.engine.currentText() if hasattr(self, "engine") else ""
        if "Duck" in engine:
            self._last_url = ("https://duckduckgo.com/?q=" +
                              urllib.parse.quote(q))
        else:
            self._last_url = ("https://en.wikipedia.org/w/index.php?search=" +
                              urllib.parse.quote(q))
        self.btn_open.setEnabled(True)

    def _load_result(self, item):
        kind, data = item.data(Qt.UserRole)
        if kind == "wiki":
            self.preview.setPlainText(
                f"{data['title']}\n\n{data['extract']}\n\nSource: {data['url']}")
            self._last_url = data["url"]
        else:
            text, url = data
            self.preview.setPlainText(f"{text}\n\nSource: {url}")
            self._last_url = url
        self.btn_open.setEnabled(bool(self._last_url))
        self.btn_insert.setEnabled(True)

    def _open_browser(self):
        if self._last_url:
            QDesktopServices.openUrl(QUrl(self._last_url))

    def _insert(self):
        text = self.preview.toPlainText().strip()
        if not text:
            return
        lines = text.split("\n")
        source_lines = [l for l in lines if l.lower().startswith("source:")]
        body = [l for l in lines if not l.lower().startswith("source:")]
        md = "\n\n".join(body)
        for s in source_lines:
            url = s.split("Source:", 1)[1].strip()
            md += f"\n\n> Source: {url}"
        self.inserted_text = md
        self.accept()


def run_web_research(template_key: str, parent=None) -> str:
    """Open the dialog; returns inserted markdown text ('' if cancelled)."""
    dlg = WebResearchDialog(template_key, parent)
    if dlg.exec() == QDialog.Accepted:
        return dlg.inserted_text
    return ""
