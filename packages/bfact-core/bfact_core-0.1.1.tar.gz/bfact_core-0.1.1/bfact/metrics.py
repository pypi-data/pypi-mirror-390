import numba as nb
import numpy as np


@nb.njit
def get_recon(y_data, membership, profiles):
    recon_matrix = (
        (membership.astype(np.float32) @ profiles.astype(np.float32)) > 0.5
    ).astype(np.int32)
    return np.count_nonzero(recon_matrix != y_data)


@nb.njit
def relative_loss(recon, orig):
    return np.abs(recon - orig).sum() / np.count_nonzero(orig)


@nb.njit
def similarity(recon, orig):
    return np.count_nonzero(recon == orig) / recon.size


@nb.njit
def get_var_explained_per_K(recon, orig, K):
    return np.count_nonzero(recon == orig) / K


@nb.njit
def compute_precision(recon, orig):
    tp = np.count_nonzero((recon == 1) & (orig > 0))
    return tp / np.count_nonzero(recon) if np.count_nonzero(recon) > 0 else 0


@nb.njit
def compute_recall(recon, orig):
    return np.count_nonzero((recon == 1) & (orig > 0)) / np.count_nonzero(orig)


@nb.njit
def compute_f_measure(recon, orig):
    precision = compute_precision(recon, orig)
    recall = compute_recall(recon, orig)
    f1 = (
        (2 * precision * recall) / (precision + recall)
        if (precision + recall) > 0
        else 0
    )
    return precision, recall, f1


@nb.njit
def get_recon_fscore(y_data, membership, profiles):
    recon_matrix = (
        (membership.astype(np.float32) @ profiles.astype(np.float32)) > 0.5
    ).astype(np.int32)
    recon = np.count_nonzero(recon_matrix != y_data)
    return recon, compute_f_measure(recon_matrix, y_data)[2]


@nb.njit
def get_description_size(y_data, membership, profiles):
    recon_matrix = (
        (membership.astype(np.float32) @ profiles.astype(np.float32)) > 0.5
    ).astype(np.int32)

    recon = np.count_nonzero(recon_matrix != y_data)
    tot_memb = np.count_nonzero(membership)
    tot_dat = np.count_nonzero(y_data)

    memb_per_factor = np.count_nonzero(membership, axis=0)
    recon_per_factor = np.count_nonzero(recon_matrix != y_data, axis=0)

    memb_mask = memb_per_factor > 0
    recon_mask = recon_per_factor > 0

    memb_per_factor = memb_per_factor[memb_mask]
    recon_per_factor = recon_per_factor[recon_mask]

    ps = np.log(memb_per_factor / (tot_memb + recon))
    prpi = np.log(recon_per_factor / (tot_memb + recon))

    on_per_feature = np.count_nonzero(y_data, axis=0)
    on_mask = on_per_feature > 0
    code_lengths = -np.log(on_per_feature[on_mask] / tot_dat)

    data_description = -(memb_per_factor * ps).sum() - (recon_per_factor * prpi).sum()
    model_description = (
        (profiles[:, on_mask] * code_lengths).sum()
        - ps.sum()
        + code_lengths.sum()
        - prpi.sum()
    )
    return data_description + model_description


def get_metrics(memb, prof, orig_data):
    recon = ((memb @ prof) > 0.5).astype(int)

    P_orig, R_orig, F_orig = compute_f_measure(recon, orig_data)

    result_dict = {
        "precision": P_orig,
        "recall": R_orig,
        "f_score": F_orig,
        "similarity": similarity(recon, orig_data),
        "relative_loss": relative_loss(recon, orig_data),
        "recon": get_recon(orig_data, memb, prof),
        "mdl_cost": get_description_size(orig_data, memb, prof),
    }

    return result_dict
