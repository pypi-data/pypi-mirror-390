context("Partial Reporter Part 2 Tests")

source("../utils.R")

setEnvForTask("../../tasks/create_partial_reporters")

# Run task main script
system("Rscript generate_partial_reporters_part2.R")

# read in the output of the task and test that it looks as expected
first_output_file <- read.csv(file = paste0(Sys.getenv("OUTPUT_PIPELINE_DIR"),"/artifacts/NIBRS_reporting_pattern_with_reta-mm.csv"))
previous_output_file <- read.csv(file = paste0(Sys.getenv("OUTPUT_PIPELINE_DIR"),"/artifacts/NIBRS_reporting_pattern.csv"))

month_list <- c("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct",
  "nov", "dec")

test_that("output files are not empty", {
  expect_false(nrow(first_output_file) == 0)
  expect_false(ncol(first_output_file) == 0)
})

test_that("the two reta-mm files have the same number of rows as their input", {
  # this step should not have changed the number of rows
  expect_equal(nrow(first_output_file), nrow(previous_output_file))
})

test_that("there are are the correct number of years and agencies covered in the reta output file", {
  expect_true(2017 %in% first_output_file[, "incident_year"])
  expect_true(2018 %in% first_output_file[, "incident_year"])
  expect_true(2019 %in% first_output_file[, "incident_year"])
  expect_true(2020 %in% first_output_file[, "incident_year"])
})

test_that("month flag variables have realistic values for the reta output file. ", {
  # numeric flag variables should be binary or 9 if unknown
  for (month in month_list) {
    expect_true(
      all(unique(first_output_file[, paste0(toupper(month), "_MM_FLAG")]) %in% c(0,1,9,NA))

    )
  }

})

test_that("TRUE/FALSE flag variables have realistic values for the reta output file. ", {
  # string flag variables should be Y/N or "" if unknown
  y_n_flag_vars = c(
    "nibrs_agn_direct_contributor_flag"
  )
  for(col in y_n_flag_vars) {
    expect_true(
      all(first_output_file[,col] %in% c(TRUE,FALSE), na.rm = TRUE)
    )
  }
})


test_that("flag variables have realistic values for the reta output file. ", {
  # string flag variables should be Y/N or "" if unknown
  y_n_flag_vars = c(
    "nibrs_agn_dormant_flag",
    "nibrs_agn_suburban_area_flag",
    "nibrs_agn_nibrs_leoka_except_flag",
    "nibrs_agn_publishable_flag",
    "nibrs_agn_nibrs_participated",
    "nibrs_agn_covered_flag",
    "PUBLISHABLE_FLAG",
    "COVERED_FLAG",
    "DORMANT_FLAG",
    "COVERING_FLAG"
  )
  for(col in y_n_flag_vars) {
    expect_true(
      all(first_output_file[,col] %in% c("Y","N",""), na.rm = TRUE)
    )
  }
})

compareOutputToGoldStandard(
  listOfFiles[["partial_reporter_part2"]],
  list(c()),
  output_folder[["partial_reporter_part2"]]
  )
