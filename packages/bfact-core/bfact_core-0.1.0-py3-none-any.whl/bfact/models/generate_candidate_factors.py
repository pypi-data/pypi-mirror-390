from concurrent.futures import ProcessPoolExecutor
from functools import partial
import warnings

import numpy as np
import pandas as pd
import scanpy as sc
from anndata import AnnData
from scipy.cluster.hierarchy import fcluster, linkage
from sklearn.preprocessing import OneHotEncoder


def process_binned_distance(binned_distance, Z):
    """Process a single binned distance to get one-hot encodings."""
    encoder = OneHotEncoder(sparse_output=False)
    cluster_labels = fcluster(Z, binned_distance, criterion='distance').reshape(-1, 1)
    return encoder.fit_transform(cluster_labels)


def get_cols_from_binned_dendrogram(Z, num_bins, unique_distances, max_workers=None):
    """Get column combinations using parallel processing."""
    max_dist = unique_distances.max()
    bins = np.linspace(0, max_dist, num_bins + 1)  # Divide into `num_bins` equal parts

    # Digitize distances into bins
    binned_distances = np.digitize(unique_distances, bins) * (max_dist / num_bins)
    unique_binned_distances = np.unique(binned_distances)
    
    # Create a partial function with Z fixed
    process_func = partial(process_binned_distance, Z=Z)
    if max_workers is None:
        one_hot_encodings = [process_func(dist) for dist in unique_binned_distances]
    else:
        print(f"Getting cols using {max_workers} processes")
        # Use parallel processing to compute one-hot encodings
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            one_hot_encodings = list(executor.map(process_func, unique_binned_distances))
        
    cols = np.unique(np.hstack(one_hot_encodings).T, axis=0)
    
    return cols

def get_binned_col_combos(input_data, num_bins=100, metric='hamming', min_threshold=None, max_threshold=None, max_workers=None):
    """Get binned column combinations with optional parallel processing."""
    Z = linkage(input_data.T, method='average', metric=metric)
    # Get the unique distances at which the dendrogram can be cut
    unique_distances = np.unique(Z[:, 2])

    _iter = 0 
    old_num_cols = 0  # arbitrary, will be diff for first 
    while True:
        cols = get_cols_from_binned_dendrogram(Z, num_bins, unique_distances, max_workers=max_workers)

        if (min_threshold is None) or (max_threshold is None):
            return cols, num_bins

        num_cols = cols.shape[0]
        print(f"Preproccesing: num cols {num_cols}")
        if ((min_threshold < num_cols) and (num_cols < max_threshold)) or (_iter > 4):
            return cols, num_bins

        coeff = (min_threshold + max_threshold)/(2*num_cols)

        if old_num_cols == num_cols:
            return cols, int(num_bins/coeff)

        num_bins = int(num_bins*coeff)  # update num_bins
        old_num_cols = num_cols
        _iter += 1


def leiden_cols(arr, n_neighbors=15, max_res=5, inc=0.1):
    warnings.filterwarnings("ignore", category=UserWarning, module="scanpy")
    warnings.filterwarnings("ignore", category=FutureWarning, module="scanpy")

    one_hot_ls = []

    for use_rep in [None, 'X']:
        adata = AnnData(arr.T)
        sc.pp.neighbors(adata, metric="hamming", use_rep=use_rep, n_neighbors=n_neighbors)

        for res in np.arange(1, max_res, inc):
            sc.tl.leiden(adata, resolution=res, flavor='igraph')
            one_hot_ls.append(pd.get_dummies(adata.obs['leiden']).T.astype(int))

    return pd.concat(one_hot_ls, axis=0, ignore_index=True).drop_duplicates().values

