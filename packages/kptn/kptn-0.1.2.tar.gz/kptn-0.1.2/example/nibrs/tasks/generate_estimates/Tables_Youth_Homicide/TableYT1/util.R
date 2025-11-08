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
    section == 1, 1,
    der_victim_age_cat_12_17_cat %in% c(1:2), der_victim_age_cat_12_17_cat + 1,
    der_victim_gender %in% c(1:3), der_victim_gender + 3,
    der_victim_ethnicity %in% c(1:3), der_victim_ethnicity + 6,
    der_victim_eth_race %in% c(1:12), der_victim_eth_race + 9)
  
  )

  return(returndata)
}

assign_section <- function(data){
  log_debug("Running assign_section function")

  returndata <- data %>% mutate(

   section = fcase(
    row %in% c(1), 1,
    row %in% c(2:3), 2,
    row %in% c(4:6), 3,
    row %in% c(7:9), 4, 
    row %in% c(10:13), 5, 
    row %in% c(14:17), 6, 
    row %in% c(18:21), 7
  )
  )

  return(returndata)

}


#New add on code for labels
assign_labels <- function(data){
  log_debug("Running assign_labels function")

  returndata <- data %>% mutate(

  estimate_domain = fcase(

	row == 1, 'Victimization count 12-17',
	row == 2, 'Victim Age: 12-14',
	row == 3, 'Victim Age: 15-17',
	row == 4, 'Victim sex: Male',
	row == 5, 'Victim sex: Female',
	row == 6, 'Victim sex: Unknown',
	row == 7, 'Victim Ethnicity: Hispanic or Latino',
	row == 8, 'Victim Ethnicity: Not Hispanic or Latino',
	row == 9, 'Victim Ethnicity: Multiple/Unknown/Not Specified',
	row == 10, 'Victim Hispanic or Latino/Race: White',
	row == 11, 'Victim Hispanic or Latino/Race: Black',
	row == 12, 'Victim Hispanic or Latino/Race: Other Race',
	row == 13, 'Victim Hispanic or Latino/Race: Unknown Race',
	row == 14, 'Victim Not Hispanic or Latino/Race: White',
	row == 15, 'Victim Not Hispanic or Latino/Race: Black',
	row == 16, 'Victim Not Hispanic or Latino/Race: Other Race',
	row == 17, 'Victim Not Hispanic or Latino/Race: Unknown Race',
	row == 18, 'Victim Multiple/Unknown/Not Specified Ethnicity/Race: White',
	row == 19, 'Victim Multiple/Unknown/Not Specified Ethnicity/Race: Black',
	row == 20, 'Victim Multiple/Unknown/Not Specified Ethnicity/Race: Other Race',
	row == 21, 'Victim Multiple/Unknown/Not Specified Ethnicity/Race: Unknown Race'
    

    
  ),

  indicator_name = fcase(
    
	column == 1, 'Murder and Non-negligent Manslaughter'

  ),

  full_table = "TableYT1-Person Victims",
  table = DER_TABLE_NAME
  )

  return(returndata)

}

estimate_type_detail_percentage_label <- function(indata){
  log_debug("Running estimate_type_detail_percentage_label function")

  returndata <- indata %>%
    mutate(
      estimate_type_detail_percentage = fcase(

    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 1, 'Victim Level Subset to 12-17 Years Old', #Victimization count 12-17
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 2, 'Victim Level Subset to 12-17 Years Old', #Victim Age: 12-14
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 3, 'Victim Level Subset to 12-17 Years Old', #Victim Age: 15-17
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 4, 'Victim Level Subset to 12-17 Years Old', #Victim sex: Male
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 5, 'Victim Level Subset to 12-17 Years Old', #Victim sex: Female
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 6, 'Victim Level Subset to 12-17 Years Old', #Victim sex: Unknown
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 7, 'Victim Level Subset to 12-17 Years Old', #Victim Ethnicity: Hispanic or Latino
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 8, 'Victim Level Subset to 12-17 Years Old', #Victim Ethnicity: Not Hispanic or Latino
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 9, 'Victim Level Subset to 12-17 Years Old', #Victim Ethnicity: Multiple/Unknown/Not Specified
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 10, 'Victim Level Subset to 12-17 Years Old', #Victim Hispanic or Latino/Race: White
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 11, 'Victim Level Subset to 12-17 Years Old', #Victim Hispanic or Latino/Race: Black
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 12, 'Victim Level Subset to 12-17 Years Old', #Victim Hispanic or Latino/Race: Other Race
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 13, 'Victim Level Subset to 12-17 Years Old', #Victim Hispanic or Latino/Race: Unknown Race
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 14, 'Victim Level Subset to 12-17 Years Old', #Victim Not Hispanic or Latino/Race: White
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 15, 'Victim Level Subset to 12-17 Years Old', #Victim Not Hispanic or Latino/Race: Black
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 16, 'Victim Level Subset to 12-17 Years Old', #Victim Not Hispanic or Latino/Race: Other Race
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 17, 'Victim Level Subset to 12-17 Years Old', #Victim Not Hispanic or Latino/Race: Unknown Race
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 18, 'Victim Level Subset to 12-17 Years Old', #Victim Multiple/Unknown/Not Specified Ethnicity/Race: White
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 19, 'Victim Level Subset to 12-17 Years Old', #Victim Multiple/Unknown/Not Specified Ethnicity/Race: Black
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 20, 'Victim Level Subset to 12-17 Years Old', #Victim Multiple/Unknown/Not Specified Ethnicity/Race: Other Race
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 21, 'Victim Level Subset to 12-17 Years Old' #Victim Multiple/Unknown/Not Specified Ethnicity/Race: Unknown Race

		
		
  ))

  return(returndata)
}

estimate_type_detail_rate_label <- function(indata){
  log_debug("Running estimate_type_detail_rate_label function")

  returndata <- indata %>%
    mutate(
      estimate_type_detail_rate = fcase(
	  
	trim_upcase(estimate_type) %in% c('RATE') & row == 1, DER_NA_CODE_STRING, #Victimization count 12-17
	trim_upcase(estimate_type) %in% c('RATE') & row == 2, DER_NA_CODE_STRING, #Victim Age: 12-14
	trim_upcase(estimate_type) %in% c('RATE') & row == 3, DER_NA_CODE_STRING, #Victim Age: 15-17
	trim_upcase(estimate_type) %in% c('RATE') & row == 4, DER_NA_CODE_STRING, #Victim sex: Male
	trim_upcase(estimate_type) %in% c('RATE') & row == 5, DER_NA_CODE_STRING, #Victim sex: Female
	trim_upcase(estimate_type) %in% c('RATE') & row == 6, DER_NA_CODE_STRING, #Victim sex: Unknown
	trim_upcase(estimate_type) %in% c('RATE') & row == 7, DER_NA_CODE_STRING, #Victim Ethnicity: Hispanic or Latino
	trim_upcase(estimate_type) %in% c('RATE') & row == 8, DER_NA_CODE_STRING, #Victim Ethnicity: Not Hispanic or Latino
	trim_upcase(estimate_type) %in% c('RATE') & row == 9, DER_NA_CODE_STRING, #Victim Ethnicity: Multiple/Unknown/Not Specified
	trim_upcase(estimate_type) %in% c('RATE') & row == 10, DER_NA_CODE_STRING, #Victim Hispanic or Latino/Race: White
	trim_upcase(estimate_type) %in% c('RATE') & row == 11, DER_NA_CODE_STRING, #Victim Hispanic or Latino/Race: Black
	trim_upcase(estimate_type) %in% c('RATE') & row == 12, DER_NA_CODE_STRING, #Victim Hispanic or Latino/Race: Other Race
	trim_upcase(estimate_type) %in% c('RATE') & row == 13, DER_NA_CODE_STRING, #Victim Hispanic or Latino/Race: Unknown Race
	trim_upcase(estimate_type) %in% c('RATE') & row == 14, DER_NA_CODE_STRING, #Victim Not Hispanic or Latino/Race: White
	trim_upcase(estimate_type) %in% c('RATE') & row == 15, DER_NA_CODE_STRING, #Victim Not Hispanic or Latino/Race: Black
	trim_upcase(estimate_type) %in% c('RATE') & row == 16, DER_NA_CODE_STRING, #Victim Not Hispanic or Latino/Race: Other Race
	trim_upcase(estimate_type) %in% c('RATE') & row == 17, DER_NA_CODE_STRING, #Victim Not Hispanic or Latino/Race: Unknown Race
	trim_upcase(estimate_type) %in% c('RATE') & row == 18, DER_NA_CODE_STRING, #Victim Multiple/Unknown/Not Specified Ethnicity/Race: White
	trim_upcase(estimate_type) %in% c('RATE') & row == 19, DER_NA_CODE_STRING, #Victim Multiple/Unknown/Not Specified Ethnicity/Race: Black
	trim_upcase(estimate_type) %in% c('RATE') & row == 20, DER_NA_CODE_STRING, #Victim Multiple/Unknown/Not Specified Ethnicity/Race: Other Race
	trim_upcase(estimate_type) %in% c('RATE') & row == 21, DER_NA_CODE_STRING #Victim Multiple/Unknown/Not Specified Ethnicity/Race: Unknown Race

	
    
    
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
  
  
  #der_victim_cat2_12_17
  #1, #12-14
  #2, #15-17
  s2 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_victim_age_cat_12_17_cat_victim_imp, var=der_victim_age_cat_12_17_cat, section=2, mergeby=c( "incident_id", "victim_id"))  
  
  #der_victim_gender
  # "M" ~ 1,
  # "F" ~ 2,
  # "U" ~ 3,
  s3 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_victim_gender_victim_imp, var=der_victim_gender, section=3, mergeby=c( "incident_id", "victim_id"))  
  
  #der_victim_ethnicity
  # 1, #Hispanic or Latino
  # 2, #Not Hispanic or Latino
  # 3),  #Multiple/Unknown/Not Specified
  s4 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_victim_ethnicity_victim_imp, var=der_victim_ethnicity, section=4, mergeby=c( "incident_id", "victim_id"))  
  
#der_victim_eth_race
# 1:    Hispanic or Latino White
# 2:    Hispanic or Latino Black
# 3:    Hispanic or Latino Other Race (i.e. American Indian or Alaska Native/Asian/Native Hawaiian or Other Pacific Islander)
# 4:    Hispanic or Latino Unknown Race
# 5:    Not Hispanic or Latino White
# 6:    Not Hispanic or Latino Black
# 7:    Not Hispanic or Latino Other Race (i.e. American Indian or Alaska Native/Asian/Native Hawaiian or Other Pacific Islander)
# 8:    Not Hispanic or Latino Unknown Race
# 9:     Multiple/Unknown/Not Specified White
# 10:     Multiple/Unknown/Not Specified Black
# 11:     Multiple/Unknown/Not Specified Other Race (i.e. American Indian or Alaska Native/Asian/Native Hawaiian or Other Pacific Islander)
# 12:     Multiple/Unknown/Not Specified Unknown Race

    s5 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_victim_eth_race_victim_imp, var=der_victim_eth_race, section=5, mergeby=c( "incident_id", "victim_id"))  


  
  
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