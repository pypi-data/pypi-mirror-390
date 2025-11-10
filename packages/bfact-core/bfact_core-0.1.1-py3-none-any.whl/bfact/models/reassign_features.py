from concurrent.futures import ProcessPoolExecutor
import numpy as np
import functools
import time

from bfact.metrics import get_recon_fscore, get_description_size


def _process_single_threshold(
    threshold, feature_on_off_per_class, sum_cells, base_profiles, y_data, membership
):
    """Process a single threshold value."""
    cnzo = np.count_nonzero
    try_profiles = (
        (feature_on_off_per_class > threshold * sum_cells) | base_profiles
    ).astype(int)
    recon, f_score = get_recon_fscore(y_data, membership, try_profiles)
    mdl_cost = get_description_size(y_data, membership, try_profiles)

    result = {
        "f_score": f_score,
        "recon": recon,
        "mdl": mdl_cost,
        "threshold": threshold,
        "profiles": try_profiles,
    }

    print(
        f"Threshold: {threshold:.3f}, recon: {recon:.4f}, f_score: {f_score:.4f}, mdl_cost: {mdl_cost:.4f} "
        f"total no. features selected: {cnzo(cnzo(try_profiles, axis=0) > 0)}, "
        f"no. features multiple factors: {cnzo(cnzo(try_profiles, axis=0) > 1)}"
    )

    return result


def _process_sequential(
    y_data,
    metric,
    thresholds,
    membership,
    feature_on_off_per_class,
    sum_cells,
    base_profiles,
):
    """Sequential processing with early stopping."""
    results = []
    print("Start thresholds")

    prev_metric_value = 0 if metric == "f_score" else float("inf")

    for i, threshold in enumerate(thresholds):
        result = _process_single_threshold(
            threshold,
            feature_on_off_per_class,
            sum_cells,
            base_profiles,
            y_data,
            membership,
        )
        results.append(result)
        # Check if performance is degrading
        current_metric_value = result[metric]
        if i > 0 and (
            (metric != "f_score" and current_metric_value > prev_metric_value)
            or (metric == "f_score" and current_metric_value < prev_metric_value)
        ):
            print(f"Breaking early as {metric} is degrading at threshold {threshold}.")
            break

        prev_metric_value = current_metric_value

    return results


def reassign_features_on_thresh(
    y_data, metric, num_thresholds, membership, profiles, params, parallel=True
):
    # remember this threshold is already on above 50%
    thresholds = np.linspace(0.001, 1, num_thresholds)
    cnzo = np.count_nonzero

    # remember this is number correct - number incorrect
    feature_on_off_per_class = np.einsum("ij,ik->kj", 2 * y_data - 1, membership)
    sum_cells = cnzo(membership, axis=0)[:, None]
    zero_features = cnzo(profiles, axis=0) == 0
    base_profiles = profiles.astype(int) | (
        (feature_on_off_per_class > 0.5 * sum_cells) & zero_features
    ) #corresponds to being on in 3/4 of cells

    # If not a large matrix or parallel=False, use optimized sequential
    if not parallel:
        return _process_sequential(
            y_data,
            metric,
            thresholds,
            membership,
            feature_on_off_per_class,
            sum_cells,
            base_profiles,
        )

    # For large matrices, use parallelism
    n_jobs = params.num_processes

    # Prepare partial function with fixed arguments
    process_threshold_partial = functools.partial(
        _process_single_threshold,
        feature_on_off_per_class=feature_on_off_per_class,
        sum_cells=sum_cells,
        base_profiles=base_profiles,
        y_data=y_data,
        membership=membership,
    )

    print(f"Starting parallel processing with {n_jobs} processes")

    # Create a pool of workers and map the function to the thresholds
    with ProcessPoolExecutor(max_workers=params.num_processes) as executor:           
        results = list(executor.map(process_threshold_partial, thresholds))

    # Sort results by threshold to maintain order
    results.sort(key=lambda x: x["threshold"])

    return results


def get_best_threshold(membership, orig_profiles, bdata, params, parallel):

    orig_recon, orig_f = get_recon_fscore(bdata.arr, membership, orig_profiles)
    orig_mdl = get_description_size(bdata.arr, membership, orig_profiles)
    orig_res = {"recon": orig_recon, "f_score": orig_f, "mdl": orig_mdl}

    print("Reassign features based on threshold.")
    start = time.time()
    results = reassign_features_on_thresh(
        bdata.arr,
        params.use_feature_metric,
        params.num_thresholds,
        membership,
        orig_profiles,
        params,
        parallel,
    )
    print(f"Time taken: {time.time() - start}")

    metric = params.use_feature_metric
    compare_func = max if metric == "f_score" else min

    best_result = compare_func(results, key=lambda x: x[metric])

    if compare_func(best_result[metric], orig_res[metric]) == orig_res[metric]:
        print("Original best")
        return orig_profiles, None

    print(f"Original result: original recon {orig_recon}, F score {orig_f}")
    print(
        f"Chosen result: recon {best_result['recon']}, F score {best_result['f_score']}, MDL cost {best_result['mdl']} for threshold {best_result['threshold']}"
    )

    return best_result["profiles"], best_result["threshold"]
