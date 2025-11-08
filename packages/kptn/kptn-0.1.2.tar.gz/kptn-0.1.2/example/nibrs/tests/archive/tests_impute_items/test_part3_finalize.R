context("Item Imputation Part 3 Finalize Tests")

source("../utils.R")
setEnvForTask("../../tasks/impute_items/part3_finalize")

# Run task main script
system("Rscript 100_Run_Impute_Final_Steps.R")

imputed_fields <- list(
  c(),
  c("sex_code_victim2","race_id_victim2","age_num_victim2"),
  c(),
  c(),
  c(),
  c()
)


compareOutputToGoldStandard(
  listOfFiles[["part3_finalize"]],
  imputed_fields,
  output_folder[["part3_finalize"]]
  )