#!/usr/bin/env python3
"""Shared verifier for coding questions: pull the code out of the model's answer (read on
stdin), run it, and compare its stdout to an expected-output file. exit 0 = pass, non-zero = fail.

Usage (typically from a question's meta.json "verify"):
    python3 ../../check_code.py <lang> <expected_output_path>

<lang> is "python" (aka "py") or "c". The expected-output path is resolved relative to the
verify cwd, which bench.py sets to the question's own directory -- so "expected_output.txt"
finds the file sitting next to prompt.txt.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

COMPILE_TIMEOUT = 30
RUN_TIMEOUT = 15


def extract_code(answer, fence):
    """Prefer a fenced code block matching the language; fall back to the whole answer."""
    m = re.search(r"```(?:" + fence + r")?\s*\n(.*?)```", answer, re.S | re.I)
    return m.group(1) if m else answer


def run_python(code):
    """Write the code to a temp file and run it. Returns a CompletedProcess."""
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(code)
        code_path = f.name
    try:
        return subprocess.run(
            [sys.executable, code_path], capture_output=True, text=True, timeout=RUN_TIMEOUT
        )
    finally:
        os.unlink(code_path)


def run_c(code):
    """Compile the code, then run the binary. Returns a CompletedProcess, or exits on a
    compile error / missing compiler (those are failures, not runnable programs)."""
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
        build = subprocess.run(
            [cc, src_path, "-o", bin_path], capture_output=True, text=True, timeout=COMPILE_TIMEOUT
        )
        if build.returncode != 0:
            print("the generated program failed to compile:", build.returncode, file=sys.stderr)
            print(build.stderr, file=sys.stderr)
            sys.exit(1)
        return subprocess.run([bin_path], capture_output=True, text=True, timeout=RUN_TIMEOUT)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# lang -> (code-fence alternatives, runner)
LANGS = {
    "python": (r"python|py", run_python),
    "py": (r"python|py", run_python),
    "c": (r"c|cpp|c\+\+", run_c),
}


def main():
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} <lang> <expected_output_path>", file=sys.stderr)
        sys.exit(2)
    lang, expected_path = sys.argv[1].lower(), sys.argv[2]
    if lang not in LANGS:
        print(f"unsupported lang {lang!r}; supported: {', '.join(sorted(LANGS))}", file=sys.stderr)
        sys.exit(2)

    fence, runner = LANGS[lang]
    code = extract_code(sys.stdin.read(), fence)
    proc = runner(code)

    if proc.returncode != 0:
        print("the generated program exited non-zero:", proc.returncode, file=sys.stderr)
        print(proc.stderr, file=sys.stderr)
        sys.exit(1)

    with open(expected_path) as f:
        expected = f.read().strip()
    got = proc.stdout.strip()
    if got == expected:
        sys.exit(0)

    print("program output did not match expected.", file=sys.stderr)
    print("--- expected ---\n" + expected, file=sys.stderr)
    print("--- got ---\n" + got, file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
