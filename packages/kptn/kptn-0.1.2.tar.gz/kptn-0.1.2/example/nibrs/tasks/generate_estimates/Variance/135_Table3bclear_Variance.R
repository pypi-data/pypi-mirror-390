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

if (DER_CURRENT_PERMUTATION_NUM==""){
   simpleError("Set DER_CURRENT_PERMUTATION_NUM as enviroment variable")
 }
 DER_CURRENT_PERMUTATION_NUM <- as.integer(Sys.getenv("DER_CURRENT_PERMUTATION_NUM"))


#source("../POP_Total_code_assignment.R")
read_csv_main <- partial(read_csv, guess_max = 10) #For now, read thru the 1st 10 rows to determine variable type
read_csv <- partial(read_csv, guess_max = 1000000) #For now, read thru the 1st 1,000,000 rows to determine variable type
write.csv0 <- partial(write.csv, row.names = FALSE, na ="0")
write.csv <- partial(write.csv, row.names = FALSE, na ="")


##########################Set the variables for table #######################
DER_TABLE_NAME = "3bclear"
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
        #Victimization count
        #Victimization count: Law enforcement officers 
        #Victimization rate (per 100k total pop)
        #Victimization rate (per 100k LE staff): Law enforcement officers
        row == 5, CREATE_PERCENTAGE_DENOMINATOR(c(5:14), column), #Age-specific victimization rate: Under 5
        row == 6, CREATE_PERCENTAGE_DENOMINATOR(c(5:14), column), #Age-specific victimization rate: 5-14
        row == 7, CREATE_PERCENTAGE_DENOMINATOR(c(5:14), column), #Age-specific victimization rate: 15
        row == 8, CREATE_PERCENTAGE_DENOMINATOR(c(5:14), column), #Age-specific victimization rate: 16
        row == 9, CREATE_PERCENTAGE_DENOMINATOR(c(5:14), column), #Age-specific victimization rate: 17
        row == 10, CREATE_PERCENTAGE_DENOMINATOR(c(5:14), column), #Age-specific victimization rate: 18-24
        row == 11, CREATE_PERCENTAGE_DENOMINATOR(c(5:14), column), #Age-specific victimization rate: 25-34
        row == 12, CREATE_PERCENTAGE_DENOMINATOR(c(5:14), column), #Age-specific victimization rate: 35-64
        row == 13, CREATE_PERCENTAGE_DENOMINATOR(c(5:14), column), #Age-specific victimization rate: 65+
        row == 14, CREATE_PERCENTAGE_DENOMINATOR(c(5:14), column), #Age-specific victimization rate: Unknown
        row == 15, CREATE_PERCENTAGE_DENOMINATOR(c(15:17), column), #Sex-specific victimization rate: Male
        row == 16, CREATE_PERCENTAGE_DENOMINATOR(c(15:17), column), #Sex-specific victimization rate: Female
        row == 17, CREATE_PERCENTAGE_DENOMINATOR(c(15:17), column), #Sex-specific victimization rate: Unknown
        row == 18, CREATE_PERCENTAGE_DENOMINATOR(c(18:23), column), #Race-specific victimization rate: White
        row == 19, CREATE_PERCENTAGE_DENOMINATOR(c(18:23), column), #Race-specific victimization rate: Black
        row == 20, CREATE_PERCENTAGE_DENOMINATOR(c(18:23), column), #Race-specific victimization rate: American Indian or Alaska Native
        row == 21, CREATE_PERCENTAGE_DENOMINATOR(c(18:23), column), #Race-specific victimization rate: Asian
        row == 22, CREATE_PERCENTAGE_DENOMINATOR(c(18:23), column), #Race-specific victimization rate: Native Hawaiian or Other Pacific Islander
        row == 23, CREATE_PERCENTAGE_DENOMINATOR(c(18:23), column), #Race-specific victimization rate: Unknown
        row == 24, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Victim Age 2: Under 12
        row == 25, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Victim Age 2: 12-17
        row == 26, CREATE_PERCENTAGE_DENOMINATOR(c(25), column), #Victim Age 2: 12-14
        row == 27, CREATE_PERCENTAGE_DENOMINATOR(c(25), column), #Victim Age 2: 15-17
        row == 28, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Victim Age 2: 18+
        row == 29, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Victim Age 2: Unknown
        row == 30, CREATE_PERCENTAGE_DENOMINATOR(c(30:31), column), #Weapon involved: No
        row == 31, CREATE_PERCENTAGE_DENOMINATOR(c(30:31), column), #Weapon involved: Yes
        row == 32, CREATE_PERCENTAGE_DENOMINATOR(c(31), column), #Weapon involved: Personal weapons
        row == 33, CREATE_PERCENTAGE_DENOMINATOR(c(31), column), #Weapon involved: Firearms
        row == 34, CREATE_PERCENTAGE_DENOMINATOR(c(31), column), #Weapon involved: Knives and other cutting instruments
        row == 35, CREATE_PERCENTAGE_DENOMINATOR(c(31), column), #Weapon involved: Blunt instruments
        row == 36, CREATE_PERCENTAGE_DENOMINATOR(c(31), column), #Weapon involved: Other non-personal weapons
        row == 37, CREATE_PERCENTAGE_DENOMINATOR(c(31), column), #Weapon involved: Unknown
        row == 38, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Victim-offender relationship: Intimate partner
        row == 39, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Victim-offender relationship: Other family
        row == 40, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Victim-offender relationship: Outside family but known to victim
        row == 41, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Victim-offender relationship: Stranger
        row == 42, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Victim-offender relationship: Victim was Offender
        row == 43, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Victim-offender relationship: Unknown relationship
		row == 44, CREATE_PERCENTAGE_DENOMINATOR(c(44:61), column), #Weapon involved hierarchy: Handgun
		row == 45, CREATE_PERCENTAGE_DENOMINATOR(c(44:61), column), #Weapon involved hierarchy: Firearm
		row == 46, CREATE_PERCENTAGE_DENOMINATOR(c(44:61), column), #Weapon involved hierarchy: Rifle
		row == 47, CREATE_PERCENTAGE_DENOMINATOR(c(44:61), column), #Weapon involved hierarchy: Shotgun
		row == 48, CREATE_PERCENTAGE_DENOMINATOR(c(44:61), column), #Weapon involved hierarchy: Other Firearm
		row == 49, CREATE_PERCENTAGE_DENOMINATOR(c(44:61), column), #Weapon involved hierarchy: Knife/Cutting Instrument
		row == 50, CREATE_PERCENTAGE_DENOMINATOR(c(44:61), column), #Weapon involved hierarchy: Blunt Object
		row == 51, CREATE_PERCENTAGE_DENOMINATOR(c(44:61), column), #Weapon involved hierarchy: Motor Vehicle
		row == 52, CREATE_PERCENTAGE_DENOMINATOR(c(44:61), column), #Weapon involved hierarchy: Personal Weapons (hands, feet, teeth, etc.)
		row == 53, CREATE_PERCENTAGE_DENOMINATOR(c(44:61), column), #Weapon involved hierarchy: Asphyxiation
		row == 54, CREATE_PERCENTAGE_DENOMINATOR(c(44:61), column), #Weapon involved hierarchy: Drugs/Narcotics/Sleeping Pills
		row == 55, CREATE_PERCENTAGE_DENOMINATOR(c(44:61), column), #Weapon involved hierarchy: Poison (include gas)
		row == 56, CREATE_PERCENTAGE_DENOMINATOR(c(44:61), column), #Weapon involved hierarchy: Explosives
		row == 57, CREATE_PERCENTAGE_DENOMINATOR(c(44:61), column), #Weapon involved hierarchy: Fire/Incendiary Device
		row == 58, CREATE_PERCENTAGE_DENOMINATOR(c(44:61), column), #Weapon involved hierarchy: Other
		row == 59, CREATE_PERCENTAGE_DENOMINATOR(c(44:61), column), #Weapon involved hierarchy: No Weapon
		row == 60, CREATE_PERCENTAGE_DENOMINATOR(c(44:61), column), #Weapon involved hierarchy: Unknown
		row == 61, CREATE_PERCENTAGE_DENOMINATOR(c(44:61), column), #Weapon involved hierarchy: Not Applicable
		row == 62, CREATE_PERCENTAGE_DENOMINATOR(c(62:69), column), #Victim-offender relationship hierarchy: Intimate partner
		row == 63, CREATE_PERCENTAGE_DENOMINATOR(c(62:69), column), #Victim-offender relationship hierarchy: Other family
		row == 64, CREATE_PERCENTAGE_DENOMINATOR(c(62:69), column), #Victim-offender relationship hierarchy: Outside family but known to victim
		row == 65, CREATE_PERCENTAGE_DENOMINATOR(c(62:69), column), #Victim-offender relationship hierarchy: Stranger
		row == 66, CREATE_PERCENTAGE_DENOMINATOR(c(62:69), column), #Victim-offender relationship hierarchy: Victim was Offender
		row == 67, CREATE_PERCENTAGE_DENOMINATOR(c(62:69), column), #Victim-offender relationship hierarchy: Unknown relationship
		row == 68, CREATE_PERCENTAGE_DENOMINATOR(c(62:69), column), #Victim-offender relationship hierarchy: Unknown Offender Incidents
		row == 69, CREATE_PERCENTAGE_DENOMINATOR(c(62:69), column), #Victim-offender relationship hierarchy: Missing from Uncleared Incidents		
		
		row == 70, CREATE_PERCENTAGE_DENOMINATOR(c(70:72), column), #Hispanic Origin-specific victimization rate: Hispanic or Latino
		row == 71, CREATE_PERCENTAGE_DENOMINATOR(c(70:72), column), #Hispanic Origin-specific victimization rate: Not Hispanic or Latino
		row == 72, CREATE_PERCENTAGE_DENOMINATOR(c(70:72), column), #Hispanic Origin-specific victimization rate: Unknown
		row == 73, CREATE_PERCENTAGE_DENOMINATOR(c(73:79), column), #Race and Hispanic Origin-specific victimization rate: Hispanic or Latino
		row == 74, CREATE_PERCENTAGE_DENOMINATOR(c(73:79), column), #Race and Hispanic Origin-specific victimization rate: Non-Hispanic, White
		row == 75, CREATE_PERCENTAGE_DENOMINATOR(c(73:79), column), #Race and Hispanic Origin-specific victimization rate: Non-Hispanic, Black
		row == 76, CREATE_PERCENTAGE_DENOMINATOR(c(73:79), column), #Race and Hispanic Origin-specific victimization rate: Non-Hispanic, American Indian or Alaska Native
		row == 77, CREATE_PERCENTAGE_DENOMINATOR(c(73:79), column), #Race and Hispanic Origin-specific victimization rate: Non-Hispanic, Asian
		row == 78, CREATE_PERCENTAGE_DENOMINATOR(c(73:79), column), #Race and Hispanic Origin-specific victimization rate: Non-Hispanic, Native Hawaiian or Other Pacific Islander
		row == 79, CREATE_PERCENTAGE_DENOMINATOR(c(73:79), column) #Race and Hispanic Origin-specific victimization rate: Unknown race or Hispanic origin
		
		
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

  raw_main <- process_single_ori_tables(intable=DER_TABLE_NAME, 
                                        inpermutation=DER_CURRENT_PERMUTATION_NUM, 
                                        infilepath=final_path) %>%
    process_permutation_series(IN_DER_CURRENT_PERMUTATION_NUM=DER_CURRENT_PERMUTATION_NUM)  

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
    mutate(der_cleared_cells = case_when(TRUE ~ 0))
  ######################################################################################################################


  ############Drop any rows that are not in the final indicator tables (i.e. all 0 rows by design)#####################
  der_drop_rows <- c(NA)
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

  #Create new object
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
