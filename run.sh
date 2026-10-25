#!/usr/bin/env sh
set -eu

root="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$root"

if [ -n "${PYTHON:-}" ]; then
    python="$PYTHON"
elif command -v python3 >/dev/null 2>&1; then
    python=python3
else
    python=python
fi

venv_python="$root/.venv/bin/python"
command_path="$root/.venv/bin/grep-knowledge"

if [ ! -x "$venv_python" ]; then
    "$python" -m venv .venv
fi
if [ ! -x "$command_path" ]; then
    "$venv_python" -m pip install -e .
fi
[ -f .env ] || cp .env.example .env
[ -f config.yml ] || cp config.example.yml config.yml

"$command_path" index
