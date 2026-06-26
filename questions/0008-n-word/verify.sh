#!/usr/bin/env bash
# Pass if the model's answer (read from STDIN) is the single expected word from
# expected.txt. Comparison ignores case, blank lines, surrounding whitespace,
# and trailing punctuation, but the answer must otherwise be exactly that word.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)" # resolve support files next to this script

# normalize: trim each line, strip surrounding punctuation/quotes, drop blank
# lines, lowercase
norm() {
  sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' \
      -e 's/^["'\''`.,!?]*//' -e 's/["'\''`.,!?]*$//' \
      -e '/^$/d' | tr '[:upper:]' '[:lower:]'
}

expected="$(norm < "$here/expected.txt")"
actual="$(norm)" # reads the model's answer from STDIN

if [ "$actual" != "$expected" ]; then
  echo "Expected '$expected' but got '$actual'."
  exit 1
fi
