#########################################################################
#Program      : 05_Populate_TableA_JD
#Description  : Generate Table A within Appendix for judicial-district-level
#
#Project      : NCS-X NIBRS Estimation Project
#Authors      : JD Bunker, Philip Lee, Taylor Lewis, Nicole Mack, Grant Swigart
#Date         :
#Modified     :
#Notes:
#########################################################################

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



#####################################################################
# Table A
# Columns: Estimate, SE(Estimate), RSE, Bias Ratio
# Rows: Offense Type
# Data: NIBRS, SRS
#####################################################################

#1.User inputs Data Files to be used

#NIBRS
#Update (05NOV2021): Adding guess_max argument
n_Univ_NIBRS_orig<-read_csv(paste0(output_weighting_data_folder,'weights_jd_cal_srs_altcombs_col.csv'),
                            guess_max=1e6)

NumStates<-n_Univ_NIBRS_orig %>% subset(!is.na(JDWgt)) %>% pull(JUDICIAL_DISTRICT_NAME) %>% unique() %>% length()

#SRS
#Update (27OCT2021): Use variables on SF instead of recreating based on cleanframe + srs2016_2020_smoothed
#Update (05NOV2021): Adding guess_max argument
SF <- read_csv(paste0(output_weighting_data_folder,"SF_postJD_cal_srs_altcombs_col.csv"),
               guess_max=1e6) %>%
  subset(!is.na(JUDICIAL_DISTRICT_NAME))


ucr_SRS_orig <- SF %>%
  select(ORI_universe,county,JUDICIAL_DISTRICT_NAME,matches("totcrime.*_imp"))
#Rename category totals to match annual SRS
colnames(ucr_SRS_orig) <- colnames(ucr_SRS_orig) %>%
  str_remove(pattern="(?<=tot)crime(?=_\\w+_imp)")



#UCR
#ucr_Arrest_orig <- "//rtpnfil02/0216153_NIBRS/03_SamplingPlan/01_Auxiliary_Data_Processing/2020/Arrest/output/UCR_Arrest_summary_2020.csv" %>%
#  read.csv()

#ucr_Arrest_orig<-ucr_Arrest_orig%>%rename(ORI_universe=ORI_UNIVERSE)
#ucr_Arrest_orig$inUCR<-1
#names(ucr_Arrest_orig)


#Stratum Totals
#Update (05NOV2021): Adding guess_max argument
SF_tots<-read_csv(paste0(output_weighting_data_folder,"SF_postJD_cal_srs_altcombs_col.csv"),
                  col_types = cols_only("wgtGpJD"=col_integer(),
                                        "county"=col_character(),
                                        "JUDICIAL_DISTRICT_NAME"=col_character(),
                                        "ORI_universe"=col_character(),
                                        "PARENT_POP_GROUP_DESC"=col_character(),
                                        "AGENCY_TYPE_NAME"=col_character(),
                                        "REGION_NAME"=col_character()),
                  guess_max=1e6) %>%
  unique() %>%
  mutate(PARENT_POP_GROUP_DESC2=case_when(PARENT_POP_GROUP_DESC %in% c("Cities under 2,500","Cities from 2,500 thru 9,999") ~ "Cities under 10,000",
                                               TRUE ~ PARENT_POP_GROUP_DESC))
# SF_tots$PARENT_POP_GROUP_DESC2
#
#
# SF_tots %>%
#   group_by(PARENT_POP_GROUP_DESC) %>%
#   summarize(n=n())
# SF_tots %>%
#   group_by(AGENCY_TYPE_NAME) %>%
#   summarize(n=n())
# SF_tots %>%
#   group_by(REGION_NAME) %>%
#   summarize(n=n())


SF_tots_all<-SF_tots %>%
  group_by(wgtGpJD) %>%
  summarise(Nh=n())


SF_tots_state_<-SF_tots %>%
  group_by(wgtGpJD,JUDICIAL_DISTRICT_NAME) %>%
  summarise(Nh=n())

SF_tots_state<-as.data.frame(SF_tots_state_) %>%
  mutate(wgtGpJD_new = row_number())


SF_tots_all_fin<-inner_join(SF_tots_all,SF_tots,by=c("wgtGpJD"))

SF_tots_all_state_fin_<-inner_join(SF_tots_state,SF_tots,by=c("wgtGpJD","JUDICIAL_DISTRICT_NAME"))
SF_tots_all_state_fin_<-SF_tots_all_state_fin_ %>%
  rename(wgtGpJD_old=wgtGpJD)


SF_tots_all_state_fin<-SF_tots_all_state_fin_%>%rename(wgtGpJD=wgtGpJD_new)


#####################################################################
# Combine applicable data
#####################################################################
#Table A
#ucr_SRS <- ucr_SRS_orig %>%
#  inner_join(SF_tots[,c("ORI_universe","wgtGpJD","Nh")],by=c("ORI_universe")) %>%
#  inner_join(select(n_Univ_NIBRS_orig,"ORI_universe",matches("calwt")),by=c("ORI_universe")) %>%
#   mutate(one=1,state_abbr=substr(ucr_SRS_orig$ori,1,2))

n_Univ_NIBRS_orig$inNIBRS<-1
ucr_SRS_orig$inUCR<-1
SF_tots$inSFtots<-1


n_Univ_NIBRS_orig$inNIBRS<-1
ucr_SRS_orig$inUCR<-1
SF_tots$inSFtots<-1
SF_tots_all_fin$inSFtots<-1
SF_tots_all_state_fin$inSFtots<-1



#names(ucr_SRS_orig)

#Not needed when using smoothed SRS
#ucr_SRS_orig<-ucr_SRS_orig%>%rename(ORI_universe=ORI_UNIVERSE)
ucr_SRS <- ucr_SRS_orig %>%
  unique() %>%
  inner_join(SF_tots_all_state_fin[,c("ORI_universe","county","JUDICIAL_DISTRICT_NAME","wgtGpJD","Nh")],by=c("ORI_universe","county","JUDICIAL_DISTRICT_NAME")) %>%
  left_join(SF_tots[,c("ORI_universe","county","JUDICIAL_DISTRICT_NAME","PARENT_POP_GROUP_DESC2")],by=c("ORI_universe","county","JUDICIAL_DISTRICT_NAME")) %>%
  inner_join(select(n_Univ_NIBRS_orig,"ORI_universe",county,JDWgt,JUDICIAL_DISTRICT_NAME),
             by=c("ORI_universe","county","JUDICIAL_DISTRICT_NAME")) %>%
  mutate(one=1)

#Update (09JUL2021): Switch from ori to ORI_universe, as ori doesn't exist on SF / smoothed SRS
#ucr_SRS$state_abbr<-substr(ucr_SRS$ori,1,2)
#ucr_SRS$state_abbr<-substr(ucr_SRS$ORI_universe,1,2) %>%
#  #Update (27AUG2021): Convert Nebraska from NB to NE in line with shell
#  str_replace(pattern="^NB$","NE")
ucr_SRS<-ucr_SRS%>%rename(totcrime_imp_orig=totcrime_imp)
ucr_SRS$totcrime_imp<-ucr_SRS$tot_violent_imp+ucr_SRS$tot_property_imp

ucr_SRS <- data.frame(ucr_SRS)





#####################################################################
# Input List of Weights and Load Functions to process data
#####################################################################
weight_state_lists<-(colnames(n_Univ_NIBRS_orig) %>%str_subset("JDWgt") %>%as.list()) #List of weights, update as necessary


weight_state_lists_n<-list("JDWgt")



weight_state_lists_n_df<-data.frame(matrix(unlist(weight_state_lists_n), 
                                           nrow=length(weight_state_lists_n), byrow=T))
names(weight_state_lists_n_df) <- c("weightVar")
weight_state_lists_n_df<-weight_state_lists_n_df %>% mutate(RowValue = row_number())



#File storing syntax for all functions used
source("Appendix_Tables_All_Functions.R",echo=TRUE)
jdall <- SF %>% select(JUDICIAL_DISTRICT_NAME) %>% unique() %>% arrange(JUDICIAL_DISTRICT_NAME)
rel <- data.frame(state_name=jdall$JUDICIAL_DISTRICT_NAME) %>%
  mutate(nid=1:nrow(.))

state_name_abb <- rel

#Change dummy as necessary
#TableADummy.csv
#TableADummypt2v2.csv

outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")

output_folder <- sprintf("%s", outputPipelineDir)

dummyDatA<-
  read.csv(file.path(output_weighting_tableshell_folder,"TableAJDDummy.csv"))%>%
  #Update (08SEP2021): Remove subset of nid==1
  #filter(nid!=1)%>%
  mutate(CrimeOrder = RowValue-2)

dummyDatA<-dummyDatA[c("state_name","CrimeOrder")]
dummyDatA$state_name<-as.character(dummyDatA$state_name)
#dummyDatA$state_abbr<-as.character(dummyDatA$state_abbr)


#####################################################################
# Table A
#####################################################################

options(survey.lonely.psu = "adjust")
####################Table A states#################################
compute_jdTotals_TabA <- function(wtvar,indata,indicator){
  respWgts <- indata %>%
    rename(wt=all_of(wtvar)) %>%
    subset(!is.na(totcrime_imp)) %>%
    subset(!is.na(wt)) %>% #Switch to indicator?
    svydesign(ids= ~1,data=.,strata=.$wgtGpJD,weights=.$wt,fpc=.$Nh)
  
  df<-data.frame(genAppA_jd(respWgts))
  
  state_tot<-gather(data=df,key,value,starts_with("tot"),-JUDICIAL_DISTRICT_NAME)%>%mutate(RowValue = as.numeric(row_number()))%>% select(-contains("se."))
  state_setot<-gather(data=df,key,value,starts_with("se"),-JUDICIAL_DISTRICT_NAME)%>%mutate(RowValue = as.numeric(row_number()))%>% select(-contains("tot"))
  
  
  state_all0<-merge(state_tot,state_setot,by=c("JUDICIAL_DISTRICT_NAME","RowValue"))%>%rename(Total=value.x)%>%rename(SE=value.y)%>% mutate(state_name=JUDICIAL_DISTRICT_NAME)
  
  
  state_all1<-state_all0 %>%mutate(CrimeOrder=case_when(
    key.x == "totcrime_imp"  ~ 0,
    key.x == "tot_violent_imp"~1,
    key.x == "tot_murder_imp"  ~ 2,
    key.x == "tot_manslaughter_imp"  ~ 3,
    key.x == "tot_rape_imp" ~ 4,
    key.x == "tot_rob_imp"  ~ 5,
    key.x == "tot_assault_imp"  ~ 6,
    key.x == "tot_aggAssault_imp"  ~ 7,
    key.x == "tot_simpAssault_imp" ~ 8,
    key.x == "tot_property_imp" ~ 9,
    key.x == "tot_burglary_imp" ~ 10,
    key.x == "tot_larceny_imp" ~ 11,
    key.x == "tot_vhcTheft_imp" ~ 12))
  
  state_all2<-merge(state_all1,state_name_abb,by=c("state_name"))
  state_all<-left_join(dummyDatA,state_all2,by=c("state_name","CrimeOrder"))
  
  state_all <- state_all[with(state_all,order(state_name,CrimeOrder)),]
  
  return(list(data.frame(state_all)))
}

#Generate UCR overall
jdEstimates_TabA_SRS <-(
  compute_jdTotals_TabA(wtvar="one",indata=ucr_SRS,indicator="inNIBRS") %>%
    .[[1]])


#Get the data frame in the list
#Note: SEs are much lower in above vs Grant's file bc we use fpc here

#Generate estimates for NIBRS Reporters
#compute_stateTotals_TabA(wtvar=weight_state_lists[[1]],indata=ucr_SRS,indicator="inNIBRS")

jdEstimates_TabA_nibrsReps <- (
  sapply(weight_state_lists,compute_jdTotals_TabA,indata=ucr_SRS,indicator="inNIBRS"))


######
#Merge estimates for SRS + NIBRS reporters
list_of_tablesA_jds <- (
  sapply(1:length(jdEstimates_TabA_nibrsReps),
         function(subTab){
           inner_join(x=jdEstimates_TabA_nibrsReps[[subTab]],
                      y=jdEstimates_TabA_SRS,
                      by=c("state_name","CrimeOrder"),
                      suffix=c(".Reps",".SRS")) %>%
             mutate(RSE.Reps=ifelse(Total.Reps!=0,round(SE.Reps/Total.Reps*100,2),"-"),
                    BR.Repsn=ifelse(Total.SRS!=0,round((Total.Reps-Total.SRS)/Total.SRS*100,2),9999),
                    BR.Reps=ifelse(BR.Repsn!=9999,BR.Repsn,"NC"),
                    Total.SRS=format(round(Total.SRS,0),nsmall=0,big.mark=","),
                    SE.SRS=format(round(SE.SRS,0),nsmall=0,big.mark=","),
                    Total.Reps=format(round(Total.Reps,0),nsmall=0,big.mark=","),
                    SE.Reps=format(round(SE.Reps,0),nsmall=0,big.mark=","),
                    BRGT5=ifelse(abs(BR.Repsn)>5 & BR.Repsn!=9999 ,"*","")
             ) %>%
             list()
         })
)

names(list_of_tablesA_jds) <- weight_state_lists

##For summary of Relative Bias Table###
summary_tableA_jds<-list_of_tablesA_jds %>% bind_rows(.id="weightVar") %>%
  rename(RowValue=RowValue.Reps,
         Total=Total.Reps,
         SE=SE.Reps) %>%
  mutate(RowValue2=RowValue %% NumStates) %>% #Make it so 1 RowValue2 per state
  mutate(RowValue2=ifelse(RowValue2==0,NumStates,RowValue2)) %>% #Set last state to 51 (originally=0)
  reshape2::melt(id.vars=c("weightVar","RowValue2","state_name","CrimeOrder"),measure.vars=c("BR.Repsn")) %>%
  reshape2::dcast(formula=state_name+RowValue2+weightVar~paste0(variable,CrimeOrder)) %>%
  {merge(state_name_abb[c("state_name","nid")],.,by=c("state_name"))} %>%
  arrange(nid,weightVar)

summary_tableA_jdspt1<-summary_tableA_jds


####################Table A national#################################
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




summary_tableA <- bind_rows(#summary_tableA_natl,
  summary_tableA_jds) %>%
  select(-matches("RowValue"))


#####################################################################
# Output Tables
#####################################################################

#Reorder to match shell
#Blank out rows as appropriate, i.e. if Violent Crime blank ("--") out
#weights calibrated to property crimes
summary_tableA<-left_join(summary_tableA,bind_rows(#weight_natl_lists_n_df,
  weight_state_lists_n_df),by=c("weightVar"))



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

str1 <- file.path(output_weighting_populated_folder,'TableA_JD_Populated_SRS_AltCombs_Collapsed')

#str1 <- '//rtpnfil02/0216153_NIBRS/03_SamplingPlan/SubTask3_new_Weighting_Validation_Results/2020/TableA_Statept2'
#paste0(str1, format(Sys.time(),'_%Y%m%d'), '.xlsx')

filein <- file.path(output_weighting_tableshell_folder,"TableA_JD_Shell.xlsx")



# Load the existing workbook
wbTabAJD <- loadWorkbook(file =filein )


# Write data to specific range in Excel, specified by start column and start row
#Moving startRow down by 1 because we're ignoring national
writeData(wbTabAJD, sheet = "Summary_JD_TabA_Ex1", x = summary_tableAKeep, startCol = 3, startRow = 8, colNames = FALSE,keepNA=FALSE)

saveWorkbook(wbTabAJD, file=paste0(str1, format(Sys.time(),'_%Y%m%d'), '.xlsx'), overwrite = TRUE)


#################
#Weights Sheets
################

#TypeTab; 9999 code if includes judicial-district-level table, 8888 code for overall table
#stZ: Startinf sheet number minus 1, i.e. if tab is 2nd sheet, stZ=1
#crime_type - Values of P or V to indicate if property or violent crime and suppress as applicable values


weight_lists <- weight_state_lists
write_files_xlsx(listfile_name = list_of_tablesA_jds,
                 infile_name=paste0(str1, format(Sys.time(),'_%Y%m%d'), '.xlsx'),
                 file_name=paste0(str1, format(Sys.time(),'_%Y%m%d'), '.xlsx'),
                 keepCols=keepColsTabA,
                 blankOut=include_dashTabA,
                 crime_type=crime_type_indTabA,
                 stZ=1, #If starting sheet is first, value should be "0", otherwise number after
                 inCol=3,
                 inRow=8,
                 typeTab=9999)
