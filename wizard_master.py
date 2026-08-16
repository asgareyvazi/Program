# ============================================================================
# MASTER PROCEDURE WIZARD TEMPLATES
# File: wizard_master.py
# Turns the consolidated master procedures (one per operation, merged from
# all library documents) into wizard templates so the user fills in the
# parameters (hole size, depth, mud weight, casing...) and gets a precise,
# field-proven procedure as a Word document.
# ============================================================================

from wizard_engine import TemplateDef, InputSpec
from master_procedures import MasterDatabase, build_master_markdown

_ICONS = {
    "Cementing": "🏗️", "Completion": "🔩", "Workover": "🛠️",
    "Mud-Fluids": "🧪", "Drilling": "🛢️", "Sidetrack": "↩️",
    "Casing-Liner": "🧱", "Re-Entry": "🔄", "Fishing": "🎣",
    "Well Testing": "📊", "Well Control": "🚨", "BOP": "🔴",
    "Stimulation": "⚗️", "Coring": "🧊", "Logging": "📈",
}

_COMMON_INPUTS = [
    InputSpec("well_name", "Well Name", "text", placeholder="e.g. WELL-101", group="1. General"),
    InputSpec("field_name", "Field", "text", placeholder="e.g. Field", group="1. General"),
    InputSpec("operator", "Operator", "text", group="1. General"),
    InputSpec("contractor", "Contractor", "text", group="1. General"),
    InputSpec("rig_name", "Rig", "text", group="1. General"),
    InputSpec("environment", "Environment", "combo",
              options=["Onshore", "Offshore Jack-up", "Semi-submersible",
                       "Fixed Platform", "Caspian Sea"], group="1. General"),
    InputSpec("well_type", "Well Type", "combo",
              options=["Vertical", "Deviated", "Horizontal", "ERD", "HPHT",
                       "Deepwater"], group="1. General"),
]

_OP_INPUTS = {
    "Cementing": [
        InputSpec("hole_size", "Hole Size", "text", placeholder='e.g. 12-1/4"', group="2. Job Parameters"),
        InputSpec("casing_size", "Casing/Liner Size", "text", placeholder='e.g. 9-5/8"', group="2. Job Parameters"),
        InputSpec("depth_m", "Depth (m)", "number", unit="m", group="2. Job Parameters"),
        InputSpec("mud_weight", "Mud Weight", "number", unit="pcf", group="2. Job Parameters"),
        InputSpec("mud_type", "Mud Type", "text", group="2. Job Parameters"),
    ],
    "Casing-Liner": [
        InputSpec("hole_size", "Hole Size", "text", placeholder='e.g. 12-1/4"', group="2. Job Parameters"),
        InputSpec("casing_size", "Casing Size", "text", placeholder='e.g. 9-5/8"', group="2. Job Parameters"),
        InputSpec("depth_m", "Depth (m)", "number", unit="m", group="2. Job Parameters"),
        InputSpec("mud_weight", "Mud Weight", "number", unit="pcf", group="2. Job Parameters"),
    ],
    "Well Control": [
        InputSpec("mud_weight", "Mud Weight", "number", unit="pcf", group="2. Job Parameters"),
        InputSpec("mud_type", "Mud Type", "text", group="2. Job Parameters"),
        InputSpec("depth_m", "Depth (m)", "number", unit="m", group="2. Job Parameters"),
        InputSpec("bop_wp", "BOP Rating", "number", unit="psi", group="2. Job Parameters"),
    ],
    "BOP": [
        InputSpec("bop_wp", "BOP Rating", "number", unit="psi", group="2. Job Parameters"),
        InputSpec("depth_m", "Depth (m)", "number", unit="m", group="2. Job Parameters"),
    ],
    "Fishing": [
        InputSpec("hole_size", "Hole Size", "text", group="2. Job Parameters"),
        InputSpec("depth_m", "Depth (m)", "number", unit="m", group="2. Job Parameters"),
    ],
    "Sidetrack": [
        InputSpec("hole_size", "Hole Size", "text", group="2. Job Parameters"),
        InputSpec("depth_m", "Depth (m)", "number", unit="m", group="2. Job Parameters"),
        InputSpec("mud_weight", "Mud Weight", "number", unit="pcf", group="2. Job Parameters"),
    ],
    "Re-Entry": [
        InputSpec("hole_size", "Hole Size", "text", group="2. Job Parameters"),
        InputSpec("depth_m", "Depth (m)", "number", unit="m", group="2. Job Parameters"),
        InputSpec("mud_weight", "Mud Weight", "number", unit="pcf", group="2. Job Parameters"),
    ],
    "Workover": [
        InputSpec("hole_size", "Hole Size", "text", group="2. Job Parameters"),
        InputSpec("depth_m", "Depth (m)", "number", unit="m", group="2. Job Parameters"),
        InputSpec("mud_weight", "Mud Weight", "number", unit="pcf", group="2. Job Parameters"),
        InputSpec("mud_type", "Mud Type", "text", group="2. Job Parameters"),
    ],
    "Completion": [
        InputSpec("hole_size", "Hole Size", "text", group="2. Job Parameters"),
        InputSpec("casing_size", "Casing Size", "text", group="2. Job Parameters"),
        InputSpec("depth_m", "Depth (m)", "number", unit="m", group="2. Job Parameters"),
    ],
    "Mud-Fluids": [
        InputSpec("mud_weight", "Mud Weight", "number", unit="pcf", group="2. Job Parameters"),
        InputSpec("mud_type", "Mud Type", "text", group="2. Job Parameters"),
        InputSpec("depth_m", "Depth (m)", "number", unit="m", group="2. Job Parameters"),
    ],
    "Well Testing": [
        InputSpec("depth_m", "Depth (m)", "number", unit="m", group="2. Job Parameters"),
        InputSpec("bop_wp", "BOP Rating", "number", unit="psi", group="2. Job Parameters"),
    ],
    "Drilling": [
        InputSpec("hole_size", "Hole Size", "text", group="2. Job Parameters"),
        InputSpec("depth_m", "Depth (m)", "number", unit="m", group="2. Job Parameters"),
        InputSpec("mud_weight", "Mud Weight", "number", unit="pcf", group="2. Job Parameters"),
        InputSpec("mud_type", "Mud Type", "text", group="2. Job Parameters"),
        InputSpec("casing_size", "Casing Size", "text", group="2. Job Parameters"),
    ],
}


def build_master_templates() -> list:
    """Build TemplateDef objects from the master procedures database."""
    db = MasterDatabase()
    templates = []
    try:
        for row in db.all():
            op = row["operation"]
            mp = db.get(op)
            if not mp or not mp["steps"]:
                continue
            inputs = list(_COMMON_INPUTS) + list(_OP_INPUTS.get(op, []))
            inputs.append(InputSpec("doc_date", "Date", "text",
                                    group="3. Document"))
            inputs.append(InputSpec("revision", "Revision", "text",
                                    default="01", group="3. Document"))
            key = f"master_{op.lower().replace(' ', '_').replace('/', '_')}"
            templates.append(TemplateDef(
                key=key,
                name=f"Master Procedure — {op}",
                icon=_ICONS.get(op, "📋"),
                kind="Procedure",
                description=(
                    f"Consolidated {op.lower()} procedure merged from "
                    f"{mp['docs_used']} reference documents — fill the "
                    f"parameters for a precise, field-proven output."),
                inputs=inputs,
                markdown=build_master_markdown(mp, {}),
                meta={"master_operation": op},
            ))
    finally:
        db.close()
    return templates
