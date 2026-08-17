# ============================================================================
# STRUCTURED PROCEDURE STEP MODEL
# File: structured_steps.py
# Audit item: each Procedure Step must carry:
#   Precondition, Action, Parameter, Acceptance Criteria, Hazard, Control,
#   Required Equipment, Role, Record Required, Escalation,
#   Hold Point / Witness Point flags.
#
# Provides: a structured dataclass, conversion from plain text steps
# (heuristic field extraction), and markdown rendering used by the
# Procedure Manager / wizard.
# ============================================================================

import re
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional


@dataclass
class StructuredStep:
    step_no: int = 0
    title: str = ""
    action: str = ""                # what to do
    precondition: str = ""          # what must be true before
    parameter: str = ""             # key parameter/value (pressure, depth...)
    acceptance: str = ""            # how to confirm success
    hazard: str = ""                # main hazard of the step
    control: str = ""               # control measure
    equipment: str = ""             # required equipment
    role: str = ""                  # responsible role
    record: str = ""                # record/document to produce
    escalation: str = ""            # when/who to escalate
    hold_point: bool = False        # operations must stop for approval
    witness_point: bool = False     # witness required at this step

    def to_dict(self) -> Dict:
        return asdict(self)

    def to_markdown(self) -> str:
        L = [f"### Step {self.step_no}: {self.title or self.action}", ""]
        if self.action:
            L.append(f"**Action:** {self.action}")
        if self.precondition:
            L.append(f"**Precondition:** {self.precondition}")
        if self.parameter:
            L.append(f"**Parameter:** {self.parameter}")
        if self.acceptance:
            L.append(f"**Acceptance criteria:** {self.acceptance}")
        if self.hazard:
            L.append(f"**Hazard:** {self.hazard}")
        if self.control:
            L.append(f"**Control:** {self.control}")
        if self.equipment:
            L.append(f"**Equipment:** {self.equipment}")
        if self.role:
            L.append(f"**Role:** {self.role}")
        if self.record:
            L.append(f"**Record required:** {self.record}")
        if self.escalation:
            L.append(f"**Escalation:** {self.escalation}")
        flags = []
        if self.hold_point:
            flags.append("⛔ **HOLD POINT**")
        if self.witness_point:
            flags.append("👁 **WITNESS POINT**")
        if flags:
            L.append(" | ".join(flags))
        return "\n".join(L)


# ---------------------------------------------------------------------------
# HEURISTIC EXTRACTION from a plain-text step
# ---------------------------------------------------------------------------

_ROLE_KEYWORDS = {
    "driller": "Driller", "toolpusher": "Toolpusher", "supervisor": "Supervisor",
    "company man": "Company Man", "mud engineer": "Mud Engineer",
    "cementer": "Cementer", "derrickman": "Derrickman",
    "electrician": "Electrician", "mechanic": "Mechanic",
    "safety officer": "Safety Officer", "logger": "Mud Logger",
}

_PRESSURE_RE = re.compile(r"\b\d{3,5}\s*psi\b", re.IGNORECASE)
_DEPTH_RE = re.compile(r"\b\d{3,5}\s*(?:m|ft)\b", re.IGNORECASE)
_TORQUE_RE = re.compile(r"\b\d{3,5}\s*(?:ft-?lb|ftlb)\b", re.IGNORECASE)
_WEIGHT_RE = re.compile(r"\b\d{1,3}(?:\.\d+)?\s*(?:ppg|pcf)\b", re.IGNORECASE)


def structure_step(text: str, step_no: int = 1) -> StructuredStep:
    """Best-effort structured extraction from a raw step sentence."""
    t = text.strip()
    s = StructuredStep(step_no=step_no, action=t)

    # title = first phrase before first verb-ish separator
    m = re.match(r"^([A-Z][^,.;]{3,60}?)(?:[,.;]|\s+and\s+|\s+to\s+)", t)
    if m and len(m.group(1)) < 60:
        s.title = m.group(1).strip()
        s.action = t[len(m.group(0)):] if len(t) > len(m.group(0)) else t

    # parameter extraction
    params = []
    p = _PRESSURE_RE.search(t)
    if p:
        params.append(p.group(0))
    d = _DEPTH_RE.search(t)
    if d:
        params.append(d.group(0))
    w = _WEIGHT_RE.search(t)
    if w:
        params.append(w.group(0))
    q = _TORQUE_RE.search(t)
    if q:
        params.append(q.group(0))
    s.parameter = "; ".join(params)

    # acceptance: phrases indicating verification
    acc = re.search(
        r"(?:verify|confirm|ensure|check)\s+([^.;]{8,120})", t, re.IGNORECASE)
    if acc:
        s.acceptance = acc.group(0).strip()

    # hazard detection
    for hazard in ("kick", "lost circulation", "stuck pipe", "H2S", "blowout",
                   "pack-off", "gas", "fire", "dropped object", "high pressure",
                   "hole collapse"):
        if hazard in t.lower():
            s.hazard = hazard.capitalize()
            s.control = (f"Follow {hazard.lower()} prevention procedure; "
                         "monitor warning signs; brief crew before start.")
            break

    # role detection
    for kw, role in _ROLE_KEYWORDS.items():
        if kw in t.lower():
            s.role = role
            break

    # hold/witness points from explicit phrases
    if re.search(r"\bhold\s*point\b|\bapproval\s*required\b|\bpermit\b",
                 t, re.IGNORECASE):
        s.hold_point = True
    if re.search(r"\bwitness\b|\bcompany\s*rep(?:resentative)?\s*to\s*"
                 r"(?:observe|witness)\b", t, re.IGNORECASE):
        s.witness_point = True

    # equipment hints
    for eq in ("casing", "bit", "BHA", "packer", "liner", "BOP", "mud pump",
               "cement unit", "slickline", "CTU", "scraper", "jars", "overshot"):
        if eq in t.lower():
            s.equipment = eq.upper() if eq.isupper() else eq.title()
            break

    return s


def steps_markdown(steps: List[str]) -> str:
    """Render a list of raw steps as structured markdown."""
    out = []
    for i, s in enumerate(steps, 1):
        out.append(structure_step(s, i).to_markdown())
    return "\n\n".join(out)


if __name__ == "__main__":
    raw = ("Run 9-5/8\" casing to 3915 m; verify fill with trip tank and "
           "check returns; hold point before cementing; witness by "
           "company rep. Torque to 12000 ft-lb.")
    ss = structure_step(raw, 1)
    print(ss.to_markdown())
