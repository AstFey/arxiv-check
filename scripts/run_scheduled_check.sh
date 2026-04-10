#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
WORKSPACE=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

cd "$WORKSPACE"

if [ -n "${PYTHONPATH:-}" ]; then
  export PYTHONPATH="src:$PYTHONPATH"
else
  export PYTHONPATH="src"
fi

resolve_python() {
  for candidate in \
    "$WORKSPACE/.venv/bin/python" \
    "$WORKSPACE/.venv/bin/python3" \
    "$WORKSPACE/.venv/Scripts/python.exe"
  do
    if [ -x "$candidate" ]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return 0
  fi

  if command -v python >/dev/null 2>&1; then
    command -v python
    return 0
  fi

  printf '%s\n' "Could not find Python. Create .venv or add python3/python to PATH." >&2
  return 1
}

PYTHON_BIN=$(resolve_python)
exec "$PYTHON_BIN" -m arxiv_check.cli check --telegram
