state <- Sys.getenv("INPUT_STATE")

list_of_tests <- c("one_state","victim_offender_rel")

listOfFiles <- list()
output_folder <- list()

listOfFiles[["one_state"]] <- c(
  paste0("01_",state,"_extract.csv.gz"),
  paste0("01_",state,"_unknown_offenders_extract.csv.gz"),
  paste0("01_",state,"_victim_other_extract.csv.gz")
)
output_folder[["one_state"]] <- "/artifacts/"

listOfFiles[["victim_offender_rel"]] <- c(
  "00_Victim_Offender_rel_extract.csv.gz"
  )
output_folder[["victim_offender_rel"]] <- "/artifacts/"