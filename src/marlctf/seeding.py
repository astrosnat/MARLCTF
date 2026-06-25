"""Deterministic seed utilities."""

from __future__ import annotations

import hashlib
import os
import random
from collections.abc import Iterable


def normalize_seed(seed: int | None) -> int:
    """Return a non-negative 32-bit seed."""

    if seed is None:
        return int.from_bytes(os.urandom(4), "big")
    if not isinstance(seed, int):
        raise TypeError("seed must be an int or None")
    return seed % (2**32)


def seed_everything(seed: int | None) -> int:
    """Seed available local RNG libraries and return the normalized seed."""

    normalized = normalize_seed(seed)
    random.seed(normalized)

    try:
        import numpy as np

        np.random.seed(normalized)
    except ImportError:
        pass

    try:
        import torch

        torch.manual_seed(normalized)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(normalized)
    except ImportError:
        pass

    return normalized


def derive_seed(base_seed: int, *parts: object) -> int:
    """Derive a stable 32-bit seed from a base seed and contextual parts."""

    digest = hashlib.blake2s(digest_size=4)
    digest.update(str(normalize_seed(base_seed)).encode("utf-8"))
    for part in parts:
        digest.update(b":")
        digest.update(str(part).encode("utf-8"))
    return int.from_bytes(digest.digest(), "big")


def make_run_id(run_type: str, scenario_id: str, seeds: Iterable[int]) -> str:
    """Create a stable, readable run id from core reproducibility fields."""

    seed_text = "-".join(str(normalize_seed(seed)) for seed in seeds)
    digest = hashlib.blake2s(f"{run_type}:{scenario_id}:{seed_text}".encode("utf-8"), digest_size=5)
    return f"{run_type}-{scenario_id}-{digest.hexdigest()}"
