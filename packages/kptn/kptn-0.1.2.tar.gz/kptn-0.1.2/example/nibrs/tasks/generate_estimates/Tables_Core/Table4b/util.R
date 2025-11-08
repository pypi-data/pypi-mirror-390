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
    der_arrest_type %in% c(1:3),  der_arrest_type + 1,
    der_arrestee_age_cat_15_17 %in% c(1:10),  der_arrestee_age_cat_15_17 + 4,
    der_arrestee_gender %in% c(1:3) ,  der_arrestee_gender + 14,
    der_arrestee_race %in% c(1:6),  der_arrestee_race + 17,

    #######Arrestee age 2###############################

    der_arrestee_age_cat_under18_2 %in% c(1:2), der_arrestee_age_cat_under18_2 + 23, ##Under 12, 12-17
    der_arrestee_age_cat_12_17_cat %in% c(1:2), der_arrestee_age_cat_12_17_cat + 25, #12-14, 15-17
    der_arrestee_age_cat_2_uo18 %in% c(2), 28, #2, #18+
    der_arrestee_age_cat_2_uo18 %in% c(3), 29, #3, #Unknown
    
    #Arrestee Hispanic Origin
    der_arrestee_ethnicity %in% c(1:3), der_arrestee_ethnicity + 29,
    
    #Arrestee race and Hispanic Origin
    der_arrestee_ethnicity_race %in% c(1:7), der_arrestee_ethnicity_race + 32     

    )
  )

  return(returndata)
}

assign_section <- function(data){
  log_debug("Running assign_section function")

  returndata <- data %>% mutate(

  section = fcase(
    row %in% c(1),  1,
    row %in% c(2:4),  2,
    row %in% c(5:14),  3,
    row %in% c(15:17),  4,
    row %in% c(18:23),  5,
    row %in% c(24:29),  6,
    row %in% c(30:32),  7,
    row %in% c(33:39),  8
    )
  )

  return(returndata)

}


#New add on code for labels
assign_labels <- function(data){
  log_debug("Running assign_labels function")

  returndata <- data %>% mutate(

  estimate_domain = fcase(

row == 1,  'Arrest rate (per 100k total population)',
row == 2,  'Arrest type-specific arrest rate: On-view arrest',
row == 3,  'Arrest type-specific arrest rate: Summoned/cited',
row == 4,  'Arrest type-specific arrest rate: Taken into custody',
row == 5,  'Age-specific arrest rate: Under 5',
row == 6,  'Age-specific arrest rate: 5-14',
row == 7,  'Age-specific arrest rate: 15',
row == 8,  'Age-specific arrest rate: 16',
row == 9,  'Age-specific arrest rate: 17',
row == 10,  'Age-specific arrest rate: 18-24',
row == 11,  'Age-specific arrest rate: 25-34',
row == 12,  'Age-specific arrest rate: 35-64',
row == 13,  'Age-specific arrest rate: 65+',
row == 14,  'Age-specific arrest rate: Unknown',
row == 15,  'Sex-specific arrest rate: Male',
row == 16,  'Sex-specific arrest rate: Female',
row == 17,  'Sex-specific arrest rate: Unknown',
row == 18,  'Race-specific arrest rate: White',
row == 19,  'Race-specific arrest rate: Black',
row == 20,  'Race-specific arrest rate: American Indian or Alaska Native',
row == 21,  'Race-specific arrest rate: Asian',
row == 22,  'Race-specific arrest rate: Native Hawaiian or Other Pacific Islander',
row == 23,  'Race-specific arrest rate: Unknown',

row == 24, 'Age-specific arrest rate 2: Under 12',
row == 25, 'Age-specific arrest rate 2: 12-17',
row == 26, 'Age-specific arrest rate 2: 12-14',
row == 27, 'Age-specific arrest rate 2: 15-17',
row == 28, 'Age-specific arrest rate 2: 18+',
row == 29, 'Age-specific arrest rate 2: Unknown',

row == 30, 'Hispanic Origin-specific arrest rate: Hispanic or Latino',
row == 31, 'Hispanic Origin-specific arrest rate: Not Hispanic or Latino',
row == 32, 'Hispanic Origin-specific arrest rate: Unknown',
row == 33, 'Race and Hispanic Origin-specific arrest rate: Hispanic or Latino',
row == 34, 'Race and Hispanic Origin-specific arrest rate: Non-Hispanic, White',
row == 35, 'Race and Hispanic Origin-specific arrest rate: Non-Hispanic, Black',
row == 36, 'Race and Hispanic Origin-specific arrest rate: Non-Hispanic, American Indian or Alaska Native',
row == 37, 'Race and Hispanic Origin-specific arrest rate: Non-Hispanic, Asian',
row == 38, 'Race and Hispanic Origin-specific arrest rate: Non-Hispanic, Native Hawaiian or Other Pacific Islander',
row == 39, 'Race and Hispanic Origin-specific arrest rate: Unknown race or Hispanic origin'





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
column == 15,  'NIBRS crimes against property (Total)',
column == 16,  'Arson',
column == 17,  'Bribery',
column == 18,  'Burglary/B&E',
column == 19,  'Counterfeiting/Forgery',
column == 20,  'Destruction/Damage/Vandalism',
column == 21,  'Embezzlement',
column == 22,  'Extortion/Blackmail',
column == 23,  'Fraud Offenses',
column == 24,  'Larceny/Theft Offenses',
column == 25,  'Motor Vehicle Theft',
column == 26,  'Robbery',
column == 27,  'Stolen Property Offenses',
column == 28,  'NIBRS crimes against society (Total)',
column == 29,  'Revised Rape',
column == 30,  'Violent Crime',
column == 31,  'Property Crime',

column == 32, 'Car Jacking',
column == 33, 'Total Arrests',

column == 34, 'Assault Offenses',
column == 35, 'Violent Crime 2',

column == 36, 'Animal Cruelty',
column == 37, 'Drug/Narcotic Offenses',
column == 38, 'Gambling Offenses',
column == 39, 'Pornography/Obscene Material',
column == 40, 'Prostitution Offenses',
column == 41, 'Weapon Law Violations',
column == 42, 'Import Violations',
column == 43, 'Export Violations',
column == 44, 'Federal Liquor Offenses',
column == 45, 'Federal Tobacco Offenses',
column == 46, 'Wildlife Trafficking',
column == 47, 'Espionage',
column == 48, 'Money Laundering',
column == 49, 'Harboring Escapee/Concealing from Arrest',
column == 50, 'Flight to Avoid Prosecution',
column == 51, 'Flight to Avoid Deportation',
column == 52, 'Illegal Entry into the United States',
column == 53, 'False Citizenship',
column == 54, 'Smuggling Aliens',
column == 55, 'Re-entry after Deportation',
column == 56, 'Failure to Register as a Sex Offender',
column == 57, 'Treason',
column == 58, 'Violation of National Firearm Act of 1934',
column == 59, 'Weapons of Mass Destruction',
column == 60, 'Explosives Violation',
column == 61, ' Drug Equipment Violations'





  ),

  full_table = "Table4b-Arrestees-Rates",
  table = DER_TABLE_NAME
  )

  return(returndata)

}

estimate_type_detail_percentage_label <- function(indata){
  log_debug("Running estimate_type_detail_percentage_label function")

  returndata <- indata %>%
    mutate(
      estimate_type_detail_percentage = fcase(

trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 1,  'Arrestee Level', #Arrest rate (per 100k total population)
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 2,  'Arrestee Level', #Arrest type-specific arrest rate: On-view arrest
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 3,  'Arrestee Level', #Arrest type-specific arrest rate: Summoned/cited
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 4,  'Arrestee Level', #Arrest type-specific arrest rate: Taken into custody
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 5,  'Arrestee Level', #Age-specific arrest rate: Under 5
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 6,  'Arrestee Level', #Age-specific arrest rate: 5-14
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 7,  'Arrestee Level', #Age-specific arrest rate: 15
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 8,  'Arrestee Level', #Age-specific arrest rate: 16
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 9,  'Arrestee Level', #Age-specific arrest rate: 17
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 10,  'Arrestee Level', #Age-specific arrest rate: 18-24
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 11,  'Arrestee Level', #Age-specific arrest rate: 25-34
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 12,  'Arrestee Level', #Age-specific arrest rate: 35-64
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 13,  'Arrestee Level', #Age-specific arrest rate: 65+
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 14,  'Arrestee Level', #Age-specific arrest rate: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 15,  'Arrestee Level', #Sex-specific arrest rate: Male
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 16,  'Arrestee Level', #Sex-specific arrest rate: Female
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 17,  'Arrestee Level', #Sex-specific arrest rate: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 18,  'Arrestee Level', #Race-specific arrest rate: White
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 19,  'Arrestee Level', #Race-specific arrest rate: Black
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 20,  'Arrestee Level', #Race-specific arrest rate: American Indian or Alaska Native
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 21,  'Arrestee Level', #Race-specific arrest rate: Asian
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 22,  'Arrestee Level', #Race-specific arrest rate: Native Hawaiian or Other Pacific Islander
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 23,  'Arrestee Level', #Race-specific arrest rate: Unknown

trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 24, 'Arrestee Level', #Age-specific arrest rate 2: Under 12
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 25, 'Arrestee Level', #Age-specific arrest rate 2: 12-17
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 26, 'Arrestee Level Subset to 12-17', #Age-specific arrest rate 2: 12-14
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 27, 'Arrestee Level Subset to 12-17', #Age-specific arrest rate 2: 15-17
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 28, 'Arrestee Level', #Age-specific arrest rate 2: 18+
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 29, 'Arrestee Level', #Age-specific arrest rate 2: Unknown

trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 30, 'Arrestee Level', #Hispanic Origin-specific arrest rate: Hispanic or Latino
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 31, 'Arrestee Level', #Hispanic Origin-specific arrest rate: Not Hispanic or Latino
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 32, 'Arrestee Level', #Hispanic Origin-specific arrest rate: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 33, 'Arrestee Level', #Race and Hispanic Origin-specific arrest rate: Hispanic or Latino
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 34, 'Arrestee Level', #Race and Hispanic Origin-specific arrest rate: Non-Hispanic, White
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 35, 'Arrestee Level', #Race and Hispanic Origin-specific arrest rate: Non-Hispanic, Black
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 36, 'Arrestee Level', #Race and Hispanic Origin-specific arrest rate: Non-Hispanic, American Indian or Alaska Native
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 37, 'Arrestee Level', #Race and Hispanic Origin-specific arrest rate: Non-Hispanic, Asian
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 38, 'Arrestee Level', #Race and Hispanic Origin-specific arrest rate: Non-Hispanic, Native Hawaiian or Other Pacific Islander
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 39, 'Arrestee Level' #Race and Hispanic Origin-specific arrest rate: Unknown race or Hispanic origin


))

  return(returndata)
}

estimate_type_detail_rate_label <- function(indata){
  log_debug("Running estimate_type_detail_rate_label function")

  returndata <- indata %>%
    mutate(
      estimate_type_detail_rate = fcase(

trim_upcase(estimate_type) %in% c('RATE') & row == 1,  'Arrestee rate per 100,000 persons', #Arrest rate (per 100k total population)
trim_upcase(estimate_type) %in% c('RATE') & row == 2,  'Arrestee rate per 100,000 persons', #Arrest type-specific arrest rate: On-view arrest
trim_upcase(estimate_type) %in% c('RATE') & row == 3,  'Arrestee rate per 100,000 persons', #Arrest type-specific arrest rate: Summoned/cited
trim_upcase(estimate_type) %in% c('RATE') & row == 4,  'Arrestee rate per 100,000 persons', #Arrest type-specific arrest rate: Taken into custody
trim_upcase(estimate_type) %in% c('RATE') & row == 5,  'Arrestee rate per 100,000 persons among persons Under 5', #Age-specific arrest rate: Under 5
trim_upcase(estimate_type) %in% c('RATE') & row == 6,  'Arrestee rate per 100,000 persons among persons 5-14', #Age-specific arrest rate: 5-14
trim_upcase(estimate_type) %in% c('RATE') & row == 7,  'Arrestee rate per 100,000 persons among persons 15', #Age-specific arrest rate: 15
trim_upcase(estimate_type) %in% c('RATE') & row == 8,  'Arrestee rate per 100,000 persons among persons 16', #Age-specific arrest rate: 16
trim_upcase(estimate_type) %in% c('RATE') & row == 9,  'Arrestee rate per 100,000 persons among persons 17', #Age-specific arrest rate: 17
trim_upcase(estimate_type) %in% c('RATE') & row == 10,  'Arrestee rate per 100,000 persons among persons 18-24', #Age-specific arrest rate: 18-24
trim_upcase(estimate_type) %in% c('RATE') & row == 11,  'Arrestee rate per 100,000 persons among persons 25-34', #Age-specific arrest rate: 25-34
trim_upcase(estimate_type) %in% c('RATE') & row == 12,  'Arrestee rate per 100,000 persons among persons 35-64', #Age-specific arrest rate: 35-64
trim_upcase(estimate_type) %in% c('RATE') & row == 13,  'Arrestee rate per 100,000 persons among persons 65+', #Age-specific arrest rate: 65+
trim_upcase(estimate_type) %in% c('RATE') & row == 14,  'Arrestee rate per 100,000 persons', #Age-specific arrest rate: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 15,  'Arrestee rate per 100,000 persons among persons Male', #Sex-specific arrest rate: Male
trim_upcase(estimate_type) %in% c('RATE') & row == 16,  'Arrestee rate per 100,000 persons among persons Female', #Sex-specific arrest rate: Female
trim_upcase(estimate_type) %in% c('RATE') & row == 17,  'Arrestee rate per 100,000 persons', #Sex-specific arrest rate: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 18,  'Arrestee rate per 100,000 persons among persons White', #Race-specific arrest rate: White
trim_upcase(estimate_type) %in% c('RATE') & row == 19,  'Arrestee rate per 100,000 persons among persons Black', #Race-specific arrest rate: Black
trim_upcase(estimate_type) %in% c('RATE') & row == 20,  'Arrestee rate per 100,000 persons among persons American Indian or Alaska Native', #Race-specific arrest rate: American Indian or Alaska Native
trim_upcase(estimate_type) %in% c('RATE') & row == 21,  'Arrestee rate per 100,000 persons among persons Asian', #Race-specific arrest rate: Asian
trim_upcase(estimate_type) %in% c('RATE') & row == 22,  'Arrestee rate per 100,000 persons among persons Native Hawaiian or Other Pacific Islander', #Race-specific arrest rate: Native Hawaiian or Other Pacific Islander
trim_upcase(estimate_type) %in% c('RATE') & row == 23,  'Arrestee rate per 100,000 persons', #Race-specific arrest rate: Unknown

trim_upcase(estimate_type) %in% c('RATE') & row == 24, 'Arrestee rate per 100,000 persons among persons Under 12', #Age-specific arrest rate 2: Under 12
trim_upcase(estimate_type) %in% c('RATE') & row == 25, 'Arrestee rate per 100,000 persons among persons 12-17', #Age-specific arrest rate 2: 12-17
trim_upcase(estimate_type) %in% c('RATE') & row == 26, 'Arrestee rate per 100,000 persons among persons 12-14', #Age-specific arrest rate 2: 12-14
trim_upcase(estimate_type) %in% c('RATE') & row == 27, 'Arrestee rate per 100,000 persons among persons 15-17', #Age-specific arrest rate 2: 15-17
trim_upcase(estimate_type) %in% c('RATE') & row == 28, 'Arrestee rate per 100,000 persons among persons 18+', #Age-specific arrest rate 2: 18+
trim_upcase(estimate_type) %in% c('RATE') & row == 29, 'Arrestee rate per 100,000 persons', #Age-specific arrest rate 2: Unknown

trim_upcase(estimate_type) %in% c('RATE') & row == 30, 'Arrestee rate per 100,000 persons among persons Hispanic or Latino', #Hispanic Origin-specific arrest rate: Hispanic or Latino
trim_upcase(estimate_type) %in% c('RATE') & row == 31, 'Arrestee rate per 100,000 persons among persons Not Hispanic or Latino', #Hispanic Origin-specific arrest rate: Not Hispanic or Latino
trim_upcase(estimate_type) %in% c('RATE') & row == 32, 'Arrestee rate per 100,000 persons', #Hispanic Origin-specific arrest rate: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 33, 'Arrestee rate per 100,000 persons among persons Hispanic or Latino', #Race and Hispanic Origin-specific arrest rate: Hispanic or Latino
trim_upcase(estimate_type) %in% c('RATE') & row == 34, 'Arrestee rate per 100,000 persons among persons Non-Hispanic, White', #Race and Hispanic Origin-specific arrest rate: Non-Hispanic, White
trim_upcase(estimate_type) %in% c('RATE') & row == 35, 'Arrestee rate per 100,000 persons among persons Non-Hispanic, Black', #Race and Hispanic Origin-specific arrest rate: Non-Hispanic, Black
trim_upcase(estimate_type) %in% c('RATE') & row == 36, 'Arrestee rate per 100,000 persons among persons Non-Hispanic, American Indian or Alaska Native', #Race and Hispanic Origin-specific arrest rate: Non-Hispanic, American Indian or Alaska Native
trim_upcase(estimate_type) %in% c('RATE') & row == 37, 'Arrestee rate per 100,000 persons among persons Non-Hispanic, Asian', #Race and Hispanic Origin-specific arrest rate: Non-Hispanic, Asian
trim_upcase(estimate_type) %in% c('RATE') & row == 38, 'Arrestee rate per 100,000 persons among persons Non-Hispanic, Native Hawaiian or Other Pacific Islander', #Race and Hispanic Origin-specific arrest rate: Non-Hispanic, Native Hawaiian or Other Pacific Islander
trim_upcase(estimate_type) %in% c('RATE') & row == 39, 'Arrestee rate per 100,000 persons' #Race and Hispanic Origin-specific arrest rate: Unknown race or Hispanic origin


))

  return(returndata)

}




#This function will calculate the counts and percentage one column at a time

generate_est <- function(maindata, subsetvareq1, column_number){
  log_debug("Running generate_est function")

  #Need to drop the missing arrestee
  maindata <- maindata %>%
    filter(!is.na(arrestee_id))

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
    summarise(final_count = (sum(weighted_count) / POP_TOTAL) * 100000 ) %>%
    mutate(population_estimate = POP_TOTAL ) %>%
    mutate(section = 1)
  #For ORI level - Need unweighted counts
  s1[[2]] <- main_filter %>%
    group_by(ori) %>%
    summarise(final_count = sum(!!infiltervar)) %>%
    ungroup() %>%
    mutate(section = 1)

  #Arrest type
  s2 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrest_type_arrestee, var=der_arrest_type, section=2, mergeby=c( "incident_id", "arrestee_id"), denom= POP_TOTAL)


  #arrestee Age
  #Under 5
  s3 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_age_cat_15_17_arrestee %>% filter(der_arrestee_age_cat_15_17 == 1), var=der_arrestee_age_cat_15_17, section=3, mergeby=c( "incident_id", "arrestee_id"), denom= DER_POP_PCTAGELT5_NUM)
  #5-14
  s4 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_age_cat_15_17_arrestee %>% filter(der_arrestee_age_cat_15_17 == 2), var=der_arrestee_age_cat_15_17, section=4, mergeby=c( "incident_id", "arrestee_id"), denom= DER_POP_PCTAGE5TO14_NUM)
  #15
  s5 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_age_cat_15_17_arrestee %>% filter(der_arrestee_age_cat_15_17 == 3), var=der_arrestee_age_cat_15_17, section=5, mergeby=c( "incident_id", "arrestee_id"), denom= DER_POP_PCTAGE15_NUM)
  #16
  s6 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_age_cat_15_17_arrestee %>% filter(der_arrestee_age_cat_15_17 == 4), var=der_arrestee_age_cat_15_17, section=6, mergeby=c( "incident_id", "arrestee_id"), denom= DER_POP_PCTAGE16_NUM)
  #17
  s7 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_age_cat_15_17_arrestee %>% filter(der_arrestee_age_cat_15_17 == 5), var=der_arrestee_age_cat_15_17, section=7, mergeby=c( "incident_id", "arrestee_id"), denom= DER_POP_PCTAGE17_NUM)
  #18-24
  s8 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_age_cat_15_17_arrestee %>% filter(der_arrestee_age_cat_15_17 == 6), var=der_arrestee_age_cat_15_17, section=8, mergeby=c( "incident_id", "arrestee_id"), denom= DER_POP_PCTAGE18TO24_NUM)
  #25-34
  s9 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_age_cat_15_17_arrestee %>% filter(der_arrestee_age_cat_15_17 == 7), var=der_arrestee_age_cat_15_17, section=9, mergeby=c( "incident_id", "arrestee_id"), denom= DER_POP_PCTAGE25TO34_NUM)
  #35-64
  s10 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_age_cat_15_17_arrestee %>% filter(der_arrestee_age_cat_15_17 == 8), var=der_arrestee_age_cat_15_17, section=10, mergeby=c( "incident_id", "arrestee_id"), denom= DER_POP_PCTAGE35TO64_NUM)
  #65+
  s11 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_age_cat_15_17_arrestee %>% filter(der_arrestee_age_cat_15_17 == 9), var=der_arrestee_age_cat_15_17, section=11, mergeby=c( "incident_id", "arrestee_id"), denom= DER_POP_PCTAGEGTE65_NUM)
  #Unknown
  s12 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_age_cat_15_17_arrestee %>% filter(der_arrestee_age_cat_15_17 == 10), var=der_arrestee_age_cat_15_17, section=12, mergeby=c( "incident_id", "arrestee_id"), denom= POP_TOTAL)

  #arrestee sex
  #Male
  s13 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_gender_arrestee %>% filter(der_arrestee_gender == 1), var=der_arrestee_gender, section=13, mergeby=c( "incident_id", "arrestee_id"), denom= DER_POP_PCTSEXMALE_NUM)
  #Female
  s14 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_gender_arrestee %>% filter(der_arrestee_gender == 2), var=der_arrestee_gender, section=14, mergeby=c( "incident_id", "arrestee_id"), denom= DER_POP_PCTSEXFEMALE_NUM)
  #Unknown
  s15 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_gender_arrestee %>% filter(der_arrestee_gender == 3), var=der_arrestee_gender, section=15, mergeby=c( "incident_id", "arrestee_id"), denom= POP_TOTAL)

  #arrestee race

  #White
  s16 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_race_arrestee %>% filter(der_arrestee_race == 1), var=der_arrestee_race, section=16, mergeby=c( "incident_id", "arrestee_id"), denom= DER_POP_PCTRACEWHITE_NUM)
  #Black
  s17 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_race_arrestee %>% filter(der_arrestee_race == 2), var=der_arrestee_race, section=17, mergeby=c( "incident_id", "arrestee_id"), denom= DER_POP_PCTRACEBLACK_NUM)
  #American Indian or Alaska Native
  s18 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_race_arrestee %>% filter(der_arrestee_race == 3), var=der_arrestee_race, section=18, mergeby=c( "incident_id", "arrestee_id"), denom= DER_POP_PCTRACEAIAN_NUM)
  #Asian
  s19 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_race_arrestee %>% filter(der_arrestee_race == 4), var=der_arrestee_race, section=19, mergeby=c( "incident_id", "arrestee_id"), denom= DER_POP_PCTRACEASIAN_NUM)
  #Native Hawaiian or Other Pacific Islander
  s20 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_race_arrestee %>% filter(der_arrestee_race == 5), var=der_arrestee_race, section=20, mergeby=c( "incident_id", "arrestee_id"), denom= DER_POP_PCTRACENHPI_NUM)
  #Unknown
  s21 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_race_arrestee %>% filter(der_arrestee_race == 6), var=der_arrestee_race, section=21, mergeby=c( "incident_id", "arrestee_id"), denom= POP_TOTAL)

  #Age-specific arrest rate 2
  s22 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_age_cat_under18_2_arrestee_imp %>% filter(der_arrestee_age_cat_under18_2 == 1), var=der_arrestee_age_cat_under18_2, section=22, mergeby=c( "incident_id", "arrestee_id"), denom=DER_POP_PCTAGE_UNDER_12_NUM) #arrestee Age 2 :   Under 12
  s23 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_age_cat_under18_2_arrestee_imp %>% filter(der_arrestee_age_cat_under18_2 == 2), var=der_arrestee_age_cat_under18_2, section=23, mergeby=c( "incident_id", "arrestee_id"), denom=DER_POP_PCTAGE_12_17_NUM) #arrestee Age 2 :   12-17
  s24 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_age_cat_12_17_cat_arrestee_imp %>% filter(der_arrestee_age_cat_12_17_cat == 1), var=der_arrestee_age_cat_12_17_cat, section=24, mergeby=c( "incident_id", "arrestee_id"), denom=DER_POP_PCTAGE_12_14_NUM) #arrestee Age 2 :   12-14
  s25 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_age_cat_12_17_cat_arrestee_imp %>% filter(der_arrestee_age_cat_12_17_cat == 2), var=der_arrestee_age_cat_12_17_cat, section=25, mergeby=c( "incident_id", "arrestee_id"), denom=DER_POP_PCTAGE_15_17_NUM) #arrestee Age 2 :   15-17
  s26 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_age_cat_2_uo18_arrestee_imp %>% filter(der_arrestee_age_cat_2_uo18 == 2), var=der_arrestee_age_cat_2_uo18, section=26, mergeby=c( "incident_id", "arrestee_id"), denom=DER_POP_PCTAGE_OVER_18_NUM) #arrestee Age 2 : 18+
  s27 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_age_cat_2_uo18_arrestee_imp %>% filter(der_arrestee_age_cat_2_uo18 == 3), var=der_arrestee_age_cat_2_uo18, section=27, mergeby=c( "incident_id", "arrestee_id"), denom=POP_TOTAL) #arrestee Age 2 :   Unknown
  
  #Arrestee Hispanic Origin
  s28 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_ethnicity_arrestee %>% filter(der_arrestee_ethnicity == 1), var=der_arrestee_ethnicity, section= 28, mergeby=c( "incident_id", "arrestee_id"), denom=DER_POP_PCT_HISP_NUM) #Hispanic Origin-specific arrest rate:   Hispanic or Latino
  s29 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_ethnicity_arrestee %>% filter(der_arrestee_ethnicity == 2), var=der_arrestee_ethnicity, section= 29, mergeby=c( "incident_id", "arrestee_id"), denom=DER_POP_PCT_NONHISP_NUM) #Hispanic Origin-specific arrest rate:   Not Hispanic or Latino
  s30 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_ethnicity_arrestee %>% filter(der_arrestee_ethnicity == 3), var=der_arrestee_ethnicity, section= 30, mergeby=c( "incident_id", "arrestee_id"), denom=POP_TOTAL) #Hispanic Origin-specific arrest rate:   Unknown
  
  
  #Arrestee race and Hispanic Origin
  s31 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_ethnicity_race_arrestee %>% filter(der_arrestee_ethnicity_race == 1), var=der_arrestee_ethnicity_race, section= 31, mergeby=c( "incident_id", "arrestee_id"), denom=DER_POP_PCT_HISP_NUM) #Race and Hispanic Origin-specific arrest rate:   Hispanic or Latino
  s32 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_ethnicity_race_arrestee %>% filter(der_arrestee_ethnicity_race == 2), var=der_arrestee_ethnicity_race, section= 32, mergeby=c( "incident_id", "arrestee_id"), denom=DER_POP_PCT_NONHISP_WHITE_NUM) #Race and Hispanic Origin-specific arrest rate:   Non-Hispanic, White
  s33 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_ethnicity_race_arrestee %>% filter(der_arrestee_ethnicity_race == 3), var=der_arrestee_ethnicity_race, section= 33, mergeby=c( "incident_id", "arrestee_id"), denom=DER_POP_PCT_NONHISP_BLACK_NUM) #Race and Hispanic Origin-specific arrest rate:   Non-Hispanic, Black
  s34 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_ethnicity_race_arrestee %>% filter(der_arrestee_ethnicity_race == 4), var=der_arrestee_ethnicity_race, section= 34, mergeby=c( "incident_id", "arrestee_id"), denom=DER_POP_PCT_NONHISP_AIAN_NUM) #Race and Hispanic Origin-specific arrest rate:   Non-Hispanic, American Indian or Alaska Native
  s35 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_ethnicity_race_arrestee %>% filter(der_arrestee_ethnicity_race == 5), var=der_arrestee_ethnicity_race, section= 35, mergeby=c( "incident_id", "arrestee_id"), denom=DER_POP_PCT_NONHISP_ASIAN_NUM) #Race and Hispanic Origin-specific arrest rate:   Non-Hispanic, Asian
  s36 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_ethnicity_race_arrestee %>% filter(der_arrestee_ethnicity_race == 6), var=der_arrestee_ethnicity_race, section= 36, mergeby=c( "incident_id", "arrestee_id"), denom=DER_POP_PCT_NONHISP_NHOPI_NUM) #Race and Hispanic Origin-specific arrest rate:   Non-Hispanic, Native Hawaiian or Other Pacific Islander
  s37 <- agg_percent_CAA_arrestee_rate(leftdata = main_filter, rightdata = agg_arrestee_ethnicity_race_arrestee %>% filter(der_arrestee_ethnicity_race == 7), var=der_arrestee_ethnicity_race, section= 37, mergeby=c( "incident_id", "arrestee_id"), denom=POP_TOTAL) #Race and Hispanic Origin-specific arrest rate:   Unknown race or Hispanic origin
  
  
  

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
    mutate(count = DER_NA_CODE) %>%
    mutate(percentage = DER_NA_CODE) %>%
    mutate(rate = fcase(row %in% c(1:DER_MAXIMUM_ROW), final_count,default = DER_NA_CODE)) %>%
    mutate(population_estimate = fcase(row %in% c(1:DER_MAXIMUM_ROW), population_estimate,default = DER_NA_CODE)) %>%
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

	#Call the functions for each column
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