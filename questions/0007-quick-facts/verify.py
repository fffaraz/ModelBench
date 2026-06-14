#!/usr/bin/env python3
"""Verify the merged quick-facts answers (model reply read from STDIN).

The model is asked five numbered questions and is expected to reply with a
numbered list. Expected answers live in `expected.txt` (one "N. <answer>" line
per question), so the bank can be edited without touching this script.

For each number we compare the model's answer to the expected one, ignoring
case and whitespace, accepting the H₂O subscript form, and requiring the
expected value to appear as a standalone token (so "six" won't match "IX",
"Australia" won't match "Au", etc.).

Partial credit: SCORE is the fraction answered correctly. Exit 0 only if all
are correct, so the question still doubles as a pass/fail CI check.
"""
import re
import sys
from pathlib import Path

NUMBERED = re.compile(r"\s*(\d+)\s*[.)]\s*(.*)")


def parse_numbered(text):
    """Map answer number -> text, from lines like "1. Jupiter" or "2) H2O"."""
    out = {}
    for line in text.splitlines():
        m = NUMBERED.match(line)
        if m:
            out.setdefault(int(m.group(1)), m.group(2).strip())
    return out


def normalize(text):
    # lowercase, collapse whitespace, accept the subscript form (H₂O -> h2o).
    # Whitespace is collapsed (not removed) so word boundaries survive and a
    # chatty "is jupiter" still matches the standalone token "jupiter".
    text = text.replace("₂", "2").lower()
    return re.sub(r"\s+", " ", text).strip()


def matches(expected, got):
    """True if normalized `expected` appears as a standalone token in `got`."""
    exp, g = normalize(expected), normalize(got)
    if not exp:
        return False
    # boundaries on the alphanumeric set so "ix"/"au"/"42" must stand alone
    return re.search(rf"(?<![a-z0-9]){re.escape(exp)}(?![a-z0-9])", g) is not None


expected_path = Path("expected.txt")
if not expected_path.exists():
    sys.exit(f"verify error: {expected_path.resolve()} not found")

expected = parse_numbered(expected_path.read_text(encoding="utf-8"))
if not expected:
    sys.exit("verify error: expected.txt has no numbered answers")

got = parse_numbered(sys.stdin.read())

passed = 0
for num in sorted(expected):
    want = expected[num]
    ans = got.get(num, "")
    ok = bool(ans) and matches(want, ans)
    passed += ok
    print(f"  [{'ok  ' if ok else 'MISS'}] {num}. want {want!r}  (got: {ans!r})")

total = len(expected)
print(f"SCORE={passed / total:.4f}")
print(f"{passed}/{total} correct")
sys.exit(0 if passed == total else 1)
