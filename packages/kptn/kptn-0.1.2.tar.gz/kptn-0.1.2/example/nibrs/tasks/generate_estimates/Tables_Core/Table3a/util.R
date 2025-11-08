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
    der_victim_gender %in% c(1:3) & section == 6,  der_victim_gender + 14,
    der_victim_race %in% c(1:6),  der_victim_race + 17,
    der_victim_offender_age_1_4 %in% c(1:5),  der_victim_offender_age_1_4 + 23,
    der_victim_offender_gender_1_4 %in% c(1:5),  der_victim_offender_gender_1_4 + 28,
    der_victim_offender_race_1_10 %in% c(1:11),  der_victim_offender_race_1_10 + 33,

    der_victim_gender == 1 & section == 12 ,   45,
    der_victim_gender_race %in% c(1:6),  der_victim_gender_race + 45,
    der_victim_gender == 2 & section == 12 ,   52,
    der_victim_gender_race %in% c(7:12),  der_victim_gender_race + 52 - 6,
    der_victim_gender == 3 & section == 12 ,   59,
    der_victim_gender_race %in% c(13:18),  der_victim_gender_race + 59 - 12,

    der_weapon_no_yes %in% c(1:2),  der_weapon_no_yes + 65,
    der_weapon_yes_cat %in% c(1:6),  der_weapon_yes_cat + 67,
    der_injury_no_yes %in% c(1:2),  der_injury_no_yes + 73,
    der_relationship %in% c(1:6),  der_relationship + 75,
    der_gang_cat_no_yes %in% c(1:2),  der_gang_cat_no_yes + 81,
    der_victim_age_cat_under18_2 %in% c(1:2), der_victim_age_cat_under18_2 + 83, ##Under 12, 12-17
    der_victim_age_cat_12_17_cat %in% c(1:2), der_victim_age_cat_12_17_cat + 85, #12-14, 15-17
    der_victim_age_cat_2_uo18 %in% c(2), 88, #2, #18+
    der_victim_age_cat_2_uo18 %in% c(3), 89, #3, #Unknown
    der_relationship2 %in% c(1:5), der_relationship2 + 89,
    der_clearance_cat %in% c(1:3),  der_clearance_cat + 94,
    der_exceptional_clearance %in% c(1:5),  der_exceptional_clearance + 97,
    der_weapon_yes_cat2 == 1, 103, #1= Firearms or Explosives
    der_weapon_subset_firearm == 1, 104,
    der_weapon_yes_cat2 == 2, 105, #2= Another weapon other than firearms or explosives
    der_weapon_subset_knives == 1,  106,
    der_weapon_yes_cat2 == 3, 107, #3= Unknown
    
    #Weapon involved hierarchy
    section == 27 & der_raw_weapon_hierarchy_recode %in% c(1:18),  der_raw_weapon_hierarchy_recode + 107,
    
    #Victim-offender relationship hierarchy
    der_relationship_hierarchy %in% c(1:8),  der_relationship_hierarchy + 125,
    
    #Location type hierarchy within offense
    der_location_residence %in% c(1:2), der_location_residence + 133, 
    
    #Weapon involved hierarchy within offense
    section == 30 & der_raw_weapon_hierarchy_recode %in% c(1:18),  der_raw_weapon_hierarchy_recode + 135,
    
    #Number of Victims Summarized at Incident Level Within Offense
    der_inc_number_of_victims_cat %in% c(1:4), der_inc_number_of_victims_cat + 153,
    
    #Weapon involved - Yes 3
    der_raw_weapon_recode_4_level %in% c(1:4), der_raw_weapon_recode_4_level + 157,
    
    #Victim Hispanic Origin
    der_victim_ethnicity %in% c(1:3), der_victim_ethnicity + 161,
    
    #Victim race and Hispanic Origin
    der_victim_ethnicity_race %in% c(1:7), der_victim_ethnicity_race + 164
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
    row %in% c(24:28),  5,
    row %in% c(29:33),  6,
    row %in% c(34:44),  7,
    row %in% c(45:65),  8,
    row %in% c(66:73),  9,
    row %in% c(74:75),  10,
    row %in% c(76:81),  11,
    row %in% c(82:83),  12,
    row %in% c(84:89),  13,
    row %in% c(90:94),  14,
    row %in% c(95:102),  15,
	  row %in% c(103:107),  16,
    row %in% c(108:125),  17,
    row %in% c(126:133),  18,
	  row %in% c(134:135),  19,
    row %in% c(136:153),  20,
    row %in% c(154:157),  21,
    row %in% c(158:161),  22,
    row %in% c(162:164),  23,
    row %in% c(165:171),  24
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
    row == 2,  'Victimization count: Law enforcement officers ',
    row == 3,  'Victimization rate (per 100k total pop)',
    row == 4,  'Victimization rate (per 100k LE staff): Law enforcement officers',
    row == 5,  'Victim Age: Under 5',
    row == 6,  'Victim Age: 5-14',
    row == 7,  'Victim Age: 15',
    row == 8,  'Victim Age: 16',
    row == 9,  'Victim Age: 17',
    row == 10,  'Victim Age: 18-24',
    row == 11,  'Victim Age: 25-34',
    row == 12,  'Victim Age: 35-64',
    row == 13,  'Victim Age: 65+',
    row == 14,  'Victim Age: Unknown',
    row == 15,  'Victim sex: Male',
    row == 16,  'Victim sex: Female',
    row == 17,  'Victim sex: Unknown',
    row == 18,  'Victim race: White',
    row == 19,  'Victim race: Black',
    row == 20,  'Victim race: American Indian or Alaska Native',
    row == 21,  'Victim race: Asian',
    row == 22,  'Victim race: Native Hawaiian or Other Pacific Islander',
    row == 23,  'Victim race: Unknown',
    row == 24,  'Victim age category by offender age category: Victim juvenile X Offender juvenile',
    row == 25,  'Victim age category by offender age category: Victim juvenile X Offender adult',
    row == 26,  'Victim age category by offender age category: Victim adult X Offender adult',
    row == 27,  'Victim age category by offender age category: Victim adult X Offender juvenile',
    row == 28,  'Victim age category by offender age category: Unknown victim age or unknown offender age',
    row == 29,  'Victim sex by offender sex: Victim male X Offender male',
    row == 30,  'Victim sex by offender sex: Victim male X Offender female',
    row == 31,  'Victim sex by offender sex: Victim female X Offender female',
    row == 32,  'Victim sex by offender sex: Victim female X Offender male',
    row == 33,  'Victim sex by offender sex: Unknown victim sex or unknown offender sex',
    row == 34,  'Victim race by offender race: Victim White X Offender White',
    row == 35,  'Victim race by offender race: Victim White X Offender All Other Races Except White',
    row == 36,  'Victim race by offender race: Victim Black X Offender Black',
    row == 37,  'Victim race by offender race: Victim Black X Offender All Other Races Except Black',
    row == 38,  'Victim race by offender race: Victim AIAN X Offender AIAN',
    row == 39,  'Victim race by offender race: Victim AIAN X Offender All Other Races Except AIAN',
    row == 40,  'Victim race by offender race: Victim Asian X Offender Asian',
    row == 41,  'Victim race by offender race: Victim Asian X Offender All Other Races Except Asian',
    row == 42,  'Victim race by offender race: Victim NHOPI X Offender NHOPI',
    row == 43,  'Victim race by offender race: Victim NHOPI X Offender All Other Races Except NHOPI',
    row == 44,  'Victim race by offender race: Unknown victim race or unknown offender race',
    row == 45,  'Victim sex and race: Male',
    row == 46,  'Victim sex and race Male: White',
    row == 47,  'Victim sex and race Male: Black',
    row == 48,  'Victim sex and race Male: American Indian or Alaska Native',
    row == 49,  'Victim sex and race Male: Asian',
    row == 50,  'Victim sex and race Male: Native Hawaiian or Other Pacific Islander',
    row == 51,  'Victim sex and race Male: Unknown',
    row == 52,  'Victim sex and race: Female',
    row == 53,  'Victim sex and race Female: White',
    row == 54,  'Victim sex and race Female: Black',
    row == 55,  'Victim sex and race Female: American Indian or Alaska Native',
    row == 56,  'Victim sex and race Female: Asian',
    row == 57,  'Victim sex and race Female: Native Hawaiian or Other Pacific Islander',
    row == 58,  'Victim sex and race Female: Unknown',
    row == 59,  'Victim sex and race: Unknown',
    row == 60,  'Victim sex and race Unknown: White',
    row == 61,  'Victim sex and race Unknown: Black',
    row == 62,  'Victim sex and race Unknown: American Indian or Alaska Native',
    row == 63,  'Victim sex and race Unknown: Asian',
    row == 64,  'Victim sex and race Unknown: Native Hawaiian or Other Pacific Islander',
    row == 65,  'Victim sex and race Unknown: Unknown',
    row == 66,  'Weapon involved: No',
    row == 67,  'Weapon involved: Yes',
    row == 68,  'Weapon involved: Personal weapons',
    row == 69,  'Weapon involved: Firearms',
    row == 70,  'Weapon involved: Knives and other cutting instruments',
    row == 71,  'Weapon involved: Blunt instruments',
    row == 72,  'Weapon involved: Other non-personal weapons',
    row == 73,  'Weapon involved: Unknown',
    row == 74,  'Injury: No',
    row == 75,  'Injury: Yes',
    row == 76,  'Victim-offender relationship: Intimate partner',
    row == 77,  'Victim-offender relationship: Other family',
    row == 78,  'Victim-offender relationship: Outside family but known to victim',
    row == 79,  'Victim-offender relationship: Stranger',
    row == 80,  'Victim-offender relationship: Victim was Offender',
    row == 81,  'Victim-offender relationship: Unknown relationship',
    row == 82,  'Gang involvement: No',
    row == 83,  'Gang involvement: Yes',
    row == 84, 'Victim Age 2: Under 12',
    row == 85, 'Victim Age 2: 12-17',
    row == 86, 'Victim Age 2: 12-14',
    row == 87, 'Victim Age 2: 15-17',
    row == 88, 'Victim Age 2: 18+',
    row == 89, 'Victim Age 2: Unknown',
    row == 90, 'Victim-offender relationship 2: Intimate partner plus Family',
    row == 91, 'Victim-offender relationship 2: Outside family but known to victim',
    row == 92, 'Victim-offender relationship 2: Stranger',
    row == 93, 'Victim-offender relationship 2: Victim was Offender',
    row == 94, 'Victim-offender relationship 2: Unknown relationship',
    row == 95, 'Clearance: Not cleared',
    row == 96, 'Clearance: Cleared through arrest',
    row == 97, 'Clearance: Exceptional clearance',
    row == 98, 'Clearance: Death of offender',
    row == 99, 'Clearance: Prosecution declined',
    row == 100, 'Clearance: In custody of other jurisdiction',
    row == 101, 'Clearance: Victim refused to cooperate',
    row == 102, 'Clearance: Juvenile/no custody',
    row == 103, 'Weapon involved - Yes 2: Firearms or Explosives',
    row == 104, 'Weapon involved - Yes 2: Firearms',
    row == 105, 'Weapon involved - Yes 2: Another weapon other than firearms or explosives',
    row == 106, 'Weapon involved - Yes 2: Knives and other cutting instruments',
    row == 107, 'Weapon involved - Yes 2: Unknown',
    row == 108, 'Weapon involved hierarchy: Handgun',
    row == 109, 'Weapon involved hierarchy: Firearm',
    row == 110, 'Weapon involved hierarchy: Rifle',
    row == 111, 'Weapon involved hierarchy: Shotgun',
    row == 112, 'Weapon involved hierarchy: Other Firearm',
    row == 113, 'Weapon involved hierarchy: Knife/Cutting Instrument',
    row == 114, 'Weapon involved hierarchy: Blunt Object',
    row == 115, 'Weapon involved hierarchy: Motor Vehicle',
    row == 116, 'Weapon involved hierarchy: Personal Weapons (hands, feet, teeth, etc.)',
    row == 117, 'Weapon involved hierarchy: Asphyxiation',
    row == 118, 'Weapon involved hierarchy: Drugs/Narcotics/Sleeping Pills',
    row == 119, 'Weapon involved hierarchy: Poison (include gas)',
    row == 120, 'Weapon involved hierarchy: Explosives',
    row == 121, 'Weapon involved hierarchy: Fire/Incendiary Device',
    row == 122, 'Weapon involved hierarchy: Other',
    row == 123, 'Weapon involved hierarchy: No Weapon',
    row == 124, 'Weapon involved hierarchy: Unknown',
    row == 125, 'Weapon involved hierarchy: Not Applicable',
    row == 126, 'Victim-offender relationship hierarchy: Intimate partner',
    row == 127, 'Victim-offender relationship hierarchy: Other family',
    row == 128, 'Victim-offender relationship hierarchy: Outside family but known to victim',
    row == 129, 'Victim-offender relationship hierarchy: Stranger',
    row == 130, 'Victim-offender relationship hierarchy: Victim was Offender',
    row == 131, 'Victim-offender relationship hierarchy: Unknown relationship',
    row == 132, 'Victim-offender relationship hierarchy: Unknown Offender Incidents',
    row == 133, 'Victim-offender relationship hierarchy: Missing from Uncleared Incidents',
    row == 134, 'Location type hierarchy within offense: Residence',
    row == 135, 'Location type hierarchy within offense: Not residence',
    row == 136, 'Weapon involved hierarchy within offense: Handgun',
    row == 137, 'Weapon involved hierarchy within offense: Firearm',
    row == 138, 'Weapon involved hierarchy within offense: Rifle',
    row == 139, 'Weapon involved hierarchy within offense: Shotgun',
    row == 140, 'Weapon involved hierarchy within offense: Other Firearm',
    row == 141, 'Weapon involved hierarchy within offense: Knife/Cutting Instrument',
    row == 142, 'Weapon involved hierarchy within offense: Blunt Object',
    row == 143, 'Weapon involved hierarchy within offense: Motor Vehicle',
    row == 144, 'Weapon involved hierarchy within offense: Personal Weapons (hands, feet, teeth, etc.)',
    row == 145, 'Weapon involved hierarchy within offense: Asphyxiation',
    row == 146, 'Weapon involved hierarchy within offense: Drugs/Narcotics/Sleeping Pills',
    row == 147, 'Weapon involved hierarchy within offense: Poison (include gas)',
    row == 148, 'Weapon involved hierarchy within offense: Explosives',
    row == 149, 'Weapon involved hierarchy within offense: Fire/Incendiary Device',
    row == 150, 'Weapon involved hierarchy within offense: Other',
    row == 151, 'Weapon involved hierarchy within offense: No Weapon',
    row == 152, 'Weapon involved hierarchy within offense: Unknown',
    row == 153, 'Weapon involved hierarchy within offense: Not Applicable',
    row == 154, 'Number of Victims Summarized at Incident Level Within Offense: 1',
    row == 155, 'Number of Victims Summarized at Incident Level Within Offense: 2',
    row == 156, 'Number of Victims Summarized at Incident Level Within Offense: 3',
    row == 157, 'Number of Victims Summarized at Incident Level Within Offense: 4+',
    row == 158, 'Weapon involved - Yes 3: Personal weapons',
    row == 159, 'Weapon involved - Yes 3: Firearms',
    row == 160, 'Weapon involved - Yes 3: Other non-personal',
    row == 161, 'Weapon involved - Yes 3: Unknown',
    row == 162, 'Victim Hispanic Origin: Hispanic or Latino',
    row == 163, 'Victim Hispanic Origin: Not Hispanic or Latino',
    row == 164, 'Victim Hispanic Origin: Unknown',
    row == 165, 'Victim race and Hispanic Origin: Hispanic or Latino',
    row == 166, 'Victim race and Hispanic Origin: Non-Hispanic, White',
    row == 167, 'Victim race and Hispanic Origin: Non-Hispanic, Black',
    row == 168, 'Victim race and Hispanic Origin: Non-Hispanic, American Indian or Alaska Native',
    row == 169, 'Victim race and Hispanic Origin: Non-Hispanic, Asian',
    row == 170, 'Victim race and Hispanic Origin: Non-Hispanic, Native Hawaiian or Other Pacific Islander',
    row == 171, 'Victim race and Hispanic Origin: Unknown race or Hispanic origin'
    

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
    column == 17,  'Robbery',
    column == 18,  'NIBRS crimes against property (Total)',
    column == 19,  'Arson',
    column == 20,  'Bribery',
    column == 21,  'Burglary/B&E',
    column == 22,  'Counterfeiting/Forgery',
    column == 23,  'Destruction/Damage/Vandalism',
    column == 24,  'Embezzlement',
    column == 25,  'Extortion/Blackmail',
    column == 26,  'Fraud Offenses',
    column == 27,  'Larceny/Theft Offenses',
    column == 28,  'Motor Vehicle Theft',
    column == 29,  'Stolen Property Offenses',
    column == 30,  'Property Crime',
    column == 31,  'Car Jacking',
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
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 5,  'Victim Level', #Victim Age: Under 5
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 6,  'Victim Level', #Victim Age: 5-14
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 7,  'Victim Level', #Victim Age: 15
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 8,  'Victim Level', #Victim Age: 16
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 9,  'Victim Level', #Victim Age: 17
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 10,  'Victim Level', #Victim Age: 18-24
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 11,  'Victim Level', #Victim Age: 25-34
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 12,  'Victim Level', #Victim Age: 35-64
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 13,  'Victim Level', #Victim Age: 65+
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 14,  'Victim Level', #Victim Age: Unknown
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 15,  'Victim Level', #Victim sex: Male
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 16,  'Victim Level', #Victim sex: Female
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 17,  'Victim Level', #Victim sex: Unknown
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 18,  'Victim Level', #Victim race: White
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 19,  'Victim Level', #Victim race: Black
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 20,  'Victim Level', #Victim race: American Indian or Alaska Native
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 21,  'Victim Level', #Victim race: Asian
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 22,  'Victim Level', #Victim race: Native Hawaiian or Other Pacific Islander
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 23,  'Victim Level', #Victim race: Unknown
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 24,  'Victim Level', #Victim age category by offender age category: Victim juvenile X Offender juvenile
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 25,  'Victim Level', #Victim age category by offender age category: Victim juvenile X Offender adult
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 26,  'Victim Level', #Victim age category by offender age category: Victim adult X Offender adult
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 27,  'Victim Level', #Victim age category by offender age category: Victim adult X Offender juvenile
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 28,  'Victim Level', #Victim age category by offender age category: Unknown victim age or unknown offender age
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 29,  'Victim Level', #Victim sex by offender sex: Victim male X Offender male
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 30,  'Victim Level', #Victim sex by offender sex: Victim male X Offender female
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 31,  'Victim Level', #Victim sex by offender sex: Victim female X Offender female
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 32,  'Victim Level', #Victim sex by offender sex: Victim female X Offender male
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 33,  'Victim Level', #Victim sex by offender sex: Unknown victim sex or unknown offender sex
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 34,  'Victim Level', #Victim race by offender race: Victim White X Offender White
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 35,  'Victim Level', #Victim race by offender race: Victim White X Offender non-White
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 36,  'Victim Level', #Victim race by offender race: Victim Black X Offender Black
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 37,  'Victim Level', #Victim race by offender race: Victim Black X Offender non-Black
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 38,  'Victim Level', #Victim race by offender race: Victim AIAN X Offender AIAN
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 39,  'Victim Level', #Victim race by offender race: Victim AIAN X Offender non-AIAN
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 40,  'Victim Level', #Victim race by offender race: Victim Asian X Offender Asian
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 41,  'Victim Level', #Victim race by offender race: Victim Asian X Offender non-Asian
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 42,  'Victim Level', #Victim race by offender race: Victim NHOPI X Offender NHOPI
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 43,  'Victim Level', #Victim race by offender race: Victim NHOPI X Offender non-NHOPI
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 44,  'Victim Level', #Victim race by offender race: Unknown victim race or unknown offender race
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 45,  'Victim Level', #Victim sex and race: Male
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 46,  'Victim Level subset to male', #Victim sex and race Male: White
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 47,  'Victim Level subset to male', #Victim sex and race Male: Black
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 48,  'Victim Level subset to male', #Victim sex and race Male: American Indian or Alaska Native
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 49,  'Victim Level subset to male', #Victim sex and race Male: Asian
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 50,  'Victim Level subset to male', #Victim sex and race Male: Native Hawaiian or Other Pacific Islander
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 51,  'Victim Level subset to male', #Victim sex and race Male: Unknown
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 52,  'Victim Level', #Victim sex and race: Female
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 53,  'Victim Level subset to female', #Victim sex and race Female: White
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 54,  'Victim Level subset to female', #Victim sex and race Female: Black
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 55,  'Victim Level subset to female', #Victim sex and race Female: American Indian or Alaska Native
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 56,  'Victim Level subset to female', #Victim sex and race Female: Asian
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 57,  'Victim Level subset to female', #Victim sex and race Female: Native Hawaiian or Other Pacific Islander
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 58,  'Victim Level subset to female', #Victim sex and race Female: Unknown
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 59,  'Victim Level', #Victim sex and race: Unknown
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 60,  'Victim Level subset to unknown gender', #Victim sex and race Unknown: White
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 61,  'Victim Level subset to unknown gender', #Victim sex and race Unknown: Black
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 62,  'Victim Level subset to unknown gender', #Victim sex and race Unknown: American Indian or Alaska Native
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 63,  'Victim Level subset to unknown gender', #Victim sex and race Unknown: Asian
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 64,  'Victim Level subset to unknown gender', #Victim sex and race Unknown: Native Hawaiian or Other Pacific Islander
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 65,  'Victim Level subset to unknown gender', #Victim sex and race Unknown: Unknown
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 66,  'Victim Level', #Weapon involved: No
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 67,  'Victim Level', #Weapon involved: Yes
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 68,  'Victim Level subset to weapon involved yes', #Weapon involved: Personal weapons
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 69,  'Victim Level subset to weapon involved yes', #Weapon involved: Firearms
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 70,  'Victim Level subset to weapon involved yes', #Weapon involved: Knives and other cutting instruments
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 71,  'Victim Level subset to weapon involved yes', #Weapon involved: Blunt instruments
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 72,  'Victim Level subset to weapon involved yes', #Weapon involved: Other non-personal weapons
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 73,  'Victim Level subset to weapon involved yes', #Weapon involved: Unknown
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 74,  'Victim Level', #Injury: No
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 75,  'Victim Level', #Injury: Yes
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 76,  'Victim Level', #Victim-offender relationship: Intimate partner
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 77,  'Victim Level', #Victim-offender relationship: Other family
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 78,  'Victim Level', #Victim-offender relationship: Outside family but known to victim
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 79,  'Victim Level', #Victim-offender relationship: Stranger
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 80,  'Victim Level', #Victim-offender relationship: Victim was Offender
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 81,  'Victim Level', #Victim-offender relationship: Unknown relationship
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 82,  'Victim Level', #Gang involvement: No
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 83,  'Victim Level', #Gang involvement: Yes
    
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 84, 'Victim Level', #Victim Age 2: Under 12
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 85, 'Victim Level', #Victim Age 2: 12-17
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 86, 'Victim Level subset to 12-17', #Victim Age 2: 12-14
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 87, 'Victim Level subset to 12-17', #Victim Age 2: 15-17
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 88, 'Victim Level', #Victim Age 2: 18+
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 89, 'Victim Level', #Victim Age 2: Unknown
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 90, 'Victim Level', #Victim-offender relationship 2: Intimate partner plus Family
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 91, 'Victim Level', #Victim-offender relationship 2: Outside family but known to victim
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 92, 'Victim Level', #Victim-offender relationship 2: Stranger
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 93, 'Victim Level', #Victim-offender relationship 2: Victim was Offender
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 94, 'Victim Level', #Victim-offender relationship 2: Unknown relationship
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 95, 'Victim Level', #Clearance: Not cleared
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 96, 'Victim Level', #Clearance: Cleared through arrest
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 97, 'Victim Level', #Clearance: Exceptional clearance
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 98, 'Victim Level subset to exceptional clearance', #Clearance: Death of offender
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 99, 'Victim Level subset to exceptional clearance', #Clearance: Prosecution declined
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 100, 'Victim Level subset to exceptional clearance', #Clearance: In custody of other jurisdiction
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 101, 'Victim Level subset to exceptional clearance', #Clearance: Victim refused to cooperate
    trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 102, 'Victim Level subset to exceptional clearance', #Clearance: Juvenile/no custody
	
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 103, 'Victim Level subset to weapon involved yes', #Weapon involved - Yes 2: Firearms or Explosives
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 104, 'Victim Level subset to weapon involved yes and firearms or explosives', #Weapon involved - Yes 2: Firearms
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 105, 'Victim Level subset to weapon involved yes', #Weapon involved - Yes 2: Another weapon other than firearms or explosives
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 106, 'Victim Level subset to weapon involved yes and another weapon other than firearms or explosives', #Weapon involved - Yes 2: Knives and other cutting instruments
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 107, 'Victim Level subset to weapon involved yes', #Weapon involved - Yes 2: Unknown
		
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 108, 'Victim Level', #Weapon involved hierarchy: Handgun
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 109, 'Victim Level', #Weapon involved hierarchy: Firearm
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 110, 'Victim Level', #Weapon involved hierarchy: Rifle
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 111, 'Victim Level', #Weapon involved hierarchy: Shotgun
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 112, 'Victim Level', #Weapon involved hierarchy: Other Firearm
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 113, 'Victim Level', #Weapon involved hierarchy: Knife/Cutting Instrument
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 114, 'Victim Level', #Weapon involved hierarchy: Blunt Object
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 115, 'Victim Level', #Weapon involved hierarchy: Motor Vehicle
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 116, 'Victim Level', #Weapon involved hierarchy: Personal Weapons (hands, feet, teeth, etc.)
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 117, 'Victim Level', #Weapon involved hierarchy: Asphyxiation
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 118, 'Victim Level', #Weapon involved hierarchy: Drugs/Narcotics/Sleeping Pills
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 119, 'Victim Level', #Weapon involved hierarchy: Poison (include gas)
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 120, 'Victim Level', #Weapon involved hierarchy: Explosives
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 121, 'Victim Level', #Weapon involved hierarchy: Fire/Incendiary Device
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 122, 'Victim Level', #Weapon involved hierarchy: Other
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 123, 'Victim Level', #Weapon involved hierarchy: No Weapon
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 124, 'Victim Level', #Weapon involved hierarchy: Unknown
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 125, 'Victim Level', #Weapon involved hierarchy: Not Applicable
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 126, 'Victim Level', #Victim-offender relationship hierarchy: Intimate partner
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 127, 'Victim Level', #Victim-offender relationship hierarchy: Other family
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 128, 'Victim Level', #Victim-offender relationship hierarchy: Outside family but known to victim
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 129, 'Victim Level', #Victim-offender relationship hierarchy: Stranger
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 130, 'Victim Level', #Victim-offender relationship hierarchy: Victim was Offender
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 131, 'Victim Level', #Victim-offender relationship hierarchy: Unknown relationship
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 132, 'Victim Level', #Victim-offender relationship hierarchy: Unknown Offender Incidents
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 133, 'Victim Level', #Victim-offender relationship hierarchy: Missing from Uncleared Incidents
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 134, 'Victim Level', #Location type hierarchy within offense: Residence
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 135, 'Victim Level', #Location type hierarchy within offense: Not residence
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 136, 'Victim Level', #Weapon involved hierarchy within offense: Handgun
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 137, 'Victim Level', #Weapon involved hierarchy within offense: Firearm
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 138, 'Victim Level', #Weapon involved hierarchy within offense: Rifle
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 139, 'Victim Level', #Weapon involved hierarchy within offense: Shotgun
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 140, 'Victim Level', #Weapon involved hierarchy within offense: Other Firearm
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 141, 'Victim Level', #Weapon involved hierarchy within offense: Knife/Cutting Instrument
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 142, 'Victim Level', #Weapon involved hierarchy within offense: Blunt Object
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 143, 'Victim Level', #Weapon involved hierarchy within offense: Motor Vehicle
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 144, 'Victim Level', #Weapon involved hierarchy within offense: Personal Weapons (hands, feet, teeth, etc.)
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 145, 'Victim Level', #Weapon involved hierarchy within offense: Asphyxiation
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 146, 'Victim Level', #Weapon involved hierarchy within offense: Drugs/Narcotics/Sleeping Pills
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 147, 'Victim Level', #Weapon involved hierarchy within offense: Poison (include gas)
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 148, 'Victim Level', #Weapon involved hierarchy within offense: Explosives
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 149, 'Victim Level', #Weapon involved hierarchy within offense: Fire/Incendiary Device
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 150, 'Victim Level', #Weapon involved hierarchy within offense: Other
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 151, 'Victim Level', #Weapon involved hierarchy within offense: No Weapon
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 152, 'Victim Level', #Weapon involved hierarchy within offense: Unknown
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 153, 'Victim Level', #Weapon involved hierarchy within offense: Not Applicable
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 154, 'Incident Level', #Number of Victims Summarized at Incident Level Within Offense: 1
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 155, 'Incident Level', #Number of Victims Summarized at Incident Level Within Offense: 2
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 156, 'Incident Level', #Number of Victims Summarized at Incident Level Within Offense: 3
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 157, 'Incident Level', #Number of Victims Summarized at Incident Level Within Offense: 4+
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 158, 'Victim Level subset to weapon involved yes', #Weapon involved - Yes 3: Personal weapons
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 159, 'Victim Level subset to weapon involved yes', #Weapon involved - Yes 3: Firearms
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 160, 'Victim Level subset to weapon involved yes', #Weapon involved - Yes 3: Other non-personal
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 161, 'Victim Level subset to weapon involved yes', #Weapon involved - Yes 3: Unknown
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 162, 'Victim Level', #Victim Hispanic Origin: Hispanic or Latino
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 163, 'Victim Level', #Victim Hispanic Origin: Not Hispanic or Latino
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 164, 'Victim Level', #Victim Hispanic Origin: Unknown
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 165, 'Victim Level', #Victim race and Hispanic Origin: Hispanic or Latino
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 166, 'Victim Level', #Victim race and Hispanic Origin: Non-Hispanic, White
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 167, 'Victim Level', #Victim race and Hispanic Origin: Non-Hispanic, Black
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 168, 'Victim Level', #Victim race and Hispanic Origin: Non-Hispanic, American Indian or Alaska Native
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 169, 'Victim Level', #Victim race and Hispanic Origin: Non-Hispanic, Asian
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 170, 'Victim Level', #Victim race and Hispanic Origin: Non-Hispanic, Native Hawaiian or Other Pacific Islander
	trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 171, 'Victim Level' #Victim race and Hispanic Origin: Unknown race or Hispanic origin
	
	
		
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
    trim_upcase(estimate_type) %in% c('RATE') & row == 5,  DER_NA_CODE_STRING, #Victim Age: Under 5
    trim_upcase(estimate_type) %in% c('RATE') & row == 6,  DER_NA_CODE_STRING, #Victim Age: 5-14
    trim_upcase(estimate_type) %in% c('RATE') & row == 7,  DER_NA_CODE_STRING, #Victim Age: 15
    trim_upcase(estimate_type) %in% c('RATE') & row == 8,  DER_NA_CODE_STRING, #Victim Age: 16
    trim_upcase(estimate_type) %in% c('RATE') & row == 9,  DER_NA_CODE_STRING, #Victim Age: 17
    trim_upcase(estimate_type) %in% c('RATE') & row == 10,  DER_NA_CODE_STRING, #Victim Age: 18-24
    trim_upcase(estimate_type) %in% c('RATE') & row == 11,  DER_NA_CODE_STRING, #Victim Age: 25-34
    trim_upcase(estimate_type) %in% c('RATE') & row == 12,  DER_NA_CODE_STRING, #Victim Age: 35-64
    trim_upcase(estimate_type) %in% c('RATE') & row == 13,  DER_NA_CODE_STRING, #Victim Age: 65+
    trim_upcase(estimate_type) %in% c('RATE') & row == 14,  DER_NA_CODE_STRING, #Victim Age: Unknown
    trim_upcase(estimate_type) %in% c('RATE') & row == 15,  DER_NA_CODE_STRING, #Victim sex: Male
    trim_upcase(estimate_type) %in% c('RATE') & row == 16,  DER_NA_CODE_STRING, #Victim sex: Female
    trim_upcase(estimate_type) %in% c('RATE') & row == 17,  DER_NA_CODE_STRING, #Victim sex: Unknown
    trim_upcase(estimate_type) %in% c('RATE') & row == 18,  DER_NA_CODE_STRING, #Victim race: White
    trim_upcase(estimate_type) %in% c('RATE') & row == 19,  DER_NA_CODE_STRING, #Victim race: Black
    trim_upcase(estimate_type) %in% c('RATE') & row == 20,  DER_NA_CODE_STRING, #Victim race: American Indian or Alaska Native
    trim_upcase(estimate_type) %in% c('RATE') & row == 21,  DER_NA_CODE_STRING, #Victim race: Asian
    trim_upcase(estimate_type) %in% c('RATE') & row == 22,  DER_NA_CODE_STRING, #Victim race: Native Hawaiian or Other Pacific Islander
    trim_upcase(estimate_type) %in% c('RATE') & row == 23,  DER_NA_CODE_STRING, #Victim race: Unknown
    trim_upcase(estimate_type) %in% c('RATE') & row == 24,  DER_NA_CODE_STRING, #Victim age category by offender age category: Victim juvenile X Offender juvenile
    trim_upcase(estimate_type) %in% c('RATE') & row == 25,  DER_NA_CODE_STRING, #Victim age category by offender age category: Victim juvenile X Offender adult
    trim_upcase(estimate_type) %in% c('RATE') & row == 26,  DER_NA_CODE_STRING, #Victim age category by offender age category: Victim adult X Offender adult
    trim_upcase(estimate_type) %in% c('RATE') & row == 27,  DER_NA_CODE_STRING, #Victim age category by offender age category: Victim adult X Offender juvenile
    trim_upcase(estimate_type) %in% c('RATE') & row == 28,  DER_NA_CODE_STRING, #Victim age category by offender age category: Unknown victim age or unknown offender age
    trim_upcase(estimate_type) %in% c('RATE') & row == 29,  DER_NA_CODE_STRING, #Victim sex by offender sex: Victim male X Offender male
    trim_upcase(estimate_type) %in% c('RATE') & row == 30,  DER_NA_CODE_STRING, #Victim sex by offender sex: Victim male X Offender female
    trim_upcase(estimate_type) %in% c('RATE') & row == 31,  DER_NA_CODE_STRING, #Victim sex by offender sex: Victim female X Offender female
    trim_upcase(estimate_type) %in% c('RATE') & row == 32,  DER_NA_CODE_STRING, #Victim sex by offender sex: Victim female X Offender male
    trim_upcase(estimate_type) %in% c('RATE') & row == 33,  DER_NA_CODE_STRING, #Victim sex by offender sex: Unknown victim sex or unknown offender sex
    trim_upcase(estimate_type) %in% c('RATE') & row == 34,  DER_NA_CODE_STRING, #Victim race by offender race: Victim White X Offender White
    trim_upcase(estimate_type) %in% c('RATE') & row == 35,  DER_NA_CODE_STRING, #Victim race by offender race: Victim White X Offender non-White
    trim_upcase(estimate_type) %in% c('RATE') & row == 36,  DER_NA_CODE_STRING, #Victim race by offender race: Victim Black X Offender Black
    trim_upcase(estimate_type) %in% c('RATE') & row == 37,  DER_NA_CODE_STRING, #Victim race by offender race: Victim Black X Offender non-Black
    trim_upcase(estimate_type) %in% c('RATE') & row == 38,  DER_NA_CODE_STRING, #Victim race by offender race: Victim AIAN X Offender AIAN
    trim_upcase(estimate_type) %in% c('RATE') & row == 39,  DER_NA_CODE_STRING, #Victim race by offender race: Victim AIAN X Offender non-AIAN
    trim_upcase(estimate_type) %in% c('RATE') & row == 40,  DER_NA_CODE_STRING, #Victim race by offender race: Victim Asian X Offender Asian
    trim_upcase(estimate_type) %in% c('RATE') & row == 41,  DER_NA_CODE_STRING, #Victim race by offender race: Victim Asian X Offender non-Asian
    trim_upcase(estimate_type) %in% c('RATE') & row == 42,  DER_NA_CODE_STRING, #Victim race by offender race: Victim NHOPI X Offender NHOPI
    trim_upcase(estimate_type) %in% c('RATE') & row == 43,  DER_NA_CODE_STRING, #Victim race by offender race: Victim NHOPI X Offender non-NHOPI
    trim_upcase(estimate_type) %in% c('RATE') & row == 44,  DER_NA_CODE_STRING, #Victim race by offender race: Unknown victim race or unknown offender race
    trim_upcase(estimate_type) %in% c('RATE') & row == 45,  DER_NA_CODE_STRING, #Victim sex and race: Male
    trim_upcase(estimate_type) %in% c('RATE') & row == 46,  DER_NA_CODE_STRING, #Victim sex and race Male: White
    trim_upcase(estimate_type) %in% c('RATE') & row == 47,  DER_NA_CODE_STRING, #Victim sex and race Male: Black
    trim_upcase(estimate_type) %in% c('RATE') & row == 48,  DER_NA_CODE_STRING, #Victim sex and race Male: American Indian or Alaska Native
    trim_upcase(estimate_type) %in% c('RATE') & row == 49,  DER_NA_CODE_STRING, #Victim sex and race Male: Asian
    trim_upcase(estimate_type) %in% c('RATE') & row == 50,  DER_NA_CODE_STRING, #Victim sex and race Male: Native Hawaiian or Other Pacific Islander
    trim_upcase(estimate_type) %in% c('RATE') & row == 51,  DER_NA_CODE_STRING, #Victim sex and race Male: Unknown
    trim_upcase(estimate_type) %in% c('RATE') & row == 52,  DER_NA_CODE_STRING, #Victim sex and race: Female
    trim_upcase(estimate_type) %in% c('RATE') & row == 53,  DER_NA_CODE_STRING, #Victim sex and race Female: White
    trim_upcase(estimate_type) %in% c('RATE') & row == 54,  DER_NA_CODE_STRING, #Victim sex and race Female: Black
    trim_upcase(estimate_type) %in% c('RATE') & row == 55,  DER_NA_CODE_STRING, #Victim sex and race Female: American Indian or Alaska Native
    trim_upcase(estimate_type) %in% c('RATE') & row == 56,  DER_NA_CODE_STRING, #Victim sex and race Female: Asian
    trim_upcase(estimate_type) %in% c('RATE') & row == 57,  DER_NA_CODE_STRING, #Victim sex and race Female: Native Hawaiian or Other Pacific Islander
    trim_upcase(estimate_type) %in% c('RATE') & row == 58,  DER_NA_CODE_STRING, #Victim sex and race Female: Unknown
    trim_upcase(estimate_type) %in% c('RATE') & row == 59,  DER_NA_CODE_STRING, #Victim sex and race: Unknown
    trim_upcase(estimate_type) %in% c('RATE') & row == 60,  DER_NA_CODE_STRING, #Victim sex and race Unknown: White
    trim_upcase(estimate_type) %in% c('RATE') & row == 61,  DER_NA_CODE_STRING, #Victim sex and race Unknown: Black
    trim_upcase(estimate_type) %in% c('RATE') & row == 62,  DER_NA_CODE_STRING, #Victim sex and race Unknown: American Indian or Alaska Native
    trim_upcase(estimate_type) %in% c('RATE') & row == 63,  DER_NA_CODE_STRING, #Victim sex and race Unknown: Asian
    trim_upcase(estimate_type) %in% c('RATE') & row == 64,  DER_NA_CODE_STRING, #Victim sex and race Unknown: Native Hawaiian or Other Pacific Islander
    trim_upcase(estimate_type) %in% c('RATE') & row == 65,  DER_NA_CODE_STRING, #Victim sex and race Unknown: Unknown
    trim_upcase(estimate_type) %in% c('RATE') & row == 66,  DER_NA_CODE_STRING, #Weapon involved: No
    trim_upcase(estimate_type) %in% c('RATE') & row == 67,  DER_NA_CODE_STRING, #Weapon involved: Yes
    trim_upcase(estimate_type) %in% c('RATE') & row == 68,  DER_NA_CODE_STRING, #Weapon involved: Personal weapons
    trim_upcase(estimate_type) %in% c('RATE') & row == 69,  DER_NA_CODE_STRING, #Weapon involved: Firearms
    trim_upcase(estimate_type) %in% c('RATE') & row == 70,  DER_NA_CODE_STRING, #Weapon involved: Knives and other cutting instruments
    trim_upcase(estimate_type) %in% c('RATE') & row == 71,  DER_NA_CODE_STRING, #Weapon involved: Blunt instruments
    trim_upcase(estimate_type) %in% c('RATE') & row == 72,  DER_NA_CODE_STRING, #Weapon involved: Other non-personal weapons
    trim_upcase(estimate_type) %in% c('RATE') & row == 73,  DER_NA_CODE_STRING, #Weapon involved: Unknown
    trim_upcase(estimate_type) %in% c('RATE') & row == 74,  DER_NA_CODE_STRING, #Injury: No
    trim_upcase(estimate_type) %in% c('RATE') & row == 75,  DER_NA_CODE_STRING, #Injury: Yes
    trim_upcase(estimate_type) %in% c('RATE') & row == 76,  DER_NA_CODE_STRING, #Victim-offender relationship: Intimate partner
    trim_upcase(estimate_type) %in% c('RATE') & row == 77,  DER_NA_CODE_STRING, #Victim-offender relationship: Other family
    trim_upcase(estimate_type) %in% c('RATE') & row == 78,  DER_NA_CODE_STRING, #Victim-offender relationship: Outside family but known to victim
    trim_upcase(estimate_type) %in% c('RATE') & row == 79,  DER_NA_CODE_STRING, #Victim-offender relationship: Stranger
    trim_upcase(estimate_type) %in% c('RATE') & row == 80,  DER_NA_CODE_STRING, #Victim-offender relationship: Victim was Offender
    trim_upcase(estimate_type) %in% c('RATE') & row == 81,  DER_NA_CODE_STRING, #Victim-offender relationship: Unknown relationship
    trim_upcase(estimate_type) %in% c('RATE') & row == 82,  DER_NA_CODE_STRING, #Gang involvement: No
    trim_upcase(estimate_type) %in% c('RATE') & row == 83,  DER_NA_CODE_STRING, #Gang involvement: Yes
    trim_upcase(estimate_type) %in% c('RATE') & row == 84, DER_NA_CODE_STRING, #Victim Age 2: Under 12
    trim_upcase(estimate_type) %in% c('RATE') & row == 85, DER_NA_CODE_STRING, #Victim Age 2: 12-17
    trim_upcase(estimate_type) %in% c('RATE') & row == 86, DER_NA_CODE_STRING, #Victim Age 2: 12-14
    trim_upcase(estimate_type) %in% c('RATE') & row == 87, DER_NA_CODE_STRING, #Victim Age 2: 15-17
    trim_upcase(estimate_type) %in% c('RATE') & row == 88, DER_NA_CODE_STRING, #Victim Age 2: 18+
    trim_upcase(estimate_type) %in% c('RATE') & row == 89, DER_NA_CODE_STRING, #Victim Age 2: Unknown
    trim_upcase(estimate_type) %in% c('RATE') & row == 90, DER_NA_CODE_STRING, #Victim-offender relationship 2: Intimate partner plus Family
    trim_upcase(estimate_type) %in% c('RATE') & row == 91, DER_NA_CODE_STRING, #Victim-offender relationship 2: Outside family but known to victim
    trim_upcase(estimate_type) %in% c('RATE') & row == 92, DER_NA_CODE_STRING, #Victim-offender relationship 2: Stranger
    trim_upcase(estimate_type) %in% c('RATE') & row == 93, DER_NA_CODE_STRING, #Victim-offender relationship 2: Victim was Offender
    trim_upcase(estimate_type) %in% c('RATE') & row == 94, DER_NA_CODE_STRING, #Victim-offender relationship 2: Unknown relationship
    trim_upcase(estimate_type) %in% c('RATE') & row == 95, DER_NA_CODE_STRING, #Clearance: Not cleared
    trim_upcase(estimate_type) %in% c('RATE') & row == 96, DER_NA_CODE_STRING, #Clearance: Cleared through arrest
    trim_upcase(estimate_type) %in% c('RATE') & row == 97, DER_NA_CODE_STRING, #Clearance: Exceptional clearance
    trim_upcase(estimate_type) %in% c('RATE') & row == 98, DER_NA_CODE_STRING, #Clearance: Death of offender
    trim_upcase(estimate_type) %in% c('RATE') & row == 99, DER_NA_CODE_STRING, #Clearance: Prosecution declined
    trim_upcase(estimate_type) %in% c('RATE') & row == 100, DER_NA_CODE_STRING, #Clearance: In custody of other jurisdiction
    trim_upcase(estimate_type) %in% c('RATE') & row == 101, DER_NA_CODE_STRING, #Clearance: Victim refused to cooperate
    trim_upcase(estimate_type) %in% c('RATE') & row == 102, DER_NA_CODE_STRING, #Clearance: Juvenile/no custody
    trim_upcase(estimate_type) %in% c('RATE') & row == 103, DER_NA_CODE_STRING, #Weapon involved - Yes 2: Firearms or Explosives
    trim_upcase(estimate_type) %in% c('RATE') & row == 104, DER_NA_CODE_STRING, #Weapon involved - Yes 2: Firearms
    trim_upcase(estimate_type) %in% c('RATE') & row == 105, DER_NA_CODE_STRING, #Weapon involved - Yes 2: Another weapon other than firearms or explosives
    trim_upcase(estimate_type) %in% c('RATE') & row == 106, DER_NA_CODE_STRING, #Weapon involved - Yes 2: Knives and other cutting instruments
    trim_upcase(estimate_type) %in% c('RATE') & row == 107, DER_NA_CODE_STRING, #Weapon involved - Yes 2: Unknown
	
    trim_upcase(estimate_type) %in% c('RATE') & row == 108, DER_NA_CODE_STRING, #Weapon involved hierarchy: Handgun
    trim_upcase(estimate_type) %in% c('RATE') & row == 109, DER_NA_CODE_STRING, #Weapon involved hierarchy: Firearm
    trim_upcase(estimate_type) %in% c('RATE') & row == 110, DER_NA_CODE_STRING, #Weapon involved hierarchy: Rifle
    trim_upcase(estimate_type) %in% c('RATE') & row == 111, DER_NA_CODE_STRING, #Weapon involved hierarchy: Shotgun
    trim_upcase(estimate_type) %in% c('RATE') & row == 112, DER_NA_CODE_STRING, #Weapon involved hierarchy: Other Firearm
    trim_upcase(estimate_type) %in% c('RATE') & row == 113, DER_NA_CODE_STRING, #Weapon involved hierarchy: Knife/Cutting Instrument
    trim_upcase(estimate_type) %in% c('RATE') & row == 114, DER_NA_CODE_STRING, #Weapon involved hierarchy: Blunt Object
    trim_upcase(estimate_type) %in% c('RATE') & row == 115, DER_NA_CODE_STRING, #Weapon involved hierarchy: Motor Vehicle
    trim_upcase(estimate_type) %in% c('RATE') & row == 116, DER_NA_CODE_STRING, #Weapon involved hierarchy: Personal Weapons (hands, feet, teeth, etc.)
    trim_upcase(estimate_type) %in% c('RATE') & row == 117, DER_NA_CODE_STRING, #Weapon involved hierarchy: Asphyxiation
    trim_upcase(estimate_type) %in% c('RATE') & row == 118, DER_NA_CODE_STRING, #Weapon involved hierarchy: Drugs/Narcotics/Sleeping Pills
    trim_upcase(estimate_type) %in% c('RATE') & row == 119, DER_NA_CODE_STRING, #Weapon involved hierarchy: Poison (include gas)
    trim_upcase(estimate_type) %in% c('RATE') & row == 120, DER_NA_CODE_STRING, #Weapon involved hierarchy: Explosives
    trim_upcase(estimate_type) %in% c('RATE') & row == 121, DER_NA_CODE_STRING, #Weapon involved hierarchy: Fire/Incendiary Device
    trim_upcase(estimate_type) %in% c('RATE') & row == 122, DER_NA_CODE_STRING, #Weapon involved hierarchy: Other
    trim_upcase(estimate_type) %in% c('RATE') & row == 123, DER_NA_CODE_STRING, #Weapon involved hierarchy: No Weapon
    trim_upcase(estimate_type) %in% c('RATE') & row == 124, DER_NA_CODE_STRING, #Weapon involved hierarchy: Unknown
    trim_upcase(estimate_type) %in% c('RATE') & row == 125, DER_NA_CODE_STRING, #Weapon involved hierarchy: Not Applicable
    trim_upcase(estimate_type) %in% c('RATE') & row == 126, DER_NA_CODE_STRING, #Victim-offender relationship hierarchy: Intimate partner
    trim_upcase(estimate_type) %in% c('RATE') & row == 127, DER_NA_CODE_STRING, #Victim-offender relationship hierarchy: Other family
    trim_upcase(estimate_type) %in% c('RATE') & row == 128, DER_NA_CODE_STRING, #Victim-offender relationship hierarchy: Outside family but known to victim
    trim_upcase(estimate_type) %in% c('RATE') & row == 129, DER_NA_CODE_STRING, #Victim-offender relationship hierarchy: Stranger
    trim_upcase(estimate_type) %in% c('RATE') & row == 130, DER_NA_CODE_STRING, #Victim-offender relationship hierarchy: Victim was Offender
    trim_upcase(estimate_type) %in% c('RATE') & row == 131, DER_NA_CODE_STRING, #Victim-offender relationship hierarchy: Unknown relationship
    trim_upcase(estimate_type) %in% c('RATE') & row == 132, DER_NA_CODE_STRING, #Victim-offender relationship hierarchy: Unknown Offender Incidents
    trim_upcase(estimate_type) %in% c('RATE') & row == 133, DER_NA_CODE_STRING, #Victim-offender relationship hierarchy: Missing from Uncleared Incidents
    trim_upcase(estimate_type) %in% c('RATE') & row == 134, DER_NA_CODE_STRING, #Location type hierarchy within offense: Residence
    trim_upcase(estimate_type) %in% c('RATE') & row == 135, DER_NA_CODE_STRING, #Location type hierarchy within offense: Not residence
    trim_upcase(estimate_type) %in% c('RATE') & row == 136, DER_NA_CODE_STRING, #Weapon involved hierarchy within offense: Handgun
    trim_upcase(estimate_type) %in% c('RATE') & row == 137, DER_NA_CODE_STRING, #Weapon involved hierarchy within offense: Firearm
    trim_upcase(estimate_type) %in% c('RATE') & row == 138, DER_NA_CODE_STRING, #Weapon involved hierarchy within offense: Rifle
    trim_upcase(estimate_type) %in% c('RATE') & row == 139, DER_NA_CODE_STRING, #Weapon involved hierarchy within offense: Shotgun
    trim_upcase(estimate_type) %in% c('RATE') & row == 140, DER_NA_CODE_STRING, #Weapon involved hierarchy within offense: Other Firearm
    trim_upcase(estimate_type) %in% c('RATE') & row == 141, DER_NA_CODE_STRING, #Weapon involved hierarchy within offense: Knife/Cutting Instrument
    trim_upcase(estimate_type) %in% c('RATE') & row == 142, DER_NA_CODE_STRING, #Weapon involved hierarchy within offense: Blunt Object
    trim_upcase(estimate_type) %in% c('RATE') & row == 143, DER_NA_CODE_STRING, #Weapon involved hierarchy within offense: Motor Vehicle
    trim_upcase(estimate_type) %in% c('RATE') & row == 144, DER_NA_CODE_STRING, #Weapon involved hierarchy within offense: Personal Weapons (hands, feet, teeth, etc.)
    trim_upcase(estimate_type) %in% c('RATE') & row == 145, DER_NA_CODE_STRING, #Weapon involved hierarchy within offense: Asphyxiation
    trim_upcase(estimate_type) %in% c('RATE') & row == 146, DER_NA_CODE_STRING, #Weapon involved hierarchy within offense: Drugs/Narcotics/Sleeping Pills
    trim_upcase(estimate_type) %in% c('RATE') & row == 147, DER_NA_CODE_STRING, #Weapon involved hierarchy within offense: Poison (include gas)
    trim_upcase(estimate_type) %in% c('RATE') & row == 148, DER_NA_CODE_STRING, #Weapon involved hierarchy within offense: Explosives
    trim_upcase(estimate_type) %in% c('RATE') & row == 149, DER_NA_CODE_STRING, #Weapon involved hierarchy within offense: Fire/Incendiary Device
    trim_upcase(estimate_type) %in% c('RATE') & row == 150, DER_NA_CODE_STRING, #Weapon involved hierarchy within offense: Other
    trim_upcase(estimate_type) %in% c('RATE') & row == 151, DER_NA_CODE_STRING, #Weapon involved hierarchy within offense: No Weapon
    trim_upcase(estimate_type) %in% c('RATE') & row == 152, DER_NA_CODE_STRING, #Weapon involved hierarchy within offense: Unknown
    trim_upcase(estimate_type) %in% c('RATE') & row == 153, DER_NA_CODE_STRING, #Weapon involved hierarchy within offense: Not Applicable
    trim_upcase(estimate_type) %in% c('RATE') & row == 154, DER_NA_CODE_STRING, #Number of Victims Summarized at Incident Level Within Offense: 1
    trim_upcase(estimate_type) %in% c('RATE') & row == 155, DER_NA_CODE_STRING, #Number of Victims Summarized at Incident Level Within Offense: 2
    trim_upcase(estimate_type) %in% c('RATE') & row == 156, DER_NA_CODE_STRING, #Number of Victims Summarized at Incident Level Within Offense: 3
    trim_upcase(estimate_type) %in% c('RATE') & row == 157, DER_NA_CODE_STRING, #Number of Victims Summarized at Incident Level Within Offense: 4+
    trim_upcase(estimate_type) %in% c('RATE') & row == 158, DER_NA_CODE_STRING, #Weapon involved - Yes 3: Personal weapons
    trim_upcase(estimate_type) %in% c('RATE') & row == 159, DER_NA_CODE_STRING, #Weapon involved - Yes 3: Firearms
    trim_upcase(estimate_type) %in% c('RATE') & row == 160, DER_NA_CODE_STRING, #Weapon involved - Yes 3: Other non-personal
    trim_upcase(estimate_type) %in% c('RATE') & row == 161, DER_NA_CODE_STRING, #Weapon involved - Yes 3: Unknown
    trim_upcase(estimate_type) %in% c('RATE') & row == 162, DER_NA_CODE_STRING, #Victim Hispanic Origin: Hispanic or Latino
    trim_upcase(estimate_type) %in% c('RATE') & row == 163, DER_NA_CODE_STRING, #Victim Hispanic Origin: Not Hispanic or Latino
    trim_upcase(estimate_type) %in% c('RATE') & row == 164, DER_NA_CODE_STRING, #Victim Hispanic Origin: Unknown
    trim_upcase(estimate_type) %in% c('RATE') & row == 165, DER_NA_CODE_STRING, #Victim race and Hispanic Origin: Hispanic or Latino
    trim_upcase(estimate_type) %in% c('RATE') & row == 166, DER_NA_CODE_STRING, #Victim race and Hispanic Origin: Non-Hispanic, White
    trim_upcase(estimate_type) %in% c('RATE') & row == 167, DER_NA_CODE_STRING, #Victim race and Hispanic Origin: Non-Hispanic, Black
    trim_upcase(estimate_type) %in% c('RATE') & row == 168, DER_NA_CODE_STRING, #Victim race and Hispanic Origin: Non-Hispanic, American Indian or Alaska Native
    trim_upcase(estimate_type) %in% c('RATE') & row == 169, DER_NA_CODE_STRING, #Victim race and Hispanic Origin: Non-Hispanic, Asian
    trim_upcase(estimate_type) %in% c('RATE') & row == 170, DER_NA_CODE_STRING, #Victim race and Hispanic Origin: Non-Hispanic, Native Hawaiian or Other Pacific Islander
    trim_upcase(estimate_type) %in% c('RATE') & row == 171, DER_NA_CODE_STRING #Victim race and Hispanic Origin: Unknown race or Hispanic origin
    
    
  ))
  return(returndata)

}



#This function will calculate the counts and percentage one column at a time

generate_est <- function(maindata, subsetvareq1, column_number){
  log_debug("Running generate_est function")
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
  main_filter <- maindata[eval(infilter), c("ori", "weight", "incident_id", "victim_id", "offense_id", "der_victim_LEO", filtervarsting, "der_offender_id_exclude"), with = FALSE]
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

  #Total Denominator
  der_total_denom <- s1[[1]] %>% select(final_count) %>% as.double()

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
  s5 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_victim_age_cat_15_17_victim, var=der_victim_age_cat_15_17, section=5, mergeby=c( "incident_id", "victim_id"))

  #Victim sex
  s6 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_victim_gender_victim, var=der_victim_gender, section=6, mergeby=c( "incident_id", "victim_id"))

  #Victim race
  s7 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_victim_race_victim, var=der_victim_race, section=7, mergeby=c( "incident_id", "victim_id"))

  #Victim age category by offender age category - Drop unknown offenders offender_seq_num = 0
  s8 <- agg_percent_CAA_victim(leftdata = main_filter %>% filter(is.na(der_offender_id_exclude)), rightdata = agg_victim_offender_age_1_4_victim, var=der_victim_offender_age_1_4, section=8, mergeby=c( "incident_id", "victim_id"), denom=der_total_denom)

  #Victim sex by offender sex - Drop unknown offenders offender_seq_num = 0
  s9 <- agg_percent_CAA_victim(leftdata = main_filter %>% filter(is.na(der_offender_id_exclude)), rightdata = agg_victim_offender_gender_1_4_victim, var=der_victim_offender_gender_1_4, section=9, mergeby=c( "incident_id", "victim_id"), denom=der_total_denom)

  #Victim race by offender race - Drop unknown offenders offender_seq_num = 0
  s10 <- agg_percent_CAA_victim(leftdata = main_filter %>% filter(is.na(der_offender_id_exclude)), rightdata = agg_victim_offender_race_1_10_victim, var=der_victim_offender_race_1_10, section=10, mergeby=c( "incident_id", "victim_id"), denom=der_total_denom)

  #Victim sex and race
  s11 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_victim_gender_race_victim_male, var=der_victim_gender_race, section=11, mergeby=c( "incident_id", "victim_id"))

  s11_1 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_victim_gender_race_victim_female, var=der_victim_gender_race, section=11.1, mergeby=c( "incident_id", "victim_id"))

  s11_2 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_victim_gender_race_victim_unknown, var=der_victim_gender_race, section=11.2, mergeby=c( "incident_id", "victim_id"))

  #Victim sex - Extra for Victim sex and race
  s12 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_victim_gender_victim, var=der_victim_gender, section=12, mergeby=c( "incident_id", "victim_id"))

  #Weapon involved
  s13 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_weapon_no_yes_victim, var=der_weapon_no_yes, section=13, mergeby=c( "incident_id", "victim_id"))

  der_weapon_yes_denom <- s13[[1]] %>%
    filter(der_weapon_no_yes == 2) %>% #Yes response
    select(final_count) %>%
    as.double()

  #Weapon involved Categories
  s14 <- agg_percent_CAA_victim(leftdata = main_filter, rightdata = agg_weapon_yes_cat_victim, var=der_weapon_yes_cat, section=14, mergeby=c( "incident_id", "victim_id"), denom=der_weapon_yes_denom)

  #Injury
  s15 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_injury_no_yes_victim, var=der_injury_no_yes, section=15, mergeby=c( "incident_id", "victim_id"))


  #Victim-offender relationship
  s16 <- agg_percent_CAA_victim(leftdata = main_filter, rightdata = agg_relationship_cat_victim, var=der_relationship, section=16, mergeby=c( "incident_id", "victim_id"), denom=der_total_denom)

  #Gang involvement
  s17 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_gang_cat_victim, var=der_gang_cat_no_yes, section=17, mergeby=c( "incident_id", "victim_id"))

  #Victim Age 2
  s18 <- agg_percent_CAA_victim(leftdata = main_filter, rightdata = agg_victim_age_cat_under18_2_victim_imp, var=der_victim_age_cat_under18_2, section=18, mergeby=c( "incident_id", "victim_id"), denom=der_total_denom)
  s19 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_victim_age_cat_12_17_cat_victim_imp, var=der_victim_age_cat_12_17_cat, section=19, mergeby=c( "incident_id", "victim_id"))
  s20 <- agg_percent_CAA_victim(leftdata = main_filter, rightdata = agg_victim_age_cat_2_uo18_victim_imp,    var=der_victim_age_cat_2_uo18,    section=20, mergeby=c( "incident_id", "victim_id"), denom=der_total_denom)

  #Victim-offender relationship2
  s21 <- agg_percent_CAA_victim(leftdata = main_filter, rightdata = agg_relationship_cat2_victim_imp, var=der_relationship2, section=21, mergeby=c( "incident_id", "victim_id"), denom=der_total_denom)


  #Clearance
  s22 <- agg_percent_by_incident_id(leftdata = main_filter, rightdata = agg_clearance_cat, var=der_clearance_cat, section=22)

  #Exceptional clearance
  s23 <- agg_percent_by_incident_id(leftdata = main_filter, rightdata = agg_exception_clearance_cat, var=der_exceptional_clearance, section=23)

  #Weapon involved - Yes 2
  s24 <- agg_percent_CAA_victim(leftdata = main_filter, rightdata = agg_weapon_yes_cat2_victim, var=der_weapon_yes_cat2, section=24, mergeby=c( "incident_id", "victim_id"), denom=der_weapon_yes_denom)

  der_weapon_yes_firearm_denom <- s24[[1]] %>%
    filter(der_weapon_yes_cat2 == 1) %>% #Firearms or Explosives
    select(final_count) %>%
    as.double()

  der_weapon_yes_knives_denom <- s24[[1]] %>%
    filter(der_weapon_yes_cat2 == 2) %>% #Another weapon other than firearms or explosives
    select(final_count) %>%
    as.double()

  #Weapon involved - Yes 2: Firearms
  s25 <- agg_percent_CAA_victim(leftdata = main_filter, rightdata = agg_weapon_subset_firearm_victim %>% filter(der_weapon_subset_firearm == 1), var=der_weapon_subset_firearm, section=25, mergeby=c( "incident_id", "victim_id"), denom=der_weapon_yes_firearm_denom)

  #Weapon involved - Yes 2: Knives and other cutting instruments
  s26 <- agg_percent_CAA_victim(leftdata = main_filter, rightdata = agg_weapon_subset_knives_victim %>% filter(der_weapon_subset_knives == 1), var=der_weapon_subset_knives, section=26, mergeby=c( "incident_id", "victim_id"), denom=der_weapon_yes_knives_denom)

  #Weapon involved hierarchy
  s27 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_raw_weapon_hierarchy_recode_victim, var=der_raw_weapon_hierarchy_recode, section=27, 
                     mergeby=c( "incident_id", "victim_id"))
  
  #Victim-offender relationship hierarchy
  s28 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_relationship_hierarchy_victim, var=der_relationship_hierarchy, section=28, 
                     mergeby=c( "incident_id", "victim_id"))  
  
  
  #Location type hierarchy
  #Bring in agg_location_residence_offenses_with_off and subset to current offense
  agg_location_residence_offenses_with_off2 <- agg_location_residence_offenses_with_off[eval(infilter),] %>%
    #Need to summarise the data at the incident, victim, and derived variable
    group_by(incident_id, victim_id, der_location_residence) %>%
    summarise(count = sum(count, na.rm=TRUE) ) %>%
    ungroup() %>%
    #Need to transpose the data
    mutate(
      new_column = paste0("der_location_residence", "_",  der_location_residence)
    ) %>%
    #Drop the variable to be transpose
    select(-der_location_residence) %>%
    spread(key=new_column, value=count) %>%
    #Create the additional new variables if not created during transpose
    add_new_columns_to_extract(indata=., inprefix="der_location_residence", instartnum=1, inmaxnum=2) %>%
    #Zero-filled the new variables
    mutate(
      across(
        .cols = starts_with("der_location_residence"),
        .fns = ~{replace_na(.x, replace=0)}
      )
    ) %>%
    #Recreate the original der_location_residence variable
    mutate(
      der_location_residence = fcase(
        der_location_residence_1 > 0, 1, # Residence
        der_location_residence_2 > 0, 2 # Residence# Not residence
      ),
      
      #Create new count variable
      count = 1
    )
    
  s29 <- agg_percent_CAA_victim(leftdata = main_filter, rightdata = agg_location_residence_offenses_with_off2, var=der_location_residence, section=29, mergeby=c( "incident_id", "victim_id"), denom=der_total_denom)
  
  #Weapon involved hierarchy within offense  
  #Bring in agg_raw_weapon_hierarchy_recode_offenses and subset to current offense
  agg_raw_weapon_hierarchy_recode_offenses_with_off2 <- agg_raw_weapon_hierarchy_recode_offenses_with_off[eval(infilter),] %>%
    #Need to summarise the data at the incident, victim, and derived variable
    group_by(incident_id, victim_id, der_raw_weapon_hierarchy_recode) %>%
    summarise(count = sum(count, na.rm=TRUE) ) %>%
    ungroup() %>%
    #Need to transpose the data
    mutate(
      new_column = paste0("der_raw_weapon_hierarchy_recode", "_",  der_raw_weapon_hierarchy_recode)
    ) %>%
    #Drop the variable to be transpose
    select(-der_raw_weapon_hierarchy_recode) %>%
    spread(key=new_column, value=count) %>%
    #Create the additional new variables if not created during transpose
    add_new_columns_to_extract(indata=., inprefix="der_raw_weapon_hierarchy_recode", instartnum=1, inmaxnum=18) %>%    
    #Zero-filled the new variables
    mutate(
      across(
        .cols = starts_with("der_raw_weapon_hierarchy_recode"),
        .fns = ~{replace_na(.x, replace=0)}
      )
    ) %>%
    #Recreate the original der_raw_weapon_hierarchy_recode variable
    mutate(
      der_raw_weapon_hierarchy_recode = fcase(
        der_raw_weapon_hierarchy_recode_1 > 0, 1, #Handgun
        der_raw_weapon_hierarchy_recode_2 > 0, 2, #Firearm
        der_raw_weapon_hierarchy_recode_3 > 0, 3, #Rifle
        der_raw_weapon_hierarchy_recode_4 > 0, 4, #Shotgun
        der_raw_weapon_hierarchy_recode_5 > 0, 5, #Other Firearm
        der_raw_weapon_hierarchy_recode_6 > 0, 6, #Knife/Cutting Instrument
        der_raw_weapon_hierarchy_recode_7 > 0, 7, #Blunt Object
        der_raw_weapon_hierarchy_recode_8 > 0, 8, #Motor Vehicle
        der_raw_weapon_hierarchy_recode_9 > 0, 9, #Personal Weapons (hands, feet, teeth, etc.)
        der_raw_weapon_hierarchy_recode_10 > 0, 10, #Asphyxiation
        der_raw_weapon_hierarchy_recode_11 > 0, 11, #Drugs/Narcotics/Sleeping Pills
        der_raw_weapon_hierarchy_recode_12 > 0, 12, #Poison (include gas)
        der_raw_weapon_hierarchy_recode_13 > 0, 13, #Explosives
        der_raw_weapon_hierarchy_recode_14 > 0, 14, #Fire/Incendiary Device
        der_raw_weapon_hierarchy_recode_15 > 0, 15, #Other
        der_raw_weapon_hierarchy_recode_16 > 0, 16, #No Weapon
        der_raw_weapon_hierarchy_recode_17 > 0, 17, #Unknown
        der_raw_weapon_hierarchy_recode_18 > 0, 18 #Not Applicable
      ),
      
      #Create new count variable
      count = 1
    )  
  
  s30 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_raw_weapon_hierarchy_recode_offenses_with_off2, var=der_raw_weapon_hierarchy_recode, section=30, 
                            mergeby=c( "incident_id", "victim_id"))
  
  #Number of Victims Summarized at Incident Level  
  #Create the variable der_inc_number_of_victims_cat using the main_filter dataset
  agg_inc_number_of_victims_cat <- main_filter %>%
    #Deduplicate the data, note main_filter is the block imputed dataset, so need to create unique incident_id and victim_id rows
    count(incident_id, victim_id) %>%
    #Drop the n variable for count
    select(-n) %>%
    #Next need to recode the number of victims in the incident
    count(incident_id) %>%
    #Note n is the number of victims in an incident
    mutate(
      der_inc_number_of_victims_cat = fcase(
        n == 1, 1, # 1
        n == 2, 2, # 2
        n == 3, 3, # 3
        n >= 4, 4 # 4+
      ),
      
      #Create the count variable and assign 1 for each incident
      count = 1) %>%
    #Keep variables of interest
    select(incident_id, der_inc_number_of_victims_cat, count)
  
  #Next need to create the incident level file using main_filter
  main_filter_inc <- main_filter[, .SD[1], by = c("ori", "incident_id", filtervarsting)]  
  
  
  #Using agg_inc_number_of_victims_cat, process as normal
  s31 <- agg_percent_by_incident_id(leftdata = main_filter_inc, rightdata = agg_inc_number_of_victims_cat, var=der_inc_number_of_victims_cat, section=31)
  
  #Weapon involved - Yes 3
  s32 <- agg_percent_CAA_victim(leftdata = main_filter, rightdata = agg_raw_weapon_recode_4_level_victim, var=der_raw_weapon_recode_4_level, section=32, mergeby=c( "incident_id", "victim_id"), denom=der_weapon_yes_denom)
  
  #Victim Hispanic Origin
  s33 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_victim_ethnicity_victim, var=der_victim_ethnicity, section=33, mergeby=c( "incident_id", "victim_id"))  
  
  #Victim race and Hispanic Origin
  s34 <- agg_percent_victim(leftdata = main_filter, rightdata = agg_victim_ethnicity_race_victim, var=der_victim_ethnicity_race, section=34, mergeby=c( "incident_id", "victim_id"))  
  
    
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
    mutate(count = fcase(!row %in% c(3:4), final_count, default = DER_NA_CODE)) %>%
    mutate(percentage = fcase(!row %in% c(1:4), percent, default = DER_NA_CODE)) %>%
    mutate(rate = fcase(row %in% c(3:4), final_count,default = DER_NA_CODE)) %>%
    mutate(population_estimate = fcase(row %in% c(3:4), population_estimate,default = DER_NA_CODE)) %>%
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
  log_dim("Inside createadditionalcolumns")
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