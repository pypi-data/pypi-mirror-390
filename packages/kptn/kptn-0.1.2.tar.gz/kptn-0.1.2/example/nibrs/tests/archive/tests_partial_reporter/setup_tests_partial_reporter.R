data_year = Sys.getenv("DATA_YEAR")

list_of_tests <- c("partial_reporter_part1","partial_reporter_part2")

listOfFiles <- list()
output_folder <- list()

listOfFiles[["partial_reporter_part1"]] <- c(
  paste0("NIBRS_reporting_pattern.csv")
  )
output_folder[["partial_reporter_part1"]] <- "/artifacts/"

listOfFiles[["partial_reporter_part2"]] <- c(
  paste0("NIBRS_reporting_pattern_with_reta-mm.csv")
  )
output_folder[["partial_reporter_part2"]] <- "/artifacts/"