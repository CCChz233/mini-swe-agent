# LocBench Official Evaluation Summary (2026-03-12)

Official evaluator: `evaluation/eval_metric.py:evaluate_results()`

## Scope

- Benchmark: `LocBench V1` full benchmark (`data/Loc-Bench_V1_dataset.jsonl`).
- Source runs: current `locbench/outputs` snapshot on `2026-03-12`.
- Runs found: `58`; officially evaluable: `56`; officially evaluable full runs: `52`; smoke runs: `4`; unevaluable runs: `2`; excluded orphan historical reports: `1`.
- Main tables below use only the main-paper settings: `Bash`, `Snippet Search`, and `CodeNav`.
- `Legacy Navigation`, prompt variants, and `Oracle Sniper` are treated as appendix-only variants and are listed separately.

See [report_scope_and_metric_definitions_20260312.md](/Users/chz/workspace/mini-swe-agent/evaluation/reports/_summary/report_scope_and_metric_definitions_20260312.md) for exact metric definitions and setting mapping.

## Main Table Scope

| Model | Setting | Method | Run | Evaluated Trajectories | Benchmark Scope |
|---|---|---|---|---:|---|
| GPT-OSS-120B | Bash | miniswe_bash | 20260305_122240 | 560 | LocBench V1 full benchmark |
| GPT-OSS-120B | Snippet Search | miniswe_tools | 20260305_125922 | 560 | LocBench V1 full benchmark |
| GPT-OSS-120B | CodeNav | codenav_tree | 20260309_212351 | 560 | LocBench V1 full benchmark |
| Qwen2.5-72B-Instruct-GPTQ-Int4 | Bash | miniswe_bash | 20260305_185720 | 560 | LocBench V1 full benchmark |
| Qwen2.5-72B-Instruct-GPTQ-Int4 | Snippet Search | miniswe_tools | 20260305_201631 | 560 | LocBench V1 full benchmark |
| Qwen2.5-72B-Instruct-GPTQ-Int4 | CodeNav | miniswe_tools_codenav | 20260305_150343 | 560 | LocBench V1 full benchmark |
| Qwen3-Coder-30B-A3B-Instruct | Bash | miniswe_bash | 20260306_025513 | 560 | LocBench V1 full benchmark |
| Qwen3-Coder-30B-A3B-Instruct | Snippet Search | miniswe_tools | 20260306_043958 | 560 | LocBench V1 full benchmark |
| Qwen3-Coder-30B-A3B-Instruct | CodeNav | miniswe_tools_codenav | 20260306_000149 | 560 | LocBench V1 full benchmark |
| gemini-3-flash-preview | Bash | miniswe_bash | 20260311_030304 | 560 | LocBench V1 full benchmark |
| gemini-3-flash-preview | Snippet Search | miniswe_tools | 20260311_050240 | 560 | LocBench V1 full benchmark |
| gemini-3-flash-preview | CodeNav | miniswe_tools_codenav | 20260310_235113 | 560 | LocBench V1 full benchmark |
| qwen3.5-plus | Bash | miniswe_bash | 20260223_225913 | 560 | LocBench V1 full benchmark |

## Metric Notes

- `Acc@k`: proportion of tasks where all `min(|GT|, k)` relevant items are recovered within top-`k` predictions at the given granularity.
- `Recall@k`: mean fraction of ground-truth items recovered within top-`k` predictions at the given granularity.
- `Pass Rate`: run-level success statistic from `run_summary.json`; reported for context and not part of the official evaluator itself.
- Best-run ranking rule in this file: `function Acc@5`, then `function Recall@10`, then `module Acc@5`, then `file Acc@1`, then latest `run_id`.

## Best Full Runs By Model And Main Setting

| Model | Setting | Method | Run | Func Acc@5 | Func Recall@10 | Module Acc@5 | File Acc@1 | Pass Rate |
|---|---|---|---|---:|---:|---:|---:|---:|
| GPT-OSS-120B | Bash | miniswe_bash | 20260305_122240 | 26.43% | 31.50% | 34.46% | 58.39% | 78.75% |
| GPT-OSS-120B | Snippet Search | miniswe_tools | 20260305_125922 | 40.18% | 47.46% | 45.71% | 73.39% | 84.82% |
| GPT-OSS-120B | CodeNav | codenav_tree | 20260309_212351 | 47.86% | 56.85% | 54.64% | 74.46% | 83.57% |
| Qwen2.5-72B-Instruct-GPTQ-Int4 | Bash | miniswe_bash | 20260305_185720 | 14.64% | 17.61% | 20.00% | 41.79% | 66.07% |
| Qwen2.5-72B-Instruct-GPTQ-Int4 | Snippet Search | miniswe_tools | 20260305_201631 | 15.18% | 19.39% | 20.18% | 65.54% | 76.79% |
| Qwen2.5-72B-Instruct-GPTQ-Int4 | CodeNav | miniswe_tools_codenav | 20260305_150343 | 25.89% | 34.34% | 30.00% | 66.96% | 78.93% |
| Qwen3-Coder-30B-A3B-Instruct | Bash | miniswe_bash | 20260306_025513 | 31.79% | 36.33% | 37.32% | 54.29% | 78.57% |
| Qwen3-Coder-30B-A3B-Instruct | Snippet Search | miniswe_tools | 20260306_043958 | 41.07% | 48.79% | 47.50% | 66.79% | 77.32% |
| Qwen3-Coder-30B-A3B-Instruct | CodeNav | miniswe_tools_codenav | 20260306_000149 | 52.32% | 60.74% | 58.57% | 67.86% | 80.89% |
| gemini-3-flash-preview | Bash | miniswe_bash | 20260311_030304 | 62.50% | 73.65% | 70.89% | 80.89% | 91.07% |
| gemini-3-flash-preview | Snippet Search | miniswe_tools | 20260311_050240 | 62.32% | 72.23% | 70.18% | 81.61% | 89.82% |
| gemini-3-flash-preview | CodeNav | miniswe_tools_codenav | 20260310_235113 | 68.93% | 79.26% | 75.18% | 81.96% | 91.07% |
| qwen3.5-plus | Bash | miniswe_bash | 20260223_225913 | 18.21% | 23.64% | 21.61% | 50.18% | 43.86% |

## Latest Full Runs By Model And Main Setting

| Model | Setting | Method | Run | Func Acc@5 | Func Recall@10 | Module Acc@5 | File Acc@1 | Pass Rate |
|---|---|---|---|---:|---:|---:|---:|---:|
| GPT-OSS-120B | Bash | miniswe_bash | 20260305_122240 | 26.43% | 31.50% | 34.46% | 58.39% | 78.75% |
| GPT-OSS-120B | Snippet Search | miniswe_tools | 20260305_125922 | 40.18% | 47.46% | 45.71% | 73.39% | 84.82% |
| GPT-OSS-120B | CodeNav | codenav_tree | 20260309_212351 | 47.86% | 56.85% | 54.64% | 74.46% | 83.57% |
| Qwen2.5-72B-Instruct-GPTQ-Int4 | Bash | miniswe_bash | 20260305_185720 | 14.64% | 17.61% | 20.00% | 41.79% | 66.07% |
| Qwen2.5-72B-Instruct-GPTQ-Int4 | Snippet Search | miniswe_tools | 20260305_201631 | 15.18% | 19.39% | 20.18% | 65.54% | 76.79% |
| Qwen2.5-72B-Instruct-GPTQ-Int4 | CodeNav | miniswe_tools_codenav | 20260305_150343 | 25.89% | 34.34% | 30.00% | 66.96% | 78.93% |
| Qwen3-Coder-30B-A3B-Instruct | Bash | miniswe_bash | 20260306_025513 | 31.79% | 36.33% | 37.32% | 54.29% | 78.57% |
| Qwen3-Coder-30B-A3B-Instruct | Snippet Search | miniswe_tools | 20260306_043958 | 41.07% | 48.79% | 47.50% | 66.79% | 77.32% |
| Qwen3-Coder-30B-A3B-Instruct | CodeNav | miniswe_tools_codenav | 20260306_000149 | 52.32% | 60.74% | 58.57% | 67.86% | 80.89% |
| gemini-3-flash-preview | Bash | miniswe_bash | 20260311_030304 | 62.50% | 73.65% | 70.89% | 80.89% | 91.07% |
| gemini-3-flash-preview | Snippet Search | miniswe_tools | 20260311_050240 | 62.32% | 72.23% | 70.18% | 81.61% | 89.82% |
| gemini-3-flash-preview | CodeNav | miniswe_tools_codenav | 20260310_235113 | 68.93% | 79.26% | 75.18% | 81.96% | 91.07% |
| qwen3.5-plus | Bash | miniswe_bash | 20260223_225913 | 18.21% | 23.64% | 21.61% | 50.18% | 43.86% |

## Latest A/B Snapshot (Main Settings Only)

| Model | Setting | Run | Func Acc@5 | Func Recall@10 | Module Acc@5 | File Acc@1 | Pass Rate |
|---|---|---|---:|---:|---:|---:|---:|
| GPT-OSS-120B | Bash | 20260305_122240 | 26.43% | 31.50% | 34.46% | 58.39% | 78.75% |
| GPT-OSS-120B | Snippet Search | 20260305_125922 | 40.18% | 47.46% | 45.71% | 73.39% | 84.82% |
| GPT-OSS-120B | CodeNav | 20260309_212351 | 47.86% | 56.85% | 54.64% | 74.46% | 83.57% |
| Qwen2.5-72B-Instruct-GPTQ-Int4 | Bash | 20260305_185720 | 14.64% | 17.61% | 20.00% | 41.79% | 66.07% |
| Qwen2.5-72B-Instruct-GPTQ-Int4 | Snippet Search | 20260305_201631 | 15.18% | 19.39% | 20.18% | 65.54% | 76.79% |
| Qwen2.5-72B-Instruct-GPTQ-Int4 | CodeNav | 20260305_150343 | 25.89% | 34.34% | 30.00% | 66.96% | 78.93% |
| Qwen3-Coder-30B-A3B-Instruct | Bash | 20260306_025513 | 31.79% | 36.33% | 37.32% | 54.29% | 78.57% |
| Qwen3-Coder-30B-A3B-Instruct | Snippet Search | 20260306_043958 | 41.07% | 48.79% | 47.50% | 66.79% | 77.32% |
| Qwen3-Coder-30B-A3B-Instruct | CodeNav | 20260306_000149 | 52.32% | 60.74% | 58.57% | 67.86% | 80.89% |
| gemini-3-flash-preview | Bash | 20260311_030304 | 62.50% | 73.65% | 70.89% | 80.89% | 91.07% |
| gemini-3-flash-preview | Snippet Search | 20260311_050240 | 62.32% | 72.23% | 70.18% | 81.61% | 89.82% |
| gemini-3-flash-preview | CodeNav | 20260310_235113 | 68.93% | 79.26% | 75.18% | 81.96% | 91.07% |
| qwen3.5-plus | Bash | 20260223_225913 | 18.21% | 23.64% | 21.61% | 50.18% | 43.86% |

## Appendix Variants

These runs are real experiments, but they should not be mixed into the main-result narrative without explicit explanation.

| Model | Variant Group | Display Label | Raw Method | Run | Records | Notes |
|---|---|---|---|---|---:|---|
| GPT-OSS-120B | oracle_sniper | miniswe_tools_oracle_sniper__smoke__feedback_rule__oracle_sniper | miniswe_tools_oracle_sniper__smoke__feedback_rule__oracle_sniper | 20260303_164249 | 560 | Oracle-only upper-bound/debug setting; appendix only. |
| GPT-OSS-120B | oracle_sniper | miniswe_tools_oracle_sniper__smoke__oracle_sniper | miniswe_tools_oracle_sniper__smoke__oracle_sniper | 20260226_121956 | 560 | Oracle-only upper-bound/debug setting; appendix only. |
| GPT-OSS-120B | oracle_sniper | miniswe_tools_oracle_sniper__smoke__oracle_sniper | miniswe_tools_oracle_sniper__smoke__oracle_sniper | 20260302_112906 | 560 | Oracle-only upper-bound/debug setting; appendix only. |
| GPT-OSS-120B | oracle_sniper | miniswe_tools_oracle_sniper__smoke__oracle_sniper | miniswe_tools_oracle_sniper__smoke__oracle_sniper | 20260302_151500 | 560 | Oracle-only upper-bound/debug setting; appendix only. |
| GPT-OSS-120B | oracle_sniper | miniswe_tools_oracle_sniper__smoke__oracle_sniper | miniswe_tools_oracle_sniper__smoke__oracle_sniper | 20260302_215647 | 560 | Oracle-only upper-bound/debug setting; appendix only. |
| GPT-OSS-120B | legacy_navigation | miniswe_tools_codenav | miniswe_tools_radar | 20260226_125920 | 560 | Earlier navigation stack; keep in appendix/ablation, not main result tables. |
| GPT-OSS-120B | legacy_navigation | miniswe_tools_codenav | miniswe_tools_radar | 20260227_002241 | 560 | Earlier navigation stack; keep in appendix/ablation, not main result tables. |
| GPT-OSS-120B | legacy_navigation | miniswe_tools_codenav | miniswe_tools_radar | 20260227_163827 | 560 | Earlier navigation stack; keep in appendix/ablation, not main result tables. |
| GPT-OSS-120B | legacy_navigation | miniswe_tools_codenav | miniswe_tools_radar | 20260228_120111 | 560 | Earlier navigation stack; keep in appendix/ablation, not main result tables. |
| GPT-OSS-120B | legacy_navigation | miniswe_tools_codenav | miniswe_tools_radar | 20260228_162756 | 560 | Earlier navigation stack; keep in appendix/ablation, not main result tables. |
| GPT-OSS-120B | legacy_navigation | miniswe_tools_codenav | miniswe_tools_radar | 20260301_142941 | 560 | Earlier navigation stack; keep in appendix/ablation, not main result tables. |
| GPT-OSS-120B | legacy_navigation | miniswe_tools_codenav | miniswe_tools_radar | 20260301_202919 | 560 | Earlier navigation stack; keep in appendix/ablation, not main result tables. |
| GPT-OSS-120B | legacy_navigation | miniswe_tools_codenav | miniswe_tools_radar | 20260301_230028 | 560 | Earlier navigation stack; keep in appendix/ablation, not main result tables. |
| GPT-OSS-120B | legacy_navigation | miniswe_tools_codenav | miniswe_tools_radar | 20260302_155409 | 560 | Earlier navigation stack; keep in appendix/ablation, not main result tables. |
| GPT-OSS-120B | legacy_navigation | miniswe_tools_codenav | miniswe_tools_radar | 20260304_235901 | 560 | Earlier navigation stack; keep in appendix/ablation, not main result tables. |
| GPT-OSS-120B | legacy_navigation | miniswe_tools_codenav | miniswe_tools_radar | 20260305_110533 | 560 | Earlier navigation stack; keep in appendix/ablation, not main result tables. |
| GPT-OSS-120B | legacy_navigation | codenav_legacy | radar_legacy | 20260309_201142 | 560 | Earlier navigation stack; keep in appendix/ablation, not main result tables. |
| Qwen2.5-72B-Instruct-GPTQ-Int4 | legacy_navigation | miniswe_tools_codenav | miniswe_tools_radar | 20260224_100724 | 560 | Earlier navigation stack; keep in appendix/ablation, not main result tables. |
| Qwen2.5-72B-Instruct-GPTQ-Int4 | legacy_navigation | miniswe_tools_codenav | miniswe_tools_radar | 20260224_122729 | 560 | Earlier navigation stack; keep in appendix/ablation, not main result tables. |
| Qwen2.5-72B-Instruct-GPTQ-Int4 | legacy_navigation | miniswe_tools_codenav | miniswe_tools_radar | 20260305_150343 | 560 | Earlier navigation stack; keep in appendix/ablation, not main result tables. |
| Qwen2.5-72B-Instruct-GPTQ-Int4 | prompt_variant | miniswe_tools__search_fallback | miniswe_tools__search_fallback | 20260201_154727 | 560 | Prompt variant of Snippet Search; appendix only. |
| Qwen2.5-72B-Instruct-GPTQ-Int4 | prompt_variant | miniswe_tools__search_first | miniswe_tools__search_first | 20260201_142909 | 560 | Prompt variant of Snippet Search; appendix only. |
| Qwen3-Coder-30B-A3B-Instruct | oracle_sniper | miniswe_tools_oracle_sniper__smoke__oracle_sniper | miniswe_tools_oracle_sniper__smoke__oracle_sniper | 20260224_214232 | 1 | Oracle-only upper-bound/debug setting; appendix only. |
| Qwen3-Coder-30B-A3B-Instruct | oracle_sniper | miniswe_tools_oracle_sniper__smoke__oracle_sniper | miniswe_tools_oracle_sniper__smoke__oracle_sniper | 20260224_214306 | 1 | Oracle-only upper-bound/debug setting; appendix only. |
| Qwen3-Coder-30B-A3B-Instruct | oracle_sniper | miniswe_tools_oracle_sniper__smoke__oracle_sniper | miniswe_tools_oracle_sniper__smoke__oracle_sniper | 20260224_214333 | 2 | Oracle-only upper-bound/debug setting; appendix only. |
| Qwen3-Coder-30B-A3B-Instruct | oracle_sniper | miniswe_tools_oracle_sniper__smoke__oracle_sniper | miniswe_tools_oracle_sniper__smoke__oracle_sniper | 20260224_215650 | 560 | Oracle-only upper-bound/debug setting; appendix only. |
| Qwen3-Coder-30B-A3B-Instruct | legacy_navigation | miniswe_tools_codenav | miniswe_tools_radar | 20260223_162533 | 1 | Earlier navigation stack; keep in appendix/ablation, not main result tables. |
| Qwen3-Coder-30B-A3B-Instruct | legacy_navigation | miniswe_tools_codenav | miniswe_tools_radar | 20260223_170944 | 560 | Earlier navigation stack; keep in appendix/ablation, not main result tables. |
| Qwen3-Coder-30B-A3B-Instruct | legacy_navigation | miniswe_tools_codenav | miniswe_tools_radar | 20260224_154605 | 560 | Earlier navigation stack; keep in appendix/ablation, not main result tables. |
| Qwen3-Coder-30B-A3B-Instruct | legacy_navigation | miniswe_tools_codenav | miniswe_tools_radar | 20260306_000149 | 560 | Earlier navigation stack; keep in appendix/ablation, not main result tables. |

## Unevaluable Runs

| Model | Setting | Method | Run | Traj | Pass Rate |
|---|---|---|---|---:|---:|
| GPT-OSS-120B | Bash | miniswe_bash | 20260127_220416 | 0 | 57.32% |
| GPT-OSS-120B | Snippet Search | miniswe_tools | 20260127_224545 | 0 | 68.35% |

## Excluded Historical Reports

- `/Users/chz/workspace/mini-swe-agent/evaluation/reports/gemini-3-flash-preview/miniswe_tools_radar__tree_v2__20260310_235113.json`

