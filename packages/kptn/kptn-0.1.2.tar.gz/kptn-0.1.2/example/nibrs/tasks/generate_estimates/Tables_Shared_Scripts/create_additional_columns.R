library(tidyverse)
library(openxlsx)
library(DBI)
library(DT)
library(lubridate)
library(data.table)
library(logger)

DER_TABLE_NAME <- Sys.getenv("DER_TABLE_NAME")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
in_file_path = paste0(inputPipelineDir, "/indicator_table_single_intermediate/")
load(paste0(in_file_path,"/",DER_TABLE_NAME,"_prep_env.RData"))

source(here::here("tasks/logging.R"))

args = commandArgs(trailingOnly=TRUE)
if (length(args)==0) {
  stop("This script expects a series number between 1000 and 260000", call.=FALSE)
} else if (length(args)==2) {
  series <- as.integer(args[1])
  colindex <- as.integer(args[2])
} else {
  stop("This script expects a series number between 1000 and 144000 followed by a column number.", call.=FALSE)
}

log_debug(system("free -mh", intern = FALSE))
if(series==1000){
  insubset <- "der_new_column_age  == 1" #Age: Under 5
} else if(series==2000){
  insubset <- "der_new_column_age  == 2" #Age: 5-14
} else if(series==3000){
  insubset <- "der_new_column_age  == 3" #Age:15
} else if(series==4000){
  insubset <- "der_new_column_age  == 4" #Age:16
} else if(series==5000){
  insubset <- "der_new_column_age  == 5" #Age:17
} else if(series==6000){
  insubset <- "der_new_column_age  == 6" #Age: 18-24
} else if(series==7000){
  insubset <- "der_new_column_age  == 7" #Age: 25-34
} else if(series==8000){
  insubset <- "der_new_column_age  == 8" #Age: 35-64
} else if(series==9000){
  insubset <- "der_new_column_age  == 9" #Age: 65+
} else if(series==10000){
  insubset <- "der_new_column_gender == 1" #Sex: Male
} else if(series==11000){
  insubset <- "der_new_column_gender == 2" #Sex: Female
} else if(series==12000){
  insubset <- "der_new_column_race == 1" #Race: White
} else if(series==13000){
  insubset <- "der_new_column_race == 2" #Race: Black
} else if(series==14000){
  insubset <- "der_new_column_race == 3" #Race: American Indian or Alaska Native
} else if(series==15000){
  insubset <- "der_new_column_race == 4" #Race: Asian
} else if(series==16000){
  insubset <- "der_new_column_race == 5" #Race: Native Hawaiian or Other Pacific
} else if(series==17000){
  insubset <- "der_new_column_age  %in% c(6:9)" #Age:18+
} else if(series==18000){
  insubset <- "der_new_column_age  %in% c(1:5)" #Age:Under 18
} else if(series==19000){
  insubset <- "der_new_column_age  %in% c(1:2)" #Age:Under 15
} else if(series==20000){
  insubset <- "der_new_column_race %in% c(3:5)" #Race:American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander
} else if(series==21000){
  insubset <- "der_new_column_age_round %in% c(0:11)" #Under 12
} else if(series==22000){
  insubset <- "der_new_column_age_round %in% c(12:17)" #12-17
} else if(series==23000){
  insubset <- "der_new_column_age_round %in% c(12:14)" #12-14
} else if(series==24000){
  insubset <- "der_new_column_age_round %in% c(15:17)" #15-17
} else if(series==25000){
  insubset <- "der_new_column_age_round >= 12" #12 or older
} else if(series==26000){
  insubset <- "der_new_column_race %in% c(4:5)" #Asian or Hawaiian/Pacific Islander
} else if(series==27000){
  insubset <- "der_new_column_age_round %in% c(18:64)" #18-64
} else if(series==28000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 1" #Sex:Male & Race:White"
} else if(series==29000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 2" #Sex:Male & Race:Black"
} else if(series==30000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 3" #Sex:Male & Race:American Indian or Alaska Native"
} else if(series==31000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 4" #Sex:Male & Race:Asian"
} else if(series==32000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 5" #Sex:Male & Race:Native Hawaiian or Other Pacific"
} else if(series==33000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race %in% c(3:5)" #Sex:Male & Race:American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander"
} else if(series==34000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race %in% c(4:5)" #Sex:Male & #Race:Asian or Native Hawaiian or Other Pacific"
} else if(series==35000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 1" #Sex:Female & Race:White"
} else if(series==36000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 2" #Sex:Female & Race:Black"
} else if(series==37000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 3" #Sex:Female & Race:American Indian or Alaska Native"
} else if(series==38000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 4" #Sex:Female & Race:Asian"
} else if(series==39000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 5" #Sex:Female & Race:Native Hawaiian or Other Pacific"
} else if(series==40000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race %in% c(3:5)" #Sex:Female & Race:American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander"
} else if(series==41000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race %in% c(4:5)" #Sex:Female & #Race:Asian or Native Hawaiian or Other Pacific"
} else if(series==42000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 1 & der_new_column_age_round %in% c(0:11)" #Sex:Male & Race:White & Age:Under 12"
} else if(series==43000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 2 & der_new_column_age_round %in% c(0:11)" #Sex:Male & Race:Black & Age:Under 12"
} else if(series==44000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 3 & der_new_column_age_round %in% c(0:11)" #Sex:Male & Race:American Indian or Alaska Native & Age:Under 12"
} else if(series==45000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 4 & der_new_column_age_round %in% c(0:11)" #Sex:Male & Race:Asian & Age:Under 12"
} else if(series==46000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 5 & der_new_column_age_round %in% c(0:11)" #Sex:Male & Race:Native Hawaiian or Other Pacific & Age:Under 12"
} else if(series==47000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race %in% c(3:5) & der_new_column_age_round %in% c(0:11)" #Sex:Male & Race:American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander & Age:Under 12"
} else if(series==48000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race %in% c(4:5) & der_new_column_age_round %in% c(0:11)" #Sex:Male & #Race:Asian or Native Hawaiian or Other Pacific & Age:Under 12"
} else if(series==49000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 1 & der_new_column_age_round %in% c(0:11)" #Sex:Female & Race:White & Age:Under 12"
} else if(series==50000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 2 & der_new_column_age_round %in% c(0:11)" #Sex:Female & Race:Black & Age:Under 12"
} else if(series==51000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 3 & der_new_column_age_round %in% c(0:11)" #Sex:Female & Race:American Indian or Alaska Native & Age:Under 12"
} else if(series==52000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 4 & der_new_column_age_round %in% c(0:11)" #Sex:Female & Race:Asian & Age:Under 12"
} else if(series==53000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 5 & der_new_column_age_round %in% c(0:11)" #Sex:Female & Race:Native Hawaiian or Other Pacific & Age:Under 12"
} else if(series==54000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race %in% c(3:5) & der_new_column_age_round %in% c(0:11)" #Sex:Female & Race:American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander & Age:Under 12"
} else if(series==55000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race %in% c(4:5) & der_new_column_age_round %in% c(0:11)" #Sex:Female & #Race:Asian or Native Hawaiian or Other Pacific & Age:Under 12"
} else if(series==56000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 1 & der_new_column_age_round %in% c(12:17)" #Sex:Male & Race:White & Age:12-17"
} else if(series==57000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 2 & der_new_column_age_round %in% c(12:17)" #Sex:Male & Race:Black & Age:12-17"
} else if(series==58000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 3 & der_new_column_age_round %in% c(12:17)" #Sex:Male & Race:American Indian or Alaska Native & Age:12-17"
} else if(series==59000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 4 & der_new_column_age_round %in% c(12:17)" #Sex:Male & Race:Asian & Age:12-17"
} else if(series==60000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 5 & der_new_column_age_round %in% c(12:17)" #Sex:Male & Race:Native Hawaiian or Other Pacific & Age:12-17"
} else if(series==61000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race %in% c(3:5) & der_new_column_age_round %in% c(12:17)" #Sex:Male & Race:American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander & Age:12-17"
} else if(series==62000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race %in% c(4:5) & der_new_column_age_round %in% c(12:17)" #Sex:Male & #Race:Asian or Native Hawaiian or Other Pacific & Age:12-17"
} else if(series==63000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 1 & der_new_column_age_round %in% c(12:17)" #Sex:Female & Race:White & Age:12-17"
} else if(series==64000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 2 & der_new_column_age_round %in% c(12:17)" #Sex:Female & Race:Black & Age:12-17"
} else if(series==65000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 3 & der_new_column_age_round %in% c(12:17)" #Sex:Female & Race:American Indian or Alaska Native & Age:12-17"
} else if(series==66000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 4 & der_new_column_age_round %in% c(12:17)" #Sex:Female & Race:Asian & Age:12-17"
} else if(series==67000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 5 & der_new_column_age_round %in% c(12:17)" #Sex:Female & Race:Native Hawaiian or Other Pacific & Age:12-17"
} else if(series==68000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race %in% c(3:5) & der_new_column_age_round %in% c(12:17)" #Sex:Female & Race:American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander & Age:12-17"
} else if(series==69000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race %in% c(4:5) & der_new_column_age_round %in% c(12:17)" #Sex:Female & #Race:Asian or Native Hawaiian or Other Pacific & Age:12-17"
} else if(series==70000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 1 & der_new_column_age_round >= 18" #Sex:Male & Race:White & Age:18+"
} else if(series==71000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 2 & der_new_column_age_round >= 18" #Sex:Male & Race:Black & Age:18+"
} else if(series==72000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 3 & der_new_column_age_round >= 18" #Sex:Male & Race:American Indian or Alaska Native & Age:18+"
} else if(series==73000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 4 & der_new_column_age_round >= 18" #Sex:Male & Race:Asian & Age:18+"
} else if(series==74000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 5 & der_new_column_age_round >= 18" #Sex:Male & Race:Native Hawaiian or Other Pacific & Age:18+"
} else if(series==75000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race %in% c(3:5) & der_new_column_age_round >= 18" #Sex:Male & Race:American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander & Age:18+"
} else if(series==76000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race %in% c(4:5) & der_new_column_age_round >= 18" #Sex:Male & #Race:Asian or Native Hawaiian or Other Pacific & Age:18+"
} else if(series==77000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 1 & der_new_column_age_round >= 18" #Sex:Female & Race:White & Age:18+"
} else if(series==78000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 2 & der_new_column_age_round >= 18" #Sex:Female & Race:Black & Age:18+"
} else if(series==79000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 3 & der_new_column_age_round >= 18" #Sex:Female & Race:American Indian or Alaska Native & Age:18+"
} else if(series==80000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 4 & der_new_column_age_round >= 18" #Sex:Female & Race:Asian & Age:18+"
} else if(series==81000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 5 & der_new_column_age_round >= 18" #Sex:Female & Race:Native Hawaiian or Other Pacific & Age:18+"
} else if(series==82000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race %in% c(3:5) & der_new_column_age_round >= 18" #Sex:Female & Race:American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander & Age:18+"
} else if(series==83000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race %in% c(4:5) & der_new_column_age_round >= 18" #Sex:Female & #Race:Asian or Native Hawaiian or Other Pacific & Age:18+"
} else if(series==84000){
  insubset <- "der_new_column_gender == 1 & der_new_column_age_round %in% c(18:24)" #Sex:Male & Age:18-24"
} else if(series==85000){
  insubset <- "der_new_column_gender == 1 & der_new_column_age_round %in% c(25:34)" #Sex:Male & Age:25-34"
} else if(series==86000){
  insubset <- "der_new_column_gender == 1 & der_new_column_age_round %in% c(35:64)" #Sex:Male & Age:35-64"
} else if(series==87000){
  insubset <- "der_new_column_gender == 1 & der_new_column_age_round >= 65" #Sex:Male & Age:65+"
} else if(series==88000){
  insubset <- "der_new_column_gender == 1 & der_new_column_age_round >= 18" #Sex:Male & Age:18+"
} else if(series==89000){
  insubset <- "der_new_column_gender == 1 & der_new_column_age_round %in% c(0:17)" #Sex:Male & Age:Under 18"
} else if(series==90000){
  insubset <- "der_new_column_gender == 1 & der_new_column_age_round %in% c(0:11)" #Sex:Male & Age:Under 12"
} else if(series==91000){
  insubset <- "der_new_column_gender == 1 & der_new_column_age_round %in% c(12:17)" #Sex:Male & Age:12-17"
} else if(series==92000){
  insubset <- "der_new_column_gender == 1 & der_new_column_age_round %in% c(12:14)" #Sex:Male & Age:12-14"
} else if(series==93000){
  insubset <- "der_new_column_gender == 1 & der_new_column_age_round %in% c(15:17)" #Sex:Male & Age:15-17"
} else if(series==94000){
  insubset <- "der_new_column_gender == 1 & der_new_column_age_round >= 12" #Sex:Male & Age:12 or older"
} else if(series==95000){
  insubset <- "der_new_column_gender == 2 & der_new_column_age_round %in% c(18:24)" #Sex:Female & Age:18-24"
} else if(series==96000){
  insubset <- "der_new_column_gender == 2 & der_new_column_age_round %in% c(25:34)" #Sex:Female & Age:25-34"
} else if(series==97000){
  insubset <- "der_new_column_gender == 2 & der_new_column_age_round %in% c(35:64)" #Sex:Female & Age:35-64"
} else if(series==98000){
  insubset <- "der_new_column_gender == 2 & der_new_column_age_round >= 65" #Sex:Female & Age:65+"
} else if(series==99000){
  insubset <- "der_new_column_gender == 2 & der_new_column_age_round >= 18" #Sex:Female & Age:18+"
} else if(series==100000){
  insubset <- "der_new_column_gender == 2 & der_new_column_age_round %in% c(0:17)" #Sex:Female & Age:Under 18"
} else if(series==101000){
  insubset <- "der_new_column_gender == 2 & der_new_column_age_round %in% c(0:11)" #Sex:Female & Age:Under 12"
} else if(series==102000){
  insubset <- "der_new_column_gender == 2 & der_new_column_age_round %in% c(12:17)" #Sex:Female & Age:12-17"
} else if(series==103000){
  insubset <- "der_new_column_gender == 2 & der_new_column_age_round %in% c(12:14)" #Sex:Female & Age:12-14"
} else if(series==104000){
  insubset <- "der_new_column_gender == 2 & der_new_column_age_round %in% c(15:17)" #Sex:Female & Age:15-17"
} else if(series==105000){
  insubset <- "der_new_column_gender == 2 & der_new_column_age_round >= 12" #Sex:Female & Age:12 or older"
} else if(series==106000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 1 & der_new_column_age_round %in% c(18:24)" #Sex:Male & Race:White & Age:18-24"
} else if(series==107000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 1 & der_new_column_age_round %in% c(25:34)" #Sex:Male & Race:White & Age:25-34"
} else if(series==108000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 1 & der_new_column_age_round %in% c(35:64)" #Sex:Male & Race:White & Age:35-64"
} else if(series==109000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 1 & der_new_column_age_round >= 65" #Sex:Male & Race:White & Age:65+"
} else if(series==110000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 1 & der_new_column_age_round %in% c(0:17)" #Sex:Male & Race:White & Age:Under 18"
} else if(series==111000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 2 & der_new_column_age_round %in% c(18:24)" #Sex:Male & Race:Black & Age:18-24"
} else if(series==112000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 2 & der_new_column_age_round %in% c(25:34)" #Sex:Male & Race:Black & Age:25-34"
} else if(series==113000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 2 & der_new_column_age_round %in% c(35:64)" #Sex:Male & Race:Black & Age:35-64"
} else if(series==114000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 2 & der_new_column_age_round >= 65" #Sex:Male & Race:Black & Age:65+"
} else if(series==115000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race == 2 & der_new_column_age_round %in% c(0:17)" #Sex:Male & Race:Black & Age:Under 18"
} else if(series==116000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race %in% c(3:5) & der_new_column_age_round %in% c(18:24)" #Sex:Male & Race:American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander & Age:18-24"
} else if(series==117000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race %in% c(3:5) & der_new_column_age_round %in% c(25:34)" #Sex:Male & Race:American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander & Age:25-34"
} else if(series==118000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race %in% c(3:5) & der_new_column_age_round %in% c(35:64)" #Sex:Male & Race:American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander & Age:35-64"
} else if(series==119000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race %in% c(3:5) & der_new_column_age_round >= 65" #Sex:Male & Race:American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander & Age:65+"
} else if(series==120000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race %in% c(3:5) & der_new_column_age_round %in% c(0:17)" #Sex:Male & Race:American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander & Age:Under 18"
} else if(series==121000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 1 & der_new_column_age_round %in% c(18:24)" #Sex:Female & Race:White & Age:18-24"
} else if(series==122000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 1 & der_new_column_age_round %in% c(25:34)" #Sex:Female & Race:White & Age:25-34"
} else if(series==123000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 1 & der_new_column_age_round %in% c(35:64)" #Sex:Female & Race:White & Age:35-64"
} else if(series==124000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 1 & der_new_column_age_round >= 65" #Sex:Female & Race:White & Age:65+"
} else if(series==125000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 1 & der_new_column_age_round %in% c(0:17)" #Sex:Female & Race:White & Age:Under 18"
} else if(series==126000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 2 & der_new_column_age_round %in% c(18:24)" #Sex:Female & Race:Black & Age:18-24"
} else if(series==127000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 2 & der_new_column_age_round %in% c(25:34)" #Sex:Female & Race:Black & Age:25-34"
} else if(series==128000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 2 & der_new_column_age_round %in% c(35:64)" #Sex:Female & Race:Black & Age:35-64"
} else if(series==129000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 2 & der_new_column_age_round >= 65" #Sex:Female & Race:Black & Age:65+"
} else if(series==130000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race == 2 & der_new_column_age_round %in% c(0:17)" #Sex:Female & Race:Black & Age:Under 18"
} else if(series==131000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race %in% c(3:5) & der_new_column_age_round %in% c(18:24)" #Sex:Female & Race:American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander & Age:18-24"
} else if(series==132000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race %in% c(3:5) & der_new_column_age_round %in% c(25:34)" #Sex:Female & Race:American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander & Age:25-34"
} else if(series==133000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race %in% c(3:5) & der_new_column_age_round %in% c(35:64)" #Sex:Female & Race:American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander & Age:35-64"
} else if(series==134000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race %in% c(3:5) & der_new_column_age_round >= 65" #Sex:Female & Race:American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander & Age:65+"
} else if(series==135000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race %in% c(3:5) & der_new_column_age_round %in% c(0:17)" #Sex:Female & Race:American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander & Age:Under 18"
} else if(series==136000){
  insubset <- "der_new_column_age_round %in% c(5:11)" #5-11"
} else if(series==137000){
  insubset <- "der_new_column_gender == 1 & der_new_column_age_round %in% c(5:11)" #Male and 5-11"
} else if(series==138000){
  insubset <- "der_new_column_gender == 2 & der_new_column_age_round %in% c(5:11)" #Female and 5-11"
} else if(series==139000){
  insubset <- "der_new_column_age_round %in% c(12:14)" #12-14"
} else if(series==140000){
  insubset <- "der_new_column_gender == 1 & der_new_column_age_round %in% c(12:14)" #Male and 12-14"
} else if(series==141000){
  insubset <- "der_new_column_gender == 2 & der_new_column_age_round %in% c(12:14)" #Female and 12-14"
} else if(series==142000){
  insubset <- "der_new_column_race %in% c(3, 5)" #American Indian or Alaska Native and Native Hawaiian or Other Pacific Islander"
} else if(series==143000){
  insubset <- "der_new_column_gender == 1 & der_new_column_race %in% c(3, 5)" #Male and American Indian or Alaska Native and Native Hawaiian or Other Pacific Islander"
} else if(series==144000){
  insubset <- "der_new_column_gender == 2 & der_new_column_race %in% c(3, 5)" #Female and American Indian or Alaska Native and Native Hawaiian or Other Pacific Islander"
} else if(series== 145000 ){ 
  insubset <-"der_new_column_ethnicity == 1"# Race :  Hispanic
} else if(series== 146000 ){ 
  insubset <-"der_new_column_ethnicity == 2"# Race :  Non-Hispanic
} else if(series== 147000 ){ 
  insubset <-"der_new_column_ethnicity == 2 & der_new_column_race == 1"# Race :  Non-Hispanic White
} else if(series== 148000 ){ 
  insubset <-"der_new_column_ethnicity == 2 & der_new_column_race == 2"# Race :  Non-Hispanic Black
} else if(series== 149000 ){ 
  insubset <-"der_new_column_ethnicity == 2 & der_new_column_race == 3"# Race :  Non-Hispanic American Indian or Alaska Native
} else if(series== 150000 ){ 
  insubset <-"der_new_column_ethnicity == 2 & der_new_column_race == 4"# Race :  Non-Hispanic Asian
} else if(series== 151000 ){ 
  insubset <-"der_new_column_ethnicity == 2 & der_new_column_race == 5"# Race :  Non-Hispanic Native Hawaiian or Other Pacific Islander
} else if(series== 152000 ){ 
  insubset <-"der_new_column_ethnicity == 2 & der_new_column_race %in% c(3:5)"# Race :  Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander
} else if(series== 153000 ){ 
  insubset <-"der_new_column_ethnicity == 2 & der_new_column_race %in% c(4:5)"# Race :  Non-Hispanic Asian or Native Hawaiian or Other Pacific Islander
} else if(series== 154000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 1"# Sex and Race :  Male and Hispanic
} else if(series== 155000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 1"# Sex and Race :  Male and Non-Hispanic White
} else if(series== 156000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 2"# Sex and Race :  Male and Non-Hispanic Black
} else if(series== 157000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 3"# Sex and Race :  Male and Non-Hispanic American Indian or Alaska Native
} else if(series== 158000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 4"# Sex and Race :  Male and Non-Hispanic Asian
} else if(series== 159000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 5"# Sex and Race :  Male and Non-Hispanic Native Hawaiian or Other Pacific Islander
} else if(series== 160000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race %in% c(3:5)"# Sex and Race :  Male and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander
} else if(series== 161000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race %in% c(4:5)"# Sex and Race :  Male and Non-Hispanic Asian or Native Hawaiian or Other Pacific Islander
} else if(series== 162000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 1"# Sex and Race :  Female and Hispanic
} else if(series== 163000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 1"# Sex and Race :  Female and Non-Hispanic White
} else if(series== 164000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 2"# Sex and Race :  Female and Non-Hispanic Black
} else if(series== 165000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 3"# Sex and Race :  Female and Non-Hispanic American Indian or Alaska Native
} else if(series== 166000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 4"# Sex and Race :  Female and Non-Hispanic Asian
} else if(series== 167000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 5"# Sex and Race :  Female and Non-Hispanic Native Hawaiian or Other Pacific Islander
} else if(series== 168000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race %in% c(3:5)"# Sex and Race :  Female and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander
} else if(series== 169000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race %in% c(4:5)"# Sex and Race :  Female and Non-Hispanic Asian or Native Hawaiian or Other Pacific Islander
} else if(series== 170000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 1 & der_new_column_age_round %in% c(0:11)"# Sex and Race and Age :  Male and Hispanic and Under 12
} else if(series== 171000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 1 & der_new_column_age_round %in% c(0:11)"# Sex and Race and Age :  Male and Non-Hispanic White and Under 12
} else if(series== 172000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 2 & der_new_column_age_round %in% c(0:11)"# Sex and Race and Age :  Male and Non-Hispanic Black and Under 12
} else if(series== 173000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 3 & der_new_column_age_round %in% c(0:11)"# Sex and Race and Age :  Male and Non-Hispanic American Indian or Alaska Native and Under 12
} else if(series== 174000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 4 & der_new_column_age_round %in% c(0:11)"# Sex and Race and Age :  Male and Non-Hispanic Asian and Under 12
} else if(series== 175000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 5 & der_new_column_age_round %in% c(0:11)"# Sex and Race and Age :  Male and Non-Hispanic Native Hawaiian or Other Pacific Islander and Under 12
} else if(series== 176000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race %in% c(3:5) & der_new_column_age_round %in% c(0:11)"# Sex and Race and Age :  Male and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and Under 12
} else if(series== 177000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race %in% c(4:5) & der_new_column_age_round %in% c(0:11)"# Sex and Race and Age :  Male and Non-Hispanic Asian or Native Hawaiian or Other Pacific Islander and Under 12
} else if(series== 178000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 1 & der_new_column_age_round %in% c(0:11)"# Sex and Race and Age :  Female and Hispanic and Under 12
} else if(series== 179000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 1 & der_new_column_age_round %in% c(0:11)"# Sex and Race and Age :  Female and Non-Hispanic White and Under 12
} else if(series== 180000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 2 & der_new_column_age_round %in% c(0:11)"# Sex and Race and Age :  Female and Non-Hispanic Black and Under 12
} else if(series== 181000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 3 & der_new_column_age_round %in% c(0:11)"# Sex and Race and Age :  Female and Non-Hispanic American Indian or Alaska Native and Under 12
} else if(series== 182000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 4 & der_new_column_age_round %in% c(0:11)"# Sex and Race and Age :  Female and Non-Hispanic Asian and Under 12
} else if(series== 183000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 5 & der_new_column_age_round %in% c(0:11)"# Sex and Race and Age :  Female and Non-Hispanic Native Hawaiian or Other Pacific Islander and Under 12
} else if(series== 184000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race %in% c(3:5) & der_new_column_age_round %in% c(0:11)"# Sex and Race and Age :  Female and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and Under 12
} else if(series== 185000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race %in% c(4:5) & der_new_column_age_round %in% c(0:11)"# Sex and Race and Age :  Female and Non-Hispanic Asian or Native Hawaiian or Other Pacific Islander and Under 12
} else if(series== 186000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 1 & der_new_column_age_round %in% c(12:17)"# Sex and Race and Age :  Male and Hispanic and 12-17
} else if(series== 187000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 1 & der_new_column_age_round %in% c(12:17)"# Sex and Race and Age :  Male and Non-Hispanic White and 12-17
} else if(series== 188000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 2 & der_new_column_age_round %in% c(12:17)"# Sex and Race and Age :  Male and Non-Hispanic Black and 12-17
} else if(series== 189000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 3 & der_new_column_age_round %in% c(12:17)"# Sex and Race and Age :  Male and Non-Hispanic American Indian or Alaska Native and 12-17
} else if(series== 190000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 4 & der_new_column_age_round %in% c(12:17)"# Sex and Race and Age :  Male and Non-Hispanic Asian and 12-17
} else if(series== 191000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 5 & der_new_column_age_round %in% c(12:17)"# Sex and Race and Age :  Male and Non-Hispanic Native Hawaiian or Other Pacific Islander and 12-17
} else if(series== 192000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race %in% c(3:5) & der_new_column_age_round %in% c(12:17)"# Sex and Race and Age :  Male and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 12-17
} else if(series== 193000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race %in% c(4:5) & der_new_column_age_round %in% c(12:17)"# Sex and Race and Age :  Male and Non-Hispanic Asian or Native Hawaiian or Other Pacific Islander and 12-17
} else if(series== 194000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 1 & der_new_column_age_round %in% c(12:17)"# Sex and Race and Age :  Female and Hispanic and 12-17
} else if(series== 195000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 1 & der_new_column_age_round %in% c(12:17)"# Sex and Race and Age :  Female and Non-Hispanic White and 12-17
} else if(series== 196000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 2 & der_new_column_age_round %in% c(12:17)"# Sex and Race and Age :  Female and Non-Hispanic Black and 12-17
} else if(series== 197000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 3 & der_new_column_age_round %in% c(12:17)"# Sex and Race and Age :  Female and Non-Hispanic American Indian or Alaska Native and 12-17
} else if(series== 198000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 4 & der_new_column_age_round %in% c(12:17)"# Sex and Race and Age :  Female and Non-Hispanic Asian and 12-17
} else if(series== 199000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 5 & der_new_column_age_round %in% c(12:17)"# Sex and Race and Age :  Female and Non-Hispanic Native Hawaiian or Other Pacific Islander and 12-17
} else if(series== 200000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race %in% c(3:5) & der_new_column_age_round %in% c(12:17)"# Sex and Race and Age :  Female and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 12-17
} else if(series== 201000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race %in% c(4:5) & der_new_column_age_round %in% c(12:17)"# Sex and Race and Age :  Female and Non-Hispanic Asian or Native Hawaiian or Other Pacific Islander and 12-17
} else if(series== 202000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 1 & der_new_column_age_round >= 18"# Sex and Race and Age :  Male and Hispanic and 18+
} else if(series== 203000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 1 & der_new_column_age_round >= 18"# Sex and Race and Age :  Male and Non-Hispanic White and 18+
} else if(series== 204000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 2 & der_new_column_age_round >= 18"# Sex and Race and Age :  Male and Non-Hispanic Black and 18+
} else if(series== 205000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 3 & der_new_column_age_round >= 18"# Sex and Race and Age :  Male and Non-Hispanic American Indian or Alaska Native and 18+
} else if(series== 206000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 4 & der_new_column_age_round >= 18"# Sex and Race and Age :  Male and Non-Hispanic Asian and 18+
} else if(series== 207000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 5 & der_new_column_age_round >= 18"# Sex and Race and Age :  Male and Non-Hispanic Native Hawaiian or Other Pacific Islander and 18+
} else if(series== 208000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race %in% c(3:5) & der_new_column_age_round >= 18"# Sex and Race and Age :  Male and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 18+
} else if(series== 209000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race %in% c(4:5) & der_new_column_age_round >= 18"# Sex and Race and Age :  Male and Non-Hispanic Asian or Native Hawaiian or Other Pacific Islander and 18+
} else if(series== 210000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 1 & der_new_column_age_round >= 18"# Sex and Race and Age :  Female and Hispanic and 18+
} else if(series== 211000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 1 & der_new_column_age_round >= 18"# Sex and Race and Age :  Female and Non-Hispanic White and 18+
} else if(series== 212000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 2 & der_new_column_age_round >= 18"# Sex and Race and Age :  Female and Non-Hispanic Black and 18+
} else if(series== 213000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 3 & der_new_column_age_round >= 18"# Sex and Race and Age :  Female and Non-Hispanic American Indian or Alaska Native and 18+
} else if(series== 214000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 4 & der_new_column_age_round >= 18"# Sex and Race and Age :  Female and Non-Hispanic Asian and 18+
} else if(series== 215000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 5 & der_new_column_age_round >= 18"# Sex and Race and Age :  Female and Non-Hispanic Native Hawaiian or Other Pacific Islander and 18+
} else if(series== 216000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race %in% c(3:5) & der_new_column_age_round >= 18"# Sex and Race and Age :  Female and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 18+
} else if(series== 217000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race %in% c(4:5) & der_new_column_age_round >= 18"# Sex and Race and Age :  Female and Non-Hispanic Asian or Native Hawaiian or Other Pacific Islander and 18+
} else if(series== 218000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 1 & der_new_column_age_round %in% c(18:24)"# Sex and Race and Age :  Male and Hispanic and 18-24
} else if(series== 219000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 1 & der_new_column_age_round %in% c(25:34)"# Sex and Race and Age :  Male and Hispanic and 25-34
} else if(series== 220000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 1 & der_new_column_age_round %in% c(35:64)"# Sex and Race and Age :  Male and Hispanic and 35-64
} else if(series== 221000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 1 & der_new_column_age_round >= 65"# Sex and Race and Age :  Male and Hispanic and 65+
} else if(series== 222000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 1 & der_new_column_age_round %in% c(0:17)"# Sex and Race and Age :  Male and Hispanic and Under 18
} else if(series== 223000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 1 & der_new_column_age_round %in% c(18:24)"# Sex and Race and Age :  Male and Non-Hispanic White and 18-24
} else if(series== 224000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 1 & der_new_column_age_round %in% c(25:34)"# Sex and Race and Age :  Male and Non-Hispanic White and 25-34
} else if(series== 225000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 1 & der_new_column_age_round %in% c(35:64)"# Sex and Race and Age :  Male and Non-Hispanic White and 35-64
} else if(series== 226000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 1 & der_new_column_age_round >= 65"# Sex and Race and Age :  Male and Non-Hispanic White and 65+
} else if(series== 227000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 1 & der_new_column_age_round %in% c(0:17)"# Sex and Race and Age :  Male and Non-Hispanic White and Under 18
} else if(series== 228000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 2 & der_new_column_age_round %in% c(18:24)"# Sex and Race and Age :  Male and Non-Hispanic Black and 18-24
} else if(series== 229000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 2 & der_new_column_age_round %in% c(25:34)"# Sex and Race and Age :  Male and Non-Hispanic Black and 25-34
} else if(series== 230000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 2 & der_new_column_age_round %in% c(35:64)"# Sex and Race and Age :  Male and Non-Hispanic Black and 35-64
} else if(series== 231000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 2 & der_new_column_age_round >= 65"# Sex and Race and Age :  Male and Non-Hispanic Black and 65+
} else if(series== 232000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race == 2 & der_new_column_age_round %in% c(0:17)"# Sex and Race and Age :  Male and Non-Hispanic Black and Under 18
} else if(series== 233000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race %in% c(3:5) & der_new_column_age_round %in% c(18:24)"# Sex and Race and Age :  Male and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 18-24
} else if(series== 234000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race %in% c(3:5) & der_new_column_age_round %in% c(25:34)"# Sex and Race and Age :  Male and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 25-34
} else if(series== 235000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race %in% c(3:5) & der_new_column_age_round %in% c(35:64)"# Sex and Race and Age :  Male and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 35-64
} else if(series== 236000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race %in% c(3:5) & der_new_column_age_round >= 65"# Sex and Race and Age :  Male and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 65+
} else if(series== 237000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race %in% c(3:5) & der_new_column_age_round %in% c(0:17)"# Sex and Race and Age :  Male and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and Under 18
} else if(series== 238000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 1 & der_new_column_age_round %in% c(18:24)"# Sex and Race and Age :  Female and Hispanic and 18-24
} else if(series== 239000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 1 & der_new_column_age_round %in% c(25:34)"# Sex and Race and Age :  Female and Hispanic and 25-34
} else if(series== 240000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 1 & der_new_column_age_round %in% c(35:64)"# Sex and Race and Age :  Female and Hispanic and 35-64
} else if(series== 241000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 1 & der_new_column_age_round >= 65"# Sex and Race and Age :  Female and Hispanic and 65+
} else if(series== 242000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 1 & der_new_column_age_round %in% c(0:17)"# Sex and Race and Age :  Female and Hispanic and Under 18
} else if(series== 243000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 1 & der_new_column_age_round %in% c(18:24)"# Sex and Race and Age :  Female and Non-Hispanic White and 18-24
} else if(series== 244000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 1 & der_new_column_age_round %in% c(25:34)"# Sex and Race and Age :  Female and Non-Hispanic White and 25-34
} else if(series== 245000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 1 & der_new_column_age_round %in% c(35:64)"# Sex and Race and Age :  Female and Non-Hispanic White and 35-64
} else if(series== 246000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 1 & der_new_column_age_round >= 65"# Sex and Race and Age :  Female and Non-Hispanic White and 65+
} else if(series== 247000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 1 & der_new_column_age_round %in% c(0:17)"# Sex and Race and Age :  Female and Non-Hispanic White and Under 18
} else if(series== 248000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 2 & der_new_column_age_round %in% c(18:24)"# Sex and Race and Age :  Female and Non-Hispanic Black and 18-24
} else if(series== 249000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 2 & der_new_column_age_round %in% c(25:34)"# Sex and Race and Age :  Female and Non-Hispanic Black and 25-34
} else if(series== 250000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 2 & der_new_column_age_round %in% c(35:64)"# Sex and Race and Age :  Female and Non-Hispanic Black and 35-64
} else if(series== 251000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 2 & der_new_column_age_round >= 65"# Sex and Race and Age :  Female and Non-Hispanic Black and 65+
} else if(series== 252000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race == 2 & der_new_column_age_round %in% c(0:17)"# Sex and Race and Age :  Female and Non-Hispanic Black and Under 18
} else if(series== 253000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race %in% c(3:5) & der_new_column_age_round %in% c(18:24)"# Sex and Race and Age :  Female and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 18-24
} else if(series== 254000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race %in% c(3:5) & der_new_column_age_round %in% c(25:34)"# Sex and Race and Age :  Female and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 25-34
} else if(series== 255000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race %in% c(3:5) & der_new_column_age_round %in% c(35:64)"# Sex and Race and Age :  Female and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 35-64
} else if(series== 256000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race %in% c(3:5) & der_new_column_age_round >= 65"# Sex and Race and Age :  Female and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 65+
} else if(series== 257000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race %in% c(3:5) & der_new_column_age_round %in% c(0:17)"# Sex and Race and Age :  Female and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and Under 18
} else if(series== 258000 ){ 
  insubset <-"der_new_column_ethnicity == 2 & der_new_column_race %in% c(3,5)"# Race :  Non-Hispanic American Indian or Alaska Native and Native Hawaiian or Other Pacific Islander
} else if(series== 259000 ){ 
  insubset <-"der_new_column_gender == 1 & der_new_column_ethnicity == 2 & der_new_column_race %in% c(3,5)"# Sex and Race :  Male and Non-Hispanic American Indian or Alaska Native and Native Hawaiian or Other Pacific Islander
} else if(series== 260000 ){ 
  insubset <-"der_new_column_gender == 2 & der_new_column_ethnicity == 2 & der_new_column_race %in% c(3,5)"# Sex and Race :  Female and Non-Hispanic American Indian or Alaska Native and Native Hawaiian or Other Pacific Islander
} else {
  stop("This script expects a series number between 1000 and 260000", call.=FALSE)
}

intotalcolumn <- DER_MAXIMUM_COLUMN
incolumnstart <- as.integer((series/1000) * intotalcolumn)

#Create the additional columns
log_info(paste0("Calling createadditionalcolumns for table ",DER_TABLE_NAME," and series:",series," insubset:",insubset))
log_debug(system("free -mh", intern = FALSE))

temp <- createadditionalcolumns(
  intotalcolumn=intotalcolumn, 
  incolumnstart=incolumnstart, 
  colindex=colindex,
  insubset=insubset, 
  inperm_num_series=series
)
datai <- paste0("data_",DER_TABLE_NAME,"_",colindex + incolumnstart)
log_debug(paste0("Saving data item ",datai))
saveRDS(temp,file=paste0(in_file_path,"/",datai,".rds"))