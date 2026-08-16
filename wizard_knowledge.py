# ============================================================================
# FIELD KNOWLEDGE ENRICHMENT — machine-learning retrieval from the library
# ============================================================================
# Uses the 214 real operations documents (programs/library/) internally to
# ground every generated document in proven field practice.
#
# Retrieval (ML):
#   1. Keyword scoring (fast, always available)
#   2. TF-IDF cosine ranking (classic ML — pure python, no dependencies)
#   3. Semantic embeddings (sentence-transformers) — used automatically when
#      installed (pip install sentence-transformers)
#
# Company/brand names are removed from everything that enters the output.
# ============================================================================

import math
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

LIBRARY_DIR = Path(__file__).resolve().parent / "programs" / "library"

_INTENSITY_LIMITS = {"brief": 2500, "moderate": 7000, "detailed": 14000}
_MAX_CHUNKS = 8

# Keyword profiles per document type — drive chunk scoring
KEYWORD_PROFILES: Dict[str, List[str]] = {
    "reentry_program": [
        "re-entry", "sidetrack", "whipstock", "window", "directional",
        "mwd", "lwd", "kick-off", "bha", "bit", "liner", "completion",
        "pooh", "rih", "mud", "scraper"],
    "offshore_workover_program": [
        "workover", "kill", "brine", "esp", "completion", "packer",
        "tubing", "trsv", "wellhead", "x-mas tree", "bop", "pooh",
        "rih", "perforation", "scraper"],
    "offshore_drilling_program": [
        "drilling", "hydraulics", "nozzle", "tfa", "hsi", "ecd",
        "formation", "casing", "mud", "bha", "bit", "well control",
        "bop", "completion", "time"],
    "casing_running_cementing_procedure": [
        "casing", "cement", "plug", "float", "centralizer", "torque", "shoe",
        "woc", "displace", "checklist", "elevator", "slips", "fill"],
    "cement_plug_procedure": [
        "cement", "plug", "slurry", "spacer", "displacement", "density",
        "woc", "tag", "bbl", "pcf", "sacks", "additive"],
    "cementing_program": [
        "cement", "slurry", "spacer", "displacement", "density", "woc",
        "shoe", "plug", "additives", "mix"],
    "well_kill_program": [
        "kill", "mud", "weight", "circulate", "pressure", "gain", "loss",
        "bullhead", "static"],
    "nisoc_kill_procedure": [
        "kill", "mud", "weight", "gain", "loss", "circulate", "stuck",
        "pooh", "bha", "bit"],
    "drilling_program": [
        "drilling", "mud", "casing", "bha", "bit", "formation",
        "directional", "bop", "cement", "time", "hse"],
    "advanced_drilling_program": [
        "drilling", "mud", "casing", "bha", "bit", "formation",
        "directional", "bop", "cement", "time", "cost", "hse", "trajectory"],
    "workover_program": [
        "workover", "completion", "kill", "pull", "packer", "tubing",
        "trsv", "ssd", "wellhead"],
    "esp_workover": [
        "esp", "pump", "cable", "splice", "packer", "tubing", "penetrator",
        "motor", "completion"],
    "esp_running_procedure": [
        "esp", "cable", "cccp", "megger", "packer", "motor", "splice",
        "tubing"],
    "fishing_program": [
        "fishing", "stuck", "jar", "backoff", "overshot", "fish", "milling"],
    "stimulation_program": [
        "acid", "stimulation", "frac", "injection", "pressure", "treatment",
        "pump"],
    "coiled_tubing_program": [
        "coiled", "tubing", "ct", "cleanout", "n2", "injector", "bop"],
    "abandonment_program": [
        "abandon", "plug", "cement", "barrier", "cut", "casing"],
    "well_testing_program": [
        "test", "flow", "choke", "separator", "dst", "build", "pressure",
        "rate"],
    "hpht_drilling_program": [
        "hpht", "pressure", "temperature", "kick", "bop", "casing", "mud"],
    "deepwater_drilling_program": [
        "deepwater", "subsea", "riser", "bop", "shallow", "hydrate", "mud"],
    "horizontal_shale_program": [
        "horizontal", "lateral", "rss", "geosteer", "curve", "frac", "shale"],
    "running_casing_procedure": [
        "casing", "running", "torque", "centralizer", "fill", "float",
        "shoe", "elevator", "slips"],
    "kick_circulation_procedure": [
        "kick", "sidpp", "circulate", "choke", "mud", "weight", "icp",
        "fcp"],
    "stuck_pipe_procedure": [
        "stuck", "jar", "overpull", "work", "backoff", "fishing", "free"],
    "slickline_procedure": [
        "slickline", "wire", "plug", "prong", "ssd", "gauge", "lubricator"],
    "packer_setting_procedure": [
        "packer", "set", "shear", "pressure", "test", "annulus"],
    "perforation_procedure": [
        "perforat", "gun", "depth", "correlation", "underbalance", "fire",
        "charges"],
    "dst_procedure": [
        "dst", "test", "flow", "build", "gauge", "sampler", "packer",
        "choke"],
    "wellhead_installation_procedure": [
        "wellhead", "p-seal", "gasket", "stud", "test", "nipple"],
    "lost_circulation_procedure": [
        "loss", "lcm", "pill", "circulation", "plug", "mud", "fracture"],
    "rig_move_procedure": ["rig", "move", "rig-up", "level", "bop", "spud"],
    "h2s_emergency_procedure": [
        "h2s", "hydrogen", "sulfide", "ba", "scba", "alarm", "evacuate",
        "monitor"],
    "tubing_pressure_test_procedure": [
        "pressure", "test", "tubing", "plug", "leak", "hold"],
    "bha_makeup_procedure": [
        "bha", "make-up", "torque", "bit", "motor", "mwd", "inspect"],
    "tripping_procedure": [
        "trip", "pooh", "rih", "fill", "trip tank", "speed", "slips"],
}

# ----------------------------------------------------------------------------
# DOCUMENT LOADING
# ----------------------------------------------------------------------------

def _resolve(num: str) -> Optional[Path]:
    """Resolve a library number prefix to the actual file path."""
    if not LIBRARY_DIR.exists():
        return None
    for p in LIBRARY_DIR.glob(f"{num}_*"):
        return p
    return None


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


# ----------------------------------------------------------------------------
# CONTENT EXTRACTION (checklists / steps / tables)
# ----------------------------------------------------------------------------

_CHECK_RE = re.compile(r"^\s*(?:[-*+]\s*\[[ xX]?\]|☐|☑|[-*+])\s*(.+)$")
_NUM_RE = re.compile(r"^\s*\d{1,3}[.)]\s+(.+)$")


def extract_checklists(text: str) -> List[str]:
    out = []
    for line in text.splitlines():
        m = _CHECK_RE.match(line)
        if m:
            item = m.group(1).strip()
            if len(item) > 5 and not item.startswith("|"):
                out.append(item)
    return out


def extract_steps(text: str) -> List[str]:
    out = []
    for line in text.splitlines():
        m = _NUM_RE.match(line)
        if m:
            item = m.group(1).strip()
            if len(item) > 5 and not item.startswith("|"):
                out.append(item)
    return out


def extract_headings(text: str) -> List[str]:
    out = []
    for line in text.splitlines():
        m = re.match(r"^(#{1,4})\s+(.+)$", line.strip())
        if m:
            out.append(m.group(2).strip())
    return out


def chunk_text(text: str, max_chars: int = 1200) -> List[str]:
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, cur = [], ""
    for p in paras:
        if cur and len(cur) + len(p) + 1 > max_chars:
            chunks.append(cur)
            cur = p
        else:
            cur = (cur + "\n" + p).strip()
    if cur:
        chunks.append(cur)
    return chunks


# ----------------------------------------------------------------------------
# ML RANKING
# ----------------------------------------------------------------------------

def _tokenize(s: str) -> List[str]:
    return re.findall(r"[a-z0-9]{3,}", s.lower())


def tfidf_rerank(chunks: List[str], query: str, top_n: int = _MAX_CHUNKS) -> List[str]:
    """Classic ML retrieval: TF-IDF vectors + cosine similarity (pure python)."""
    docs = [_tokenize(c) for c in chunks]
    q = _tokenize(query)
    vocab = set()
    for d in docs:
        vocab.update(d)
    vocab.update(q)
    n = len(docs)
    df = {w: sum(1 for d in docs if w in d) for w in vocab}
    idf = {w: math.log((n + 1) / (df[w] + 1)) + 1.0 for w in vocab}

    def vec(d):
        v: Dict[str, float] = {}
        for w in set(d):
            v[w] = d.count(w) * idf.get(w, 1.0)
        return v

    qv = vec(q)

    def cos(a, b):
        num = sum(a[w] * b[w] for w in set(a) & set(b))
        na = math.sqrt(sum(x * x for x in a.values()))
        nb = math.sqrt(sum(x * x for x in b.values()))
        return num / (na * nb + 1e-9)

    scored = sorted(((cos(qv, vec(d)), c) for c, d in zip(chunks, docs)),
                    reverse=True)
    return [c for s, c in scored[:top_n] if s > 0] or chunks[:top_n]


def semantic_rerank(chunks: List[str], query: str,
                    top_n: int = _MAX_CHUNKS) -> Optional[List[str]]:
    """Semantic embedding retrieval — used when sentence-transformers is
    installed; returns None otherwise (caller falls back to TF-IDF)."""
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore
        import numpy as np  # type: ignore
        model = SentenceTransformer("all-MiniLM-L6-v2")
        qv = model.encode([query])[0]
        vecs = model.encode(chunks, show_progress_bar=False)
        sims = np.dot(vecs, qv) / (
            np.linalg.norm(vecs, axis=1) * np.linalg.norm(qv) + 1e-9)
        order = np.argsort(-sims)[:top_n]
        return [chunks[i] for i in order]
    except Exception:
        return None


# ----------------------------------------------------------------------------
# CHUNK RETRIEVAL (used by the LLM rewriter)
# ----------------------------------------------------------------------------

def filter_refs_by_profile(refs, profile: Optional[Dict] = None):
    """Filter (num, label) reference list using the document catalog.

    profile: {"well_type", "environment", "operation", "holes"}
    Documents that match the profile are kept first; if nothing matches,
    the original list is returned (fallback).
    """
    if not profile or not refs:
        return refs
    try:
        from document_catalog import get_catalog
        cat = get_catalog()
        matched = []
        for num, label in refs:
            row = cat.conn.execute(
                "SELECT * FROM docs WHERE num=?", (int(num),)).fetchone()
            if not row:
                continue
            ok = True
            if profile.get("operation") and profile["operation"] != "Undefined":
                if row["operation"] != profile["operation"]:
                    ok = False
            if ok and profile.get("environment") and \
                    profile["environment"] != "Undefined":
                if row["environment"] not in ("Undefined", profile["environment"]):
                    ok = False
            if ok:
                matched.append((num, label))
        return matched or refs
    except Exception:
        return refs


def get_chunks_for(template_key: str, intensity: str = "moderate",
                   max_docs: int = 2, use_ml: bool = True,
                   max_chunks: int = 8,
                   profile: Optional[Dict] = None) -> List[str]:
    """Return the top-ranked library chunks (raw text) for a template.

    profile (optional): dict with well_type/environment/operation/holes —
    filters the reference documents to the closest matches first.
    """
    try:
        from wizard_references import get_reference_docs
    except Exception:
        return []
    refs = get_reference_docs(template_key)
    if not refs:
        return []
    refs = filter_refs_by_profile(refs, profile)
    keywords = KEYWORD_PROFILES.get(template_key,
                                    ["drilling", "procedure", "checklist", "test"])
    query = " ".join(keywords)

    chunks: List[Tuple[str, str, str]] = []
    for num, label in refs[:max_docs]:
        p = _resolve(num)
        if p is None:
            continue
        text = _load_text(p)
        ck = extract_checklists(text)
        st = extract_steps(text)
        parts = []
        if ck:
            parts.append("Checklist:\n" + "\n".join("- " + cc for cc in ck[:25]))
        if st:
            parts.append("Steps:\n" + "\n".join(st[:30]))
        if not parts:
            parts.append(text[:1500])
        for ch in chunk_text("\n\n".join(parts)):
            chunks.append((num, label, ch))
    if not chunks:
        return []

    texts = [ch for _, _, ch in chunks]
    if use_ml:
        sem = semantic_rerank(texts, query)
        if sem is not None:
            order = {t: i for i, t in enumerate(texts)}
            chunks.sort(key=lambda x: order.get(x[2], 0))
            chunks = chunks[:max_chunks]
        else:
            ranked = tfidf_rerank(texts, query, top_n=max_chunks)
            chunks = [x for x in chunks if x[2] in ranked][:max_chunks]
    else:
        chunks = chunks[:max_chunks]
    return [ch for _, _, ch in chunks]


# ----------------------------------------------------------------------------
# ENRICHMENT
# ----------------------------------------------------------------------------

def enrich_template(template_key: str, intensity: str = "moderate",
                    max_docs: int = 2, use_ml: bool = True,
                    operator_name: str = "", contractor_name: str = "") -> str:
    """Return a markdown section of the most relevant field-library content
    for the given document type (company names removed)."""
    try:
        from wizard_references import get_reference_docs
    except Exception:
        return ""
    refs = get_reference_docs(template_key)
    if not refs:
        return ""

    limit = _INTENSITY_LIMITS.get(intensity, 7000)
    keywords = KEYWORD_PROFILES.get(template_key,
                                    ["drilling", "procedure", "checklist", "test"])
    query = " ".join(keywords)

    chunks: List[Tuple[str, str, str]] = []  # (num, label, text)
    for num, label in refs[:max_docs]:
        p = _resolve(num)
        if p is None:
            continue
        text = _load_text(p)
        ck = extract_checklists(text)
        st = extract_steps(text)
        parts = []
        if ck:
            parts.append("Checklist:\n" + "\n".join("- " + c for c in ck[:25]))
        if st:
            parts.append("Steps:\n" + "\n".join(st[:30]))
        if not parts:
            parts.append(text[:1500])
        body = "\n\n".join(parts)
        for ch in chunk_text(body):
            chunks.append((num, label, ch))
    if not chunks:
        return ""

    texts = [c for _, _, c in chunks]
    if use_ml:
        sem = semantic_rerank(texts, query)
        if sem is not None:
            by_text = {c: (n, l) for n, l, c in chunks}
            chunks = [(by_text[c][0], by_text[c][1], c) for c in sem]
        else:
            ranked = tfidf_rerank(texts, query)
            by_text = {c: (n, l) for n, l, c in chunks}
            chunks = [(by_text[c][0], by_text[c][1], c) for c in ranked]
    else:
        chunks = chunks[:_MAX_CHUNKS]

    # Assemble markdown
    out = [
        "## FIELD KNOWLEDGE ENRICHMENT (FROM REAL OPERATIONS LIBRARY)",
        "",
        "Content below was selected automatically by the ML retrieval engine "
        "from the internal field-document library to ground this document in "
        "proven operational practice. Company names have been removed.",
        "",
    ]
    total = 0
    for num, label, ch in chunks:
        if total >= limit:
            break
        out.append(f"### {label}")
        out.append("")
        for ln in ch.split("\n"):
            s = ln.strip()
            if not s:
                continue
            if s.startswith("Checklist:") or s.startswith("Steps:"):
                out.append(f"**{s}**")
            elif s.startswith("- ") or s.startswith("#"):
                out.append(s)
            else:
                out.append(f"- {s}")
        out.append("")
        total += len(ch)

    md = "\n".join(out)
    try:
        from wizard_engine import neutralize_text
        return neutralize_text(md, operator_name, contractor_name)
    except Exception:
        return md
