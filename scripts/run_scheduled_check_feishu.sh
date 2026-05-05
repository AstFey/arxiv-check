#!/usr/bin/env sh
# Daily scheduled check — sends results to Feishu (Lark).
# Usage: add to cron, e.g.:
#   0 9 * * * /bin/sh /path/to/arxiv-check/scripts/run_scheduled_check_feishu.sh >> /tmp/arxiv-check.log 2>&1
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
WORKSPACE=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

cd "$WORKSPACE"

# Load .env if present so secrets don't have to be set manually.
if [ -f "$WORKSPACE/.env" ]; then
  # shellcheck disable=SC1091
  . "$WORKSPACE/.env"
fi

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
exec "$PYTHON_BIN" -m arxiv_check.cli check --feishu
