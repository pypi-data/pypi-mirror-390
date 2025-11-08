#!/bin/bash
set -e

timeout --verbose 4h env LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2 Rscript 100_Run_Copula_Imputation_Step1.R "popResidAgcyCounty_cbi>0 & nDemoMissing==0"
timeout --verbose 4h env LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2 Rscript 100_Run_Copula_Imputation_Step1.R "popResidAgcyCounty_cbi>0 & nDemoMissing>0"
timeout --verbose 4h env LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2 Rscript 100_Run_Copula_Imputation_Step1.R "popResidAgcyCounty_cbi==0"

# if STOP_AFTER_PART1 == 0 then we keep going after part 1. Otherwise we stop to let the validation results be evaluated.
if [ "$STOP_AFTER_PART1" = "0" ]; then
  timeout --verbose 4h env LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2 Rscript 100_Run_Copula_Imputation_Step2_Alt.R "popResidAgcyCounty_cbi>0 & nDemoMissing==0"
  timeout --verbose 4h env LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2 Rscript 100_Run_Copula_Imputation_Step2_Alt.R "popResidAgcyCounty_cbi>0 & nDemoMissing>0"
  timeout --verbose 4h env LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2 Rscript 100_Run_Copula_Imputation_Step2_Alt.R "popResidAgcyCounty_cbi==0"
  timeout --verbose 4h env LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2 Rscript 100_Run_Copula_Imputation_Step3_Alt.R "popResidAgcyCounty_cbi>0 & nDemoMissing==0"
  timeout --verbose 4h env LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2 Rscript 100_Run_Copula_Imputation_Step3_Alt.R "popResidAgcyCounty_cbi>0 & nDemoMissing>0"
  timeout --verbose 4h env LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2 Rscript 100_Run_Copula_Imputation_Step3_Alt.R "popResidAgcyCounty_cbi==0"
  timeout --verbose 4h env LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2 Rscript 100_Run_Copula_Imputation_Step4.R "popResidAgcyCounty_cbi>0 & nDemoMissing==0"
  timeout --verbose 4h env LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2 Rscript 100_Run_Copula_Imputation_Step4.R "popResidAgcyCounty_cbi>0 & nDemoMissing>0"
  timeout --verbose 4h env LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2 Rscript 100_Run_Copula_Imputation_Step4.R "popResidAgcyCounty_cbi==0"
fi