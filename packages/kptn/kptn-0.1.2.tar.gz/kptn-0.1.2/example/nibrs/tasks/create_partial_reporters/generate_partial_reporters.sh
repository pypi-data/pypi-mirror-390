#!/bin/bash
set -e
Rscript generate_partial_reporters.R
Rscript generate_partial_reporters_part2.R
