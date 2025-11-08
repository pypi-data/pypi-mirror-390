#########################################################################
#Program      : 05_Populate_TableA_Groupings_Region
#Description  : Generate Table A within Appendix for region-level by grouping
#
#Project      : NCS-X NIBRS Estimation Project
#Authors      : JD Bunker, Philip Lee, Taylor Lewis, Nicole Mack, Grant Swigart
#Date         :
#Modified     :
#Notes:
#########################################################################
#Update (26AUG2021): Replaced all instances of 'stratum_f' with 'wgtGpRegion'

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


log_info("Running 05_Populate_TableA_Groupings_Region.R")
#####################################################################
# Table A
# Columns: Estimate, SE(Estimate), RSE, Bias Ratio
# Rows: Offense Type
# Data: NIBRS, SRS
#####################################################################

#1.User inputs Data Files to be used

#NIBRS
#Update (05NOV2021): Adding guess_max argument
n_Univ_NIBRS_orig<-read_csv_logging(paste0(output_weighting_data_folder,'weights_region.csv'),
                            guess_max=1e6)
#n_Univ_NIBRS_orig$RegionWgt<-n_Univ_NIBRS_orig$calwt_m3_2

NumRegions<-subset(n_Univ_NIBRS_orig,!is.na(RegionWgt)) %>%
  .$REGION_NAME %>%
  unique() %>%
  length()

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
SF_tots<-read_csv_logging(paste0(output_weighting_data_folder,"SF_postSP.csv"),
                  col_types = cols_only("wgtGpRegion"=col_integer(),
                                        "STATE_ABBR"=col_character(),
                                        "ORI_universe"=col_character(),
                                        "PARENT_POP_GROUP_DESC"=col_character(),
                                        "AGENCY_TYPE_NAME"=col_character(),
                                        "REGION_NAME"=col_character()),
                  guess_max=1e6) %>%
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

#Updating from using STATE_NAME to REGION_NAME
SF_tots_all<-SF_tots %>%
  group_by(wgtGpRegion) %>%
  summarise(Nh=n())


SF_tots_region_<-SF_tots %>%
  group_by(wgtGpRegion,REGION_NAME) %>%
  summarise(Nh=n())

SF_tots_region<-as.data.frame(SF_tots_region_) %>%
  mutate(wgtGpRegion_new = row_number())


SF_tots_all_fin<-inner_join(SF_tots_all,SF_tots,by=c("wgtGpRegion"))

SF_tots_all_region_fin_<-inner_join(SF_tots_region,SF_tots,by=c("wgtGpRegion","REGION_NAME"))
SF_tots_all_region_fin_<-SF_tots_all_region_fin_ %>%
  rename(wgtGpRegion_old=wgtGpRegion)


SF_tots_all_region_fin<-SF_tots_all_region_fin_%>%rename(wgtGpRegion=wgtGpRegion_new)


#####################################################################
# Combine applicable data
#####################################################################
#Table A
#ucr_SRS <- ucr_SRS_orig %>%
#  inner_join(SF_tots[,c("ORI_universe","wgtGpRegion","Nh")],by=c("ORI_universe")) %>%
#  inner_join(select(n_Univ_NIBRS_orig,"ORI_universe",matches("calwt")),by=c("ORI_universe")) %>%
#   mutate(one=1,state_abbr=substr(ucr_SRS_orig$ori,1,2))

n_Univ_NIBRS_orig$inNIBRS<-1
ucr_SRS_orig$inUCR<-1
SF_tots$inSFtots<-1


n_Univ_NIBRS_orig$inNIBRS<-1
ucr_SRS_orig$inUCR<-1
SF_tots$inSFtots<-1
SF_tots_all_fin$inSFtots<-1
SF_tots_all_region_fin$inSFtots<-1



#names(ucr_SRS_orig)

#ucr_SRS_orig<-ucr_SRS_orig%>%rename(ORI_universe=ORI_UNIVERSE)
ucr_SRS <- ucr_SRS_orig %>%
  inner_join(SF_tots_all_region_fin[,c("ORI_universe","wgtGpRegion","Nh")],by=c("ORI_universe")) %>%
  left_join(SF_tots[,c("ORI_universe","AGENCY_TYPE_NAME","REGION_NAME","PARENT_POP_GROUP_DESC2")],by=c("ORI_universe")) %>%
  inner_join(select(n_Univ_NIBRS_orig,"ORI_universe",RegionWgt),by=c("ORI_universe")) %>%
  mutate(one=1)

ucr_SRS$state_abbr<-substr(ucr_SRS$ORI_universe,1,2)
ucr_SRS<-ucr_SRS%>%rename(totcrime_imp_orig=totcrime_imp)
ucr_SRS$totcrime_imp<-ucr_SRS$tot_violent_imp+ucr_SRS$tot_property_imp

ucr_SRS <- data.frame(ucr_SRS)





#####################################################################
# Input List of Weights and Load Functions to process data
#####################################################################
#weight_state_lists<-(colnames(n_Univ_NIBRS_orig) %>%str_subset("calwt2") %>%as.list()) #List of weights, update as necessary
weight_region_lists_n<-(colnames(n_Univ_NIBRS_orig) %>%str_subset("RegionWgt") %>%as.list()) #List of weights, update as necessary



weight_region_lists_n_df<-data.frame(matrix(unlist(weight_region_lists_n), nrow=length(weight_region_lists_n), byrow=T))
names(weight_region_lists_n_df) <- c("weightVar")
weight_region_lists_n_df<-weight_region_lists_n_df %>% mutate(RowValue = row_number())



#File storing syntax for all functions used
log_debug("Running file Appendix_Tables_All_Functions.R")
source("Appendix_Tables_All_Functions.R")

#Dummy rows

outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")

output_folder <- sprintf("%s", outputPipelineDir)
dummyDatA_groupings<-
  read_dot_csv_logging(file.path(output_weighting_tableshell_folder,"TableAGpRegionDummy.csv"))%>%
  #filter(nid!=1)%>%
  mutate(CrimeOrder = RowValue-2) %>%
  mutate(REGION_NAME2=str_to_title(state_name)) %>%
  mutate(AGENCY_TYPE_NAME=case_when(AGENCY_TYPE_NAME=="REGION LEVEL ESTIMATES" ~ NA_character_,
                                    TRUE ~ AGENCY_TYPE_NAME))%>%
  mutate(PARENT_POP_GROUP_DESC2=case_when(PARENT_POP_GROUP_DESC2=="REGION LEVEL ESTIMATES" ~ NA_character_,
                                    TRUE ~ PARENT_POP_GROUP_DESC2))

popGps<-subset(dummyDatA_groupings,!is.na(PARENT_POP_GROUP_DESC2)) %>% .$PARENT_POP_GROUP_DESC2 %>% unique() %>% data.frame(PARENT_POP_GROUP_DESC2=.)
popGps$nid <- seq.int(nrow(popGps))
types<-subset(dummyDatA_groupings,!is.na(AGENCY_TYPE_NAME)) %>% .$AGENCY_TYPE_NAME %>% unique() %>% data.frame(AGENCY_TYPE_NAME=.)
types$nid <- max(popGps$nid)+seq.int(nrow(types))
regions<-subset(dummyDatA_groupings,!is.na(REGION_NAME)) %>% .$REGION_NAME %>% unique() %>% data.frame(REGION_NAME=.)
regions$nid <- max(types$nid)+seq.int(nrow(regions))
reg2 <- subset(dummyDatA_groupings,!is.na(REGION_NAME2)) %>% .$REGION_NAME2 %>% unique() %>% data.frame(REGION_NAME2=.)


dummyDatA_groupings<-dummyDatA_groupings[c("REGION_NAME2","AGENCY_TYPE_NAME","PARENT_POP_GROUP_DESC2","REGION_NAME","CrimeOrder","nid")]
#dummyDatA_groupings$state_name<-factor(dummyDatA_groupings$state_name,levels=states$state_name)
dummyDatA_groupings$AGENCY_TYPE_NAME<-factor(dummyDatA_groupings$AGENCY_TYPE_NAME,levels=types$AGENCY_TYPE_NAME)
dummyDatA_groupings$PARENT_POP_GROUP_DESC2<-factor(dummyDatA_groupings$PARENT_POP_GROUP_DESC2,levels=popGps$PARENT_POP_GROUP_DESC2)
dummyDatA_groupings$REGION_NAME<-factor(dummyDatA_groupings$REGION_NAME,levels=regions$REGION_NAME)
dummyDatA_groupings$REGION_NAME2<-factor(dummyDatA_groupings$REGION_NAME2,levels=reg2$REGION_NAME2)

groupings <- dummyDatA_groupings %>%
  select(REGION_NAME2,PARENT_POP_GROUP_DESC2,AGENCY_TYPE_NAME,REGION_NAME,nid) %>%
  subset(duplicated(.)==FALSE)
#groupings <- bind_rows(popGps,types,regions)


ucr_SRS <- ucr_SRS%>%
  mutate(REGION_NAME2=REGION_NAME)%>%#Dummy var for tables
  mutate(PARENT_POP_GROUP_DESC2=as.character(PARENT_POP_GROUP_DESC2),
         PARENT_POP_GROUP_DESC2=factor(PARENT_POP_GROUP_DESC2,levels=popGps$PARENT_POP_GROUP_DESC2),
         AGENCY_TYPE_NAME=as.character(AGENCY_TYPE_NAME),
         AGENCY_TYPE_NAME=factor(AGENCY_TYPE_NAME,levels=types$AGENCY_TYPE_NAME),
         REGION_NAME=as.character(REGION_NAME),
         REGION_NAME=factor(REGION_NAME,levels=regions$REGION_NAME),
         REGION_NAME2=as.character(REGION_NAME2),
         REGION_NAME2=factor(REGION_NAME2,levels=reg2$REGION_NAME2)
  )

#ucr_SRS$PARENT_POP_GROUP_DESC2 %>% head()
#ucr_SRS$AGENCY_TYPE_NAME %>% head()



NumPopGps<-ucr_SRS %>% subset(!is.na(RegionWgt)) %>% .$PARENT_POP_GROUP_DESC2 %>% unique() %>% length()
NumTypes<-ucr_SRS %>%subset(!is.na(RegionWgt)) %>% .$AGENCY_TYPE_NAME %>% unique() %>% length()
NumRegions <- ucr_SRS %>%subset(!is.na(RegionWgt)) %>% .$REGION_NAME %>% unique() %>% length()
NumGroups <- NumPopGps+NumTypes+NumRegions
#####################################################################
# Table A
#####################################################################

options(survey.lonely.psu = "adjust")
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

compute_regionTotals_TabA <- function(wtvar,indata,indicator){
  log_debug("Running function compute_regionTotals_TabA")
  respWgts <- indata %>%
    rename(wt=all_of(wtvar)) %>%
    subset(!is.na(totcrime_imp)) %>%
    subset(!is.na(wt)) %>% #Switch to indicator?
    svydesign(ids= ~1,data=.,strata=.$wgtGpRegion,weights=.$wt,fpc=.$Nh)

  df<-data.frame(genAppA_region(respWgts))
  #print(df)
  region_tot<-gather(data=df,key,value,starts_with("tot"),-REGION_NAME)%>%mutate(RowValue = as.numeric(row_number()))%>% select(-contains("se."))
  region_setot<-gather(data=df,key,value,starts_with("se"),-REGION_NAME)%>%mutate(RowValue = as.numeric(row_number()))%>% select(-contains("tot"))


  region_all0<-merge(region_tot,region_setot,by=c("REGION_NAME","RowValue"))%>%rename(Total=value.x)%>%rename(SE=value.y) %>% mutate(state_name=str_to_upper(REGION_NAME))
  #print(region_all0)

  region_all1<-region_all0 %>%mutate(CrimeOrder=case_when(
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

  region_all2<-region_all1 %>% mutate(REGION_NAME2=str_to_title(state_name))
  #print(region_all2)
  region_all<-left_join(dummyDatA_groupings %>%
                          subset(is.na(AGENCY_TYPE_NAME) &is.na(PARENT_POP_GROUP_DESC2) & is.na(REGION_NAME)),
                        region_all2,
                        by=c("REGION_NAME2",#"state_abbr",
                             "CrimeOrder"))
  #print(region_all)
  region_all <- region_all[with(region_all,order(REGION_NAME2,#state_abbr,
                                                 CrimeOrder)),]
  #print(region_all)
  return(list(data.frame(region_all)))
}
#Generate UCR overall
regionEstimates_TabA_SRS <-(
  compute_regionTotals_TabA(wtvar="one",indata=ucr_SRS,indicator="inNIBRS") %>%
    .[[1]]) #Get the data frame in the list
#Note: SEs are much lower in above vs Grant's file bc we use fpc here

#Generate estimates for NIBRS Reporters
#compute_regionTotals_TabA(wtvar=weight_lists_n[[1]],indata=ucr_SRS,indicator="inNIBRS")

regionEstimates_TabA_nibrsReps <- (
  sapply(weight_region_lists_n,compute_regionTotals_TabA,indata=ucr_SRS,indicator="inNIBRS"))
#names(ucr_SRS)

######
#Merge estimates for SRS + NIBRS reporters
list_of_tablesA_region <- (
  sapply(1:length(regionEstimates_TabA_nibrsReps),
         function(subTab){
           inner_join(x=regionEstimates_TabA_nibrsReps[[subTab]],
                      y=regionEstimates_TabA_SRS,
                      by=c("REGION_NAME2","CrimeOrder"),
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

names(list_of_tablesA_region) <- weight_region_lists_n



##For summary of Relative Bias Table###
summary_tableA_region<-list_of_tablesA_region %>% bind_rows(.id="weightVar") %>%
  rename(RowValue=RowValue.Reps,
         Total=Total.Reps,
         SE=SE.Reps) %>%
  mutate(RowValue2=RowValue %% NumRegions) %>% #Make it so 1 RowValue2 per state
  mutate(RowValue2=ifelse(RowValue2==0,NumRegions,RowValue2)) %>% #Set last state to 51 (originally=0)
  reshape2::melt(id.vars=c("weightVar","RowValue2","REGION_NAME2","CrimeOrder"),measure.vars=c("BR.Repsn")) %>%
  reshape2::dcast(formula=REGION_NAME2+RowValue2+weightVar~paste0(variable,CrimeOrder)) %>%
  {merge(groupings %>% subset(nid%%nrow(.)==1) %>% .[c("REGION_NAME2","nid")],.,by=c("REGION_NAME2"))} %>%
  arrange(nid,weightVar)







#By group
genAppA_region_gp <- function(des,byFormula){
  log_debug("Running function genAppA_region_gp")
  survey::svyby(~totcrime_imp+tot_violent_imp+
                  tot_murder_imp+tot_manslaughter_imp+tot_rape_imp+tot_rob_imp+
                  tot_assault_imp+tot_aggAssault_imp+tot_simpAssault_imp+
                  tot_property_imp+
                  tot_burglary_imp+tot_larceny_imp+tot_vhcTheft_imp,by=byFormula,design= des, FUN=svytotal)

}

compute_regionTotals_gp_TabA<- function(wtvar,indata,indicator){
  log_debug("Running function compute_regionTotals_gp_TabA")

  respWgts <- indata %>%
    rename(wt=all_of(wtvar)) %>%
    subset(!is.na(totcrime_imp)) %>%
    subset(!is.na(wt)) %>% #Switch to indicator?
    svydesign(ids= ~1,data=.,strata=.$wgtGpRegion,weights=.$wt,fpc=.$Nh)
  #print(respWgts)
  # print(indata %>%
  #         rename(wt=all_of(wtvar)) %>%
  #         subset(AGENCY_TYPE_NAME=="State Police") %>%
  #         subset(!is.na(totcrime_imp)) %>%
  #         subset(!is.na(wt)) %>%
  #         select(ORI_universe,totcrime_imp,wt))
  #print("Start pop gp")
  df<-data.frame(genAppA_region_gp(respWgts,byFormula= ~REGION_NAME2+PARENT_POP_GROUP_DESC2))
  #print(df)
  popGp_tot<-gather(data=df,key,value,starts_with("tot"),-c(REGION_NAME2,PARENT_POP_GROUP_DESC2))%>%mutate(RowValue = as.numeric(row_number()))%>% select(-contains("se."))
  popGp_setot<-gather(data=df,key,value,starts_with("se"),-c(REGION_NAME2,PARENT_POP_GROUP_DESC2))%>%mutate(RowValue = as.numeric(row_number()))%>% select(-contains("tot"))
  #print(popGp_tot)

  popGp_all0<-merge(popGp_tot,popGp_setot,by=c("REGION_NAME2","PARENT_POP_GROUP_DESC2","RowValue"))%>%rename(Total=value.x)%>%rename(SE=value.y)
  #print(popGp_all0)

  popGp_all1<-popGp_all0 %>%mutate(CrimeOrder=case_when(
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
  #print(popGp_all1)
  popGp_all<-left_join(dummyDatA_groupings,popGp_all1,by=c("REGION_NAME2","PARENT_POP_GROUP_DESC2","CrimeOrder")) %>%
    subset(!is.na(PARENT_POP_GROUP_DESC2))
  #print(popGp_all)
  popGp_all <- popGp_all[with(popGp_all,order(REGION_NAME2,PARENT_POP_GROUP_DESC2,CrimeOrder)),]

  #print("End Pop gp")

  df<-data.frame(genAppA_region_gp(respWgts,byFormula= ~REGION_NAME2+AGENCY_TYPE_NAME))
  #print(df)
  type_tot<-gather(data=df,key,value,starts_with("tot"),-c(REGION_NAME2,AGENCY_TYPE_NAME))%>%mutate(RowValue = as.numeric(row_number()))%>% select(-contains("se."))
  type_setot<-gather(data=df,key,value,starts_with("se"),-c(REGION_NAME2,AGENCY_TYPE_NAME))%>%mutate(RowValue = as.numeric(row_number()))%>% select(-contains("tot"))
  #print(type_tot)

  type_all0<-merge(type_tot,type_setot,by=c("REGION_NAME2","AGENCY_TYPE_NAME","RowValue"))%>%rename(Total=value.x)%>%rename(SE=value.y)
  #print(type_all0)

  type_all1<-type_all0 %>%mutate(CrimeOrder=case_when(
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
  #print(type_all1)

  type_all<-left_join(dummyDatA_groupings,type_all1,by=c("REGION_NAME2","AGENCY_TYPE_NAME","CrimeOrder"))%>%
    subset(!is.na(AGENCY_TYPE_NAME))
  #print(type_all)
  type_all <- type_all[with(type_all,order(REGION_NAME2,AGENCY_TYPE_NAME,CrimeOrder)),]
  #print(type_all)

  #print("End Agency type")

  #Region name
  df<-data.frame(genAppA_region_gp(respWgts,byFormula= ~REGION_NAME2+REGION_NAME))
  #print(df)
  region_tot<-gather(data=df,key,value,starts_with("tot"),-c(REGION_NAME2,REGION_NAME))%>%mutate(RowValue = as.numeric(row_number()))%>% select(-contains("se."))
  region_setot<-gather(data=df,key,value,starts_with("se"),-c(REGION_NAME2,REGION_NAME))%>%mutate(RowValue = as.numeric(row_number()))%>% select(-contains("tot"))


  region_all0<-merge(region_tot,region_setot,by=c("REGION_NAME2","REGION_NAME","RowValue"))%>%rename(Total=value.x)%>%rename(SE=value.y)
  #print(region_all0)

  region_all1<-region_all0 %>%mutate(CrimeOrder=case_when(
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
  #print(region_all1)

  region_all<-left_join(dummyDatA_groupings,region_all1,by=c("REGION_NAME2","REGION_NAME","CrimeOrder"))%>%
    subset(!is.na(REGION_NAME))
  #print(region_all)

  region_all <- region_all[with(region_all,order(REGION_NAME,CrimeOrder)),]
  #print(region_all)

  groupings_all <- bind_rows(popGp_all %>% subset(!is.na(PARENT_POP_GROUP_DESC2)),
                             type_all %>% subset(!is.na(AGENCY_TYPE_NAME)),
                             region_all %>% subset(!is.na(REGION_NAME)))
  #print(groupings_all)

  groupings_all <- groupings_all[with(groupings_all,order(REGION_NAME2,PARENT_POP_GROUP_DESC2,AGENCY_TYPE_NAME,REGION_NAME,CrimeOrder)),]

  #print(groupings_all)
  #print(groupings_all %>% subset(!is.na(AGENCY_TYPE_NAME)))
  return(list(data.frame(groupings_all)))
}
#Generate UCR overall
regionEstimates_TabA_gp_SRS <-(
  compute_regionTotals_gp_TabA(wtvar="one",indata=ucr_SRS,indicator="inNIBRS") %>%
    .[[1]]) #Get the data frame in the list
#Note: SEs are much lower in above vs Grant's file bc we use fpc here



#Generate estimates for NIBRS Reporters
#compute_regionTotals_TabA(wtvar=weight_lists_n[[1]],indata=ucr_SRS,indicator="inNIBRS")

regionEstimates_TabA_gp_nibrsReps <- (
  sapply(weight_region_lists_n,compute_regionTotals_gp_TabA,indata=ucr_SRS,indicator="inNIBRS"))
#names(ucr_SRS)

######
#Merge estimates for SRS + NIBRS reporters
list_of_tablesA_gp_region <- (
  sapply(1:length(regionEstimates_TabA_gp_nibrsReps),
         function(subTab){
           inner_join(x=regionEstimates_TabA_gp_nibrsReps[[subTab]],
                      y=regionEstimates_TabA_gp_SRS,
                      by=c("REGION_NAME2","PARENT_POP_GROUP_DESC2","AGENCY_TYPE_NAME","REGION_NAME","CrimeOrder"),
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

names(list_of_tablesA_gp_region) <- weight_region_lists_n


#list_of_tablesA_gp_region


summary_tableA_gp_region <- list_of_tablesA_gp_region %>% bind_rows(.id="weightVar") %>%
  rename(RowValue=RowValue.Reps,
         Total=Total.Reps,
         SE=SE.Reps) %>%
  #mutate(RowValue2=case_when(!is.na(PARENT_POP_GROUP_DESC2) ~ RowValue %% NumPopGps,
  #                           !is.na(AGENCY_TYPE_NAME) ~ (RowValue %% NumTypes)+NumPopGps,
  #                           !is.na(REGION_NAME) ~ (RowValue %% NumRegions)+NumPopGps+NumTypes)) %>% #Make it so 1 RowValue2 per state
  #mutate(RowValue2=case_when(!is.na(PARENT_POP_GROUP_DESC2) ~ ifelse(RowValue2==0,NumPopGps,RowValue2),
  #                           !is.na(AGENCY_TYPE_NAME) ~ ifelse(RowValue2==NumPopGps,NumTypes+NumPopGps,RowValue2),
  #                           !is.na(REGION_NAME) ~ ifelse(RowValue2==NumPopGps,NumTypes+NumPopGps+NumRegions,RowValue2))) %>% #Set last state to 51 (originally=0)
  reshape2::melt(id.vars=c("weightVar",#"RowValue2",
                           "REGION_NAME2","PARENT_POP_GROUP_DESC2","AGENCY_TYPE_NAME","REGION_NAME","CrimeOrder"),measure.vars=c("BR.Repsn")) %>%
  reshape2::dcast(formula=REGION_NAME2+PARENT_POP_GROUP_DESC2+AGENCY_TYPE_NAME+REGION_NAME+#RowValue2+
                    weightVar~paste0(variable,CrimeOrder)) %>%
  {merge(groupings[c("REGION_NAME2","PARENT_POP_GROUP_DESC2","AGENCY_TYPE_NAME","REGION_NAME","nid")],.,by=c("REGION_NAME2","PARENT_POP_GROUP_DESC2","AGENCY_TYPE_NAME","REGION_NAME"))} %>%
  arrange(REGION_NAME2,nid,weightVar)
#summary_tableA_gp_region
####################Table A combined#################################

summary_tableA_gp <- bind_rows(summary_tableA_region,summary_tableA_gp_region) %>%
  select(-matches("RowValue")) %>%
  arrange(nid)%>%
  arrange(REGION_NAME2,nid)


#####################################################################
# Output Tables
#####################################################################

#Reorder to match shell
#Blank out rows as appropriate, i.e. if Violent Crime blank ("--") out
#weights calibrated to property crimes
summary_tableA_gp<-left_join(summary_tableA_gp,bind_rows(weight_region_lists_n_df),#weight_state_lists_n_df),
                             by=c("weightVar"))

#summary_tableA_gp

#####################################################################
# Table A
# Columns: Estimate, SE(Estimate), RSE, Bias Ratio
# Rows: Offense Type
# Data: NIBRS, SRS
#####################################################################

#Blank out appropriate rows per weight
summary_tableA_blankOut_gp<-summary_tableA_gp%>%
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

summary_tableA_blankOut_gp<- summary_tableA_blankOut_gp %>%
 arrange(REGION_NAME2,nid,RowValue)




#names(list_of_tablesA) <- weight_lists #excel sheet names
crime_type_indTabA=matrix(c("N", rep("V",8), rep("P",4)),nrow=663) #Crime types -V=Violent, P=Property
keepColsTabA<-c("Total.Reps", "SE.Reps", "RSE.Reps", "Total.SRS","BR.Reps","BRGT5")
include_dashTabA<-matrix(rep("---", times =6),nrow=1)
summary_tableAKeep_gp<-summary_tableA_blankOut_gp[c("BR.Repsn0","BR.Repsn1","BR.Repsn2",
                                                    "BR.Repsn3","BR.Repsn4","BR.Repsn5",
                                                    "BR.Repsn6","BR.Repsn7","BR.Repsn8",
                                                    "BR.Repsn9","BR.Repsn10","BR.Repsn11",
                                                    "BR.Repsn12")]



#################
#Summary Sheet
################

str1 <- file.path(output_weighting_populated_folder,'TableA_Groupings_Region_Populated')

#str1 <- '//rtpnfil02/0216153_NIBRS/03_SamplingPlan/SubTask3_new_Weighting_Validation_Results/2019/TableA_Statept2'
#paste0(str1, format(Sys.time(),'_%Y%m%d'), '.xlsx')

filein <- file.path(output_weighting_tableshell_folder,"TableA_Groupings_Region_Shell.xlsx")



# Load the existing workbook
wbTabARegion <- loadWorkbook(file =filein )


# Write data to specific range in Excel, specified by start column and start row
log_debug("Writing sheet Summary_Region_TabA_Ex1")
writeData(wbTabARegion, sheet = "Summary_Region_TabA_Ex1", x = summary_tableAKeep_gp, startCol = 4, startRow = 8, colNames = FALSE,keepNA=FALSE)

saveWorkbook(wbTabARegion, file=paste0(str1, format(Sys.time(),'_%Y%m%d'), '.xlsx'), overwrite = TRUE)


#################
#Weights Sheets
################

#TypeTab; 9999 code if includes state-level table, 8888 code for overall table
#stZ: Startinf sheet number minus 1, i.e. if tab is 2nd sheet, stZ=1
#crime_type - Values of P or V to indicate if property or violent crime and suppress as applicable values

list_of_tablesA_region_all <- bind_rows(list_of_tablesA_region %>% bind_rows(.id="weightVar") %>% #select(keepColsTabA) %>%
                                         mutate(RSE.Reps=as.character(RSE.Reps),
                                                BR.Reps=as.character(BR.Reps)),
                                         list_of_tablesA_gp_region %>% bind_rows(.id="weightVar")) %>% #select(keepColsTabA)) #%>%
  full_join(dummyDatA_groupings) %>%
  arrange(REGION_NAME2,nid) %>%
  list()
weight_lists <- weight_region_lists_n
write_files_xlsx(listfile_name = list_of_tablesA_region_all,
                 infile_name=paste0(str1, format(Sys.time(),'_%Y%m%d'), '.xlsx'),
                 file_name= paste0(str1, format(Sys.time(),'_%Y%m%d'), '.xlsx'),
                 keepCols=keepColsTabA,
                 blankOut=include_dashTabA,
                 crime_type=crime_type_indTabA,
                 stZ=1, #If starting sheet is first, value should be "0", otherwise number after
                 inCol=4,
                 inRow=8,
                 typeTab=9999)
log_info("Finished 05_Populate_TableA_Groupings_Region.R\n\n")