###-------------------------------------------------------------------------------
### Define libraries
###-------------------------------------------------------------------------------

library(tidyverse)
# library(openxlsx)
# library(haven)
# library(mice)
# library(miceadds)
# library(VIM)
# library(naniar)
# library(visdat)
# library(ggplot2)
# library(StatMatch)
# library(writexl)
# library(sas7bdat)
# library(sjmisc)
# library(gtools)
# library(zoo)
# library(reshape2)
# library(lazyeval)
library(data.table)

set.seed(5242023)

###-------------------------------------------------------------------------------
### Data preparation: Read in the imputed SRS file
###-------------------------------------------------------------------------------

#Okay to use read_csv as is since it is just a character ori variable and all numeric v variables
raw_converted_srs <- read_csv(paste0(filepathin, "SRS_Original_Combined.csv"))
log_dim(raw_converted_srs)


#Next need to create the final dataset and keep certain variables
final_converted_srs <- raw_converted_srs %>%
  select(ori, matches("v\\d+")) %>%
  #Note need to zero filled the NA v variables, the reasoning is that these agencies did not report
  #any incidents to NIBRS, so they are our 0 reporters
  mutate(
    across(
      .cols = matches("v\\d+"),
      .fns = ~ {
        replace_na(.x, replace = 0) 
        },
      .names="{.col}")
  )  %>%
  #Make ori into upper case
  rename(ORI = ori)

#Delete all the raw and tbd datasets
rm(list=c(ls(pattern="tbd"), setdiff(ls(pattern="raw"), "raw_srs_file_path")))

#Create a list or variables to be drop from the srs
CONST_DROP_VARS <- colnames(final_converted_srs) %>%
  as_tibble() %>%
  filter(value != "ORI") %>%
  select(value) %>%
  pull()

#See the list of variables
print(CONST_DROP_VARS)

###-------------------------------------------------------------------------------
### Data preparation: recoding and creating variables
###-------------------------------------------------------------------------------

# Read file created by Philip

tbd_srs <- read_csv(file.path(raw_srs_file_path,paste0("UCR_SRS_",year,"_clean_reta_mm_selected_vars.csv")))
log_dim(tbd_srs)

#Using srs0 need to identify the ori that are in the final_converted_srs and replace 
#their data with the converted SRS data

#Do the merge by ORI
tbd_good_1 <- tbd_srs %>%
  inner_join(final_converted_srs %>% select(ORI), by=c("ORI" = "ORI")) %>%
  #Create a temporary ORI variable for match
  mutate(ORI_MATCH = ORI)

tbd_bad_1 <- tbd_srs %>%
  anti_join(final_converted_srs %>% select(ORI), by=("ORI" = "ORI"))

#Do the remaining merge by ORI_UNIV

tbd_good_2 <- tbd_bad_1 %>%
  inner_join(final_converted_srs %>% select(ORI), by=c("ORI_UNIV" = "ORI")) %>%
  #Create a temporary ORI variable for match
  mutate(ORI_MATCH = ORI_UNIV)

tbd_bad_2 <- tbd_bad_1 %>%
  anti_join(final_converted_srs %>% select(ORI), by=c("ORI_UNIV" = "ORI"))

#Create the dataset
tbd_match    <- bind_rows(tbd_good_1, tbd_good_2)
tbd_no_match <- tbd_bad_2

#Check the dimension
log_dim(tbd_srs)
log_dim(final_converted_srs)
log_dim(tbd_match)
log_dim(tbd_no_match)


log_dim(tbd_good_1)
log_dim(tbd_bad_1)
log_dim(tbd_good_2)
log_dim(tbd_bad_2)

#Next using tbd_match, need to drop the v variables and mm flags and replace them
#with the converted version

#Need to drop the variables in common
tbd_match2 <- tbd_match %>%
  select(!!!paste0("-", CONST_DROP_VARS) %>% rlang:::parse_exprs() )

log_dim(tbd_match)
log_dim(tbd_match2)

#Next need to merge on the converted variables and create an indicator variable
tbd_match3 <- tbd_match2 %>%
  left_join(final_converted_srs %>% 
              mutate(der_in_nibrs_converted = 1), by=c("ORI_MATCH" = "ORI"))

#Check to see if everything merges
log_dim(tbd_match2)
log_dim(tbd_match3)
sum(tbd_match3$der_in_nibrs_converted)

#Using tbd_match3 and tbd_no_match, need to stack the dataset together to create
#the srs dataset 

srs <- bind_rows(tbd_match3, tbd_no_match)

#Check the dimension
log_dim(tbd_srs)
log_dim(srs)
log_dim(tbd_match3)
log_dim(tbd_no_match)


# Recode variables from character to numeric
srs <- srs %>% mutate(rpt_type  = 
                        fcase(
                          REPORTING_TYPE_UNIV =="I", 1,
                          REPORTING_TYPE_UNIV=="S", 2))

srs <- srs %>% mutate(suburb_flg  = 
                        fcase(
                          SUBURBAN_AREA_FLAG_UNIV=="Y", 1,
                          SUBURBAN_AREA_FLAG_UNIV=="N", 0))


srs <- srs %>% mutate(cover_flg  = 
                        fcase(
                          COVERED_FLAG_UNIV=="Y", 1,
                          COVERED_FLAG_UNIV=="N", 0))

srs <- srs %>% mutate(agn_status  = 
                        fcase(
                          AGENCY_STATUS_UNIV=="A", 1,
                          AGENCY_STATUS_UNIV=="D", 2,
                          AGENCY_STATUS_UNIV=="L", 3,
                          AGENCY_STATUS_UNIV=="F", 4))

srs <- srs %>% mutate(agn_type  = 
                        fcase(
                          AGENCY_TYPE_NAME_UNIV=="City", 1,
                          AGENCY_TYPE_NAME_UNIV=="County", 2,
                          AGENCY_TYPE_NAME_UNIV=="Federal", 3,
                          AGENCY_TYPE_NAME_UNIV=="Other", 4,
                          AGENCY_TYPE_NAME_UNIV=="Other State Agency", 5,
                          AGENCY_TYPE_NAME_UNIV=="State Police", 6,
                          AGENCY_TYPE_NAME_UNIV=="Tribal", 7,
                          AGENCY_TYPE_NAME_UNIV=="University or College", 8))

# Determine eligibility

states= c(
  "AL",     #Alabama
  "AK",     #Alaska
  "AZ",     #Arizona
  "AR",     #Arkansas
  "CA",     #California
  "CO",     #Colorado
  "CT",     #Connecticut
  "DE",     #Delaware
  "DC",     #District of Columbia
  "FL",     #Florida
  "GA",     #Georgia
  "HI",     #Hawaii
  "ID",     #Idaho
  "IL",     #Illinois
  "IN",     #Indiana
  "IA",     #Iowa
  "KS",     #Kansas
  "KY",     #Kentucky
  "LA",     #Louisiana
  "ME",     #Maine
  "MD",     #Maryland
  "MA",     #Massachusetts
  "MI",     #Michigan
  "MN",     #Minnesota
  "MS",     #Mississippi
  "MO",     #Missouri
  "MT",     #Montana
  "NB",     #Nebraska
  "NV",     #Nevada
  "NH",     #New Hampshire
  "NJ",     #New Jersey
  "NM",     #New Mexico
  "NY",     #New York
  "NC",     #North Carolina
  "ND",     #North Dakota
  "OH",     #Ohio
  "OK",     #Oklahoma
  "OR",     #Oregon
  "PA",     #Pennsylvania
  "RI",     #Rhode Island
  "SC",     #South Carolina
  "SD",     #South Dakota
  "TN",     #Tennessee
  "TX",     #Texas
  "UT",     #Utah
  "VT",     #Vermont
  "VA",     #Virginia
  "WA",     #Washington
  "WV",     #West Virginia
  "WI",     #Wisconsin
  "WY")     #Wyoming

trim_upper <- compose(toupper, partial(trimws, which="both"))

elig_recode <- function(data){
  
  returndata <- data %>% mutate(
    
    in_univ_elig_state = trim_upper(STATE_ABBR_UNIV) %in% states,
    
    der_in_univ_elig =  case_when(
      trim_upper(AGENCY_STATUS_UNIV) == "A" & 
        trim_upper(COVERED_FLAG_UNIV) == "N" &  
        trim_upper(DORMANT_FLAG_UNIV) == "N" &
        trim_upper(AGENCY_TYPE_NAME_UNIV) != "FEDERAL" &
        in_univ_elig_state == TRUE ~ 1,
      TRUE ~ 0)
  )
  
  #Return the data
  return(returndata)
}    

srs <- elig_recode(srs)

# Covering agencies - will be used to define imputation classes
covering <- srs %>% filter(!is.na(COVERED_BY_LEGACY_ORI_UNIV)) %>%
  select(COVERED_BY_LEGACY_ORI_UNIV) %>%
  rename(ORI_UNIV=COVERED_BY_LEGACY_ORI_UNIV) %>%
  mutate(coveringAgency=1) %>%
  distinct()

srs2 <- srs %>% left_join(covering,by="ORI_UNIV") %>% mutate(coveringAgency=coalesce(coveringAgency,0))

# Keep variables and records needed for imputation
srs3 <- srs2 %>% filter(data_year==year & der_in_univ_elig==1) %>%
  select(ORI,ORI_UNIV,ORI_MATCH,data_year,
         cover_flg, suburb_flg,
         rpt_type, agn_type, agn_status, coveringAgency,
         STATE_ID_UNIV, POPULATION_UNIV, REGION_CODE_UNIV, DIVISION_CODE_UNIV, POPULATION_GROUP_ID_UNIV,
         MALE_OFFICER_UNIV, MALE_CIVILIAN_UNIV, FEMALE_OFFICER_UNIV, FEMALE_CIVILIAN_UNIV, ends_with("_UNIV"),
         starts_with("v"), ends_with("mm_flag"))

#Output to the share
srs3 %>%
  write_csv(paste0(block_imputation_output, "Raw_SRS_Using_Converted.csv"), na="")


