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
    der_location_1_10 %in% c(1:10),  der_location_1_10 + 2,
    der_time_of_day_incident %in% c(1:7),  der_time_of_day_incident + 12,
    der_time_of_day_report %in% c(1:7),  der_time_of_day_report + 19,
    der_population_group %in% c(1:6),  der_population_group + 26,
    der_agency_type_1_7 %in% c(1:7),  der_agency_type_1_7 + 32,
    der_clearance_cat_1_2 %in% c(1:2),  der_clearance_cat_1_2 + 39,
    der_gang_cat_no_yes %in% c(1:2),  der_gang_cat_no_yes + 41,
    der_msa %in% c(1:4), der_msa + 43,
    der_location_1_11 %in% c(1:11), der_location_1_11 + 47,
    der_location_residence %in% c(1:2), der_location_residence + 58, 
    der_cleared_cat_1_2 %in% c(1:2), der_cleared_cat_1_2 + 60    
    
    )



  )
  return(returndata)
}

assign_section <- function(data){
  log_debug("Running assign_section function")

  returndata <- data %>% mutate(

  section = fcase(
    row %in% c(1:2),  1,
    row %in% c(3:12),  2,
    row %in% c(13:19),  3,
    row %in% c(20:26),  4,
    row %in% c(27:32),  5,
    row %in% c(33:39),  6,
    row %in% c(40:41),  7,
    row %in% c(42:43),  8,
    row %in% c(44:47),  9,
    row %in% c(48:58),  10,
    row %in% c(59:60),  11,
    row %in% c(61:62),  12   
    
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
row == 32,  'Population group: Possessions and Canal Zone',
row == 33,  'Agency indicator: City',
row == 34,  'Agency indicator: County',
row == 35,  'Agency indicator: University or college',
row == 36,  'Agency indicator: State police',
row == 37,  'Agency indicator: Other state agencies',
row == 38,  'Agency indicator: Tribal agencies',
row == 39,  'Agency indicator: Federal agencies',
row == 40,  'Clearance: Not cleared through arrest',
row == 41,  'Clearance: Cleared through arrest',
row == 42,  'Gang Involvement: None/Unknown gang involvement',
row == 43,  'Gang Involvement: Juvenile or other gang',
row == 44,  'MSA: MSA Counties',
row == 45,  'MSA: Outside MSA',
row == 46,  'MSA: Non-MSA Counties',
row == 47,  'MSA: Missing',

row == 48, 'Location type 2: Residence/hotel',
row == 49, 'Location type 2: Transportation hub/outdoor public locations',
row == 50, 'Location type 2: Schools, daycares, and universities',
row == 51, 'Location type 2: Retail/financial/other commercial establishment',
row == 52, 'Location type 2: Restaurant/bar/sports or entertainment venue',
row == 53, 'Location type 2: Religious buildings',
row == 54, 'Location type 2: Government/public buildings',
row == 55, 'Location type 2: Jail/prison',
row == 56, 'Location type 2: Shelter-mission/homeless',
row == 57, 'Location type 2: Drug Store/Doctor Office/Hospital',
row == 58, 'Location type 2: Other/unknown location',

row == 59, 'Location type 3: Residence',
row == 60, 'Location type 3: Not residence',
row == 61, 'Clearance 2: Cleared incident',
row == 62, 'Clearance 2: Not cleared incident'


  ),

  indicator_name = fcase(

column == 1,  'NIBRS crimes against society (Total)',
column == 2,  'Animal Cruelty',
column == 3,  'Drug/Narcotic Offenses',
column == 4,  'Gambling Offenses',
column == 5,  'Pornography/Obscene Material',
column == 6,  'Prostitution Offenses',
column == 7,  'Weapon Law Violations',
column == 8, 'Import Violations',
column == 9, 'Export Violations',
column == 10, 'Federal Liquor Offenses',
column == 11, 'Federal Tobacco Offenses',
column == 12, 'Wildlife Trafficking',
column == 13, 'Espionage',
column == 14, 'Money Laundering',
column == 15, 'Harboring Escapee/Concealing from Arrest',
column == 16, 'Flight to Avoid Prosecution',
column == 17, 'Flight to Avoid Deportation',
column == 18, 'Illegal Entry into the United States',
column == 19, 'False Citizenship',
column == 20, 'Smuggling Aliens',
column == 21, 'Re-entry after Deportation',
column == 22, 'Failure to Register as a Sex Offender',
column == 23, 'Treason',
column == 24, 'Violation of National Firearm Act of 1934',
column == 25, 'Weapons of Mass Destruction',
column == 26, 'Explosives Violation',
column == 27, ' Drug Equipment Violations'



  ),

  full_table = "Table2c-Society Offenses",
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
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 3,  'Offense Level', #Location type: Residence/hotel
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 4,  'Offense Level', #Location type: Transportation hub/outdoor public locations
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 5,  'Offense Level', #Location type: Schools, daycares, and universities
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 6,  'Offense Level', #Location type: Retail/financial/other commercial establishment
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 7,  'Offense Level', #Location type: Restaurant/bar/sports or entertainment venue
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 8,  'Offense Level', #Location type: Religious buildings
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 9,  'Offense Level', #Location type: Government/public buildings
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 10,  'Offense Level', #Location type: Jail/prison
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 11,  'Offense Level', #Location type: Shelter-mission/homeless
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 12,  'Offense Level', #Location type: Other/unknown location
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 13,  'Offense Level', #Time of day- Incident time: Midnight-4am
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 14,  'Offense Level', #Time of day- Incident time: 4-8am
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 15,  'Offense Level', #Time of day- Incident time: 8am-noon
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 16,  'Offense Level', #Time of day- Incident time: Noon-4pm
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 17,  'Offense Level', #Time of day- Incident time: 4-8pm
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 18,  'Offense Level', #Time of day- Incident time: 8pm-midnight
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 19,  'Offense Level', #Time of day- Incident time: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 20,  'Offense Level', #Time of day- Report time: Midnight-4am
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 21,  'Offense Level', #Time of day- Report time: 4-8am
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 22,  'Offense Level', #Time of day- Report time: 8am-noon
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 23,  'Offense Level', #Time of day- Report time: Noon-4pm
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 24,  'Offense Level', #Time of day- Report time: 4-8pm
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 25,  'Offense Level', #Time of day- Report time: 8pm-midnight
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 26,  'Offense Level', #Time of day- Report time: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 27,  'Offense Level', #Population group: Cities and counties 100,000 or over
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 28,  'Offense Level', #Population group: Cities and counties 25,000-99,999
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 29,  'Offense Level', #Population group: Cities and counties 10,000-24,999
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 30,  'Offense Level', #Population group: Cities and counties under 10,000
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 31,  'Offense Level', #Population group: State police
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 32,  'Offense Level', #Population group: Possessions and Canal Zone
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 33,  'Offense Level', #Agency indicator: City
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 34,  'Offense Level', #Agency indicator: County
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 35,  'Offense Level', #Agency indicator: University or college
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 36,  'Offense Level', #Agency indicator: State police
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 37,  'Offense Level', #Agency indicator: Other state agencies
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 38,  'Offense Level', #Agency indicator: Tribal agencies
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 39,  'Offense Level', #Agency indicator: Federal agencies
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 40,  'Offense Level', #Clearance: Not cleared through arrest
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 41,  'Offense Level', #Clearance: Cleared through arrest
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 42,  'Offense Level', #Gang Involvement: None/Unknown gang involvement
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 43,  'Offense Level', #Gang Involvement: Juvenile or other gang
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 44, 'Offense Level', #MSA: MSA Counties
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 45, 'Offense Level', #MSA: Outside MSA
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 46, 'Offense Level', #MSA: Non-MSA Counties
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 47, 'Offense Level', #MSA: Missing

trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 48, 'Offense Level', #Location type 2: Residence/hotel
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 49, 'Offense Level', #Location type 2: Transportation hub/outdoor public locations
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 50, 'Offense Level', #Location type 2: Schools, daycares, and universities
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 51, 'Offense Level', #Location type 2: Retail/financial/other commercial establishment
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 52, 'Offense Level', #Location type 2: Restaurant/bar/sports or entertainment venue
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 53, 'Offense Level', #Location type 2: Religious buildings
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 54, 'Offense Level', #Location type 2: Government/public buildings
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 55, 'Offense Level', #Location type 2: Jail/prison
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 56, 'Offense Level', #Location type 2: Shelter-mission/homeless
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 57, 'Offense Level', #Location type 2: Drug Store/Doctor Office/Hospital
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 58, 'Offense Level', #Location type 2: Other/unknown location

trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 59, 'Offense Level', #Location type 3: Residence
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 60, 'Offense Level', #Location type 3: Not residence
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 61, 'Offense Level', #Clearance 2: Cleared incident
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 62, 'Offense Level' #Clearance 2: Not cleared incident


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
trim_upcase(estimate_type) %in% c('RATE') & row == 32,  DER_NA_CODE_STRING, #Population group: Possessions and Canal Zone
trim_upcase(estimate_type) %in% c('RATE') & row == 33,  DER_NA_CODE_STRING, #Agency indicator: City
trim_upcase(estimate_type) %in% c('RATE') & row == 34,  DER_NA_CODE_STRING, #Agency indicator: County
trim_upcase(estimate_type) %in% c('RATE') & row == 35,  DER_NA_CODE_STRING, #Agency indicator: University or college
trim_upcase(estimate_type) %in% c('RATE') & row == 36,  DER_NA_CODE_STRING, #Agency indicator: State police
trim_upcase(estimate_type) %in% c('RATE') & row == 37,  DER_NA_CODE_STRING, #Agency indicator: Other state agencies
trim_upcase(estimate_type) %in% c('RATE') & row == 38,  DER_NA_CODE_STRING, #Agency indicator: Tribal agencies
trim_upcase(estimate_type) %in% c('RATE') & row == 39,  DER_NA_CODE_STRING, #Agency indicator: Federal agencies
trim_upcase(estimate_type) %in% c('RATE') & row == 40,  DER_NA_CODE_STRING, #Clearance: Not cleared through arrest
trim_upcase(estimate_type) %in% c('RATE') & row == 41,  DER_NA_CODE_STRING, #Clearance: Cleared through arrest
trim_upcase(estimate_type) %in% c('RATE') & row == 42,  DER_NA_CODE_STRING, #Gang Involvement: None/Unknown gang involvement
trim_upcase(estimate_type) %in% c('RATE') & row == 43,  DER_NA_CODE_STRING, #Gang Involvement: Juvenile or other gang
trim_upcase(estimate_type) %in% c('RATE') & row == 44, DER_NA_CODE_STRING, #MSA: MSA Counties
trim_upcase(estimate_type) %in% c('RATE') & row == 45, DER_NA_CODE_STRING, #MSA: Outside MSA
trim_upcase(estimate_type) %in% c('RATE') & row == 46, DER_NA_CODE_STRING, #MSA: Non-MSA Counties
trim_upcase(estimate_type) %in% c('RATE') & row == 47, DER_NA_CODE_STRING, #MSA: Missing


trim_upcase(estimate_type) %in% c('RATE') & row == 48, DER_NA_CODE_STRING, #Location type 2: Residence/hotel
trim_upcase(estimate_type) %in% c('RATE') & row == 49, DER_NA_CODE_STRING, #Location type 2: Transportation hub/outdoor public locations
trim_upcase(estimate_type) %in% c('RATE') & row == 50, DER_NA_CODE_STRING, #Location type 2: Schools, daycares, and universities
trim_upcase(estimate_type) %in% c('RATE') & row == 51, DER_NA_CODE_STRING, #Location type 2: Retail/financial/other commercial establishment
trim_upcase(estimate_type) %in% c('RATE') & row == 52, DER_NA_CODE_STRING, #Location type 2: Restaurant/bar/sports or entertainment venue
trim_upcase(estimate_type) %in% c('RATE') & row == 53, DER_NA_CODE_STRING, #Location type 2: Religious buildings
trim_upcase(estimate_type) %in% c('RATE') & row == 54, DER_NA_CODE_STRING, #Location type 2: Government/public buildings
trim_upcase(estimate_type) %in% c('RATE') & row == 55, DER_NA_CODE_STRING, #Location type 2: Jail/prison
trim_upcase(estimate_type) %in% c('RATE') & row == 56, DER_NA_CODE_STRING, #Location type 2: Shelter-mission/homeless
trim_upcase(estimate_type) %in% c('RATE') & row == 57, DER_NA_CODE_STRING, #Location type 2: Drug Store/Doctor Office/Hospital
trim_upcase(estimate_type) %in% c('RATE') & row == 58, DER_NA_CODE_STRING, #Location type 2: Other/unknown location

trim_upcase(estimate_type) %in% c('RATE') & row == 59, DER_NA_CODE_STRING, #Location type 3: Residence
trim_upcase(estimate_type) %in% c('RATE') & row == 60, DER_NA_CODE_STRING, #Location type 3: Not residence
trim_upcase(estimate_type) %in% c('RATE') & row == 61, DER_NA_CODE_STRING, #Clearance 2: Cleared incident
trim_upcase(estimate_type) %in% c('RATE') & row == 62, DER_NA_CODE_STRING #Clearance 2: Not cleared incident



))

  return(returndata)

}



#This function will calculate the counts and percentage one column at a time

generate_est <- function(maindata, subsetvareq1, column_number){

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
  main_filter <- maindata[eval(infilter), c("ori", "weight", "incident_id", "offense_id", filtervarsting), with = FALSE]

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
           population_estimate = POP_TOTAL ) %>%
    mutate(section = 2)
  #For ORI level - Report totals - Need unweighted counts
  s2[[2]] <- main_filter %>%
    group_by(ori) %>%
    summarise(final_count = sum(!!infiltervar)) %>%
    ungroup() %>%
    mutate(section = 2)

  #Location type
  s3 <- agg_percent_CAA(leftdata = main_filter, rightdata = agg_location_cat_1_10_inc_offenses, var=der_location_1_10, section=3, mergeby=c( "incident_id", "offense_id"), denom=der_total_denom)

  #Time of day - Incident
  s4 <- agg_percent(leftdata = main_filter, rightdata = agg_time_of_day_cat_incident, var=der_time_of_day_incident, section=4, mergeby=c( "incident_id"))

  #Time of day - Report
  s5 <- agg_percent(leftdata = main_filter, rightdata = agg_time_of_day_cat_report, var=der_time_of_day_report, section=5, mergeby=c( "incident_id"))

  #Population group
  s6 <- agg_percent(leftdata = main_filter, rightdata = ori_population_group_cat, var=der_population_group, section=6, mergeby=c("ori"))
  
  #Agency indicator
  s7 <- agg_percent(leftdata = main_filter, rightdata = ori_agency_type_cat_1_7, var=der_agency_type_1_7, section=7, mergeby=c("ori"))
  
  #Clearance
  s8 <- agg_percent(leftdata = main_filter, rightdata = agg_clearance_cat_1_2, var=der_clearance_cat_1_2, section=8, mergeby=c( "incident_id"))
  
  #Gang Involvement
  s9 <- agg_percent(leftdata = main_filter, rightdata = agg_gang_cat_inc_offenses, 
                    var=der_gang_cat_no_yes, section=9, mergeby=c( "incident_id", "offense_id"))  
  
  #MSA indicator
  s10 <- agg_percent(leftdata = main_filter, rightdata = ori_msa_cat, var=der_msa, section=10, mergeby=c("ori"))  
  
  #Location type 2
  s11 <- agg_percent_CAA(leftdata = main_filter, rightdata = agg_location_cat_1_11_inc_offenses, var=der_location_1_11, section=11, mergeby=c( "incident_id", "offense_id"), denom=der_total_denom)

  
  #Location type
  s12 <- agg_percent_CAA(leftdata = main_filter, rightdata = agg_location_residence_inc_offenses, var=der_location_residence, section=12, mergeby=c( "incident_id", "offense_id"), denom=der_total_denom)
  
  #Clearance 2:  1 -2
  s13 <- agg_percent(leftdata = main_filter, rightdata = agg_cleared_cat_1_2, var=der_cleared_cat_1_2, section=13, mergeby=c( "incident_id"))  
  
  
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