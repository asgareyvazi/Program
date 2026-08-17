# ============================================================================
# HEADLESS GENERATION PIPELINE
# File: generation_pipeline.py
# Audit item (P2 / buyer Q14): the deterministic document-generation core,
# shared by the desktop wizard, the REST API server (api_server.py) and the
# template regression suite.  No Qt required.
#
# Mirrors the wizard's _GeneratePage flow:
#   fill_template -> render_selected -> neutralize -> validation -> readiness
#   -> standards -> compliance -> deep engineering -> calculation register
#   -> Word render
# ============================================================================

import os
from typing import Dict, List, Optional

from wizard_engine import (fill_template, render_selected, extract_sections,
                           neutralize_text, md_to_docx)
from wizard_library import ALL_TEMPLATES
from wizard_procedures import PROCEDURE_TEMPLATES
from wizard_offshore import OFFSHORE_TEMPLATES
from wizard_master import build_master_templates
from validation_engine import validate_well_data, findings_markdown
from operations_engine import readiness_markdown
from standards_engine import compliance_markdown as scm
from document_compliance import compliance_check, compliance_markdown
from engineering_register import compute_register, register_markdown
from engineering_deep import deep_verify_markdown


def all_templates() -> List:
    """All 51 wizard templates (programs + procedures + offshore + master)."""
    return (list(ALL_TEMPLATES) + list(PROCEDURE_TEMPLATES) +
            list(OFFSHORE_TEMPLATES) + build_master_templates())


def template_by_key(key: str):
    for t in all_templates():
        if t.key == key:
            return t
    return None


def build_document_markdown(tdef, values: Dict,
                            operator: str = "", contractor: str = "",
                            rop_calib: Optional[Dict] = None) -> str:
    """Assemble the full document markdown (all sections selected)."""
    values = dict(values or {})
    md = fill_template(tdef, values)
    heads = [h for h, _ in extract_sections(md)]
    md = render_selected(md, heads)
    md = neutralize_text(md, operator, contractor)

    # validation
    findings = validate_well_data(values)
    fmd = findings_markdown(findings, operator)
    if fmd:
        md = md.rstrip() + "\n\n---\n\n" + fmd
    # readiness
    rmd = readiness_markdown(values, operator)
    if rmd:
        md = md.rstrip() + "\n\n---\n\n" + rmd
    # time breakdown summary (from the time-breakdown project database)
    try:
        from cbs_db import get_time_breakdown_summary
        tb = get_time_breakdown_summary()
        if tb.get("total_days", 0) > 0:
            tlines = ["## TIME BREAKDOWN SUMMARY", ""]
            if tb.get("sections"):
                tlines.append("| Phase |")
                tlines.append("|---|")
                for s in tb["sections"]:
                    tlines.append(f"| {s} |")
                tlines.append("")
            tlines.append(f"**Total planned: {tb['total_days']:,.2f} days**"
                          + (f" (+ {tb['contingency_days']:,.2f} days "
                             "contingency)"
                             if tb.get("contingency_days", 0) > 0 else "")
                          + f" — {tb.get('rows', 0)} activity rows"
                          + (f", project: {tb['name']}"
                             if tb.get("name") else "") + ".")
            tlines.append("")
            md = md.rstrip() + "\n\n---\n\n" + "\n".join(tlines)
    except Exception:
        pass
    # standards
    smd = scm(values, operator)
    if smd:
        md = md.rstrip() + "\n\n---\n\n" + smd
    # document compliance
    comp = compliance_check(tdef.key, md)
    cmd = compliance_markdown(comp, operator)
    if cmd:
        md = md.rstrip() + "\n\n---\n\n" + cmd
    # deep engineering verification
    dmd = deep_verify_markdown(values, rop_calib, operator)
    if dmd:
        dmd = neutralize_text(dmd, operator, contractor)
        md = md.rstrip() + "\n\n---\n\n" + dmd
    # calculation register
    rows = compute_register(values)
    rmd2 = register_markdown(rows, operator)
    if rmd2:
        rmd2 = neutralize_text(rmd2, operator, contractor)
        md = md.rstrip() + "\n\n---\n\n" + rmd2
    return md


def generate_document(tdef, values: Dict,
                      meta: Optional[Dict] = None,
                      options: Optional[Dict] = None,
                      out_path: str = "",
                      rop_calib: Optional[Dict] = None) -> Dict:
    """Generate a Word document; returns a report dict.

    report: {ok, path, sections, register_rows, findings (counts),
             readiness_score, standards_count, compliance_score}
    """
    values = dict(values or {})
    operator = str(values.get("operator") or meta.get("operator") or "")
    contractor = str(values.get("contractor") or meta.get("contractor") or "")
    md = build_document_markdown(tdef, values, operator, contractor,
                                 rop_calib=rop_calib)

    meta = dict(meta or {})
    meta.setdefault("title", tdef.name)
    meta.setdefault("operator", operator)
    meta.setdefault("contractor", contractor)
    options = dict(options or {})
    if out_path:
        os.makedirs(os.path.dirname(os.path.abspath(out_path)),
                    exist_ok=True)
    ok = md_to_docx(md, out_path, meta, options)

    findings = validate_well_data(values)
    r = readiness_markdown(values, operator)
    rows = compute_register(values)
    # section list present in the final markdown
    sections = [h for h, _ in extract_sections(md)]

    return {
        "ok": bool(ok) and bool(out_path) and os.path.exists(out_path),
        "path": out_path,
        "sections": sections,
        "register_rows": len(rows),
        "validation_findings": len(findings),
        "validation_critical": sum(1 for f in findings if f.is_blocking),
        "readiness_included": "PROGRAM READINESS SCORE" in md,
        "compliance_included": "DOCUMENT COMPLIANCE REPORT" in md,
        "register_included": "ENGINEERING CALCULATION REGISTER" in md,
        "characters": len(md),
    }


if __name__ == "__main__":
    t = template_by_key("drilling_program")
    print(f"pipeline selftest: {len(all_templates())} templates")
    print(f"  {t.icon} {t.name}: {len(t.inputs)} inputs")
    print("generation_pipeline OK")
