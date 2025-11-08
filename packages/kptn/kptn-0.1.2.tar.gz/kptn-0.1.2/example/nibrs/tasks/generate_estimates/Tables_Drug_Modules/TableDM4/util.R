library(tidyverse)
library(openxlsx)
library(DBI)
library(DT)
library(lubridate)
library(data.table)

#Declare the final section and row number for the table
assign_row <- function(data){

  returndata <- data %>% mutate(

  row = fcase(
    section == 1,  1,
    der_suspected_type_of_drug %in% c(1:9),  der_suspected_type_of_drug + 1
    #der_suspected_type_of_drug_seized %in% c(1:9),  der_suspected_type_of_drug_seized + 10
    )
  )

  return(returndata)
}

assign_section <- function(data){

  returndata <- data %>% mutate(

  section = fcase(
    row %in% c(1),  1,
    row %in% c(2:10),  2
    #row %in% c(11:19),  3
    )
  )

  return(returndata)

}


#New add on code for labels
assign_labels <- function(data){

  returndata <- data %>% mutate(

  estimate_domain = fcase(

row == 1,  'Total',
row == 2,  'Suspected type of drug: Cocaine/crack cocaine (A, B)',
row == 3,  'Suspected type of drug: Marijuana/hashish (C, E)',
row == 4,  'Suspected type of drug: Opiate/narcotic (D, F, G, H)',
row == 5,  'Suspected type of drug: Hallucinogen (I, J, K)',
row == 6,  'Suspected type of drug: Stimulant (L, M)',
row == 7,  'Suspected type of drug: Depressant (N, O)',
row == 8,  'Suspected type of drug: Other (P)',
row == 9,  'Suspected type of drug: Unknown (U)',
row == 10,  'Suspected type of drug: More Than 3 Types (X)'
# row == 11,  'Suspected type of seized drug: Cocaine/crack cocaine (A, B)',
# row == 12,  'Suspected type of seized drug: Marijuana/hashish (C, E)',
# row == 13,  'Suspected type of seized drug: Opiate/narcotic (D, F, G, H)',
# row == 14,  'Suspected type of seized drug: Hallucinogen (I, J, K)',
# row == 15,  'Suspected type of seized drug: Stimulant (L, M)',
# row == 16,  'Suspected type of seized drug: Depressant (N, O)',
# row == 17,  'Suspected type of seized drug: Other (P)',
# row == 18,  'Suspected type of seized drug: Unknown (U)',
# row == 19,  'Suspected type of seized drug: More Than 3 Types (X)'



  ),

  indicator_name = fcase(

column == 1,  'Completed Drug/Narcotic Violation'


  ),

  full_table = "TableDM4 - Drug Type",
  table = DER_TABLE_NAME
  )

  return(returndata)

}

estimate_type_detail_percentage_label <- function(indata){

  returndata <- indata %>%
    mutate(
      estimate_type_detail_percentage = fcase(

trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 1,  'Incident Level', #Total
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 2,  'Incident Level', #Suspected type of drug: Cocaine/crack cocaine (A, B)
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 3,  'Incident Level', #Suspected type of drug: Marijuana/hashish (C, E)
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 4,  'Incident Level', #Suspected type of drug: Opiate/narcotic (D, F, G, H)
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 5,  'Incident Level', #Suspected type of drug: Hallucinogen (I, J, K)
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 6,  'Incident Level', #Suspected type of drug: Stimulant (L, M)
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 7,  'Incident Level', #Suspected type of drug: Depressant (N, O)
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 8,  'Incident Level', #Suspected type of drug: Other (P)
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 9,  'Incident Level', #Suspected type of drug: Unknown (U)
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 10,  'Incident Level' #Suspected type of drug: More Than 3 Types (X)
# trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 11,  'Incident Level', #Suspected type of seized drug: Cocaine/crack cocaine (A, B)
# trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 12,  'Incident Level', #Suspected type of seized drug: Marijuana/hashish (C, E)
# trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 13,  'Incident Level', #Suspected type of seized drug: Opiate/narcotic (D, F, G, H)
# trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 14,  'Incident Level', #Suspected type of seized drug: Hallucinogen (I, J, K)
# trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 15,  'Incident Level', #Suspected type of seized drug: Stimulant (L, M)
# trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 16,  'Incident Level', #Suspected type of seized drug: Depressant (N, O)
# trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 17,  'Incident Level', #Suspected type of seized drug: Other (P)
# trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 18,  'Incident Level', #Suspected type of seized drug: Unknown (U)
# trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 19,  'Incident Level' #Suspected type of seized drug: More Than 3 Types (X)




))

  return(returndata)
}

estimate_type_detail_rate_label <- function(indata){

  returndata <- indata %>%
    mutate(
      estimate_type_detail_rate = fcase(

trim_upcase(estimate_type) %in% c('RATE') & row == 1,  DER_NA_CODE_STRING, #Total
trim_upcase(estimate_type) %in% c('RATE') & row == 2,  DER_NA_CODE_STRING, #Suspected type of drug: Cocaine/crack cocaine (A, B)
trim_upcase(estimate_type) %in% c('RATE') & row == 3,  DER_NA_CODE_STRING, #Suspected type of drug: Marijuana/hashish (C, E)
trim_upcase(estimate_type) %in% c('RATE') & row == 4,  DER_NA_CODE_STRING, #Suspected type of drug: Opiate/narcotic (D, F, G, H)
trim_upcase(estimate_type) %in% c('RATE') & row == 5,  DER_NA_CODE_STRING, #Suspected type of drug: Hallucinogen (I, J, K)
trim_upcase(estimate_type) %in% c('RATE') & row == 6,  DER_NA_CODE_STRING, #Suspected type of drug: Stimulant (L, M)
trim_upcase(estimate_type) %in% c('RATE') & row == 7,  DER_NA_CODE_STRING, #Suspected type of drug: Depressant (N, O)
trim_upcase(estimate_type) %in% c('RATE') & row == 8,  DER_NA_CODE_STRING, #Suspected type of drug: Other (P)
trim_upcase(estimate_type) %in% c('RATE') & row == 9,  DER_NA_CODE_STRING, #Suspected type of drug: Unknown (U)
trim_upcase(estimate_type) %in% c('RATE') & row == 10,  DER_NA_CODE_STRING #Suspected type of drug: More Than 3 Types (X)
# trim_upcase(estimate_type) %in% c('RATE') & row == 11,  DER_NA_CODE_STRING, #Suspected type of seized drug: Cocaine/crack cocaine (A, B)
# trim_upcase(estimate_type) %in% c('RATE') & row == 12,  DER_NA_CODE_STRING, #Suspected type of seized drug: Marijuana/hashish (C, E)
# trim_upcase(estimate_type) %in% c('RATE') & row == 13,  DER_NA_CODE_STRING, #Suspected type of seized drug: Opiate/narcotic (D, F, G, H)
# trim_upcase(estimate_type) %in% c('RATE') & row == 14,  DER_NA_CODE_STRING, #Suspected type of seized drug: Hallucinogen (I, J, K)
# trim_upcase(estimate_type) %in% c('RATE') & row == 15,  DER_NA_CODE_STRING, #Suspected type of seized drug: Stimulant (L, M)
# trim_upcase(estimate_type) %in% c('RATE') & row == 16,  DER_NA_CODE_STRING, #Suspected type of seized drug: Depressant (N, O)
# trim_upcase(estimate_type) %in% c('RATE') & row == 17,  DER_NA_CODE_STRING, #Suspected type of seized drug: Other (P)
# trim_upcase(estimate_type) %in% c('RATE') & row == 18,  DER_NA_CODE_STRING, #Suspected type of seized drug: Unknown (U)
# trim_upcase(estimate_type) %in% c('RATE') & row == 19,  DER_NA_CODE_STRING #Suspected type of seized drug: More Than 3 Types (X)



))

  return(returndata)

}

#This function will calculate the counts and percentage one column at a time

generate_est <- function(maindata, subsetvareq1, column_number){

  #Declare the variable for the column subset
  filtervarsting <- subsetvareq1

  #Make the var into a symbol
  infiltervar <- filtervarsting %>% rlang:::parse_expr()

  #Create the incidicator filter
  infilter <- paste0(filtervarsting," == 1") %>% rlang:::parse_expr()

  #Create the column variable
  columnnum <- column_number
  incolumn_count <- paste0("final_count_", columnnum) %>% rlang:::parse_expr()
  incolumn_percentage <- paste0("percent_", columnnum) %>% rlang:::parse_expr()

  #Filter the dataset
  main_filter <- maindata %>%
    ############################################
    filter(!!infilter) %>%
    #Deduplicate by Incident ID, and one instance of crime type
    group_by(ori, incident_id, !!infiltervar) %>%
    mutate(raw_first = row_number() == 1 ) %>%
    ungroup() %>%
    filter(raw_first == TRUE) %>%
    select(-raw_first) %>%

    select(ori, weight, incident_id, !!infiltervar)

  #Incident count
  s1 <- vector("list", 2)
  #For Table
  s1[[1]] <- main_filter %>%
    mutate(weighted_count = weight *!!infiltervar) %>%
    summarise(final_count = sum(weighted_count)) %>%
    mutate(section = 1)
  #For ORI level - Need unweighted counts
  s1[[2]] <- main_filter %>%
    group_by(ori) %>%
    summarise(final_count = sum(!!infiltervar)) %>%
    ungroup() %>%
    mutate(section = 1)


  #Total Denominator
  der_total_denom <- s1[[1]] %>% select(final_count) %>% as.double()

  #Suspected type of drug
  s2 <- agg_percent_by_incident_id(leftdata = main_filter, rightdata = agg_suspected_type_of_drug, var=der_suspected_type_of_drug, section=2)


  #Suspected type of seized drug
  # s3 <- agg_percent_by_incident_id(leftdata = main_filter, rightdata = agg_suspected_type_of_drug_seized, var=der_suspected_type_of_drug_seized, section=3)

  #Need to get objects of interest
  raw_s_list <- ls(pattern="s\\d+")

  maximum_s_object <- length(raw_s_list)

  #Loop thru to separate the original table information and the ORI level totals
  raw_list_table <- vector("list", maximum_s_object)
  raw_list_ori <- vector("list", maximum_s_object)

  for(i in 1:maximum_s_object){

    #get the object
    raw_object <- get(raw_s_list[[i]])

    #Extract the information to list
    raw_list_table[[i]] <- raw_object[[1]]
    raw_list_ori[[i]] <- raw_object[[2]]

    #Clear the object
    rm(raw_object)
    invisible(gc())


  }

  #Get the datsets together
  #merge_list <- ls(pattern="s\\d+")
  #merge_list_data <- mget(merge_list)

  #Stack the datasets, fix the final_count variable, and rename the variables
  final_data <- reduce(raw_list_table, bind_rows)
  final_data2 <- final_data %>%
    mutate(
      final_count = as.double(final_count)) %>%
    mutate(!!incolumn_count := final_count,
           !!incolumn_percentage := percent)

  #Create the row and reassign the section variable
  final_data3 <- assign_row(final_data2)
  final_data4 <- assign_section(final_data3)

  #Keep variables and sort the dataset
  final_data5 <- final_data4 %>%
    select(section, row, !!incolumn_count, !!incolumn_percentage) %>%
    arrange(section, row)

  #Output data in reporting database

  #Create the filler dataset
  raw_filler <- c(1:DER_MAXIMUM_ROW) %>% as_tibble() %>%
    rename(row = value)
  raw_filler <- assign_section(raw_filler)

  final_reporting_database <-
    raw_filler %>%
    left_join(final_data4, by=c("section","row") ) %>%
    mutate(column = column_number) %>%
    assign_labels() %>%
    arrange(section, row, column) %>%
    #Check to make sure that the NA are in the proper section
    mutate(final_count = case_when(is.na(final_count) ~ 0,
                                   TRUE ~ final_count),
           percent = case_when(is.na(percent) ~ 0,
                                   TRUE ~ percent),

           #UPDATE this for each table:  Make the estimates of the database
           count    = case_when(row %in% c(1:10) ~ final_count,
                                      TRUE ~ DER_NA_CODE),
           percentage  = case_when(
                                      TRUE ~ DER_NA_CODE),
           rate     = case_when(
                                      TRUE ~ DER_NA_CODE),
           population_estimate     = case_when(
                                      TRUE ~ DER_NA_CODE)
           ) %>%
    select(full_table, table, section, row, estimate_domain, column, indicator_name,  count, percentage, rate, population_estimate)

  #Create ORI dataset for variance estimation
  raw_list_ori2 <- raw_list_ori %>%
    bind_rows() %>%
    mutate(column = column_number) %>%
    assign_row() %>%
    assign_section() %>%
    assign_labels() %>%
    arrange(ori, table, section, row, column) %>%
    select(ori, table, section, row, column, final_count) %>%
    mutate(new_key = paste0("t_", table,"_", section, "_", row, "_", column) )

  #Get list of variables in order
  raw_ori_vars <-raw_list_ori2 %>%
    select(table, section, row, column, new_key) %>%
    #Dedepulicate
    group_by(table, section, row, column) %>%
    mutate(raw_first = row_number() == 1) %>%
    ungroup() %>%
    filter(raw_first == TRUE) %>%
    #Sort
    arrange(table, section, row, column) %>%
    select(new_key) %>%
    pull() %>%
    rlang:::enquos()


  #Transpose the dataset
  raw_list_ori3 <- raw_list_ori2 %>%
    select(ori, new_key, final_count) %>%
    spread(new_key, final_count) %>%
    select(ori, !!!raw_ori_vars, everything() )

  #Create list object to return
    return_object <- vector("list", 3)

    return_object[[1]] <- final_data5
    return_object[[2]] <- final_reporting_database
    return_object[[3]] <- raw_list_ori3

  return(return_object)

}
