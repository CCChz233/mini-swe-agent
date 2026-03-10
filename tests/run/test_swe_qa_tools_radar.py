import sys
from pathlib import Path

import pytest
import yaml

from minisweagent.agents.tool_agent import FormatError, Submitted
from minisweagent.environments.local import LocalEnvironment
from minisweagent.models.test_models import DeterministicModel
from minisweagent.run_swe_qa import main as run_swe_qa_main
from minisweagent.swe_qa_bench.run_from_yaml import main as run_from_yaml_main
from minisweagent.swe_qa_bench.runners.tools_runner import ProgressTrackingToolAgent
from minisweagent.swe_qa_bench.utils import FileReadTracker, TrackingToolRegistry
from minisweagent.tools.base import ToolResult
from minisweagent.tools.registry import ToolRegistry


class _NoopProgress:
    def update_instance_status(self, *_args, **_kwargs):
        return None


def _load_agent_config() -> dict:
    config_path = Path("swe_qa_bench/config/agent_tools_radar_neutral.yaml")
    with config_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)["agent"]


def _build_agent(repo_root: Path) -> ProgressTrackingToolAgent:
    agent = ProgressTrackingToolAgent(
        model=DeterministicModel(outputs=[]),
        env=LocalEnvironment(cwd=str(repo_root)),
        tool_registry=ToolRegistry(),
        progress_manager=_NoopProgress(),
        instance_id="sweqa-test",
        enforce_tool_verification=True,
        **_load_agent_config(),
    )
    agent._file_tracker = FileReadTracker(  # noqa: SLF001
        repo_path=repo_root,
        repo_mount_path=str(repo_root),
        workdir=str(repo_root),
    )
    return agent


def test_run_swe_qa_tools_radar_routes_to_file_radar_search(monkeypatch, tmp_path: Path):
    dataset_root = tmp_path / "dataset"
    (dataset_root / "questions").mkdir(parents=True)
    repos_root = tmp_path / "repos"
    repos_root.mkdir()
    indexes_root = tmp_path / "indexes"
    indexes_root.mkdir()
    model_root = tmp_path / "embedder"
    model_root.write_text("stub", encoding="utf-8")

    captured: dict[str, object] = {}

    class _StubRunner:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def run(self):
            captured["ran"] = True

    monkeypatch.setattr("minisweagent.run_swe_qa.runners.ToolsRunner", _StubRunner)

    run_swe_qa_main(
        [
            "--mode",
            "tools_radar",
            "--dataset-root",
            str(dataset_root),
            "--repos-root",
            str(repos_root),
            "--indexes-root",
            str(indexes_root),
            "--model-root",
            str(model_root),
            "--output-model-name",
            "test_model",
        ]
    )

    assert captured["ran"] is True
    assert captured["method"] == "miniswe_tools_radar"
    assert captured["tool_backend"] == "file_radar_search"
    assert captured["enforce_tool_verification"] is True
    assert captured["tools_prompt"] == "neutral"
    assert Path(str(captured["config_path"])).name == "agent_tools_radar_neutral.yaml"
    assert Path(str(captured["tool_config_path"])).name == "file_radar_search.yaml"


def test_run_swe_qa_tools_radar_rejects_non_neutral_prompt(tmp_path: Path):
    dataset_root = tmp_path / "dataset"
    (dataset_root / "questions").mkdir(parents=True)
    repos_root = tmp_path / "repos"
    repos_root.mkdir()
    indexes_root = tmp_path / "indexes"
    indexes_root.mkdir()
    model_root = tmp_path / "embedder"
    model_root.write_text("stub", encoding="utf-8")

    with pytest.raises(ValueError, match="tools_radar only supports tools_prompt=neutral"):
        run_swe_qa_main(
            [
                "--mode",
                "tools_radar",
                "--tools-prompt",
                "search_first",
                "--dataset-root",
                str(dataset_root),
                "--repos-root",
                str(repos_root),
                "--indexes-root",
                str(indexes_root),
                "--model-root",
                str(model_root),
                "--output-model-name",
                "test_model",
            ]
        )


def test_run_from_yaml_tools_radar_routes_to_file_radar_search(monkeypatch, tmp_path: Path):
    dataset_root = tmp_path / "dataset"
    repos_root = tmp_path / "repos"
    output_root = tmp_path / "results"
    indexes_root = tmp_path / "indexes"
    model_root = tmp_path / "embedder"
    for path in [dataset_root, repos_root, output_root, indexes_root]:
        path.mkdir(parents=True, exist_ok=True)
    model_root.write_text("stub", encoding="utf-8")

    config_path = tmp_path / "run.yaml"
    config_path.write_text(
        yaml.safe_dump(
            {
                "mode": "tools_radar",
                "dataset_root": str(dataset_root),
                "repos_root": str(repos_root),
                "output_root": str(output_root),
                "output_model_name": "test_model",
                "indexes_root": str(indexes_root),
                "model_root": str(model_root),
            }
        ),
        encoding="utf-8",
    )

    captured: dict[str, object] = {}

    class _StubRunner:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def run(self):
            captured["ran"] = True

    monkeypatch.setattr("minisweagent.swe_qa_bench.run_from_yaml.tools_runner.ToolsRunner", _StubRunner)
    monkeypatch.setattr(sys, "argv", ["run_from_yaml", "--config", str(config_path)])

    run_from_yaml_main()

    assert captured["ran"] is True
    assert captured["method"] == "miniswe_tools_radar"
    assert captured["tool_backend"] == "file_radar_search"
    assert captured["enforce_tool_verification"] is True
    assert captured["tools_prompt"] == "neutral"
    assert Path(str(captured["config_path"])).name == "agent_tools_radar_neutral.yaml"
    assert Path(str(captured["tool_config_path"])).name == "file_radar_search.yaml"


def test_tracking_tool_registry_records_file_radar_candidates(tmp_path: Path):
    repo_root = tmp_path / "repo"
    (repo_root / "pkg").mkdir(parents=True)
    (repo_root / "pkg" / "a.py").write_text("print('a')\n", encoding="utf-8")

    class _StubRadarTool:
        name = "file_radar_search"
        description = "stub"

        def run(self, _args: dict, _context: dict) -> ToolResult:
            return ToolResult(
                success=True,
                output="ok",
                data={"results": [{"path": "pkg/a.py", "score": 0.9, "evidence_count": 1}]},
                returncode=0,
            )

    registry = TrackingToolRegistry(
        repo_path=repo_root,
        repo_mount_path=str(repo_root),
        workdir=str(repo_root),
    )
    registry.register(_StubRadarTool())

    result = registry.execute("@tool file_radar_search --query answer", context={"repo_path": str(repo_root)})

    assert result.success is True
    assert registry.tool_candidates == ["pkg/a.py"]


def test_submission_requires_radar_candidate_bash_read(tmp_path: Path):
    repo_root = tmp_path / "repo"
    (repo_root / "pkg").mkdir(parents=True)
    (repo_root / "pkg" / "a.py").write_text("value = 1\n", encoding="utf-8")

    agent = _build_agent(repo_root)
    agent.candidate_files = {"pkg/a.py"}
    agent.needs_verification = True
    agent.radar_called_count = 1

    with pytest.raises(FormatError):
        agent.execute_bash({"command": "printf 'MINI_SWE_AGENT_FINAL_OUTPUT\\n{\"answer\":\"x\"}\\n'"})

    assert agent.blocked_submission_count == 1
    assert agent.verified_files == set()


def test_combined_read_and_submit_satisfies_radar_verification(tmp_path: Path):
    repo_root = tmp_path / "repo"
    (repo_root / "pkg").mkdir(parents=True)
    (repo_root / "pkg" / "a.py").write_text("value = 1\n", encoding="utf-8")

    agent = _build_agent(repo_root)
    agent.candidate_files = {"pkg/a.py"}
    agent.needs_verification = True
    agent.radar_called_count = 1

    with pytest.raises(Submitted) as exc_info:
        agent.execute_bash(
            {
                "command": (
                    "sed -n '1,5p' pkg/a.py >/dev/null && "
                    "printf 'MINI_SWE_AGENT_FINAL_OUTPUT\\n{\"answer\":\"done\"}\\n'"
                )
            }
        )

    assert str(exc_info.value).strip() == '{"answer":"done"}'
    assert agent.verified_files == {"pkg/a.py"}
    assert agent.needs_verification is False
