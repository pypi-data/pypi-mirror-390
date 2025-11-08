context("Item Imputation Part 1 Setup Logical Edits Tests")

source("../utils.R")
setEnvForTask("../../tasks/impute_items/part1_setup_logical_edits")

# Run task main script
system("Rscript 100_Run_Logical_Edits.R")

compareOutputToGoldStandard(
    listOfFiles[["part1_logical_edits"]],
    list(c()),
    output_folder[["part1_logical_edits"]]
    )
