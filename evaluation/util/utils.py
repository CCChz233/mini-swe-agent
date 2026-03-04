import json
from pathlib import Path
from typing import Any


def load_jsonl(path: Path | str) -> list[dict[str, Any]]:
    """Load JSONL file and return list of records."""
    if isinstance(path, str):
        path = Path(path)
    
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_num, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_num} of {path}") from exc
    return records
