suppressPackageStartupMessages({
    library(tidyverse)
    library(rjson)
})

inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
externalDir <- Sys.getenv("EXTERNAL_FILE_PATH")
year <- Sys.getenv("DATA_YEAR")
input_files_folder <- paste0(inputPipelineDir, "/initial_tasks_output/")

# Sleep to simulate a longer task.
Sys.sleep(5)


# Read from an external file.
external_paths <- fromJSON(file = paste0(inputPipelineDir, "/external_file_locations.json"))
universe <- read_csv(
    paste0(input_files_folder, "orig_ref_agency_", year, ".csv"),
    show_col_types = FALSE
)


# Create a file in the scratch directory.
taskOutputDir <- paste0(outputPipelineDir, "/smoketest")
if (! dir.exists(taskOutputDir)) {
    dir.create(taskOutputDir, recursive = TRUE)
}
sink(paste0(taskOutputDir, "/universe.txt"))
cat(nrow(universe))
sink()
