# ============================================================================
# RISK REVIEW — WIZARD INTEGRATION
# ============================================================================
# Connects the Drilling Risk Analyzer (drilling_risk_analyzer.py) to the
# document wizard pipeline:
#   1. Build an operation sequence from the user-selected sections + inputs
#   2. Run the risk analysis engine (expert knowledge base)
#   3. Ask the user confirmation questions for Critical/High risks
#   4. Render a "RISK ASSESSMENT & CONTINGENCY PLAN" section into the
#      generated Word document (before final output)
# ============================================================================

import re
from typing import Dict, List, Optional, Tuple

from drilling_risk_analyzer import AnalysisEngine, RiskLevel

# ----------------------------------------------------------------------------
# 1. BUILD OPERATION SEQUENCE FROM THE DOCUMENT
# ----------------------------------------------------------------------------

_HEADING_RE = re.compile(r"^#{2,4}\s+(.+)$")
_STEP_RE = re.compile(r"^\s*(?:[-*+>]|\d+[.)]|\[\s*[xX ]?\s*\])\s*(.+)$")


def build_sequence_from_document(md_text: str,
                                 values: Optional[Dict[str, str]] = None,
                                 max_lines: int = 60) -> str:
    """Convert the (filled, section-selected) markdown into an operation
    sequence that the risk analyzer understands.

    Headings and numbered/bulleted steps are collected; value keywords
    (kill method, H2S, mud type...) are appended so well-control and
    H2S risks are matched even if the document text is sparse.
    """
    lines_out: List[str] = []
    seen = set()

    def add(line: str):
        s = line.strip()
        if not s or s.lower() in seen:
            return
        seen.add(s.lower())
        lines_out.append(s)

    for raw in md_text.replace("\r\n", "\n").split("\n"):
        m = _HEADING_RE.match(raw)
        if m:
            add(m.group(1).strip())
            continue
        m = _STEP_RE.match(raw)
        if m:
            step = m.group(1).strip()
            # skip pure table rows / separators
            if step.startswith("|") or set(step) <= {"-", "|", ":", " "}:
                continue
            add(step)
        if len(lines_out) >= max_lines:
            break

    # Keyword hints from user inputs (ensures well-control coverage)
    kw = values or {}
    hints = [
        kw.get("kill_method", ""), kw.get("kill_fluid", ""),
        kw.get("mud_type", ""), kw.get("bop_stack", ""),
        kw.get("packer_depth", ""), kw.get("h2s", ""),
        kw.get("workover_type", ""), kw.get("completion_type", ""),
    ]
    for h in hints:
        if h and str(h).strip() and str(h).strip().lower() != "x":
            add(str(h))

    return "\n".join(lines_out)


# ----------------------------------------------------------------------------
# 2. RISK ANALYSIS (engine cached — the knowledge base is large)
# ----------------------------------------------------------------------------

_engine: Optional[AnalysisEngine] = None


def get_engine() -> AnalysisEngine:
    global _engine
    if _engine is None:
        _engine = AnalysisEngine()
    return _engine


def run_risk_analysis(sequence: str) -> Dict:
    """Run the risk analyzer; returns the full result dict."""
    return get_engine().analyze(sequence)


# ----------------------------------------------------------------------------
# 3. CONFIRMATION QUESTIONS
# ----------------------------------------------------------------------------

def generate_risk_questions(results: Dict, values: Optional[Dict] = None) -> List[str]:
    """Build a list of confirmation questions for the user.

    - For every Critical/High risk: ask whether the mitigation is planned.
    - Plus fixed key questions driven by operations/inputs.
    """
    questions: List[str] = []
    values = values or {}

    # High/Critical risks
    for risk in results.get("risks", []):
        if risk.severity in (RiskLevel.CRITICAL, RiskLevel.HIGH):
            plan = ""
            if risk.contingency_plans:
                plan = risk.contingency_plans[0].action
            q = (f"Risk '{risk.problem}' ({risk.severity.value}) — is the "
                 f"mitigation planned in the program? "
                 f"(e.g. {plan[:70]})")
            questions.append(q)

    # Fixed key questions
    h2s = str(values.get("h2s", "")).lower()
    if h2s and h2s not in ("no", "0", "x", ""):
        questions.append(
            "H2S is present — are gas monitoring, BA/SCBA sets and the H2S "
            "emergency plan included?")
    ops = " ".join(str(o.get("operation_type", ""))
                   for o in results.get("operations", []))
    if "BOP" in ops.upper() or any(k in ops.upper() for k in
                                   ("KICK", "KILL", "WELL_CONTROL")):
        questions.append(
            "Well-control operations detected — are BOP pressure tests and "
            "a kill sheet included in the program?")
    if "TRIPPING" in ops.upper():
        questions.append(
            "Tripping operations detected — is a trip tank with gain/loss "
            "alarm included?")
    if "CASING" in ops.upper() or "CEMENT" in ops.upper():
        questions.append(
            "Casing/cementing detected — are float equipment tests and "
            "shoe pressure test included?")
    if "FISHING" in ops.upper() or "STUCK" in ops.upper():
        questions.append(
            "Fishing/stuck-pipe operations detected — are jarring limits "
            "and a back-off plan included?")
    if "PERFORATION" in ops.upper() or "DST" in ops.upper():
        questions.append(
            "Perforation/DST detected — is the underbalance and flow "
            "contingency (H2S, well control) included?")

    # De-duplicate, cap at 8
    out: List[str] = []
    for q in questions:
        if q not in out:
            out.append(q)
    return out[:8]


# ----------------------------------------------------------------------------
# 4. RENDER RISK SECTION (markdown for the document)
# ----------------------------------------------------------------------------

def build_risk_section_md(results: Dict,
                          answers: Optional[Dict[str, bool]] = None,
                          sequence: str = "") -> str:
    """Build the 'RISK ASSESSMENT & CONTINGENCY PLAN' markdown section."""
    answers = answers or {}
    risks = results.get("risks", [])
    forgotten = results.get("forgotten_items", [])
    sev = results.get("severity_counts", {})
    total_npt = results.get("total_expected_npt", 0)

    crit = sev.get(RiskLevel.CRITICAL, 0)
    high = sev.get(RiskLevel.HIGH, 0)
    med = sev.get(RiskLevel.MEDIUM, 0)

    lines = [
        "## RISK ASSESSMENT & CONTINGENCY PLAN",
        "",
        f"This section was produced automatically by the risk analysis "
        f"engine before final output: **{crit} critical, {high} high, "
        f"{med} medium** risks identified across the selected operations. "
        f"Expected NPT (probability-weighted): **{total_npt:,.0f} hrs**.",
        "",
    ]

    # --- High/Critical risks with mitigation ------------------------------
    top = [r for r in risks
           if r.severity in (RiskLevel.CRITICAL, RiskLevel.HIGH)]
    if top:
        lines.append("### Key Risks & Mitigation")
        lines.append("")
        lines.append("| Risk | Severity | Probability | NPT (hrs) | Mitigation / Contingency |")
        lines.append("|---|---|---|---|---|")
        for r in top[:12]:
            plan = r.contingency_plans[0].action if r.contingency_plans else "—"
            lines.append(
                f"| {r.problem} | {r.severity.value} | "
                f"{r.probability:.0%} | {r.npt_hours:.0f} | {plan} |")
        lines.append("")

    # --- Contingency actions ----------------------------------------------
    plans = []
    for r in risks[:12]:
        for p in r.contingency_plans[:2]:
            plans.append((p.priority, r.problem, p))
    plans.sort(key=lambda x: x[0])
    if plans:
        lines.append("### Contingency Actions (priority order)")
        lines.append("")
        lines.append("| # | Risk | Action | Success | Duration (hrs) |")
        lines.append("|---|---|---|---|---|")
        for idx, (pri, problem, p) in enumerate(plans[:10], 1):
            lines.append(
                f"| {idx} | {problem[:40]} | {p.action} | "
                f"{p.success_probability:.0%} | {p.duration_hours:.1f} |")
        lines.append("")

    # --- Forgotten-items checklist ----------------------------------------
    if forgotten:
        lines.append("### Pre-Job Best-Practice Checklist (auto-generated)")
        lines.append("")
        for item in forgotten[:12]:
            lines.append(f"- [ ] {item.description} — "
                         f"*{item.recommended_action}*")
        lines.append("")

    # --- User confirmation answers ----------------------------------------
    if answers:
        lines.append("### Risk Confirmation (answered by the planner)")
        lines.append("")
        lines.append("| # | Question | Status |")
        lines.append("|---|---|---|")
        for idx, (q, ok) in enumerate(answers.items(), 1):
            status = "✅ Addressed in program" if ok else "⚠️ Needs follow-up"
            lines.append(f"| {idx} | {q} | {status} |")
        lines.append("")

    if sequence:
        lines.append("### Operations Analyzed")
        lines.append("")
        lines.append("```")
        lines.append(sequence[:1500])
        lines.append("```")
        lines.append("")

    return "\n".join(lines)
