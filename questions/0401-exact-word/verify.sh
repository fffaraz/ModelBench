#!/usr/bin/env bash
# Tests whether the model follows a strict "output only this" instruction. Pass
# only if the whole answer (read from STDIN) is the word "pong" (case-insensitive),
# ignoring surrounding whitespace. Any extra words, punctuation, or lines -> fail.
set -euo pipefail
ans="$(tr '[:upper:]' '[:lower:]')"
# Strip leading/trailing whitespace across the WHOLE answer, including newlines, so
# a stray surrounding newline (e.g. "\npong") still passes. Internal extra words,
# punctuation, or lines remain and correctly fail.
ans="${ans#"${ans%%[![:space:]]*}"}"   # strip leading whitespace
ans="${ans%"${ans##*[![:space:]]}"}"   # strip trailing whitespace
[ "$ans" = "pong" ]
