
#title: '00-Create Datasets'
#author: "Philip Lee"
#date: "July 22, 2020"
#install.packages("RPostgres")
#install.packages("dbplyr")

#Update on 20200803:
#1.  Free up memory by deleting dataset and queries object after processing
#2.  Make the in_univ variable for subsetting to eligible agencies if needed on task

library(tidyverse)
library(openxlsx)
library(DT)
library(lubridate)
library(readxl)
library(data.table)

#Read in the common functions to be used in R
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))

DATASET_TO_GENERATE <- Sys.getenv("DATASET_TO_GENERATE")

#This function will aggregate the counts and remove the missing categories, must include the incident_id
NIBRS_count_agg <- function(data, var){
  var <- deparse(substitute(var))
  dt <- as.data.table(data)[!is.na(get(var)), .N, by = c("incident_id", var)]
  setnames(dt, "N", "count")
  return(dt)
}

#This function will aggregate the counts and remove the missing categories, must include the incident_id, victim_id, and offense_id.  Note to get unique offense count, must include both victim and offense id and must merge by incident_id, victim_id, offense_id.  Note that more than one victim could share the same offense id as the offense id only appears only once in an incident.
NIBRS_count_agg_offense <- function(data, var){
  var <- deparse(substitute(var))
  dt <- as.data.table(data)[!is.na(get(var)), .N, by = c("incident_id", "victim_id", "offense_id", var)]
  setnames(dt, "N", "count")
  return(dt)
}

#This function will aggregate the counts and remove the missing categories, must include the incident_id and victim_id
NIBRS_count_agg_victim <- function(data, var) {
  var <- deparse(substitute(var))
  dt <- as.data.table(data)[!is.na(get(var)), .N, by = c("incident_id", "victim_id", var)]
  setnames(dt, "N", "count")
  return(dt)
}

#This function will aggregate the counts and remove the missing categories, must include the incident_id and arrestee_id
NIBRS_count_agg_arrestee <- function(data, var){
  var <- deparse(substitute(var))
  dt <- as.data.table(data)[!is.na(get(var)), .N, by = c("incident_id", "arrestee_id", var)]
  setnames(dt, "N", "count")
  return(dt)
}

#This function will aggregate the counts and remove the missing categories, must include the  groupb_arrestee_id
NIBRS_count_agg_groupb_arrestee <- function(data, var){
  var <- deparse(substitute(var))
  dt <- as.data.table(data)[!is.na(get(var)), .N, by = c("groupb_arrestee_id", var)]
  setnames(dt, "N", "count")
  return(dt)
}

#This function will aggregate the counts and remove the missing categories, must include the incident_id
NIBRS_count_agg_keep_level_1_count_1 <- function(data, var) {
  dt <- as.data.table(data)
  var <- deparse(substitute(var))
  # Subset data to level 1, group, count, and cap count at 1
  result <- dt[get(var) == 1, .N, by = c("incident_id", var)]
  #Change the count to 1 if more than 1
  result[, count := ifelse(N > 1, 1, as.double(N))]
  # Remove the intermediate count column
  #result[, N := NULL]
  return(result)
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

#Create function for replacing old values with imputed values
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

#Must update universe file below:
#universe - read in file
#raw_selected_universe_file <- paste0(CONST_DEPENDENCY_UNIVERSE, list.files(path = CONST_DEPENDENCY_UNIVERSE, pattern=paste0(CONST_YEAR))[[1]])

#print(raw_selected_universe_file)

univ_raw <-file.path(input_files_folder, paste0("ref_agency_", CONST_YEAR, ".csv")) %>%
  read_csv(guess_max=1e6)

univ <- univ_raw %>%
  select(ORI, LEGACY_ORI, AGENCY_TYPE_NAME)

read_csv_1e6 <- partial(read_csv, guess_max = 1000000) #For now, read thru the 1st 1,000,000 rows to determine variable type
read_xlsx <- partial(read_xlsx, guess_max = 1000000) #For now, read thru the 1st 1,000,000 rows to determine variable type

#Get the legacy_ori and agency names from the NIBRS

if(DATASET_TO_GENERATE=="VICTIM"){
  #We can use the file raw_victim from the Raw Indicator Table task

   df4_raw <- fread(paste0(der_file_path, "raw_victim.csv.gz"), 
                    colClasses = list(character = c("victim_age_code"))) %>% 
     mutate(victim_age_num = as.numeric(victim_age_num))


  #Need to create number of victims
  #incident_id	der_number_of_victims_cat	count
  
  df4_victim_count <- df4_raw %>%
    #Need to filter to person victims
    #Victim Type ID = "I" is Individual; Victim Type ID = "L is Law Enforcement Officer;
    filter(victim_type_code %in% c("I", "L")) %>% 
    group_by(incident_id) %>%
    summarise(raw_victim_count = n() ) %>% 
    ungroup() %>%
    mutate(der_number_of_victims_cat = fcase(
      raw_victim_count == 1, 1, # 1
      raw_victim_count == 2, 2, # 2
      raw_victim_count == 3, 3, # 3
      raw_victim_count  > 3, 4 # 4+
    ), 
    
    #Create a count variable of 1
    count = 1
    )
  
  #Check the recodes
  # df4_victim_count %>% checkfunction(der_number_of_victims_cat, raw_victim_count)
  
  #Output to share
  df4_victim_count %>%
    select(incident_id, der_number_of_victims_cat, count) %>% 
    write_csv(gzfile(paste0(der_file_path,"/agg_number_of_victims_cat.csv.gz")), na="") 


  df4_imputed_list <- list.files(path=item_imp_path, pattern="17_\\w+_victim_imputed_final_flag.csv.gz")
  log_debug("Merging list of imputed victim files",toString(df4_imputed_list))

  #Create list to hold files
  df4_imputed <- vector("list", length(df4_imputed_list))

  for(i in 1:length(df4_imputed_list)){

    df4_imputed[[i]] <- fread(paste0(item_imp_path, df4_imputed_list[[i]]), 
                              colClasses = list(character = c("age_code_victim_raw", "age_code_victim_le"))) %>%
      recode_all_race_ints_to_char() %>%
      mutate(
        age_code_victim_raw = as.character(age_code_victim_raw),
        age_code_victim_le = as.character(age_code_victim_le)
      )
  }

  victim_df4_imputed_final <- df4_imputed %>%
    bind_rows() %>%
    select(incident_id,
           victim_id,
           victim_sex_code = sex_code_victim_i,
           victim_race_code = race_code_victim_i,
           victim_age_num = age_num_victim_i)
  
  gc(rm(list=c("df4_imputed")))
  
  #Next need to process Hispanic 
  df4_imputed_hisp_list <- list.files(path=item_imp_path, pattern="17_\\w+_victim_imputed_final_flag_hisp.csv.gz")
  log_debug("Merging list of imputed victim files",toString(df4_imputed_hisp_list))
  
  victim_df4_imputed_hisp_final <- map_dfr(df4_imputed_hisp_list, ~{
    
    returndata <-fread(paste0(item_imp_path, .x)) %>% 
      recode_all_ethnicity_ints_to_char() %>%
      select(incident_id,
             victim_id,
             victim_ethnicity_code = ethnicity_code_victim_i
             )
    
    #Return the data
    return(returndata)
      
  })
  
  gc(rm(list=c("df4_imputed_hisp_list")))  
  

  #Create dataset
  df4 <- replacedemovars2(base=df4_raw, imputed=victim_df4_imputed_final, mergeonby=c("incident_id", "victim_id"))
  df4 <- replacedemovars2(base=df4, imputed=victim_df4_imputed_hisp_final, mergeonby=c("incident_id", "victim_id"))
  gc(rm(list=c("df4_raw", "victim_df4_imputed_final", "victim_df4_imputed_hisp_final")))
  

  #Create the demographics variables at the victim level

  df4_recode <- df4 %>%
    mutate(
      der_victim_age = case_when(!is.na(victim_age_num) ~ victim_age_num,
                                 victim_age_code %in% c("NN","NB","BB") ~ 0, #1: Under 24 Hours, 2: 1-6 Days Old, 3: 7-364 Days Old
                                 victim_age_code %in% c("99") ~ 99, #6: Over 98 Years Old
                                 victim_age_code %in% c("00","NS") ~ NA_real_, #4: Unknown or #0: Not Specified
                                 TRUE ~ as.double(victim_age_num)),


      der_victim_age_cat = fcase( 0 <= der_victim_age  & der_victim_age < 5 , 1, #Under 5
                                      5 <= der_victim_age  & der_victim_age < 15, 2, #5-14
                                      15 <= der_victim_age & der_victim_age < 18, 3, #15-17
                                      18 <= der_victim_age & der_victim_age < 25, 4, #18-24
                                      25 <= der_victim_age & der_victim_age < 35, 5, #25-34
                                      35 <= der_victim_age & der_victim_age < 65, 6, #35-64
                                      65 <= der_victim_age                      , 7, #65+
                                      victim_age_code %in% c("00","NS")         , 8, #Unknown or Not Specified
                                      default = 8 # Unknown
      ),

      der_victim_age_cat_15_17 = fcase( 0 <= der_victim_age  & der_victim_age < 5, 1, #Under 5
                                        5 <= der_victim_age  & der_victim_age < 15, 2, #5-14
                                        der_victim_age == 15, 3, #15
                  										  der_victim_age == 16, 4, #16
                  										  der_victim_age == 17, 5, #17
                                        18 <= der_victim_age & der_victim_age < 25, 6, #18-24
                                        25 <= der_victim_age & der_victim_age < 35, 7, #25-34
                                        35 <= der_victim_age & der_victim_age < 65, 8, #35-64
                                        65 <= der_victim_age, 9, #65+
                  										  victim_age_code %in% c("00","NS")         , 10, #Unknown or Not Specified
                                        default = 10 # Unknown
      ),

      der_victim_age_cat_1_2 = fcase( 0 <= der_victim_age  & der_victim_age < 18, 1, #Juvenile
                                      18 <= der_victim_age, 2, #Adult
                                      victim_age_code %in% c("00","NS")         , 3, #Unknown or Not Specified
                                      default = 3 # Unknown
      ),

      der_victim_age_cat_2_uo18 = fcase( 0 <= der_victim_age  & der_victim_age < 18 , 1, #Under 18
                                  18 <= der_victim_age                              , 2, #18+
                                  victim_age_code %in% c("00","NS")                 , 3, #Unknown or Not Specified
                                  default = 3 # Unknown
      ),

      #Create a generic age variable for subsetting in demographic permutations.  Should have range of 0 - 99
      der_victim_age_round = floor(der_victim_age),
      
      der_victim_age_cat_under18_2 = fcase( 0 <= der_victim_age  & der_victim_age  < 12, 1, #Under 12
                                            12 <= der_victim_age  & der_victim_age < 18, 2 #12-17
      ),  

      der_victim_age_cat_12_17_cat = fcase( 12 <= der_victim_age  & der_victim_age  < 15, 1, #12-14
                                            15 <= der_victim_age  & der_victim_age < 18, 2 #15-17
      ),   


      der_victim_gender = fcase(trim_upper(victim_sex_code)  == "M", 1,
                                    trim_upper(victim_sex_code)  == "F", 2,
                                    trim_upper(victim_sex_code)  == "U", 3,
                                    default = 3 # Unknown
                                    ),

      der_victim_race = fcase(
                                  victim_race_code == "W", 1, #White:  White
                                  victim_race_code == "B", 2, #Black or African American:  Black
                                  victim_race_code == "I", 3, #American Indian or Alaska Native:  American Indian or Alaska Native
                                  victim_race_code == "A", 4, #Asian:  Asian
                                  victim_race_code == "AP", 4, #Asian, Native Hawaiian, or Other Pacific Islander:  Asian
                                  victim_race_code == "C", 4, #Chinese:  Asian
                                  victim_race_code == "J", 4, #Japanese:  Asian
                                  victim_race_code == "P", 5, #Native Hawaiian or Other Pacific Islander:  Native Hawaiian or Other Pacific Islander
                                  victim_race_code == "U", 6, # Unknown
                                  default = 6 ),              # O (Other), M (Multiple), NS (Not Specified)

    #Male
    #1   White
    #2   Black
    #3   American Indian or Alaska Native
    #4   Asian
    #5   Native Hawaiian or Other Pacific Islander
    #Female
    #6   White
    #7   Black
    #8   American Indian or Alaska Native
    #9   Asian
    #10   Native Hawaiian or Other Pacific Islander

    der_victim_gender_race = (der_victim_gender - 1)*6 + der_victim_race,
	  
    der_victim_ethnicity = fcase(victim_ethnicity_code == "H", 1, #Hispanic or Latino
                                 victim_ethnicity_code == "N", 2, #Not Hispanic or Latino
                                 default= 3),  #Multiple/Unknown/Not Specified
    
    
    der_victim_ethnicity_race = fcase(
      victim_ethnicity_code == "H", 1, #  Hispanic or Latino
      victim_ethnicity_code == "N" & victim_race_code == "W", 2,  # Non-Hispanic, White
      victim_ethnicity_code == "N" & victim_race_code == "B", 3,  #  Non-Hispanic, Black
      victim_ethnicity_code == "N" & victim_race_code == "I", 4,  # Non-Hispanic, American Indian or Alaska Native
      victim_ethnicity_code == "N" & victim_race_code == "A", 5,  # Asian:  Non-Hispanic, Asian
      victim_ethnicity_code == "N" & victim_race_code == "AP", 5, # Asian, Native Hawaiian or Other Pacific Islander: Non-Hispanic, Asian
      victim_ethnicity_code == "N" & victim_race_code == "C", 5,  # Chinese: Non-Hispanic, Asian
      victim_ethnicity_code == "N" & victim_race_code == "J", 5,  # Japanese: Non-Hispanic, Asian
      victim_ethnicity_code == "N" & victim_race_code == "P", 6,  # Non-Hispanic, Native Hawaiian or Other Pacific Islander
      victim_ethnicity_code == "N" & victim_race_code == "U", 7,  # U - Unknown
      default = 7                    # includes O (Other), M (Multiple), NS (Not Specified)
    ),    
    
								 
    der_victim_race_col = fcase(
                                victim_race_code == "W", 1, #White:  White
                                victim_race_code == "B", 2, #Black or African American:  Black
                                victim_race_code == "I", 3, #American Indian or Alaska Native:  Other Race
                                victim_race_code == "A", 3, #Asian:  Other Race
                                victim_race_code == "AP", 3, #Asian, Native Hawaiian, or Other Pacific Islander:  Other Race
                                victim_race_code == "C", 3, #Chinese:  Other Race
                                victim_race_code == "J", 3, #Japanese:  Other Race
                                victim_race_code == "P", 3, #Native Hawaiian or Other Pacific Islander:  Other Race
                                victim_race_code == "U", 4, # Unknown
                                default = 4),             # includes O (Other), M (Multiple), NS (Not Specified)  
    
    der_victim_eth_race = (der_victim_ethnicity - 1)*4 +  der_victim_race_col 								 
	
    )
  gc(rm(list=c("df4")))

  #Check recodes
  # df4_recode %>% checkfunction(victim_type_code, der_victim_age_cat_1_2, der_victim_age_cat_15_17, der_victim_age_cat, der_victim_age, victim_age_code, victim_age_num)
  # df4_recode %>% checkfunction(victim_type_code, der_victim_age_cat_2_uo18, der_victim_age, victim_age_code, victim_age_num)  
  # df4_recode %>% checkfunction(victim_type_code, der_victim_age_cat_under18_2, der_victim_age, victim_age_code, victim_age_num) 
  # df4_recode %>% checkfunction(victim_type_code, der_victim_age_round, der_victim_age, victim_age_code, victim_age_num) 
  # df4_recode %>% checkfunction(victim_type_code, der_victim_age_cat_12_17_cat, der_victim_age, victim_age_code, victim_age_num) 
  #   
  # df4_recode %>% checkfunction(victim_type_code, der_victim_gender, victim_sex_code)
  # df4_recode %>% checkfunction(victim_type_code, der_victim_race, victim_race_code)
  # df4_recode %>% checkfunction(victim_type_code, der_victim_gender_race, der_victim_gender, der_victim_race)
  # 
  # df4_recode %>% checkfunction(victim_type_code, victim_type_name, der_victim_ethnicity, victim_ethnicity_code, victim_ethnicity_name)
  # df4_recode %>% checkfunction(victim_type_code, victim_type_name, der_victim_ethnicity_race, victim_ethnicity_code, victim_ethnicity_name, victim_race_code)  
  
  # df4_recode %>% checkfunction(victim_type_code, victim_type_name, der_victim_race_col, victim_race_code, victim_race_desc)
  # df4_recode %>% checkfunction(victim_type_code, victim_type_name, der_victim_eth_race, der_victim_ethnicity, der_victim_race_col)
  # 

  #Victim Age Category at Victim Level

  NIBRS_count_agg_victim(data=df4_recode, var=der_victim_age_cat) %>%
  	write_csv(gzfile(paste0(der_file_path,"/agg_victim_age_cat_victim_imp.csv.gz")), na="")

  NIBRS_count_agg_victim(data=df4_recode, var=der_victim_age_cat_15_17) %>%
  	write_csv(gzfile(paste0(der_file_path,"/agg_victim_age_cat_15_17_victim_imp.csv.gz")), na="")

  NIBRS_count_agg_victim(data=df4_recode, var=der_victim_age_cat_2_uo18) %>%
    write_csv(gzfile(paste0(der_file_path,"/agg_victim_age_cat_2_uo18_victim_imp.csv.gz")), na="")  
  
  NIBRS_count_agg_victim(data=df4_recode, var=der_victim_age_cat_under18_2) %>%
    write_csv(gzfile(paste0(der_file_path,"/agg_victim_age_cat_under18_2_victim_imp.csv.gz")), na="")    
  
  NIBRS_count_agg_victim(data=df4_recode, var=der_victim_age_round) %>%
    write_csv(gzfile(paste0(der_file_path,"/agg_victim_age_round_victim_imp.csv.gz")), na="")     
    
  NIBRS_count_agg_victim(data=df4_recode, var=der_victim_age_cat_12_17_cat) %>%
    write_csv(gzfile(paste0(der_file_path,"/agg_victim_age_cat_12_17_cat_victim_imp.csv.gz")), na="")  	
	

  #Victim Gender at Victim Level

  NIBRS_count_agg_victim(data=df4_recode, var=der_victim_gender) %>%
  	write_csv(gzfile(paste0(der_file_path,"/agg_victim_gender_victim_imp.csv.gz")), na="")

  #Victim Race at Victim Level

  NIBRS_count_agg_victim(data=df4_recode, var=der_victim_race) %>%
  	write_csv(gzfile(paste0(der_file_path,"/agg_victim_race_victim_imp.csv.gz")), na="")
  
  #Victim Hispanic Race at Victim Level
  
  NIBRS_count_agg_victim(data=df4_recode, var=der_victim_ethnicity_race) %>%
    write_csv(gzfile(paste0(der_file_path,"/agg_victim_ethnicity_race_victim_imp.csv.gz")), na="")  

  #Victim Sex and Race at Victim Level

  NIBRS_count_agg_victim(data=df4_recode, var=der_victim_gender_race) %>%
  	write_csv(gzfile(paste0(der_file_path,"/agg_victim_gender_race_victim_imp.csv.gz")), na="")

  #Victim Ethnicity
  # 1, #Hispanic or Latino
  # 2, #Not Hispanic or Latino
  # 3),  #Multiple/Unknown/Not Specified

  NIBRS_count_agg_victim(data=df4_recode, var=der_victim_ethnicity) %>% 
    write_csv(gzfile(paste0(der_file_path,"/agg_victim_ethnicity_victim_imp.csv.gz")), na="")	
    
  #Victim ethnicity and race at Victim Level
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


  NIBRS_count_agg_victim(data=df4_recode, var=der_victim_eth_race) %>% 
    write_csv(gzfile(paste0(der_file_path,"/agg_victim_eth_race_victim_imp.csv.gz")), na="")	


  #Clear the objects and free up memory
  cleanup_memory()
}else if(DATASET_TO_GENERATE=="OFFENDER"){
  #Now we need to process the offender data
  tbd_list_offender <- list.files(path=query_folder_path, pattern= "raw_offender_all_cols_\\w+\\.csv\\.gz")
  
  log_debug("Merging list of raw offender files",toString(tbd_list_offender))
  
  df6_raw_off <- map_dfr(tbd_list_offender, ~{
    
    returndata <- fread(paste0(query_folder_path, .x), 
                        colClasses = list(character = c("offender_age_code")))
    
    #Return the data
    return(returndata)
    
  }) %>%
    #Rename to match code below
    rename(
      offender_sex_code = sex_code_offender 
    )
  
  #Delete the tbd_list_offender list
  rm(tbd_list_offender)
  invisible(gc())

  df6_imputed_list_off <- list.files(path=item_imp_path, pattern="17_\\w+_offender_imputed_final_flag.csv.gz")
  log_debug("Merging list of imputed offender files",toString(df6_imputed_list_off))

  #Create list to hold files
  df6_imputed_off <- vector("list", length(df6_imputed_list_off))

  for(i in 1:length(df6_imputed_list_off)){

    df6_imputed_off[[i]] <- fread(paste0(item_imp_path, df6_imputed_list_off[[i]]), 
                                  colClasses = list(character = c("age_code_offender_raw", "age_code_offender_le"))) %>% 
      recode_all_race_ints_to_char() %>% 
      mutate(
        age_code_offender_raw = as.character(age_code_offender_raw),
        age_code_offender_le = as.character(age_code_offender_le),
    )

  }

  offender_df6_imputed_final <- df6_imputed_off %>%
    bind_rows() %>%
    select(incident_id,
           offender_id,
           offender_sex_code = sex_code_offender_i,
           offender_race_code = race_code_offender_i,
           offender_age_num = age_num_offender_i)
  
   gc(rm(list=c("df6_imputed_off")))

   df4_imputed_list <- list.files(path=item_imp_path, pattern="17_\\w+_victim_imputed_final_flag.csv.gz")
   log_debug("Merging list of imputed victim files",toString(df4_imputed_list))

   #Create list to hold files
   df4_imputed <- vector("list", length(df4_imputed_list))

   for(i in 1:length(df4_imputed_list)){

     df4_imputed[[i]] <- fread(paste0(item_imp_path, df4_imputed_list[[i]]), 
                               colClasses = list(character = c("age_code_victim_raw", "age_code_victim_le"))) %>% 
       recode_all_race_ints_to_char()%>% 
       mutate(
        age_code_victim_raw = as.character(age_code_victim_raw),
        age_code_victim_le = as.character(age_code_victim_le)
    )

   }

   victim_df4_imputed_final <- df4_imputed %>%
     bind_rows() %>%
     select(incident_id,
            victim_id,
            victim_sex_code = sex_code_victim_i,
            victim_race_code = race_code_victim_i,
            victim_age_num = age_num_victim_i)
   
   gc(rm(list=c("df4_imputed")))

  #Reserve space for victim-offender relationship when ready

  #df6_imputed_list_vor <- list.files(path=item_imp_path, pattern="04_imputed_relationship_code_\\w+\\.csv.gz")
   df6_imputed_list_vor <- bind_rows(
     list.files(path=item_imp_path, pattern="04_imputed_relationship_code_\\w+\\.csv.gz") %>% as_tibble(),
     list.files(path=item_imp_path, pattern="05_imputed_relationship_code_offender_propertyoffense_\\w+\\.csv.gz")  %>% as_tibble()
   ) %>%
     select(value) %>%
     pull()																																	 
  log_debug("Merging list of imputed vic-offender files",toString(df6_imputed_list_vor))

  #Create list to hold files
  df6_imputed_vor <- vector("list", length(df6_imputed_list_vor))

  for(i in 1:length(df6_imputed_list_vor)){

    df6_imputed_vor[[i]] <- fread(paste0(item_imp_path, df6_imputed_list_vor[[i]])) %>% 
      recode_all_race_ints_to_char()

  }

  vor_df6_imputed_final <- df6_imputed_vor %>%
    bind_rows() %>%
    select(incident_id,
           victim_id,
           offender_id,
		   #Note der_relationship is already in the collapsed version of the variable
		   der_relationship
		   #relationship_code = der_relationship
           ) %>%
    #Just in case, keep one instance of the VOR of each incident_id, victim_id, offender_id
    group_by(incident_id, victim_id, offender_id) %>%
    mutate(tbd_keep = row_number() == 1) %>%
    ungroup() %>%
    filter(tbd_keep == TRUE)
  
  #Check the dimension
  log_dim(bind_rows(df6_imputed_vor))
  log_dim(vor_df6_imputed_final)																						   


  gc(rm(list=c("df6_imputed_vor")))

  #Bring in the dataset from prior run
  df6_raw <- fread(paste0(der_file_path, "raw_victim_offender_rel.csv.gz"), 
                   colClasses = list(character = c("victim_age_code", "offender_age_code"))) %>%
    mutate(offender_age_num = as.numeric(offender_age_num),
             victim_age_num = as.numeric(victim_age_num))

  #Check the dimension before the merge
  log_dim(df6_raw)
  
  #20231120:  Need to bring in the incident identified as unknown offender incidents
  df_unknown_off_inc <- fread(paste0(der_file_path, "unknown_offender_incident.csv.gz"))
  
  #Merge on df6_raw with df_unknown_off_inc
  df6_raw <- df6_raw %>%
    left_join(df_unknown_off_inc, by=c("incident_id"))
  
  #Check the dimension - after the merge
  log_dim(df6_raw)
  log_dim(df_unknown_off_inc)  	
  gc(rm(list=c("df_unknown_off_inc")))
  
  #Create dataset - using victim_df4_imputed_final and offender_df6_imputed_final
  df6 <- replacedemovars2(base=df6_raw, imputed=victim_df4_imputed_final, mergeonby=c("incident_id", "victim_id"))
  df6_1 <- replacedemovars2(base=df6,   imputed=offender_df6_imputed_final, mergeonby=c("incident_id", "offender_id"))
  gc(rm(list=c("df_unknown_off_inc", "victim_df4_imputed_final")))
  
  log_debug("Right before all of the df6_recode recodes")
  df6_recode <- df6_1 %>%
    mutate( der_relationship = fcase(
            relationship_code == "AQ", 3, #Victim Was Acquaintance:  Outside family but known to victim
            relationship_code == "BE", 3, #Victim Was Babysittee:  Outside family but known to victim
            relationship_code == "BG", 1, #Victim Was Boyfriend/Girlfriend:  Intimate partner
			      relationship_code == "CF", 2, #Victim Was Child of Boyfriend or Girlfriend:  Other family			
            relationship_code == "CH", 2, #Victim Was Child:  Other family
            relationship_code == "CS", 1, #Victim Was Common-Law Spouse:  Intimate partner
            relationship_code == "EE", 3, #Victim was Employee:  Outside family but known to victim
            relationship_code == "ER", 3, #Victim was Employer:  Outside family but known to victim
            relationship_code == "FR", 3, #Victim Was Friend:  Outside family but known to victim
            relationship_code == "GC", 2, #Victim Was Grandchild:  Other family
            relationship_code == "GP", 2, #Victim Was Grandparent:  Other family
            relationship_code == "IL", 2, #Victim Was In-law:  Other family
            relationship_code == "NE", 3, #Victim Was Neighbor:  Outside family but known to victim
            relationship_code == "OF", 2, #Victim Was Other Family Member:  Other family
            relationship_code == "OK", 3, #Victim was Otherwise Known:  Outside family but known to victim
            relationship_code == "PA", 2, #Victim Was Parent:  Other family
            relationship_code == "RU", 6, #Relationship Unknown:  Unknown relationship
            relationship_code == "SB", 2, #Victim Was Sibling:  Other family
            relationship_code == "SC", 2, #Victim Was Stepchild:  Other family
            relationship_code == "SE", 1, #Victim Was Spouse:  Intimate partner
            relationship_code == "SP", 2, #Victim Was Stepparent:  Other family
            relationship_code == "SS", 2, #Victim Was Stepsibling:  Other family
            relationship_code == "ST", 4, #Victim Was Stranger:  Stranger
            relationship_code == "VO", 5, #Victim Was Offender:  Victim was Offender
            relationship_code == "XS", 1, #Victim was Ex-Spouse:  Intimate partner
            relationship_code == "XR", 1, #Victim Was Ex-Relationship (Ex-Boyfriend/Girlfriend):  Intimate partner
			      relationship_code == "CO", 3, #Cohabitant (non-intimate relationship):  Outside family but known to victim
			      relationship_code =="FP", 3, #Victim was Foster Parent:  Outside family but known to victim
			      relationship_code == "FC", 3, #Victim was Foster Child:  Outside family but known to victim																											 
            default = NA_real_
    )
  )
  
  gc(rm(list=c("df6_raw", "df6", "df6_1")))

  df6_recode <- df6_recode %>%
      mutate(
        #####Victim########
        der_victim_age = case_when(victim_age_code %in% c("NN","NB","BB") ~ 0, #1: Under 24 Hours, 2: 1-6 Days Old, 3: 7-364 Days Old
                                   victim_age_code %in% c("99") ~ 99, #6: Over 98 Years Old
                                   victim_age_code %in% c("00","NS") ~ NA_real_, #4: Unknown or #0: Not Specified
                                   TRUE ~ as.double(victim_age_num)),
        )

  df6_recode <- df6_recode %>%
      mutate(
        der_victim_age_cat = fcase( 0 <= der_victim_age  & der_victim_age < 5 , 1, #Under 5
                                        5 <= der_victim_age  & der_victim_age < 15, 2, #5-14
                                        15 <= der_victim_age & der_victim_age < 18, 3, #15-17
                                        18 <= der_victim_age & der_victim_age < 25, 4, #18-24
                                        25 <= der_victim_age & der_victim_age < 35, 5, #25-34
                                        35 <= der_victim_age & der_victim_age < 65, 6, #35-64
                                        65 <= der_victim_age                      , 7, #65+
                                        victim_age_code %in% c("00","NS")         , 8,  #Unknown
                                        default = 8 #Unknown
        )
    )

  df6_recode <- df6_recode %>%
      mutate(

        der_victim_age_cat_1_2 = fcase( 0 <= der_victim_age  & der_victim_age < 18 , 1, #Juvenile
                                        18 <= der_victim_age                       , 2,  #Adult
                                        victim_age_code %in% c("00","NS")          , 3,  #Unknown
                                        default = 3 #Unknown

        )
    )

  df6_recode <- df6_recode %>%
      mutate(

      der_victim_gender = fcase(trim_upper(victim_sex_code)  == "M", 1,
                                    trim_upper(victim_sex_code)  == "F", 2,
                                    trim_upper(victim_sex_code)  == "U", 3,
                                    default = 3 ), #Unknown

      der_victim_race = fcase(
                                  victim_race_code == "W", 1, #White:  White
                                  victim_race_code == "B", 2, #Black or African American:  Black
                                  victim_race_code == "I", 3, #American Indian or Alaska Native:  American Indian or Alaska Native
                                  victim_race_code == "A", 4, #Asian:  Asian
                                  victim_race_code == "AP", 4, #Asian, Native Hawaiian, or Other Pacific Islander:  Asian
                                  victim_race_code == "C", 4, #Chinese:  Asian
                                  victim_race_code == "J", 4, #Japanese:  Asian
                                  victim_race_code == "P", 5, #Native Hawaiian or Other Pacific Islander:  Native Hawaiian or Other Pacific Islander
                                  victim_race_code == "U", 6, #Unknown
                                  default = 6)              #O (Other), M (Multiple), NS (Not Specified)
  )

  ###Offender#####
  df6_recode <- df6_recode %>%
      mutate(
        der_offender_age = case_when(offender_age_code %in% c("NN","NB","BB") ~ 0, #1: Under 24 Hours, 2: 1-6 Days Old, 3: 7-364 Days Old
                                     offender_age_code %in% c("99") ~ 99, #6: Over 98 Years Old
                                     offender_age_code %in% c("00","NS") ~ NA_real_, #4: Unknown or #0: Not Specified
                                     TRUE ~ as.double(offender_age_num)),
  )

  df6_recode <- df6_recode %>%
      mutate(
        der_offender_age_cat = fcase( 0 <= der_offender_age  & der_offender_age < 5 , 1, #Under 5
                                        5 <= der_offender_age  & der_offender_age < 15, 2, #5-14
                                        15 <= der_offender_age & der_offender_age < 18, 3, #15-17
                                        18 <= der_offender_age & der_offender_age < 25, 4, #18-24
                                        25 <= der_offender_age & der_offender_age < 35, 5, #25-34
                                        35 <= der_offender_age & der_offender_age < 65, 6, #35-64
                                        65 <= der_offender_age                      , 7,  #65+
                                        offender_age_code %in% c("00","NS")            , 8, #Unknown or Not Specified
                                        default = 8  #Unknown
      )
  )

  df6_recode <- df6_recode %>%
      mutate(
        der_offender_age_cat_1_2 = fcase( 0 <= der_offender_age  & der_offender_age < 18 , 1, #Juvenile
                                        18 <= der_offender_age                           ,     2,  #Adult
                                        offender_age_code %in% c("00","NS")                , 3, #Unknown or Not Specified
                                        default = 3 ),#Unknown
        der_offender_gender = fcase(trim_upper(offender_sex_code)  == "M", 1,
                                      trim_upper(offender_sex_code)  == "F", 2,
                                      trim_upper(offender_sex_code)  == "U", 3,
                                      default = 3 ), #Unknown

        der_offender_race = fcase(
                                    offender_race_code == "W", 1, #White:  White
                                    offender_race_code == "B", 2, #Black or African American:  Black
                                    offender_race_code == "I", 3, #American Indian or Alaska Native:  American Indian or Alaska Native
                                    offender_race_code == "A", 4, #Asian:  Asian
                                    offender_race_code == "AP", 4, #Asian, Native Hawaiian, or Other Pacific Islander:  Asian
                                    offender_race_code == "C", 4, #Chinese:  Asian
                                    offender_race_code == "J", 4, #Japanese:  Asian
                                    offender_race_code == "P", 5, #Native Hawaiian or Other Pacific Islander:  Native Hawaiian or Other Pacific Islander
                                    offender_race_code == "U", 6, #Unknown
                                    default = 6 )               #O (Other), M (Multiple), NS (Not Specified)
  )

  df6_recode <- df6_recode %>%
      mutate(
       der_victim_offender_age_1_4 = fcase(

          der_victim_age_cat_1_2 == 1 & der_offender_age_cat_1_2 == 1, 1, #Victim juvenile X Offender juvenile
          der_victim_age_cat_1_2 == 1 & der_offender_age_cat_1_2 == 2, 2, #Victim juvenile X Offender adult
          der_victim_age_cat_1_2 == 2 & der_offender_age_cat_1_2 == 2, 3, #Victim adult X Offender adult
          der_victim_age_cat_1_2 == 2 & der_offender_age_cat_1_2 == 1, 4, #Victim adult X Offender juvenile
          der_victim_age_cat_1_2 == 3 | der_offender_age_cat_1_2 == 3, 5,  #Unknown victim age or unknown offender age
          default = 5
        ),

       der_victim_offender_gender_1_4 = fcase(

          der_victim_gender == 1 & der_offender_gender == 1, 1, #Victim male X Offender male
          der_victim_gender == 1 & der_offender_gender == 2, 2, #Victim male X Offender female
          der_victim_gender == 2 & der_offender_gender == 2, 3, #Victim female X Offender female
          der_victim_gender == 2 & der_offender_gender == 1, 4, #Victim female X Offender male
          der_victim_gender == 3 | der_offender_gender == 3, 5, #Unknown victim sex or unknown offender sex
          default = 5
       ),

      der_victim_offender_race_1_10 = fcase(

        der_victim_race == 1 & der_offender_race == 1            , 1, #Victim White X Offender White
        der_victim_race == 1 & der_offender_race %in% c(2:5)     , 2, #Victim White X Offender non-White
        der_victim_race == 2 & der_offender_race == 2            , 3, #Victim Black X Offender Black
        der_victim_race == 2 & der_offender_race %in% c(1, 3:5)  , 4, #Victim Black X Offender non-Black
        der_victim_race == 3 & der_offender_race == 3            , 5, #Victim AIAN X Offender AIAN
        der_victim_race == 3 & der_offender_race %in% c(1:2, 4:5) , 6, #Victim AIAN X Offender non-AIAN
        der_victim_race == 4 & der_offender_race == 4             , 7, #Victim Asian X Offender Asian
        der_victim_race == 4 & der_offender_race %in% c(1:3, 5)   , 8, #Victim Asian X Offender non-Asian
        der_victim_race == 5 & der_offender_race == 5             , 9, #Victim NHOPI X Offender NHOPI
        der_victim_race == 5 & der_offender_race %in% (1:4)       , 10, #Victim NHOPI X Offender non-NHOPI
        der_victim_race == 6 | der_offender_race == 6             , 11, #Unknown victim race or unknown offender race
        default = 11
    )

  )
  
  #Need to replace the raw der_relationship with the imputed version of der_relationship
  df6_recode <- replacedemovars2(base=df6_recode, imputed=vor_df6_imputed_final, mergeonby=c("incident_id", "victim_id", "offender_id"))  
  
  #Recode the new der_relationship2 variables
  df6_recode <- df6_recode %>%
	mutate(
		der_relationship2 = fcase(
			der_relationship %in% c(1:2), 1, #1=Intimate partner, 2=Other family: Intimate partner plus Family
			der_relationship %in% c(3), 2, #3=Outside family but known to victim:  Outside family but known to victim
			der_relationship %in% c(4), 3, #4=Stranger:  Stranger
			der_relationship %in% c(5), 4, #5=Victim was Offender:  Victim was Offender
			der_relationship %in% c(6), 5 #6=Unknown relationship:  Unknown relationship
			
		),
		
		#20231120 - Implement new VOR hierarchy rule, keep the derived categories the same as der_relationship
		# Intimate partner	1
		# Other family	2
		# Outside family but known to victim	3
		# Stranger	4
		# Victim was Offender	5
		# Unknown relationship	6
		
		#But add new categories for not imputed 
		# VOR from Unknown Offender Incidents 7
		# VOR Missing from Uncleared Cases 8
		
		der_relationship_hierarchy = fcase(
		  #Assign relationship if not missing
		  !is.na(der_relationship), der_relationship,
		  #If unknown offender incident 
		  victim_type_code %in% c("I", "L") & der_offender_id_exclude == 1, 7,
		  #If uncleared and person victim 
		  victim_type_code %in% c("I","L"), 8)
	)

  #Check recodes

  # df6_recode %>% checkfunction(der_relationship,        relationship_code, relationship_name)
  # # df6_recode %>% checkfunction(der_relationship_forimp, relationship_code, relationship_name)
  # df6_recode %>% checkfunction(der_relationship2,  der_relationship,       relationship_code, relationship_name)  
  # 
  # df6_recode %>% checkfunction(der_victim_age_cat_1_2, der_victim_age_cat, der_victim_age, victim_age_code, victim_age_num)
  # df6_recode %>% checkfunction(der_victim_gender, victim_sex_code)
  # df6_recode %>% checkfunction(der_victim_race, victim_race_code)
  # 
  # df6_recode %>%
  #   checkfunction(der_offender_age_cat_1_2, der_offender_age_cat, der_offender_age, offender_age_code, offender_age_num)
  # df6_recode %>% checkfunction(der_offender_gender, offender_sex_code)
  # df6_recode %>% checkfunction(der_offender_race, offender_race_code)
  # 
  # 
  # df6_recode %>% checkfunction(der_victim_offender_age_1_4, der_victim_age_cat_1_2, der_offender_age_cat_1_2)
  # df6_recode %>% checkfunction(der_victim_offender_gender_1_4, der_victim_gender, der_offender_gender)
  # df6_recode %>% checkfunction(der_victim_offender_race_1_10, der_victim_race, der_offender_race)

  #Check recodes for hierarchy
  df6_recode %>% filter(victim_type_code %in% c("I","L")) %>%
    checkfunction(der_relationship_hierarchy, der_relationship, der_offender_id_exclude)  


  #Victim-offender relationship # error here
  NIBRS_count_agg(data=df6_recode, var=der_relationship) %>%
  	write_csv(gzfile(paste0(der_file_path,"/agg_relationship_cat_imp.csv.gz")), na="")

  #Victim-offender relationship - At Victim level
  NIBRS_count_agg_victim(data=df6_recode, var=der_relationship) %>%
  	write_csv(gzfile(paste0(der_file_path,"/agg_relationship_cat_victim_imp.csv.gz")), na="")

  NIBRS_count_agg(data=df6_recode, var=der_relationship2) %>%
  	write_csv(gzfile(paste0(der_file_path,"/agg_relationship_cat2_imp.csv.gz")), na="")

  #Victim-offender relationship - At Victim level
  NIBRS_count_agg_victim(data=df6_recode, var=der_relationship2) %>%
  	write_csv(gzfile(paste0(der_file_path,"/agg_relationship_cat2_victim_imp.csv.gz")), na="")	

 
  #Victim-offender relationship - hierarchy
  #Aggregate by incident_id and der_relationship_hierarchy (i.e. a row for each vor)
  NIBRS_count_agg(data=df6_recode, var=der_relationship_hierarchy) %>%
    as.data.frame() %>% 
    #Need to keep only one vor per incident_id 
    arrange(incident_id,  der_relationship_hierarchy) %>%
    #Need to keep one row per incident_id
    group_by(incident_id) %>%
    mutate(der_row_number = row_number()) %>%
    ungroup() %>%
    #Keep the first row
    filter(der_row_number == 1) %>%
    #Make the count variable to be 1 for indicator
    mutate(count = 1) %>%
    write_csv(gzfile(paste0(der_file_path,"agg_relationship_hierarchy_imp.csv.gz")), na="")
  
  #Victim-offender relationship - hierarchy - At Victim Level
  #Aggregate by incident_id, victim_id and der_relationship_hierarchy (i.e. a row for each vor)
  NIBRS_count_agg_victim(data=df6_recode, var=der_relationship_hierarchy) %>%
    as.data.frame() %>% 
    #Need to keep only one vor per incident_id and victim_id
    arrange(incident_id, victim_id,  der_relationship_hierarchy) %>%
    #Need to keep one row per incident_id and victim_id
    group_by(incident_id, victim_id) %>%
    mutate(der_row_number = row_number()) %>%
    ungroup() %>%
    #Keep the first row
    filter(der_row_number == 1) %>%
    #Make the count variable to be 1 for indicator
    mutate(count = 1) %>%
    write_csv(gzfile(paste0(der_file_path,"agg_relationship_hierarchy_victim_imp.csv.gz")), na="") 
  
  
  #Not needed since it is not imputed
  #Victim-offender relationship for imputation
  # NIBRS_count_agg(data=df6_recode, var=der_relationship_forimp) %>%
  # 	write_csv(gzfile(paste0(der_file_path,"/agg_relationship_cat_forimp_imp.csv.gz")), na="")
  # 
  # #Victim-offender relationship - At Victim level for imputation
  # NIBRS_count_agg_victim(data=df6_recode, var=der_relationship_forimp) %>%
  # 	write_csv(gzfile(paste0(der_file_path,"/agg_relationship_cat_forimp_victim_imp.csv.gz")), na="")



  #Victim Offender Age - At Victim Level
  NIBRS_count_agg_victim(data=df6_recode, var=der_victim_offender_age_1_4) %>%
  	write_csv(gzfile(paste0(der_file_path,"/agg_victim_offender_age_1_4_victim_imp.csv.gz")), na="")

  #Victim Offender Gender - At Victim Level
  NIBRS_count_agg_victim(data=df6_recode, var=der_victim_offender_gender_1_4) %>%
  	write_csv(gzfile(paste0(der_file_path,"/agg_victim_offender_gender_1_4_victim_imp.csv.gz")), na="")

  #Victim Offender Race - At Victim Level
  NIBRS_count_agg_victim(data=df6_recode, var=der_victim_offender_race_1_10) %>%
  	write_csv(gzfile(paste0(der_file_path,"/agg_victim_offender_race_1_10_victim_imp.csv.gz")), na="")

  #Clear the objects and free up memory
  cleanup_memory()
} else if(DATASET_TO_GENERATE=="ARRESTEE"){
  #We can use the file raw_arrestee from the Raw Indicator Table task

  #df9_raw <- fread(paste0(der_file_path, "raw_arrestee.csv.gz")) %>% mutate(arrestee_age_num = as.numeric(arrestee_age_num))
  
  tbd_list_arrestee <- list.files(path=query_folder_path, pattern= "raw_arrestee_all_cols_\\w+\\.csv\\.gz")
  
  log_debug("Merging list of raw arrestee files",toString(tbd_list_arrestee))
  
  df9_raw <- map_dfr(tbd_list_arrestee, ~{
    
    returndata <- fread(paste0(query_folder_path, .x), 
                        colClasses = list(character = c("age_code_arrestee")))
    
    #Return the data
    return(returndata)
    
  }) %>%
    rename(
      arrestee_age_code = age_code_arrestee,
      arrestee_age_num = age_num_arrestee,
      arrestee_sex_code = sex_code_arrestee,
      arrestee_race_code = race_code_arrestee,
      arrestee_ethnicity_code = ethnicity_code_arrestee
    )
  
  #Delete the tbd_list_arrestee list
  rm(tbd_list_arrestee)
  invisible(gc())  
  

  df9_imputed_list <- list.files(path=item_imp_path, pattern="17_\\w+_arrestee_imputed_final_flag.csv.gz")
  log_debug("Merging list of imputed arrestee files",toString(df9_imputed_list))

  #Create list to hold files
  df9_imputed <- vector("list", length(df9_imputed_list))

  for(i in 1:length(df9_imputed_list)){

    df9_imputed[[i]] <- fread(paste0(item_imp_path, df9_imputed_list[[i]]), 
                              colClasses = list(character = c("age_code_arrestee_raw", "age_code_arrestee_le"))) %>% 
      recode_all_race_ints_to_char()

  }

  arrestee_df9_imputed_final <- df9_imputed %>%
    bind_rows() %>%
    select(incident_id,
           arrestee_id,
           arrestee_sex_code = sex_code_arrestee_i,
           arrestee_race_code = race_code_arrestee_i,
           arrestee_age_num = age_num_arrestee_i)
  
  gc(rm(list=c("df9_imputed", "df9_imputed_list")))
  
  #Next need to process Hispanic 
  df9_imputed_hisp_list <- list.files(path=item_imp_path, pattern="17_\\w+_arrestee_imputed_final_flag_hisp.csv.gz")
  log_debug("Merging list of imputed arrestee files",toString(df9_imputed_hisp_list))
  
  arrestee_df9_imputed_hisp_final <- map_dfr(df9_imputed_hisp_list, ~{
    
    returndata <-fread(paste0(item_imp_path, .x)) %>% 
      recode_all_ethnicity_ints_to_char() %>%
      select(incident_id,
             arrestee_id,
             arrestee_ethnicity_code = ethnicity_code_arrestee_i
      )
    
    #Return the data
    return(returndata)
    
  })
  
  gc(rm(list=c("df9_imputed_hisp_list")))    
  

  #Create dataset
  df9 <- replacedemovars2(base=df9_raw, imputed=arrestee_df9_imputed_final, mergeonby=c("incident_id", "arrestee_id"))
  df9 <- replacedemovars2(base=df9, imputed=arrestee_df9_imputed_hisp_final, mergeonby=c("incident_id", "arrestee_id"))  
  gc(rm(list=c("df9_raw", "arrestee_df9_imputed_final", "arrestee_df9_imputed_hisp_final")))

  #Create the demographics variables at the arrestee level
  log_debug("Right before all of the df9_recode recodes")
  df9_recode <- df9 %>%
    mutate(
      der_arrestee_age = case_when(!is.na(arrestee_age_num) ~ arrestee_age_num,
                                   arrestee_age_code %in% c("NN","NB","BB") ~ 0, #1: Under 24 Hours, 2: 1-6 Days Old, 3: 7-364 Days Old
                                   arrestee_age_code %in% c("99") ~ 99, #6: Over 98 Years Old
                                   arrestee_age_code %in% c("00","NS") ~ NA_real_, #4: Unknown or #0: Not Specified
                                   TRUE ~ as.double(arrestee_age_num)),
  )
  gc(rm(list=c("df9")))

  df9_recode <- df9_recode %>%
    mutate(
      der_arrestee_age_cat = fcase( 0 <= der_arrestee_age  & der_arrestee_age < 5 , 1, #Under 5
                                      5 <= der_arrestee_age  & der_arrestee_age < 15, 2, #5-14
                                      15 <= der_arrestee_age & der_arrestee_age < 18, 3, #15-17
                                      18 <= der_arrestee_age & der_arrestee_age < 25, 4, #18-24
                                      25 <= der_arrestee_age & der_arrestee_age < 35, 5, #25-34
                                      35 <= der_arrestee_age & der_arrestee_age < 65, 6, #35-64
                                      65 <= der_arrestee_age                      , 7,  #65+
                                      arrestee_age_code %in% c("00","NS")         , 8, #Unknown or Not Specified
                                      default = 8 # Unknown
      )
    )

  df9_recode <- df9_recode %>%
    mutate(
      der_arrestee_age_cat_15_17 = fcase( 0 <= der_arrestee_age  & der_arrestee_age < 5 , 1, #Under 5
                                      5 <= der_arrestee_age  & der_arrestee_age < 15, 2, #5-14
                                           der_arrestee_age                    == 15, 3, #15
                  										 der_arrestee_age  == 16, 4, #16
                  										 der_arrestee_age  == 17, 5, #17
                                      18 <= der_arrestee_age & der_arrestee_age < 25, 6, #18-24
                                      25 <= der_arrestee_age & der_arrestee_age < 35, 7, #25-34
                                      35 <= der_arrestee_age & der_arrestee_age < 65, 8, #35-64
                                      65 <= der_arrestee_age                      , 9,  #65+
                  										arrestee_age_code %in% c("00","NS")         , 10, #Unknown or Not Specified
                                      default = 10 # Unknown
      ),

      der_arrestee_age_cat_1_2 = fcase( 0 <= der_arrestee_age  & der_arrestee_age < 18 , 1, #Juvenile
                                      18 <= der_arrestee_age                           , 2,  #Adult
                                      default = 3 # Unknown
      ),
      
      der_arrestee_age_cat_2_uo18 = fcase( 0 <= der_arrestee_age  & der_arrestee_age < 18 , 1, #Under 18
                                         18 <= der_arrestee_age                        , 2, #18+
                                         arrestee_age_code %in% c("00","NS")           , 3, #Unknown or Not Specified
                                         default = 3 # Unknown
      ),
      
      #Create a generic age variable for subsetting in demographic permutations.  Should have range of 0 - 99
      der_arrestee_age_round = floor(der_arrestee_age),
      
      der_arrestee_age_cat_under18_2 = fcase( 0 <= der_arrestee_age  & der_arrestee_age  < 12, 1, #Under 12
                                            12 <= der_arrestee_age  & der_arrestee_age < 18, 2 #12-17
      ),
	  
	  der_arrestee_age_cat_12_17_cat = fcase( 12 <= der_arrestee_age  & der_arrestee_age  < 15, 1, #12-14
                                            15 <= der_arrestee_age  & der_arrestee_age < 18, 2 #15-17
      )	  
	  
    )


  df9_recode <- df9_recode %>%
    mutate(
      der_arrestee_gender = fcase(trim_upper(arrestee_sex_code)  == "M", 1,
                                    trim_upper(arrestee_sex_code)  == "F", 2,
                                    trim_upper(arrestee_sex_code)  == "U", 3,
                                    default = 3 # Unknown
                                    ),
      
      der_arrestee_race = fcase(arrestee_race_code == "W", 1,  # White
                                arrestee_race_code == "B", 2,  # Black or African American
                                arrestee_race_code == "I", 3,  # American Indian or Alaskan Native
                                arrestee_race_code == "A", 4,  # Asian
                                arrestee_race_code == "AP", 4, # Asian, Native Hawaiian or Other Pacific Islander: Asian
                                arrestee_race_code == "C", 4,  # Chinese: Asian
                                arrestee_race_code == "J", 4,  # Japanese: Asian
                                arrestee_race_code == "P", 5,  # Native Hawaiian or Other Pacific Islander
                                arrestee_race_code == "U", 6,  # U - Unknown
                                default = 6                    # includes O (Other), M (Multiple), NS (Not Specified)
                              ),
      
      der_arrestee_ethnicity = fcase(arrestee_ethnicity_code == "H", 1, #Hispanic or Latino
                                     arrestee_ethnicity_code == "N", 2, #Not Hispanic or Latino
                                     default= 3),  #Multiple/Unknown/Not Specified	
      
      der_arrestee_ethnicity_race = fcase(
        arrestee_ethnicity_code == "H", 1, #  Hispanic or Latino
        arrestee_ethnicity_code == "N" & arrestee_race_code == "W", 2,  # Non-Hispanic, White
        arrestee_ethnicity_code == "N" & arrestee_race_code == "B", 3,  #  Non-Hispanic, Black
        arrestee_ethnicity_code == "N" & arrestee_race_code == "I", 4,  # Non-Hispanic, American Indian or Alaska Native
        arrestee_ethnicity_code == "N" & arrestee_race_code == "A", 5,  # Asian:  Non-Hispanic, Asian
        arrestee_ethnicity_code == "N" & arrestee_race_code == "AP", 5, # Asian, Native Hawaiian or Other Pacific Islander: Non-Hispanic, Asian
        arrestee_ethnicity_code == "N" & arrestee_race_code == "C", 5,  # Chinese: Non-Hispanic, Asian
        arrestee_ethnicity_code == "N" & arrestee_race_code == "J", 5,  # Japanese: Non-Hispanic, Asian
        arrestee_ethnicity_code == "N" & arrestee_race_code == "P", 6,  # Non-Hispanic, Native Hawaiian or Other Pacific Islander
        arrestee_ethnicity_code == "N" & arrestee_race_code == "U", 7,  # U - Unknown
        default = 7                    # includes O (Other), M (Multiple), NS (Not Specified)
      )
      
    )
    #Male
    #1   White
    #2   Black
    #3   American Indian or Alaska Native
    #4   Asian
    #5   Native Hawaiian or Other Pacific Islander
    #Female
    #6   White
    #7   Black
    #8   American Indian or Alaska Native
    #9   Asian
    #10   Native Hawaiian or Other Pacific Islander
  df9_recode <- df9_recode %>%
    mutate(
      der_arrestee_gender_race = (der_arrestee_gender - 1)*6 + der_arrestee_race,
      #Juvenile disposition
      der_juvenile_disp = fcase(

        trim_upcase(under_18_disposition_code) == "H", 1, #Handled within department
        trim_upcase(under_18_disposition_code) == "R", 2, #Referred to other authorities
        der_arrestee_age >= 18, 3, #Not applicable
        default = 4 #Unknown
      ),

      #Multiple arrest indicator
      der_multiple_arrest = fcase(

        trim_upcase(multiple_indicator) == "M", 1, #Multiple
        trim_upcase(multiple_indicator) == "C", 2, #Count
        trim_upcase(multiple_indicator) == "N", 3, #Not applicable
        default = NA_real_
      )

    )

  #Check recodes
  # df9_recode %>% checkfunction(der_arrestee_age_cat_1_2, der_arrestee_age_cat_15_17, der_arrestee_age_cat, der_arrestee_age, arrestee_age_code, arrestee_age_num)
  # df9_recode %>% checkfunction(der_arrestee_age_cat_2_uo18, der_arrestee_age, arrestee_age_code, arrestee_age_num)  
  # df9_recode %>% checkfunction(der_arrestee_age_cat_under18_2, der_arrestee_age, arrestee_age_code, arrestee_age_num) 
  # df9_recode %>% checkfunction(der_arrestee_age_round, der_arrestee_age, arrestee_age_code, arrestee_age_num)
  # df9_recode %>% checkfunction(der_arrestee_age_cat_12_17_cat, der_arrestee_age, arrestee_age_code, arrestee_age_num)
  # 
  # 
  # 
  # df9_recode %>% checkfunction(der_arrestee_gender, arrestee_sex_code)
  # df9_recode %>% checkfunction(der_arrestee_race, arrestee_race_code)
  # df9_recode %>% checkfunction(der_arrestee_ethnicity, arrestee_ethnicity_code)
  # df9_recode %>% checkfunction(der_arrestee_ethnicity_race, arrestee_ethnicity_code, arrestee_race_code)
  # df9_recode %>% checkfunction(der_arrestee_gender_race, der_arrestee_gender, der_arrestee_race)
  # df9_recode %>% checkfunction(der_juvenile_disp, under_18_disposition_code, der_arrestee_age)
  # df9_recode %>% checkfunction(der_multiple_arrest, multiple_indicator)
  
  #arrestee Age Category at arrestee Level

  NIBRS_count_agg_arrestee(data=df9_recode, var=der_arrestee_age_cat) %>%
  	write_csv(gzfile(paste0(der_file_path,"/agg_arrestee_age_cat_arrestee_imp.csv.gz")), na="")

  NIBRS_count_agg_arrestee(data=df9_recode, var=der_arrestee_age_cat_15_17) %>%
  	write_csv(gzfile(paste0(der_file_path,"/agg_arrestee_age_cat_15_17_arrestee_imp.csv.gz")), na="")
  
  NIBRS_count_agg_arrestee(data=df9_recode, var=der_arrestee_age_cat_2_uo18) %>%
    write_csv(gzfile(paste0(der_file_path,"/agg_arrestee_age_cat_2_uo18_arrestee_imp.csv.gz")), na="")  
  
  NIBRS_count_agg_arrestee(data=df9_recode, var=der_arrestee_age_cat_under18_2) %>%
    write_csv(gzfile(paste0(der_file_path,"/agg_arrestee_age_cat_under18_2_arrestee_imp.csv.gz")), na="")    
  
  NIBRS_count_agg_arrestee(data=df9_recode, var=der_arrestee_age_round) %>%
    write_csv(gzfile(paste0(der_file_path,"/agg_arrestee_age_round_arrestee_imp.csv.gz")), na="")     
	
  NIBRS_count_agg_arrestee(data=df9_recode, var=der_arrestee_age_cat_12_17_cat) %>%
    write_csv(gzfile(paste0(der_file_path,"/agg_arrestee_age_cat_12_17_cat_arrestee_imp.csv.gz")), na="")    	



  #arrestee Gender at arrestee Level

  NIBRS_count_agg_arrestee(data=df9_recode, var=der_arrestee_gender) %>%
  	write_csv(gzfile(paste0(der_file_path,"/agg_arrestee_gender_arrestee_imp.csv.gz")), na="")

  #arrestee Race at arrestee Level

  NIBRS_count_agg_arrestee(data=df9_recode, var=der_arrestee_race) %>%
  	write_csv(gzfile(paste0(der_file_path,"/agg_arrestee_race_arrestee_imp.csv.gz")), na="")
  
  #arrestee ethnicity at arrestee Level
  
  NIBRS_count_agg_arrestee(data=df9_recode, var=der_arrestee_ethnicity) %>%
    write_csv(gzfile(paste0(der_file_path,"/agg_arrestee_ethnicity_arrestee_imp.csv.gz")), na="")
  
  #arrestee ethnicity race at arrestee Level
  
  NIBRS_count_agg_arrestee(data=df9_recode, var=der_arrestee_ethnicity_race) %>%
    write_csv(gzfile(paste0(der_file_path,"/agg_arrestee_ethnicity_race_arrestee_imp.csv.gz")), na="")  
  

  #arrestee Sex and Race at arrestee Level

  NIBRS_count_agg_arrestee(data=df9_recode, var=der_arrestee_gender_race) %>%
  	write_csv(gzfile(paste0(der_file_path,"/agg_arrestee_gender_race_arrestee_imp.csv.gz")), na="")

  #arrestee Juvenile disposition at arrestee Level

  NIBRS_count_agg_arrestee(data=df9_recode, var=der_juvenile_disp) %>%
  	write_csv(gzfile(paste0(der_file_path,"/agg_juvenile_disp_arrestee_imp.csv.gz")), na="")

  #arrestee Multiple arrest indicator at arrestee Level

  NIBRS_count_agg_arrestee(data=df9_recode, var=der_multiple_arrest) %>%
  	write_csv(gzfile(paste0(der_file_path,"/agg_multiple_arrest_arrestee_imp.csv.gz")), na="")

  #Clear the objects and free up memory
  cleanup_memory()

}else if(DATASET_TO_GENERATE=="OFFENDERYOUTHTABLE"){
  #Now we need to process the offender data
  df6_raw_off <- fread(paste0(der_file_path, "raw_offender.csv.gz"), 
                       colClasses = list(character = c("offender_age_code")))

  df6_imputed_list_off <- list.files(path=item_imp_path, pattern="17_\\w+_offender_imputed_final_flag.csv.gz")
  log_debug("Merging list of imputed offender files",toString(df6_imputed_list_off))

  #Create list to hold files
  df6_imputed_off <- vector("list", length(df6_imputed_list_off))

  for(i in 1:length(df6_imputed_list_off)){

    df6_imputed_off[[i]] <- fread(paste0(item_imp_path, df6_imputed_list_off[[i]]), 
                                  colClasses = list(character = c("age_code_offender_raw", "age_code_offender_le"))) %>% 
      recode_all_race_ints_to_char()

  }

  offender_df6_imputed_final <- df6_imputed_off %>%
    bind_rows() %>%
    select(incident_id,
           offender_id,
           offender_sex_code = sex_code_offender_i,
           offender_race_code = race_code_offender_i,
           offender_age_num = age_num_offender_i)  
	
  gc(rm(list=c("df6_imputed_off", "df6_imputed_list_off")))
  
  #Create dataset 
  df6 <- replacedemovars2(base=df6_raw_off %>% mutate(offender_age_num = as.numeric(offender_age_num)), 
                          imputed=offender_df6_imputed_final, mergeonby=c("incident_id", "offender_id"))
  gc(rm(list=c("df6_raw_off", "offender_df6_imputed_final")))
  
  #Recode the offender variables
  df6_recode <- df6 %>%
      mutate(
        der_offender_age = case_when(!is.na(offender_age_num) ~ offender_age_num,
                                     offender_age_code %in% c("NN","NB","BB") ~ 0, #1: Under 24 Hours, 2: 1-6 Days Old, 3: 7-364 Days Old
                                     offender_age_code %in% c("99") ~ 99, #6: Over 98 Years Old
                                     offender_age_code %in% c("00","NS") ~ NA_real_, #4: Unknown or #0: Not Specified
                                     TRUE ~ as.double(offender_age_num)),
        
        der_unknown_offender_incident = fcase(offender_seq_num == 0, 1,
                                                  default= 0),

        der_offender_age_missing = fcase(is.na(der_offender_age) & 
                                             der_unknown_offender_incident == 0, 1, #Missing offender age
                                      default = 0),           
        
        der_offender_age_12_plus_missing_unk_inc = fcase(
          der_offender_age >= 12, 1, #Offender aged 12 or older
          der_offender_age_missing == 1, 1, #Offender age is unknown
          der_unknown_offender_incident == 1, 1, #Unknown offender incidents
          default = 0
    
        ),
        
    der_offender_cat_12_17 = fcase( 12 <= der_offender_age  & der_offender_age < 18,  1, #12-17
                                      default=0),
    
    der_offender_cat_18_plus = fcase(der_offender_age >= 18,  1, #18 or older
                                      default=0)   
    

        
  )  
  
  gc(rm(list=c("df6")))
  
  
  #Check the recodes
  # df6_recode %>% checkfunction(der_offender_age, offender_age_num, offender_age_code, offender_age_name)
  # df6_recode %>% checkfunction(der_unknown_offender_incident, offender_seq_num)
  # df6_recode %>% checkfunction(der_offender_age_missing, der_offender_age, der_unknown_offender_incident)
  # df6_recode %>% checkfunction(der_offender_age_12_plus_missing_unk_inc, der_offender_age, der_offender_age_missing, der_unknown_offender_incident)
  # df6_recode %>% checkfunction(der_offender_cat_12_17, der_offender_age)
  # df6_recode %>% checkfunction(der_offender_cat_18_plus, der_offender_age)
  # 
  
  
  #Using dataset df6_recode, need to summarise at the incident level
  
  #Incident level data with the following values:
  #1, #Unknown offender incidents
  
  NIBRS_count_agg_keep_level_1_count_1(data=df6_recode, var=der_unknown_offender_incident) %>% 
  	write_csv(gzfile(paste0(der_file_path,"/agg_unknown_offender_incident_inc_imp.csv.gz")), na="")    
  
  #Incident level data with the following values:
  #1, #Known offender age missing  
  
  NIBRS_count_agg_keep_level_1_count_1(data=df6_recode, var=der_offender_age_missing) %>% 
  	write_csv(gzfile(paste0(der_file_path,"/agg_offender_age_missing_inc_imp.csv.gz")), na="")    
  
  #Incident level data with the following values:
  # 1, #Offender aged 12 or older
  # 1, #Offender age is unknown
  # 1, #Unknown offender incidents
  
  NIBRS_count_agg_keep_level_1_count_1(data=df6_recode, var=der_offender_age_12_plus_missing_unk_inc) %>% 
  	write_csv(gzfile(paste0(der_file_path,"/agg_offender_age_12_plus_missing_unk_inc_inc_imp.csv.gz")), na="")  
  
  #Incident level data with the following values:
  #1, #12-17
  
  NIBRS_count_agg_keep_level_1_count_1(data=df6_recode, var=der_offender_cat_12_17) %>% 
  	write_csv(gzfile(paste0(der_file_path,"/agg_offender_cat_12_17_inc_imp.csv.gz")), na="")   
  
  #Incident level data with the following values:
  #1, #18 or older
  
  NIBRS_count_agg_keep_level_1_count_1(data=df6_recode, var=der_offender_cat_18_plus) %>% 
  	write_csv(gzfile(paste0(der_file_path,"/agg_offender_cat_18_plus_inc_imp.csv.gz")), na="")    
  
  

  #Clear the objects and free up memory
  cleanup_memory()
  
  #Remove any objects
  invisible(gc())
		   
       
  
 
} else if(DATASET_TO_GENERATE=="GROUPBARRESTEE"){
  #We can use the file raw_arrestee from the Raw Indicator Table task

  #df9_raw <- fread(paste0(der_file_path, "raw_arrestee.csv.gz")) %>% mutate(arrestee_age_num = as.numeric(arrestee_age_num))
  
  tbd_list_arrestee <- list.files(path=der_bystate_file_path, pattern= "raw_all_arrestee_group_b_\\w+\\.csv\\.gz")
  
  log_debug("Merging list of raw group b arrestee files",toString(tbd_list_arrestee))
  
  df9_raw <- map_dfr(tbd_list_arrestee, ~{
    
    returndata <- fread(paste0(der_bystate_file_path, .x), 
                        colClasses = list(character = c("age_code","arrest_number")))
    
    #Return the data
    return(returndata)
    
  }) %>%
    rename(
      arrestee_age_code = age_code,      
      arrestee_sex_code = sex_code,
      arrestee_race_code = race_code,
      arrestee_ethnicity_code = ethnicity_code
    ) %>%
	mutate(
	  #arrestee_age_num should only be a numeric age value and not the code
		arrestee_age_num = fcase(		
		   arrestee_age_code %in% c("NN","NB","BB"), NA_real_, #1: Under 24 Hours, 2: 1-6 Days Old, 3: 7-364 Days Old
		   arrestee_age_code %in% c("99"),  NA_real_, #6: Over 98 Years Old
		   arrestee_age_code %in% c("00","NS"),  NA_real_, #4: Unknown or #0: Not Specified						
		   !is.na(arrestee_age_code), as.numeric(arrestee_age_code)		   
		)
	)
  
  #Check recodes
  df9_raw %>% checkfunction(arrestee_age_num, arrestee_age_code)
  
  #Delete the tbd_list_arrestee list
  rm(tbd_list_arrestee)
  invisible(gc())  
  
  #Read in the imputed group b arrestee data - All the imputed data is on one file
  arrestee_df9_imputed_final <- fread(paste0(item_imp_path, "02_mice_group_b_arrestee.csv.gz")) %>%
    select(
      groupb_arrestee_id, 
      arrestee_age_num = age_num_i,      
      arrestee_sex_code = sex_code_i,
      arrestee_race_code = race_code_i,
      arrestee_ethnicity_code = ethnicity_code_i
    )
    
  # #Create dataset
  df9 <- replacedemovars2(base=df9_raw, imputed=arrestee_df9_imputed_final, mergeonby=c("groupb_arrestee_id"))
  
  #Create the demographics variables at the arrestee level
  log_debug("Right before all of the df9_recode recodes")
  df9_recode <- df9 %>%
    mutate(
      der_arrestee_age = case_when(!is.na(arrestee_age_num) ~ arrestee_age_num,
                                   arrestee_age_code %in% c("NN","NB","BB") ~ 0, #1: Under 24 Hours, 2: 1-6 Days Old, 3: 7-364 Days Old
                                   arrestee_age_code %in% c("99") ~ 99, #6: Over 98 Years Old
                                   arrestee_age_code %in% c("00","NS") ~ NA_real_, #4: Unknown or #0: Not Specified
                                   TRUE ~ as.double(arrestee_age_num)),
  )

  df9_recode <- df9_recode %>%
    mutate(
      der_arrestee_age_cat = fcase( 0 <= der_arrestee_age  & der_arrestee_age < 5 , 1, #Under 5
                                      5 <= der_arrestee_age  & der_arrestee_age < 15, 2, #5-14
                                      15 <= der_arrestee_age & der_arrestee_age < 18, 3, #15-17
                                      18 <= der_arrestee_age & der_arrestee_age < 25, 4, #18-24
                                      25 <= der_arrestee_age & der_arrestee_age < 35, 5, #25-34
                                      35 <= der_arrestee_age & der_arrestee_age < 65, 6, #35-64
                                      65 <= der_arrestee_age                      , 7,  #65+
                                      arrestee_age_code %in% c("00","NS")         , 8, #Unknown or Not Specified
                                      default = 8 # Unknown
      )
    )

  df9_recode <- df9_recode %>%
    mutate(
      der_arrestee_age_cat_15_17 = fcase( 0 <= der_arrestee_age  & der_arrestee_age < 5 , 1, #Under 5
                                      5 <= der_arrestee_age  & der_arrestee_age < 15, 2, #5-14
                                           der_arrestee_age                    == 15, 3, #15
                  										 der_arrestee_age  == 16, 4, #16
                  										 der_arrestee_age  == 17, 5, #17
                                      18 <= der_arrestee_age & der_arrestee_age < 25, 6, #18-24
                                      25 <= der_arrestee_age & der_arrestee_age < 35, 7, #25-34
                                      35 <= der_arrestee_age & der_arrestee_age < 65, 8, #35-64
                                      65 <= der_arrestee_age                      , 9,  #65+
                  										arrestee_age_code %in% c("00","NS")         , 10, #Unknown or Not Specified
                                      default = 10 # Unknown
      ),

      der_arrestee_age_cat_1_2 = fcase( 0 <= der_arrestee_age  & der_arrestee_age < 18 , 1, #Juvenile
                                      18 <= der_arrestee_age                           , 2,  #Adult
                                      default = 3 # Unknown
      ),
      
      der_arrestee_age_cat_2_uo18 = fcase( 0 <= der_arrestee_age  & der_arrestee_age < 18 , 1, #Under 18
                                         18 <= der_arrestee_age                        , 2, #18+
                                         arrestee_age_code %in% c("00","NS")           , 3, #Unknown or Not Specified
                                         default = 3 # Unknown
      ),
      
      #Create a generic age variable for subsetting in demographic permutations.  Should have range of 0 - 99
      der_arrestee_age_round = floor(der_arrestee_age),
      
      der_arrestee_age_cat_under18_2 = fcase( 0 <= der_arrestee_age  & der_arrestee_age  < 12, 1, #Under 12
                                            12 <= der_arrestee_age  & der_arrestee_age < 18, 2 #12-17
      ),
	  
	  der_arrestee_age_cat_12_17_cat = fcase( 12 <= der_arrestee_age  & der_arrestee_age  < 15, 1, #12-14
                                            15 <= der_arrestee_age  & der_arrestee_age < 18, 2 #15-17
      )	  
	  
    )


  df9_recode <- df9_recode %>%
    mutate(
      der_arrestee_gender = fcase(trim_upper(arrestee_sex_code)  == "M", 1,
                                    trim_upper(arrestee_sex_code)  == "F", 2,
                                    trim_upper(arrestee_sex_code)  == "U", 3,
                                    default = 3 # Unknown
                                    ),
      
      der_arrestee_race = fcase(arrestee_race_code == "W", 1,  # White
                                arrestee_race_code == "B", 2,  # Black or African American
                                arrestee_race_code == "I", 3,  # American Indian or Alaskan Native
                                arrestee_race_code == "A", 4,  # Asian
                                arrestee_race_code == "AP", 4, # Asian, Native Hawaiian or Other Pacific Islander: Asian
                                arrestee_race_code == "C", 4,  # Chinese: Asian
                                arrestee_race_code == "J", 4,  # Japanese: Asian
                                arrestee_race_code == "P", 5,  # Native Hawaiian or Other Pacific Islander
                                arrestee_race_code == "U", 6,  # U - Unknown
                                default = 6                    # includes O (Other), M (Multiple), NS (Not Specified)
                              ),
      
      der_arrestee_ethnicity = fcase(arrestee_ethnicity_code == "H", 1, #Hispanic or Latino
                                     arrestee_ethnicity_code == "N", 2, #Not Hispanic or Latino
                                     default= 3),  #Multiple/Unknown/Not Specified	
      
      der_arrestee_ethnicity_race = fcase(
        arrestee_ethnicity_code == "H", 1, #  Hispanic or Latino
        arrestee_ethnicity_code == "N" & arrestee_race_code == "W", 2,  # Non-Hispanic, White
        arrestee_ethnicity_code == "N" & arrestee_race_code == "B", 3,  #  Non-Hispanic, Black
        arrestee_ethnicity_code == "N" & arrestee_race_code == "I", 4,  # Non-Hispanic, American Indian or Alaska Native
        arrestee_ethnicity_code == "N" & arrestee_race_code == "A", 5,  # Asian:  Non-Hispanic, Asian
        arrestee_ethnicity_code == "N" & arrestee_race_code == "AP", 5, # Asian, Native Hawaiian or Other Pacific Islander: Non-Hispanic, Asian
        arrestee_ethnicity_code == "N" & arrestee_race_code == "C", 5,  # Chinese: Non-Hispanic, Asian
        arrestee_ethnicity_code == "N" & arrestee_race_code == "J", 5,  # Japanese: Non-Hispanic, Asian
        arrestee_ethnicity_code == "N" & arrestee_race_code == "P", 6,  # Non-Hispanic, Native Hawaiian or Other Pacific Islander
        arrestee_ethnicity_code == "N" & arrestee_race_code == "U", 7,  # U - Unknown
        default = 7                    # includes O (Other), M (Multiple), NS (Not Specified)
      )
      
    )
    #Male
    #1   White
    #2   Black
    #3   American Indian or Alaska Native
    #4   Asian
    #5   Native Hawaiian or Other Pacific Islander
    #Female
    #6   White
    #7   Black
    #8   American Indian or Alaska Native
    #9   Asian
    #10   Native Hawaiian or Other Pacific Islander
  df9_recode <- df9_recode %>%
    mutate(
      der_arrestee_gender_race = (der_arrestee_gender - 1)*6 + der_arrestee_race,
      #Juvenile disposition
      der_juvenile_disp = fcase(

        trim_upcase(under_18_disposition_code) == "H", 1, #Handled within department
        trim_upcase(under_18_disposition_code) == "R", 2, #Referred to other authorities
        der_arrestee_age >= 18, 3, #Not applicable
        default = 4 #Unknown
      )

      #Multiple arrest indicator
      # der_multiple_arrest = fcase(
      # 
      #   trim_upcase(multiple_indicator) == "M", 1, #Multiple
      #   trim_upcase(multiple_indicator) == "C", 2, #Count
      #   trim_upcase(multiple_indicator) == "N", 3, #Not applicable
      #   default = NA_real_
      # )

    )

  #Check recodes
  # df9_recode %>% checkfunction(der_arrestee_age_cat_1_2, der_arrestee_age_cat_15_17, der_arrestee_age_cat, der_arrestee_age, arrestee_age_code, arrestee_age_num)
  # df9_recode %>% checkfunction(der_arrestee_age_cat_2_uo18, der_arrestee_age, arrestee_age_code, arrestee_age_num)  
  # df9_recode %>% checkfunction(der_arrestee_age_cat_under18_2, der_arrestee_age, arrestee_age_code, arrestee_age_num) 
  # df9_recode %>% checkfunction(der_arrestee_age_round, der_arrestee_age, arrestee_age_code, arrestee_age_num)
  # df9_recode %>% checkfunction(der_arrestee_age_cat_12_17_cat, der_arrestee_age, arrestee_age_code, arrestee_age_num)
  # 
  # 
  # 
  # df9_recode %>% checkfunction(der_arrestee_gender, arrestee_sex_code)
  # df9_recode %>% checkfunction(der_arrestee_race, arrestee_race_code)
  # df9_recode %>% checkfunction(der_arrestee_ethnicity, arrestee_ethnicity_code)
  # df9_recode %>% checkfunction(der_arrestee_ethnicity_race, arrestee_ethnicity_code, arrestee_race_code)
  # df9_recode %>% checkfunction(der_arrestee_gender_race, der_arrestee_gender, der_arrestee_race)
  # df9_recode %>% checkfunction(der_juvenile_disp, under_18_disposition_code, der_arrestee_age)
  # df9_recode %>% checkfunction(der_multiple_arrest, multiple_indicator)
  
  #arrestee Age Category at arrestee Level

  NIBRS_count_agg_groupb_arrestee(data=df9_recode, var=der_arrestee_age_cat) %>%
  	write_csv(gzfile(paste0(der_file_path,"/agg_arrestee_age_cat_arrestee_groupb_imp.csv.gz")), na="")

  NIBRS_count_agg_groupb_arrestee(data=df9_recode, var=der_arrestee_age_cat_15_17) %>%
  	write_csv(gzfile(paste0(der_file_path,"/agg_arrestee_age_cat_15_17_arrestee_groupb_imp.csv.gz")), na="")
  
  NIBRS_count_agg_groupb_arrestee(data=df9_recode, var=der_arrestee_age_cat_2_uo18) %>%
    write_csv(gzfile(paste0(der_file_path,"/agg_arrestee_age_cat_2_uo18_arrestee_groupb_imp.csv.gz")), na="")  
  
  NIBRS_count_agg_groupb_arrestee(data=df9_recode, var=der_arrestee_age_cat_under18_2) %>%
    write_csv(gzfile(paste0(der_file_path,"/agg_arrestee_age_cat_under18_2_arrestee_groupb_imp.csv.gz")), na="")    
  
  NIBRS_count_agg_groupb_arrestee(data=df9_recode, var=der_arrestee_age_round) %>%
    write_csv(gzfile(paste0(der_file_path,"/agg_arrestee_age_round_arrestee_groupb_imp.csv.gz")), na="")     
	
  NIBRS_count_agg_groupb_arrestee(data=df9_recode, var=der_arrestee_age_cat_12_17_cat) %>%
    write_csv(gzfile(paste0(der_file_path,"/agg_arrestee_age_cat_12_17_cat_arrestee_groupb_imp.csv.gz")), na="")    	



  #arrestee Gender at arrestee Level

  NIBRS_count_agg_groupb_arrestee(data=df9_recode, var=der_arrestee_gender) %>%
  	write_csv(gzfile(paste0(der_file_path,"/agg_arrestee_gender_arrestee_groupb_imp.csv.gz")), na="")

  #arrestee Race at arrestee Level

  NIBRS_count_agg_groupb_arrestee(data=df9_recode, var=der_arrestee_race) %>%
  	write_csv(gzfile(paste0(der_file_path,"/agg_arrestee_race_arrestee_groupb_imp.csv.gz")), na="")
  
  #arrestee ethnicity at arrestee Level
  
  NIBRS_count_agg_groupb_arrestee(data=df9_recode, var=der_arrestee_ethnicity) %>%
    write_csv(gzfile(paste0(der_file_path,"/agg_arrestee_ethnicity_arrestee_groupb_imp.csv.gz")), na="")
  
  #arrestee ethnicity race at arrestee Level
  
  NIBRS_count_agg_groupb_arrestee(data=df9_recode, var=der_arrestee_ethnicity_race) %>%
    write_csv(gzfile(paste0(der_file_path,"/agg_arrestee_ethnicity_race_arrestee_groupb_imp.csv.gz")), na="")  
  

  #arrestee Sex and Race at arrestee Level

  NIBRS_count_agg_groupb_arrestee(data=df9_recode, var=der_arrestee_gender_race) %>%
  	write_csv(gzfile(paste0(der_file_path,"/agg_arrestee_gender_race_arrestee_groupb_imp.csv.gz")), na="")

  #arrestee Juvenile disposition at arrestee Level

  NIBRS_count_agg_groupb_arrestee(data=df9_recode, var=der_juvenile_disp) %>%
  	write_csv(gzfile(paste0(der_file_path,"/agg_juvenile_disp_arrestee_groupb_imp.csv.gz")), na="")

  #arrestee Multiple arrest indicator at arrestee Level

  # NIBRS_count_agg_groupb_arrestee(data=df9_recode, var=der_multiple_arrest) %>%
  # 	write_csv(gzfile(paste0(der_file_path,"/agg_multiple_arrest_arrestee_groupb_imp.csv.gz")), na="")

  #Clear the objects and free up memory
  cleanup_memory()

}else {
  log_error(paste0("ERROR: DATASET_TO_GENERATE was not a valid value:",DATASET_TO_GENERATE))
}
