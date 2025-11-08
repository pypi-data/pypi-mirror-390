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
    der_suspected_type_of_drug_crim_activity %in% c(1:72),  der_suspected_type_of_drug_crim_activity + 1,
    der_1suspected_type_of_drug_1crim_activity %in% c(1:72),  der_1suspected_type_of_drug_1crim_activity + 73
    )
  )

  return(returndata)
}

assign_section <- function(data){

  returndata <- data %>% mutate(

  section = fcase(
    row %in% c(1),  1,
    row %in% c(2:73),  2,
    row %in% c(74:145),  3
    )
  )

  return(returndata)

}


#New add on code for labels
assign_labels <- function(data){

  returndata <- data %>% mutate(

  estimate_domain = fcase(

row == 1,  'Total',
row == 2,  'Cocaine/crack cocaine (A, B): Buying/receiving',
row == 3,  'Cocaine/crack cocaine (A, B): Cultivating/manufacturing/publishing',
row == 4,  'Cocaine/crack cocaine (A, B): Distributing/selling',
row == 5,  'Cocaine/crack cocaine (A, B): Exploiting children',
row == 6,  'Cocaine/crack cocaine (A, B): Operating/promoting/assisting',
row == 7,  'Cocaine/crack cocaine (A, B): Possessing/concealing',
row == 8,  'Cocaine/crack cocaine (A, B): Transporting/transmitting/importing',
row == 9,  'Cocaine/crack cocaine (A, B): Using/consuming',
row == 10,  'Marijuana/hashish (C, E): Buying/receiving',
row == 11,  'Marijuana/hashish (C, E): Cultivating/manufacturing/publishing',
row == 12,  'Marijuana/hashish (C, E): Distributing/selling',
row == 13,  'Marijuana/hashish (C, E): Exploiting children',
row == 14,  'Marijuana/hashish (C, E): Operating/promoting/assisting',
row == 15,  'Marijuana/hashish (C, E): Possessing/concealing',
row == 16,  'Marijuana/hashish (C, E): Transporting/transmitting/importing',
row == 17,  'Marijuana/hashish (C, E): Using/consuming',
row == 18,  'Opiate/narcotic (D, F, G, H): Buying/receiving',
row == 19,  'Opiate/narcotic (D, F, G, H): Cultivating/manufacturing/publishing',
row == 20,  'Opiate/narcotic (D, F, G, H): Distributing/selling',
row == 21,  'Opiate/narcotic (D, F, G, H): Exploiting children',
row == 22,  'Opiate/narcotic (D, F, G, H): Operating/promoting/assisting',
row == 23,  'Opiate/narcotic (D, F, G, H): Possessing/concealing',
row == 24,  'Opiate/narcotic (D, F, G, H): Transporting/transmitting/importing',
row == 25,  'Opiate/narcotic (D, F, G, H): Using/consuming',
row == 26,  'Hallucinogen (I, J, K): Buying/receiving',
row == 27,  'Hallucinogen (I, J, K): Cultivating/manufacturing/publishing',
row == 28,  'Hallucinogen (I, J, K): Distributing/selling',
row == 29,  'Hallucinogen (I, J, K): Exploiting children',
row == 30,  'Hallucinogen (I, J, K): Operating/promoting/assisting',
row == 31,  'Hallucinogen (I, J, K): Possessing/concealing',
row == 32,  'Hallucinogen (I, J, K): Transporting/transmitting/importing',
row == 33,  'Hallucinogen (I, J, K): Using/consuming',
row == 34,  'Stimulant (L, M): Buying/receiving',
row == 35,  'Stimulant (L, M): Cultivating/manufacturing/publishing',
row == 36,  'Stimulant (L, M): Distributing/selling',
row == 37,  'Stimulant (L, M): Exploiting children',
row == 38,  'Stimulant (L, M): Operating/promoting/assisting',
row == 39,  'Stimulant (L, M): Possessing/concealing',
row == 40,  'Stimulant (L, M): Transporting/transmitting/importing',
row == 41,  'Stimulant (L, M): Using/consuming',
row == 42,  'Depressant (N, O): Buying/receiving',
row == 43,  'Depressant (N, O): Cultivating/manufacturing/publishing',
row == 44,  'Depressant (N, O): Distributing/selling',
row == 45,  'Depressant (N, O): Exploiting children',
row == 46,  'Depressant (N, O): Operating/promoting/assisting',
row == 47,  'Depressant (N, O): Possessing/concealing',
row == 48,  'Depressant (N, O): Transporting/transmitting/importing',
row == 49,  'Depressant (N, O): Using/consuming',
row == 50,  'Other (P): Buying/receiving',
row == 51,  'Other (P): Cultivating/manufacturing/publishing',
row == 52,  'Other (P): Distributing/selling',
row == 53,  'Other (P): Exploiting children',
row == 54,  'Other (P): Operating/promoting/assisting',
row == 55,  'Other (P): Possessing/concealing',
row == 56,  'Other (P): Transporting/transmitting/importing',
row == 57,  'Other (P): Using/consuming',
row == 58,  'Unknown (U): Buying/receiving',
row == 59,  'Unknown (U): Cultivating/manufacturing/publishing',
row == 60,  'Unknown (U): Distributing/selling',
row == 61,  'Unknown (U): Exploiting children',
row == 62,  'Unknown (U): Operating/promoting/assisting',
row == 63,  'Unknown (U): Possessing/concealing',
row == 64,  'Unknown (U): Transporting/transmitting/importing',
row == 65,  'Unknown (U): Using/consuming',
row == 66,  'More Than 3 Types (X): Buying/receiving',
row == 67,  'More Than 3 Types (X): Cultivating/manufacturing/publishing',
row == 68,  'More Than 3 Types (X): Distributing/selling',
row == 69,  'More Than 3 Types (X): Exploiting children',
row == 70,  'More Than 3 Types (X): Operating/promoting/assisting',
row == 71,  'More Than 3 Types (X): Possessing/concealing',
row == 72,  'More Than 3 Types (X): Transporting/transmitting/importing',
row == 73,  'More Than 3 Types (X): Using/consuming',
row == 74,  'One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Buying/receiving',
row == 75,  'One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Cultivating/manufacturing/publishing',
row == 76,  'One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Distributing/selling',
row == 77,  'One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Exploiting children',
row == 78,  'One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Operating/promoting/assisting',
row == 79,  'One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Possessing/concealing',
row == 80,  'One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Transporting/transmitting/importing',
row == 81,  'One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Using/consuming',
row == 82,  'One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Buying/receiving',
row == 83,  'One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Cultivating/manufacturing/publishing',
row == 84,  'One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Distributing/selling',
row == 85,  'One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Exploiting children',
row == 86,  'One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Operating/promoting/assisting',
row == 87,  'One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Possessing/concealing',
row == 88,  'One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Transporting/transmitting/importing',
row == 89,  'One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Using/consuming',
row == 90,  'One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Buying/receiving',
row == 91,  'One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Cultivating/manufacturing/publishing',
row == 92,  'One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Distributing/selling',
row == 93,  'One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Exploiting children',
row == 94,  'One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Operating/promoting/assisting',
row == 95,  'One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Possessing/concealing',
row == 96,  'One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Transporting/transmitting/importing',
row == 97,  'One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Using/consuming',
row == 98,  'One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Buying/receiving',
row == 99,  'One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Cultivating/manufacturing/publishing',
row == 100,  'One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Distributing/selling',
row == 101,  'One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Exploiting children',
row == 102,  'One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Operating/promoting/assisting',
row == 103,  'One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Possessing/concealing',
row == 104,  'One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Transporting/transmitting/importing',
row == 105,  'One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Using/consuming',
row == 106,  'One Criminal Activity or One Suspected Drug Stimulant (L, M): Buying/receiving',
row == 107,  'One Criminal Activity or One Suspected Drug Stimulant (L, M): Cultivating/manufacturing/publishing',
row == 108,  'One Criminal Activity or One Suspected Drug Stimulant (L, M): Distributing/selling',
row == 109,  'One Criminal Activity or One Suspected Drug Stimulant (L, M): Exploiting children',
row == 110,  'One Criminal Activity or One Suspected Drug Stimulant (L, M): Operating/promoting/assisting',
row == 111,  'One Criminal Activity or One Suspected Drug Stimulant (L, M): Possessing/concealing',
row == 112,  'One Criminal Activity or One Suspected Drug Stimulant (L, M): Transporting/transmitting/importing',
row == 113,  'One Criminal Activity or One Suspected Drug Stimulant (L, M): Using/consuming',
row == 114,  'One Criminal Activity or One Suspected Drug Depressant (N, O): Buying/receiving',
row == 115,  'One Criminal Activity or One Suspected Drug Depressant (N, O): Cultivating/manufacturing/publishing',
row == 116,  'One Criminal Activity or One Suspected Drug Depressant (N, O): Distributing/selling',
row == 117,  'One Criminal Activity or One Suspected Drug Depressant (N, O): Exploiting children',
row == 118,  'One Criminal Activity or One Suspected Drug Depressant (N, O): Operating/promoting/assisting',
row == 119,  'One Criminal Activity or One Suspected Drug Depressant (N, O): Possessing/concealing',
row == 120,  'One Criminal Activity or One Suspected Drug Depressant (N, O): Transporting/transmitting/importing',
row == 121,  'One Criminal Activity or One Suspected Drug Depressant (N, O): Using/consuming',
row == 122,  'One Criminal Activity or One Suspected Drug Other (P): Buying/receiving',
row == 123,  'One Criminal Activity or One Suspected Drug Other (P): Cultivating/manufacturing/publishing',
row == 124,  'One Criminal Activity or One Suspected Drug Other (P): Distributing/selling',
row == 125,  'One Criminal Activity or One Suspected Drug Other (P): Exploiting children',
row == 126,  'One Criminal Activity or One Suspected Drug Other (P): Operating/promoting/assisting',
row == 127,  'One Criminal Activity or One Suspected Drug Other (P): Possessing/concealing',
row == 128,  'One Criminal Activity or One Suspected Drug Other (P): Transporting/transmitting/importing',
row == 129,  'One Criminal Activity or One Suspected Drug Other (P): Using/consuming',
row == 130,  'One Criminal Activity or One Suspected Drug Unknown (U): Buying/receiving',
row == 131,  'One Criminal Activity or One Suspected Drug Unknown (U): Cultivating/manufacturing/publishing',
row == 132,  'One Criminal Activity or One Suspected Drug Unknown (U): Distributing/selling',
row == 133,  'One Criminal Activity or One Suspected Drug Unknown (U): Exploiting children',
row == 134,  'One Criminal Activity or One Suspected Drug Unknown (U): Operating/promoting/assisting',
row == 135,  'One Criminal Activity or One Suspected Drug Unknown (U): Possessing/concealing',
row == 136,  'One Criminal Activity or One Suspected Drug Unknown (U): Transporting/transmitting/importing',
row == 137,  'One Criminal Activity or One Suspected Drug Unknown (U): Using/consuming',
row == 138,  'One Criminal Activity or One Suspected Drug More Than 3 Types (X): Buying/receiving',
row == 139,  'One Criminal Activity or One Suspected Drug More Than 3 Types (X): Cultivating/manufacturing/publishing',
row == 140,  'One Criminal Activity or One Suspected Drug More Than 3 Types (X): Distributing/selling',
row == 141,  'One Criminal Activity or One Suspected Drug More Than 3 Types (X): Exploiting children',
row == 142,  'One Criminal Activity or One Suspected Drug More Than 3 Types (X): Operating/promoting/assisting',
row == 143,  'One Criminal Activity or One Suspected Drug More Than 3 Types (X): Possessing/concealing',
row == 144,  'One Criminal Activity or One Suspected Drug More Than 3 Types (X): Transporting/transmitting/importing',
row == 145,  'One Criminal Activity or One Suspected Drug More Than 3 Types (X): Using/consuming'




  ),

  indicator_name = fcase(

column == 1,  'Completed Drug/Narcotic Violation'


  ),

  full_table = "TableDM5 - Drug Type + Activity",
  table = DER_TABLE_NAME
  )

  return(returndata)

}

estimate_type_detail_percentage_label <- function(indata){

  returndata <- indata %>%
    mutate(
      estimate_type_detail_percentage = fcase(

trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 1,  'Incident Level', #Total
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 2,  'Incident Level', #Cocaine/crack cocaine (A, B): Buying/receiving
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 3,  'Incident Level', #Cocaine/crack cocaine (A, B): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 4,  'Incident Level', #Cocaine/crack cocaine (A, B): Distributing/selling
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 5,  'Incident Level', #Cocaine/crack cocaine (A, B): Exploiting children
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 6,  'Incident Level', #Cocaine/crack cocaine (A, B): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 7,  'Incident Level', #Cocaine/crack cocaine (A, B): Possessing/concealing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 8,  'Incident Level', #Cocaine/crack cocaine (A, B): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 9,  'Incident Level', #Cocaine/crack cocaine (A, B): Using/consuming
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 10,  'Incident Level', #Marijuana/hashish (C, E): Buying/receiving
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 11,  'Incident Level', #Marijuana/hashish (C, E): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 12,  'Incident Level', #Marijuana/hashish (C, E): Distributing/selling
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 13,  'Incident Level', #Marijuana/hashish (C, E): Exploiting children
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 14,  'Incident Level', #Marijuana/hashish (C, E): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 15,  'Incident Level', #Marijuana/hashish (C, E): Possessing/concealing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 16,  'Incident Level', #Marijuana/hashish (C, E): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 17,  'Incident Level', #Marijuana/hashish (C, E): Using/consuming
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 18,  'Incident Level', #Opiate/narcotic (D, F, G, H): Buying/receiving
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 19,  'Incident Level', #Opiate/narcotic (D, F, G, H): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 20,  'Incident Level', #Opiate/narcotic (D, F, G, H): Distributing/selling
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 21,  'Incident Level', #Opiate/narcotic (D, F, G, H): Exploiting children
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 22,  'Incident Level', #Opiate/narcotic (D, F, G, H): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 23,  'Incident Level', #Opiate/narcotic (D, F, G, H): Possessing/concealing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 24,  'Incident Level', #Opiate/narcotic (D, F, G, H): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 25,  'Incident Level', #Opiate/narcotic (D, F, G, H): Using/consuming
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 26,  'Incident Level', #Hallucinogen (I, J, K): Buying/receiving
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 27,  'Incident Level', #Hallucinogen (I, J, K): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 28,  'Incident Level', #Hallucinogen (I, J, K): Distributing/selling
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 29,  'Incident Level', #Hallucinogen (I, J, K): Exploiting children
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 30,  'Incident Level', #Hallucinogen (I, J, K): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 31,  'Incident Level', #Hallucinogen (I, J, K): Possessing/concealing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 32,  'Incident Level', #Hallucinogen (I, J, K): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 33,  'Incident Level', #Hallucinogen (I, J, K): Using/consuming
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 34,  'Incident Level', #Stimulant (L, M): Buying/receiving
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 35,  'Incident Level', #Stimulant (L, M): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 36,  'Incident Level', #Stimulant (L, M): Distributing/selling
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 37,  'Incident Level', #Stimulant (L, M): Exploiting children
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 38,  'Incident Level', #Stimulant (L, M): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 39,  'Incident Level', #Stimulant (L, M): Possessing/concealing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 40,  'Incident Level', #Stimulant (L, M): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 41,  'Incident Level', #Stimulant (L, M): Using/consuming
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 42,  'Incident Level', #Depressant (N, O): Buying/receiving
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 43,  'Incident Level', #Depressant (N, O): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 44,  'Incident Level', #Depressant (N, O): Distributing/selling
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 45,  'Incident Level', #Depressant (N, O): Exploiting children
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 46,  'Incident Level', #Depressant (N, O): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 47,  'Incident Level', #Depressant (N, O): Possessing/concealing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 48,  'Incident Level', #Depressant (N, O): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 49,  'Incident Level', #Depressant (N, O): Using/consuming
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 50,  'Incident Level', #Other (P): Buying/receiving
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 51,  'Incident Level', #Other (P): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 52,  'Incident Level', #Other (P): Distributing/selling
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 53,  'Incident Level', #Other (P): Exploiting children
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 54,  'Incident Level', #Other (P): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 55,  'Incident Level', #Other (P): Possessing/concealing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 56,  'Incident Level', #Other (P): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 57,  'Incident Level', #Other (P): Using/consuming
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 58,  'Incident Level', #Unknown (U): Buying/receiving
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 59,  'Incident Level', #Unknown (U): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 60,  'Incident Level', #Unknown (U): Distributing/selling
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 61,  'Incident Level', #Unknown (U): Exploiting children
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 62,  'Incident Level', #Unknown (U): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 63,  'Incident Level', #Unknown (U): Possessing/concealing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 64,  'Incident Level', #Unknown (U): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 65,  'Incident Level', #Unknown (U): Using/consuming
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 66,  'Incident Level', #More Than 3 Types (X): Buying/receiving
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 67,  'Incident Level', #More Than 3 Types (X): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 68,  'Incident Level', #More Than 3 Types (X): Distributing/selling
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 69,  'Incident Level', #More Than 3 Types (X): Exploiting children
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 70,  'Incident Level', #More Than 3 Types (X): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 71,  'Incident Level', #More Than 3 Types (X): Possessing/concealing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 72,  'Incident Level', #More Than 3 Types (X): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 73,  'Incident Level', #More Than 3 Types (X): Using/consuming
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 74,  'Incident Level', #One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Buying/receiving
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 75,  'Incident Level', #One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 76,  'Incident Level', #One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Distributing/selling
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 77,  'Incident Level', #One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Exploiting children
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 78,  'Incident Level', #One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 79,  'Incident Level', #One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Possessing/concealing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 80,  'Incident Level', #One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 81,  'Incident Level', #One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Using/consuming
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 82,  'Incident Level', #One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Buying/receiving
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 83,  'Incident Level', #One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 84,  'Incident Level', #One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Distributing/selling
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 85,  'Incident Level', #One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Exploiting children
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 86,  'Incident Level', #One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 87,  'Incident Level', #One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Possessing/concealing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 88,  'Incident Level', #One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 89,  'Incident Level', #One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Using/consuming
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 90,  'Incident Level', #One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Buying/receiving
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 91,  'Incident Level', #One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 92,  'Incident Level', #One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Distributing/selling
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 93,  'Incident Level', #One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Exploiting children
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 94,  'Incident Level', #One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 95,  'Incident Level', #One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Possessing/concealing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 96,  'Incident Level', #One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 97,  'Incident Level', #One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Using/consuming
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 98,  'Incident Level', #One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Buying/receiving
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 99,  'Incident Level', #One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 100,  'Incident Level', #One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Distributing/selling
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 101,  'Incident Level', #One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Exploiting children
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 102,  'Incident Level', #One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 103,  'Incident Level', #One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Possessing/concealing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 104,  'Incident Level', #One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 105,  'Incident Level', #One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Using/consuming
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 106,  'Incident Level', #One Criminal Activity or One Suspected Drug Stimulant (L, M): Buying/receiving
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 107,  'Incident Level', #One Criminal Activity or One Suspected Drug Stimulant (L, M): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 108,  'Incident Level', #One Criminal Activity or One Suspected Drug Stimulant (L, M): Distributing/selling
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 109,  'Incident Level', #One Criminal Activity or One Suspected Drug Stimulant (L, M): Exploiting children
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 110,  'Incident Level', #One Criminal Activity or One Suspected Drug Stimulant (L, M): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 111,  'Incident Level', #One Criminal Activity or One Suspected Drug Stimulant (L, M): Possessing/concealing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 112,  'Incident Level', #One Criminal Activity or One Suspected Drug Stimulant (L, M): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 113,  'Incident Level', #One Criminal Activity or One Suspected Drug Stimulant (L, M): Using/consuming
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 114,  'Incident Level', #One Criminal Activity or One Suspected Drug Depressant (N, O): Buying/receiving
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 115,  'Incident Level', #One Criminal Activity or One Suspected Drug Depressant (N, O): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 116,  'Incident Level', #One Criminal Activity or One Suspected Drug Depressant (N, O): Distributing/selling
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 117,  'Incident Level', #One Criminal Activity or One Suspected Drug Depressant (N, O): Exploiting children
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 118,  'Incident Level', #One Criminal Activity or One Suspected Drug Depressant (N, O): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 119,  'Incident Level', #One Criminal Activity or One Suspected Drug Depressant (N, O): Possessing/concealing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 120,  'Incident Level', #One Criminal Activity or One Suspected Drug Depressant (N, O): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 121,  'Incident Level', #One Criminal Activity or One Suspected Drug Depressant (N, O): Using/consuming
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 122,  'Incident Level', #One Criminal Activity or One Suspected Drug Other (P): Buying/receiving
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 123,  'Incident Level', #One Criminal Activity or One Suspected Drug Other (P): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 124,  'Incident Level', #One Criminal Activity or One Suspected Drug Other (P): Distributing/selling
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 125,  'Incident Level', #One Criminal Activity or One Suspected Drug Other (P): Exploiting children
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 126,  'Incident Level', #One Criminal Activity or One Suspected Drug Other (P): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 127,  'Incident Level', #One Criminal Activity or One Suspected Drug Other (P): Possessing/concealing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 128,  'Incident Level', #One Criminal Activity or One Suspected Drug Other (P): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 129,  'Incident Level', #One Criminal Activity or One Suspected Drug Other (P): Using/consuming
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 130,  'Incident Level', #One Criminal Activity or One Suspected Drug Unknown (U): Buying/receiving
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 131,  'Incident Level', #One Criminal Activity or One Suspected Drug Unknown (U): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 132,  'Incident Level', #One Criminal Activity or One Suspected Drug Unknown (U): Distributing/selling
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 133,  'Incident Level', #One Criminal Activity or One Suspected Drug Unknown (U): Exploiting children
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 134,  'Incident Level', #One Criminal Activity or One Suspected Drug Unknown (U): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 135,  'Incident Level', #One Criminal Activity or One Suspected Drug Unknown (U): Possessing/concealing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 136,  'Incident Level', #One Criminal Activity or One Suspected Drug Unknown (U): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 137,  'Incident Level', #One Criminal Activity or One Suspected Drug Unknown (U): Using/consuming
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 138,  'Incident Level', #One Criminal Activity or One Suspected Drug More Than 3 Types (X): Buying/receiving
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 139,  'Incident Level', #One Criminal Activity or One Suspected Drug More Than 3 Types (X): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 140,  'Incident Level', #One Criminal Activity or One Suspected Drug More Than 3 Types (X): Distributing/selling
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 141,  'Incident Level', #One Criminal Activity or One Suspected Drug More Than 3 Types (X): Exploiting children
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 142,  'Incident Level', #One Criminal Activity or One Suspected Drug More Than 3 Types (X): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 143,  'Incident Level', #One Criminal Activity or One Suspected Drug More Than 3 Types (X): Possessing/concealing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 144,  'Incident Level', #One Criminal Activity or One Suspected Drug More Than 3 Types (X): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('PERCENTAGE') & row == 145,  'Incident Level' #One Criminal Activity or One Suspected Drug More Than 3 Types (X): Using/consuming



))

  return(returndata)
}

estimate_type_detail_rate_label <- function(indata){

  returndata <- indata %>%
    mutate(
      estimate_type_detail_rate = fcase(

trim_upcase(estimate_type) %in% c('RATE') & row == 1,  DER_NA_CODE_STRING, #Total
trim_upcase(estimate_type) %in% c('RATE') & row == 2,  DER_NA_CODE_STRING, #Cocaine/crack cocaine (A, B): Buying/receiving
trim_upcase(estimate_type) %in% c('RATE') & row == 3,  DER_NA_CODE_STRING, #Cocaine/crack cocaine (A, B): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('RATE') & row == 4,  DER_NA_CODE_STRING, #Cocaine/crack cocaine (A, B): Distributing/selling
trim_upcase(estimate_type) %in% c('RATE') & row == 5,  DER_NA_CODE_STRING, #Cocaine/crack cocaine (A, B): Exploiting children
trim_upcase(estimate_type) %in% c('RATE') & row == 6,  DER_NA_CODE_STRING, #Cocaine/crack cocaine (A, B): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('RATE') & row == 7,  DER_NA_CODE_STRING, #Cocaine/crack cocaine (A, B): Possessing/concealing
trim_upcase(estimate_type) %in% c('RATE') & row == 8,  DER_NA_CODE_STRING, #Cocaine/crack cocaine (A, B): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('RATE') & row == 9,  DER_NA_CODE_STRING, #Cocaine/crack cocaine (A, B): Using/consuming
trim_upcase(estimate_type) %in% c('RATE') & row == 10,  DER_NA_CODE_STRING, #Marijuana/hashish (C, E): Buying/receiving
trim_upcase(estimate_type) %in% c('RATE') & row == 11,  DER_NA_CODE_STRING, #Marijuana/hashish (C, E): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('RATE') & row == 12,  DER_NA_CODE_STRING, #Marijuana/hashish (C, E): Distributing/selling
trim_upcase(estimate_type) %in% c('RATE') & row == 13,  DER_NA_CODE_STRING, #Marijuana/hashish (C, E): Exploiting children
trim_upcase(estimate_type) %in% c('RATE') & row == 14,  DER_NA_CODE_STRING, #Marijuana/hashish (C, E): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('RATE') & row == 15,  DER_NA_CODE_STRING, #Marijuana/hashish (C, E): Possessing/concealing
trim_upcase(estimate_type) %in% c('RATE') & row == 16,  DER_NA_CODE_STRING, #Marijuana/hashish (C, E): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('RATE') & row == 17,  DER_NA_CODE_STRING, #Marijuana/hashish (C, E): Using/consuming
trim_upcase(estimate_type) %in% c('RATE') & row == 18,  DER_NA_CODE_STRING, #Opiate/narcotic (D, F, G, H): Buying/receiving
trim_upcase(estimate_type) %in% c('RATE') & row == 19,  DER_NA_CODE_STRING, #Opiate/narcotic (D, F, G, H): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('RATE') & row == 20,  DER_NA_CODE_STRING, #Opiate/narcotic (D, F, G, H): Distributing/selling
trim_upcase(estimate_type) %in% c('RATE') & row == 21,  DER_NA_CODE_STRING, #Opiate/narcotic (D, F, G, H): Exploiting children
trim_upcase(estimate_type) %in% c('RATE') & row == 22,  DER_NA_CODE_STRING, #Opiate/narcotic (D, F, G, H): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('RATE') & row == 23,  DER_NA_CODE_STRING, #Opiate/narcotic (D, F, G, H): Possessing/concealing
trim_upcase(estimate_type) %in% c('RATE') & row == 24,  DER_NA_CODE_STRING, #Opiate/narcotic (D, F, G, H): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('RATE') & row == 25,  DER_NA_CODE_STRING, #Opiate/narcotic (D, F, G, H): Using/consuming
trim_upcase(estimate_type) %in% c('RATE') & row == 26,  DER_NA_CODE_STRING, #Hallucinogen (I, J, K): Buying/receiving
trim_upcase(estimate_type) %in% c('RATE') & row == 27,  DER_NA_CODE_STRING, #Hallucinogen (I, J, K): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('RATE') & row == 28,  DER_NA_CODE_STRING, #Hallucinogen (I, J, K): Distributing/selling
trim_upcase(estimate_type) %in% c('RATE') & row == 29,  DER_NA_CODE_STRING, #Hallucinogen (I, J, K): Exploiting children
trim_upcase(estimate_type) %in% c('RATE') & row == 30,  DER_NA_CODE_STRING, #Hallucinogen (I, J, K): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('RATE') & row == 31,  DER_NA_CODE_STRING, #Hallucinogen (I, J, K): Possessing/concealing
trim_upcase(estimate_type) %in% c('RATE') & row == 32,  DER_NA_CODE_STRING, #Hallucinogen (I, J, K): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('RATE') & row == 33,  DER_NA_CODE_STRING, #Hallucinogen (I, J, K): Using/consuming
trim_upcase(estimate_type) %in% c('RATE') & row == 34,  DER_NA_CODE_STRING, #Stimulant (L, M): Buying/receiving
trim_upcase(estimate_type) %in% c('RATE') & row == 35,  DER_NA_CODE_STRING, #Stimulant (L, M): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('RATE') & row == 36,  DER_NA_CODE_STRING, #Stimulant (L, M): Distributing/selling
trim_upcase(estimate_type) %in% c('RATE') & row == 37,  DER_NA_CODE_STRING, #Stimulant (L, M): Exploiting children
trim_upcase(estimate_type) %in% c('RATE') & row == 38,  DER_NA_CODE_STRING, #Stimulant (L, M): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('RATE') & row == 39,  DER_NA_CODE_STRING, #Stimulant (L, M): Possessing/concealing
trim_upcase(estimate_type) %in% c('RATE') & row == 40,  DER_NA_CODE_STRING, #Stimulant (L, M): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('RATE') & row == 41,  DER_NA_CODE_STRING, #Stimulant (L, M): Using/consuming
trim_upcase(estimate_type) %in% c('RATE') & row == 42,  DER_NA_CODE_STRING, #Depressant (N, O): Buying/receiving
trim_upcase(estimate_type) %in% c('RATE') & row == 43,  DER_NA_CODE_STRING, #Depressant (N, O): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('RATE') & row == 44,  DER_NA_CODE_STRING, #Depressant (N, O): Distributing/selling
trim_upcase(estimate_type) %in% c('RATE') & row == 45,  DER_NA_CODE_STRING, #Depressant (N, O): Exploiting children
trim_upcase(estimate_type) %in% c('RATE') & row == 46,  DER_NA_CODE_STRING, #Depressant (N, O): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('RATE') & row == 47,  DER_NA_CODE_STRING, #Depressant (N, O): Possessing/concealing
trim_upcase(estimate_type) %in% c('RATE') & row == 48,  DER_NA_CODE_STRING, #Depressant (N, O): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('RATE') & row == 49,  DER_NA_CODE_STRING, #Depressant (N, O): Using/consuming
trim_upcase(estimate_type) %in% c('RATE') & row == 50,  DER_NA_CODE_STRING, #Other (P): Buying/receiving
trim_upcase(estimate_type) %in% c('RATE') & row == 51,  DER_NA_CODE_STRING, #Other (P): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('RATE') & row == 52,  DER_NA_CODE_STRING, #Other (P): Distributing/selling
trim_upcase(estimate_type) %in% c('RATE') & row == 53,  DER_NA_CODE_STRING, #Other (P): Exploiting children
trim_upcase(estimate_type) %in% c('RATE') & row == 54,  DER_NA_CODE_STRING, #Other (P): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('RATE') & row == 55,  DER_NA_CODE_STRING, #Other (P): Possessing/concealing
trim_upcase(estimate_type) %in% c('RATE') & row == 56,  DER_NA_CODE_STRING, #Other (P): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('RATE') & row == 57,  DER_NA_CODE_STRING, #Other (P): Using/consuming
trim_upcase(estimate_type) %in% c('RATE') & row == 58,  DER_NA_CODE_STRING, #Unknown (U): Buying/receiving
trim_upcase(estimate_type) %in% c('RATE') & row == 59,  DER_NA_CODE_STRING, #Unknown (U): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('RATE') & row == 60,  DER_NA_CODE_STRING, #Unknown (U): Distributing/selling
trim_upcase(estimate_type) %in% c('RATE') & row == 61,  DER_NA_CODE_STRING, #Unknown (U): Exploiting children
trim_upcase(estimate_type) %in% c('RATE') & row == 62,  DER_NA_CODE_STRING, #Unknown (U): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('RATE') & row == 63,  DER_NA_CODE_STRING, #Unknown (U): Possessing/concealing
trim_upcase(estimate_type) %in% c('RATE') & row == 64,  DER_NA_CODE_STRING, #Unknown (U): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('RATE') & row == 65,  DER_NA_CODE_STRING, #Unknown (U): Using/consuming
trim_upcase(estimate_type) %in% c('RATE') & row == 66,  DER_NA_CODE_STRING, #More Than 3 Types (X): Buying/receiving
trim_upcase(estimate_type) %in% c('RATE') & row == 67,  DER_NA_CODE_STRING, #More Than 3 Types (X): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('RATE') & row == 68,  DER_NA_CODE_STRING, #More Than 3 Types (X): Distributing/selling
trim_upcase(estimate_type) %in% c('RATE') & row == 69,  DER_NA_CODE_STRING, #More Than 3 Types (X): Exploiting children
trim_upcase(estimate_type) %in% c('RATE') & row == 70,  DER_NA_CODE_STRING, #More Than 3 Types (X): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('RATE') & row == 71,  DER_NA_CODE_STRING, #More Than 3 Types (X): Possessing/concealing
trim_upcase(estimate_type) %in% c('RATE') & row == 72,  DER_NA_CODE_STRING, #More Than 3 Types (X): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('RATE') & row == 73,  DER_NA_CODE_STRING, #More Than 3 Types (X): Using/consuming
trim_upcase(estimate_type) %in% c('RATE') & row == 74,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Buying/receiving
trim_upcase(estimate_type) %in% c('RATE') & row == 75,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('RATE') & row == 76,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Distributing/selling
trim_upcase(estimate_type) %in% c('RATE') & row == 77,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Exploiting children
trim_upcase(estimate_type) %in% c('RATE') & row == 78,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('RATE') & row == 79,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Possessing/concealing
trim_upcase(estimate_type) %in% c('RATE') & row == 80,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('RATE') & row == 81,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Cocaine/crack cocaine (A, B): Using/consuming
trim_upcase(estimate_type) %in% c('RATE') & row == 82,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Buying/receiving
trim_upcase(estimate_type) %in% c('RATE') & row == 83,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('RATE') & row == 84,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Distributing/selling
trim_upcase(estimate_type) %in% c('RATE') & row == 85,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Exploiting children
trim_upcase(estimate_type) %in% c('RATE') & row == 86,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('RATE') & row == 87,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Possessing/concealing
trim_upcase(estimate_type) %in% c('RATE') & row == 88,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('RATE') & row == 89,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Marijuana/hashish (C, E): Using/consuming
trim_upcase(estimate_type) %in% c('RATE') & row == 90,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Buying/receiving
trim_upcase(estimate_type) %in% c('RATE') & row == 91,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('RATE') & row == 92,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Distributing/selling
trim_upcase(estimate_type) %in% c('RATE') & row == 93,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Exploiting children
trim_upcase(estimate_type) %in% c('RATE') & row == 94,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('RATE') & row == 95,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Possessing/concealing
trim_upcase(estimate_type) %in% c('RATE') & row == 96,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('RATE') & row == 97,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Opiate/narcotic (D, F, G, H): Using/consuming
trim_upcase(estimate_type) %in% c('RATE') & row == 98,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Buying/receiving
trim_upcase(estimate_type) %in% c('RATE') & row == 99,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('RATE') & row == 100,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Distributing/selling
trim_upcase(estimate_type) %in% c('RATE') & row == 101,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Exploiting children
trim_upcase(estimate_type) %in% c('RATE') & row == 102,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('RATE') & row == 103,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Possessing/concealing
trim_upcase(estimate_type) %in% c('RATE') & row == 104,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('RATE') & row == 105,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Hallucinogen (I, J, K): Using/consuming
trim_upcase(estimate_type) %in% c('RATE') & row == 106,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Stimulant (L, M): Buying/receiving
trim_upcase(estimate_type) %in% c('RATE') & row == 107,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Stimulant (L, M): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('RATE') & row == 108,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Stimulant (L, M): Distributing/selling
trim_upcase(estimate_type) %in% c('RATE') & row == 109,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Stimulant (L, M): Exploiting children
trim_upcase(estimate_type) %in% c('RATE') & row == 110,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Stimulant (L, M): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('RATE') & row == 111,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Stimulant (L, M): Possessing/concealing
trim_upcase(estimate_type) %in% c('RATE') & row == 112,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Stimulant (L, M): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('RATE') & row == 113,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Stimulant (L, M): Using/consuming
trim_upcase(estimate_type) %in% c('RATE') & row == 114,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Depressant (N, O): Buying/receiving
trim_upcase(estimate_type) %in% c('RATE') & row == 115,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Depressant (N, O): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('RATE') & row == 116,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Depressant (N, O): Distributing/selling
trim_upcase(estimate_type) %in% c('RATE') & row == 117,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Depressant (N, O): Exploiting children
trim_upcase(estimate_type) %in% c('RATE') & row == 118,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Depressant (N, O): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('RATE') & row == 119,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Depressant (N, O): Possessing/concealing
trim_upcase(estimate_type) %in% c('RATE') & row == 120,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Depressant (N, O): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('RATE') & row == 121,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Depressant (N, O): Using/consuming
trim_upcase(estimate_type) %in% c('RATE') & row == 122,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Other (P): Buying/receiving
trim_upcase(estimate_type) %in% c('RATE') & row == 123,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Other (P): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('RATE') & row == 124,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Other (P): Distributing/selling
trim_upcase(estimate_type) %in% c('RATE') & row == 125,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Other (P): Exploiting children
trim_upcase(estimate_type) %in% c('RATE') & row == 126,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Other (P): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('RATE') & row == 127,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Other (P): Possessing/concealing
trim_upcase(estimate_type) %in% c('RATE') & row == 128,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Other (P): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('RATE') & row == 129,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Other (P): Using/consuming
trim_upcase(estimate_type) %in% c('RATE') & row == 130,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Unknown (U): Buying/receiving
trim_upcase(estimate_type) %in% c('RATE') & row == 131,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Unknown (U): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('RATE') & row == 132,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Unknown (U): Distributing/selling
trim_upcase(estimate_type) %in% c('RATE') & row == 133,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Unknown (U): Exploiting children
trim_upcase(estimate_type) %in% c('RATE') & row == 134,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Unknown (U): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('RATE') & row == 135,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Unknown (U): Possessing/concealing
trim_upcase(estimate_type) %in% c('RATE') & row == 136,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Unknown (U): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('RATE') & row == 137,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug Unknown (U): Using/consuming
trim_upcase(estimate_type) %in% c('RATE') & row == 138,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug More Than 3 Types (X): Buying/receiving
trim_upcase(estimate_type) %in% c('RATE') & row == 139,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug More Than 3 Types (X): Cultivating/manufacturing/publishing
trim_upcase(estimate_type) %in% c('RATE') & row == 140,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug More Than 3 Types (X): Distributing/selling
trim_upcase(estimate_type) %in% c('RATE') & row == 141,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug More Than 3 Types (X): Exploiting children
trim_upcase(estimate_type) %in% c('RATE') & row == 142,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug More Than 3 Types (X): Operating/promoting/assisting
trim_upcase(estimate_type) %in% c('RATE') & row == 143,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug More Than 3 Types (X): Possessing/concealing
trim_upcase(estimate_type) %in% c('RATE') & row == 144,  DER_NA_CODE_STRING, #One Criminal Activity or One Suspected Drug More Than 3 Types (X): Transporting/transmitting/importing
trim_upcase(estimate_type) %in% c('RATE') & row == 145,  DER_NA_CODE_STRING #One Criminal Activity or One Suspected Drug More Than 3 Types (X): Using/consuming



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
  main_filter <- maindata %>%
    ############################################
    filter(!!infilter) %>%
    #Deduplicate by Incident ID, and one instance of crime type
    group_by(ori, incident_id, !!infiltervar) %>%
    mutate(raw_first = row_number() == 1 ) %>%
    ungroup() %>%
    filter(raw_first == TRUE) %>%
    select(-raw_first) %>%

    select(ori, weight, incident_id, !!infiltervar)

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

  #Drug by Criminal Activity
  s2 <- agg_percent_by_incident_id_CAA(leftdata = main_filter, rightdata = agg_suspected_type_of_drug_crim_activity_35A_c, var=der_suspected_type_of_drug_crim_activity, section=2, denom=der_total_denom)


  #One Criminal Activity or One Suspected Drug
  s3 <- agg_percent_by_incident_id_CAA(leftdata = main_filter, rightdata = agg_1suspected_type_of_drug_1crim_activity_35A_c, var=der_1suspected_type_of_drug_1crim_activity, section=3, denom=der_total_denom)

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
    mutate(final_count = case_when(is.na(final_count) ~ 0,
                                   TRUE ~ final_count),
           percent = case_when(is.na(percent) ~ 0,
                                   TRUE ~ percent),

           #UPDATE this for each table:  Make the estimates of the database
           count    = case_when(row %in% c(1:145) ~ final_count,
                                      TRUE ~ DER_NA_CODE),
           percentage  = case_when(
                                      TRUE ~ DER_NA_CODE),
           rate     = case_when(
                                      TRUE ~ DER_NA_CODE),
           population_estimate     = case_when(
                                      TRUE ~ DER_NA_CODE)
           ) %>%
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
