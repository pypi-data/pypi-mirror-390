state <- Sys.getenv("INPUT_STATE")

list_of_tests <- c(
    "part1_logical_edits",
    "part2_nonperson_victims",
    "part2_person_victims",
    "part3_finalize",
    "part4_victim_offender"
    )

output_folder <- list()
listOfFiles <- list()

output_folder[["part1_logical_edits"]] <- "/item_imputation_data/"
listOfFiles[["part1_logical_edits"]] <- c(
  c(paste0("02_",state,"_logical_edits.csv.gz"))
)

output_folder[["part2_nonperson_victims"]] <- "/item_imputation_data/"
listOfFiles[["part2_nonperson_victims"]] <- c(
  paste0("10_",state,"_imputed_arrestee_offender_match.csv.gz"),
  paste0("11_",state,"_offender_for_imputation.csv.gz"),
  paste0("12_",state,"_offender_imputed.csv.gz"),
  paste0("13_",state,"_arrestee_for_imputation.csv.gz"),
  paste0("14_",state,"_arrestee_imputed_final.csv.gz")
)

output_folder[["part2_person_victims"]] <- "/item_imputation_data/"
listOfFiles[["part2_person_victims"]] <- c(
  paste0("03_",state,"_imputed_arrestee_offender_match.csv.gz"),
  paste0("04_",state,"_offender_for_imputation.csv.gz"),
  paste0("05_",state,"_offender_imputed.csv.gz"),
  paste0("06_",state,"_victim_for_imputation.csv.gz"),
  paste0("07_",state,"_victim_imputed_final.csv.gz"),
  paste0("08_",state,"_arrestee_for_imputation.csv.gz"),
  paste0("09_",state,"_arrestee_imputed_final.csv.gz")
)

output_folder[["part3_finalize"]] <- "/item_imputation_data/"
listOfFiles[["part3_finalize"]] <- c(
  paste0("15_",state,"_victim_for_imputation.csv.gz"),
  paste0("16_",state,"_victim_imputed_final.csv.gz"),
  paste0("17_",state,"_Combined.csv.gz"),
  paste0("17_",state,"_victim_imputed_final_flag.csv.gz"),
  paste0("17_",state,"_offender_imputed_final_flag.csv.gz"),
  paste0("17_",state,"_arrestee_imputed_final_flag.csv.gz")
)

output_folder[["part4_victim_offender"]] <- "/item_imputation_data/"
listOfFiles[["part4_victim_offender"]] <- c(
  paste0("01_",state,"_recoded_for_imputation.csv.gz"),
  paste0("04_imputed_relationship_id_offender_le3_",state,".csv.gz"),
  paste0("04_imputed_relationship_id_offender_gt3_",state,".csv.gz")
)