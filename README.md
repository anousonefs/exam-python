# Python exam kit (works offline)

Small Python command-line programs, one for each type of exam task.
They use **only the Python standard library**: nothing to install, no internet needed.

| Exam task                   | Program       | Standard library modules                             |
|-----------------------------|---------------|------------------------------------------------------|
| Query users in SQLite       | `users.py`    | `sqlite3`, `json`, `argparse`                        |
| Analyze a CSV log file      | `logs.py`     | `csv`, `collections.Counter`, `datetime`, `statistics` |
| Validate "create user" JSON | `validate.py` | `json`, `re`                                         |
| Sort 1 array                | `sort1.py`    | none                                                 |
| Sort 2 arrays               | `sort2.py`    | none                                                 |

Each program is **one `.py` file**. Practice data is in `data/` (the same data as the Go kit).
Every program prints its help with `-h`.

Needs Python 3.8 or newer. Tested with Python 3.9, 3.11, 3.13, 3.14 and 3.15 (same output on all).

## Run

There is no build step: the `.py` file is the program.

- Mac / Linux: `python3 sort1.py 5 3 1` (or `./sort1.py 5 3 1`, the files are executable)
- Windows: `python sort1.py 5 3 1` or `py sort1.py 5 3 1`

## Run with the sample data

```bash
# 1. Query users in SQLite
python3 users.py tables                  # tables, columns, row counts: always start here
python3 users.py list
python3 users.py get 3
python3 users.py get 3 --json
python3 users.py search vong
python3 users.py status blocked
python3 users.py stats                   # COUNT, AVG, GROUP BY and JOIN examples
python3 users.py sql "SELECT * FROM users WHERE age > 40 ORDER BY age DESC"
python3 users.py add '{"username":"bob","full_name":"Bob Smith","email":"bob@example.com","age":30}'
python3 users.py --db exam.db load exam.sql   # if the exam gives a .sql file instead of a .db file

# 2. Analyze the CSV log file
python3 logs.py data/logs.csv
python3 logs.py data/logs.csv --level ERROR --top 3

# 3. Validate "create user" JSON
python3 validate.py data/user_valid.json
python3 validate.py < data/user_invalid.json
python3 validate.py data/users_batch.json --json
python3 validate.py '{"username":"bob","age":"twenty"}'

# 4. Sort 1 array
python3 sort1.py 64 34 25 12 22 11 90
python3 sort1.py --desc --algo bubble -5 3 0 9
python3 sort1.py                         # then type the numbers

# 5. Sort 2 arrays
python3 sort2.py "5,3,9,1" "8,2,3,7"
python3 sort2.py --desc "[5, -3, 9]" "[8, 2, 3]"
```

Windows: JSON inside quotes is hard to type in the Windows terminal, so give a
file instead: `py validate.py data\user_valid.json`.

Reset the practice database: `python3 users.py load data/users.sql`

## Differences from the Go kit

- SQLite is built into Python (`import sqlite3`): no driver, no `vendor/` folder.
- No build step.
- Options have two dashes: `--db`, `--json`, `--top`, `--level`, `--desc`, `--algo`.
- An empty database value (NULL) is `None` in Python. It shows as `NULL` in tables and `null` in JSON.
- After INSERT, UPDATE or DELETE you must call `conn.commit()`, or the change is lost.

## Before exam day: checklist

1. On the exam computer, check `python3 --version` (Windows: `py --version`). You need 3.8 or newer.
2. If you may bring files, copy this folder to a USB drive. Nothing else is needed.
3. `pip install` needs internet, so only use the standard library (everything here does).
4. Read the docs offline: `python3 -m pydoc str.split`, `python3 -m pydoc csv`,
   `python3 -m pydoc sqlite3`. Or inside Python: `help(str.split)`.

## Change the code for your exam question

**users.py**
1. `python3 users.py --db exam.db tables` to see the table and column names.
2. `python3 users.py --db exam.db sql "SELECT * FROM users LIMIT 5"` to see the data.
3. Change `USER_COLUMNS` (the table name is in `SELECT_USERS`).
4. New question: add the name to `choices`, an `elif` in `main()`, and a function.
   Always pass values with `?` placeholders: `conn.execute("... WHERE id = ?", (user_id,))`.

**logs.py**
1. Run it once on the exam file. If a column name is different, the error shows the real header.
2. Change the `COL_...` constants, the `LogEntry` class and `parse_entry()`.
3. In `report()`, keep the sections you need. Most questions are one line:
   `print_counts(Counter(e.user for e in entries if e.failed), len(entries), top)`.
4. Another time format? Add it to `TIME_FORMATS`.

**validate.py**
1. Change `FIELDS` (field names and their types).
2. Change the rules in `validate_user()`. Each rule is a short `if`.

**sort1.py / sort2.py**: keep what the question asks for. If the built-in sort is
allowed, `sorted(nums)` is enough, and sets do the rest:
`sorted(set(a) | set(b))` (union), `sorted(set(a) & set(b))` (in both).

## Python cheat sheet

Not a program: copy the lines you need.

```python
# --- arguments, numbers, strings ---
import sys
args = sys.argv[1:]                     # command-line arguments (list of str)
n = int("42"); f = float("3.5"); s = str(42)
f"{3.14159:.2f}"                        # '3.14'
"a,b,c".split(",")                      # ['a', 'b', 'c']
"  a   b ".split()                      # ['a', 'b'] (split on any spaces)
", ".join(["a", "b"])                   # 'a, b'
s.strip(); s.lower(); s.upper(); "x" in s; s.startswith("x")
len("ສະບາຍດີ")                           # number of characters (not bytes)

# --- read input ---
line = input("Enter: ")                 # one line from the keyboard
text = sys.stdin.read()                 # everything sent with < file or a pipe
with open("file.txt", encoding="utf-8") as f:
    for line in f:                      # a file line by line
        line = line.rstrip("\n")

# --- count and group ---
from collections import Counter, defaultdict
count = Counter(words)                  # Counter({'a': 3, 'b': 1})
count.most_common(3)                    # top 3: [('a', 3), ('b', 1)]
groups = defaultdict(list)
for u in users:
    groups[u["city"]].append(u)

# --- sort ---
sorted(nums); sorted(nums, reverse=True); nums.sort()
sorted(users, key=lambda u: (u["age"], u["name"]))     # by age, then by name
sorted(users, key=lambda u: (-u["age"], u["name"]))    # age high -> low, then name

# sort two lists together (names by score)
pairs = sorted(zip(names, scores), key=lambda p: p[1], reverse=True)
names = [p[0] for p in pairs]; scores = [p[1] for p in pairs]

# --- dates: %Y year, %m month, %d day, %H hour, %M minute, %S second ---
from datetime import datetime
t = datetime.strptime("2026-10-12 08:30:00", "%Y-%m-%d %H:%M:%S")
t.strftime("%d/%m/%Y"); t.hour; t.weekday(); (t2 - t).total_seconds() / 60; datetime.now()

# --- JSON ---
import json
data = json.loads(text)                                 # JSON text -> dict / list
text = json.dumps(data, indent=2, ensure_ascii=False)   # dict -> JSON text (keeps Lao letters)

# --- CSV ---
import csv
with open("logs.csv", newline="", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):                       # each row is a dict: row["level"]
        print(row["level"])

# --- SQL (sqlite3) ---
import sqlite3
conn = sqlite3.connect("users.db")
conn.row_factory = sqlite3.Row                          # rows work like dicts: row["email"]
rows = conn.execute("SELECT id, name FROM users WHERE age > ?", (30,)).fetchall()  # (30,) needs the comma
row = conn.execute("SELECT COUNT(*) FROM users").fetchone()   # one row, or None
conn.execute("UPDATE users SET status = ? WHERE id = ?", ("blocked", 3))
conn.commit()                                           # needed after INSERT / UPDATE / DELETE!

# --- errors and exit codes ---
try:
    n = int(text)
except ValueError:
    print("error: not a number", file=sys.stderr)
    sys.exit(1)
```

## Plan for the 2 hours

| Time      | Do                                                                                   |
|-----------|--------------------------------------------------------------------------------------|
| 0:00–0:10 | Read all 5 questions. Look at the files: `python3 users.py --db X.db tables`, `head logs.csv`. |
| 0:10–0:35 | Sort 1 array and sort 2 arrays (quick points).                                       |
| 0:35–1:00 | Validate JSON.                                                                       |
| 1:00–1:25 | SQLite query.                                                                        |
| 1:25–1:50 | Log analysis.                                                                        |
| 1:50–2:00 | Run every program again with the exam's input and check the output format.           |

When a task works, **don't break it**: copy the file before big changes.
