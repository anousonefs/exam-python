#!/usr/bin/env python3
"""Read a CSV log file and print a report.

    python3 logs.py data/logs.csv
    python3 logs.py data/logs.csv --top 3
    python3 logs.py data/logs.csv --level ERROR     only rows with level ERROR
    python3 logs.py data/logs.csv --sep ";"         file uses ; instead of ,

Standard library only.
EXAM: change the column names, LogEntry + parse_entry() and the sections in
report() to answer the questions you are given.
"""
import argparse
import csv
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from statistics import mean

# Column names in the CSV header (compared in lower case).
COL_TIME = "timestamp"
COL_LEVEL = "level"
COL_USER = "username"
COL_IP = "ip"
COL_ACTION = "action"
COL_STATUS = "status_code"
COL_DURATION = "response_time_ms"
COL_MESSAGE = "message"
REQUIRED_COLUMNS = [COL_TIME, COL_LEVEL, COL_USER, COL_IP, COL_ACTION, COL_STATUS, COL_DURATION, COL_MESSAGE]

# Time formats we try: %Y year, %m month, %d day, %H hour, %M minute, %S second.
TIME_FORMATS = [
    "%Y-%m-%d %H:%M:%S",     # 2026-10-12 08:30:00
    "%Y-%m-%d %H:%M:%S.%f",  # 2026-10-12 08:30:00.123
    "%Y-%m-%dT%H:%M:%S",     # 2026-10-12T08:30:00
    "%Y-%m-%dT%H:%M:%S%z",   # 2026-10-12T08:30:00Z or 2026-10-12T08:30:00+07:00
    "%d/%m/%Y %H:%M:%S",     # 12/10/2026 08:30:00 (day/month/year)
    "%Y/%m/%d %H:%M:%S",     # 2026/10/12 08:30:00
]


@dataclass
class LogEntry:
    """One row of the log file."""
    time: datetime
    level: str       # INFO, WARN, ERROR
    user: str
    ip: str
    action: str      # LOGIN, TRANSFER, ...
    status: int      # 200 = OK, 4xx = client error, 5xx = server error
    duration: float  # response time in milliseconds
    message: str

    @property
    def failed(self):
        """True when the request failed (status code 400 or more)."""
        return self.status >= 400


def main():
    parser = argparse.ArgumentParser(description="Read a CSV log file and print a report.")
    parser.add_argument("file", help="the CSV log file")
    parser.add_argument("--top", type=int, default=5, help="number of rows in each TOP list (default: 5)")
    parser.add_argument("--level", help="only analyze rows with this level, e.g. ERROR")
    parser.add_argument("--sep", default=",", help='field separator, e.g. ";" or "tab" (default: ",")')
    args = parser.parse_args()

    sep = "\t" if args.sep in ("tab", "\\t") else args.sep
    if len(sep) != 1:
        parser.error("--sep must be one character")

    try:
        entries, skipped = read_logs(args.file, sep)
    except (OSError, ValueError, csv.Error) as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
    if args.level:
        entries = [e for e in entries if e.level == args.level.upper()]
    report(entries, skipped, args.top)


def read_logs(path, sep):
    """Read the whole file. Broken rows are skipped (and printed on stderr),
    so one bad line does not stop the analysis."""
    entries = []
    skipped = 0
    # newline="" is needed by the csv module; utf-8-sig removes the BOM that Excel adds
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=sep, skipinitialspace=True)
        header = next(reader, None)
        if header is None:
            raise ValueError("the file is empty")
        col = {name.strip().lower(): i for i, name in enumerate(header)}  # column name -> position
        for name in REQUIRED_COLUMNS:
            if name not in col:
                raise ValueError(f"column {name!r} not found, the header is: {','.join(header)}")

        for row in reader:
            if not row:  # empty line
                continue
            try:
                entries.append(parse_entry(row, col, len(header)))
            except ValueError as e:
                skipped += 1
                print(f"skip line {reader.line_num}: {e}", file=sys.stderr)
    return entries, skipped


def parse_entry(row, col, num_fields):
    """Turn one CSV row into a LogEntry. Raises ValueError for a bad row."""
    if len(row) != num_fields:
        raise ValueError(f"has {len(row)} fields, expected {num_fields}")

    def get(name):
        return row[col[name]].strip()

    return LogEntry(
        time=parse_time(get(COL_TIME)),
        level=get(COL_LEVEL).upper(),
        user=get(COL_USER),
        ip=get(COL_IP),
        action=get(COL_ACTION).upper(),
        status=to_number(int, COL_STATUS, get(COL_STATUS)),
        duration=to_number(float, COL_DURATION, get(COL_DURATION)),
        message=get(COL_MESSAGE),
    )


def parse_time(text):
    for fmt in TIME_FORMATS:
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=None)  # drop the time zone so all times compare
        except ValueError:
            pass
    raise ValueError(f"unknown time format {text!r} (add it to TIME_FORMATS)")


def to_number(kind, name, text):
    """int("abc") fails with an unclear message, so add the column name."""
    try:
        return kind(text)
    except ValueError:
        raise ValueError(f"bad {name} {text!r}") from None


def report(entries, skipped, top):
    """Print all sections. EXAM: add or remove sections for your questions."""
    failed = [e for e in entries if e.failed]

    title("SUMMARY")
    print(f"Rows analyzed   : {len(entries)}")
    print(f"Rows skipped    : {skipped}")
    if not entries:
        return
    first = min(e.time for e in entries)
    last = max(e.time for e in entries)
    print(f"Time range      : {first} -> {last}")
    print(f"Failed requests : {len(failed)} ({percent(len(failed), len(entries)):.1f}%)")

    title("BY LEVEL")
    print_counts(Counter(e.level for e in entries), len(entries))

    title("BY STATUS CODE")
    print_counts(Counter(e.status for e in entries), len(entries))

    title(f"TOP {top} ACTIONS")
    print_counts(Counter(e.action for e in entries), len(entries), top)

    title(f"TOP {top} USERS")
    print_counts(Counter(e.user for e in entries), len(entries), top)

    title(f"TOP {top} USERS WITH FAILED REQUESTS")
    print_counts(Counter(e.user for e in failed), len(failed), top)

    title(f"TOP {top} IPS WITH FAILED REQUESTS")
    print_counts(Counter(e.ip for e in failed), len(failed), top)

    title("RESPONSE TIME (ms)")
    print_durations(entries)

    title("REQUESTS PER HOUR")
    print_per_hour(entries)

    title("SUSPICIOUS: 3 OR MORE FAILED LOGINS")
    failed_logins = Counter(e.user for e in failed if e.action == "LOGIN")
    suspicious = [(user, n) for user, n in sort_by_count(failed_logins) if n >= 3]
    for user, n in suspicious:
        print(f"{user}: {n} failed logins")
    if not suspicious:
        print("(none)")


def print_durations(entries):
    """Average / min / max response time, overall and per action."""
    durations = [e.duration for e in entries]
    print(f"All requests: avg {mean(durations):.1f}, min {min(durations):.0f}, max {max(durations):.0f}\n")

    by_action = defaultdict(list)  # action -> list of durations
    for e in entries:
        by_action[e.action].append(e.duration)
    actions = sorted(by_action, key=lambda a: mean(by_action[a]), reverse=True)  # slowest first
    print_table(["ACTION", "AVG ms", "REQUESTS"],
                [[a, f"{mean(by_action[a]):.1f}", len(by_action[a])] for a in actions])


def print_per_hour(entries):
    """Requests (and failures) in each hour, with a bar chart."""
    per_hour = Counter(e.time.strftime("%Y-%m-%d %H:00") for e in entries)
    failed = Counter(e.time.strftime("%Y-%m-%d %H:00") for e in entries if e.failed)
    most = max(per_hour.values())
    rows = []
    for hour in sorted(per_hour):  # "2026-10-12 08:00" text sorts in time order
        n = per_hour[hour]
        rows.append([hour, n, failed[hour], "#" * (n * 30 // most)])  # the busiest hour gets 30 #
    print_table(["HOUR", "REQUESTS", "FAILED", ""], rows)


# ---- small helpers you can reuse for any "count X by Y" question ----

def sort_by_count(counts):
    """Sort a Counter by count (high to low), then by key."""
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def print_counts(counts, total, limit=None):
    """Print "key  count  percent" lines, biggest first. limit=None shows all."""
    rows = [[key, n, f"{percent(n, total):5.1f}%"] for key, n in sort_by_count(counts)[:limit]]
    if rows:
        print_table(None, rows)
    else:
        print("(none)")


def print_table(header, rows):
    """Print rows as aligned columns (header=None: no header line)."""
    lines = ([header] if header else []) + rows
    lines = [[str(v) for v in line] for line in lines]
    widths = [max(len(line[i]) for line in lines) for i in range(len(lines[0]))]
    for line in lines:
        print("  ".join(cell.ljust(width) for cell, width in zip(line, widths)).rstrip())


def percent(part, total):
    return 100 * part / total if total else 0


def title(text):
    print(f"\n== {text} ==")


if __name__ == "__main__":
    main()
