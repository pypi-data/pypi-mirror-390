
state <- Sys.getenv("INPUT_STATE")

listOfFiles <- list()
output_folder <- list()
list_of_tests <- c("block_imputation")

listOfFiles[["block_imputation"]] <- c(
  "donorids.csv",
  "dat_m3_final_v3b.csv", 
  "NIBRS_INCIDENT_PLUS_IMPUTED_BLOCK.csv.gz"
  )
output_folder[["block_imputation"]] <- "/block_imputation_data/"

