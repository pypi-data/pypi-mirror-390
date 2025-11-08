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
    section == 3,  3,
    section == 4,  4,
    der_victim_age_cat_15_17 %in% c(1:10),  der_victim_age_cat_15_17 + 4,
    der_victim_gender %in% c(1:3) ,  der_victim_gender + 14,
    der_victim_race %in% c(1:6),  der_victim_race + 17,
    der_victim_age_cat_under18_2 %in% c(1:2), der_victim_age_cat_under18_2 + 23, ##Under 12, 12-17
    der_victim_age_cat_12_17_cat %in% c(1:2), der_victim_age_cat_12_17_cat + 25, #12-14, 15-17
    der_victim_age_cat_2_uo18 %in% c(2), 28, #2, #18+
    der_victim_age_cat_2_uo18 %in% c(3), 29, #3, #Unknown
    der_weapon_no_yes %in% c(1:2),  der_weapon_no_yes + 29,
    der_weapon_yes_cat %in% c(1:6),  der_weapon_yes_cat + 31,
    der_relationship %in% c(1:6),  der_relationship + 37,
	  der_raw_weapon_hierarchy_recode %in% c(1:18),  der_raw_weapon_hierarchy_recode + 43,
    der_relationship_hierarchy %in% c(1:8),  der_relationship_hierarchy + 61, 
  	#Victim Hispanic Origin
  	der_victim_ethnicity %in% c(1:3), der_victim_ethnicity + 69,
  	#Victim race and Hispanic Origin
  	der_victim_ethnicity_race %in% c(1:7), der_victim_ethnicity_race + 72	
    )
  )

  return(returndata)
}

assign_section <- function(data){
  log_debug("Running assign_section function")

  returndata <- data %>% mutate(

  section = fcase(
    row %in% c(1:4),  1,
    row %in% c(5:14),  2,
    row %in% c(15:17),  3,
    row %in% c(18:23),  4,
    row %in% c(24:29),  5,
    row %in% c(30:37),  6,
    row %in% c(38:43),  7,
  	row %in% c(44:61),  8,
  	row %in% c(62:69),  9,
    row %in% c(70:72),  10,
    row %in% c(73:79),  11    
    )
  )

  return(returndata)

}




#New add on code for labels
assign_labels <- function(data){
  log_debug("Running assign_labels function")

  returndata <- data %>% mutate(

  estimate_domain = fcase(

row == 1,  'Victimization count',
row == 2,  'Victimization count: Law enforcement officers',
row == 3,  'Victimization rate (per 100k total pop)',
row == 4,  'Victimization rate (per 100k LE staff): Law enforcement officers',
row == 5,  'Age-specific victimization rate: Under 5',
row == 6,  'Age-specific victimization rate: 5-14',
row == 7,  'Age-specific victimization rate: 15',
row == 8,  'Age-specific victimization rate: 16',
row == 9,  'Age-specific victimization rate: 17',
row == 10,  'Age-specific victimization rate: 18-24',
row == 11,  'Age-specific victimization rate: 25-34',
row == 12,  'Age-specific victimization rate: 35-64',
row == 13,  'Age-specific victimization rate: 65+',
row == 14,  'Age-specific victimization rate: Unknown',
row == 15,  'Sex-specific victimization rate: Male',
row == 16,  'Sex-specific victimization rate: Female',
row == 17,  'Sex-specific victimization rate: Unknown',
row == 18,  'Race-specific victimization rate: White',
row == 19,  'Race-specific victimization rate: Black',
row == 20,  'Race-specific victimization rate: American Indian or Alaska Native',
row == 21,  'Race-specific victimization rate: Asian',
row == 22,  'Race-specific victimization rate: Native Hawaiian or Other Pacific Islander',
row == 23,  'Race-specific victimization rate: Unknown',
row == 24, 'Victim Age 2: Under 12',
row == 25, 'Victim Age 2: 12-17',
row == 26, 'Victim Age 2: 12-14',
row == 27, 'Victim Age 2: 15-17',
row == 28, 'Victim Age 2: 18+',
row == 29, 'Victim Age 2: Unknown',
row == 30, 'Weapon involved: No',
row == 31, 'Weapon involved: Yes',
row == 32, 'Weapon involved: Personal weapons',
row == 33, 'Weapon involved: Firearms',
row == 34, 'Weapon involved: Knives and other cutting instruments',
row == 35, 'Weapon involved: Blunt instruments',
row == 36, 'Weapon involved: Other non-personal weapons',
row == 37, 'Weapon involved: Unknown',
row == 38, 'Victim-offender relationship: Intimate partner',
row == 39, 'Victim-offender relationship: Other family',
row == 40, 'Victim-offender relationship: Outside family but known to victim',
row == 41, 'Victim-offender relationship: Stranger',
row == 42, 'Victim-offender relationship: Victim was Offender',
row == 43, 'Victim-offender relationship: Unknown relationship',

row == 44, 'Weapon involved hierarchy: Handgun',
row == 45, 'Weapon involved hierarchy: Firearm',
row == 46, 'Weapon involved hierarchy: Rifle',
row == 47, 'Weapon involved hierarchy: Shotgun',
row == 48, 'Weapon involved hierarchy: Other Firearm',
row == 49, 'Weapon involved hierarchy: Knife/Cutting Instrument',
row == 50, 'Weapon involved hierarchy: Blunt Object',
row == 51, 'Weapon involved hierarchy: Motor Vehicle',
row == 52, 'Weapon involved hierarchy: Personal Weapons (hands, feet, teeth, etc.)',
row == 53, 'Weapon involved hierarchy: Asphyxiation',
row == 54, 'Weapon involved hierarchy: Drugs/Narcotics/Sleeping Pills',
row == 55, 'Weapon involved hierarchy: Poison (include gas)',
row == 56, 'Weapon involved hierarchy: Explosives',
row == 57, 'Weapon involved hierarchy: Fire/Incendiary Device',
row == 58, 'Weapon involved hierarchy: Other',
row == 59, 'Weapon involved hierarchy: No Weapon',
row == 60, 'Weapon involved hierarchy: Unknown',
row == 61, 'Weapon involved hierarchy: Not Applicable',
row == 62, 'Victim-offender relationship hierarchy: Intimate partner',
row == 63, 'Victim-offender relationship hierarchy: Other family',
row == 64, 'Victim-offender relationship hierarchy: Outside family but known to victim',
row == 65, 'Victim-offender relationship hierarchy: Stranger',
row == 66, 'Victim-offender relationship hierarchy: Victim was Offender',
row == 67, 'Victim-offender relationship hierarchy: Unknown relationship',
row == 68, 'Victim-offender relationship hierarchy: Unknown Offender Incidents',
row == 69, 'Victim-offender relationship hierarchy: Missing from Uncleared Incidents',

row == 70, 'Hispanic Origin-specific victimization rate: Hispanic or Latino',
row == 71, 'Hispanic Origin-specific victimization rate: Not Hispanic or Latino',
row == 72, 'Hispanic Origin-specific victimization rate: Unknown',
row == 73, 'Race and Hispanic Origin-specific victimization rate: Hispanic or Latino',
row == 74, 'Race and Hispanic Origin-specific victimization rate: Non-Hispanic, White',
row == 75, 'Race and Hispanic Origin-specific victimization rate: Non-Hispanic, Black',
row == 76, 'Race and Hispanic Origin-specific victimization rate: Non-Hispanic, American Indian or Alaska Native',
row == 77, 'Race and Hispanic Origin-specific victimization rate: Non-Hispanic, Asian',
row == 78, 'Race and Hispanic Origin-specific victimization rate: Non-Hispanic, Native Hawaiian or Other Pacific Islander',
row == 79, 'Race and Hispanic Origin-specific victimization rate: Unknown race or Hispanic origin'


  ),

  indicator_name = fcase(
column == 1,  'NIBRS crimes against persons (Total)',
column == 2,  'Aggravated Assault',
column == 3,  'Simple Assault',
column == 4,  'Intimidation',
column == 5,  'Murder and Non-negligent Manslaughter',
column == 6,  'Negligent Manslaughter',
column == 7,  'Kidnapping/Abduction',
column == 8,  'Human Trafficking-Sex',
column == 9,  'Human Trafficking-Labor',
column == 10,  'Rape',
column == 11,  'Sodomy',
column == 12,  'Sexual Assault with an Object',
column == 13,  'Fondling',
column == 14,  'Sex Offenses, Nonforcible',
column == 15,  'Revised Rape',
column == 16,  'Violent Crime',
column == 17, 'Robbery',
column == 18, 'NIBRS crimes against property (Total)',
column == 19, 'Arson',
column == 20, 'Bribery',
column == 21, 'Burglary/B&E',
column == 22, 'Counterfeiting/Forgery',
column == 23, 'Destruction/Damage/Vandalism',
column == 24, 'Embezzlement',
column == 25, 'Extortion/Blackmail',
column == 26, 'Fraud Offenses',
column == 27, 'Larceny/Theft Offenses',
column == 28, 'Motor Vehicle Theft',
column == 29, 'Stolen Property Offenses',
column == 30, 'Property Crime',
column == 31, 'Car Jacking',
column == 32, 'Assault Offenses',
column == 33, 'Violent Crime 2'




  ),

  full_table = full_table,
  table = DER_TABLE_NAME
  )

  return(returndata)

}

estimate_type_detail_percentage_label <- function(indata){
  log_debug("Running estimate_type_detail_percentage_label function")

  returndata <- indata %>%
    mutate(
      estimate_type_detail_percentage = fcase(
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 1,  'Victim Level', #Victimization count
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 2,  'Victim Level', #Victimization count: Law enforcement officers
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 3,  'Victim Level', #Victimization rate (per 100k total pop)
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 4,  'Victim Level', #Victimization rate (per 100k LE staff): Law enforcement officers
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 5,  'Victim Level', #Age-specific victimization rate: Under 5
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 6,  'Victim Level', #Age-specific victimization rate: 5-14
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 7,  'Victim Level', #Age-specific victimization rate: 15
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 8,  'Victim Level', #Age-specific victimization rate: 16
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 9,  'Victim Level', #Age-specific victimization rate: 17
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 10,  'Victim Level', #Age-specific victimization rate: 18-24
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 11,  'Victim Level', #Age-specific victimization rate: 25-34
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 12,  'Victim Level', #Age-specific victimization rate: 35-64
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 13,  'Victim Level', #Age-specific victimization rate: 65+
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 14,  'Victim Level', #Age-specific victimization rate: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 15,  'Victim Level', #Sex-specific victimization rate: Male
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 16,  'Victim Level', #Sex-specific victimization rate: Female
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 17,  'Victim Level', #Sex-specific victimization rate: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 18,  'Victim Level', #Race-specific victimization rate: White
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 19,  'Victim Level', #Race-specific victimization rate: Black
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 20,  'Victim Level', #Race-specific victimization rate: American Indian or Alaska Native
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 21,  'Victim Level', #Race-specific victimization rate: Asian
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 22,  'Victim Level', #Race-specific victimization rate: Native Hawaiian or Other Pacific Islander
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 23,  'Victim Level', #Race-specific victimization rate: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 24, 'Victim Level', #Victim Age 2: Under 12
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 25, 'Victim Level', #Victim Age 2: 12-17
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 26, 'Victim Level', #Victim Age 2: 12-14
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 27, 'Victim Level', #Victim Age 2: 15-17
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 28, 'Victim Level', #Victim Age 2: 18+
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 29, 'Victim Level', #Victim Age 2: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 30, 'Victim Level', #Weapon involved: No
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 31, 'Victim Level', #Weapon involved: Yes
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 32, 'Victim Level', #Weapon involved: Personal weapons
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 33, 'Victim Level', #Weapon involved: Firearms
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 34, 'Victim Level', #Weapon involved: Knives and other cutting instruments
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 35, 'Victim Level', #Weapon involved: Blunt instruments
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 36, 'Victim Level', #Weapon involved: Other non-personal weapons
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 37, 'Victim Level', #Weapon involved: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 38, 'Victim Level', #Victim-offender relationship: Intimate partner
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 39, 'Victim Level', #Victim-offender relationship: Other family
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 40, 'Victim Level', #Victim-offender relationship: Outside family but known to victim
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 41, 'Victim Level', #Victim-offender relationship: Stranger
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 42, 'Victim Level', #Victim-offender relationship: Victim was Offender
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 43, 'Victim Level', #Victim-offender relationship: Unknown relationship

trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 44, 'Victim Level', #Weapon involved hierarchy: Handgun
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 45, 'Victim Level', #Weapon involved hierarchy: Firearm
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 46, 'Victim Level', #Weapon involved hierarchy: Rifle
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 47, 'Victim Level', #Weapon involved hierarchy: Shotgun
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 48, 'Victim Level', #Weapon involved hierarchy: Other Firearm
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 49, 'Victim Level', #Weapon involved hierarchy: Knife/Cutting Instrument
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 50, 'Victim Level', #Weapon involved hierarchy: Blunt Object
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 51, 'Victim Level', #Weapon involved hierarchy: Motor Vehicle
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 52, 'Victim Level', #Weapon involved hierarchy: Personal Weapons (hands, feet, teeth, etc.)
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 53, 'Victim Level', #Weapon involved hierarchy: Asphyxiation
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 54, 'Victim Level', #Weapon involved hierarchy: Drugs/Narcotics/Sleeping Pills
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 55, 'Victim Level', #Weapon involved hierarchy: Poison (include gas)
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 56, 'Victim Level', #Weapon involved hierarchy: Explosives
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 57, 'Victim Level', #Weapon involved hierarchy: Fire/Incendiary Device
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 58, 'Victim Level', #Weapon involved hierarchy: Other
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 59, 'Victim Level', #Weapon involved hierarchy: No Weapon
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 60, 'Victim Level', #Weapon involved hierarchy: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 61, 'Victim Level', #Weapon involved hierarchy: Not Applicable
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 62, 'Victim Level', #Victim-offender relationship hierarchy: Intimate partner
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 63, 'Victim Level', #Victim-offender relationship hierarchy: Other family
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 64, 'Victim Level', #Victim-offender relationship hierarchy: Outside family but known to victim
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 65, 'Victim Level', #Victim-offender relationship hierarchy: Stranger
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 66, 'Victim Level', #Victim-offender relationship hierarchy: Victim was Offender
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 67, 'Victim Level', #Victim-offender relationship hierarchy: Unknown relationship
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 68, 'Victim Level', #Victim-offender relationship hierarchy: Unknown Offender Incidents
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 69, 'Victim Level', #Victim-offender relationship hierarchy: Missing from Uncleared Incidents

trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 70, 'Victim Level', #Hispanic Origin-specific victimization rate: Hispanic or Latino
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 71, 'Victim Level', #Hispanic Origin-specific victimization rate: Not Hispanic or Latino
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 72, 'Victim Level', #Hispanic Origin-specific victimization rate: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 73, 'Victim Level', #Race and Hispanic Origin-specific victimization rate: Hispanic or Latino
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 74, 'Victim Level', #Race and Hispanic Origin-specific victimization rate: Non-Hispanic, White
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 75, 'Victim Level', #Race and Hispanic Origin-specific victimization rate: Non-Hispanic, Black
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 76, 'Victim Level', #Race and Hispanic Origin-specific victimization rate: Non-Hispanic, American Indian or Alaska Native
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 77, 'Victim Level', #Race and Hispanic Origin-specific victimization rate: Non-Hispanic, Asian
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 78, 'Victim Level', #Race and Hispanic Origin-specific victimization rate: Non-Hispanic, Native Hawaiian or Other Pacific Islander
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 79, 'Victim Level' #Race and Hispanic Origin-specific victimization rate: Unknown race or Hispanic origin


))

  return(returndata)
}

estimate_type_detail_rate_label <- function(indata){
  log_debug("Running estimate_type_detail_rate_label function")

  returndata <- indata %>%
    mutate(
      estimate_type_detail_rate = fcase(

trim_upcase(estimate_type) %in% c('RATE') & row == 1,  DER_NA_CODE_STRING, #Victimization count
trim_upcase(estimate_type) %in% c('RATE') & row == 2,  DER_NA_CODE_STRING, #Victimization count: Law enforcement officers
trim_upcase(estimate_type) %in% c('RATE') & row == 3,  'Victim rate per 100,000 persons', #Victimization rate (per 100k total pop)
trim_upcase(estimate_type) %in% c('RATE') & row == 4,  'Victim rate per 100,000 LE staff', #Victimization rate (per 100k LE staff): Law enforcement officers
trim_upcase(estimate_type) %in% c('RATE') & row == 5,  'Victim rate per 100,000 persons among persons Under 5', #Age-specific victimization rate: Under 5
trim_upcase(estimate_type) %in% c('RATE') & row == 6,  'Victim rate per 100,000 persons among persons 5-14', #Age-specific victimization rate: 5-14
trim_upcase(estimate_type) %in% c('RATE') & row == 7,  'Victim rate per 100,000 persons among persons 15', #Age-specific victimization rate: 15
trim_upcase(estimate_type) %in% c('RATE') & row == 8,  'Victim rate per 100,000 persons among persons 16', #Age-specific victimization rate: 16
trim_upcase(estimate_type) %in% c('RATE') & row == 9,  'Victim rate per 100,000 persons among persons 17', #Age-specific victimization rate: 17
trim_upcase(estimate_type) %in% c('RATE') & row == 10,  'Victim rate per 100,000 persons among persons 18-24', #Age-specific victimization rate: 18-24
trim_upcase(estimate_type) %in% c('RATE') & row == 11,  'Victim rate per 100,000 persons among persons 25-34', #Age-specific victimization rate: 25-34
trim_upcase(estimate_type) %in% c('RATE') & row == 12,  'Victim rate per 100,000 persons among persons 35-64', #Age-specific victimization rate: 35-64
trim_upcase(estimate_type) %in% c('RATE') & row == 13,  'Victim rate per 100,000 persons among persons 65+', #Age-specific victimization rate: 65+
trim_upcase(estimate_type) %in% c('RATE') & row == 14,  'Victim rate per 100,000 persons', #Age-specific victimization rate: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 15,  'Victim rate per 100,000 persons among persons Male', #Sex-specific victimization rate: Male
trim_upcase(estimate_type) %in% c('RATE') & row == 16,  'Victim rate per 100,000 persons among persons Female', #Sex-specific victimization rate: Female
trim_upcase(estimate_type) %in% c('RATE') & row == 17,  'Victim rate per 100,000 persons', #Sex-specific victimization rate: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 18,  'Victim rate per 100,000 persons among persons White', #Race-specific victimization rate: White
trim_upcase(estimate_type) %in% c('RATE') & row == 19,  'Victim rate per 100,000 persons among persons Black', #Race-specific victimization rate: Black
trim_upcase(estimate_type) %in% c('RATE') & row == 20,  'Victim rate per 100,000 persons among persons American Indian or Alaska Native', #Race-specific victimization rate: American Indian or Alaska Native
trim_upcase(estimate_type) %in% c('RATE') & row == 21,  'Victim rate per 100,000 persons among persons Asian', #Race-specific victimization rate: Asian
trim_upcase(estimate_type) %in% c('RATE') & row == 22,  'Victim rate per 100,000 persons among persons Native Hawaiian or Other Pacific Islander', #Race-specific victimization rate: Native Hawaiian or Other Pacific Islander
trim_upcase(estimate_type) %in% c('RATE') & row == 23,  'Victim rate per 100,000 persons', #Race-specific victimization rate: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 24, 'Victim rate per 100,000 persons among persons Under 12', #Victim Age 2: Under 12
trim_upcase(estimate_type) %in% c('RATE') & row == 25, 'Victim rate per 100,000 persons among persons 12-17', #Victim Age 2: 12-17
trim_upcase(estimate_type) %in% c('RATE') & row == 26, 'Victim rate per 100,000 persons among persons 12-14', #Victim Age 2: 12-14
trim_upcase(estimate_type) %in% c('RATE') & row == 27, 'Victim rate per 100,000 persons among persons 15-17', #Victim Age 2: 15-17
trim_upcase(estimate_type) %in% c('RATE') & row == 28, 'Victim rate per 100,000 persons among persons 18+', #Victim Age 2: 18+
trim_upcase(estimate_type) %in% c('RATE') & row == 29, 'Victim rate per 100,000 persons', #Victim Age 2: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 30, 'Victim rate per 100,000 persons', #Weapon involved: No
trim_upcase(estimate_type) %in% c('RATE') & row == 31, 'Victim rate per 100,000 persons', #Weapon involved: Yes
trim_upcase(estimate_type) %in% c('RATE') & row == 32, 'Victim rate per 100,000 persons', #Weapon involved: Personal weapons
trim_upcase(estimate_type) %in% c('RATE') & row == 33, 'Victim rate per 100,000 persons', #Weapon involved: Firearms
trim_upcase(estimate_type) %in% c('RATE') & row == 34, 'Victim rate per 100,000 persons', #Weapon involved: Knives and other cutting instruments
trim_upcase(estimate_type) %in% c('RATE') & row == 35, 'Victim rate per 100,000 persons', #Weapon involved: Blunt instruments
trim_upcase(estimate_type) %in% c('RATE') & row == 36, 'Victim rate per 100,000 persons', #Weapon involved: Other non-personal weapons
trim_upcase(estimate_type) %in% c('RATE') & row == 37, 'Victim rate per 100,000 persons', #Weapon involved: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 38, 'Victim rate per 100,000 persons', #Victim-offender relationship: Intimate partner
trim_upcase(estimate_type) %in% c('RATE') & row == 39, 'Victim rate per 100,000 persons', #Victim-offender relationship: Other family
trim_upcase(estimate_type) %in% c('RATE') & row == 40, 'Victim rate per 100,000 persons', #Victim-offender relationship: Outside family but known to victim
trim_upcase(estimate_type) %in% c('RATE') & row == 41, 'Victim rate per 100,000 persons', #Victim-offender relationship: Stranger
trim_upcase(estimate_type) %in% c('RATE') & row == 42, 'Victim rate per 100,000 persons', #Victim-offender relationship: Victim was Offender
trim_upcase(estimate_type) %in% c('RATE') & row == 43, 'Victim rate per 100,000 persons', #Victim-offender relationship: Unknown relationship

trim_upcase(estimate_type) %in% c('RATE') & row == 44, 'Victim rate per 100,000 persons', #Weapon involved hierarchy: Handgun
trim_upcase(estimate_type) %in% c('RATE') & row == 45, 'Victim rate per 100,000 persons', #Weapon involved hierarchy: Firearm
trim_upcase(estimate_type) %in% c('RATE') & row == 46, 'Victim rate per 100,000 persons', #Weapon involved hierarchy: Rifle
trim_upcase(estimate_type) %in% c('RATE') & row == 47, 'Victim rate per 100,000 persons', #Weapon involved hierarchy: Shotgun
trim_upcase(estimate_type) %in% c('RATE') & row == 48, 'Victim rate per 100,000 persons', #Weapon involved hierarchy: Other Firearm
trim_upcase(estimate_type) %in% c('RATE') & row == 49, 'Victim rate per 100,000 persons', #Weapon involved hierarchy: Knife/Cutting Instrument
trim_upcase(estimate_type) %in% c('RATE') & row == 50, 'Victim rate per 100,000 persons', #Weapon involved hierarchy: Blunt Object
trim_upcase(estimate_type) %in% c('RATE') & row == 51, 'Victim rate per 100,000 persons', #Weapon involved hierarchy: Motor Vehicle
trim_upcase(estimate_type) %in% c('RATE') & row == 52, 'Victim rate per 100,000 persons', #Weapon involved hierarchy: Personal Weapons (hands, feet, teeth, etc.)
trim_upcase(estimate_type) %in% c('RATE') & row == 53, 'Victim rate per 100,000 persons', #Weapon involved hierarchy: Asphyxiation
trim_upcase(estimate_type) %in% c('RATE') & row == 54, 'Victim rate per 100,000 persons', #Weapon involved hierarchy: Drugs/Narcotics/Sleeping Pills
trim_upcase(estimate_type) %in% c('RATE') & row == 55, 'Victim rate per 100,000 persons', #Weapon involved hierarchy: Poison (include gas)
trim_upcase(estimate_type) %in% c('RATE') & row == 56, 'Victim rate per 100,000 persons', #Weapon involved hierarchy: Explosives
trim_upcase(estimate_type) %in% c('RATE') & row == 57, 'Victim rate per 100,000 persons', #Weapon involved hierarchy: Fire/Incendiary Device
trim_upcase(estimate_type) %in% c('RATE') & row == 58, 'Victim rate per 100,000 persons', #Weapon involved hierarchy: Other
trim_upcase(estimate_type) %in% c('RATE') & row == 59, 'Victim rate per 100,000 persons', #Weapon involved hierarchy: No Weapon
trim_upcase(estimate_type) %in% c('RATE') & row == 60, 'Victim rate per 100,000 persons', #Weapon involved hierarchy: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 61, 'Victim rate per 100,000 persons', #Weapon involved hierarchy: Not Applicable
trim_upcase(estimate_type) %in% c('RATE') & row == 62, 'Victim rate per 100,000 persons', #Victim-offender relationship hierarchy: Intimate partner
trim_upcase(estimate_type) %in% c('RATE') & row == 63, 'Victim rate per 100,000 persons', #Victim-offender relationship hierarchy: Other family
trim_upcase(estimate_type) %in% c('RATE') & row == 64, 'Victim rate per 100,000 persons', #Victim-offender relationship hierarchy: Outside family but known to victim
trim_upcase(estimate_type) %in% c('RATE') & row == 65, 'Victim rate per 100,000 persons', #Victim-offender relationship hierarchy: Stranger
trim_upcase(estimate_type) %in% c('RATE') & row == 66, 'Victim rate per 100,000 persons', #Victim-offender relationship hierarchy: Victim was Offender
trim_upcase(estimate_type) %in% c('RATE') & row == 67, 'Victim rate per 100,000 persons', #Victim-offender relationship hierarchy: Unknown relationship
trim_upcase(estimate_type) %in% c('RATE') & row == 68, 'Victim rate per 100,000 persons', #Victim-offender relationship hierarchy: Unknown Offender Incidents
trim_upcase(estimate_type) %in% c('RATE') & row == 69, 'Victim rate per 100,000 persons', #Victim-offender relationship hierarchy: Missing from Uncleared Incidents

trim_upcase(estimate_type) %in% c('RATE') & row == 70, 'Victim rate per 100,000 persons among persons Hispanic or Latino', #Hispanic Origin-specific victimization rate: Hispanic or Latino
trim_upcase(estimate_type) %in% c('RATE') & row == 71, 'Victim rate per 100,000 persons among persons Not Hispanic or Latino', #Hispanic Origin-specific victimization rate: Not Hispanic or Latino
trim_upcase(estimate_type) %in% c('RATE') & row == 72, 'Victim rate per 100,000 persons', #Hispanic Origin-specific victimization rate: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 73, 'Victim rate per 100,000 persons among persons Hispanic or Latino', #Race and Hispanic Origin-specific victimization rate: Hispanic or Latino
trim_upcase(estimate_type) %in% c('RATE') & row == 74, 'Victim rate per 100,000 persons among persons Non-Hispanic, White', #Race and Hispanic Origin-specific victimization rate: Non-Hispanic, White
trim_upcase(estimate_type) %in% c('RATE') & row == 75, 'Victim rate per 100,000 persons among persons Non-Hispanic, Black', #Race and Hispanic Origin-specific victimization rate: Non-Hispanic, Black
trim_upcase(estimate_type) %in% c('RATE') & row == 76, 'Victim rate per 100,000 persons among persons Non-Hispanic, American Indian or Alaska Native', #Race and Hispanic Origin-specific victimization rate: Non-Hispanic, American Indian or Alaska Native
trim_upcase(estimate_type) %in% c('RATE') & row == 77, 'Victim rate per 100,000 persons among persons Non-Hispanic, Asian', #Race and Hispanic Origin-specific victimization rate: Non-Hispanic, Asian
trim_upcase(estimate_type) %in% c('RATE') & row == 78, 'Victim rate per 100,000 persons among persons Non-Hispanic, Native Hawaiian or Other Pacific Islander', #Race and Hispanic Origin-specific victimization rate: Non-Hispanic, Native Hawaiian or Other Pacific Islander
trim_upcase(estimate_type) %in% c('RATE') & row == 79, 'Victim rate per 100,000 persons' #Race and Hispanic Origin-specific victimization rate: Unknown race or Hispanic origin



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


  #Filter the dataset
  main_filter <- maindata[eval(infilter), c("ori", "weight", "incident_id", "victim_id", "offense_id", "der_victim_LEO", filtervarsting), with = FALSE]
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

  #Incident count for LEO - Hard code the variable
  s2 <- vector("list", 2)
  #For Table
  s2[[1]] <- main_filter %>%
    filter(der_victim_LEO == 1) %>%
    mutate(weighted_count = weight *!!infiltervar) %>%
    summarise(final_count = sum(weighted_count)) %>%
    mutate(section = 2)
  #For ORI level - Need unweighted counts
  s2[[2]] <- main_filter %>%
    filter(der_victim_LEO == 1) %>%
    group_by(ori) %>%
    summarise(final_count = sum(!!infiltervar)) %>%
    ungroup() %>%
    mutate(section = 2)

  #Incident rate
  s3 <- vector("list", 2)
  #For Table
  s3[[1]] <- s1[[1]] %>%
    mutate(final_count = (final_count / POP_TOTAL) * 100000,
           population_estimate = POP_TOTAL ) %>%
    mutate(section = 3)
  #For ORI level - Need unweighted counts
  s3[[2]] <- main_filter %>%
    group_by(ori) %>%
    summarise(final_count = sum(!!infiltervar)) %>%
    ungroup() %>%
    mutate(section = 3)

  #Incident rate for LEO
  s4 <- vector("list", 2)
  #For Table
  s4[[1]] <- s2[[1]] %>%
    mutate(final_count = (final_count / DER_POP_OFFICER_NUM) * 100000,
           population_estimate = DER_POP_OFFICER_NUM ) %>%
    mutate(section = 4)
  #For ORI level - Need unweighted counts
  s4[[2]] <- main_filter %>%
    filter(der_victim_LEO == 1) %>%
    group_by(ori) %>%
    summarise(final_count = sum(!!infiltervar)) %>%
    ungroup() %>%
    mutate(section = 4)


  #Victim Age
  #Under 5
  s5 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_age_cat_15_17_victim %>% filter(der_victim_age_cat_15_17 == 1), var=der_victim_age_cat_15_17, section=5, mergeby=c( "incident_id", "victim_id"), denom=DER_POP_PCTAGELT5_NUM)
  #5-14
  s6 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_age_cat_15_17_victim %>% filter(der_victim_age_cat_15_17 == 2), var=der_victim_age_cat_15_17, section=6, mergeby=c( "incident_id", "victim_id"), denom=DER_POP_PCTAGE5TO14_NUM)
  #15
  s7 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_age_cat_15_17_victim %>% filter(der_victim_age_cat_15_17 == 3), var=der_victim_age_cat_15_17, section=7, mergeby=c( "incident_id", "victim_id"), denom=DER_POP_PCTAGE15_NUM)
  #16
  s8 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_age_cat_15_17_victim %>% filter(der_victim_age_cat_15_17 == 4), var=der_victim_age_cat_15_17, section=8, mergeby=c( "incident_id", "victim_id"), denom=DER_POP_PCTAGE16_NUM)
  #17
  s9 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_age_cat_15_17_victim %>% filter(der_victim_age_cat_15_17 == 5), var=der_victim_age_cat_15_17, section=9, mergeby=c( "incident_id", "victim_id"), denom=DER_POP_PCTAGE17_NUM)

  #18-24
  s10 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_age_cat_15_17_victim %>% filter(der_victim_age_cat_15_17 == 6), var=der_victim_age_cat_15_17, section=10, mergeby=c( "incident_id", "victim_id"), denom=DER_POP_PCTAGE18TO24_NUM)
  #25-34
  s11 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_age_cat_15_17_victim %>% filter(der_victim_age_cat_15_17 == 7), var=der_victim_age_cat_15_17, section=11, mergeby=c( "incident_id", "victim_id"), denom=DER_POP_PCTAGE25TO34_NUM)
  #35-64
  s12 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_age_cat_15_17_victim %>% filter(der_victim_age_cat_15_17 == 8), var=der_victim_age_cat_15_17, section=12, mergeby=c( "incident_id", "victim_id"), denom=DER_POP_PCTAGE35TO64_NUM)
  #65+
  s13 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_age_cat_15_17_victim %>% filter(der_victim_age_cat_15_17 == 9), var=der_victim_age_cat_15_17, section=13, mergeby=c( "incident_id", "victim_id"), denom=DER_POP_PCTAGEGTE65_NUM)
  #Unknown
  s14 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_age_cat_15_17_victim %>% filter(der_victim_age_cat_15_17 == 10), var=der_victim_age_cat_15_17, section=14, mergeby=c( "incident_id", "victim_id"), denom=POP_TOTAL)


  #Victim sex
  #Male
  s15 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_gender_victim %>% filter(der_victim_gender == 1), var=der_victim_gender, section=15, mergeby=c( "incident_id", "victim_id"), denom=DER_POP_PCTSEXMALE_NUM)
  #Female
  s16 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_gender_victim %>% filter(der_victim_gender == 2), var=der_victim_gender, section=16, mergeby=c( "incident_id", "victim_id"), denom=DER_POP_PCTSEXFEMALE_NUM)
  #Unknown
  s17 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_gender_victim %>% filter(der_victim_gender == 3), var=der_victim_gender, section=17, mergeby=c( "incident_id", "victim_id"), denom=POP_TOTAL)


  #Victim race
  #White
    s18 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_race_victim %>% filter(der_victim_race == 1), var=der_victim_race, section=18, mergeby=c( "incident_id", "victim_id"), denom=DER_POP_PCTRACEWHITE_NUM)
  #Black
    s19 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_race_victim %>% filter(der_victim_race == 2), var=der_victim_race, section=19, mergeby=c( "incident_id", "victim_id"), denom=DER_POP_PCTRACEBLACK_NUM)
  #American Indian or Alaska Native
    s20 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_race_victim %>% filter(der_victim_race == 3), var=der_victim_race, section=20, mergeby=c( "incident_id", "victim_id"), denom=DER_POP_PCTRACEAIAN_NUM)
  #Asian
    s21 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_race_victim %>% filter(der_victim_race == 4), var=der_victim_race, section=21, mergeby=c( "incident_id", "victim_id"), denom=DER_POP_PCTRACEASIAN_NUM)
  #Native Hawaiian or Other Pacific Islander
    s22 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_race_victim %>% filter(der_victim_race == 5), var=der_victim_race, section=22, mergeby=c( "incident_id", "victim_id"), denom=DER_POP_PCTRACENHPI_NUM)
  #Unknown
    s23 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_race_victim %>% filter(der_victim_race == 6), var=der_victim_race, section=23, mergeby=c( "incident_id", "victim_id"), denom=POP_TOTAL)

    s24 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_age_cat_under18_2_victim_imp %>% filter(der_victim_age_cat_under18_2 == 1), var=der_victim_age_cat_under18_2, section=24, mergeby=c( "incident_id", "victim_id"), denom=DER_POP_PCTAGE_UNDER_12_NUM) #Victim Age 2 :   Under 12
    s25 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_age_cat_under18_2_victim_imp %>% filter(der_victim_age_cat_under18_2 == 2), var=der_victim_age_cat_under18_2, section=25, mergeby=c( "incident_id", "victim_id"), denom=DER_POP_PCTAGE_12_17_NUM) #Victim Age 2 :   12-17
    s26 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_age_cat_12_17_cat_victim_imp %>% filter(der_victim_age_cat_12_17_cat == 1), var=der_victim_age_cat_12_17_cat, section=26, mergeby=c( "incident_id", "victim_id"), denom=DER_POP_PCTAGE_12_14_NUM) #Victim Age 2 :   12-14
    s27 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_age_cat_12_17_cat_victim_imp %>% filter(der_victim_age_cat_12_17_cat == 2), var=der_victim_age_cat_12_17_cat, section=27, mergeby=c( "incident_id", "victim_id"), denom=DER_POP_PCTAGE_15_17_NUM) #Victim Age 2 :   15-17
    s28 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_age_cat_2_uo18_victim_imp %>% filter(der_victim_age_cat_2_uo18 == 2), var=der_victim_age_cat_2_uo18, section=28, mergeby=c( "incident_id", "victim_id"), denom=DER_POP_PCTAGE_OVER_18_NUM) #Victim Age 2 : 18+
    s29 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_age_cat_2_uo18_victim_imp %>% filter(der_victim_age_cat_2_uo18 == 3), var=der_victim_age_cat_2_uo18, section=29, mergeby=c( "incident_id", "victim_id"), denom=POP_TOTAL) #Victim Age 2 :   Unknown
    s30 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_weapon_no_yes_victim %>% filter(der_weapon_no_yes == 1), var=der_weapon_no_yes, section=30, mergeby=c( "incident_id", "victim_id"), denom=POP_TOTAL) #Weapon involved :   No
    s31 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_weapon_no_yes_victim %>% filter(der_weapon_no_yes == 2), var=der_weapon_no_yes, section=31, mergeby=c( "incident_id", "victim_id"), denom=POP_TOTAL) #Weapon involved :   Yes
    s32 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_weapon_yes_cat_victim %>% filter(der_weapon_yes_cat == 1), var=der_weapon_yes_cat, section=32, mergeby=c( "incident_id", "victim_id"), denom=POP_TOTAL) #Weapon involved :           Personal weapons
    s33 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_weapon_yes_cat_victim %>% filter(der_weapon_yes_cat == 2), var=der_weapon_yes_cat, section=33, mergeby=c( "incident_id", "victim_id"), denom=POP_TOTAL) #Weapon involved :           Firearms
    s34 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_weapon_yes_cat_victim %>% filter(der_weapon_yes_cat == 3), var=der_weapon_yes_cat, section=34, mergeby=c( "incident_id", "victim_id"), denom=POP_TOTAL) #Weapon involved :           Knives and other cutting instruments
    s35 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_weapon_yes_cat_victim %>% filter(der_weapon_yes_cat == 4), var=der_weapon_yes_cat, section=35, mergeby=c( "incident_id", "victim_id"), denom=POP_TOTAL) #Weapon involved :           Blunt instruments
    s36 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_weapon_yes_cat_victim %>% filter(der_weapon_yes_cat == 5), var=der_weapon_yes_cat, section=36, mergeby=c( "incident_id", "victim_id"), denom=POP_TOTAL) #Weapon involved :           Other non-personal weapons
    s37 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_weapon_yes_cat_victim %>% filter(der_weapon_yes_cat == 6), var=der_weapon_yes_cat, section=37, mergeby=c( "incident_id", "victim_id"), denom=POP_TOTAL) #Weapon involved :           Unknown
    s38 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_relationship_cat_victim %>% filter(der_relationship == 1), var=der_relationship, section=38, mergeby=c( "incident_id", "victim_id"), denom=POP_TOTAL) #Victim-offender relationship :   Intimate partner
    s39 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_relationship_cat_victim %>% filter(der_relationship == 2), var=der_relationship, section=39, mergeby=c( "incident_id", "victim_id"), denom=POP_TOTAL) #Victim-offender relationship :   Other family
    s40 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_relationship_cat_victim %>% filter(der_relationship == 3), var=der_relationship, section=40, mergeby=c( "incident_id", "victim_id"), denom=POP_TOTAL) #Victim-offender relationship :   Outside family but known to victim
    s41 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_relationship_cat_victim %>% filter(der_relationship == 4), var=der_relationship, section=41, mergeby=c( "incident_id", "victim_id"), denom=POP_TOTAL) #Victim-offender relationship :   Stranger
    s42 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_relationship_cat_victim %>% filter(der_relationship == 5), var=der_relationship, section=42, mergeby=c( "incident_id", "victim_id"), denom=POP_TOTAL) #Victim-offender relationship :   Victim was Offender
    s43 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_relationship_cat_victim %>% filter(der_relationship == 6), var=der_relationship, section=43, mergeby=c( "incident_id", "victim_id"), denom=POP_TOTAL) #Victim-offender relationship :   Unknown relationship

	#Weapon involved hierarchy
	  s44 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_raw_weapon_hierarchy_recode_victim, var=der_raw_weapon_hierarchy_recode, section=44, 
						 mergeby=c( "incident_id", "victim_id"), denom=POP_TOTAL)
  
	#Victim-offender relationship hierarchy
	  s45 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_relationship_hierarchy_victim, var=der_relationship_hierarchy, section=45, 
						 mergeby=c( "incident_id", "victim_id"), denom=POP_TOTAL) 
			
	#Hispanic Origin-specific victimization rate
	  s46 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_ethnicity_victim %>% filter(der_victim_ethnicity == 1), var=der_victim_ethnicity, section= 46, mergeby=c( "incident_id", "victim_id"), denom=DER_POP_PCT_HISP_NUM) #Hispanic Origin-specific victimization rate:   Hispanic or Latino
	  s47 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_ethnicity_victim %>% filter(der_victim_ethnicity == 2), var=der_victim_ethnicity, section= 47, mergeby=c( "incident_id", "victim_id"), denom=DER_POP_PCT_NONHISP_NUM) #Hispanic Origin-specific victimization rate:   Not Hispanic or Latino
	  s48 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_ethnicity_victim %>% filter(der_victim_ethnicity == 3), var=der_victim_ethnicity, section= 48, mergeby=c( "incident_id", "victim_id"), denom=POP_TOTAL) #Hispanic Origin-specific victimization rate:   Unknown
	  
  
	
	#Race and Hispanic Origin-specific victimization rate
	  s49 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_ethnicity_race_victim %>% filter(der_victim_ethnicity_race == 1), var=der_victim_ethnicity_race, section= 49, mergeby=c( "incident_id", "victim_id"), denom=DER_POP_PCT_HISP_NUM) #Race and Hispanic Origin-specific victimization rate:   Hispanic or Latino
	  s50 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_ethnicity_race_victim %>% filter(der_victim_ethnicity_race == 2), var=der_victim_ethnicity_race, section= 50, mergeby=c( "incident_id", "victim_id"), denom=DER_POP_PCT_NONHISP_WHITE_NUM) #Race and Hispanic Origin-specific victimization rate:   Non-Hispanic, White
	  s51 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_ethnicity_race_victim %>% filter(der_victim_ethnicity_race == 3), var=der_victim_ethnicity_race, section= 51, mergeby=c( "incident_id", "victim_id"), denom=DER_POP_PCT_NONHISP_BLACK_NUM) #Race and Hispanic Origin-specific victimization rate:   Non-Hispanic, Black
	  s52 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_ethnicity_race_victim %>% filter(der_victim_ethnicity_race == 4), var=der_victim_ethnicity_race, section= 52, mergeby=c( "incident_id", "victim_id"), denom=DER_POP_PCT_NONHISP_AIAN_NUM) #Race and Hispanic Origin-specific victimization rate:   Non-Hispanic, American Indian or Alaska Native
	  s53 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_ethnicity_race_victim %>% filter(der_victim_ethnicity_race == 5), var=der_victim_ethnicity_race, section= 53, mergeby=c( "incident_id", "victim_id"), denom=DER_POP_PCT_NONHISP_ASIAN_NUM) #Race and Hispanic Origin-specific victimization rate:   Non-Hispanic, Asian
	  s54 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_ethnicity_race_victim %>% filter(der_victim_ethnicity_race == 6), var=der_victim_ethnicity_race, section= 54, mergeby=c( "incident_id", "victim_id"), denom=DER_POP_PCT_NONHISP_NHOPI_NUM) #Race and Hispanic Origin-specific victimization rate:   Non-Hispanic, Native Hawaiian or Other Pacific Islander
	  s55 <- agg_percent_CAA_victim_rate(leftdata = main_filter, rightdata = agg_victim_ethnicity_race_victim %>% filter(der_victim_ethnicity_race == 7), var=der_victim_ethnicity_race, section= 55, mergeby=c( "incident_id", "victim_id"), denom=POP_TOTAL) #Race and Hispanic Origin-specific victimization rate:   Unknown race or Hispanic origin
	  
  

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
    mutate(!!incolumn_count := final_count)


  #Create the row and reassign the section variable
  final_data3 <- assign_row(final_data2)
  final_data4 <- assign_section(final_data3)

  #Keep variables and sort the dataset
  final_data5 <- final_data4 %>%
    select(section, row, !!incolumn_count) %>%
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
    mutate(count = fcase(row %in% c(1:2), final_count, default = DER_NA_CODE)) %>%
    #mutate(percentage = fcase(!row %in% c(1:43), percent, default = DER_NA_CODE)) %>%
    mutate(percentage =  DER_NA_CODE) %>%
    mutate(rate = fcase(!row %in% c(1:2), final_count,default = DER_NA_CODE)) %>%
    mutate(population_estimate = fcase(!row %in% c(1:2), population_estimate,default = DER_NA_CODE)) %>%
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
	#Create new symbol to subset data
	insymbol <- insubset %>% rlang:::parse_expr()
  subsetvareq <- collist
  log_debug(paste0("About to generate_est for col",colindex))
  log_debug(system("free -mh", intern = FALSE))
  temp <- generate_est(
    maindata=main %>% filter(!!insymbol),
    subsetvareq1 = subsetvareq[colindex],
    column_number=colindex+inperm_num_series
  )
  return(temp)
}