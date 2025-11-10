from dataclasses import asdict
import pickle

import numpy as np
from bfact.models.generate_candidate_factors import get_binned_col_combos, leiden_cols
from bfact.models.base_funcs import BinData
from bfact.models.iterate_main import run_IP_K_list



def get_cols(data, params):
    g_vals = [] 
    final_num_bins = None
    workers = None if data.size < params.parallel_switch_size else params.num_processes

    for dist_metric in params.initial_column_dist_metrics:
        if dist_metric == "leiden":
            leiden = leiden_cols(data)
            print(f"Num factors for {dist_metric}: {leiden.shape[0]}")
            g_vals.append(leiden)
        else:
            gf, final_num_bins = get_binned_col_combos(data, params.num_bins, dist_metric, params.min_col_threshold, params.max_col_threshold, workers)
            print(f"Num factors for {dist_metric}: {gf.shape[0]}, with num bins {final_num_bins}")
            g_vals.append(gf)

    total_g = np.unique(np.vstack(g_vals), axis=0)

    if params.to_save_cols: 
        with open(f"{params.save_stub}_{total_g.shape[0]}_cols.pkl", "wb") as f:
            pickle.dump(total_g, f)
    
    return total_g, final_num_bins


def run_setmip_bool(y_data, params):    
    transposed = y_data.shape[1] < y_data.shape[0] and params.can_transpose

    data = y_data.T if transposed else y_data

    if transposed:
        print("using transposes to obtain factorisation as: N < M and can_transpose is ON")

    if params.saved_cols_path is not None:
        with open(params.saved_cols_path, "rb") as f:
            total_g = pickle.load(f)
        num_bins = None

        if data.shape[1] != total_g.shape[1]:
            print("Misalignment between saved columns")
            total_g, num_bins = get_cols(data, params)
    else:
        total_g, num_bins = get_cols(data, params)

    print(f"Total factors across dist metrics: {total_g.shape[0]}")

    bdata = BinData(data, likely_factors=total_g)

    save_info = {"transposed": transposed, "bin_nums": num_bins, "num_factors_choice": total_g.shape[0], "params": asdict(params)}

    return run_IP_K_list(bdata, params, save_info=save_info)