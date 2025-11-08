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
DER_TABLE_NAME = "DM5"
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
        #Total
        row == 2, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Cocaine/crack cocaine (A, B): Buying/receiving
        row == 3, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Cocaine/crack cocaine (A, B): Cultivating/manufacturing/publishing
        row == 4, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Cocaine/crack cocaine (A, B): Distributing/selling
        row == 5, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Cocaine/crack cocaine (A, B): Exploiting children
        row == 6, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Cocaine/crack cocaine (A, B): Operating/promoting/assisting
        row == 7, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Cocaine/crack cocaine (A, B): Possessing/concealing
        row == 8, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Cocaine/crack cocaine (A, B): Transporting/transmitting/importing
        row == 9, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Cocaine/crack cocaine (A, B): Using/consuming
        row == 10, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Marijuana/hashish (C, E): Buying/receiving
        row == 11, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Marijuana/hashish (C, E): Cultivating/manufacturing/publishing
        row == 12, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Marijuana/hashish (C, E): Distributing/selling
        row == 13, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Marijuana/hashish (C, E): Exploiting children
        row == 14, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Marijuana/hashish (C, E): Operating/promoting/assisting
        row == 15, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Marijuana/hashish (C, E): Possessing/concealing
        row == 16, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Marijuana/hashish (C, E): Transporting/transmitting/importing
        row == 17, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Marijuana/hashish (C, E): Using/consuming
        row == 18, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Opiate/narcotic (D, F, G, H): Buying/receiving
        row == 19, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Opiate/narcotic (D, F, G, H): Cultivating/manufacturing/publishing
        row == 20, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Opiate/narcotic (D, F, G, H): Distributing/selling
        row == 21, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Opiate/narcotic (D, F, G, H): Exploiting children
        row == 22, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Opiate/narcotic (D, F, G, H): Operating/promoting/assisting
        row == 23, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Opiate/narcotic (D, F, G, H): Possessing/concealing
        row == 24, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Opiate/narcotic (D, F, G, H): Transporting/transmitting/importing
        row == 25, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Opiate/narcotic (D, F, G, H): Using/consuming
        row == 26, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Hallucinogen (I, J, K): Buying/receiving
        row == 27, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Hallucinogen (I, J, K): Cultivating/manufacturing/publishing
        row == 28, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Hallucinogen (I, J, K): Distributing/selling
        row == 29, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Hallucinogen (I, J, K): Exploiting children
        row == 30, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Hallucinogen (I, J, K): Operating/promoting/assisting
        row == 31, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Hallucinogen (I, J, K): Possessing/concealing
        row == 32, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Hallucinogen (I, J, K): Transporting/transmitting/importing
        row == 33, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Hallucinogen (I, J, K): Using/consuming
        row == 34, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Stimulant (L, M): Buying/receiving
        row == 35, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Stimulant (L, M): Cultivating/manufacturing/publishing
        row == 36, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Stimulant (L, M): Distributing/selling
        row == 37, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Stimulant (L, M): Exploiting children
        row == 38, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Stimulant (L, M): Operating/promoting/assisting
        row == 39, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Stimulant (L, M): Possessing/concealing
        row == 40, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Stimulant (L, M): Transporting/transmitting/importing
        row == 41, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Stimulant (L, M): Using/consuming
        row == 42, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Depressant (N, O): Buying/receiving
        row == 43, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Depressant (N, O): Cultivating/manufacturing/publishing
        row == 44, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Depressant (N, O): Distributing/selling
        row == 45, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Depressant (N, O): Exploiting children
        row == 46, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Depressant (N, O): Operating/promoting/assisting
        row == 47, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Depressant (N, O): Possessing/concealing
        row == 48, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Depressant (N, O): Transporting/transmitting/importing
        row == 49, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Depressant (N, O): Using/consuming
        row == 50, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Other (P): Buying/receiving
        row == 51, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Other (P): Cultivating/manufacturing/publishing
        row == 52, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Other (P): Distributing/selling
        row == 53, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Other (P): Exploiting children
        row == 54, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Other (P): Operating/promoting/assisting
        row == 55, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Other (P): Possessing/concealing
        row == 56, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Other (P): Transporting/transmitting/importing
        row == 57, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Other (P): Using/consuming
        row == 58, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Unknown (U): Buying/receiving
        row == 59, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Unknown (U): Cultivating/manufacturing/publishing
        row == 60, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Unknown (U): Distributing/selling
        row == 61, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Unknown (U): Exploiting children
        row == 62, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Unknown (U): Operating/promoting/assisting
        row == 63, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Unknown (U): Possessing/concealing
        row == 64, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Unknown (U): Transporting/transmitting/importing
        row == 65, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #Unknown (U): Using/consuming
        row == 66, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #More Than 3 Types (X): Buying/receiving
        row == 67, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #More Than 3 Types (X): Cultivating/manufacturing/publishing
        row == 68, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #More Than 3 Types (X): Distributing/selling
        row == 69, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #More Than 3 Types (X): Exploiting children
        row == 70, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #More Than 3 Types (X): Operating/promoting/assisting
        row == 71, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #More Than 3 Types (X): Possessing/concealing
        row == 72, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #More Than 3 Types (X): Transporting/transmitting/importing
        row == 73, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #More Than 3 Types (X): Using/consuming
        row == 74, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Buying/receiving
        row == 75, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Cultivating/manufacturing/publishing
        row == 76, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Distributing/selling
        row == 77, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Exploiting children
        row == 78, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Operating/promoting/assisting
        row == 79, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Possessing/concealing
        row == 80, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Transporting/transmitting/importing
        row == 81, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Using/consuming
        row == 82, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Buying/receiving
        row == 83, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Cultivating/manufacturing/publishing
        row == 84, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Distributing/selling
        row == 85, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Exploiting children
        row == 86, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Operating/promoting/assisting
        row == 87, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Possessing/concealing
        row == 88, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Transporting/transmitting/importing
        row == 89, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Using/consuming
        row == 90, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Buying/receiving
        row == 91, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Cultivating/manufacturing/publishing
        row == 92, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Distributing/selling
        row == 93, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Exploiting children
        row == 94, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Operating/promoting/assisting
        row == 95, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Possessing/concealing
        row == 96, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Transporting/transmitting/importing
        row == 97, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Using/consuming
        row == 98, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Buying/receiving
        row == 99, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Cultivating/manufacturing/publishing
        row == 100, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Distributing/selling
        row == 101, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Exploiting children
        row == 102, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Operating/promoting/assisting
        row == 103, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Possessing/concealing
        row == 104, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Transporting/transmitting/importing
        row == 105, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Using/consuming
        row == 106, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Stimulant (L, M): Buying/receiving
        row == 107, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Stimulant (L, M): Cultivating/manufacturing/publishing
        row == 108, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Stimulant (L, M): Distributing/selling
        row == 109, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Stimulant (L, M): Exploiting children
        row == 110, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Stimulant (L, M): Operating/promoting/assisting
        row == 111, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Stimulant (L, M): Possessing/concealing
        row == 112, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Stimulant (L, M): Transporting/transmitting/importing
        row == 113, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Stimulant (L, M): Using/consuming
        row == 114, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Depressant (N, O): Buying/receiving
        row == 115, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Depressant (N, O): Cultivating/manufacturing/publishing
        row == 116, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Depressant (N, O): Distributing/selling
        row == 117, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Depressant (N, O): Exploiting children
        row == 118, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Depressant (N, O): Operating/promoting/assisting
        row == 119, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Depressant (N, O): Possessing/concealing
        row == 120, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Depressant (N, O): Transporting/transmitting/importing
        row == 121, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Depressant (N, O): Using/consuming
        row == 122, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Other (P): Buying/receiving
        row == 123, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Other (P): Cultivating/manufacturing/publishing
        row == 124, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Other (P): Distributing/selling
        row == 125, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Other (P): Exploiting children
        row == 126, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Other (P): Operating/promoting/assisting
        row == 127, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Other (P): Possessing/concealing
        row == 128, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Other (P): Transporting/transmitting/importing
        row == 129, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Other (P): Using/consuming
        row == 130, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Unknown (U): Buying/receiving
        row == 131, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Unknown (U): Cultivating/manufacturing/publishing
        row == 132, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Unknown (U): Distributing/selling
        row == 133, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Unknown (U): Exploiting children
        row == 134, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Unknown (U): Operating/promoting/assisting
        row == 135, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Unknown (U): Possessing/concealing
        row == 136, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Unknown (U): Transporting/transmitting/importing
        row == 137, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug Unknown (U): Using/consuming
        row == 138, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug More Than 3 Types (X): Buying/receiving
        row == 139, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug More Than 3 Types (X): Cultivating/manufacturing/publishing
        row == 140, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug More Than 3 Types (X): Distributing/selling
        row == 141, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug More Than 3 Types (X): Exploiting children
        row == 142, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug More Than 3 Types (X): Operating/promoting/assisting
        row == 143, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug More Than 3 Types (X): Possessing/concealing
        row == 144, CREATE_PERCENTAGE_DENOMINATOR(c(1), column), #One Criminal Activity or One Suspected Drug More Than 3 Types (X): Transporting/transmitting/importing
        row == 145, CREATE_PERCENTAGE_DENOMINATOR(c(1), column) #One Criminal Activity or One Suspected Drug More Than 3 Types (X): Using/consuming
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
