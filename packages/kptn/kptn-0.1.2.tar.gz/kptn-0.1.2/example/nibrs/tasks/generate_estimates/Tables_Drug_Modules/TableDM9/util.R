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
    der_arrestee_age_cat %in% c(1:8),  der_arrestee_age_cat + 2,
    der_arrestee_gender %in% c(1:2) & section == 4,  der_arrestee_gender + 10,
    der_arrestee_race %in% c(1:6),  der_arrestee_race + 12,


    der_arrestee_gender == 1 & section == 8 ,   19,
    der_arrestee_gender_race %in% c(1:6),  der_arrestee_gender_race + 19,
    der_arrestee_gender == 2 & section == 8 ,   26,
    der_arrestee_gender_race %in% c(7:12),  der_arrestee_gender_race + 26 - 6,
    der_arrestee_gender == 3 & section == 8 ,   33,
    der_arrestee_gender_race %in% c(13:18),  der_arrestee_gender_race + 33 - 12,

    der_juvenile_disp %in% c(1:4),  der_juvenile_disp + 39,
    der_multiple_arrest %in% c(1:3),  der_multiple_arrest + 43,

    ###Weapon at Arrestee Level - Armed with #####

    der_weapon_no_yes %in% c(1:2) & section == 11,  der_weapon_no_yes + 46,
	section == 12,  49,

	#######Arrestee age 2###############################

	der_arrestee_age_cat_under18_2 %in% c(1:2), der_arrestee_age_cat_under18_2 + 49, ##Under 12, 12-17
	der_arrestee_age_cat_12_17_cat %in% c(1:2), der_arrestee_age_cat_12_17_cat + 51, #12-14, 15-17
	der_arrestee_age_cat_2_uo18 %in% c(2), 54, #2, #18+
	der_arrestee_age_cat_2_uo18 %in% c(3), 55, #3, #Unknown
    
    #Arrestee Hispanic Origin
    der_arrestee_ethnicity %in% c(1:3), der_arrestee_ethnicity + 55,
    
    #Arrestee race and Hispanic Origin
    der_arrestee_ethnicity_race %in% c(1:7), der_arrestee_ethnicity_race + 58       

  ))

  return(returndata)
}

assign_section <- function(data){

  returndata <- data %>% mutate(

  section = fcase(
    row %in% c(1),  1,
    row %in% c(2),  2,
    row %in% c(3:10),  3,
    row %in% c(11:12),  4,
    row %in% c(13:18),  5,
    row %in% c(19:39),  6,
    row %in% c(40:43),  7,
    row %in% c(44:46),  8,
    row %in% c(47:48),  9,
	  row %in% c(49),  10,
    row %in% c(50:55),  11,
    row %in% c(56:58),  12,
    row %in% c(59:65),  13						   
	)
  )

  return(returndata)

}



#New add on code for labels
assign_labels <- function(data){

  returndata <- data %>% mutate(

  estimate_domain = fcase(

row == 1,  'Total Arrests per Activity',
row == 2,  'Total Arrests per Drug Category',
row == 3,  'Arrestee age: Under 5',
row == 4,  'Arrestee age: 5-14',
row == 5,  'Arrestee age: 15-17',
row == 6,  'Arrestee age: 18-24',
row == 7,  'Arrestee age: 25-34',
row == 8,  'Arrestee age: 35-64',
row == 9,  'Arrestee age: 65+',
row == 10,  'Arrestee age: Unknown',
row == 11,  'Arrestee sex: Male',
row == 12,  'Arrestee sex: Female',
row == 13,  'Arrestee race: White',
row == 14,  'Arrestee race: Black',
row == 15,  'Arrestee race: American Indian or Alaska Native',
row == 16,  'Arrestee race: Asian',
row == 17,  'Arrestee race: Native Hawaiian or Other Pacific Islander',
row == 18,  'Arrestee race: Unknown',
row == 19,  'Arrestee sex and race: Male',
row == 20,  'Arrestee sex and race Male: White',
row == 21,  'Arrestee sex and race Male: Black',
row == 22,  'Arrestee sex and race Male: American Indian or Alaska Native',
row == 23,  'Arrestee sex and race Male: Asian',
row == 24,  'Arrestee sex and race Male: Native Hawaiian or Other Pacific Islander',
row == 25,  'Arrestee sex and race Male: Unknown',
row == 26,  'Arrestee sex and race: Female',
row == 27,  'Arrestee sex and race Female: White',
row == 28,  'Arrestee sex and race Female: Black',
row == 29,  'Arrestee sex and race Female: American Indian or Alaska Native',
row == 30,  'Arrestee sex and race Female: Asian',
row == 31,  'Arrestee sex and race Female: Native Hawaiian or Other Pacific Islander',
row == 32,  'Arrestee sex and race Female: Unknown',
row == 33,  'Arrestee sex and race: Unknown',
row == 34,  'Arrestee sex and race Unknown: White',
row == 35,  'Arrestee sex and race Unknown: Black',
row == 36,  'Arrestee sex and race Unknown: American Indian or Alaska Native',
row == 37,  'Arrestee sex and race Unknown: Asian',
row == 38,  'Arrestee sex and race Unknown: Native Hawaiian or Other Pacific Islander',
row == 39,  'Arrestee sex and race Unknown: Unknown',
row == 40,  'Juvenile disposition: Handled within department',
row == 41,  'Juvenile disposition: Referred to other authorities',
row == 42,  'Juvenile disposition: Not applicable',
row == 43,  'Juvenile disposition: Unknown',
row == 44,  'Multiple arrest indicator: Multiple',
row == 45,  'Multiple arrest indicator: Count',
row == 46,  'Multiple arrest indicator: Not applicable',
row == 47,  'Arrestee armed: No',
row == 48,  'Arrestee armed: Yes',
row == 49,  'Total: Total',

row == 50, 'Arrestee age 2: Under 12',
row == 51, 'Arrestee age 2: 12-17',
row == 52, 'Arrestee age 2: 12-14',
row == 53, 'Arrestee age 2: 15-17',
row == 54, 'Arrestee age 2: 18+',
row == 55, 'Arrestee age 2: Unknown',

row == 56, 'Arrestee Hispanic Origin: Hispanic or Latino',
row == 57, 'Arrestee Hispanic Origin: Not Hispanic or Latino',
row == 58, 'Arrestee Hispanic Origin: Unknown',
row == 59, 'Arrestee race and Hispanic Origin: Hispanic or Latino',
row == 60, 'Arrestee race and Hispanic Origin: Non-Hispanic, White',
row == 61, 'Arrestee race and Hispanic Origin: Non-Hispanic, Black',
row == 62, 'Arrestee race and Hispanic Origin: Non-Hispanic, American Indian or Alaska Native',
row == 63, 'Arrestee race and Hispanic Origin: Non-Hispanic, Asian',
row == 64, 'Arrestee race and Hispanic Origin: Non-Hispanic, Native Hawaiian or Other Pacific Islander',
row == 65, 'Arrestee race and Hispanic Origin: Unknown race or Hispanic origin'



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

  full_table = "TableDM9 - Drug Count By Arrestee - Involving More Than One Suspected Drug And More Than One Criminal Activity",
  table = DER_TABLE_NAME
  )

  return(returndata)

}

estimate_type_detail_percentage_label <- function(indata){

  returndata <- indata %>%
    mutate(
      estimate_type_detail_percentage = fcase(

trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 1,  'Arrestee Level', #Total Arrests per Activity
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 2,  'Arrestee Level', #Total Arrests per Drug Category
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 3,  'Arrestee Level', #Arrestee age: Under 5
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 4,  'Arrestee Level', #Arrestee age: 5-14
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 5,  'Arrestee Level', #Arrestee age: 15-17
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 6,  'Arrestee Level', #Arrestee age: 18-24
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 7,  'Arrestee Level', #Arrestee age: 25-34
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 8,  'Arrestee Level', #Arrestee age: 35-64
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 9,  'Arrestee Level', #Arrestee age: 65+
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 10,  'Arrestee Level', #Arrestee age: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 11,  'Arrestee Level', #Arrestee sex: Male
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 12,  'Arrestee Level', #Arrestee sex: Female
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 13,  'Arrestee Level', #Arrestee race: White
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 14,  'Arrestee Level', #Arrestee race: Black
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 15,  'Arrestee Level', #Arrestee race: American Indian or Alaska Native
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 16,  'Arrestee Level', #Arrestee race: Asian
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 17,  'Arrestee Level', #Arrestee race: Native Hawaiian or Other Pacific Islander
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 18,  'Arrestee Level', #Arrestee race: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 19,  'Arrestee Level', #Arrestee sex and race: Male
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 20,  'Arrestee Level subset to male', #Arrestee sex and race Male: White
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 21,  'Arrestee Level subset to male', #Arrestee sex and race Male: Black
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 22,  'Arrestee Level subset to male', #Arrestee sex and race Male: American Indian or Alaska Native
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 23,  'Arrestee Level subset to male', #Arrestee sex and race Male: Asian
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 24,  'Arrestee Level subset to male', #Arrestee sex and race Male: Native Hawaiian or Other Pacific Islander
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 25,  'Arrestee Level subset to male', #Arrestee sex and race Male: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 26,  'Arrestee Level', #Arrestee sex and race: Female
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 27,  'Arrestee Level subset to female', #Arrestee sex and race Female: White
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 28,  'Arrestee Level subset to female', #Arrestee sex and race Female: Black
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 29,  'Arrestee Level subset to female', #Arrestee sex and race Female: American Indian or Alaska Native
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 30,  'Arrestee Level subset to female', #Arrestee sex and race Female: Asian
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 31,  'Arrestee Level subset to female', #Arrestee sex and race Female: Native Hawaiian or Other Pacific Islander
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 32,  'Arrestee Level subset to female', #Arrestee sex and race Female: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 33,  'Arrestee Level', #Arrestee sex and race: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 34,  'Arrestee Level subset to unknown gender', #Arrestee sex and race Unknown: White
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 35,  'Arrestee Level subset to unknown gender', #Arrestee sex and race Unknown: Black
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 36,  'Arrestee Level subset to unknown gender', #Arrestee sex and race Unknown: American Indian or Alaska Native
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 37,  'Arrestee Level subset to unknown gender', #Arrestee sex and race Unknown: Asian
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 38,  'Arrestee Level subset to unknown gender', #Arrestee sex and race Unknown: Native Hawaiian or Other Pacific Islander
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 39,  'Arrestee Level subset to unknown gender', #Arrestee sex and race Unknown: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 40,  'Arrestee Level', #Juvenile disposition: Handled within department
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 41,  'Arrestee Level', #Juvenile disposition: Referred to other authorities
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 42,  'Arrestee Level', #Juvenile disposition: Not applicable
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 43,  'Arrestee Level', #Juvenile disposition: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 44,  'Arrestee Level', #Multiple arrest indicator: Multiple
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 45,  'Arrestee Level', #Multiple arrest indicator: Count
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 46,  'Arrestee Level', #Multiple arrest indicator: Not applicable
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 47,  'Arrestee Level', #Arrestee armed: No
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 48,  'Arrestee Level', #Arrestee armed: Yes
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 49,  'Arrestee Level', #Total: Total

trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 50, 'Arrestee Level', #Arrestee age 2: Under 12
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 51, 'Arrestee Level', #Arrestee age 2: 12-17
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 52, 'Arrestee Level Subset to 12-17', #Arrestee age 2: 12-14
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 53, 'Arrestee Level Subset to 12-17', #Arrestee age 2: 15-17
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 54, 'Arrestee Level', #Arrestee age 2: 18+
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 55, 'Arrestee Level', #Arrestee age 2: Unknown

trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 56, 'Arrestee Level', #Arrestee Hispanic Origin: Hispanic or Latino
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 57, 'Arrestee Level', #Arrestee Hispanic Origin: Not Hispanic or Latino
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 58, 'Arrestee Level', #Arrestee Hispanic Origin: Unknown
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 59, 'Arrestee Level', #Arrestee race and Hispanic Origin: Hispanic or Latino
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 60, 'Arrestee Level', #Arrestee race and Hispanic Origin: Non-Hispanic, White
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 61, 'Arrestee Level', #Arrestee race and Hispanic Origin: Non-Hispanic, Black
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 62, 'Arrestee Level', #Arrestee race and Hispanic Origin: Non-Hispanic, American Indian or Alaska Native
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 63, 'Arrestee Level', #Arrestee race and Hispanic Origin: Non-Hispanic, Asian
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 64, 'Arrestee Level', #Arrestee race and Hispanic Origin: Non-Hispanic, Native Hawaiian or Other Pacific Islander
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 65, 'Arrestee Level' #Arrestee race and Hispanic Origin: Unknown race or Hispanic origin


))

  return(returndata)
}

estimate_type_detail_rate_label <- function(indata){

  returndata <- indata %>%
    mutate(
      estimate_type_detail_rate = fcase(

trim_upcase(estimate_type) %in% c('RATE') & row == 1,  DER_NA_CODE_STRING, #Total Arrests per Activity
trim_upcase(estimate_type) %in% c('RATE') & row == 2,  DER_NA_CODE_STRING, #Total Arrests per Drug Category
trim_upcase(estimate_type) %in% c('RATE') & row == 3,  DER_NA_CODE_STRING, #Arrestee age: Under 5
trim_upcase(estimate_type) %in% c('RATE') & row == 4,  DER_NA_CODE_STRING, #Arrestee age: 5-14
trim_upcase(estimate_type) %in% c('RATE') & row == 5,  DER_NA_CODE_STRING, #Arrestee age: 15-17
trim_upcase(estimate_type) %in% c('RATE') & row == 6,  DER_NA_CODE_STRING, #Arrestee age: 18-24
trim_upcase(estimate_type) %in% c('RATE') & row == 7,  DER_NA_CODE_STRING, #Arrestee age: 25-34
trim_upcase(estimate_type) %in% c('RATE') & row == 8,  DER_NA_CODE_STRING, #Arrestee age: 35-64
trim_upcase(estimate_type) %in% c('RATE') & row == 9,  DER_NA_CODE_STRING, #Arrestee age: 65+
trim_upcase(estimate_type) %in% c('RATE') & row == 10,  DER_NA_CODE_STRING, #Arrestee age: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 11,  DER_NA_CODE_STRING, #Arrestee sex: Male
trim_upcase(estimate_type) %in% c('RATE') & row == 12,  DER_NA_CODE_STRING, #Arrestee sex: Female
trim_upcase(estimate_type) %in% c('RATE') & row == 13,  DER_NA_CODE_STRING, #Arrestee race: White
trim_upcase(estimate_type) %in% c('RATE') & row == 14,  DER_NA_CODE_STRING, #Arrestee race: Black
trim_upcase(estimate_type) %in% c('RATE') & row == 15,  DER_NA_CODE_STRING, #Arrestee race: American Indian or Alaska Native
trim_upcase(estimate_type) %in% c('RATE') & row == 16,  DER_NA_CODE_STRING, #Arrestee race: Asian
trim_upcase(estimate_type) %in% c('RATE') & row == 17,  DER_NA_CODE_STRING, #Arrestee race: Native Hawaiian or Other Pacific Islander
trim_upcase(estimate_type) %in% c('RATE') & row == 18,  DER_NA_CODE_STRING, #Arrestee race: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 19,  DER_NA_CODE_STRING, #Arrestee sex and race: Male
trim_upcase(estimate_type) %in% c('RATE') & row == 20,  DER_NA_CODE_STRING, #Arrestee sex and race Male: White
trim_upcase(estimate_type) %in% c('RATE') & row == 21,  DER_NA_CODE_STRING, #Arrestee sex and race Male: Black
trim_upcase(estimate_type) %in% c('RATE') & row == 22,  DER_NA_CODE_STRING, #Arrestee sex and race Male: American Indian or Alaska Native
trim_upcase(estimate_type) %in% c('RATE') & row == 23,  DER_NA_CODE_STRING, #Arrestee sex and race Male: Asian
trim_upcase(estimate_type) %in% c('RATE') & row == 24,  DER_NA_CODE_STRING, #Arrestee sex and race Male: Native Hawaiian or Other Pacific Islander
trim_upcase(estimate_type) %in% c('RATE') & row == 25,  DER_NA_CODE_STRING, #Arrestee sex and race Male: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 26,  DER_NA_CODE_STRING, #Arrestee sex and race: Female
trim_upcase(estimate_type) %in% c('RATE') & row == 27,  DER_NA_CODE_STRING, #Arrestee sex and race Female: White
trim_upcase(estimate_type) %in% c('RATE') & row == 28,  DER_NA_CODE_STRING, #Arrestee sex and race Female: Black
trim_upcase(estimate_type) %in% c('RATE') & row == 29,  DER_NA_CODE_STRING, #Arrestee sex and race Female: American Indian or Alaska Native
trim_upcase(estimate_type) %in% c('RATE') & row == 30,  DER_NA_CODE_STRING, #Arrestee sex and race Female: Asian
trim_upcase(estimate_type) %in% c('RATE') & row == 31,  DER_NA_CODE_STRING, #Arrestee sex and race Female: Native Hawaiian or Other Pacific Islander
trim_upcase(estimate_type) %in% c('RATE') & row == 32,  DER_NA_CODE_STRING, #Arrestee sex and race Female: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 33,  DER_NA_CODE_STRING, #Arrestee sex and race: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 34,  DER_NA_CODE_STRING, #Arrestee sex and race Unknown: White
trim_upcase(estimate_type) %in% c('RATE') & row == 35,  DER_NA_CODE_STRING, #Arrestee sex and race Unknown: Black
trim_upcase(estimate_type) %in% c('RATE') & row == 36,  DER_NA_CODE_STRING, #Arrestee sex and race Unknown: American Indian or Alaska Native
trim_upcase(estimate_type) %in% c('RATE') & row == 37,  DER_NA_CODE_STRING, #Arrestee sex and race Unknown: Asian
trim_upcase(estimate_type) %in% c('RATE') & row == 38,  DER_NA_CODE_STRING, #Arrestee sex and race Unknown: Native Hawaiian or Other Pacific Islander
trim_upcase(estimate_type) %in% c('RATE') & row == 39,  DER_NA_CODE_STRING, #Arrestee sex and race Unknown: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 40,  DER_NA_CODE_STRING, #Juvenile disposition: Handled within department
trim_upcase(estimate_type) %in% c('RATE') & row == 41,  DER_NA_CODE_STRING, #Juvenile disposition: Referred to other authorities
trim_upcase(estimate_type) %in% c('RATE') & row == 42,  DER_NA_CODE_STRING, #Juvenile disposition: Not applicable
trim_upcase(estimate_type) %in% c('RATE') & row == 43,  DER_NA_CODE_STRING, #Juvenile disposition: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 44,  DER_NA_CODE_STRING, #Multiple arrest indicator: Multiple
trim_upcase(estimate_type) %in% c('RATE') & row == 45,  DER_NA_CODE_STRING, #Multiple arrest indicator: Count
trim_upcase(estimate_type) %in% c('RATE') & row == 46,  DER_NA_CODE_STRING, #Multiple arrest indicator: Not applicable
trim_upcase(estimate_type) %in% c('RATE') & row == 47,  DER_NA_CODE_STRING, #Arrestee armed: No
trim_upcase(estimate_type) %in% c('RATE') & row == 48,  DER_NA_CODE_STRING, #Arrestee armed: Yes
trim_upcase(estimate_type) %in% c('RATE') & row == 49,  DER_NA_CODE_STRING, #Total: Total

trim_upcase(estimate_type) %in% c('RATE') & row == 50, DER_NA_CODE_STRING, #Arrestee age 2: Under 12
trim_upcase(estimate_type) %in% c('RATE') & row == 51, DER_NA_CODE_STRING, #Arrestee age 2: 12-17
trim_upcase(estimate_type) %in% c('RATE') & row == 52, DER_NA_CODE_STRING, #Arrestee age 2: 12-14
trim_upcase(estimate_type) %in% c('RATE') & row == 53, DER_NA_CODE_STRING, #Arrestee age 2: 15-17
trim_upcase(estimate_type) %in% c('RATE') & row == 54, DER_NA_CODE_STRING, #Arrestee age 2: 18+
trim_upcase(estimate_type) %in% c('RATE') & row == 55, DER_NA_CODE_STRING, #Arrestee age 2: Unknown

trim_upcase(estimate_type) %in% c('RATE') & row == 56, DER_NA_CODE_STRING, #Arrestee Hispanic Origin: Hispanic or Latino
trim_upcase(estimate_type) %in% c('RATE') & row == 57, DER_NA_CODE_STRING, #Arrestee Hispanic Origin: Not Hispanic or Latino
trim_upcase(estimate_type) %in% c('RATE') & row == 58, DER_NA_CODE_STRING, #Arrestee Hispanic Origin: Unknown
trim_upcase(estimate_type) %in% c('RATE') & row == 59, DER_NA_CODE_STRING, #Arrestee race and Hispanic Origin: Hispanic or Latino
trim_upcase(estimate_type) %in% c('RATE') & row == 60, DER_NA_CODE_STRING, #Arrestee race and Hispanic Origin: Non-Hispanic, White
trim_upcase(estimate_type) %in% c('RATE') & row == 61, DER_NA_CODE_STRING, #Arrestee race and Hispanic Origin: Non-Hispanic, Black
trim_upcase(estimate_type) %in% c('RATE') & row == 62, DER_NA_CODE_STRING, #Arrestee race and Hispanic Origin: Non-Hispanic, American Indian or Alaska Native
trim_upcase(estimate_type) %in% c('RATE') & row == 63, DER_NA_CODE_STRING, #Arrestee race and Hispanic Origin: Non-Hispanic, Asian
trim_upcase(estimate_type) %in% c('RATE') & row == 64, DER_NA_CODE_STRING, #Arrestee race and Hispanic Origin: Non-Hispanic, Native Hawaiian or Other Pacific Islander
trim_upcase(estimate_type) %in% c('RATE') & row == 65, DER_NA_CODE_STRING #Arrestee race and Hispanic Origin: Unknown race or Hispanic origin




))

  return(returndata)

}



#This function will calculate the counts and percentage one column at a time

generate_est <- function(maindata, subsetvareq1, subsetvareq2, column_number){

  #Need to drop the missing arrestee
  maindata <- maindata %>%
	#Need to drop the missing arrestee
    filter(!is.na(arrestee_id)) %>%
    #Filter to drug/narcotic violations (35A)
    #der_drug_narcotic_any == 1 & der_drug_equipment_any == 1 ~ 3, #Both drug/narcotic and drug equipment violations
    #der_drug_narcotic_any == 1 ~ 1, #Only drug/narcotic violations
    #Note this variable contains completed offenses
    filter(der_drug_narcotic_equipment_cat %in% c(1,3)) %>%
    #Filter to non-missing activity
    filter(!is.na(der_suspected_type_of_drug_crim_activity)) %>%
	#Filter to activities on table
	filter(der_suspected_type_of_drug_crim_activity %in% c(
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
    #Deduplicate by Incident ID and one arrestee
    group_by(ori, incident_id, arrestee_id) %>%
    mutate(raw_first = row_number() == 1 ) %>%
    ungroup() %>%
    filter(raw_first == TRUE) %>%
    select(-raw_first) %>%
    mutate(weighted_count = weight *one) %>%
    summarise(final_count = sum(weighted_count)) %>%
    mutate(section = 1)
  #For ORI level - Need unweighted counts
   s1[[2]] <- maindata %>%
    #Deduplicate by Incident ID and one arrestee
    group_by(ori, incident_id, arrestee_id) %>%
    mutate(raw_first = row_number() == 1 ) %>%
    ungroup() %>%
    filter(raw_first == TRUE) %>%
    select(-raw_first) %>%
    group_by(ori) %>%
    summarise(final_count = sum(one)) %>%
    ungroup() %>%
    mutate(section = 1)


  #Get only one incident per drug category
  s2 <- vector("list", 2)
  #For Table
  s2[[1]] <- maindata %>%
    #Dedepulicate by subsetvareq2 contains the code to subset to the specific drug and activity
    filter(!!(subsetvareq2 %>% rlang:::parse_expr())  ) %>%
    #Deduplicate by Incident ID and one arrestee
    group_by(ori, incident_id, arrestee_id) %>%
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
    #Deduplicate by Incident ID and one arrestee
    group_by(ori, incident_id, arrestee_id) %>%
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

#Get the totals - object will be the last section s12
  s12 <- vector("list", 2)
  #For Table
  s12[[1]] <- maindata %>%
    ############################################
    #Subset to specific column in table
    filter(!!(subsetvareq1 %>% rlang:::parse_expr()) ) %>%
    #Deduplicate by Incident ID, arrestee ID, and one instance of crime type
    group_by(ori, incident_id, arrestee_id) %>%
    mutate(raw_first = row_number() == 1 ) %>%
    ungroup() %>%
    filter(raw_first == TRUE) %>%
    select(-raw_first) %>%
    mutate(weighted_count = weight *one) %>%
    summarise(final_count = sum(weighted_count)) %>%
    mutate(section = 12)
  #For ORI level - Need unweighted counts
  s12[[2]] <- maindata %>%
    ############################################
    #Subset to specific column in table
    filter(!!(subsetvareq1 %>% rlang:::parse_expr()) ) %>%
    #Deduplicate by Incident ID, arrestee ID, and one instance of crime type
    group_by(ori, incident_id, arrestee_id) %>%
    mutate(raw_first = row_number() == 1 ) %>%
    ungroup() %>%
    filter(raw_first == TRUE) %>%
    select(-raw_first) %>%
    group_by(ori) %>%
    summarise(final_count = sum(one)) %>%
    ungroup() %>%
    mutate(section = 12)

  #Total Denominator
  der_total_denom <- s12[[1]] %>% select(final_count) %>% as.double()		

  #Filter the dataset
  main_filter <- maindata %>%
    ############################################
    #Subset to specific column in table
    filter(!!(subsetvareq1 %>% rlang:::parse_expr()) ) %>%
    #Deduplicate by Incident ID, arrestee ID, and one instance of crime type
    group_by(ori, incident_id, arrestee_id) %>%
    mutate(raw_first = row_number() == 1 ) %>%
    ungroup() %>%
    filter(raw_first == TRUE) %>%
    select(-raw_first) %>%
    ############################################
    select(ori, weight, incident_id, arrestee_id)


  #arrestee Age
  s3 <- agg_percent_arrestee(leftdata = main_filter, rightdata = agg_arrestee_age_cat_arrestee, var=der_arrestee_age_cat, section=3, mergeby=c( "incident_id", "arrestee_id"))

  #arrestee sex
  s4 <- agg_percent_arrestee(leftdata = main_filter, rightdata = agg_arrestee_gender_arrestee, var=der_arrestee_gender, section=4, mergeby=c( "incident_id", "arrestee_id"))

  #arrestee race
  s5 <- agg_percent_arrestee(leftdata = main_filter, rightdata = agg_arrestee_race_arrestee, var=der_arrestee_race, section=5, mergeby=c( "incident_id", "arrestee_id"))

  #arrestee sex and race
  s6 <- agg_percent_arrestee(leftdata = main_filter, rightdata = agg_arrestee_gender_race_arrestee_male, var=der_arrestee_gender_race, section=6, mergeby=c( "incident_id", "arrestee_id"))

  s7 <- agg_percent_arrestee(leftdata = main_filter, rightdata = agg_arrestee_gender_race_arrestee_female, var=der_arrestee_gender_race, section=7, mergeby=c( "incident_id", "arrestee_id"))

  s7_1 <- agg_percent_arrestee(leftdata = main_filter, rightdata = agg_arrestee_gender_race_arrestee_unknown, var=der_arrestee_gender_race, section=7.1, mergeby=c( "incident_id", "arrestee_id"))


  #arrestee sex - Extra for arrestee sex and race
  s8 <- agg_percent_arrestee(leftdata = main_filter, rightdata = agg_arrestee_gender_arrestee, var=der_arrestee_gender, section=8, mergeby=c( "incident_id", "arrestee_id"))

  #Juvenile disposition
  s9 <- agg_percent_arrestee(leftdata = main_filter, rightdata = agg_juvenile_disp_arrestee, var=der_juvenile_disp, section=9, mergeby=c( "incident_id", "arrestee_id"))

  #Multiple arrest indicator
  s10 <- agg_percent_arrestee(leftdata = main_filter, rightdata = agg_multiple_arrest_arrestee, var=der_multiple_arrest, section=10, mergeby=c( "incident_id", "arrestee_id"))

  #Arrestee armed
  s11 <- agg_percent_arrestee(leftdata = main_filter, rightdata = agg_weapon_no_yes_arrestee, var=der_weapon_no_yes, section=11, mergeby=c( "incident_id", "arrestee_id"))

  #Arrestee Age 2
  s13 <- agg_percent_CAA_arrestee(leftdata = main_filter, rightdata = agg_arrestee_age_cat_under18_2_arrestee_imp, var=der_arrestee_age_cat_under18_2, section=13, mergeby=c( "incident_id", "arrestee_id"), denom=  der_total_denom)
  s14 <- agg_percent_arrestee(leftdata = main_filter, rightdata = agg_arrestee_age_cat_12_17_cat_arrestee_imp, var=der_arrestee_age_cat_12_17_cat, section=14, mergeby=c( "incident_id", "arrestee_id"))
  s15 <- agg_percent_CAA_arrestee(leftdata = main_filter, rightdata = agg_arrestee_age_cat_2_uo18_arrestee_imp,    var=der_arrestee_age_cat_2_uo18,    section=15, mergeby=c( "incident_id", "arrestee_id"), denom=  der_total_denom)

  #Arrestee Hispanic Origin
  s16 <- agg_percent_arrestee(leftdata = main_filter, rightdata = agg_arrestee_ethnicity_arrestee, var=der_arrestee_ethnicity, section=16, mergeby=c( "incident_id", "arrestee_id"))
  
  #Arrestee race and Hispanic Origin
  s17 <- agg_percent_arrestee(leftdata = main_filter, rightdata = agg_arrestee_ethnicity_race_arrestee, var=der_arrestee_ethnicity_race, section=17, mergeby=c( "incident_id", "arrestee_id"))
  

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

createadditionalcolumns <- function(intotalcolumn, incolumnstart, colindex, insubset, inperm_num_series){
  #Create new symbol to subset data
  insymbol <- insubset %>% rlang:::parse_expr()
  
  if(colindex == 1){
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 1", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(1, 2, 3, 6, 7, 8)", column_number=1+inperm_num_series) #Cocaine/crack cocaine (A, B):  Buying/receiving
  } else if(colindex == 2) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 2", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(1, 2, 3, 6, 7, 8)", column_number=2+inperm_num_series) #Cocaine/crack cocaine (A, B):  Cultivating/manufacturing/publishing
  } else if(colindex == 3) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 3", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(1, 2, 3, 6, 7, 8)", column_number=3+inperm_num_series) #Cocaine/crack cocaine (A, B):  Distributing/selling
  } else if(colindex == 4) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 6", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(1, 2, 3, 6, 7, 8)", column_number=4+inperm_num_series) #Cocaine/crack cocaine (A, B):  Possessing/concealing
  } else if(colindex == 5) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 7", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(1, 2, 3, 6, 7, 8)", column_number=5+inperm_num_series) #Cocaine/crack cocaine (A, B):  Transporting/transmitting/importing
  } else if(colindex == 6) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 8", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(1, 2, 3, 6, 7, 8)", column_number=6+inperm_num_series) #Cocaine/crack cocaine (A, B):  Using/consuming
  } else if(colindex == 7) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 9", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(9, 10, 11, 14, 15, 16)", column_number=7+inperm_num_series) #Marijuana/hashish (C, E):  Buying/receiving
  } else if(colindex == 8) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 10", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(9, 10, 11, 14, 15, 16)", column_number=8+inperm_num_series) #Marijuana/hashish (C, E):  Cultivating/manufacturing/publishing
  } else if(colindex == 9) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 11", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(9, 10, 11, 14, 15, 16)", column_number=9+inperm_num_series) #Marijuana/hashish (C, E):  Distributing/selling
  } else if(colindex == 10) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 14", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(9, 10, 11, 14, 15, 16)", column_number=10+inperm_num_series) #Marijuana/hashish (C, E):  Possessing/concealing
  } else if(colindex == 11) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 15", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(9, 10, 11, 14, 15, 16)", column_number=11+inperm_num_series) #Marijuana/hashish (C, E):  Transporting/transmitting/importing
  } else if(colindex == 12) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 16", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(9, 10, 11, 14, 15, 16)", column_number=12+inperm_num_series) #Marijuana/hashish (C, E):  Using/consuming
  } else if(colindex == 13) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 17", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(17, 18, 19, 22, 23, 24)", column_number=13+inperm_num_series) #Opiate/narcotic (D, F, G, H):  Buying/receiving
  } else if(colindex == 14) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 18", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(17, 18, 19, 22, 23, 24)", column_number=14+inperm_num_series) #Opiate/narcotic (D, F, G, H):  Cultivating/manufacturing/publishing
  } else if(colindex == 15) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 19", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(17, 18, 19, 22, 23, 24)", column_number=15+inperm_num_series) #Opiate/narcotic (D, F, G, H):  Distributing/selling
  } else if(colindex == 16) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 22", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(17, 18, 19, 22, 23, 24)", column_number=16+inperm_num_series) #Opiate/narcotic (D, F, G, H):  Possessing/concealing
  } else if(colindex == 17) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 23", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(17, 18, 19, 22, 23, 24)", column_number=17+inperm_num_series) #Opiate/narcotic (D, F, G, H):  Transporting/transmitting/importing
  } else if(colindex == 18) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 24", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(17, 18, 19, 22, 23, 24)", column_number=18+inperm_num_series) #Opiate/narcotic (D, F, G, H):  Using/consuming
  } else if(colindex == 19) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 25", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(25, 26, 27, 30, 31, 32)", column_number=19+inperm_num_series) #Hallucinogen (I, J, K):  Buying/receiving
  } else if(colindex == 20) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 26", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(25, 26, 27, 30, 31, 32)", column_number=20+inperm_num_series) #Hallucinogen (I, J, K):  Cultivating/manufacturing/publishing
  } else if(colindex == 21) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 27", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(25, 26, 27, 30, 31, 32)", column_number=21+inperm_num_series) #Hallucinogen (I, J, K):  Distributing/selling
  } else if(colindex == 22) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 30", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(25, 26, 27, 30, 31, 32)", column_number=22+inperm_num_series) #Hallucinogen (I, J, K):  Possessing/concealing
  } else if(colindex == 23) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 31", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(25, 26, 27, 30, 31, 32)", column_number=23+inperm_num_series) #Hallucinogen (I, J, K):  Transporting/transmitting/importing
  } else if(colindex == 24) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 32", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(25, 26, 27, 30, 31, 32)", column_number=24+inperm_num_series) #Hallucinogen (I, J, K):  Using/consuming
  } else if(colindex == 25) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 33", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(33, 34, 35, 38, 39, 40)", column_number=25+inperm_num_series) #Stimulant (L, M):  Buying/receiving
  } else if(colindex == 26) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 34", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(33, 34, 35, 38, 39, 40)", column_number=26+inperm_num_series) #Stimulant (L, M):  Cultivating/manufacturing/publishing
  } else if(colindex == 27) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 35", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(33, 34, 35, 38, 39, 40)", column_number=27+inperm_num_series) #Stimulant (L, M):  Distributing/selling
  } else if(colindex == 28) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 38", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(33, 34, 35, 38, 39, 40)", column_number=28+inperm_num_series) #Stimulant (L, M):  Possessing/concealing
  } else if(colindex == 29) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 39", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(33, 34, 35, 38, 39, 40)", column_number=29+inperm_num_series) #Stimulant (L, M):  Transporting/transmitting/importing
  } else if(colindex == 30) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 40", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(33, 34, 35, 38, 39, 40)", column_number=30+inperm_num_series) #Stimulant (L, M):  Using/consuming
  } else if(colindex == 31) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 41", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(41, 42, 43, 46, 47, 48)", column_number=31+inperm_num_series) #Depressant (N, O):  Buying/receiving
  } else if(colindex == 32) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 42", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(41, 42, 43, 46, 47, 48)", column_number=32+inperm_num_series) #Depressant (N, O):  Cultivating/manufacturing/publishing
  } else if(colindex == 33) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 43", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(41, 42, 43, 46, 47, 48)", column_number=33+inperm_num_series) #Depressant (N, O):  Distributing/selling
  } else if(colindex == 34) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 46", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(41, 42, 43, 46, 47, 48)", column_number=34+inperm_num_series) #Depressant (N, O):  Possessing/concealing
  } else if(colindex == 35) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 47", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(41, 42, 43, 46, 47, 48)", column_number=35+inperm_num_series) #Depressant (N, O):  Transporting/transmitting/importing
  } else if(colindex == 36) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 48", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(41, 42, 43, 46, 47, 48)", column_number=36+inperm_num_series) #Depressant (N, O):  Using/consuming
  } else if(colindex == 37) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 49", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(49, 50, 51, 54, 55, 56)", column_number=37+inperm_num_series) #Other (P):  Buying/receiving
  } else if(colindex == 38) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 50", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(49, 50, 51, 54, 55, 56)", column_number=38+inperm_num_series) #Other (P):  Cultivating/manufacturing/publishing
  } else if(colindex == 39) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 51", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(49, 50, 51, 54, 55, 56)", column_number=39+inperm_num_series) #Other (P):  Distributing/selling
  } else if(colindex == 40) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 54", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(49, 50, 51, 54, 55, 56)", column_number=40+inperm_num_series) #Other (P):  Possessing/concealing
  } else if(colindex == 41) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 55", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(49, 50, 51, 54, 55, 56)", column_number=41+inperm_num_series) #Other (P):  Transporting/transmitting/importing
  } else if(colindex == 42) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 56", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(49, 50, 51, 54, 55, 56)", column_number=42+inperm_num_series) #Other (P):  Using/consuming
  } else if(colindex == 43) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 57", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(57, 58, 59, 62, 63, 64)", column_number=43+inperm_num_series) #Unknown (U):  Buying/receiving
  } else if(colindex == 44) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 58", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(57, 58, 59, 62, 63, 64)", column_number=44+inperm_num_series) #Unknown (U):  Cultivating/manufacturing/publishing
  } else if(colindex == 45) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 59", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(57, 58, 59, 62, 63, 64)", column_number=45+inperm_num_series) #Unknown (U):  Distributing/selling
  } else if(colindex == 46) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 62", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(57, 58, 59, 62, 63, 64)", column_number=46+inperm_num_series) #Unknown (U):  Possessing/concealing
  } else if(colindex == 47) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 63", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(57, 58, 59, 62, 63, 64)", column_number=47+inperm_num_series) #Unknown (U):  Transporting/transmitting/importing
  } else if(colindex == 48) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 64", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(57, 58, 59, 62, 63, 64)", column_number=48+inperm_num_series) #Unknown (U):  Using/consuming
  } else if(colindex == 49) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 65", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(65, 66, 67, 70, 71, 72)", column_number=49+inperm_num_series) #More Than 3 Types (X):  Buying/receiving
  } else if(colindex == 50) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 66", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(65, 66, 67, 70, 71, 72)", column_number=50+inperm_num_series) #More Than 3 Types (X):  Cultivating/manufacturing/publishing
  } else if(colindex == 51) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 67", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(65, 66, 67, 70, 71, 72)", column_number=51+inperm_num_series) #More Than 3 Types (X):  Distributing/selling
  } else if(colindex == 52) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 70", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(65, 66, 67, 70, 71, 72)", column_number=52+inperm_num_series) #More Than 3 Types (X):  Possessing/concealing
  } else if(colindex == 53) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 71", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(65, 66, 67, 70, 71, 72)", column_number=53+inperm_num_series) #More Than 3 Types (X):  Transporting/transmitting/importing
  } else if(colindex == 54) {
    temp <- generate_est(maindata=main %>% filter(!!insymbol), subsetvareq1 = "der_suspected_type_of_drug_crim_activity == 72", subsetvareq2="der_suspected_type_of_drug_crim_activity %in%c(65, 66, 67, 70, 71, 72)", column_number=54+inperm_num_series) #More Than 3 Types (X):  Using/consuming	
  }
  return(temp)
}