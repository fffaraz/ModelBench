#!/usr/bin/env python3
"""Programming-question verifier: pull the code out of the model's answer, run it, and compare
its stdout to expected_output.txt. exit 0 = pass, non-zero = fail.

Reports *why* it failed so an empty/garbled model answer is distinguishable from code that
ran but produced the wrong output.
"""
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
answer = sys.stdin.read()

# Case 1: the model returned nothing at all. With a non-trivial latency this usually means a
# reasoning model spent its whole max_tokens budget on hidden reasoning and was cut off
# (finish_reason "length") before emitting visible content. Bumping max_tokens often fixes it.
if not answer.strip():
    print("the model returned an empty answer (no content to verify).", file=sys.stderr)
    print("likely a reasoning model that hit max_tokens before producing output; "
          "try raising max_tokens in config.json or meta.json.", file=sys.stderr)
    sys.exit(1)

# Prefer a fenced code block; fall back to the whole answer.
m = re.search(r"```(?:python|py)?\s*\n(.*?)```", answer, re.S | re.I)
if m:
    code = m.group(1)
else:
    # Case 2: there is an answer but no ```python block — the model ignored the format
    # instruction. Note it, then try running the raw answer as a last resort.
    print("warning: no fenced ```python code block found; "
          "treating the whole answer as code.", file=sys.stderr)
    code = answer

with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
    f.write(code)
    code_path = f.name
try:
    proc = subprocess.run([sys.executable, code_path], capture_output=True, text=True, timeout=15)
finally:
    os.unlink(code_path)


def show_answer():
    """Print the raw model answer so failures can be diagnosed from the captured output."""
    print("--- model answer ---\n" + answer.strip(), file=sys.stderr)


if proc.returncode != 0:
    print("the generated program exited non-zero:", proc.returncode, file=sys.stderr)
    print("--- stderr ---\n" + proc.stderr.strip(), file=sys.stderr)
    show_answer()
    sys.exit(1)

expected = (HERE / "expected_output.txt").read_text().strip()
got = proc.stdout.strip()
if got == expected:
    sys.exit(0)

print("program output did not match expected.", file=sys.stderr)
print("--- expected ---\n" + expected, file=sys.stderr)
print("--- got ---\n" + (got if got else "(program produced no output)"), file=sys.stderr)
show_answer()
sys.exit(1)
