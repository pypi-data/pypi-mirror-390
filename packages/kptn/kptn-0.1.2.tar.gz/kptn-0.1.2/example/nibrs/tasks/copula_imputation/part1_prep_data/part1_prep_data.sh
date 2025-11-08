#!/bin/bash
set -e

env LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2 Rscript 100_Run_Copula_Data_Prep_Step1.R
env LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2 Rscript 100_Run_Copula_Data_Prep_Step2.R
env LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2 Rscript 100_Run_Copula_Data_Prep_Step3.R
env LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2 Rscript 100_Run_Copula_Data_Prep_Step4.R
