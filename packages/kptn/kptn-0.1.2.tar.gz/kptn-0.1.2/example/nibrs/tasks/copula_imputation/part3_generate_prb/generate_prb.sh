#!/bin/bash
set -e

env LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2 Rscript 02_Generate_PRB_Copula.R
env LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2 Rscript 03_Generate_PRB_Copula_2.R
