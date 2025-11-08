context("NIBRS Extract Victim Offender Relationships")

source("../utils.R")
setEnvForTask("../../tasks/create_nibrs_extracts/victim_offender_relationship")

# Run task main script
system("Rscript 100-Run_Program.R")

compareOutputToGoldStandard(
  listOfFiles[["victim_offender_rel"]],
  list(c(),c(),c()),
  output_folder[["victim_offender_rel"]]
)