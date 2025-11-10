
import gurobipy as gp
import numpy as np
from gurobipy import GRB

from bfact.metrics import get_recon_fscore
from bfact.models.base_funcs import Params, Timer, get_cost

from bfact.models.feature_prune import greedy_feature_prune
from bfact.models.reassign_features import get_best_threshold


def main_problem(bdata, K_max, params: Params):
    main = gp.Model("main")
    
    timer = Timer()
    timer.set_time()
    factors = main.addVars(bdata.num_factors, vtype=GRB.BINARY, name="factors")
    print(f"Added factors, elapsed time: {timer.elapsed_time():.2f}")

    timer.set_time()
    uncovered_feature = main.addVars(
        bdata.n_features, vtype=GRB.BINARY, name="uncovered_feature"
    )
    print(f"Added uncovered_feature, elapsed time: {timer.elapsed_time():.2f}")
    
    timer.set_time()
    cost, full_memb_t = get_cost(
        bdata.arr, bdata.likely_factors, return_memb=True
    )
    print(f"Got cost, elapsed time: {timer.elapsed_time():.2f}")

    timer.set_time()
    cell_sum = bdata.arr.sum(axis=0)
    objective = gp.LinExpr(cost, factors.select("*")) + gp.LinExpr(
        cell_sum, uncovered_feature.select("*")
    )

    mult_arr = np.ones(bdata.num_factors)
    factor_sum = gp.LinExpr(mult_arr, factors.select("*"))

    if params.K_penalty:
        multiplier = bdata.arr.sum() * (1 - params.K_score_factor)
        objective.add(factor_sum, multiplier)

    main.setObjective(objective, GRB.MINIMIZE)
    print(f"Set objective, elapsed time: {timer.elapsed_time():.2f}")

    timer.set_time()
    # looks non-orthog, cost implicitly favours orthogonality
    feature_repr = main.addConstrs(
        (
            gp.LinExpr(bdata.likely_factors[:, j], factors.select("*"))
            + uncovered_feature[j]
            >= 1
            for j in range(bdata.n_features)
        ),
        name=f"feature_repr",
    )

    print(f"Add feature repr constraints, elapsed time: {timer.elapsed_time():.2f}")

    timer.set_time()
    k_factors = main.addConstr(factor_sum <= int(K_max), name="k_factors")
    print(f"Add K factor constraints, elapsed time: {timer.elapsed_time():.2f}")

    main._Constr = {"feature_repr": feature_repr, "k_factors": k_factors}
    main._Vars = {"factors": factors, "uncovered_feature": uncovered_feature}
    main._columns = bdata.likely_factors.copy()

    return main


def get_membership_vals(input_arr, factor_arr):
    intersect = np.tensordot(
        factor_arr, input_arr, axes=([1], [1])
    )  # Shape: (len(factor_arr), input_arr.shape[0])
    total_factors = factor_arr.sum(axis=1, keepdims=True)  # Shape: (len(factor_arr), 1)
    return np.argmin(np.stack([intersect, total_factors - intersect]), axis=0).T


def get_results(main, bdata):
    factors = main._Vars["factors"]
    chosen_factors = main._columns[[bool(round(factors[alpha].x)) for alpha in factors]]
    membership = get_membership_vals(bdata.arr, chosen_factors)

    main._Vars["profile"] = chosen_factors
    main._Vars["membership"] = membership
    recon, f_score = get_recon_fscore(bdata.arr, membership, chosen_factors)
    print(
        f"MIP results for K {membership.shape[1]}- Recon: {recon}, F score {f_score}."
    )
    print(
        f"No. features selected: {(chosen_factors.sum(axis=0) > 0).sum()}, no. features multiple factors: {(chosen_factors.sum(axis=0) > 1).sum()}"
    )


def get_non_orthog_results(main, bdata, params):
    # Detect matrix size to auto-select processing method
    is_large = bdata.arr.size > params.parallel_switch_size

    prof_reassign_feature, threshold = get_best_threshold(
        main._Vars["membership"],
        main._Vars["profile"],
        bdata,
        params,
        parallel=is_large,
    )

    memb, prof = greedy_feature_prune(
        bdata.arr,
        main._Vars["membership"],
        prof_reassign_feature,
        params,
    )

    main._Vars["profile_no"] = prof
    main._Vars["membership_no"] = memb
    main._Vars["threshold"] = threshold


def run_RMP(bdata, K_max, params):
    main = main_problem(bdata, K_max, params)
    main.setParam("OutputFlag", 0)
    main.setParam("MIPGap", 0)

    # main.write(main_name)
    print("Optimizing")
    main.optimize()
    print("Optimized")
    get_results(main, bdata)

    if params.orthog is False:
        get_non_orthog_results(main, bdata, params)

    return main


def run_RMP_new_K(main, bdata, curr_K, params):
    main._Constr["k_factors"].rhs = int(curr_K)
    main.optimize()
    get_results(main, bdata)

    if params.orthog is False:
        get_non_orthog_results(main, bdata, params)

    return main


