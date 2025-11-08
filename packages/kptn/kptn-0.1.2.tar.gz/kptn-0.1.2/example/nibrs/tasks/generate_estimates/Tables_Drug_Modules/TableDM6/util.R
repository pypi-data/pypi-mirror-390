library(tidyverse)
library(openxlsx)
library(DBI)
library(DT)
library(lubridate)
library(data.table)


#Declare the final section and row number for the table
assign_row <- function(data){

  returndata <- data %>% mutate(

  row = fcase(
    section == 1,  1,
    section == 2,  2,
    der_location_1_10 %in% c(1:10),  der_location_1_10 + 2,
    der_time_of_day_incident %in% c(1:7),  der_time_of_day_incident + 12,
    der_time_of_day_report %in% c(1:7),  der_time_of_day_report + 19,
    der_population_group %in% c(1:5),  der_population_group + 26, #Drop category 6-Possessions and Canal Zone
    der_agency_type_1_7 %in% c(1:6),  der_agency_type_1_7 + 31, #Drop category 7-Federal agencies
    section == 8,  38,
    der_msa %in% c(1:4), der_msa + 38,
    der_location_1_11 %in% c(1:11), der_location_1_11 + 42
  )
  )

  return(returndata)
}

assign_section <- function(data){

  returndata <- data %>% mutate(

  section = fcase(
    row %in% c(1),  1,
    row %in% c(2),  2,
    row %in% c(3:12),  3,
    row %in% c(13:19),  4,
    row %in% c(20:26),  5,
    row %in% c(27:31),  6,
    row %in% c(32:37),  7,
    row %in% c(38),  8,
    row %in% c(39:42), 9,
    row %in% c(43:53), 10
  )
  )

  return(returndata)

}


#New add on code for labels
assign_labels <- function(data){

  returndata <- data %>% mutate(

  estimate_domain = fcase(

row == 1,  'Total Incident Counts per Activity',
row == 2,  'Total Incident Counts per Drug Category',
row == 3,  'Location type: Residence/hotel',
row == 4,  'Location type: Transportation hub/outdoor public locations',
row == 5,  'Location type: Schools, daycares, and universities',
row == 6,  'Location type: Retail/financial/other commercial establishment',
row == 7,  'Location type: Restaurant/bar/sports or entertainment venue',
row == 8,  'Location type: Religious buildings',
row == 9,  'Location type: Government/public buildings',
row == 10,  'Location type: Jail/prison',
row == 11,  'Location type: Shelter-mission/homeless',
row == 12,  'Location type: Other/unknown location',
row == 13,  'Time of day- Incident time: Midnight-4am',
row == 14,  'Time of day- Incident time: 4-8am',
row == 15,  'Time of day- Incident time: 8am-noon',
row == 16,  'Time of day- Incident time: Noon-4pm',
row == 17,  'Time of day- Incident time: 4-8pm',
row == 18,  'Time of day- Incident time: 8pm-midnight',
row == 19,  'Time of day- Incident time: Unknown',
row == 20,  'Time of day- Report time: Midnight-4am',
row == 21,  'Time of day- Report time: 4-8am',
row == 22,  'Time of day- Report time: 8am-noon',
row == 23,  'Time of day- Report time: Noon-4pm',
row == 24,  'Time of day- Report time: 4-8pm',
row == 25,  'Time of day- Report time: 8pm-midnight',
row == 26,  'Time of day- Report time: Unknown',
row == 27,  'Population group: Cities and counties 100,000 or over',
row == 28,  'Population group: Cities and counties 25,000-99,999',
row == 29,  'Population group: Cities and counties 10,000-24,999',
row == 30,  'Population group: Cities and counties under 10,000',
row == 31,  'Population group: State police',
row == 32,  'Agency indicator: City',
row == 33,  'Agency indicator: County',
row == 34,  'Agency indicator: University or college',
row == 35,  'Agency indicator: State police',
row == 36,  'Agency indicator: Other state agencies',
row == 37,  'Agency indicator: Tribal agencies',
row == 38,  'Total: Total',
row == 39, 'MSA: MSA Counties',
row == 40, 'MSA: Outside MSA',
row == 41, 'MSA: Non-MSA Counties',
row == 42, 'MSA: Missing',

row == 43, 'Location type 2: Residence/hotel',
row == 44, 'Location type 2: Transportation hub/outdoor public locations',
row == 45, 'Location type 2: Schools, daycares, and universities',
row == 46, 'Location type 2: Retail/financial/other commercial establishment',
row == 47, 'Location type 2: Restaurant/bar/sports or entertainment venue',
row == 48, 'Location type 2: Religious buildings',
row == 49, 'Location type 2: Government/public buildings',
row == 50, 'Location type 2: Jail/prison',
row == 51, 'Location type 2: Shelter-mission/homeless',
row == 52, 'Location type 2: Drug Store/Doctor Office/Hospital',
row == 53, 'Location type 2: Other/unknown location'




  ),

  indicator_name = fcase(

column == 1,  '35A - Cocaine/Crack Cocaine (A,B) - B (Buying/Receiving)',
column == 2,  '35A - Cocaine/Crack Cocaine (A,B) - C (Cultivating/Manufacturing/Publishing)',
column == 3,  '35A - Cocaine/Crack Cocaine (A,B) - D (Distributing/Selling)',
column == 4,  '35A - Cocaine/Crack Cocaine (A,B) - P (Possessing/Concealing)',
column == 5,  '35A - Cocaine/Crack Cocaine (A,B) - T (Transporting/transmitting/importing)',
column == 6,  '35A - Cocaine/Crack Cocaine (A,B) - U (Using/consuming)',
column == 7,  '35A - Marijuana/Hashish (C,E) - B (Buying/Receiving)',
column == 8,  '35A - Marijuana/Hashish (C,E) - C (Cultivating/Manufacturing/Publishing)',
column == 9,  '35A - Marijuana/Hashish (C,E) - D (Distributing/Selling)',
column == 10,  '35A - Marijuana/Hashish (C,E) - P (Possessing/Concealing)',
column == 11,  '35A - Marijuana/Hashish (C,E) - T (Transporting/transmitting/importing)',
column == 12,  '35A - Marijuana/Hashish (C,E) - U (Using/consuming)',
column == 13,  '35A - Opiate/Narcotic (D,F,G,H) - B (Buying/Receiving)',
column == 14,  '35A - Opiate/Narcotic (D,F,G,H) - C (Cultivating/Manufacturing/Publishing)',
column == 15,  '35A - Opiate/Narcotic (D,F,G,H) - D (Distributing/Selling)',
column == 16,  '35A - Opiate/Narcotic (D,F,G,H) - P (Possessing/Concealing)',
column == 17,  '35A - Opiate/Narcotic (D,F,G,H) - T (Transporting/transmitting/importing)',
column == 18,  '35A - Opiate/Narcotic (D,F,G,H) - U (Using/consuming)',
column == 19,  '35A - Hallucinogen (I,J,K) - B (Buying/Receiving)',
column == 20,  '35A - Hallucinogen (I,J,K) - C (Cultivating/Manufacturing/Publishing)',
column == 21,  '35A - Hallucinogen (I,J,K) - D (Distributing/Selling)',
column == 22,  '35A - Hallucinogen (I,J,K) - P (Possessing/Concealing)',
column == 23,  '35A - Hallucinogen (I,J,K) - T (Transporting/transmitting/importing)',
column == 24,  '35A - Hallucinogen (I,J,K) - U (Using/consuming)',
column == 25,  '35A - Stimulant (L,M) - B (Buying/Receiving)',
column == 26,  '35A - Stimulant (L,M) - C (Cultivating/Manufacturing/Publishing)',
column == 27,  '35A - Stimulant (L,M) - D (Distributing/Selling)',
column == 28,  '35A - Stimulant (L,M) - P (Possessing/Concealing)',
column == 29,  '35A - Stimulant (L,M) - T (Transporting/transmitting/importing)',
column == 30,  '35A - Stimulant (L,M) - U (Using/consuming)',
column == 31,  '35A - Depressant (N,O) - B (Buying/Receiving)',
column == 32,  '35A - Depressant (N,O) - C (Cultivating/Manufacturing/Publishing)',
column == 33,  '35A - Depressant (N,O) - D (Distributing/Selling)',
column == 34,  '35A - Depressant (N,O) - P (Possessing/Concealing)',
column == 35,  '35A - Depressant (N,O) - T (Transporting/transmitting/importing)',
column == 36,  '35A - Depressant (N,O) - U (Using/consuming)',
column == 37,  '35A - Other Drug Type (P) - B (Buying/Receiving)',
column == 38,  '35A - Other Drug Type (P) - C (Cultivating/Manufacturing/Publishing)',
column == 39,  '35A - Other Drug Type (P) - D (Distributing/Selling)',
column == 40,  '35A - Other Drug Type (P) - P (Possessing/Concealing)',
column == 41,  '35A - Other Drug Type (P) - T (Transporting/transmitting/importing)',
column == 42,  '35A - Other Drug Type (P) - U (Using/consuming)',
column == 43,  '35A - Unknown Drug Type (U) - B (Buying/Receiving)',
column == 44,  '35A - Unknown Drug Type (U) - C (Cultivating/Manufacturing/Publishing)',
column == 45,  '35A - Unknown Drug Type (U) - D (Distributing/Selling)',
column == 46,  '35A - Unknown Drug Type (U) - P (Possessing/Concealing)',
column == 47,  '35A - Unknown Drug Type (U) - T (Transporting/transmitting/importing)',
column == 48,  '35A - Unknown Drug Type (U) - U (Using/consuming)',
column == 49,  '35A - More Than 3 Types (X) - B (Buying/Receiving)',
column == 50,  '35A - More Than 3 Types (X) - C (Cultivating/Manufacturing/Publishing)',
column == 51,  '35A - More Than 3 Types (X) - D (Distributing/Selling)',
column == 52,  '35A - More Than 3 Types (X) - P (Possessing/Concealing)',
column == 53,  '35A - More Than 3 Types (X) - T (Transporting/transmitting/importing)',
column == 54,  '35A - More Than 3 Types (X) - U (Using/consuming)'



  ),

  full_table = "TableDM6 - Drug Count by Activity",
  table = DER_TABLE_NAME
  )

  return(returndata)

}

estimate_type_detail_percentage_label <- function(indata){

  returndata <- indata %>%
    mutate(
      estimate_type_detail_percentage = fcase(

trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 1,  'Incident Level', #Total Incident Counts per Activity
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 2,  'Incident Level', #Total Incident Counts per Drug Category
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 3,  'Incident Level', #Location type: Residence/hotel
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 4,  'Incident Level', #Location type: Transportation hub/outdoor public locations
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 5,  'Incident Level', #Location type: Schools, daycares, and universities
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 6,  'Incident Level', #Location type: Retail/financial/other commercial establishment
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 7,  'Incident Level', #Location type: Restaurant/bar/sports or entertainment venue
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 8,  'Incident Level', #Location type: Religious buildings
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 9,  'Incident Level', #Location type: Government/public buildings
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 10,  'Incident Level', #Location type: Jail/prison
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 11,  'Incident Level', #Location type: Shelter-mission/homeless
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 12,  'Incident Level', #Location type: Other/unknown location
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 13,  'Incident Level', #Time of day- Incident time: Midnight-4am
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 14,  'Incident Level', #Time of day- Incident time: 4-8am
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 15,  'Incident Level', #Time of day- Incident time: 8am-noon
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 16,  'Incident Level', #Time of day- Incident time: Noon-4pm
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 17,  'Incident Level', #Time of day- Incident time: 4-8pm
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 18,  'Incident Level', #Time of day- Incident time: 8pm-midnight
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 19,  'Incident Level', #Time of day- Incident time: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 20,  'Incident Level', #Time of day- Report time: Midnight-4am
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 21,  'Incident Level', #Time of day- Report time: 4-8am
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 22,  'Incident Level', #Time of day- Report time: 8am-noon
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 23,  'Incident Level', #Time of day- Report time: Noon-4pm
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 24,  'Incident Level', #Time of day- Report time: 4-8pm
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 25,  'Incident Level', #Time of day- Report time: 8pm-midnight
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 26,  'Incident Level', #Time of day- Report time: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 27,  'Incident Level', #Population group: Cities and counties 100,000 or over
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 28,  'Incident Level', #Population group: Cities and counties 25,000-99,999
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 29,  'Incident Level', #Population group: Cities and counties 10,000-24,999
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 30,  'Incident Level', #Population group: Cities and counties under 10,000
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 31,  'Incident Level', #Population group: State police
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 32,  'Incident Level', #Agency indicator: City
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 33,  'Incident Level', #Agency indicator: County
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 34,  'Incident Level', #Agency indicator: University or college
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 35,  'Incident Level', #Agency indicator: State police
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 36,  'Incident Level', #Agency indicator: Other state agencies
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 37,  'Incident Level', #Agency indicator: Tribal agencies
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 38,  'Incident Level', #Total: Total
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 39, 'Incident Level', #MSA: MSA Counties
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 40, 'Incident Level', #MSA: Outside MSA
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 41, 'Incident Level', #MSA: Non-MSA Counties
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 42, 'Incident Level', #MSA: Missing

trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 43, 'Incident Level', #Location type 2: Residence/hotel
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 44, 'Incident Level', #Location type 2: Transportation hub/outdoor public locations
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 45, 'Incident Level', #Location type 2: Schools, daycares, and universities
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 46, 'Incident Level', #Location type 2: Retail/financial/other commercial establishment
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 47, 'Incident Level', #Location type 2: Restaurant/bar/sports or entertainment venue
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 48, 'Incident Level', #Location type 2: Religious buildings
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 49, 'Incident Level', #Location type 2: Government/public buildings
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 50, 'Incident Level', #Location type 2: Jail/prison
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 51, 'Incident Level', #Location type 2: Shelter-mission/homeless
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 52, 'Incident Level', #Location type 2: Drug Store/Doctor Office/Hospital
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 53, 'Incident Level' #Location type 2: Other/unknown location


))

  return(returndata)
}

estimate_type_detail_rate_label <- function(indata){

  returndata <- indata %>%
    mutate(
      estimate_type_detail_rate = fcase(

trim_upcase(estimate_type) %in% c('RATE') & row == 1,  DER_NA_CODE_STRING, #Total Incident Counts per Activity
trim_upcase(estimate_type) %in% c('RATE') & row == 2,  DER_NA_CODE_STRING, #Total Incident Counts per Drug Category
trim_upcase(estimate_type) %in% c('RATE') & row == 3,  DER_NA_CODE_STRING, #Location type: Residence/hotel
trim_upcase(estimate_type) %in% c('RATE') & row == 4,  DER_NA_CODE_STRING, #Location type: Transportation hub/outdoor public locations
trim_upcase(estimate_type) %in% c('RATE') & row == 5,  DER_NA_CODE_STRING, #Location type: Schools, daycares, and universities
trim_upcase(estimate_type) %in% c('RATE') & row == 6,  DER_NA_CODE_STRING, #Location type: Retail/financial/other commercial establishment
trim_upcase(estimate_type) %in% c('RATE') & row == 7,  DER_NA_CODE_STRING, #Location type: Restaurant/bar/sports or entertainment venue
trim_upcase(estimate_type) %in% c('RATE') & row == 8,  DER_NA_CODE_STRING, #Location type: Religious buildings
trim_upcase(estimate_type) %in% c('RATE') & row == 9,  DER_NA_CODE_STRING, #Location type: Government/public buildings
trim_upcase(estimate_type) %in% c('RATE') & row == 10,  DER_NA_CODE_STRING, #Location type: Jail/prison
trim_upcase(estimate_type) %in% c('RATE') & row == 11,  DER_NA_CODE_STRING, #Location type: Shelter-mission/homeless
trim_upcase(estimate_type) %in% c('RATE') & row == 12,  DER_NA_CODE_STRING, #Location type: Other/unknown location
trim_upcase(estimate_type) %in% c('RATE') & row == 13,  DER_NA_CODE_STRING, #Time of day- Incident time: Midnight-4am
trim_upcase(estimate_type) %in% c('RATE') & row == 14,  DER_NA_CODE_STRING, #Time of day- Incident time: 4-8am
trim_upcase(estimate_type) %in% c('RATE') & row == 15,  DER_NA_CODE_STRING, #Time of day- Incident time: 8am-noon
trim_upcase(estimate_type) %in% c('RATE') & row == 16,  DER_NA_CODE_STRING, #Time of day- Incident time: Noon-4pm
trim_upcase(estimate_type) %in% c('RATE') & row == 17,  DER_NA_CODE_STRING, #Time of day- Incident time: 4-8pm
trim_upcase(estimate_type) %in% c('RATE') & row == 18,  DER_NA_CODE_STRING, #Time of day- Incident time: 8pm-midnight
trim_upcase(estimate_type) %in% c('RATE') & row == 19,  DER_NA_CODE_STRING, #Time of day- Incident time: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 20,  DER_NA_CODE_STRING, #Time of day- Report time: Midnight-4am
trim_upcase(estimate_type) %in% c('RATE') & row == 21,  DER_NA_CODE_STRING, #Time of day- Report time: 4-8am
trim_upcase(estimate_type) %in% c('RATE') & row == 22,  DER_NA_CODE_STRING, #Time of day- Report time: 8am-noon
trim_upcase(estimate_type) %in% c('RATE') & row == 23,  DER_NA_CODE_STRING, #Time of day- Report time: Noon-4pm
trim_upcase(estimate_type) %in% c('RATE') & row == 24,  DER_NA_CODE_STRING, #Time of day- Report time: 4-8pm
trim_upcase(estimate_type) %in% c('RATE') & row == 25,  DER_NA_CODE_STRING, #Time of day- Report time: 8pm-midnight
trim_upcase(estimate_type) %in% c('RATE') & row == 26,  DER_NA_CODE_STRING, #Time of day- Report time: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 27,  DER_NA_CODE_STRING, #Population group: Cities and counties 100,000 or over
trim_upcase(estimate_type) %in% c('RATE') & row == 28,  DER_NA_CODE_STRING, #Population group: Cities and counties 25,000-99,999
trim_upcase(estimate_type) %in% c('RATE') & row == 29,  DER_NA_CODE_STRING, #Population group: Cities and counties 10,000-24,999
trim_upcase(estimate_type) %in% c('RATE') & row == 30,  DER_NA_CODE_STRING, #Population group: Cities and counties under 10,000
trim_upcase(estimate_type) %in% c('RATE') & row == 31,  DER_NA_CODE_STRING, #Population group: State police
trim_upcase(estimate_type) %in% c('RATE') & row == 32,  DER_NA_CODE_STRING, #Agency indicator: City
trim_upcase(estimate_type) %in% c('RATE') & row == 33,  DER_NA_CODE_STRING, #Agency indicator: County
trim_upcase(estimate_type) %in% c('RATE') & row == 34,  DER_NA_CODE_STRING, #Agency indicator: University or college
trim_upcase(estimate_type) %in% c('RATE') & row == 35,  DER_NA_CODE_STRING, #Agency indicator: State police
trim_upcase(estimate_type) %in% c('RATE') & row == 36,  DER_NA_CODE_STRING, #Agency indicator: Other state agencies
trim_upcase(estimate_type) %in% c('RATE') & row == 37,  DER_NA_CODE_STRING, #Agency indicator: Tribal agencies
trim_upcase(estimate_type) %in% c('RATE') & row == 38,  DER_NA_CODE_STRING, #Total: Total
trim_upcase(estimate_type) %in% c('RATE') & row == 39, DER_NA_CODE_STRING, #MSA: MSA Counties
trim_upcase(estimate_type) %in% c('RATE') & row == 40, DER_NA_CODE_STRING, #MSA: Outside MSA
trim_upcase(estimate_type) %in% c('RATE') & row == 41, DER_NA_CODE_STRING, #MSA: Non-MSA Counties
trim_upcase(estimate_type) %in% c('RATE') & row == 42, DER_NA_CODE_STRING, #MSA: Missing

trim_upcase(estimate_type) %in% c('RATE') & row == 43, DER_NA_CODE_STRING, #Location type 2: Residence/hotel
trim_upcase(estimate_type) %in% c('RATE') & row == 44, DER_NA_CODE_STRING, #Location type 2: Transportation hub/outdoor public locations
trim_upcase(estimate_type) %in% c('RATE') & row == 45, DER_NA_CODE_STRING, #Location type 2: Schools, daycares, and universities
trim_upcase(estimate_type) %in% c('RATE') & row == 46, DER_NA_CODE_STRING, #Location type 2: Retail/financial/other commercial establishment
trim_upcase(estimate_type) %in% c('RATE') & row == 47, DER_NA_CODE_STRING, #Location type 2: Restaurant/bar/sports or entertainment venue
trim_upcase(estimate_type) %in% c('RATE') & row == 48, DER_NA_CODE_STRING, #Location type 2: Religious buildings
trim_upcase(estimate_type) %in% c('RATE') & row == 49, DER_NA_CODE_STRING, #Location type 2: Government/public buildings
trim_upcase(estimate_type) %in% c('RATE') & row == 50, DER_NA_CODE_STRING, #Location type 2: Jail/prison
trim_upcase(estimate_type) %in% c('RATE') & row == 51, DER_NA_CODE_STRING, #Location type 2: Shelter-mission/homeless
trim_upcase(estimate_type) %in% c('RATE') & row == 52, DER_NA_CODE_STRING, #Location type 2: Drug Store/Doctor Office/Hospital
trim_upcase(estimate_type) %in% c('RATE') & row == 53, DER_NA_CODE_STRING #Location type 2: Other/unknown location


))

  return(returndata)

}

#This function will calculate the counts and percentage one column at a time

generate_est <- function(maindata, subsetvareq1, subsetvareq2, column_number){

  #Filter the data for the table
  maindata <- maindata %>%
    #Filter to drug/narcotic violations (35A)
    #der_drug_narcotic_any == 1 & der_drug_equipment_any == 1 ~ 3, #Both drug/narcotic and drug equipment violations
    #der_drug_narcotic_any == 1 ~ 1, #Only drug/narcotic violations
    #Note this variable contains completed offenses
    filter(der_drug_narcotic_equipment_cat %in% c(1,3)) %>%
    #Filter to non-missing activity
    filter(!is.na(der_1suspected_type_of_drug_1crim_activity)) %>%
	#Filter to activities on table
	filter(der_1suspected_type_of_drug_1crim_activity %in% c(
	1, 2, 3, 6, 7, 8,
	9, 10, 11, 14, 15, 16,
	17, 18, 19, 22, 23, 24,
	25, 26, 27, 30, 31, 32,
	33, 34, 35, 38, 39, 40,
	41, 42, 43, 46, 47, 48,
	49, 50, 51, 54, 55, 56,
	57, 58, 59, 62, 63, 64,
	65, 66, 67, 70, 71, 72))



  #Get only one incident for all drug
  s1 <- vector("list", 2)
  #For Table
  s1[[1]] <- maindata %>%
    #Deduplicate by Incident ID
    group_by(ori, incident_id) %>%
    mutate(raw_first = row_number() == 1 ) %>%
    ungroup() %>%
    filter(raw_first == TRUE) %>%
    select(-raw_first) %>%
    mutate(weighted_count = weight *one) %>%
    summarise(final_count = sum(weighted_count)) %>%
    mutate(section = 1)
  #For ORI level - Need unweighted counts
  s1[[2]] <- maindata %>%
    #Deduplicate by Incident ID
    group_by(ori, incident_id) %>%
    mutate(raw_first = row_number() == 1 ) %>%
    ungroup() %>%
    filter(raw_first == TRUE) %>%
    select(-raw_first) %>%
    group_by(ori) %>%
    summarise(final_count = sum(one)) %>%
    ungroup() %>%
    mutate(section = 1)


  #Get only one incident per drug category
  #Note parameter subsetvareq2 contains the code to subset to the specific drug and activity
  s2 <- vector("list", 2)
  #For Table
  s2[[1]] <- maindata %>%
    #Dedepulicate by subsetvareq2 contains the code to subset to the specific drug and activity
    filter(!!(subsetvareq2 %>% rlang:::parse_expr())  ) %>%
    #Deduplicate by Incident ID
    group_by(ori, incident_id) %>%
    mutate(raw_first = row_number() == 1 ) %>%
    ungroup() %>%
    filter(raw_first == TRUE) %>%
    select(-raw_first) %>%
    mutate(weighted_count = weight *one) %>%
    summarise(final_count = sum(weighted_count)) %>%
    mutate(section = 2)

  #For ORI level - Need unweighted counts
  s2[[2]] <- maindata %>%
    #Dedepulicate by subsetvareq2 contains the code to subset to the specific drug and activity
    filter(!!(subsetvareq2 %>% rlang:::parse_expr())  ) %>%
    #Deduplicate by Incident ID
    group_by(ori, incident_id) %>%
    mutate(raw_first = row_number() == 1 ) %>%
    ungroup() %>%
    filter(raw_first == TRUE) %>%
    select(-raw_first) %>%
    group_by(ori) %>%
    summarise(final_count = sum(one)) %>%
    ungroup() %>%
    mutate(section = 2)


  #Declare the variable for the column subset
  #filtervarsting <- subsetvareq1

  #Make the var into a symbol
  #infiltervar <- filtervarsting %>% rlang:::parse_expr()

  #Create the incidicator filter
  #infilter <- paste0(filtervarsting," == 1") %>% rlang:::parse_expr()

  #Create the column variable
  columnnum <- column_number
  incolumn_count <- paste0("final_count_", columnnum) %>% rlang:::parse_expr()
  incolumn_percentage <- paste0("percent_", columnnum) %>% rlang:::parse_expr()

#Get the totals - object will be the last section s8
  s8 <- vector("list", 2)
  #For Table
  s8[[1]] <- maindata %>%
    ############################################
    #Subset to specific column in table
    filter(!!(subsetvareq1 %>% rlang:::parse_expr()) ) %>%
    #Deduplicate by Incident ID
    group_by(ori, incident_id) %>%
    mutate(raw_first = row_number() == 1 ) %>%
    ungroup() %>%
    filter(raw_first == TRUE) %>%
    select(-raw_first) %>%
    mutate(weighted_count = weight *one) %>%
    summarise(final_count = sum(weighted_count)) %>%
    mutate(section = 8)
  #For ORI level - Need unweighted counts
  s8[[2]] <- maindata %>%
    ############################################
    #Subset to specific column in table
    filter(!!(subsetvareq1 %>% rlang:::parse_expr()) ) %>%
    #Deduplicate by Incident ID
    group_by(ori, incident_id) %>%
    mutate(raw_first = row_number() == 1 ) %>%
    ungroup() %>%
    filter(raw_first == TRUE) %>%
    select(-raw_first) %>%
    group_by(ori) %>%
    summarise(final_count = sum(one)) %>%
    ungroup() %>%
    mutate(section = 8)


  #Filter the dataset
  main_filter <- maindata %>%
    ############################################
    #Subset to specific column in table
    filter(!!(subsetvareq1 %>% rlang:::parse_expr()) ) %>%
    #Deduplicate by Incident ID, and one instance of crime type
    group_by(ori, incident_id) %>%
    mutate(raw_first = row_number() == 1 ) %>%
    ungroup() %>%
    filter(raw_first == TRUE) %>%
    select(-raw_first) %>%

    select(ori, weight, incident_id)


  #Total Denominator
  der_total_denom <- s8[[1]] %>% select(final_count) %>% as.double()

  #Location type
  s3 <- agg_percent_by_incident_id_CAA(leftdata = main_filter, rightdata = agg_location_cat_1_10, var=der_location_1_10, section=3, denom=der_total_denom)

  #Time of day - Incident
  s4 <- agg_percent_by_incident_id(leftdata = main_filter, rightdata = agg_time_of_day_cat_incident, var=der_time_of_day_incident, section=4)

  #Time of day - Report
  s5 <- agg_percent_by_incident_id(leftdata = main_filter, rightdata = agg_time_of_day_cat_report, var=der_time_of_day_report, section=5)

  #Population group
  s6 <- agg_percent(leftdata = main_filter, rightdata = ori_population_group_cat, var=der_population_group, section=6, mergeby=c("ori"))
  
  #Agency indicator
  s7 <- agg_percent(leftdata = main_filter, rightdata = ori_agency_type_cat_1_7, var=der_agency_type_1_7, section=7, mergeby=c("ori"))
  
  #Section 8 is define above and is total row
  
  #MSA indicator
  s9 <- agg_percent(leftdata = main_filter, rightdata = ori_msa_cat, var=der_msa, section=9, mergeby=c("ori"))  
  
  #Location type 2
  s10 <- agg_percent_by_incident_id_CAA(leftdata = main_filter, rightdata = agg_location_cat_1_11, var=der_location_1_11, section=10, denom=der_total_denom)


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
    filter(!is.na(row)) %>%
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
           count    = final_count,

           percentage  =  DER_NA_CODE,
           rate     = DER_NA_CODE,
           population_estimate     = DER_NA_CODE) %>%
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