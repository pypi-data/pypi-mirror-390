#!/bin/bash
set -e

timeout --verbose 1h env LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2 Rscript 100_run_copula_part2_impute.R "popResidAgcyCounty_cbi>0 & nDemoMissing==0"
timeout --verbose 1h env LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2 Rscript 100_run_copula_part2_impute.R "popResidAgcyCounty_cbi>0 & nDemoMissing>0"
timeout --verbose 1h env LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2 Rscript 100_run_copula_part2_impute.R "popResidAgcyCounty_cbi==0"
