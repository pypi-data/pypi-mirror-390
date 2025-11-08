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
DER_TABLE_NAME = "DM9"
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
        #Total Arrests per Activity
        #Total Arrests per Drug Category
        row == 3, CREATE_PERCENTAGE_DENOMINATOR(c(3:10), column), #Arrestee age: Under 5
        row == 4, CREATE_PERCENTAGE_DENOMINATOR(c(3:10), column), #Arrestee age: 5-14
        row == 5, CREATE_PERCENTAGE_DENOMINATOR(c(3:10), column), #Arrestee age: 15-17
        row == 6, CREATE_PERCENTAGE_DENOMINATOR(c(3:10), column), #Arrestee age: 18-24
        row == 7, CREATE_PERCENTAGE_DENOMINATOR(c(3:10), column), #Arrestee age: 25-34
        row == 8, CREATE_PERCENTAGE_DENOMINATOR(c(3:10), column), #Arrestee age: 35-64
        row == 9, CREATE_PERCENTAGE_DENOMINATOR(c(3:10), column), #Arrestee age: 65+
        row == 10, CREATE_PERCENTAGE_DENOMINATOR(c(3:10), column), #Arrestee age: Unknown
        row == 11, CREATE_PERCENTAGE_DENOMINATOR(c(11:12), column), #Arrestee sex: Male
        row == 12, CREATE_PERCENTAGE_DENOMINATOR(c(11:12), column), #Arrestee sex: Female
        row == 13, CREATE_PERCENTAGE_DENOMINATOR(c(13:18), column), #Arrestee race: White
        row == 14, CREATE_PERCENTAGE_DENOMINATOR(c(13:18), column), #Arrestee race: Black
        row == 15, CREATE_PERCENTAGE_DENOMINATOR(c(13:18), column), #Arrestee race: American Indian or Alaska Native
        row == 16, CREATE_PERCENTAGE_DENOMINATOR(c(13:18), column), #Arrestee race: Asian
        row == 17, CREATE_PERCENTAGE_DENOMINATOR(c(13:18), column), #Arrestee race: Native Hawaiian or Other Pacific Islander
        row == 18, CREATE_PERCENTAGE_DENOMINATOR(c(13:18), column), #Arrestee race: Unknown
        row == 19, CREATE_PERCENTAGE_DENOMINATOR(c(11:12), column), #Arrestee sex and race: Male
        row == 20, CREATE_PERCENTAGE_DENOMINATOR(c(20:25), column), #Arrestee sex and race Male: White
        row == 21, CREATE_PERCENTAGE_DENOMINATOR(c(20:25), column), #Arrestee sex and race Male: Black
        row == 22, CREATE_PERCENTAGE_DENOMINATOR(c(20:25), column), #Arrestee sex and race Male: American Indian or Alaska Native
        row == 23, CREATE_PERCENTAGE_DENOMINATOR(c(20:25), column), #Arrestee sex and race Male: Asian
        row == 24, CREATE_PERCENTAGE_DENOMINATOR(c(20:25), column), #Arrestee sex and race Male: Native Hawaiian or Other Pacific Islander
        row == 25, CREATE_PERCENTAGE_DENOMINATOR(c(20:25), column), #Arrestee sex and race Male: Unknown
        row == 26, CREATE_PERCENTAGE_DENOMINATOR(c(11:12), column), #Arrestee sex and race: Female
        row == 27, CREATE_PERCENTAGE_DENOMINATOR(c(27:32), column), #Arrestee sex and race Female: White
        row == 28, CREATE_PERCENTAGE_DENOMINATOR(c(27:32), column), #Arrestee sex and race Female: Black
        row == 29, CREATE_PERCENTAGE_DENOMINATOR(c(27:32), column), #Arrestee sex and race Female: American Indian or Alaska Native
        row == 30, CREATE_PERCENTAGE_DENOMINATOR(c(27:32), column), #Arrestee sex and race Female: Asian
        row == 31, CREATE_PERCENTAGE_DENOMINATOR(c(27:32), column), #Arrestee sex and race Female: Native Hawaiian or Other Pacific Islander
        row == 32, CREATE_PERCENTAGE_DENOMINATOR(c(27:32), column), #Arrestee sex and race Female: Unknown
        row == 33, CREATE_PERCENTAGE_DENOMINATOR(c(11:12), column), #Arrestee sex and race: Unknown
        row == 34, CREATE_PERCENTAGE_DENOMINATOR(c(34:39), column), #Arrestee sex and race Unknown: White
        row == 35, CREATE_PERCENTAGE_DENOMINATOR(c(34:39), column), #Arrestee sex and race Unknown: Black
        row == 36, CREATE_PERCENTAGE_DENOMINATOR(c(34:39), column), #Arrestee sex and race Unknown: American Indian or Alaska Native
        row == 37, CREATE_PERCENTAGE_DENOMINATOR(c(34:39), column), #Arrestee sex and race Unknown: Asian
        row == 38, CREATE_PERCENTAGE_DENOMINATOR(c(34:39), column), #Arrestee sex and race Unknown: Native Hawaiian or Other Pacific Islander
        row == 39, CREATE_PERCENTAGE_DENOMINATOR(c(34:39), column), #Arrestee sex and race Unknown: Unknown
        row == 40, CREATE_PERCENTAGE_DENOMINATOR(c(40:43), column), #Juvenile disposition: Handled within department
        row == 41, CREATE_PERCENTAGE_DENOMINATOR(c(40:43), column), #Juvenile disposition: Referred to other authorities
        row == 42, CREATE_PERCENTAGE_DENOMINATOR(c(40:43), column), #Juvenile disposition: Not applicable
        row == 43, CREATE_PERCENTAGE_DENOMINATOR(c(40:43), column), #Juvenile disposition: Unknown
        row == 44, CREATE_PERCENTAGE_DENOMINATOR(c(44:46), column), #Multiple arrest indicator: Multiple
        row == 45, CREATE_PERCENTAGE_DENOMINATOR(c(44:46), column), #Multiple arrest indicator: Count
        row == 46, CREATE_PERCENTAGE_DENOMINATOR(c(44:46), column), #Multiple arrest indicator: Not applicable
        row == 47, CREATE_PERCENTAGE_DENOMINATOR(c(47:48), column), #Arrestee armed: No
        row == 48, CREATE_PERCENTAGE_DENOMINATOR(c(47:48), column), #Arrestee armed: Yes
        #Total: Total
        row == 50, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Arrestee age 2: Under 12
        row == 51, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Arrestee age 2: 12-17
        row == 52, CREATE_PERCENTAGE_DENOMINATOR(c(51), column), #Arrestee age 2: 12-14
        row == 53, CREATE_PERCENTAGE_DENOMINATOR(c(51), column), #Arrestee age 2: 15-17
        row == 54, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Arrestee age 2: 18+
        row == 55, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Arrestee age 2: Unknown
        
        row == 56, CREATE_PERCENTAGE_DENOMINATOR(c(56:58), column), #Arrestee Hispanic Origin: Hispanic or Latino
        row == 57, CREATE_PERCENTAGE_DENOMINATOR(c(56:58), column), #Arrestee Hispanic Origin: Not Hispanic or Latino
        row == 58, CREATE_PERCENTAGE_DENOMINATOR(c(56:58), column), #Arrestee Hispanic Origin: Unknown
        row == 59, CREATE_PERCENTAGE_DENOMINATOR(c(59:65), column), #Arrestee race and Hispanic Origin: Hispanic or Latino
        row == 60, CREATE_PERCENTAGE_DENOMINATOR(c(59:65), column), #Arrestee race and Hispanic Origin: Non-Hispanic, White
        row == 61, CREATE_PERCENTAGE_DENOMINATOR(c(59:65), column), #Arrestee race and Hispanic Origin: Non-Hispanic, Black
        row == 62, CREATE_PERCENTAGE_DENOMINATOR(c(59:65), column), #Arrestee race and Hispanic Origin: Non-Hispanic, American Indian or Alaska Native
        row == 63, CREATE_PERCENTAGE_DENOMINATOR(c(59:65), column), #Arrestee race and Hispanic Origin: Non-Hispanic, Asian
        row == 64, CREATE_PERCENTAGE_DENOMINATOR(c(59:65), column), #Arrestee race and Hispanic Origin: Non-Hispanic, Native Hawaiian or Other Pacific Islander
        row == 65, CREATE_PERCENTAGE_DENOMINATOR(c(59:65), column) #Arrestee race and Hispanic Origin: Unknown race or Hispanic origin
        
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
