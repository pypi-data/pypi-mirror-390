# Running Step YT1

Table YT1 is the first of two tables which generate stats for youth homicides.


1. Run Part1_prepare_datasets.R
1. Run step 2 with the following inputs
  1. `Part2_generate_est.R <column>`, where <column> is 1. These columns each map to a specific variable of interest.
1. Run the finalize script `Part3_finalize.R` to merge the outputs from the Part2 runs.
