from pathlib import Path

from minisweagent.tools.file_radar_search.tool import FileRadarSearchTool


def _write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _build_tool(tmp_path: Path, **overrides) -> FileRadarSearchTool:
    config = {
        "embedding_provider": "local",
        "embedding_model": "dummy-embedder",
        "embedding_device": "cpu",
        "index_root": str(tmp_path / "indexes"),
        "chunker": "sliding",
        "chunk_size": 800,
        "overlap": 200,
        "aggregation": "hybrid",
        "index_validation_mode": "static",
        "index_build_policy": "read_only",
    }
    config.update(overrides)
    return FileRadarSearchTool(config)


def test_auto_skeleton_top3_compact_output(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_file(
        repo / "src" / "auth.py",
        (
            "import os\n"
            "from typing import Any\n\n"
            "class AuthService:\n"
            "    \"\"\"Authenticate user tokens for API requests.\"\"\"\n"
            "    def login(self, user: str) -> bool:\n"
            "        \"\"\"Login with token-aware credential check.\"\"\"\n"
            "        return bool(user)\n\n"
            "def helper(token: str) -> bool:\n"
            "    \"\"\"Validate whether a token uses x-prefix.\"\"\"\n"
            "    return token.startswith('x')\n"
        ),
    )
    _write_file(
        repo / "src" / "token_cache.py",
        (
            "import time\n\n"
            "class TokenCache:\n"
            "    def load(self) -> dict:\n"
            "        return {}\n"
        ),
    )
    _write_file(
        repo / "src" / "middleware.py",
        (
            "from .auth import AuthService\n\n"
            "def require_auth() -> None:\n"
            "    pass\n"
        ),
    )

    tool = _build_tool(
        tmp_path,
        auto_skeleton_enabled=True,
        auto_skeleton_topn=3,
        auto_skeleton_budget_chars=3500,
        auto_skeleton_max_imports_per_file=0,
    )
    candidates = [
        {"path": "src/auth.py", "score": 0.93, "evidence_count": 8},
        {"path": "src/token_cache.py", "score": 0.82, "evidence_count": 5},
        {"path": "src/middleware.py", "score": 0.75, "evidence_count": 4},
    ]

    auto = tool._build_auto_skeleton(query="auth token login", repo_root=repo, results=candidates)
    assert auto["enabled"] is True
    assert auto["topn"] == 3
    assert len(auto["files"]) == 3
    assert auto["files"][0]["path"] == "src/auth.py"
    assert "AuthService" in auto["files"][0]["anchors_preview"]
    assert auto["files"][0]["folded_symbols_count"] >= 0

    output = tool._format_results("auth token login", candidates, auto_skeleton=auto)
    assert "Auto skeleton (Top-3, balanced folded, no code body):" in output
    assert "🎯 Anchors:" in output
    assert "🧭 Context Glimpse:" in output
    assert "📦 Folded:" in output
    assert "➡ Next:" in output
    assert "💡 Next-Step Playbook:" in output
    assert "Anchor First" in output
    assert "Expand When Needed" in output
    assert "Re-query If Needed" in output
    assert "Validate whether a token uses x-prefix." in output
    assert "return bool(user)" not in output


def test_auto_skeleton_without_omission_keeps_truncation_false(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_file(
        repo / "src" / "dense.py",
        (
            "class AuthService:\n"
            "    def build_payload(self):\n"
            "        return 1\n\n"
            "def compute_context():\n"
            "    return 2\n"
        ),
    )

    tool = _build_tool(
        tmp_path,
        auto_skeleton_enabled=True,
        auto_skeleton_topn=1,
        auto_skeleton_budget_chars=120,
        auto_skeleton_max_imports_per_file=0,
        auto_skeleton_max_symbols_per_file=20,
    )
    candidates = [{"path": "src/dense.py", "score": 0.99, "evidence_count": 12}]

    auto = tool._build_auto_skeleton(query="auth payload context", repo_root=repo, results=candidates)
    assert auto["enabled"] is True
    assert len(auto["files"]) == 1
    assert auto["truncated"] is False
    file_item = auto["files"][0]
    assert file_item["folded_imports_count"] >= 0
    assert file_item["folded_symbols_count"] >= 0

    output = tool._format_results("auth payload context", candidates, auto_skeleton=auto)
    assert "truncated:" not in output


def test_tree_v2_output_renders_directory_edges_and_coverage_candidates(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_file(
        repo / "backend" / "chainlit" / "config.py",
        (
            "OAUTH_ENABLED = True\n"
            "CLIENT_ID = 'demo'\n"
        ),
    )
    _write_file(
        repo / "backend" / "chainlit" / "server.py",
        (
            "from backend.chainlit.config import CLIENT_ID\n\n"
            "def validate_token(token: str) -> bool:\n"
            "    return token.startswith('x')\n\n"
            "def oauth_callback(token: str) -> bool:\n"
            "    return validate_token(token)\n\n"
            "def init_app() -> None:\n"
            "    oauth_callback('x')\n"
        ),
    )

    tool = _build_tool(
        tmp_path,
        auto_skeleton_enabled=True,
        auto_skeleton_topn=3,
        auto_skeleton_budget_chars=3500,
        auto_skeleton_max_imports_per_file=0,
        auto_skeleton_max_symbols_per_file=14,
        radar_output_style="tree_v2",
        coverage_candidates_topn=4,
    )
    candidates = [
        {"path": "backend/chainlit/config.py", "score": 0.91, "evidence_count": 1},
        {"path": "backend/chainlit/server.py", "score": 0.88, "evidence_count": 35},
    ]
    auto = tool._build_auto_skeleton(query="oauth callback auth init", repo_root=repo, results=candidates)
    assert auto["enabled"] is True
    assert len(auto["files"]) == 2
    server_item = next(item for item in auto["files"] if item["path"] == "backend/chainlit/server.py")
    assert 1 <= len(server_item["coverage_candidates"]) <= 4

    output = tool._format_results("oauth callback auth init", candidates, auto_skeleton=auto)
    assert "[DIR] backend/chainlit/" in output
    assert "[FILE] backend/chainlit/config.py (evidence: 1)" in output
    assert "imports-by <- backend/chainlit/server.py (evidence: 0.88)" in output
    assert output.count("[ANCHORS]") == 1
    assert "`backend/chainlit/server.py:oauth_callback` ::" in output
    assert "invokes -> validate_token | invokes-by <- init_app" in output
    assert "[COVERAGE_CANDIDATES] (Top suspects based on AST & calls):" in output
    assert "`backend/chainlit/server.py:oauth_callback`" in output
    assert "- <none>" not in output
    assert "└── -" not in output
    assert "strictly run `@tool list_symbols` to harvest siblings before submitting." in output


def test_auto_skeleton_truncation_flag_reflects_symbol_cap(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_file(
        repo / "src" / "service.py",
        (
            "def alpha() -> int:\n"
            "    return 1\n\n"
            "def beta() -> int:\n"
            "    return alpha()\n\n"
            "def gamma() -> int:\n"
            "    return beta()\n"
        ),
    )

    tool = _build_tool(
        tmp_path,
        auto_skeleton_enabled=True,
        auto_skeleton_topn=1,
        auto_skeleton_budget_chars=3500,
        auto_skeleton_max_imports_per_file=0,
        auto_skeleton_max_symbols_per_file=1,
    )
    candidates = [{"path": "src/service.py", "score": 0.99, "evidence_count": 7}]

    auto = tool._build_auto_skeleton(query="alpha beta gamma", repo_root=repo, results=candidates)
    assert auto["truncated"] is True
    assert len(auto["files"]) == 1
    assert auto["files"][0]["truncated"] is True


def test_auto_skeleton_truncation_flag_reflects_import_cap(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_file(
        repo / "src" / "imports_dense.py",
        (
            "import alpha_module\n"
            "import beta_module\n"
            "import gamma_module\n\n"
            "def run() -> int:\n"
            "    return 1\n"
        ),
    )
    tool = _build_tool(
        tmp_path,
        auto_skeleton_enabled=True,
        auto_skeleton_topn=1,
        auto_skeleton_budget_chars=3500,
        auto_skeleton_max_imports_per_file=1,
        auto_skeleton_max_symbols_per_file=20,
    )
    candidates = [{"path": "src/imports_dense.py", "score": 0.55, "evidence_count": 2}]
    auto = tool._build_auto_skeleton(query="run imports", repo_root=repo, results=candidates)
    assert auto["truncated"] is True
    assert auto["files"][0]["truncated"] is True


def test_auto_skeleton_truncation_flag_reflects_candidate_omission(tmp_path: Path):
    repo = tmp_path / "repo"
    _write_file(repo / "src" / "a.py", "def alpha():\n    return 1\n")
    _write_file(repo / "src" / "b.py", "def beta():\n    return 1\n")
    _write_file(repo / "src" / "c.py", "def gamma():\n    return 1\n")
    tool = _build_tool(
        tmp_path,
        auto_skeleton_enabled=True,
        auto_skeleton_topn=1,
        auto_skeleton_budget_chars=3500,
        auto_skeleton_max_imports_per_file=0,
        auto_skeleton_max_symbols_per_file=20,
    )
    candidates = [
        {"path": "src/a.py", "score": 0.91, "evidence_count": 9},
        {"path": "src/b.py", "score": 0.88, "evidence_count": 8},
        {"path": "src/c.py", "score": 0.77, "evidence_count": 7},
    ]
    auto = tool._build_auto_skeleton(query="alpha beta gamma", repo_root=repo, results=candidates)
    assert auto["truncated"] is True
    assert len(auto["files"]) == 1


def test_auto_skeleton_truncation_flag_reflects_preview_string_cutoff(tmp_path: Path):
    repo = tmp_path / "repo"
    long_name = "auth_" + ("verylongsegment_" * 12) + "handler"
    _write_file(
        repo / "src" / "long_preview.py",
        (
            f"def {long_name}() -> int:\n"
            "    return 1\n"
        ),
    )
    tool = _build_tool(
        tmp_path,
        auto_skeleton_enabled=True,
        auto_skeleton_topn=1,
        auto_skeleton_budget_chars=3500,
        auto_skeleton_max_imports_per_file=0,
        auto_skeleton_max_symbols_per_file=20,
    )
    candidates = [{"path": "src/long_preview.py", "score": 0.66, "evidence_count": 3}]
    auto = tool._build_auto_skeleton(query="auth handler", repo_root=repo, results=candidates)
    assert auto["truncated"] is True
    assert auto["files"][0]["truncated"] is True
