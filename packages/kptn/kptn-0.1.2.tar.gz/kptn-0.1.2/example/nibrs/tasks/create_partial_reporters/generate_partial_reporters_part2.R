
library(dplyr)
library(dbplyr)
library(tidyverse)

library(openxlsx)
library(DT)
library(lubridate)
library(rjson)

# read in logging functions
source(here::here("tasks/logging.R"))

#Create extra functions
tablena <- partial(table, useNA = "ifany")
trim_upper <- compose(toupper, partial(trimws, which="both"))
trim <- partial(trimws, which="both")


checkfunction <- function(data, ...){
  
  groupbyinput <- rlang:::enquos(...)
  grouped_data <- data %>% group_by( !!!(groupbyinput) ) %>% summarise(count = n() )
  datatable( grouped_data %>% print())
  log_debug(twodlist_tostring(grouped_data))
}

outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")
year <- as.integer(Sys.getenv("DATA_YEAR"))

output_folder <- sprintf("%s/artifacts", outputPipelineDir)
input_folder <- sprintf("%s/artifacts", inputPipelineDir)
input_files_folder <- paste0(inputPipelineDir, "/initial_tasks_output/")
queried_data_path = paste0(outputPipelineDir, "/initial_tasks_output/database_queries/")

file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", inputPipelineDir))

log_info("generate_partial_reporters_part2.R starting...")

list_of_years <- seq(year - 4, year)

#Edit for 1993 - 2023 update, need to tweak the amount of files available for the early years
if(year == 1993){
  list_of_years <- list_of_years[3:5]
} else if(year == 1994){
  list_of_years <- list_of_years[2:5]
} else {
  list_of_years <- list_of_years 
}

# read in agencies table and df2 (agency county info for last 5 years)
tbd_agency_table <- read_csv(file=paste0(queried_data_path, "agencies_five_years.csv.gz"))

#Deduplicate the universe file in case of duplicates due to dormant agencies
tbd_agency_table1 <- tbd_agency_table %>%
  group_by(data_year, ori) %>%
  mutate(
    tbd_keep_first = row_number() == 1
  ) %>%
  ungroup() %>%
  #Keep one agency per year.  Duplicate often happen for dormant agencies
  filter(tbd_keep_first == TRUE) %>%
  select(-tbd_keep_first)  

#Check the dimension
log_dim(tbd_agency_table1)
log_dim(tbd_agency_table)


#Create the agency_table
agency_table <- tbd_agency_table1

#Remove the tbd data
rm(list=ls(pattern="tbd_"))
invisible(gc())

df2 <- read_csv(file=paste0(queried_data_path, "agencies_counties_", year-4, "_", year, ".csv.gz"))

df3 <- left_join(agency_table, df2, by=c("agency_id"="agency_id", "data_year"="data_year") )


df3_good <- df3 %>% group_by(agency_id, data_year) %>% mutate(raw_first_id_year = row_number() == 1,
                                                              raw_last_row = row_number() ==  max(row_number()),
                                                              raw_first_last_id_year = (raw_first_id_year == TRUE) & (raw_last_row==TRUE) ) %>% filter(raw_first_last_id_year == TRUE)

df3_bad <-  df3 %>% group_by(agency_id, data_year) %>% mutate(raw_first_id_year = row_number() == 1,
                                                              raw_last_row = row_number() ==  max(row_number()),
                                                              raw_first_last_id_year = (raw_first_id_year == TRUE) & (raw_last_row==TRUE) ) %>% filter(raw_first_last_id_year == FALSE)


#Need to collapse the df3_bad to have one record on the variable fips_code and county_name

dedup_county <- function(){
  log_debug("Running function dedup_county")
  
  #Declare temporary variables
  temp_fips_code_all = NA
  temp_county_code_all = NA
  temp_county_name_all = NA
  
  #Make sure the dataset is sorted
  df3_bad <- df3_bad %>% group_by(agency_id, data_year)
  
  #Loop though the dataset and combine the county variables
  for(i in 1:nrow(df3_bad)) {
    
    if (df3_bad[i, "raw_first_id_year"] == TRUE){
      #Initialize
      temp_fips_code_all = df3_bad[i, "fips_code_all"]
      temp_county_code_all = df3_bad[i, "county_fips_code_all"]
      temp_county_name_all = df3_bad[i, "county_name_all"]
    }else if((df3_bad[i, "raw_first_id_year"] == FALSE)){
      #Add on to the list
      temp_fips_code_all = paste(temp_fips_code_all    , df3_bad[i, "fips_code_all"],sep = ";")
      temp_county_code_all = paste(temp_county_code_all, df3_bad[i, "county_fips_code_all"],sep = ";")
      temp_county_name_all = paste(temp_county_name_all, df3_bad[i, "county_name_all"],sep = ";")
    }
    
    #When on the final row, overwrite the variables and output
    
    if (df3_bad[i, "raw_last_row"] == TRUE){
      df3_bad[i, "fips_code_all"]         = temp_fips_code_all
      df3_bad[i, "county_fips_code_all"]  = temp_county_code_all
      df3_bad[i, "county_name_all"]       = temp_county_name_all
      
      #Reset the temporary variables
      temp_fips_code_all = NA
      temp_county_code_all = NA
      temp_county_name_all = NA
    }
  }
  
  #Ungroup the dataset and return the last record for each grouping
  df3_bad %>% ungroup() %>% filter(raw_last_row==TRUE)
}

df3_good_2 <- dedup_county()

#Combine good and dedup
keep <- bind_rows(df3_good, df3_good_2)

#Check the dimensions
log_dim(agency_table)
log_dim(keep)
log_dim(df3_good)
log_dim(df3_good_2)



#Drop the raw variables
keep <- keep %>% select(-starts_with("raw_") )


#Clean the workspace
rawlist <- ls(pattern="^df")

rm(list=as.character(c(rawlist, "rawlist") ))
invisible(gc())

df1 <- keep %>% ungroup()

rm(keep)

#Update on 20200728, use the above df1 dataset and create the eligibility variable
df4 <- agency_table

#Lists of States
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

df4_recode <- df4 %>%
  mutate(
    
    in_univ_elig_state = trim_upper(state_abbr) %in% states,
    
    in_univ_elig = fcase(
      trim_upper(agency_status) == "A" &
      trim_upper(covered_flag) == "N" &
      trim_upper(dormant_flag) == "N" &
      trim_upper(agency_type_name) != "FEDERAL" & 
      in_univ_elig_state == TRUE, 1,
      default = 0)
    )

df4_recode %>% checkfunction(in_univ_elig_state, state_abbr)
df4_recode %>% checkfunction(in_univ_elig,
                             agency_status,
                             covered_flag,
                             dormant_flag,
                             agency_type_name,
                             in_univ_elig_state)

keep <- df1 %>% left_join(df4_recode %>%
                            select(data_year, agency_id, in_univ_elig),
                          by=c("data_year", "agency_id"))


#Make sure non-missing
keep %>% checkfunction(in_univ_elig)
keep %>% checkfunction(data_year, in_univ_elig)
keep %>% checkfunction(data_year,state_abbr, in_univ_elig)

#Clean the workspace
rawlist <- ls(pattern="^df")

rm(list=as.character(c(rawlist, "rawlist") ))

df1 <- keep
rm(keep)


invisible(gc())


#Create a new function to trim and upcase to handle character variables
trim_upcase <- compose(toupper, partial(trimws, which="both"))
table_func <- partial(table, useNA="ifany")
sum_func <- partial(sum, na.rm=TRUE)


#Merge on the Missing files
mainfile <- paste0(input_folder,"/NIBRS_reporting_pattern.csv")

#Read the datasets

maindata <- read_csv(mainfile) %>% mutate(STATE = substr(trim_upcase(ori), 1, 2))

#Keep only the records with non-missing ORIs
maindata <- maindata %>% filter(!is.na(trim_upcase(ori)))

raw_list <- map(list_of_years, ~ read_csv(file.path(input_folder, paste0("missing_months_",.x,".csv"))) %>% mutate(incident_year = .x, in_reta_mm = 1, STATE = substr(trim_upcase(ORI), 1, 2)))


tbd_mainmissing <- bind_rows(raw_list)

#Need to deduplicate the file
tbd_mainmissing_1 <- tbd_mainmissing %>%
  group_by(DATA_YEAR, ORI) %>%
  mutate(
    tbd_keep_first = row_number() == 1
  ) %>%
  ungroup() %>%
  #Keep one agency per year.  Duplicate often happen for dormant agencies
  filter(tbd_keep_first == TRUE) %>%
  select(-tbd_keep_first)

#Check the dimension
log_dim(tbd_mainmissing_1)
log_dim(tbd_mainmissing)


#Create mainmissing file
mainmissing <- tbd_mainmissing_1 %>%
  select(-STATE)

#Delete the tbd data
rm(list=ls(pattern="tbd_"))
invisible(gc())


#Rename the variables in df1

df1_1 <- df1
colnames(df1_1) <- paste0("nibrs_agn_",colnames(df1_1))
#Change some back

df1_1 <- df1_1 %>% select(data_year       =nibrs_agn_data_year,
                          ori             =nibrs_agn_ori,
                          legacy_ori      =nibrs_agn_legacy_ori,
                          ucr_agency_name =nibrs_agn_ucr_agency_name,
                          everything()
) %>% mutate(
  
  nibrs_agn_nibrs_start_date_num = as.Date(nibrs_agn_nibrs_start_date, format='%m/%d/%Y'),
  nibrs_agn_nibrs_start_date_month = month(nibrs_agn_nibrs_start_date_num),
  nibrs_agn_nibrs_start_date_year = year(nibrs_agn_nibrs_start_date_num)
  
)


df1_1 %>% checkfunction(nibrs_agn_nibrs_start_date_month, nibrs_agn_nibrs_start_date)
df1_1 %>% checkfunction(nibrs_agn_nibrs_start_date_year, nibrs_agn_nibrs_start_date)

#Merge on the extra information from the NIBRS for help to identify agencies
#Okay to merge by year and ori since both datasets are from the NIBRS

#Need to use df1_1 - universe file - contain all agencies of interest
#maindata - is the reported incident offense counts
#mainmissing - is the missing month file

#Join the universe with MM file first
tbd_good <- df1_1 %>%
  inner_join(mainmissing, by = c("ori" = "ORI", "data_year" = "DATA_YEAR"))

tbd_bad <- df1_1 %>%
  anti_join(mainmissing, by = c("ori" = "ORI", "data_year" = "DATA_YEAR"))

tbd_good2 <- tbd_bad %>%
  inner_join(mainmissing, by = c("legacy_ori" = "ORI", "data_year" = "DATA_YEAR"))

tbd_bad2 <- tbd_bad %>%
  anti_join(mainmissing, by = c("legacy_ori" = "ORI", "data_year" = "DATA_YEAR"))

#Stack the data
raw_universe_mm <- bind_rows(tbd_good, tbd_good2, tbd_bad2)

#Check the dimension
log_dim(df1_1)
log_dim(raw_universe_mm)

log_dim(tbd_good)
log_dim(tbd_bad)
log_dim(tbd_good2)
log_dim(tbd_bad2)

#Delete the tbd data
rm(list=ls(pattern="tbd_"))
invisible(gc())

#Using raw_universe_mm, need to merge on the incident counts maindata
tbd_good <- raw_universe_mm %>%
  inner_join(maindata, by = c("ori" = "ori", "data_year" = "incident_year"))

tbd_bad <- raw_universe_mm %>%
  anti_join(maindata, by = c("ori" = "ori", "data_year" = "incident_year"))

tbd_good2 <- tbd_bad %>%
  inner_join(maindata, by = c("legacy_ori" = "ori", "data_year" = "incident_year"))

tbd_bad2 <- tbd_bad %>%
  anti_join(maindata, by = c("legacy_ori" = "ori", "data_year" = "incident_year"))

#Stack the data
tbd_finalstack <- bind_rows(tbd_good, tbd_good2, tbd_bad2)

#Need to zero filled the incident offense variables
tbd_zero_fill_vars <- colnames(tbd_finalstack) %>%
  as_tibble() %>%
  mutate(
    keep = fcase(
      str_detect(string=value, pattern="jan_"), 1,
      str_detect(string=value, pattern="feb_"), 1,
      str_detect(string=value, pattern="mar_"), 1,
      str_detect(string=value, pattern="apr_"), 1,
      str_detect(string=value, pattern="may_"), 1,
      str_detect(string=value, pattern="jun_"), 1,
      str_detect(string=value, pattern="jul_"), 1,
      str_detect(string=value, pattern="aug_"), 1,
      str_detect(string=value, pattern="sep_"), 1,
      str_detect(string=value, pattern="oct_"), 1,
      str_detect(string=value, pattern="nov_"), 1,
      str_detect(string=value, pattern="dec_"), 1,
      #Want the nibrs_total_crime
      str_detect(string=value, pattern="nibrs_total_crime_"), 1
    )
  ) %>%
  filter(keep == 1) %>%
  #Do not want the "ratio_v_p" variables to be zero filled
  filter(!(str_detect(string=value, pattern=regex(pattern="ratio_v_p", ignore_case=TRUE)))) %>%
  select(value) %>%
  pull()

#See the list of variables to be zero filled
print(tbd_zero_fill_vars)

tbd_finalstack1 <- tbd_finalstack %>%
  mutate(
    across(
      .cols=any_of(tbd_zero_fill_vars), 
      .fns = ~{
        replace_na(data=., replace=0)
      }
    )
  )

#Declare the finalstack dataset
finalstack <- tbd_finalstack1

#Check the dimension
log_dim(raw_universe_mm)
log_dim(finalstack)

log_dim(tbd_good)
log_dim(tbd_bad)
log_dim(tbd_good2)
log_dim(tbd_bad2)

#Delete the tbd data
rm(list=ls(pattern="tbd_"))
invisible(gc())



# maindata_2 <- left_join(maindata, df1_1, by = c("ori" = "ori", "incident_year" = "data_year") )
# #Get all the matches between the two datasets by ori
# maindata_3 <- inner_join(maindata_2, mainmissing, by=c("ori" = "ORI",  "incident_year" = "incident_year") )
# 
# #Get the unmatched ones
# maindata_3_anti_join <- anti_join(maindata_2, mainmissing, by=c("ori" = "ORI", "incident_year" = "incident_year") )
# 
# #Merge the unmatched ones by legacy_ori
# maindata_4 <- inner_join(maindata_3_anti_join, mainmissing, by=c("legacy_ori" = "ORI", "incident_year" = "incident_year") )
# 
# #Get the unmatched ones
# maindata_4_anti_join <- anti_join(maindata_3_anti_join, mainmissing, by=c("legacy_ori" = "ORI", "incident_year" = "incident_year") )

#Merge the unmatched ones by agency_name and State
# maindata_5 <- inner_join(maindata_4_anti_join, mainmissing, by=c("nibrs_agn_ucr_agency_name" = "UCR_AGENCY_NAME", "STATE" = "STATE", "incident_year" = "incident_year") )
# dim(maindata_5)

#Get the unmatched ones
#Merge the unmatched ones by agency_name and State
# maindata_5_anti_join <- anti_join(maindata_4_anti_join, mainmissing, by=c("nibrs_agn_ucr_agency_name" = "UCR_AGENCY_NAME", "STATE" = "STATE", "incident_year" = "incident_year") )
# dim(maindata_5_anti_join)


#Show the agencies that can't merge to the RETA MM file
# 
# DT::datatable(
#   maindata_4_anti_join %>% select(incident_year, ori, legacy_ori, ucr_agency_name, nibrs_agn_ncic_agency_name, nibrs_agn_population, nibrs_agn_in_univ_elig, nibrs_agn_nibrs_start_date)
# )


#Stack all the datasets together
#finalstack <- bind_rows(maindata_3, maindata_4, maindata_4_anti_join )

maindata <- maindata %>% arrange(ori, incident_year)
finalstack <- finalstack %>% arrange(ori, incident_year)

#Add on 2020-05-01:  Create a new population variable to account for the agencies that are cover by using Lance Couzen's code
#Just note, the Universe files must be used to account for the agencies that are non-NIBRS reporters.  We do not have the universe
#file for 2016, so we would not calcualte the altpop for that year.

#Read the datasets

universevarskeep <- c("incident_year",
                      "COVERED_BY_LEGACY_ORI",
                      "LEGACY_ORI",
                      "POPULATION",
                      "REPORTING_TYPE",
                      "PE_MALE_OFFICER_COUNT",#male_officer
                      "PE_FEMALE_OFFICER_COUNT",#female_officer
                      "PE_MALE_CIVILIAN_COUNT",#male_civilian,
                      "PE_FEMALE_CIVILIAN_COUNT"#female_civilian,
)

rawmergeunivlist <- map(list_of_years, 
                        ~ read_csv(paste0(input_files_folder, paste0("ref_agency_",toString(.x),".csv"))) %>% mutate(incident_year = .x) %>% select(!!!universevarskeep))

tbd_universe <- reduce(rawmergeunivlist, rbind)

#Deduplicate the universe file in case of duplicates due to dormant agencies
tbd_universe1 <- tbd_universe %>%
  group_by(incident_year, LEGACY_ORI) %>%
  mutate(
    tbd_keep_first = row_number() == 1
  ) %>%
  ungroup() %>%
  #Keep one agency per year.  Duplicate often happen for dormant agencies
  filter(tbd_keep_first == TRUE) %>%
  select(-tbd_keep_first)  

#Check the dimension
log_dim(tbd_universe1)
log_dim(tbd_universe)

#Create universe file
universe <- tbd_universe1

#Remove the tbd data
rm(list=ls(pattern="tbd_"))
invisible(gc())

#Create a spare universe file
spare_universe <- universe

rm(list=as.character("rawmergeunivlist") )

#create dataset containing covering ORIs
coverers<-filter(universe,!(is.na(COVERED_BY_LEGACY_ORI))) %>%
  select(incident_year, COVERED_BY_LEGACY_ORI) %>%
  unique() %>%
  mutate(covers=1) %>%
  rename(LEGACY_ORI=COVERED_BY_LEGACY_ORI)

#merge on covers indicator and create altpop which has the cumulative populations of covered agencies deducted from covering agencies
universe<-left_join(universe,coverers,by=c("incident_year", "LEGACY_ORI")) %>%
  mutate(covers=replace_na(covers,0)) %>%
  mutate(group_ori=if_else(is.na(COVERED_BY_LEGACY_ORI),LEGACY_ORI,COVERED_BY_LEGACY_ORI)) %>%
  group_by(incident_year,group_ori) %>%
  mutate(deductpop=(group_ori==LEGACY_ORI)*sum(POPULATION*(!group_ori==LEGACY_ORI))) %>%
  ungroup() %>%
  mutate(group_ori=if_else(!is.na(COVERED_BY_LEGACY_ORI) & covers==1,LEGACY_ORI,group_ori)) %>%
  group_by(incident_year,group_ori) %>%
  mutate(deductpop2=(group_ori==LEGACY_ORI & deductpop==0)*sum(POPULATION*(!group_ori==LEGACY_ORI))) %>%
  ungroup() %>%
  mutate(altpop=POPULATION-deductpop-deductpop2) %>%
  select(legacy_ori = LEGACY_ORI,
         incident_year,
         covers,
         group_ori,
         deductpop,
         altpop,
         univ_population = POPULATION,
         deductpop2,
         PE_MALE_OFFICER_COUNT,#male_officer
         PE_FEMALE_OFFICER_COUNT,#female_officer
         PE_MALE_CIVILIAN_COUNT,#male_civilian,
         PE_FEMALE_CIVILIAN_COUNT,#female_civilian,
         REPORTING_TYPE
  ) %>% rename (
    nibrs_agn_male_officer = PE_MALE_OFFICER_COUNT,
    nibrs_agn_female_officer = PE_FEMALE_OFFICER_COUNT,
    nibrs_agn_male_civilian = PE_MALE_CIVILIAN_COUNT,
    nibrs_agn_female_civilian = PE_FEMALE_CIVILIAN_COUNT,
    nibrs_agn_reporting_type = REPORTING_TYPE
  ) %>% mutate(
    nibrs_agn_male_total = nibrs_agn_male_officer + nibrs_agn_male_civilian,
    nibrs_agn_female_total = nibrs_agn_female_officer + nibrs_agn_female_civilian,
    nibrs_agn_officer_rate = 0,
    nibrs_agn_employee_rate = 0
  )

#Note these are the agencies where we don't have information at the agency level

#checkfunction(universe %>% filter(is.na(group_ori)), !!!colnames(universe) %>% rlang:::parse_exprs() )
#checkfunction(universe, incident_year, covers, group_ori, legacy_ori, altpop,  univ_population, deductpop, deductpop2 )

#Check the dimension
log_dim(finalstack)

finalstack <- left_join(finalstack, universe, by=c("incident_year", "legacy_ori"))

#Check the dimension
log_dim(finalstack)

#Add on 2020-06-17, create the new variable COVERING_FLAG.  If an agency's ORI or LEGACY_ORI is mentioned under "COVERED_BY_LEGACY_ORI" in the universe, this agency will have COVERING_FLAG=Y; it not, COVERING_FLAG=N.

#Use the universe dataset:  universe

#####################
####COVERING_FLAG####
#####################

covering_flag <- spare_universe %>%
  mutate(COVERING_FLAG = "Y") %>%
  select(ori=COVERED_BY_LEGACY_ORI,
         incident_year,
         COVERING_FLAG) %>%
  group_by(ori, incident_year, COVERING_FLAG) %>%
  summarise(raw_delete= n()) %>%
  ungroup() %>%
  filter(!is.na(ori)) %>%
  select(ori, incident_year, COVERING_FLAG)

##############################Merge on the covering_flag###########################################

#Merge on the extra information from the NIBRS for help to identify agencies
raw_maindata_1 <- inner_join(finalstack, covering_flag, by = c("ori" = "ori", "incident_year" = "incident_year"))

#Get the unmatched ones
raw_maindata_1_anti_join <- finalstack %>%
  anti_join(covering_flag, by = c("ori" = "ori", "incident_year" = "incident_year"))

#Merge the unmatched ones by legacy_ori
raw_maindata_2 <- raw_maindata_1_anti_join %>%
  inner_join(covering_flag, by=c("legacy_ori" = "ori", "incident_year" = "incident_year") )

#Get the unmatched ones
raw_maindata_2_anti_join <- raw_maindata_1_anti_join %>%
  anti_join(covering_flag, by=c("legacy_ori" = "ori", "incident_year" = "incident_year") )

#Stack all the datasets together
finalmain <- bind_rows(raw_maindata_1, raw_maindata_2, raw_maindata_2_anti_join)

#Overwrite the dataset
finalstack <- finalmain %>%
  mutate(
    COVERING_FLAG = fcase(is.na(COVERING_FLAG), "N",
                          rep_len(TRUE, length(COVERING_FLAG)), COVERING_FLAG)
  )

#Delete the dataset
rm(list=c("raw_maindata_1", "raw_maindata_1_anti_join", "raw_maindata_2", "raw_maindata_2_anti_join", "finalmain") )
invisible(gc())

checkfunction(finalstack, incident_year,  COVERING_FLAG)


# Add on 2020-04-21:  Write a function that will update the MM flags to 1 if there are updates to the NIBRS.  This will
#fix the issue when we don't receive a new MM file for prior years.


Update_MM_0_flag <- function(data) {
  log_debug("Running function Update_MM_0_flag")
  
  raw_vars <- data %>% select(
    #Columns 1-2 IDs:
    ori, incident_year,
    #Columns 3-14 MM_FLAG variables
    JAN_MM_FLAG,	FEB_MM_FLAG,	MAR_MM_FLAG,	APR_MM_FLAG,	MAY_MM_FLAG,	JUN_MM_FLAG,	JUL_MM_FLAG,	AUG_MM_FLAG,	SEP_MM_FLAG,	OCT_MM_FLAG,	NOV_MM_FLAG,	DEC_MM_FLAG,
    #Columns 15-26 Crime Count all variables
    jan_all, feb_all, mar_all, apr_all, may_all, jun_all, jul_all, aug_all, sep_all, oct_all, nov_all, dec_all,
    #Keep the remaining variables
    everything()
  )
  
  # MM_FLAG and crime count (month_all) columns
  mm_flag_cols <- names(raw_vars)[grep("MM_FLAG", names(raw_vars))]
  crime_count_cols <- names(raw_vars)[grep("^..._all$", names(raw_vars))]
  
  # create new columns for UPDATE_IND, ORG_VALUE for each month
  for (col in mm_flag_cols) {
    raw_vars[[paste0(col, "_UPDATE_IND")]] <- NA
    raw_vars[[paste0(col, "_ORG_VALUE")]] <- NA
  }
  # create new update col
  raw_vars[["MM_FLAG_ALL_UPDATE_IND"]] <- NA
  
  # update values (vectorized)
  for (i in seq_along(mm_flag_cols)) {
    mm_flag_col <- mm_flag_cols[i]
    crime_count_col <- crime_count_cols[i]
    
    # update rows if: 
    # (MM_flag == 0 & is not NA) and (crime count == 0 and is not NA)
    update_idx <- which((raw_vars[[mm_flag_col]] == 0 & !is.na(raw_vars[[mm_flag_col]])) & (raw_vars[[crime_count_col]] > 0 & !is.na(raw_vars[[crime_count_col]])))
    
    # Create indicator flag to show update
    raw_vars[update_idx, paste0(mm_flag_col, "_UPDATE_IND")] <- 1
    raw_vars[update_idx, "MM_FLAG_ALL_UPDATE_IND"] <- 1
    
    # Create ORG flag to hold original value
    raw_vars[update_idx, paste0(mm_flag_col, "_ORG_VALUE")] <- raw_vars[update_idx, mm_flag_col]
    
    # Update the corresponding MM_Flag variable to 1
    raw_vars[update_idx, mm_flag_col] <- 1
  }
  
  return(raw_vars)
}

finalstack <- Update_MM_0_flag(finalstack)

#Note 0 = Did note report, 1 = Report, 9 = Coverby another agency (true 0) for variables JAN_MM_FLAG - DEC_MM_FLAG

#Next step, update the NIBRS reporting pattern file, so that a) if an LEA has reta_mm=0 or 9 and  its total crime count is zero in a particular month, the agency's monthly crime counts in that month should be missing;  b) otherwise, if its reta_mm=1 and total crime count is 0, its monthly crime counts in that month should be 0.

#2019-11-21, after talking with Dan we believe that 1 and 9 should be considered reporting agencies for the month and that 0 should be missing

MM_0_9_to_na <- function(data, ...) {
  log_debug("Running function MM_0_9_to_na")
  
  crimeinputvars <- rlang::enquos(...)
  
  # Select columns
  raw_vars <- data %>% select(
    #Columns 1-2 IDs:
    ori, incident_year,
    #Columns 3-14 MM_FLAG variables
    JAN_MM_FLAG,	FEB_MM_FLAG,	MAR_MM_FLAG,	APR_MM_FLAG,	MAY_MM_FLAG,	JUN_MM_FLAG,	JUL_MM_FLAG,	AUG_MM_FLAG,	SEP_MM_FLAG,	OCT_MM_FLAG,	NOV_MM_FLAG,	DEC_MM_FLAG,
    #Columns 15-26 Crime Count variables
    !!!crimeinputvars,
    #Column 27 NIBRS Start date year and month
    nibrs_agn_nibrs_start_date_year,
    nibrs_agn_nibrs_start_date_month,
    #Everything else
    everything())
  
  # get MM_FLAG and crime count (month_all) columns
  mm_flag_cols <- grep("_MM_FLAG$", names(raw_vars))
  crime_count_cols <- mm_flag_cols + 12
  
  for (i in 1:length(mm_flag_cols)) {
    mm_flag_col <- mm_flag_cols[i]
    crime_count_col <- crime_count_cols[i]
    
    # Identify rows where (MM_FLAG is 0 and not NA) and (crime count col is 0 and not NA)
    update_idx <- which((raw_vars[[mm_flag_col]] == 0 & !is.na(raw_vars[[mm_flag_col]])) &
                          (raw_vars[[crime_count_col]] == 0 & !is.na(raw_vars[[crime_count_col]])))
    
    # Set crime count to NA for rows that meet condition above
    raw_vars[update_idx, crime_count_col] <- NA
  }
  
  return(raw_vars)
}

#Process the various crime types:
part1v_tona0 <- MM_0_9_to_na(finalstack,
                             jan_part1v,
                             feb_part1v,
                             mar_part1v,
                             apr_part1v,
                             may_part1v,
                             jun_part1v,
                             jul_part1v,
                             aug_part1v,
                             sep_part1v,
                             oct_part1v,
                             nov_part1v,
                             dec_part1v)

part1p_tona0 <- MM_0_9_to_na(part1v_tona0,
                             jan_part1p,
                             feb_part1p,
                             mar_part1p,
                             apr_part1p,
                             may_part1p,
                             jun_part1p,
                             jul_part1p,
                             aug_part1p,
                             sep_part1p,
                             oct_part1p,
                             nov_part1p,
                             dec_part1p)

otherc_tona0 <- MM_0_9_to_na(part1p_tona0,
                             jan_otherc,
                             feb_otherc,
                             mar_otherc,
                             apr_otherc,
                             may_otherc,
                             jun_otherc,
                             jul_otherc,
                             aug_otherc,
                             sep_otherc,
                             oct_otherc,
                             nov_otherc,
                             dec_otherc)

all_tona0 <- MM_0_9_to_na(otherc_tona0,
                          jan_all,
                          feb_all,
                          mar_all,
                          apr_all,
                          may_all,
                          jun_all,
                          jul_all,
                          aug_all,
                          sep_all,
                          oct_all,
                          nov_all,
                          dec_all)


#2020-01-17, after discussing with Dan and Kelly, we believed we need to use the nibrs_start_date to account for the late starters.  The issue is that when an LEA is a late starter within the year they started, they may report their crimes to both the SRS and NIBRS, so in the NIBRS side, the months where the LEA don't report yet, since they weren't ready, will have 0 crime counts and the RETA MM file if the MM FLAG is equal to 1 will falsely accept the 0 crime counts as correct.  The fix will consider the nibrs_start_date variable and make the crime counts to missing for the months before the LEAs are ready to be NIBRS ready.

#2020-01-21, edit code to see which positive crime counts before the NIBRS_START are turn to NA.  This function return a list of 2 datasets
#raw_vars: containing the data frame with the corrected late starters counts by changing crime counts before the NIBRS_START_DATE to NA
#reportbfsd:  Keep account of the LEA where the crime counts are non-zero before changing to NA due to happening before NIBRS_START_DATE

#2020-01-29, edit code to make if the incident year is before the NIBRS_START_DATE Year then make all missing.

fix_late_starters <- function(data, ...){
  log_debug("Running function fix_late_starters")
  
  crimeinputvars <- rlang:::enquos(...)
  
  #Set up code to store NIBRS crime counts that are reported before the nibrs_start_date
  
  reportbfsd <- vector("list", nrow(data) )
  reportbfsd_count <- 1
  
  
  raw_vars <- data %>% select(
    
    #Columns 1-2 IDs:
    ori, incident_year,
    
    #Columns 3-14 MM_FLAG variables
    JAN_MM_FLAG,	FEB_MM_FLAG,	MAR_MM_FLAG,	APR_MM_FLAG,	MAY_MM_FLAG,	JUN_MM_FLAG,	JUL_MM_FLAG,	AUG_MM_FLAG,	SEP_MM_FLAG,	OCT_MM_FLAG,	NOV_MM_FLAG,	DEC_MM_FLAG,
    
    #Columns 15-26 Crime Count variables
    !!!crimeinputvars,
    
    #Column 27 NIBRS Start date year and month
    nibrs_agn_nibrs_start_date_year,
    nibrs_agn_nibrs_start_date_month,
    
    #Everything else
    everything() )
  
  
  
  #loop through row to fix late starters
  for (x in 1:nrow(raw_vars)){
    
    
    #Initialize the raw variable to hold
    raw_stoplsmon <- NA
    
    
    #If the incident year is before the NIBRS_START_DATE year then make all missing
    if (
      
      (raw_vars[x, "incident_year"] < raw_vars[x,"nibrs_agn_nibrs_start_date_year"])  &
      
      
      (!is.na(raw_vars[x, "incident_year"]) & !is.na(raw_vars[x, "nibrs_agn_nibrs_start_date_year"] ) )
      
    ){
      
      for (i in 15:26){
        #Log the entries where we found a non-zero crime count before the nibrs_start_date
        if (raw_vars[x, i] > 0 & !is.na(raw_vars[x, i]) ){
          
          #Get the variables of interest
          reportbfsd[[reportbfsd_count]] <- raw_vars[x, c(1,2, i-12, i, 27, 28) ]
          
          #Increase the counter
          reportbfsd_count = reportbfsd_count + 1
        }
        
        #Loop through the crime count variables and make missing
        
        raw_vars[x, i] <- NA
        
      }
    }
    
    else if (
      
      (raw_vars[x, "nibrs_agn_nibrs_start_date_year"] == raw_vars[x, "incident_year"])  &
      
      
      
      (!is.na(raw_vars[x, "nibrs_agn_nibrs_start_date_year"]) & !is.na(raw_vars[x, "incident_year"] ) )
      
    ){
      
      #Initialize the stop variable for late starters, we want to start correcting with February on column 16
      raw_stoplsmon = as.double(raw_vars[x, "nibrs_agn_nibrs_start_date_month"] + 14)
      
      # Only fix the variables if the late starter is February or later
      if(raw_stoplsmon >= 16){
        #Substract one to handle the prior months and not the month started reporting
        for (z in seq(15, raw_stoplsmon - 1) ){
          
          #Log the entries where we found a non-zero crime count before the nibrs_start_date
          if (raw_vars[x, z] > 0 & !is.na(raw_vars[x, z]) ){
            
            #Get the variables of interest
            reportbfsd[[reportbfsd_count]] <- raw_vars[x, c(1,2, z-12, z, 27, 28) ]
            
            
            
            #Increase the counter
            reportbfsd_count = reportbfsd_count + 1
          }
          
          #Make the crime counts to missing
          raw_vars[x, z] <- NA
          
        }
      }
      
      #Make it NA for the next cycle
      raw_stoplsmon <- NA
    }
  }
  
  return(list(raw_vars, reportbfsd))
  
}

# TODO update 
fix_late_starters <- function(data, ...){
  log_debug("Running function fix_late_starters")
  
  crimeinputvars <- rlang:::enquos(...)
  
  # Select variables
  raw_vars <- data %>% select(
    #Columns 1-2 IDs:
    ori, incident_year,
    #Columns 3-14 MM_FLAG variables
    JAN_MM_FLAG,	FEB_MM_FLAG,	MAR_MM_FLAG,	APR_MM_FLAG,	MAY_MM_FLAG,	JUN_MM_FLAG,	JUL_MM_FLAG,	AUG_MM_FLAG,	SEP_MM_FLAG,	OCT_MM_FLAG,	NOV_MM_FLAG,	DEC_MM_FLAG,
    #Columns 15-26 Crime Count variables
    !!!crimeinputvars,
    #Column 27 NIBRS Start date year and month
    nibrs_agn_nibrs_start_date_year,
    nibrs_agn_nibrs_start_date_month,
    #Everything else
    everything())
  
  # condition1: the incident year is before the NIBRS_START_DATE year
  condition1 <- !is.na(raw_vars$incident_year) & 
    !is.na(raw_vars$nibrs_agn_nibrs_start_date_year) & 
    (raw_vars$incident_year < raw_vars$nibrs_agn_nibrs_start_date_year)
  
  # condition2: the incident year == NIBRS_START_DATE year
  condition2 <- !is.na(raw_vars$nibrs_agn_nibrs_start_date_year) & 
    !is.na(raw_vars$incident_year) & 
    (raw_vars$nibrs_agn_nibrs_start_date_year == raw_vars$incident_year)
  
  # Set MM_FLAGs to NA based on condition1 (incident year < NIBRS_START_DATE year)
  raw_vars[condition1, 15:26] <- NA
  
  #Initialize the stop variable for late starters, we want to start correcting with February on column 16
  start_date_adjustment <- as.numeric(raw_vars$nibrs_agn_nibrs_start_date_month) + 14
  # Set MM_FLAGs to NA based on condition2 (incident year == NIBRS_START_DATE year), 
  #  but only fix the variables if the late starter is February or later
  for (i in 15:26) {
    raw_vars[condition2 & i < start_date_adjustment, i] <- NA
  }
  
  reportbfsd <- list()
  
  list(raw_vars, reportbfsd)
}


part1v_tona1 <- fix_late_starters(all_tona0,
                                  jan_part1v,
                                  feb_part1v,
                                  mar_part1v,
                                  apr_part1v,
                                  may_part1v,
                                  jun_part1v,
                                  jul_part1v,
                                  aug_part1v,
                                  sep_part1v,
                                  oct_part1v,
                                  nov_part1v,
                                  dec_part1v)

part1p_tona1 <- fix_late_starters(part1v_tona1[[1]],
                                  jan_part1p,
                                  feb_part1p,
                                  mar_part1p,
                                  apr_part1p,
                                  may_part1p,
                                  jun_part1p,
                                  jul_part1p,
                                  aug_part1p,
                                  sep_part1p,
                                  oct_part1p,
                                  nov_part1p,
                                  dec_part1p)

otherc_tona1 <- fix_late_starters(part1p_tona1[[1]],
                                  jan_otherc,
                                  feb_otherc,
                                  mar_otherc,
                                  apr_otherc,
                                  may_otherc,
                                  jun_otherc,
                                  jul_otherc,
                                  aug_otherc,
                                  sep_otherc,
                                  oct_otherc,
                                  nov_otherc,
                                  dec_otherc)

all_tona1 <- fix_late_starters(otherc_tona1[[1]],
                               jan_all,
                               feb_all,
                               mar_all,
                               apr_all,
                               may_all,
                               jun_all,
                               jul_all,
                               aug_all,
                               sep_all,
                               oct_all,
                               nov_all,
                               dec_all)



#Extract the dataset with the late starter fix
all_tona <- all_tona1[[1]]


#Note all_tona is the final dataset
#Need to correct the following variables for each of the specific crimes type after
# nibrs_missing_pattern_
# nibrs_max_consecutive_month_missing_

make_missing_pattern <- function(data, var, suffix){
  log_debug("Running function make_missing_pattern")
  
  #Overwrite the variable
  varcreate <- rlang:::parse_expr( paste0(var, suffix))
  
  #Declare the month variable
  janvar <- rlang:::parse_expr( paste0("jan", suffix))
  febvar <- rlang:::parse_expr( paste0("feb", suffix))
  marvar <- rlang:::parse_expr( paste0("mar", suffix))
  aprvar <- rlang:::parse_expr( paste0("apr", suffix))
  mayvar <- rlang:::parse_expr( paste0("may", suffix))
  junvar <- rlang:::parse_expr( paste0("jun", suffix))
  julvar <- rlang:::parse_expr( paste0("jul", suffix))
  augvar <- rlang:::parse_expr( paste0("aug", suffix))
  sepvar <- rlang:::parse_expr( paste0("sep", suffix))
  octvar <- rlang:::parse_expr( paste0("oct", suffix))
  novvar <- rlang:::parse_expr( paste0("nov", suffix))
  decvar <- rlang:::parse_expr( paste0("dec", suffix))
  
  #Create the variable
  raw_1 <- data %>% mutate(!!varcreate := paste0(ifelse(is.na(!!janvar), 0, 1),
                                                 ifelse(is.na(!!febvar), 0, 1),
                                                 ifelse(is.na(!!marvar), 0, 1),
                                                 "-",
                                                 ifelse(is.na(!!aprvar), 0, 1),
                                                 ifelse(is.na(!!mayvar), 0, 1),
                                                 ifelse(is.na(!!junvar), 0, 1),
                                                 "-",
                                                 ifelse(is.na(!!julvar), 0, 1),
                                                 ifelse(is.na(!!augvar), 0, 1),
                                                 ifelse(is.na(!!sepvar), 0, 1),
                                                 "-",
                                                 ifelse(is.na(!!octvar), 0, 1),
                                                 ifelse(is.na(!!novvar), 0, 1),
                                                 ifelse(is.na(!!decvar), 0, 1)))
  
  #Fix the counts for all months
  result <- raw_1 %>% select( !!janvar, !!febvar, !!marvar,
                              !!aprvar, !!mayvar, !!junvar,
                              !!julvar, !!augvar, !!sepvar,
                              !!octvar, !!novvar, !!decvar) %>% rowSums(.,na.rm=TRUE)
  
  #Create new variable name
  total_crime_var <- rlang:::parse_expr(paste0("nibrs_total_crime", suffix))
  
  raw_1 <- cbind(raw_1 %>% select(-!!total_crime_var) , result)
  
  raw2 <- raw_1 %>% rename(!!total_crime_var := result)
  
  
}

fixingdataset <- make_missing_pattern(data=all_tona,      var="nibrs_missing_pattern", suffix="_part1v")
fixingdataset <- make_missing_pattern(data=fixingdataset, var="nibrs_missing_pattern", suffix="_part1p")
fixingdataset <- make_missing_pattern(data=fixingdataset, var="nibrs_missing_pattern", suffix="_otherc")
fixingdataset <- make_missing_pattern(data=fixingdataset, var="nibrs_missing_pattern", suffix="_all")

#Fix the nibrs_max_consecutive_month_missing variables

fix_max_consecutive_month_missing <- function(data, suffix){
  log_debug("Running function fix_max_consecutive_month_missing")
  
  #Get the names of the dataset for order and reorder dataset after rearrange
  datasetorder <- syms(colnames(data))
  
  
  #Declare the month variable
  janvar <- rlang:::parse_expr( paste0("jan", suffix))
  febvar <- rlang:::parse_expr( paste0("feb", suffix))
  marvar <- rlang:::parse_expr( paste0("mar", suffix))
  aprvar <- rlang:::parse_expr( paste0("apr", suffix))
  mayvar <- rlang:::parse_expr( paste0("may", suffix))
  junvar <- rlang:::parse_expr( paste0("jun", suffix))
  julvar <- rlang:::parse_expr( paste0("jul", suffix))
  augvar <- rlang:::parse_expr( paste0("aug", suffix))
  sepvar <- rlang:::parse_expr( paste0("sep", suffix))
  octvar <- rlang:::parse_expr( paste0("oct", suffix))
  novvar <- rlang:::parse_expr( paste0("nov", suffix))
  decvar <- rlang:::parse_expr( paste0("dec", suffix))
  
  raw1 <- data %>% select(!!janvar, !!febvar, !!marvar,
                          !!aprvar, !!mayvar, !!junvar,
                          !!julvar, !!augvar, !!sepvar,
                          !!octvar, !!novvar, !!decvar,
                          
                          everything() )
  
  
  #Initialize the nibrs_max_consecutive_month_missing to be missing
  raw1[, paste0("nibrs_max_consecutive_month_missing", suffix)] <- NA
  
  #Loop through the variables nibrs_jan_report - nibrs_dec_report and keep count the number of largest consecutive month missing
  numberofmissing<-NA
  numberofmissing[1:12] <-0
  
  #Loop through the dataset row by row
  for (i in 1:nrow(raw1) ) {
    
    #make the array missing and variable for new row processing
    numberofmissing[1:12] <- 0
    countmissing <- 0
    
    #Loop through nibrs_jan_report - nibrs_dec_report and find if there are no crime reported
    for (j in 1:12) {
      
      #If found, increase the variable countmissing by 1 and store the cumculative count in the array numberofmissing
      if (is.na(raw1[i,j])){
        countmissing = countmissing + 1
        numberofmissing[j] =countmissing
        
      }
      #If the count is not zero, then reset the variable countmissing to zero and report it back to the array
      else{
        countmissing = 0
        numberofmissing[j] <- 0
      }
    }
    #Get the max from the array
    raw1[i, paste0("nibrs_max_consecutive_month_missing", suffix)] <- max(numberofmissing)
    
    
  }
  
  #Perserve the order
  raw2 <- raw1 %>% select(!!!(datasetorder), everything() )
  
  #Return dataset
  return(raw2)
}


fixingdataset <- fix_max_consecutive_month_missing(data=fixingdataset, suffix="_part1v")
fixingdataset <- fix_max_consecutive_month_missing(data=fixingdataset, suffix="_part1p")
fixingdataset <- fix_max_consecutive_month_missing(data=fixingdataset, suffix="_otherc")
fixingdataset <- fix_max_consecutive_month_missing(data=fixingdataset, suffix="_all")



#Do a QC check

DT::datatable(
  fixingdataset %>% select(ends_with("_part1v")) %>% head(1000)
)

DT::datatable(
  fixingdataset %>% select(ends_with("_part1p")) %>% head(1000)
)

DT::datatable(
  fixingdataset %>% select(ends_with("_otherc")) %>% head(1000)
)

DT::datatable(
  fixingdataset %>% select(ends_with("_all")) %>% head(1000)
)



#Get the names of the dataset for order and reorder dataset after rearrange for making zeros
datasetorder <- syms(colnames(finalstack))

final_tomake_na <- fixingdataset %>% select(!!!(datasetorder), everything() )

#Fix the ratios
final_tomake_na <- final_tomake_na %>% mutate(
  jan_ratio_v_p = ifelse(jan_part1p ==0, NA,  jan_part1v/jan_part1p),
  feb_ratio_v_p = ifelse(feb_part1p ==0, NA,  feb_part1v/feb_part1p),
  mar_ratio_v_p = ifelse(mar_part1p ==0, NA,  mar_part1v/mar_part1p),
  apr_ratio_v_p = ifelse(apr_part1p ==0, NA,  apr_part1v/apr_part1p),
  may_ratio_v_p = ifelse(may_part1p ==0, NA,  may_part1v/may_part1p),
  jun_ratio_v_p = ifelse(jun_part1p ==0, NA,  jun_part1v/jun_part1p),
  jul_ratio_v_p = ifelse(jul_part1p ==0, NA,  jul_part1v/jul_part1p),
  aug_ratio_v_p = ifelse(aug_part1p ==0, NA,  aug_part1v/aug_part1p),
  sep_ratio_v_p = ifelse(sep_part1p ==0, NA,  sep_part1v/sep_part1p),
  oct_ratio_v_p = ifelse(oct_part1p ==0, NA,  oct_part1v/oct_part1p),
  nov_ratio_v_p = ifelse(nov_part1p ==0, NA,  nov_part1v/nov_part1p),
  dec_ratio_v_p = ifelse(dec_part1p ==0, NA,  dec_part1v/dec_part1p),
  total_ratio_v_p = ifelse(nibrs_total_crime_part1p ==0, NA,  nibrs_total_crime_part1v/nibrs_total_crime_part1p)
)

final_tomake_na <- final_tomake_na %>% mutate(STATE = substr(trim_upcase(ori), 1, 2 ))

#Keep the 50 U.S. States + D.C.

#DT::datatable(
#	final_tomake_na %>% group_by(STATE, STATE_NAME) %>% summarise(count=n())
#)

#Write the dataset with reta_mm information merge on and true missings are blank
write.csv(final_tomake_na, file=paste0(output_folder,"/NIBRS_reporting_pattern_with_reta-mm.csv"), na="", row.names = FALSE)