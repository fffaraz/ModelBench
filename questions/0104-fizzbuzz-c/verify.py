#!/usr/bin/env python3
"""Programming-question verifier: pull the C code out of the model's answer, compile it, run it,
and compare its stdout to expected_output.txt. exit 0 = pass, non-zero = fail.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
answer = sys.stdin.read()

# Prefer a fenced code block; fall back to the whole answer.
m = re.search(r"```(?:c|cpp|c\+\+)?\s*\n(.*?)```", answer, re.S | re.I)
code = m.group(1) if m else answer

cc = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
if cc is None:
    print("no C compiler (cc/gcc/clang) found on PATH", file=sys.stderr)
    sys.exit(1)

tmp = tempfile.mkdtemp()
src_path = os.path.join(tmp, "prog.c")
bin_path = os.path.join(tmp, "prog")
try:
    with open(src_path, "w") as f:
        f.write(code)

    build = subprocess.run([cc, src_path, "-o", bin_path], capture_output=True, text=True, timeout=30)
    if build.returncode != 0:
        print("the generated program failed to compile:", build.returncode, file=sys.stderr)
        print(build.stderr, file=sys.stderr)
        sys.exit(1)

    proc = subprocess.run([bin_path], capture_output=True, text=True, timeout=15)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

if proc.returncode != 0:
    print("the generated program exited non-zero:", proc.returncode, file=sys.stderr)
    print(proc.stderr, file=sys.stderr)
    sys.exit(1)

expected = (HERE / "expected_output.txt").read_text().strip()
got = proc.stdout.strip()
if got == expected:
    sys.exit(0)

print("program output did not match expected.", file=sys.stderr)
print("--- expected ---\n" + expected, file=sys.stderr)
print("--- got ---\n" + got, file=sys.stderr)
sys.exit(1)
