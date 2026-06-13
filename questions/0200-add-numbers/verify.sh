#!/usr/bin/env bash
# Pass if the answer (read from STDIN) contains the number 42 as a standalone token.
set -euo pipefail
grep -qE '(^|[^0-9])42([^0-9]|$)'
