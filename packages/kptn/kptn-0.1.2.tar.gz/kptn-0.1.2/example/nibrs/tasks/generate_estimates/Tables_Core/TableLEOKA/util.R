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

    der_activity %in% c(1:11),  der_activity + 2,

    der_assignment %in% c(1:6) ,  der_assignment + 13,

    der_weapon_no_yes %in% c(1:2),  der_weapon_no_yes + 19,
    der_weapon_yes_cat %in% c(1:6),  der_weapon_yes_cat + 21,

    der_injury_no_yes %in% c(1:2),  der_injury_no_yes + 27,

    der_victim_count %in% c(1:2),  der_victim_count + 29,

    der_offender_count %in% c(1:3),  der_offender_count + 31,

    der_offense_count %in% c(1:3),  der_offense_count + 34,

    der_relationship %in% c(1:6),  der_relationship + 37,

    der_location_1_10 %in% c(1:10),  der_location_1_10 + 43,

    der_time_of_day_incident %in% c(1:7),  der_time_of_day_incident + 53,
    der_time_of_day_report %in% c(1:7),  der_time_of_day_report + 60,

    der_clearance_cat %in% c(1:3),  der_clearance_cat + 67,
    der_exceptional_clearance %in% c(1:5),  der_exceptional_clearance + 70,

    der_location_1_11 %in% c(1:11), der_location_1_11 + 75,
    der_relationship2 %in% c(1:5), der_relationship2 + 86
    )

  )

  return(returndata)
}

assign_section <- function(data){
  log_debug("Running assign_section function")

  returndata <- data %>% mutate(

  section = fcase(
    row %in% c(1:2),  1,
    row %in% c(3:13),  2,
    row %in% c(14:19),  3,
    row %in% c(20:27),  4,
    row %in% c(28:29),  5,
    row %in% c(30:31),  6,
    row %in% c(32:34),  7,
    row %in% c(35:37),  8,
    row %in% c(38:43),  9,
    row %in% c(44:53),  10,
    row %in% c(54:60),  11,
    row %in% c(61:67),  12,
    row %in% c(68:75),  13,
    row %in% c(76:86),  14,
    row %in% c(87:91),  15
    )
  )

  return(returndata)

}




#New add on code for labels
assign_labels <- function(data){
  log_debug("Running assign_labels function")

  returndata <- data %>% mutate(

  estimate_domain = fcase(

row == 1,  'Victimization count: Law enforcement officers',
row == 2,  'Victimization rate (per 100k LE staff): Law enforcement officers',
row == 3,  'LEOKA Types of Activity: Responding to disturbance call',
row == 4,  'LEOKA Types of Activity: Burglary',
row == 5,  'LEOKA Types of Activity: Robbery in process',
row == 6,  'LEOKA Types of Activity: Attempting other arrest',
row == 7,  'LEOKA Types of Activity: Civil disorder',
row == 8,  'LEOKA Types of Activity: Handling, transporting, custody of prisoners',
row == 9,  'LEOKA Types of Activity: Investigating suspicious persons',
row == 10,  'LEOKA Types of Activity: Ambush',
row == 11,  'LEOKA Types of Activity: Mentally challenged',
row == 12,  'LEOKA Types of Activity: Traffic pursuits',
row == 13,  'LEOKA Types of Activity: All other',
row == 14,  'Type of Assignment: Two-officer vehicle',
row == 15,  'Type of Assignment: One-officer vehicle alone',
row == 16,  'Type of Assignment: One-officer vehicle assisted',
row == 17,  'Type of Assignment: Detective or Special Assignment alone',
row == 18,  'Type of Assignment: Detective or Special Assignment assisted',
row == 19,  'Type of Assignment: Other',
row == 20,  'Weapon involved: No',
row == 21,  'Weapon involved: Yes',
row == 22,  'Weapon involved: Personal weapons',
row == 23,  'Weapon involved: Firearms',
row == 24,  'Weapon involved: Knives and other cutting instruments',
row == 25,  'Weapon involved: Blunt instruments',
row == 26,  'Weapon involved: Other non-personal weapons',
row == 27,  'Weapon involved: Unknown',
row == 28,  'Injury: No',
row == 29,  'Injury: Yes',
row == 30,  'Multiple victims: 1 victim',
row == 31,  'Multiple victims: 2+ victims',
row == 32,  'Multiple offenders: 1 offender',
row == 33,  'Multiple offenders: 2+ offenders',
row == 34,  'Multiple offenders: Unknown offenders',
row == 35,  'Multiple offense incident: 1 offense',
row == 36,  'Multiple offense incident: 2 offenses',
row == 37,  'Multiple offense incident: 3+ offenses',
row == 38,  'Victim-offender relationship: Intimate partner',
row == 39,  'Victim-offender relationship: Other family',
row == 40,  'Victim-offender relationship: Outside family but known to victim',
row == 41,  'Victim-offender relationship: Stranger',
row == 42,  'Victim-offender relationship: Victim was Offender',
row == 43,  'Victim-offender relationship: Unknown relationship',
row == 44,  'Location type: Residence/hotel',
row == 45,  'Location type: Transportation hub/outdoor public locations',
row == 46,  'Location type: Schools, daycares, and universities',
row == 47,  'Location type: Retail/financial/other commercial establishment',
row == 48,  'Location type: Restaurant/bar/sports or entertainment venue',
row == 49,  'Location type: Religious buildings',
row == 50,  'Location type: Government/public buildings',
row == 51,  'Location type: Jail/prison',
row == 52,  'Location type: Shelter-mission/homeless',
row == 53,  'Location type: Other/unknown location',
row == 54,  'Time of day- Incident time: Midnight-4am',
row == 55,  'Time of day- Incident time: 4-8am',
row == 56,  'Time of day- Incident time: 8am-noon',
row == 57,  'Time of day- Incident time: Noon-4pm',
row == 58,  'Time of day- Incident time: 4-8pm',
row == 59,  'Time of day- Incident time: 8pm-midnight',
row == 60,  'Time of day- Incident time: Unknown',
row == 61,  'Time of day- Report time: Midnight-4am',
row == 62,  'Time of day- Report time: 4-8am',
row == 63,  'Time of day- Report time: 8am-noon',
row == 64,  'Time of day- Report time: Noon-4pm',
row == 65,  'Time of day- Report time: 4-8pm',
row == 66,  'Time of day- Report time: 8pm-midnight',
row == 67,  'Time of day- Report time: Unknown',
row == 68,  'Clearance: Not cleared',
row == 69,  'Clearance: Cleared through arrest',
row == 70,  'Clearance: Exceptional clearance',
row == 71,  'Clearance: Death of offender',
row == 72,  'Clearance: Prosecution declined',
row == 73,  'Clearance: In custody of other jurisdiction',
row == 74,  'Clearance: Victim refused to cooperate',
row == 75,  'Clearance: Juvenile/no custody',

row == 76, 'Location type 2: Residence/hotel',
row == 77, 'Location type 2: Transportation hub/outdoor public locations',
row == 78, 'Location type 2: Schools, daycares, and universities',
row == 79, 'Location type 2: Retail/financial/other commercial establishment',
row == 80, 'Location type 2: Restaurant/bar/sports or entertainment venue',
row == 81, 'Location type 2: Religious buildings',
row == 82, 'Location type 2: Government/public buildings',
row == 83, 'Location type 2: Jail/prison',
row == 84, 'Location type 2: Shelter-mission/homeless',
row == 85, 'Location type 2: Drug Store/Doctor Office/Hospital',
row == 86, 'Location type 2: Other/unknown location',
row == 87, 'Victim-offender relationship 2: Intimate partner plus Family',
row == 88, 'Victim-offender relationship 2: Outside family but known to victim',
row == 89, 'Victim-offender relationship 2: Stranger',
row == 90, 'Victim-offender relationship 2: Victim was Offender',
row == 91, 'Victim-offender relationship 2: Unknown relationship'




  ),

  indicator_name = fcase(

column == 1,  'ASSAULT OFFENSES'

  ),

  full_table = "LEOKA",
  table = DER_TABLE_NAME
  )

  return(returndata)

}

estimate_type_detail_percentage_label <- function(indata){
  log_debug("Running estimate_type_detail_percentage_label function")

  returndata <- indata %>%
    mutate(
      estimate_type_detail_percentage = fcase(

trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 1,  'Victim Level', #Victimization count: Law enforcement officers
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 2,  'Victim Level', #Victimization rate (per 100k LE staff): Law enforcement officers
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 3,  'Victim Level', #LEOKA Types of Activity: Responding to disturbance call
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 4,  'Victim Level', #LEOKA Types of Activity: Burglary
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 5,  'Victim Level', #LEOKA Types of Activity: Robbery in process
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 6,  'Victim Level', #LEOKA Types of Activity: Attempting other arrest
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 7,  'Victim Level', #LEOKA Types of Activity: Civil disorder
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 8,  'Victim Level', #LEOKA Types of Activity: Handling, transporting, custody of prisoners
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 9,  'Victim Level', #LEOKA Types of Activity: Investigating suspicious persons
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 10,  'Victim Level', #LEOKA Types of Activity: Ambush
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 11,  'Victim Level', #LEOKA Types of Activity: Mentally challenged
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 12,  'Victim Level', #LEOKA Types of Activity: Traffic pursuits
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 13,  'Victim Level', #LEOKA Types of Activity: All other
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 14,  'Victim Level', #Type of Assignment: Two-officer vehicle
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 15,  'Victim Level', #Type of Assignment: One-officer vehicle alone
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 16,  'Victim Level', #Type of Assignment: One-officer vehicle assisted
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 17,  'Victim Level', #Type of Assignment: Detective or Special Assignment alone
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 18,  'Victim Level', #Type of Assignment: Detective or Special Assignment assisted
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 19,  'Victim Level', #Type of Assignment: Other
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 20,  'Victim Level', #Weapon involved: No
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 21,  'Victim Level', #Weapon involved: Yes
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 22,  'Victim Level subset to weapon involved yes', #Weapon involved: Personal weapons
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 23,  'Victim Level subset to weapon involved yes', #Weapon involved: Firearms
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 24,  'Victim Level subset to weapon involved yes', #Weapon involved: Knives and other cutting instruments
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 25,  'Victim Level subset to weapon involved yes', #Weapon involved: Blunt instruments
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 26,  'Victim Level subset to weapon involved yes', #Weapon involved: Other non-personal weapons
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 27,  'Victim Level subset to weapon involved yes', #Weapon involved: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 28,  'Victim Level', #Injury: No
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 29,  'Victim Level', #Injury: Yes
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 30,  'Victim Level', #Multiple victims: 1 victim
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 31,  'Victim Level', #Multiple victims: 2+ victims
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 32,  'Victim Level', #Multiple offenders: 1 offender
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 33,  'Victim Level', #Multiple offenders: 2+ offenders
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 34,  'Victim Level', #Multiple offenders: Unknown offenders
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 35,  'Victim Level', #Multiple offense incident: 1 offense
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 36,  'Victim Level', #Multiple offense incident: 2 offenses
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 37,  'Victim Level', #Multiple offense incident: 3+ offenses
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 38,  'Victim Level', #Victim-offender relationship: Intimate partner
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 39,  'Victim Level', #Victim-offender relationship: Other family
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 40,  'Victim Level', #Victim-offender relationship: Outside family but known to victim
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 41,  'Victim Level', #Victim-offender relationship: Stranger
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 42,  'Victim Level', #Victim-offender relationship: Victim was Offender
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 43,  'Victim Level', #Victim-offender relationship: Unknown relationship
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 44,  'Victim Level', #Location type: Residence/hotel
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 45,  'Victim Level', #Location type: Transportation hub/outdoor public locations
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 46,  'Victim Level', #Location type: Schools, daycares, and universities
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 47,  'Victim Level', #Location type: Retail/financial/other commercial establishment
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 48,  'Victim Level', #Location type: Restaurant/bar/sports or entertainment venue
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 49,  'Victim Level', #Location type: Religious buildings
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 50,  'Victim Level', #Location type: Government/public buildings
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 51,  'Victim Level', #Location type: Jail/prison
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 52,  'Victim Level', #Location type: Shelter-mission/homeless
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 53,  'Victim Level', #Location type: Other/unknown location
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 54,  'Victim Level', #Time of day- Incident time: Midnight-4am
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 55,  'Victim Level', #Time of day- Incident time: 4-8am
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 56,  'Victim Level', #Time of day- Incident time: 8am-noon
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 57,  'Victim Level', #Time of day- Incident time: Noon-4pm
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 58,  'Victim Level', #Time of day- Incident time: 4-8pm
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 59,  'Victim Level', #Time of day- Incident time: 8pm-midnight
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 60,  'Victim Level', #Time of day- Incident time: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 61,  'Victim Level', #Time of day- Report time: Midnight-4am
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 62,  'Victim Level', #Time of day- Report time: 4-8am
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 63,  'Victim Level', #Time of day- Report time: 8am-noon
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 64,  'Victim Level', #Time of day- Report time: Noon-4pm
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 65,  'Victim Level', #Time of day- Report time: 4-8pm
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 66,  'Victim Level', #Time of day- Report time: 8pm-midnight
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 67,  'Victim Level', #Time of day- Report time: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 68,  'Victim Level', #Clearance: Not cleared
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 69,  'Victim Level', #Clearance: Cleared through arrest
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 70,  'Victim Level', #Clearance: Exceptional clearance
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 71,  'Victim Level subset to exceptional clearance', #Clearance: Death of offender
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 72,  'Victim Level subset to exceptional clearance', #Clearance: Prosecution declined
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 73,  'Victim Level subset to exceptional clearance', #Clearance: In custody of other jurisdiction
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 74,  'Victim Level subset to exceptional clearance', #Clearance: Victim refused to cooperate
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 75,  'Victim Level subset to exceptional clearance', #Clearance: Juvenile/no custody

trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 76, 'Victim Level', #Location type 2: Residence/hotel
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 77, 'Victim Level', #Location type 2: Transportation hub/outdoor public locations
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 78, 'Victim Level', #Location type 2: Schools, daycares, and universities
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 79, 'Victim Level', #Location type 2: Retail/financial/other commercial establishment
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 80, 'Victim Level', #Location type 2: Restaurant/bar/sports or entertainment venue
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 81, 'Victim Level', #Location type 2: Religious buildings
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 82, 'Victim Level', #Location type 2: Government/public buildings
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 83, 'Victim Level', #Location type 2: Jail/prison
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 84, 'Victim Level', #Location type 2: Shelter-mission/homeless
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 85, 'Victim Level', #Location type 2: Drug Store/Doctor Office/Hospital
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 86, 'Victim Level', #Location type 2: Other/unknown location
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 87, 'Victim Level', #Victim-offender relationship 2: Intimate partner plus Family
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 88, 'Victim Level', #Victim-offender relationship 2: Outside family but known to victim
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 89, 'Victim Level', #Victim-offender relationship 2: Stranger
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 90, 'Victim Level', #Victim-offender relationship 2: Victim was Offender
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 91, 'Victim Level' #Victim-offender relationship 2: Unknown relationship


))

  return(returndata)
}

estimate_type_detail_rate_label <- function(indata){
  log_debug("Running estimate_type_detail_rate_label function")

  returndata <- indata %>%
    mutate(
      estimate_type_detail_rate = fcase(

trim_upcase(estimate_type) %in% c('RATE') & row == 1,  DER_NA_CODE_STRING, #Victimization count: Law enforcement officers
trim_upcase(estimate_type) %in% c('RATE') & row == 2,  'Victim rate per 100,000 LE staff', #Victimization rate (per 100k LE staff): Law enforcement officers
trim_upcase(estimate_type) %in% c('RATE') & row == 3,  DER_NA_CODE_STRING, #LEOKA Types of Activity: Responding to disturbance call
trim_upcase(estimate_type) %in% c('RATE') & row == 4,  DER_NA_CODE_STRING, #LEOKA Types of Activity: Burglary
trim_upcase(estimate_type) %in% c('RATE') & row == 5,  DER_NA_CODE_STRING, #LEOKA Types of Activity: Robbery in process
trim_upcase(estimate_type) %in% c('RATE') & row == 6,  DER_NA_CODE_STRING, #LEOKA Types of Activity: Attempting other arrest
trim_upcase(estimate_type) %in% c('RATE') & row == 7,  DER_NA_CODE_STRING, #LEOKA Types of Activity: Civil disorder
trim_upcase(estimate_type) %in% c('RATE') & row == 8,  DER_NA_CODE_STRING, #LEOKA Types of Activity: Handling, transporting, custody of prisoners
trim_upcase(estimate_type) %in% c('RATE') & row == 9,  DER_NA_CODE_STRING, #LEOKA Types of Activity: Investigating suspicious persons
trim_upcase(estimate_type) %in% c('RATE') & row == 10,  DER_NA_CODE_STRING, #LEOKA Types of Activity: Ambush
trim_upcase(estimate_type) %in% c('RATE') & row == 11,  DER_NA_CODE_STRING, #LEOKA Types of Activity: Mentally challenged
trim_upcase(estimate_type) %in% c('RATE') & row == 12,  DER_NA_CODE_STRING, #LEOKA Types of Activity: Traffic pursuits
trim_upcase(estimate_type) %in% c('RATE') & row == 13,  DER_NA_CODE_STRING, #LEOKA Types of Activity: All other
trim_upcase(estimate_type) %in% c('RATE') & row == 14,  DER_NA_CODE_STRING, #Type of Assignment: Two-officer vehicle
trim_upcase(estimate_type) %in% c('RATE') & row == 15,  DER_NA_CODE_STRING, #Type of Assignment: One-officer vehicle alone
trim_upcase(estimate_type) %in% c('RATE') & row == 16,  DER_NA_CODE_STRING, #Type of Assignment: One-officer vehicle assisted
trim_upcase(estimate_type) %in% c('RATE') & row == 17,  DER_NA_CODE_STRING, #Type of Assignment: Detective or Special Assignment alone
trim_upcase(estimate_type) %in% c('RATE') & row == 18,  DER_NA_CODE_STRING, #Type of Assignment: Detective or Special Assignment assisted
trim_upcase(estimate_type) %in% c('RATE') & row == 19,  DER_NA_CODE_STRING, #Type of Assignment: Other
trim_upcase(estimate_type) %in% c('RATE') & row == 20,  DER_NA_CODE_STRING, #Weapon involved: No
trim_upcase(estimate_type) %in% c('RATE') & row == 21,  DER_NA_CODE_STRING, #Weapon involved: Yes
trim_upcase(estimate_type) %in% c('RATE') & row == 22,  DER_NA_CODE_STRING, #Weapon involved: Personal weapons
trim_upcase(estimate_type) %in% c('RATE') & row == 23,  DER_NA_CODE_STRING, #Weapon involved: Firearms
trim_upcase(estimate_type) %in% c('RATE') & row == 24,  DER_NA_CODE_STRING, #Weapon involved: Knives and other cutting instruments
trim_upcase(estimate_type) %in% c('RATE') & row == 25,  DER_NA_CODE_STRING, #Weapon involved: Blunt instruments
trim_upcase(estimate_type) %in% c('RATE') & row == 26,  DER_NA_CODE_STRING, #Weapon involved: Other non-personal weapons
trim_upcase(estimate_type) %in% c('RATE') & row == 27,  DER_NA_CODE_STRING, #Weapon involved: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 28,  DER_NA_CODE_STRING, #Injury: No
trim_upcase(estimate_type) %in% c('RATE') & row == 29,  DER_NA_CODE_STRING, #Injury: Yes
trim_upcase(estimate_type) %in% c('RATE') & row == 30,  DER_NA_CODE_STRING, #Multiple victims: 1 victim
trim_upcase(estimate_type) %in% c('RATE') & row == 31,  DER_NA_CODE_STRING, #Multiple victims: 2+ victims
trim_upcase(estimate_type) %in% c('RATE') & row == 32,  DER_NA_CODE_STRING, #Multiple offenders: 1 offender
trim_upcase(estimate_type) %in% c('RATE') & row == 33,  DER_NA_CODE_STRING, #Multiple offenders: 2+ offenders
trim_upcase(estimate_type) %in% c('RATE') & row == 34,  DER_NA_CODE_STRING, #Multiple offenders: Unknown offenders
trim_upcase(estimate_type) %in% c('RATE') & row == 35,  DER_NA_CODE_STRING, #Multiple offense incident: 1 offense
trim_upcase(estimate_type) %in% c('RATE') & row == 36,  DER_NA_CODE_STRING, #Multiple offense incident: 2 offenses
trim_upcase(estimate_type) %in% c('RATE') & row == 37,  DER_NA_CODE_STRING, #Multiple offense incident: 3+ offenses
trim_upcase(estimate_type) %in% c('RATE') & row == 38,  DER_NA_CODE_STRING, #Victim-offender relationship: Intimate partner
trim_upcase(estimate_type) %in% c('RATE') & row == 39,  DER_NA_CODE_STRING, #Victim-offender relationship: Other family
trim_upcase(estimate_type) %in% c('RATE') & row == 40,  DER_NA_CODE_STRING, #Victim-offender relationship: Outside family but known to victim
trim_upcase(estimate_type) %in% c('RATE') & row == 41,  DER_NA_CODE_STRING, #Victim-offender relationship: Stranger
trim_upcase(estimate_type) %in% c('RATE') & row == 42,  DER_NA_CODE_STRING, #Victim-offender relationship: Victim was Offender
trim_upcase(estimate_type) %in% c('RATE') & row == 43,  DER_NA_CODE_STRING, #Victim-offender relationship: Unknown relationship
trim_upcase(estimate_type) %in% c('RATE') & row == 44,  DER_NA_CODE_STRING, #Location type: Residence/hotel
trim_upcase(estimate_type) %in% c('RATE') & row == 45,  DER_NA_CODE_STRING, #Location type: Transportation hub/outdoor public locations
trim_upcase(estimate_type) %in% c('RATE') & row == 46,  DER_NA_CODE_STRING, #Location type: Schools, daycares, and universities
trim_upcase(estimate_type) %in% c('RATE') & row == 47,  DER_NA_CODE_STRING, #Location type: Retail/financial/other commercial establishment
trim_upcase(estimate_type) %in% c('RATE') & row == 48,  DER_NA_CODE_STRING, #Location type: Restaurant/bar/sports or entertainment venue
trim_upcase(estimate_type) %in% c('RATE') & row == 49,  DER_NA_CODE_STRING, #Location type: Religious buildings
trim_upcase(estimate_type) %in% c('RATE') & row == 50,  DER_NA_CODE_STRING, #Location type: Government/public buildings
trim_upcase(estimate_type) %in% c('RATE') & row == 51,  DER_NA_CODE_STRING, #Location type: Jail/prison
trim_upcase(estimate_type) %in% c('RATE') & row == 52,  DER_NA_CODE_STRING, #Location type: Shelter-mission/homeless
trim_upcase(estimate_type) %in% c('RATE') & row == 53,  DER_NA_CODE_STRING, #Location type: Other/unknown location
trim_upcase(estimate_type) %in% c('RATE') & row == 54,  DER_NA_CODE_STRING, #Time of day- Incident time: Midnight-4am
trim_upcase(estimate_type) %in% c('RATE') & row == 55,  DER_NA_CODE_STRING, #Time of day- Incident time: 4-8am
trim_upcase(estimate_type) %in% c('RATE') & row == 56,  DER_NA_CODE_STRING, #Time of day- Incident time: 8am-noon
trim_upcase(estimate_type) %in% c('RATE') & row == 57,  DER_NA_CODE_STRING, #Time of day- Incident time: Noon-4pm
trim_upcase(estimate_type) %in% c('RATE') & row == 58,  DER_NA_CODE_STRING, #Time of day- Incident time: 4-8pm
trim_upcase(estimate_type) %in% c('RATE') & row == 59,  DER_NA_CODE_STRING, #Time of day- Incident time: 8pm-midnight
trim_upcase(estimate_type) %in% c('RATE') & row == 60,  DER_NA_CODE_STRING, #Time of day- Incident time: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 61,  DER_NA_CODE_STRING, #Time of day- Report time: Midnight-4am
trim_upcase(estimate_type) %in% c('RATE') & row == 62,  DER_NA_CODE_STRING, #Time of day- Report time: 4-8am
trim_upcase(estimate_type) %in% c('RATE') & row == 63,  DER_NA_CODE_STRING, #Time of day- Report time: 8am-noon
trim_upcase(estimate_type) %in% c('RATE') & row == 64,  DER_NA_CODE_STRING, #Time of day- Report time: Noon-4pm
trim_upcase(estimate_type) %in% c('RATE') & row == 65,  DER_NA_CODE_STRING, #Time of day- Report time: 4-8pm
trim_upcase(estimate_type) %in% c('RATE') & row == 66,  DER_NA_CODE_STRING, #Time of day- Report time: 8pm-midnight
trim_upcase(estimate_type) %in% c('RATE') & row == 67,  DER_NA_CODE_STRING, #Time of day- Report time: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 68,  DER_NA_CODE_STRING, #Clearance: Not cleared
trim_upcase(estimate_type) %in% c('RATE') & row == 69,  DER_NA_CODE_STRING, #Clearance: Cleared through arrest
trim_upcase(estimate_type) %in% c('RATE') & row == 70,  DER_NA_CODE_STRING, #Clearance: Exceptional clearance
trim_upcase(estimate_type) %in% c('RATE') & row == 71,  DER_NA_CODE_STRING, #Clearance: Death of offender
trim_upcase(estimate_type) %in% c('RATE') & row == 72,  DER_NA_CODE_STRING, #Clearance: Prosecution declined
trim_upcase(estimate_type) %in% c('RATE') & row == 73,  DER_NA_CODE_STRING, #Clearance: In custody of other jurisdiction
trim_upcase(estimate_type) %in% c('RATE') & row == 74,  DER_NA_CODE_STRING, #Clearance: Victim refused to cooperate
trim_upcase(estimate_type) %in% c('RATE') & row == 75,  DER_NA_CODE_STRING, #Clearance: Juvenile/no custody

trim_upcase(estimate_type) %in% c('RATE') & row == 76,  DER_NA_CODE_STRING, #Location type 2: Residence/hotel
trim_upcase(estimate_type) %in% c('RATE') & row == 77,  DER_NA_CODE_STRING, #Location type 2: Transportation hub/outdoor public locations
trim_upcase(estimate_type) %in% c('RATE') & row == 78,  DER_NA_CODE_STRING, #Location type 2: Schools, daycares, and universities
trim_upcase(estimate_type) %in% c('RATE') & row == 79,  DER_NA_CODE_STRING, #Location type 2: Retail/financial/other commercial establishment
trim_upcase(estimate_type) %in% c('RATE') & row == 80,  DER_NA_CODE_STRING, #Location type 2: Restaurant/bar/sports or entertainment venue
trim_upcase(estimate_type) %in% c('RATE') & row == 81,  DER_NA_CODE_STRING, #Location type 2: Religious buildings
trim_upcase(estimate_type) %in% c('RATE') & row == 82,  DER_NA_CODE_STRING, #Location type 2: Government/public buildings
trim_upcase(estimate_type) %in% c('RATE') & row == 83,  DER_NA_CODE_STRING, #Location type 2: Jail/prison
trim_upcase(estimate_type) %in% c('RATE') & row == 84,  DER_NA_CODE_STRING, #Location type 2: Shelter-mission/homeless
trim_upcase(estimate_type) %in% c('RATE') & row == 85,  DER_NA_CODE_STRING, #Location type 2: Drug Store/Doctor Office/Hospital
trim_upcase(estimate_type) %in% c('RATE') & row == 86,  DER_NA_CODE_STRING, #Location type 2: Other/unknown location
trim_upcase(estimate_type) %in% c('RATE') & row == 87,  DER_NA_CODE_STRING, #Victim-offender relationship 2: Intimate partner plus Family
trim_upcase(estimate_type) %in% c('RATE') & row == 88,  DER_NA_CODE_STRING, #Victim-offender relationship 2: Outside family but known to victim
trim_upcase(estimate_type) %in% c('RATE') & row == 89,  DER_NA_CODE_STRING, #Victim-offender relationship 2: Stranger
trim_upcase(estimate_type) %in% c('RATE') & row == 90,  DER_NA_CODE_STRING, #Victim-offender relationship 2: Victim was Offender
trim_upcase(estimate_type) %in% c('RATE') & row == 91,  DER_NA_CODE_STRING #Victim-offender relationship 2: Unknown relationship



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
  incolumn_percentage <- paste0("percent_", columnnum) %>% rlang:::parse_expr()

  #Filter the dataset
  main_filter <- maindata[eval(infilter), c("ori", "weight", "incident_id", "victim_id", filtervarsting), with = FALSE]
  #Deduplicate by Incident ID, victim ID, and one instance of crime type
  main_filter <- main_filter[, .SD[1], by = c("ori", "incident_id", "victim_id", filtervarsting)]

  log_debug("After filtering and deduping main")
  log_dim(main_filter)
  log_debug(system("free -mh", intern = FALSE))


  #Incident count for LEO - Hard code the variable
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

  #Incident rate for LEO
  s2 <- vector("list", 2)
  #For Table
  s2[[1]] <- s1[[1]] %>%
    mutate(final_count = (final_count / DER_POP_OFFICER_NUM) * 100000,
           population_estimate = DER_POP_OFFICER_NUM ) %>%
    mutate(section = 2)
  #For ORI level - Need unweighted counts
  s2[[2]] <- main_filter %>%
    group_by(ori) %>%
    summarise(final_count = sum(!!infiltervar)) %>%
    ungroup() %>%
    mutate(section = 2)

  #LEOKA Types of Activity
  s3 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_activity_cat_victim, var=der_activity, section=3, mergeby=c("incident_id", "victim_id"))

  #Type of Assignment
  s4 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_assignment_cat_victim, var=der_assignment, section=4, mergeby=c("incident_id", "victim_id"))

  #Weapon involved
  s5 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_weapon_no_yes_victim, var=der_weapon_no_yes, section=5, mergeby=c("incident_id", "victim_id"))

  der_weapon_yes_denom <- s5[[1]] %>%
    filter(der_weapon_no_yes == 2) %>% #Yes response
    select(final_count) %>%
    as.double()

  s6 <- agg_percent_CAA_victim(leftdata = main_filter, rightdata = agg_weapon_yes_cat_victim, var=der_weapon_yes_cat, section=6, mergeby=c("incident_id", "victim_id"), denom=der_weapon_yes_denom)

  #Injury
  s7 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_injury_no_yes_victim, var=der_injury_no_yes, section=7, mergeby=c("incident_id", "victim_id"))

  #Multiple victims
  s8 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_victim_count_1_2_plus, var=der_victim_count, section=8, mergeby=c("incident_id"))

  #Multiple offenders
  s9 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_offender_count_1_2_plus, var=der_offender_count, section=9, mergeby=c("incident_id"))

  #Multiple offense incident
  s10 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_offense_count_1_2_3_plus, var=der_offense_count, section=10, mergeby=c("incident_id"))

  #Victim-offender relationship
  s11 <- agg_percent_CAA_victim(leftdata = main_filter, rightdata = agg_relationship_cat_victim, var=der_relationship, section=11, mergeby=c("incident_id", "victim_id"), denom=der_total_denom)

  #Location type
  s12 <- agg_percent_CAA_victim(leftdata = main_filter, rightdata = agg_location_cat_1_10_victim, var=der_location_1_10, section=12, mergeby=c("incident_id", "victim_id"), denom=der_total_denom)

  ##Time of day - Incident
  s13 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_time_of_day_cat_incident, var=der_time_of_day_incident, section=13, mergeby=c("incident_id"))

  #Time of day - Report
  s14 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_time_of_day_cat_report, var=der_time_of_day_report, section=14, mergeby=c("incident_id"))

  #Clearance
  s15 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_clearance_cat, var=der_clearance_cat, section=15, mergeby=c("incident_id"))

  der_exceptional_clearance_denom <- s15[[1]] %>%
    filter(der_clearance_cat == 3) %>% #Yes response
    select(final_count) %>%
    as.double()

  s16 <- agg_percent_CAA_victim(leftdata = main_filter, rightdata = agg_exception_clearance_cat, var=der_exceptional_clearance, section=16, mergeby=c("incident_id"), denom=der_exceptional_clearance_denom)

  #Location type
  s17 <- agg_percent_CAA_victim(leftdata = main_filter, rightdata = agg_location_cat_1_11_victim, var=der_location_1_11, section=17, mergeby=c("incident_id", "victim_id"), denom=der_total_denom)

  #Victim-offender relationship
  s18 <- agg_percent_CAA_victim(leftdata = main_filter, rightdata = agg_relationship_cat2_victim, var=der_relationship2, section=18, mergeby=c("incident_id", "victim_id"), denom=der_total_denom)


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
    mutate(count = fcase(!row %in% c(2), final_count, default = DER_NA_CODE)) %>%
           #UPDATE this for each table:  Make the estimates of the database
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