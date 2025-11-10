import functools
import json

import numpy as np
from bfact.metrics import get_description_size, get_recon_fscore
from bfact.models.base_funcs import BinData
from bfact.models.double_IP import run_double_IP
from bfact.models.restricted_master_problem import run_RMP, run_RMP_new_K


def get_small_metrics(main, bdata, params):

    memb = main._Vars.get("membership_no", main._Vars["membership"])
    prof = main._Vars.get("profile_no", main._Vars["profile"])

    recon, f_score = get_recon_fscore(bdata.arr, memb, prof)
    result = {
        "K": memb.shape[1],
        "recon": recon,
        "membership": memb,
        "profile": prof,
        "threshold": main._Vars.get("threshold"),
        "f_score": f_score,
    }

    if params.use_feature_metric == "mdl":
        result["mdl_cost"] = get_description_size(bdata.arr, memb, prof)

    return result


def save_result(best_result, params, save_info):
    if save_info.get("transposed", False):
        t_membership = best_result["membership"].T
        best_result["membership"] = best_result["profile"].T
        best_result["profile"] = t_membership

    save_result = best_result.copy()
    if params.save_stub is not None:
        f_base = f"{params.save_stub}_best_{params.use_feature_metric}"
        np.savetxt(f"{f_base}.L.txt", save_result.pop("membership"), delimiter="\t", fmt="%d")
        np.savetxt(f"{f_base}.R.txt", save_result.pop("profile"), delimiter="\t", fmt="%d")

        with open(f"{f_base}.summary_info.json", "w") as f:
            json.dump(save_result | save_info, f, indent=2)


def run_double(bdata, curr_K, params, get_func=run_RMP):
    params.orthog=True
    main = get_func(bdata, curr_K, params)
    result = get_small_metrics(main, bdata, params)

    bdata_dbl = BinData(arr=bdata.arr.T, likely_factors=np.unique(main._Vars["membership"], axis=1).T)
    result, dbl_main = run_double_IP(bdata_dbl, curr_K)
    params.orthog=False
    return result, main


def run_IP_K_list(bdata, params, main=None, save_info={}):
    """
    Because of post-processing, the recon can be better for different K values not accounted for in the MIP.
    """
    K_list = np.linspace(
        params.min_considered_K, params.max_considered_K, params.num_K
    ).tolist()

    def get_ip_func(iter, _main):
        if _main is None:
            return run_RMP
        else:
            return functools.partial(
                run_RMP_new_K, _main,
            )

    best_result = None
    best_idx = 0
    for i, curr_K in enumerate(K_list):
        ip_func = get_ip_func(i, main)
        if params.use_feature_metric == "mip":
            new_result, main = run_double(bdata, curr_K, params, ip_func)
        else:
            main = ip_func(bdata, curr_K, params)
            new_result = get_small_metrics(main, bdata, params)

        print_str = (
            lambda _, v: f" given maximum metric impairment factor of {params.K_score_factor} (per feature)."
            if v
            else ""
        )
        if params.use_feature_metric == "mdl":
            print_str = lambda x, _: f", MDL: {x['mdl_cost']}"

        print(
            f"K: {new_result['K']}, Recon: {new_result['recon']:.4f}, F-score: {new_result['f_score']:.4f}{print_str(new_result, False)}"
        )

        if best_result is None:
            result_better = True
        elif params.use_feature_metric == "recon":
            result_better = new_result["recon"] < best_result["recon"]*(params.K_score_factor**(new_result["K"] - best_result["K"]))
        elif params.use_feature_metric == "f_score":
            result_better = (
                new_result["f_score"]
                * (params.K_score_factor ** (new_result["K"] - best_result["K"]))
                > best_result["f_score"]
            )
        else:
            result_better = new_result["mdl_cost"] < best_result["mdl_cost"]

        if result_better:
            print("This is the best result so far")
            best_result = new_result
            best_idx = i
            best_result["input_K"] = curr_K
            save_result(best_result, params, save_info)
        
        if i - best_idx > params.early_stop_iter:
            print(f"Stopping early, has not improved in {params.early_stop_iter} K iterations")
            break

    print(
        f"Best:\nK: {best_result['K']}, Recon: {best_result['recon']}, F score: {best_result['f_score']}{print_str(best_result, True)}"
    )

    # main model may not have K_max or best result assoc now, but returned in case wanted for further analysis
    return best_result, main
