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
    der_injury_no_yes %in% c(1:2),  der_injury_no_yes + 10,
    der_victim_count %in% c(1:2),  der_victim_count + 12,
    der_offender_count %in% c(1:3),  der_offender_count + 14,
    der_relationship %in% c(1:6),  der_relationship + 17,
    der_location_1_10 %in% c(1:10),  der_location_1_10 + 23,
    der_time_of_day_incident %in% c(1:7),  der_time_of_day_incident + 33,
    der_time_of_day_report %in% c(1:7),  der_time_of_day_report + 40,
    der_population_group %in% c(1:6),  der_population_group + 47,
    der_agency_type_1_7 %in% c(1:7),  der_agency_type_1_7 + 53,
    der_clearance_cat_1_2 %in% c(1:2),  der_clearance_cat_1_2 + 60,
    der_msa %in% c(1:4), der_msa + 62,
    der_location_1_11 %in% c(1:11), der_location_1_11 + 66,
    der_relationship2 %in% c(1:5), der_relationship2 + 77,
    der_location_cyberspace %in% c(1), 83,
	der_raw_weapon_hierarchy_recode %in% c(1:18),  der_raw_weapon_hierarchy_recode + 83,
	der_location_residence %in% c(1:2), der_location_residence + 101, 
	der_cleared_cat_1_2 %in% c(1:2), der_cleared_cat_1_2 + 103,
	der_raw_weapon_hierarchy_recode_col %in% c(1:5), der_raw_weapon_hierarchy_recode_col + 105


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
    row %in% c(13:14),  4,
    row %in% c(15:17),  5,
    row %in% c(18:23),  6,
    row %in% c(24:33),  7,
    row %in% c(34:40),  8,
    row %in% c(41:47),  9,
    row %in% c(48:53),  10,
    row %in% c(54:60),  11,
    row %in% c(61:62),  12,
    row %in% c(63:66),  13,
    row %in% c(67:77),  14,
    row %in% c(78:82),  15,
    row %in% c(83),  16,
	row %in% c(84:101), 17,
	row %in% c(102:103), 18,
	row %in% c(104:105), 19,
	row %in% c(106:110), 20

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
row == 11,  'Injury: No',
row == 12,  'Injury: Yes',
row == 13,  'Multiple victims: 1 victim',
row == 14,  'Multiple victims: 2+ victims',
row == 15,  'Multiple offenders: 1 offender',
row == 16,  'Multiple offenders: 2+ offenders',
row == 17,  'Multiple offenders: Unknown offenders',
row == 18,  'Victim-offender relationship: Intimate partner',
row == 19,  'Victim-offender relationship: Other family',
row == 20,  'Victim-offender relationship: Outside family but known to victim',
row == 21,  'Victim-offender relationship: Stranger',
row == 22,  'Victim-offender relationship: Victim was Offender',
row == 23,  'Victim-offender relationship: Unknown relationship',
row == 24,  'Location type: Residence/hotel',
row == 25,  'Location type: Transportation hub/outdoor public locations',
row == 26,  'Location type: Schools, daycares, and universities',
row == 27,  'Location type: Retail/financial/other commercial establishment',
row == 28,  'Location type: Restaurant/bar/sports or entertainment venue',
row == 29,  'Location type: Religious buildings',
row == 30,  'Location type: Government/public buildings',
row == 31,  'Location type: Jail/prison',
row == 32,  'Location type: Shelter-mission/homeless',
row == 33,  'Location type: Other/unknown location',
row == 34,  'Time of day- Incident time: Midnight-4am',
row == 35,  'Time of day- Incident time: 4-8am',
row == 36,  'Time of day- Incident time: 8am-noon',
row == 37,  'Time of day- Incident time: Noon-4pm',
row == 38,  'Time of day- Incident time: 4-8pm',
row == 39,  'Time of day- Incident time: 8pm-midnight',
row == 40,  'Time of day- Incident time: Unknown',
row == 41,  'Time of day- Report time: Midnight-4am',
row == 42,  'Time of day- Report time: 4-8am',
row == 43,  'Time of day- Report time: 8am-noon',
row == 44,  'Time of day- Report time: Noon-4pm',
row == 45,  'Time of day- Report time: 4-8pm',
row == 46,  'Time of day- Report time: 8pm-midnight',
row == 47,  'Time of day- Report time: Unknown',
row == 48,  'Population group: Cities and counties 100,000 or over',
row == 49,  'Population group: Cities and counties 25,000-99,999',
row == 50,  'Population group: Cities and counties 10,000-24,999',
row == 51,  'Population group: Cities and counties under 10,000',
row == 52,  'Population group: State police',
row == 53,  'Population group: Possessions and Canal Zone',
row == 54,  'Agency indicator: City',
row == 55,  'Agency indicator: County',
row == 56,  'Agency indicator: University or college',
row == 57,  'Agency indicator: State police',
row == 58,  'Agency indicator: Other state agencies',
row == 59,  'Agency indicator: Tribal agencies',
row == 60,  'Agency indicator: Federal agencies',
row == 61,  'Clearance: Not cleared through arrest',
row == 62,  'Clearance: Cleared through arrest',
row == 63,  'MSA: MSA Counties',
row == 64,  'MSA: Outside MSA',
row == 65,  'MSA: Non-MSA Counties',
row == 66,  'MSA: Missing',

row == 67, 'Location type 2: Residence/hotel',
row == 68, 'Location type 2: Transportation hub/outdoor public locations',
row == 69, 'Location type 2: Schools, daycares, and universities',
row == 70, 'Location type 2: Retail/financial/other commercial establishment',
row == 71, 'Location type 2: Restaurant/bar/sports or entertainment venue',
row == 72, 'Location type 2: Religious buildings',
row == 73, 'Location type 2: Government/public buildings',
row == 74, 'Location type 2: Jail/prison',
row == 75, 'Location type 2: Shelter-mission/homeless',
row == 76, 'Location type 2: Drug Store/Doctor Office/Hospital',
row == 77, 'Location type 2: Other/unknown location',
row == 78, 'Victim-offender relationship 2: Intimate partner plus Family',
row == 79, 'Victim-offender relationship 2: Outside family but known to victim',
row == 80, 'Victim-offender relationship 2: Stranger',
row == 81, 'Victim-offender relationship 2: Victim was Offender',
row == 82, 'Victim-offender relationship 2: Unknown relationship',
row == 83, 'Location cyberspace: Cyberspace',

row == 84, 'Weapon involved hierarchy: Handgun',
row == 85, 'Weapon involved hierarchy: Firearm',
row == 86, 'Weapon involved hierarchy: Rifle',
row == 87, 'Weapon involved hierarchy: Shotgun',
row == 88, 'Weapon involved hierarchy: Other Firearm',
row == 89, 'Weapon involved hierarchy: Knife/Cutting Instrument',
row == 90, 'Weapon involved hierarchy: Blunt Object',
row == 91, 'Weapon involved hierarchy: Motor Vehicle',
row == 92, 'Weapon involved hierarchy: Personal Weapons (hands, feet, teeth, etc.)',
row == 93, 'Weapon involved hierarchy: Asphyxiation',
row == 94, 'Weapon involved hierarchy: Drugs/Narcotics/Sleeping Pills',
row == 95, 'Weapon involved hierarchy: Poison (include gas)',
row == 96, 'Weapon involved hierarchy: Explosives',
row == 97, 'Weapon involved hierarchy: Fire/Incendiary Device',
row == 98, 'Weapon involved hierarchy: Other',
row == 99, 'Weapon involved hierarchy: No Weapon',
row == 100, 'Weapon involved hierarchy: Unknown',
row == 101, 'Weapon involved hierarchy: Not Applicable',

row == 102, 'Location type 3: Residence',
row == 103, 'Location type 3: Not residence',
row == 104, 'Clearance 2: Cleared incident',
row == 105, 'Clearance 2: Not cleared incident',

row == 106, 'Weapon involved hierarchy collapse: Firearm',
row == 107, 'Weapon involved hierarchy collapse: Other Weapon',
row == 108, 'Weapon involved hierarchy collapse: No Weapon',
row == 109, 'Weapon involved hierarchy collapse: Unknown',
row == 110, 'Weapon involved hierarchy collapse: Not Applicable'



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
column == 15,  'Robbery',
column == 16,  'Revised Rape',
column == 17,  'Violent Crime',
column == 18, 'Car Jacking',
column == 19, 'Assault Offenses',
column == 20, 'Violent Crime 2'




  ),

  full_table = "Table2a-Person Offenses",
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
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 11,  'Offense Level', #Injury: No
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 12,  'Offense Level', #Injury: Yes
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 13,  'Offense Level', #Multiple victims: 1 victim
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 14,  'Offense Level', #Multiple victims: 2+ victims
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 15,  'Offense Level', #Multiple offenders: 1 offender
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 16,  'Offense Level', #Multiple offenders: 2+ offenders
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 17,  'Offense Level', #Multiple offenders: Unknown offenders
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 18,  'Offense Level', #Victim-offender relationship: Intimate partner
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 19,  'Offense Level', #Victim-offender relationship: Other family
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 20,  'Offense Level', #Victim-offender relationship: Outside family but known to victim
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 21,  'Offense Level', #Victim-offender relationship: Stranger
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 22,  'Offense Level', #Victim-offender relationship: Victim was Offender
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 23,  'Offense Level', #Victim-offender relationship: Unknown relationship
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 24,  'Offense Level', #Location type: Residence/hotel
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 25,  'Offense Level', #Location type: Transportation hub/outdoor public locations
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 26,  'Offense Level', #Location type: Schools, daycares, and universities
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 27,  'Offense Level', #Location type: Retail/financial/other commercial establishment
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 28,  'Offense Level', #Location type: Restaurant/bar/sports or entertainment venue
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 29,  'Offense Level', #Location type: Religious buildings
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 30,  'Offense Level', #Location type: Government/public buildings
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 31,  'Offense Level', #Location type: Jail/prison
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 32,  'Offense Level', #Location type: Shelter-mission/homeless
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 33,  'Offense Level', #Location type: Other/unknown location
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 34,  'Offense Level', #Time of day- Incident time: Midnight-4am
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 35,  'Offense Level', #Time of day- Incident time: 4-8am
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 36,  'Offense Level', #Time of day- Incident time: 8am-noon
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 37,  'Offense Level', #Time of day- Incident time: Noon-4pm
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 38,  'Offense Level', #Time of day- Incident time: 4-8pm
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 39,  'Offense Level', #Time of day- Incident time: 8pm-midnight
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 40,  'Offense Level', #Time of day- Incident time: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 41,  'Offense Level', #Time of day- Report time: Midnight-4am
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 42,  'Offense Level', #Time of day- Report time: 4-8am
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 43,  'Offense Level', #Time of day- Report time: 8am-noon
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 44,  'Offense Level', #Time of day- Report time: Noon-4pm
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 45,  'Offense Level', #Time of day- Report time: 4-8pm
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 46,  'Offense Level', #Time of day- Report time: 8pm-midnight
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 47,  'Offense Level', #Time of day- Report time: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 48,  'Offense Level', #Population group: Cities and counties 100,000 or over
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 49,  'Offense Level', #Population group: Cities and counties 25,000-99,999
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 50,  'Offense Level', #Population group: Cities and counties 10,000-24,999
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 51,  'Offense Level', #Population group: Cities and counties under 10,000
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 52,  'Offense Level', #Population group: State police
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 53,  'Offense Level', #Population group: Possessions and Canal Zone
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 54,  'Offense Level', #Agency indicator: City
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 55,  'Offense Level', #Agency indicator: County
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 56,  'Offense Level', #Agency indicator: University or college
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 57,  'Offense Level', #Agency indicator: State police
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 58,  'Offense Level', #Agency indicator: Other state agencies
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 59,  'Offense Level', #Agency indicator: Tribal agencies
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 60,  'Offense Level', #Agency indicator: Federal agencies
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 61,  'Offense Level', #Clearance: Not cleared through arrest
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 62,  'Offense Level', #Clearance: Cleared through arrest
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 63,  'Offense Level', #MSA: MSA Counties
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 64,  'Offense Level', #MSA: Outside MSA
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 65,  'Offense Level', #MSA: Non-MSA Counties
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 66,  'Offense Level', #MSA: Missing

trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 67, 'Offense Level', #Location type 2: Residence/hotel
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 68, 'Offense Level', #Location type 2: Transportation hub/outdoor public locations
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 69, 'Offense Level', #Location type 2: Schools, daycares, and universities
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 70, 'Offense Level', #Location type 2: Retail/financial/other commercial establishment
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 71, 'Offense Level', #Location type 2: Restaurant/bar/sports or entertainment venue
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 72, 'Offense Level', #Location type 2: Religious buildings
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 73, 'Offense Level', #Location type 2: Government/public buildings
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 74, 'Offense Level', #Location type 2: Jail/prison
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 75, 'Offense Level', #Location type 2: Shelter-mission/homeless
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 76, 'Offense Level', #Location type 2: Drug Store/Doctor Office/Hospital
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 77, 'Offense Level', #Location type 2: Other/unknown location
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 78, 'Offense Level', #Victim-offender relationship 2: Intimate partner plus Family
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 79, 'Offense Level', #Victim-offender relationship 2: Outside family but known to victim
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 80, 'Offense Level', #Victim-offender relationship 2: Stranger
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 81, 'Offense Level', #Victim-offender relationship 2: Victim was Offender
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 82, 'Offense Level', #Victim-offender relationship 2: Unknown relationship
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 83, 'Offense Level', #Location cyberspace: Cyberspace

trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 84, 'Offense Level', #Weapon involved hierarchy: Handgun
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 85, 'Offense Level', #Weapon involved hierarchy: Firearm
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 86, 'Offense Level', #Weapon involved hierarchy: Rifle
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 87, 'Offense Level', #Weapon involved hierarchy: Shotgun
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 88, 'Offense Level', #Weapon involved hierarchy: Other Firearm
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 89, 'Offense Level', #Weapon involved hierarchy: Knife/Cutting Instrument
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 90, 'Offense Level', #Weapon involved hierarchy: Blunt Object
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 91, 'Offense Level', #Weapon involved hierarchy: Motor Vehicle
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 92, 'Offense Level', #Weapon involved hierarchy: Personal Weapons (hands, feet, teeth, etc.)
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 93, 'Offense Level', #Weapon involved hierarchy: Asphyxiation
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 94, 'Offense Level', #Weapon involved hierarchy: Drugs/Narcotics/Sleeping Pills
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 95, 'Offense Level', #Weapon involved hierarchy: Poison (include gas)
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 96, 'Offense Level', #Weapon involved hierarchy: Explosives
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 97, 'Offense Level', #Weapon involved hierarchy: Fire/Incendiary Device
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 98, 'Offense Level', #Weapon involved hierarchy: Other
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 99, 'Offense Level', #Weapon involved hierarchy: No Weapon
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 100, 'Offense Level', #Weapon involved hierarchy: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 101, 'Offense Level', #Weapon involved hierarchy: Not Applicable

trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 102, 'Offense Level', #Location type 3: Residence
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 103, 'Offense Level', #Location type 3: Not residence
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 104, 'Offense Level', #Clearance 2: Cleared incident
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 105, 'Offense Level', #Clearance 2: Not cleared incident

trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 106, 'Offense Level', #Weapon involved hierarchy collapse: Firearm
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 107, 'Offense Level', #Weapon involved hierarchy collapse: Other Weapon
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 108, 'Offense Level', #Weapon involved hierarchy collapse: No Weapon
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 109, 'Offense Level', #Weapon involved hierarchy collapse: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 110, 'Offense Level' #Weapon involved hierarchy collapse: Not Applicable



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
trim_upcase(estimate_type) %in% c('RATE') & row == 11,  DER_NA_CODE_STRING, #Injury: No
trim_upcase(estimate_type) %in% c('RATE') & row == 12,  DER_NA_CODE_STRING, #Injury: Yes
trim_upcase(estimate_type) %in% c('RATE') & row == 13,  DER_NA_CODE_STRING, #Multiple victims: 1 victim
trim_upcase(estimate_type) %in% c('RATE') & row == 14,  DER_NA_CODE_STRING, #Multiple victims: 2+ victims
trim_upcase(estimate_type) %in% c('RATE') & row == 15,  DER_NA_CODE_STRING, #Multiple offenders: 1 offender
trim_upcase(estimate_type) %in% c('RATE') & row == 16,  DER_NA_CODE_STRING, #Multiple offenders: 2+ offenders
trim_upcase(estimate_type) %in% c('RATE') & row == 17,  DER_NA_CODE_STRING, #Multiple offenders: Unknown offenders
trim_upcase(estimate_type) %in% c('RATE') & row == 18,  DER_NA_CODE_STRING, #Victim-offender relationship: Intimate partner
trim_upcase(estimate_type) %in% c('RATE') & row == 19,  DER_NA_CODE_STRING, #Victim-offender relationship: Other family
trim_upcase(estimate_type) %in% c('RATE') & row == 20,  DER_NA_CODE_STRING, #Victim-offender relationship: Outside family but known to victim
trim_upcase(estimate_type) %in% c('RATE') & row == 21,  DER_NA_CODE_STRING, #Victim-offender relationship: Stranger
trim_upcase(estimate_type) %in% c('RATE') & row == 22,  DER_NA_CODE_STRING, #Victim-offender relationship: Victim was Offender
trim_upcase(estimate_type) %in% c('RATE') & row == 23,  DER_NA_CODE_STRING, #Victim-offender relationship: Unknown relationship
trim_upcase(estimate_type) %in% c('RATE') & row == 24,  DER_NA_CODE_STRING, #Location type: Residence/hotel
trim_upcase(estimate_type) %in% c('RATE') & row == 25,  DER_NA_CODE_STRING, #Location type: Transportation hub/outdoor public locations
trim_upcase(estimate_type) %in% c('RATE') & row == 26,  DER_NA_CODE_STRING, #Location type: Schools, daycares, and universities
trim_upcase(estimate_type) %in% c('RATE') & row == 27,  DER_NA_CODE_STRING, #Location type: Retail/financial/other commercial establishment
trim_upcase(estimate_type) %in% c('RATE') & row == 28,  DER_NA_CODE_STRING, #Location type: Restaurant/bar/sports or entertainment venue
trim_upcase(estimate_type) %in% c('RATE') & row == 29,  DER_NA_CODE_STRING, #Location type: Religious buildings
trim_upcase(estimate_type) %in% c('RATE') & row == 30,  DER_NA_CODE_STRING, #Location type: Government/public buildings
trim_upcase(estimate_type) %in% c('RATE') & row == 31,  DER_NA_CODE_STRING, #Location type: Jail/prison
trim_upcase(estimate_type) %in% c('RATE') & row == 32,  DER_NA_CODE_STRING, #Location type: Shelter-mission/homeless
trim_upcase(estimate_type) %in% c('RATE') & row == 33,  DER_NA_CODE_STRING, #Location type: Other/unknown location
trim_upcase(estimate_type) %in% c('RATE') & row == 34,  DER_NA_CODE_STRING, #Time of day- Incident time: Midnight-4am
trim_upcase(estimate_type) %in% c('RATE') & row == 35,  DER_NA_CODE_STRING, #Time of day- Incident time: 4-8am
trim_upcase(estimate_type) %in% c('RATE') & row == 36,  DER_NA_CODE_STRING, #Time of day- Incident time: 8am-noon
trim_upcase(estimate_type) %in% c('RATE') & row == 37,  DER_NA_CODE_STRING, #Time of day- Incident time: Noon-4pm
trim_upcase(estimate_type) %in% c('RATE') & row == 38,  DER_NA_CODE_STRING, #Time of day- Incident time: 4-8pm
trim_upcase(estimate_type) %in% c('RATE') & row == 39,  DER_NA_CODE_STRING, #Time of day- Incident time: 8pm-midnight
trim_upcase(estimate_type) %in% c('RATE') & row == 40,  DER_NA_CODE_STRING, #Time of day- Incident time: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 41,  DER_NA_CODE_STRING, #Time of day- Report time: Midnight-4am
trim_upcase(estimate_type) %in% c('RATE') & row == 42,  DER_NA_CODE_STRING, #Time of day- Report time: 4-8am
trim_upcase(estimate_type) %in% c('RATE') & row == 43,  DER_NA_CODE_STRING, #Time of day- Report time: 8am-noon
trim_upcase(estimate_type) %in% c('RATE') & row == 44,  DER_NA_CODE_STRING, #Time of day- Report time: Noon-4pm
trim_upcase(estimate_type) %in% c('RATE') & row == 45,  DER_NA_CODE_STRING, #Time of day- Report time: 4-8pm
trim_upcase(estimate_type) %in% c('RATE') & row == 46,  DER_NA_CODE_STRING, #Time of day- Report time: 8pm-midnight
trim_upcase(estimate_type) %in% c('RATE') & row == 47,  DER_NA_CODE_STRING, #Time of day- Report time: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 48,  DER_NA_CODE_STRING, #Population group: Cities and counties 100,000 or over
trim_upcase(estimate_type) %in% c('RATE') & row == 49,  DER_NA_CODE_STRING, #Population group: Cities and counties 25,000-99,999
trim_upcase(estimate_type) %in% c('RATE') & row == 50,  DER_NA_CODE_STRING, #Population group: Cities and counties 10,000-24,999
trim_upcase(estimate_type) %in% c('RATE') & row == 51,  DER_NA_CODE_STRING, #Population group: Cities and counties under 10,000
trim_upcase(estimate_type) %in% c('RATE') & row == 52,  DER_NA_CODE_STRING, #Population group: State police
trim_upcase(estimate_type) %in% c('RATE') & row == 53,  DER_NA_CODE_STRING, #Population group: Possessions and Canal Zone
trim_upcase(estimate_type) %in% c('RATE') & row == 54,  DER_NA_CODE_STRING, #Agency indicator: City
trim_upcase(estimate_type) %in% c('RATE') & row == 55,  DER_NA_CODE_STRING, #Agency indicator: County
trim_upcase(estimate_type) %in% c('RATE') & row == 56,  DER_NA_CODE_STRING, #Agency indicator: University or college
trim_upcase(estimate_type) %in% c('RATE') & row == 57,  DER_NA_CODE_STRING, #Agency indicator: State police
trim_upcase(estimate_type) %in% c('RATE') & row == 58,  DER_NA_CODE_STRING, #Agency indicator: Other state agencies
trim_upcase(estimate_type) %in% c('RATE') & row == 59,  DER_NA_CODE_STRING, #Agency indicator: Tribal agencies
trim_upcase(estimate_type) %in% c('RATE') & row == 60,  DER_NA_CODE_STRING, #Agency indicator: Federal agencies
trim_upcase(estimate_type) %in% c('RATE') & row == 61,  DER_NA_CODE_STRING, #Clearance: Not cleared through arrest
trim_upcase(estimate_type) %in% c('RATE') & row == 62,  DER_NA_CODE_STRING, #Clearance: Cleared through arrest
trim_upcase(estimate_type) %in% c('RATE') & row == 63,  DER_NA_CODE_STRING, #MSA: MSA Counties
trim_upcase(estimate_type) %in% c('RATE') & row == 64,  DER_NA_CODE_STRING, #MSA: Outside MSA
trim_upcase(estimate_type) %in% c('RATE') & row == 65,  DER_NA_CODE_STRING, #MSA: Non-MSA Counties
trim_upcase(estimate_type) %in% c('RATE') & row == 66,  DER_NA_CODE_STRING, #MSA: Missing

trim_upcase(estimate_type) %in% c('RATE') & row == 67, DER_NA_CODE_STRING, #Location type 2: Residence/hotel
trim_upcase(estimate_type) %in% c('RATE') & row == 68, DER_NA_CODE_STRING, #Location type 2: Transportation hub/outdoor public locations
trim_upcase(estimate_type) %in% c('RATE') & row == 69, DER_NA_CODE_STRING, #Location type 2: Schools, daycares, and universities
trim_upcase(estimate_type) %in% c('RATE') & row == 70, DER_NA_CODE_STRING, #Location type 2: Retail/financial/other commercial establishment
trim_upcase(estimate_type) %in% c('RATE') & row == 71, DER_NA_CODE_STRING, #Location type 2: Restaurant/bar/sports or entertainment venue
trim_upcase(estimate_type) %in% c('RATE') & row == 72, DER_NA_CODE_STRING, #Location type 2: Religious buildings
trim_upcase(estimate_type) %in% c('RATE') & row == 73, DER_NA_CODE_STRING, #Location type 2: Government/public buildings
trim_upcase(estimate_type) %in% c('RATE') & row == 74, DER_NA_CODE_STRING, #Location type 2: Jail/prison
trim_upcase(estimate_type) %in% c('RATE') & row == 75, DER_NA_CODE_STRING, #Location type 2: Shelter-mission/homeless
trim_upcase(estimate_type) %in% c('RATE') & row == 76, DER_NA_CODE_STRING, #Location type 2: Drug Store/Doctor Office/Hospital
trim_upcase(estimate_type) %in% c('RATE') & row == 77, DER_NA_CODE_STRING, #Location type 2: Other/unknown location
trim_upcase(estimate_type) %in% c('RATE') & row == 78, DER_NA_CODE_STRING, #Victim-offender relationship 2: Intimate partner plus Family
trim_upcase(estimate_type) %in% c('RATE') & row == 79, DER_NA_CODE_STRING, #Victim-offender relationship 2: Outside family but known to victim
trim_upcase(estimate_type) %in% c('RATE') & row == 80, DER_NA_CODE_STRING, #Victim-offender relationship 2: Stranger
trim_upcase(estimate_type) %in% c('RATE') & row == 81, DER_NA_CODE_STRING, #Victim-offender relationship 2: Victim was Offender
trim_upcase(estimate_type) %in% c('RATE') & row == 82, DER_NA_CODE_STRING, #Victim-offender relationship 2: Unknown relationship
trim_upcase(estimate_type) %in% c('RATE') & row == 83, DER_NA_CODE_STRING, #Location cyberspace: Cyberspace

trim_upcase(estimate_type) %in% c('RATE') & row == 84, DER_NA_CODE_STRING, #Weapon involved hierarchy: Handgun
trim_upcase(estimate_type) %in% c('RATE') & row == 85, DER_NA_CODE_STRING, #Weapon involved hierarchy: Firearm
trim_upcase(estimate_type) %in% c('RATE') & row == 86, DER_NA_CODE_STRING, #Weapon involved hierarchy: Rifle
trim_upcase(estimate_type) %in% c('RATE') & row == 87, DER_NA_CODE_STRING, #Weapon involved hierarchy: Shotgun
trim_upcase(estimate_type) %in% c('RATE') & row == 88, DER_NA_CODE_STRING, #Weapon involved hierarchy: Other Firearm
trim_upcase(estimate_type) %in% c('RATE') & row == 89, DER_NA_CODE_STRING, #Weapon involved hierarchy: Knife/Cutting Instrument
trim_upcase(estimate_type) %in% c('RATE') & row == 90, DER_NA_CODE_STRING, #Weapon involved hierarchy: Blunt Object
trim_upcase(estimate_type) %in% c('RATE') & row == 91, DER_NA_CODE_STRING, #Weapon involved hierarchy: Motor Vehicle
trim_upcase(estimate_type) %in% c('RATE') & row == 92, DER_NA_CODE_STRING, #Weapon involved hierarchy: Personal Weapons (hands, feet, teeth, etc.)
trim_upcase(estimate_type) %in% c('RATE') & row == 93, DER_NA_CODE_STRING, #Weapon involved hierarchy: Asphyxiation
trim_upcase(estimate_type) %in% c('RATE') & row == 94, DER_NA_CODE_STRING, #Weapon involved hierarchy: Drugs/Narcotics/Sleeping Pills
trim_upcase(estimate_type) %in% c('RATE') & row == 95, DER_NA_CODE_STRING, #Weapon involved hierarchy: Poison (include gas)
trim_upcase(estimate_type) %in% c('RATE') & row == 96, DER_NA_CODE_STRING, #Weapon involved hierarchy: Explosives
trim_upcase(estimate_type) %in% c('RATE') & row == 97, DER_NA_CODE_STRING, #Weapon involved hierarchy: Fire/Incendiary Device
trim_upcase(estimate_type) %in% c('RATE') & row == 98, DER_NA_CODE_STRING, #Weapon involved hierarchy: Other
trim_upcase(estimate_type) %in% c('RATE') & row == 99, DER_NA_CODE_STRING, #Weapon involved hierarchy: No Weapon
trim_upcase(estimate_type) %in% c('RATE') & row == 100, DER_NA_CODE_STRING, #Weapon involved hierarchy: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 101, DER_NA_CODE_STRING, #Weapon involved hierarchy: Not Applicable

trim_upcase(estimate_type) %in% c('RATE') & row == 102, DER_NA_CODE_STRING, #Location type 3: Residence
trim_upcase(estimate_type) %in% c('RATE') & row == 103, DER_NA_CODE_STRING, #Location type 3: Not residence
trim_upcase(estimate_type) %in% c('RATE') & row == 104, DER_NA_CODE_STRING, #Clearance 2: Cleared incident
trim_upcase(estimate_type) %in% c('RATE') & row == 105, DER_NA_CODE_STRING, #Clearance 2: Not cleared incident

trim_upcase(estimate_type) %in% c('RATE') & row == 106, DER_NA_CODE_STRING, #Weapon involved hierarchy collapse: Firearm
trim_upcase(estimate_type) %in% c('RATE') & row == 107, DER_NA_CODE_STRING, #Weapon involved hierarchy collapse: Other Weapon
trim_upcase(estimate_type) %in% c('RATE') & row == 108, DER_NA_CODE_STRING, #Weapon involved hierarchy collapse: No Weapon
trim_upcase(estimate_type) %in% c('RATE') & row == 109, DER_NA_CODE_STRING, #Weapon involved hierarchy collapse: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 110, DER_NA_CODE_STRING #Weapon involved hierarchy collapse: Not Applicable


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
  main_filter <- maindata[eval(infilter), c("ori", "weight", "incident_id", "victim_id", "offense_id", filtervarsting), with = FALSE]

  log_debug("After filtering main")
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

  #Total Denominator
  der_total_denom <- s1[[1]] %>% select(final_count) %>% as.double()

  #Incident rate
  s2 <- vector("list", 2)
  #For Table
  s2[[1]] <- s1[[1]] %>%
    mutate(final_count = (final_count / POP_TOTAL) * 100000,
           population_estimate = POP_TOTAL
           ) %>%
    mutate(section = 2)
  #For ORI level - Report totals - Need unweighted counts
  s2[[2]] <- main_filter %>%
    group_by(ori) %>%
    summarise(final_count = sum(!!infiltervar)) %>%
    ungroup() %>%
    mutate(section = 2)

  #Weapon involved
  s3 <- agg_percent(leftdata = main_filter, rightdata = agg_weapon_no_yes_offenses, var=der_weapon_no_yes, section=3, mergeby=c( "incident_id", "victim_id", "offense_id"))

  der_weapon_yes_denom <- s3[[1]] %>%
    filter(der_weapon_no_yes == 2) %>% #Yes response
    select(final_count) %>%
    as.double()

  #Weapon involved Categories
  s4 <- agg_percent_CAA(leftdata = main_filter, rightdata = agg_weapon_yes_cat_offenses, var=der_weapon_yes_cat, section=4, mergeby=c( "incident_id", "victim_id", "offense_id"), denom=der_weapon_yes_denom )

  #Injury
  s5 <- agg_percent(leftdata = main_filter, rightdata = agg_injury_no_yes_victim, var=der_injury_no_yes, section=5, mergeby=c( "incident_id", "victim_id"))

  #Multiple victims
  s6 <- agg_percent(leftdata = main_filter, rightdata = agg_victim_count_1_2_plus, var=der_victim_count, section=6, mergeby=c( "incident_id"))

  #Multiple offenders
  s7 <- agg_percent(leftdata = main_filter, rightdata = agg_offender_count_1_2_plus, var=der_offender_count, section=7, mergeby=c( "incident_id"))

  #Victim-offender relationship
  s8 <- agg_percent_CAA(leftdata = main_filter, rightdata = agg_relationship_cat_victim, var=der_relationship, section=8, mergeby=c( "incident_id", "victim_id"), denom=der_total_denom)

  #Location type
  s9 <- agg_percent_CAA(leftdata = main_filter, rightdata = agg_location_cat_1_10_offenses, var=der_location_1_10, section=9, mergeby=c( "incident_id", "victim_id", "offense_id"), denom=der_total_denom)

  #Time of day - Incident
  s10 <- agg_percent(leftdata = main_filter, rightdata = agg_time_of_day_cat_incident, var=der_time_of_day_incident, section=10, mergeby=c( "incident_id"))

  #Time of day - Report
  s11 <- agg_percent(leftdata = main_filter, rightdata = agg_time_of_day_cat_report, var=der_time_of_day_report, section=11, mergeby=c( "incident_id"))

  #Population group
  s12 <- agg_percent(leftdata = main_filter, rightdata = ori_population_group_cat, var=der_population_group, section=12,mergeby=c("ori"))

  #Agency indicator
  s13 <- agg_percent(leftdata = main_filter, rightdata = ori_agency_type_cat_1_7, var=der_agency_type_1_7, section=13, mergeby=c("ori"))

  #Clearance 1 -2
  s14 <- agg_percent(leftdata = main_filter, rightdata = agg_clearance_cat_1_2, var=der_clearance_cat_1_2, section=14, mergeby=c( "incident_id"))

  #MSA indicator
  s15 <- agg_percent(leftdata = main_filter, rightdata = ori_msa_cat, var=der_msa, section=15, mergeby=c("ori"))

  #Location type2
  s16 <- agg_percent_CAA(leftdata = main_filter, rightdata = agg_location_cat_1_11_offenses, var=der_location_1_11, section=16, mergeby=c( "incident_id", "victim_id", "offense_id"), denom=der_total_denom)

  #Victim-offender relationship 2
  s17 <- agg_percent_CAA(leftdata = main_filter, rightdata = agg_relationship_cat2_victim_imp, var=der_relationship2, section=17, mergeby=c( "incident_id", "victim_id"), denom=der_total_denom)

  #Location Cyberspace
  s18 <- agg_percent_CAA(leftdata = main_filter, rightdata = agg_location_cyberspace_offenses, var=der_location_cyberspace, section=18, mergeby=c( "incident_id", "victim_id", "offense_id"), denom=der_total_denom)

  #Weapon involved hierarchy
  s19 <- agg_percent(leftdata = main_filter, rightdata = agg_raw_weapon_hierarchy_recode_offenses, var=der_raw_weapon_hierarchy_recode, section=19, 
                     mergeby=c( "incident_id", "victim_id", "offense_id"))  	
  
  #Location type
  s20 <- agg_percent_CAA(leftdata = main_filter, rightdata = agg_location_residence_offenses, var=der_location_residence, section=20, mergeby=c( "incident_id", "victim_id", "offense_id"), denom=der_total_denom)
  
  #Clearance 2:  1 -2
  s21 <- agg_percent(leftdata = main_filter, rightdata = agg_cleared_cat_1_2, var=der_cleared_cat_1_2, section=21, mergeby=c( "incident_id"))  

  #Weapon involved hierarchy collapse
  s22 <- agg_percent(leftdata = main_filter, rightdata = agg_raw_weapon_hierarchy_recode_col_offenses, var=der_raw_weapon_hierarchy_recode_col, section=22, mergeby=c( "incident_id", "victim_id", "offense_id"))  

  
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