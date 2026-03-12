# LocBench Official Evaluation Summary (Acc/Recall @ 1,5,10,15)

Official evaluator: `evaluation/eval_metric.py:evaluate_results()`

## Scope

- Benchmark: `LocBench V1` full benchmark (`data/Loc-Bench_V1_dataset.jsonl`).
- Source runs: current `locbench/outputs` snapshot on `2026-03-12`.
- Runs found: `58`; officially evaluable: `56`; officially evaluable full runs: `52`; smoke runs: `4`; unevaluable runs: `2`.
- Every included main-result row below is computed from the latest officially evaluable full run for that model-setting pair; each included run contains `560` evaluated trajectories.
- Main-paper settings: `Bash`, `Snippet Search`, `CodeNav`. Auxiliary variants are listed separately and should be treated as appendix-only.

See [report_scope_and_metric_definitions_20260312.md](/Users/chz/workspace/mini-swe-agent/evaluation/reports_k151015/_summary/report_scope_and_metric_definitions_20260312.md) for exact metric definitions and behavior-metric naming conventions.

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
- `Pass Rate`: run-level success statistic from `run_summary.json`; it is shown for context only.
- Why these metrics: they measure whether `CodeNav` improves localization quality beyond flat snippet-following, while staying comparable across file/module/function levels.

## Latest Full Runs (Function Level (Main Settings Only))

| Model | Setting | Run | Acc@1 | Acc@5 | Acc@10 | Acc@15 | Recall@1 | Recall@5 | Recall@10 | Recall@15 | Pass Rate |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| GPT-OSS-120B | Bash | 20260305_122240 | 28.93% | 26.43% | 26.96% | 26.96% | 22.11% | 30.77% | 31.50% | 31.59% | 78.75% |
| GPT-OSS-120B | Snippet Search | 20260305_125922 | 42.50% | 40.18% | 41.07% | 41.07% | 32.36% | 46.33% | 47.46% | 47.46% | 84.82% |
| GPT-OSS-120B | CodeNav | 20260309_212351 | 48.93% | 47.86% | 48.93% | 48.93% | 36.70% | 54.51% | 56.85% | 56.85% | 83.57% |
| Qwen2.5-72B-Instruct-GPTQ-Int4 | Bash | 20260305_185720 | 14.82% | 14.64% | 15.36% | 15.36% | 11.57% | 16.87% | 17.61% | 17.61% | 66.07% |
| Qwen2.5-72B-Instruct-GPTQ-Int4 | Snippet Search | 20260305_201631 | 17.32% | 15.18% | 15.89% | 15.89% | 12.52% | 18.29% | 19.39% | 19.39% | 76.79% |
| Qwen2.5-72B-Instruct-GPTQ-Int4 | CodeNav | 20260305_150343 | 24.64% | 25.89% | 29.64% | 29.64% | 17.36% | 30.73% | 34.34% | 34.34% | 78.93% |
| Qwen3-Coder-30B-A3B-Instruct | Bash | 20260306_025513 | 34.64% | 31.79% | 31.96% | 31.96% | 27.39% | 35.93% | 36.33% | 36.33% | 78.57% |
| Qwen3-Coder-30B-A3B-Instruct | Snippet Search | 20260306_043958 | 45.36% | 41.07% | 41.43% | 41.43% | 34.12% | 47.63% | 48.79% | 48.79% | 77.32% |
| Qwen3-Coder-30B-A3B-Instruct | CodeNav | 20260306_000149 | 51.43% | 52.32% | 53.57% | 53.57% | 39.48% | 59.43% | 60.74% | 60.74% | 80.89% |
| gemini-3-flash-preview | Bash | 20260311_030304 | 62.86% | 62.50% | 64.64% | 64.64% | 48.18% | 70.41% | 73.65% | 73.65% | 91.07% |
| gemini-3-flash-preview | Snippet Search | 20260311_050240 | 63.57% | 62.32% | 63.04% | 63.04% | 48.14% | 70.28% | 72.23% | 72.23% | 89.82% |
| gemini-3-flash-preview | CodeNav | 20260310_235113 | 68.57% | 68.93% | 71.25% | 71.25% | 51.97% | 76.66% | 79.26% | 79.26% | 91.07% |
| qwen3.5-plus | Bash | 20260223_225913 | 23.93% | 18.21% | 18.21% | 18.57% | 16.48% | 23.03% | 23.64% | 23.78% | 43.86% |

## Latest Full Runs (File Level (Main Settings Only))

| Model | Setting | Run | Acc@1 | Acc@5 | Acc@10 | Acc@15 | Recall@1 | Recall@5 | Recall@10 | Recall@15 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| GPT-OSS-120B | Bash | 20260305_122240 | 58.39% | 63.04% | 63.04% | 63.04% | 55.33% | 66.00% | 66.00% | 66.00% |
| GPT-OSS-120B | Snippet Search | 20260305_125922 | 73.39% | 76.43% | 76.43% | 76.43% | 69.05% | 80.29% | 80.38% | 80.38% |
| GPT-OSS-120B | CodeNav | 20260309_212351 | 74.46% | 74.82% | 74.82% | 74.82% | 69.26% | 78.73% | 78.79% | 78.79% |
| Qwen2.5-72B-Instruct-GPTQ-Int4 | Bash | 20260305_185720 | 41.79% | 46.79% | 46.79% | 46.79% | 39.82% | 48.57% | 48.57% | 48.57% |
| Qwen2.5-72B-Instruct-GPTQ-Int4 | Snippet Search | 20260305_201631 | 65.54% | 67.14% | 67.50% | 67.50% | 61.02% | 70.47% | 70.82% | 70.82% |
| Qwen2.5-72B-Instruct-GPTQ-Int4 | CodeNav | 20260305_150343 | 66.96% | 68.57% | 68.57% | 68.57% | 62.24% | 72.35% | 72.35% | 72.35% |
| Qwen3-Coder-30B-A3B-Instruct | Bash | 20260306_025513 | 54.29% | 56.07% | 56.07% | 56.07% | 50.94% | 58.87% | 58.87% | 58.87% |
| Qwen3-Coder-30B-A3B-Instruct | Snippet Search | 20260306_043958 | 66.79% | 67.14% | 67.14% | 67.14% | 62.40% | 70.56% | 70.65% | 70.65% |
| Qwen3-Coder-30B-A3B-Instruct | CodeNav | 20260306_000149 | 67.86% | 70.18% | 70.18% | 70.18% | 63.64% | 73.28% | 73.28% | 73.28% |
| gemini-3-flash-preview | Bash | 20260311_030304 | 80.89% | 83.57% | 83.75% | 83.75% | 75.35% | 87.43% | 87.61% | 87.61% |
| gemini-3-flash-preview | Snippet Search | 20260311_050240 | 81.61% | 82.32% | 82.32% | 82.32% | 75.93% | 86.12% | 86.12% | 86.12% |
| gemini-3-flash-preview | CodeNav | 20260310_235113 | 81.96% | 83.04% | 83.21% | 83.21% | 76.42% | 86.91% | 87.00% | 87.00% |
| qwen3.5-plus | Bash | 20260223_225913 | 50.18% | 47.14% | 47.32% | 47.32% | 45.14% | 50.78% | 50.87% | 50.87% |

## Latest Full Runs (Module Level (Main Settings Only))

| Model | Setting | Run | Acc@1 | Acc@5 | Acc@10 | Acc@15 | Recall@1 | Recall@5 | Recall@10 | Recall@15 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| GPT-OSS-120B | Bash | 20260305_122240 | 36.43% | 34.46% | 34.82% | 34.82% | 30.82% | 38.27% | 38.74% | 38.83% |
| GPT-OSS-120B | Snippet Search | 20260305_125922 | 46.79% | 45.71% | 46.61% | 46.61% | 38.59% | 51.17% | 52.03% | 52.03% |
| GPT-OSS-120B | CodeNav | 20260309_212351 | 57.14% | 54.64% | 55.00% | 55.00% | 47.52% | 60.46% | 61.59% | 61.59% |
| Qwen2.5-72B-Instruct-GPTQ-Int4 | Bash | 20260305_185720 | 20.89% | 20.00% | 20.71% | 20.71% | 17.96% | 22.34% | 23.02% | 23.02% |
| Qwen2.5-72B-Instruct-GPTQ-Int4 | Snippet Search | 20260305_201631 | 20.71% | 20.18% | 21.25% | 21.25% | 16.28% | 23.23% | 24.62% | 24.62% |
| Qwen2.5-72B-Instruct-GPTQ-Int4 | CodeNav | 20260305_150343 | 29.82% | 30.00% | 33.21% | 33.21% | 23.41% | 34.31% | 38.09% | 38.09% |
| Qwen3-Coder-30B-A3B-Instruct | Bash | 20260306_025513 | 38.75% | 37.32% | 37.14% | 37.14% | 33.14% | 40.75% | 40.92% | 40.92% |
| Qwen3-Coder-30B-A3B-Instruct | Snippet Search | 20260306_043958 | 50.36% | 47.50% | 48.04% | 48.04% | 41.89% | 53.21% | 53.99% | 53.99% |
| Qwen3-Coder-30B-A3B-Instruct | CodeNav | 20260306_000149 | 58.75% | 58.57% | 58.93% | 58.93% | 49.92% | 64.50% | 64.98% | 64.98% |
| gemini-3-flash-preview | Bash | 20260311_030304 | 70.36% | 70.89% | 71.96% | 71.96% | 59.67% | 77.31% | 78.68% | 78.68% |
| gemini-3-flash-preview | Snippet Search | 20260311_050240 | 70.89% | 70.18% | 70.18% | 70.18% | 59.53% | 76.54% | 77.12% | 77.12% |
| gemini-3-flash-preview | CodeNav | 20260310_235113 | 75.36% | 75.18% | 76.25% | 76.25% | 63.83% | 81.40% | 82.52% | 82.52% |
| qwen3.5-plus | Bash | 20260223_225913 | 26.43% | 21.61% | 21.61% | 21.79% | 19.43% | 25.86% | 26.26% | 26.32% |

## Appendix Variants

These variants should be reported as ablations or appendix-only behavior studies, not as the main result line.

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

