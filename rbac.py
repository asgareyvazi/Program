# ============================================================================
# RBAC — role-based access control (audit P2, lightweight desktop version)
# File: rbac.py
# Roles: Engineer / Reviewer / Approver / Admin / Read-Only.
# Every guarded action is checked here and recorded in the audit log.
# ============================================================================

import json
from pathlib import Path

from audit_log import log_action

APP_DIR = Path.home() / ".drilling_program"
USERS_FILE = APP_DIR / "users.json"

ROLES = ["Read-Only", "Engineer", "Reviewer", "Approver", "Admin"]

# action -> minimum role index (0=Read-Only .. 4=Admin)
ACTION_LEVEL = {
    "view": 0,
    "create_well": 1,
    "edit_well": 1,
    "generate_document": 1,
    "import_knowledge": 2,
    "review_procedure": 2,
    "edit_procedure": 1,
    "approve_procedure": 3,
    "release_procedure": 3,
    "override_critical": 3,
    "manage_users": 4,
    "delete": 4,
}

_LEVEL = {r: i for i, r in enumerate(ROLES)}


def _load_users() -> dict:
    if USERS_FILE.exists():
        try:
            return json.loads(USERS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_users(users: dict):
    USERS_FILE.parent.mkdir(exist_ok=True)
    USERS_FILE.write_text(json.dumps(users, indent=1), encoding="utf-8")


def default_users() -> dict:
    """Bootstrap: single admin so the app is usable out of the box."""
    return {"admin": {"role": "Admin", "display": "Administrator"}}


def current_user() -> str:
    """Return the logged-in user name (desktop: first user or admin)."""
    users = _load_users() or default_users()
    return next(iter(users), "admin")


def role_of(user: str) -> str:
    users = _load_users() or default_users()
    return users.get(user, {}).get("role", "Read-Only")


def can(user: str, action: str) -> bool:
    """Check whether a user may perform an action."""
    return _LEVEL.get(role_of(user), 0) >= ACTION_LEVEL.get(action, 1)


def require(user: str, action: str) -> bool:
    """Check + audit. Returns True if allowed."""
    allowed = can(user, action)
    if not allowed:
        log_action("access_denied", user, action,
                   f"requires role >= {ROLES[ACTION_LEVEL.get(action, 1)]}",
                   "HIGH")
    return allowed


def add_user(user: str, role: str, display: str = "", actor: str = "admin"):
    if not require(actor, "manage_users"):
        return False
    if role not in ROLES:
        return False
    users = _load_users() or default_users()
    users[user] = {"role": role, "display": display or user}
    _save_users(users)
    log_action("user_added", actor, user, f"role={role}", "HIGH")
    return True


def list_users() -> dict:
    return _load_users() or default_users()


if __name__ == "__main__":
    print("users:", list_users())
    print("admin can approve:", can("admin", "approve_procedure"))
    print("admin can override critical:", can("admin", "override_critical"))
    print("read-only can approve:", can("viewer", "approve_procedure"))
    # bootstrap an engineer for demo
    add_user("eng1", "Engineer", "Engineer One")
    print("eng1 can edit well:", can("eng1", "edit_well"))
    print("eng1 can approve:", can("eng1", "approve_procedure"))
