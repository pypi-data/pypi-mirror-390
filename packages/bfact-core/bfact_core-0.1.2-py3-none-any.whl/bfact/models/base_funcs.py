import time
from dataclasses import dataclass
from typing import Literal

import numpy as np


@dataclass
class BinData:
    arr: np.ndarray
    likely_factors: np.ndarray

    @property
    def n_cells(self):
        return self.arr.shape[0]

    @property
    def n_features(self):
        return self.arr.shape[1]

    @property
    def num_factors(self):
        return self.likely_factors.shape[0]

    @property
    def factor_idx(self):
        return range(self.num_factors)


@dataclass
class Params:
    save_stub: str 
    use_feature_metric: Literal["recon", "f_score", "mdl", "mip"] = "recon"
    K_score_factor: float = (
        0.999  # 1 - factor is approx. required increase prop per col
    )
    can_transpose: bool = True

    # note this is per dist metric
    min_col_threshold: int = 2000
    max_col_threshold: int = 10000

    min_considered_K: int = 10
    max_considered_K: int = 100
    num_K: int = 10
    early_stop_iter: int = 3

    parallel_switch_size: int = 5_000_000
    num_processes: int = 12  # only used if matrix > parallel_switch_size

    to_save_cols: bool | None = False
    saved_cols_path: str | None = None

    # possible binary metrics are ‘hamming’, ‘jaccard’, ‘matching’, ‘rogerstanimoto’, ‘russellrao’, ‘yule’.
    # initial_column_dist_metrics = ["hamming", "rogerstanimoto"]
    initial_column_dist_metrics: tuple[
        Literal[
            "hamming",
            "jaccard",
            "matching",
            "rogerstanimoto",
            "russellrao",
            "yul",
            "leiden",
        ]
    ] = ("hamming", "leiden")

    K_penalty: bool = False
    orthog: bool = False
    num_thresholds: int = 20  # only used if orthog is False
    num_bins: float = 100 # for binning hierarchical clustering to find columns.

    def __post_init__(self):
        if (self.use_feature_metric == "mip" and self.orthog):
            raise ValueError("mip feature metric is by default non-orthog.")


@dataclass
class Timer:
    _start_time: float | None = None

    def set_time(self):
        self._start_time = time.time()

    def elapsed_time(self):
        if self._start_time:
            return time.time() - self._start_time
        return 0



def get_cost(input_arr, factor_arr, return_memb=False):
    intersect = np.tensordot(
        factor_arr, input_arr, axes=([1], [1])
    )  # Shape: (len(factor_arr), input_arr.shape[0])
    total_factors = factor_arr.sum(axis=1, keepdims=True)  # Shape: (len(factor_arr), 1)
    # RHS preferred when intersect high, LHS preferred when intersect low

    rhs = (total_factors - intersect)
    min_values = np.minimum(intersect, rhs)

    if return_memb:
        return min_values.sum(axis=1), (intersect > rhs).astype(int)

    return min_values.sum(axis=1)


