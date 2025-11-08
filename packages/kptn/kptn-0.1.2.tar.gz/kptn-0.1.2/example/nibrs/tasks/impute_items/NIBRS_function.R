replacedemovars <- function(base, imputed, mergeonby){
  
  #Get the variable names that are in the datasets and save as a dataset
  listofvarsmain <- colnames(base) %>% as_tibble() 
  listofvarsimpute <- colnames(imputed) %>% as_tibble() 
  
  #See the variables that are in common except for the mergonby variables
  listofcommonvars <- listofvarsmain %>%
    inner_join(listofvarsimpute, by= "value") %>%
    filter(!(value %in% mergeonby ))
  
  print("Will drop these variables from the base dataset and replace with imputed dataset")
  print(listofcommonvars$value)
  
  #Create the code to drop variables
  listofcommonvars_sym <- paste0("-",listofcommonvars) %>%
    rlang:::parse_exprs()
  
   #Change to symbols the list of mergeonby variables for tidyverse 
   mergeonby_syms <- mergeonby %>% rlang:::syms()
   
  #Will deduplicate just in case 
  tbd_1 <- imputed %>%
    #Deduplicate just in case
    group_by(!!!mergeonby_syms) %>%
    summarise(raw_count = n() ) %>%
    ungroup() %>%
    select(!!!mergeonby_syms)
  
  print("The number of rows in the imputed dataset:")
  print(dim(imputed))
  print("The number of rows in the imputed dataset after deduplication:")
  print(dim(tbd_1))
    
  
  #Need to keep the records that do not need the update
  raw_good <- base %>%
    anti_join(tbd_1, by=mergeonby)
  
  #Identify the records where MICE been process
  raw_tbd_1 <-base %>%
    inner_join(tbd_1, by=mergeonby)
  

  
  #Need to drop the demographic variables records from raw_tbd_1 and join by imputed
  
  raw_good2 <- raw_tbd_1 %>%
    select(!!!listofcommonvars_sym) %>%
  left_join(imputed, by = mergeonby)
  
  #Stack the data together and create final
  final <- bind_rows(raw_good, raw_good2)
  
  print("The base dataset has:")
  print(dim(base))
  
  print("The imputed dataset has:")
  print(dim(imputed))
  
  print("The final dataset has:")
  print(dim(final))
  
  print("These are the number of records from the base dataset that are not in the imputed dataset:")
  print(dim(raw_good))
  
  print("These are the number of records in both the base and imputed datasets:")
  print(dim(raw_good2))
  

  #Return the dataset
  return(final)
}


replacedemovars2 <- function(base, imputed, mergeonby){
  
  #Get the variable names that are in the datasets and save as a dataset
  listofvarsmain <- colnames(base) %>% as_tibble() 
  listofvarsimpute <- colnames(imputed) %>% as_tibble() 
  
  #See the variables that are in common except for the mergonby variables
  listofcommonvars <- listofvarsmain %>%
    inner_join(listofvarsimpute, by= "value") %>%
    filter(!(value %in% mergeonby ))
  
  #Only do if there are variables in common
  if(nrow(listofcommonvars) > 0){
  
	  print("Will drop these variables from the base dataset and replace with imputed dataset")
	  print(listofcommonvars$value)
	  
	  #Create the code to drop variables
	   
	  listofcommonvars_sym <- paste0("-",listofcommonvars) %>%
		rlang:::parse_exprs()
  
  }
  
   #Change to symbols the list of mergeonby variables for tidyverse 
   mergeonby_syms <- mergeonby %>% rlang:::syms()
   
  #Will deduplicate just in case 
  tbd_1 <- imputed %>%
    #Deduplicate just in case
    group_by(!!!mergeonby_syms) %>%
    summarise(raw_count = n() ) %>%
    ungroup() %>%
    select(!!!mergeonby_syms)
  
  print("The number of rows in the imputed dataset:")
  print(dim(imputed))
  print("The number of rows in the imputed dataset after deduplication:")
  print(dim(tbd_1))
    
  
  #Need to keep the records that do not need the update
  raw_good <- base %>%
    anti_join(tbd_1, by=mergeonby)
  
  #Identify the records where MICE been process
  raw_tbd_1 <-base %>%
    inner_join(tbd_1, by=mergeonby)
  

  
  #Need to drop the demographic variables records from raw_tbd_1 and join by imputed
    
  #Only do if there are variables in common
  if(nrow(listofcommonvars) > 0){
	  raw_good2 <- raw_tbd_1 %>%
		select(!!!listofcommonvars_sym) %>%
	  left_join(imputed, by = mergeonby)
  }else{
	  raw_good2 <- raw_tbd_1 %>%
	  left_join(imputed, by = mergeonby)
  }
  
  #Stack the data together and create final
  final <- bind_rows(raw_good, raw_good2)
  
  print("The base dataset has:")
  print(dim(base))
  
  print("The imputed dataset has:")
  print(dim(imputed))
  
  print("The final dataset has:")
  print(dim(final))
  
  print("These are the number of records from the base dataset that are not in the imputed dataset:")
  print(dim(raw_good))
  
  print("These are the number of records in both the base and imputed datasets:")
  print(dim(raw_good2))
  

  #Return the dataset
  return(final)
}
