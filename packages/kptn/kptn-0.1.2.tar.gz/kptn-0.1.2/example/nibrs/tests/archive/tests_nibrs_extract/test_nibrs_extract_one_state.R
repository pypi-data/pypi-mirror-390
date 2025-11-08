context("NIBRS Extract one State Tests")


source("../utils.R")
setEnvForTask("../../tasks/create_nibrs_extracts/extract_one_state")

# Run task main script
system("Rscript 100-Run_Program.R")

compareOutputToGoldStandard(
  listOfFiles[["one_state"]],
  list(c(),c(),c()),
  output_folder[["one_state"]]
)
