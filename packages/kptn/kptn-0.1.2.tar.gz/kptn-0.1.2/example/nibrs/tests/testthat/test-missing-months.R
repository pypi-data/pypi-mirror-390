library(testthat)
library(withr)
library(fs)

# DESCRIPTION
#
# Tests the missing months script which generates a file that identifies which months
# each law enforcement agency reported NIBRS data.
# The script reads data from the NIBRS monthly reporting table and agency reference
# data (universe), then creates a file with month-by-month reporting flags
# (1=reported, 0=not reported) for each agency. This output is used in subsequent
# processing to identify reporting patterns and handle missing data appropriately.

# Delete temporary files that may exist from previous runs
unlink(tempdir(), recursive = TRUE, force = TRUE)

setup <- function(input_dir, output_dir, data_year) {

  # Create temporary directories and mock data
  dir.create(path(input_dir, "initial_tasks_output/database_queries"), recursive = TRUE)
  dir.create(path(output_dir, "artifacts"), recursive = TRUE)

  # Mock external_file_locations.json
  writeLines(
    '{"key": "value"}',
    path(input_dir, "external_file_locations.json")
  )

  # Each row represents a month that an agency reported data
  # ORI1: Jan, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec
  # ORI2: Feb
  # ORI3: Mar
  # ORI4: No months reported
  write.csv(
    data.frame(
      ori = c("ORI1", "ORI2", "ORI3", rep("ORI1", 9)),
      month_num = c(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12),
      stringsAsFactors = FALSE
    ),
    file = path(input_dir, paste0("initial_tasks_output/database_queries/nibrs_month_agencies_", data_year, ".csv.gz")),
    row.names = FALSE
  )

  # Mock universe data
  write.csv(
    data.frame(
      ORI = c("ORI1", "ORI2", "ORI3", "ORI4"),
      UCR_AGENCY_NAME = c("Agency 1", "Agency 2", "Agency 3", "Agency 4"),
      NIBRS_START_DATE = c("2020-01-01", "2020-01-01", "2020-01-01", "2020-01-01"),
      STATE_NAME = c(NA, NA, NA, NA),
      AGENCY_STATUS = c("A", "D", "F", "L"),
      PUBLISHABLE_FLAG = NA,
      COVERED_FLAG = NA,
      DORMANT_FLAG = NA,
      AGENCY_TYPE_NAME = NA,
      POPULATION = NA,
      PARENT_POP_GROUP_CODE = NA,
      DATA_YEAR = c(NA, NA, NA, NA)
    ),
    file = path(input_dir, paste0("initial_tasks_output/ref_agency_", data_year, ".csv")),
    row.names = FALSE
  )
}

test_that("Missing months output file has expected structure", {
  with_envvar(c(
    OUTPUT_PIPELINE_DIR = tempdir(),
    EXTERNAL_FILE_PATH = tempdir(),
    INPUT_PIPELINE_DIR = tempdir(),
    DATA_YEAR = "2020"
  ), {
    setup(Sys.getenv("INPUT_PIPELINE_DIR"), Sys.getenv("OUTPUT_PIPELINE_DIR"), Sys.getenv("DATA_YEAR"))

    # Run the main program
    source(here::here("tasks/missing_months/100-Run_Program.R"), keep.source = TRUE)

    output_file <- path(Sys.getenv("OUTPUT_PIPELINE_DIR"), "artifacts", paste0("missing_months_", Sys.getenv("DATA_YEAR"), ".csv"))
    expect_true(file.exists(output_file), info = "Output file was not created.")
    output_data <- read.csv(output_file, stringsAsFactors = FALSE, na.strings = "")

    # 1 row for each agency
    expected_data <- data.frame(
      STATE_NAME = rep(NA, 4),
      ORI = c("ORI1", "ORI2", "ORI3", "ORI4"),
      UCR_AGENCY_NAME = c("Agency 1", "Agency 2", "Agency 3", "Agency 4"),
      AGENCY_STATUS = c("Active", NA_character_, "Federal", "LEOKA"),
      PUBLISHABLE_FLAG = rep(NA, 4),
      COVERED_FLAG = rep(NA, 4),
      DORMANT_FLAG = rep(NA, 4),
      AGENCY_TYPE_NAME = rep(NA, 4),
      POPULATION = rep(NA, 4),
      PARENT_POP_GROUP_CODE = rep(NA, 4),
      DATA_YEAR = rep(NA, 4),
      JAN_MM_FLAG = c(1, 0, 0, 0),
      FEB_MM_FLAG = c(0, 1, 0, 0),
      MAR_MM_FLAG = c(0, 0, 1, 0),
      APR_MM_FLAG = c(1, 0, 0, 0),
      MAY_MM_FLAG = c(1, 0, 0, 0),
      JUN_MM_FLAG = c(1, 0, 0, 0),
      JUL_MM_FLAG = c(1, 0, 0, 0),
      AUG_MM_FLAG = c(1, 0, 0, 0),
      SEP_MM_FLAG = c(1, 0, 0, 0),
      OCT_MM_FLAG = c(1, 0, 0, 0),
      NOV_MM_FLAG = c(1, 0, 0, 0),
      DEC_MM_FLAG = c(1, 0, 0, 0),
      stringsAsFactors = FALSE
    )

    expect_equal(output_data, expected_data, info = "Output data does not match expected data.")
  })
})