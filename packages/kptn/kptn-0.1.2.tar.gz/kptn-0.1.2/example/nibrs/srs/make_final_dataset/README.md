# SRS Estimation Pipeline

## Running make final database scripts outside of Docker

The final database script requires one additional environment variable, `PERMUTATION_NAME`, outside of the environment variables set in the main README. The expected values for `PERMUTATION_NAME` are 1-859. The working directly also needs to be set to `./nibrs-estimation-pipeline/srs/make_final_dataset`

To run a single permutation through the make final dataset script, you'd add the following line to your environment script:

`PERMUTATION_NAME = 1`

and then run `10000 - Make Final Database.R`.

To run all or a subset of permutations through the make final dataset script, you'd run code similar to the following:

```
perm_list = as.list(1:859)

for (perm in perm_list) {
    Sys.setenv(PERMUTATION_NAME = perm)

    source('10000 - Make Final Database.R')
}
```
