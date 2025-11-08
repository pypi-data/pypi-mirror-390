#This program is for testing variations of the state weights
#Specifically, this is based on 4 strata with SRS calibration

maxAdj <- 10 #Max adjustment factor
maxIt <- 1000 #Max iterations during variable selection
srK <- 30 #01May2024: added today

### Purpose of program is to calibrate state weights by state X grouping (e.g., All cities 250,000 or over)
### Author: JD Bunker
### Last updated: 29OCT2021
#Update (28OCT2021): Commenting out/removing unnecessary print statements and removing no longer needed commented-out code
#Update (29OCT2021): Continuing clean up efforts (commenting out / deleting commented-out code)
#Update (07OCT2022): Adding maxWgt and maxIt values for final weight
#Update (10AUG2025): Removing use of gencalib() with only overall crime if 
#                      can't fit >1 variable; instead, just use the inverse
#                      crime coverage as the weight (like we had been doing if
#                      even the 1-variable model failed in gencalib()).
#                    Additionally, include the overall crime in the 
#                      V[NUMBER]_[A-I] calibration variables for crossings 
#                      where we use the inverse crime coverage as the weights
#                      in the output.

library(tidyverse)
library(openxlsx)
library(lubridate)
library(sampling)
library(data.table)
library(Hmisc)

log_info("Running 03_Weights_Calibration_State_SRS_AltCombs.R")

##Note (22Jun2023): Reading in new crossing worksheet
stateCrosses <- paste0(input_weighting_data_folder,"Geography_Crossings.xlsx") %>%
  read_xlsx(sheet="State") %>%
  rename(STATE_NAME=stateLvl,
         wgtGpState=stateWgtGp)

# read in SF data

SF <- paste0(input_weighting_data_folder,"SF_postR.csv") %>%
  #read.csv(header=TRUE, sep=",") %>%
  fread() %>%
  data.frame() %>%
  mutate(totcrime_imp=totcrime_violent_imp+totcrime_property_imp)

print("Columns of SF:")
colnames(SF)
crimeVars <- SF %>%
  colnames() %>%
  str_subset("^tot.*_imp")

#Crime variables for weight calibration
#Note (28Apr2023): Splitting into variables for all state X weighting groups vs. extra crime vars
crimeVarsWgtAll <- c("totcrime_imp",
                     "totcrime_violent_imp",
                     "totcrime_property_imp")
crimeVarsWgtRest <- c("totcrime_murder_imp",
                      "totcrime_rape_imp","totcrime_aggAssault_imp",
                      "totcrime_burglary_imp","totcrime_rob_imp",
                      "totcrime_larceny_imp","totcrime_vhcTheft_imp")
crimeVarsWgt <- c(crimeVarsWgtAll,crimeVarsWgtRest)

stateGps <- SF %>%
  select(STATE_NAME) %>%
  unique() %>%
  .$STATE_NAME
nStateGps <- SF %>%
  select(STATE_NAME) %>%
  unique() %>%
  nrow()


srs_state_control_totals <- SF %>%
  group_by(STATE_NAME) %>%
  dplyr::summarize(across(.cols=all_of(crimeVarsWgt),.fns=list("sum"=sum),.names="{.fn}_{.col}",na.rm=TRUE))


wgtGpStateDescs <-  c("Cities 1,000,000 or over",
                      "Cities from 500,000 thru 999,999",
                      "Cities from 250,000 thru 499,999",
                      "Cities from 100,000 thru 249,999",
                      "Cities from 50,000 thru 99,999",
                      "Cities from 25,000 thru 49,999",
                      "Cities from 10,000 thru 24,999",
                      "Cities from 2,500 thru 9,999",
                      "Cities under 2,500",
                      "MSA counties 100,000 or over",
                      "MSA counties from 25,000 thru 99,999",
                      "MSA counties from 10,000 thru 24,999",
                      "MSA counties under 10,000",
                      "MSA State Police",
                      "Non-MSA counties 100,000 or over",
                      "Non-MSA counties from 25,000 thru 99,999",
                      "Non-MSA counties from 10,000 thru 24,999",
                      "Non-MSA counties under 10,000",
                      "Non-MSA State Police",
                      "CITY AGENCY-ZERO POP",
                      "MSA COUNTY/STATE AGENCY-ZERO POP",
                      "NON-MSA COUNTY/STATE AGENCY-ZERO POP")
SF2 <- SF %>%
  mutate(totcrime_agg_rob_imp=totcrime_aggAssault_imp+totcrime_rob_imp)%>%
  mutate(wgtGpState=case_when(POPULATION_GROUP_DESC=="Cities 1,000,000 or over" ~ 1,
                              POPULATION_GROUP_DESC=="Cities from 500,000 thru 999,999" ~ 2,
                              POPULATION_GROUP_DESC=="Cities from 250,000 thru 499,999" ~ 3,
                              POPULATION_GROUP_DESC=="Cities from 100,000 thru 249,999" ~ 4,
                              POPULATION_GROUP_DESC=="Cities from 50,000 thru 99,999" ~ 5,
                              POPULATION_GROUP_DESC=="Cities from 25,000 thru 49,999" ~ 6,
                              POPULATION_GROUP_DESC=="Cities from 10,000 thru 24,999" ~ 7,
                              #Note: splitting out cities under 10K into 2 groups... these were combined in weighting program and thus throw off levels by 1
                              POPULATION_GROUP_DESC %in% c("Cities from 2,500 thru 9,999") ~ 8,
                              POPULATION_GROUP_DESC=="Cities under 2,500" & POPULATION> 0 ~ 9,
                              
                              POPULATION_GROUP_DESC=="MSA counties 100,000 or over" ~ 10,
                              POPULATION_GROUP_DESC=="MSA counties from 25,000 thru 99,999" ~ 11,
                              POPULATION_GROUP_DESC=="MSA counties from 10,000 thru 24,999" ~ 12,
                              POPULATION_GROUP_DESC=="MSA counties under 10,000" &  POPULATION> 0 ~ 13,
                              POPULATION_GROUP_DESC=="MSA State Police" & POPULATION>0 ~ 14,
                              #Note: splitting out non-msa counties 25K and up into 2 groups... these were combined in weighting program and thus throw off levels by 1
                              POPULATION_GROUP_DESC %in% c("Non-MSA counties from 25,000 thru 99,999") ~ 15,
                              POPULATION_GROUP_DESC=="Non-MSA counties 100,000 or over" ~ 16,
                              POPULATION_GROUP_DESC=="Non-MSA counties from 10,000 thru 24,999" ~ 17,
                              POPULATION_GROUP_DESC=="Non-MSA counties under 10,000" & POPULATION >0 ~ 18,
                              POPULATION_GROUP_DESC=="Non-MSA State Police" & POPULATION>0 ~ 19,
                              
                              POPULATION_GROUP_DESC=="Cities under 2,500" & POPULATION==0 ~ 20,
                              POPULATION_GROUP_DESC %in% c("MSA counties under 10,000","MSA State Police") & POPULATION==0 ~ 21,
                              POPULATION_GROUP_DESC %in% c("Non-MSA counties under 10,000","Non-MSA State Police") & POPULATION==0 ~ 22),
         wgtGpStateDesc=factor(wgtGpState,levels=1:22,labels=wgtGpStateDescs))%>%
  #Note (01May2024): Drop all calibration variables that already exist (e.g., national and region)
  select(-matches("^V\\d+_\\w"))

stateGps2 <- SF2 %>%
  pull(STATE_NAME) %>%
  unique()
nStateGps2 <- stateGps2 %>%
  length()

wgtGpsState <- SF2 %>%
  pull(wgtGpState) %>%
  unique()
nWgtGpsState <- length(wgtGpsState)

#01May2024: implementing self-reporting treatment:
#>Summarize to the agency level
#>Count the number of nonreporters among agencies with >30x the state's mean crime count
#>If all agencies are reporters, isolate them into their own weighting group 
#>Then proceed with weighting as usual with the remaining agencies (e.g., exclude large agencies' crime counts with remaining agencies)  

srEligible <- SF2 %>%
  #group_by(ORI,JUDICIAL_DISTRICT_NAME,resp_ind_srs) %>%
  #dplyr::summarize(totcrime_imp=sum(totcrime_imp),
  #                 POPULATION_UNIV=sum(POPULATION_UNIV)) %>%
  #Now, get mean for the judicial district
  group_by(STATE_NAME) %>%
  mutate(mean_totcrime_imp_state=mean(totcrime_imp),
         POP_ELIG=sum(POPULATION),
         POP_RESP=sum(POPULATION*resp_ind_m3),
         propCoverage=POP_RESP/POP_ELIG
  ) %>%
  ungroup() %>%
  subset(totcrime_imp>srK*mean_totcrime_imp_state)
#Get list of states where we'll implement self representing methodology
srStates <- srEligible %>% 
  group_by(STATE_NAME) %>% 
  dplyr::summarize(nSREligible=n(),
                   nSRReporter=sum(resp_ind_m3)) %>%
  subset(nSREligible==nSRReporter)
#Now, let's get a list of agency crossings that are going to be self-representing
srLEA <- srEligible %>%
  inner_join(srStates) %>%
  select(ORI) %>%
  unique() %>%
  arrange(ORI)


#Detect and perform any necessary collapsing (number of respondents in non-empty state X grouping is 0)
#Note (14Aug2023): perform different collapsing for 2020 vs. 2021 onward
#Note (01May2024): Accounting for addition of self-representing weighting group
if (year>=2021){
  wgtGpsState2 <- 1:10
  wgtGpStateDescs2 <- c("Not self-representing - Cities 250,000 or over",
                        "Not self-representing - Cities from 100,000 thru 249,999 and MSA counties 100,000 or over",
                        "Not self-representing - Zero population agencies",
                        "Not self-representing - Other strata",
                        "Not self-representing - Cities 250,000 or over and Cities from 100,000 thru 249,999 and MSA counties 100,000 or over",
                        "Not self-representing - Cities 250,000 or over and Other strata",
                        "Not self-representing - Cities from 100,000 thru 249,999 and MSA counties 100,000 or over and Other strata",
                        "Not self-representing - Cities 250,000 or over and Cities from 100,000 thru 249,999 and MSA counties 100,000 or over and Other strata",
                        "Not self-representing - All strata",
                        "Self-representing")
  SF2 <- SF2 %>%
    mutate(wgtGpState2=case_when((!STATE_NAME %in% c("Alaska","Florida","Hawaii","Louisiana","Maryland","Pennsylvania")) & wgtGpState %in% 1:3 ~ 1,
                                 (!STATE_NAME %in% c("Florida","Hawaii","Louisiana","Maryland","Mississippi","Pennsylvania")) & wgtGpState %in% c(4,10) ~ 2,
                                 (!STATE_NAME %in% c("Florida","Hawaii")) & wgtGpState %in% 20:22 ~ 3,
                                 !STATE_NAME %in% c("Alaska","Florida","Hawaii","Mississippi","Pennsylvania") & wgtGpState %in% c(5:9,11:19) ~ 4,
                                 STATE_NAME %in% c("Louisiana","Maryland") & wgtGpState %in% c(1:3,4,10) ~ 5,
                                 STATE_NAME %in% "Alaska" & wgtGpState %in% c(1:3,5:9,11:19) ~ 6,
                                 STATE_NAME %in% "Mississippi" & wgtGpState %in% c(4,10,5:9,11:19) ~ 7,
                                 STATE_NAME %in% "Pennsylvania" & wgtGpState %in% c(1:3,4,10,5:9,11:19) ~ 8,
                                 STATE_NAME %in% c("Florida","Hawaii") ~ 9
                                 
    ),
    wgtGpStateDesc2=factor(wgtGpState2,levels=wgtGpsState2,labels=wgtGpStateDescs2))
} else if (year==2020){
  wgtGpsState2 <- 1:12
  wgtGpStateDescs2 <- c("Not self-representing - Cities 250,000 or over",
                        "Not self-representing - Cities from 100,000 thru 249,999 and MSA counties 100,000 or over",
                        "Not self-representing - Zero population agencies",
                        "Not self-representing - Other strata",
                        "Not self-representing - Cities 250,000 or over and Cities from 100,000 thru 249,999 and MSA counties 100,000 or over",
                        "Not self-representing - Cities 250,000 or over and Other strata",
                        "Not self-representing - Cities from 100,000 thru 249,999 and MSA counties 100,000 or over and Other strata",
                        "Not self-representing - Cities 250,000 or over and Cities from 100,000 thru 249,999 and MSA counties 100,000 or over and Other strata",
                        "Not self-representing - All strata",
                        "Not self-representing - Cities 250,000 or over and Zero population agencies",
                        "Not self-representing - Zero population agencies and Other strata")
  SF2 <- SF2 %>%
    mutate(wgtGpState2=case_when((!STATE_NAME %in% c("Alaska","California","District of Columbia","Florida","Hawaii","Illinois","Louisiana","Maryland","Nebraska","New Jersey","Pennsylvania")) & wgtGpState %in% 1:3 ~ 1,
                                 (!STATE_NAME %in% c("Alabama","California","Florida","Hawaii","Illinois","Louisiana","Maryland","Mississippi","New Jersey","Pennsylvania")) & wgtGpState %in% c(4,10) ~ 2,
                                 (!STATE_NAME %in% c("California","District of Columbia","Florida","Hawaii","Illinois","Maryland","New Jersey","Pennsylvania","Wyoming")) & wgtGpState %in% 20:22 ~ 3,
                                 !STATE_NAME %in% c("Alabama","Alaska","California","Florida","Hawaii","Illinois","Maryland","Mississippi","Nebraska","New Jersey","Pennsylvania","Wyoming") & wgtGpState %in% c(5:9,11:19) ~ 4,
                                 STATE_NAME %in% c("Louisiana") & wgtGpState %in% c(1:3,4,10) ~ 5,
                                 STATE_NAME %in% c("Nebraska") & wgtGpState %in% c(1:3,5:9,11:19) ~ 6,
                                 STATE_NAME %in% c("Alabama","Mississippi") & wgtGpState %in% c(4,10,5:9,11:19) ~ 7,
                                 #STATE_NAME %in% "Pennsylvania" & wgtGpState %in% c(1:3,4,10,5:9,11:19) ~ 8,
                                 STATE_NAME %in% c("Alaska","California","Florida","Hawaii","Illinois","Maryland","New Jersey","Pennsylvania") ~ 9,
                                 STATE_NAME %in% "District of Columbia" ~ 10,
                                 STATE_NAME %in% c("Wyoming") ~ 11
                                 
    ),
    wgtGpStateDesc2=factor(wgtGpState2,levels=wgtGpsState2,labels=wgtGpStateDescs2))
}
#10May2024: adding dummy wgtGpsState3 and wgtGpStateDescs3 - was getting error during combination summaries after recent self-reporting update
wgtGpsState3 <- wgtGpsState2
wgtGpStateDescs3 <- wgtGpStateDescs2

SF2 <- SF2 %>%
  rename(wgtGpState_raw=wgtGpState,
         wgtGpStateDesc_raw=wgtGpStateDesc) %>%
  rename(wgtGpState=wgtGpState2,
         wgtGpStateDesc=wgtGpStateDesc2)

#Set aside SR agencies...
SF2_skipSR <- SF2 %>%
  inner_join(srLEA) %>%
  mutate(StateWgt=1)
#Exclude SR agencies from further processing...
SF2 <- SF2 %>%
  anti_join(srLEA)


#21Apr2023: collapsing all non-zero pop together
#wgtGpsState3 <- wgtGpsState2
#wgtGpStateDescs3 <- wgtGpStateDescs2

#SF2 <- SF2 %>%
#  mutate(wgtGpState3=wgtGpState2,
#         wgtGpStateDesc3=factor(wgtGpState3,levels=wgtGpsState3,labels=wgtGpStateDescs3))


#SF2 <- SF2 %>%
#  rename(wgtGpState_raw=wgtGpState,
#         wgtGpStateDesc_raw=wgtGpStateDesc) %>%
#  rename(wgtGpState=wgtGpState2,
#         wgtGpStateDesc=wgtGpStateDesc2)



stateCrosses2 <- SF2 %>%
  select(STATE_NAME,wgtGpState) %>%
  unique() %>%
  inner_join(stateCrosses)

#Get totals by weighting group
srs_state_control_totals <- SF2 %>%
  group_by(STATE_NAME,wgtGpState) %>%
  dplyr::summarize(across(all_of(crimeVarsWgt),.fns=list("sum"=sum),.names="{fn}_{col}",na.rm=TRUE),
                   .groups="drop")
SF2 <- SF2 %>%
  left_join(srs_state_control_totals,by=c("STATE_NAME","wgtGpState"))

#Get n NIBRS Reporters and n Eligible - used for base weights and lower bounds
#Note (12Apr2023): adding ratio for totcrime_imp - state X weighting groups with >=99% will skip weighting and be assigned weights of 1
ratio <- SF2 %>%
  group_by(STATE_NAME,wgtGpState) %>%
  dplyr::summarize(n=sum(resp_ind_m3==1),
                   N=n(),
                   sum_totcrime_imp_NIBRS=sum(totcrime_imp*resp_ind_m3),
                   sum_totcrime_imp_all=sum(totcrime_imp),
                   ratio_totcrime_imp=sum_totcrime_imp_NIBRS/sum_totcrime_imp_all) %>%
  mutate(baseWgt=N/n,
         lowBound=n/N)

SF2 <- SF2 %>%
  select(-matches("sum_totcrime")) %>%
  inner_join(srs_state_control_totals) %>%
  select(-matches("^(n|N|baseWgt|lowBound)$")) %>%
  full_join(ratio,by=c("STATE_NAME","wgtGpState"))

#Note (14Aug2023): Handle skips differently for 2021 onward vs. 2020
if (year>=2021){
  #Note (12Apr2023): Setting aside state X weighting group crossings with >=99%
  crossings_skips <- ratio %>%
    subset(ratio_totcrime_imp>=0.99) %>%
    select(STATE_NAME,wgtGpState)
} else if (year==2020){
  #States with no respondents (AK, CA, FL, NJ)
  crossings_skipsA <- ratio %>%
    subset(STATE_NAME %in% c("Alaska","California","Florida","New Jersey")) %>%
    select(STATE_NAME,wgtGpState)
  crossings_skipsB <- ratio %>% 
    subset(ratio_totcrime_imp>=0.99) %>%
    select(STATE_NAME,wgtGpState)
  crossings_skips <- bind_rows(crossings_skipsA,
                               crossings_skipsB) %>%
    unique()
}
SF2_skips <- SF2 %>%
  inner_join(crossings_skips) %>%
  mutate(StateWgt=ifelse(resp_ind_m3==1,1,NA_real_))
SF2 <- SF2 %>%
  anti_join(crossings_skips)
srs_state_control_totals <- srs_state_control_totals %>%
  anti_join(crossings_skips)
stateGps2 <- SF2 %>%
  pull(STATE_NAME) %>%
  unique() %>%
  sort()
#Note (12Apr2023): Dropping skipped crossings from main file
#SF2 %>%
#  group_by(STATE_NAME,wgtGpState,wgtGpStateDesc) %>%
#  dplyr::summarize(N=n(),
#                   n=sum(resp_ind_m3)) %>%
#  DT::datatable()
#  
#stop()

#Update (28OCT2021): Reducing print statements
#Update (23MAR2022): Stop running after first successful convergence for weighting group
#Update (23MAR2022): Lowering max_iter from 10000 to 1000
#Update (21MAR2023): Reducing number of print and log statements
#Update (11AUG2025): Reducing log statements (only print # of gps if stopInd=0)
#                    Also, updating weights for nVar==1 (don't use gencalib())
SF2_wgts2_test <- sapply(stateGps2,function(i){#Loop over weight groupings
  log_debug("Running function SF2_wgts2_test")
  log_debug("##################")
  log_debug(paste0("State: ",i))
  #Note (09Jan2023): Removing totcrime_imp requirement
  SF_temp_state <- SF2 %>%
    subset(STATE_NAME==i & resp_ind_m3==1)
  srs_control_totals_temp_state <- srs_state_control_totals %>%
    subset(STATE_NAME==i)
  ratio_state <- ratio %>% subset(STATE_NAME==i)
  temp.wgtGps <- srs_control_totals_temp_state %>% pull(wgtGpState)
  
  SF2_wgts_state <- sapply(temp.wgtGps,function(j){#Loop over weight groupingstemp.#wgtGps,function(j){#Loop over weight groupings
    log_debug("#########")
    log_debug(paste0("State: ",i,". Weight group: ",j))
    #Take weighting group subset within state subset
    #Note (09Jan2023): Removing totcrime_imp requirement
    SF_temp <- SF_temp_state %>%
      subset(wgtGpState==j & resp_ind_m3==1)
    if (nrow(SF_temp)>0){
      stopInd <- 0 #Initialize stop indicator to 0
      tempEnv <- environment() #Function environment
      out_temp <- sapply(length(crimeVarsWgtRest):0,function(nVar){#Loop over n control total variables
        if (stopInd==0){
          log_debug(paste0("State: ",i,". Weight group: ",j,". n SRS Variables: ",nVar+length(crimeVarsWgtAll)))
        }
        varCombs_nVar <- combn(crimeVarsWgtRest,m=nVar,simplify=FALSE)
        #print(varCombs_nVar)
        nVarCombs <- length(varCombs_nVar) #Number of combinations
        #print(nVarCombs)
        sapply(1:nVarCombs,function(nComb){#Loop over variable combinations
          if (stopInd==0){
            log_debug("stopInd==0")
            ctrlVars <- c(crimeVarsWgtAll,varCombs_nVar[[nComb]])
            print(paste0("Combination ",nComb,"/",nVarCombs))
            #print(varCombs_nVar)
            print(ctrlVars)
            
            total_temp <- srs_control_totals_temp_state %>%
              subset(wgtGpState==j) %>%
              select(all_of(paste0("sum_",ctrlVars))) %>%
              as.numeric()
            #print(total_temp)
            #Update (28OCT2021): Running invisibly (no messages)
            #Update (04NOV2021): Adding suppressWarnings() 
            #suppressWarnings(capture.output(
            wgts_temp <- gencalib(Xs=select(SF_temp,all_of(ctrlVars)),
                                  Zs=select(SF_temp,all_of(ctrlVars)),
                                  #d=rep(1,nrow(SF_temp)),
                                  d=pull(SF_temp,baseWgt),
                                  total=total_temp,
                                  method="logit",
                                  #bounds=c(low=1,1e6),
                                  bounds=c(pull(SF_temp,lowBound) %>% unique(),maxAdj),#1e6),
                                  max_iter=maxIt,#1000,#10000
                                  C=1)#))
            
            #Update (27AUG2021): Ensure model converges AND calibration totals can be hit
            if (is.null(wgts_temp)){
              log_debug("No convergence")
              wgts_temp <- matrix(nrow=nrow(SF_temp),ncol=1) %>% as.data.frame() %>%
                mutate(!!paste0("StateWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb) := rep(NA,nrow(SF_temp))) %>%
                select(paste0("StateWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb))
            } else {
              #Update (29OCT2021): Run calibration check silently
              capture.output(test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                                      #d=rep(1,nrow(SF_temp)),
                                                      d=pull(SF_temp,baseWgt),
                                                      total=total_temp,
                                                      g=wgts_temp,
                                                      EPS=ifelse(any(total_temp==0),1,1e-6)))#EPS=1))
              if (test$result==TRUE){
                log_debug("Success!")
                stopInd <- 1
                list2env(list("stopInd"=stopInd),tempEnv) #Update stopInd in function environment
                wgts_temp <- wgts_temp %>%
                  data.frame() %>%
                  dplyr::mutate(!!paste0("StateWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb) := .) %>%
                  select(paste0("StateWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb))
              } else {
                log_debug("Convergence, calibration failed")
                wgts_temp <- matrix(nrow=nrow(SF_temp),ncol=1) %>% as.data.frame() %>%
                  mutate(!!paste0("StateWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb) := rep(NA,nrow(SF_temp))) %>%
                  select(paste0("StateWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb))
              }
            }
          } else {
            #Skipping bc stopInd==1
            wgts_temp <- matrix(nrow=nrow(SF_temp),ncol=1) %>% as.data.frame() %>%
              mutate(!!paste0("StateWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb) := rep(NA,nrow(SF_temp))) %>%
              select(paste0("StateWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb))
          }
          return(wgts_temp)
          
        },simplify=FALSE) %>%
          bind_cols()
        
      },simplify=FALSE) %>%
        {bind_cols(SF_temp,.)}
      #In case even the crimeVarsWgtAll model fails...
      #10Aug2025: no longer using gencalib() in this situation... instead, 
      #             just using the inverse crime coverage...
      #           because creating the g-weights here, we need to use 1/(b*r),
      #             where b is the base weight and r is the crime coverage
      if (stopInd==0){
        log_debug(paste0("State: ",i,". Weight group: ",j,". n SRS Variables: ",1))
        
        log_debug("stopInd==0")
        
        log_debug("Setting g-weight equal to 1/(r*b),
                  where r is the crime coverage and b is the base weight")
        
        ratio_temp <- ratio %>% 
          filter(STATE_NAME==i & wgtGpState==j) %>%
          pull(ratio_totcrime_imp)
        
        wgts_temp <- SF_temp %>%
          mutate(!!paste0("StateWgt_nVar",1,"_comb",1) := 1/(ratio_temp*baseWgt)) %>%
          select(paste0("StateWgt_nVar",1,"_comb",1))
      } else {
        #Skipping bc stopInd==1
        wgts_temp <- matrix(nrow=nrow(SF_temp),ncol=1) %>% as.data.frame() %>%
          mutate(!!paste0("StateWgt_nVar",1,"_comb",1) := rep(NA,nrow(SF_temp))) %>%
          select(paste0("StateWgt_nVar",1,"_comb",1))
      }
      out_temp <- bind_cols(out_temp,
                            wgts_temp)
      
    } else {
      log_debug("No LEAs in state X weighting group")
      return(NULL)
    }
  },simplify=FALSE) %>%
    bind_rows()
  #If cell not empty, merge on SF
  #02May2024: getting errors when merging in certain states... modifying merge (only keep certain variables from SF2_wgts_state)
  if (nrow(SF2_wgts_state)>0){
    SF2_wgts_state <- SF2_wgts_state %>%
      select(ORI,matches("^StateWgt_")) %>% #01May2024: added today
      #left_join(SF_temp_state,by=colnames(SF_temp_state))
      left_join(SF_temp_state,by=c("ORI"))
  }
  
  #print(out_temp)
},simplify=FALSE) %>%
  bind_rows()


#####
#Combination summaries

#Update (28OCT2021): Previously was copy-pasting code chunks by number of variables in model. Create function that will streamline
combs_table_state_gps <- function(indat,crimeVarsWgt,crimeVarsWgtAll,crimeVarsWgtRest,inWgtGps,wgtVar,wgtGpVar,wgtGpDescVar,suffix="",nInWgtGps=length(inWgtGps),nVars=length(crimeVarsWgtRest)){
  log_debug("Running function combs_table_state_gps")
  inGps <- expand.grid(STATE_NAME=stateGps2,wgtGp=inWgtGps)
  colnames(inGps) <- c("STATE_NAME",wgtGpVar)
  nInGps <- nrow(inGps)
  out <- sapply(nVars:0,function(temp.nVar){ #Loop over number of variables from nVars down to 1
    #print("temp.nVar")
    #print(temp.nVar)
    #Combinations of crimeVarsWgt of size i
    temp.combs <- combn(crimeVarsWgtRest,m=temp.nVar,simplify=FALSE)
    #print("length(temp.combs)")
    #print(length(temp.combs))
    temp.dat <- matrix(ncol=nVars+length(crimeVarsWgtAll),
                       nrow=length(temp.combs)) %>%
      data.frame()
    colnames(temp.dat) <- crimeVarsWgt
    temp.dat <- temp.dat %>%
      mutate(nVar=temp.nVar+length(crimeVarsWgtAll),
             comb=1:length(temp.combs)) %>%
      select(nVar,comb,everything()) %>%
      mutate(across(crimeVarsWgtAll,~"X",.names="{.col}"))
    #Create table
    temp.table <- sapply(1:length(temp.combs),function(i){#Loop over each combination in temp.combs
      temp.out <- temp.dat[i,]
      temp.env <- environment()
      sapply(crimeVarsWgtRest,function(temp.var){
        temp.out <- temp.out %>%
          mutate(!! temp.var:=case_when(temp.var %in% temp.combs[[i]] ~ "X",
                                        TRUE ~ ""))
        list2env(list("temp.out"=temp.out),temp.env)
        return(NULL)
      })
      
      #Stack row once per state X weighting group
      
      temp.out <- temp.out[rep(seq_len(nrow(temp.out)), each = nInGps), ]  %>%
        bind_cols(inGps) %>%
        mutate(!!wgtGpDescVar:=factor(eval(as.symbol(wgtGpVar)),levels=wgtGpsState3,labels=wgtGpStateDescs3))
      #Note (09Jan2023): Removing totcrime_imp requirement
      temp.converge <- indat %>%
        subset(resp_ind_m3==1) %>%
        mutate(converge=!is.na(eval(as.symbol(paste0(wgtVar,"_nVar",temp.nVar+length(crimeVarsWgtAll),"_comb",i))))) %>%
        select(STATE_NAME,all_of(wgtGpVar),all_of(wgtGpDescVar),converge) %>%
        group_by_at(.vars=c("STATE_NAME",wgtGpVar,wgtGpDescVar)) %>%
        dplyr::summarize(converge=any(converge),
                         .groups="drop") %>%
        select(STATE_NAME,all_of(wgtGpVar),all_of(wgtGpDescVar),converge)
      
      temp.out <- temp.out %>% left_join(temp.converge,by=c("STATE_NAME",wgtGpVar,wgtGpDescVar))
    },simplify=FALSE) %>%
      bind_rows()
    return(temp.table)
  },simplify=FALSE)
  
  names(out) <- paste0("comb",(nVars+length(crimeVarsWgtAll)):3,"_table_",suffix)
  list2env(out,envir=.GlobalEnv)
  
  #Repeat for single SRS variable model
  temp.dat <- matrix(ncol=nVars+length(crimeVarsWgtAll),
                     nrow=1) %>%
    data.frame()
  colnames(temp.dat) <- crimeVarsWgt
  temp.dat <- temp.dat %>%
    mutate(nVar=1,
           comb=1) %>%
    select(nVar,comb,everything()) %>%
    mutate(across(crimeVarsWgtAll[1],~"X",.names="{.col}"),
           across(crimeVarsWgtAll[2:length(crimeVarsWgtAll)],~"",.names="{.col}"),
           across(crimeVarsWgtRest,~"",.names="{.col}"))
  #Create table
  temp.out <- temp.dat[1,]
  temp.env <- environment()
  
  #Stack row once per state X weighting group
  
  temp.out <- temp.out[rep(seq_len(nrow(temp.out)), each = nInGps), ]  %>%
    bind_cols(inGps) %>%
    mutate(!!wgtGpDescVar:=factor(eval(as.symbol(wgtGpVar)),levels=wgtGpsState3,labels=wgtGpStateDescs3))
  print(temp.out)
  #Note (09Jan2023): Removing totcrime_imp requirement
  temp.converge <- indat %>%
    subset(resp_ind_m3==1) %>%
    mutate(converge=!is.na(eval(as.symbol(paste0(wgtVar,"_nVar",1,"_comb",1))))) %>%
    select(STATE_NAME,all_of(wgtGpVar),all_of(wgtGpDescVar),converge) %>%
    group_by_at(.vars=c("STATE_NAME",wgtGpVar,wgtGpDescVar)) %>%
    dplyr::summarize(converge=any(converge),
                     .groups="drop") %>%
    select(STATE_NAME,all_of(wgtGpVar),all_of(wgtGpDescVar),converge)
  
  out <- temp.out %>% left_join(temp.converge,by=c("STATE_NAME",wgtGpVar,wgtGpDescVar)) %>%
    list()
  colnames(out) %>% print()
  names(out) <- paste0("comb",1,"_table_",suffix)
  list2env(out,envir=.GlobalEnv)
  return(NULL)
}

combs_table_state_gps(indat=SF2_wgts2_test,crimeVarsWgt,crimeVarsWgtAll,crimeVarsWgtRest,inWgtGps=wgtGpsState3,
                      wgtVar="StateWgt",wgtGpVar="wgtGpState",wgtGpDescVar="wgtGpStateDesc",
                      suffix="test")




#Update (20Mar2023): Some groups don't have a model that converges - for now, create row representing 0 variables (N/n)
#Update (05May2023): Adding back in
#Update (10Aug2025): Excluding 0 variable code (this is now done in the 
#                      1-variable case)
# comb0_table_test <- SF2_wgts2_test %>% 
#   select(STATE_NAME,wgtGpState,wgtGpStateDesc) %>% 
#   subset(duplicated(.)==FALSE) %>% 
#   mutate(nVar=0,
#          comb=1,
#          converge=TRUE)
#Note (08May2023): Since StateWgt_nVarX_combY is g-weight, need to divide by baseWgt
# SF2_wgts2_test <- SF2_wgts2_test %>%
#   mutate(StateWgt_nVar0_comb1=ifelse(resp_ind_m3==1 & rowSums(!is.na(select(.,matches("StateWgt_nVar\\d"))),na.rm=TRUE)==0,
#                                      1/(ratio_totcrime_imp*baseWgt),
#                                      NA_real_))


#Stack all tables together
combAll_table <- bind_rows(comb10_table_test,
                           comb9_table_test,
                           comb8_table_test,
                           comb7_table_test,
                           comb6_table_test,
                           comb5_table_test,
                           comb4_table_test,
                           comb3_table_test,
                           #comb2_table_test,
                           comb1_table_test#,
                           #comb0_table_test
) %>%
  arrange(STATE_NAME,wgtGpState,wgtGpStateDesc,-converge,-nVar,comb) %>%
  group_by(STATE_NAME,wgtGpState,wgtGpStateDesc) %>%
  mutate(Select=ifelse(row_number(wgtGpState)==1 & converge==TRUE,"X","")) %>%
  ungroup() %>%
  arrange(STATE_NAME,wgtGpState,wgtGpStateDesc,-nVar,comb) %>%
  mutate(Variables=apply(.,FUN=function(i){
    c(ifelse(i["totcrime_imp"]=="X","totcrime_imp",""),
      ifelse(i["totcrime_violent_imp"]=="X","totcrime_violent_imp",""),
      ifelse(i["totcrime_property_imp"]=="X","totcrime_property_imp",""),
      ifelse(i["totcrime_murder_imp"]=="X","totcrime_murder_imp",""),
      ifelse(i["totcrime_rape_imp"]=="X","totcrime_rape_imp",""),
      ifelse(i["totcrime_aggAssault_imp"]=="X","totcrime_aggAssault_imp",""),
      ifelse(i["totcrime_burglary_imp"]=="X","totcrime_burglary_imp",""),
      ifelse(i["totcrime_rob_imp"]=="X","totcrime_rob_imp",""),
      ifelse(i["totcrime_larceny_imp"]=="X","totcrime_larceny_imp",""),
      ifelse(i["totcrime_vhcTheft_imp"]=="X","totcrime_vhcTheft_imp","")) %>%
      subset(.!="") %>%
      str_flatten(collapse=",")},MARGIN=1))%>%
  select(STATE_NAME,wgtGpState,wgtGpStateDesc,nVar,comb,
         totcrime_imp,totcrime_violent_imp,
         totcrime_property_imp,totcrime_murder_imp,
         totcrime_rape_imp,
         totcrime_aggAssault_imp,
         totcrime_burglary_imp,totcrime_rob_imp,
         totcrime_larceny_imp,totcrime_vhcTheft_imp,Variables,everything()) %>%
  left_join(stateCrosses2)




#Update (14Jun2022): Switching Excel output functions (fixing overwrite bug)
#combAll_table %>%
#  list("All Combinations"=.) %>%
#  write.xlsx(file=paste0(output_weighting_data_folder,"SRS_Variable_Combination_Convergence_by_State_X_Weighting_Group_Automatic.xlsx"))
log_debug("Writing excel workbook SRS_Variable_Combination_Convergence_by_State_X_Weighting_Group_AltCombs_Automatic.xlsx")
workbook <- paste0(output_weighting_data_folder,
                   "SRS_Variable_Combination_Convergence_by_State_X_Weighting_Group_AltCombs_Automatic.xlsx")
wb <- createWorkbook()
addWorksheet(wb,"All Combinations")
writeData(wb,"All Combinations",combAll_table)
saveWorkbook(wb,workbook,overwrite=TRUE) 


stateCW <- data.frame(STATE_NAME=c(state.name,"District of Columbia") %>% sort(),STATE_CODE=1:51)

SF2 <- SF2 %>%
  arrange(ORI) %>%
  left_join(stateCrosses2) %>%
  select(-matches("^(STATE_CODE|totcrime_agg_rob_imp)$")) %>%
  inner_join(stateCW,by=c("STATE_NAME")) %>%
  mutate(wgtGpState2=stateCrossNum,
         totcrime_agg_rob_imp=0)

#choosing best model that converges
ctrlVars <- combAll_table %>% subset(Select=="X")

ctrlVars %>% 
  group_by(nVar) %>% 
  dplyr::summarize(n=n()) %>% 
  DT::datatable()
ctrlVars %>% 
  dplyr::summarize(across(matches("totcrime"),
                          ~sum(.x=="X",na.rm=TRUE))) %>% 
  DT::datatable()
ctrlVars %>% 
  group_by(STATE_NAME) %>% 
  dplyr::summarize(n=n(),
                   nVar10=sum(nVar==10),
                   nVar9=sum(nVar==9),
                   nVar8=sum(nVar==8),
                   nVar7=sum(nVar==7),
                   nVar6=sum(nVar==6),
                   nVar5=sum(nVar==5),
                   nVar4=sum(nVar==4),
                   nVar3=sum(nVar==3)) %>% 
  DT::datatable()
#01May2024: accounting for addition of self-representing weighting group
if (nrow(ctrlVars)==SF2 %>% select(STATE_NAME,wgtGpState) %>% subset(duplicated(.)==FALSE) %>% nrow()){
  
  #capture.output({
  SF2_wgts2 <- sapply(stateGps2,function(i){#Loop over weight groupings - just gp 1 for test
    print("##############################")
    print(paste0("State: ",i))
    SF_state <- SF2 %>%
      subset(STATE_NAME==i) #%>%
    #select(-matches("V\\d+_\\w"))
    #Note (10Jan2023): Removing totcrime_imp requirement
    SF_temp_state <- SF_state %>%
      subset(resp_ind_m3==1)
    #temp_state_code <- SF2 %>% subset(STATE_NAME==i) %>% getElement("STATE_CODE") %>% unique()
    temp_wgtGp1_code <- ctrlVars %>% subset(STATE_NAME==i & wgtGpState==1) %>% pull(stateCrossNum) %>% unique()
    temp_wgtGp2_code <- ctrlVars %>% subset(STATE_NAME==i & wgtGpState==2) %>% pull(stateCrossNum) %>% unique()
    temp_wgtGp3_code <- ctrlVars %>% subset(STATE_NAME==i & wgtGpState==3) %>% pull(stateCrossNum) %>% unique()
    temp_wgtGp4_code <- ctrlVars %>% subset(STATE_NAME==i & wgtGpState==4) %>% pull(stateCrossNum) %>% unique()
    temp_wgtGp5_code <- ctrlVars %>% subset(STATE_NAME==i & wgtGpState==5) %>% pull(stateCrossNum) %>% unique()
    temp_wgtGp6_code <- ctrlVars %>% subset(STATE_NAME==i & wgtGpState==6) %>% pull(stateCrossNum) %>% unique()
    temp_wgtGp7_code <- ctrlVars %>% subset(STATE_NAME==i & wgtGpState==7) %>% pull(stateCrossNum) %>% unique()
    temp_wgtGp8_code <- ctrlVars %>% subset(STATE_NAME==i & wgtGpState==8) %>% pull(stateCrossNum) %>% unique()
    temp_wgtGp9_code <- ctrlVars %>% subset(STATE_NAME==i & wgtGpState==9) %>% pull(stateCrossNum) %>% unique()
    temp_wgtGp10_code <- ctrlVars %>% subset(STATE_NAME==i & wgtGpState==10) %>% pull(stateCrossNum) %>% unique()
    temp_wgtGp11_code <- ctrlVars %>% subset(STATE_NAME==i & wgtGpState==11) %>% pull(stateCrossNum) %>% unique()
    temp_wgtGp12_code <- ctrlVars %>% subset(STATE_NAME==i & wgtGpState==12) %>% pull(stateCrossNum) %>% unique()
    
    #choosing best model that converges
    ctrlInds_state <- combAll_table %>% 
      subset(Select=="X" & STATE_NAME==i) %>% 
      rename_at(.vars=vars(matches("^totcrime")),.funs=~paste0(.x,"_ind")) %>%
      mutate(wgtGpState2=stateCrossNum) %>%
      select(wgtGpState2,matches("_ind")) %>%
      mutate(across(matches("_ind"),~ifelse(.x!="X",0,1))) %>%
      mutate(across(matches("_ind"),~ifelse(is.na(.x),0,.x))) %>%
      arrange(wgtGpState2) %>%
      mutate(totcrime_agg_rob_imp_ind=0) %>% #Creating dummy variable to retain same names as national & region
      select(wgtGpState2,
             totcrime_imp_ind,totcrime_violent_imp_ind,
             totcrime_property_imp_ind,totcrime_murder_imp_ind,
             totcrime_rape_imp_ind,totcrime_agg_rob_imp_ind,
             totcrime_aggAssault_imp_ind,totcrime_burglary_imp_ind,
             totcrime_rob_imp_ind,totcrime_larceny_imp_ind,
             totcrime_vhcTheft_imp_ind)
    
    
    ctrlIndsM_state <- ctrlInds_state %>%
      select(colnames(ctrlInds_state)) %>%
      select(-wgtGpState2) %>%
      as.matrix()
    
    ctrlTtlsM_state <- srs_state_control_totals %>%
      subset(STATE_NAME==i) %>%
      left_join(stateCrosses2) %>%
      mutate(wgtGpState2=stateCrossNum) %>%
      arrange(wgtGpState) %>%
      mutate(sum_totcrime_agg_rob_imp=0) %>% #Creating dummy variable to retain order
      select(sum_totcrime_imp,sum_totcrime_violent_imp,
             sum_totcrime_property_imp,sum_totcrime_murder_imp,
             sum_totcrime_rape_imp,sum_totcrime_agg_rob_imp,
             sum_totcrime_aggAssault_imp,sum_totcrime_burglary_imp,
             sum_totcrime_rob_imp,sum_totcrime_larceny_imp,
             sum_totcrime_vhcTheft_imp) %>%
      as.matrix()
    print("ncol(ctrlTtlsM_state):")
    print(ncol(ctrlTtlsM_state))
    print("ncol(ctrlIndsM_state):")
    print(ncol(ctrlIndsM_state))
    ctrlTtlsM2_state <- ctrlTtlsM_state*ctrlIndsM_state #Element-wise multiplication
    colnames(ctrlTtlsM2_state) <- LETTERS[1:ncol(ctrlTtlsM2_state)] #Would normally include 'sum_' before, but will add that later
    
    ctrlTtls2_state <- ctrlTtlsM2_state %>%
      data.frame() %>%
      mutate(wgtGpState2=ctrlInds_state %>% getElement("wgtGpState2")) %>%
      reshape2::melt(id.vars="wgtGpState2") %>%
      reshape2::dcast(formula=.~wgtGpState2+variable) %>%
      select(-.) #Drop dummy variable
    colnames(ctrlTtls2_state) <- paste0("sum_V",colnames(ctrlTtls2_state))
    #print("colnames(ctrlTtls2_state):")
    #print(colnames(ctrlTtls2_state))
    
    colnames(ctrlTtls2_state) <- colnames(ctrlTtls2_state) %>% str_replace("^(\\w)$","sum_\\1")
    
    #Control variables
    #Note (10Jan2023): Removing totcrime_imp requirement
    ctrlIndsM_state <- ctrlInds_state %>%
      inner_join(SF_state) %>%
      subset(STATE_NAME==i & resp_ind_m3==1) %>%
      arrange(ORI) %>%
      select(colnames(ctrlInds_state)) %>%
      select(-wgtGpState2) %>%
      as.matrix()
    #Note (10Jan2023): Removing totcrime_imp requirement
    ctrlVarsM_state <- SF2%>%
      subset(STATE_NAME==i & resp_ind_m3==1) %>%
      arrange(ORI) %>%
      select(totcrime_imp,totcrime_violent_imp,totcrime_property_imp,
             totcrime_murder_imp,
             totcrime_rape_imp,totcrime_agg_rob_imp,
             totcrime_aggAssault_imp,totcrime_burglary_imp,
             totcrime_rob_imp,totcrime_larceny_imp,
             totcrime_vhcTheft_imp) %>%
      as.matrix()
    
    print("ncol(ctrlVarsM_state):")
    print(ncol(ctrlVarsM_state))
    print("ncol(ctrlIndsM_state):")
    print(ncol(ctrlIndsM_state))
    print("nrow(ctrlVarsM_state):")
    print(nrow(ctrlVarsM_state))
    print("nrow(ctrlIndsM_state):")
    print(nrow(ctrlIndsM_state))
    ctrlVarsM2_state <- ctrlVarsM_state*ctrlIndsM_state
    colnames(ctrlVarsM2_state) <- LETTERS[1:ncol(ctrlVarsM2_state)]
    
    #print("ctrVars2_state")
    ctrlVars2_state <- ctrlVarsM2_state %>%
      data.frame() %>%
      #Note (10Jan2023): Removing totcrime_imp requirement
      mutate(ORI=SF_state %>% arrange(ORI) %>% subset(STATE_NAME==i & resp_ind_m3==1) %>% getElement("ORI"),
             wgtGpState2=SF_state %>% arrange(ORI) %>% subset(STATE_NAME==i & resp_ind_m3==1) %>% getElement("wgtGpState2"))
    
    #Note (22Jun2023): Only create if they exist
    if (length(temp_wgtGp1_code)==1){
      ctrlVars2_state <- ctrlVars2_state %>%
        mutate(across(matches("^\\w{1}$"),
                      .fns=~.x*ifelse(wgtGpState2==temp_wgtGp1_code,1,0),
                      .names=paste0("V",temp_wgtGp1_code,"_{col}")))
    }
    if (length(temp_wgtGp2_code)==1){
      ctrlVars2_state <- ctrlVars2_state %>%
        mutate(across(matches("^\\w{1}$"),
                      .fns=~.x*ifelse(wgtGpState2==temp_wgtGp2_code,1,0),
                      .names=paste0("V",temp_wgtGp2_code,"_{col}")))
    }
    if (length(temp_wgtGp3_code)==1){ 
      ctrlVars2_state <- ctrlVars2_state %>%
        mutate(across(matches("^\\w{1}$"),
                      .fns=~.x*ifelse(wgtGpState2==temp_wgtGp3_code,1,0),
                      .names=paste0("V",temp_wgtGp3_code,"_{col}")))
    }
    if (length(temp_wgtGp4_code)==1){ 
      ctrlVars2_state <- ctrlVars2_state %>%
        mutate(across(matches("^\\w{1}$"),
                      .fns=~.x*ifelse(wgtGpState2==temp_wgtGp4_code,1,0),
                      .names=paste0("V",temp_wgtGp4_code,"_{col}")))
    }
    if (length(temp_wgtGp5_code)==1){ 
      ctrlVars2_state <- ctrlVars2_state %>%
        mutate(across(matches("^\\w{1}$"),
                      .fns=~.x*ifelse(wgtGpState2==temp_wgtGp5_code,1,0),
                      .names=paste0("V",temp_wgtGp5_code,"_{col}")))
    }
    if (length(temp_wgtGp6_code)==1){ 
      ctrlVars2_state <- ctrlVars2_state %>%
        mutate(across(matches("^\\w{1}$"),
                      .fns=~.x*ifelse(wgtGpState2==temp_wgtGp6_code,1,0),
                      .names=paste0("V",temp_wgtGp6_code,"_{col}")))
    }
    if (length(temp_wgtGp7_code)==1){ 
      ctrlVars2_state <- ctrlVars2_state %>%
        mutate(across(matches("^\\w{1}$"),
                      .fns=~.x*ifelse(wgtGpState2==temp_wgtGp7_code,1,0),
                      .names=paste0("V",temp_wgtGp7_code,"_{col}")))
    }
    if (length(temp_wgtGp8_code)==1){ 
      ctrlVars2_state <- ctrlVars2_state %>%
        mutate(across(matches("^\\w{1}$"),
                      .fns=~.x*ifelse(wgtGpState2==temp_wgtGp8_code,1,0),
                      .names=paste0("V",temp_wgtGp8_code,"_{col}")))
    }
    if (length(temp_wgtGp9_code)==1){ 
      ctrlVars2_state <- ctrlVars2_state %>%
        mutate(across(matches("^\\w{1}$"),
                      .fns=~.x*ifelse(wgtGpState2==temp_wgtGp9_code,1,0),
                      .names=paste0("V",temp_wgtGp9_code,"_{col}")))
    } 
    if (length(temp_wgtGp10_code)==1){ 
      ctrlVars2_state <- ctrlVars2_state %>%
        mutate(across(matches("^\\w{1}$"),
                      .fns=~.x*ifelse(wgtGpState2==temp_wgtGp10_code,1,0),
                      .names=paste0("V",temp_wgtGp10_code,"_{col}")))
    }
    if (length(temp_wgtGp11_code)==1){ 
      ctrlVars2_state <- ctrlVars2_state %>%
        mutate(across(matches("^\\w{1}$"),
                      .fns=~.x*ifelse(wgtGpState2==temp_wgtGp11_code,1,0),
                      .names=paste0("V",temp_wgtGp11_code,"_{col}")))
    }
    if (length(temp_wgtGp12_code)==1){ 
      ctrlVars2_state <- ctrlVars2_state %>%
        mutate(across(matches("^\\w{1}$"),
                      .fns=~.x*ifelse(wgtGpState2==temp_wgtGp12_code,1,0),
                      .names=paste0("V",temp_wgtGp12_code,"_{col}")))
    }
    
    
    #Add on the new control totals/variables
    SF_state <- SF_state %>%
      full_join(ctrlVars2_state) %>%
      #select(-matches("^sum_\\w+_imp$")) %>%
      #full_join(ctrlTtls2) %>%
      arrange(ORI)
    #Note (10Jan2023): Removing totcrime_imp requirement
    SF_temp <- SF_state %>%
      subset(resp_ind_m3==1)
    
    #21Mar2023: adding requirement that columns are in ctrlTtls2_state
    temp.ctrlVars <- colnames(ctrlVars2_state) %>% str_subset("^V\\d+_\\w$") %>% subset(. %in% (colnames(ctrlTtls2_state) %>% str_remove("sum_")))
    #Update (28OCT2021): Comment out print statement
    #print(temp.ctrlVars)
    total_temp <- ctrlTtls2_state %>%
      select(all_of(paste0("sum_",temp.ctrlVars))) %>%
      as.numeric()
    #names(total_temp) <- NULL
    vars_temp <- SF_temp %>%
      select(all_of(temp.ctrlVars)) 
    
    ratio_state <- ratio %>% subset(STATE_NAME==i)
    #names(vars_temp) <- NULL
    #Update (10Oct2022): Don't redo calibration, juse use weights from earlier
    #print("gencalib(Xs=select(SF_temp,all_of(temp.ctrlVars)), ...:")
    # SF_temp_wgts2 <- gencalib(Xs=vars_temp,
    #                       Zs=vars_temp,
    #                       #d=rep(1,nrow(SF_temp)),
    #                       d=rep(ratio_state$baseWgt,nrow(SF_temp)),
    #                       total=total_temp,
    #                       method="logit",
    #                       #bounds=c(low=1,1e6),
    #                       bounds=c(low=ratio_state$lowBound,maxWgt/ratio_state$baseWgt),#1e6),
    #                       max_iter=5*maxIt,#10000
    #                       C=1,
    #                       description=TRUE) %>%
    #   data.frame(gWgt=.) %>%
    #   mutate(StateWgt=gWgt*ratio_state$baseWgt) %>%
    #   {bind_cols(SF_temp,.)} %>%
    #   full_join(SF_state,by=colnames(SF_state))
    #Note (10Jan2023): Removing totcrime_imp requirement
    SF_temp_wgts2 <- SF2_wgts2_test %>%
      subset(resp_ind_m3==1 & STATE_NAME==i) %>%
      mutate(gWgt=select(.,matches("StateWgt_nVar\\d")) %>% rowMeans(na.rm=TRUE)) %>%
      mutate(StateWgt=gWgt*baseWgt) %>%
      select(ORI,gWgt,StateWgt) %>%
      right_join(SF_temp)
    #print("SF_temp_wgts2:")
    #print(SF_temp_wgts2)
    #print("select(SF_temp_wgts2,all_of(temp.ctrlVars)) %>% as.matrix():")
    #print(select(SF_temp_wgts2,all_of(temp.ctrlVars)) %>% as.matrix())
    #print("rep(ratio_state$baseWgt,nrow(SF_temp_wgts2)):")
    #print(rep(ratio_state$baseWgt,nrow(SF_temp_wgts2)))
    #print("temp.ctrlVars:")
    #print(temp.ctrlVars)
    #print("total_temp:")
    #print(total_temp)
    #print("SF_temp_wgts2$gWgt:")
    #print(SF_temp_wgts2$gWgt)
    print("Check calibration on full model")
    checkcalibration(Xs=select(SF_temp_wgts2,all_of(temp.ctrlVars)) %>% as.matrix(),
                     d=pull(SF_temp_wgts2,baseWgt),
                     total=total_temp,
                     g=SF_temp_wgts2$gWgt,
                     EPS=ifelse(any(total_temp==0),1,1e-6)) %>% #EPS=1) %>%
      print()
    temp.wgtGps <- srs_state_control_totals %>%
      subset(STATE_NAME==i) %>%
      pull(wgtGpState)
    SF2_wgts_state <- sapply(temp.wgtGps,function(j){#Loop over weight groupings
      print("##############")
      print(paste0("State: ",i,". Weight group: ",j))
      #Take weighting group subset within state subset
      #Note (10Jan2023): Removing totcrime_imp requirement
      SF_temp <- SF_temp_wgts2 %>%
        subset(wgtGpState==j & resp_ind_m3==1)
      if (j==1){
        temp_wgtGp_code <- temp_wgtGp1_code
      } else if (j==2){
        temp_wgtGp_code <- temp_wgtGp2_code
      } else if (j==3){
        temp_wgtGp_code <- temp_wgtGp3_code
      } else if (j==4){
        temp_wgtGp_code <- temp_wgtGp4_code
      } else if (j==5){
        temp_wgtGp_code <- temp_wgtGp5_code
      } else if (j==6){
        temp_wgtGp_code <- temp_wgtGp6_code
      } else if (j==7){
        temp_wgtGp_code <- temp_wgtGp7_code
      } else if (j==8){
        temp_wgtGp_code <- temp_wgtGp8_code
      } else if (j==9){
        temp_wgtGp_code <- temp_wgtGp9_code
      } else if (j==10){
        temp_wgtGp_code <- temp_wgtGp10_code
      } else if (j==11){
        temp_wgtGp_code <- temp_wgtGp11_code
      } else if (j==12){
        temp_wgtGp_code <- temp_wgtGp12_code
      }
      if (nrow(SF_temp)>0){
        
        temp.ctrlVars <- colnames(SF_temp) %>% str_subset(paste0("^V",temp_wgtGp_code,"_\\w$"))
        
        
        total_temp_state <- ctrlTtls2_state %>%
          select(all_of(paste0("sum_",temp.ctrlVars))) %>%
          as.numeric()
        print(total_temp_state)
        out_temp <- SF_temp
        
        #Update (20AUG2021): Adding requested checks
        #Update (05Jul2022): Switch to table format (1 row per weight group) - commenting out old cold
        #Update (16May2024): Adding min and max
        
        # #Check calibration
        # print("checkcalibration(Xs=select(SF_temp,all_of(temp.ctrlVars)), ...:")
        # checkcalibration(Xs=select(SF_temp,all_of(temp.ctrlVars)),
        #                  d=rep(1,nrow(SF_temp)),
        #                  total=total_temp,
        #                  g=out_temp$StateWgt,
        #                  EPS=1) %>%
        #   print()
        # #Weight checks - summary, UWE, etc.
        # print("Distribution of weights:")
        # describe(out_temp$StateWgt) %>%
        #   print()
        # print("Number of missing weights:")
        # sum(is.na(out_temp$StateWgt))%>%
        #   print()
        # print("Number of weights equal to 1:")
        # sum(out_temp$StateWgt == 1, na.rm=TRUE) %>%
        #   print()
        # print("Number of weights greater than 1:")
        # sum(out_temp$StateWgt > 1, na.rm=TRUE) %>%
        #   print()
        # print("Number of weights less than 1:")
        # sum(out_temp$StateWgt < 1, na.rm=TRUE) %>%
        #   print()
        # print("Number of weights greater than 100:")
        # sum(out_temp$StateWgt > 100, na.rm=TRUE) %>%
        #   print()
        # print("UWE:")
        # UWE_StateWgt <- 1+var(out_temp$StateWgt,na.rm=TRUE)/(mean(out_temp$StateWgt,na.rm=TRUE)^2)
        # UWE_StateWgt %>%
        #   print()
        
        #Calibration worked (T/F)?
        temp.cal <- checkcalibration(Xs=select(SF_temp,all_of(temp.ctrlVars)) %>% as.matrix(),
                                     d=pull(SF_temp,baseWgt),
                                     total=total_temp_state,
                                     g=out_temp$gWgt,
                                     EPS=ifelse(any(total_temp_state==0),1,1e-6))%>%#EPS=1) %>%
          .$result
        temp.describe <- describe(out_temp$StateWgt)
        temp.quantiles <- quantile(out_temp$StateWgt,
                                   probs=c(0,0.05,0.1,0.25,0.5,0.75,0.9,0.95,1),
                                   na.rm=TRUE)
        #Note (26Jul2022): Adding n Eligible LEAs
        temp.nElig <- SF2 %>%
          subset(STATE_NAME==i & wgtGpState==j) %>%
          nrow()
        #Note (16May2024): rounding weight to 6 digits before checking if <1 (to avoid false flags)
        temp.nLT1 <- sum(round(out_temp$StateWgt,digits=6) < 1 & out_temp$StateWgt>0, na.rm=TRUE)
        #Note (29Jul2022): Switching from >100 to >20
        #temp.nGT100 <- sum(out_temp$StateWgt > 100, na.rm=TRUE)
        temp.nGT20 <- sum(out_temp$StateWgt > 20, na.rm=TRUE)
        temp.UWE <- 1+var(out_temp$StateWgt,na.rm=TRUE)/(mean(out_temp$StateWgt,na.rm=TRUE)^2)
        temp.out <- data.frame(stateGp=i,
                               wgtGpStateDesc=wgtGpStateDescs3[which(wgtGpsState3==j)],
                               calibrated=temp.cal,
                               #Note (26Jul2022): Changing counts - include n Eligible LEAs, n NIBRS LEAs, n NIBRS LEAs missing weights
                               #nOverall=as.numeric(temp.describe$counts["n"])+as.numeric(temp.describe$counts["missing"]),
                               nElig=temp.nElig,
                               nNIBRS=as.numeric(temp.describe$counts["n"])+as.numeric(temp.describe$counts["missing"]),
                               nMissing=as.numeric(temp.describe$counts["missing"]),
                               nLT1=temp.nLT1,
                               #nGT100=temp.nGT100,
                               nGT20=temp.nGT20,
                               UWE=sprintf(temp.UWE,fmt="%1.3f"),
                               Mean=sprintf(as.numeric(temp.describe$counts["Mean"]),fmt="%1.3f"),
                               Min=sprintf(temp.quantiles["0%"],fmt="%1.3f"),
                               pt05=sprintf(temp.quantiles["5%"],fmt="%1.3f"),
                               pt10=sprintf(temp.quantiles["10%"],fmt="%1.3f"),
                               pt25=sprintf(temp.quantiles["25%"],fmt="%1.3f"),
                               pt50=sprintf(temp.quantiles["50%"],fmt="%1.3f"),
                               pt75=sprintf(temp.quantiles["75%"],fmt="%1.3f"),
                               pt90=sprintf(temp.quantiles["90%"],fmt="%1.3f"),
                               pt95=sprintf(temp.quantiles["95%"],fmt="%1.3f"),
                               Max=sprintf(temp.quantiles["100%"],fmt="%1.3f"))
        colnames(temp.out) <- c("State","Weight Group","Calibrated",
                                "n Eligible LEAs","n NIBRS LEAs, Overall","n NIBRS LEAs, Missing Weight",
                                "n LT 1","n GT 20","UWE",#"n GT 100","UWE",
                                "Mean","Minimum","5th Pctl","10th Pctl","25th Pctl","50th Pctl",
                                "75th Pctl","90th Pctl","95th Pctl","Maximum")
        temp.out <- temp.out %>%
          list()
        names(temp.out) <- paste0("results_",i,"_",j)
        list2env(temp.out,.GlobalEnv)
        return(out_temp)
      } else {
        return(NULL)
      }
      
    },simplify=FALSE) %>%
      bind_rows()
    
    
  },simplify=FALSE) %>%
    bind_rows()%>%
    #01May2024: issues during merge... reducing number of variables to only ID variables plus new variables (gWgt, JDWgt, and calibration variables
    select(ORI,gWgt,StateWgt,matches("V\\d+_\\w")) %>%
    #full_join(SF2,by=colnames(SF2))
    full_join(SF2,by=c("ORI"))
  #},file=paste0(output_weighting_data_folder,'weights_state_checks.txt'))
  #Note (JDB 06Jul2022): Combine weight check results
  results_state <- #outer(paste0("results_",stateGps2,"_"),wgtGpsState,FUN=paste0) %>%
    #as.character() %>% 
    SF2 %>% select(STATE_NAME,wgtGpState) %>% subset(duplicated(.)==FALSE) %>% mutate(name=paste0("results_",STATE_NAME,"_",wgtGpState)) %>% pull(name) %>%
    mget(envir=.GlobalEnv) %>%
    bind_rows()
  
  
  
  
  ###############
  #Output
  #Note (12Apr2023): Stacking skipped crossings
  
  states_all <- SF %>%
    .$STATE_NAME %>%
    unique()
  
  states_all %>%
    data.frame(STATE_NAME=.) %>%
    write_dot_csv_logging(paste0(output_weighting_data_folder,'states_all.csv'),
                          row.names = FALSE)
  
  new_weights <- SF2_wgts2 %>%
    bind_rows(SF2_skips,SF2_skipSR)
  
  ### export for others to start writing functions to analyze bias, MSE, etc.
  new_weights[,c("ORI_universe","LEGACY_ORI","wgtGpState","wgtGpStateDesc","STATE_NAME",
                 #Update (27AUG2021): Add raw weight group variable
                 "wgtGpState_raw","wgtGpStateDesc_raw",
                 "StateWgt")] %>%
    #write.csv(paste0(output_weighting_data_folder,'weights_state.csv'),
    fwrite(paste0(output_weighting_data_folder,'weights_state.csv'),
           row.names = FALSE)
  
  #Update (26AUG2021): Add wgtGpState and wgtGpStateDesc to SF file from 02_Weights_Data_Setup
  # oldSF <- read_csv(paste0(input_weighting_data_folder,"SF_postN.csv"),
  #                   guess_max=1e6)%>%
  #   #Adding just in case already on file...
  #   select(-matches("wgtGpState"))
  calVars <- colnames(SF2_wgts2) %>%
    str_subset("^V\\d+_\\w") %>% #All calibration vars
    subset(. %in% (outer(paste0("V",stateCrosses$stateCrossNum,"_"),
                         paste0(c("A","B","C","D","E","F","G","H","I","J","K")),
                         paste0) %>% as.character()))
  calVarsRegEx <- str_flatten(calVars,collapse="|")
  oldSF <- fread(paste0(input_weighting_data_folder,"SF_postR.csv"))#%>%
  #Adding just in case already on file...
  #01May2024: commenting out this line
  #select(-matches(paste0("(wgtGpState|",calVars,")")))
  #19Jun2023: binding SF2 and SF2_skips in 1st left_join
  newSF <- oldSF %>%
    left_join(bind_rows(SF2,SF2_skips,SF2_skipSR) %>% 
                select(ORI_universe,wgtGpState,wgtGpStateDesc,
                       #Update (27AUG2021): Add raw weight group variable
                       wgtGpState_raw,wgtGpStateDesc_raw),
              by=c("ORI_universe")) %>%
    #Update (18Jan2023): adding new calibration variables
    left_join(SF2_wgts2 %>%
                select(ORI_universe,all_of(calVars)),
              by=c("ORI_universe"))
  
  #write_csv(newSF,file=paste0(output_weighting_data_folder,"SF_postS_cal.csv"))
  fwrite(newSF,file=paste0(output_weighting_data_folder,"SF_postS.csv"))
  
  #Note (JDB 06Jul2022): Export weight check results
  #write_csv(results_state,
  fwrite(results_state,
         file=paste0(output_weighting_data_folder,"weights_state_checks.csv"))
} else {
  stop("No calibration model converged for 1+ (state X weighting group) crossing")
}
log_info("Finished 03_Weights_Calibration_State_SRS_AltCombs.R\n\n")
