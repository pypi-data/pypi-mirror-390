# ---
# title: '10000 - Make Momentum Rule'
# author: "Philip Lee"
# date: "October 1, 2021"
# output:
#   html_document: default
#   pdf_document:  default
# ---

#Read in the common code starting code for program
source("0-Common Code for Suppression.R")


#Next need to identify and keep the momentum rule tables and also the main 
#geographic permutations

raw_list_files_mom_rule <- raw_list_files %>%
  as_tibble() %>%
  #Create variables to identify which files to keep
  mutate(
    der_file_table              = str_match(string=value, pattern="Table (\\w+)_Reporting_Database_After_Variance_(\\d+).csv")[,2],
    der_file_permutation_number = str_match(string=value, pattern="Table (\\w+)_Reporting_Database_After_Variance_(\\d+).csv")[,3] %>% as.numeric()
  ) %>%
  mutate(
    der_file_table_keep = fcase(der_file_table %in% c(CONST_MOMENTUM_RULE_TABLES), 1,
                                default = 0),
    der_file_permutation_number_keep = fcase(der_file_permutation_number <= CONST_MAIN_PERMUTATION_MAX, 1,
                                             default = 0)
  )

#Check the recodes
raw_list_files_mom_rule %>% checkfunction(der_file_table, value)
raw_list_files_mom_rule %>% checkfunction(der_file_permutation_number, value)
raw_list_files_mom_rule %>% checkfunction(der_file_table_keep, der_file_table)
raw_list_files_mom_rule %>% checkfunction(der_file_permutation_number_keep, der_file_permutation_number)

#Keep the files we are interested in for momentum rule and overwrite old variable
raw_list_files <- raw_list_files_mom_rule %>%
  filter(der_file_table_keep == 1 & 
         der_file_permutation_number_keep == 1) %>%
         select(value) %>%
         pull()

#See the list of files used
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

#Next add on the suppression code
raw_7 <- raw_4 %>%
  #Create common variables
  create_variables_suppression1() %>%
  mutate(
   
    #Need to get the main indicator tables and drop the drug modules
    der_main_indicator_tables = fcase(trim_upcase(full_table) %in% der_main_tables, 1,
                                          default = 0),

    #Write the code to identify Level 1 and 2 suppression criteria
    der_suppression_level = fcase(
      ###################################Table 1a###############################################
      #Top row
      trim_upcase(table) == "1A" &
        row %in% c(
          1 #Incident count
        ), 1,

      #Secondary row
      trim_upcase(table) == "1A" &
        row %in% c(
          3, #Weapon involved: No
          4, #Weapon involved: Yes
          11, #Injury: No
          12, #Injury: Yes
          13, #Multiple victims: 1 victim
          14, #Multiple victims: 2+ victims
          15, #Multiple offenders: 1 offender
          16, #Multiple offenders: 2+ offenders
          17, #Multiple offenders: Unknown offenders
          21, #Victim-offender relationship: Intimate partner
          22, #Victim-offender relationship: Other family
          23, #Victim-offender relationship: Outside family but known to victim
          24, #Victim-offender relationship: Stranger
          25, #Victim-offender relationship: Victim was Offender
          26, #Victim-offender relationship: Unknown relationship
          64, #Clearance: Not cleared
          65, #Clearance: Cleared through arrest
          66 #Clearance: Exceptional clearance
        ), 2,

      ###################################Table 1b###############################################
      #Top row
      trim_upcase(table) == "1B" &
        row %in% c(
          1 #Incident count
        ), 1,

      #Secondary row
      trim_upcase(table) == "1B" &
        row %in% c(
          3, #Weapon involved: No
          4, #Weapon involved: Yes
          11, #Multiple victims: 1 victim
          12, #Multiple victims: 2+ victims
          13, #Multiple offenders: 1 offender
          14, #Multiple offenders: 2+ offenders
          15, #Multiple offenders: Unknown offenders
          56, #Clearance: Not cleared
          57, #Clearance: Cleared through arrest
          58, #Clearance: Exceptional clearance
          64 #Property loss: None

        ), 2,

      ###################################Table 1c###############################################
      #Top row
      trim_upcase(table) == "1C" &
        row %in% c(
          1 #Incident count
        ), 1,

      #Secondary row
      trim_upcase(table) == "1C" &
        row %in% c(
          3, #Multiple offenders: 1 offender
          4, #Multiple offenders: 2+ offenders
          5, #Multiple offenders: Unknown offenders
          46, #Clearance: Not cleared
          47, #Clearance: Cleared through arrest
          48 #Clearance: Exceptional clearance
        ), 2,

      ###################################Table 2a###############################################
      #Top row
      trim_upcase(table) == "2A" &
        row %in% c(
          1 #Offense count
        ), 1,

      #Secondary row
      trim_upcase(table) == "2A" &
        row %in% c(
          3, #Weapon involved: No
          4, #Weapon involved: Yes
          11, #Injury: No
          12, #Injury: Yes
          13, #Multiple victims: 1 victim
          14, #Multiple victims: 2+ victims
          15, #Multiple offenders: 1 offender
          16, #Multiple offenders: 2+ offenders
          17, #Multiple offenders: Unknown offenders
          18, #Victim-offender relationship: Intimate partner
          19, #Victim-offender relationship: Other family
          20, #Victim-offender relationship: Outside family but known to victim
          21, #Victim-offender relationship: Stranger
          22, #Victim-offender relationship: Victim was Offender
          23, #Victim-offender relationship: Unknown relationship
          61, #Clearance: Not cleared through arrest
          62 #Clearance: Cleared through arrest
        ), 2,

      ###################################Table 2b###############################################
      #Top row
      trim_upcase(table) == "2B" &
        row %in% c(
          1 #Offense count
        ), 1,

      #Secondary row
      trim_upcase(table) == "2B" &
        row %in% c(
          11, #Multiple victims: 1 victim
          12, #Multiple victims: 2+ victims
          13, #Multiple offenders: 1 offender
          14, #Multiple offenders: 2+ offenders
          15, #Multiple offenders: Unknown offenders
          53, #Clearance: Not cleared through arrest
          54 #Clearance: Cleared through arrest
        ), 2,

      ###################################Table 2c###############################################
      #Top row
      trim_upcase(table) == "2C" &
        row %in% c(
          1 #Offense count
        ), 1,

      #Secondary row
      trim_upcase(table) == "2C" &
        row %in% c(
          40, #Clearance: Not cleared through arrest
          41 #Clearance: Cleared through arrest
        ), 2,

      ###################################Table 3a###############################################
      #Top row
      trim_upcase(table) == "3A" &
        row %in% c(
          1 #Victimization count
        ), 1,

      #Secondary row
      trim_upcase(table) == "3A" &
        row %in% c(
          5, #Victim Age: Under 5
          6, #Victim Age: 5-14
          7, #Victim Age: 15
          8, #Victim Age: 16
          9, #Victim Age: 17
          10, #Victim Age: 18-24
          11, #Victim Age: 25-34
          12, #Victim Age: 35-64
          13, #Victim Age: 65+
          15, #Victim sex: Male
          16, #Victim sex: Female
          18, #Victim race: White
          19, #Victim race: Black
          20, #Victim race: American Indian or Alaska Native
          21, #Victim race: Asian
          22, #Victim race: Native Hawaiian or Other Pacific Islander
          66, #Weapon involved: No
          67, #Weapon involved: Yes
          74, #Injury: No
          75, #Injury: Yes
          76, #Victim-offender relationship: Intimate partner
          77, #Victim-offender relationship: Other family
          78, #Victim-offender relationship: Outside family but known to victim
          79, #Victim-offender relationship: Stranger
          80, #Victim-offender relationship: Victim was Offender
          81 #Victim-offender relationship: Unknown relationship
        ), 2,

      ###################################Table 3C###############################################
      #Top row
      trim_upcase(table) == "3C" &
        row %in% c(
          1, #Businesses: Victimization count
          3 #Other non-person victims: Victimization count
        ), 1,

      #Secondary row
      # trim_upcase(table) == "" &
      #   row %in% c(
      #
      #     ) ~ 2,

      ###################################Table 4a###############################################
      #Top row
      trim_upcase(table) == "4A" &
        row %in% c(
          1 #Arrest count
        ), 1,

      #Secondary row
      trim_upcase(table) == "4A" &
        row %in% c(
          2, #Arrest type: On-view arrest
          3, #Arrest type: Summoned/cited
          4, #Arrest type: Taken into custody
          10, #Arrestee age: 18-24
          11, #Arrestee age: 25-34
          12, #Arrestee age: 35-64
          13, #Arrestee age: 65+
          15, #Arrestee sex: Male
          16, #Arrestee sex: Female
          18, #Arrestee race: White
          19, #Arrestee race: Black
          20, #Arrestee race: American Indian or Alaska Native
          21, #Arrestee race: Asian
          22, #Arrestee race: Native Hawaiian or Other Pacific Islander
          52, #Arrestee armed: No
          53, #Arrestee armed: Yes
          57, #Weapon involved: No
          58 #Weapon involved: Yes
        ), 2,

      ###################################Table 5a###############################################
      #Top row
      trim_upcase(table) == "5A" &
        #Want selected offenses in 5a
        column %in% c(
          1, #NIBRS crimes against persons (Total)
          2, #Aggravated Assault
          3, #Simple Assault
          4, #Intimidation
          5, #Murder and Non-negligent Manslaughter
          6, #Negligent Manslaughter
          7, #Kidnapping/Abduction
          8, #Human Trafficking-Sex
          9, #Human Trafficking-Labor
          10, #Rape
          11, #Sodomy
          12, #Sexual Assault with an Object
          13, #Fondling
          14, #Sex Offenses, Nonforcible
          15, #NIBRS crimes against property (Total)
          16, #Arson
          17, #Bribery
          18, #Burglary/B&E
          19, #Counterfeiting/Forgery
          20, #Destruction/Damage/Vandalism
          21, #Embezzlement
          22, #Extortion/Blackmail
          23, #Fraud Offenses
          24, #Larceny/Theft Offenses
          25, #Motor Vehicle Theft
          26, #Robbery
          27, #Stolen Property Offenses
          28, #NIBRS crimes against society (Total)
          29, #Revised Rape
          30, #Violent Crime
          31 #Property Crime
        ) &
        row %in% c(
          1 #Arrest count
        ), 1,

      #Secondary row
      trim_upcase(table) == "5A" &
        #Want selected offenses in 5a
        column %in% c(
          1, #NIBRS crimes against persons (Total)
          2, #Aggravated Assault
          3, #Simple Assault
          4, #Intimidation
          5, #Murder and Non-negligent Manslaughter
          6, #Negligent Manslaughter
          7, #Kidnapping/Abduction
          8, #Human Trafficking-Sex
          9, #Human Trafficking-Labor
          10, #Rape
          11, #Sodomy
          12, #Sexual Assault with an Object
          13, #Fondling
          14, #Sex Offenses, Nonforcible
          15, #NIBRS crimes against property (Total)
          16, #Arson
          17, #Bribery
          18, #Burglary/B&E
          19, #Counterfeiting/Forgery
          20, #Destruction/Damage/Vandalism
          21, #Embezzlement
          22, #Extortion/Blackmail
          23, #Fraud Offenses
          24, #Larceny/Theft Offenses
          25, #Motor Vehicle Theft
          26, #Robbery
          27, #Stolen Property Offenses
          28, #NIBRS crimes against society (Total)
          29, #Revised Rape
          30, #Violent Crime
          31 #Property Crime
        ) &
        row %in% c(
          2, #Arrest type: On-view arrest
          3, #Arrest type: Summoned/cited
          4, #Arrest type: Taken into custody
          10, #Arrestee age: 18-24
          11, #Arrestee age: 25-34
          12, #Arrestee age: 35-64
          13, #Arrestee age: 65+
          15, #Arrestee sex: Male
          16, #Arrestee sex: Female
          18, #Arrestee race: White
          19, #Arrestee race: Black
          20, #Arrestee race: American Indian or Alaska Native
          21, #Arrestee race: Asian
          22, #Arrestee race: Native Hawaiian or Other Pacific Islander
          52, #Arrestee armed: No
          53, #Arrestee armed: Yes
          57, #Weapon involved: No
          58 #Weapon involved: Yes
        ), 2

    )
)

#Check the recodes
raw_7 %>%
  checkfunction(der_na_agency_counts, agency_counts)

raw_7 %>%
  filter(estimate == DER_NA_CODE) %>%
  checkfunction(der_estimate_na_code, estimate)

raw_7 %>%
  checkfunction(der_elig_suppression, der_na_agency_counts, der_estimate_na_code)

raw_7 %>% checkfunction(der_main_indicator_tables, full_table)

#Check that the correct rows are selected
raw_7 %>%
  filter(!is.na(der_suppression_level)) %>%
  checkfunction(table, der_suppression_level, row, estimate_domain)

#Check for 5A that the correct offenses are selected
raw_7 %>%
  filter(trim_upper(table) == "5A") %>%
  checkfunction(table, der_suppression_level, column, indicator_name)

#Make sure that when der_na_agency_counts == 1 that the estimate makes sense
raw_7 %>%
  filter(der_na_agency_counts == 1) %>%
  checkfunction(estimate)

raw_7_1 <- raw_7 %>%
  create_variables_suppression2()
 
  #Delete the old objects
  rm(list=ls(pattern= "raw_\\d+$"))
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

#Next need to create each of the momentum rule
raw_8_top <-  raw_8 %>%
  #Filter to the main indicator tables only
  filter(der_main_indicator_tables == 1 & der_suppression_level %in% c(1)) %>%
  #For this program, main difference is to subset to the main permutation 
  filter(PERMUTATION_NUMBER %in% c(1:CONST_MAIN_PERMUTATION_MAX)) %>%
  #Need to use the overall permutation number
  group_by(POPTOTAL_ORIG_PERMUTATION_NUMBER) %>%
  summarise(
  
  # Alt 6
  # RMSE > 0.3 OR {
  # (estimate = 0 OR var(estimate) = 0) AND [
  # (agency type domain or permutation in (state police, other state agencies, tribal, federal) AND cell agency coverage < 80%) OR 
  # (^not that AND cell population coverage < 80%)
  # ]
  # }
  
    der_rrmse_gt_30_se_estimate_0_2_cond_top = sum(der_rrmse_gt_30_se_estimate_0_2_cond == 1 & der_estimate_na_code == 0, na.rm=TRUE) / sum(der_estimate_na_code == 0, na.rm=TRUE)
  
  

  ) %>%
  ungroup()

#Need to output raw_8_top as this contains the percentage of estimates that are suppressed using the momentum rule
#der_rrmse_gt_30_se_estimate_0_2_cond_top is the variable

raw_8_top %>%
  write_rds(paste0(filepathout_Momentum_Rule, "Momemtum_Rule_", PERMUTATION_NAME, ".rds"))

#Delete all the raw files
rm(list=ls(pattern="raw"))
invisible(gc())
