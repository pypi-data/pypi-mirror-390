import gurobipy as gp
from gurobipy import GRB
import numpy as np

from bfact.metrics import get_description_size, get_recon_fscore
from bfact.models.base_funcs import Timer


def double_main(bdata, K_max):
    main = gp.Model('main')
    timer = Timer()

    timer.set_time()
    factors = main.addMVar(bdata.num_factors, vtype=GRB.BINARY, name="factors")
    print(f"Added factors, elapsed time: {timer.elapsed_time():.2f}")

    timer.set_time()
    memb = main.addMVar((bdata.num_factors, bdata.n_cells), vtype=GRB.BINARY, name="el_covered")
    print(f"Added membership, elapsed time: {timer.elapsed_time():.2f}")


    timer.set_time()
    on_off = list(zip(*np.nonzero(bdata.arr)))
    els_on_in_dat = main.addMVar(len(on_off), vtype=GRB.BINARY, name="els_on_in_dat")
    print(f"Added cover els, elapsed time: {timer.elapsed_time():.2f}")


    timer.set_time()
    bin_product = memb.T@bdata.likely_factors
    uncovered = main.addConstr(els_on_in_dat <=  bin_product[bdata.arr>0.5])
    # bin_product[i,j] for idx, (i, j) in enumerate(on_off))
    print(f"Added uncover constraints, elapsed time: {timer.elapsed_time():.2f}")

    timer.set_time()
    tot_bdata = bdata.arr.sum()

    recon = tot_bdata - els_on_in_dat@np.ones(len(on_off)) + memb.reshape(-1)@(bdata.likely_factors@(1 - bdata.arr).T).ravel()
    # last term is: bin_product[bdata.arr<0.5].sum(), but way faster, do not change 

    memb_sum = memb@np.ones(bdata.n_cells)
    model_complexity = gp.quicksum(factors[alpha]*bdata.likely_factors[alpha].sum() + memb_sum[alpha] for alpha in bdata.factor_idx)

    main.setObjective(recon + model_complexity, GRB.MINIMIZE)
    print(f"Added objective, elapsed time: {timer.elapsed_time():.2f}")

    timer.set_time()
    memb_enforce = main.addConstrs(memb_sum[alpha] <= bdata.n_cells*factors[alpha] for alpha in bdata.factor_idx)
    print(f"Added membership constraints, elapsed time: {timer.elapsed_time():.2f}")

    k_factors = main.addConstr(gp.quicksum(factors[alpha] for alpha in bdata.factor_idx) <= K_max, name="k_factors")
    print(f"Added k factor constraints, elapsed time: {timer.elapsed_time():.2f}")

    main._Vars = {"factors": factors, "membership": memb}
    main._columns = bdata.likely_factors.copy()

    return main



def get_results_dbl(main, bdata, transposed=True):
    # designed to be used on transposed data in pipeline

    factors = main._Vars["factors"]
    factor_mask = factors.x.astype(bool)
    chosen_factors = main._columns[factor_mask]
    membership_ = main._Vars["membership"].x[factor_mask].T
    
    recon, f_score = get_recon_fscore(bdata.arr, membership_, chosen_factors)
    mdl = get_description_size(bdata.arr, membership_, chosen_factors)
    
    if transposed:
        membership = chosen_factors.T
        profiles = membership_.T
    else:
        membership = membership_
        profiles = chosen_factors

    result = {"membership": membership, "profile": profiles, "recon": recon, "f_score": f_score, "mdl_cost": mdl, "K": membership.shape[1]}

    print(f"MIP results for K {result['K']}- Recon: {recon}, F score {f_score}, MDL: {mdl}")

    return result



def run_double_IP(bdata, K_max):
    main = double_main(bdata, K_max)
    main.setParam("OutputFlag", 1)  
    main.setParam('MIPGap', 0.05)
    # main.setParam("Presolve", 0)

    print("Optimizing Dbl")
    main.optimize()
    print("Optimized Dbl")
    result = get_results_dbl(main, bdata)
    return result, main 
