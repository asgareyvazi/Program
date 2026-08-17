# ============================================================================
# BACKUP / RESTORE + SECRETS MANAGEMENT
# File: backup_restore.py
# Audit items (P2):
#   - Backup/restore & disaster recovery for all SQLite DBs + settings
#   - Encryption at rest: password-protected backups (Fernet + PBKDF2-SHA256)
#   - Secrets management: API keys should NOT sit in a plain JSON file;
#     this module offers OS-keyring storage when available and warns
#     otherwise.
# ============================================================================

import base64
import io
import json
import os
import shutil
import sqlite3
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

APP_DIR = Path.home() / ".drilling_program"
BACKUP_DIR = APP_DIR / "backups"

# DBs to back up (all app data)
DB_NAMES = ["procedures.db", "cbs.db", "problems.db", "catalog.db",
            "wells.db", "time_breakdown.db", "master_procedures.db",
            "operations.db"]
# JSON settings to back up
SETTINGS_FILES = ["llm_settings.json", "users.json"]

ENC_MAGIC = b"DRL1"      # encrypted backup header
_SALT_SIZE = 16


def _derive_key(password: str, salt: bytes) -> bytes:
    """PBKDF2-HMAC-SHA256 key derivation (200k iterations)."""
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32,
                     salt=salt, iterations=200_000)
    return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))


# ---------------------------------------------------------------------------
# BACKUP / RESTORE
# ---------------------------------------------------------------------------

def _safe_copy(src: Path, dst: Path) -> bool:
    try:
        # SQLite safe copy: use backup API when possible
        if src.suffix == ".db":
            con = sqlite3.connect(str(src))
            bck = sqlite3.connect(str(dst))
            con.backup(bck)
            bck.close()
            con.close()
        else:
            shutil.copy2(src, dst)
        return True
    except Exception:
        try:
            shutil.copy2(src, dst)
            return True
        except Exception:
            return False


def create_backup(tag: str = "", password: Optional[str] = None) -> Optional[Path]:
    """Snapshot all DBs + settings into a timestamped backup folder.

    When a password is given, the whole backup is encrypted at rest into a
    single .enc archive (Fernet + PBKDF2-SHA256, 200k iterations) and the
    plain folder is removed.
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"backup_{ts}" + (f"_{tag}" if tag else "")
    target = BACKUP_DIR / name
    target.mkdir(parents=True, exist_ok=True)
    saved = 0
    manifest = {}
    for fname in DB_NAMES:
        src = APP_DIR / fname
        if src.exists():
            if _safe_copy(src, target / fname):
                manifest[fname] = src.stat().st_size
                saved += 1
    for fname in SETTINGS_FILES:
        src = APP_DIR / fname
        if src.exists():
            if _safe_copy(src, target / fname):
                manifest[fname] = src.stat().st_size
                saved += 1
    if saved == 0:
        return None
    (target / "manifest.json").write_text(
        json.dumps({"created": ts, "files": manifest}, indent=1),
        encoding="utf-8")
    if password:
        return _encrypt_backup_folder(target, password)
    return target


# ---------------------------------------------------------------------------
# ENCRYPTION AT REST
# ---------------------------------------------------------------------------

def _encrypt_backup_folder(folder: Path, password: str) -> Path:
    """Zip the backup folder and encrypt it (Fernet). Removes the plain
    folder. Returns the .enc path."""
    from cryptography.fernet import Fernet
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(folder.iterdir()):
            if f.is_file():
                z.write(f, f.name)
    salt = os.urandom(_SALT_SIZE)
    key = _derive_key(password, salt)
    token = Fernet(key).encrypt(buf.getvalue())
    out = folder.with_name(folder.name + ".enc")
    out.write_bytes(ENC_MAGIC + salt + token)
    shutil.rmtree(folder)
    return out


def _decrypt_backup(payload: bytes, password: str) -> bytes:
    from cryptography.fernet import Fernet, InvalidToken
    if not payload.startswith(ENC_MAGIC):
        raise ValueError("not an encrypted backup (missing header)")
    salt = payload[len(ENC_MAGIC):len(ENC_MAGIC) + _SALT_SIZE]
    token = payload[len(ENC_MAGIC) + _SALT_SIZE:]
    key = _derive_key(password, salt)
    try:
        return Fernet(key).decrypt(token)
    except InvalidToken:
        raise ValueError("wrong password or corrupted backup")


def _restore_encrypted(backup_name: str, password: str) -> Dict:
    enc_path = BACKUP_DIR / backup_name
    if not enc_path.exists():
        return {"error": f"backup not found: {backup_name}"}
    try:
        payload = _decrypt_backup(enc_path.read_bytes(), password)
    except ValueError as e:
        return {"error": str(e)}
    tmp = BACKUP_DIR / ("_restore_" + backup_name.rstrip(".enc"))
    tmp.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as z:
            z.extractall(tmp)
        results = {}
        for fname in DB_NAMES + SETTINGS_FILES:
            f = tmp / fname
            if f.exists() and f.is_file():
                results[fname] = _safe_copy(f, APP_DIR / fname)
        if not results:
            return {"error": "backup contains no recognizable files"}
        return results
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def list_backups() -> List[Dict]:
    if not BACKUP_DIR.exists():
        return []
    out = []
    for d in sorted(BACKUP_DIR.iterdir()):
        if d.is_dir():
            man = {}
            mf = d / "manifest.json"
            if mf.exists():
                try:
                    man = json.loads(mf.read_text(encoding="utf-8"))
                except Exception:
                    man = {}
            out.append({
                "name": d.name,
                "created": man.get("created", d.name),
                "files": list(man.get("files", {}).keys()),
                "count": len(man.get("files", {})),
                "encrypted": False,
            })
        elif d.suffix == ".enc":
            created = d.name.replace("backup_", "").replace(".enc", "")
            out.append({
                "name": d.name,
                "created": created[:15],
                "files": ["encrypted archive"],
                "count": "🔒",
                "encrypted": True,
            })
    return out


def restore_backup(backup_name: str,
                   password: Optional[str] = None) -> Dict:
    """Restore a backup by name. Returns per-file results.

    For encrypted (.enc) backups the password is required.
    """
    if backup_name.endswith(".enc"):
        if not password:
            return {"error": "encrypted backup requires a password"}
        return _restore_encrypted(backup_name, password)
    src = BACKUP_DIR / backup_name
    if not src.is_dir():
        return {"error": f"backup not found: {backup_name}"}
    results = {}
    for fname in DB_NAMES + SETTINGS_FILES:
        f = src / fname
        if f.exists():
            # close any open handles: we can't force-close app DBs, but
            # sqlite handles concurrent restore of copies fine on next open
            results[fname] = _safe_copy(f, APP_DIR / fname)
    return results


# ---------------------------------------------------------------------------
# SECRETS MANAGEMENT
# ---------------------------------------------------------------------------

class SecretsManager:
    """Store API keys securely.

    Uses the OS keyring (Windows Credential Manager / macOS Keychain /
    Linux Secret Service) when `keyring` is installed. Falls back to a
    file with restrictive permissions (0600) and a warning.
    """

    def __init__(self, service: str = "DrillingProgram"):
        self.service = service
        self._keyring = None
        try:
            import keyring
            self._keyring = keyring
        except ImportError:
            self._keyring = None
        self._fallback_file = APP_DIR / ".secrets.json"

    def set_secret(self, key: str, value: str) -> str:
        """Store a secret; returns the storage method used."""
        if self._keyring is not None:
            try:
                self._keyring.set_password(self.service, key, value)
                return "keyring"
            except Exception:
                pass
        # fallback: file with 0600 perms
        try:
            APP_DIR.mkdir(exist_ok=True)
            data = {}
            if self._fallback_file.exists():
                data = json.loads(
                    self._fallback_file.read_text(encoding="utf-8"))
            data[key] = value
            self._fallback_file.write_text(
                json.dumps(data), encoding="utf-8")
            try:
                self._fallback_file.chmod(0o600)
            except Exception:
                pass
            return "file"
        except Exception:
            return "error"

    def get_secret(self, key: str) -> str:
        if self._keyring is not None:
            try:
                v = self._keyring.get_password(self.service, key)
                if v:
                    return v
            except Exception:
                pass
        try:
            if self._fallback_file.exists():
                data = json.loads(
                    self._fallback_file.read_text(encoding="utf-8"))
                return data.get(key, "")
        except Exception:
            pass
        return ""

    def delete_secret(self, key: str) -> bool:
        if self._keyring is not None:
            try:
                self._keyring.delete_password(self.service, key)
                return True
            except Exception:
                pass
        try:
            if self._fallback_file.exists():
                data = json.loads(
                    self._fallback_file.read_text(encoding="utf-8"))
                data.pop(key, None)
                self._fallback_file.write_text(
                    json.dumps(data), encoding="utf-8")
                return True
        except Exception:
            pass
        return False

    def storage_method(self) -> str:
        return "keyring" if self._keyring is not None else "file (0600)"


def migrate_llm_key_to_secrets() -> str:
    """Move the LLM API key from llm_settings.json into the secrets store."""
    sm = SecretsManager()
    settings = APP_DIR / "llm_settings.json"
    if not settings.exists():
        return "no settings file"
    try:
        data = json.loads(settings.read_text(encoding="utf-8"))
    except Exception:
        return "unreadable settings"
    key = data.get("api_key", "")
    backend = data.get("backend", "none")
    if not key or backend in ("none", "Ollama"):
        return "no cloud key to migrate"
    method = sm.set_secret(f"{backend.lower()}_api_key", key)
    # remove the key from the plaintext file (keep backend only)
    data["api_key"] = ""
    settings.write_text(json.dumps(data, indent=1), encoding="utf-8")
    return f"migrated to {method}"


def load_llm_key(backend: str) -> str:
    """Read the LLM key from the secrets store (fallback: settings file)."""
    sm = SecretsManager()
    v = sm.get_secret(f"{backend.lower()}_api_key")
    if v:
        return v
    # legacy fallback
    try:
        settings = APP_DIR / "llm_settings.json"
        if settings.exists():
            data = json.loads(settings.read_text(encoding="utf-8"))
            return data.get("api_key", "")
    except Exception:
        pass
    return ""


if __name__ == "__main__":
    # backup demo
    b = create_backup("test")
    print("backup:", b.name if b else None, "| total backups:", len(list_backups()))
    # secrets demo
    sm = SecretsManager()
    sm.set_secret("demo_key", "super-secret-value")
    print("storage method:", sm.storage_method())
    print("roundtrip:", sm.get_secret("demo_key") == "super-secret-value")
    sm.delete_secret("demo_key")
    print("deleted:", sm.get_secret("demo_key") == "")
