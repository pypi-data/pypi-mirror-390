#########################################################################
#Program      : 05_Populate_TableA_University
#Description  : Generate Table A within Appendix for university LEAs
#
#Project      : NCS-X NIBRS Estimation Project
#Authors      : JD Bunker, Philip Lee, Taylor Lewis, Nicole Mack, Grant Swigart
#Date         :
#Modified     :
#Notes:
#########################################################################
#Update (26AUG2021): Replaced all instances of 'stratum_f' with 'wgtGpNational'
#Update (02FEB2022): Replaced all instances of 'wgtGpNational' with 'one'
#Update (08FEB2022): Looks like 'one' was already being used - change old instances of 'wgtGpNational' to 'dummy'
#################################################################################
#Load packages
#NOTE: when loading Source files some packages may overwrite functions in others
#      Check if that is the case
library(tidyverse)
library(dplyr)
library(survey)
library(Hmisc)
library(openxlsx)
library(foreign)
library(srvyr)
library(haven)
library(rlang)
library(reshape2)
#################################################################################


log_info("Running 05_Populate_TableA_University.R")
#####################################################################
# Table A
# Columns: Estimate, SE(Estimate), RSE, Bias Ratio
# Rows: Offense Type
# Data: NIBRS, SRS
#####################################################################

#1.User inputs Data Files to be used

#NIBRS
#Update (05NOV2021): Adding guess_max argument
n_Univ_NIBRS_orig<-read_csv_logging(paste0(output_weighting_data_folder,'weights_university.csv'),
                            guess_max=1e6)

NumStates<-(dim(distinct(subset(n_Univ_NIBRS_orig,!is.na(UniversityWgt)) %>%  mutate(state_abbr=substr(ORI_universe,1,2)),state_abbr,.keep_all = TRUE))[1])


#SRS
#Update (27OCT2021): Use variables on SF instead of recreating based on cleanframe + srs2016_2020_smoothed
#Update (05NOV2021): Adding guess_max argument
SF <- read_csv_logging(paste0(output_weighting_data_folder,"SF_postSP.csv"),
               guess_max=1e6)


ucr_SRS_orig <- SF %>%
  select(ORI_universe,matches("totcrime.*_imp"))
#Rename category totals to match annual SRS
colnames(ucr_SRS_orig) <- colnames(ucr_SRS_orig) %>%
  str_remove(pattern="(?<=tot)crime(?=_\\w+_imp)")



#Stratum Totals
#Update (05NOV2021): Adding guess_max argument
#Update (08FEB2022): Subset to universities
SF_tots<-read_csv_logging(paste0(output_weighting_data_folder,"SF_postSP.csv"),
                  col_types = cols_only(#"wgtGpNational"=col_integer(),
                                        "STATE_ABBR"=col_character(),
                                        "ORI_universe"=col_character(),
                                        "PARENT_POP_GROUP_DESC"=col_character(),
                                        "AGENCY_TYPE_NAME"=col_character(),
                                        "REGION_NAME"=col_character()),
                  guess_max=1e6) %>%
  subset(AGENCY_TYPE_NAME=="University or College") %>%
  mutate(dummy=1) %>%
  mutate(PARENT_POP_GROUP_DESC2=case_when(PARENT_POP_GROUP_DESC %in% c("Cities under 2,500","Cities from 2,500 thru 9,999") ~ "Cities under 10,000",
                                          TRUE ~ PARENT_POP_GROUP_DESC))



SF_tots_all<-SF_tots %>%
  #group_by(wgtGpNational) %>%
  group_by(dummy) %>%
  summarise(Nh=n())

#Update (08FEB2022): Comment out old code pertaining to state
SF_tots_state_<-SF_tots %>%
  group_by(dummy,#wgtGpNational,
    STATE_ABBR) %>%
  summarise(Nh=n())
SF_tots_state<-as.data.frame(SF_tots_state_) %>%
 # mutate(wgtGpNational_new = row_number())
  mutate(dummy_new=row_number())


SF_tots_all_fin<-inner_join(SF_tots_all,SF_tots,by=c("dummy"))#"wgtGpNational"))

SF_tots_all_state_fin_<-inner_join(SF_tots_state,SF_tots,by=c("dummy",#"wgtGpNational",
                                                              "STATE_ABBR"))
SF_tots_all_state_fin_<-SF_tots_all_state_fin_ %>%
  #rename(wgtGpNational_old=wgtGpNational)
  rename(dummy_old=dummy)
 
 
 SF_tots_all_state_fin<-SF_tots_all_state_fin_%>%rename(dummy=dummy_new)#rename(wgtGpNational=wgtGpNational_new)
# SF_tots_all_fin<-inner_join(SF_tots_all,SF_tots,by=c("dummy"))
# SF_tots_all_state_fin <- SF_tots_all_fin

#####################################################################
# Combine applicable data
#####################################################################
#Table A

n_Univ_NIBRS_orig$inNIBRS<-1
ucr_SRS_orig$inUCR<-1
SF_tots$inSFtots<-1


n_Univ_NIBRS_orig$inNIBRS<-1
ucr_SRS_orig$inUCR<-1
SF_tots$inSFtots<-1
SF_tots_all_fin$inSFtots<-1
SF_tots_all_state_fin$inSFtots<-1



ucr_SRS <- ucr_SRS_orig %>%
  inner_join(SF_tots_all_state_fin[,c("ORI_universe","dummy",#"wgtGpNational",
                                      "Nh")],by=c("ORI_universe")) %>%
  inner_join(select(n_Univ_NIBRS_orig,"ORI_universe",UniversityWgt),by=c("ORI_universe")) %>%
  mutate(one=1)

#Update (09JUL2021): Switch from ori to ORI_universe, as ori doesn't exist on SF / smoothed SRS
#ucr_SRS$state_abbr<-substr(ucr_SRS$ori,1,2)
ucr_SRS$state_abbr<-substr(ucr_SRS$ORI_universe,1,2)
ucr_SRS<-ucr_SRS%>%rename(totcrime_imp_orig=totcrime_imp)
ucr_SRS$totcrime_imp<-ucr_SRS$tot_violent_imp+ucr_SRS$tot_property_imp





#####################################################################
# Input List of Weights and Load Functions to process data
#####################################################################
weight_natl_lists_n<-(colnames(n_Univ_NIBRS_orig) %>%str_subset("UniversityWgt") %>%as.list()) #List of weights, update as necessary



weight_natl_lists_n_df<-data.frame(matrix(unlist(weight_natl_lists_n), nrow=length(weight_natl_lists_n), byrow=T))
names(weight_natl_lists_n_df) <- c("weightVar")
weight_natl_lists_n_df<-weight_natl_lists_n_df %>% mutate(RowValue = row_number())



#File storing syntax for all functions used
log_debug("Running file Appendix_Tables_All_Functions.R")
source("Appendix_Tables_All_Functions.R")


outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")

output_folder <- sprintf("%s", outputPipelineDir)

dummyDatA<-
  read_dot_csv_logging(file.path(output_weighting_tableshell_folder,"TableAUniversityDummy.csv"))%>%
  filter(nid!=1)%>%mutate(CrimeOrder = RowValue-2)
dummyDatA<-dummyDatA[c("state_name","CrimeOrder","state_abbr")]
dummyDatA$state_name<-as.character(dummyDatA$state_name)
dummyDatA$state_abbr<-as.character(dummyDatA$state_abbr)


#####################################################################
# Table A
#####################################################################

options(survey.lonely.psu = "adjust")

####################Table A university#################################
rowNames_TabA=c(
  "M-(0) All Crime",
  "M-(1) All Murder",
  "M-(2) Murder and non-negligent manslaughter",
  "M-(3) Manslaughter by negligence",
  "M-(4) Forcible rape",
  "M-(5) Robbery",
  "M-(6) Assault",
  "M-(6a) Aggravated assault",
  "M-(6b) Simple assault",
  "P-(7) All Property",
  "P-(8) Burglary-breaking or entering",
  "P-(9) Larceny-theft (not motor vehicle)",
  "P-(10) Motor vehicle theft")

compute_natlTotals_TabA<- function(wtvar,indata,indicator){
  log_debug("Running function compute_natlTotals_TabA")
  respWgts <- indata %>%
    rename(wt=all_of(wtvar)) %>%
    subset(!is.na(totcrime_imp)) %>%
    subset(!is.na(wt)) %>% #Switch to indicator?
    svydesign(ids= ~1,data=.,strata=.$dummy,#strata=.$wgtGpNational,
              weights=.$wt,fpc=.$Nh)
  return(list(data.frame(genAppA(respWgts),
                         rowName=rowNames_TabA)))
}
#Generate UCR overall
natlEstimates_TabA_SRS <-(
  compute_natlTotals_TabA(wtvar="one",indata=ucr_SRS,indicator="inNIBRS") %>%
    .[[1]]) #Get the data frame in the list
#Note: SEs are much lower in above vs Grant's file bc we use fpc here

#Generate estimates for NIBRS Reporters
#compute_natlTotals_TabA(wtvar=weight_lists_n[[1]],indata=ucr_SRS,indicator="inNIBRS")

natlEstimates_TabA_nibrsReps <- (
  sapply(weight_natl_lists_n,compute_natlTotals_TabA,indata=ucr_SRS,indicator="inNIBRS"))
#names(ucr_SRS)

######
#Merge estimates for SRS + NIBRS reporters
list_of_tablesA_natl <- (
  sapply(1:length(natlEstimates_TabA_nibrsReps),
         function(subTab){
		 print(subTab)
           inner_join(x=natlEstimates_TabA_nibrsReps[[subTab]] %>%
                        mutate(rowVar=rownames(.)),
                      y=natlEstimates_TabA_SRS,
                      by="rowName",
                      suffix=c(".Reps",".SRS")) %>%
             rename(Total.SRS=total.SRS,
                    Total.Reps=total.Reps) %>%
             mutate(RSE.Reps=round(SE.Reps/Total.Reps*100,2),
                    BR.Repsn=ifelse(Total.SRS!=0,round((Total.Reps-Total.SRS)/Total.SRS*100,2),9999),
                    BR.Reps=ifelse(BR.Repsn!=9999,BR.Repsn,"NC"),
                    Total.SRS=format(round(Total.SRS,0),nsmall=0,big.mark=","),
                    SE.SRS=format(round(SE.SRS,0),nsmall=0,big.mark=","),
                    Total.Reps=format(round(Total.Reps,0),nsmall=0,big.mark=","),
                    SE.Reps=format(round(SE.Reps,0),nsmall=0,big.mark=","),
					BRGT5=ifelse(!is.na(as.numeric(BR.Reps)),
					             ifelse(abs(as.numeric(BR.Reps))>5,"*",""),
								 "")) %>%
             list()
         })
)

names(list_of_tablesA_natl) <- weight_natl_lists_n



summary_tableA_natl <-list_of_tablesA_natl %>% bind_rows(.id="weightVar") %>%
  mutate(RowValue=0) %>%
  rename(Total=Total.Reps,
         SE=SE.Reps) %>%
  mutate(state_abbr="US",
         CrimeOrder=case_when(
           rowVar == "totcrime_imp"  ~ 0,
           rowVar == "tot_violent_imp"~1,
           rowVar == "tot_murder_imp"  ~ 2,
           rowVar == "tot_manslaughter_imp"  ~ 3,
           rowVar == "tot_rape_imp" ~ 4,
           rowVar == "tot_rob_imp"  ~ 5,
           rowVar == "tot_assault_imp"  ~ 6,
           rowVar == "tot_aggAssault_imp"  ~ 7,
           rowVar == "tot_simpAssault_imp" ~ 8,
           rowVar == "tot_property_imp" ~ 9,
           rowVar == "tot_burglary_imp" ~ 10,
           rowVar == "tot_larceny_imp" ~ 11,
           rowVar == "tot_vhcTheft_imp" ~ 12)) %>%
  reshape2::melt(id.vars=c("weightVar","RowValue","state_abbr","CrimeOrder"),measure.vars=c("BR.Repsn")) %>%
  reshape2::dcast(formula=state_abbr+RowValue+weightVar~paste0(variable,CrimeOrder)) %>%
  mutate(nid=0) %>%
  arrange(nid,weightVar)

####################Table A combined#################################

summary_tableA <- bind_rows(summary_tableA_natl) %>%#,summary_tableA_states) %>%
  select(-matches("RowValue"))


#####################################################################
# Output Tables
#####################################################################

#Reorder to match shell
#Blank out rows as appropriate, i.e. if Violent Crime blank ("--") out
#weights calibrated to property crimes
summary_tableA<-left_join(summary_tableA,bind_rows(weight_natl_lists_n_df),#,weight_state_lists_n_df),
                          by=c("weightVar"))



#####################################################################
# Table A
# Columns: Estimate, SE(Estimate), RSE, Bias Ratio
# Rows: Offense Type
# Data: NIBRS, SRS
#####################################################################

#Blank out appropriate rows per weight
summary_tableA_blankOut<-summary_tableA%>%
  mutate(BR.Repsn1=ifelse(str_detect(weightVar,"_prop")==1,"--",BR.Repsn1),
         BR.Repsn2=ifelse(str_detect(weightVar,"_prop")==1,"--",BR.Repsn2),
         BR.Repsn3=ifelse(str_detect(weightVar,"_prop")==1,"--",BR.Repsn3),
         BR.Repsn4=ifelse(str_detect(weightVar,"_prop")==1,"--",BR.Repsn4),
         BR.Repsn6=ifelse(str_detect(weightVar,"_prop")==1,"--",BR.Repsn6),
         BR.Repsn7=ifelse(str_detect(weightVar,"_prop")==1,"--",BR.Repsn7),
         BR.Repsn8=ifelse(str_detect(weightVar,"_prop")==1,"--",BR.Repsn8),
         
         BR.Repsn9=ifelse(str_detect(weightVar,"_viol")==1,"--",BR.Repsn9),
         BR.Repsn10=ifelse(str_detect(weightVar,"_viol")==1,"--",BR.Repsn10),
         BR.Repsn11=ifelse(str_detect(weightVar,"_viol")==1,"--",BR.Repsn11),
         BR.Repsn12=ifelse(str_detect(weightVar,"_viol")==1,"--",BR.Repsn12),
  )

summary_tableA_blankOut<- summary_tableA_blankOut[order(summary_tableA_blankOut$nid,summary_tableA_blankOut$RowValue),]




#names(list_of_tablesA) <- weight_lists #excel sheet names
crime_type_indTabA=matrix(c("N", rep("V",8), rep("P",4)),nrow=663) #Crime types -V=Violent, P=Property
keepColsTabA<-c("Total.Reps", "SE.Reps", "RSE.Reps", "Total.SRS","BR.Reps","BRGT5")
include_dashTabA<-matrix(rep("---", times =6),nrow=1)
summary_tableAKeep<-summary_tableA_blankOut[c("BR.Repsn0","BR.Repsn1","BR.Repsn2",
                                              "BR.Repsn3","BR.Repsn4","BR.Repsn5",
                                              "BR.Repsn6","BR.Repsn7","BR.Repsn8",
                                              "BR.Repsn9","BR.Repsn10","BR.Repsn11",
                                              "BR.Repsn12")]



#################
#Summary Sheet
################

str1 <- file.path(output_weighting_populated_folder,'TableA_University_Populated')

filein <- file.path(output_weighting_tableshell_folder,"TableA_University_Shell.xlsx")


# Load the existing workbook
wbTabAUniversity <- loadWorkbook(file =filein )

log_debug("Writing sheet Summary_University_TabA_Ex1")
# Write data to specific range in Excel, specified by start column and start row
writeData(wbTabAUniversity, sheet = "Summary_University_TabA_Ex1", x = summary_tableAKeep, startCol = 3, startRow = 8, colNames = FALSE,keepNA=FALSE)

saveWorkbook(wbTabAUniversity, file=paste0(str1, format(Sys.time(),'_%Y%m%d'), '.xlsx'), overwrite = TRUE)


#################
#Weights Sheets
################

#TypeTab; 9999 code if includes state-level table, 8888 code for overall table
#stZ: Startinf sheet number minus 1, i.e. if tab is 2nd sheet, stZ=1
#crime_type - Values of P or V to indicate if property or violent crime and suppress as applicable values


weight_lists <- weight_natl_lists_n
write_files_xlsx(listfile_name = list_of_tablesA_natl,
                 infile_name=paste0(str1, format(Sys.time(),'_%Y%m%d'), '.xlsx'),
                 file_name= paste0(str1, format(Sys.time(),'_%Y%m%d'), '.xlsx'),
                 keepCols=keepColsTabA,
                 blankOut=include_dashTabA,
                 crime_type=crime_type_indTabA,
                 stZ=1, #If starting sheet is first, value should be "0", otherwise number after
                 inCol=3,
                 inRow=8,
                 typeTab=9999)
log_info("Finished 05_Populate_TableA_University.R\n\n")