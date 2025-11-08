context("Item Imputation Part 4 Victim Offender Relationship Tests")

source("../utils.R")
setEnvForTask("../../tasks/impute_items/part4_victim_offender")

# Run task main script
system("Rscript 100-Run_Programs_relationship_id.R")

imputed_fields <- list(
  c(),
  c("der_relationship"),
  c("der_relationship")
)

compareOutputToGoldStandard(
  listOfFiles[["part4_victim_offender"]],
  imputed_fields,
  output_folder[["part4_victim_offender"]]
  )