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
    der_offense_count %in% c(1:3),  der_offense_count + 17,
    der_relationship %in% c(1:6),  der_relationship + 20,
    der_location_1_10 %in% c(1:10),  der_location_1_10 + 26,
    der_time_of_day_incident %in% c(1:7),  der_time_of_day_incident + 36,
	der_time_of_day_report %in% c(1:7),  der_time_of_day_report + 43,
    der_population_group %in% c(1:6),  der_population_group + 50,
    der_agency_type_1_7 %in% c(1:7),  der_agency_type_1_7 + 56,
    der_clearance_cat %in% c(1:3),  der_clearance_cat + 63,
    der_exceptional_clearance %in% c(1:5),  der_exceptional_clearance + 66,
    der_property_loss %in% c(1:8),  der_property_loss + 71,
	  der_msa %in% c(1:4), der_msa + 79,
	  der_location_1_11 %in% c(1:11), der_location_1_11 + 83,
	  der_relationship2 %in% c(1:5), der_relationship2 + 94,
	  der_location_residence %in% c(1:2), der_location_residence + 99
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
    row %in% c(18:20),  6,
    row %in% c(21:26),  7,
    row %in% c(27:36),  8,
    row %in% c(37:43),  9,
    row %in% c(44:50),  10,
    row %in% c(51:56),  11,
    row %in% c(57:63),  12,
    row %in% c(64:71),  13,
	  row %in% c(72:79),  14,
    row %in% c(80:83),  15,
    row %in% c(84:94),  16,
    row %in% c(95:99),  17,
	row %in% c(100:101),  18
    )
  )

  return(returndata)

}


#New add on code for labels
assign_labels <- function(data){
  log_debug("Running assign_labels function")
  returndata <- data %>% mutate(

  estimate_domain = fcase(

row == 1,  'Incident count',
row == 2,  'Incident rate (per 100k total pop)',
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
row == 18,  'Multiple offense incident: 1 offense',
row == 19,  'Multiple offense incident: 2 offenses',
row == 20,  'Multiple offense incident: 3+ offenses',
row == 21,  'Victim-offender relationship: Intimate partner',
row == 22,  'Victim-offender relationship: Other family',
row == 23,  'Victim-offender relationship: Outside family but known to victim',
row == 24,  'Victim-offender relationship: Stranger',
row == 25,  'Victim-offender relationship: Victim was Offender',
row == 26,  'Victim-offender relationship: Unknown relationship',
row == 27,  'Location type: Residence/hotel',
row == 28,  'Location type: Transportation hub/outdoor public locations',
row == 29,  'Location type: Schools, daycares, and universities',
row == 30,  'Location type: Retail/financial/other commercial establishment',
row == 31,  'Location type: Restaurant/bar/sports or entertainment venue',
row == 32,  'Location type: Religious buildings',
row == 33,  'Location type: Government/public buildings',
row == 34,  'Location type: Jail/prison',
row == 35,  'Location type: Shelter-mission/homeless',
row == 36,  'Location type: Other/unknown location',
row == 37,  'Time of day- Incident time: Midnight-4am',
row == 38,  'Time of day- Incident time: 4-8am',
row == 39,  'Time of day- Incident time: 8am-noon',
row == 40,  'Time of day- Incident time: Noon-4pm',
row == 41,  'Time of day- Incident time: 4-8pm',
row == 42,  'Time of day- Incident time: 8pm-midnight',
row == 43,  'Time of day- Incident time: Unknown',
row == 44,  'Time of day- Report time: Midnight-4am',
row == 45,  'Time of day- Report time: 4-8am',
row == 46,  'Time of day- Report time: 8am-noon',
row == 47,  'Time of day- Report time: Noon-4pm',
row == 48,  'Time of day- Report time: 4-8pm',
row == 49,  'Time of day- Report time: 8pm-midnight',
row == 50,  'Time of day- Report time: Unknown',
row == 51,  'Population group: Cities and counties 100,000 or over',
row == 52,  'Population group: Cities and counties 25,000-99,999',
row == 53,  'Population group: Cities and counties 10,000-24,999',
row == 54,  'Population group: Cities and counties under 10,000',
row == 55,  'Population group: State police',
row == 56,  'Population group: Possessions and Canal Zone',
row == 57,  'Agency indicator: City',
row == 58,  'Agency indicator: County',
row == 59,  'Agency indicator: University or college',
row == 60,  'Agency indicator: State police',
row == 61,  'Agency indicator: Other state agencies',
row == 62,  'Agency indicator: Tribal agencies',
row == 63,  'Agency indicator: Federal agencies',
row == 64,  'Clearance: Not cleared',
row == 65,  'Clearance: Cleared through arrest',
row == 66,  'Clearance: Exceptional clearance',
row == 67,  'Clearance: Death of offender',
row == 68,  'Clearance: Prosecution declined',
row == 69,  'Clearance: In custody of other jurisdiction',
row == 70,  'Clearance: Victim refused to cooperate',
row == 71,  'Clearance: Juvenile/no custody',
row == 72,  'Property loss: None',
row == 73,  'Property loss: Burned',
row == 74,  'Property loss: Counterfeited/forged',
row == 75,  'Property loss: Destroyed/damaged/vandalized',
row == 76,  'Property loss: Recovered',
row == 77,  'Property loss: Seized',
row == 78,  'Property loss: Stolen/Et',
row == 79,  'Property loss: Unknown',
row == 80, 'MSA: MSA Counties',
row == 81, 'MSA: Outside MSA',
row == 82, 'MSA: Non-MSA Counties',
row == 83, 'MSA: Missing',

row == 84, 'Location type 2: Residence/hotel',
row == 85, 'Location type 2: Transportation hub/outdoor public locations',
row == 86, 'Location type 2: Schools, daycares, and universities',
row == 87, 'Location type 2: Retail/financial/other commercial establishment',
row == 88, 'Location type 2: Restaurant/bar/sports or entertainment venue',
row == 89, 'Location type 2: Religious buildings',
row == 90, 'Location type 2: Government/public buildings',
row == 91, 'Location type 2: Jail/prison',
row == 92, 'Location type 2: Shelter-mission/homeless',
row == 93, 'Location type 2: Drug Store/Doctor Office/Hospital',
row == 94, 'Location type 2: Other/unknown location',
row == 95, 'Victim-offender relationship 2: Intimate partner plus Family',
row == 96, 'Victim-offender relationship 2: Outside family but known to victim',
row == 97, 'Victim-offender relationship 2: Stranger',
row == 98, 'Victim-offender relationship 2: Victim was Offender',
row == 99, 'Victim-offender relationship 2: Unknown relationship',

row == 100, 'Location type 3: Residence',
row == 101, 'Location type 3: Not residence'


  )
)
returndata <- returndata %>% mutate(
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
column == 18,  'Car Jacking',
column == 19, 'Assault Offenses',
column == 20, 'Violent Crime 2'


  ),

  full_table = "Table1a-Person Incidents",
  table = DER_TABLE_NAME
  )

  return(returndata)

}

estimate_type_detail_percentage_label <- function(indata){
  log_debug("Running estimate_type_detail_percentage_label function")
  returndata <- indata %>%
    mutate(
      estimate_type_detail_percentage = fcase(

trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 1,  'Incident Level', #Incident count
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 2,  'Incident Level', #Incident rate (per 100k total pop)
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 3,  'Incident Level', #Weapon involved: No
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 4,  'Incident Level', #Weapon involved: Yes
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 5,  'Incident Level subset to weapon involved yes', #Weapon involved: Personal weapons
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 6,  'Incident Level subset to weapon involved yes', #Weapon involved: Firearms
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 7,  'Incident Level subset to weapon involved yes', #Weapon involved: Knives and other cutting instruments
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 8,  'Incident Level subset to weapon involved yes', #Weapon involved: Blunt instruments
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 9,  'Incident Level subset to weapon involved yes', #Weapon involved: Other non-personal weapons
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 10,  'Incident Level subset to weapon involved yes', #Weapon involved: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 11,  'Incident Level', #Injury: No
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 12,  'Incident Level', #Injury: Yes
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 13,  'Incident Level', #Multiple victims: 1 victim
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 14,  'Incident Level', #Multiple victims: 2+ victims
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 15,  'Incident Level', #Multiple offenders: 1 offender
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 16,  'Incident Level', #Multiple offenders: 2+ offenders
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 17,  'Incident Level', #Multiple offenders: Unknown offenders
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 18,  'Incident Level', #Multiple offense incident: 1 offense
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 19,  'Incident Level', #Multiple offense incident: 2 offenses
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 20,  'Incident Level', #Multiple offense incident: 3+ offenses
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 21,  'Incident Level', #Victim-offender relationship: Intimate partner
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 22,  'Incident Level', #Victim-offender relationship: Other family
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 23,  'Incident Level', #Victim-offender relationship: Outside family but known to victim
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 24,  'Incident Level', #Victim-offender relationship: Stranger
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 25,  'Incident Level', #Victim-offender relationship: Victim was Offender
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 26,  'Incident Level', #Victim-offender relationship: Unknown relationship
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 27,  'Incident Level', #Location type: Residence/hotel
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 28,  'Incident Level', #Location type: Transportation hub/outdoor public locations
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 29,  'Incident Level', #Location type: Schools, daycares, and universities
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 30,  'Incident Level', #Location type: Retail/financial/other commercial establishment
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 31,  'Incident Level', #Location type: Restaurant/bar/sports or entertainment venue
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 32,  'Incident Level', #Location type: Religious buildings
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 33,  'Incident Level', #Location type: Government/public buildings
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 34,  'Incident Level', #Location type: Jail/prison
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 35,  'Incident Level', #Location type: Shelter-mission/homeless
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 36,  'Incident Level', #Location type: Other/unknown location
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 37,  'Incident Level', #Time of day- Incident time: Midnight-4am
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 38,  'Incident Level', #Time of day- Incident time: 4-8am
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 39,  'Incident Level', #Time of day- Incident time: 8am-noon
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 40,  'Incident Level', #Time of day- Incident time: Noon-4pm
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 41,  'Incident Level', #Time of day- Incident time: 4-8pm
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 42,  'Incident Level', #Time of day- Incident time: 8pm-midnight
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 43,  'Incident Level', #Time of day- Incident time: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 44,  'Incident Level', #Time of day- Report time: Midnight-4am
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 45,  'Incident Level', #Time of day- Report time: 4-8am
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 46,  'Incident Level', #Time of day- Report time: 8am-noon
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 47,  'Incident Level', #Time of day- Report time: Noon-4pm
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 48,  'Incident Level', #Time of day- Report time: 4-8pm
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 49,  'Incident Level', #Time of day- Report time: 8pm-midnight
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 50,  'Incident Level', #Time of day- Report time: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 51,  'Incident Level', #Population group: Cities and counties 100,000 or over
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 52,  'Incident Level', #Population group: Cities and counties 25,000-99,999
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 53,  'Incident Level', #Population group: Cities and counties 10,000-24,999
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 54,  'Incident Level', #Population group: Cities and counties under 10,000
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 55,  'Incident Level', #Population group: State police
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 56,  'Incident Level', #Population group: Possessions and Canal Zone
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 57,  'Incident Level', #Agency indicator: City
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 58,  'Incident Level', #Agency indicator: County
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 59,  'Incident Level', #Agency indicator: University or college
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 60,  'Incident Level', #Agency indicator: State police
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 61,  'Incident Level', #Agency indicator: Other state agencies
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 62,  'Incident Level', #Agency indicator: Tribal agencies
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 63,  'Incident Level', #Agency indicator: Federal agencies
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 64,  'Incident Level', #Clearance: Not cleared
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 65,  'Incident Level', #Clearance: Cleared through arrest
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 66,  'Incident Level', #Clearance: Exceptional clearance
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 67,  'Incident Level subset to exceptional clearance', #Clearance: Death of offender
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 68,  'Incident Level subset to exceptional clearance', #Clearance: Prosecution declined
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 69,  'Incident Level subset to exceptional clearance', #Clearance: In custody of other jurisdiction
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 70,  'Incident Level subset to exceptional clearance', #Clearance: Victim refused to cooperate
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 71,  'Incident Level subset to exceptional clearance', #Clearance: Juvenile/no custody
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 72,  'Incident Level', #Property loss: None
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 73,  'Incident Level', #Property loss: Burned
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 74,  'Incident Level', #Property loss: Counterfeited/forged
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 75,  'Incident Level', #Property loss: Destroyed/damaged/vandalized
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 76,  'Incident Level', #Property loss: Recovered
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 77,  'Incident Level', #Property loss: Seized
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 78,  'Incident Level', #Property loss: Stolen/Et
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 79, 'Incident Level', #Property loss: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 80, 'Incident Level', #MSA: MSA Counties
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 81, 'Incident Level', #MSA: Outside MSA
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 82, 'Incident Level', #MSA: Non-MSA Counties
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 83, 'Incident Level', #MSA: Missing

trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 84, 'Incident Level', #Location type 2: Residence/hotel
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 85, 'Incident Level', #Location type 2: Transportation hub/outdoor public locations
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 86, 'Incident Level', #Location type 2: Schools, daycares, and universities
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 87, 'Incident Level', #Location type 2: Retail/financial/other commercial establishment
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 88, 'Incident Level', #Location type 2: Restaurant/bar/sports or entertainment venue
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 89, 'Incident Level', #Location type 2: Religious buildings
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 90, 'Incident Level', #Location type 2: Government/public buildings
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 91, 'Incident Level', #Location type 2: Jail/prison
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 92, 'Incident Level', #Location type 2: Shelter-mission/homeless
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 93, 'Incident Level', #Location type 2: Drug Store/Doctor Office/Hospital
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 94, 'Incident Level', #Location type 2: Other/unknown location
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 95, 'Incident Level', #Victim-offender relationship 2: Intimate partner plus Family
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 96, 'Incident Level', #Victim-offender relationship 2: Outside family but known to victim
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 97, 'Incident Level', #Victim-offender relationship 2: Stranger
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 98, 'Incident Level', #Victim-offender relationship 2: Victim was Offender
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 99, 'Incident Level', #Victim-offender relationship 2: Unknown relationship

trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 100, 'Incident Level', #Location type 3: Residence
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 101, 'Incident Level' #Location type 3: Not residence


))

  return(returndata)
}

estimate_type_detail_rate_label <- function(indata){
  log_debug("Running estimate_type_detail_rate_label function")
  returndata <- indata %>%
    mutate(
      estimate_type_detail_rate = fcase(
trim_upcase(estimate_type) %in% c('RATE') & row == 1,  DER_NA_CODE_STRING, #Incident count
trim_upcase(estimate_type) %in% c('RATE') & row == 2,  'Incident rate per 100,000 persons', #Incident rate (per 100k total pop)
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
trim_upcase(estimate_type) %in% c('RATE') & row == 18,  DER_NA_CODE_STRING, #Multiple offense incident: 1 offense
trim_upcase(estimate_type) %in% c('RATE') & row == 19,  DER_NA_CODE_STRING, #Multiple offense incident: 2 offenses
trim_upcase(estimate_type) %in% c('RATE') & row == 20,  DER_NA_CODE_STRING, #Multiple offense incident: 3+ offenses
trim_upcase(estimate_type) %in% c('RATE') & row == 21,  DER_NA_CODE_STRING, #Victim-offender relationship: Intimate partner
trim_upcase(estimate_type) %in% c('RATE') & row == 22,  DER_NA_CODE_STRING, #Victim-offender relationship: Other family
trim_upcase(estimate_type) %in% c('RATE') & row == 23,  DER_NA_CODE_STRING, #Victim-offender relationship: Outside family but known to victim
trim_upcase(estimate_type) %in% c('RATE') & row == 24,  DER_NA_CODE_STRING, #Victim-offender relationship: Stranger
trim_upcase(estimate_type) %in% c('RATE') & row == 25,  DER_NA_CODE_STRING, #Victim-offender relationship: Victim was Offender
trim_upcase(estimate_type) %in% c('RATE') & row == 26,  DER_NA_CODE_STRING, #Victim-offender relationship: Unknown relationship
trim_upcase(estimate_type) %in% c('RATE') & row == 27,  DER_NA_CODE_STRING, #Location type: Residence/hotel
trim_upcase(estimate_type) %in% c('RATE') & row == 28,  DER_NA_CODE_STRING, #Location type: Transportation hub/outdoor public locations
trim_upcase(estimate_type) %in% c('RATE') & row == 29,  DER_NA_CODE_STRING, #Location type: Schools, daycares, and universities
trim_upcase(estimate_type) %in% c('RATE') & row == 30,  DER_NA_CODE_STRING, #Location type: Retail/financial/other commercial establishment
trim_upcase(estimate_type) %in% c('RATE') & row == 31,  DER_NA_CODE_STRING, #Location type: Restaurant/bar/sports or entertainment venue
trim_upcase(estimate_type) %in% c('RATE') & row == 32,  DER_NA_CODE_STRING, #Location type: Religious buildings
trim_upcase(estimate_type) %in% c('RATE') & row == 33,  DER_NA_CODE_STRING, #Location type: Government/public buildings
trim_upcase(estimate_type) %in% c('RATE') & row == 34,  DER_NA_CODE_STRING, #Location type: Jail/prison
trim_upcase(estimate_type) %in% c('RATE') & row == 35,  DER_NA_CODE_STRING, #Location type: Shelter-mission/homeless
trim_upcase(estimate_type) %in% c('RATE') & row == 36,  DER_NA_CODE_STRING, #Location type: Other/unknown location
trim_upcase(estimate_type) %in% c('RATE') & row == 37,  DER_NA_CODE_STRING, #Time of day- Incident time: Midnight-4am
trim_upcase(estimate_type) %in% c('RATE') & row == 38,  DER_NA_CODE_STRING, #Time of day- Incident time: 4-8am
trim_upcase(estimate_type) %in% c('RATE') & row == 39,  DER_NA_CODE_STRING, #Time of day- Incident time: 8am-noon
trim_upcase(estimate_type) %in% c('RATE') & row == 40,  DER_NA_CODE_STRING, #Time of day- Incident time: Noon-4pm
trim_upcase(estimate_type) %in% c('RATE') & row == 41,  DER_NA_CODE_STRING, #Time of day- Incident time: 4-8pm
trim_upcase(estimate_type) %in% c('RATE') & row == 42,  DER_NA_CODE_STRING, #Time of day- Incident time: 8pm-midnight
trim_upcase(estimate_type) %in% c('RATE') & row == 43,  DER_NA_CODE_STRING, #Time of day- Incident time: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 44,  DER_NA_CODE_STRING, #Time of day- Report time: Midnight-4am
trim_upcase(estimate_type) %in% c('RATE') & row == 45,  DER_NA_CODE_STRING, #Time of day- Report time: 4-8am
trim_upcase(estimate_type) %in% c('RATE') & row == 46,  DER_NA_CODE_STRING, #Time of day- Report time: 8am-noon
trim_upcase(estimate_type) %in% c('RATE') & row == 47,  DER_NA_CODE_STRING, #Time of day- Report time: Noon-4pm
trim_upcase(estimate_type) %in% c('RATE') & row == 48,  DER_NA_CODE_STRING, #Time of day- Report time: 4-8pm
trim_upcase(estimate_type) %in% c('RATE') & row == 49,  DER_NA_CODE_STRING, #Time of day- Report time: 8pm-midnight
trim_upcase(estimate_type) %in% c('RATE') & row == 50,  DER_NA_CODE_STRING, #Time of day- Report time: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 51,  DER_NA_CODE_STRING, #Population group: Cities and counties 100,000 or over
trim_upcase(estimate_type) %in% c('RATE') & row == 52,  DER_NA_CODE_STRING, #Population group: Cities and counties 25,000-99,999
trim_upcase(estimate_type) %in% c('RATE') & row == 53,  DER_NA_CODE_STRING, #Population group: Cities and counties 10,000-24,999
trim_upcase(estimate_type) %in% c('RATE') & row == 54,  DER_NA_CODE_STRING, #Population group: Cities and counties under 10,000
trim_upcase(estimate_type) %in% c('RATE') & row == 55,  DER_NA_CODE_STRING, #Population group: State police
trim_upcase(estimate_type) %in% c('RATE') & row == 56,  DER_NA_CODE_STRING, #Population group: Possessions and Canal Zone
trim_upcase(estimate_type) %in% c('RATE') & row == 57,  DER_NA_CODE_STRING, #Agency indicator: City
trim_upcase(estimate_type) %in% c('RATE') & row == 58,  DER_NA_CODE_STRING, #Agency indicator: County
trim_upcase(estimate_type) %in% c('RATE') & row == 59,  DER_NA_CODE_STRING, #Agency indicator: University or college
trim_upcase(estimate_type) %in% c('RATE') & row == 60,  DER_NA_CODE_STRING, #Agency indicator: State police
trim_upcase(estimate_type) %in% c('RATE') & row == 61,  DER_NA_CODE_STRING, #Agency indicator: Other state agencies
trim_upcase(estimate_type) %in% c('RATE') & row == 62,  DER_NA_CODE_STRING, #Agency indicator: Tribal agencies
trim_upcase(estimate_type) %in% c('RATE') & row == 63,  DER_NA_CODE_STRING, #Agency indicator: Federal agencies
trim_upcase(estimate_type) %in% c('RATE') & row == 64,  DER_NA_CODE_STRING, #Clearance: Not cleared
trim_upcase(estimate_type) %in% c('RATE') & row == 65,  DER_NA_CODE_STRING, #Clearance: Cleared through arrest
trim_upcase(estimate_type) %in% c('RATE') & row == 66,  DER_NA_CODE_STRING, #Clearance: Exceptional clearance
trim_upcase(estimate_type) %in% c('RATE') & row == 67,  DER_NA_CODE_STRING, #Clearance: Death of offender
trim_upcase(estimate_type) %in% c('RATE') & row == 68,  DER_NA_CODE_STRING, #Clearance: Prosecution declined
trim_upcase(estimate_type) %in% c('RATE') & row == 69,  DER_NA_CODE_STRING, #Clearance: In custody of other jurisdiction
trim_upcase(estimate_type) %in% c('RATE') & row == 70,  DER_NA_CODE_STRING, #Clearance: Victim refused to cooperate
trim_upcase(estimate_type) %in% c('RATE') & row == 71,  DER_NA_CODE_STRING, #Clearance: Juvenile/no custody
trim_upcase(estimate_type) %in% c('RATE') & row == 72,  DER_NA_CODE_STRING, #Property loss: None
trim_upcase(estimate_type) %in% c('RATE') & row == 73,  DER_NA_CODE_STRING, #Property loss: Burned
trim_upcase(estimate_type) %in% c('RATE') & row == 74,  DER_NA_CODE_STRING, #Property loss: Counterfeited/forged
trim_upcase(estimate_type) %in% c('RATE') & row == 75,  DER_NA_CODE_STRING, #Property loss: Destroyed/damaged/vandalized
trim_upcase(estimate_type) %in% c('RATE') & row == 76,  DER_NA_CODE_STRING, #Property loss: Recovered
trim_upcase(estimate_type) %in% c('RATE') & row == 77,  DER_NA_CODE_STRING, #Property loss: Seized
trim_upcase(estimate_type) %in% c('RATE') & row == 78,  DER_NA_CODE_STRING, #Property loss: Stolen/Et
trim_upcase(estimate_type) %in% c('RATE') & row == 79, DER_NA_CODE_STRING, #Property loss: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 80, DER_NA_CODE_STRING, #MSA: MSA Counties
trim_upcase(estimate_type) %in% c('RATE') & row == 81, DER_NA_CODE_STRING, #MSA: Outside MSA
trim_upcase(estimate_type) %in% c('RATE') & row == 82, DER_NA_CODE_STRING, #MSA: Non-MSA Counties
trim_upcase(estimate_type) %in% c('RATE') & row == 83, DER_NA_CODE_STRING, #MSA: Missing


trim_upcase(estimate_type) %in% c('RATE') & row == 84,  DER_NA_CODE_STRING, #Location type 2: Residence/hotel
trim_upcase(estimate_type) %in% c('RATE') & row == 85,  DER_NA_CODE_STRING, #Location type 2: Transportation hub/outdoor public locations
trim_upcase(estimate_type) %in% c('RATE') & row == 86,  DER_NA_CODE_STRING, #Location type 2: Schools, daycares, and universities
trim_upcase(estimate_type) %in% c('RATE') & row == 87,  DER_NA_CODE_STRING, #Location type 2: Retail/financial/other commercial establishment
trim_upcase(estimate_type) %in% c('RATE') & row == 88,  DER_NA_CODE_STRING, #Location type 2: Restaurant/bar/sports or entertainment venue
trim_upcase(estimate_type) %in% c('RATE') & row == 89,  DER_NA_CODE_STRING, #Location type 2: Religious buildings
trim_upcase(estimate_type) %in% c('RATE') & row == 90,  DER_NA_CODE_STRING, #Location type 2: Government/public buildings
trim_upcase(estimate_type) %in% c('RATE') & row == 91,  DER_NA_CODE_STRING, #Location type 2: Jail/prison
trim_upcase(estimate_type) %in% c('RATE') & row == 92,  DER_NA_CODE_STRING, #Location type 2: Shelter-mission/homeless
trim_upcase(estimate_type) %in% c('RATE') & row == 93,  DER_NA_CODE_STRING, #Location type 2: Drug Store/Doctor Office/Hospital
trim_upcase(estimate_type) %in% c('RATE') & row == 94,  DER_NA_CODE_STRING, #Location type 2: Other/unknown location
trim_upcase(estimate_type) %in% c('RATE') & row == 95,  DER_NA_CODE_STRING, #Victim-offender relationship 2: Intimate partner plus Family
trim_upcase(estimate_type) %in% c('RATE') & row == 96,  DER_NA_CODE_STRING, #Victim-offender relationship 2: Outside family but known to victim
trim_upcase(estimate_type) %in% c('RATE') & row == 97,  DER_NA_CODE_STRING, #Victim-offender relationship 2: Stranger
trim_upcase(estimate_type) %in% c('RATE') & row == 98,  DER_NA_CODE_STRING, #Victim-offender relationship 2: Victim was Offender
trim_upcase(estimate_type) %in% c('RATE') & row == 99,  DER_NA_CODE_STRING, #Victim-offender relationship 2: Unknown relationship

trim_upcase(estimate_type) %in% c('RATE') & row == 100,  DER_NA_CODE_STRING, #Location type 3: Residence
trim_upcase(estimate_type) %in% c('RATE') & row == 101,  DER_NA_CODE_STRING #Location type 3: Not residence


))

  return(returndata)

}


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
  main_filter <- maindata[eval(infilter), c("ori", "weight", "incident_id", filtervarsting), with = FALSE]
  #Deduplicate by Incident ID, and one instance of crime type
  main_filter <- main_filter[, .SD[1], by = c("ori", "incident_id", filtervarsting)]

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
  s3 <- agg_percent_by_incident_id(leftdata = main_filter, rightdata = agg_weapon_no_yes, var=der_weapon_no_yes, section=3)

  der_weapon_yes_denom <- s3[[1]] %>%
    filter(der_weapon_no_yes == 2) %>% #Yes response
    select(final_count) %>%
    as.double()

  #Weapon involved Categories
  s4 <- agg_percent_by_incident_id_CAA(leftdata = main_filter, rightdata = agg_weapon_yes_cat, var=der_weapon_yes_cat, section=4, denom=der_weapon_yes_denom)

  #Injury
  s5 <- agg_percent_by_incident_id(leftdata = main_filter, rightdata = agg_injury_no_yes, var=der_injury_no_yes, section=5)

  #Multiple victims
  s6 <- agg_percent_by_incident_id(leftdata = main_filter, rightdata = agg_victim_count_1_2_plus, var=der_victim_count, section=6)

  #Multiple offenders
  s7 <- agg_percent_by_incident_id(leftdata = main_filter, rightdata = agg_offender_count_1_2_plus, var=der_offender_count, section=7)

  #Multiple offense incident
  s8 <- agg_percent_by_incident_id(leftdata = main_filter, rightdata = agg_offense_count_1_2_3_plus, var=der_offense_count, section=8)

  #Victim-offender relationship
  s9 <- agg_percent_by_incident_id_CAA(leftdata = main_filter, rightdata = agg_relationship_cat, var=der_relationship, section=9, denom=der_total_denom)

  #Location type
  s10 <- agg_percent_by_incident_id_CAA(leftdata = main_filter, rightdata = agg_location_cat_1_10, var=der_location_1_10, section=10, denom=der_total_denom)

  #Time of day - Incident
  s11 <- agg_percent_by_incident_id(leftdata = main_filter, rightdata = agg_time_of_day_cat_incident, var=der_time_of_day_incident, section=11)

  #Time of day - Report
  s12 <- agg_percent_by_incident_id(leftdata = main_filter, rightdata = agg_time_of_day_cat_report, var=der_time_of_day_report, section=12)

  #Population group
  s13 <- agg_percent(leftdata = main_filter, rightdata = ori_population_group_cat, var=der_population_group, section=13, mergeby=c("ori"))
  
  #Agency indicator
  s14 <- agg_percent(leftdata = main_filter, rightdata = ori_agency_type_cat_1_7, var=der_agency_type_1_7, section=14, mergeby=c("ori"))
  
  #Clearance
  s15 <- agg_percent_by_incident_id(leftdata = main_filter, rightdata = agg_clearance_cat, var=der_clearance_cat, section=15)

  #Exceptional clearance
  s16 <- agg_percent_by_incident_id(leftdata = main_filter, rightdata = agg_exception_clearance_cat, var=der_exceptional_clearance, section=16)

  #Property loss
  s17 <- agg_percent_by_incident_id_CAA(leftdata = main_filter, rightdata = agg_property_loss, var=der_property_loss, section=17, denom=der_total_denom)

  #MSA indicator
  s18 <- agg_percent(leftdata = main_filter, rightdata = ori_msa_cat, var=der_msa, section=18, mergeby=c("ori"))
  
  #Location type 2
  s19 <- agg_percent_by_incident_id_CAA(leftdata = main_filter, rightdata = agg_location_cat_1_11, var=der_location_1_11, section=19, denom=der_total_denom)
  
  #Victim-offender relationship
  s20 <- agg_percent_by_incident_id_CAA(leftdata = main_filter, rightdata = agg_relationship_cat2_imp, var=der_relationship2, section=20, denom=der_total_denom)
  
  #Location type 3
  s21 <- agg_percent_by_incident_id_CAA(leftdata = main_filter, rightdata = agg_location_residence, var=der_location_residence, section=21, denom=der_total_denom)  
  
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
