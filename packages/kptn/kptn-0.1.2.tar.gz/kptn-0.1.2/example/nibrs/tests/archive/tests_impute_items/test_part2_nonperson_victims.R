context("Item Imputation Part 2 Nonperson Victims Tests")

source("../utils.R")
setEnvForTask("../../tasks/impute_items/part2_nonperson_victims")

# Run task main script
system("Rscript 100_Run_Nonperson_Victims.R")

imputed_fields <- list(
  c("sex_code_offender2","race_id_offender2","age_num_offender2","sex_code_arrestee2","race_id_arrestee2","age_num_arrestee2"),
  c(),
  c("sex_code_offender2","race_id_offender2","age_num_offender2"),
  c(),
  c("sex_code_arrestee2","race_id_arrestee2","age_num_arrestee2")
)


compareOutputToGoldStandard(
  listOfFiles[["part2_nonperson_victims"]],
  imputed_fields,
  output_folder[["part2_nonperson_victims"]]
  )
