#!/usr/bin/env bash
PYTHONPATH=src python -m minisweagent.run_locbench \
  --mode tools_radar \
  --tools-prompt neutral \
  --method miniswe_tools_radar__neutral \
  --workers 4 \
  --skip-missing \
  --redo-existing 
  


PYTHONPATH=src python -m minisweagent.run_locbench \
  --mode tools_radar \
  --tools-prompt neutral \
  --method miniswe_tools_radar__neutral__feedback_rule \
  --workers 4 \
  --skip-missing \
  --redo-existing \
  --feedback-loop \
  --feedback-mode rule \
  --feedback-every-n-steps 3 \
  --feedback-max-rounds 6 \
  --feedback-submission-gate

PYTHONPATH=src python -m minisweagent.run_locbench \
  --mode bash \
  --method miniswe_bash__feedback_rule \
  --workers 4 \
  --skip-missing \
  --redo-existing \
  --feedback-loop \
  --feedback-mode rule \
  --feedback-every-n-steps 3 \
  --feedback-max-rounds 6 \
  --feedback-submission-gate

PYTHONPATH=src python -m minisweagent.run_locbench \
  --mode tools \
  --tools-prompt neutral \
  --method miniswe_tools__neutral__feedback_rule \
  --workers 4 \
  --skip-missing \
  --redo-existing \
  --feedback-loop \
  --feedback-mode rule \
  --feedback-every-n-steps 3 \
  --feedback-max-rounds 6 \
  --feedback-submission-gate
