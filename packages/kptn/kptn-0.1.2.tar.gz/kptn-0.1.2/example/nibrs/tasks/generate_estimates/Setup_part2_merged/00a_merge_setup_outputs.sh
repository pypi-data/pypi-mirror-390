#!/bin/bash
set -e
env LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2 Rscript 00a_Merge_Setup_Outputs_pt1.R
env LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2 Rscript 00a_Merge_Setup_Outputs_pt2.R