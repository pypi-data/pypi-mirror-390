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
    der_victim_age_cat %in% c(1:8),  der_victim_age_cat + 2,
    
    der_victim_age_cat_2_uo18 %in% c(1),  11, #Under 18
    der_victim_age_cat_under18_2 %in% c(1:2),  der_victim_age_cat_under18_2 + 11,
    der_victim_age_cat_2_uo18 %in% c(2:3),  der_victim_age_cat_2_uo18 + 12, #18+ and unknown
    
    der_number_of_victims_cat %in% c(1:4),  der_number_of_victims_cat + 15,
    der_victim_gender %in% c(1:3),  der_victim_gender + 19,
    der_victim_race %in% c(1:6),  der_victim_race + 22,
    der_inc_number_of_victims_cat %in% c(1:4),  der_inc_number_of_victims_cat + 28,
    der_victim_murder_non_neg_manslaughter %in% c(1:2),  der_victim_murder_non_neg_manslaughter + 32,
    der_number_of_victims_firearm_cat %in% c(1:4), der_number_of_victims_firearm_cat + 34,
    
    der_injury_hierarchy %in% c(1:5), der_injury_hierarchy + 38,
    der_injury_hierarchy2 %in% c(1:6), der_injury_hierarchy2 + 43,
    der_relationship_hierarchy %in% c(1:8), der_relationship_hierarchy + 49,
    der_relationship_hierarchy_victim_known %in% c(1:6), der_relationship_hierarchy_victim_known + 57,
    
    #Victim Hispanic Origin
    der_victim_ethnicity %in% c(1:3), der_victim_ethnicity + 63,
    
    #Victim race and Hispanic Origin
    der_victim_ethnicity_race %in% c(1:7), der_victim_ethnicity_race + 66    
    

  )

  )
  
  return(returndata)
}

assign_section <- function(data){
  log_debug("Running assign_section function")

  returndata <- data %>% mutate(

  section = fcase(
    row %in% c(1:2),  1,
    row %in% c(3:10),  2,
    row %in% c(11:15),  3,
    row %in% c(16:19),  4,
    row %in% c(20:22),  5,
    row %in% c(23:28),  6,
    row %in% c(29:32),  7,
    row %in% c(33:34),  8,
    row %in% c(35:38),  9,
    row %in% c(39:43),  10,
    row %in% c(44:49),  11,
    row %in% c(50:57),  12,
    row %in% c(58:63),  13,
    row %in% c(64:66),  14,
    row %in% c(67:73),  15
  )
  )   

  return(returndata)

}


#New add on code for labels
assign_labels <- function(data){
  log_debug("Running assign_labels function")

  returndata <- data %>% mutate(

  estimate_domain = fcase(

    row == 1 , 'Known Victim count',
    row == 2 , 'Known Victim rate (per 100k total pop)',
    row == 3 , 'Victim Age: Under 5',
    row == 4 , 'Victim Age: 5-14',
    row == 5 , 'Victim Age: 15-17',
    row == 6 , 'Victim Age: 18-24',
    row == 7 , 'Victim Age: 25-34',
    row == 8 , 'Victim Age: 35-64',
    row == 9 , 'Victim Age: 65+',
    row == 10 , 'Victim Age: Unknown',
    row == 11 , 'Victim age 2: Under 18',
    row == 12 , 'Victim age 2: Under 12',
    row == 13 , 'Victim age 2: 12-17',
    row == 14 , 'Victim age 2: 18+',
    row == 15 , 'Victim age 2: Unknown',
    row == 16 , 'Number of Victims: 1',
    row == 17 , 'Number of Victims: 2',
    row == 18 , 'Number of Victims: 3',
    row == 19 , 'Number of Victims: 4+',
    row == 20 , 'Victim sex: Male',
    row == 21 , 'Victim sex: Female',
    row == 22 , 'Victim sex: Unknown',
    row == 23 , 'Victim race: White',
    row == 24 , 'Victim race: Black',
    row == 25 , 'Victim race: American Indian or Alaska Native',
    row == 26 , 'Victim race: Asian',
    row == 27 , 'Victim race: Native Hawaiian or Other Pacific Islander',
    row == 28 , 'Victim race: Unknown',
    row == 29 , 'Number of Victims Summarized at Incident Level: 1',
    row == 30 , 'Number of Victims Summarized at Incident Level: 2',
    row == 31 , 'Number of Victims Summarized at Incident Level: 3',
    row == 32 , 'Number of Victims Summarized at Incident Level: 4+',
    row == 33 , 'Number of Victims Murdered: Yes',
    row == 34 , 'Number of Victims Murdered: No',
    row == 35 , 'Number of Firearm Victims: 1',
    row == 36 , 'Number of Firearm Victims: 2',
    row == 37 , 'Number of Firearm Victims: 3',
    row == 38 , 'Number of Firearm Victims: 4+',
    
    row == 39 , 'Injury hierarchy : Murder and Non-negligent Manslaughter, Negligent Manslaughter',
    row == 40 , 'Injury hierarchy : Major injury (other major injury, severe laceration, possible internal injury, gunshot wound)',
    row == 41 , 'Injury hierarchy : Unconsciousness, apparent broken bones, loss of teeth',
    row == 42 , 'Injury hierarchy : Apparent minor injury',
    row == 43 , 'Injury hierarchy : No injury',
    row == 44 , 'Injury hierarchy 2: Murder and Non-negligent Manslaughter, Negligent Manslaughter',
    row == 45 , 'Injury hierarchy 2: Other major injury, gunshot wound',
    row == 46 , 'Injury hierarchy 2: Severe laceration, possible internal injury',
    row == 47 , 'Injury hierarchy 2: Unconsciousness, apparent broken bones, loss of teeth',
    row == 48 , 'Injury hierarchy 2: Apparent minor injury',
    row == 49 , 'Injury hierarchy 2: No injury',
    row == 50 , 'Victim-offender relationship hierarchy: Intimate partner',
    row == 51 , 'Victim-offender relationship hierarchy: Other family',
    row == 52 , 'Victim-offender relationship hierarchy: Outside family but known to victim',
    row == 53 , 'Victim-offender relationship hierarchy: Stranger',
    row == 54 , 'Victim-offender relationship hierarchy: Victim was Offender',
    row == 55 , 'Victim-offender relationship hierarchy: Unknown relationship',
    row == 56 , 'Victim-offender relationship hierarchy: Unknown Offender Incidents',
    row == 57 , 'Victim-offender relationship hierarchy: Missing from Uncleared Incidents',
    row == 58 , 'Victim-offender relationship hierarchy among known offenders: Intimate partner',
    row == 59 , 'Victim-offender relationship hierarchy among known offenders: Other family',
    row == 60 , 'Victim-offender relationship hierarchy among known offenders: Outside family but known to victim',
    row == 61 , 'Victim-offender relationship hierarchy among known offenders: Stranger',
    row == 62 , 'Victim-offender relationship hierarchy among known offenders: Victim was Offender',
    row == 63 , 'Victim-offender relationship hierarchy among known offenders: Unknown relationship',
    
    row == 64 , 'Victim Hispanic Origin: Hispanic or Latino',
    row == 65 , 'Victim Hispanic Origin: Not Hispanic or Latino',
    row == 66 , 'Victim Hispanic Origin: Unknown',
    row == 67 , 'Victim race and Hispanic Origin: Hispanic or Latino',
    row == 68 , 'Victim race and Hispanic Origin: Non-Hispanic, White',
    row == 69 , 'Victim race and Hispanic Origin: Non-Hispanic, Black',
    row == 70 , 'Victim race and Hispanic Origin: Non-Hispanic, American Indian or Alaska Native',
    row == 71 , 'Victim race and Hispanic Origin: Non-Hispanic, Asian',
    row == 72 , 'Victim race and Hispanic Origin: Non-Hispanic, Native Hawaiian or Other Pacific Islander',
    row == 73 , 'Victim race and Hispanic Origin: Unknown race or Hispanic origin'
    

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

  full_table = "TableGV2a-Victim",
  table = DER_TABLE_NAME
  )

  return(returndata)

}

estimate_type_detail_percentage_label <- function(indata){
  log_debug("Running estimate_type_detail_percentage_label function")

  returndata <- indata %>%
    mutate(
      estimate_type_detail_percentage = fcase(

        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 1 , 'Victim Level', #Known Victim count
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 2 , 'Victim Level', #Known Victim rate (per 100k total pop)
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 3 , 'Victim Level', #Victim Age: Under 5
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 4 , 'Victim Level', #Victim Age: 5-14
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 5 , 'Victim Level', #Victim Age: 15-17
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 6 , 'Victim Level', #Victim Age: 18-24
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 7 , 'Victim Level', #Victim Age: 25-34
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 8 , 'Victim Level', #Victim Age: 35-64
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 9 , 'Victim Level', #Victim Age: 65+
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 10 , 'Victim Level', #Victim Age: Unknown
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 11 , 'Victim Level', #Victim age 2: Under 18
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 12 , 'Victim Level subset to Under 18', #Victim age 2: Under 12
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 13 , 'Victim Level subset to Under 18', #Victim age 2: 12-17
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 14 , 'Victim Level', #Victim age 2: 18+
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 15 , 'Victim Level', #Victim age 2: Unknown
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 16 , 'Victim Level', #Number of Victims: 1
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 17 , 'Victim Level', #Number of Victims: 2
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 18 , 'Victim Level', #Number of Victims: 3
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 19 , 'Victim Level', #Number of Victims: 4+
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 20 , 'Victim Level', #Victim sex: Male
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 21 , 'Victim Level', #Victim sex: Female
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 22 , 'Victim Level', #Victim sex: Unknown
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 23 , 'Victim Level', #Victim race: White
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 24 , 'Victim Level', #Victim race: Black
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 25 , 'Victim Level', #Victim race: American Indian or Alaska Native
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 26 , 'Victim Level', #Victim race: Asian
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 27 , 'Victim Level', #Victim race: Native Hawaiian or Other Pacific Islander
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 28 , 'Victim Level', #Victim race: Unknown
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 29 , 'Incident Level', #Number of Victims Summarized at Incident Level: 1
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 30 , 'Incident Level', #Number of Victims Summarized at Incident Level: 2
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 31 , 'Incident Level', #Number of Victims Summarized at Incident Level: 3
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 32 , 'Incident Level', #Number of Victims Summarized at Incident Level: 4+
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 33 , 'Victim Level', #Number of Victims Murdered: Yes
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 34 , 'Victim Level', #Number of Victims Murdered: No
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 35 , 'Victim Level', #Number of Firearm Victims: 1
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 36 , 'Victim Level', #Number of Firearm Victims: 2
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 37 , 'Victim Level', #Number of Firearm Victims: 3
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 38 , 'Victim Level', #Number of Firearm Victims: 4+
        
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 39 , 'Victim Level', #Injury hierarchy : Murder and Non-negligent Manslaughter, Negligent Manslaughter
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 40 , 'Victim Level', #Injury hierarchy : Major injury (other major injury, severe laceration, possible internal injury)
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 41 , 'Victim Level', #Injury hierarchy : Unconsciousness, apparent broken bones, loss of teeth
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 42 , 'Victim Level', #Injury hierarchy : Apparent minor injury
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 43 , 'Victim Level', #Injury hierarchy : No injury
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 44 , 'Victim Level', #Injury hierarchy 2: Murder and Non-negligent Manslaughter, Negligent Manslaughter
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 45 , 'Victim Level', #Injury hierarchy 2: Other major injury
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 46 , 'Victim Level', #Injury hierarchy 2: Severe laceration, possible internal injury
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 47 , 'Victim Level', #Injury hierarchy 2: Unconsciousness, apparent broken bones, loss of teeth
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 48 , 'Victim Level', #Injury hierarchy 2: Apparent minor injury
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 49 , 'Victim Level', #Injury hierarchy 2: No injury
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 50 , 'Victim Level', #Victim-offender relationship hierarchy: Intimate partner
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 51 , 'Victim Level', #Victim-offender relationship hierarchy: Other family
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 52 , 'Victim Level', #Victim-offender relationship hierarchy: Outside family but known to victim
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 53 , 'Victim Level', #Victim-offender relationship hierarchy: Stranger
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 54 , 'Victim Level', #Victim-offender relationship hierarchy: Victim was Offender
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 55 , 'Victim Level', #Victim-offender relationship hierarchy: Unknown relationship
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 56 , 'Victim Level', #Victim-offender relationship hierarchy: Unknown Offender Incidents
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 57 , 'Victim Level', #Victim-offender relationship hierarchy: Missing from Uncleared Incidents
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 58 , 'Victim Level', #Victim-offender relationship hierarchy among known offenders: Intimate partner
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 59 , 'Victim Level', #Victim-offender relationship hierarchy among known offenders: Other family
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 60 , 'Victim Level', #Victim-offender relationship hierarchy among known offenders: Outside family but known to victim
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 61 , 'Victim Level', #Victim-offender relationship hierarchy among known offenders: Stranger
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 62 , 'Victim Level', #Victim-offender relationship hierarchy among known offenders: Victim was Offender
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 63 , 'Victim Level', #Victim-offender relationship hierarchy among known offenders: Unknown relationship
        
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 64 , 'Victim Level', #Victim Hispanic Origin: Hispanic or Latino
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 65 , 'Victim Level', #Victim Hispanic Origin: Not Hispanic or Latino
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 66 , 'Victim Level', #Victim Hispanic Origin: Unknown
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 67 , 'Victim Level', #Victim race and Hispanic Origin: Hispanic or Latino
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 68 , 'Victim Level', #Victim race and Hispanic Origin: Non-Hispanic, White
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 69 , 'Victim Level', #Victim race and Hispanic Origin: Non-Hispanic, Black
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 70 , 'Victim Level', #Victim race and Hispanic Origin: Non-Hispanic, American Indian or Alaska Native
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 71 , 'Victim Level', #Victim race and Hispanic Origin: Non-Hispanic, Asian
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 72 , 'Victim Level', #Victim race and Hispanic Origin: Non-Hispanic, Native Hawaiian or Other Pacific Islander
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 73 , 'Victim Level' #Victim race and Hispanic Origin: Unknown race or Hispanic origin
        
        
           
  ))

  return(returndata)
}

estimate_type_detail_rate_label <- function(indata){
  log_debug("Running estimate_type_detail_rate_label function")

  returndata <- indata %>%
    mutate(
      estimate_type_detail_rate = fcase(
    
        trim_upcase(estimate_type) %in% c('RATE') & row == 1 , DER_NA_CODE_STRING, #Known Victim count
        trim_upcase(estimate_type) %in% c('RATE') & row == 2 , 'Victim rate per 100,000 persons', #Known Victim rate (per 100k total pop)
        trim_upcase(estimate_type) %in% c('RATE') & row == 3 , DER_NA_CODE_STRING, #Victim Age: Under 5
        trim_upcase(estimate_type) %in% c('RATE') & row == 4 , DER_NA_CODE_STRING, #Victim Age: 5-14
        trim_upcase(estimate_type) %in% c('RATE') & row == 5 , DER_NA_CODE_STRING, #Victim Age: 15-17
        trim_upcase(estimate_type) %in% c('RATE') & row == 6 , DER_NA_CODE_STRING, #Victim Age: 18-24
        trim_upcase(estimate_type) %in% c('RATE') & row == 7 , DER_NA_CODE_STRING, #Victim Age: 25-34
        trim_upcase(estimate_type) %in% c('RATE') & row == 8 , DER_NA_CODE_STRING, #Victim Age: 35-64
        trim_upcase(estimate_type) %in% c('RATE') & row == 9 , DER_NA_CODE_STRING, #Victim Age: 65+
        trim_upcase(estimate_type) %in% c('RATE') & row == 10 , DER_NA_CODE_STRING, #Victim Age: Unknown
        trim_upcase(estimate_type) %in% c('RATE') & row == 11 , DER_NA_CODE_STRING, #Victim age 2: Under 18
        trim_upcase(estimate_type) %in% c('RATE') & row == 12 , DER_NA_CODE_STRING, #Victim age 2: Under 12
        trim_upcase(estimate_type) %in% c('RATE') & row == 13 , DER_NA_CODE_STRING, #Victim age 2: 12-17
        trim_upcase(estimate_type) %in% c('RATE') & row == 14 , DER_NA_CODE_STRING, #Victim age 2: 18+
        trim_upcase(estimate_type) %in% c('RATE') & row == 15 , DER_NA_CODE_STRING, #Victim age 2: Unknown
        trim_upcase(estimate_type) %in% c('RATE') & row == 16 , DER_NA_CODE_STRING, #Number of Victims: 1
        trim_upcase(estimate_type) %in% c('RATE') & row == 17 , DER_NA_CODE_STRING, #Number of Victims: 2
        trim_upcase(estimate_type) %in% c('RATE') & row == 18 , DER_NA_CODE_STRING, #Number of Victims: 3
        trim_upcase(estimate_type) %in% c('RATE') & row == 19 , DER_NA_CODE_STRING, #Number of Victims: 4+
        trim_upcase(estimate_type) %in% c('RATE') & row == 20 , DER_NA_CODE_STRING, #Victim sex: Male
        trim_upcase(estimate_type) %in% c('RATE') & row == 21 , DER_NA_CODE_STRING, #Victim sex: Female
        trim_upcase(estimate_type) %in% c('RATE') & row == 22 , DER_NA_CODE_STRING, #Victim sex: Unknown
        trim_upcase(estimate_type) %in% c('RATE') & row == 23 , DER_NA_CODE_STRING, #Victim race: White
        trim_upcase(estimate_type) %in% c('RATE') & row == 24 , DER_NA_CODE_STRING, #Victim race: Black
        trim_upcase(estimate_type) %in% c('RATE') & row == 25 , DER_NA_CODE_STRING, #Victim race: American Indian or Alaska Native
        trim_upcase(estimate_type) %in% c('RATE') & row == 26 , DER_NA_CODE_STRING, #Victim race: Asian
        trim_upcase(estimate_type) %in% c('RATE') & row == 27 , DER_NA_CODE_STRING, #Victim race: Native Hawaiian or Other Pacific Islander
        trim_upcase(estimate_type) %in% c('RATE') & row == 28 , DER_NA_CODE_STRING, #Victim race: Unknown
        trim_upcase(estimate_type) %in% c('RATE') & row == 29 , DER_NA_CODE_STRING, #Number of Victims Summarized at Incident Level: 1
        trim_upcase(estimate_type) %in% c('RATE') & row == 30 , DER_NA_CODE_STRING, #Number of Victims Summarized at Incident Level: 2
        trim_upcase(estimate_type) %in% c('RATE') & row == 31 , DER_NA_CODE_STRING, #Number of Victims Summarized at Incident Level: 3
        trim_upcase(estimate_type) %in% c('RATE') & row == 32 , DER_NA_CODE_STRING, #Number of Victims Summarized at Incident Level: 4+
        trim_upcase(estimate_type) %in% c('RATE') & row == 33 , DER_NA_CODE_STRING, #Number of Victims Murdered: Yes
        trim_upcase(estimate_type) %in% c('RATE') & row == 34 , DER_NA_CODE_STRING, #Number of Victims Murdered: No
        trim_upcase(estimate_type) %in% c('RATE') & row == 35 , DER_NA_CODE_STRING, #Number of Firearm Victims: 1
        trim_upcase(estimate_type) %in% c('RATE') & row == 36 , DER_NA_CODE_STRING, #Number of Firearm Victims: 2
        trim_upcase(estimate_type) %in% c('RATE') & row == 37 , DER_NA_CODE_STRING, #Number of Firearm Victims: 3
        trim_upcase(estimate_type) %in% c('RATE') & row == 38 , DER_NA_CODE_STRING, #Number of Firearm Victims: 4+
        
        trim_upcase(estimate_type) %in% c('RATE') & row == 39 , DER_NA_CODE_STRING, #Injury hierarchy : Murder and Non-negligent Manslaughter, Negligent Manslaughter
        trim_upcase(estimate_type) %in% c('RATE') & row == 40 , DER_NA_CODE_STRING, #Injury hierarchy : Major injury (other major injury, severe laceration, possible internal injury)
        trim_upcase(estimate_type) %in% c('RATE') & row == 41 , DER_NA_CODE_STRING, #Injury hierarchy : Unconsciousness, apparent broken bones, loss of teeth
        trim_upcase(estimate_type) %in% c('RATE') & row == 42 , DER_NA_CODE_STRING, #Injury hierarchy : Apparent minor injury
        trim_upcase(estimate_type) %in% c('RATE') & row == 43 , DER_NA_CODE_STRING, #Injury hierarchy : No injury
        trim_upcase(estimate_type) %in% c('RATE') & row == 44 , DER_NA_CODE_STRING, #Injury hierarchy 2: Murder and Non-negligent Manslaughter, Negligent Manslaughter
        trim_upcase(estimate_type) %in% c('RATE') & row == 45 , DER_NA_CODE_STRING, #Injury hierarchy 2: Other major injury
        trim_upcase(estimate_type) %in% c('RATE') & row == 46 , DER_NA_CODE_STRING, #Injury hierarchy 2: Severe laceration, possible internal injury
        trim_upcase(estimate_type) %in% c('RATE') & row == 47 , DER_NA_CODE_STRING, #Injury hierarchy 2: Unconsciousness, apparent broken bones, loss of teeth
        trim_upcase(estimate_type) %in% c('RATE') & row == 48 , DER_NA_CODE_STRING, #Injury hierarchy 2: Apparent minor injury
        trim_upcase(estimate_type) %in% c('RATE') & row == 49 , DER_NA_CODE_STRING, #Injury hierarchy 2: No injury
        trim_upcase(estimate_type) %in% c('RATE') & row == 50 , DER_NA_CODE_STRING, #Victim-offender relationship hierarchy: Intimate partner
        trim_upcase(estimate_type) %in% c('RATE') & row == 51 , DER_NA_CODE_STRING, #Victim-offender relationship hierarchy: Other family
        trim_upcase(estimate_type) %in% c('RATE') & row == 52 , DER_NA_CODE_STRING, #Victim-offender relationship hierarchy: Outside family but known to victim
        trim_upcase(estimate_type) %in% c('RATE') & row == 53 , DER_NA_CODE_STRING, #Victim-offender relationship hierarchy: Stranger
        trim_upcase(estimate_type) %in% c('RATE') & row == 54 , DER_NA_CODE_STRING, #Victim-offender relationship hierarchy: Victim was Offender
        trim_upcase(estimate_type) %in% c('RATE') & row == 55 , DER_NA_CODE_STRING, #Victim-offender relationship hierarchy: Unknown relationship
        trim_upcase(estimate_type) %in% c('RATE') & row == 56 , DER_NA_CODE_STRING, #Victim-offender relationship hierarchy: Unknown Offender Incidents
        trim_upcase(estimate_type) %in% c('RATE') & row == 57 , DER_NA_CODE_STRING, #Victim-offender relationship hierarchy: Missing from Uncleared Incidents
        trim_upcase(estimate_type) %in% c('RATE') & row == 58 , DER_NA_CODE_STRING, #Victim-offender relationship hierarchy among known offenders: Intimate partner
        trim_upcase(estimate_type) %in% c('RATE') & row == 59 , DER_NA_CODE_STRING, #Victim-offender relationship hierarchy among known offenders: Other family
        trim_upcase(estimate_type) %in% c('RATE') & row == 60 , DER_NA_CODE_STRING, #Victim-offender relationship hierarchy among known offenders: Outside family but known to victim
        trim_upcase(estimate_type) %in% c('RATE') & row == 61 , DER_NA_CODE_STRING, #Victim-offender relationship hierarchy among known offenders: Stranger
        trim_upcase(estimate_type) %in% c('RATE') & row == 62 , DER_NA_CODE_STRING, #Victim-offender relationship hierarchy among known offenders: Victim was Offender
        trim_upcase(estimate_type) %in% c('RATE') & row == 63 , DER_NA_CODE_STRING, #Victim-offender relationship hierarchy among known offenders: Unknown relationship
        
        trim_upcase(estimate_type) %in% c('RATE') & row == 64 , DER_NA_CODE_STRING, #Victim Hispanic Origin: Hispanic or Latino
        trim_upcase(estimate_type) %in% c('RATE') & row == 65 , DER_NA_CODE_STRING, #Victim Hispanic Origin: Not Hispanic or Latino
        trim_upcase(estimate_type) %in% c('RATE') & row == 66 , DER_NA_CODE_STRING, #Victim Hispanic Origin: Unknown
        trim_upcase(estimate_type) %in% c('RATE') & row == 67 , DER_NA_CODE_STRING, #Victim race and Hispanic Origin: Hispanic or Latino
        trim_upcase(estimate_type) %in% c('RATE') & row == 68 , DER_NA_CODE_STRING, #Victim race and Hispanic Origin: Non-Hispanic, White
        trim_upcase(estimate_type) %in% c('RATE') & row == 69 , DER_NA_CODE_STRING, #Victim race and Hispanic Origin: Non-Hispanic, Black
        trim_upcase(estimate_type) %in% c('RATE') & row == 70 , DER_NA_CODE_STRING, #Victim race and Hispanic Origin: Non-Hispanic, American Indian or Alaska Native
        trim_upcase(estimate_type) %in% c('RATE') & row == 71 , DER_NA_CODE_STRING, #Victim race and Hispanic Origin: Non-Hispanic, Asian
        trim_upcase(estimate_type) %in% c('RATE') & row == 72 , DER_NA_CODE_STRING, #Victim race and Hispanic Origin: Non-Hispanic, Native Hawaiian or Other Pacific Islander
        trim_upcase(estimate_type) %in% c('RATE') & row == 73 , DER_NA_CODE_STRING #Victim race and Hispanic Origin: Unknown race or Hispanic origin
        
        
        
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


  #Victim Age
  s3 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_victim_age_cat_victim, var=der_victim_age_cat, section=3, mergeby=c( "incident_id", "victim_id"))

  #Victim Age2
  s4 <- agg_percent_CAA_victim(leftdata = main_filter, rightdata = agg_victim_age_cat_2_uo18_victim, var=der_victim_age_cat_2_uo18, section=4, mergeby=c( "incident_id", "victim_id"), denom=der_total_denom)
  
  #Total Denominator
  der_under18_denom <- s4[[1]] %>% filter(der_victim_age_cat_2_uo18 == 1) %>% select(final_count) %>% as.double()
    
  s5 <- agg_percent_CAA_victim(leftdata = main_filter, rightdata = agg_victim_age_cat_under18_2_victim, var=der_victim_age_cat_under18_2, section=5, mergeby=c( "incident_id", "victim_id"), denom=der_under18_denom)
  
  #Number of Victims
  s6 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_number_of_victims_cat, var=der_number_of_victims_cat, section=6, mergeby=c( "incident_id"))
  
  #Victim sex
  s7 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_victim_gender_victim, var=der_victim_gender, section=7, mergeby=c( "incident_id", "victim_id"))

  #Victim race
  s8 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_victim_race_victim, var=der_victim_race, section=8, mergeby=c( "incident_id", "victim_id"))

  #Number of Victims Summarized at Incident Level  
  #Create the variable der_inc_number_of_victims_cat using the main_filter dataset
  agg_inc_number_of_victims_cat <- main_filter %>%
    #Deduplicate the data, note main_filter is the block imputed dataset, so need to create unique incident_id and victim_id rows
    count(incident_id, victim_id) %>%
    #Drop the n variable for count
    select(-n) %>%
    #Next need to recode the number of victims in the incident
    count(incident_id) %>%
    #Note n is the number of victims in an incident
    mutate(
      der_inc_number_of_victims_cat = fcase(
        n == 1, 1, # 1
        n == 2, 2, # 2
        n == 3, 3, # 3
        n >= 4, 4 # 4+
      ),
      
    #Create the count variable and assign 1 for each incident
      count = 1) %>%
    #Keep variables of interest
    select(incident_id, der_inc_number_of_victims_cat, count)
  
  #Next need to create the incident level file using main_filter
  main_filter_inc <- main_filter[, .SD[1], by = c("ori", "incident_id", filtervarsting)]  
  
  
  #Using agg_inc_number_of_victims_cat, process as normal
  s9 <- agg_percent_by_incident_id(leftdata = main_filter_inc, rightdata = agg_inc_number_of_victims_cat, var=der_inc_number_of_victims_cat, section=9)
    
  #Number of Victims Murdered   
  s10 <- agg_percent_CAA_victim(leftdata = main_filter, rightdata = agg_victim_murder_non_neg_manslaughter_victim, var=der_victim_murder_non_neg_manslaughter, section=10, mergeby=c( "incident_id", "victim_id"), denom = der_total_denom)
    
  #Number of Firearm Victims
  s11 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_number_of_victims_firearm_cat, var=der_number_of_victims_firearm_cat, section=11, mergeby=c( "incident_id"))
  
  #Injury hierarchy 
  s12 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_injury_hierarchy_victim, var=der_injury_hierarchy, section=12, mergeby=c( "incident_id", "victim_id"))

  #Injury hierarchy 2
  s13 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_injury_hierarchy2_victim, var=der_injury_hierarchy2, section=13, mergeby=c( "incident_id", "victim_id"))
  
  #Victim-offender relationship hierarchy
  s14 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_relationship_hierarchy_victim, var=der_relationship_hierarchy, section=14, mergeby=c( "incident_id", "victim_id"))

  #Victim-offender relationship hierarchy among known offenders
  s15 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_relationship_hierarchy_victim_known, var=der_relationship_hierarchy_victim_known, section=15, mergeby=c( "incident_id", "victim_id"))
  
  #Victim Hispanic Origin
  s16 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_victim_ethnicity_victim, var=der_victim_ethnicity, section=16, mergeby=c( "incident_id", "victim_id"))  
  
  #Victim race and Hispanic Origin
  s17 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_victim_ethnicity_race_victim, var=der_victim_ethnicity_race, section=17, mergeby=c( "incident_id", "victim_id"))  
  
  
  
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

createadditionalcolumns <- function(intotalcolumn, incolumnstart, colindex, insubset, inperm_num_series){
  log_dim("Inside createadditionalcolumns")

	#Create new symbol to subset data
	insymbol <- insubset %>% rlang:::parse_expr()

	#Call the functions for each column
  subsetvareq <- c(
    "der_against_person",
    "der_total_gun_violence",
    "der_fatal_gun_violence",
    "der_nonfatal_gun_violence",
    "der_nonfatal_gun_violence2",
    "der_murder_non_neg_manslaughter",
    "der_neg_manslaughter",
    "der_revised_rape",
    "der_robbery",
    "der_aggravated_assault", 
    "der_kidnapping_abduction",
    "der_human_trafficking_offenses",
    "der_car_jacking"
  )
  temp <- generate_est(
    maindata=main %>% filter(!!insymbol), 
    subsetvareq1 = subsetvareq[colindex], 
    column_number=colindex+inperm_num_series
  )
  return(temp)
}
