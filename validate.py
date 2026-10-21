#!/usr/bin/env python3
"""Check the JSON data for "create user" and print every problem found.

    python3 validate.py '{"username":"somchai","password":"Secret@123","full_name":"Somchai P","email":"somchai@mail.com","phone":"02055512345","age":30}'
    python3 validate.py data/user_valid.json        JSON from a file
    python3 validate.py < data/user_invalid.json    JSON from stdin
    python3 validate.py data/users_batch.json --json   JSON output; an array = many users

Exit code: 0 = valid, 1 = invalid. Standard library only.
EXAM: change FIELDS and the rules in validate_user().
"""
import argparse
import json
import re
import string
import sys

# The JSON fields and their types. EXAM: change them to match the question.
FIELDS = {
    "username": str,
    "password": str,
    "full_name": str,
    "email": str,
    "phone": str,
    "age": int,
    "role": str,
}

# fullmatch() checks the WHOLE text, so no ^ and $ are needed.
USERNAME_RE = re.compile(r"[a-z0-9_]{3,20}")
EMAIL_RE = re.compile(r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")
PHONE_RE = re.compile(r"(\+856|0)20[0-9]{8}")  # Lao mobile: 020 + 8 digits, or +856 20 + 8 digits
ROLES = ["customer", "teller", "admin"]


def main():
    parser = argparse.ArgumentParser(description='Validate "create user" JSON.')
    parser.add_argument("input", nargs="*", help="JSON text or a .json file (nothing: read stdin)")
    parser.add_argument("--json", action="store_true", help="print the result as JSON")
    args = parser.parse_intermixed_args()  # flags may come anywhere: user.json --json

    try:
        text = read_input(args.input)
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(2)

    try:
        results = [check(user) for user in decode_users(text)]
    except ValueError as e:  # the JSON itself is broken: report it like a validation error
        results = [{"valid": False, "errors": [{"field": "json", "message": str(e)}]}]

    is_list = text.strip().startswith("[")
    if args.json:
        print(json.dumps(results if is_list else results[0], indent=2, ensure_ascii=False))
    else:
        print_text(results)
    sys.exit(0 if all(r["valid"] for r in results) else 1)


def check(user):
    """Check one user: field names and types, then clean it, then the rules."""
    errors = check_fields(user)
    if not errors:
        user = normalize(user)
        errors = validate_user(user)
    if errors:
        return {"valid": False, "errors": errors}
    user["password"] = "********"  # never print a password
    return {"valid": True, "user": user}


def check_fields(user):
    """json.loads() accepts any fields and types, so check them here."""
    if not isinstance(user, dict):
        return [error("json", "each user must be a JSON object {...}")]
    errors = []
    for key, value in user.items():
        if key not in FIELDS:
            errors.append(error(key, "unknown field"))
        elif value is not None and not has_type(value, FIELDS[key]):
            errors.append(error(key, f"has the wrong type: expected {FIELDS[key].__name__}, got {type(value).__name__}"))
    return errors


def has_type(value, kind):
    # In Python True/False are ints too, so "age": true must be rejected by hand.
    return isinstance(value, kind) and not isinstance(value, bool)


def normalize(user):
    """Clean the input before validating: trim spaces, lower case, defaults."""
    u = {key: user.get(key) for key in FIELDS}  # every field exists now; missing ones are None
    u["username"] = (u["username"] or "").strip().lower()
    u["password"] = u["password"] or ""
    u["full_name"] = " ".join((u["full_name"] or "").split())  # trim and remove double spaces
    u["email"] = (u["email"] or "").strip().lower()
    u["phone"] = (u["phone"] or "").replace(" ", "").replace("-", "")
    u["age"] = u["age"] or 0
    u["role"] = (u["role"] or "").strip().lower() or "customer"  # default value
    return u


def validate_user(u):
    """Return ALL the problems, not only the first one."""
    errors = []

    def add(field, message):
        errors.append(error(field, message))

    # username: required, 3-20 characters, only a-z 0-9 _
    if not u["username"]:
        add("username", "is required")
    elif not USERNAME_RE.fullmatch(u["username"]):
        add("username", "must be 3-20 characters: letters, digits or _")

    # password: at least 8 characters with upper case, lower case, digit and symbol
    password = u["password"]
    if not password:
        add("password", "is required")
    else:
        if len(password) < 8:
            add("password", "must be at least 8 characters")
        if not any(c.isupper() for c in password):
            add("password", "must contain an upper case letter")
        if not any(c.islower() for c in password):
            add("password", "must contain a lower case letter")
        if not any(c.isdigit() for c in password):
            add("password", "must contain a digit")
        if not any(c in string.punctuation for c in password):
            add("password", "must contain a symbol like @ # $ !")

    # full_name: required, 2-100 characters (len() counts characters, also Lao letters)
    n = len(u["full_name"])
    if n == 0:
        add("full_name", "is required")
    elif n < 2 or n > 100:
        add("full_name", "must be 2-100 characters")

    # email: required, valid format
    if not u["email"]:
        add("email", "is required")
    elif not EMAIL_RE.fullmatch(u["email"]):
        add("email", "is not a valid email address")

    # phone: required, Lao mobile number
    if not u["phone"]:
        add("phone", "is required")
    elif not PHONE_RE.fullmatch(u["phone"]):
        add("phone", "must be a Lao mobile number like 02055512345 or +8562055512345")

    # age: 18-100 (0 or missing means it was not sent)
    if not u["age"]:
        add("age", "is required")
    elif not 18 <= u["age"] <= 100:
        add("age", "must be between 18 and 100")

    # role: one of the allowed values
    if u["role"] not in ROLES:
        add("role", "must be one of: " + ", ".join(ROLES))
    return errors


def error(field, message):
    return {"field": field, "message": message}


def read_input(words):
    """Get the JSON text from the arguments, from a file, or from stdin."""
    text = " ".join(words).strip()
    if text in ("", "-"):
        if sys.stdin.isatty():
            print("Paste the JSON, then press Ctrl+D (Windows: Ctrl+Z then Enter):", file=sys.stderr)
        return sys.stdin.read()
    if text.startswith(("{", "[")):
        return text  # JSON typed on the command line
    with open(text, encoding="utf-8-sig") as f:  # a file name (utf-8-sig removes a BOM)
        return f.read()


def decode_users(text):
    """Read one user {...} or a list of users [{...}, {...}]. Raises ValueError."""
    if not text.strip():
        raise ValueError("no JSON input")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:  # e says the line and column of the problem
        raise ValueError(f"invalid JSON: {e}") from None
    users = data if isinstance(data, list) else [data]
    if not users:
        raise ValueError("the list of users is empty")
    return users


def print_text(results):
    for i, result in enumerate(results, start=1):
        prefix = f"User #{i}: " if len(results) > 1 else ""
        if result["valid"]:
            print(prefix + "VALID")
            print(json.dumps(result["user"], indent=2, ensure_ascii=False))
        else:
            print(f"{prefix}INVALID - {len(result['errors'])} error(s)")
            for e in result["errors"]:
                print(f"  - {e['field']}: {e['message']}")


if __name__ == "__main__":
    main()
