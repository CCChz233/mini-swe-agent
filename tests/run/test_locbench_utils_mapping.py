from pathlib import Path

from minisweagent.locbench.utils import map_functions_to_entities


def _write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_map_functions_to_entities_exact_file_hint_selects_single_match(tmp_path: Path) -> None:
    _write_file(tmp_path / "src" / "a" / "foo.py", "def process():\n    return 1\n")
    _write_file(tmp_path / "src" / "b" / "foo.py", "def process():\n    return 2\n")

    found_files, found_entities, _ = map_functions_to_entities(
        str(tmp_path),
        [{"function": "process", "file_hint": "src/a/foo.py"}],
        top_k=10,
    )

    assert found_files == ["src/a/foo.py"]
    assert found_entities == ["src/a/foo.py:process"]


def test_map_functions_to_entities_ambiguous_file_hint_keeps_multiple_matches(tmp_path: Path) -> None:
    _write_file(tmp_path / "src" / "a" / "foo.py", "def process():\n    return 1\n")
    _write_file(tmp_path / "src" / "b" / "foo.py", "def process():\n    return 2\n")
    _write_file(tmp_path / "src" / "c" / "bar.py", "def process():\n    return 3\n")

    found_files, found_entities, _ = map_functions_to_entities(
        str(tmp_path),
        [{"function": "process", "file_hint": "foo.py"}],
        top_k=10,
    )

    assert "src/a/foo.py" in found_files
    assert "src/b/foo.py" in found_files
    assert "src/c/bar.py" not in found_files
    assert "src/a/foo.py:process" in found_entities
    assert "src/b/foo.py:process" in found_entities
