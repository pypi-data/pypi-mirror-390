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
    der_weapon_no_yes %in% c(1:2),  der_weapon_no_yes + 2,
    der_weapon_yes_cat %in% c(1:6),  der_weapon_yes_cat + 4,
    der_victim_count %in% c(1:2),  der_victim_count + 10,
    der_offender_count %in% c(1:3),  der_offender_count + 12,
    der_location_1_10 %in% c(1:10),  der_location_1_10 + 15,
    der_time_of_day_incident %in% c(1:7),  der_time_of_day_incident + 25,
    der_time_of_day_report %in% c(1:7),  der_time_of_day_report + 32 ,
    der_population_group %in% c(1:6),  der_population_group + 39,
    der_agency_type_1_7 %in% c(1:7),  der_agency_type_1_7 + 45,
    der_clearance_cat_1_2 %in% c(1:2),  der_clearance_cat_1_2 + 52,
    der_gang_cat_no_yes %in% c(1:2),  der_gang_cat_no_yes + 54,
    der_msa %in% c(1:4), der_msa + 56,
    der_location_1_11 %in% c(1:11), der_location_1_11 + 60,
    der_location_residence %in% c(1:2), der_location_residence + 71, 
    der_cleared_cat_1_2 %in% c(1:2), der_cleared_cat_1_2 + 73    
    
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
    row %in% c(11:12),  3,
    row %in% c(13:15),  4,
    row %in% c(16:25),  5,
    row %in% c(26:32),  6,
    row %in% c(33:39),  7,
    row %in% c(40:45),  8,
    row %in% c(46:52),  9,
    row %in% c(53:54),  10,
    row %in% c(55:56),  11,
    row %in% c(57:60),  12,
    row %in% c(61:71),  13,
    row %in% c(72:73),  14,
    row %in% c(74:75),  15
    )
  )

  return(returndata)

}



#New add on code for labels
assign_labels <- function(data){
  log_debug("Running assign_labels function")

  returndata <- data %>% mutate(

  estimate_domain = fcase(

row == 1,  'Offense count',
row == 2,  'Offense rate (per 100k total pop)',
row == 3,  'Weapon involved: No',
row == 4,  'Weapon involved: Yes',
row == 5,  'Weapon involved: Personal weapons',
row == 6,  'Weapon involved: Firearms',
row == 7,  'Weapon involved: Knives and other cutting instruments',
row == 8,  'Weapon involved: Blunt instruments',
row == 9,  'Weapon involved: Other non-personal weapons',
row == 10,  'Weapon involved: Unknown',
row == 11,  'Multiple victims: 1 victim',
row == 12,  'Multiple victims: 2+ victims',
row == 13,  'Multiple offenders: 1 offender',
row == 14,  'Multiple offenders: 2+ offenders',
row == 15,  'Multiple offenders: Unknown offenders',
row == 16,  'Location type: Residence/hotel',
row == 17,  'Location type: Transportation hub/outdoor public locations',
row == 18,  'Location type: Schools, daycares, and universities',
row == 19,  'Location type: Retail/financial/other commercial establishment',
row == 20,  'Location type: Restaurant/bar/sports or entertainment venue',
row == 21,  'Location type: Religious buildings',
row == 22,  'Location type: Government/public buildings',
row == 23,  'Location type: Jail/prison',
row == 24,  'Location type: Shelter-mission/homeless',
row == 25,  'Location type: Other/unknown location',
row == 26,  'Time of day- Incident time: Midnight-4am',
row == 27,  'Time of day- Incident time: 4-8am',
row == 28,  'Time of day- Incident time: 8am-noon',
row == 29,  'Time of day- Incident time: Noon-4pm',
row == 30,  'Time of day- Incident time: 4-8pm',
row == 31,  'Time of day- Incident time: 8pm-midnight',
row == 32,  'Time of day- Incident time: Unknown',
row == 33,  'Time of day- Report time: Midnight-4am',
row == 34,  'Time of day- Report time: 4-8am',
row == 35,  'Time of day- Report time: 8am-noon',
row == 36,  'Time of day- Report time: Noon-4pm',
row == 37,  'Time of day- Report time: 4-8pm',
row == 38,  'Time of day- Report time: 8pm-midnight',
row == 39,  'Time of day- Report time: Unknown',
row == 40,  'Population group: Cities and counties 100,000 or over',
row == 41,  'Population group: Cities and counties 25,000-99,999',
row == 42,  'Population group: Cities and counties 10,000-24,999',
row == 43,  'Population group: Cities and counties under 10,000',
row == 44,  'Population group: State police',
row == 45,  'Population group: Possessions and Canal Zone',
row == 46,  'Agency indicator: City',
row == 47,  'Agency indicator: County',
row == 48,  'Agency indicator: University or college',
row == 49,  'Agency indicator: State police',
row == 50,  'Agency indicator: Other state agencies',
row == 51,  'Agency indicator: Tribal agencies',
row == 52,  'Agency indicator: Federal agencies',
row == 53,  'Clearance: Not cleared through arrest',
row == 54,  'Clearance: Cleared through arrest',
row == 55,  'Gang Involvement: None/Unknown gang involvement',
row == 56,  'Gang Involvement: Juvenile or other gang',
row == 57, 'MSA: MSA Counties',
row == 58, 'MSA: Outside MSA',
row == 59, 'MSA: Non-MSA Counties',
row == 60, 'MSA: Missing',

row == 61, 'Location type 2: Residence/hotel',
row == 62, 'Location type 2: Transportation hub/outdoor public locations',
row == 63, 'Location type 2: Schools, daycares, and universities',
row == 64, 'Location type 2: Retail/financial/other commercial establishment',
row == 65, 'Location type 2: Restaurant/bar/sports or entertainment venue',
row == 66, 'Location type 2: Religious buildings',
row == 67, 'Location type 2: Government/public buildings',
row == 68, 'Location type 2: Jail/prison',
row == 69, 'Location type 2: Shelter-mission/homeless',
row == 70, 'Location type 2: Drug Store/Doctor Office/Hospital',
row == 71, 'Location type 2: Other/unknown location',

row == 72, 'Location type 3: Residence',
row == 73, 'Location type 3: Not residence',
row == 74, 'Clearance 2: Cleared incident',
row == 75, 'Clearance 2: Not cleared incident'




  ),

  indicator_name = fcase(

column == 1,  'NIBRS crimes against property (Total)',
column == 2,  'Arson',
column == 3,  'Bribery',
column == 4,  'Burglary/B&E',
column == 5,  'Counterfeiting/Forgery',
column == 6,  'Destruction/Damage/Vandalism',
column == 7,  'Embezzlement',
column == 8,  'Extortion/Blackmail',
column == 9,  'Fraud Offenses',
column == 10,  'Larceny/Theft Offenses',
column == 11,  'Motor Vehicle Theft',
column == 12,  'Robbery',
column == 13,  'Stolen Property Offenses',
column == 14,  'Property Crime',
column == 15,  'Car Jacking',
column == 16, 'Corruption',
column == 17, 'Other Acts of Corruption',
column == 18, 'Hacking/Computer Invasion'


  ),

  full_table = "Table2b-Property Offenses",
  table = DER_TABLE_NAME
  )

  return(returndata)

}

estimate_type_detail_percentage_label <- function(indata){
  log_debug("Running estimate_type_detail_percentage_label function")

  returndata <- indata %>%
    mutate(
      estimate_type_detail_percentage = fcase(

trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 1,  'Offense Level', #Offense count
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 2,  'Offense Level', #Offense rate (per 100k total pop)
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 3,  'Offense Level', #Weapon involved: No
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 4,  'Offense Level', #Weapon involved: Yes
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 5,  'Offense Level subset to weapon involved yes', #Weapon involved: Personal weapons
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 6,  'Offense Level subset to weapon involved yes', #Weapon involved: Firearms
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 7,  'Offense Level subset to weapon involved yes', #Weapon involved: Knives and other cutting instruments
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 8,  'Offense Level subset to weapon involved yes', #Weapon involved: Blunt instruments
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 9,  'Offense Level subset to weapon involved yes', #Weapon involved: Other non-personal weapons
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 10,  'Offense Level subset to weapon involved yes', #Weapon involved: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 11,  'Offense Level', #Multiple victims: 1 victim
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 12,  'Offense Level', #Multiple victims: 2+ victims
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 13,  'Offense Level', #Multiple offenders: 1 offender
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 14,  'Offense Level', #Multiple offenders: 2+ offenders
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 15,  'Offense Level', #Multiple offenders: Unknown offenders
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 16,  'Offense Level', #Location type: Residence/hotel
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 17,  'Offense Level', #Location type: Transportation hub/outdoor public locations
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 18,  'Offense Level', #Location type: Schools, daycares, and universities
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 19,  'Offense Level', #Location type: Retail/financial/other commercial establishment
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 20,  'Offense Level', #Location type: Restaurant/bar/sports or entertainment venue
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 21,  'Offense Level', #Location type: Religious buildings
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 22,  'Offense Level', #Location type: Government/public buildings
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 23,  'Offense Level', #Location type: Jail/prison
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 24,  'Offense Level', #Location type: Shelter-mission/homeless
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 25,  'Offense Level', #Location type: Other/unknown location
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 26,  'Offense Level', #Time of day- Incident time: Midnight-4am
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 27,  'Offense Level', #Time of day- Incident time: 4-8am
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 28,  'Offense Level', #Time of day- Incident time: 8am-noon
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 29,  'Offense Level', #Time of day- Incident time: Noon-4pm
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 30,  'Offense Level', #Time of day- Incident time: 4-8pm
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 31,  'Offense Level', #Time of day- Incident time: 8pm-midnight
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 32,  'Offense Level', #Time of day- Incident time: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 33,  'Offense Level', #Time of day- Report time: Midnight-4am
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 34,  'Offense Level', #Time of day- Report time: 4-8am
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 35,  'Offense Level', #Time of day- Report time: 8am-noon
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 36,  'Offense Level', #Time of day- Report time: Noon-4pm
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 37,  'Offense Level', #Time of day- Report time: 4-8pm
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 38,  'Offense Level', #Time of day- Report time: 8pm-midnight
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 39,  'Offense Level', #Time of day- Report time: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 40,  'Offense Level', #Population group: Cities and counties 100,000 or over
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 41,  'Offense Level', #Population group: Cities and counties 25,000-99,999
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 42,  'Offense Level', #Population group: Cities and counties 10,000-24,999
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 43,  'Offense Level', #Population group: Cities and counties under 10,000
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 44,  'Offense Level', #Population group: State police
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 45,  'Offense Level', #Population group: Possessions and Canal Zone
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 46,  'Offense Level', #Agency indicator: City
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 47,  'Offense Level', #Agency indicator: County
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 48,  'Offense Level', #Agency indicator: University or college
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 49,  'Offense Level', #Agency indicator: State police
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 50,  'Offense Level', #Agency indicator: Other state agencies
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 51,  'Offense Level', #Agency indicator: Tribal agencies
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 52,  'Offense Level', #Agency indicator: Federal agencies
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 53,  'Offense Level', #Clearance: Not cleared through arrest
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 54,  'Offense Level', #Clearance: Cleared through arrest
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 55,  'Offense Level', #Gang Involvement: None/Unknown gang involvement
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 56,  'Offense Level', #Gang Involvement: Juvenile or other gang
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 57, 'Offense Level', #MSA: MSA Counties
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 58, 'Offense Level', #MSA: Outside MSA
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 59, 'Offense Level', #MSA: Non-MSA Counties
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 60, 'Offense Level', #MSA: Missing

trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 61, 'Offense Level', #Location type 2: Residence/hotel
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 62, 'Offense Level', #Location type 2: Transportation hub/outdoor public locations
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 63, 'Offense Level', #Location type 2: Schools, daycares, and universities
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 64, 'Offense Level', #Location type 2: Retail/financial/other commercial establishment
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 65, 'Offense Level', #Location type 2: Restaurant/bar/sports or entertainment venue
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 66, 'Offense Level', #Location type 2: Religious buildings
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 67, 'Offense Level', #Location type 2: Government/public buildings
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 68, 'Offense Level', #Location type 2: Jail/prison
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 69, 'Offense Level', #Location type 2: Shelter-mission/homeless
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 70, 'Offense Level', #Location type 2: Drug Store/Doctor Office/Hospital
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 71, 'Offense Level', #Location type 2: Other/unknown location

trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 72, 'Offense Level', #Location type 3: Residence
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 73, 'Offense Level', #Location type 3: Not residence
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 74, 'Offense Level', #Clearance 2: Cleared incident
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 75, 'Offense Level' #Clearance 2: Not cleared incident



))

  return(returndata)
}

estimate_type_detail_rate_label <- function(indata){
  log_debug("Running estimate_type_detail_rate_label function")

  returndata <- indata %>%
    mutate(
      estimate_type_detail_rate = fcase(

trim_upcase(estimate_type) %in% c('RATE') & row == 1,  DER_NA_CODE_STRING, #Offense count
trim_upcase(estimate_type) %in% c('RATE') & row == 2,  'Offense rate per 100,000 persons', #Offense rate (per 100k total pop)
trim_upcase(estimate_type) %in% c('RATE') & row == 3,  DER_NA_CODE_STRING, #Weapon involved: No
trim_upcase(estimate_type) %in% c('RATE') & row == 4,  DER_NA_CODE_STRING, #Weapon involved: Yes
trim_upcase(estimate_type) %in% c('RATE') & row == 5,  DER_NA_CODE_STRING, #Weapon involved: Personal weapons
trim_upcase(estimate_type) %in% c('RATE') & row == 6,  DER_NA_CODE_STRING, #Weapon involved: Firearms
trim_upcase(estimate_type) %in% c('RATE') & row == 7,  DER_NA_CODE_STRING, #Weapon involved: Knives and other cutting instruments
trim_upcase(estimate_type) %in% c('RATE') & row == 8,  DER_NA_CODE_STRING, #Weapon involved: Blunt instruments
trim_upcase(estimate_type) %in% c('RATE') & row == 9,  DER_NA_CODE_STRING, #Weapon involved: Other non-personal weapons
trim_upcase(estimate_type) %in% c('RATE') & row == 10,  DER_NA_CODE_STRING, #Weapon involved: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 11,  DER_NA_CODE_STRING, #Multiple victims: 1 victim
trim_upcase(estimate_type) %in% c('RATE') & row == 12,  DER_NA_CODE_STRING, #Multiple victims: 2+ victims
trim_upcase(estimate_type) %in% c('RATE') & row == 13,  DER_NA_CODE_STRING, #Multiple offenders: 1 offender
trim_upcase(estimate_type) %in% c('RATE') & row == 14,  DER_NA_CODE_STRING, #Multiple offenders: 2+ offenders
trim_upcase(estimate_type) %in% c('RATE') & row == 15,  DER_NA_CODE_STRING, #Multiple offenders: Unknown offenders
trim_upcase(estimate_type) %in% c('RATE') & row == 16,  DER_NA_CODE_STRING, #Location type: Residence/hotel
trim_upcase(estimate_type) %in% c('RATE') & row == 17,  DER_NA_CODE_STRING, #Location type: Transportation hub/outdoor public locations
trim_upcase(estimate_type) %in% c('RATE') & row == 18,  DER_NA_CODE_STRING, #Location type: Schools, daycares, and universities
trim_upcase(estimate_type) %in% c('RATE') & row == 19,  DER_NA_CODE_STRING, #Location type: Retail/financial/other commercial establishment
trim_upcase(estimate_type) %in% c('RATE') & row == 20,  DER_NA_CODE_STRING, #Location type: Restaurant/bar/sports or entertainment venue
trim_upcase(estimate_type) %in% c('RATE') & row == 21,  DER_NA_CODE_STRING, #Location type: Religious buildings
trim_upcase(estimate_type) %in% c('RATE') & row == 22,  DER_NA_CODE_STRING, #Location type: Government/public buildings
trim_upcase(estimate_type) %in% c('RATE') & row == 23,  DER_NA_CODE_STRING, #Location type: Jail/prison
trim_upcase(estimate_type) %in% c('RATE') & row == 24,  DER_NA_CODE_STRING, #Location type: Shelter-mission/homeless
trim_upcase(estimate_type) %in% c('RATE') & row == 25,  DER_NA_CODE_STRING, #Location type: Other/unknown location
trim_upcase(estimate_type) %in% c('RATE') & row == 26,  DER_NA_CODE_STRING, #Time of day- Incident time: Midnight-4am
trim_upcase(estimate_type) %in% c('RATE') & row == 27,  DER_NA_CODE_STRING, #Time of day- Incident time: 4-8am
trim_upcase(estimate_type) %in% c('RATE') & row == 28,  DER_NA_CODE_STRING, #Time of day- Incident time: 8am-noon
trim_upcase(estimate_type) %in% c('RATE') & row == 29,  DER_NA_CODE_STRING, #Time of day- Incident time: Noon-4pm
trim_upcase(estimate_type) %in% c('RATE') & row == 30,  DER_NA_CODE_STRING, #Time of day- Incident time: 4-8pm
trim_upcase(estimate_type) %in% c('RATE') & row == 31,  DER_NA_CODE_STRING, #Time of day- Incident time: 8pm-midnight
trim_upcase(estimate_type) %in% c('RATE') & row == 32,  DER_NA_CODE_STRING, #Time of day- Incident time: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 33,  DER_NA_CODE_STRING, #Time of day- Report time: Midnight-4am
trim_upcase(estimate_type) %in% c('RATE') & row == 34,  DER_NA_CODE_STRING, #Time of day- Report time: 4-8am
trim_upcase(estimate_type) %in% c('RATE') & row == 35,  DER_NA_CODE_STRING, #Time of day- Report time: 8am-noon
trim_upcase(estimate_type) %in% c('RATE') & row == 36,  DER_NA_CODE_STRING, #Time of day- Report time: Noon-4pm
trim_upcase(estimate_type) %in% c('RATE') & row == 37,  DER_NA_CODE_STRING, #Time of day- Report time: 4-8pm
trim_upcase(estimate_type) %in% c('RATE') & row == 38,  DER_NA_CODE_STRING, #Time of day- Report time: 8pm-midnight
trim_upcase(estimate_type) %in% c('RATE') & row == 39,  DER_NA_CODE_STRING, #Time of day- Report time: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 40,  DER_NA_CODE_STRING, #Population group: Cities and counties 100,000 or over
trim_upcase(estimate_type) %in% c('RATE') & row == 41,  DER_NA_CODE_STRING, #Population group: Cities and counties 25,000-99,999
trim_upcase(estimate_type) %in% c('RATE') & row == 42,  DER_NA_CODE_STRING, #Population group: Cities and counties 10,000-24,999
trim_upcase(estimate_type) %in% c('RATE') & row == 43,  DER_NA_CODE_STRING, #Population group: Cities and counties under 10,000
trim_upcase(estimate_type) %in% c('RATE') & row == 44,  DER_NA_CODE_STRING, #Population group: State police
trim_upcase(estimate_type) %in% c('RATE') & row == 45,  DER_NA_CODE_STRING, #Population group: Possessions and Canal Zone
trim_upcase(estimate_type) %in% c('RATE') & row == 46,  DER_NA_CODE_STRING, #Agency indicator: City
trim_upcase(estimate_type) %in% c('RATE') & row == 47,  DER_NA_CODE_STRING, #Agency indicator: County
trim_upcase(estimate_type) %in% c('RATE') & row == 48,  DER_NA_CODE_STRING, #Agency indicator: University or college
trim_upcase(estimate_type) %in% c('RATE') & row == 49,  DER_NA_CODE_STRING, #Agency indicator: State police
trim_upcase(estimate_type) %in% c('RATE') & row == 50,  DER_NA_CODE_STRING, #Agency indicator: Other state agencies
trim_upcase(estimate_type) %in% c('RATE') & row == 51,  DER_NA_CODE_STRING, #Agency indicator: Tribal agencies
trim_upcase(estimate_type) %in% c('RATE') & row == 52,  DER_NA_CODE_STRING, #Agency indicator: Federal agencies
trim_upcase(estimate_type) %in% c('RATE') & row == 53,  DER_NA_CODE_STRING, #Clearance: Not cleared through arrest
trim_upcase(estimate_type) %in% c('RATE') & row == 54,  DER_NA_CODE_STRING, #Clearance: Cleared through arrest
trim_upcase(estimate_type) %in% c('RATE') & row == 55,  DER_NA_CODE_STRING, #Gang Involvement: None/Unknown gang involvement
trim_upcase(estimate_type) %in% c('RATE') & row == 56,  DER_NA_CODE_STRING, #Gang Involvement: Juvenile or other gang
trim_upcase(estimate_type) %in% c('RATE') & row == 57, DER_NA_CODE_STRING, #MSA: MSA Counties
trim_upcase(estimate_type) %in% c('RATE') & row == 58, DER_NA_CODE_STRING, #MSA: Outside MSA
trim_upcase(estimate_type) %in% c('RATE') & row == 59, DER_NA_CODE_STRING, #MSA: Non-MSA Counties
trim_upcase(estimate_type) %in% c('RATE') & row == 60, DER_NA_CODE_STRING, #MSA: Missing


trim_upcase(estimate_type) %in% c('RATE') & row == 61, DER_NA_CODE_STRING, #Location type 2: Residence/hotel
trim_upcase(estimate_type) %in% c('RATE') & row == 62, DER_NA_CODE_STRING, #Location type 2: Transportation hub/outdoor public locations
trim_upcase(estimate_type) %in% c('RATE') & row == 63, DER_NA_CODE_STRING, #Location type 2: Schools, daycares, and universities
trim_upcase(estimate_type) %in% c('RATE') & row == 64, DER_NA_CODE_STRING, #Location type 2: Retail/financial/other commercial establishment
trim_upcase(estimate_type) %in% c('RATE') & row == 65, DER_NA_CODE_STRING, #Location type 2: Restaurant/bar/sports or entertainment venue
trim_upcase(estimate_type) %in% c('RATE') & row == 66, DER_NA_CODE_STRING, #Location type 2: Religious buildings
trim_upcase(estimate_type) %in% c('RATE') & row == 67, DER_NA_CODE_STRING, #Location type 2: Government/public buildings
trim_upcase(estimate_type) %in% c('RATE') & row == 68, DER_NA_CODE_STRING, #Location type 2: Jail/prison
trim_upcase(estimate_type) %in% c('RATE') & row == 69, DER_NA_CODE_STRING, #Location type 2: Shelter-mission/homeless
trim_upcase(estimate_type) %in% c('RATE') & row == 70, DER_NA_CODE_STRING, #Location type 2: Drug Store/Doctor Office/Hospital
trim_upcase(estimate_type) %in% c('RATE') & row == 71, DER_NA_CODE_STRING, #Location type 2: Other/unknown location

trim_upcase(estimate_type) %in% c('RATE') & row == 72, DER_NA_CODE_STRING, #Location type 3: Residence
trim_upcase(estimate_type) %in% c('RATE') & row == 73, DER_NA_CODE_STRING, #Location type 3: Not residence
trim_upcase(estimate_type) %in% c('RATE') & row == 74, DER_NA_CODE_STRING, #Clearance 2: Cleared incident
trim_upcase(estimate_type) %in% c('RATE') & row == 75, DER_NA_CODE_STRING #Clearance 2: Not cleared incident


))

  return(returndata)

}


#This function will calculate the counts and percentage one column at a time

generate_est <- function(maindata, subsetvareq1, column_number, additionalweight){

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

  #Create the additional weight variable
  inweight <- additionalweight %>% rlang:::parse_expr()

  #Filter the dataset
  main_filter <- maindata[eval(infilter), c("ori", "weight", "incident_id", "offense_id", additionalweight, filtervarsting), with = FALSE]

  log_debug("After filtering main")
  log_dim(main_filter)
  log_debug(system("free -mh", intern = FALSE))

  #Incident count
  s1 <- vector("list", 2)
  #For Table
  s1[[1]] <- main_filter %>%
    mutate(weighted_count = weight *!!inweight *!!infiltervar) %>%
    summarise(final_count = sum(weighted_count, na.rm=TRUE)) %>%
    mutate(section = 1)
  #For ORI level - Need unweighted counts
  s1[[2]] <- main_filter %>%
    group_by(ori) %>%
    summarise(final_count = sum(!!inweight*!!infiltervar, na.rm=TRUE)) %>%
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
  #For ORI level - Report totals - Need unweighted counts
  s2[[2]] <- main_filter %>%
    group_by(ori) %>%
    summarise(final_count = sum(!!inweight*!!infiltervar, na.rm=TRUE)) %>%
    ungroup() %>%
    mutate(section = 2)

  #Weapon involved
  s3 <- agg_percent_add_weight(leftdata = main_filter, rightdata = agg_weapon_no_yes_inc_offenses, var=der_weapon_no_yes, section=3, mergeby=c( "incident_id", "offense_id"), addweight=additionalweight)

  der_weapon_yes_denom <- s3[[1]] %>%
    filter(der_weapon_no_yes == 2) %>% #Yes response
    select(final_count) %>%
    as.double()

  #Weapon involved Categories
  s4 <- agg_percent_CAA_add_weight(leftdata = main_filter, rightdata = agg_weapon_yes_cat_inc_offenses, var=der_weapon_yes_cat, section=4, mergeby=c( "incident_id", "offense_id"), denom=der_weapon_yes_denom, addweight=additionalweight )


  #Multiple victims
  s5 <- agg_percent_add_weight(leftdata = main_filter, rightdata = agg_victim_count_1_2_plus, var=der_victim_count, section=5, mergeby=c( "incident_id"), addweight=additionalweight)

  #Multiple offenders
  s6 <- agg_percent_add_weight(leftdata = main_filter, rightdata = agg_offender_count_1_2_plus, var=der_offender_count, section=6, mergeby=c( "incident_id"), addweight=additionalweight)

  #Location type
  s7 <- agg_percent_CAA_add_weight(leftdata = main_filter, rightdata = agg_location_cat_1_10_inc_offenses, var=der_location_1_10, section=7, mergeby=c( "incident_id", "offense_id"), denom=der_total_denom, addweight=additionalweight)

  #Time of day - Incident
  s8 <- agg_percent_add_weight(leftdata = main_filter, rightdata = agg_time_of_day_cat_incident, var=der_time_of_day_incident, section=8, mergeby=c( "incident_id"), addweight=additionalweight)

  #Time of day - Report
  s9 <- agg_percent_add_weight(leftdata = main_filter, rightdata = agg_time_of_day_cat_report, var=der_time_of_day_report, section=9, mergeby=c( "incident_id"), addweight=additionalweight)

  #Population group
  s10 <- agg_percent_add_weight(leftdata = main_filter, rightdata = ori_population_group_cat, var=der_population_group, section=10, mergeby=c( "ori"), addweight=additionalweight)
  
  #Agency indicator
  s11 <- agg_percent_add_weight(leftdata = main_filter, rightdata = ori_agency_type_cat_1_7, var=der_agency_type_1_7, section=11, mergeby=c( "ori"), addweight=additionalweight)
  
  #Clearance
  s12 <- agg_percent_add_weight(leftdata = main_filter, rightdata = agg_clearance_cat_1_2, var=der_clearance_cat_1_2, section=12, mergeby=c( "incident_id"), addweight=additionalweight)
  
  #Gang Involvement
  s13 <- agg_percent_add_weight(leftdata = main_filter, rightdata = agg_gang_cat_inc_offenses, 
                                var=der_gang_cat_no_yes, section=13, mergeby=c( "incident_id", "offense_id"), addweight=additionalweight)  
  
  #MSA indicator
  s14 <- agg_percent_add_weight(leftdata = main_filter, rightdata = ori_msa_cat, var=der_msa, section=14, mergeby=c("ori"), addweight=additionalweight)
  
  #Location type 2
  s15 <- agg_percent_CAA_add_weight(leftdata = main_filter, rightdata = agg_location_cat_1_11_inc_offenses, var=der_location_1_11, section=15, mergeby=c( "incident_id", "offense_id"), denom=der_total_denom, addweight=additionalweight)
  
  #Location type
  s16 <- agg_percent_CAA_add_weight(leftdata = main_filter, rightdata = agg_location_residence_inc_offenses, var=der_location_residence, section=16, mergeby=c( "incident_id", "offense_id"), denom=der_total_denom, addweight=additionalweight)
  
  #Clearance 2:  1 -2
  s17 <- agg_percent_add_weight(leftdata = main_filter, rightdata = agg_cleared_cat_1_2, var=der_cleared_cat_1_2, section=17, mergeby=c( "incident_id"), addweight=additionalweight)  
  

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
    mutate(count = fcase(!row %in% c(2) , final_count, default = DER_NA_CODE)) %>%
    mutate(percentage = fcase(!row %in% c(1,2), percent, default = DER_NA_CODE)) %>%
    mutate(rate = fcase(row %in% c(2), final_count, default = DER_NA_CODE)) %>%
    mutate(population_estimate = fcase(row %in% c(2), population_estimate, default = DER_NA_CODE)) %>%
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