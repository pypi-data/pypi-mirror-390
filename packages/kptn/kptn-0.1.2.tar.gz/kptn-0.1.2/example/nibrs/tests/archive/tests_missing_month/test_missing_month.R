context("Missing Month Tests")

source("../utils.R")
setEnvForTask("../../tasks/missing_months")
source(here::here("tasks/logging.R"))
con <- dbConnect(RPostgres::Postgres())
year_query <- 
  "SELECT DISTINCT EXTRACT(year FROM nibrs_incident.incident_date) AS data_year
   FROM ucr_prd.nibrs_incident"
list_of_years <- time_query(con,year_query)

old_data_year <- Sys.getenv("DATA_YEAR")
# Run task main script
for (y in list_of_years$data_year){
    Sys.setenv(DATA_YEAR = y)
    system("Rscript 100-Run_Program.R")
}
Sys.setenv(DATA_YEAR = old_data_year)
compareOutputToGoldStandard(listOfFiles[["missing_months"]], list(c(),c(),c(),c(),c()),output_folder[["missing_months"]])