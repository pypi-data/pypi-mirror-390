#####################List all the derived property variables######################
CONST_ALL_PROPERTY_LEVEL_RECODES <- c(
  paste0("der_property_cat_", c(1:10))
)

CONST_ALL_VICTIM_PROPERTY_OFFENSES <- c(
	"der_against_property",
	"der_arson",
	"der_bribery",
	"der_burglary_b_e",
	"der_counterf_forgery",
	"der_destruction_damage_vand",
	"der_embezzlement",
	"der_extortion_black_mail",
	"der_fraud_offenses",
	"der_larceny_theft",
	"der_motor_vehicle_theft",
	"der_stolen_property_offenses",
	"der_property_crime_all"
)

CONST_DRUG_SEIZED_CODE <- 222222222
##################################################################################


create_property_recodes <- function(indata){
  
  #Create the following variable
  #Note this is an RTI derived variable where the statistician categorize
  # 1-transportation
  # 2-building
  # 3-equipment
  # 4-money
  # 5-documents
  # 6-firearm
  # 7-agricultural
  # 8-drug/alcohol
  # 9-consumables
  # 10-other
  

	returndata <- indata %>%
	mutate(
		der_property_1_10 = fcase(
		
		prop_desc_code == 1, 1, #Aircraft:  transportation
		prop_desc_code == 2, 8, #Alcohol:  drug/alcohol
		prop_desc_code == 3, 1, #Automobile:  transportation
		prop_desc_code == 4, 1, #Bicycles:  transportation
		prop_desc_code == 5, 1, #Buses:  transportation
		prop_desc_code == 6, 9, #Clothes/ Furs:  consumables
		prop_desc_code == 7, 3, #Computer Hard/ Software:  equipment
		prop_desc_code == 8, 9, #Consumable Goods:  consumables
		prop_desc_code == 9, 4, #Credit/ Debit cards:  money
		prop_desc_code == 10, 8, #Drugs/ Narcotics:  drug/alcohol
		prop_desc_code == 11, 3, #Drug Equipment:  equipment
		prop_desc_code == 12, 3, #Farm Equipment:  equipment
		prop_desc_code == 13, 6, #Firearms:  firearm
		prop_desc_code == 14, 3, #Gambling Equipment:  equipment
		prop_desc_code == 15, 3, #Industrial Equipment:  equipment
		prop_desc_code == 16, 3, #Household Goods:  equipment
		prop_desc_code == 17, 4, #Jewelry/ Precious Metals:  money
		prop_desc_code == 18, 7, #Livestock:  agricultural
		prop_desc_code == 19, 9, #Merchandise:  consumables
		prop_desc_code == 20, 4, #Money:  money
		prop_desc_code == 21, 4, #Negotiable Instruments:  money
		prop_desc_code == 22, 4, #Non Negotiable Instruments:  money
		prop_desc_code == 23, 3, #Office Equipment:  equipment
		prop_desc_code == 24, 1, #Other Motor Vehicles:  transportation
		prop_desc_code == 25, 4, #Purse/ Wallet:  money
		prop_desc_code == 26, 3, #Radio/ TV/ VCR:  equipment
		prop_desc_code == 27, 3, #Recordings:  equipment
		prop_desc_code == 28, 1, #Recreational Vehicles:  transportation
		prop_desc_code == 29, 2, #Structure/ Single dwelling:  building
		prop_desc_code == 30, 2, #Structure/ Other residence:  building
		prop_desc_code == 31, 2, #Structure/ Other commercial:  building
		prop_desc_code == 32, 2, #Structure/ Other industrial:  building
		prop_desc_code == 33, 2, #Structure/ Public:  building
		prop_desc_code == 34, 2, #Structure/ Storage:  building
		prop_desc_code == 35, 2, #Structure/ Other:  building
		prop_desc_code == 36, 3, #Tools:  equipment
		prop_desc_code == 37, 1, #Trucks:  transportation
		prop_desc_code == 38, 1, #Vehicle Parts:  transportation
		prop_desc_code == 39, 1, #Watercraft:  transportation
		prop_desc_code == 41, 1, #Aircraft Parts/ Accessories:  transportation
		prop_desc_code == 42, 3, #Artistic Supplies/ Accessories:  equipment
		prop_desc_code == 43, 2, #Building Materials:  building
		prop_desc_code == 44, 3, #Camping/ Hunting/ Fishing Equipment/ Supplies:  equipment
		prop_desc_code == 45, 8, #Chemicals:  drug/alcohol
		prop_desc_code == 46, 4, #Collections/ Collectibles:  money
		prop_desc_code == 47, 7, #Crops:  agricultural
		prop_desc_code == 48, 5, #Documents/ Personal or Business:  documents
		prop_desc_code == 49, 6, #Explosives:  firearm
		prop_desc_code == 59, 6, #Firearm Accessories:  firearm
		prop_desc_code == 64, 9, #Fuel:  consumables
		prop_desc_code == 65, 5, #Identity Documents:  documents
		prop_desc_code == 66, 5, #Identity-Intangible:  documents
		prop_desc_code == 67, 3, #Law Enforcement Equipment:  equipment
		prop_desc_code == 68, 3, #Lawn/ Yard/ Garden Equipment:  equipment
		prop_desc_code == 69, 3, #Logging Equipment:  equipment
		prop_desc_code == 70, 3, #Medical/ Medical Lab Equipment:  equipment
		prop_desc_code == 71, 10, #Metals, Non-Precious:  other
		prop_desc_code == 72, 3, #Musical Instruments:  equipment
		prop_desc_code == 73, 7, #Pets:  agricultural
		prop_desc_code == 74, 3, #Photographic/ Optical Equipment:  equipment
		prop_desc_code == 75, 3, #Portable Electronic Communications:  equipment
		prop_desc_code == 76, 3, #Recreational/ Sports Equipment:  equipment
		prop_desc_code == 77, 10, #Other:  other
		prop_desc_code == 78, 1, #Trailers:  transportation
		prop_desc_code == 79, 1, #Watercraft Equipment/ Parts/ Accessories:  transportation
		prop_desc_code == 80, 6, #Weapons-Other:  firearm
		prop_desc_code == 88, 10, #Pending Inventory:  other
		prop_desc_code == 99, 10 #Special:  other
		)
	)
}

#Create a function to create the property categories indicator

create_property_incident_ind = function(indata){
  
  #Using raw_property2, need to create 0/1 indicator for the property categories 
  #Need to aggregate at the incident_id
  tbd_1 <- indata %>%
    #Drop the missing property levels
    filter(!is.na(der_property_1_10)) %>%
    group_by(incident_id, der_property_1_10) %>%
    summarise(
      der_property_counts = n()
    ) %>%
    ungroup() %>%
    #Create the indicator version
    mutate(
      der_property_counts_01 = fcase(
        der_property_counts == 0, 0, 
        der_property_counts >  0, 1 
      )
    )
  
  #Check the recodes
  tbd_1 %>% checkfunction(der_property_counts_01, der_property_counts)
  
  #Check the dim
  log_dim(indata)
  log_dim(tbd_1)
  
  #Next need to create indicator variables at the incident level
  tbd_2 <- tbd_1 %>%
    mutate(der_property_level = paste0("der_property_cat_", der_property_1_10) ) %>%
    select(incident_id , der_property_level, der_property_counts_01) %>%
    spread(key=der_property_level, value=der_property_counts_01)
  
  #Check the dim
  log_dim(tbd_2)
  log_dim(tbd_1)  
  
  #Need to make sure that all the variables are present and if not create them
  tbd_property_variables <- colnames(tbd_2) %>% 
    as_tibble() %>%
    #Keep the property variables
    mutate(der_keep = str_detect(string=value, pattern="^der_property_cat_\\d+")) %>%
    filter(der_keep == TRUE)
  
  tbd_property_variables_needed <- CONST_ALL_PROPERTY_LEVEL_RECODES %>%
    as_tibble() %>%
    anti_join(tbd_property_variables, by="value") %>%
    select(value) %>%
    pull()
  
  #Create a message
  #print(paste0("See the property variables that must be added for state:  ", input_state, " and year:  ", CONST_YEAR))
  #print(tbd_property_variables_needed)
  
  #Create tbd_3 and create the additional variables
  tbd_3 <- tbd_2
  
  #Check the dim
  log_dim(tbd_3)    
  log_dim(tbd_2)
  
  #Run this code if tbd_property_variables_needed is greater than 0
  
  if (length(tbd_property_variables_needed) > 0){
    
    #Loop thru the list and create the additional variables
    for(i in 1:length(tbd_property_variables_needed)){
      
      #Create the variable and 0 filled
      tbdvar <- tbd_property_variables_needed[[i]]
      
      #Print message 
      print(paste0("Creating variable ", tbdvar, " for state:  ", input_state, " and year:  ", CONST_YEAR))
      
      tbd_3 <- tbd_3 %>%
        mutate(
          !!(tbdvar %>% rlang:::parse_expr()) := 0
        )
      
      #Delete the tbdvar
      rm(tbdvar)
      invisible(gc())
      
      
    }
  }
  
  #Next using tbd_3, loop thru the main property variables and zero filled the 0/1 variable
  tbd_4 <- tbd_3 %>%
    mutate(
      #Create an indicator version of the variables
      across(
        .cols = any_of(CONST_ALL_PROPERTY_LEVEL_RECODES),
        .fns = ~{
          fcase(
            #If missing make 0
            is.na(.x), 0, 
            #Just in case, if 0 appears, keep as 0
            .x == 0, 0, 
            #Otherwise if the count is greater than 0 then create indicator of 1
            .x > 0, 1)
        },
        .names = "{.col}_ind"
      )
    ) %>%
    ungroup() %>%
    #Drop the original variables
    select( !!!paste0("-", CONST_ALL_PROPERTY_LEVEL_RECODES) %>% rlang:::parse_exprs() )
  
  #Check the dim
  log_dim(tbd_4)    
  log_dim(tbd_3)  
  
  #Return the data
  return(tbd_4)
  
}

#Create function to create the property loss value at the incident level 
#This function will do the following
#1.  First we will deduplicate any property values that are reported twice.  For example,
#a.  a property can be stolen and recovered.
#b.  a property can be both burned and vandalize
#Since the property is assigned a different property_id when a new property loss description is assigned
#The same property may have multiple records within an incident, if there is more than one loss description is reported for the same property.
#2.  After the dedeuplication, need to top code any property_value greater than 1,000,000 to 1,000,000.
#3.  For the unknown property value of $1.00 do the following:
#    a.  For property code of pending, keep as $1.00
#    b.  For all other property code, make missing
#4.  Code in the property that should be 0 if missing:
#     9,  #Credit/Debit Cards
#     22, #Nonnegotiable Instruments
#     48, #Documents–Personal or Business
#     65, #Identity Documents
#     66, #Identity–Intangible
#     77, #Other
#5.  Code the property values for the seized drugs from missing to 222,222,222
#6.  Once 1 - 5 is done, then do the following heirarchy
#    a.  If there are any legitimate values (i.e. greater than 1 and not the drug seized property of code 222,222,222) within incident_id, then sum up the legitimate values and this is the incident property value
#    b.  If there are any drug seized property of code 222,222,222, then make the incident property value to be 222,222,222
#    c.  If there are any pending property, then make the incident property value to be $1
#    d.  The remaining amounts should be missing, if so then leave as missing to be imputed



create_propertyloss_incident_ind = function(indata){

  #First step is to dedeuplicate any property values that are reported twice, but under different property losses
  #Create the recodes
  tbd_1 <- indata %>%
    #Drop if there is no property
    filter(!is.na(prop_desc_code) ) 
  
  #Check the dim
  log_dim(indata)   
  log_dim(tbd_1) 
  
  #Need to get aside any records where the only property loss is recovered for a property
  final_recovered_only <- tbd_1 %>%
    #Group by the property code
    group_by(incident_id, prop_desc_code) %>%
    #prop_loss_code == 5, "der_propertyloss_recovered", #Recovered
    mutate(der_any_recovered = any(prop_loss_code %in% c(5)),
           der_property_loss_numrecord = n()
           ) %>%
    ungroup() %>%
    #Filter to the records to keep
    #Property within an incident that is recovered and there the only loss record associated is recovered
    filter(der_any_recovered == TRUE & der_property_loss_numrecord == 1) %>%
    #Drop the variables
    select(-der_any_recovered, -der_property_loss_numrecord)
  
  #Check the dim
  log_dim(final_recovered_only)
  log_dim(tbd_1)
  
  
  
  #Using tbd_1, need to identify and deduplicate values within an incident id
  #Note can't use property_id, since this id has a different value for different 
  #prop_desc_code and prop_loss_code combination.  Will try to identify with prop_desc_code
  
  #First need to drop off the "Recovered" loss code since it is often reported with "Stolen/Etc" loss code
  #Also drop the none and unknown codes
  tbd_1_2 <- tbd_1 %>%
    #prop_loss_code == 1, "der_propertyloss_none", #None
    #prop_loss_code == 5, "der_propertyloss_recovered", #Recovered
    #prop_loss_code == 8, "der_propertyloss_unknown" #Unknown
    filter(!prop_loss_code %in% c(1, 5, 8))
    
  #Check the dim
  log_dim(tbd_1_2)
  log_dim(tbd_1)
  
  #Using tbd_1_2, need to identify if there are distinct loss codes
  tbd_1_3 <- tbd_1_2 %>%
    group_by(incident_id) %>%
    mutate(der_distinct_proploss = n_distinct(prop_loss_code) ) %>%
    ungroup()
  
  #Need to separate out the property loss
  final_prop_loss_1   <- tbd_1_3 %>% filter(der_distinct_proploss == 1) 
  tbd_prop_loss_mt1   <- tbd_1_3 %>% filter(der_distinct_proploss > 1) 
  
  #Check the dimension
  log_dim(tbd_1_3)
  log_dim(final_prop_loss_1)
  log_dim(tbd_prop_loss_mt1)
  
  #Using tbd_prop_loss_mt1, need to identify if there are more than one loss code for the same property category
  tbd_prop_loss_mt1_2 <- tbd_prop_loss_mt1 %>%
    group_by(incident_id, prop_desc_code) %>%
    mutate(der_inc_property_count = n() ) %>%
    ungroup()
  
  #Need to split out the tbd_prop_loss_mt1_2
  final_oneproperty   <- tbd_prop_loss_mt1_2 %>% filter(der_inc_property_count == 1) 
  tbd_mtoneproperty   <- tbd_prop_loss_mt1_2 %>% filter(der_inc_property_count > 1)  
  
  #Check the dimension
  log_dim(tbd_prop_loss_mt1_2)
  log_dim(final_oneproperty)
  log_dim(tbd_mtoneproperty)  
  
  #Using tbd_mtoneproperty, need to deduplicate if they have the same value
  final_mtoneproperty <- tbd_mtoneproperty %>%
    group_by(incident_id, prop_desc_code, property_value) %>%
    mutate(tbd_row_number = row_number() == 1) %>%
    ungroup() %>%
    #Keep one record
    filter(tbd_row_number == TRUE) %>%
    #Drop the tbd_row_number variable
    select(-tbd_row_number)
  
  #Check the dimension
  log_dim(final_mtoneproperty)
  log_dim(tbd_mtoneproperty)
  
  #Next need to stack the data together for the property value using the following data
  #final_mtoneproperty
  #final_oneproperty
  #final_prop_loss_1
  
  #Create the property value
  main_property_value_stack <- bind_rows(
    final_mtoneproperty,
    final_oneproperty,
    final_prop_loss_1,
    final_recovered_only
  )
  
  #Check the dimension
  log_dim(tbd_1)
  log_dim(tbd_1_2)
  log_dim(main_property_value_stack)
  log_dim(final_mtoneproperty)
  log_dim(final_oneproperty)
  log_dim(final_prop_loss_1)
  log_dim(final_recovered_only)
  
  #Delete the tbd and final dataset, but use main_property_value_stack for next round of recodes
  rm(list=ls(pattern="tbd_"))
  rm(list=ls(pattern="final_"))
  
  #Using main_property_value_stack, create a clean_property_value
  main_property_value_stack2 <- main_property_value_stack %>%
    mutate(
      one = 1,
      
      #Code the property that should be 0
      tbd_mandatory_property0 = fcase(
        prop_desc_code %in% c(
          9,  #Credit/Debit Cards
          22, #Nonnegotiable Instruments
          48, #Documents–Personal or Business
          65, #Identity Documents
          66 #Identity–Intangible
        ), 1, 
        default = 0),    
      
      tbd_other_property0 = fcase(
        prop_desc_code %in% c(
          77  #Other
        ), 1, 
        default = 0),         
      
      tbd_drug_seized = fcase(
        prop_desc_code %in% c(
          10 #Drugs/Narcotics
        ) &
        prop_loss_code == 6, 1, #Seized
        default= 0
      ),
      
      tbd_property_pending = fcase(
        prop_desc_code %in% c(
          88 #Pending Inventory
        ), 1, 
        default= 0
      ),      
      
      clean_property_value = fcase(
        #If the tbd_mandatory_property0 == 1 and is missing, change to 0
        tbd_mandatory_property0 == 1 & is.na(property_value), 0, 
        tbd_other_property0 == 1 & is.na(property_value), 0, 
        
        #If the property_value is $1.00 for unknown then make missing if it is not
        #Inventory pending
        property_value == 1 & tbd_property_pending == 0, NA_real_,
        #Top code the property value to 1,000,000
        property_value >= 1000000, 1000000,
        #Recode the drug seized incidents to have a value of 222,222,222 if property value is  missing
        tbd_drug_seized == 1 & is.na(property_value), CONST_DRUG_SEIZED_CODE,
        #Otherwise keep values the same
        one == 1, as.double(property_value)
      ),
      
      #Create a version of clean_property_value that does not include the 
      #unknown value of $1.00 from pending inventory
      #and the CONST_DRUG_SEIZED_CODE seized code
      clean_property_value_known = fcase(
        clean_property_value == 1 | clean_property_value == CONST_DRUG_SEIZED_CODE, NA_real_,
        one == 1, clean_property_value
      )
      
    )
  
  #Check the recodes
  main_property_value_stack2 %>% checkfunction(tbd_mandatory_property0, prop_desc_code, prop_desc_name)
  main_property_value_stack2 %>% checkfunction(tbd_other_property0, prop_desc_code, prop_desc_name) 
  main_property_value_stack2 %>% checkfunction(tbd_drug_seized, prop_desc_code, prop_desc_name, prop_loss_code, prop_loss_name)
  main_property_value_stack2 %>% checkfunction(tbd_property_pending, prop_desc_code, prop_desc_name)
  main_property_value_stack2 %>% checkfunction(clean_property_value, tbd_mandatory_property0, tbd_other_property0, tbd_property_pending, tbd_drug_seized, property_value)
  main_property_value_stack2 %>% checkfunction(clean_property_value_known, clean_property_value)
  
  #Using main_property_value_stack2, need to look at the incident level to determine which values to use
  main_property_value_stack3 <- main_property_value_stack2 %>%
    group_by(incident_id) %>%
    mutate(
      #Known property values are not the unknown pending and the CONST_DRUG_SEIZED_CODE
      any_known_value = fcase(
        any(clean_property_value >= 0 & !(clean_property_value %in% c(CONST_DRUG_SEIZED_CODE, 1))), 1, 
        default = 0),
      
      any_drugseized = fcase(
        any(tbd_drug_seized == 1), 1, 
        default = 0),      
      
      any_pending = fcase(
        any(tbd_property_pending == 1), 1, 
        default = 0)
      ) %>%
    ungroup() 
  
  #Look at the recode at the incident level
  main_property_value_stack3 %>% checkfunction(any_known_value, any_drugseized, any_pending)
  #Check to see if remaining cases if property values are blank
  main_property_value_stack3 %>%
    filter(any_known_value == 0 & any_drugseized == 0 & any_pending == 0) %>% 
    checkfunction(property_value, clean_property_value)
  
  #Look at the dimension
  log_dim(main_property_value_stack3)
  log_dim(main_property_value_stack2)
  
  #Using main_property_value_stack3, sum up the values at the incident id level and 
  #the incident level variables to determine which variables to use
  main_property_value_stack4 <- main_property_value_stack3 %>%
    group_by(incident_id, any_known_value, any_drugseized, any_pending) %>%
    summarise(
      total_clean_property_value_known = sum(clean_property_value_known, na.rm=TRUE)
    ) %>%
    ungroup() %>%
    #Create the version of the property to use based on the heirarchy rule
    #    a.  If there are any legitimate values (i.e. greater than 1 and not the drug seized property of code 222,222,222) within incident_id, then sum up the legitimate values and this is the incident property value
    #    b.  If there are any drug seized property of code 222,222,222, then make the incident property value to be 222,222,222
    #    c.  If there are any pending property, then make the incident property value to be $1
    #    d.  The remaining amounts should be missing, if so then leave as missing to be imputed  
    mutate(
      der_final_property_value = fcase(
        any_known_value == 1, total_clean_property_value_known,
        any_drugseized  == 1, CONST_DRUG_SEIZED_CODE,
        any_pending     == 1, 1,
        default = NA_real_
      )
    )

  #Look at the dimension
  log_dim(main_property_value_stack4)
  log_dim(main_property_value_stack3)
  
  #Check the recodes
  main_property_value_stack4 %>% checkfunction(der_final_property_value, any_known_value, any_drugseized, any_pending, total_clean_property_value_known)
    
  #Return the dataset with the final property values
  return(
    main_property_value_stack4 %>%
      select(incident_id, der_final_property_value)
  )

}

#Create the additional offense recodes
#Write the function for common offense recode

property_offense_recode <- function(data){
  
  returndata <- data %>% mutate(
    
    der_against_property = fcase(
      #20210804 Do not include arson in total property crime
      #20230703 Include arson in  total property crime
      #trim_upcase(offense_code) %in% c("200"), 0, #200	Arson
      trim_upcase(crime_against) == "PROPERTY", 1,
      default = 0),    
    
    der_arson	= fcase(
      trim_upcase(offense_code) %in% c("200"), 1,
      default = 0),    
    
    der_bribery	= fcase(
      trim_upcase(offense_code) %in% c("510"), 1,
      default = 0),
    
    der_burglary_b_e	= fcase(
      trim_upcase(offense_code) %in% c("220"), 1,
      default = 0),
    
    der_counterf_forgery	= fcase(
      trim_upcase(offense_code) %in% c("250"), 1,
      default = 0),
    
    der_destruction_damage_vand	= fcase(
      trim_upcase(offense_code) %in% c("290"), 1,
      default = 0),
    
    der_embezzlement	= fcase(
      trim_upcase(offense_code) %in% c("270"), 1,
      default = 0),
    
    der_extortion_black_mail	= fcase(
      trim_upcase(offense_code) %in% c("210"), 1,
      default = 0),
    
    der_fraud_offenses	= fcase(
      #20231117:  Include "26F","26G" per FBI instructions from quarterly estimates to main system																							
      trim_upcase(offense_code) %in% c("26A", "26B","26C","26D","26E", "26F","26G"), 1,
      default = 0),
    
    der_larceny_theft	= fcase(
      trim_upcase(offense_code) %in% c("23A","23B","23C","23D","23E","23F","23G","23H"), 1,
      default = 0),
    
    der_motor_vehicle_theft	= fcase(
      trim_upcase(offense_code) %in% c("240"), 1,
      default = 0),
    
    der_stolen_property_offenses	= fcase(
      trim_upcase(offense_code) %in% c("280"), 1,
      default = 0),
    
    #This indicator includes MVT
    der_property_crime_all  = fcase(
      trim_upcase(offense_code) %in%
        c("220", #220 Burglary/Breaking & Entering
          #####larceny-theft#########################
          "23A", #23A Pocket-picking
          "23B", #23B Purse-snatching
          "23C", #23C Shoplifting
          "23D", #23D Theft From Building
          "23E", #23E Theft From Coin-Operated Machine or Device
          "23F", #23F Theft From Motor Vehicle
          "23G", #23G Theft of Motor Vehicle Parts or Accessories
          "23H", #23H All Other Larceny
          #20231117 - per FBI's instructions from quarterly estimates remove code since it does not exist in NIBRS																								  
          #"23*", #23* Not Specified
          ###########################################
          "240" #240 Motor Vehicle Theft
        ), 1,
      default = 0)    
    
  )  
    
  return(returndata)
  
}

create_propertyoffense_incidentvictim_ind = function(indata){
  
  tbd_1 <- indata %>%
    #Need to aggregate to the incident and victim level
    group_by(incident_id, victim_id) %>%
    summarise(
      across(
        .cols = any_of(CONST_ALL_VICTIM_PROPERTY_OFFENSES),
        .fns = ~{
          sum(.x, na.rm = TRUE)
        }
      )  
    ) %>%
    ungroup() 
  
  #Check the dimension
  log_dim(tbd_1)
  log_dim(indata)
  
  #Next need to create the indicator version
  tbd_2 <- tbd_1 %>%
    mutate(
      across(
        .cols = any_of(CONST_ALL_VICTIM_PROPERTY_OFFENSES),
        .fns = ~{
          fcase(.x > 0, 1, #if sum if greater than 0, create indicator of 1 
                default = 0) #Otherwise 0
        },
        .names = "{.col}_offense"
      )  
    ) %>%
    #Drop the original variables
    select(!!!(paste0("-", CONST_ALL_VICTIM_PROPERTY_OFFENSES) %>% rlang:::parse_exprs() ))
  
  #Check the dimension
  log_dim(tbd_2)
  log_dim(tbd_1)  
  
  #Return the data
  return(tbd_2)

  
}







