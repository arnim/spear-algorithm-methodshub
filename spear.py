"""Small, dependency-light implementation of the SPEAR ranking algorithm.

SPEAR ranks users by expertise and resources/items by quality from a chronological
list of user-resource activities. It follows the formulation described by Noll et
al. (2009) and the reference examples at michael-noll.com/projects/spear-algorithm/.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

import numpy as np
import pandas as pd

CreditFunction = Callable[[np.ndarray], np.ndarray]


@dataclass(frozen=True)
class SpearResult:
    """Container for SPEAR scores and the weighted adjacency matrix."""

    expertise: pd.DataFrame
    quality: pd.DataFrame
    adjacency: pd.DataFrame


def sqrt_credit(x: np.ndarray) -> np.ndarray:
    """Default SPEAR credit scoring function, C(x)=sqrt(x)."""

    return np.sqrt(x)


def constant_credit(x: np.ndarray) -> np.ndarray:
    """Credit scoring function C(x)=1 for observed edges, similar to HITS."""

    return (x > 0).astype(float)


def build_adjacency(
    activities: pd.DataFrame,
    user_col: str = "user",
    resource_col: str = "resource",
    time_col: str = "timestamp",
    credit: CreditFunction = sqrt_credit,
) -> pd.DataFrame:
    """Create the SPEAR user-resource matrix from chronological activities.

    For every resource, earlier users receive more credit when later users also
    interact with the same resource. Activities are sorted by ``time_col`` before
    the matrix is constructed. Repeated user-resource pairs are counted only at
    their first occurrence.
    """

    required = {user_col, resource_col, time_col}
    missing = required.difference(activities.columns)
    if missing:
        raise ValueError(f"activities is missing required columns: {sorted(missing)}")

    ordered = activities.sort_values(time_col, kind="mergesort")
    users = list(dict.fromkeys(ordered[user_col].astype(str)))
    resources = list(dict.fromkeys(ordered[resource_col].astype(str)))
    user_index = {user: i for i, user in enumerate(users)}
    resource_index = {resource: j for j, resource in enumerate(resources)}

    weights = np.zeros((len(users), len(resources)), dtype=float)
    seen: set[tuple[str, str]] = set()

    for row in ordered.itertuples(index=False):
        user = str(getattr(row, user_col))
        resource = str(getattr(row, resource_col))
        pair = (user, resource)
        if pair in seen:
            continue
        seen.add(pair)
        j = resource_index[resource]
        previous = weights[:, j] > 0
        weights[previous, j] += 1.0
        weights[user_index[user], j] = 1.0

    return pd.DataFrame(credit(weights), index=users, columns=resources)


def _normalise(vector: np.ndarray) -> np.ndarray:
    total = vector.sum()
    if total == 0:
        return vector
    return vector / total


def run_spear(
    activities: pd.DataFrame,
    user_col: str = "user",
    resource_col: str = "resource",
    time_col: str = "timestamp",
    credit: CreditFunction = sqrt_credit,
    iterations: int = 20,
    tolerance: float = 1e-12,
) -> SpearResult:
    """Run SPEAR and return ranked expertise and quality scores."""

    adjacency = build_adjacency(activities, user_col, resource_col, time_col, credit)
    matrix = adjacency.to_numpy(dtype=float)
    expertise = np.ones(matrix.shape[0], dtype=float) / matrix.shape[0]
    quality = np.ones(matrix.shape[1], dtype=float) / matrix.shape[1]

    for _ in range(iterations):
        new_expertise = _normalise(quality @ matrix.T)
        new_quality = _normalise(new_expertise @ matrix)
        if (
            np.linalg.norm(new_expertise - expertise, ord=1) < tolerance
            and np.linalg.norm(new_quality - quality, ord=1) < tolerance
        ):
            expertise, quality = new_expertise, new_quality
            break
        expertise, quality = new_expertise, new_quality

    expertise_df = (
        pd.DataFrame({"user": adjacency.index, "expertise": expertise})
        .sort_values("expertise", ascending=False, ignore_index=True)
    )
    quality_df = (
        pd.DataFrame({"resource": adjacency.columns, "quality": quality})
        .sort_values("quality", ascending=False, ignore_index=True)
    )
    return SpearResult(expertise=expertise_df, quality=quality_df, adjacency=adjacency)
