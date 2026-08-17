# ============================================================================
# ENGINEERING DEPENDENCY GRAPH
# File: engineering_dependency.py
# P0 audit item: when an input changes, the software must know which other
# modules/artifacts are affected. This central registry replaces the
# string-matching / implicit orchestration between modules.
#
# Each entry: input key -> list of (affected module, impact, note)
# Modules: hydrostatic, ecd, maasp, kick_tolerance, casing_burst,
#          casing_collapse, casing_tension, cement, hydraulics, torque_drag,
#          bha, bit, mud, well_control, directional, hole_cleaning,
#          surge_swab, time, cost, risk, document, procedure
# ============================================================================

from typing import Dict, List, Tuple

Dependency = Tuple[str, str, str]  # (module, impact, note)

DEPENDENCY_GRAPH: Dict[str, List[Dependency]] = {
    "mud_weight": [
        ("hydrostatic", "direct", "P = 0.052 × MW × depth"),
        ("ecd", "direct", "ECD = MW + annular losses"),
        ("maasp", "direct", "MAASP = (FG − MW) × 0.052 × shoe"),
        ("kick_tolerance", "direct", "higher MW lowers kick tolerance"),
        ("casing_burst", "direct", "surface pressure depends on MW"),
        ("well_control", "direct", "KMW and shut-in decisions"),
        ("risk", "indirect", "overbalance / lost circulation risk"),
        ("time", "indirect", "mud conditioning & treatment time"),
        ("cost", "indirect", "mud materials cost"),
    ],
    "mud_type": [
        ("mud", "direct", "system selection (WBM/OBM/SBM)"),
        ("hole_cleaning", "indirect", "rheology & inhibition"),
        ("risk", "indirect", "shale stability, HSE"),
        ("cost", "direct", "mud system cost per bbl"),
    ],
    "hole_size": [
        ("hydraulics", "direct", "annular velocity & pressure loss"),
        ("ecd", "direct", "annular geometry"),
        ("torque_drag", "direct", "annular friction & clearance"),
        ("cement", "direct", "slurry volume & displacement"),
        ("bha", "direct", "BHA size compatibility"),
        ("bit", "direct", "bit size"),
        ("mud", "direct", "hole volume"),
        ("hole_cleaning", "direct", "cuttings transport"),
        ("surge_swab", "direct", "geometry"),
        ("time", "direct", "drilling & tripping time"),
        ("cost", "direct", "drilling cost"),
    ],
    "casing_size": [
        ("cement", "direct", "annular volume"),
        ("hydraulics", "indirect", "restriction"),
        ("bha", "direct", "BHA pass-through"),
        ("well_control", "direct", "BOP/wellhead interface"),
        ("time", "direct", "casing running time"),
        ("cost", "direct", "casing cost"),
        ("document", "direct", "architecture schematic"),
    ],
    "casing_depth": [
        ("casing_burst", "direct", "load cases"),
        ("casing_collapse", "direct", "load cases"),
        ("casing_tension", "direct", "string weight"),
        ("cement", "direct", "cement volume & top"),
        ("well_control", "direct", "shoe strength / MAASP"),
        ("time", "direct", "drilling time to shoe"),
        ("cost", "direct", "casing & cement cost"),
    ],
    "casing_grade": [
        ("casing_burst", "direct", "yield strength"),
        ("casing_collapse", "direct", "collapse rating"),
        ("casing_tension", "direct", "body yield"),
        ("cost", "direct", "premium for grade"),
    ],
    "formation_pressure": [
        ("mud", "direct", "mud window lower bound"),
        ("casing_burst", "indirect", "gas load cases"),
        ("well_control", "direct", "kick tolerance & KMW"),
        ("risk", "direct", "kick risk"),
    ],
    "fracture_gradient": [
        ("mud", "direct", "mud window upper bound"),
        ("maasp", "direct", "MAASP at shoe"),
        ("casing_depth", "indirect", "shoe placement"),
        ("risk", "direct", "loss risk"),
    ],
    "td_depth": [
        ("casing_depth", "indirect", "section design"),
        ("cement", "indirect", "volumes"),
        ("time", "direct", "duration"),
        ("cost", "direct", "total cost"),
        ("document", "indirect", "well data"),
    ],
    "bop_wp": [
        ("well_control", "direct", "pressure containment"),
        ("casing_burst", "indirect", "surface pressure rating"),
        ("risk", "direct", "blowout risk"),
        ("cost", "direct", "BOP rental"),
    ],
    "rig_type": [
        ("time", "direct", "trip speed, mob/demob"),
        ("cost", "direct", "day rate"),
        ("document", "direct", "rig data"),
    ],
    "directional_profile": [
        ("torque_drag", "direct", "friction & side force"),
        ("bha", "direct", "motor/RSS selection"),
        ("hole_cleaning", "direct", "cuttings bed in high angle"),
        ("anti_collision", "direct", "separation"),
        ("surge_swab", "indirect", "trip envelope"),
    ],
    "npt_event": [
        ("time", "direct", "adds NPT days"),
        ("cost", "direct", "adds NPT cost"),
        ("lessons_learned", "direct", "records for offsets"),
        ("risk", "indirect", "recurrence risk"),
    ],
    "h2s": [
        ("risk", "direct", "H2S contingency"),
        ("procedure", "direct", "H2S procedure required"),
        ("cost", "direct", "H2S equipment"),
    ],
}

# reverse index: module -> inputs that affect it
_MODULE_INPUTS: Dict[str, List[str]] = {}
for _inp, deps in DEPENDENCY_GRAPH.items():
    for mod, _, _ in deps:
        _MODULE_INPUTS.setdefault(mod, []).append(_inp)


def affected_modules(changed_inputs: List[str]) -> Dict[str, List[str]]:
    """Return {module: [input keys]} affected by the given changed inputs."""
    out: Dict[str, List[str]] = {}
    for inp in changed_inputs:
        for mod, impact, note in DEPENDENCY_GRAPH.get(inp, []):
            out.setdefault(mod, []).append(f"{inp} ({impact})")
    return out


def inputs_affecting(module: str) -> List[str]:
    """All inputs that feed a module (reverse lookup)."""
    return _MODULE_INPUTS.get(module, [])


def dependency_markdown(changed_inputs: List[str]) -> str:
    """Human-readable 'affected modules' section for the document."""
    if not changed_inputs:
        return ""
    affected = affected_modules(changed_inputs)
    if not affected:
        return ""
    L = ["## ENGINEERING DEPENDENCY IMPACT", "",
         "The following modules are affected by the current inputs:"]
    for mod, inputs in sorted(affected.items()):
        L.append(f"- **{mod.replace('_', ' ').title()}** ← " + ", ".join(inputs))
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    print(affected_modules(["mud_weight", "casing_depth"]))
