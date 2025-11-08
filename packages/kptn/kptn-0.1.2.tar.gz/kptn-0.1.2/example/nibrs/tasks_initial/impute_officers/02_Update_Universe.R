###-------------------------------------------------------------------------------
### Read the libraries
###-------------------------------------------------------------------------------

library(tidyverse)
library(rjson)
library(readxl)
library(DT)

###-------------------------------------------------------------------------------


###-------------------------------------------------------------------------------
### Set up what's needed to run in pipeline

source(here::here("tasks/logging.R"))
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))

inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")

file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", inputPipelineDir))

# YEAR
CONST_YEAR <- Sys.getenv("DATA_YEAR")

CONST_INPUT_OFFICER <- paste0(outputPipelineDir, "/initial_tasks_output/officer_imputation/")
CONST_OUTPUT <- paste0(outputPipelineDir, "/initial_tasks_output/")


###-------------------------------------------------------------------------------


###Create additional functions
trim_upper <- compose(toupper, partial(trimws, which="both"))

###-------------------------------------------------------------------------------

#Read in the current universe file
raw_universe <- read_csv(paste0(CONST_OUTPUT, "orig_ref_agency_", CONST_YEAR, ".csv"), guess_max=10000 )

#Read in the output from the officer imputation
raw_officer <- read_csv(paste0(CONST_INPUT_OFFICER, "ORI_Level_Officer_Imputed_in_model.csv.gz"), guess_max=10000) %>%
  select(ORI, MALE_OFFICER_UNIV, FEMALE_OFFICER_UNIV, MALE_CIVILIAN_UNIV, FEMALE_CIVILIAN_UNIV)

#Next need to rename the officer variables in the raw_universe file

raw_universe2 <- raw_universe %>%
  rename(
    ORIG_PE_MALE_OFFICER_COUNT          =PE_MALE_OFFICER_COUNT,
    ORIG_PE_MALE_CIVILIAN_COUNT         =PE_MALE_CIVILIAN_COUNT,
    `ORIG_MALE_OFFICER+MALE_CIVILIAN`   =`MALE_OFFICER+MALE_CIVILIAN`,
    
    ORIG_PE_FEMALE_OFFICER_COUNT         =PE_FEMALE_OFFICER_COUNT,
    ORIG_PE_FEMALE_CIVILIAN_COUNT        =PE_FEMALE_CIVILIAN_COUNT,
    `ORIG_FEMALE_OFFICER+FEMALE_CIVILIAN`=`FEMALE_OFFICER+FEMALE_CIVILIAN`
)
  
#Using raw_universe2 and raw_officer, merge the two dataset together
tbd_good <- raw_universe2 %>%
  inner_join(raw_officer %>% mutate(tbd_in_officer=1), by= c("ORI"))

tbd_bad <- raw_universe2 %>%
  anti_join(raw_officer, by= c("ORI"))

tbd_good2 <- tbd_bad %>%
  inner_join(raw_officer %>% mutate(tbd_in_officer=1), by= c("LEGACY_ORI" = "ORI"))

tbd_bad2 <- tbd_bad %>%
  anti_join(raw_officer, by= c("LEGACY_ORI" = "ORI"))

#Put the universe file together
raw_universe3 <- bind_rows(tbd_good, tbd_good2, tbd_bad2)

#Check the dim
log_dim(raw_universe3)
log_dim(tbd_good)
log_dim(tbd_bad)
log_dim(tbd_good2)
log_dim(tbd_bad2)

#Should add up
log_dim(raw_officer)
log_dim(tbd_good)
log_dim(tbd_good2)

#Should be the same # of records
log_dim(raw_universe3)
log_dim(raw_universe2)

#Check the frequencies
log_dim(raw_officer)
table(raw_universe3$tbd_in_officer, useNA="always")

#Next rename the officer variables
raw_universe4 <- raw_universe3 %>%
  #Drop the tbd variables
  select(-tbd_in_officer) %>%
  #Create the officer count variables
  #Note we only impute the eligible NIBRS agencies, but will add on the original
  #just in case someone needs to use them.
  mutate(
    
    PE_MALE_OFFICER_COUNT = fcase(
      !is.na(MALE_OFFICER_UNIV), MALE_OFFICER_UNIV,
      !is.na(ORIG_PE_MALE_OFFICER_COUNT), ORIG_PE_MALE_OFFICER_COUNT
    ),
    
    PE_FEMALE_OFFICER_COUNT = fcase(
      !is.na(FEMALE_OFFICER_UNIV), FEMALE_OFFICER_UNIV,
      !is.na(ORIG_PE_FEMALE_OFFICER_COUNT), ORIG_PE_FEMALE_OFFICER_COUNT
    ),    
    
    
    PE_MALE_CIVILIAN_COUNT = fcase(
      !is.na(MALE_CIVILIAN_UNIV), MALE_CIVILIAN_UNIV,
      !is.na(ORIG_PE_MALE_CIVILIAN_COUNT), ORIG_PE_MALE_CIVILIAN_COUNT
    ),   
    
    PE_FEMALE_CIVILIAN_COUNT = fcase(
      !is.na(FEMALE_CIVILIAN_UNIV), FEMALE_CIVILIAN_UNIV,
      !is.na(ORIG_PE_FEMALE_CIVILIAN_COUNT), ORIG_PE_FEMALE_CIVILIAN_COUNT
    )  
  ) 

#Check the recodes
raw_universe4 %>% checkfunction(PE_MALE_OFFICER_COUNT, MALE_OFFICER_UNIV, ORIG_PE_MALE_OFFICER_COUNT)
raw_universe4 %>% checkfunction(PE_FEMALE_OFFICER_COUNT, FEMALE_OFFICER_UNIV, ORIG_PE_FEMALE_OFFICER_COUNT)
raw_universe4 %>% checkfunction(PE_MALE_CIVILIAN_COUNT, MALE_CIVILIAN_UNIV, ORIG_PE_MALE_CIVILIAN_COUNT)
raw_universe4 %>% checkfunction(PE_FEMALE_CIVILIAN_COUNT, FEMALE_CIVILIAN_UNIV, ORIG_PE_FEMALE_CIVILIAN_COUNT)

#Check to see which agencies have higher counts and make sure it is fine
raw_universe4 %>% filter(ORIG_PE_MALE_OFFICER_COUNT > MALE_OFFICER_UNIV) %>% select(ORI, NCIC_AGENCY_NAME, ORIG_PE_MALE_OFFICER_COUNT, MALE_OFFICER_UNIV) %>% datatable()
raw_universe4 %>% filter(ORIG_PE_FEMALE_OFFICER_COUNT > FEMALE_OFFICER_UNIV) %>% select(ORI, NCIC_AGENCY_NAME, ORIG_PE_FEMALE_OFFICER_COUNT, FEMALE_OFFICER_UNIV) %>% datatable()

raw_universe4 %>% filter(ORIG_PE_MALE_CIVILIAN_COUNT > MALE_CIVILIAN_UNIV) %>% select(ORI, NCIC_AGENCY_NAME, ORIG_PE_MALE_CIVILIAN_COUNT, MALE_CIVILIAN_UNIV) %>% datatable()
raw_universe4 %>% filter(ORIG_PE_FEMALE_CIVILIAN_COUNT > FEMALE_CIVILIAN_UNIV) %>% select(ORI, NCIC_AGENCY_NAME, ORIG_PE_FEMALE_CIVILIAN_COUNT, FEMALE_CIVILIAN_UNIV) %>% datatable()
  
#Next need to make the aggregate variable
raw_universe5 <- raw_universe4 %>%
  rowwise() %>%
  mutate(
    `MALE_OFFICER+MALE_CIVILIAN`     = sum(PE_MALE_OFFICER_COUNT, PE_MALE_CIVILIAN_COUNT),
    `FEMALE_OFFICER+FEMALE_CIVILIAN` = sum(PE_FEMALE_OFFICER_COUNT, PE_FEMALE_CIVILIAN_COUNT)
  ) %>%
  #Drop the original imputed officer variables
  select(-MALE_OFFICER_UNIV, -FEMALE_OFFICER_UNIV, -MALE_CIVILIAN_UNIV, -FEMALE_CIVILIAN_UNIV)

#Check the recodes
raw_universe5 %>% checkfunction(`MALE_OFFICER+MALE_CIVILIAN`, PE_MALE_OFFICER_COUNT, PE_MALE_CIVILIAN_COUNT)
raw_universe5 %>% checkfunction(`FEMALE_OFFICER+FEMALE_CIVILIAN`, PE_FEMALE_OFFICER_COUNT, PE_FEMALE_CIVILIAN_COUNT)

#Output to share
raw_universe5 %>%
  write_csv(paste0(CONST_OUTPUT, "ref_agency_", CONST_YEAR, ".csv"), na="")

# rename the back year universe files so the tasks that need them don't fail
years <- seq(as.numeric(CONST_YEAR)-4,as.numeric(CONST_YEAR)-1)

# Rename files
for (y in years) {
  file.rename(from = paste0(CONST_OUTPUT, "orig_ref_agency_", y, ".csv"), 
              to = paste0(CONST_OUTPUT, "ref_agency_", y, ".csv"))
}