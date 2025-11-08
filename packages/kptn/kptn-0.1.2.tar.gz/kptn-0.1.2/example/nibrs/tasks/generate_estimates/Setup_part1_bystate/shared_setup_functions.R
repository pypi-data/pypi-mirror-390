#This function will aggregate the counts and remove the missing categories, must include the incident_id
NIBRS_count_agg <- function(data, var){

  #Make it to a symbol
  invar <- enquo(var)

data2 <- data %>%
  filter(!is.na(!!invar)) %>%
  group_by(incident_id, !!invar) %>%
  summarise(count = n() ) %>%
  ungroup()

  return(data2)

}

#This function will aggregate the counts and remove the missing categories, must include the incident_id and offense_id
NIBRS_count_inc_off_agg <- function(data, var){

  #Make it to a symbol
  invar <- enquo(var)

data2 <- data %>%
  filter(!is.na(!!invar)) %>%
  group_by(incident_id, offense_id, !!invar) %>%
  summarise(count = n() ) %>%
  ungroup()

  return(data2)

}

#This function will aggregate the counts and remove the missing categories, must include the incident_id, victim_id, and offense_id.  Note to get unique offense count, must include both victim and offense id and must merge by incident_id, victim_id, offense_id.  Note that more than one victim could share the same offense id as the offense id only appears only once in an incident.

NIBRS_count_agg_offense <- function(data, var){

  #Make it to a symbol
  invar <- enquo(var)


data2 <- data %>%
  filter(!is.na(!!invar)) %>%
  group_by(incident_id, victim_id, offense_id, !!invar) %>%
  summarise(count = n() ) %>%
  ungroup()

  return(data2)

}

#This function will aggregate the counts and remove the missing categories, must include the incident_id and victim_id
NIBRS_count_agg_victim <- function(data, var){

  #Make it to a symbol
  invar <- enquo(var)

data2 <- data %>%
  filter(!is.na(!!invar)) %>%
  group_by(incident_id, victim_id, !!invar) %>%
  summarise(count = n() ) %>%
  ungroup()

  return(data2)

}

#This function will aggregate the counts and remove the missing categories, must include the incident_id and arrestee_id
NIBRS_count_agg_arrestee <- function(data, var){

  #Make it to a symbol
  invar <- enquo(var)

data2 <- data %>%
  filter(!is.na(!!invar)) %>%
  group_by(incident_id, arrestee_id, !!invar) %>%
  summarise(count = n() ) %>%
  ungroup()

  return(data2)

}

#This function will aggregate the counts and remove the missing categories, must include the incident_id and arrestee_id
NIBRS_count_agg_arrestee_group_b <- function(data, var){

  #Make it to a symbol
  invar <- enquo(var)

data2 <- data %>%
  filter(!is.na(!!invar)) %>%
  group_by(groupb_arrestee_id, !!invar) %>%
  summarise(count = n() ) %>%
  ungroup()

  return(data2)

}

#This function will clear up the memory for any object that starts with df and query
#Clear the memory

cleanup_memory <- function(){

  #Get the list of objects
  tbd_list <- c(ls(pattern="^df", envir=.GlobalEnv), ls(pattern="^query", envir=.GlobalEnv))
  print("Removing objects:  ")
  print(as.character(tbd_list))

  #Remove the objects
  rm(list=c(as.character(tbd_list)), envir=.GlobalEnv)

  #Free up memory
  gc()

}


#Create function for eligible states

elig_recode <- function(data){

    returndata <- data %>% mutate(

      in_univ_elig_state = trim_upper(state_abbr) %in% states,

      der_in_univ_elig =  fcase(
                                    trim_upper(agency_status) == "A" &
                                    trim_upper(covered_flag) == "N" &
                                    trim_upper(dormant_flag) == "N" &
                                    trim_upper(agency_type_name) != "FEDERAL" &
                                    in_univ_elig_state == TRUE, 1,
                                    default = 0)
    )

    #Return the data
    return(returndata)

}

#Create a function to create additional variable after transposing the data does not create all variables
createadditionalvars_after_transpose <- function(indata, inlist, infill){

  #Add log message
  log_debug("Running function createadditionalvars_after_transpose")
  
  #Get the data
  tbd_data <- indata
  
  #Get the current variable names
  tbd_current_vars <- colnames(tbd_data) %>%
    as_tibble()
  
  #Get variables that needs to be created
  tbd_create_var <- inlist %>%
    as_tibble() %>%
    anti_join(tbd_current_vars, by="value") %>%
    select(value) %>%
    pull()
  
  #Generate additional variables if missing
  if(length(tbd_create_var) > 0){
    
    #Loop thru and create additional variables
    for(tbd_var in tbd_create_var){
      
      #Add a log message
      log_debug(paste0("Creating variable "), tbd_var)
      
      #Create the variable
      tbd_data <- tbd_data %>%
        mutate(
          !!(tbd_var %>% rlang:::parse_expr()) := infill
        )
    }
  }
  
  #Return the data
  return(tbd_data)
  
  
}
