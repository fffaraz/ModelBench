#!/usr/bin/env python3
"""Verify the merged quick-facts answers (read from STDIN).

The model is asked five numbered questions and is expected to reply with a
numbered list. We map each "N. <answer>" line to its number and check it with
the same matching rules the original standalone questions used.

Partial credit: SCORE is the fraction answered correctly. Exit 0 only if all
five are correct, so the question still doubles as a pass/fail CI check.
"""
import re
import sys

answer = sys.stdin.read()

# Map answer number -> text, from lines like "1. Jupiter" or "2) H2O".
got = {}
for line in answer.splitlines():
    m = re.match(r"\s*(\d+)\s*[.)]\s*(.*)", line)
    if m:
        got.setdefault(int(m.group(1)), m.group(2).strip())


def has(pattern, text):
    return re.search(pattern, text, re.IGNORECASE) is not None


def water(text):
    # ignore whitespace and accept the subscript form (H₂O)
    norm = re.sub(r"\s+", "", text).replace("₂", "2")
    return has(r"h2o", norm)


# (number, label, predicate) — predicates mirror the original verify scripts
checks = [
    (1, "largest planet = Jupiter", lambda t: has(r"\bjupiter\b", t)),
    (2, "water formula = H2O", water),
    (3, "Roman numeral 9 = IX", lambda t: has(r"\bix\b", t)),
    (4, "gold symbol = Au", lambda t: has(r"\bau\b", t)),
    (5, "17 + 25 = 42", lambda t: has(r"(^|[^0-9])42([^0-9]|$)", t)),
]

passed = 0
for num, label, pred in checks:
    text = got.get(num, "")
    ok = bool(text) and pred(text)
    passed += ok
    print(f"  [{'ok  ' if ok else 'MISS'}] {num}. {label}  (got: {text!r})")

total = len(checks)
print(f"SCORE={passed / total:.4f}")
print(f"{passed}/{total} correct")
sys.exit(0 if passed == total else 1)
