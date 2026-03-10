#!/usr/bin/env python3

"""Run mini-SWE-agent on SWE-QA-Bench with tool support."""

from __future__ import annotations

import concurrent.futures
import copy
import random
import shlex
import subprocess
import threading
import time
from pathlib import Path
from typing import Any

import yaml
from jinja2 import StrictUndefined, Template
from rich.live import Live

from minisweagent.agents.tool_agent import (
    ExecutionTimeoutError,
    FormatError,
    LimitsExceeded,
    Submitted,
    ToolAgent,
    ToolExecutionError,
    ToolFormatError,
)
from minisweagent.config import get_config_path
from minisweagent.environments import get_environment
from minisweagent.environments.repo_mounts import build_repo_mount_args
from minisweagent.models import get_model
from minisweagent.run.extra.utils.batch_progress import RunBatchProgressManager
from minisweagent.run.extra.utils.run_summary import write_run_summary
from minisweagent.run.utils.save import save_traj
from minisweagent.swe_qa_bench.utils import (
    FileReadTracker,
    TrackingToolRegistry,
    append_jsonl,
    build_answer_stats,
    extract_json_payload,
    load_jsonl,
    merge_relative_code_list,
    validate_output_model_name,
)
from minisweagent.tools.code_search import CodeSearchTool
from minisweagent.tools.file_radar_search import FileRadarSearchTool
from minisweagent.tools.list_symbols import ListSymbolsTool
from minisweagent.tools.registry import ToolRegistryError
from minisweagent.utils.log import add_file_handler, logger

_OUTPUT_FILE_LOCK = threading.Lock()


def _get_last_assistant_content(agent: ToolAgent | None) -> str:
    if agent is None:
        return ""
    for message in reversed(agent.messages):
        if message.get("role") == "assistant":
            return message.get("content", "") or ""
    return ""


class ProgressTrackingToolAgent(ToolAgent):
    def __init__(
        self,
        *args,
        progress_manager: RunBatchProgressManager,
        instance_id: str = "",
        enforce_tool_verification: bool = False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.progress_manager = progress_manager
        self.instance_id = instance_id
        self.enforce_tool_verification = enforce_tool_verification
        self.needs_verification = False
        self.candidate_files: set[str] = set()
        self.verified_files: set[str] = set()
        self.inspected_files: set[str] = set()
        self.radar_called_count = 0
        self.radar_tool_output_chars = 0
        self.list_symbols_called_count = 0
        self.blocked_submission_count = 0
        self.radar_index_status_counts: dict[str, int] = {}
        self.radar_last_index_status: str | None = None
        self.radar_last_index_reason: str | None = None
        self.radar_last_index_dir: str | None = None

    def step(self) -> dict:
        tokens = getattr(self.model, "total_tokens", 0)
        self.progress_manager.update_instance_status(
            self.instance_id, f"Step {self.model.n_calls + 1:3d} ({tokens} toks)"
        )
        return super().step()

    def _candidate_preview_lines(self) -> str:
        candidates = sorted(self.candidate_files)
        preview = candidates[:5]
        lines = "\n".join(f"- {path}" for path in preview) if preview else "- <none recorded>"
        if len(candidates) > len(preview):
            lines += f"\n- ... ({len(candidates) - len(preview)} more)"
        return lines

    def _verification_interception_message(self) -> str:
        return (
            "SYSTEM_INTERCEPTION: Verification Required.\n"
            "You invoked file_radar_search, but have not inspected any returned candidate file with bash.\n"
            "This is not a JSON formatting error.\n"
            "Before submitting the final answer, inspect at least one candidate file via bash.\n"
            "Allowed commands: rg, grep, sed, cat, nl, head, tail.\n"
            "Examples: `rg -n \"symbol\" path/to/candidate.py` or `sed -n '1,80p' path/to/candidate.py`.\n"
            "Candidate files from radar:\n"
            f"{self._candidate_preview_lines()}"
        )

    def _verification_final_prompt_message(self) -> str:
        target = sorted(self.candidate_files)[0] if self.candidate_files else "path/to/candidate.py"
        target_q = shlex.quote(target)
        return (
            "FINAL STEP OVERRIDE: Verification is still required before submission.\n"
            "This message supersedes the normal final-answer instruction.\n"
            "You must run exactly ONE bash command that BOTH:\n"
            "1) Reads at least one candidate file from file_radar_search\n"
            "2) Prints the final output marker and JSON payload\n"
            "Use a pattern like:\n"
            f"`sed -n '1,80p' {target_q} >/dev/null && "
            "printf 'MINI_SWE_AGENT_FINAL_OUTPUT\\n{\"answer\":\"...\"}\\n'`\n"
            "Candidate files from radar:\n"
            f"{self._candidate_preview_lines()}"
        )

    def query(self) -> dict:
        if (
            self.config.step_limit > 0
            and self.model.n_calls == self.config.step_limit - 1
            and self.config.final_prompt_template
            and not self._final_prompt_injected
        ):
            if self.enforce_tool_verification and self.needs_verification:
                self.add_message("user", self._verification_final_prompt_message())
            else:
                self.add_message("user", self.render_template(self.config.final_prompt_template))
            self._final_prompt_injected = True
        if 0 < self.config.step_limit <= self.model.n_calls or 0 < self.config.cost_limit <= self.model.cost:
            raise LimitsExceeded()
        response = self.model.query(self.messages)
        self.add_message("assistant", **response)
        return response

    def execute_tool(self, action: dict) -> dict:
        try:
            context = dict(self.extra_template_vars)
            if self.candidate_files:
                context["allowed_files"] = sorted(self.candidate_files)
            result = self.tool_registry.execute(action["raw"], context=context)
        except ToolRegistryError as exc:
            available = self.tool_registry.available_tools()
            raise ToolFormatError(
                self.render_template(
                    self.config.tool_format_error_template,
                    command=action["raw"],
                    available_tools=available,
                )
            ) from exc
        if not result.success:
            raise ToolExecutionError(
                self.render_template(
                    self.config.tool_error_template,
                    tool_name=action["raw"].split()[1] if action["raw"].split() else "unknown",
                    error=result.error or result.output,
                )
            )

        command = action.get("raw", "")
        if command.startswith("@tool file_radar_search"):
            self.radar_called_count += 1
            self.radar_tool_output_chars += len(result.output or "")
            if isinstance(result.data, dict):
                index_status = str(result.data.get("index_status") or "").strip()
                if index_status:
                    self.radar_index_status_counts[index_status] = (
                        self.radar_index_status_counts.get(index_status, 0) + 1
                    )
                    self.radar_last_index_status = index_status
                index_reason = str(result.data.get("index_compat_reason") or "").strip()
                if index_reason:
                    self.radar_last_index_reason = index_reason
                index_dir = str(result.data.get("index_dir") or "").strip()
                if index_dir:
                    self.radar_last_index_dir = index_dir
            candidates: set[str] = set()
            for item in result.data.get("results", []) if isinstance(result.data, dict) else []:
                path = item.get("path")
                if isinstance(path, str) and path.strip():
                    candidates.add(path.strip())
            self.candidate_files = candidates
            self.verified_files = set()
            self.inspected_files = set()
            self.needs_verification = self.enforce_tool_verification and bool(candidates)
        elif command.startswith("@tool list_symbols"):
            self.list_symbols_called_count += 1

        return {
            "type": "tool",
            "output": result.output,
            "returncode": result.returncode,
            "action": action["raw"],
            "data": result.data,
        }

    def _refresh_verification_state(self) -> None:
        tracker: FileReadTracker | None = getattr(self, "_file_tracker", None)
        if tracker is None:
            return
        self.inspected_files = set(tracker.paths)
        self.verified_files = self.candidate_files & self.inspected_files
        if self.verified_files:
            self.needs_verification = False

    def execute_bash(self, action: dict) -> dict:
        try:
            output = self.env.execute(action["command"])
        except (TimeoutError, subprocess.TimeoutExpired) as exc:
            timeout_output = exc.output.decode("utf-8", errors="replace") if getattr(exc, "output", None) else ""
            raise ExecutionTimeoutError(
                self.render_template(self.config.timeout_template, action=action, output=timeout_output)
            ) from exc

        tracker: FileReadTracker | None = getattr(self, "_file_tracker", None)
        if tracker is not None:
            tracker.ingest(action.get("command", ""), output.get("output", ""))
            self._refresh_verification_state()
        self.has_finished(output)
        return output | {"type": "bash", "action": action["command"]}

    def has_finished(self, output: dict[str, str]):
        lines = output.get("output", "").lstrip().splitlines(keepends=True)
        if not lines:
            return
        marker = lines[0].strip()
        if marker not in {"MINI_SWE_AGENT_FINAL_OUTPUT", "COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"}:
            return
        if self.enforce_tool_verification and self.needs_verification:
            self.blocked_submission_count += 1
            raise FormatError(self._verification_interception_message())
        raise Submitted("".join(lines[1:]))


class ToolsRunner:
    def __init__(
        self,
        *,
        dataset_root: Path,
        repos_root: Path,
        output_root: Path,
        repos: list[str],
        slice_spec: str,
        shuffle: bool,
        shuffle_seed: int,
        workers: int,
        config_path: Path,
        tool_config_path: Path,
        model: str | None,
        model_class: str | None,
        environment_class: str | None,
        image: str | None,
        output_model_name: str,
        method: str,
        run_id: str,
        output_dir: str,
        redo_existing: bool,
        indexes_root: str | None,
        model_root: str | None,
        tools_prompt: str,
        tool_backend: str,
        enforce_tool_verification: bool,
        pricing: dict[str, Any] | None,
        billing: dict[str, Any] | None,
    ) -> None:
        self.dataset_root = dataset_root
        self.repos_root = repos_root
        self.output_root = output_root
        self.repos = repos
        self.slice_spec = slice_spec
        self.shuffle = shuffle
        self.shuffle_seed = shuffle_seed
        self.workers = workers
        self.config_path = config_path
        self.tool_config_path = tool_config_path
        self.model = model
        self.model_class = model_class
        self.environment_class = environment_class
        self.image = image
        self.output_model_name = output_model_name
        self.method = method
        self.run_id = run_id
        self.output_dir = output_dir
        self.redo_existing = redo_existing
        self.indexes_root = indexes_root
        self.model_root = model_root
        self.tools_prompt = tools_prompt
        self.tool_backend = tool_backend
        self.enforce_tool_verification = enforce_tool_verification
        self.pricing = pricing
        self.billing = billing

    def run(self) -> None:
        run_tools(
            dataset_root=self.dataset_root,
            repos_root=self.repos_root,
            output_root=self.output_root,
            repos=",".join(self.repos),
            slice_spec=self.slice_spec,
            shuffle=self.shuffle,
            shuffle_seed=self.shuffle_seed,
            workers=self.workers,
            config_path=self.config_path,
            tool_config_path=self.tool_config_path,
            model=self.model,
            model_class=self.model_class,
            environment_class=self.environment_class,
            image=self.image,
            output_model_name=self.output_model_name,
            method=self.method,
            run_id=self.run_id,
            output_dir=self.output_dir,
            redo_existing=self.redo_existing,
            indexes_root=self.indexes_root,
            model_root=self.model_root,
            tools_prompt=self.tools_prompt,
            tool_backend=self.tool_backend,
            enforce_tool_verification=self.enforce_tool_verification,
            pricing=self.pricing,
            billing=self.billing,
        )


def _collect_repos(questions_dir: Path, repos_csv: str) -> list[str]:
    if repos_csv:
        return [item.strip() for item in repos_csv.split(",") if item.strip()]
    return sorted(path.stem for path in questions_dir.glob("*.jsonl"))


def _load_existing_questions(path: Path) -> set[str]:
    if not path.exists():
        return set()
    questions = set()
    for record in load_jsonl(path):
        question = record.get("question")
        if question:
            questions.add(question)
    return questions


def _build_instances(
    questions_dir: Path,
    repos_root: Path,
    repos: list[str],
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    missing_question_files: list[str] = []
    missing_repos: list[str] = []
    instances: list[dict[str, Any]] = []
    for repo in repos:
        question_path = questions_dir / f"{repo}.jsonl"
        repo_path = repos_root / repo
        if not question_path.exists():
            missing_question_files.append(repo)
            continue
        if not repo_path.exists():
            missing_repos.append(repo)
            continue
        records = load_jsonl(question_path)
        for idx, record in enumerate(records):
            question = (record.get("question") or "").strip()
            if not question:
                continue
            instance_id = f"{repo}-{idx}"
            instance = {
                "instance_id": instance_id,
                "repo": repo,
                "repo_dir": repo,
                "repo_path": str(repo_path.resolve()),
                "repo_mount_path": f"/repos/{repo}",
                "workdir": f"/repos/{repo}",
                "workdir_q": shlex.quote(f"/repos/{repo}"),
                "question": question,
                "question_index": idx,
                "base_commit": "HEAD",
            }
            instances.append(instance)
    return instances, missing_question_files, missing_repos


def _filter_instances(
    instances: list[dict[str, Any]],
    *,
    slice_spec: str,
    shuffle: bool,
    shuffle_seed: int,
) -> list[dict[str, Any]]:
    if shuffle:
        instances = sorted(instances.copy(), key=lambda x: x["instance_id"])
        random.seed(shuffle_seed)
        random.shuffle(instances)
    if slice_spec:
        values = [int(x) if x else None for x in slice_spec.split(":")]
        instances = instances[slice(*values)]
    return instances


def _default_output_dir(output_root: Path, output_model_name: str, method: str, run_id: str | None) -> Path:
    stamp = run_id or time.strftime("%Y%m%d_%H%M%S")
    return output_root / "outputs" / output_model_name / method / stamp


def _get_answer_path(output_root: Path, output_model_name: str, method: str, run_id: str, repo: str) -> Path:
    return output_root / "answers" / output_model_name / method / run_id / f"{repo}.jsonl"


def _get_environment(config: dict[str, Any], instance: dict[str, Any], repos_root: Path):
    env_config = copy.deepcopy(config.get("environment", {}))
    env_config["environment_class"] = env_config.get("environment_class", "docker")
    repo_mount_mode = env_config.pop("repo_mount_mode", "single")
    if env_config["environment_class"] != "docker":
        raise ValueError("SWE-QA-Bench runner supports docker only.")

    image = env_config.get("image")
    if image is None:
        raise ValueError("Docker image must be set for SWE-QA-Bench.")
    env_config["image"] = image

    env_config["run_args"] = build_repo_mount_args(
        run_args=env_config.get("run_args", ["--rm"]),
        repo_mount_mode=repo_mount_mode,
        repo_root=repos_root,
        repo_source_path=Path(instance["repo_path"]),
        repo_mount_path=instance["repo_mount_path"],
    )

    env = get_environment(env_config)
    if startup_command := config.get("run", {}).get("env_startup_command"):
        startup_command = Template(startup_command, undefined=StrictUndefined).render(**instance)
        out = env.execute(startup_command)
        if out["returncode"] != 0:
            raise RuntimeError(f"Error executing startup command: {out}")
    if instance.get("workdir"):
        env.config.cwd = instance["workdir"]
    return env


def _cleanup_environment(env: Any) -> None:
    if env is None:
        return
    if hasattr(env, "stop"):
        env.stop()
    elif hasattr(env, "cleanup"):
        env.cleanup()


def _run_teardown_command(env: Any, config: dict[str, Any], instance: dict[str, Any]) -> None:
    if env is None:
        return
    teardown_command = config.get("run", {}).get("env_teardown_command")
    if not teardown_command:
        return
    try:
        rendered = Template(teardown_command, undefined=StrictUndefined).render(**instance)
        out = env.execute(rendered)
        if out.get("returncode", 0) != 0:
            logger.warning("Teardown command failed for %s: %s", instance.get("instance_id"), out)
    except Exception as exc:
        logger.warning("Teardown command error for %s: %s", instance.get("instance_id"), exc)


def _parse_answer(result: str) -> str:
    payload, _ = extract_json_payload(result)
    if payload and isinstance(payload.get("answer"), str):
        return payload.get("answer", "").strip()
    return result.strip()


def _append_answer_record(path: Path, record: dict[str, Any]) -> None:
    with _OUTPUT_FILE_LOCK:
        append_jsonl(path, record)


def process_instance(
    instance: dict[str, Any],
    output_dir: Path,
    config: dict[str, Any],
    tools: list[Any],
    progress_manager: RunBatchProgressManager,
    dataset_root: Path,
    output_root: Path,
    output_model_name: str,
    method: str,
    run_id: str,
    repos_root: Path,
    tools_prompt: str,
    tool_backend: str,
    enforce_tool_verification: bool,
    summary_sink: list[dict[str, Any]],
    summary_lock: threading.Lock,
) -> None:
    instance_id = instance["instance_id"]
    trajectories_dir = output_dir / "trajectories"
    trajectories_dir.mkdir(parents=True, exist_ok=True)
    traj_path = trajectories_dir / f"{instance_id}.traj.json"
    traj_path.unlink(missing_ok=True)

    model = get_model(config=config.get("model", {}))
    question = instance["question"]
    answer_path = _get_answer_path(output_root, output_model_name, method, run_id, instance["repo"])

    progress_manager.on_instance_start(instance_id)
    progress_manager.update_instance_status(instance_id, "Starting container")

    agent = None
    env = None
    exit_status = "Unknown"
    result = ""

    tracker = FileReadTracker(
        repo_path=Path(instance["repo_path"]),
        repo_mount_path=instance["repo_mount_path"],
        workdir=instance["workdir"],
    )

    tool_registry = TrackingToolRegistry(
        repo_path=Path(instance["repo_path"]),
        repo_mount_path=instance["repo_mount_path"],
        workdir=instance["workdir"],
    )
    for tool in tools:
        tool_registry.register(tool)

    try:
        env = _get_environment(config, instance, repos_root)
        agent = ProgressTrackingToolAgent(
            model=model,
            env=env,
            tool_registry=tool_registry,
            progress_manager=progress_manager,
            instance_id=instance_id,
            enforce_tool_verification=enforce_tool_verification,
            **config.get("agent", {}),
        )
        agent._file_tracker = tracker
        exit_status, result = agent.run(
            task=question,
            repo=instance["repo"],
            repo_dir=instance["repo_dir"],
            repo_path=instance["repo_path"],
            base_commit=instance.get("base_commit", "HEAD"),
            workdir=instance["workdir"],
            repo_mount_path=instance["repo_mount_path"],
        )
        if exit_status == "LimitsExceeded":
            fallback_text = _get_last_assistant_content(agent)
            if fallback_text:
                result = fallback_text
    except Exception as exc:
        exit_status = f"{type(exc).__name__}"
        result = str(exc)
        logger.error(f"Error processing {instance_id}: {exc}", exc_info=True)
    finally:
        _run_teardown_command(env, config, instance)
        _cleanup_environment(env)

    answer = _parse_answer(result) if exit_status in {"Submitted", "LimitsExceeded"} else ""
    relative_code_list = merge_relative_code_list(tool_registry.tool_candidates, tracker.paths)
    stats = build_answer_stats(model)
    billing_stats = model.get_billing_stats() if model and hasattr(model, "get_billing_stats") else {}
    radar_called = getattr(agent, "radar_called_count", 0) if agent else 0
    radar_tool_output_chars = getattr(agent, "radar_tool_output_chars", 0) if agent else 0
    list_symbols_called = getattr(agent, "list_symbols_called_count", 0) if agent else 0
    blocked_submission_count = getattr(agent, "blocked_submission_count", 0) if agent else 0
    verified_files = sorted(getattr(agent, "verified_files", set())) if agent else []
    candidate_files = sorted(getattr(agent, "candidate_files", set())) if agent else []
    verification_satisfied: bool | None = None
    if tool_backend == "file_radar_search" and agent and radar_called:
        verification_satisfied = bool(not getattr(agent, "needs_verification", False))

    record = {
        "question": question,
        "answer": answer,
        "final_answer": answer,
        "relative_code_list": relative_code_list,
        "stats": stats,
        "exit_status": exit_status,
        "steps": getattr(model, "n_calls", 0) if model else 0,
        "trace_tokens": billing_stats.get("trace_tokens", billing_stats.get("total_tokens", 0)),
        "billed_tokens": billing_stats.get("billed_tokens", billing_stats.get("total_tokens", 0)),
        "tools_prompt": tools_prompt,
    }
    if tool_backend == "file_radar_search":
        record["radar_called"] = bool(radar_called)
        record["radar_tool_calls"] = radar_called
        record["radar_tool_output_chars"] = radar_tool_output_chars
        record["blocked_submission_count"] = blocked_submission_count
        record["radar_candidate_files"] = candidate_files
        record["radar_verified_files"] = verified_files
        record["radar_verification_satisfied"] = verification_satisfied
        record["list_symbols_called"] = list_symbols_called
    _append_answer_record(answer_path, record)
    logger.info("Answer appended to: %s", answer_path)

    extra_info = {
        "repo": instance["repo"],
        "question": question,
        "relative_code_list": relative_code_list,
        "tool_candidates": tool_registry.tool_candidates,
    }
    save_traj(
        agent,
        traj_path,
        print_fct=logger.info,
        exit_status=exit_status,
        result=result,
        extra_info=extra_info,
    )
    summary_record = {
        "instance_id": instance_id,
        "exit_status": exit_status,
        "steps": getattr(model, "n_calls", 0) if model else 0,
        "trace_tokens": billing_stats.get("trace_tokens", billing_stats.get("total_tokens", 0)),
        "billed_tokens": billing_stats.get("billed_tokens", billing_stats.get("total_tokens", 0)),
        "cost_usd": billing_stats.get("cost_usd", getattr(model, "cost", 0.0)),
        "correct": None,
        "tools_prompt": tools_prompt,
    }
    if tool_backend == "file_radar_search":
        summary_record["radar_called"] = bool(radar_called)
        summary_record["radar_tool_calls"] = radar_called
        summary_record["radar_tool_output_chars"] = radar_tool_output_chars
        summary_record["blocked_submission_count"] = blocked_submission_count
        summary_record["radar_verification_satisfied"] = verification_satisfied
        summary_record["list_symbols_called"] = list_symbols_called
    with summary_lock:
        summary_sink.append(summary_record)

    progress_manager.on_instance_end(instance_id, exit_status)


def run_tools(
    dataset_root: Path,
    repos_root: Path,
    output_root: Path,
    repos: str,
    slice_spec: str,
    shuffle: bool,
    shuffle_seed: int,
    workers: int,
    config_path: Path,
    tool_config_path: Path,
    model: str | None,
    model_class: str | None,
    environment_class: str | None,
    image: str | None,
    output_model_name: str,
    method: str,
    run_id: str,
    output_dir: str,
    redo_existing: bool,
    indexes_root: str | None,
    model_root: str | None,
    tools_prompt: str,
    tool_backend: str,
    enforce_tool_verification: bool,
    pricing: dict[str, Any] | None,
    billing: dict[str, Any] | None,
) -> None:
    dataset_root = dataset_root.resolve()
    repos_root = repos_root.resolve()
    output_root = output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    if not dataset_root.exists():
        raise ValueError(f"Dataset root not found: {dataset_root}")
    if not repos_root.exists():
        raise ValueError(f"Repos root not found: {repos_root}")
    validate_output_model_name(output_model_name)

    config_path = get_config_path(config_path)
    logger.info(f"Loading agent config from '{config_path}'")
    config = yaml.safe_load(config_path.read_text())
    if environment_class is not None:
        config.setdefault("environment", {})["environment_class"] = environment_class
    if image is not None:
        config.setdefault("environment", {})["image"] = image
    if model is not None:
        config.setdefault("model", {})["model_name"] = model
    if model_class is not None:
        config.setdefault("model", {})["model_class"] = model_class
    if billing is not None:
        config.setdefault("model", {})["billing"] = billing

    tool_config_path = get_config_path(tool_config_path)
    tool_config = yaml.safe_load(tool_config_path.read_text())
    if indexes_root:
        tool_config["index_root"] = str(indexes_root)
    if model_root:
        tool_config["embedding_model"] = str(model_root)
    tools: list[Any]
    if tool_backend == "code_search":
        tools = [CodeSearchTool(tool_config)]
    elif tool_backend == "file_radar_search":
        max_file_size = int(tool_config.get("max_file_size", 512 * 1024))
        tools = [FileRadarSearchTool(tool_config), ListSymbolsTool({"max_file_size": max_file_size})]
    else:
        raise ValueError(f"Unsupported tool backend: {tool_backend}")

    default_output_dir = _default_output_dir(output_root, output_model_name, method, run_id)
    if output_dir:
        output_dir_path = Path(output_dir)
        if not output_dir_path.is_absolute():
            output_dir_path = output_root / output_dir_path
        elif output_root not in output_dir_path.parents and output_dir_path != output_root:
            logger.warning("output_dir outside run root; forcing under %s", output_root)
            output_dir_path = default_output_dir
    else:
        output_dir_path = default_output_dir
    output_dir_path.mkdir(parents=True, exist_ok=True)
    add_file_handler(output_dir_path / "minisweagent.log")
    logger.info(f"Results will be saved to {output_dir_path}")

    questions_dir = dataset_root / "questions"
    repo_list = _collect_repos(questions_dir, repos)
    instances, missing_questions, missing_repos = _build_instances(questions_dir, repos_root, repo_list)
    if missing_questions:
        missing_preview = ", ".join(missing_questions[:10])
        raise ValueError(f"Missing question files (first 10): {missing_preview}")
    if missing_repos:
        missing_preview = ", ".join(missing_repos[:10])
        raise ValueError(f"Missing repos (first 10): {missing_preview}")

    if not redo_existing:
        existing_by_repo = {
            repo: _load_existing_questions(_get_answer_path(output_root, output_model_name, method, run_id, repo))
            for repo in repo_list
        }
        instances = [
            inst for inst in instances if inst["question"] not in existing_by_repo.get(inst["repo"], set())
        ]

    instances = _filter_instances(
        instances,
        slice_spec=slice_spec,
        shuffle=shuffle,
        shuffle_seed=shuffle_seed,
    )
    logger.info(f"Running on {len(instances)} instances...")

    progress_manager = RunBatchProgressManager(len(instances), output_dir_path / f"exit_statuses_{time.time()}.yaml")
    instance_summaries: list[dict[str, Any]] = []
    summary_lock = threading.Lock()

    def process_futures(futures: dict[concurrent.futures.Future, str]):
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except concurrent.futures.CancelledError:
                pass
            except Exception as exc:
                instance_id = futures[future]
                logger.error(f"Error in future for instance {instance_id}: {exc}", exc_info=True)
                progress_manager.on_uncaught_exception(instance_id, exc)

    with Live(progress_manager.render_group, refresh_per_second=4):
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(
                    process_instance,
                    instance,
                    output_dir_path,
                    config,
                    tools,
                    progress_manager,
                    dataset_root,
                    output_root,
                    output_model_name,
                    method,
                    run_id,
                    repos_root,
                    tools_prompt,
                    tool_backend,
                    enforce_tool_verification,
                    instance_summaries,
                    summary_lock,
                ): instance["instance_id"]
                for instance in instances
            }
            process_futures(futures)

    progress_manager.print_report()
    write_run_summary(
        output_dir_path / "run_summary.json",
        meta={
            "benchmark": "swe_qa_bench",
            "model": model or config.get("model", {}).get("model_name"),
            "model_class": model_class or config.get("model", {}).get("model_class"),
            "method": method,
            "effective_method": method,
            "run_id": run_id,
            "tools_prompt": tools_prompt,
            "tool_backend": tool_backend,
            "enforce_tool_verification": enforce_tool_verification,
            "agent_config": str(config_path),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        },
        instance_summaries=instance_summaries,
        csv_path=output_dir_path / "run_summary.csv",
    )
