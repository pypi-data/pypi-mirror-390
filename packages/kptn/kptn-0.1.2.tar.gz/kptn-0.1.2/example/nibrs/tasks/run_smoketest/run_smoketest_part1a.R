suppressPackageStartupMessages({
    library(DBI)
    library(tidyverse)
    library(bit64)
})

outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
year <- Sys.getenv("DATA_YEAR")


# Sleep to simulate a longer task.
Sys.sleep(10)


# Run a sample DB query.
con <- dbConnect(RPostgres::Postgres())
query <- dbSendQuery(con, "SELECT count(*) AS count FROM nibrs_incident WHERE data_year = $1")
dbBind(query, list(year))
df <- dbFetch(query)
dbClearResult(query)
dbDisconnect(con)


# Create a file in the scratch directory.
taskOutputDir <- paste0(outputPipelineDir, "/smoketest")
if (! dir.exists(taskOutputDir)) {
    dir.create(taskOutputDir, recursive = TRUE)
}
sink(paste0(taskOutputDir, "/db.txt"))
cat(as.character(df$count))
sink()
