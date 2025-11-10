## BFACT

This is python package for performing Boolean matrix factorisation.

### Install & run

Install as `pip install bfact-core`, which should create CLI command `bfact`. 

You can then get available options by running `bfact --help`.

### Expected inputs: 

--in-file: path to .h5ad or a tab separated file containing binary matric

--out-stub: The path + prefix for ouputs.

Any other input, see `bfact --help` for available options.

### Expected ouptuts: 

`{out_stub}_best_{metric}.L.txt`

`{out_stub}_best_{metric}.R.txt`

`{out_stub}_best_{metric}.summary_info.json`

`{out_stub}_{num_considered_factors}_cols.pkl` (only if --to-save-cols specified true). This file stores the candidate factors used in the restricted master problem. It is useful for large matrices to save time if provided in future runs (using the base as --saved-cols-stub).
     
