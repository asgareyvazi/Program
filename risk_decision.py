# ============================================================================
# RISK DECISION ENGINE
# File: risk_decision.py
# Audit item: move from a risk list to a decision/response engine — each
# risk has trigger, diagnostics, mitigation, escalation, recovery and
# acceptance criteria. Extends the risk analyzer with an executable layer.
# ============================================================================

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RiskDecision:
    code: str
    name: str
    category: str
    triggers: List[str] = field(default_factory=list)   # warning signs
    diagnostics: List[str] = field(default_factory=list)  # how to confirm
    mitigation: List[str] = field(default_factory=list)   # preventive
    escalation: List[str] = field(default_factory=list)   # who/when to escalate
    recovery: List[str] = field(default_factory=list)     # response in order
    acceptance: List[str] = field(default_factory=list)   # criteria to close
    owner: str = "Drilling Supervisor"
    timeout_min: int = 15


# ---------------------------------------------------------------------------
# KNOWLEDGE BASE — executable risk decisions (extends problem DB with action)
# ---------------------------------------------------------------------------

RISK_DECISIONS: List[RiskDecision] = [
    RiskDecision(
        code="RD-001", name="Kick / Influx", category="Well Control",
        triggers=["Flow at flowline with pumps off", "Pit volume gain",
                  "Flow increase while drilling", "Drilling break"],
        diagnostics=["Flow check", "Trip tank monitor", "Compare SIDPP/SICP",
                     "Gas readings trend"],
        mitigation=["Maintain design MW + margin", "Trip procedures & flow checks",
                    "Trip tank discipline", "Well-control drills"],
        escalation=["Toolpusher immediately", "Company man < 5 min",
                    "Well control instructor on call"],
        recovery=["Shut in (close BOP)", "Record SIDPP/SICP & gain",
                  "Driller's or Wait & Weight method", "Circulate at kill rate"],
        acceptance=["Well static on flow check", "Pit level stable",
                    "Kill mud weight circulated", "SIDPP = 0"]),
    RiskDecision(
        code="RD-002", name="Lost Circulation", category="Drilling Fluids",
        triggers=["Mud level drop", "Loss of returns at shaker",
                  "Pit volume decrease"],
        diagnostics=["Pit volume trend", "Check surface losses",
                     "Calibrate trip tank", "Fracture gradient check"],
        mitigation=["Keep ECD below FG", "LCM sweeps in known zones",
                    "Controlled ROP", "Casing off weak zones early"],
        escalation=["Toolpusher < 10 min", "Mud engineer",
                    "Company man if severe"],
        recovery=["Pick up off bottom", "Reduce pump rate",
                  "Spot LCM / gunk pill", "Cement plug if no returns"],
        acceptance=["Returns regained", "Pit level stable",
                    "Well static", "Loss zone isolated or cured"]),
    RiskDecision(
        code="RD-003", name="Stuck Pipe — Differential", category="Stuck Pipe",
        triggers=["Pipe static across permeable zone", "No rotation/circulation",
                  "Overbalance high"],
        diagnostics=["Free point indicator", "Check filter cake",
                     "Torque/drag history", "Stuck mechanism checklist"],
        mitigation=["Minimize overbalance", "Thin filter cake",
                    "Keep pipe moving", "Pipe-free agents"],
        escalation=["Toolpusher < 15 min", "Drilling engineer on call"],
        recovery=["Spot pipe-free pill", "Reduce MW if safe",
                  "Jar with accelerator", "Back-off & sidetrack if stuck"],
        acceptance=["Pipe free", "Circulation restored", "No fish left"]),
    RiskDecision(
        code="RD-004", name="H2S Release", category="HSE",
        triggers=["H2S alarm", "Gas reading increase", "Rotten egg odour"],
        diagnostics=["H2S sensors", "Personal monitors", "Wind direction"],
        mitigation=["H2S training & drills", "Breathing air on location",
                    "Sensors calibrated", "Upwind muster points"],
        escalation=["Sound alarm", "Muster & headcount", "Emergency response team",
                    "Local authorities if community risk"],
        recovery=["Evacuate upwind", "Shut in well if safe", "First aid for exposure",
                  "Ventilate & monitor"],
        acceptance=["All personnel accounted", "H2S below safe level",
                    "Incident reported & investigated"]),
    RiskDecision(
        code="RD-005", name="Wellbore Instability / Pack-off", category="Hole Stability",
        triggers=["Torque/drag increase", "Cavings at shaker", "Pack-off pressure",
                  "Fill on bottom"],
        diagnostics=["Cavings analysis", "Caliper log", "ECD trend",
                     "Hole condition while tripping"],
        mitigation=["Inhibitive mud", "Adequate MW for stability",
                    "Sweeps & wiper trips", "Minimize exposure time"],
        escalation=["Toolpusher < 15 min", "Mud engineer", "Geomechanics support"],
        recovery=["Circulate & ream", "High-vis sweep", "Wiper trip",
                  "Raise MW in steps if required"],
        acceptance=["Hole stable", "No further cavings", "Trips normal"]),
]


def find_decisions(risk_text: str) -> List[RiskDecision]:
    """Match risk descriptions against the decision base (keyword scoring)."""
    t = risk_text.lower()
    out = []
    for d in RISK_DECISIONS:
        score = 0
        # name keywords: each significant word of the risk name scores
        for w in re.findall(r"[a-z0-9]{2,}", d.name.lower()):
            if w in t:
                score += 1
        # trigger phrases score higher
        score += sum(2 for tr in d.triggers if tr.lower() in t)
        if score > 0:
            out.append((score, d))
    out.sort(key=lambda x: -x[0])
    return [d for _, d in out]


def decision_markdown(decisions: List[RiskDecision]) -> str:
    if not decisions:
        return ""
    L = ["## RISK DECISION & RESPONSE MATRIX", "",
         "| Code | Risk | Trigger | First Response | Escalation | "
         "Acceptance Criteria |", "|---|---|---|---|---|---|"]
    for d in decisions:
        L.append(f"| {d.code} | {d.name} | {d.triggers[0] if d.triggers else ''} | "
                 f"{d.recovery[0] if d.recovery else ''} | "
                 f"{d.escalation[0] if d.escalation else ''} | "
                 f"{d.acceptance[0] if d.acceptance else ''} |")
    L.append("")
    for d in decisions:
        L.append(f"### {d.code} — {d.name} (Owner: {d.owner})")
        L.append("")
        L.append("**Triggers (warning signs):**")
        L.extend(f"- {t}" for t in d.triggers)
        L.append("")
        L.append("**Diagnostics (confirm the condition):**")
        L.extend(f"- {x}" for x in d.diagnostics)
        L.append("")
        L.append("**Mitigation (prevention):**")
        L.extend(f"- {m}" for m in d.mitigation)
        L.append("")
        L.append("**Escalation:**")
        L.extend(f"- {e}" for e in d.escalation)
        L.append("")
        L.append("**Recovery (in order):**")
        for i, r in enumerate(d.recovery, 1):
            L.append(f"{i}. {r}")
        L.append("")
        L.append("**Acceptance criteria (close-out):**")
        L.extend(f"- [ ] {a}" for a in d.acceptance)
        L.append("")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    # demo: match against a risk description
    text = "Potential kick from over-pressured zone; lost circulation risk in fractured limestone; H2S present"
    ds = find_decisions(text)
    print("matched:", [d.code for d in ds])
    print(decision_markdown(ds)[:300])
