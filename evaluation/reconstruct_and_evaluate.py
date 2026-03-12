from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from eval_metric import evaluate_results


LEVEL2KEY = {
    "file": "found_files",
    "module": "found_modules",
    "function": "found_entities",
}


def parse_submission(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}

    text = raw.strip()
    candidates = [text]
    if text.startswith("{") and not text.endswith("}"):
        candidates.append(f"{text}}}")

    for candidate in candidates:
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    return {}


def normalize_function_name(name: str) -> str:
    if name.endswith(".__init__"):
        return name[: -len(".__init__")]
    return name


def build_loc_record(instance_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    if any(key in payload for key in LEVEL2KEY.values()):
        return {
            "instance_id": instance_id,
            "found_files": list(payload.get("found_files") or []),
            "found_modules": list(payload.get("found_modules") or []),
            "found_entities": list(payload.get("found_entities") or []),
        }

    found_files: list[str] = []
    found_modules: list[str] = []
    found_entities: list[str] = []
    seen_files: set[str] = set()
    seen_modules: set[str] = set()
    seen_entities: set[str] = set()

    for item in payload.get("functions") or []:
        if not isinstance(item, dict):
            continue
        function_name = item.get("function")
        file_hint = item.get("file_hint")
        if not function_name or not file_hint:
            continue

        normalized_name = normalize_function_name(str(function_name))
        file_hint = str(file_hint)
        module_name = normalized_name.split(".", 1)[0]
        entity_id = f"{file_hint}:{normalized_name}"
        module_id = f"{file_hint}:{module_name}"

        if file_hint not in seen_files:
            found_files.append(file_hint)
            seen_files.add(file_hint)
        if module_id not in seen_modules:
            found_modules.append(module_id)
            seen_modules.add(module_id)
        if entity_id not in seen_entities:
            found_entities.append(entity_id)
            seen_entities.add(entity_id)

    return {
        "instance_id": instance_id,
        "found_files": found_files,
        "found_modules": found_modules,
        "found_entities": found_entities,
    }


def reconstruct_loc_output(trajectory_dir: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(trajectory_dir.glob("*.traj.json")):
        trajectory = json.loads(path.read_text(encoding="utf-8"))
        instance_id = trajectory.get("instance_id") or path.name.removesuffix(".traj.json")
        submission = parse_submission((trajectory.get("info") or {}).get("submission"))
        records.append(build_loc_record(str(instance_id), submission))
    return records


def write_jsonl(records: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Reconstruct LocBench loc_output JSONL from trajectories and run official evaluation.")
    parser.add_argument("--trajectory-dir", required=True, help="Directory containing *.traj.json files")
    parser.add_argument("--dataset-path", required=True, help="LocBench dataset JSONL path")
    parser.add_argument("--output-jsonl", required=True, help="Where to write reconstructed loc_output JSONL")
    parser.add_argument("--metrics-json", required=True, help="Where to write evaluator metrics as JSON")
    args = parser.parse_args()

    trajectory_dir = Path(args.trajectory_dir).resolve()
    dataset_path = Path(args.dataset_path).resolve()
    output_jsonl = Path(args.output_jsonl).resolve()
    metrics_json = Path(args.metrics_json).resolve()

    records = reconstruct_loc_output(trajectory_dir)
    write_jsonl(records, output_jsonl)

    metrics = evaluate_results(
        loc_file=str(output_jsonl),
        level2key_dict=LEVEL2KEY,
        dataset_path=str(dataset_path),
    )
    metrics_json.parent.mkdir(parents=True, exist_ok=True)
    metrics_json.write_text(metrics.to_json(indent=2), encoding="utf-8")
    print(metrics.to_string())


if __name__ == "__main__":
    main()
