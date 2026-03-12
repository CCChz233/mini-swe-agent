# Report Scope, Setting Map, and Metric Definitions

## Statistical Scope

- Benchmark: `LocBench V1` from `data/Loc-Bench_V1_dataset.jsonl`.
- Source runs: the current snapshot of `locbench/outputs` as of `2026-03-12`.
- Official evaluator: `evaluation/eval_metric.py:evaluate_results()`.
- A run is `officially evaluable` if its trajectory reconstruction produces at least one `loc_output` record.
- A `full run` means `record_count >= 500`; in practice, every included main-result run in these summaries contains `560` evaluated trajectories.
- `Latest full run` means the latest officially evaluable full run for a given model-setting pair.
- `Best full run` means the best officially evaluable full run for a given model-setting pair under the ranking rule stated in each summary.

## Main Settings vs Appendix Variants

Main-paper settings:
- `Bash` -> raw method family `miniswe_bash`.
- `Snippet Search` -> raw method family `miniswe_tools`.
- `CodeNav` -> the final tree-based navigation setting. In raw outputs this appears as `miniswe_tools_codenav` or `radar_tree` and is normalized to `codenav` in presentation.

Appendix-only variants:
- `Legacy Navigation` -> older navigation experiments such as `miniswe_tools_radar` and `radar_legacy`.
- `Prompt Variants` -> `search_first` / `search_fallback` runs.
- `Oracle Sniper` -> oracle-only upper-bound or debugging setting.

Recommended reporting rule:
- Use only `Bash`, `Snippet Search`, and `CodeNav` in main-result tables.
- Move `Legacy Navigation`, `Prompt Variants`, and `Oracle Sniper` to appendix or ablation sections.

## Official Localization Metric Definitions

These summaries report the official evaluator exactly as implemented in `evaluation/eval_metric.py`.

- `File / Module / Function Recall@k`: for each task, the fraction of ground-truth items recovered within the top-`k` predicted items at the given granularity, averaged across tasks.
- `File / Module / Function Acc@k`: for each task, whether all `min(|GT|, k)` relevant items at the given granularity are recovered within the top-`k` predictions, averaged across tasks.
- `Pass Rate`: copied from the corresponding `run_summary.json`; this is a run-level success statistic, not part of the official evaluator itself.

## Behavioral Trajectory Metric Definitions

Use the following definitions consistently whenever reporting behavior tables.

- `SymbolBrowse%`: percentage of trajectories that call `list-symbols` at least once. It is a trajectory-level usage rate, not a share of actions.
- `Inspected Files`: average number of unique files inspected per trajectory.
- `Non-Top1 Explore%`: percentage of trajectories that inspect at least one retrieved candidate that is not rank-1.
- `Top1-First%`: percentage of trajectories whose first inspected retrieved file is the rank-1 retrieved candidate.
- `Cross-File Trans.`: average number of file-to-file transitions between consecutive file inspections within a trajectory.

## Why These Metrics

- Official localization metrics (`Acc@k`, `Recall@k`) quantify end-task localization quality.
- Behavioral metrics quantify whether `CodeNav` changes exploration from flat snippet-following toward more structured symbol-guided navigation.
- When using behavioral tables, always include the exact source run(s), the benchmark subset, and the number of trajectories used to compute each row.
