#!/bin/bash
# SWE-QA-Bench scoring using original scoring logic (faithful port).
# Scores are written to swe_qa_bench/results/scores_original/<model>/<method>/<run_id>/

cd /Users/chz/workspace/mini-swe-agent
python swe_qa_bench/score_original.py \
  --dataset-root /Users/chz/workspace/SWE-QA-Bench/SWE-QA-Bench/datasets \
  --answers-root /Users/chz/workspace/mini-swe-agent/swe_qa_bench/results/answers \
  --judge-model openai/gpt-5 \
  --judge-api-base https://api.commonstack.ai/v1 \
  --judge-api-key ak-ecc3fe95e3d59baf13263beda0cdc82ca4ff26cf5332a24bec121a8d126841e5 \
  --max-workers 8
