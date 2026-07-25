#!/usr/bin/env python3
"""Check a SQLite database for foreign key violations.

Usage: python scripts/check_orphans.py <path-to-database>
"""
import sqlite3
import sys


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <database-path>", file=sys.stderr)
        sys.exit(1)

    db_path = sys.argv[1]
    con = sqlite3.connect(db_path)
    try:
        con.execute("PRAGMA foreign_keys=ON")
        rows = con.execute("PRAGMA foreign_key_check").fetchall()
        for table, rowid, parent, _fkid in rows:
            print(f"ORPHAN  {table}  rowid={rowid}  -> missing parent in {parent}")
        print(f"\n{len(rows)} violation(s)")
    finally:
        con.close()


if __name__ == "__main__":
    main()
