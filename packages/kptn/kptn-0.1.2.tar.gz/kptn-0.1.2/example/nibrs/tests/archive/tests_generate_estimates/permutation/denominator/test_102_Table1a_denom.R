here::i_am("tests/tests_generate_estimates/permutation/denominator/test_102_Table1a_denom.R")
library(here)
library(data.table)
library(testthat)

# source(here("tasks/logging.R"))
source(here("tasks/generate_estimates/POP_create_percentage_denominator.R"))
source(here("tasks/generate_estimates/Permutation/denominator/102_Table1a_denom.R"))
mockdata_path <- here("tests/tests_generate_estimates/permutation/denominator/mockdata/test_102_Table1a_denom")

test_that("table1a denominator column is correct", {
  raw_percentage_2 <- fread(here(mockdata_path, "in_raw_percentage_2.csv"))
  main_reporting_db3 <- fread(here(mockdata_path, "in_main_reporting_db_3.csv"))
  expected_out <- fread(here(mockdata_path, "out.csv"))

  raw_percentage_3 <- set_table1a_denominator_column(raw_percentage_2, main_reporting_db3)
  expect_equal(raw_percentage_3$raw_denominator, expected_out$raw_denominator)
})
