#!/usr/bin/env python3
"""Query a SQLite database of users.

    python3 users.py tables                 see all tables and columns (start here!)
    python3 users.py list                   all users
    python3 users.py get 3 --json           one user, as JSON
    python3 users.py search som             search username / full name / email
    python3 users.py sql "SELECT city, COUNT(*) AS n FROM users GROUP BY city"
    python3 users.py --db exam.db list      use another database file

Standard library only: the sqlite3 module is built into Python.
EXAM: change USER_COLUMNS and the queries to match the real table.
"""

import argparse
import json
import os
import sqlite3
import sys

# Columns of the users table. EXAM: change them (see "python3 users.py tables").
USER_COLUMNS = [
    "id",
    "username",
    "full_name",
    "email",
    "phone",
    "age",
    "city",
    "status",
    "created_at",
]
SELECT_USERS = "SELECT " + ", ".join(USER_COLUMNS) + " FROM users"

COMMANDS = """commands:
  tables          show all tables, their columns and row counts (start here!)
  list            list all users
  get ID          show one user
  search TEXT     users whose username, full name or email contains TEXT
  status STATUS   users with this status (active, inactive, blocked)
  stats           COUNT, AVG, GROUP BY and JOIN examples
  sql "QUERY"     run any SQL, e.g. sql "SELECT * FROM users WHERE age > 40"
  add JSON|FILE   insert a user, e.g. add '{"username":"bob","full_name":"Bob","email":"bob@mail.com"}'
  load FILE.sql   run a .sql script (create tables, insert data)
"""

STATS_QUERIES = [
    (
        "Users by status",
        """
        SELECT status, COUNT(*) AS users FROM users
        GROUP BY status ORDER BY users DESC""",
    ),
    (
        "Users by city",
        """
        SELECT COALESCE(city, '-') AS city, COUNT(*) AS users, ROUND(AVG(age), 1) AS avg_age
        FROM users GROUP BY city ORDER BY users DESC, city""",
    ),
    (
        "Top 5 users by LAK balance (JOIN users + accounts)",
        """
        SELECT u.id, u.full_name, COUNT(a.id) AS accounts, SUM(a.balance) AS total_lak
        FROM users u JOIN accounts a ON a.user_id = u.id
        WHERE a.currency = 'LAK'
        GROUP BY u.id, u.full_name ORDER BY total_lak DESC LIMIT 5""",
    ),
]


def main():
    parser = argparse.ArgumentParser(
        description="Query a SQLite database of users.",
        epilog=COMMANDS,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "command",
        metavar="COMMAND",
        choices=[
            "tables",
            "list",
            "get",
            "search",
            "status",
            "stats",
            "sql",
            "add",
            "load",
        ],
    )
    parser.add_argument("arg", nargs="*", help="ID, TEXT, STATUS, QUERY, JSON or FILE")
    parser.add_argument(
        "--db",
        default="data/users.db",
        help="SQLite database file (default: data/users.db)",
    )
    parser.add_argument("--json", action="store_true", help="print users as JSON")
    args = parser.parse_intermixed_args()  # flags may come anywhere: get 3 --json
    text = " ".join(args.arg)

    # sqlite3.connect() silently CREATES a new empty database when the path is
    # wrong, which gives confusing "no such table" errors. So check first.
    if args.command == "load":
        if not os.path.exists(need(text, "FILE")):
            fail(f"file {text!r} not found")
    elif not os.path.exists(args.db):
        fail(f"database file {args.db!r} not found (use --db FILE)")

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row  # rows work like dicts: row["email"]
    try:
        if args.command == "tables":
            show_tables(conn)
        elif args.command == "list":
            show_users(query_users(conn, "ORDER BY id"), args.json)
        elif args.command == "get":
            get_user(conn, need(text, "ID"), args.json)
        elif args.command == "search":
            like = "%" + need(text, "TEXT") + "%"
            users = query_users(
                conn,
                "WHERE username LIKE ? OR full_name LIKE ? OR email LIKE ? ORDER BY id",
                (like, like, like),
            )
            show_users(users, args.json)
        elif args.command == "status":
            show_users(
                query_users(
                    conn, "WHERE status = ? ORDER BY id", (need(text, "STATUS"),)
                ),
                args.json,
            )
        elif args.command == "stats":
            show_stats(conn)
        elif args.command == "sql":
            run_sql(conn, need(text, "QUERY"))
        elif args.command == "add":
            add_user(conn, need(text, "JSON or FILE"))
        elif args.command == "load":
            load_file(conn, text)
    except (sqlite3.Error, OSError) as e:
        fail(e)
    finally:
        conn.close()


def query_users(conn, where="", params=()):
    """Return the users that match `where` (it can also hold ORDER BY / LIMIT) as dicts.

    Values always go in params with ? placeholders. Never put user input into
    the SQL text with + or f-strings (that is SQL injection).
    """
    rows = conn.execute(SELECT_USERS + " " + where, params).fetchall()
    return [dict(row) for row in rows]


def get_user(conn, id_text, as_json):
    """Print one user. fetchone() gives None when nothing matches."""
    try:
        user_id = int(id_text)
    except ValueError:
        fail(f"ID must be a number, got {id_text!r}")
    row = conn.execute(
        SELECT_USERS + " WHERE id = ?", (user_id,)
    ).fetchone()  # (x,) = a tuple with 1 item
    if row is None:
        fail(f"user with id {user_id} not found")
    if as_json:
        print(json.dumps(dict(row), indent=2, ensure_ascii=False))
    else:
        show_users([dict(row)], False)


def show_users(users, as_json):
    """Print users as a table, or as JSON with --json."""
    if as_json:
        print(
            json.dumps(users, indent=2, ensure_ascii=False)
        )  # ensure_ascii=False keeps Lao letters
    else:
        print_table(
            USER_COLUMNS, [[user[col] for col in USER_COLUMNS] for user in users]
        )


def show_tables(conn):
    """Print every table with its CREATE statement and row count.
    Run this first in the exam to learn an unknown database."""
    tables = conn.execute("""SELECT name, sql FROM sqlite_master
        WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name""").fetchall()
    for name, create_sql in tables:
        count = conn.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
        print(f"-- table {name}: {count} rows\n{create_sql};\n")


def show_stats(conn):
    """Aggregate queries: COUNT, AVG, GROUP BY and a JOIN."""
    total, avg_age = conn.execute("SELECT COUNT(*), AVG(age) FROM users").fetchone()
    print(
        f"Total users: {total}, average age: {avg_age or 0:.1f}"
    )  # AVG gives None (NULL) when there are no rows
    for title, sql in STATS_QUERIES:
        print(f"\n{title}:")
        print_query(conn, sql)


def run_sql(conn, query):
    """Run any SQL typed on the command line. SELECT-like queries print a
    table; other statements (INSERT, UPDATE, DELETE ...) print the rows changed."""
    words = query.split()
    if not words:
        fail("empty query")
    if words[0].upper() in ("SELECT", "WITH", "PRAGMA", "EXPLAIN", "VALUES"):
        print_query(conn, query)
    else:
        cur = conn.execute(query)
        conn.commit()  # without commit() the change is lost when the program ends
        print(f"OK, {cur.rowcount} rows changed")


def print_query(conn, sql, params=()):
    """Run any SELECT and print all its columns. Works for every table and JOIN."""
    cur = conn.execute(sql, params)
    columns = [d[0] for d in cur.description]  # column names of the result
    print_table(columns, cur.fetchall())


def print_table(columns, rows):
    """Print rows as an aligned text table. None (SQL NULL) is shown as NULL."""
    lines = [list(columns)] + [
        ["NULL" if v is None else str(v) for v in row] for row in rows
    ]
    widths = [max(len(line[i]) for line in lines) for i in range(len(columns))]
    for line in lines:
        print(
            "  ".join(cell.ljust(width) for cell, width in zip(line, widths)).rstrip()
        )
    print(f"({len(rows)} rows)")


def add_user(conn, text):
    """Insert a user from JSON text or from a .json file.

    The full validation rules are in validate.py: copy validate_user() here if
    the exam asks to validate before saving.
    """
    if not text.lstrip().startswith(("{", "[")):  # not JSON, so it is a file name
        with open(text, encoding="utf-8-sig") as f:
            text = f.read()
    try:
        user = json.loads(text)
    except ValueError as e:
        fail(f"bad JSON: {e}")
    if not isinstance(user, dict):
        fail("the JSON must be one object {...}")
    unknown = sorted(set(user) - set(USER_COLUMNS))
    if unknown:
        fail("unknown field(s): " + ", ".join(unknown))
    if not (user.get("username") and user.get("full_name") and user.get("email")):
        fail("username, full_name and email are required")

    cur = conn.execute(
        "INSERT INTO users (username, full_name, email, phone, age, city, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            user["username"],
            user["full_name"],
            user["email"],
            user.get("phone"),
            user.get("age"),
            user.get("city"),
            user.get("status") or "active",
        ),
    )  # a duplicate gives sqlite3.IntegrityError: UNIQUE constraint failed: users.email
    conn.commit()
    print("created user with id", cur.lastrowid)


def load_file(conn, path):
    """Run a .sql script with many statements (CREATE TABLE, INSERT ...).
    Use it when the exam gives a .sql file:  python3 users.py --db exam.db load exam.sql"""
    with open(path, encoding="utf-8-sig") as f:
        conn.executescript(
            f.read()
        )  # executescript() runs many statements; execute() runs only one
    print(f"loaded {path}")


def need(text, name):
    """Return the command's argument, or stop with an error when it is missing."""
    if not text:
        fail(f"missing {name} (see -h)")
    return text


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
