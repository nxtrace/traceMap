#!/usr/bin/env bash

# Regenerate HTML outputs from stored JSON logs.
# Processes each ./log/*.json through main.process() and writes ./html/<name>.html.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${SCRIPT_DIR}"
LOG_DIR="${REPO_ROOT}/log"
HTML_DIR="${REPO_ROOT}/html"

if [[ ! -d "${LOG_DIR}" ]]; then
  echo "Log directory not found: ${LOG_DIR}" >&2
  exit 1
fi

mkdir -p "${HTML_DIR}"

if ! find "${LOG_DIR}" -maxdepth 1 -type f -name '*.json' -print -quit | grep -q .; then
  echo "No JSON log files found in ${LOG_DIR}; nothing to regenerate." >&2
  exit 0
fi

echo "Removing previous HTML outputs in ${HTML_DIR}"
find "${HTML_DIR}" -maxdepth 1 -type f -name '*.html' -exec rm -f {} +

(
  cd "${REPO_ROOT}"
  python3 - "${LOG_DIR}" "${HTML_DIR}" <<'PY'
import json
import traceback
import sys
from pathlib import Path

from main import process

log_dir = Path(sys.argv[1])
html_dir = Path(sys.argv[2])

for idx, json_path in enumerate(log_dir.glob("*.json"), start=1):
    output_name = json_path.stem + ".html"
    print(f"[{idx}] Generating {output_name} from {json_path.name}", flush=True)
    try:
        with json_path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        result = process(data, filename=output_name)
        output_file = html_dir / output_name

        if isinstance(result, str) and result.endswith(output_name) and output_file.exists():
            continue
        if output_file.exists():
            continue
        print(f"Skipping {json_path.name}; process() returned: {result}", file=sys.stderr, flush=True)
    except Exception as exc:
        print(f"Skipping {json_path.name}; error encountered: {exc}", file=sys.stderr, flush=True)
        traceback.print_exc()

print(f"HTML regeneration complete. Files saved to {html_dir}")
PY
)
