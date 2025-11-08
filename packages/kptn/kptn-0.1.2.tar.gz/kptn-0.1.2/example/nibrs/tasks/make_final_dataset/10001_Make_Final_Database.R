# ---
# title: '10001 - Make Final Database'
# author: "Philip Lee"
# date: "October 1, 2021"
# output:
#   html_document: default
#   pdf_document:  default
# ---

#Read in the common code starting code for program
source("0-Common Code for Suppression.R")

log_info(paste0("RUNNING 10001 - Make Final Database ",PERMUTATION_NAME, " Table ", TABLE_NAME))


#Need to edit raw_list_files and keep files we are interested in

raw_list_files1 <- raw_list_files %>%
  as_tibble() %>%
  #Create variables to identify which files to keep
  mutate(
    der_file_table              = str_match(string=value, pattern="Table (\\w+)_Reporting_Database_After_Variance_(\\d+).csv")[,2]
  ) %>%
  mutate(
    der_file_table_keep = fcase(der_file_table %in% c(TABLE_NAME), 1,
                                default = 0)
)

#Check the recodes
raw_list_files1 %>% checkfunction(der_file_table, value)
raw_list_files1 %>% checkfunction(der_file_table_keep, der_file_table)


#Keep the files we are interested in for momentum rule and overwrite old variable
raw_list_files <- raw_list_files1 %>%
  filter(der_file_table_keep == 1) %>%
  select(value) %>%
  pull()

print(raw_list_files)


#Stack all the files together
raw_1 <- vector("list", length(raw_list_files))

for(i in 1:length(raw_list_files)){

  #Get the current file name and the permutation number
  raw_perm_num <- str_match(raw_list_files[[i]], "(\\d+)\\.csv") %>%
    as_tibble() %>%
    select(V2) %>%
    pull()

  #Save the data to the list
  raw_1[[i]] <- read_csv1(paste0(estimate_paths_after_variance, raw_list_files[[i]]), col_types=raw_files_column_type) %>%
    mutate(PERMUTATION_NUMBER = as.numeric(raw_perm_num),
           FILE_NAME =  raw_list_files[[i]])

  #Delete the items
  rm(raw_perm_num)
  invisible(gc())

}


#raw_2 contains the combined data
raw_2 <- bind_rows(raw_1) %>%
	#Drop the PRB_ACTUAL variable and use estimate_prb
	select(-PRB_ACTUAL) %>%
	mutate(PRB_ACTUAL = estimate_prb)

log_dim(raw_2)


#Create the der_variable_name variable, since some variables are not created if the estimate is zero (i.e. no counts)
raw_3 <- create_variables_for_id(indata=raw_2)
         

#Check to see which variables have no counts and also make sure that the der_variable_name is created correctly
raw_3 %>%
  checkfunction(der_variable_name, variable_name)

raw_3 %>%
  checkfunction(der_demographic_main_number, PERMUTATION_NUMBER)

raw_3 %>%
  checkfunction(der_geographic_main_number, PERMUTATION_NUMBER)


#Next need to merge on the Population file
raw_pop <- read_csv1(paste0(filepathin_initial, "POP_TOTALS_PERM_", year, ".csv"))
#Add on a prefix so not to create duplicate variables
colnames(raw_pop) <- paste0("POPTOTAL_", colnames(raw_pop))

raw_4 <- raw_3 %>%
  left_join(raw_pop, by=c("PERMUTATION_NUMBER" = "POPTOTAL_PERMUTATION_NUMBER"))

log_dim(raw_3)
log_dim(raw_pop)
log_dim(raw_4)

#Fix the population variable population_estimate when estimate_type = "rate" and is.na(population_estimate)
raw_4 %>%
  filter(trim_upcase(estimate_type) == "RATE" & is.na(population_estimate) ) %>%
  checkfunction(estimate_type, population_estimate, estimate)

#########################Make 100% population coverage to have 0 rmse variables#############
tbd_estimate_0 <- c(
  "estimate_standard_error", 
  "estimate_prb",
  "estimate_bias",
  "estimate_rmse",
  "relative_standard_error",
  "relative_rmse",
  "PRB_ACTUAL"
)

tbd_ci_same <- c(
  "estimate_upper_bound",
  "estimate_lower_bound"  
)


raw_4 <- raw_4 %>%
  mutate(
    #Make the estimates to 0 for the 100% population coverage, if not the NA code and not missing
    across(
      .cols = any_of(tbd_estimate_0),
      .fns = ~{
        fcase(
          #Keep NA code as is
          .x == DER_NA_CODE, DER_NA_CODE,
          #If estimate is not missing and population coverage is 100%
          !is.na(.x) & POPTOTAL_UNIV_POP_COV == 1, 0,
          #Otherwise leave estimate as is
          !is.na(.x), .x
        )}
    )
  )

raw_4 <- raw_4 %>%
  mutate(
    #Make the confidence intervals to be the same as the estimate, if not the NA code and not missing
    across(
      .cols = any_of(tbd_ci_same),
      .fns = ~{
        fcase(
          #Keep NA code as is
          .x == DER_NA_CODE, DER_NA_CODE,
          #If estimate is not missing and population coverage is 100%
          !is.na(.x) & POPTOTAL_UNIV_POP_COV == 1, estimate,
          #Otherwise leave estimate as is
          !is.na(.x), .x          
        )}
    )
  )  


#Delete the tbd variables
rm(tbd_estimate_0, tbd_ci_same)
invisible(gc())


############################################################################################




raw_5 <- raw_4 %>%
  mutate(

    #Create indicator variable
    population_estimate_na_ind = fcase(
      is.na(population_estimate),  1,
      default = 0),

    #Save original variable for QC
    population_estimate_org = population_estimate,

    #Fix the population_estimate variable
    population_estimate = fcase(
    #If population_estimate is not missing then it is fine
    !is.na(population_estimate),  population_estimate,

    #Code for fixes in this workbook Final_Clean_Up_Code.xlsx
    trim_upcase(table)=="1A" & row == 2 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Incident rate (per 100k total pop)
    trim_upcase(table)=="1B" & row == 2 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Incident rate (per 100k total pop)
    trim_upcase(table)=="1C" & row == 2 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Incident rate (per 100k total pop)
    trim_upcase(table)=="2A" & row == 2 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Offense rate (per 100k total pop)
    trim_upcase(table)=="2B" & row == 2 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Offense rate (per 100k total pop)
    trim_upcase(table)=="2C" & row == 2 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Offense rate (per 100k total pop)
    trim_upcase(table)=="3A" & row == 3 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victimization rate (per 100k total pop)
    trim_upcase(table)=="3A" & row == 4 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_OFFICER_NUM_WEIGHTED, #Victimization rate (per 100k LE staff): Law enforcement officers
    trim_upcase(table)=="3AUNCLEAR" & row == 3 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victimization rate (per 100k total pop)
    trim_upcase(table)=="3AUNCLEAR" & row == 4 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_OFFICER_NUM_WEIGHTED, #Victimization rate (per 100k LE staff): Law enforcement officers
    trim_upcase(table)=="3ACLEAR" & row == 3 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victimization rate (per 100k total pop)
    trim_upcase(table)=="3ACLEAR" & row == 4 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_OFFICER_NUM_WEIGHTED, #Victimization rate (per 100k LE staff): Law enforcement officers
    trim_upcase(table)=="3B" & row == 3 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victimization rate (per 100k total pop)
    trim_upcase(table)=="3B" & row == 4 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_OFFICER_NUM_WEIGHTED, #Victimization rate (per 100k LE staff): Law enforcement officers
    trim_upcase(table)=="3B" & row == 5 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGELT5_NUM_WEIGHTED, #Under 5
    trim_upcase(table)=="3B" & row == 6 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE5TO14_NUM_WEIGHTED, #5-14
    trim_upcase(table)=="3B" & row == 7 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE15_NUM_WEIGHTED, #15
    trim_upcase(table)=="3B" & row == 8 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE16_NUM_WEIGHTED, #16
    trim_upcase(table)=="3B" & row == 9 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE17_NUM_WEIGHTED, #17
    trim_upcase(table)=="3B" & row == 10 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE18TO24_NUM_WEIGHTED, #18-24
    trim_upcase(table)=="3B" & row == 11 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE25TO34_NUM_WEIGHTED, #25-34
    trim_upcase(table)=="3B" & row == 12 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE35TO64_NUM_WEIGHTED, #35-64
    trim_upcase(table)=="3B" & row == 13 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGEGTE65_NUM_WEIGHTED, #65+
    trim_upcase(table)=="3B" & row == 14 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Unknown
    trim_upcase(table)=="3B" & row == 15 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTSEXMALE_NUM_WEIGHTED, #Male
    trim_upcase(table)=="3B" & row == 16 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTSEXFEMALE_NUM_WEIGHTED, #Female
    trim_upcase(table)=="3B" & row == 17 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Unknown
    trim_upcase(table)=="3B" & row == 18 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACEWHITE_NUM_WEIGHTED, #White
    trim_upcase(table)=="3B" & row == 19 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACEBLACK_NUM_WEIGHTED, #Black
    trim_upcase(table)=="3B" & row == 20 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACEAIAN_NUM_WEIGHTED, #American Indian or Alaska Native
    trim_upcase(table)=="3B" & row == 21 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACEASIAN_NUM_WEIGHTED, #Asian
    trim_upcase(table)=="3B" & row == 22 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACENHPI_NUM_WEIGHTED, #Native Hawaiian or Other Pacific Islander
    trim_upcase(table)=="3B" & row == 23 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Unknown
    trim_upcase(table)=="3B" & row == 24 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_UNDER_12_NUM_WEIGHTED, #Victim Age 2: Under 12
    trim_upcase(table)=="3B" & row == 25 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_12_17_NUM_WEIGHTED, #Victim Age 2: 12-17
    trim_upcase(table)=="3B" & row == 26 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_12_14_NUM_WEIGHTED, #Victim Age 2: 12-14
    trim_upcase(table)=="3B" & row == 27 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_15_17_NUM_WEIGHTED, #Victim Age 2: 15-17
    trim_upcase(table)=="3B" & row == 28 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_OVER_18_NUM_WEIGHTED, #Victim Age 2: 18+
    trim_upcase(table)=="3B" & row == 29 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim Age 2: Unknown
    trim_upcase(table)=="3B" & row == 30 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved: No
    trim_upcase(table)=="3B" & row == 31 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved: Yes
    trim_upcase(table)=="3B" & row == 32 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved: Personal weapons
    trim_upcase(table)=="3B" & row == 33 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved: Firearms
    trim_upcase(table)=="3B" & row == 34 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved: Knives and other cutting instruments
    trim_upcase(table)=="3B" & row == 35 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved: Blunt instruments
    trim_upcase(table)=="3B" & row == 36 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved: Other non-personal weapons
    trim_upcase(table)=="3B" & row == 37 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved: Unknown
    trim_upcase(table)=="3B" & row == 38 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship: Intimate partner
    trim_upcase(table)=="3B" & row == 39 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship: Other family
    trim_upcase(table)=="3B" & row == 40 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship: Outside family but known to victim
    trim_upcase(table)=="3B" & row == 41 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship: Stranger
    trim_upcase(table)=="3B" & row == 42 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship: Victim was Offender
    trim_upcase(table)=="3B" & row == 43 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship: Unknown relationship
    trim_upcase(table)=="3B" & row == 44 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Handgun
    trim_upcase(table)=="3B" & row == 45 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Firearm
    trim_upcase(table)=="3B" & row == 46 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Rifle
    trim_upcase(table)=="3B" & row == 47 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Shotgun
    trim_upcase(table)=="3B" & row == 48 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Other Firearm
    trim_upcase(table)=="3B" & row == 49 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Knife/Cutting Instrument
    trim_upcase(table)=="3B" & row == 50 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Blunt Object
    trim_upcase(table)=="3B" & row == 51 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Motor Vehicle
    trim_upcase(table)=="3B" & row == 52 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Personal Weapons (hands, feet, teeth, etc.)
    trim_upcase(table)=="3B" & row == 53 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Asphyxiation
    trim_upcase(table)=="3B" & row == 54 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Drugs/Narcotics/Sleeping Pills
    trim_upcase(table)=="3B" & row == 55 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Poison (include gas)
    trim_upcase(table)=="3B" & row == 56 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Explosives
    trim_upcase(table)=="3B" & row == 57 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Fire/Incendiary Device
    trim_upcase(table)=="3B" & row == 58 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Other
    trim_upcase(table)=="3B" & row == 59 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: No Weapon
    trim_upcase(table)=="3B" & row == 60 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Unknown
    trim_upcase(table)=="3B" & row == 61 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Not Applicable
    trim_upcase(table)=="3B" & row == 62 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Intimate partner
    trim_upcase(table)=="3B" & row == 63 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Other family
    trim_upcase(table)=="3B" & row == 64 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Outside family but known to victim
    trim_upcase(table)=="3B" & row == 65 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Stranger
    trim_upcase(table)=="3B" & row == 66 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Victim was Offender
    trim_upcase(table)=="3B" & row == 67 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Unknown relationship
    trim_upcase(table)=="3B" & row == 68 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Unknown Offender Incidents
    trim_upcase(table)=="3B" & row == 69 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Missing from Uncleared Incidents
    trim_upcase(table)=="3B" & row == 70 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_HISP_NUM_WEIGHTED, #Hispanic Origin-specific victimization rate:   Hispanic or Latino
    trim_upcase(table)=="3B" & row == 71 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_NUM_WEIGHTED, #Hispanic Origin-specific victimization rate:   Not Hispanic or Latino
    trim_upcase(table)=="3B" & row == 72 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Hispanic Origin-specific victimization rate:   Unknown
    trim_upcase(table)=="3B" & row == 73 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_HISP_NUM_WEIGHTED, #Race and Hispanic Origin-specific victimization rate:   Hispanic or Latino
    trim_upcase(table)=="3B" & row == 74 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_WHITE_NUM_WEIGHTED, #Race and Hispanic Origin-specific victimization rate:   Non-Hispanic, White
    trim_upcase(table)=="3B" & row == 75 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_BLACK_NUM_WEIGHTED, #Race and Hispanic Origin-specific victimization rate:   Non-Hispanic, Black
    trim_upcase(table)=="3B" & row == 76 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_AIAN_NUM_WEIGHTED, #Race and Hispanic Origin-specific victimization rate:   Non-Hispanic, American Indian or Alaska Native
    trim_upcase(table)=="3B" & row == 77 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_ASIAN_NUM_WEIGHTED, #Race and Hispanic Origin-specific victimization rate:   Non-Hispanic, Asian
    trim_upcase(table)=="3B" & row == 78 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_NHOPI_NUM_WEIGHTED, #Race and Hispanic Origin-specific victimization rate:   Non-Hispanic, Native Hawaiian or Other Pacific Islander
    trim_upcase(table)=="3B" & row == 79 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Race and Hispanic Origin-specific victimization rate:   Unknown race or Hispanic origin
    trim_upcase(table)=="3BUNCLEAR" & row == 3 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victimization rate (per 100k total pop)
    trim_upcase(table)=="3BUNCLEAR" & row == 4 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_OFFICER_NUM_WEIGHTED, #Victimization rate (per 100k LE staff): Law enforcement officers
    trim_upcase(table)=="3BUNCLEAR" & row == 5 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGELT5_NUM_WEIGHTED, #Under 5
    trim_upcase(table)=="3BUNCLEAR" & row == 6 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE5TO14_NUM_WEIGHTED, #5-14
    trim_upcase(table)=="3BUNCLEAR" & row == 7 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE15_NUM_WEIGHTED, #15
    trim_upcase(table)=="3BUNCLEAR" & row == 8 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE16_NUM_WEIGHTED, #16
    trim_upcase(table)=="3BUNCLEAR" & row == 9 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE17_NUM_WEIGHTED, #17
    trim_upcase(table)=="3BUNCLEAR" & row == 10 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE18TO24_NUM_WEIGHTED, #18-24
    trim_upcase(table)=="3BUNCLEAR" & row == 11 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE25TO34_NUM_WEIGHTED, #25-34
    trim_upcase(table)=="3BUNCLEAR" & row == 12 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE35TO64_NUM_WEIGHTED, #35-64
    trim_upcase(table)=="3BUNCLEAR" & row == 13 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGEGTE65_NUM_WEIGHTED, #65+
    trim_upcase(table)=="3BUNCLEAR" & row == 14 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Unknown
    trim_upcase(table)=="3BUNCLEAR" & row == 15 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTSEXMALE_NUM_WEIGHTED, #Male
    trim_upcase(table)=="3BUNCLEAR" & row == 16 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTSEXFEMALE_NUM_WEIGHTED, #Female
    trim_upcase(table)=="3BUNCLEAR" & row == 17 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Unknown
    trim_upcase(table)=="3BUNCLEAR" & row == 18 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACEWHITE_NUM_WEIGHTED, #White
    trim_upcase(table)=="3BUNCLEAR" & row == 19 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACEBLACK_NUM_WEIGHTED, #Black
    trim_upcase(table)=="3BUNCLEAR" & row == 20 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACEAIAN_NUM_WEIGHTED, #American Indian or Alaska Native
    trim_upcase(table)=="3BUNCLEAR" & row == 21 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACEASIAN_NUM_WEIGHTED, #Asian
    trim_upcase(table)=="3BUNCLEAR" & row == 22 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACENHPI_NUM_WEIGHTED, #Native Hawaiian or Other Pacific Islander
    trim_upcase(table)=="3BUNCLEAR" & row == 23 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Unknown
    trim_upcase(table)=="3BUNCLEAR" & row == 24 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_UNDER_12_NUM_WEIGHTED, #Victim Age 2: Under 12
    trim_upcase(table)=="3BUNCLEAR" & row == 25 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_12_17_NUM_WEIGHTED, #Victim Age 2: 12-17
    trim_upcase(table)=="3BUNCLEAR" & row == 26 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_12_14_NUM_WEIGHTED, #Victim Age 2: 12-14
    trim_upcase(table)=="3BUNCLEAR" & row == 27 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_15_17_NUM_WEIGHTED, #Victim Age 2: 15-17
    trim_upcase(table)=="3BUNCLEAR" & row == 28 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_OVER_18_NUM_WEIGHTED, #Victim Age 2: 18+
    trim_upcase(table)=="3BUNCLEAR" & row == 29 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim Age 2: Unknown
    trim_upcase(table)=="3BUNCLEAR" & row == 30 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved: No
    trim_upcase(table)=="3BUNCLEAR" & row == 31 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved: Yes
    trim_upcase(table)=="3BUNCLEAR" & row == 32 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved: Personal weapons
    trim_upcase(table)=="3BUNCLEAR" & row == 33 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved: Firearms
    trim_upcase(table)=="3BUNCLEAR" & row == 34 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved: Knives and other cutting instruments
    trim_upcase(table)=="3BUNCLEAR" & row == 35 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved: Blunt instruments
    trim_upcase(table)=="3BUNCLEAR" & row == 36 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved: Other non-personal weapons
    trim_upcase(table)=="3BUNCLEAR" & row == 37 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved: Unknown
    trim_upcase(table)=="3BUNCLEAR" & row == 38 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship: Intimate partner
    trim_upcase(table)=="3BUNCLEAR" & row == 39 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship: Other family
    trim_upcase(table)=="3BUNCLEAR" & row == 40 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship: Outside family but known to victim
    trim_upcase(table)=="3BUNCLEAR" & row == 41 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship: Stranger
    trim_upcase(table)=="3BUNCLEAR" & row == 42 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship: Victim was Offender
    trim_upcase(table)=="3BUNCLEAR" & row == 43 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship: Unknown relationship
    trim_upcase(table)=="3BUNCLEAR" & row == 44 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Handgun
    trim_upcase(table)=="3BUNCLEAR" & row == 45 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Firearm
    trim_upcase(table)=="3BUNCLEAR" & row == 46 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Rifle
    trim_upcase(table)=="3BUNCLEAR" & row == 47 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Shotgun
    trim_upcase(table)=="3BUNCLEAR" & row == 48 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Other Firearm
    trim_upcase(table)=="3BUNCLEAR" & row == 49 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Knife/Cutting Instrument
    trim_upcase(table)=="3BUNCLEAR" & row == 50 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Blunt Object
    trim_upcase(table)=="3BUNCLEAR" & row == 51 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Motor Vehicle
    trim_upcase(table)=="3BUNCLEAR" & row == 52 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Personal Weapons (hands, feet, teeth, etc.)
    trim_upcase(table)=="3BUNCLEAR" & row == 53 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Asphyxiation
    trim_upcase(table)=="3BUNCLEAR" & row == 54 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Drugs/Narcotics/Sleeping Pills
    trim_upcase(table)=="3BUNCLEAR" & row == 55 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Poison (include gas)
    trim_upcase(table)=="3BUNCLEAR" & row == 56 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Explosives
    trim_upcase(table)=="3BUNCLEAR" & row == 57 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Fire/Incendiary Device
    trim_upcase(table)=="3BUNCLEAR" & row == 58 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Other
    trim_upcase(table)=="3BUNCLEAR" & row == 59 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: No Weapon
    trim_upcase(table)=="3BUNCLEAR" & row == 60 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Unknown
    trim_upcase(table)=="3BUNCLEAR" & row == 61 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Not Applicable
    trim_upcase(table)=="3BUNCLEAR" & row == 62 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Intimate partner
    trim_upcase(table)=="3BUNCLEAR" & row == 63 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Other family
    trim_upcase(table)=="3BUNCLEAR" & row == 64 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Outside family but known to victim
    trim_upcase(table)=="3BUNCLEAR" & row == 65 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Stranger
    trim_upcase(table)=="3BUNCLEAR" & row == 66 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Victim was Offender
    trim_upcase(table)=="3BUNCLEAR" & row == 67 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Unknown relationship
    trim_upcase(table)=="3BUNCLEAR" & row == 68 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Unknown Offender Incidents
    trim_upcase(table)=="3BUNCLEAR" & row == 69 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Missing from Uncleared Incidents
    trim_upcase(table)=="3BUNCLEAR" & row == 70 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_HISP_NUM_WEIGHTED, #Hispanic Origin-specific victimization rate:   Hispanic or Latino
    trim_upcase(table)=="3BUNCLEAR" & row == 71 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_NUM_WEIGHTED, #Hispanic Origin-specific victimization rate:   Not Hispanic or Latino
    trim_upcase(table)=="3BUNCLEAR" & row == 72 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Hispanic Origin-specific victimization rate:   Unknown
    trim_upcase(table)=="3BUNCLEAR" & row == 73 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_HISP_NUM_WEIGHTED, #Race and Hispanic Origin-specific victimization rate:   Hispanic or Latino
    trim_upcase(table)=="3BUNCLEAR" & row == 74 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_WHITE_NUM_WEIGHTED, #Race and Hispanic Origin-specific victimization rate:   Non-Hispanic, White
    trim_upcase(table)=="3BUNCLEAR" & row == 75 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_BLACK_NUM_WEIGHTED, #Race and Hispanic Origin-specific victimization rate:   Non-Hispanic, Black
    trim_upcase(table)=="3BUNCLEAR" & row == 76 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_AIAN_NUM_WEIGHTED, #Race and Hispanic Origin-specific victimization rate:   Non-Hispanic, American Indian or Alaska Native
    trim_upcase(table)=="3BUNCLEAR" & row == 77 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_ASIAN_NUM_WEIGHTED, #Race and Hispanic Origin-specific victimization rate:   Non-Hispanic, Asian
    trim_upcase(table)=="3BUNCLEAR" & row == 78 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_NHOPI_NUM_WEIGHTED, #Race and Hispanic Origin-specific victimization rate:   Non-Hispanic, Native Hawaiian or Other Pacific Islander
    trim_upcase(table)=="3BUNCLEAR" & row == 79 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Race and Hispanic Origin-specific victimization rate:   Unknown race or Hispanic origin
    trim_upcase(table)=="3BCLEAR" & row == 3 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victimization rate (per 100k total pop)
    trim_upcase(table)=="3BCLEAR" & row == 4 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_OFFICER_NUM_WEIGHTED, #Victimization rate (per 100k LE staff): Law enforcement officers
    trim_upcase(table)=="3BCLEAR" & row == 5 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGELT5_NUM_WEIGHTED, #Under 5
    trim_upcase(table)=="3BCLEAR" & row == 6 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE5TO14_NUM_WEIGHTED, #5-14
    trim_upcase(table)=="3BCLEAR" & row == 7 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE15_NUM_WEIGHTED, #15
    trim_upcase(table)=="3BCLEAR" & row == 8 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE16_NUM_WEIGHTED, #16
    trim_upcase(table)=="3BCLEAR" & row == 9 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE17_NUM_WEIGHTED, #17
    trim_upcase(table)=="3BCLEAR" & row == 10 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE18TO24_NUM_WEIGHTED, #18-24
    trim_upcase(table)=="3BCLEAR" & row == 11 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE25TO34_NUM_WEIGHTED, #25-34
    trim_upcase(table)=="3BCLEAR" & row == 12 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE35TO64_NUM_WEIGHTED, #35-64
    trim_upcase(table)=="3BCLEAR" & row == 13 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGEGTE65_NUM_WEIGHTED, #65+
    trim_upcase(table)=="3BCLEAR" & row == 14 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Unknown
    trim_upcase(table)=="3BCLEAR" & row == 15 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTSEXMALE_NUM_WEIGHTED, #Male
    trim_upcase(table)=="3BCLEAR" & row == 16 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTSEXFEMALE_NUM_WEIGHTED, #Female
    trim_upcase(table)=="3BCLEAR" & row == 17 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Unknown
    trim_upcase(table)=="3BCLEAR" & row == 18 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACEWHITE_NUM_WEIGHTED, #White
    trim_upcase(table)=="3BCLEAR" & row == 19 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACEBLACK_NUM_WEIGHTED, #Black
    trim_upcase(table)=="3BCLEAR" & row == 20 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACEAIAN_NUM_WEIGHTED, #American Indian or Alaska Native
    trim_upcase(table)=="3BCLEAR" & row == 21 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACEASIAN_NUM_WEIGHTED, #Asian
    trim_upcase(table)=="3BCLEAR" & row == 22 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACENHPI_NUM_WEIGHTED, #Native Hawaiian or Other Pacific Islander
    trim_upcase(table)=="3BCLEAR" & row == 23 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Unknown
    trim_upcase(table)=="3BCLEAR" & row == 24 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_UNDER_12_NUM_WEIGHTED, #Victim Age 2: Under 12
    trim_upcase(table)=="3BCLEAR" & row == 25 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_12_17_NUM_WEIGHTED, #Victim Age 2: 12-17
    trim_upcase(table)=="3BCLEAR" & row == 26 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_12_14_NUM_WEIGHTED, #Victim Age 2: 12-14
    trim_upcase(table)=="3BCLEAR" & row == 27 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_15_17_NUM_WEIGHTED, #Victim Age 2: 15-17
    trim_upcase(table)=="3BCLEAR" & row == 28 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_OVER_18_NUM_WEIGHTED, #Victim Age 2: 18+
    trim_upcase(table)=="3BCLEAR" & row == 29 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim Age 2: Unknown
    trim_upcase(table)=="3BCLEAR" & row == 30 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved: No
    trim_upcase(table)=="3BCLEAR" & row == 31 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved: Yes
    trim_upcase(table)=="3BCLEAR" & row == 32 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved: Personal weapons
    trim_upcase(table)=="3BCLEAR" & row == 33 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved: Firearms
    trim_upcase(table)=="3BCLEAR" & row == 34 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved: Knives and other cutting instruments
    trim_upcase(table)=="3BCLEAR" & row == 35 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved: Blunt instruments
    trim_upcase(table)=="3BCLEAR" & row == 36 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved: Other non-personal weapons
    trim_upcase(table)=="3BCLEAR" & row == 37 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved: Unknown
    trim_upcase(table)=="3BCLEAR" & row == 38 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship: Intimate partner
    trim_upcase(table)=="3BCLEAR" & row == 39 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship: Other family
    trim_upcase(table)=="3BCLEAR" & row == 40 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship: Outside family but known to victim
    trim_upcase(table)=="3BCLEAR" & row == 41 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship: Stranger
    trim_upcase(table)=="3BCLEAR" & row == 42 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship: Victim was Offender
    trim_upcase(table)=="3BCLEAR" & row == 43 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship: Unknown relationship
    trim_upcase(table)=="3BCLEAR" & row == 44 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Handgun
    trim_upcase(table)=="3BCLEAR" & row == 45 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Firearm
    trim_upcase(table)=="3BCLEAR" & row == 46 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Rifle
    trim_upcase(table)=="3BCLEAR" & row == 47 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Shotgun
    trim_upcase(table)=="3BCLEAR" & row == 48 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Other Firearm
    trim_upcase(table)=="3BCLEAR" & row == 49 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Knife/Cutting Instrument
    trim_upcase(table)=="3BCLEAR" & row == 50 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Blunt Object
    trim_upcase(table)=="3BCLEAR" & row == 51 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Motor Vehicle
    trim_upcase(table)=="3BCLEAR" & row == 52 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Personal Weapons (hands, feet, teeth, etc.)
    trim_upcase(table)=="3BCLEAR" & row == 53 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Asphyxiation
    trim_upcase(table)=="3BCLEAR" & row == 54 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Drugs/Narcotics/Sleeping Pills
    trim_upcase(table)=="3BCLEAR" & row == 55 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Poison (include gas)
    trim_upcase(table)=="3BCLEAR" & row == 56 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Explosives
    trim_upcase(table)=="3BCLEAR" & row == 57 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Fire/Incendiary Device
    trim_upcase(table)=="3BCLEAR" & row == 58 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Other
    trim_upcase(table)=="3BCLEAR" & row == 59 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: No Weapon
    trim_upcase(table)=="3BCLEAR" & row == 60 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Unknown
    trim_upcase(table)=="3BCLEAR" & row == 61 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Weapon involved hierarchy: Not Applicable
    trim_upcase(table)=="3BCLEAR" & row == 62 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Intimate partner
    trim_upcase(table)=="3BCLEAR" & row == 63 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Other family
    trim_upcase(table)=="3BCLEAR" & row == 64 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Outside family but known to victim
    trim_upcase(table)=="3BCLEAR" & row == 65 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Stranger
    trim_upcase(table)=="3BCLEAR" & row == 66 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Victim was Offender
    trim_upcase(table)=="3BCLEAR" & row == 67 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Unknown relationship
    trim_upcase(table)=="3BCLEAR" & row == 68 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Unknown Offender Incidents
    trim_upcase(table)=="3BCLEAR" & row == 69 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Missing from Uncleared Incidents
    trim_upcase(table)=="3BCLEAR" & row == 70 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_HISP_NUM_WEIGHTED, #Hispanic Origin-specific victimization rate:   Hispanic or Latino
    trim_upcase(table)=="3BCLEAR" & row == 71 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_NUM_WEIGHTED, #Hispanic Origin-specific victimization rate:   Not Hispanic or Latino
    trim_upcase(table)=="3BCLEAR" & row == 72 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Hispanic Origin-specific victimization rate:   Unknown
    trim_upcase(table)=="3BCLEAR" & row == 73 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_HISP_NUM_WEIGHTED, #Race and Hispanic Origin-specific victimization rate:   Hispanic or Latino
    trim_upcase(table)=="3BCLEAR" & row == 74 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_WHITE_NUM_WEIGHTED, #Race and Hispanic Origin-specific victimization rate:   Non-Hispanic, White
    trim_upcase(table)=="3BCLEAR" & row == 75 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_BLACK_NUM_WEIGHTED, #Race and Hispanic Origin-specific victimization rate:   Non-Hispanic, Black
    trim_upcase(table)=="3BCLEAR" & row == 76 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_AIAN_NUM_WEIGHTED, #Race and Hispanic Origin-specific victimization rate:   Non-Hispanic, American Indian or Alaska Native
    trim_upcase(table)=="3BCLEAR" & row == 77 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_ASIAN_NUM_WEIGHTED, #Race and Hispanic Origin-specific victimization rate:   Non-Hispanic, Asian
    trim_upcase(table)=="3BCLEAR" & row == 78 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_NHOPI_NUM_WEIGHTED, #Race and Hispanic Origin-specific victimization rate:   Non-Hispanic, Native Hawaiian or Other Pacific Islander
    trim_upcase(table)=="3BCLEAR" & row == 79 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Race and Hispanic Origin-specific victimization rate:   Unknown race or Hispanic origin
    trim_upcase(table)=="3C" & row == 2 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victimization rate (victimization county population)
    trim_upcase(table)=="3C" & row == 4 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victimization rate (victimization county population)
    trim_upcase(table)=="4B" & row == 1 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Arrest rate (per 100k total population)
    trim_upcase(table)=="4B" & row == 2 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #On-view arrest
    trim_upcase(table)=="4B" & row == 3 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Summoned/cited
    trim_upcase(table)=="4B" & row == 4 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Taken into custody
    trim_upcase(table)=="4B" & row == 5 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGELT5_NUM_WEIGHTED, #Under 5
    trim_upcase(table)=="4B" & row == 6 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE5TO14_NUM_WEIGHTED, #5-14
    trim_upcase(table)=="4B" & row == 7 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE15_NUM_WEIGHTED, #15
    trim_upcase(table)=="4B" & row == 8 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE16_NUM_WEIGHTED, #16
    trim_upcase(table)=="4B" & row == 9 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE17_NUM_WEIGHTED, #17
    trim_upcase(table)=="4B" & row == 10 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE18TO24_NUM_WEIGHTED, #18-24
    trim_upcase(table)=="4B" & row == 11 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE25TO34_NUM_WEIGHTED, #25-34
    trim_upcase(table)=="4B" & row == 12 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE35TO64_NUM_WEIGHTED, #35-64
    trim_upcase(table)=="4B" & row == 13 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGEGTE65_NUM_WEIGHTED, #65+
    trim_upcase(table)=="4B" & row == 14 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Unknown
    trim_upcase(table)=="4B" & row == 15 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTSEXMALE_NUM_WEIGHTED, #Male
    trim_upcase(table)=="4B" & row == 16 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTSEXFEMALE_NUM_WEIGHTED, #Female
    trim_upcase(table)=="4B" & row == 17 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Unknown
    trim_upcase(table)=="4B" & row == 18 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACEWHITE_NUM_WEIGHTED, #White
    trim_upcase(table)=="4B" & row == 19 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACEBLACK_NUM_WEIGHTED, #Black
    trim_upcase(table)=="4B" & row == 20 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACEAIAN_NUM_WEIGHTED, #American Indian or Alaska Native
    trim_upcase(table)=="4B" & row == 21 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACEASIAN_NUM_WEIGHTED, #Asian
    trim_upcase(table)=="4B" & row == 22 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACENHPI_NUM_WEIGHTED, #Native Hawaiian or Other Pacific Islander
    trim_upcase(table)=="4B" & row == 23 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Unknown
    trim_upcase(table)=="4B" & row == 24 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_UNDER_12_NUM_WEIGHTED, #Under 12
    trim_upcase(table)=="4B" & row == 25 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_12_17_NUM_WEIGHTED, #12-17
    trim_upcase(table)=="4B" & row == 26 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_12_14_NUM_WEIGHTED, #12-14
    trim_upcase(table)=="4B" & row == 27 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_15_17_NUM_WEIGHTED, #15-17
    trim_upcase(table)=="4B" & row == 28 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_OVER_18_NUM_WEIGHTED, #18+
    trim_upcase(table)=="4B" & row == 29 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Unknown
    trim_upcase(table)=="4B" & row == 30 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_HISP_NUM_WEIGHTED, #Hispanic Origin-specific arrest rate:   Hispanic or Latino
    trim_upcase(table)=="4B" & row == 31 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_NUM_WEIGHTED, #Hispanic Origin-specific arrest rate:   Not Hispanic or Latino
    trim_upcase(table)=="4B" & row == 32 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Hispanic Origin-specific arrest rate:   Unknown
    trim_upcase(table)=="4B" & row == 33 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_HISP_NUM_WEIGHTED, #Race and Hispanic Origin-specific arrest rate:   Hispanic or Latino
    trim_upcase(table)=="4B" & row == 34 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_WHITE_NUM_WEIGHTED, #Race and Hispanic Origin-specific arrest rate:   Non-Hispanic, White
    trim_upcase(table)=="4B" & row == 35 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_BLACK_NUM_WEIGHTED, #Race and Hispanic Origin-specific arrest rate:   Non-Hispanic, Black
    trim_upcase(table)=="4B" & row == 36 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_AIAN_NUM_WEIGHTED, #Race and Hispanic Origin-specific arrest rate:   Non-Hispanic, American Indian or Alaska Native
    trim_upcase(table)=="4B" & row == 37 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_ASIAN_NUM_WEIGHTED, #Race and Hispanic Origin-specific arrest rate:   Non-Hispanic, Asian
    trim_upcase(table)=="4B" & row == 38 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_NHOPI_NUM_WEIGHTED, #Race and Hispanic Origin-specific arrest rate:   Non-Hispanic, Native Hawaiian or Other Pacific Islander
    trim_upcase(table)=="4B" & row == 39 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Race and Hispanic Origin-specific arrest rate:   Unknown race or Hispanic origin
    trim_upcase(table)=="5B" & row == 1 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Arrest rate (per 100k total population)
    trim_upcase(table)=="5B" & row == 2 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #On-view arrest
    trim_upcase(table)=="5B" & row == 3 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Summoned/cited
    trim_upcase(table)=="5B" & row == 4 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Taken into custody
    trim_upcase(table)=="5B" & row == 5 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGELT5_NUM_WEIGHTED, #Under 5
    trim_upcase(table)=="5B" & row == 6 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE5TO14_NUM_WEIGHTED, #5-14
    trim_upcase(table)=="5B" & row == 7 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE15_NUM_WEIGHTED, #15
    trim_upcase(table)=="5B" & row == 8 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE16_NUM_WEIGHTED, #16
    trim_upcase(table)=="5B" & row == 9 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE17_NUM_WEIGHTED, #17
    trim_upcase(table)=="5B" & row == 10 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE18TO24_NUM_WEIGHTED, #18-24
    trim_upcase(table)=="5B" & row == 11 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE25TO34_NUM_WEIGHTED, #25-34
    trim_upcase(table)=="5B" & row == 12 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE35TO64_NUM_WEIGHTED, #35-64
    trim_upcase(table)=="5B" & row == 13 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGEGTE65_NUM_WEIGHTED, #65+
    trim_upcase(table)=="5B" & row == 14 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Unknown
    trim_upcase(table)=="5B" & row == 15 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTSEXMALE_NUM_WEIGHTED, #Male
    trim_upcase(table)=="5B" & row == 16 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTSEXFEMALE_NUM_WEIGHTED, #Female
    trim_upcase(table)=="5B" & row == 17 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Unknown
    trim_upcase(table)=="5B" & row == 18 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACEWHITE_NUM_WEIGHTED, #White
    trim_upcase(table)=="5B" & row == 19 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACEBLACK_NUM_WEIGHTED, #Black
    trim_upcase(table)=="5B" & row == 20 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACEAIAN_NUM_WEIGHTED, #American Indian or Alaska Native
    trim_upcase(table)=="5B" & row == 21 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACEASIAN_NUM_WEIGHTED, #Asian
    trim_upcase(table)=="5B" & row == 22 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACENHPI_NUM_WEIGHTED, #Native Hawaiian or Other Pacific Islander
    trim_upcase(table)=="5B" & row == 23 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Unknown
    trim_upcase(table)=="5B" & row == 24 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_UNDER_12_NUM_WEIGHTED, #Under 12
    trim_upcase(table)=="5B" & row == 25 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_12_17_NUM_WEIGHTED, #12-17
    trim_upcase(table)=="5B" & row == 26 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_12_14_NUM_WEIGHTED, #12-14
    trim_upcase(table)=="5B" & row == 27 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_15_17_NUM_WEIGHTED, #15-17
    trim_upcase(table)=="5B" & row == 28 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_OVER_18_NUM_WEIGHTED, #18+
    trim_upcase(table)=="5B" & row == 29 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Unknown
    trim_upcase(table)=="5B" & row == 30 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_HISP_NUM_WEIGHTED, #Hispanic Origin-specific arrest rate:   Hispanic or Latino
    trim_upcase(table)=="5B" & row == 31 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_NUM_WEIGHTED, #Hispanic Origin-specific arrest rate:   Not Hispanic or Latino
    trim_upcase(table)=="5B" & row == 32 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Hispanic Origin-specific arrest rate:   Unknown
    trim_upcase(table)=="5B" & row == 33 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_HISP_NUM_WEIGHTED, #Race and Hispanic Origin-specific arrest rate:   Hispanic or Latino
    trim_upcase(table)=="5B" & row == 34 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_WHITE_NUM_WEIGHTED, #Race and Hispanic Origin-specific arrest rate:   Non-Hispanic, White
    trim_upcase(table)=="5B" & row == 35 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_BLACK_NUM_WEIGHTED, #Race and Hispanic Origin-specific arrest rate:   Non-Hispanic, Black
    trim_upcase(table)=="5B" & row == 36 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_AIAN_NUM_WEIGHTED, #Race and Hispanic Origin-specific arrest rate:   Non-Hispanic, American Indian or Alaska Native
    trim_upcase(table)=="5B" & row == 37 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_ASIAN_NUM_WEIGHTED, #Race and Hispanic Origin-specific arrest rate:   Non-Hispanic, Asian
    trim_upcase(table)=="5B" & row == 38 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_NHOPI_NUM_WEIGHTED, #Race and Hispanic Origin-specific arrest rate:   Non-Hispanic, Native Hawaiian or Other Pacific Islander
    trim_upcase(table)=="5B" & row == 39 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Race and Hispanic Origin-specific arrest rate:   Unknown race or Hispanic origin
    trim_upcase(table)=="LEOKA" & row == 2 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_OFFICER_NUM_WEIGHTED, #Victimization rate (per 100k LE staff): Law enforcement officers
    trim_upcase(table)=="GV1A" & row == 2 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Offense rate (per 100k total pop)
    trim_upcase(table)=="GV2A" & row == 2 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Known Victim rate (per 100k total pop)
    trim_upcase(table)=="GV2A" & row == 3 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGELT5_NUM_WEIGHTED, #Under 5
    trim_upcase(table)=="GV2A" & row == 4 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE5TO14_NUM_WEIGHTED, #5-14
    trim_upcase(table)=="GV2A" & row == 5 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_15_17_NUM_WEIGHTED, #15-17
    trim_upcase(table)=="GV2A" & row == 6 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE18TO24_NUM_WEIGHTED, #18-24
    trim_upcase(table)=="GV2A" & row == 7 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE25TO34_NUM_WEIGHTED, #25-34
    trim_upcase(table)=="GV2A" & row == 8 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE35TO64_NUM_WEIGHTED, #35-64
    trim_upcase(table)=="GV2A" & row == 9 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGEGTE65_NUM_WEIGHTED, #65+
    trim_upcase(table)=="GV2A" & row == 10 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Unknown
    trim_upcase(table)=="GV2A" & row == 11 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_UNDER_18_NUM_WEIGHTED, #Under 18
    trim_upcase(table)=="GV2A" & row == 12 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_UNDER_12_NUM_WEIGHTED, #Under 12
    trim_upcase(table)=="GV2A" & row == 13 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_12_17_NUM_WEIGHTED, #12-17
    trim_upcase(table)=="GV2A" & row == 14 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTAGE_OVER_18_NUM_WEIGHTED, #18+
    trim_upcase(table)=="GV2A" & row == 15 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Unknown
    trim_upcase(table)=="GV2A" & row == 16 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Number of Victims: 1
    trim_upcase(table)=="GV2A" & row == 17 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Number of Victims: 2
    trim_upcase(table)=="GV2A" & row == 18 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Number of Victims: 3
    trim_upcase(table)=="GV2A" & row == 19 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Number of Victims: 4+
    trim_upcase(table)=="GV2A" & row == 20 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTSEXMALE_NUM_WEIGHTED, #Male
    trim_upcase(table)=="GV2A" & row == 21 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTSEXFEMALE_NUM_WEIGHTED, #Female
    trim_upcase(table)=="GV2A" & row == 22 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Unknown
    trim_upcase(table)=="GV2A" & row == 23 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACEWHITE_NUM_WEIGHTED, #White
    trim_upcase(table)=="GV2A" & row == 24 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACEBLACK_NUM_WEIGHTED, #Black
    trim_upcase(table)=="GV2A" & row == 25 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACEAIAN_NUM_WEIGHTED, #American Indian or Alaska Native
    trim_upcase(table)=="GV2A" & row == 26 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACEASIAN_NUM_WEIGHTED, #Asian
    trim_upcase(table)=="GV2A" & row == 27 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCTRACENHPI_NUM_WEIGHTED, #Native Hawaiian or Other Pacific Islander
    trim_upcase(table)=="GV2A" & row == 28 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Unknown
    trim_upcase(table)=="GV2A" & row == 29 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Number of Victims Summarized at Incident Level: 1
    trim_upcase(table)=="GV2A" & row == 30 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Number of Victims Summarized at Incident Level: 2
    trim_upcase(table)=="GV2A" & row == 31 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Number of Victims Summarized at Incident Level: 3
    trim_upcase(table)=="GV2A" & row == 32 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Number of Victims Summarized at Incident Level: 4+
    trim_upcase(table)=="GV2A" & row == 33 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Number of Victims Murdered: Yes
    trim_upcase(table)=="GV2A" & row == 34 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Number of Victims Murdered: No
    trim_upcase(table)=="GV2A" & row == 35 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Number of Firearm Victims: 1
    trim_upcase(table)=="GV2A" & row == 36 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Number of Firearm Victims: 2
    trim_upcase(table)=="GV2A" & row == 37 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Number of Firearm Victims: 3
    trim_upcase(table)=="GV2A" & row == 38 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Number of Firearm Victims: 4+
    trim_upcase(table)=="GV2A" & row == 39 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Injury hierarchy : Murder and Non-negligent Manslaughter, Negligent Manslaughter
    trim_upcase(table)=="GV2A" & row == 40 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Injury hierarchy : Major injury (other major injury, severe laceration, possible internal injury)
    trim_upcase(table)=="GV2A" & row == 41 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Injury hierarchy : Unconsciousness, apparent broken bones, loss of teeth
    trim_upcase(table)=="GV2A" & row == 42 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Injury hierarchy : Apparent minor injury
    trim_upcase(table)=="GV2A" & row == 43 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Injury hierarchy : No injury
    trim_upcase(table)=="GV2A" & row == 44 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Injury hierarchy 2: Murder and Non-negligent Manslaughter, Negligent Manslaughter
    trim_upcase(table)=="GV2A" & row == 45 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Injury hierarchy 2: Other major injury
    trim_upcase(table)=="GV2A" & row == 46 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Injury hierarchy 2: Severe laceration, possible internal injury
    trim_upcase(table)=="GV2A" & row == 47 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Injury hierarchy 2: Unconsciousness, apparent broken bones, loss of teeth
    trim_upcase(table)=="GV2A" & row == 48 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Injury hierarchy 2: Apparent minor injury
    trim_upcase(table)=="GV2A" & row == 49 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Injury hierarchy 2: No injury
    trim_upcase(table)=="GV2A" & row == 50 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Intimate partner
    trim_upcase(table)=="GV2A" & row == 51 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Other family
    trim_upcase(table)=="GV2A" & row == 52 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Outside family but known to victim
    trim_upcase(table)=="GV2A" & row == 53 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Stranger
    trim_upcase(table)=="GV2A" & row == 54 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Victim was Offender
    trim_upcase(table)=="GV2A" & row == 55 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Unknown relationship
    trim_upcase(table)=="GV2A" & row == 56 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Unknown Offender Incidents
    trim_upcase(table)=="GV2A" & row == 57 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy: Missing from Uncleared Incidents
    trim_upcase(table)=="GV2A" & row == 58 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy among known offenders: Intimate partner
    trim_upcase(table)=="GV2A" & row == 59 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy among known offenders: Other family
    trim_upcase(table)=="GV2A" & row == 60 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy among known offenders: Outside family but known to victim
    trim_upcase(table)=="GV2A" & row == 61 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy among known offenders: Stranger
    trim_upcase(table)=="GV2A" & row == 62 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy among known offenders: Victim was Offender
    trim_upcase(table)=="GV2A" & row == 63 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim-offender relationship hierarchy among known offenders: Unknown relationship
    trim_upcase(table)=="GV2A" & row == 64 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_HISP_NUM_WEIGHTED, #Victim Hispanic Origin:   Hispanic or Latino
    trim_upcase(table)=="GV2A" & row == 65 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_NUM_WEIGHTED, #Victim Hispanic Origin:   Not Hispanic or Latino
    trim_upcase(table)=="GV2A" & row == 66 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim Hispanic Origin:   Unknown
    trim_upcase(table)=="GV2A" & row == 67 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_HISP_NUM_WEIGHTED, #Victim race and Hispanic Origin:   Hispanic or Latino
    trim_upcase(table)=="GV2A" & row == 68 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_WHITE_NUM_WEIGHTED, #Victim race and Hispanic Origin:   Non-Hispanic, White
    trim_upcase(table)=="GV2A" & row == 69 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_BLACK_NUM_WEIGHTED, #Victim race and Hispanic Origin:   Non-Hispanic, Black
    trim_upcase(table)=="GV2A" & row == 70 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_AIAN_NUM_WEIGHTED, #Victim race and Hispanic Origin:   Non-Hispanic, American Indian or Alaska Native
    trim_upcase(table)=="GV2A" & row == 71 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_ASIAN_NUM_WEIGHTED, #Victim race and Hispanic Origin:   Non-Hispanic, Asian
    trim_upcase(table)=="GV2A" & row == 72 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_DER_POP_PCT_NONHISP_NHOPI_NUM_WEIGHTED, #Victim race and Hispanic Origin:   Non-Hispanic, Native Hawaiian or Other Pacific Islander
    trim_upcase(table)=="GV2A" & row == 73 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED, #Victim race and Hispanic Origin:   Unknown race or Hispanic origin
    trim_upcase(table)=="GV3A" & row == 2 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED #Incident rate (per 100k total pop)
    

  ) )

#Check to see if the numbers are unique(i.e. no wrong coding to fill in the population_estimate table)
raw_test <- raw_5 %>%
  filter(trim_upcase(estimate_type) == "RATE") %>%
  #Filter to PERMUTATION_NUMBER, table, row
  group_by(PERMUTATION_NUMBER, table, row) %>%
  summarise(final_count = n_distinct(floor(population_estimate))) %>%
  ungroup()


#Make sure that the population_estimate are unique
raw_test %>%
  filter(final_count > 1) %>%
  datatable()

#Clear the data
rm(raw_test)
invisible(gc())

#Need to fix the grey cells
raw_6 <- raw_5 %>%
  mutate(

der_cleared_cells_qc = fcase(

########################################Table 1A#######################################
trim_upcase(table)=="1A" & (
column == 5 | #~ 'Murder and Non-negligent Manslaughter',
column == 6 #~ 'Negligent Manslaughter',
) & (
row == 11 |#,  'Injury: No',
row == 12  #,  'Injury: Yes',
),  1,

trim_upcase(table)=="1A" & (
column == 1 | # 'NIBRS crimes against persons (Total)',
column == 2 | # 'Aggravated Assault',
column == 3 | # 'Simple Assault',
column == 4 | # 'Intimidation',
column == 5 | # 'Murder and Non-negligent Manslaughter',
column == 6 | # 'Negligent Manslaughter',
#column == 7 | # 'Kidnapping/Abduction',
column == 8 | # 'Human Trafficking-Sex',
column == 9 | # 'Human Trafficking-Labor',
column == 10 | # 'Rape',
column == 11 | # 'Sodomy',
column == 12 | # 'Sexual Assault with an Object',
column == 13 | # 'Fondling',
column == 14 | # 'Sex Offenses, Nonforcible',
column == 15 | # 'Robbery',
column == 16 | # 'Revised Rape',
column == 17 | # 'Violent Crime',
column == 18   #'Car Jacking',

) & (
row == 72 | # 'Property loss: None',
row == 73 | # 'Property loss: Burned',
row == 74 | # 'Property loss: Counterfeited/forged',
row == 75 | # 'Property loss: Destroyed/damaged/vandalized',
row == 76 | # 'Property loss: Recovered',
row == 77 | # 'Property loss: Seized',
row == 78 | # 'Property loss: Stolen/Et',
row == 79  # 'Property loss: Unknown',

),  1,

########################################Table 1B#######################################

trim_upcase(table)=="1B" & (

column == 1 | # 'NIBRS crimes against property (Total)',
column == 2 | # 'Arson',
column == 3 | # 'Bribery',
column == 4 | # 'Burglary/B&E',
column == 5 | # 'Counterfeiting/Forgery',
column == 6 | # 'Destruction/Damage/Vandalism',
column == 7 | # 'Embezzlement',
#column == 8 | # 'Extortion/Blackmail',
column == 9 | # 'Fraud Offenses',
column == 10 | # 'Larceny/Theft Offenses',
column == 11 | # 'Motor Vehicle Theft',
column == 12 | # 'Robbery',
column == 13 | # 'Stolen Property Offenses',
column == 14 | #'Property Crime',
column == 15   #'Car Jacking',


) & (
row == 3 | # 'Weapon involved: No',
row == 4 | # 'Weapon involved: Yes',
row == 5 | # 'Weapon involved: Personal weapons',
row == 6 | # 'Weapon involved: Firearms',
row == 7 | # 'Weapon involved: Knives and other cutting instruments',
row == 8 | # 'Weapon involved: Blunt instruments',
row == 9 | # 'Weapon involved: Other non-personal weapons',
row == 10  # 'Weapon involved: Unknown',

),  1,

########################################Table 1C#######################################

trim_upcase(table)=="1C" & (

column == 1 | # 'NIBRS crimes against society (Total)',
column == 2 | # 'Animal Cruelty',
#column == 3 | # 'Drug/Narcotic Offenses',
#column == 4 | # 'Gambling Offenses',
column == 5 | # 'Pornography/Obscene Material',
column == 6 | # 'Prostitution Offenses',
column == 7  # 'Weapon Law Violations',



) & (
row == 54 | # 'Property loss: None',
row == 55 | # 'Property loss: Burned',
row == 56 | # 'Property loss: Counterfeited/forged',
row == 57 | # 'Property loss: Destroyed/damaged/vandalized',
row == 58 | # 'Property loss: Recovered',
row == 59 | # 'Property loss: Seized',
row == 60 | # 'Property loss: Stolen/Et',
row == 61  # 'Property loss: Unknown',


),  1,

########################################Table 2A#######################################

trim_upcase(table)=="2A" & (

column == 4 | # 'Intimidation',
column == 14  # 'Sex Offenses, Nonforcible',


) & (
row == 3 | # 'Weapon involved: No',
row == 4 | # 'Weapon involved: Yes',
row == 5 | # 'Weapon involved: Personal weapons',
row == 6 | # 'Weapon involved: Firearms',
row == 7 | # 'Weapon involved: Knives and other cutting instruments',
row == 8 | # 'Weapon involved: Blunt instruments',
row == 9 | # 'Weapon involved: Other non-personal weapons',
row == 10  # 'Weapon involved: Unknown',

),  1,

trim_upcase(table)=="2A" & (

column == 5 | # 'Murder and Non-negligent Manslaughter',
column == 6  # 'Negligent Manslaughter',


) & (
row == 11 | # 'Injury: No',
row == 12  # 'Injury: Yes',
),  1,

########################################Table 2B#######################################

trim_upcase(table)=="2B" & (

column == 1 | # 'NIBRS crimes against property (Total)',
column == 2 | # 'Arson',
column == 3 | # 'Bribery',
column == 4 | # 'Burglary/B&E',
column == 5 | # 'Counterfeiting/Forgery',
column == 6 | # 'Destruction/Damage/Vandalism',
column == 7 | # 'Embezzlement',
#column == 8 | # 'Extortion/Blackmail',
column == 9 | # 'Fraud Offenses',
column == 10 | # 'Larceny/Theft Offenses',
column == 11 | # 'Motor Vehicle Theft',
column == 12 | # 'Robbery',
column == 13 |  # 'Stolen Property Offenses',
column == 14 | #'Property Crime',
column == 15 | #'Car Jacking',
column == 16 | #'Corruption',
column == 17 | #'Other Acts of Corruption',
column == 18  #'Hacking/Computer Invasion',


) & (
row == 3 | # 'Weapon involved: No',
row == 4 | # 'Weapon involved: Yes',
row == 5 | # 'Weapon involved: Personal weapons',
row == 6 | # 'Weapon involved: Firearms',
row == 7 | # 'Weapon involved: Knives and other cutting instruments',
row == 8 | # 'Weapon involved: Blunt instruments',
row == 9 | # 'Weapon involved: Other non-personal weapons',
row == 10  # 'Weapon involved: Unknown',


),  1,

trim_upcase(table)=="2B" & (

column == 1 | # 'NIBRS crimes against property (Total)',
column == 2 | # 'Arson',
column == 3 | # 'Bribery',
column == 4 | # 'Burglary/B&E',
#column == 5 | # 'Counterfeiting/Forgery',
column == 6 | # 'Destruction/Damage/Vandalism',
column == 7 | # 'Embezzlement',
column == 8 | # 'Extortion/Blackmail',
column == 9 | # 'Fraud Offenses',
column == 10 | # 'Larceny/Theft Offenses',
column == 11 | # 'Motor Vehicle Theft',
column == 12 | # 'Robbery',
#column == 13 | # 'Stolen Property Offenses',
column == 14 | #'Property Crime',
column == 15 | #'Car Jacking',
column == 16 | #'Corruption',
column == 17 | #'Other Acts of Corruption',
column == 18  #'Hacking/Computer Invasion',

) & (
row == 55 | # 'Gang Involvement: None/Unknown gang involvement',
row == 56  # 'Gang Involvement: Juvenile or other gang',

),  1,

########################################Table 2C#######################################

trim_upcase(table)=="2C" & (

column == 1 | # 'NIBRS crimes against society (Total)',
column == 6  # 'Prostitution Offenses',


) & (
row == 42 | # 'Gang Involvement: None/Unknown gang involvement',
row == 43  # 'Gang Involvement: Juvenile or other gang',



),  1,

########################################Table 3A#######################################

trim_upcase(table) %in% c("3A", "3AUNCLEAR", "3ACLEAR") & (
column == 5 | # 'Murder and Non-negligent Manslaughter',
column == 6  # 'Negligent Manslaughter',

) & (
row == 74 | # 'Injury: No',
row == 75  # 'Injury: Yes',
),  1,

trim_upcase(table) %in% c("3A", "3AUNCLEAR", "3ACLEAR") & (
column == 1 | # 'NIBRS crimes against persons (Total)',
column == 2 | # 'Aggravated Assault',
column == 3 | # 'Simple Assault',
column == 4 | # 'Intimidation',
#column == 5 | # 'Murder and Non-negligent Manslaughter',
#column == 6 | # 'Negligent Manslaughter',
column == 7 | # 'Kidnapping/Abduction',
column == 8 | # 'Human Trafficking-Sex',
column == 9 | # 'Human Trafficking-Labor',
column == 10 | # 'Rape',
column == 11 | # 'Sodomy',
column == 12 | # 'Sexual Assault with an Object',
column == 13 | # 'Fondling',
column == 14 | # 'Sex Offenses, Nonforcible',
column == 15 | # 'Revised Rape',
column == 16 |  # 'Violent Crime',
column == 17 | #'Robbery',
column == 18 | #'NIBRS crimes against property (Total)',
column == 19 | #'Arson',
column == 20 | #'Bribery',
column == 21 | #'Burglary/B&E',
#column == 22 | #'Counterfeiting/Forgery',
column == 23 | #'Destruction/Damage/Vandalism',
column == 24 | #'Embezzlement',
column == 25 | #'Extortion/Blackmail',
column == 26 | #'Fraud Offenses',
column == 27 | #'Larceny/Theft Offenses',
column == 28 | #'Motor Vehicle Theft',
#column == 29 | #'Stolen Property Offenses',
column == 30 | #'Property Crime',
column == 31  #'Car Jacking',
  


) & (
row == 82 | # 'Gang involvement: No',
row == 83  # 'Gang involvement: Yes',

),  1,

########################################Table 3A Demographics Disaggregation#######################################
#Age Permutation 1000	Age	 Under 5 to
#                9000	Age	 65+
#                17000 Age Age:18+
#                18000 Age Under 18
#                19000 Age Under 15

der_demographic_main_number %in% c(
  CONST_ALL_AGE
) &

trim_upcase(table) %in% c("3A", "3AUNCLEAR", "3ACLEAR")  & (
row == 5| #Victim Age:  Under 5
row == 6| #Victim Age:  5-14
row == 7| #Victim Age:15
row == 8| #Victim Age:16
row == 9| #Victim Age:17
row == 10| #Victim Age:  18-24
row == 11| #Victim Age:  25-34
row == 12| #Victim Age:  35-64
row == 13| #Victim Age:  65+
row == 14| #Victim Age:  Unknown
row == 84| #Victim Age 2:  Under 12
row == 85| #Victim Age 2:  12-17
row == 86| #Victim Age 2:  12-14
row == 87| #Victim Age 2:  15-17
row == 88| #Victim Age 2:18+
row == 89 #Victim Age 2:  Unknown
  
), 1,

#Gender Permutation 10000	Sex	 Male
#                   11000	Sex	 Female

der_demographic_main_number %in% c(
  CONST_ALL_SEX
) &
trim_upcase(table) %in% c("3A", "3AUNCLEAR", "3ACLEAR") & 
(
row == 15| #Victim sex:  Male
row == 16| #Victim sex:  Female
row == 17 #Victim sex:  Unknown
), 1,

#Race Permutation 12000	Race	 White
#                 16000	Race	 Native Hawaiian or Other Pacific Islander
#                 20000	Race	 American Indian or Alaska Native, Asian, and Native Hawaiian or Other

der_demographic_main_number %in% c(
  CONST_ALL_RACE
) &

trim_upcase(table) %in% c("3A", "3AUNCLEAR", "3ACLEAR") & (
row == 18| #Victim race:  White
row == 19| #Victim race:  Black
row == 20| #Victim race:  American Indian or Alaska Native
row == 21| #Victim race:  Asian
row == 22| #Victim race:  Native Hawaiian or Other Pacific Islander
row == 23 | #Victim race:  Unknown
row == 162 | #Victim Hispanic Origin:   Hispanic or Latino
row == 163 | #Victim Hispanic Origin:   Not Hispanic or Latino
row == 164 | #Victim Hispanic Origin:   Unknown
row == 165 | #Victim race and Hispanic Origin:   Hispanic or Latino
row == 166 | #Victim race and Hispanic Origin:   Non-Hispanic, White
row == 167 | #Victim race and Hispanic Origin:   Non-Hispanic, Black
row == 168 | #Victim race and Hispanic Origin:   Non-Hispanic, American Indian or Alaska Native
row == 169 | #Victim race and Hispanic Origin:   Non-Hispanic, Asian
row == 170 | #Victim race and Hispanic Origin:   Non-Hispanic, Native Hawaiian or Other Pacific Islander
row == 171  #Victim race and Hispanic Origin:   Unknown race or Hispanic origin
  

  ), 1,


########################################Table 3B Demographics Disaggregation#######################################
#Age Permutation 1000	Age	 Under 5 to
#                9000	Age	 65+
#                17000 Age Age:18+
#                18000 Age Under 18
#                19000 Age Under 15

der_demographic_main_number %in% c(
  CONST_ALL_AGE
) &
trim_upcase(table) %in% c("3B", "3BUNCLEAR", "3BCLEAR")  & (
row == 5| #Age-specific victimization rate:  Under 5
row == 6| #Age-specific victimization rate:  5-14
row == 7| #Age-specific victimization rate:15
row == 8| #Age-specific victimization rate:16
row == 9| #Age-specific victimization rate:17
row == 10| #Age-specific victimization rate:  18-24
row == 11| #Age-specific victimization rate:  25-34
row == 12| #Age-specific victimization rate:  35-64
row == 13| #Age-specific victimization rate:  65+
row == 14| #Age-specific victimization rate:  Unknown
row == 24| #Victim Age 2:  Under 12
row == 25| #Victim Age 2:  12-17
row == 26| #Victim Age 2:  12-14
row == 27| #Victim Age 2:  15-17
row == 28| #Victim Age 2:18+
row == 29 #Victim Age 2:  Unknown
  
), 1,

#Gender Permutation 10000	Sex	 Male
#                   11000	Sex	 Female


der_demographic_main_number %in% c(
  CONST_ALL_SEX
) &
  trim_upcase(table) %in% c("3B", "3BUNCLEAR", "3BCLEAR") & (
      row == 15| #Sex-specific victimization rate:  Male
      row == 16| #Sex-specific victimization rate:  Female
      row == 17 #Sex-specific victimization rate:  Unknown

  ), 1,

#Race Permutation 12000	Race	 White
#                 16000	Race	 Native Hawaiian or Other Pacific Islander
#                 20000	Race	 American Indian or Alaska Native, Asian, and Native Hawaiian or Other

der_demographic_main_number %in% c(
  CONST_ALL_RACE
) &
  trim_upcase(table) %in% c("3B", "3BUNCLEAR", "3BCLEAR") & (
    row == 18| #Race-specific victimization rate:  White
      row == 19| #Race-specific victimization rate:  Black
      row == 20| #Race-specific victimization rate:  American Indian or Alaska Native
      row == 21| #Race-specific victimization rate:  Asian
      row == 22| #Race-specific victimization rate:  Native Hawaiian or Other Pacific Islander
      row == 23| #Race-specific victimization rate:  Unknown
      row == 70 | #Hispanic Origin-specific victimization rate:   Hispanic or Latino
      row == 71 | #Hispanic Origin-specific victimization rate:   Not Hispanic or Latino
      row == 72 | #Hispanic Origin-specific victimization rate:   Unknown
      row == 73 | #Race and Hispanic Origin-specific victimization rate:   Hispanic or Latino
      row == 74 | #Race and Hispanic Origin-specific victimization rate:   Non-Hispanic, White
      row == 75 | #Race and Hispanic Origin-specific victimization rate:   Non-Hispanic, Black
      row == 76 | #Race and Hispanic Origin-specific victimization rate:   Non-Hispanic, American Indian or Alaska Native
      row == 77 | #Race and Hispanic Origin-specific victimization rate:   Non-Hispanic, Asian
      row == 78 | #Race and Hispanic Origin-specific victimization rate:   Non-Hispanic, Native Hawaiian or Other Pacific Islander
      row == 79  #Race and Hispanic Origin-specific victimization rate:   Unknown race or Hispanic origin
  ), 1,

########################################Table 4A Demographics Disaggregation#######################################
#Age Permutation 1000	Age	 Under 5 to
#                9000	Age	 65+
#                17000 Age Age:18+
#                18000 Age Under 18
#                19000 Age Under 15

der_demographic_main_number %in% c(
  CONST_ALL_AGE
) &

  trim_upcase(table)=="4A" & (
    row == 5| #Arrestee age:  Under 5
      row == 6| #Arrestee age:  5-14
      row == 7| #Arrestee age:15
      row == 8| #Arrestee age:16
      row == 9| #Arrestee age:17
      row == 10| #Arrestee age:  18-24
      row == 11| #Arrestee age:  25-34
      row == 12| #Arrestee age:  35-64
      row == 13| #Arrestee age:  65+
      row == 14| #Arrestee age:  Unknown
      row == 65| #Arrestee age 2:  Under 12
      row == 66| #Arrestee age 2:  12-17
      row == 67| #Arrestee age 2:  12-14
      row == 68| #Arrestee age 2:  15-17
      row == 69| #Arrestee age 2:18+
      row == 70 #Arrestee age 2:  Unknown

  ), 1,

#Gender Permutation 10000	Sex	 Male
#                   11000	Sex	 Female


der_demographic_main_number %in% c(
  CONST_ALL_SEX
) &

  trim_upcase(table)=="4A" & (
    row == 15| #Arrestee sex:  Male
      row == 16| #Arrestee sex:  Female
      row == 17 #Arrestee sex:  Unknown


  ), 1,

#Race Permutation 12000	Race	 White
#                 16000	Race	 Native Hawaiian or Other Pacific Islander
#                 20000	Race	 American Indian or Alaska Native, Asian, and Native Hawaiian or Other

der_demographic_main_number %in% c(
  CONST_ALL_RACE
) &

  trim_upcase(table)=="4A" & (
    row == 18| #Arrestee race:  White
      row == 19| #Arrestee race:  Black
      row == 20| #Arrestee race:  American Indian or Alaska Native
      row == 21| #Arrestee race:  Asian
      row == 22| #Arrestee race:  Native Hawaiian or Other Pacific Islander
      row == 23| #Arrestee race:  Unknown
      row == 71 | #Arrestee Hispanic Origin:   Hispanic or Latino
      row == 72 | #Arrestee Hispanic Origin:   Not Hispanic or Latino
      row == 73 | #Arrestee Hispanic Origin:   Unknown
      row == 74 | #Arrestee race and Hispanic Origin:   Hispanic or Latino
      row == 75 | #Arrestee race and Hispanic Origin:   Non-Hispanic, White
      row == 76 | #Arrestee race and Hispanic Origin:   Non-Hispanic, Black
      row == 77 | #Arrestee race and Hispanic Origin:   Non-Hispanic, American Indian or Alaska Native
      row == 78 | #Arrestee race and Hispanic Origin:   Non-Hispanic, Asian
      row == 79 | #Arrestee race and Hispanic Origin:   Non-Hispanic, Native Hawaiian or Other Pacific Islander
      row == 80  #Arrestee race and Hispanic Origin:   Unknown race or Hispanic origin
  ), 1,

########################################Table 4B Demographics Disaggregation#######################################
#Age Permutation 1000	Age	 Under 5 to
#                9000	Age	 65+
#                17000 Age Age:18+
#                18000 Age Under 18
#                19000 Age Under 15

der_demographic_main_number %in% c(
  CONST_ALL_AGE
) &

  trim_upcase(table)=="4B" & (

    row == 5| #Age-specific arrest rate:  Under 5
      row == 6| #Age-specific arrest rate:  5-14
      row == 7| #Age-specific arrest rate:15
      row == 8| #Age-specific arrest rate:16
      row == 9| #Age-specific arrest rate:17
      row == 10| #Age-specific arrest rate:  18-24
      row == 11| #Age-specific arrest rate:  25-34
      row == 12| #Age-specific arrest rate:  35-64
      row == 13| #Age-specific arrest rate:  65+
      row == 14| #Age-specific arrest rate:  Unknown
      row == 24| #Age-specific arrest rate 2:  Under 12
      row == 25| #Age-specific arrest rate 2:  12-17
      row == 26| #Age-specific arrest rate 2:  12-14
      row == 27| #Age-specific arrest rate 2:  15-17
      row == 28| #Age-specific arrest rate 2:18+
      row == 29 #Age-specific arrest rate 2:  Unknown
    
  ), 1,

#Gender Permutation 10000	Sex	 Male
#                   11000	Sex	 Female


der_demographic_main_number %in% c(
  CONST_ALL_SEX
) &

  trim_upcase(table)=="4B" & (

    row == 15| #Sex-specific arrest rate:  Male
      row == 16| #Sex-specific arrest rate:  Female
      row == 17 #Sex-specific arrest rate:  Unknown

  ), 1,

#Race Permutation 12000	Race	 White
#                 16000	Race	 Native Hawaiian or Other Pacific Islander
#                 20000	Race	 American Indian or Alaska Native, Asian, and Native Hawaiian or Other

der_demographic_main_number %in% c(
  CONST_ALL_RACE
) &

  trim_upcase(table)=="4B" & (

    row == 18| #Race-specific arrest rate:  White
      row == 19| #Race-specific arrest rate:  Black
      row == 20| #Race-specific arrest rate:  American Indian or Alaska Native
      row == 21| #Race-specific arrest rate:  Asian
      row == 22| #Race-specific arrest rate:  Native Hawaiian or Other Pacific Islander
      row == 23| #Race-specific arrest rate:  Unknown
      row == 30 | #Hispanic Origin-specific arrest rate:   Hispanic or Latino
      row == 31 | #Hispanic Origin-specific arrest rate:   Not Hispanic or Latino
      row == 32 | #Hispanic Origin-specific arrest rate:   Unknown
      row == 33 | #Race and Hispanic Origin-specific arrest rate:   Hispanic or Latino
      row == 34 | #Race and Hispanic Origin-specific arrest rate:   Non-Hispanic, White
      row == 35 | #Race and Hispanic Origin-specific arrest rate:   Non-Hispanic, Black
      row == 36 | #Race and Hispanic Origin-specific arrest rate:   Non-Hispanic, American Indian or Alaska Native
      row == 37 | #Race and Hispanic Origin-specific arrest rate:   Non-Hispanic, Asian
      row == 38 | #Race and Hispanic Origin-specific arrest rate:   Non-Hispanic, Native Hawaiian or Other Pacific Islander
      row == 39 #Race and Hispanic Origin-specific arrest rate:   Unknown race or Hispanic origin
  ), 1,


########################################Table 5A Demographics Disaggregation#######################################
#Age Permutation 1000	Age	 Under 5 to
#                9000	Age	 65+
#                17000 Age Age:18+
#                18000 Age Under 18
#                19000 Age Under 15

der_demographic_main_number %in% c(
  CONST_ALL_AGE
) &

 trim_upcase(table)=="5A" & (
    row == 5| #Arrestee age:  Under 5
      row == 6| #Arrestee age:  5-14
      row == 7| #Arrestee age:15
      row == 8| #Arrestee age:16
      row == 9| #Arrestee age:17
      row == 10| #Arrestee age:  18-24
      row == 11| #Arrestee age:  25-34
      row == 12| #Arrestee age:  35-64
      row == 13| #Arrestee age:  65+
      row == 14| #Arrestee age:  Unknown
      row == 65| #Arrestee age 2:  Under 12
      row == 66| #Arrestee age 2:  12-17
      row == 67| #Arrestee age 2:  12-14
      row == 68| #Arrestee age 2:  15-17
      row == 69| #Arrestee age 2:18+
      row == 70 #Arrestee age 2:  Unknown
  
  ) , 1,

#Gender Permutation 10000	Sex	 Male
#                   11000	Sex	 Female

der_demographic_main_number %in% c(
  CONST_ALL_SEX
) &

trim_upcase(table)=="5A" & (
   
    row == 15| #Arrestee sex:  Male
      row == 16| #Arrestee sex:  Female
      row == 17 #Arrestee sex:  Unknown


  ) , 1,


#Race Permutation 12000	Race	 White
#                 16000	Race	 Native Hawaiian or Other Pacific Islander
#                 20000	Race	 American Indian or Alaska Native, Asian, and Native Hawaiian or Other

der_demographic_main_number %in% c(
  CONST_ALL_RACE
) &

  trim_upcase(table)=="5A" & (
   
    row == 18| #Arrestee race:  White
      row == 19| #Arrestee race:  Black
      row == 20| #Arrestee race:  American Indian or Alaska Native
      row == 21| #Arrestee race:  Asian
      row == 22| #Arrestee race:  Native Hawaiian or Other Pacific Islander
      row == 23| #Arrestee race:  Unknown
      row == 71 | #Arrestee Hispanic Origin:   Hispanic or Latino
      row == 72 | #Arrestee Hispanic Origin:   Not Hispanic or Latino
      row == 73 | #Arrestee Hispanic Origin:   Unknown
      row == 74 | #Arrestee race and Hispanic Origin:   Hispanic or Latino
      row == 75 | #Arrestee race and Hispanic Origin:   Non-Hispanic, White
      row == 76 | #Arrestee race and Hispanic Origin:   Non-Hispanic, Black
      row == 77 | #Arrestee race and Hispanic Origin:   Non-Hispanic, American Indian or Alaska Native
      row == 78 | #Arrestee race and Hispanic Origin:   Non-Hispanic, Asian
      row == 79 | #Arrestee race and Hispanic Origin:   Non-Hispanic, Native Hawaiian or Other Pacific Islander
      row == 80  #Arrestee race and Hispanic Origin:   Unknown race or Hispanic origin
      
      
      

  ), 1,


########################################Table 5B Demographics Disaggregation#######################################
#Age Permutation 1000	Age	 Under 5 to
#                9000	Age	 65+
#                17000 Age Age:18+
#                18000 Age Under 18
#                19000 Age Under 15

der_demographic_main_number %in% c(
  CONST_ALL_AGE
) &

trim_upcase(table)=="5B" & (
   
    row == 5| #Age-specific arrest rate:  Under 5
      row == 6| #Age-specific arrest rate:  5-14
      row == 7| #Age-specific arrest rate:15
      row == 8| #Age-specific arrest rate:16
      row == 9| #Age-specific arrest rate:17
      row == 10| #Age-specific arrest rate:  18-24
      row == 11| #Age-specific arrest rate:  25-34
      row == 12| #Age-specific arrest rate:  35-64
      row == 13| #Age-specific arrest rate:  65+
      row == 14| #Age-specific arrest rate:  Unknown
      row == 24| #Age-specific arrest rate 2:  Under 12
      row == 25| #Age-specific arrest rate 2:  12-17
      row == 26| #Age-specific arrest rate 2:  12-14
      row == 27| #Age-specific arrest rate 2:  15-17
      row == 28| #Age-specific arrest rate 2:18+
      row == 29 #Age-specific arrest rate 2:  Unknown
      




  ) , 1,

#Gender Permutation 10000	Sex	 Male
#                   11000	Sex	 Female


der_demographic_main_number %in% c(
  CONST_ALL_SEX
) &

  trim_upcase(table)=="5B" & (
    row == 15| #Sex-specific arrest rate:  Male
      row == 16| #Sex-specific arrest rate:  Female
      row == 17 #Sex-specific arrest rate:  Unknown

  ) , 1,

#Race Permutation 12000	Race	 White
#                 16000	Race	 Native Hawaiian or Other Pacific Islander
#                 20000	Race	 American Indian or Alaska Native, Asian, and Native Hawaiian or Other

der_demographic_main_number %in% c(
  CONST_ALL_RACE
) &

trim_upcase(table)=="5B" & (

    row == 18| #Race-specific arrest rate:  White
      row == 19| #Race-specific arrest rate:  Black
      row == 20| #Race-specific arrest rate:  American Indian or Alaska Native
      row == 21| #Race-specific arrest rate:  Asian
      row == 22| #Race-specific arrest rate:  Native Hawaiian or Other Pacific Islander
      row == 23| #Race-specific arrest rate:  Unknown
      row == 30 | #Hispanic Origin-specific arrest rate:   Hispanic or Latino
      row == 31 | #Hispanic Origin-specific arrest rate:   Not Hispanic or Latino
      row == 32 | #Hispanic Origin-specific arrest rate:   Unknown
      row == 33 | #Race and Hispanic Origin-specific arrest rate:   Hispanic or Latino
      row == 34 | #Race and Hispanic Origin-specific arrest rate:   Non-Hispanic, White
      row == 35 | #Race and Hispanic Origin-specific arrest rate:   Non-Hispanic, Black
      row == 36 | #Race and Hispanic Origin-specific arrest rate:   Non-Hispanic, American Indian or Alaska Native
      row == 37 | #Race and Hispanic Origin-specific arrest rate:   Non-Hispanic, Asian
      row == 38 | #Race and Hispanic Origin-specific arrest rate:   Non-Hispanic, Native Hawaiian or Other Pacific Islander
      row == 39  #Race and Hispanic Origin-specific arrest rate:   Unknown race or Hispanic origin
  ), 1,

########################################Table DM7 Demographics Disaggregation#######################################
#Age Permutation 1000	Age	 Under 5 to
#                9000	Age	 65+
#                17000 Age Age:18+
#                18000 Age Under 18
#                19000 Age Under 15

der_demographic_main_number %in% c(
  CONST_ALL_AGE
) &

  trim_upcase(table)=="DM7" & (


    row == 3 | #  'Arrestee age: Under 5',
      row == 4 | #  'Arrestee age: 5-14',
      row == 5 | #  'Arrestee age: 15-17',
      row == 6 | #  'Arrestee age: 18-24',
      row == 7 | #  'Arrestee age: 25-34',
      row == 8 | #  'Arrestee age: 35-64',
      row == 9 | #  'Arrestee age: 65+',
      row == 10| #Arrestee age:  Unknown
      row == 50| #Arrestee age 2:  Under 12
      row == 51| #Arrestee age 2:  12-17
      row == 52| #Arrestee age 2:  12-14
      row == 53| #Arrestee age 2:  15-17
      row == 54| #Arrestee age 2:18+
      row == 55 #Arrestee age 2:  Unknown
      

  ), 1,


#Gender Permutation 10000	Sex	 Male
#                   11000	Sex	 Female

der_demographic_main_number %in% c(
  CONST_ALL_SEX
) &

  trim_upcase(table)=="DM7" & (

    row == 11 | #  'Arrestee sex: Male',
      row == 12   #  'Arrestee sex: Female',


  ), 1,


#Race Permutation 12000	Race	 White
#                 16000	Race	 Native Hawaiian or Other Pacific Islander
#                 20000	Race	 American Indian or Alaska Native, Asian, and Native Hawaiian or Other

der_demographic_main_number %in% c(
  CONST_ALL_RACE
) &

  trim_upcase(table)=="DM7" & (
    
    row == 13 | #  'Arrestee race: White',
      row == 14 | #  'Arrestee race: Black',
      row == 15 | #  'Arrestee race: American Indian or Alaska Native',
      row == 16 | #  'Arrestee race: Asian',
      row == 17 | #  'Arrestee race: Native Hawaiian or Other Pacific Islander',
      row == 18 |  # 'Arrestee race: Unknown',
      row == 56 | #Arrestee Hispanic Origin:   Hispanic or Latino
      row == 57 | #Arrestee Hispanic Origin:   Not Hispanic or Latino
      row == 58 | #Arrestee Hispanic Origin:   Unknown
      row == 59 | #Arrestee race and Hispanic Origin:   Hispanic or Latino
      row == 60 | #Arrestee race and Hispanic Origin:   Non-Hispanic, White
      row == 61 | #Arrestee race and Hispanic Origin:   Non-Hispanic, Black
      row == 62 | #Arrestee race and Hispanic Origin:   Non-Hispanic, American Indian or Alaska Native
      row == 63 | #Arrestee race and Hispanic Origin:   Non-Hispanic, Asian
      row == 64 | #Arrestee race and Hispanic Origin:   Non-Hispanic, Native Hawaiian or Other Pacific Islander
      row == 65  #Arrestee race and Hispanic Origin:   Unknown race or Hispanic origin
      

  ), 1,

########################################Table DM9 Demographics Disaggregation#######################################
#Age Permutation 1000	Age	 Under 5 to
#                9000	Age	 65+
#                17000 Age Age:18+
#                18000 Age Under 18
#                19000 Age Under 15

der_demographic_main_number %in% c(
  CONST_ALL_AGE
) &

  trim_upcase(table)=="DM9" & (

    row == 3 | #  'Arrestee age: Under 5',
      row == 4 | #  'Arrestee age: 5-14',
      row == 5 | #  'Arrestee age: 15-17',
      row == 6 | #  'Arrestee age: 18-24',
      row == 7 | #  'Arrestee age: 25-34',
      row == 8 | #  'Arrestee age: 35-64',
      row == 9 | #  'Arrestee age: 65+',
      row == 10| #Arrestee age:  Unknown
      row == 50| #Arrestee age 2:  Under 12
      row == 51| #Arrestee age 2:  12-17
      row == 52| #Arrestee age 2:  12-14
      row == 53| #Arrestee age 2:  15-17
      row == 54| #Arrestee age 2:18+
      row == 55 #Arrestee age 2:  Unknown
      

  ), 1,


#Gender Permutation 10000	Sex	 Male
#                   11000	Sex	 Female


der_demographic_main_number %in% c(
  CONST_ALL_SEX
) &

  trim_upcase(table)=="DM9" & (

   
    row == 11 | #  'Arrestee sex: Male',
      row == 12   #  'Arrestee sex: Female',


  ), 1,

#Race Permutation 12000	Race	 White
#                 16000	Race	 Native Hawaiian or Other Pacific Islander
#                 20000	Race	 American Indian or Alaska Native, Asian, and Native Hawaiian or Other

der_demographic_main_number %in% c(
  CONST_ALL_RACE
) &

  trim_upcase(table)=="DM9" & (

    row == 13 | #  'Arrestee race: White',
      row == 14 | #  'Arrestee race: Black',
      row == 15 | #  'Arrestee race: American Indian or Alaska Native',
      row == 16 | #  'Arrestee race: Asian',
      row == 17 | #  'Arrestee race: Native Hawaiian or Other Pacific Islander',
      row == 18 | # 'Arrestee race: Unknown',
      row == 56 | #Arrestee Hispanic Origin:   Hispanic or Latino
      row == 57 | #Arrestee Hispanic Origin:   Not Hispanic or Latino
      row == 58 | #Arrestee Hispanic Origin:   Unknown
      row == 59 | #Arrestee race and Hispanic Origin:   Hispanic or Latino
      row == 60 | #Arrestee race and Hispanic Origin:   Non-Hispanic, White
      row == 61 | #Arrestee race and Hispanic Origin:   Non-Hispanic, Black
      row == 62 | #Arrestee race and Hispanic Origin:   Non-Hispanic, American Indian or Alaska Native
      row == 63 | #Arrestee race and Hispanic Origin:   Non-Hispanic, Asian
      row == 64 | #Arrestee race and Hispanic Origin:   Non-Hispanic, Native Hawaiian or Other Pacific Islander
      row == 65  #Arrestee race and Hispanic Origin:   Unknown race or Hispanic origin

), 1,


########################################Table DM10 Demographics Disaggregation#######################################


#Gender Permutation 10000	Sex	 Male
#                   11000	Sex	 Female


der_demographic_main_number %in% c(
  CONST_ALL_SEX
) &
  
  trim_upcase(table)=="DM10" & (
    
    row == 2| #Arrestee sex:  Male
    row == 3 #Arrestee sex:  Female
      
    
    
  ), 1,


########################################Table GV2a Demographics Disaggregation#######################################
#Age Permutation 1000	Age	 Under 5 to
#                9000	Age	 65+
#                17000 Age Age:18+
#                18000 Age Under 18
#                19000 Age Under 15

der_demographic_main_number %in% c(
  CONST_ALL_AGE
) &
  
  trim_upcase(table)=="GV2A" & (
    
    row == 3| #Victim Age:   Under 5
      row == 4| #Victim Age:   5-14
      row == 5| #Victim Age:15-17
      row == 6| #Victim Age:   18-24
      row == 7| #Victim Age:   25-34
      row == 8| #Victim Age:   35-64
      row == 9| #Victim Age:   65+
      row == 10| #Victim Age:   Unknown
      row == 11| #Victim age 2:  Under 18
      row == 12| #Victim age 2:    Under 12
      row == 13| #Victim age 2:    12-17
      row == 14| #Victim age 2:  18+
      row == 15 #Victim age 2:  Unknown
      
    
    
  ), 1,


#Gender Permutation 10000	Sex	 Male
#                   11000	Sex	 Female


der_demographic_main_number %in% c(
  CONST_ALL_SEX
) &
  
  trim_upcase(table)=="GV2A" & (
    
    
    row == 20| #Victim sex:  Male
      row == 21| #Victim sex:  Female
      row == 22 #Victim sex:  Unknown
      
    
    
  ), 1,

#Race Permutation 12000	Race	 White
#                 16000	Race	 Native Hawaiian or Other Pacific Islander
#                 20000	Race	 American Indian or Alaska Native, Asian, and Native Hawaiian or Other

der_demographic_main_number %in% c(
  CONST_ALL_RACE
) &
  
  trim_upcase(table)=="GV2A" & (
    
    row == 23| #Victim race:  White
      row == 24| #Victim race:  Black
      row == 25| #Victim race:  American Indian or Alaska Native
      row == 26| #Victim race:  Asian
      row == 27| #Victim race:  Native Hawaiian or Other Pacific Islander
      row == 28| #Victim race:  Unknown
      row == 64 | #Victim Hispanic Origin:   Hispanic or Latino
      row == 65 | #Victim Hispanic Origin:   Not Hispanic or Latino
      row == 66 | #Victim Hispanic Origin:   Unknown
      row == 67 | #Victim race and Hispanic Origin:   Hispanic or Latino
      row == 68 | #Victim race and Hispanic Origin:   Non-Hispanic, White
      row == 69 | #Victim race and Hispanic Origin:   Non-Hispanic, Black
      row == 70 | #Victim race and Hispanic Origin:   Non-Hispanic, American Indian or Alaska Native
      row == 71 | #Victim race and Hispanic Origin:   Non-Hispanic, Asian
      row == 72 | #Victim race and Hispanic Origin:   Non-Hispanic, Native Hawaiian or Other Pacific Islander
      row == 73  #Victim race and Hispanic Origin:   Unknown race or Hispanic origin

  ), 1,


########################################University Permutation#######################################
#University Permutation ends in 107
#Need to NA all age permutation for all estimates

der_geographic_main_number == 107 & 
  der_demographic_main_number %in% c(
    CONST_ALL_AGE
  ) &
  trim_upcase(table) %in% c(CONST_DEMOGRAPHIC_UPCASE_TABLES), 1,

########################################Tribal Permutation#######################################
#Tribal Permutation ends in 108
#Need to NA all age, gender, and race permutations for all estimates


der_geographic_main_number == 108 & 
  der_demographic_main_number %in% c(
    CONST_ALL_AGE,
    CONST_ALL_SEX,
    CONST_ALL_RACE
  ) &
  trim_upcase(table) %in% c(CONST_DEMOGRAPHIC_UPCASE_TABLES), 1,


  ######################################################NA Unknown Demographic Rows#######################################################

  trim_upcase(table) %in% c("3A", "3AUNCLEAR", "3ACLEAR")  & (
  row == 14 | #Victim Age: Unknown
  row == 17 | #Victim sex: Unknown
  row == 23 | #Victim race: Unknown
  row == 51 | #Victim sex and race Male: Unknown
  row == 58 | #Victim sex and race Female: Unknown
  row == 59 | #Victim sex and race: Unknown
  row == 60 | #Victim sex and race Unknown: White
  row == 61 | #Victim sex and race Unknown: Black
  row == 62 | #Victim sex and race Unknown: American Indian or Alaska Native
  row == 63 | #Victim sex and race Unknown: Asian
  row == 64 | #Victim sex and race Unknown: Native Hawaiian or Other Pacific Islander
  row == 65 |  #Victim sex and race Unknown: Unknown
  row == 89 |#'Victim Age 2: Unknown',
  row == 164 | #Victim Hispanic Origin:   Unknown
  row == 171  #Victim race and Hispanic Origin:   Unknown race or Hispanic origin
    
  
  ), 1,
  
trim_upcase(table) %in% c("3B", "3BUNCLEAR", "3BCLEAR") & (
  row == 14 | #Age-specific victimization rate: Unknown
  row == 17 | #Sex-specific victimization rate: Unknown
  row == 23 | #Race-specific victimization rate: Unknown
  row == 29 |  #'Victim Age 2: Unknown',
  row == 72 | #Hispanic Origin-specific victimization rate:   Unknown
  row == 79  #Race and Hispanic Origin-specific victimization rate:   Unknown race or Hispanic origin
  

  ), 1,

  trim_upcase(table)=="4A" & (
  row == 14 | #Arrestee age: Unknown
  row == 17 | #Arrestee sex: Unknown
  row == 23 | #Arrestee race: Unknown
  row == 30 | #Arrestee sex and race Male: Unknown
  row == 37 | #Arrestee sex and race Female: Unknown
  row == 38 | #Arrestee sex and race: Unknown
  row == 39 | #Arrestee sex and race Unknown: White
  row == 40 | #Arrestee sex and race Unknown: Black
  row == 41 | #Arrestee sex and race Unknown: American Indian or Alaska Native
  row == 42 | #Arrestee sex and race Unknown: Asian
  row == 43 | #Arrestee sex and race Unknown: Native Hawaiian or Other Pacific Islander
  row == 44 | #Arrestee sex and race Unknown: Unknown
  row == 70 |  #'Arrestee age 2: Unknown',
  row == 73 | #Arrestee Hispanic Origin:   Unknown
  row == 80  #Arrestee race and Hispanic Origin:   Unknown race or Hispanic origin
    
    
  
  ), 1,

  trim_upcase(table)=="4B" & (
  row == 14 | #Age-specific arrest rate: Unknown
  row == 17 | #Sex-specific arrest rate: Unknown
  row == 23 | #Race-specific arrest rate: Unknown
  row == 29 |  #'Age-specific arrest rate 2: Unknown',
  row == 32 | #Hispanic Origin-specific arrest rate:   Unknown
  row == 39  #Race and Hispanic Origin-specific arrest rate:   Unknown race or Hispanic origin

  ), 1,

  trim_upcase(table)=="5A" & (
  row == 14 | #Arrestee age: Unknown
  row == 17 | #Arrestee sex: Unknown
  row == 23 | #Arrestee race: Unknown
  row == 30 | #Arrestee sex and race Male: Unknown
  row == 37 | #Arrestee sex and race Female: Unknown
  row == 38 | #Arrestee sex and race: Unknown
  row == 39 | #Arrestee sex and race Unknown: White
  row == 40 | #Arrestee sex and race Unknown: Black
  row == 41 | #Arrestee sex and race Unknown: American Indian or Alaska Native
  row == 42 | #Arrestee sex and race Unknown: Asian
  row == 43 | #Arrestee sex and race Unknown: Native Hawaiian or Other Pacific Islander
  row == 44 | #Arrestee sex and race Unknown: Unknown
  row == 70 |  #'Arrestee age 2: Unknown',
  row == 73 | #Arrestee Hispanic Origin:   Unknown
  row == 80  #Arrestee race and Hispanic Origin:   Unknown race or Hispanic origin
    
    
  
  ), 1,

  trim_upcase(table)=="5B" & (
  row == 14 | #Age-specific arrest rate: Unknown
  row == 17 | #Sex-specific arrest rate: Unknown
  row == 23 |  #Race-specific arrest rate: Unknown
  row == 29 |   #'Age-specific arrest rate 2: Unknown',
  row == 32 | #Hispanic Origin-specific arrest rate:   Unknown
  row == 39  #Race and Hispanic Origin-specific arrest rate:   Unknown race or Hispanic origin
    
    
  
  ), 1,

  trim_upcase(table)=="DM7" & (
  row == 10 | #Arrestee age: Unknown
  row == 18 | #Arrestee race: Unknown
  row == 25 | #Arrestee sex and race Male: Unknown
  row == 32 | #Arrestee sex and race Female: Unknown
  row == 33 | #Arrestee sex and race: Unknown
  row == 34 | #Arrestee sex and race Unknown: White
  row == 35 | #Arrestee sex and race Unknown: Black
  row == 36 | #Arrestee sex and race Unknown: American Indian or Alaska Native
  row == 37 | #Arrestee sex and race Unknown: Asian
  row == 38 | #Arrestee sex and race Unknown: Native Hawaiian or Other Pacific Islander
  row == 39 | #Arrestee sex and race Unknown: Unknown
  row == 55 |  #'Arrestee age 2: Unknown',
  row == 58 | #Arrestee Hispanic Origin:   Unknown
  row == 65  #Arrestee race and Hispanic Origin:   Unknown race or Hispanic origin
  
  
  ), 1,

  trim_upcase(table)=="DM9" & (
  row == 10 | #Arrestee age: Unknown
  row == 18 | #Arrestee race: Unknown
  row == 25 | #Arrestee sex and race Male: Unknown
  row == 32 | #Arrestee sex and race Female: Unknown
  row == 33 | #Arrestee sex and race: Unknown
  row == 34 | #Arrestee sex and race Unknown: White
  row == 35 | #Arrestee sex and race Unknown: Black
  row == 36 | #Arrestee sex and race Unknown: American Indian or Alaska Native
  row == 37 | #Arrestee sex and race Unknown: Asian
  row == 38 | #Arrestee sex and race Unknown: Native Hawaiian or Other Pacific Islander
  row == 39 | #Arrestee sex and race Unknown: Unknown
  row == 55 |  #'Arrestee age 2: Unknown',  
  row == 58 | #Arrestee Hispanic Origin:   Unknown
  row == 65  #Arrestee race and Hispanic Origin:   Unknown race or Hispanic origin
    
    
  ), 1,

trim_upcase(table)=="GV2A" & (
  row == 10 | #'Victim Age: Unknown',
  row == 15 | #'Victim age 2: Unknown',
  row == 22 | #'Victim sex: Unknown',
  row == 28 |  #'Victim race: Unknown',
  row == 66 | #Victim Hispanic Origin:   Unknown
  row == 73  #Victim race and Hispanic Origin:   Unknown race or Hispanic origin
    
    
), 1,


default = 0
)
)

#Double check der_cleared_cells_qc has original values as der_cleared_cells, but der_cleared_cells could have missing values
raw_6 %>%
  filter(der_cleared_cells_qc != der_cleared_cells) %>%
  checkfunction(der_cleared_cells_qc, der_cleared_cells, POPTOTAL_PERMUTATION_DESCRIPTION, table, row, estimate_domain, column)

#See the full check
raw_6 %>%
  checkfunction(der_cleared_cells_qc, der_cleared_cells, table, row, column)

#See the added cleared cells
raw_6 %>%
  filter(is.na(der_cleared_cells)) %>%
  checkfunction(der_cleared_cells_qc, der_cleared_cells, table, row, column)

#Overal freqs
raw_6 %>%
  checkfunction(der_cleared_cells_qc, der_cleared_cells)

#Make the der_cleared_cells_qc cells to the DER_NA_CODE

raw_list_vars_to_na <- c(
  "population_estimate",
  "estimate",
  "estimate_standard_error",
  "estimate_prb",
  "estimate_bias",
  "estimate_rmse",
  "estimate_upper_bound",
  "estimate_lower_bound",
  "relative_standard_error",
  "relative_rmse",
  "PRB_ACTUAL",
  "tbd_estimate",
  "estimate_unweighted",
  "population_estimate_unweighted",
  "unweighted_counts",
  "agency_counts"
)


#Look thru and fix estimates
for(i in 1:length(raw_list_vars_to_na)){

  #Current variable
  invar <- raw_list_vars_to_na[[i]] %>% rlang:::parse_expr()

  #If der_cleared_cells_qc, make sure the DER_NA_CODE overwrites the cells
  raw_6 <- raw_6 %>%
    mutate(!!invar := case_when(der_cleared_cells_qc == 1 ~  DER_NA_CODE,
                                        TRUE ~ !!invar))


}

#Quick QC to make sure that the DER_NA_CODE is used properly
raw_6 %>%
  filter(der_cleared_cells_qc == 1) %>%
  checkfunction(!!!(raw_list_vars_to_na %>% rlang:::parse_exprs()) )

raw_6 %>%
  filter(der_cleared_cells_qc == 0) %>%
  head(100) %>%
  datatable()


#Next add on the suppression code
raw_7 <- raw_6 %>%
  #Create common variables
  create_variables_suppression1()


#Check the recodes
raw_7 %>%
  checkfunction(der_na_agency_counts, agency_counts)

raw_7 %>%
  filter(estimate == DER_NA_CODE) %>%
  checkfunction(der_estimate_na_code, estimate)

raw_7 %>%
  checkfunction(der_elig_suppression, der_na_agency_counts, der_estimate_na_code)


#Make sure that when der_na_agency_counts == 1 that the estimate makes sense
raw_7 %>%
  filter(der_na_agency_counts == 1) %>%
  checkfunction(estimate)

raw_7_1 <- raw_7 %>%
  create_variables_suppression2()

  #Delete the old objects
  rm(list=c(paste0("raw_", 1:7)))
  invisible(gc())

  #Need to make object raw_7_1 to make code work
  #Code to define special cell and Tribal permutation suppression rule  
  #Need to handle at each permutation/cell level using dataset raw_7_1 as a base
  
  #Call the R program to create the der_rrmse_gt_30_se_estimate_0_2_cond variable
  source("0-Create main suppression variable.R")  
  
  #Check the merge
  log_dim(raw_7_2)
  log_dim(raw_8)
  log_dim(raw_7_r0)
  log_dim(raw_7_r1)
  log_dim(raw_7_r2)
  log_dim(raw_7_r3)
  log_dim(raw_7_r4)
  
  
  #Delete the old objects
  rm(list=ls(pattern="raw_7_"))
  invisible(gc())  
  
  
  #################################################################################################################

 

#Check the recodes
raw_8 %>% head(1000) %>% checkfunction(der_rrmse_gt_30, relative_rmse, der_estimate_na_code)
raw_8 %>% head(1000) %>% checkfunction(der_estimate_0, estimate, der_estimate_na_code)
raw_8 %>% head(1000) %>% checkfunction(der_estimate_se_0, estimate_standard_error, der_estimate_na_code)
raw_8 %>% head(1000) %>% checkfunction(der_estimate_0_se_0, der_estimate_0, der_estimate_se_0, der_estimate_na_code)

#For Alt 6 check   

raw_8 %>% checkfunction(der_rrmse_gt_30_se_estimate_0_2_cond, der_rrmse_gt_30, der_estimate_0_se_0, POPTOTAL_ORIG_PERMUTATION_NUMBER, POPTOTAL_UNIV_COV_AGENCY_TRIBAL)
raw_8 %>% filter(trimws(estimate_domain, which="both") =="Agency indicator: Tribal agencies") %>% checkfunction(der_rrmse_gt_30_se_estimate_0_2_cond, der_rrmse_gt_30, der_estimate_0_se_0, estimate_domain,POPTOTAL_UNIV_COV_AGENCY_TRIBAL)
raw_8 %>% filter(trimws(estimate_domain, which="both") =="Agency indicator: State police") %>% checkfunction(der_rrmse_gt_30_se_estimate_0_2_cond, der_rrmse_gt_30, der_estimate_0_se_0, estimate_domain,POPTOTAL_UNIV_COV_AGENCY_STATE_POLICE)
raw_8 %>% filter(trimws(estimate_domain, which="both") =="Agency indicator: Other state agencies") %>% checkfunction(der_rrmse_gt_30_se_estimate_0_2_cond, der_rrmse_gt_30, der_estimate_0_se_0, estimate_domain,POPTOTAL_UNIV_COV_AGENCY_OTHER)

raw_8 %>% filter( !(trimws(estimate_domain, which="both") %in% c("Agency indicator: Tribal agencies", "Agency indicator: State police", "Agency indicator: Other state agencies"))) %>% checkfunction(der_rrmse_gt_30_se_estimate_0_2_cond, der_rrmse_gt_30, der_estimate_0_se_0, POPTOTAL_UNIV_POP_COV)

raw_8 %>%
  checkfunction(der_na_estimate_prb , estimate_prb)


raw_8 %>%
  head(1000) %>%
  checkfunction(der_rrmse_30, relative_rmse)



raw_8 %>%
  checkfunction(der_agency_count_10, agency_counts)

#See the cells where estimate_prb is missing
raw_8 %>%
  filter(is.na(estimate_prb) & der_elig_suppression == 1) %>%
  checkfunction(estimate_prb, PERMUTATION_NUMBER, POPTOTAL_PERMUTATION_DESCRIPTION, indicator_name)

raw_8 %>%
  checkfunction(der_orig_permutation , PERMUTATION_NUMBER)


#Read in the momentum rule
raw_8_top <- read_rds(
  paste0(filepathout_Momentum_Rule, "Momemtum_Rule_", PERMUTATION_NAME, ".rds")
)


#Merge on the results
raw_9 <- raw_8 %>%
  left_join(raw_8_top, by=c("POPTOTAL_ORIG_PERMUTATION_NUMBER"))

log_dim(raw_9)
log_dim(raw_8)
log_dim(raw_8_top)


#From raw_9 use the following for suppression rule
#a.	Any estimate with > 30% %RRMSE OR 10 or fewer unweighted agencies with incidents get an estimate level suppression flag of 1; else 0:  der_rrmse_30_agency_10
#b.	Grouping by estimate_geographic_location, calculate the % of estimates with a value of 1 in the flag from 2.a above:  prop_30_10
#c. Grouping by estimate_geographic_location, calculate the population coverage for the permutation group:  pop_cov

raw_10 <- raw_9 %>%
  mutate(
    #d.	Any permutation group (estimate_geographic_location level) with a value from 2.b > 50% AND a value from 2.c < 80% gets a permutation group level suppression flag of 1; else 0.	This flag applies to all estimates in the permutation group

    # der_perm_group_suppression_flag = fcase(
    #     prop_30_10 > 0.50 & pop_cov < 0.8,  1,
    #     default = 0
    # ),

    #Update on 2022-07-19:
    #for the momentum rule use main tables and level 1 estimates only and use a cutoff of 75%
    #prop_30_10_top is the variable to use
    # der_perm_group_suppression_flag = fcase(
    #   prop_30_10_top > 0.75 & pop_cov < 0.8, 1,
    #   default = 0
    # ),
    
    #Update on 2023-02-10%:
    #	More than 75% of key estimates in the permutation are suppressed based on estimate-level criteria AND
    #	Permutation-level population coverage is less than 80%

    der_perm_group_suppression_flag = fcase(
      der_rrmse_gt_30_se_estimate_0_2_cond_top > 0.75 & (POPTOTAL_ORIG_PERMUTATION_NUMBER_COV) < 0.8, 1,
      default = 0
    ),
    

    #e.	Any permutation group (estimate_geographic_location level) with a value from 2.c > 95% gets a permutation group level force un-suppress flag of 1; else 0. This flag applies to all estimates in the permutation group

    # der_perm_group_unsuppression_flag = fcase(
    #     pop_cov > 0.95,  1,
    #     default = 0
    #  ),
    #Update on 2022-07-19
    #the 95%+ coverage rule is based on PERM 0 only (and all lower permutations follow if PERM 0 has coverage greater than 95%)
    # der_perm_group_unsuppression_flag = fcase(
    #   pop_cov_perm0 > 0.95, 1,
    #   default = 0
    # ),
    
    #Update on 2023-02-10
    #the 80%+ coverage rule is based on PERM 0 only (and all lower permutations follow if PERM 0 has coverage greater than 80%)
    der_perm_group_unsuppression_flag = fcase(
      POPTOTAL_ORIG_PERMUTATION_NUMBER_COV > 0.80, 1,
      default = 0
    ),    

    #Variable to create for database:  suppression_flag_indicator
    #Create suppression flag for the national permutation
    #No 10% agency rule
    #No principal city
    #No momentum rule
    #Do the unsuppression rule
    suppression_flag_indicator_national = fcase(
      #i.	If the flag from 2.e=1 then the final estimate level suppression flag=0; else. Unsuppression rule
      der_perm_group_unsuppression_flag == 1 & !is.na(der_rrmse_gt_30_se_estimate_0_2_cond)  , 0,
      #iii.	Set the final estimate level suppression flag to the value from 2.a
      der_perm_group_unsuppression_flag == 0 ,  der_rrmse_gt_30_se_estimate_0_2_cond
    ),
    
    #Create suppression flag for our regular rules for non-MSA
    #10% agency rule
    #momentum rule
    #Do the unsuppression rule    
    suppression_flag_indicator_regular = fcase(
      #New.  Add on the Missing Certainty Agency Rule	
      POPTOTAL_ORIG_UNIV_ELIG_PERM_AGENCY_MISSING_OVER_10_PERCENT == TRUE , 1,	      
      #i.	If the flag from 2.e=1 then the final estimate level suppression flag=0; else.
      der_perm_group_unsuppression_flag == 1 & !is.na(der_rrmse_gt_30_se_estimate_0_2_cond)  , 0,
      #ii.	If the flag from 2.d=1 then the final estimate level suppression flag=1; else.
      der_perm_group_suppression_flag == 1 & !is.na(der_rrmse_gt_30_se_estimate_0_2_cond) , 1,
      #iii.	Set the final estimate level suppression flag to the value from 2.a
      der_perm_group_unsuppression_flag == 0 ,  der_rrmse_gt_30_se_estimate_0_2_cond
    ),    
    
    #Create suppression flag for our MSA only
    #principal city
    #momentum rule
    #Do the unsuppression rule    
    suppression_flag_indicator_msa = fcase(
      #New.  Add on the Missing Principal city Rule	
      POPTOTAL_ORIG_ELIG_PERM_AGENCY_MISSING_PRINCIPAL_CITY == TRUE , 1,	      
      #i.	If the flag from 2.e=1 then the final estimate level suppression flag=0; else.
      der_perm_group_unsuppression_flag == 1 & !is.na(der_rrmse_gt_30_se_estimate_0_2_cond)  , 0,
      #ii.	If the flag from 2.d=1 then the final estimate level suppression flag=1; else.
      der_perm_group_suppression_flag == 1 & !is.na(der_rrmse_gt_30_se_estimate_0_2_cond) , 1,
      #iii.	Set the final estimate level suppression flag to the value from 2.a
      der_perm_group_unsuppression_flag == 0 ,  der_rrmse_gt_30_se_estimate_0_2_cond
    ),      
    
    #Create suppression flag for our university and tribal only
    #No 10% agency rule
    #No principal city
    #Do momentum rule
    #Do the unsuppression rule
    suppression_flag_indicator_univ_tribal = fcase(
      #i.	If the flag from 2.e=1 then the final estimate level suppression flag=0; else.
      der_perm_group_unsuppression_flag == 1 & !is.na(der_rrmse_gt_30_se_estimate_0_2_cond)  , 0,
      #ii.	If the flag from 2.d=1 then the final estimate level suppression flag=1; else.
      der_perm_group_suppression_flag == 1 & !is.na(der_rrmse_gt_30_se_estimate_0_2_cond) , 1,
      #iii.	Set the final estimate level suppression flag to the value from 2.a
      der_perm_group_unsuppression_flag == 0 ,  der_rrmse_gt_30_se_estimate_0_2_cond
    ),       
    
    #List of geographic permutations 
    # CONST_NATIONAL_PERM     <- c(1)
    # CONST_NATIONAL_AGN_PERM <- c(2:11)
    # CONST_REGIONAL_PERM     <- c(12:55)
    # CONST_STATE_PERM        <- c(56:106)
    # CONST_UNIV_PERM         <- c(107)
    # CONST_TRIBAL_PERM       <- c(108)
    # CONST_MSA_PERM          <- c(109:492, 638:709)
    # CONST_JD_PERM           <- c(493:582)
    # CONST_FO_PERM           <- c(583:637)
    
    suppression_flag_indicator = fcase(
      #National permutation
      POPTOTAL_ORIG_PERMUTATION_NUMBER %in% c(CONST_NATIONAL_PERM), suppression_flag_indicator_national, 
      #University and Tribal
      POPTOTAL_ORIG_PERMUTATION_NUMBER %in% c(CONST_UNIV_PERM, 
                                              CONST_TRIBAL_PERM),   suppression_flag_indicator_univ_tribal, 
      #MSA permutation
      POPTOTAL_ORIG_PERMUTATION_NUMBER %in% c(CONST_MSA_PERM), suppression_flag_indicator_msa, 
      #Remaining permutations
      POPTOTAL_ORIG_PERMUTATION_NUMBER %in% c(
        CONST_NATIONAL_AGN_PERM,
        CONST_REGIONAL_PERM,
        CONST_STATE_PERM,
        CONST_JD_PERM,
        CONST_FO_PERM), suppression_flag_indicator_regular
    
    
    
    )
)

#QC the variables
raw_10 %>%
  checkfunction(der_perm_group_suppression_flag, der_rrmse_gt_30_se_estimate_0_2_cond_top, POPTOTAL_ORIG_PERMUTATION_NUMBER_COV, PERMUTATION_NUMBER, POPTOTAL_PERMUTATION_DESCRIPTION)

raw_10 %>%
  checkfunction(der_perm_group_unsuppression_flag, POPTOTAL_ORIG_PERMUTATION_NUMBER_COV, PERMUTATION_NUMBER, POPTOTAL_PERMUTATION_DESCRIPTION)

#National permutation
raw_10 %>%
  filter(POPTOTAL_ORIG_PERMUTATION_NUMBER %in% c(CONST_NATIONAL_PERM)) %>%
  checkfunction(suppression_flag_indicator, der_perm_group_unsuppression_flag, der_rrmse_gt_30_se_estimate_0_2_cond)

#University and Tribal
raw_10 %>%
  filter(POPTOTAL_ORIG_PERMUTATION_NUMBER %in% c(CONST_UNIV_PERM, CONST_TRIBAL_PERM)) %>%
  checkfunction(suppression_flag_indicator, der_perm_group_unsuppression_flag, der_perm_group_suppression_flag, der_rrmse_gt_30_se_estimate_0_2_cond)


#MSA permutation
raw_10 %>%
  filter(POPTOTAL_ORIG_PERMUTATION_NUMBER %in% c(CONST_MSA_PERM)) %>%
  checkfunction(suppression_flag_indicator, POPTOTAL_ORIG_ELIG_PERM_AGENCY_MISSING_PRINCIPAL_CITY, der_perm_group_unsuppression_flag, der_perm_group_suppression_flag, der_rrmse_gt_30_se_estimate_0_2_cond)

#Remaining permutations
raw_10 %>%
  filter(
    #Remaining permutations
    POPTOTAL_ORIG_PERMUTATION_NUMBER %in% c(
      CONST_NATIONAL_AGN_PERM,
      CONST_REGIONAL_PERM,
      CONST_STATE_PERM,
      CONST_JD_PERM,
      CONST_FO_PERM)) %>%  
  checkfunction(suppression_flag_indicator, POPTOTAL_ORIG_UNIV_ELIG_PERM_AGENCY_MISSING_OVER_10_PERCENT, der_perm_group_unsuppression_flag, der_perm_group_suppression_flag, der_rrmse_gt_30_se_estimate_0_2_cond)



#Need to ask if suppression_flag_indicator missing for NA and missing agency_counts
raw_10 %>%
  filter(is.na(suppression_flag_indicator)) %>%
  checkfunction(estimate)

#Need to make the estimate_domain to become estimate_domain_1 and estimate_domain_2 and split by the ":"
raw_10 %>%
  checkfunction(estimate_domain)

raw_11  <- raw_10 %>%
  mutate(tbd_estimate_domain = estimate_domain) %>%
  separate(estimate_domain, c("estimate_domain_1", "estimate_domain_2"),  ":") %>%
  #Make sure that the blank spaces are removed
  mutate(estimate_domain_1 = trimws(estimate_domain_1, which="both"),
         estimate_domain_2 = trimws(estimate_domain_2, which="both"))

raw_11 %>%
  checkfunction(tbd_estimate_domain, estimate_domain_1, estimate_domain_2)

#Add code to unsuppress state estimates for violent crime offense and property crime offense

#Code for subset
off_violent_property_subset <- "    PERMUTATION_NUMBER %in% c(56:106)    & #State permutations
                                    der_perm_group_suppression_flag == 1 & #Suppress due to permutation
                                    suppression_flag_indicator == 1      & #Suppression
                                    der_rrmse_gt_30_se_estimate_0_2_cond == 0            #Not suppress by itself" %>% rlang:::parse_expr()

#Identify the offense crime indicators
off_violent_crime <- c("t_2a_1_1_17", "t_2a_1_2_17")
off_property_crime <- c("t_2b_1_1_14", "t_2b_1_2_14")

test_off_violent <- raw_11 %>%
  filter(
    der_variable_name %in% off_violent_crime[[1]]   & #Violent Crime Total at position 1
    !!off_violent_property_subset
    )  %>%
  #Need to process by Permutation only interested in state permutations:  PERMUTATION_NUMBER %in% c(56:106)
  group_by(PERMUTATION_NUMBER) %>%
  mutate(der_off_violent_crime_unsuppress = 1) %>%
  ungroup() %>%
  select(PERMUTATION_NUMBER, der_off_violent_crime_unsuppress)

log_dim(raw_11)
log_dim(test_off_violent)

test_off_property <- raw_11 %>%
  filter(
    der_variable_name %in% off_property_crime[[1]]  & #Property Crime Total at position 1
    !!off_violent_property_subset
    )  %>%
  #Need to process by Permutation only interested in state permutations:  PERMUTATION_NUMBER %in% c(56:106)
  group_by(PERMUTATION_NUMBER) %>%
  mutate(der_off_property_crime_unsuppress = 1) %>%
  ungroup() %>%
  select(PERMUTATION_NUMBER, der_off_property_crime_unsuppress)

log_dim(raw_11)
log_dim(test_off_property)

raw_12 <- reduce(list(raw_11, test_off_violent, test_off_property), left_join, by="PERMUTATION_NUMBER") %>%
  #Unsuppress the Offense Violent crime and property crime estimate
  mutate(
    suppression_flag_indicator = case_when(
      #Choose the offense violent crime and property variables
      der_variable_name %in% c( off_violent_crime,    #Violent Crime
                                off_property_crime) & #Property Crime)
      #When both the violent and property crime are unsuppress within the state permutations
      der_off_violent_crime_unsuppress  == 1 &
      der_off_property_crime_unsuppress == 1 &
      #If the estimate is not the NA code then make 0 and unsuppress
      estimate != DER_NA_CODE ~ 0,
      #Otherwise keep as is
      TRUE ~ suppression_flag_indicator
    )
  )

log_dim(raw_12)
log_dim(raw_11)
log_dim(test_off_violent)
log_dim(test_off_property)

#Check to see for the permutations that have unsuppress offenses violent and property crimes
raw_12 %>%
  filter(der_off_violent_crime_unsuppress == 1 & der_off_property_crime_unsuppress == 1) %>%
  checkfunction(estimate_geographic_location, suppression_flag_indicator, der_off_violent_crime_unsuppress, der_off_property_crime_unsuppress)

#Check to see for the permutations that have unsuppress offenses violent and property crimes the variables
raw_12 %>%
  filter(der_off_violent_crime_unsuppress == 1 & der_off_property_crime_unsuppress == 1 &
          der_variable_name %in% c( off_violent_crime,    #Violent Crime
                                    off_property_crime)  #Property Crime)
           ) %>%
  checkfunction(estimate_geographic_location, suppression_flag_indicator, der_variable_name, estimate, estimate_type,   der_off_violent_crime_unsuppress, der_off_property_crime_unsuppress)

#Remove the objects
rm(off_violent_property_subset, off_violent_crime, off_property_crime, test_off_violent, test_off_property)
invisible(gc())

#20220810: Need to swap out the old prop_30_10 with the new variable prop_30_10_top, but rename it to be prop_30_10
raw_12 <- raw_12 %>%
  #Drop the old prop_30_10 variable
  #select(-prop_30_10) %>%
  #Rename prop_30_10_top to prop_30_10
  rename(#prop_30_10 = prop_30_10_top,
         pop_cov = POPTOTAL_UNIV_POP_COV,
         orig_estimate_lower_bound = estimate_lower_bound
         ) %>%
  mutate(
    one = 1,
    
    #Need to edit the lower bounds
    estimate_lower_bound = fcase(      
      #If the orig_estimate_lower_bound is negative and not the NA code then make 0
      (orig_estimate_lower_bound < 0) & (orig_estimate_lower_bound != DER_NA_CODE), 0, 
      #Otherwise keep the lower bound as is
      one == 1, orig_estimate_lower_bound
    )
  )

#Check the estimate_lower_bound
raw_12 %>%
  filter(orig_estimate_lower_bound != estimate_lower_bound) %>%
  checkfunction(table, section, row, column, estimate_type_num, estimate_lower_bound, orig_estimate_lower_bound)


#Need to drop the following offenses:
#Drop legacy rape, and also drop sexual assault with an object and sodomy 


#Change Revised Rape to	Rape
#Change fondling to	criminal sexual contact
raw_13 <- raw_12 %>%
  rename(old_indicator_name = indicator_name) %>%
  mutate(
    #Create variable to drop records
    der_drop_indicator_name = fcase(
      str_detect(string=old_indicator_name, pattern = regex(pattern="^Rape$", ignore_case=TRUE)), 1,
      str_detect(string=old_indicator_name, pattern = regex(pattern="^Sodomy$", ignore_case=TRUE)), 1,
      str_detect(string=old_indicator_name, pattern = regex(pattern="^Sexual\\s+Assault\\s+with\\s+an\\s+Object$", ignore_case=TRUE)), 1,
      default = 0
    ), 
    
    #Create new indicator_name with the new names
    indicator_name = fcase(
      str_detect(string=old_indicator_name, pattern = regex(pattern="^Revised\\s+Rape$", ignore_case=TRUE)), "Rape",
      str_detect(string=old_indicator_name, pattern = regex(pattern="^Fondling$", ignore_case=TRUE)), "Criminal Sexual Contact",
      !is.na(old_indicator_name), old_indicator_name
    )
  )

#Check recodes 
raw_13 %>% checkfunction(der_drop_indicator_name, indicator_name, old_indicator_name)

#Drop the records
raw_14 <- raw_13 %>%
  filter(der_drop_indicator_name == 0)

#Check the dimension
log_dim(raw_14)
log_dim(raw_13)

#Need to make estimate_prb and PRB_ACTUAL to be all missing
#Need to create a estimate_copula.  Currently estimate_bias = estimate - estimate_copula
#So estimate_copula = estimate - estimate_bias for all estimate type

raw_15 <- raw_14 %>%
  mutate(
    #Make the one variable
    one = 1,
    
    #Make estimate_prb to all missing
    estimate_prb = NA_real_, 
	
    #Make PRB_ACTUAL to all missing
    PRB_ACTUAL = NA_real_, 	
    
    #Create estimate_copula
    estimate_copula = fcase(
      #Keep NA code as is
      estimate == DER_NA_CODE, DER_NA_CODE,
      #Otherwise apply the formula
      one == 1, estimate - estimate_bias
    )
  )

#Check the recodes
raw_15 %>% checkfunction(estimate_prb)
#raw_15 %>% checkfunction(estimate_copula, estimate, estimate_bias)

#Declare the final data
final_data_output <- raw_15


  
# Add on the correlations, if the data_year = most recent data year, so update next year
# the actual correlation values are subject to change in future years
if (year == 2024) {
  final_data_output_corr <- final_data_output %>%
    mutate(# Calculate proportion of eligible pseudo-ORIs reporting 1+ incidents
      PROP_ELIG_ORIS_NONZERO_COUNT=fcase(estimate==-9,-9,
                estimate!=-9 & POPTOTAL_NUMBER_OF_ELIGIBLE_PSEUDO_ORIS != 0, agency_counts/POPTOTAL_NUMBER_OF_ELIGIBLE_PSEUDO_ORIS),
      # Use the proportion to set the correlation
      CORRELATION_WITH_PRIOR_YEAR=fcase(
          estimate==-9, -9,
          estimate==0 | estimate_standard_error==0 | is.na(agency_counts) | PROP_ELIG_ORIS_NONZERO_COUNT < 0.007, 0,
          PROP_ELIG_ORIS_NONZERO_COUNT < 0.014, 0.126,
          PROP_ELIG_ORIS_NONZERO_COUNT < 0.024, 0.175,
          PROP_ELIG_ORIS_NONZERO_COUNT < 0.041, 0.261,
          PROP_ELIG_ORIS_NONZERO_COUNT < 0.071, 0.355,
          PROP_ELIG_ORIS_NONZERO_COUNT < 0.121, 0.465,
          PROP_ELIG_ORIS_NONZERO_COUNT < 0.204, 0.585,
          PROP_ELIG_ORIS_NONZERO_COUNT < 0.344, 0.692,
          PROP_ELIG_ORIS_NONZERO_COUNT < 0.564, 0.762,
          PROP_ELIG_ORIS_NONZERO_COUNT <= 1, 0.835
      )
    )
  
  #Create a list of variables to output for each section
  OUTPUT_VARS <- c(
    "indicator_name",
    "estimate",
    "estimate_unweighted",
    "estimate_geographic_location",
    "estimate_type",
    "estimate_type_num",
    "estimate_type_detail_percentage",
    "estimate_type_detail_rate",
    "estimate_domain_1",
    "estimate_domain_2",
    "estimate_standard_error",
    "estimate_upper_bound",
    "estimate_lower_bound",
    "relative_standard_error",
    "analysis_weight_name",
    "estimate_prb",
    "estimate_bias",
    "estimate_rmse",
    "relative_rmse",
    #poor_quality_indicator",
    "suppression_flag_indicator",
    "der_elig_suppression",
    "pop_cov",
    "agency_counts",
    "der_rrmse_30",
    #der_agency_count_10",
    "der_rrmse_gt_30_se_estimate_0_2_cond", #der_rrmse_30_agency_10",
    "der_rrmse_gt_30_se_estimate_0_2_cond_top", #prop_30_10",
    "der_perm_group_unsuppression_flag",
    "der_perm_group_suppression_flag",
    "population_estimate",
    "time_series_start_year",
    "full_table",
    "der_variable_name",
    "PERMUTATION_NUMBER",
    "PRB_ACTUAL",
    "POPTOTAL_ORIG_UNIV_ELIG_PERM_AGENCY_MISSING_OVER_10_PERCENT",
    "POPTOTAL_ORIG_ELIG_PERM_AGENCY_MISSING_PRINCIPAL_CITY",
    "PROP_ELIG_ORIS_NONZERO_COUNT",
    "CORRELATION_WITH_PRIOR_YEAR", 
    "estimate_copula"
  ) %>% rlang:::parse_exprs()
} else if (year < 2024) {
  final_data_output_corr <- final_data_output
  
  #Create a list of variables to output for each section
  OUTPUT_VARS <- c(
    "indicator_name",
    "estimate",
    "estimate_unweighted",
    "estimate_geographic_location",
    "estimate_type",
    "estimate_type_num",
    "estimate_type_detail_percentage",
    "estimate_type_detail_rate",
    "estimate_domain_1",
    "estimate_domain_2",
    "estimate_standard_error",
    "estimate_upper_bound",
    "estimate_lower_bound",
    "relative_standard_error",
    "analysis_weight_name",
    "estimate_prb",
    "estimate_bias",
    "estimate_rmse",
    "relative_rmse",
    #poor_quality_indicator",
    "suppression_flag_indicator",
    "der_elig_suppression",
    "pop_cov",
    "agency_counts",
    "der_rrmse_30",
    #der_agency_count_10",
    "der_rrmse_gt_30_se_estimate_0_2_cond", #der_rrmse_30_agency_10",
    "der_rrmse_gt_30_se_estimate_0_2_cond_top", #prop_30_10",
    "der_perm_group_unsuppression_flag",
    "der_perm_group_suppression_flag",
    "population_estimate",
    "time_series_start_year",
    "full_table",
    "der_variable_name",
    "PERMUTATION_NUMBER",
    "PRB_ACTUAL",
    "POPTOTAL_ORIG_UNIV_ELIG_PERM_AGENCY_MISSING_OVER_10_PERCENT",
    "POPTOTAL_ORIG_ELIG_PERM_AGENCY_MISSING_PRINCIPAL_CITY", 
    "estimate_copula"
  ) %>% rlang:::parse_exprs()
} else {
  stop(paste0("ERROR: need to code in correlation rules for ",year))
}

for(t in unique(final_data_output_corr$table)){
  final_data_output_table <- final_data_output_corr %>% filter(table==t)

  final_data_output_table %>%
  mutate(time_series_start_year = year) %>%
  select(
  !!!OUTPUT_VARS
) %>%
  write.csv1(paste0(filepathout_Indicator_Tables, "Indicator_Tables_",PERMUTATION_NAME,"_",t,".csv"))


final_data_output_table %>%
  mutate(time_series_start_year = year) %>%
  filter(suppression_flag_indicator == 0) %>%
  select(
  !!!OUTPUT_VARS
) %>%
  write.csv1(paste0(filepathout_Indicator_Tables_no_supp, "Indicator_Tables_no_supp_",PERMUTATION_NAME,"_",t,".csv"))


#Identify any missing PRBs and non-zero estimates
final_data_output_table %>%
  filter(is.na(estimate_copula) & estimate > 0) %>%
  mutate(time_series_start_year = year) %>%
  select(
  !!!OUTPUT_VARS
  ) %>%
  write.csv1(paste0(filepathout_Indicator_Tables_flag_non_zero_estimates_with_no_prb, "Indicator_Tables_flag_non_zero_estimates_with_no_prb_",PERMUTATION_NAME,"_",t,".csv"))
  
final_data_output_table %>%
  filter(estimate_type == "count") %>% mutate(
    p1=table,
    p2=section,
    p3=row,
    p4=column
  ) %>%
    select(
    p1,
    p2,
    p3,
    p4,
    der_variable_name,
    PERMUTATION_NUMBER
 ) %>% write.csv1(paste0(filepathout_for_validation, "der_variable_name_",PERMUTATION_NAME,"_",t,".csv"))

}

#Delete all the raw files
rm(list=ls(pattern="raw"))
invisible(gc())

