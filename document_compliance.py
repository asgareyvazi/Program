# ============================================================================
# DOCUMENT COMPLIANCE ENGINE
# File: document_compliance.py
# Audit item: Word Generator must run a compliance gate before Generate —
# completeness of required sections, unresolved critical findings, and
# reference coverage. Produces a compliance report card for the document.
# ============================================================================

import re
from typing import Dict, List, Tuple

# Required sections per document kind (template family)
# key: template key prefix -> required section title fragments
REQUIRED_SECTIONS: Dict[str, List[str]] = {
    "drilling_program": ["scope", "well", "casing", "mud", "bha",
                         "hydraulic", "well control", "cement"],
    "advanced_drilling_program": ["scope", "well", "casing", "mud", "bha",
                                  "hydraulic", "well control", "directional"],
    "offshore_drilling_program": ["scope", "well", "casing", "mud",
                                  "hydraulic", "completion"],
    "workover_program": ["introduction", "well information", "reservoir",
                         "completion", "operation sequence", "kill"],
    "reentry_program": ["objective", "well information", "operation sequence",
                        "directional", "completion"],
    "cementing_program": ["design", "slurry", "displacement", "job",
                          "evaluation"],
    "well_kill_program": ["procedure", "shut-in", "kill", "pressure"],
    "bop_test_procedure": ["test", "pressure", "acceptance"],
    "stuck_pipe_procedure": ["diagnostic", "freeing", "prevention"],
    "fishing_program": ["assembly", "procedure", "fish"],
    "h2s_emergency_procedure": ["alarm", "drill", "evacuation", "first aid"],
    "master_": ["scope", "parameters", "prerequisites", "operation steps",
                "checklist", "references"],
}

DEFAULT_REQUIRED = ["scope", "procedure", "safety", "references"]


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def required_for(template_key: str) -> List[str]:
    for prefix, reqs in REQUIRED_SECTIONS.items():
        if template_key.startswith(prefix):
            return reqs
    return DEFAULT_REQUIRED


def compliance_check(template_key: str, markdown: str,
                     findings: List = None) -> Dict:
    """Run the compliance gate over generated markdown.

    Returns dict with: score, missing_sections, critical_findings,
    has_references, report.
    """
    md = markdown.lower()
    sections = {_norm(s) for s in re.findall(r"^##\s+(.+)$", markdown, re.M)}

    reqs = required_for(template_key)
    missing = []
    for r in reqs:
        rn = _norm(r)
        # a section counts as present if the heading or the phrase appears
        if not any(rn in s or s in rn for s in sections) and rn not in md:
            missing.append(r)
    score = max(0, 100 - len(missing) * 10)

    # critical findings from the validation engine (if passed in)
    crit = [f for f in (findings or []) if getattr(f, "level", "") == "CRITICAL"]

    has_refs = "reference" in md or "provenance" in md
    has_validation = "validation" in md
    has_readiness = "readiness" in md

    ok = (len(missing) == 0 and len(crit) == 0 and has_refs
          and has_validation and has_readiness)
    report = {
        "template_key": template_key,
        "score": score,
        "missing_sections": missing,
        "critical_findings": [f.code for f in crit],
        "has_references": has_refs,
        "has_validation": has_validation,
        "has_readiness": has_readiness,
        "compliant": ok,
    }
    return report


def compliance_markdown(report: Dict, operator: str = "") -> str:
    """Human-readable compliance report card appended to the document."""
    L = ["## DOCUMENT COMPLIANCE REPORT", ""]
    if operator:
        L.append(f"**Operator:** {operator}")
        L.append("")
    status = "COMPLIANT ✅" if report["compliant"] else "NOT COMPLIANT ⚠️"
    L.append(f"**Status: {status} — Score {report['score']}/100**")
    L.append("")
    if report["missing_sections"]:
        L.append("**Missing required sections:**")
        L.append("")
        for s in report["missing_sections"]:
            L.append(f"- [ ] {s}")
        L.append("")
    if report["critical_findings"]:
        L.append("**Unresolved CRITICAL findings:**")
        L.append("")
        for c in report["critical_findings"]:
            L.append(f"- ⛔ {c}")
        L.append("")
    L.append("| Check | Status |")
    L.append("|---|---|")
    L.append(f"| Required sections | "
             f"{'✅' if not report['missing_sections'] else '⚠️'} |")
    L.append(f"| Critical findings resolved | "
             f"{'✅' if not report['critical_findings'] else '⛔'} |")
    L.append(f"| References / provenance | "
             f"{'✅' if report['has_references'] else '⚠️'} |")
    L.append(f"| Validation record | "
             f"{'✅' if report['has_validation'] else '⚠️'} |")
    L.append(f"| Readiness record | "
             f"{'✅' if report['has_readiness'] else '⚠️'} |")
    L.append("")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    # demo: a compliant-ish document
    demo_md = """## 1. SCOPE
## 2. WELL INFORMATION
## 3. CASING PROGRAM
## 4. MUD PROGRAM
## 5. BHA & BITS
## 6. HYDRAULICS
## 7. WELL CONTROL
## 8. CEMENTING
## 9. SAFETY
## VALIDATION & COMPLIANCE
## PROGRAM READINESS SCORE
## REFERENCE DOCUMENTS
"""
    r = compliance_check("drilling_program", demo_md, [])
    print("score:", r["score"], "| missing:", r["missing_sections"],
          "| compliant:", r["compliant"])
