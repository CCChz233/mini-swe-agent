#!/usr/bin/env bash
set -euo pipefail

COMMON_ARGS=(
  --workers 4
  --skip-missing
  --redo-existing
)

FEEDBACK_ARGS=(
  --feedback-loop
  --feedback-mode rule
  --feedback-every-n-steps 2
  --feedback-max-rounds 6
  --feedback-submission-gate
)

PYTHONPATH=src python -m minisweagent.run_locbench \
  --mode tools_radar \
  --tools-prompt oracle_sniper \
  --method miniswe_tools_oracle_sniper__smoke__feedback_rule \
  "${COMMON_ARGS[@]}" \
  "${FEEDBACK_ARGS[@]}"

PYTHONPATH=src python -m minisweagent.run_locbench \
  --mode tools_radar \
  --tools-prompt neutral \
  --method miniswe_tools_radar__neutral__feedback_rule \
  "${COMMON_ARGS[@]}" \
  "${FEEDBACK_ARGS[@]}"

PYTHONPATH=src python -m minisweagent.run_locbench \
  --mode tools_radar \
  --tools-prompt search_first \
  --method miniswe_tools_radar__search_first__feedback_rule \
  "${COMMON_ARGS[@]}" \
  "${FEEDBACK_ARGS[@]}"

PYTHONPATH=src python -m minisweagent.run_locbench \
  --mode bash \
  --method miniswe_bash__feedback_rule \
  "${COMMON_ARGS[@]}" \
  "${FEEDBACK_ARGS[@]}"

PYTHONPATH=src python -m minisweagent.run_locbench \
  --mode tools \
  --tools-prompt neutral \
  --method miniswe_tools__neutral__feedback_rule \
  "${COMMON_ARGS[@]}" \
  "${FEEDBACK_ARGS[@]}"
