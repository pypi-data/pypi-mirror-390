print("Running setup for missing months")

list_of_tests <- c("missing_months")

res_list <- list()
listOfFiles <- list()
output_folder <- list()
listOfFiles[["missing_months"]] <-  c(
  "missing_months_2017.csv",
  "missing_months_2018.csv",
  "missing_months_2019.csv",
  "missing_months_2020.csv",
  "missing_months_2021.csv"
)
  
output_folder[["missing_months"]] <- "/artifacts/"