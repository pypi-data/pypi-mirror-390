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
    der_offender_age_12_plus_missing_unk_inc == 1, 1,
    der_offender_cat_12_17 %in% c(1), 2,
    der_offender_cat_18_plus %in% c(1), 3,
    der_offender_age_missing %in% c(1), 4,
    der_unknown_offender_incident %in% c(1), 5)
  
  )

  return(returndata)
}

assign_section <- function(data){
  log_debug("Running assign_section function")

  returndata <- data %>% mutate(

  section = fcase(
    row %in% c(1), 1,
    row %in% c(2:5), 2)
  )

  return(returndata)

}


#New add on code for labels
assign_labels <- function(data){
  log_debug("Running assign_labels function")

  returndata <- data %>% mutate(

  estimate_domain = fcase(

	row == 1, 'Number of Victimizations performed by offenders aged 12 or older, or missing age, or from unknown offender incidents',
	row == 2, 'Victimization performed by any offenders in an incident by age: 12-17',
	row == 3, 'Victimization performed by any offenders in an incident by age: 18 or older',
	row == 4, 'Victimization performed by any offenders in an incident by age: Known offenders and missing age',
	row == 5, 'Victimization performed by any offenders in an incident by age: Unknown offender incidents'

    
  ),

  indicator_name = fcase(
    
	column == 1, 'Murder and Non-negligent Manslaughter'

  ),

  full_table = "TableYT2-Person Offenders",
  table = DER_TABLE_NAME
  )

  return(returndata)

}

estimate_type_detail_percentage_label <- function(indata){
  log_debug("Running estimate_type_detail_percentage_label function")

  returndata <- indata %>%
    mutate(
      estimate_type_detail_percentage = fcase(

	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 1, 'Number of Victimizations performed by offenders aged 12 or older, or missing age, or from unknown offender incidents', #Number of Victimizations performed by offenders aged 12 or older, or missing age, or from unknown offender incidents
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 2, 'Number of Victimizations performed by offenders aged 12 or older, or missing age, or from unknown offender incidents', #Victimization performed by any offenders in an incident by age: 12-17
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 3, 'Number of Victimizations performed by offenders aged 12 or older, or missing age, or from unknown offender incidents', #Victimization performed by any offenders in an incident by age: 18 or older
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 4, 'Number of Victimizations performed by offenders aged 12 or older, or missing age, or from unknown offender incidents', #Victimization performed by any offenders in an incident by age: Known offenders and missing age
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 5, 'Number of Victimizations performed by offenders aged 12 or older, or missing age, or from unknown offender incidents' #Victimization performed by any offenders in an incident by age: Unknown offender incidents
		

		
		
  ))

  return(returndata)
}

estimate_type_detail_rate_label <- function(indata){
  log_debug("Running estimate_type_detail_rate_label function")

  returndata <- indata %>%
    mutate(
      estimate_type_detail_rate = fcase(
	  
		trim_upcase(estimate_type) %in% c('RATE') & row == 1, DER_NA_CODE_STRING, #Number of Victimizations performed by offenders aged 12 or older, or missing age, or from unknown offender incidents
		trim_upcase(estimate_type) %in% c('RATE') & row == 2, DER_NA_CODE_STRING, #Victimization performed by any offenders in an incident by age: 12-17
		trim_upcase(estimate_type) %in% c('RATE') & row == 3, DER_NA_CODE_STRING, #Victimization performed by any offenders in an incident by age: 18 or older
		trim_upcase(estimate_type) %in% c('RATE') & row == 4, DER_NA_CODE_STRING, #Victimization performed by any offenders in an incident by age: Known offenders and missing age
		trim_upcase(estimate_type) %in% c('RATE') & row == 5, DER_NA_CODE_STRING #Victimization performed by any offenders in an incident by age: Unknown offender incidents
	

	
    
    
  ))
  return(returndata)

}



#This function will calculate the counts and percentage one column at a time

generate_est <- function(maindata, subsetvareq1, column_number){
  log_debug("Running generate_est function")
  log_debug(system("free -mh", intern = FALSE))

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
  main_filter <- maindata[eval(infilter), c("ori", "weight", "incident_id", "victim_id", "offense_id", "der_victim_LEO", filtervarsting, "der_offender_id_exclude"), with = FALSE]
  #Deduplicate by Incident ID, victim ID, and one instance of crime type
  main_filter <- main_filter[, .SD[1], by = c("ori", "incident_id", "victim_id", filtervarsting)]

  log_debug("After filtering and deduping main")
  log_dim(main_filter)
  log_debug(system("free -mh", intern = FALSE))
  
  
#der_offender_age_12_plus_missing_unk_inc
  #Incident level data with the following values:
  # 1, #Offender aged 12 or older
  # 1, #Offender age is unknown
  # 1, #Unknown offender incidents
  
  s1 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_offender_age_12_plus_missing_unk_inc_inc_imp, var=der_offender_age_12_plus_missing_unk_inc, section=1, mergeby=c( "incident_id"))  
  
  #Total Denominator
  der_total_denom <- s1[[1]] %>% select(final_count) %>% pull() %>% as.double()   
  
  #der_offender_cat_12_17
  #Incident level data with the following values:
  #1, #12-17
  
  s2 <- agg_percent_CAA_victim(leftdata = main_filter, rightdata = agg_offender_cat_12_17_inc_imp, var=der_offender_cat_12_17, section=2, mergeby=c( "incident_id"), denom=der_total_denom)  
  
  #der_offender_cat_18_plus
  #Incident level data with the following values:
  #1, #18 or older
  
  s3 <- agg_percent_CAA_victim(leftdata = main_filter, rightdata = agg_offender_cat_18_plus_inc_imp, var=der_offender_cat_18_plus, section=3, mergeby=c( "incident_id"), denom=der_total_denom)  
  
  #der_offender_age_missing
  #Incident level data with the following values:
  #1, #Known offender age missing  
  
    s4 <- agg_percent_CAA_victim(leftdata = main_filter, rightdata = agg_offender_age_missing_inc_imp, var=der_offender_age_missing, section=4, mergeby=c( "incident_id"), denom=der_total_denom)  
    
    
  #der_unknown_offender_incident
  #Incident level data with the following values:
  #1, #Unknown offender incidents

    s5 <- agg_percent_CAA_victim(leftdata = main_filter, rightdata = agg_unknown_offender_incident_inc_imp, var=der_unknown_offender_incident, section=5, mergeby=c( "incident_id"), denom=der_total_denom)      
  

  
  
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
    mutate(
	   #UPDATE this for each table:  Make the estimates of the database
	   count    = final_count,
	   percentage  = fcase(!row %in% c(1), percent,
								  default = DER_NA_CODE),
	   rate     =                 DER_NA_CODE,
	   population_estimate     =  DER_NA_CODE
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