library(tidyverse)
library(openxlsx)
library(DBI)
library(DT)
library(lubridate)
library(data.table)

#Declare the final section and row number for the table
assign_row <- function(data){
  log_debug("Running assign_row function")

  returndata <- data %>% mutate(

  row = fcase(
    section == 1,  1

  )
)

  return(returndata)
}

assign_section <- function(data){
  log_debug("Running assign_section function")

  returndata <- data %>% mutate(

  section = fcase(
    row %in% c(1),  1
    
    )
  )

  return(returndata)

}




#New add on code for labels
assign_labels <- function(data){
  log_debug("Running assign_labels function")

  returndata <- data %>% mutate(

  estimate_domain = fcase(
    
    row == 1, 'Offense count'

  ),

  indicator_name = fcase(

    column == 1, 'Violent Crime',
    column == 2, 'Murder and Non-negligent Manslaughter',
    column == 3, 'Rape',
    column == 4, 'Robbery',
    column == 5, 'Aggravated Assault',
    column == 6, 'Property Crime',
    column == 7, 'Burglary',
    column == 8, 'Larceny-theft',
    column == 9, 'Motor Vehicle Theft'

  ),

  full_table = "TableSRS1a-SRS Offenses",
  table = DER_TABLE_NAME
  )

  return(returndata)

}

estimate_type_detail_percentage_label <- function(indata){
  log_debug("Running estimate_type_detail_percentage_label function")

  returndata <- indata %>%
    mutate(
      estimate_type_detail_percentage = fcase(

        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 1, 'Offense Level' #Offense count
        
        
        
))

  return(returndata)
}

estimate_type_detail_rate_label <- function(indata){
  log_debug("Running estimate_type_detail_rate_label function")

  returndata <- indata %>%
    mutate(
      estimate_type_detail_rate = fcase(

        trim_upcase(estimate_type) %in% c('RATE') & row == 1,  'Offense rate per 100,000 persons' #Offense count
        
))

  return(returndata)

}


generate_est <- function(maindata, subsetvareq1, column_number){
  
  #Create infiltervar variable
  infiltervar   <- subsetvareq1 %>% rlang:::parse_expr()
  
  #Create the column variable
  columnnum <- column_number
  incolumn_count <- paste0("final_count_", columnnum) %>% rlang:::parse_expr()
  incolumn_percentage <- paste0("percent_", columnnum) %>% rlang:::parse_expr()  
  incolumn_rate <- paste0("rate_", columnnum) %>% rlang:::parse_expr()  
  
  #Incident count
  s1 <- vector("list", 2)
  #For Table
  s1[[1]] <- maindata %>%
    mutate(weighted_count = weight *!!infiltervar) %>%
    summarise(final_count = sum(weighted_count), 
              final_rate = (final_count / POP_TOTAL) * 100000,
              population_estimate = POP_TOTAL
    ) %>%
    mutate(section = 1)
  #For ORI level - Need unweighted counts
  s1[[2]] <- maindata %>%
    group_by(ori) %>%
    summarise(final_count = sum(!!infiltervar)) %>%
    ungroup() %>%
    mutate(section = 1)  
  
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
           #!!incolumn_percentage := percent,
           !!incolumn_rate := final_rate)
  
  #Create the row and reassign the section variable
  final_data3 <- assign_row(final_data2)
  final_data4 <- assign_section(final_data3)
  
  #Keep variables and sort the dataset
  final_data5 <- final_data4 %>%
    select(section, row, !!incolumn_count, !!incolumn_rate) %>% # !!incolumn_percentage) %>%
    arrange(section, row)
  
  #Output data in reporting database
  
  #Create the filler dataset
  raw_filler <- c(1:DER_MAXIMUM_ROW) %>% as_tibble() %>%
    rename(row = value)
  raw_filler <- assign_section(raw_filler)
  log_debug("Creating final_reporting_database")
  
  final_reporting_database <-
    raw_filler %>%
    left_join(final_data4, by=c("section","row") ) %>%
    mutate(column = column_number) %>%
    assign_labels() %>%
    arrange(section, row, column) %>%
    #Check to make sure that the NA are in the proper section
    mutate(final_count = case_when(is.na(final_count) ~ 0,TRUE ~ final_count)) %>%
    #mutate(percent = case_when(is.na(percent) ~ 0,TRUE ~ percent)) %>%
    mutate(final_rate = case_when(is.na(final_rate) ~ 0,TRUE ~ final_rate)) %>%
    
    #UPDATE this for each table:  Make the estimates of the database
    mutate(count = fcase(row %in% c(1:DER_MAXIMUM_ROW) , final_count, default = DER_NA_CODE)) %>%
    #mutate(percentage = fcase(!row %in% c(1,2), percent, default = DER_NA_CODE)) %>%
    mutate(percentage = DER_NA_CODE) %>%
    mutate(rate = fcase(row %in% c(1), final_rate, default = DER_NA_CODE)) %>%
    mutate(population_estimate = fcase(row %in% c(1), population_estimate, default = DER_NA_CODE)) %>%
    select(full_table, table, section, row, estimate_domain, column, indicator_name,  count, percentage, rate, population_estimate)
    #select(full_table, table, section, row, estimate_domain, column, indicator_name,  count, rate, population_estimate)
  
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


