# ============================================================================
# BACKUP / RESTORE CLI
# File: backup_cli.py
# Audit item (P2): disaster recovery from the command line.
#
# Usage:
#   python3 backup_cli.py create [--tag NAME] [--password ...]
#   python3 backup_cli.py list
#   python3 backup_cli.py restore <backup_name> [--password ...]
# ============================================================================

import argparse
import getpass
import sys
from pathlib import Path

from backup_restore import (BACKUP_DIR, create_backup, list_backups,
                            restore_backup)


def _password(args) -> str:
    if args.password:
        return args.password
    return getpass.getpass("Backup password: ")


def main():
    ap = argparse.ArgumentParser(prog="backup_cli",
                                 description="Drilling Program backup/restore")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_create = sub.add_parser("create", help="create a backup")
    p_create.add_argument("--tag", default="", help="optional tag")
    p_create.add_argument("--password", default=None,
                          help="password -> encrypted backup (use \"\" for "
                               "a plain, unencrypted backup)")
    p_create.add_argument("--encrypt", action="store_true",
                          help="prompt for a password and encrypt")

    sub.add_parser("list", help="list backups")

    p_restore = sub.add_parser("restore", help="restore a backup")
    p_restore.add_argument("backup_name")
    p_restore.add_argument("--password", default=None,
                           help="password for encrypted backups")

    args = ap.parse_args()

    if args.cmd == "create":
        if args.encrypt:
            pwd = _password(args)
        elif args.password in (None, ""):
            pwd = None            # plain backup
        else:
            pwd = args.password   # encrypted backup
        b = create_backup(tag=args.tag, password=pwd)
        if b:
            print(f"✅ Backup created: {b.name}"
                  + (" (encrypted 🔒)" if b.suffix == ".enc" else ""))
        else:
            print("❌ No data found to back up.")
            return 1
        return 0

    if args.cmd == "list":
        bs = list_backups()
        if not bs:
            print("No backups yet.")
            return 0
        for b in bs:
            mark = "🔒 encrypted" if b.get("encrypted") else \
                f"{b['count']} file(s)"
            print(f"  {b['name']}  ({b['created']}, {mark})")
        return 0

    if args.cmd == "restore":
        name = args.backup_name
        if name.endswith(".enc"):
            pwd = args.password if args.password is not None else \
                getpass.getpass("Backup password: ")
            if not pwd:
                print("❌ Password required for encrypted backup.")
                return 1
        else:
            pwd = None
        res = restore_backup(name, password=pwd)
        if "error" in res:
            print(f"❌ {res['error']}")
            return 1
        ok = sum(1 for v in res.values() if v)
        print(f"✅ Restored {ok}/{len(res)} files from {name}")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
