###-------------------------------------------------------------------------------
### Define libraries
###-------------------------------------------------------------------------------

library(tidyverse)
library(openxlsx)
library(haven)
library(mice)
library(miceadds)
library(VIM)
library(naniar)
library(visdat)
library(ggplot2)
library(StatMatch)
library(writexl)
library(sas7bdat)
library(sjmisc)
library(gtools)
library(zoo)
library(reshape2)
library(lazyeval)
library(data.table)
library(DT)		   

set.seed(5242023)

#Create a dataset for the state factors
CONST_STATE_FACTOR <- c(
"1=AK",
"2=AL",
"3=AR",
"4=AS",
"5=AZ",
"6=CA",
"7=CO",
"8=CT",
"9=CZ",
"10=DC",
"11=DE",
"12=FL",
"13=GA",
"14=GM",
"15=HI",
"16=IA",
"17=ID",
"18=IL",
"19=IN",
"20=KS",
"21=KY",
"22=LA",
"23=MA",
"24=MD",
"25=ME",
"26=MI",
"27=MN",
"28=MO",
"29=MS",
"30=MT",
"31=NB",
"32=NC",
"33=ND",
"34=NH",
"35=NJ",
"36=NM",
"37=NV",
"38=NY",
"39=OH",
"40=OK",
"41=OR",
"42=PA",
"43=PR",
"44=RI",
"45=SC",
"46=SD",
"47=TN",
"48=TX",
"49=UT",
"50=VI",
"51=VA",
"52=VT",
"53=WA",
"54=WI",
"55=WV",
"56=WY",
"57=MP",
"98=FS") %>%
  as_tibble() %>%
  rename(
    state_factor=value
  ) %>%
  mutate(
    state_num = str_match(string=state_factor, pattern="(\\d+)=")[,2] %>% as.character()
  )

#See the dataset
CONST_STATE_FACTOR %>% datatable()

###-------------------------------------------------------------------------------
### Data preparation: Read in the imputed SRS file
###-------------------------------------------------------------------------------

#Okay to use read_csv as is since it is just a character ori variable and all numeric v variables
raw_imputed_srs <- read_csv(paste0(filepathin, "SRS_NIBRS_BLOCK_IMP_ONLY_MAX.csv"))
log_dim(raw_imputed_srs)

###-------------------------------------------------------------------------------
### Data preparation: Read in the NIBRS sampling frame and use the response 
###   indicator JD creates
###-------------------------------------------------------------------------------
nibrs_sf_raw <- fread(paste0(nibrs_weights_in, "/SF.csv")) 

nibrs_sf <- nibrs_sf_raw %>%
  filter(resp_ind_m3 == 1) 

#Check the dim
log_dim(nibrs_sf_raw)
log_dim(nibrs_sf)

#Do the merge by ori
tbd_good_1 <- nibrs_sf %>%
  inner_join(raw_imputed_srs, by="ORI")

tbd_bad_1 <- nibrs_sf %>%
  anti_join(raw_imputed_srs, by="ORI")

#Do the remaining merge by LEGACY_ORI

tbd_good_2 <- tbd_bad_1 %>%
  inner_join(raw_imputed_srs, by=c("LEGACY_ORI" = "ORI"))

tbd_bad_2 <- tbd_bad_1 %>%
  anti_join(raw_imputed_srs, by=c("LEGACY_ORI" = "ORI"))

#Create the dataset that have the partial reporters converted to 

tbd_imputed_srs <- bind_rows(tbd_good_1, tbd_good_2, tbd_bad_2)

#Check the dimension
log_dim(tbd_imputed_srs)
log_dim(nibrs_sf)

log_dim(tbd_good_1)
log_dim(tbd_bad_1)
log_dim(tbd_good_2)
log_dim(tbd_bad_2)

#Next need to create the final dataset and keep certain variables
final_imputed_srs <- tbd_imputed_srs %>%
  select(ORI, matches("v\\d+")) %>%
  #Note need to zero filled the NA v variables, the reasoning is that these agencies did not report
  #any incidents to NIBRS, so they are our 0 reporters
  mutate(
    across(
      .cols = matches("v\\d+"),
      .fns = ~ {
        replace_na(.x, value = 0) 
        },
      .names="{.col}")
  ) %>%
  #Next need to create the MM flags and make them all 1 to be a full year reporters since 
  #any ORI given a weight greater than or equal to 1 is at least a 3 month reporters
  mutate(
    jan_mm_flag = 1,
    feb_mm_flag = 1,
    mar_mm_flag = 1,
    apr_mm_flag = 1,
    may_mm_flag = 1,
    jun_mm_flag = 1,
    jul_mm_flag = 1,
    aug_mm_flag = 1,
    sep_mm_flag = 1,
    oct_mm_flag = 1,
    nov_mm_flag = 1,
    dec_mm_flag = 1
) 

#Delete all the raw and tbd datasets
rm(list=c(ls(pattern="tbd"), setdiff(ls(pattern="raw"), "raw_srs_file_path")))

#Create a list or variables to be drop from the srs
CONST_DROP_VARS <- colnames(final_imputed_srs) %>%
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

#Using srs0 need to identify the ori that are in the final_imputed_srs and replace 
#their data with the imputed SRS data

#Do the merge by ORI
tbd_good_1 <- tbd_srs %>%
  inner_join(final_imputed_srs %>% select(ORI), by=c("ORI" = "ORI")) %>%
  #Create a temporary ORI variable for match
  mutate(ORI_MATCH = ORI)

tbd_bad_1 <- tbd_srs %>%
  anti_join(final_imputed_srs %>% select(ORI), by=("ORI" = "ORI"))

#Do the remaining merge by ORI_UNIV

tbd_good_2 <- tbd_bad_1 %>%
  inner_join(final_imputed_srs %>% select(ORI), by=c("ORI_UNIV" = "ORI")) %>%
  #Create a temporary ORI variable for match
  mutate(ORI_MATCH = ORI_UNIV)

tbd_bad_2 <- tbd_bad_1 %>%
  anti_join(final_imputed_srs %>% select(ORI), by=c("ORI_UNIV" = "ORI"))

#Create the dataset
tbd_match    <- bind_rows(tbd_good_1, tbd_good_2)
tbd_no_match <- tbd_bad_2

#Check the dimension
log_dim(tbd_srs)
log_dim(final_imputed_srs)
log_dim(tbd_match)
log_dim(tbd_no_match)


log_dim(tbd_good_1)
log_dim(tbd_bad_1)
log_dim(tbd_good_2)
log_dim(tbd_bad_2)

#Next using tbd_match, need to drop the v variables and mm flags and replace them
#with the imputed version

#Need to drop the variables in common
tbd_match2 <- tbd_match %>%
  select(!!!paste0("-", CONST_DROP_VARS) %>% rlang:::parse_exprs() )

log_dim(tbd_match)
log_dim(tbd_match2)

#Next need to merge on the imputed variables and create an indicator variable
tbd_match3 <- tbd_match2 %>%
  left_join(final_imputed_srs %>% 
              mutate(der_in_nibrs_imputed = 1), by=c("ORI_MATCH" = "ORI"))

#Check to see if everything merges
log_dim(tbd_match3)
sum(tbd_match3$der_in_nibrs_imputed)

#Using tbd_match3 and tbd_no_match, need to stack the dataset together to create
#the srs dataset 

srs <- bind_rows(tbd_match3, tbd_no_match)

#Check the dimension
log_dim(tbd_srs)
log_dim(srs)
log_dim(tbd_match3)
log_dim(tbd_no_match)

#Need to delete the tbd datasets
rm(list=ls(pattern="tbd_"))
invisible(gc())								


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
#Remove year since it may cause issue, since it is not the partial reporter output																				  
#srs3 <- srs2 %>% filter(data_year==year & der_in_univ_elig==1) %>%
tbd_srs <- srs2 %>% filter(der_in_univ_elig==1) %>%												   
  select(ORI, #data_year,
         cover_flg, suburb_flg,
         rpt_type, agn_type, agn_status, coveringAgency,
         STATE_ID_UNIV, POPULATION_UNIV, REGION_CODE_UNIV, DIVISION_CODE_UNIV, POPULATION_GROUP_ID_UNIV,
         MALE_OFFICER_UNIV, MALE_CIVILIAN_UNIV, FEMALE_OFFICER_UNIV, FEMALE_CIVILIAN_UNIV,
         starts_with("v"), ends_with("mm_flag")) %>%
         #Need to drop the non-imputed officer variables
        select(-MALE_OFFICER_UNIV, -MALE_CIVILIAN_UNIV, -FEMALE_OFFICER_UNIV, -FEMALE_CIVILIAN_UNIV)

################New need to use the imputed officer counts here ##################################

#Next need to read in the pseudo ori file
tbd_universe <- read_csv(paste0(raw_srs_file_path, "ref_agency_", year, ".csv")) 
log_dim(tbd_universe)

#Next need to keep certain variables
tbd_universe2 <- tbd_universe %>%
  select(ORI, LEGACY_ORI, PE_MALE_OFFICER_COUNT, PE_FEMALE_OFFICER_COUNT, PE_MALE_CIVILIAN_COUNT, PE_FEMALE_CIVILIAN_COUNT) %>%
  #Need to deduplicate
  distinct(ORI, LEGACY_ORI, PE_MALE_OFFICER_COUNT, PE_FEMALE_OFFICER_COUNT, PE_MALE_CIVILIAN_COUNT, PE_FEMALE_CIVILIAN_COUNT)

#Check to see the dim
log_dim(tbd_universe2)

#Need to join tbd_srs and tbd_universe2
tbd_good <- tbd_srs %>%
  inner_join(tbd_universe2 %>% select(-LEGACY_ORI), by = c("ORI" = "ORI"))

tbd_bad <- tbd_srs %>%
  anti_join(tbd_universe2 %>% select(-LEGACY_ORI), by = c("ORI" ="ORI"))

tbd_good2 <- tbd_bad %>%
  inner_join(tbd_universe2 %>% select(-ORI), by = c("ORI" = "LEGACY_ORI"))

tbd_bad2 <- tbd_bad %>%
  anti_join(tbd_universe2 %>% select(-ORI), by = c("ORI" ="LEGACY_ORI"))

#Put the dataset together
tbd_srs2 <- bind_rows(tbd_good, tbd_good2, tbd_bad2)

#See the dim
log_dim(tbd_srs2)
log_dim(tbd_good)
log_dim(tbd_bad)
log_dim(tbd_good2)
log_dim(tbd_bad2)

#Drop the old police employment variables and rename them
tbd_srs3 <- tbd_srs2 %>%
  #Rename the police officer variables
  rename(
    MALE_OFFICER_UNIV    = PE_MALE_OFFICER_COUNT, 
    FEMALE_OFFICER_UNIV  = PE_FEMALE_OFFICER_COUNT, 
    MALE_CIVILIAN_UNIV    = PE_MALE_CIVILIAN_COUNT, 
    FEMALE_CIVILIAN_UNIV  = PE_FEMALE_CIVILIAN_COUNT
  )

#Create the srs3 to be consistent with rest of program
srs3 <- tbd_srs3

#Delete the tbd_objects
rm(list=ls(pattern="^tbd_"))
invisible(gc())

###################################################################################################




# Define factor variables
srs3 <- srs3 %>% mutate_at(c("cover_flg", "suburb_flg", "rpt_type", "agn_type", "REGION_CODE_UNIV",
                                   "agn_status", "coveringAgency", "STATE_ID_UNIV", "POPULATION_GROUP_ID_UNIV",
                                   "DIVISION_CODE_UNIV"), as.factor)


#NEW using srs3 need to make into missing the SRS's v variables using the MM flag variables
CONST_V_VARS  <- srs3 %>%
  colnames() %>%
  as_tibble() %>%
  mutate(
    #Keep the v variables
    der_keep = str_detect(value, pattern="^v\\d+$")
  ) %>%
  #Filter to the variables
  filter(der_keep == TRUE) %>%
  select(value) %>%
  pull()

CONST_MM_VARS <- srs3 %>%
  colnames() %>%
  as_tibble() %>%
  mutate(
    #Keep the mm flag variables
    der_keep2 = str_detect(value, pattern="_mm_flag$"),
  ) %>%
  #Filter to the variables
  filter(der_keep2 == TRUE) %>%
  select(value) %>%
  pull()


CONST_V_MM_VARS <- c(CONST_V_VARS, CONST_MM_VARS)
  

#See the list of variables
print(CONST_V_VARS)
print(CONST_MM_VARS)
print(CONST_V_MM_VARS)

#Declare the monthly variables
CONST_VARS_JAN <- c(70:95)
CONST_VARS_FEB <- c(188:213)
CONST_VARS_MAR <- c(306:331)

CONST_VARS_APR <- c(424:449)
CONST_VARS_MAY <- c(542:567)
CONST_VARS_JUN <- c(660:685)

CONST_VARS_JUL <- c(778:803)
CONST_VARS_AUG <- c(896:921)
CONST_VARS_SEP <- c(1014:1039)

CONST_VARS_OCT <- c(1132:1157)
CONST_VARS_NOV <- c(1250:1275)
CONST_VARS_DEC <- c(1368:1393)

CONST_VARS_ALL_MONTH <-paste0(
  "v", 
  c(CONST_VARS_JAN, CONST_VARS_FEB, CONST_VARS_MAR,
    CONST_VARS_APR, CONST_VARS_MAY, CONST_VARS_JUN,
    CONST_VARS_JUL, CONST_VARS_AUG, CONST_VARS_SEP,
    CONST_VARS_OCT, CONST_VARS_NOV, CONST_VARS_DEC
    )
)
  


#Declare the ID variables
CONST_ID <- c("ORI", "STATE_ID_UNIV")

#Using srs3 - split to two datasets
#tbd_final_vars contains all variables that are not the v variables
#tbd_srs0       contains the v variables

tbd_final_vars <- srs3 %>%
  #Drop the variables
  select(!!!(paste0("-", CONST_V_VARS) %>% rlang:::parse_exprs()))

tbd_srs0 <- srs3 %>%
  #Keep selected variables
  select(
    !!!(CONST_ID %>% rlang:::parse_exprs()),
    !!!(CONST_V_MM_VARS %>% rlang:::parse_exprs())
  )

#Check the dimension
log_dim(srs3)
log_dim(tbd_final_vars)
log_dim(tbd_srs0)

#Get the list of state_id to loop thru
CONST_STATE_ID_LOOP <- tbd_srs0 %>%
  distinct(STATE_ID_UNIV) %>%
  select(STATE_ID_UNIV) %>%
  pull()

#See the list of State ids
print(CONST_STATE_ID_LOOP)

#Using tbd_srs0, need to transpose the data from wide to long

final_edited_srs <- map_dfr(CONST_STATE_ID_LOOP, ~{
  
  print(paste0("Processing STATE_ID_UNIV ", .x))
  
  raw_srs1 <- tbd_srs0 %>%
    #Filter to current state
    filter(STATE_ID_UNIV == .x) %>%
    gather(
      #Identify the IDs
      !!! paste0("-", CONST_ID) %>% rlang:::parse_exprs(),
      #Name the v variables and mm flags and its current values
      key   = "variables",
      value = "value"
    )
  
  #Need to code the v variables from the mm flags
  raw_srs2 <- raw_srs1 %>%
    mutate(
      der_v_vars  = str_detect(variables, pattern="v\\d+"),
      der_mm_vars = str_detect(variables, pattern="_mm_flag$"),
      
    )
  
  #Check to see if all variables are accounted for
  log_dim(raw_srs2)
  print(table(raw_srs2$der_v_vars))
  print(table(raw_srs2$der_mm_vars))
  
  #Next split up the datasets
  raw_srs3_v_vars  <- raw_srs2 %>% filter(der_v_vars == TRUE) 
  raw_srs3_mm_vars <- raw_srs2 %>% filter(der_mm_vars == TRUE) 
  
  #Check to see if all variables are accounted for
  log_dim(raw_srs2)
  log_dim(raw_srs3_v_vars)
  log_dim(raw_srs3_mm_vars)
  
  #First process the raw_srs3_mm_vars
  raw_mm <- raw_srs3_mm_vars %>%
    mutate(
      der_month = fcase(
        trim_upper(variables) == "JAN_MM_FLAG", 1, 
        trim_upper(variables) == "FEB_MM_FLAG", 2, 
        trim_upper(variables) == "MAR_MM_FLAG", 3, 
        trim_upper(variables) == "APR_MM_FLAG", 4, 
        trim_upper(variables) == "MAY_MM_FLAG", 5, 
        trim_upper(variables) == "JUN_MM_FLAG", 6, 
        trim_upper(variables) == "JUL_MM_FLAG", 7, 
        trim_upper(variables) == "AUG_MM_FLAG", 8, 
        trim_upper(variables) == "SEP_MM_FLAG", 9, 
        trim_upper(variables) == "OCT_MM_FLAG", 10, 
        trim_upper(variables) == "NOV_MM_FLAG", 11, 
        trim_upper(variables) == "DEC_MM_FLAG", 12)
    )
  
  #Check the recodes
  table(raw_mm$der_month, raw_mm$variables)
  
  #Second process the raw_srs3_v_vars
  raw_v <- raw_srs3_v_vars %>%
    #Create the numeric version 
    mutate(
      der_v_num = str_match(string=variables, pattern="v(\\d+)")[,2] %>% as.numeric(),
      
      #Create the der_month variable to merge on the mm flag
      der_month = fcase(
        
        
        der_v_num %in% c(CONST_VARS_JAN), 1, 
        der_v_num %in% c(CONST_VARS_FEB), 2, 
        der_v_num %in% c(CONST_VARS_MAR), 3, 
        
        der_v_num %in% c(CONST_VARS_APR), 4, 
        der_v_num %in% c(CONST_VARS_MAY), 5, 
        der_v_num %in% c(CONST_VARS_JUN), 6, 
        
        der_v_num %in% c(CONST_VARS_JUL), 7, 
        der_v_num %in% c(CONST_VARS_AUG), 8, 
        der_v_num %in% c(CONST_VARS_SEP), 9, 
        
        der_v_num %in% c(CONST_VARS_OCT), 10,
        der_v_num %in% c(CONST_VARS_NOV), 11,
        der_v_num %in% c(CONST_VARS_DEC), 12
        
      )
    )
  
  #Check to see if der_month is non missing
  raw_v %>%
    group_by(der_month) %>%
    summarise(
      min_v = min(der_v_num),
      max_v = max(der_v_num)
    ) %>%
    print()
  
  #Next need to merge on raw_v and raw_mm
  raw_v_mm <- raw_v %>%
    select(ORI, STATE_ID_UNIV, der_month, variables,
            #Rename value to srs_value
            srs_value = value) %>%
    full_join(raw_mm  %>%
              select(ORI, STATE_ID_UNIV, der_month,
                     #Rename value to mm_flag_value
                     mm_flag_value= value
                     ), by=c("ORI", "STATE_ID_UNIV", "der_month"))
  
  #Check the dimension
  log_dim(raw_v_mm)
  log_dim(raw_v)
  log_dim(raw_mm)
  
  #Using raw_v_mm, need to make the srs_value that have values of 0 and mm_flag_value of 0 to missing
  raw_v_mm2 <- raw_v_mm %>%
    mutate(
      #Make a one variable to be always TRUE
      one = 1,
      
      final_srs_value = fcase(
        #Make the srs value to be missing if the srs value is 0 and mm flag is 0
        srs_value == 0 & mm_flag_value == 0, NA_real_, 
        one == 1,   srs_value
        
      )
  )
  
  #Next need to transpose the data back from long to wide 
  raw_v_mm3 <- raw_v_mm2 %>%
    #Keep selected variables
    select(
      #Identify the IDs
      !!!(CONST_ID %>% rlang:::parse_exprs()),
      
      #Identify the variables to transpose back
      variables,
      final_srs_value) %>%
    #Make from long to wide and provide back original variable names with final edited values
    spread(key=variables, value=final_srs_value) %>%
    #put in the correct order
    select(
      !!!(CONST_ID %>% rlang:::parse_exprs()),
      !!!(CONST_VARS_ALL_MONTH %>% rlang:::parse_exprs()),
      everything()
    )
  
  #Return the dataset
  return(raw_v_mm3)
    
})  



#Create the srs object
srs3_1 <- final_edited_srs %>%
  full_join(tbd_final_vars, by=CONST_ID)

#Check the joins
log_dim(srs3_1)
log_dim(final_edited_srs)
log_dim(tbd_final_vars)

# Keep the original state variable as numeric instead of factor for later use
srs3_1$STATE_ID_UNIV <- factor(srs3_1$STATE_ID_UNIV,
	levels=CONST_STATE_FACTOR %>% select(state_num) %>% pull(),
	labels=CONST_STATE_FACTOR %>% select(state_factor) %>% pull())

# Make sure only the variables of interest start with the month name as prefix and factors are defined properly
str(srs3_1)

###-------------------------------------------------------------------------------
### Staff count imputation 
###-------------------------------------------------------------------------------

# Specify prediction matrix and variables that need to be included in variable selection
init = mice(srs3_1, maxit=0)
meth = init$method
pred = init$predictorMatrix

incpreds  <- c("state","agn_type","POPULATION_GROUP_ID_UNIV", "suburb_flg")
predQuick <- quickpred(srs3_1, minpuc = 0.25, include = incpreds) 
predQuick[,c("ORI", "REGION_CODE_UNIV", "DIVISION_CODE_UNIV")] <- 0
# Need to convert matrix to DF first - set all the counts and mm_flag vars to 0 so not used for imputation of
# officer counts
predQuick2=as.data.frame(predQuick)
predQuick3 <- predQuick2 %>% mutate(across(
                                .cols = starts_with("v") | ends_with("mm_flag"),
                                .fns = ~ {.x=0},
                                .names = "{.col}"))
# And then convert back to matrix
predQuick4=data.matrix(predQuick3)


# Run the imputation
impLEA = mice(srs3_1, pred=predQuick4, meth="pmm", m=1, seed=254658, maxit=15)

# Plot variables of interest  
#plot(impLEA,c("MALE_OFFICER_UNIV","MALE_CIVILIAN_UNIV","FEMALE_OFFICER_UNIV","FEMALE_CIVILIAN_UNIV"))

# Create complete dataset that will be used to check imputations
LEAcomp <- complete(impLEA,"broad",1)
LEAcomp <- as.data.frame(LEAcomp)

# Create dataset with staff count imputed variables to be used in the next imputation section
ImputedVars <- complete(impLEA,1)

###-------------------------------------------------------------------------------
### Combine different sources of information and calculate CT for imputation
###-------------------------------------------------------------------------------

# Keep only the staff imputed variables and calculate total based on imputed values
ImputedVars <- ImputedVars %>% select(ORI, MALE_OFFICER_UNIV, FEMALE_OFFICER_UNIV, MALE_CIVILIAN_UNIV, FEMALE_CIVILIAN_UNIV)  %>% 
  mutate(TOTAL_OFFICERS=MALE_OFFICER_UNIV+FEMALE_OFFICER_UNIV)
names(ImputedVars)
dim(ImputedVars)


# Read JD's data and merge it to exclude outlier records
out <- read_csv(file.path(outlier_detection_in,"outlier_data_file.csv"))

year_end = substr(year,3,4)

out <- out %>% select(ori, nSeqs, nBlueOutliers, nRedOutliers, nOrangeOutliers, ends_with(year_end)) %>%
  rename(
              p1=paste0("Jan-", year_end),
              p2=paste0("Feb-", year_end),
              p3=paste0("Mar-", year_end),
              p4=paste0("Apr-", year_end),
              p5=paste0("May-", year_end),
              p6=paste0("Jun-", year_end),
              p7=paste0("Jul-", year_end),
              p8=paste0("Aug-", year_end),
              p9=paste0("Sep-", year_end),
              p10=paste0("Oct-", year_end),
              p11=paste0("Nov-", year_end),
              p12=paste0("Dec-", year_end)
       )  

# High outliers - can't be donors
vals <- c("brown","blue")
out <- out %>% rowwise() %>% 
        mutate(out_months=sum(p1 %in% vals, p2 %in% vals, p3 %in% vals, p4 %in% vals,
                              p5 %in% vals, p6 %in% vals, p7 %in% vals, p8 %in% vals,
                              p9 %in% vals, p10 %in% vals, p11 %in% vals, p12 %in% vals, 
                              na.rm=TRUE)) %>%
        mutate(outlier_elig_donor=fcase(out_months==0,1,
                                        out_months>0,0)) %>%
        ungroup()

out_final <- out %>% select(ori,outlier_elig_donor)

ImputedVars_1 <- ImputedVars %>% left_join(out_final,by=c("ORI"="ori")) %>% 
                 mutate(outlier_elig_donor=replace_na(outlier_elig_donor,value=1))

# Merge original file, excluding the original staff counts and state not being a factor
srs3_orig <- srs3 %>% select(-c(MALE_OFFICER_UNIV, MALE_CIVILIAN_UNIV, FEMALE_OFFICER_UNIV, FEMALE_CIVILIAN_UNIV))
srs4 <- left_join(ImputedVars_1, srs3_orig, by =c("ORI"))
names(srs4)
dim(srs4)

# Make sure there are no missing values
summary(srs4$MALE_OFFICER_UNIV)
summary(srs4$FEMALE_OFFICER_UNIV)
summary(srs4$TOTAL_OFFICERS)
summary(srs4$STATE_ID_UNIV)
summary(srs4$agn_type)
summary(srs4$REGION_CODE_UNIV)
summary(srs4$POPULATION_UNIV)

# Calculate crime totals across 12 months
srs4 <- srs4 %>% rowwise() %>%
         mutate(ct=sum(v95,v213,v331,v449,v567,v685,v803,v921,v1039,v1157,v1275,v1393)) %>%
         ungroup()

# Create a NR_flag for non-respondents (=1) and respondents (=0)

rpt <- c(1,9)
srs4 <- srs4 %>%
  rowwise() %>%
  mutate(mosNR = sum(jan_mm_flag==0,feb_mm_flag==0,mar_mm_flag==0,
                     apr_mm_flag==0,may_mm_flag==0,jun_mm_flag==0,
                     jul_mm_flag==0,aug_mm_flag==0,sep_mm_flag==0,
                     oct_mm_flag==0,nov_mm_flag==0,dec_mm_flag==0,na.rm=TRUE)) %>%
  mutate(mosRPT = sum(jan_mm_flag %in% rpt,feb_mm_flag %in% rpt,mar_mm_flag %in% rpt,
                      apr_mm_flag %in% rpt,may_mm_flag %in% rpt,jun_mm_flag %in% rpt,
                      jul_mm_flag %in% rpt,aug_mm_flag %in% rpt,sep_mm_flag %in% rpt,
                      oct_mm_flag %in% rpt,nov_mm_flag %in% rpt,dec_mm_flag %in% rpt,
                      na.rm=TRUE)) %>%
  mutate(mosNA = sum(is.na(jan_mm_flag),is.na(feb_mm_flag),is.na(mar_mm_flag),is.na(apr_mm_flag),
                     is.na(may_mm_flag),is.na(jun_mm_flag),is.na(jul_mm_flag),is.na(aug_mm_flag),
                     is.na(sep_mm_flag),is.na(oct_mm_flag),is.na(nov_mm_flag),is.na(dec_mm_flag)
                     )) %>%
  mutate(NR_flag=ifelse(mosRPT==12,0,1)) %>% #non-respondents
  mutate(partialRPTR=ifelse(NR_flag==1 & mosRPT > 2,1,0)) %>% #partial reporter
  mutate(POP0=ifelse(POPULATION_UNIV==0,1,0)) %>% #pop0 used for imputation classes
  ungroup()

table(srs4$NR_flag,srs4$partialRPTR,useNA="always")



###-------------------------------------------------------------------------------
### Imputation Method #3
###-------------------------------------------------------------------------------

# Define factor variables
srs4_2 <- srs4 %>% mutate_at(c("suburb_flg", "rpt_type", "agn_type", "agn_status", "STATE_ID_UNIV", "REGION_CODE_UNIV", "POP0", "coveringAgency"), as.factor)

# Split between donors and agencies that need imputation
don_m3 <- srs4_2 %>% filter(NR_flag==0 & outlier_elig_donor==1) %>%
                     filter(!(if_any(.cols=starts_with("v"), .fns = ~ .x < 0)))

# Run regression only on donors but no high/low outliers
fit <- lm(ct ~ 
            suburb_flg + agn_type+ STATE_ID_UNIV + POPULATION_UNIV + MALE_OFFICER_UNIV + FEMALE_OFFICER_UNIV + coveringAgency, data=don_m3)

fit2 <- MASS:::stepAIC(fit, direction="both")

pred_m3 <- predict(fit2, srs4_2)

srs4_2['pred'] <- pred_m3

# Split between donors and agencies that need imputation
imp_m3 <- srs4_2 %>% filter(NR_flag==1 & partialRPTR==1)
don_m3 <- srs4_2 %>% filter(NR_flag==0 & outlier_elig_donor==1) %>%
                     filter(!(if_any(.cols=starts_with("v"), .fns = ~ .x < 0)))

# Save the complete cases that can't be donors and agencies reporting < 3 months
don_m3_out <- srs4_2 %>% filter(NR_flag==0 & outlier_elig_donor==0) # outliers
don_m3_neg <- srs4_2 %>% filter(NR_flag==0 & outlier_elig_donor==1) %>%
                         filter((if_any(.cols=starts_with("v"), .fns = ~ .x < 0))) # cases with negative crime counts
non_reporters <- srs4_2 %>% filter(NR_flag==1 & partialRPTR==0) # will save non-reporters for later

imp_m3 <- data.frame(imp_m3)
don_m3 <- data.frame(don_m3)


imp_meth3 <- NND.hotdeck(imp_m3, don_m3, match.vars=c("pred"), don.class=c("POP0","coveringAgency"), dist.fun="Euclidean", k=5)

# Get a list of the donor variables we need
dummyd <- don_m3 %>% select("ORI","ct","pred",starts_with("v"))
donorvars <- colnames(dummyd)

dat_m3_grp1 <- create.fused(imp_m3, don_m3, imp_meth3$mtc.ids, dup.x=T, 
                            match.vars=donorvars, z.vars=NULL)



imp_dat <- dat_m3_grp1 %>% mutate(across(num_range("v", 70:95),
                                  .fns= ~ fcase(jan_mm_flag==0 , get(glue::glue("{cur_column()}.don")),
                                                jan_mm_flag %in% c(1,9) , .x,
                                                default = -9),
                                  .names="{.col}")) %>%
                           mutate(across(num_range("v", 188:213),
                                  .fns= ~ fcase(feb_mm_flag==0 , get(glue::glue("{cur_column()}.don")),
                                                feb_mm_flag %in% c(1,9) , .x,
                                                default = -9),
                                  .names="{.col}")) %>%
                           mutate(across(num_range("v", 306:331),
                                  .fns= ~ fcase(mar_mm_flag==0 , get(glue::glue("{cur_column()}.don")),
                                                mar_mm_flag %in% c(1,9) , .x,
                                                default = -9),
                                  .names="{.col}")) %>%
                           mutate(across(num_range("v", 424:449),
                                  .fns= ~ fcase(apr_mm_flag==0 , get(glue::glue("{cur_column()}.don")),
                                                apr_mm_flag %in% c(1,9) , .x,
                                                default = -9),
                                  .names="{.col}")) %>%
                           mutate(across(num_range("v", 542:567),
                                  .fns= ~ fcase(may_mm_flag==0 , get(glue::glue("{cur_column()}.don")),
                                                may_mm_flag %in% c(1,9) , .x,
                                                default = -9),
                                  .names="{.col}")) %>%
                           mutate(across(num_range("v", 660:685),
                                  .fns= ~ fcase(jun_mm_flag==0 , get(glue::glue("{cur_column()}.don")),
                                                jun_mm_flag %in% c(1,9) , .x,
                                                default = -9),
                                  .names="{.col}")) %>%
                           mutate(across(num_range("v", 778:803),
                                  .fns= ~ fcase(jul_mm_flag==0 , get(glue::glue("{cur_column()}.don")),
                                                jul_mm_flag %in% c(1,9) , .x,
                                                default = -9),
                                  .names="{.col}")) %>%
                           mutate(across(num_range("v", 896:921),
                                  .fns= ~ fcase(aug_mm_flag==0 , get(glue::glue("{cur_column()}.don")),
                                                aug_mm_flag %in% c(1,9) , .x,
                                                default = -9),
                                  .names="{.col}")) %>%
                           mutate(across(num_range("v", 1014:1039),
                                  .fns= ~ fcase(sep_mm_flag==0 , get(glue::glue("{cur_column()}.don")),
                                                sep_mm_flag %in% c(1,9) , .x,
                                                default = -9),
                                  .names="{.col}")) %>%
                           mutate(across(num_range("v", 1132:1157),
                                  .fns= ~ fcase(oct_mm_flag==0 , get(glue::glue("{cur_column()}.don")),
                                                oct_mm_flag %in% c(1,9) , .x,
                                                default = -9),
                                  .names="{.col}")) %>%
                           mutate(across(num_range("v", 1250:1275),
                                  .fns= ~ fcase(nov_mm_flag==0 , get(glue::glue("{cur_column()}.don")),
                                                nov_mm_flag %in% c(1,9) , .x,
                                                default = -9),
                                  .names="{.col}")) %>%
                           mutate(across(num_range("v", 1368:1393),
                                  .fns= ~ fcase(dec_mm_flag==0 , get(glue::glue("{cur_column()}.don")),
                                                dec_mm_flag %in% c(1,9) , .x,
                                                default = -9),
                                  .names="{.col}")) 


imp_dat2 <- imp_dat %>% select(!ends_with(".don"))

# Combine all of the agency records (do not include ineligible agencies)
all_dat <- imp_dat2 %>% # imputed cases
           bind_rows(don_m3) %>% # donors
           bind_rows(don_m3_out) %>% # outliers
           bind_rows(don_m3_neg) %>% # respondents with negative crime counts
           bind_rows(non_reporters) %>% # reported < 3 months
           rename(MALE_OFFICER_IMP=MALE_OFFICER_UNIV,FEMALE_OFFICER_IMP=FEMALE_OFFICER_UNIV,
                  MALE_CIVILIAN_IMP=MALE_CIVILIAN_UNIV,FEMALE_CIVILIAN_IMP=FEMALE_CIVILIAN_UNIV,
                  TOTAL_OFFICERS_IMP=TOTAL_OFFICERS) %>%
           select(ORI,starts_with("v"),ends_with("mm_flag"),ends_with("_IMP"),mosRPT,NR_flag,partialRPTR)

univ_vars <- srs %>% select(ORI,ends_with("_UNIV"),der_in_univ_elig) %>% filter(der_in_univ_elig==1)

final_imp_dat <- univ_vars %>% left_join(all_dat,by=c("ORI"))

write_csv(final_imp_dat,file.path(block_imputation_output, "SRS_Imputed.csv"))

# Output the donor IDs for imputed cases
donorids <- dat_m3_grp1 %>% select("ORI","ORI.don")

write_csv(donorids,file.path(block_imputation_output, "donor_ids_srs_imp.csv"))

