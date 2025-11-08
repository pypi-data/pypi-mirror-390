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
      section %in% c(1, 20) , 1,
      der_arrest_type %in% c(1:3) , der_arrest_type + 1,
      der_arrestee_age_cat_15_17 %in% c(1:10) , der_arrestee_age_cat_15_17 + 4,
      der_arrestee_gender %in% c(1:3) & section %in% c(4, 23) , der_arrestee_gender + 14,
      der_arrestee_race %in% c(1:6) , der_arrestee_race + 17,
      
      
      der_arrestee_gender == 1 & section %in% c(8, 28)  ,  24,
      der_arrestee_gender_race %in% c(1:6) , der_arrestee_gender_race + 24,
      der_arrestee_gender == 2 & section %in% c(8, 28)  ,  31,
      der_arrestee_gender_race %in% c(7:12) , der_arrestee_gender_race + 31 - 6,
      der_arrestee_gender == 3 & section %in% c(8, 28)  ,  38,
      der_arrestee_gender_race %in% c(13:18) , der_arrestee_gender_race + 38 - 12,    
      
      der_juvenile_disp %in% c(1:4) , der_juvenile_disp + 44,
      der_multiple_arrest %in% c(1:3) , der_multiple_arrest + 48,
      
      ###Weapon at Arrestee Level - Armed with #####
      
      der_weapon_no_yes %in% c(1:2) & section %in% c(11, 30) , der_weapon_no_yes + 51,
      der_weapon_yes_cat %in% c(1:3) & section %in% c(12, 31) , der_weapon_yes_cat + 53,
      
      ###Weapon at Incident Level - Weapon involved #####
      
      der_weapon_no_yes %in% c(1:2) & section ==  13 , der_weapon_no_yes + 56,
      der_weapon_yes_cat %in% c(1:6) & section == 14 , der_weapon_yes_cat + 58,

      #######Arrestee age 2###############################

      der_arrestee_age_cat_under18_2 %in% c(1:2), der_arrestee_age_cat_under18_2 + 64, ##Under 12, 12-17
      der_arrestee_age_cat_12_17_cat %in% c(1:2), der_arrestee_age_cat_12_17_cat + 66, #12-14, 15-17
      der_arrestee_age_cat_2_uo18 %in% c(2), 69, #2, #18+
      der_arrestee_age_cat_2_uo18 %in% c(3), 70, #3, #Unknown
      
      #Arrestee Hispanic Origin
      der_arrestee_ethnicity %in% c(1:3), der_arrestee_ethnicity + 70,
      
      #Arrestee race and Hispanic Origin
      der_arrestee_ethnicity_race %in% c(1:7), der_arrestee_ethnicity_race + 73        
      
      )
    
  )
  
  return(returndata)
}


assign_section <- function(data){
  log_debug("Running assign_section function")
  
  returndata <- data %>% mutate(
    
    section = fcase(
      row %in% c(1) , 1,
      row %in% c(2:4) , 2,
      row %in% c(5:14) , 3,
      row %in% c(15:17) , 4, 
      row %in% c(18:23) , 5, 
      row %in% c(24:44) , 6, 
      row %in% c(45:48) , 7, 
      row %in% c(49:51) , 8, 
      row %in% c(52:56) , 9, 
      row %in% c(57:64) , 10,
      row %in% c(65:70),  11,
      row %in% c(71:73),  12,
      row %in% c(74:80),  13      
      
      )
  )
  
  return(returndata)
  
}


#New add on code for labels
assign_labels <- function(data){
  log_debug("Running assign_labels function")
  
  returndata <- data %>% mutate(
    
    estimate_domain = fcase(
      
      row == 1 , 'Arrest count',
      row == 2 , 'Arrest type: On-view arrest',
      row == 3 , 'Arrest type: Summoned/cited',
      row == 4 , 'Arrest type: Taken into custody',
      row == 5 , 'Arrestee age: Under 5',
      row == 6 , 'Arrestee age: 5-14',
      row == 7 , 'Arrestee age: 15',
      row == 8 , 'Arrestee age: 16',
      row == 9 , 'Arrestee age: 17',
      row == 10 , 'Arrestee age: 18-24',
      row == 11 , 'Arrestee age: 25-34',
      row == 12 , 'Arrestee age: 35-64',
      row == 13 , 'Arrestee age: 65+',
      row == 14 , 'Arrestee age: Unknown',
      row == 15 , 'Arrestee sex: Male',
      row == 16 , 'Arrestee sex: Female',
      row == 17 , 'Arrestee sex: Unknown',
      row == 18 , 'Arrestee race: White',
      row == 19 , 'Arrestee race: Black',
      row == 20 , 'Arrestee race: American Indian or Alaska Native',
      row == 21 , 'Arrestee race: Asian',
      row == 22 , 'Arrestee race: Native Hawaiian or Other Pacific Islander',
      row == 23 , 'Arrestee race: Unknown',
      row == 24 , 'Arrestee sex and race: Male',
      row == 25 , 'Arrestee sex and race Male: White',
      row == 26 , 'Arrestee sex and race Male: Black',
      row == 27 , 'Arrestee sex and race Male: American Indian or Alaska Native',
      row == 28 , 'Arrestee sex and race Male: Asian',
      row == 29 , 'Arrestee sex and race Male: Native Hawaiian or Other Pacific Islander',
      row == 30 , 'Arrestee sex and race Male: Unknown',
      row == 31 , 'Arrestee sex and race: Female',
      row == 32 , 'Arrestee sex and race Female: White',
      row == 33 , 'Arrestee sex and race Female: Black',
      row == 34 , 'Arrestee sex and race Female: American Indian or Alaska Native',
      row == 35 , 'Arrestee sex and race Female: Asian',
      row == 36 , 'Arrestee sex and race Female: Native Hawaiian or Other Pacific Islander',
      row == 37 , 'Arrestee sex and race Female: Unknown',
      row == 38 , 'Arrestee sex and race: Unknown',
      row == 39 , 'Arrestee sex and race Unknown: White',
      row == 40 , 'Arrestee sex and race Unknown: Black',
      row == 41 , 'Arrestee sex and race Unknown: American Indian or Alaska Native',
      row == 42 , 'Arrestee sex and race Unknown: Asian',
      row == 43 , 'Arrestee sex and race Unknown: Native Hawaiian or Other Pacific Islander',
      row == 44 , 'Arrestee sex and race Unknown: Unknown',
      row == 45 , 'Juvenile disposition: Handled within department',
      row == 46 , 'Juvenile disposition: Referred to other authorities',
      row == 47 , 'Juvenile disposition: Not applicable',
      row == 48 , 'Juvenile disposition: Unknown',
      row == 49 , 'Multiple arrest indicator: Multiple',
      row == 50 , 'Multiple arrest indicator: Count',
      row == 51 , 'Multiple arrest indicator: Not applicable',
      row == 52 , 'Arrestee armed: No',
      row == 53 , 'Arrestee armed: Yes',
      row == 54 , 'Arrestee armed: Firearm',
      row == 55 , 'Arrestee armed: Lethal cutting instrument',
      row == 56 , 'Arrestee armed: Club/blackjack/brass knuckles',
      row == 57 , 'Weapon involved: No',
      row == 58 , 'Weapon involved: Yes',
      row == 59 , 'Weapon involved: Personal weapons',
      row == 60 , 'Weapon involved: Firearms',
      row == 61 , 'Weapon involved: Knives and other cutting instruments',
      row == 62 , 'Weapon involved: Blunt instruments',
      row == 63 , 'Weapon involved: Other non-personal weapons',
      row == 64 , 'Weapon involved: Unknown',
      row == 65, 'Arrestee age 2: Under 12',
      row == 66, 'Arrestee age 2: 12-17',
      row == 67, 'Arrestee age 2: 12-14',
      row == 68, 'Arrestee age 2: 15-17',
      row == 69, 'Arrestee age 2: 18+',
      row == 70, 'Arrestee age 2: Unknown',
      
      row == 71, 'Arrestee Hispanic Origin: Hispanic or Latino',
      row == 72, 'Arrestee Hispanic Origin: Not Hispanic or Latino',
      row == 73, 'Arrestee Hispanic Origin: Unknown',
      row == 74, 'Arrestee race and Hispanic Origin: Hispanic or Latino',
      row == 75, 'Arrestee race and Hispanic Origin: Non-Hispanic, White',
      row == 76, 'Arrestee race and Hispanic Origin: Non-Hispanic, Black',
      row == 77, 'Arrestee race and Hispanic Origin: Non-Hispanic, American Indian or Alaska Native',
      row == 78, 'Arrestee race and Hispanic Origin: Non-Hispanic, Asian',
      row == 79, 'Arrestee race and Hispanic Origin: Non-Hispanic, Native Hawaiian or Other Pacific Islander',
      row == 80, 'Arrestee race and Hispanic Origin: Unknown race or Hispanic origin'
      
      
      
    ),
    
    indicator_name = fcase(
      
      column == 1 , 'NIBRS crimes against persons (Total)',
      column == 2 , 'Aggravated Assault',
      column == 3 , 'Simple Assault',
      column == 4 , 'Intimidation',
      column == 5 , 'Murder and Non-negligent Manslaughter',
      column == 6 , 'Negligent Manslaughter',
      column == 7 , 'Kidnapping/Abduction',
      column == 8 , 'Human Trafficking-Sex',
      column == 9 , 'Human Trafficking-Labor',
      column == 10 , 'Rape',
      column == 11 , 'Sodomy',
      column == 12 , 'Sexual Assault with an Object',
      column == 13 , 'Fondling',
      column == 14 , 'Sex Offenses, Nonforcible',
      column == 15 , 'NIBRS crimes against property (Total)',
      column == 16 , 'Arson',
      column == 17 , 'Bribery',
      column == 18 , 'Burglary/B&E',
      column == 19 , 'Counterfeiting/Forgery',
      column == 20 , 'Destruction/Damage/Vandalism',
      column == 21 , 'Embezzlement',
      column == 22 , 'Extortion/Blackmail',
      column == 23 , 'Fraud Offenses',
      column == 24 , 'Larceny/Theft Offenses',
      column == 25 , 'Motor Vehicle Theft',
      column == 26 , 'Robbery',
      column == 27 , 'Stolen Property Offenses',
      column == 28 , 'NIBRS crimes against society (Total)',
      column == 29 , 'Revised Rape',
      column == 30 , 'Violent Crime',
      column == 31 , 'Property Crime',
      column == 32 , 'Import Violations',
      column == 33 , 'Export Violations',
      column == 34 , 'Federal Liquor Offenses',
      column == 35 , 'Federal Tobacco Offenses',
      column == 36 , 'Wildlife Trafficking',
      column == 37 , 'Espionage',
      column == 38 , 'Money Laundering',
      column == 39 , 'Harboring Escapee/Concealing from Arrest',
      column == 40 , 'Flight to Avoid Prosecution',
      column == 41 , 'Flight to Avoid Deportation',
      column == 42 , 'Illegal Entry into the United States',
      column == 43 , 'False Citizenship',
      column == 44 , 'Smuggling Aliens',
      column == 45 , 'Re-entry after Deportation',
      column == 46 , 'Failure to Register as a Sex Offender',
      column == 47 , 'Treason',
      column == 48 , 'Violation of National Firearm Act of 1934',
      column == 49 , 'Weapons of Mass Destruction',
      column == 50 , 'Explosives Violation',
      column == 51 , 'Family Offenses, Nonviolent',
      column == 52 , 'Trespass of Real Property',
      column == 53 , 'Curfew/Loitering/Vagrancy Violations',
      column == 54 , 'Liquor Law Violations',
      column == 55 , 'Disorderly Conduct',
      column == 56 , 'Failure to Appear',
      column == 57 , 'Federal Resource Violations',
      column == 58 , 'Perjury',
      column == 59 , 'Driving Under the Influence',
      column == 60 , 'All Other Offenses',
      column == 61 , 'Car Jacking',
      column == 62 , 'Total Arrests',
      
      column == 63, 'Assault Offenses',
      column == 64, 'Violent Crime 2',
      column == 65, 'Animal Cruelty',
      column == 66, 'Drug/Narcotic Offenses',
      column == 67, 'Gambling Offenses',
      column == 68, 'Pornography/Obscene Material',
      column == 69, 'Prostitution Offenses',
      column == 70, 'Weapon Law Violations',
      column == 71, ' Drug Equipment Violations'
      
    ),
    
    full_table = "Table5a-Arrestees Arrest Code",
    table = DER_TABLE_NAME
  )
  
  return(returndata)
  
}


estimate_type_detail_percentage_label <- function(indata){
  log_debug("Running estimate_type_detail_percentage_label function")
  
  returndata <- indata %>%
    mutate(
      estimate_type_detail_percentage = fcase(
        
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 1 , 'Arrestee Level', #Arrest count
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 2 , 'Arrestee Level', #Arrest type: On-view arrest
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 3 , 'Arrestee Level', #Arrest type: Summoned/cited
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 4 , 'Arrestee Level', #Arrest type: Taken into custody
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 5 , 'Arrestee Level', #Arrestee age: Under 5
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 6 , 'Arrestee Level', #Arrestee age: 5-14
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 7 , 'Arrestee Level', #Arrestee age: 15
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 8 , 'Arrestee Level', #Arrestee age: 16
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 9 , 'Arrestee Level', #Arrestee age: 17
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 10 , 'Arrestee Level', #Arrestee age: 18-24
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 11 , 'Arrestee Level', #Arrestee age: 25-34
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 12 , 'Arrestee Level', #Arrestee age: 35-64
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 13 , 'Arrestee Level', #Arrestee age: 65+
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 14 , 'Arrestee Level', #Arrestee age: Unknown
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 15 , 'Arrestee Level', #Arrestee sex: Male
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 16 , 'Arrestee Level', #Arrestee sex: Female
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 17 , 'Arrestee Level', #Arrestee sex: Unknown
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 18 , 'Arrestee Level', #Arrestee race: White
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 19 , 'Arrestee Level', #Arrestee race: Black
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 20 , 'Arrestee Level', #Arrestee race: American Indian or Alaska Native
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 21 , 'Arrestee Level', #Arrestee race: Asian
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 22 , 'Arrestee Level', #Arrestee race: Native Hawaiian or Other Pacific Islander
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 23 , 'Arrestee Level', #Arrestee race: Unknown
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 24 , 'Arrestee Level', #Arrestee sex and race: Male
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 25 , 'Arrestee Level subset to male', #Arrestee sex and race Male: White
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 26 , 'Arrestee Level subset to male', #Arrestee sex and race Male: Black
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 27 , 'Arrestee Level subset to male', #Arrestee sex and race Male: American Indian or Alaska Native
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 28 , 'Arrestee Level subset to male', #Arrestee sex and race Male: Asian
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 29 , 'Arrestee Level subset to male', #Arrestee sex and race Male: Native Hawaiian or Other Pacific Islander
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 30 , 'Arrestee Level subset to male', #Arrestee sex and race Male: Unknown
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 31 , 'Arrestee Level', #Arrestee sex and race: Female
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 32 , 'Arrestee Level subset to female', #Arrestee sex and race Female: White
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 33 , 'Arrestee Level subset to female', #Arrestee sex and race Female: Black
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 34 , 'Arrestee Level subset to female', #Arrestee sex and race Female: American Indian or Alaska Native
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 35 , 'Arrestee Level subset to female', #Arrestee sex and race Female: Asian
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 36 , 'Arrestee Level subset to female', #Arrestee sex and race Female: Native Hawaiian or Other Pacific Islander
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 37 , 'Arrestee Level subset to female', #Arrestee sex and race Female: Unknown
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 38 , 'Arrestee Level', #Arrestee sex and race: Unknown
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 39 , 'Arrestee Level subset to unknown gender', #Arrestee sex and race Unknown: White
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 40 , 'Arrestee Level subset to unknown gender', #Arrestee sex and race Unknown: Black
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 41 , 'Arrestee Level subset to unknown gender', #Arrestee sex and race Unknown: American Indian or Alaska Native
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 42 , 'Arrestee Level subset to unknown gender', #Arrestee sex and race Unknown: Asian
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 43 , 'Arrestee Level subset to unknown gender', #Arrestee sex and race Unknown: Native Hawaiian or Other Pacific Islander
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 44 , 'Arrestee Level subset to unknown gender', #Arrestee sex and race Unknown: Unknown
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 45 , 'Arrestee Level', #Juvenile disposition: Handled within department
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 46 , 'Arrestee Level', #Juvenile disposition: Referred to other authorities
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 47 , 'Arrestee Level', #Juvenile disposition: Not applicable
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 48 , 'Arrestee Level', #Juvenile disposition: Unknown
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 49 , 'Arrestee Level', #Multiple arrest indicator: Multiple
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 50 , 'Arrestee Level', #Multiple arrest indicator: Count
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 51 , 'Arrestee Level', #Multiple arrest indicator: Not applicable
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 52 , 'Arrestee Level', #Arrestee armed: No
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 53 , 'Arrestee Level', #Arrestee armed: Yes
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 54 , 'Arrestee Level subset to arrestee armed yes', #Arrestee armed: Firearm
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 55 , 'Arrestee Level subset to arrestee armed yes', #Arrestee armed: Lethal cutting instrument
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 56 , 'Arrestee Level subset to arrestee armed yes', #Arrestee armed: Club/blackjack/brass knuckles
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 57 , 'Arrestee Level', #Weapon involved: No
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 58 , 'Arrestee Level', #Weapon involved: Yes
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 59 , 'Arrestee Level subset to weapon involved yes', #Weapon involved: Personal weapons
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 60 , 'Arrestee Level subset to weapon involved yes', #Weapon involved: Firearms
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 61 , 'Arrestee Level subset to weapon involved yes', #Weapon involved: Knives and other cutting instruments
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 62 , 'Arrestee Level subset to weapon involved yes', #Weapon involved: Blunt instruments
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 63 , 'Arrestee Level subset to weapon involved yes', #Weapon involved: Other non-personal weapons
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 64 , 'Arrestee Level subset to weapon involved yes', #Weapon involved: Unknown
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 65, 'Arrestee Level', #Arrestee age 2: Under 12
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 66, 'Arrestee Level', #Arrestee age 2: 12-17
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 67, 'Arrestee Level Subset to 12-17', #Arrestee age 2: 12-14
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 68, 'Arrestee Level Subset to 12-17', #Arrestee age 2: 15-17
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 69, 'Arrestee Level', #Arrestee age 2: 18+
        trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 70, 'Arrestee Level', #Arrestee age 2: Unknown
		
		trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 71, 'Arrestee Level', #Arrestee Hispanic Origin: Hispanic or Latino
		trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 72, 'Arrestee Level', #Arrestee Hispanic Origin: Not Hispanic or Latino
		trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 73, 'Arrestee Level', #Arrestee Hispanic Origin: Unknown
		trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 74, 'Arrestee Level', #Arrestee race and Hispanic Origin: Hispanic or Latino
		trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 75, 'Arrestee Level', #Arrestee race and Hispanic Origin: Non-Hispanic, White
		trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 76, 'Arrestee Level', #Arrestee race and Hispanic Origin: Non-Hispanic, Black
		trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 77, 'Arrestee Level', #Arrestee race and Hispanic Origin: Non-Hispanic, American Indian or Alaska Native
		trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 78, 'Arrestee Level', #Arrestee race and Hispanic Origin: Non-Hispanic, Asian
		trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 79, 'Arrestee Level', #Arrestee race and Hispanic Origin: Non-Hispanic, Native Hawaiian or Other Pacific Islander
		trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 80, 'Arrestee Level' #Arrestee race and Hispanic Origin: Unknown race or Hispanic origin
				
		
      )) 
  
  return(returndata)
}

estimate_type_detail_rate_label <- function(indata){
  log_debug("Running estimate_type_detail_rate_label function")
  
  returndata <- indata %>%
    mutate(
      estimate_type_detail_rate = fcase(
        
        trim_upcase(estimate_type) %in% c('RATE') & row == 1 , DER_NA_CODE_STRING, #Arrest count
        trim_upcase(estimate_type) %in% c('RATE') & row == 2 , DER_NA_CODE_STRING, #Arrest type: On-view arrest
        trim_upcase(estimate_type) %in% c('RATE') & row == 3 , DER_NA_CODE_STRING, #Arrest type: Summoned/cited
        trim_upcase(estimate_type) %in% c('RATE') & row == 4 , DER_NA_CODE_STRING, #Arrest type: Taken into custody
        trim_upcase(estimate_type) %in% c('RATE') & row == 5 , DER_NA_CODE_STRING, #Arrestee age: Under 5
        trim_upcase(estimate_type) %in% c('RATE') & row == 6 , DER_NA_CODE_STRING, #Arrestee age: 5-14
        trim_upcase(estimate_type) %in% c('RATE') & row == 7 , DER_NA_CODE_STRING, #Arrestee age: 15
        trim_upcase(estimate_type) %in% c('RATE') & row == 8 , DER_NA_CODE_STRING, #Arrestee age: 16
        trim_upcase(estimate_type) %in% c('RATE') & row == 9 , DER_NA_CODE_STRING, #Arrestee age: 17
        trim_upcase(estimate_type) %in% c('RATE') & row == 10 , DER_NA_CODE_STRING, #Arrestee age: 18-24
        trim_upcase(estimate_type) %in% c('RATE') & row == 11 , DER_NA_CODE_STRING, #Arrestee age: 25-34
        trim_upcase(estimate_type) %in% c('RATE') & row == 12 , DER_NA_CODE_STRING, #Arrestee age: 35-64
        trim_upcase(estimate_type) %in% c('RATE') & row == 13 , DER_NA_CODE_STRING, #Arrestee age: 65+
        trim_upcase(estimate_type) %in% c('RATE') & row == 14 , DER_NA_CODE_STRING, #Arrestee age: Unknown
        trim_upcase(estimate_type) %in% c('RATE') & row == 15 , DER_NA_CODE_STRING, #Arrestee sex: Male
        trim_upcase(estimate_type) %in% c('RATE') & row == 16 , DER_NA_CODE_STRING, #Arrestee sex: Female
        trim_upcase(estimate_type) %in% c('RATE') & row == 17 , DER_NA_CODE_STRING, #Arrestee sex: Unknown
        trim_upcase(estimate_type) %in% c('RATE') & row == 18 , DER_NA_CODE_STRING, #Arrestee race: White
        trim_upcase(estimate_type) %in% c('RATE') & row == 19 , DER_NA_CODE_STRING, #Arrestee race: Black
        trim_upcase(estimate_type) %in% c('RATE') & row == 20 , DER_NA_CODE_STRING, #Arrestee race: American Indian or Alaska Native
        trim_upcase(estimate_type) %in% c('RATE') & row == 21 , DER_NA_CODE_STRING, #Arrestee race: Asian
        trim_upcase(estimate_type) %in% c('RATE') & row == 22 , DER_NA_CODE_STRING, #Arrestee race: Native Hawaiian or Other Pacific Islander
        trim_upcase(estimate_type) %in% c('RATE') & row == 23 , DER_NA_CODE_STRING, #Arrestee race: Unknown
        trim_upcase(estimate_type) %in% c('RATE') & row == 24 , DER_NA_CODE_STRING, #Arrestee sex and race: Male
        trim_upcase(estimate_type) %in% c('RATE') & row == 25 , DER_NA_CODE_STRING, #Arrestee sex and race Male: White
        trim_upcase(estimate_type) %in% c('RATE') & row == 26 , DER_NA_CODE_STRING, #Arrestee sex and race Male: Black
        trim_upcase(estimate_type) %in% c('RATE') & row == 27 , DER_NA_CODE_STRING, #Arrestee sex and race Male: American Indian or Alaska Native
        trim_upcase(estimate_type) %in% c('RATE') & row == 28 , DER_NA_CODE_STRING, #Arrestee sex and race Male: Asian
        trim_upcase(estimate_type) %in% c('RATE') & row == 29 , DER_NA_CODE_STRING, #Arrestee sex and race Male: Native Hawaiian or Other Pacific Islander
        trim_upcase(estimate_type) %in% c('RATE') & row == 30 , DER_NA_CODE_STRING, #Arrestee sex and race Male: Unknown
        trim_upcase(estimate_type) %in% c('RATE') & row == 31 , DER_NA_CODE_STRING, #Arrestee sex and race: Female
        trim_upcase(estimate_type) %in% c('RATE') & row == 32 , DER_NA_CODE_STRING, #Arrestee sex and race Female: White
        trim_upcase(estimate_type) %in% c('RATE') & row == 33 , DER_NA_CODE_STRING, #Arrestee sex and race Female: Black
        trim_upcase(estimate_type) %in% c('RATE') & row == 34 , DER_NA_CODE_STRING, #Arrestee sex and race Female: American Indian or Alaska Native
        trim_upcase(estimate_type) %in% c('RATE') & row == 35 , DER_NA_CODE_STRING, #Arrestee sex and race Female: Asian
        trim_upcase(estimate_type) %in% c('RATE') & row == 36 , DER_NA_CODE_STRING, #Arrestee sex and race Female: Native Hawaiian or Other Pacific Islander
        trim_upcase(estimate_type) %in% c('RATE') & row == 37 , DER_NA_CODE_STRING, #Arrestee sex and race Female: Unknown
        trim_upcase(estimate_type) %in% c('RATE') & row == 38 , DER_NA_CODE_STRING, #Arrestee sex and race: Unknown
        trim_upcase(estimate_type) %in% c('RATE') & row == 39 , DER_NA_CODE_STRING, #Arrestee sex and race Unknown: White
        trim_upcase(estimate_type) %in% c('RATE') & row == 40 , DER_NA_CODE_STRING, #Arrestee sex and race Unknown: Black
        trim_upcase(estimate_type) %in% c('RATE') & row == 41 , DER_NA_CODE_STRING, #Arrestee sex and race Unknown: American Indian or Alaska Native
        trim_upcase(estimate_type) %in% c('RATE') & row == 42 , DER_NA_CODE_STRING, #Arrestee sex and race Unknown: Asian
        trim_upcase(estimate_type) %in% c('RATE') & row == 43 , DER_NA_CODE_STRING, #Arrestee sex and race Unknown: Native Hawaiian or Other Pacific Islander
        trim_upcase(estimate_type) %in% c('RATE') & row == 44 , DER_NA_CODE_STRING, #Arrestee sex and race Unknown: Unknown
        trim_upcase(estimate_type) %in% c('RATE') & row == 45 , DER_NA_CODE_STRING, #Juvenile disposition: Handled within department
        trim_upcase(estimate_type) %in% c('RATE') & row == 46 , DER_NA_CODE_STRING, #Juvenile disposition: Referred to other authorities
        trim_upcase(estimate_type) %in% c('RATE') & row == 47 , DER_NA_CODE_STRING, #Juvenile disposition: Not applicable
        trim_upcase(estimate_type) %in% c('RATE') & row == 48 , DER_NA_CODE_STRING, #Juvenile disposition: Unknown
        trim_upcase(estimate_type) %in% c('RATE') & row == 49 , DER_NA_CODE_STRING, #Multiple arrest indicator: Multiple
        trim_upcase(estimate_type) %in% c('RATE') & row == 50 , DER_NA_CODE_STRING, #Multiple arrest indicator: Count
        trim_upcase(estimate_type) %in% c('RATE') & row == 51 , DER_NA_CODE_STRING, #Multiple arrest indicator: Not applicable
        trim_upcase(estimate_type) %in% c('RATE') & row == 52 , DER_NA_CODE_STRING, #Arrestee armed: No
        trim_upcase(estimate_type) %in% c('RATE') & row == 53 , DER_NA_CODE_STRING, #Arrestee armed: Yes
        trim_upcase(estimate_type) %in% c('RATE') & row == 54 , DER_NA_CODE_STRING, #Arrestee armed: Firearm
        trim_upcase(estimate_type) %in% c('RATE') & row == 55 , DER_NA_CODE_STRING, #Arrestee armed: Lethal cutting instrument
        trim_upcase(estimate_type) %in% c('RATE') & row == 56 , DER_NA_CODE_STRING, #Arrestee armed: Club/blackjack/brass knuckles
        trim_upcase(estimate_type) %in% c('RATE') & row == 57 , DER_NA_CODE_STRING, #Weapon involved: No
        trim_upcase(estimate_type) %in% c('RATE') & row == 58 , DER_NA_CODE_STRING, #Weapon involved: Yes
        trim_upcase(estimate_type) %in% c('RATE') & row == 59 , DER_NA_CODE_STRING, #Weapon involved: Personal weapons
        trim_upcase(estimate_type) %in% c('RATE') & row == 60 , DER_NA_CODE_STRING, #Weapon involved: Firearms
        trim_upcase(estimate_type) %in% c('RATE') & row == 61 , DER_NA_CODE_STRING, #Weapon involved: Knives and other cutting instruments
        trim_upcase(estimate_type) %in% c('RATE') & row == 62 , DER_NA_CODE_STRING, #Weapon involved: Blunt instruments
        trim_upcase(estimate_type) %in% c('RATE') & row == 63 , DER_NA_CODE_STRING, #Weapon involved: Other non-personal weapons
        trim_upcase(estimate_type) %in% c('RATE') & row == 64 , DER_NA_CODE_STRING, #Weapon involved: Unknown
        trim_upcase(estimate_type) %in% c('RATE') & row == 65, DER_NA_CODE_STRING, #Arrestee age 2: Under 12
        trim_upcase(estimate_type) %in% c('RATE') & row == 66, DER_NA_CODE_STRING, #Arrestee age 2: 12-17
        trim_upcase(estimate_type) %in% c('RATE') & row == 67, DER_NA_CODE_STRING, #Arrestee age 2: 12-14
        trim_upcase(estimate_type) %in% c('RATE') & row == 68, DER_NA_CODE_STRING, #Arrestee age 2: 15-17
        trim_upcase(estimate_type) %in% c('RATE') & row == 69, DER_NA_CODE_STRING, #Arrestee age 2: 18+
        trim_upcase(estimate_type) %in% c('RATE') & row == 70, DER_NA_CODE_STRING, #Arrestee age 2: Unknown
                
        trim_upcase(estimate_type) %in% c('RATE') & row == 71, DER_NA_CODE_STRING, #Arrestee Hispanic Origin: Hispanic or Latino
        trim_upcase(estimate_type) %in% c('RATE') & row == 72, DER_NA_CODE_STRING, #Arrestee Hispanic Origin: Not Hispanic or Latino
        trim_upcase(estimate_type) %in% c('RATE') & row == 73, DER_NA_CODE_STRING, #Arrestee Hispanic Origin: Unknown
        trim_upcase(estimate_type) %in% c('RATE') & row == 74, DER_NA_CODE_STRING, #Arrestee race and Hispanic Origin: Hispanic or Latino
        trim_upcase(estimate_type) %in% c('RATE') & row == 75, DER_NA_CODE_STRING, #Arrestee race and Hispanic Origin: Non-Hispanic, White
        trim_upcase(estimate_type) %in% c('RATE') & row == 76, DER_NA_CODE_STRING, #Arrestee race and Hispanic Origin: Non-Hispanic, Black
        trim_upcase(estimate_type) %in% c('RATE') & row == 77, DER_NA_CODE_STRING, #Arrestee race and Hispanic Origin: Non-Hispanic, American Indian or Alaska Native
        trim_upcase(estimate_type) %in% c('RATE') & row == 78, DER_NA_CODE_STRING, #Arrestee race and Hispanic Origin: Non-Hispanic, Asian
        trim_upcase(estimate_type) %in% c('RATE') & row == 79, DER_NA_CODE_STRING, #Arrestee race and Hispanic Origin: Non-Hispanic, Native Hawaiian or Other Pacific Islander
        trim_upcase(estimate_type) %in% c('RATE') & row == 80, DER_NA_CODE_STRING  #Arrestee race and Hispanic Origin: Unknown race or Hispanic origin
        
        
      ))
  
  return(returndata)      
  
}




#This function will calculate the counts and percentage one column at a time

generate_est <- function(maindata, maindatagroupb, subsetvareq1, column_number){
  log_debug("Running generate_est function")
  
  #Need to drop the missing arrestee
  maindata <- maindata %>%
    filter(!is.na(arrestee_id))
  
  log_debug("After dropping missing arrestees")
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
  main_filter <- maindata[eval(infilter), c("ori", "weight", "incident_id", "arrestee_id", filtervarsting), with = FALSE]
  #Deduplicate by Incident ID, arrestee ID, and one instance of crime type
  main_filter <- main_filter[, .SD[1], by = c("ori", "incident_id", "arrestee_id", filtervarsting)]
  
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
  
  ######################Early run for Group B Arrestee #################################
  #Need to drop the missing arrestee
  maindatagroupb <- maindatagroupb %>%
    filter(!is.na(groupb_arrestee_id))
  
  log_debug("After dropping missing arrestees groupb")
  log_debug(system("free -mh", intern = FALSE))
  
  
  #Filter the dataset
  main_filter_groupb <- maindatagroupb[eval(infilter), c("ori", "weight",  "groupb_arrestee_id", filtervarsting), with = FALSE]
  #Deduplicate by Incident ID, arrestee ID, and one instance of crime type
  main_filter_groupb <- main_filter_groupb[, .SD[1], by = c("ori",  "groupb_arrestee_id", filtervarsting)]
  
  log_debug("After filtering and deduping maindatagroupb")
  log_dim(main_filter_groupb)
  log_debug(system("free -mh", intern = FALSE))
  
  #Incident count
  s20 <- vector("list", 2)
  #For Table  
  s20[[1]] <- main_filter_groupb %>% 
    mutate(weighted_count = weight *!!infiltervar) %>%
    summarise(final_count = sum(weighted_count)) %>%
    mutate(section = 20)
  #For ORI level - Need unweighted counts
  s20[[2]] <- main_filter_groupb %>% 
    group_by(ori) %>%
    summarise(final_count = sum(!!infiltervar)) %>%
    ungroup() %>%
    mutate(section = 20)    
  
  #Total Denominator
  der_total_denom_groupb <- s20[[1]] %>% select(final_count) %>% as.double()		

  #Total Denominator
  der_total_denom <- s1[[1]] %>% select(final_count) %>% as.double()	
  #Need to add on the Group B
  der_total_denom <- sum(der_total_denom, der_total_denom_groupb, na.rm=TRUE)
  
  
  log_debug("After computing the group b arrest counts")
  log_debug(system("free -mh", intern = FALSE))  
  
  #arrestee sex
  s23 <- agg_percent_CAA_arrestee_groupb(leftdata = main_filter_groupb, rightdata = agg_arrestee_gender_arrestee_groupb, var=der_arrestee_gender, section=23, mergeby=c(  "groupb_arrestee_id"), denom=  der_total_denom)  
  
  der_denom_arrestee_male_groupb <- s23[[1]] %>%
    filter(der_arrestee_gender == 1) %>% 
    select(final_count) %>% 
    as.double()    
  
  der_denom_arrestee_female_groupb <- s23[[1]] %>%
    filter(der_arrestee_gender == 2) %>% 
    select(final_count) %>% 
    as.double()    
  
  der_denom_arrestee_unknown_groupb <- s23[[1]] %>%
    filter(der_arrestee_gender == 3) %>% 
    select(final_count) %>% 
    as.double()    
  
  
  
  #Arrestee armed
  s30 <- agg_percent_CAA_arrestee_groupb(leftdata = main_filter_groupb, rightdata = agg_weapon_no_yes_arrestee_groupb, var=der_weapon_no_yes, section=30, mergeby=c(  "groupb_arrestee_id"), denom=  der_total_denom)
  
  der_weapon_yes_denom_arrestee_groupb <- s30[[1]] %>%
    filter(der_weapon_no_yes == 2) %>% #Yes response
    select(final_count) %>% 
    as.double()   
  
  #Arrestee Age Group 2
  s32 <- agg_percent_CAA_arrestee_groupb(leftdata = main_filter_groupb, rightdata = agg_arrestee_age_cat_under18_2_arrestee_groupb_imp, var=der_arrestee_age_cat_under18_2, section=32, mergeby=c(  "groupb_arrestee_id"), denom=  der_total_denom)
  
  der_denom_arrestee_12_17_groupb <- s32[[1]] %>%
    filter(der_arrestee_age_cat_under18_2 == 2) %>% 
    select(final_count) %>% 
    as.double()    
  
  ######################################################################################
  


  log_debug("After computing the incident counts")
  log_debug(system("free -mh", intern = FALSE))

  #Arrest type
  s2 <- agg_percent_CAA_arrestee(leftdata = main_filter, rightdata = agg_arrest_type_arrestee, var=der_arrest_type, section=2, mergeby=c( "incident_id", "arrestee_id"), denom=  der_total_denom)    
  
  
  #arrestee Age
  s3 <- agg_percent_CAA_arrestee(leftdata = main_filter, rightdata = agg_arrestee_age_cat_15_17_arrestee, var=der_arrestee_age_cat_15_17, section=3, mergeby=c( "incident_id", "arrestee_id"), denom=  der_total_denom)  
  
  #arrestee sex
  s4 <- agg_percent_CAA_arrestee(leftdata = main_filter, rightdata = agg_arrestee_gender_arrestee, var=der_arrestee_gender, section=4, mergeby=c( "incident_id", "arrestee_id"), denom=  der_total_denom)  
  
  der_denom_arrestee_male <- s4[[1]] %>%
    filter(der_arrestee_gender == 1) %>% 
    select(final_count) %>% 
    as.double()    
  
  der_denom_arrestee_female <- s4[[1]] %>%
    filter(der_arrestee_gender == 2) %>% 
    select(final_count) %>% 
    as.double()    
  
  der_denom_arrestee_unknown <- s4[[1]] %>%
    filter(der_arrestee_gender == 3) %>% 
    select(final_count) %>% 
    as.double()    
  
  #Need to add on the Group B
  der_denom_arrestee_male <- sum(der_denom_arrestee_male, der_denom_arrestee_male_groupb, na.rm=TRUE)  
  der_denom_arrestee_female <- sum(der_denom_arrestee_female, der_denom_arrestee_female_groupb, na.rm=TRUE)  
  der_denom_arrestee_unknown <- sum(der_denom_arrestee_unknown, der_denom_arrestee_unknown_groupb, na.rm=TRUE)  
  
  
  #arrestee race
  s5 <- agg_percent_CAA_arrestee(leftdata = main_filter, rightdata = agg_arrestee_race_arrestee, var=der_arrestee_race, section=5, mergeby=c( "incident_id", "arrestee_id"), denom=  der_total_denom)  
  
  #arrestee sex and race
  s6 <- agg_percent_CAA_arrestee(leftdata = main_filter, rightdata = agg_arrestee_gender_race_arrestee_male, var=der_arrestee_gender_race, section=6, mergeby=c( "incident_id", "arrestee_id"), denom=  der_denom_arrestee_male)  
  
  s7 <- agg_percent_CAA_arrestee(leftdata = main_filter, rightdata = agg_arrestee_gender_race_arrestee_female, var=der_arrestee_gender_race, section=7, mergeby=c( "incident_id", "arrestee_id"), denom=  der_denom_arrestee_female)
  
  s7_1 <- agg_percent_CAA_arrestee(leftdata = main_filter, rightdata = agg_arrestee_gender_race_arrestee_unknown, var=der_arrestee_gender_race, section=7.1, mergeby=c( "incident_id", "arrestee_id"), denom=  der_denom_arrestee_unknown)  
  
  
  #arrestee sex - Extra for arrestee sex and race
  s8 <- agg_percent_CAA_arrestee(leftdata = main_filter, rightdata = agg_arrestee_gender_arrestee, var=der_arrestee_gender, section=8, mergeby=c( "incident_id", "arrestee_id"), denom=  der_total_denom) 
  
  #Juvenile disposition
  s9 <- agg_percent_CAA_arrestee(leftdata = main_filter, rightdata = agg_juvenile_disp_arrestee, var=der_juvenile_disp, section=9, mergeby=c( "incident_id", "arrestee_id"), denom=  der_total_denom)        
  
  #Multiple arrest indicator
  s10 <- agg_percent_arrestee(leftdata = main_filter, rightdata = agg_multiple_arrest_arrestee, var=der_multiple_arrest, section=10, mergeby=c( "incident_id", "arrestee_id"))     
  
  #Arrestee armed
  s11 <- agg_percent_CAA_arrestee(leftdata = main_filter, rightdata = agg_weapon_no_yes_arrestee, var=der_weapon_no_yes, section=11, mergeby=c( "incident_id", "arrestee_id"), denom=  der_total_denom)
  
  der_weapon_yes_denom_arrestee <- s11[[1]] %>%
    filter(der_weapon_no_yes == 2) %>% #Yes response
    select(final_count) %>% 
    as.double()  
  
  #Need to add on the Group B
  der_weapon_yes_denom_arrestee <- sum(der_weapon_yes_denom_arrestee,der_weapon_yes_denom_arrestee_groupb, na.rm=TRUE)  
  
  
  
  
  #Arrestee armed Categories
  s12 <- agg_percent_CAA_arrestee(leftdata = main_filter, rightdata = agg_weapon_yes_cat_arrestee, var=der_weapon_yes_cat, section=12, mergeby=c( "incident_id", "arrestee_id"), denom= der_weapon_yes_denom_arrestee)
  
  #Weapon involved - Incident Level
  s13 <- agg_percent_arrestee(leftdata = main_filter, rightdata = agg_weapon_no_yes, var=der_weapon_no_yes, section=13, mergeby=c( "incident_id"))
  
  der_weapon_yes_denom <- s13[[1]] %>%
    filter(der_weapon_no_yes == 2) %>% #Yes response
    select(final_count) %>% 
    as.double()    
  
  
  #Weapon involved Categories  - Incident Level
  s14 <- agg_percent_CAA_arrestee(leftdata = main_filter, rightdata = agg_weapon_yes_cat, var=der_weapon_yes_cat, section=14, mergeby=c( "incident_id"), denom = der_weapon_yes_denom)  
  
  #Arrestee Age 2

  s15 <- agg_percent_CAA_arrestee(leftdata = main_filter, rightdata = agg_arrestee_age_cat_under18_2_arrestee_imp, var=der_arrestee_age_cat_under18_2, section=15, mergeby=c( "incident_id", "arrestee_id"), denom=  der_total_denom)
  
  der_denom_arrestee_12_17 <- s15[[1]] %>%
    filter(der_arrestee_age_cat_under18_2 == 2) %>% 
    select(final_count) %>% 
    as.double()   
  
  #Need to add on the Group B
  der_denom_arrestee_12_17 <- sum(der_denom_arrestee_12_17, der_denom_arrestee_12_17_groupb, na.rm=TRUE)    
  
  s16 <- agg_percent_CAA_arrestee(leftdata = main_filter, rightdata = agg_arrestee_age_cat_12_17_cat_arrestee_imp, var=der_arrestee_age_cat_12_17_cat, section=16, mergeby=c( "incident_id", "arrestee_id"), denom=  der_denom_arrestee_12_17)
  s17 <- agg_percent_CAA_arrestee(leftdata = main_filter, rightdata = agg_arrestee_age_cat_2_uo18_arrestee_imp,    var=der_arrestee_age_cat_2_uo18,    section=17, mergeby=c( "incident_id", "arrestee_id"), denom=  der_total_denom)

  #Arrestee Hispanic Origin
  s18 <- agg_percent_CAA_arrestee(leftdata = main_filter, rightdata = agg_arrestee_ethnicity_arrestee, var=der_arrestee_ethnicity, section=18, mergeby=c( "incident_id", "arrestee_id"), denom=  der_total_denom)
  
  #Arrestee race and Hispanic Origin
  s19 <- agg_percent_CAA_arrestee(leftdata = main_filter, rightdata = agg_arrestee_ethnicity_race_arrestee, var=der_arrestee_ethnicity_race, section=19, mergeby=c( "incident_id", "arrestee_id"), denom=  der_total_denom)
  
  ################################################Group B Arrestee######################################################################################
  # #Need to drop the missing arrestee
  # maindatagroupb <- maindatagroupb %>%
  #   filter(!is.na(groupb_arrestee_id))
  # 
  # log_debug("After dropping missing arrestees groupb")
  # log_debug(system("free -mh", intern = FALSE))
  # 
  # 
  # #Filter the dataset
  # main_filter_groupb <- maindatagroupb[eval(infilter), c("ori", "weight",  "groupb_arrestee_id", filtervarsting), with = FALSE]
  # #Deduplicate by Incident ID, arrestee ID, and one instance of crime type
  # main_filter_groupb <- main_filter_groupb[, .SD[1], by = c("ori",  "groupb_arrestee_id", filtervarsting)]
  # 
  # log_debug("After filtering and deduping maindatagroupb")
  # log_dim(main_filter_groupb)
  # log_debug(system("free -mh", intern = FALSE))
  # 
  # #Incident count
  # s20 <- vector("list", 2)
  # #For Table  
  # s20[[1]] <- main_filter_groupb %>% 
  #   mutate(weighted_count = weight *!!infiltervar) %>%
  #   summarise(final_count = sum(weighted_count)) %>%
  #   mutate(section = 1)
  # #For ORI level - Need unweighted counts
  # s20[[2]] <- main_filter_groupb %>% 
  #   group_by(ori) %>%
  #   summarise(final_count = sum(!!infiltervar)) %>%
  #   ungroup() %>%
  #   mutate(section = 1)    
  # 
  # #Total Denominator
  # der_total_denom_groupb <- s20[[1]] %>% select(final_count) %>% as.double()						
  # 
  # 
  # log_debug("After computing the group b arrest counts")
  # log_debug(system("free -mh", intern = FALSE))
  
  #Arrest type
  s21 <- agg_percent_CAA_arrestee_groupb(leftdata = main_filter_groupb, rightdata = agg_arrest_type_arrestee_groupb, var=der_arrest_type, section=21, mergeby=c(  "groupb_arrestee_id"), denom=  der_total_denom)    
  
  
  #arrestee Age
  s22 <- agg_percent_CAA_arrestee_groupb(leftdata = main_filter_groupb, rightdata = agg_arrestee_age_cat_15_17_arrestee_groupb, var=der_arrestee_age_cat_15_17, section=22, mergeby=c(  "groupb_arrestee_id"), denom=  der_total_denom)  
  
  #arrestee sex - Create denominator early
  #s23 <- agg_percent_CAA_arrestee_groupb(leftdata = main_filter_groupb, rightdata = agg_arrestee_gender_arrestee_groupb, var=der_arrestee_gender, section=23, mergeby=c(  "groupb_arrestee_id"), denom=  der_total_denom)  
  
  #arrestee race
  s24 <- agg_percent_CAA_arrestee_groupb(leftdata = main_filter_groupb, rightdata = agg_arrestee_race_arrestee_groupb, var=der_arrestee_race, section=24, mergeby=c(  "groupb_arrestee_id"), denom=  der_total_denom)  
  
  #arrestee sex and race
  s25 <- agg_percent_CAA_arrestee_groupb(leftdata = main_filter_groupb, rightdata = agg_arrestee_gender_race_arrestee_groupb_male, var=der_arrestee_gender_race, section=25, mergeby=c(  "groupb_arrestee_id"), denom=  der_denom_arrestee_male)  
  
  s26 <- agg_percent_CAA_arrestee_groupb(leftdata = main_filter_groupb, rightdata = agg_arrestee_gender_race_arrestee_groupb_female, var=der_arrestee_gender_race, section=26, mergeby=c(  "groupb_arrestee_id"), denom=  der_denom_arrestee_female)
  
  s27 <- agg_percent_CAA_arrestee_groupb(leftdata = main_filter_groupb, rightdata = agg_arrestee_gender_race_arrestee_groupb_unknown, var=der_arrestee_gender_race, section=27, mergeby=c(  "groupb_arrestee_id"), denom=  der_denom_arrestee_unknown)  
  
  
  #arrestee sex - Extra for arrestee sex and race
  s28 <- agg_percent_CAA_arrestee_groupb(leftdata = main_filter_groupb, rightdata = agg_arrestee_gender_arrestee_groupb, var=der_arrestee_gender, section=28, mergeby=c(  "groupb_arrestee_id"), denom=  der_total_denom) 
  
  #Juvenile disposition
  s29 <- agg_percent_CAA_arrestee_groupb(leftdata = main_filter_groupb, rightdata = agg_juvenile_disp_arrestee_groupb, var=der_juvenile_disp, section=29, mergeby=c(  "groupb_arrestee_id"), denom=  der_total_denom)        
  
  #Multiple arrest indicator
  #Does not exist for Group B
  # s10 <- agg_percent_CAA_arrestee_groupb(leftdata = main_filter_groupb, rightdata = agg_multiple_arrest_arrestee_groupb, var=der_multiple_arrest, section=10, mergeby=c(  "groupb_arrestee_id"), denom=  der_total_denom)     
  
  #Arrestee armed
  # s30 <- agg_percent_CAA_arrestee_groupb(leftdata = main_filter_groupb, rightdata = agg_weapon_no_yes_arrestee_groupb, var=der_weapon_no_yes, section=30, mergeby=c(  "groupb_arrestee_id"), denom=  der_total_denom)
  # 
  # der_weapon_yes_denom_arrestee_groupb <- s30[[1]] %>%
  #   filter(der_weapon_no_yes == 2) %>% #Yes response
  #   select(final_count) %>% 
  #   as.double()  
  
  
  #Arrestee armed Categories
  s31 <- agg_percent_CAA_arrestee_groupb(leftdata = main_filter_groupb, rightdata = agg_weapon_yes_cat_arrestee_groupb, var=der_weapon_yes_cat, section=31, mergeby=c(  "groupb_arrestee_id"), denom= der_weapon_yes_denom_arrestee)
  
  #Weapon involved - Incident Level
  #Does not Exist for Group B
  # s13 <- agg_percent_CAA_arrestee_groupb(leftdata = main_filter_groupb, rightdata = agg_weapon_no_yes, var=der_weapon_no_yes, section=13, mergeby=c( "incident_id"))
  # 
  # der_weapon_yes_denom <- s13[[1]] %>%
  #   filter(der_weapon_no_yes == 2) %>% #Yes response
  #   select(final_count) %>% 
  #   as.double()    
  # 
  # 
  # #Weapon involved Categories  - Incident Level
  # s14 <- agg_percent_CAA_arrestee_groupb(leftdata = main_filter_groupb, rightdata = agg_weapon_yes_cat, var=der_weapon_yes_cat, section=14, mergeby=c( "incident_id"), denom = der_weapon_yes_denom)  
  
  #Arrestee Age 2
  
  #Commented out to create the 12-17 denominator early
  #s32 <- agg_percent_CAA_arrestee_groupb(leftdata = main_filter_groupb, rightdata = agg_arrestee_age_cat_under18_2_arrestee_groupb_imp, var=der_arrestee_age_cat_under18_2, section=32, mergeby=c(  "groupb_arrestee_id"), denom=  der_total_denom)
  s33 <- agg_percent_CAA_arrestee_groupb(leftdata = main_filter_groupb, rightdata = agg_arrestee_age_cat_12_17_cat_arrestee_groupb_imp, var=der_arrestee_age_cat_12_17_cat, section=33, mergeby=c(  "groupb_arrestee_id"), denom=  der_denom_arrestee_12_17)
  s34 <- agg_percent_CAA_arrestee_groupb(leftdata = main_filter_groupb, rightdata = agg_arrestee_age_cat_2_uo18_arrestee_groupb_imp,    var=der_arrestee_age_cat_2_uo18,    section=34, mergeby=c(  "groupb_arrestee_id"), denom=  der_total_denom)
  
  #Arrestee Hispanic Origin
  s35 <- agg_percent_CAA_arrestee_groupb(leftdata = main_filter_groupb, rightdata = agg_arrestee_ethnicity_arrestee_groupb, var=der_arrestee_ethnicity, section=35, mergeby=c(  "groupb_arrestee_id"), denom=  der_total_denom)
  
  #Arrestee race and Hispanic Origin
  s36 <- agg_percent_CAA_arrestee_groupb(leftdata = main_filter_groupb, rightdata = agg_arrestee_ethnicity_race_arrestee_groupb, var=der_arrestee_ethnicity_race, section=36, mergeby=c(  "groupb_arrestee_id"), denom=  der_total_denom)
  
  ####################################################################################################################################################################
    
  
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
  final_data4 <- assign_section(final_data3)  %>%
    ######Need to combine the Group A and B Arrestee#################
    group_by(section, row) %>%
    summarise(final_count = sum(final_count, na.rm=TRUE), 
              percent = sum(percent, na.rm=TRUE), 
              !!(incolumn_count) := sum(!!(incolumn_count), na.rm=TRUE),
              !!(incolumn_percentage) := sum(!!(incolumn_percentage), na.rm=TRUE),
    ) %>%
    ungroup() %>%
    #Drop missing data
    filter(!is.na(section) & !is.na(row))
  ####################################################################   
  
  #Keep variables and sort the dataset
  final_data5 <- final_data4 %>%
    select(section, row, !!incolumn_count, !!incolumn_percentage) %>%
    arrange(section, row)
  
  #Output data in reporting database
  
  #Create the filler dataset
  raw_filler <- c(1:DER_MAXIMUM_ROW) %>% as_tibble() %>% 
    rename(row = value)
  raw_filler <- assign_section(raw_filler)
  
  final_reporting_database <- 
    raw_filler %>% 
    left_join(final_data4, by=c("section","row") ) %>%
    mutate(column = column_number) %>%
    assign_labels() %>%
    arrange(section, row, column) %>%
    #Check to make sure that the NA are in the proper section
    mutate(final_count = case_when(is.na(final_count) ~ 0,
                                   TRUE ~ final_count),
           percent = case_when(is.na(percent) ~ 0,
                               TRUE ~ percent),
           
           #UPDATE this for each table:  Make the estimates of the database
           count    = case_when(row %in% c(1:DER_MAXIMUM_ROW) ~ final_count,
                                TRUE ~ DER_NA_CODE),
           percentage  = case_when(!row %in% c(1) ~ percent,
                                   TRUE ~ DER_NA_CODE),
           rate     = DER_NA_CODE,
           population_estimate     =  DER_NA_CODE) %>%
    select(full_table, table, section, row, estimate_domain, column, indicator_name,  count, percentage, rate, population_estimate) 
  
  #Create ORI dataset for variance estimation
  raw_list_ori2 <- raw_list_ori %>%
    bind_rows() %>%
    mutate(column = column_number) %>%
    assign_row() %>%
    assign_section() %>%
    ######Need to combine the Group A and B Arrestee#################
    group_by(ori, section, column, row) %>%
    summarise(final_count = sum(final_count, na.rm=TRUE)) %>%
    ungroup() %>%
    ####################################################################    
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
  
  #Need to fix final_data5 by adding on missing rows and zero filled
  final_data6 <- raw_filler %>%
    left_join(final_data5, by=c("section", "row")) %>%
    mutate(
      across(
        .cols = starts_with("final_count") | starts_with("percent"),
        .fns = ~{replace_na(data=., replace=0)}
      )
    )
  
  #Create list object to return
  return_object <- vector("list", 3)
  
  return_object[[1]] <- final_data6
  return_object[[2]] <- final_reporting_database
  return_object[[3]] <- raw_list_ori3
  
  return(return_object)  
  
  
}    


createadditionalcolumns <- function(intotalcolumn, incolumnstart, colindex, insubset, inperm_num_series){
  #Create new symbol to subset data
  insymbol <- insubset %>% rlang:::parse_expr()

  subsetvareq <- collist
  log_debug(paste0("About to generate_est for col",colindex))
  log_debug(system("free -mh", intern = FALSE))
    
  temp <- generate_est(
    maindata=main %>% filter(!!insymbol),
    maindatagroupb=main_group_b %>% filter(!!insymbol),
    subsetvareq1 = subsetvareq[colindex],
    column_number=colindex+inperm_num_series
  )
  return(temp)
}