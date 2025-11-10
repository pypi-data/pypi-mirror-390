import time
import numpy as np
from bfact.metrics import get_description_size, get_recon_fscore
import numba as nb


@nb.njit
def get_small_metrics(y_data, memb, prof, metric):
    recon, f_score = get_recon_fscore(y_data, memb, prof)
    mdl = get_description_size(y_data, memb, prof) if metric == "mdl" else np.nan
    return np.array([recon, -f_score, mdl])


@nb.njit(parallel=True)
def evaluate_all_features(y_data, memb, prof, metric):
    n_features = memb.shape[1]
    scores = np.empty((n_features, 3))
    
    for k in nb.prange(n_features):  # parallel loop
        memb_temp = memb.copy()
        prof_temp = prof.copy()
        memb_temp[:, k] = 0
        prof_temp[k, :] = 0
        
        scores[k] = get_small_metrics(y_data, memb_temp, prof_temp, metric) 
    
    return scores


@nb.njit()
def feature_prune_core(y_data, memb, prof, metric, base_factor, current_results):
    """
    Sequential version of feature pruning (original implementation).
    """

    axis = 0 if metric == 'recon' else 1 if metric == 'f_score' else 2

    factor = base_factor if metric == 'recon' else 1/base_factor if metric == 'f_score' else 1

    while memb.shape[1] > 0:  # Stop if no features left
        scores = evaluate_all_features(y_data, memb, prof, metric)
        best_k = np.argmin(scores[:, axis])  # or argmax depending on your metric
        new_val = scores[best_k]
        # Check termination condition
        if new_val[axis]*factor >= current_results[axis]:
            break

        # Apply best removal
        memb = np.hstack((memb[:, :best_k], memb[:, best_k + 1:]))
        prof = np.vstack((prof[:best_k, :], prof[best_k+1:, :]))

        current_results = new_val  # Update score

    return memb, prof, current_results



def greedy_feature_prune(y_data, memb, prof, params):
    memb, prof = memb.copy(), prof.copy()

    metric = params.use_feature_metric

    current_results = get_small_metrics(y_data, memb, prof, params.use_feature_metric)

    if metric == "mdl":
        print("Prune features based on MDL cost.")
        include_str = lambda res: f", MDL cost {res[2]:.2f}"
    else:
        print(
            f"Prune freatures based on {metric} and max per-feature-impairment factor {params.K_score_factor}."
        )
        include_str = lambda _: ""

    print_statement = (
        lambda v1, res, m: f"{v1} recon {res[0]}, F score {-res[1]}{include_str(res)} with {m.shape[1]} features."
    )

    print(print_statement("Start", current_results, memb))
    start_time = time.time()

    memb, prof, final_res = feature_prune_core(y_data, memb, prof, params.use_feature_metric, params.K_score_factor, current_results)

    print(f"Time taken: {time.time() - start_time:.2f} seconds")
    print(print_statement("End", final_res, memb))
    return memb, prof
