"""Minimal datasets shim for local-file evaluation.

The original evaluator supports either a Hugging Face dataset or a local
JSONL file. We only use the local-file path in this repository workflow.
"""

from __future__ import annotations


def load_dataset(*args, **kwargs):
    del args, kwargs
    raise RuntimeError("Use dataset_path with the local evaluation workflow.")
