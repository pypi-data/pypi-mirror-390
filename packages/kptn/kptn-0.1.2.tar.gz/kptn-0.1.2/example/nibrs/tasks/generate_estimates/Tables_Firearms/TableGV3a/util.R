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
    section == 1,  1,
    section == 2,  2,
    
    der_offender_cat %in% c(1:5), der_offender_cat + 2, 
    der_clearance_cat %in% c(1:3), der_clearance_cat + 7, 
    der_exceptional_clearance %in% c(1:5), der_exceptional_clearance + 10  

  )

  )
  
  return(returndata)
}

assign_section <- function(data){
  log_debug("Running assign_section function")

  returndata <- data %>% mutate(

  section = fcase(
    row %in% c(1:2),  1,
    row %in% c(3:7),  2,
    row %in% c(8:15),  3
    
  )
  )   

  return(returndata)

}


#New add on code for labels
assign_labels <- function(data){
  log_debug("Running assign_labels function")

  returndata <- data %>% mutate(

  estimate_domain = fcase(

    row == 1 , 'Incident count',
    row == 2 , 'Incident rate (per 100k total pop)',
    row == 3 , 'Number of Offenders: 1',
    row == 4 , 'Number of Offenders: 2',
    row == 5 , 'Number of Offenders: 3',
    row == 6 , 'Number of Offenders: 4+',
    row == 7 , 'Number of Offenders: Unknown Offender Incidents',
    row == 8 , 'Clearance: Not cleared',
    row == 9 , 'Clearance: Cleared through arrest',
    row == 10 , 'Clearance: Exceptional clearance',
    row == 11 , 'Clearance: Death of offender',
    row == 12 , 'Clearance: Prosecution declined',
    row == 13 , 'Clearance: In custody of other jurisdiction',
    row == 14 , 'Clearance: Victim refused to cooperate',
    row == 15 , 'Clearance: Juvenile/no custody'
  

  ),

  indicator_name = fcase(
    column == 1 , 'NIBRS crimes against persons (Total)',
    column == 2 , 'Total Gun Violence',
    column == 3 , 'Fatal Gun Violence',
    column == 4 , 'Nonfatal Gun Violence',
    column == 5 , 'Nonfatal Gun Violence 2',
    column == 6 , 'Murder and Non-negligent Manslaughter',
    column == 7 , 'Negligent Manslaughter',
    column == 8 , 'Revised Rape',
    column == 9 , 'Robbery',
    column == 10 , 'Aggravated Assault',
    column == 11 , 'Kidnapping/Abduction',
    column == 12 , 'Human Trafficking- Sex and Human Trafficking-Labor',
	  column == 13 , 'Car Jacking'
    

  ),

  full_table = "TableGV3a-Incidents",
  table = DER_TABLE_NAME
  )

  return(returndata)

}

estimate_type_detail_percentage_label <- function(indata){
  log_debug("Running estimate_type_detail_percentage_label function")

  returndata <- indata %>%
    mutate(
      estimate_type_detail_percentage = fcase(

        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 1 , 'Incident Level', #Incident count
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 2 , 'Incident Level', #Incident rate (per 100k total pop)
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 3 , 'Incident Level', #Number of Offenders: 1
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 4 , 'Incident Level', #Number of Offenders: 2
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 5 , 'Incident Level', #Number of Offenders: 3
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 6 , 'Incident Level', #Number of Offenders: 4+
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 7 , 'Incident Level', #Number of Offenders: Unknown Offender Incidents
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 8 , 'Incident Level', #Clearance: Not cleared
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 9 , 'Incident Level', #Clearance: Cleared through arrest
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 10 , 'Incident Level', #Clearance: Exceptional clearance
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 11 , 'Incident Level subset to exceptional clearance', #Clearance: Death of offender
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 12 , 'Incident Level subset to exceptional clearance', #Clearance: Prosecution declined
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 13 , 'Incident Level subset to exceptional clearance', #Clearance: In custody of other jurisdiction
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 14 , 'Incident Level subset to exceptional clearance', #Clearance: Victim refused to cooperate
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 15 , 'Incident Level subset to exceptional clearance' #Clearance: Juvenile/no custody
        
        
           
  ))

  return(returndata)
}

estimate_type_detail_rate_label <- function(indata){
  log_debug("Running estimate_type_detail_rate_label function")

  returndata <- indata %>%
    mutate(
      estimate_type_detail_rate = fcase(
    
        trim_upcase(estimate_type) %in% c('RATE') & row == 1 , DER_NA_CODE_STRING, #Incident count
        trim_upcase(estimate_type) %in% c('RATE') & row == 2 , 'Incident rate per 100,000 persons', #Incident rate (per 100k total pop)
        trim_upcase(estimate_type) %in% c('RATE') & row == 3 , DER_NA_CODE_STRING, #Number of Offenders: 1
        trim_upcase(estimate_type) %in% c('RATE') & row == 4 , DER_NA_CODE_STRING, #Number of Offenders: 2
        trim_upcase(estimate_type) %in% c('RATE') & row == 5 , DER_NA_CODE_STRING, #Number of Offenders: 3
        trim_upcase(estimate_type) %in% c('RATE') & row == 6 , DER_NA_CODE_STRING, #Number of Offenders: 4+
        trim_upcase(estimate_type) %in% c('RATE') & row == 7 , DER_NA_CODE_STRING, #Number of Offenders: Unknown Offender Incidents
        trim_upcase(estimate_type) %in% c('RATE') & row == 8 , DER_NA_CODE_STRING, #Clearance: Not cleared
        trim_upcase(estimate_type) %in% c('RATE') & row == 9 , DER_NA_CODE_STRING, #Clearance: Cleared through arrest
        trim_upcase(estimate_type) %in% c('RATE') & row == 10 , DER_NA_CODE_STRING, #Clearance: Exceptional clearance
        trim_upcase(estimate_type) %in% c('RATE') & row == 11 , DER_NA_CODE_STRING, #Clearance: Death of offender
        trim_upcase(estimate_type) %in% c('RATE') & row == 12 , DER_NA_CODE_STRING, #Clearance: Prosecution declined
        trim_upcase(estimate_type) %in% c('RATE') & row == 13 , DER_NA_CODE_STRING, #Clearance: In custody of other jurisdiction
        trim_upcase(estimate_type) %in% c('RATE') & row == 14 , DER_NA_CODE_STRING, #Clearance: Victim refused to cooperate
        trim_upcase(estimate_type) %in% c('RATE') & row == 15 , DER_NA_CODE_STRING #Clearance: Juvenile/no custody
        
        
  ))
  return(returndata)

}



#This function will calculate the counts and percentage one column at a time

generate_est <- function(maindata, subsetvareq1, column_number){
  log_debug("Running generate_est function")
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
  main_filter <- maindata[eval(infilter), c("ori", "weight", "incident_id", filtervarsting), with = FALSE]
  #Deduplicate by Incident ID, and one instance of crime type
  main_filter <- main_filter[, .SD[1], by = c("ori", "incident_id", filtervarsting)]
  
  log_debug("After filtering and deduping main")
  log_dim(main_filter)
  log_debug(system("free -mh", intern = FALSE))
  
  
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


  #Incident rate
  s2 <- vector("list", 2)
  #For Table
  s2[[1]] <- s1[[1]] %>%
    mutate(final_count = (final_count / POP_TOTAL) * 100000,
           population_estimate = POP_TOTAL ) %>%
    mutate(section = 2)
  #For ORI level - Need unweighted counts
  s2[[2]] <- main_filter %>%
    group_by(ori) %>%
    summarise(final_count = sum(!!infiltervar)) %>%
    ungroup() %>%
    mutate(section = 2)

  # Number of Offenders
  # 1
  # 2
  # 3
  # 4+
  #   Unknown Offender Incidents
  
  s3 <- agg_percent(leftdata = main_filter, rightdata = agg_offender_cat, var=der_offender_cat, section=3, mergeby=c( "incident_id"))
  
  
  # Clearance
  # Not cleared
  # Cleared through arrest
  # Exceptional clearance
  
  s4 <- agg_percent(leftdata = main_filter, rightdata = agg_clearance_cat, var=der_clearance_cat, section=4, mergeby=c( "incident_id"))
  
  #   Death of offender
  #   Prosecution declined
  #   In custody of other jurisdiction
  #   Victim refused to cooperate
  #   Juvenile/no custody
  
  s5 <- agg_percent(leftdata = main_filter, rightdata = agg_exception_clearance_cat, var=der_exceptional_clearance, section=5, mergeby=c( "incident_id"))
  

  
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
  log_debug("Creating final_reporting_database")

  final_reporting_database <-
    raw_filler %>%
    left_join(final_data4, by=c("section","row") ) %>%
    mutate(column = column_number) %>%
    assign_labels() %>%
    arrange(section, row, column) %>%
    #Check to make sure that the NA are in the proper section
    mutate(final_count = case_when(is.na(final_count) ~ 0,TRUE ~ final_count)) %>%
    mutate(percent = case_when(is.na(percent) ~ 0,TRUE ~ percent)) %>%

    #UPDATE this for each table:  Make the estimates of the database
    mutate(count = fcase(!row %in% c(2), final_count, default = DER_NA_CODE)) %>%
    mutate(percentage = fcase(!row %in% c(1:2), percent, default = DER_NA_CODE)) %>%
    mutate(rate = fcase(row %in% c(2), final_count,default = DER_NA_CODE)) %>%
    mutate(population_estimate = fcase(row %in% c(2), population_estimate,default = DER_NA_CODE)) %>%
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