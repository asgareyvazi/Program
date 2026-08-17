# ============================================================================
# DIAGNOSTIC DECISION TREES — STUCK PIPE & FISHING
# File: engineering_decisions.py
# Audit items (P1):
#   - Stuck Pipe: the audit asked for a complete diagnostic tree
#   - Fishing: the audit asked for a deeper decision tree / tool selection
#
# Two engines:
#   1. stuck_pipe_diagnosis(rotate, circulate, move) — symptom-based
#      branching that walks the rig crew from first response to
#      free-point/back-off/fishing.
#   2. fishing_tool_selection(fish description/geometry) — picks the
#      primary fishing tool and backups by fish type.
# Both render as Word-ready markdown sections. Deterministic, testable.
# ============================================================================

from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# STUCK PIPE DIAGNOSTIC TREE
# ---------------------------------------------------------------------------

def stuck_pipe_diagnosis(rotate: bool, circulate: bool,
                         move: bool) -> List[Dict]:
    """Diagnostic branching from three binary symptoms.

    rotate / circulate / move — can the string still rotate, circulate
    and move?  Returns an ordered list of decision steps:
      {step, condition, interpretation, actions, escalate}
    """
    steps: List[Dict] = []

    if not rotate and not circulate and not move:
        steps.append({
            "step": 1,
            "condition": "No rotation, no circulation, no pipe movement",
            "interpretation": "Fully stuck — mechanical pack-off, key seat "
                              "or junk (possible collapse in open hole).",
            "actions": [
                "1. Attempt to establish circulation at reduced rate "
                "(≤ ½ normal) — record pressures.",
                "2. Work pipe within safe limits (up/down) and apply "
                "jarring (up-jar then down-jar) per torque/drag limits.",
                "3. If no movement after 2–3 attempts: run FREE POINT "
                "indicator, back-off at the free point, lay out the free "
                "string and prepare FISHING.",
                "4. If circulation is lost while trying: follow the "
                "lost-circulation / well-control response first.",
            ],
            "escalate": "Free Point & Back-Off (FI-02) → Fishing (FI-01)",
        })
    elif not rotate and not circulate and move:
        steps.append({
            "step": 1,
            "condition": "Cannot rotate or circulate, but pipe moves",
            "interpretation": "Partial sticking — early pack-off / "
                              "mechanical restriction; string not yet "
                              "fully immobilized.",
            "actions": [
                "1. Keep moving pipe (within limits) to prevent full "
                "pack-off.",
                "2. Attempt circulation at low rate with the pumps; if "
                "returns are lost, treat as losses first.",
                "3. Ream / work through the tight spot in small steps; "
                "avoid overpull that could key-seat.",
            ],
            "escalate": "If full stick develops → step 1 (fully stuck)",
        })
    elif rotate and circulate and not move:
        steps.append({
            "step": 1,
            "condition": "Can rotate and circulate, cannot move up/down",
            "interpretation": "Mechanical restriction while tripping — "
                              "likely undergauge hole, ledges or key seat "
                              "on the low side.",
            "actions": [
                "1. Stop pulling; rotate in place and ream through the "
                "restriction at low RPM.",
                "2. Circulate and condition the hole; pump hi-vis or "
                "sweep pills to clean the annulus.",
                "3. Work the string with controlled slack-off; if the "
                "restriction clears, continue at reduced speed.",
            ],
            "escalate": "Key-seat diagnosis (SP-03); if stuck → step 1",
        })
    elif circulate and not rotate and not move:
        steps.append({
            "step": 1,
            "condition": "Can circulate, cannot rotate or move",
            "interpretation": "Classic DIFFERENTIAL STICKING signature "
                              "(permeable zone, static time, overbalance).",
            "actions": [
                "1. DO NOT overpull — reduce the differential pressure: "
                "lower the pump rate and, if safe, reduce mud weight "
                "per the design envelope.",
                "2. Spot a pipe-loosening / diesel-oil or surfactant pill "
                "across the stuck interval; allow soak time.",
                "3. Jar down repeatedly with the jars in the string; "
                "maintain circulation while jarring.",
                "4. If still stuck: free point & back-off, then fish.",
            ],
            "escalate": "Differential Sticking (SP-01) → Free Point (FI-02)",
        })
    elif rotate and not circulate and move:
        steps.append({
            "step": 1,
            "condition": "Can rotate and move, cannot circulate",
            "interpretation": "Plugged bit / nozzles or pack-off at the "
                              "bit — flow path blocked.",
            "actions": [
                "1. Stop rotation; attempt circulation at low rate — "
                "record standpipe pressure behaviour.",
                "2. If no flow: pull clear of bottom, try to 'bump' the "
                "pumps; if the string clears, run in and jet ream.",
                "3. Prepare for a bit-run / BHA inspection if the "
                "plugging persists.",
            ],
            "escalate": "Bit balling / plugged nozzles (HS-03, DP-01)",
        })
    else:  # rotate & circulate & move — not stuck
        steps.append({
            "step": 1,
            "condition": "String can rotate, circulate and move",
            "interpretation": "No sticking indication — continue normal "
                              "operations while monitoring torque, drag "
                              "and trip-tank volumes.",
            "actions": [
                "1. Monitor overpull on connections and trip tank "
                "gains/losses.",
                "2. Maintain mud properties and hole-cleaning "
                "parameters (AV ≥ critical).",
            ],
            "escalate": "—",
        })

    # common step 2: documentation & barrier to escalation
    steps.append({
        "step": 2,
        "condition": "All cases",
        "interpretation": "Record the event for the lessons-learned and "
                          "NPT registers.",
        "actions": [
            "1. Log time, depth, mud weight, pump pressure, overpull, "
            "and all attempts made.",
            "2. Report to the operator per the well-site reporting "
            "procedure; register NPT with root cause.",
        ],
        "escalate": "NPT register + Lessons Learned",
    })
    return steps


# ---------------------------------------------------------------------------
# FISHING TOOL SELECTION
# ---------------------------------------------------------------------------

def _guess_fish_type(fish_desc: str) -> str:
    t = (fish_desc or "").lower()
    if any(k in t for k in ("wireline", "cable", "slickline", "e-line",
                            "elog")):
        return "wireline"
    if any(k in t for k in ("pipe", "drill", "string", "tubing", "casing",
                            "liner", "bha", "collar")):
        return "pipe"
    if any(k in t for k in ("packer", "bridge plug", "plug")):
        return "packer"
    if any(k in t for k in ("junk", "milling", "debris", "bit cone",
                            "roller", "nozzle")):
        return "junk"
    if any(k in t for k in ("stabilizer", "motor", "mwd", "lwd")):
        return "bha"
    return "unknown"


def fishing_tool_selection(fish_desc: str = "",
                           fish_od_in: float = 0.0,
                           fish_id_in: float = 0.0,
                           fish_top_ft: float = 0.0,
                           condition: str = "") -> Dict:
    """Pick the primary fishing tool and backups for the fish."""
    ftype = _guess_fish_type(fish_desc)
    tools: Dict[str, Dict] = {
        "pipe": {
            "primary": "Overshot (spiral grapple, dressed to fish OD "
                       "±1/8 in)",
            "backups": ["Releaseable overshot with mill-to-release",
                        "Taper tap (if fish top damaged)",
                        "Spear (if fish ID accessible)"],
            "prep": "Free point & back-off first (FI-02); dress the "
                    "overshot grapple to the measured fish OD; verify "
                    "catch with weight-on-fish and jarring.",
        },
        "bha": {
            "primary": "Overshot dressed to the BHA collar OD, or "
                       "hydraulic spear",
            "backups": ["Bumper sub + accelerator above the overshot",
                        "Magnet / junk basket if debris on top of fish"],
            "prep": "Screw-in or wash-over; use washover pipe when the "
                    "fish is wall-stuck.",
        },
        "junk": {
            "primary": "Junk basket (reverse-circulation type) for small "
                       "debris",
            "backups": ["Milling shoe / flat-bottom mill for larger "
                        "pieces",
                        "Permanent magnet (if ferromagnetic debris)"],
            "prep": "Circulate debris to surface when possible; otherwise "
                    "mill the junk to small pieces and basket them.",
        },
        "packer": {
            "primary": "Packer retriever / releasing spear with "
                       "left-hand safety joint",
            "backups": ["Milling assembly (packer milling) if retrieval "
                        "fails",
                        "Wireline-conveyed pulling tool for "
                        "wireline-set plugs"],
            "prep": "Confirm packer type (retrievable vs permanent); "
                    "run the appropriate retrieving tool with jars.",
        },
        "wireline": {
            "primary": "Wireline spear / rope spear (fishing neck "
                       "assembly)",
            "backups": ["Wireline cutting tool to part the cable at a "
                        "known depth",
                        "Overshot with fine grapple if the tool is "
                        "caught"],
            "prep": "Cut the cable above the stuck point, run a rope "
                    "spear, engage, and pull; never overpull the cable.",
        },
        "unknown": {
            "primary": "Bend survey / impression block to identify the "
                       "fish top",
            "backups": ["Overshot (universal) after identification",
                        "Magnet + junk basket combination run"],
            "prep": "Run an impression block or bend survey first to "
                    "identify fish geometry and orientation.",
        },
    }
    sel = tools.get(ftype, tools["unknown"])
    geom = []
    if fish_od_in > 0:
        geom.append(f"OD {fish_od_in:g} in")
    if fish_id_in > 0:
        geom.append(f"ID {fish_id_in:g} in")
    if fish_top_ft > 0:
        geom.append(f"fish top at {fish_top_ft:,.0f} ft")
    return {
        "fish_type": ftype,
        "fish_desc": fish_desc or "—",
        "geometry": "; ".join(geom) or "not provided",
        "primary_tool": sel["primary"],
        "backup_tools": sel["backups"],
        "preparation": sel["prep"],
        "condition": condition or "—",
    }


# ---------------------------------------------------------------------------
# Markdown sections
# ---------------------------------------------------------------------------

def stuck_pipe_markdown(values: Dict, operator: str = "") -> str:
    """Word-ready STUCK PIPE DIAGNOSTIC TREE section."""
    def _pick(*keys) -> str:
        for k in keys:
            s = str(values.get(k, "") or "").strip()
            if s:
                return s
        return ""

    rotate = _pick("can_rotate")
    circulate = _pick("can_circulate")
    move = _pick("can_move_pipe")
    if not (rotate or circulate or move):
        return ""   # no symptoms provided — skip section
    flags = {
        "rotate": rotate.lower() in ("yes", "y", "true", "1"),
        "circulate": circulate.lower() in ("yes", "y", "true", "1"),
        "move": move.lower() in ("yes", "y", "true", "1"),
    }
    steps = stuck_pipe_diagnosis(flags["rotate"], flags["circulate"],
                                 flags["move"])
    op = (operator or "").strip() or "the Operator"
    L = [
        "## STUCK PIPE DIAGNOSTIC TREE",
        "",
        f"Symptoms: rotate = **{rotate}**, circulate = **{circulate}**, "
        f"pipe movement = **{move}**.",
        "",
    ]
    for s in steps:
        L.append(f"### Step {s['step']} — {s['condition']}")
        L.append("")
        L.append(f"**Interpretation:** {s['interpretation']}")
        L.append("")
        L.append("**Actions:**")
        L.append("")
        for a in s["actions"]:
            L.append(f"- {a}")
        L.append("")
        if s["escalate"] != "—":
            L.append(f"**Escalate:** {s['escalate']}")
            L.append("")
    L.append(f"*Diagnostic tree computed deterministically for {op}; "
             "always follow the operator's well-control and stuck-pipe "
             "policies first.*")
    return "\n".join(L)


def fishing_markdown(values: Dict, operator: str = "") -> str:
    """Word-ready FISHING TOOL SELECTION section."""
    def _pick(*keys) -> str:
        for k in keys:
            s = str(values.get(k, "") or "").strip()
            if s:
                return s
        return ""

    desc = _pick("fish_description", "fish_condition", "fish_desc")
    if not desc:
        return ""
    sel = fishing_tool_selection(
        fish_desc=desc,
        fish_od_in=float(_pick("fish_od") or 0) or 0.0,
        fish_id_in=float(_pick("fish_id") or 0) or 0.0,
        fish_top_ft=float(_pick("fish_top") or 0) or 0.0,
        condition=_pick("fish_condition"))
    op = (operator or "").strip() or "the Operator"
    L = [
        "## FISHING TOOL SELECTION",
        "",
        f"**Fish:** {sel['fish_desc']}",
        f"**Classification:** {sel['fish_type']}  |  "
        f"**Geometry:** {sel['geometry']}",
        "",
        f"**Primary tool:** {sel['primary_tool']}",
        "",
        "**Backup tools:**",
        "",
    ]
    for b in sel["backup_tools"]:
        L.append(f"- {b}")
    L.append("")
    L.append(f"**Preparation:** {sel['preparation']}")
    L.append("")
    L.append(f"*Tool selection computed deterministically for {op}; "
             "final tool selection must be confirmed with the fishing "
             "service company and the operator's procedures.*")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _selftest():
    # fully stuck -> back-off/fishing path
    s1 = stuck_pipe_diagnosis(False, False, False)
    assert "FREE POINT" in s1[0]["actions"][2].upper() or \
        "Free Point" in s1[0]["actions"][2]
    assert "Fishing" in s1[0]["escalate"]
    # differential signature
    s2 = stuck_pipe_diagnosis(False, True, False)
    assert "DIFFERENTIAL" in s2[0]["interpretation"].upper()
    assert "do not overpull" in s2[0]["actions"][0].lower() or \
        "DO NOT overpull" in s2[0]["actions"][0]
    # key seat / ream path
    s3 = stuck_pipe_diagnosis(True, True, False)
    assert "undergauge" in s3[0]["interpretation"].lower() or \
        "restriction" in s3[0]["interpretation"].lower()
    # not stuck
    s4 = stuck_pipe_diagnosis(True, True, True)
    assert "no sticking indication" in s4[0]["interpretation"].lower()
    # fishing selection
    f1 = fishing_tool_selection(fish_desc="Drill pipe fish in hole",
                                fish_od_in=5.0, fish_top_ft=8000)
    assert f1["fish_type"] == "pipe"
    assert "overshot" in f1["primary_tool"].lower()
    f2 = fishing_tool_selection(fish_desc="Junk and debris on top of fish")
    assert f2["fish_type"] == "junk"
    assert "basket" in f2["primary_tool"].lower()
    f3 = fishing_tool_selection(fish_desc="Wireline stuck in hole")
    assert f3["fish_type"] == "wireline"
    assert "rope spear" in f3["primary_tool"].lower() or \
        "spear" in f3["primary_tool"].lower()
    print("  ✔ decision-tree selftest: stuck-pipe + fishing OK")
    return s1


if __name__ == "__main__":
    _selftest()
    print("engineering_decisions OK")
