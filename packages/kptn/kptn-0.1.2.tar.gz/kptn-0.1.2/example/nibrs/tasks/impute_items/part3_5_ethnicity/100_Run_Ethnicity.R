library("rmarkdown")
library("tidyverse")
library(RPostgres)
library(DT)
library(mice)
library(miceadds)
library(data.table)

source(here::here("tasks/logging.R"))

#Read in the common functions to be used in R
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))
source("../NIBRS_function.R")
source("../NIBRS_Offense_function.r")

#SET UP ALL THE NECESSARY INPUT/OUTPUT PATHS
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
filepathout = paste0(outputPipelineDir, "/markdown/") #output path for markdown files

if (! dir.exists(filepathout)) {
  dir.create(filepathout, recursive = TRUE)
}

mainpath = paste0(outputPipelineDir, "/item_imputation_data/") #output path for data

if (! dir.exists(mainpath)) {
  dir.create(mainpath, recursive = TRUE)
}

miscPathout = paste0(outputPipelineDir, "/item_imputation_misc/") #other misc item imputation output

if (! dir.exists(miscPathout)) {
  dir.create(miscPathout, recursive = TRUE)
}

read_csv <- partial(read_csv, guess_max = 1000000) #For now, read thru the 1st 1,000,000 rows to determine variable type
md.pattern <- partial(md.pattern, plot=FALSE)


#output location of create_NIBRS_extracts
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
inputmainpath = paste0(inputPipelineDir, "/item_imputation_data/") #input path for part 1 output
artifactsmainpath = paste0(inputPipelineDir, "/artifacts/") #input path for other task output

#Get the current number to process
input_state_group <- Sys.getenv("ETHNICITY_INPUT_NUM")
ctrl <- read_csv("./Data/Ethnicity_State_PERM.csv") %>%
  filter(ETH_PERM_NUM == as.numeric(input_state_group))

Sys.setenv(INPUT_STATE = ctrl$ETH_PERM_STATES)


# 10 Imputation when offender and arrestee match and the incident is cleared
log_info(paste0(input_state_group,": 10_MICE_Item_Missing_Imputation_arr_off_match_v3-non-person_Eth.Rmd starting..."))
rmarkdown::render("10_MICE_Item_Missing_Imputation_arr_off_match_v3-non-person_Eth.Rmd", output_format = html_document(),
                  output_file = paste0(filepathout, "10_MICE_Item_Missing_Imputation_arr_off_match_v3-non-person_Eth_", input_state_group, ".html"),
                  envir = new.env(), quiet = TRUE)
invisible(gc())
knitr::knit_meta(clean = TRUE)


# 12 Imputation of offender when offender and arrestee do not match and the incident is cleared
log_info(paste0(input_state_group,": 12_MICE_Item_Missing_Imputation_offender_v3-non-person_Eth.Rmd starting..."))
rmarkdown::render("12_MICE_Item_Missing_Imputation_offender_v3-non-person_Eth.Rmd", output_format = html_document(),
                  output_file = paste0(filepathout, "12_MICE_Item_Missing_Imputation_offender_v3-non-person_Eth_", input_state_group, ".html"),
                  envir = new.env(), quiet = TRUE)
invisible(gc())
knitr::knit_meta(clean = TRUE)

# 14 Imputation of arrestee when offender and arrestee do not match and the incident is cleared
log_info(paste0(input_state_group,": 14_MICE_Item_Missing_Imputation_Arrestee_v3-non-person_Eth.Rmd starting..."))
rmarkdown::render("14_MICE_Item_Missing_Imputation_Arrestee_v3-non-person_Eth.Rmd", output_format = html_document(),
                  output_file = paste0(filepathout, "14_MICE_Item_Missing_Imputation_Arrestee_v3-non-person_Eth_", input_state_group, ".html"),
                  envir = new.env(), quiet = TRUE)
invisible(gc())
knitr::knit_meta(clean = TRUE)

###################Start of Person Victim Imputation#####################################################

# 03 Impute Offender/Arrestee when they match
log_info(paste0(input_state_group,": 03_MICE_Item_Missing_Imputation_arrestee_offender_match_v3_Eth.Rmd starting..."))
rmarkdown::render("03_MICE_Item_Missing_Imputation_arrestee_offender_match_v3_Eth.Rmd",
                  output_format = html_document(),
                  output_file = paste0(filepathout, "03_MICE_Item_Missing_Imputation_arrestee_offender_match_v3_Eth_", input_state_group, ".html"),
                  envir = new.env(), quiet = TRUE)
invisible(gc())
knitr::knit_meta(clean = TRUE)


# 05 Impute Offender when offender/arrestee don't match
log_info(paste0(input_state_group,": 05_MICE_Item_Missing_Imputation_offender_v3_Eth.Rmd starting..."))
rmarkdown::render("05_MICE_Item_Missing_Imputation_offender_v3_Eth.Rmd",
                  output_format = html_document(),
                  output_file = paste0(filepathout, "05_MICE_Item_Missing_Imputation_offender_v3_Eth_", input_state_group, ".html"),
                  envir = new.env(), quiet = TRUE)
invisible(gc())
knitr::knit_meta(clean = TRUE)


# 07 Impute Victim
log_info(paste0(input_state_group,": 07_MICE_Item_Missing_Imputation_victim_v3_Eth.Rmd starting..."))
rmarkdown::render("07_MICE_Item_Missing_Imputation_victim_v3_Eth.Rmd",
                  output_format = html_document(),
                  output_file = paste0(filepathout, "07_MICE_Item_Missing_Imputation_victim_v3_Eth_", input_state_group, ".html"),
                  envir = new.env(), quiet = TRUE)
invisible(gc())
knitr::knit_meta(clean = TRUE)


# 09 Impute Arrestee when offender/arrestee do not match
log_info(paste0(input_state_group,": 09_MICE_Item_Missing_Imputation_Arrestee_v3_Eth.Rmd starting..."))
rmarkdown::render("09_MICE_Item_Missing_Imputation_Arrestee_v3_Eth.Rmd",
                  output_format = html_document(),
                  output_file = paste0(filepathout, "09_MICE_Item_Missing_Imputation_Arrestee_v3_Eth_", input_state_group, ".html"),
                  envir = new.env(), quiet = TRUE)
invisible(gc())
knitr::knit_meta(clean = TRUE)

#######################################Victim Uncleared###########################################
# 16 Impute victim Uncleared
log_info(paste0(input_state_group,": 16_MICE_Item_Missing_Imputation_victim_v3_Uncleared_Eth.Rmd starting..."))
rmarkdown::render("16_MICE_Item_Missing_Imputation_victim_v3_Uncleared_Eth.Rmd",
                  output_format = html_document(),
                  output_file = paste0(filepathout, "16_MICE_Item_Missing_Imputation_victim_v3_Uncleared_Eth_", input_state_group, ".html"),
                  envir = new.env(), quiet = TRUE)
invisible(gc())
knitr::knit_meta(clean = TRUE)




