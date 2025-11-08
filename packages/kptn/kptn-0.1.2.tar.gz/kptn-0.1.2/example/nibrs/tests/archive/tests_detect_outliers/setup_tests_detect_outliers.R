state <- Sys.getenv("INPUT_STATE")
list_of_tests <- c("outlier_detection")

listOfFiles <- list()
output_folder <- list()

listOfFiles[["outlier_detection"]] <- c("outlier_data_file.csv")
output_folder[["outlier_detection"]] <- "/outlier_data/"