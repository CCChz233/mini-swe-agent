#!/usr/bin/env python3
"""SWE-QA-Bench scoring — faithful port of the original SWE-QA-Bench/score/main.py.

Changes from original:
  - Accepts CLI args instead of hardcoded paths / env vars.
  - Auto-discovers model/method/run_id from answers directory.
  - Auto-discovers repos from reference directory.
  - Uses raw HTTP requests instead of openai SDK (same payload).
Everything else (prompt, field handling, skip logic, output format) is identical.
"""

from __future__ import annotations

import argparse
import json
import os
import concurrent.futures
from pathlib import Path
from typing import Any, Optional

import requests


PROMPT_TEMPLATE = """You are a professional evaluator. Please rate the candidate answer against the reference answer based on five criteria.
    Evaluation Criteria and Scoring Guidelines (each scored 1 to 10):
        1. Correctness:
            10 — Completely correct; core points and details are accurate with no ambiguity.
            8-9 — Mostly correct; only minor details are slightly inaccurate or loosely expressed.
            6-7 — Partially correct; some errors or omissions, but main points are generally accurate.
            4-5 — Several errors or ambiguities that affect understanding of the core information.
            2-3 — Many errors; misleading or fails to convey key information.
            1 — Serious errors; completely wrong or misleading.
        2. Completeness:
            10 — Covers all key points from the reference answer without omission.
            8-9 — Covers most key points; only minor non-critical information missing.
            6-7 — Missing several key points; content is somewhat incomplete.
            4-5 — Important information largely missing; content is one-sided.
            2-3 — Covers very little relevant information; seriously incomplete.
            1 — Covers almost no relevant information; completely incomplete.
        3. Relevance:
            10 — Content fully focused on the question topic; no irrelevant information.
            8-9 — Mostly focused; only minor irrelevant or peripheral information.
            6-7 — Generally on topic; some off-topic content but still relevant overall.
            4-5 — Topic not sufficiently focused; contains considerable off-topic content.
            2-3 — Content deviates from topic; includes excessive irrelevant information.
            1 — Majority of content irrelevant to the question.
        4. Clarity:
            10 — Fluent language; clear and precise expression; very easy to understand.
            8-9 — Mostly fluent; clear expression with minor unclear points.
            6-7 — Generally clear; some expressions slightly unclear or not concise.
            4-5 — Expression somewhat awkward; some ambiguity or lack of fluency.
            2-3 — Language obscure; sentences are not smooth; hinders understanding.
            1 — Expression confusing; very difficult to understand.
        5. Reasoning:
            10 — Reasoning is clear, logical, and well-structured; argumentation is excellent.
            8-9 — Reasoning is clear and logical; well-structured with solid argumentation.
            6-7 — Reasoning generally reasonable; mostly clear logic; minor jumps.
            4-5 — Reasoning is average; some logical jumps or organization issues.
            2-3 — Reasoning unclear; lacks logical order; difficult to follow.
            1 — No clear reasoning; logic is chaotic.

INPUT:
    Question:{question}
    Reference Answer:{reference}
    Candidate Answer:{candidate}

OUTPUT:
    Please output ONLY a JSON object with 5 integer fields in the range [1,10], corresponding
    to the evaluation scores:
        {{
        "correctness": <1-10>,
        "completeness": <1-10>,
        "relevance": <1-10>,
        "clarity": <1-10>,
        "reasoning": <1-10>
        }}

REQUIREMENT:
    No explanation, no extra text, no formatting other than valid JSON"""


def _resolve_api_url(base: str) -> str:
    base = base.strip().rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    return base + "/chat/completions"


def score_answer(
    question: str,
    reference: str,
    candidate: str,
    *,
    api_url: str,
    api_key: str,
    model: str,
    timeout: int,
) -> dict[str, int] | None:
    """Identical to original score_answer: sends prompt, parses 5-dim JSON scores."""
    prompt = PROMPT_TEMPLATE.format(question=question, reference=reference, candidate=candidate)
    try:
        resp = requests.post(
            api_url,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=timeout,
        )
        resp.raise_for_status()
        score_str = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
    except Exception as e:
        print(f"Scoring error: {e}")
        return None

    try:
        if score_str.startswith("```json"):
            score_str = score_str[7:]
        if score_str.startswith("```"):
            score_str = score_str[3:]
        if score_str.endswith("```"):
            score_str = score_str[:-3]
        score_str = score_str.strip()
        scores = json.loads(score_str)
        for key in ["correctness", "completeness", "clarity", "relevance", "reasoning"]:
            if key not in scores or not (0 <= scores[key] <= 10):
                print(f"Score validation failed: {key} = {scores.get(key)}")
                return None
        return scores
    except Exception as e:
        print(f"JSON parsing failed: {e}")
        return None


def process_single_record(
    candidate_record: dict[str, Any],
    reference_dict: dict[str, str],
    *,
    api_url: str,
    api_key: str,
    model: str,
    timeout: int,
) -> Optional[dict[str, Any]]:
    """Identical to original process_single_record: only reads 'final_answer', skips 'No answer found'."""
    question = candidate_record.get("question", "")
    candidate_answer = candidate_record.get("final_answer", "")
    reference = reference_dict.get(question, "")

    if not reference:
        print("Skipping record: Missing reference answer")
        return None
    if not candidate_answer or candidate_answer.strip() == "No answer found":
        print("Skipping record: Candidate answer is empty or 'No answer found'")
        return None

    scores = score_answer(question, reference, candidate_answer, api_url=api_url, api_key=api_key, model=model, timeout=timeout)
    if scores is None:
        print("Skipping record: Scoring failed")
        return None

    result = {
        "question": question,
        "candidate_answer": candidate_answer,
        "reference": reference,
        "correctness": scores["correctness"],
        "completeness": scores["completeness"],
        "clarity": scores["clarity"],
        "relevance": scores["relevance"],
        "reasoning": scores["reasoning"],
        "total_score": sum(scores.values()),
    }
    print(f"Scored question: {question[:50]}... - Sub-scores: {scores} - Total: {sum(scores.values())}")
    return result


def evaluate_jsonl_parallel(
    candidate_jsonl_path: Path,
    reference_jsonl_path: Path,
    output_jsonl_path: Path,
    *,
    api_url: str,
    api_key: str,
    model: str,
    timeout: int,
    max_workers: int = 16,
) -> None:
    """Identical to original evaluate_jsonl_parallel: only reads 'aggregated_answer' for reference."""
    reference_dict: dict[str, str] = {}
    for line in reference_jsonl_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
            question = record.get("question", "")
            answer = record.get("aggregated_answer", "") or record.get("answer", "")
            if question and answer:
                reference_dict[question] = answer
        except Exception as e:
            print(f"[Skip] Invalid reference answer JSON line: {e}")

    print(f"Read {len(reference_dict)} reference answers")

    candidate_records: list[dict[str, Any]] = []
    for line in candidate_jsonl_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            candidate_records.append(json.loads(line))
        except Exception as e:
            print(f"[Skip] Invalid candidate answer JSON line: {e}")

    print(f"Total read {len(candidate_records)} candidate answer records, starting parallel processing...")

    results: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_record = {
            executor.submit(
                process_single_record, record, reference_dict,
                api_url=api_url, api_key=api_key, model=model, timeout=timeout,
            ): record
            for record in candidate_records
        }
        for future in concurrent.futures.as_completed(future_to_record):
            try:
                result = future.result()
                if result is not None:
                    results.append(result)
            except Exception as e:
                print(f"Error processing record: {e}")

    print(f"Scoring completed, processed {len(results)} records, preparing to write results...")

    output_jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with output_jsonl_path.open("w", encoding="utf-8") as fout:
        for result in results:
            fout.write(json.dumps(result, ensure_ascii=False) + "\n")

    print(f"Results saved to: {output_jsonl_path}")


def _iter_answer_sets(answers_root: Path) -> list[tuple[str, str, str]]:
    """Discover all model/method/run_id combinations under answers_root."""
    pairs: list[tuple[str, str, str]] = []
    for model_dir in sorted(answers_root.iterdir()):
        if not model_dir.is_dir():
            continue
        for method_dir in sorted(model_dir.iterdir()):
            if not method_dir.is_dir():
                continue
            for run_dir in sorted(method_dir.iterdir()):
                if run_dir.is_dir() and any(run_dir.glob("*.jsonl")):
                    pairs.append((model_dir.name, method_dir.name, run_dir.name))
    return pairs


def main() -> None:
    parser = argparse.ArgumentParser(description="Score SWE-QA answers with original scoring logic.")
    parser.add_argument("--dataset-root", required=True, help="Path to SWE-QA-Bench/datasets")
    parser.add_argument("--answers-root", required=True, help="Path to answers directory")
    parser.add_argument("--output-root", help="Path to output scores (default: sibling 'scores' dir of answers)")
    parser.add_argument("--judge-model", required=True, help="Judge model name")
    parser.add_argument("--judge-api-base", required=True, help="Judge API base URL")
    parser.add_argument("--judge-api-key", required=True, help="Judge API key")
    parser.add_argument("--max-workers", type=int, default=16, help="Parallel workers (default: 16)")
    parser.add_argument("--timeout", type=int, default=60, help="API timeout in seconds (default: 60)")
    parser.add_argument("--model-filter", default="", help="Only score this model (optional)")
    parser.add_argument("--method-filter", default="", help="Only score this method (optional)")
    args = parser.parse_args()

    dataset_root = Path(args.dataset_root).resolve()
    answers_root = Path(args.answers_root).resolve()
    reference_dir = dataset_root / "reference"

    if args.output_root:
        output_root = Path(args.output_root).resolve()
    else:
        output_root = answers_root.parent / "scores_original"

    api_url = _resolve_api_url(args.judge_api_base)
    repos = sorted(p.stem for p in reference_dir.glob("*.jsonl"))
    pairs = _iter_answer_sets(answers_root)

    if not pairs:
        print(f"No answer sets found under {answers_root}")
        return

    print(f"Found {len(pairs)} answer set(s), {len(repos)} reference repos")

    for candidate_model, method, run_id in pairs:
        if args.model_filter and candidate_model != args.model_filter:
            continue
        if args.method_filter and method != args.method_filter:
            continue

        print(f"\n{'='*60}")
        print(f"Scoring: {candidate_model} / {method} / {run_id}")
        print(f"{'='*60}")

        for repo in repos:
            candidate_path = answers_root / candidate_model / method / run_id / f"{repo}.jsonl"
            reference_path = reference_dir / f"{repo}.jsonl"
            output_path = output_root / candidate_model / method / run_id / f"{repo}.jsonl"

            if not candidate_path.exists():
                print(f"Skipping {repo}: candidate file does not exist")
                continue
            if not reference_path.exists():
                print(f"Skipping {repo}: reference file does not exist")
                continue
            if output_path.exists():
                print(f"Skipping {repo}: output already exists ({output_path})")
                continue

            print(f"\nStarting to process {repo}...")
            evaluate_jsonl_parallel(
                candidate_path, reference_path, output_path,
                api_url=api_url, api_key=args.judge_api_key, model=args.judge_model,
                timeout=args.timeout, max_workers=args.max_workers,
            )
            print(f"Completed processing {repo}")


if __name__ == "__main__":
    main()
