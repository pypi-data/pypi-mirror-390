
#Store the list of offenses in a vector
listofoffensesrecoded <- c(
  "der_off_assault_hom",
  "der_off_kidnapping_ht",
  "der_off_sex",
  "der_off_arson_bur_vand",
  "der_off_mvt_rob",
  "der_off_other_property",
  "der_off_other_society"
)

#This function will count the number of offense of each person type (i.e. type).  Due to the structure of the NIBRS file, there might be some
#duplicate records cause by crossing multiple files.  In order to reduce the amount of deduplicate records, another id variable (i.e. deduptype) is 
#used to identify the number of offenses.

#Want to deduplicate the amount of duplicate records due to cross.
#Will use an additional ID variable for deduplication process
#For victim use offender
#For offender use victim
#For arrestee use victim


createoffenserecodeindicator <- function(data, type, deduptype){

  #Create vector to hold results
  summarisevector <- vector("list", length(listofoffensesrecoded) + 1 )
  
  #Put the main data at the front
  summarisevector[[1]] <- data
  
  #Loop thru the list listofoffensesrecoded and create the summarized variables
  for(i in 1:length(listofoffensesrecoded)){
    
    #Create symbol version of variables
    offense      <- listofoffensesrecoded[[i]] %>% rlang:::parse_expr()
    offense_type <- paste0(listofoffensesrecoded[[i]],"_",type) %>% rlang:::parse_expr()
    id           <- paste0(type, "_id") %>% rlang:::parse_expr()  
    dedupid      <- paste0(deduptype, "_id") %>% rlang:::parse_expr()  
  
    #Need to increment by 1 to handle first spot taken
    summarisevector[[i + 1]] <- data %>%
      #For for Person ID, dedeuplicate by incident_id, person id, additional person id, and offense_id
      group_by(incident_id, !!id, !!dedupid, offense_id) %>%
      mutate(raw_first_row = row_number() == 1) %>% 
      filter(raw_first_row == TRUE) %>% 
      ungroup() %>%
      #Next count the number of distinct offense codes in the larger offense category 
      group_by(incident_id, !!id) %>%
      summarise(!!offense_type := sum(!!offense) ) %>%
      ungroup() %>%
    #Make consistent with VOR imputation, make indicator variable 01 instead of counts
    mutate(
    !!(offense_type) := case_when(
      !!(offense_type) >= 1 ~ 1, 
      TRUE ~ 0
    ))
  }
  
  #Do a left join
  data2 <- reduce(summarisevector, left_join, by = c("incident_id", paste0(type, "_id") ) )
  
  #Return the data
  return(data2)

} 