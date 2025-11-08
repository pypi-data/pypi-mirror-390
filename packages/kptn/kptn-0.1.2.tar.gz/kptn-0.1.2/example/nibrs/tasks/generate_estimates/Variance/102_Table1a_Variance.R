#install.packages("RPostgres")
#install.packages("dbplyr")

library(tidyverse)
#library(xlsx)
library(openxlsx)
library(DBI)
library(DT)
library(lubridate)
#library(dplyr)
#library(dbplyr)
#library(rlang)
library(ReGenesees)
library(survey)

#Read in the common functions to be used in R
#source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))

# if (DER_CURRENT_PERMUTATION_NUM==""){
#   simpleError("Set DER_CURRENT_PERMUTATION_NUM as enviroment variable")
#   DER_CURRENT_PERMUTATION_NUM <- Sys.getenv("DER_CURRENT_PERMUTATION_NUM")
# }

#source("../POP_Total_code_assignment.R")
read_csv_main <- partial(read_csv, guess_max = 10) #For now, read thru the 1st 10 rows to determine variable type
read_csv <- partial(read_csv, guess_max = 1000000) #For now, read thru the 1st 1,000,000 rows to determine variable type
write.csv0 <- partial(write.csv, row.names = FALSE, na ="0")
write.csv <- partial(write.csv, row.names = FALSE, na ="")


##########################Set the variables for table #######################
DER_TABLE_NAME = "1a"
#############################################################################

set_denominator_column <- function (raw_percentage_3, main_reporting_db3) {
  # The code below loops over every row in raw_percentage_3
  # It creates a new column on it, raw_denominator, containing the list of variables to use as the denominator
  # That list of variables is pulled from the requested row, column, and other filtering of the main_reporting_db3 table
  if(nrow(raw_percentage_3) > 0) {
    raw_percentage_3_dt <- as.data.table(raw_percentage_3)
    main_reporting_db3 <- as.data.table(main_reporting_db3)
    CREATE_PERCENTAGE_DENOMINATOR <- CREATE_PERCENTAGE_DENOMINATOR_init(main_reporting_db3)
    raw_percentage_3_dt[,
      raw_denominator := fcase(
        row == 3, CREATE_PERCENTAGE_DENOMINATOR(c(3:4), column), #Weapon involved: No
        row == 4, CREATE_PERCENTAGE_DENOMINATOR(c(3:4), column), #Weapon involved: Yes
        row == 5, CREATE_PERCENTAGE_DENOMINATOR(c(4), column), #Weapon involved: Personal weapons
        row == 6, CREATE_PERCENTAGE_DENOMINATOR(c(4), column), #Weapon involved: Firearms
        row == 7, CREATE_PERCENTAGE_DENOMINATOR(c(4), column), #Weapon involved: Knives and other cutting instruments
        row == 8, CREATE_PERCENTAGE_DENOMINATOR(c(4), column), #Weapon involved: Blunt instruments
        row == 9, CREATE_PERCENTAGE_DENOMINATOR(c(4), column), #Weapon involved: Other non-personal weapons
        row == 10, CREATE_PERCENTAGE_DENOMINATOR(c(4), column), #Weapon involved: Unknown
        row == 11, CREATE_PERCENTAGE_DENOMINATOR(c(11:12), column), #Injury: No
        row == 12, CREATE_PERCENTAGE_DENOMINATOR(c(11:12), column), #Injury: Yes
        row == 13, CREATE_PERCENTAGE_DENOMINATOR(c(13:14), column), #Multiple victims: 1 victim
        row == 14, CREATE_PERCENTAGE_DENOMINATOR(c(13:14), column), #Multiple victims: 2+ victims
        row == 15, CREATE_PERCENTAGE_DENOMINATOR(c(15:17), column), #Multiple offenders: 1 offender
        row == 16, CREATE_PERCENTAGE_DENOMINATOR(c(15:17), column), #Multiple offenders: 2+ offenders
        row == 17, CREATE_PERCENTAGE_DENOMINATOR(c(15:17), column), #Multiple offenders: Unknown offenders
        row == 18, CREATE_PERCENTAGE_DENOMINATOR(c(18:20), column), #Multiple offense incident: 1 offense
        row == 19, CREATE_PERCENTAGE_DENOMINATOR(c(18:20), column), #Multiple offense incident: 2 offenses
        row == 20, CREATE_PERCENTAGE_DENOMINATOR(c(18:20), column), #Multiple offense incident: 3+ offenses
        row == 21, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Victim-offender relationship: Intimate partner
        row == 22, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Victim-offender relationship: Other family
        row == 23, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Victim-offender relationship: Outside family but known to victim
        row == 24, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Victim-offender relationship: Stranger
        row == 25, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Victim-offender relationship: Victim was Offender
        row == 26, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Victim-offender relationship: Unknown relationship
        row == 27, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Location type: Residence/hotel
        row == 28, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Location type: Transportation hub/outdoor public locations
        row == 29, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Location type: Schools, daycares, and universities
        row == 30, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Location type: Retail/financial/other commercial establishment
        row == 31, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Location type: Restaurant/bar/sports or entertainment venue
        row == 32, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Location type: Religious buildings
        row == 33, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Location type: Government/public buildings
        row == 34, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Location type: Jail/prison
        row == 35, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Location type: Shelter-mission/homeless
        row == 36, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Location type: Other/unknown location
        row == 37, CREATE_PERCENTAGE_DENOMINATOR(c(37:43), column), #Time of day- Incident time: Midnight-4am
        row == 38, CREATE_PERCENTAGE_DENOMINATOR(c(37:43), column), #Time of day- Incident time: 4-8am
        row == 39, CREATE_PERCENTAGE_DENOMINATOR(c(37:43), column), #Time of day- Incident time: 8am-noon
        row == 40, CREATE_PERCENTAGE_DENOMINATOR(c(37:43), column), #Time of day- Incident time: Noon-4pm
        row == 41, CREATE_PERCENTAGE_DENOMINATOR(c(37:43), column), #Time of day- Incident time: 4-8pm
        row == 42, CREATE_PERCENTAGE_DENOMINATOR(c(37:43), column), #Time of day- Incident time: 8pm-midnight
        row == 43, CREATE_PERCENTAGE_DENOMINATOR(c(37:43), column), #Time of day- Incident time: Unknown
        row == 44, CREATE_PERCENTAGE_DENOMINATOR(c(44:50), column), #Time of day- Report time: Midnight-4am
        row == 45, CREATE_PERCENTAGE_DENOMINATOR(c(44:50), column), #Time of day- Report time: 4-8am
        row == 46, CREATE_PERCENTAGE_DENOMINATOR(c(44:50), column), #Time of day- Report time: 8am-noon
        row == 47, CREATE_PERCENTAGE_DENOMINATOR(c(44:50), column), #Time of day- Report time: Noon-4pm
        row == 48, CREATE_PERCENTAGE_DENOMINATOR(c(44:50), column), #Time of day- Report time: 4-8pm
        row == 49, CREATE_PERCENTAGE_DENOMINATOR(c(44:50), column), #Time of day- Report time: 8pm-midnight
        row == 50, CREATE_PERCENTAGE_DENOMINATOR(c(44:50), column), #Time of day- Report time: Unknown
        row == 51, CREATE_PERCENTAGE_DENOMINATOR(c(51:55), column), #Population group: Cities and counties 100,000 or over
        row == 52, CREATE_PERCENTAGE_DENOMINATOR(c(51:55), column), #Population group: Cities and counties 25,000-99,999
        row == 53, CREATE_PERCENTAGE_DENOMINATOR(c(51:55), column), #Population group: Cities and counties 10,000-24,999
        row == 54, CREATE_PERCENTAGE_DENOMINATOR(c(51:55), column), #Population group: Cities and counties under 10,000
        row == 55, CREATE_PERCENTAGE_DENOMINATOR(c(51:55), column), #Population group: State police
        #Population group: Possessions and Canal Zone
        row == 57, CREATE_PERCENTAGE_DENOMINATOR(c(57:62), column), #Agency indicator: City
        row == 58, CREATE_PERCENTAGE_DENOMINATOR(c(57:62), column), #Agency indicator: County
        row == 59, CREATE_PERCENTAGE_DENOMINATOR(c(57:62), column), #Agency indicator: University or college
        row == 60, CREATE_PERCENTAGE_DENOMINATOR(c(57:62), column), #Agency indicator: State police
        row == 61, CREATE_PERCENTAGE_DENOMINATOR(c(57:62), column), #Agency indicator: Other state agencies
        row == 62, CREATE_PERCENTAGE_DENOMINATOR(c(57:62), column), #Agency indicator: Tribal agencies
        #Agency indicator: Federal agencies
        row == 64, CREATE_PERCENTAGE_DENOMINATOR(c(64:66), column), #Clearance: Not cleared
        row == 65, CREATE_PERCENTAGE_DENOMINATOR(c(64:66), column), #Clearance: Cleared through arrest
        row == 66, CREATE_PERCENTAGE_DENOMINATOR(c(64:66), column), #Clearance: Exceptional clearance
        row == 67, CREATE_PERCENTAGE_DENOMINATOR(c(67:71), column), #Clearance: Death of offender
        row == 68, CREATE_PERCENTAGE_DENOMINATOR(c(67:71), column), #Clearance: Prosecution declined
        row == 69, CREATE_PERCENTAGE_DENOMINATOR(c(67:71), column), #Clearance: In custody of other jurisdiction
        row == 70, CREATE_PERCENTAGE_DENOMINATOR(c(67:71), column), #Clearance: Victim refused to cooperate
        row == 71, CREATE_PERCENTAGE_DENOMINATOR(c(67:71), column), #Clearance: Juvenile/no custody
        row == 72, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Property loss: None
        row == 73, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Property loss: Burned
        row == 74, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Property loss: Counterfeited/forged
        row == 75, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Property loss: Destroyed/damaged/vandalized
        row == 76, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Property loss: Recovered
        row == 77, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Property loss: Seized
        row == 78, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Property loss: Stolen/Et
        row == 79, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Property loss: Unknown
        row == 80, CREATE_PERCENTAGE_DENOMINATOR(c(80:83), column), #MSA: MSA Counties
        row == 81, CREATE_PERCENTAGE_DENOMINATOR(c(80:83), column), #MSA: Outside MSA
        row == 82, CREATE_PERCENTAGE_DENOMINATOR(c(80:83), column), #MSA: Non-MSA Counties
        row == 83, CREATE_PERCENTAGE_DENOMINATOR(c(80:83), column), #MSA: Missing
        row == 84, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Location type 2: Residence/hotel
        row == 85, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Location type 2: Transportation hub/outdoor public locations
        row == 86, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Location type 2: Schools, daycares, and universities
        row == 87, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Location type 2: Retail/financial/other commercial establishment
        row == 88, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Location type 2: Restaurant/bar/sports or entertainment venue
        row == 89, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Location type 2: Religious buildings
        row == 90, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Location type 2: Government/public buildings
        row == 91, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Location type 2: Jail/prison
        row == 92, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Location type 2: Shelter-mission/homeless
        row == 93, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Location type 2: Drug Store/Doctor Office/Hospital
        row == 94, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Location type 2: Other/unknown location
        row == 95, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Victim-offender relationship 2: Intimate partner plus Family
        row == 96, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Victim-offender relationship 2: Outside family but known to victim
        row == 97, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Victim-offender relationship 2: Stranger
        row == 98, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Victim-offender relationship 2: Victim was Offender
        row == 99, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Victim-offender relationship 2: Unknown relationship
		
		row == 100, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Location type 3: Residence
		row == 101, CREATE_PERCENTAGE_DENOMINATOR(c(1), column) #Location type 3: Not residence
		
      ),
      by = seq_len(nrow(raw_percentage_3_dt))
    ]
    # Convert back to tibble for now (keeping in data.table would be better)
    return(tibble::as_tibble(raw_percentage_3_dt))
  } else {
    return(tibble::as_tibble(raw_percentage_3))
  }
}


run_main <- function(){

  log_debug("Program Start")
  #Read in the main datasets to be used for the table
  raw_main <- fread_logging(paste0(final_path, "Table ", DER_TABLE_NAME, " ORI.csv.gz"))
  log_debug("Read in ORI file")
  main_reporting_db <- read_csv(file=paste0(final_path, "Table ", DER_TABLE_NAME, "_Reporting_Database.csv")) %>%
    POPUALATION_VARIABLE_FUNCTION()
  log_debug("Read in reporting DB")

  #Merge on the information from the weight dataset
  main <- merge_on_weights_variance(raw_main)

  log_dim(raw_main)
  log_dim(main) 

  #Check to see if the weight variable from the ORI level dataset for variance has the same amount of records as raw_main
  main %>%
    mutate(check_merge = case_when(!is.na(weight) ~ 1,
                                  TRUE ~ 0)) %>%
    checkfunction(check_merge)
  log_dim(raw_main)

  #Delete raw_main
  rm(raw_main)
  invisible(gc())


  #Read in the Percent Relative Bias file
  main_prb <- readRDS(paste0(input_copula_prb_folder, "/Relative_Bias_Estimates_", DER_TABLE_NAME, "_", DER_CURRENT_PERMUTATION_NUM, ".rds"))


  #Get the variables we want to do the variances on
  der_variables_variance <- main %>%
    create_table_variables() %>%
  ################Filter any variables not needed###################################################################
    mutate(der_cleared_cells = case_when(
      
  (
  column == 5 | #~ 'Murder and Non-negligent Manslaughter',
  column == 6 #~ 'Negligent Manslaughter',
  ) & (
  row == 11 |# ~ 'Injury: No',
  row == 12  # ~ 'Injury: Yes',
  ) ~ 1,

  (
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
  column == 17 |  # 'Violent Crime',
  column == 18    # 'Car Jacking',


  ) & (
  row == 72 | # 'Property loss: None',
  row == 73 | # 'Property loss: Burned',
  row == 74 | # 'Property loss: Counterfeited/forged',
  row == 75 | # 'Property loss: Destroyed/damaged/vandalized',
  row == 76 | # 'Property loss: Recovered',
  row == 77 | # 'Property loss: Seized',
  row == 78 | # 'Property loss: Stolen/Et',
  row == 79  # 'Property loss: Unknown',


  ) ~ 1,
  TRUE ~ 0))
  ######################################################################################################################


  ############Drop any rows that are not in the final indicator tables (i.e. all 0 rows by design)#####################
  der_drop_rows <- c(
    56,	#Population group	  Possessions and Canal Zone
    63	#Agency indicator	  Federal agencies
  )
  ######################################################################################################################
  #From reporting database drop any row
  main_reporting_db2 <- main_reporting_db %>%
    drop_rows_from_table(der_drop_rows)

  log_dim(main_reporting_db)
  log_dim(main_reporting_db2)

  #From any variables drop any row variables
  der_variables_variance2 <- der_variables_variance  %>%
    drop_rows_from_table(der_drop_rows)

  log_dim(der_variables_variance)
  log_dim(der_variables_variance2)

  #Clean up the database by making the cells in der_cleared_cells to have the DER_NA_CODE
  main_reporting_db3 <- main_reporting_db2 %>%
    left_join(der_variables_variance2, by=c("table", "section", "row", "column")) %>%
    clear_cells_from_table()

  #Need to get the variables for processing
  der_list_of_variables_variance <- der_variables_variance2 %>%
    #Keep variables identified for variance estimation
    filter(der_cleared_cells == 0) %>%
    select(variable_name) %>%
    pull()

  #See the list of variables
  print(der_list_of_variables_variance)

  #Remove objects
  rm(der_variables_variance, der_variables_variance2,
    main_reporting_db, main_reporting_db2)

  invisible(gc())

  #########################Calculate the Total Standard error

  #Need to split out the variables to loop thru 100 at a time to prevent an error message
  der_list_of_variables_variance_total_list <- der_list_of_variables_variance %>%
    as_tibble() %>%
    #Rename value to variable
    rename(variable = value) %>%
    #Assign a row to each variable
    mutate(row = row_number()) %>%
    #Get the quotient to split up processing by 500
    mutate(row_split = row %/% 500) %>%
    #Split by row_split to create a list 
    split(.$row_split) 

  #Use map to create a list object to hold results
  der_list_TOTAL_SE <- map(der_list_of_variables_variance_total_list, ~ {
    #Create a formula for processing
    der_list_of_variables_variance_formula <- paste("~",paste(.x$variable %>% unlist(),collapse="+")) %>% as.formula()                    
    #Call the function
    returndata <- TOTAL_SE_FUNCTION(indata=main, invar=der_list_of_variables_variance_formula, inmainprb=main_prb)
              
    #Return the data
    return(returndata)
  })

  #Combined the results
  final_TOTAL_SE <- bind_rows(der_list_TOTAL_SE)

  #Remove objects
  rm(der_list_TOTAL_SE, der_list_of_variables_variance_total_list)
  invisible(gc())
  #######################Calculate the Rate
  #Using main_reporting_db3 - Identify the cells where estimate_type_detail_rate is not missing or have the DER_NA_CODE


  final_RATE_SE <- RATE_SE_FUNCTION(indatabase=main_reporting_db3, intotalse=final_TOTAL_SE, inmainprb=main_prb) %>%
    select(table, section, row, column, estimate_type_num, 
          estimate_standard_error, estimate_prb, estimate_bias, estimate_rmse,
          estimate_upper_bound, estimate_lower_bound, 
          relative_standard_error, relative_rmse, !!DER_PRB_VARIABLE_IND_SYMBOL,
          tbd_estimate, estimate_unweighted, population_estimate_unweighted)
  #######################Calculate the Percentages standard error
  #der_list_of_variables_variance is the list of variables that needs to do the variance estimation

  #Need to filter out the DER_NA_CODE to not do percentages
  raw_percentage_1 <- der_list_of_variables_variance %>%
    as_tibble() %>%
    rename(raw_variable = value) %>%
    #Create the additional variables
      mutate(variable = str_match(string=raw_variable, pattern=DER_TABLE_PATTERN_STRING)[,1],
            table   = str_match(string=raw_variable, pattern=DER_TABLE_PATTERN_STRING)[,2],
            section = str_match(string=raw_variable, pattern=DER_TABLE_PATTERN_STRING)[,3] %>% as.numeric(),
            row     = str_match(string=raw_variable, pattern=DER_TABLE_PATTERN_STRING)[,4] %>% as.numeric(),
            column  = str_match(string=raw_variable, pattern=DER_TABLE_PATTERN_STRING)[,5] %>% as.numeric())

  #Identify the variables to not do percentages
  raw_percentage_drop <- main_reporting_db3 %>%
      #Filter to percentages and DER_NA_CODE
      filter(estimate_type_num == 2 & estimate == DER_NA_CODE) %>%
      select(variable_name)

  #raw_percentage_2 contains the variables that are not the DER_NA_CODE for percentages
  raw_percentage_2 <- raw_percentage_1 %>%
    anti_join(raw_percentage_drop, by=c("variable"="variable_name"))

  #Note we already drop some variables from the cleaning above, so the totals will not add up
  log_dim(raw_percentage_1)
  log_dim(raw_percentage_2)
  log_dim(raw_percentage_drop)
                                
    
  ##################################Edit code for each table on how to define the denominator #########################  

  raw_percentage_3 <- set_denominator_column(raw_percentage_2, main_reporting_db3)

  ##################################################################################################################### 

  final_processing(
    raw_percentage_3,
    main,
    main_prb,
    main_reporting_db3,
    final_TOTAL_SE,
    der_list_of_variables_variance,
    final_RATE_SE,
    final_path_after_variance,
    DER_TABLE_NAME,
    DER_CURRENT_PERMUTATION_NUM
  )
}