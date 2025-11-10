import glob
import json
import scanpy as sc
import numpy as np
import click

from bfact.models.base_funcs import Params
from bfact.run_bfact import run_setmip_bool


@click.command(help="Run bfact for input file, giving output results for given metric.")
@click.option(
    "--in-file",
    required=True,
    help="The input file for binary matrix, assumes either .tsv or h5ad format.",
    show_default=True,
)
@click.option(
    "--out-stub",
    required=True,
    help="The output path + prefix for output files- output is written too- this  ",
    show_default=True,
)
@click.option(
    "--metric",
    required=False,
    default="mdl",
    type=click.Choice(["mdl", "recon", "mip", "f_score"]),
    help="Metric for eval, if mip will run second mip instead of heuristic approach.",
    show_default=True,
)
@click.option(
    "--saved-cols-stub",
    required=False,
    default=None,
    help="The path + prefix for where previous columns have been saved, to reuse found columns. If multiple matches for the same stub, will use the first. If not provided, will create columns.",
    show_default=True,
)
@click.option(
    "--to-save-cols",
    required=False,
    default=False,
    help="Whether to save columns to file. Recommended for large matrices as this is a bottleneck.",
    show_default=True,
)
@click.option(
    "--k-score-factor",
    required=False,
    default=None,
    help="Only applies to recon/f_score. Min prop. of metric that should be maintained if a factor is removed. Defaults to 0.997. Can decrease this value to get lower rank factorisations if desired. A good rule of thumb is that shoulld be around 1 - 1/min(M, N), and should induce some pruning especially as K increases. If no pruning occurs, try decreasing slightly (i.e to 0.993).",
    show_default=True,
)
@click.option(
    "--min-col-threshold",
    required=False,
    default=2000,
    help="Attempted minimum no. of columns to generate from clustering. If bounds are not achieved within 4 iterations, or no. of columns does not change with itereations, will continue out of bounds. Option max-col-threshold defines maximum bound.",
    show_default=True,
)
@click.option(
    "--max-col-threshold",
    required=False,
    default=15000,
    help="Attempted maximum no. of columns to generate from clustering. If bounds are not achieved within 4 iterations, or no. of columns does not change with itereations, will continue out of bounds. Option min-col-threshold defines minimum bound.",
    show_default=True,
)
@click.option(
    "--can-transpose",
    required=False,
    default=True,
    help="Whether or not to transpose matrix- for smaller matrices this should be set to True, as improves result in cases where N < M (for small).",
    show_default=True,
)
@click.option(
    "--min-considered-k",
    required=False,
    default=10,
    help="Final rank can be less than this, but this is the minimum value that the RMP is solved for. Can help to run at a few different values. See max-considered-k and num-k for different parameters that control this.",
    show_default=True,
)
@click.option(
    "--max-considered-k",
    required=False,
    default=100,
    help="Final rank can be less than this, but this is the maximum value that the RMP will be solved for, unless early stopping triggered. Can help to run at a few different values. See min-considered-k and num-k for different parameters that control this.",
    show_default=True,
)
@click.option(
    "--num-k",
    required=False,
    default=10,
    help="Number of times the RMP is solved for values between min-considerd-k and max-considered, unless early stopping triggered. Can help model to run at few different values, depending on the selected columns for each value. If num-k is 1, it will select the minimum bound.",
    show_default=True,
)
@click.option(
    "--early-stop-iter",
    required=False,
    default=3,
    help="Number of iterations without improvement in the result, before early stopping is triggered. Pruning at large factors is costly, so only does this if necessary",
    show_default=True,
)
@click.option(
    "--parallel-switch-size",
    required=False,
    default=5_000_000,
    help="Size of matrix (M x N) before switching to parallelism over the pre and post processing. Note that for smaller matrices this will not be faster, but for larger matrices parallelism is desirable.",
    show_default=True,
)
@click.option(
    "--num-processes",
    required=False,
    default=6,
    help="Default number of processes (i.e cpus) if parallelism invoked by parallel-switch-size.",
    show_default=True,
)
def run_bfact(
    in_file,
    out_stub,
    metric='recon',
    saved_cols_stub=None,
    to_save_cols=False,
    k_score_factor=None,
    min_col_threshold=2000,
    max_col_threshold=15000,
    can_transpose=True,
    min_considered_k=10,
    max_considered_k=100,
    num_k=10,
    early_stop_iter=3,
    parallel_switch_size=5_000_000,
    num_processes=6,
):
    if "h5ad" in in_file:
        arr = sc.read_h5ad(in_file).X
    elif ".json" in in_file:
        with open(in_file) as f:
            arr = np.array(json.load(f)["y_data"])
    else:
        arr = np.loadtxt(in_file, delimiter="\t")

    saved_cols_path = None
    if saved_cols_stub is not None:
        hits = glob.glob(f"{saved_cols_stub}*cols.pkl")
        if len(hits) != 0:
            print("Found saved columns, re-using")
            saved_cols_path = hits[0]
        else:
            raise ValueError(f"Columns not found for path stub {saved_cols_stub}")

    params = Params(
        min_col_threshold=min_col_threshold,
        K_score_factor=k_score_factor or 0.997,
        max_col_threshold=max_col_threshold,
        can_transpose=can_transpose,
        min_considered_K=max(1, min_considered_k),
        max_considered_K=min(max_considered_k, arr.shape[1]),
        num_K=num_k,
        early_stop_iter=early_stop_iter,
        save_stub=out_stub,
        to_save_cols=to_save_cols,
        use_feature_metric=metric,
        saved_cols_path=saved_cols_path,
        parallel_switch_size=parallel_switch_size,
        num_processes=num_processes
    )

    run_setmip_bool(arr, params)


if __name__ == "__main__":
    run_bfact()
