"""Minimal torch shim for the original evaluation code.

This keeps the evaluator logic unchanged while avoiding the heavyweight
PyTorch dependency for simple metric calculations.
"""

from __future__ import annotations

import numpy as np

float32 = np.float32


class Tensor(np.ndarray):
    def __new__(cls, data, dtype=None):
        return np.asarray(data, dtype=dtype).view(cls)

    def __array_finalize__(self, obj):
        del obj

    @property
    def device(self) -> str:
        return "cpu"

    def tile(self, reps) -> "Tensor":
        return Tensor(np.tile(np.asarray(self), reps))

    def sum(self, dim=None) -> "Tensor":
        return Tensor(np.sum(np.asarray(self), axis=dim))

    def mean(self, dim=None) -> "Tensor":
        return Tensor(np.mean(np.asarray(self), axis=dim))

    def nan_to_num_(self, nan=0.0, posinf=0.0, neginf=0.0) -> "Tensor":
        np.nan_to_num(self, copy=False, nan=nan, posinf=posinf, neginf=neginf)
        return self

    def item(self):
        return np.asarray(self).item()


def tensor(data, dtype=None) -> Tensor:
    return Tensor(data, dtype=dtype)


def arange(start, end=None, dtype=None, device=None) -> Tensor:
    del device
    if end is None:
        start, end = 0, start
    return Tensor(np.arange(start, end, dtype=dtype))


def log2(value) -> Tensor:
    return Tensor(np.log2(np.asarray(value)))
