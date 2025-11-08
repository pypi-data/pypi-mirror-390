context("Partial Reporter Part 1 Tests")

source("../utils.R")

setEnvForTask("../../tasks/create_partial_reporters")

# Run task main script
system("Rscript generate_partial_reporters.R")

# read in the output of the task and test that it looks as expected
output_df <- read.csv(file = paste0(Sys.getenv("OUTPUT_PIPELINE_DIR"),"/artifacts/NIBRS_reporting_pattern.csv"))

month_list <- c("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct",
  "nov", "dec")
section_list <- c("_part1v", "_part1p", "_otherc", "_all")

test_that("output file is not empty", {
  expect_false(nrow(output_df) == 0)
  expect_false(ncol(output_df) == 0)
})

test_that("there are the correct number of years and agencies covered", {
  expect_true(2017 %in% output_df[, "incident_year"])
  expect_true(2018 %in% output_df[, "incident_year"])
  expect_true(2019 %in% output_df[, "incident_year"])
  expect_true(2020 %in% output_df[, "incident_year"])
})

test_that("the counts and ratios have reasonable values", {
  # crime counts should be non-negative
  for (sec in section_list) {
    expect_true(all(output_df[, paste0("nibrs_total_crime", sec)] >= 0, na.rm = TRUE))
    # missing months should be between 0 and 12
    expect_true(all(output_df[, paste0("nibrs_max_consecutive_month_missing",
      sec)] >= 0, na.rm = TRUE))
    expect_true(all(output_df[, paste0("nibrs_max_consecutive_month_missing",
      sec)] <= 12, na.rm = TRUE))

  }

  for (month in month_list) {
    for (sec in section_list) {
      # each monthly crime count should also be non-negative
      expect_true(all(output_df[, paste0(month, sec)] >= 0, na.rm = TRUE))
    }
    # the ratios should be greater than 0 with some NA
    expect_true(all(output_df[, paste0(month, "_ratio_v_p")] >= 0, na.rm = TRUE))
  }
})


test_that("erroneous null value was properly removed", {
  # check that the values 9218868437227407266 aren't showing up anywhere
  # this value was appearing in the place of nulls due to a bug, and had to be
  # specifically identified and fixed in the code
  for (col in colnames(output_df)) {
    expect_false("9218868437227407266" %in% output_df[, col])
    expect_false(9218868437227407360 %in% output_df[, col])
  }
})


compareOutputToGoldStandard(
  listOfFiles[["partial_reporter_part1"]],
  list(c()),
  output_folder[["partial_reporter_part1"]]
  )