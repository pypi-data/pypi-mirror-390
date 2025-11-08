#This program is for testing variations of the MSA weights
#Specifically, this is based on 4 strata with SRS calibration

maxAdj <- 10 #Max adjustment factor
maxIt <- 1000 #Max iterations during variable selection
srK <- 30 #17May2024: K to use for self-representing agencies ... added today

### Purpose of program is to calibrate MSA weights by grouping (e.g., zero pop vs. nonzero pop LEAs)
### Author: JD Bunker
### Last updated: 29OCT2021
#Update (28OCT2021): Commenting out/removing unnecessary print statements and removing no longer needed commented-out code
#Update (29OCT2021): Continuing clean up efforts (commenting out / deleting commented-out code)
#Update (07OCT2022): Adding maxWgt and maxIt values for final weight
#Update (20JUN2025): Automatically handling assignments of metro divisions and 
#                      self-reporting agencies (previously, manually tracked).
#Update (11AUG2025): Removing use of gencalib() with only overall crime if 
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

log_info("Running 03_Weights_Calibration_MSA_SRS_AltCombs_Collapsed.R")

#Note (20Jun2023): Reading in new crossing worksheet
msaCrosses <- paste0(input_weighting_data_folder,"Geography_Crossings.xlsx") %>%
  read_xlsx(sheet="MSA") %>%
  rename(MSA_NAME_COUNTY=msaLvl,
         wgtGpMSA=msaWgtGp)

# read in SF data

SF <- paste0(input_weighting_data_folder,"SF_postJD_cal_srs_altcombs_col.csv") %>%
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
#Note (28Apr2023): Splitting into variables for all MSA X weighting groups vs. extra crime vars
crimeVarsWgtAll <- c("totcrime_imp",
                     "totcrime_violent_imp",
                     "totcrime_property_imp")
crimeVarsWgtRest <- c("totcrime_murder_imp",
                      "totcrime_rape_imp","totcrime_aggAssault_imp",
                      "totcrime_burglary_imp","totcrime_rob_imp",
                      "totcrime_larceny_imp","totcrime_vhcTheft_imp")
crimeVarsWgt <- c(crimeVarsWgtAll,crimeVarsWgtRest)

msaGps <- SF %>%
  pull(MSA_NAME_COUNTY) %>%
  unique()
nMSAGps <- msaGps %>%
  length()


#srs_MSA_control_totals <- SF %>%
#  group_by(MSA_NAME_COUNTY) %>%
#  dplyr::summarize(across(.cols=all_of(crimeVarsWgt),.fns=list("sum"=sum),.names="{.fn}_{.col}",na.rm=TRUE))


wgtGpMSADescs <-  c("Cities 1,000,000 or over",
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
  mutate(wgtGpMSA=case_when(POPULATION_GROUP_DESC=="Cities 1,000,000 or over" ~ 1,
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
         wgtGpMSADesc=factor(wgtGpMSA,levels=1:22,labels=wgtGpMSADescs)) %>%
  #Note (02May2024): Drop all calibration variables that already exist (e.g., FO and JD)
  select(-matches("^V\\d+_\\w"))

msaGps2 <- SF2 %>%
  pull(MSA_NAME_COUNTY) %>%
  unique()
nMSAGps2 <- msaGps2 %>%
  length()

wgtGpsMSA <- SF2 %>%
  pull(wgtGpMSA) %>%
  unique()
nWgtGpsMSA <- length(wgtGpsMSA)


#16May2024: implementing self-reporting treatment:
#>Count the number of nonreporters among (agency X county) records with >30x the MSA's mean crime count
#>If all (agency X county) records are reporters, isolate them into their own weighting group 
#>Then proceed with weighting as usual with the remaining agencies (e.g., exclude large (agency X county) records' crime counts with remaining (agency X county) records)  

srEligible <- SF2 %>%
  #Now, get mean for the MSA
  group_by(MSA_NAME_COUNTY) %>%
  mutate(mean_totcrime_imp_msa=mean(totcrime_imp),
         POP_ELIG=sum(POPULATION),
         POP_RESP=sum(POPULATION*resp_ind_m3),
         propCoverage=POP_RESP/POP_ELIG
  ) %>%
  ungroup() %>%
  subset(totcrime_imp>srK*mean_totcrime_imp_msa)
#Get list of MSAs where we'll implement self representing methodology
srMSAs <- srEligible %>% 
  group_by(MSA_NAME_COUNTY) %>% 
  dplyr::summarize(nSREligible=n(),
                   nSRReporter=sum(resp_ind_m3)) %>%
  subset(nSREligible==nSRReporter)
#Now, let's get a list of agency X county crossings that are going to be self-representing
srLEACounties <- srEligible %>%
  inner_join(srMSAs) %>%
  select(ORI,county) %>%
  unique() %>%
  arrange(ORI,county)


#Detect and perform any necessary collapsing (number of respondents in non-empty MSA X grouping is 0)
#Note (02May2024): we now need to incorporate metro division into the groups
#					In wgtGpsMSA2 and wgtGpMSADescs2 I will leave room for the collapsed (all agencies) strata,
#					But I won't actually assign agencies there until next time we update wgtGpsMSA2 and wgtGpMSADescs2
#Note (16May2024): Updating to reflect addition of the self-representing weighting group
#Note (20Jun2025): Automatically tracking lists of metro divisions
if (year >= 2022){
  mdList <- SF2 %>% 
    group_by(MSA_NAME_COUNTY,METRO_DIVISION_COUNTY) %>% 
    dplyr::summarize(n=n()) %>%
    group_by(MSA_NAME_COUNTY) %>% 
    mutate(nMD=n()) %>% 
    ungroup() %>%
    filter(nMD > 1) %>% 
    arrange(METRO_DIVISION_COUNTY) %>% 
    pull(METRO_DIVISION_COUNTY) 
  
  nMDs <- length(mdList)
  
  wgtGpsMSA2 <- 1:(3*(nMDs+1)+1)
  
  wgtGpMSADescs2 <- c("Not self-representing - Not Select Metro Division - Nonzero population agencies",
                      "Not self-representing - Not Select Metro Division - Zero population agencies",
                      "Not self-representing - Not Select Metro Division - All agencies",
                      expand.grid(str_c("Not self-representing - ",mdList," - "),
                                  c("Nonzero population agencies",
                                    "Zero population agencies",
                                    "All agencies")) %>%
                        arrange(Var1,Var2) %>%
                        mutate(string=str_c(Var1,Var2)) %>%
                        pull(string),
                      "Self-representing")
  #20Jun2025: this will help assign wgtGpMSA2 for cases in select metro divisions...
  mdCW <- SF2 %>%
    ungroup() %>%
    filter(METRO_DIVISION_COUNTY %in% mdList) %>%
    arrange(METRO_DIVISION_COUNTY) %>%
    select(METRO_DIVISION_COUNTY) %>%
    unique() %>%
    mutate(mdNum=row_number())
  SF2 <- SF2 %>%
    left_join(srLEACounties %>% 
                mutate(wgtGpMSA2=115)) %>%
    left_join(mdCW) %>%
    mutate(mdNum=ifelse(is.na(mdNum),0,mdNum)) %>%
    mutate(wgtGpMSA2=case_when(
      wgtGpMSA2==115 ~ 115, #16May2024: new Self-representing weighting group
      wgtGpMSA %in% 20:22 ~ mdNum*3+2,
      TRUE ~ mdNum*3+1),
      wgtGpMSADesc2=factor(wgtGpMSA2,levels=wgtGpsMSA2,labels=wgtGpMSADescs2))
}

#Note (12Mar2024): Incorporate revised version of metro division (only non missing for applicable metro divisions)
SF2 <- SF2 %>%
  mutate(METRO_DIVISION_COUNTY2=ifelse(METRO_DIVISION_COUNTY %in% mdList,METRO_DIVISION_COUNTY,"Not Applicable")) %>%
  rename(wgtGpMSA_raw=wgtGpMSA,
         wgtGpMSADesc_raw=wgtGpMSADesc) %>%
  rename(wgtGpMSA=wgtGpMSA2,
         wgtGpMSADesc=wgtGpMSADesc2)


#Set aside SR agencies...
SF2_skipSR <- SF2 %>%
  inner_join(srLEACounties) %>%
  mutate(MSAWgt=1)
#Exclude SR agencies from further processing...
SF2 <- SF2 %>%
  anti_join(srLEACounties)

#Get totals by weighting group
srs_MSA_control_totals <- SF2 %>%
  group_by(MSA_NAME_COUNTY,wgtGpMSA) %>%
  dplyr::summarize(across(all_of(crimeVarsWgt),.fns=list("sum"=sum),.names="{fn}_{col}",na.rm=TRUE),
                   .groups="drop")
#Get n NIBRS Reporters and n Eligible - used for base weights and lower bounds
#Note (12Apr2023): adding ratio for totcrime_imp - MSA X weighting groups with >=99% will skip weighting and be assigned weights of 1
ratio <- SF2 %>%
  group_by(MSA_NAME_COUNTY,METRO_DIVISION_COUNTY2,wgtGpMSA) %>%
  dplyr::summarize(n=sum(resp_ind_m3==1),
                   N=n(),
                   sum_totcrime_imp_NIBRS=sum(totcrime_imp*resp_ind_m3),
                   sum_totcrime_imp_all=sum(totcrime_imp),
                   ratio_totcrime_imp=sum_totcrime_imp_NIBRS/sum_totcrime_imp_all) %>%
  mutate(baseWgt=N/n,
         lowBound=n/N)

SF2 <- SF2 %>%
  select(-matches("sum_totcrime")) %>%
  inner_join(srs_MSA_control_totals) %>%
  select(-matches("^(n|N|baseWgt|lowBound)$")) %>%
  full_join(ratio,by=c("MSA_NAME_COUNTY","METRO_DIVISION_COUNTY2","wgtGpMSA"))


#Note (18May2023): Moving collapsing before skips


#Note (17May2023): collapse MSAs where 1+ weighting group has ratio_totcrime_imp<
#Note (02May2024): Also need to now worry about respecting metro divisions when collapsing
crossings_col <- ratio %>%
  subset(ratio_totcrime_imp<0.2) %>%
  select(MSA_NAME_COUNTY,METRO_DIVISION_COUNTY2) %>%
  unique() %>%
  mutate(collapse=TRUE)
SF2 <- SF2 %>%
  #anti_join(crossings_skips) %>%
  left_join(crossings_col) %>%
  mutate(collapse=ifelse(is.na(collapse),0,collapse)) %>%
  #mutate(wgtGpMSA=ifelse(collapse==TRUE,3,wgtGpMSA))
  mutate(wgtGpMSA=ifelse(collapse==TRUE,3*floor(wgtGpMSA/3)+3,wgtGpMSA))

#02May2024: no longer update weighting groups here
#wgtGpsMSA2 <- 1:3
#wgtGpMSADescs2 <- c("Nonzero population agencies",
#                    "Zero population agencies",
#                    "All agencies")

SF2 <- SF2 %>%
  mutate(wgtGpMSADesc=factor(wgtGpMSA,levels=wgtGpsMSA2,labels=wgtGpMSADescs2))

msaCrosses2 <- SF2 %>%
  select(MSA_NAME_COUNTY,wgtGpMSA) %>%
  unique() %>%
  inner_join(msaCrosses)

#Get totals by (collapsed) weighting group
srs_MSA_control_totals <- SF2 %>%
  group_by(MSA_NAME_COUNTY,wgtGpMSA) %>%
  dplyr::summarize(across(all_of(crimeVarsWgt),.fns=list("sum"=sum),.names="{fn}_{col}",na.rm=TRUE),
                   .groups="drop")

#Get n NIBRS Reporters and n Eligible - used for base weights and lower bounds
#Note (12Apr2023): adding ratio for totcrime_imp - MSA X weighting groups with >=99% will skip weighting and be assigned weights of 1
ratio <- SF2 %>%
  group_by(MSA_NAME_COUNTY,wgtGpMSA) %>%
  dplyr::summarize(n=sum(resp_ind_m3==1),
                   N=n(),
                   sum_totcrime_imp_NIBRS=sum(totcrime_imp*resp_ind_m3),
                   sum_totcrime_imp_all=sum(totcrime_imp),
                   ratio_totcrime_imp=sum_totcrime_imp_NIBRS/sum_totcrime_imp_all) %>%
  mutate(baseWgt=N/n,
         lowBound=n/N)
SF2 <- SF2 %>%
  select(-matches("sum_totcrime")) %>%
  left_join(srs_MSA_control_totals,by=c("MSA_NAME_COUNTY","wgtGpMSA")) %>%
  select(-matches("^(n|N|sum_totcrime_imp_NIBRS|sum_totcrime_imp_all|ratio_totcrime_imp|baseWgt|lowBound)$")) %>%
  left_join(ratio,by=c("MSA_NAME_COUNTY","wgtGpMSA")) 
#Note (12Apr2023): Setting aside MSA X weighting group crossings with >=99%
#Note (16May2023): Temporarily setting aside crossigns with 0 respondents
crossings_skips <- ratio %>%
  subset(ratio_totcrime_imp>=0.99) %>%
  select(MSA_NAME_COUNTY,wgtGpMSA)
#24May2023: also drop MSAs with 0 respondents
#29May2023: actually, drop if NIBRS reporters responsible for 0 crimes and eligible have >0 crimes
#30May2023: split out into whether all eligible have >0 or 0 crimes
crossings_skipsB <- ratio %>%
  subset(sum_totcrime_imp_NIBRS==0 & sum_totcrime_imp_all==0)
crossings_skipsC <- ratio %>%
  subset(sum_totcrime_imp_NIBRS==0 & sum_totcrime_imp_all>0)

SF2_skips <- SF2 %>%
  inner_join(crossings_skips) %>%
  #30May2023: adding ifelse() requirement
  mutate(MSAWgt=ifelse(resp_ind_m3==1,1,NA_real_))
SF2_skipsB <- SF2 %>%
  inner_join(crossings_skipsB) %>%
  mutate(MSAWgt=ifelse(resp_ind_m3==1,1,NA_real_))
SF2_skipsC <- SF2 %>%
  inner_join(crossings_skipsC) %>%
  mutate(MSAWgt=NA_real_)



#ratio <- ratio %>%
#  anti_join(crossings_skips)

SF2 <- SF2 %>%
  anti_join(crossings_skips,by=c("MSA_NAME_COUNTY","wgtGpMSA")) %>%
  anti_join(crossings_skipsB,by=c("MSA_NAME_COUNTY","wgtGpMSA")) %>%
  anti_join(crossings_skipsC,by=c("MSA_NAME_COUNTY","wgtGpMSA"))

#Get totals by weighting group
srs_MSA_control_totals <- SF2 %>%
  group_by(MSA_NAME_COUNTY,wgtGpMSA) %>%
  dplyr::summarize(across(all_of(crimeVarsWgt),.fns=list("sum"=sum),.names="{fn}_{col}",na.rm=TRUE),
                   .groups="drop")

msaGps2 <- SF2 %>%
  pull(MSA_NAME_COUNTY) %>%
  unique() %>%
  sort()

#Note (12Apr2023): Dropping skipped crossings from main file
#SF2 %>%
#  group_by(MSA_NAME_COUNTY,wgtGpMSA,wgtGpMSADesc) %>%
#  dplyr::summarize(N=n(),
#                   n=sum(resp_ind_m3)) %>%
#  DT::datatable()
#  
#stop()

#Update (28OCT2021): Reducing print statements
#Update (23MAR2022): Stop running after first successful convergence for weighting group
#Update (23MAR2022): Lowering max_iter from 10000 to 1000
#Update (21MAR2023): Reducing number of print and log statements
SF2_wgts2_test <- sapply(msaGps2,function(i){#Loop over weight groupings
  log_debug("Running function SF2_wgts2_test")
  log_debug("##################")
  log_debug(paste0("MSA: ",i))
  #Note (09Jan2023): Removing totcrime_imp requirement
  SF_temp_MSA <- SF2 %>%
    subset(MSA_NAME_COUNTY==i & resp_ind_m3==1)
  srs_control_totals_temp_MSA <- srs_MSA_control_totals %>%
    subset(MSA_NAME_COUNTY==i)
  ratio_MSA <- ratio %>% subset(MSA_NAME_COUNTY==i)
  temp.wgtGps <- srs_control_totals_temp_MSA %>% pull(wgtGpMSA)
  
  SF2_wgts_MSA <- sapply(temp.wgtGps,function(j){#Loop over weight groupingstemp.#wgtGps,function(j){#Loop over weight groupings
    log_debug("#########")
    log_debug(paste0("MSA: ",i,". Weight group: ",j))
    #Take weighting group subset within MSA subset
    #Note (09Jan2023): Removing totcrime_imp requirement
    SF_temp <- SF_temp_MSA %>%
      subset(wgtGpMSA==j & resp_ind_m3==1)
    if (nrow(SF_temp)>0){
      stopInd <- 0 #Initialize stop indicator to 0
      tempEnv <- environment() #Function environment
      out_temp <- sapply(length(crimeVarsWgtRest):0,function(nVar){#Loop over n control total variables
        if (stopInd==0){
          log_debug(paste0("MSA: ",i,". Weight group: ",j,". n SRS Variables: ",nVar+length(crimeVarsWgtAll)))
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
            
            total_temp <- srs_control_totals_temp_MSA %>%
              subset(wgtGpMSA==j) %>%
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
                mutate(!!paste0("MSAWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb) := rep(NA,nrow(SF_temp))) %>%
                select(paste0("MSAWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb))
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
                  dplyr::mutate(!!paste0("MSAWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb) := .) %>%
                  select(paste0("MSAWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb))
              } else {
                log_debug("Convergence, calibration failed")
                wgts_temp <- matrix(nrow=nrow(SF_temp),ncol=1) %>% as.data.frame() %>%
                  mutate(!!paste0("MSAWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb) := rep(NA,nrow(SF_temp))) %>%
                  select(paste0("MSAWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb))
              }
            }
          } else {
            #Skipping bc stopInd==1
            wgts_temp <- matrix(nrow=nrow(SF_temp),ncol=1) %>% as.data.frame() %>%
              mutate(!!paste0("MSAWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb) := rep(NA,nrow(SF_temp))) %>%
              select(paste0("MSAWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb))
          }
          return(wgts_temp)
          
        },simplify=FALSE) %>%
          bind_cols()
        
      },simplify=FALSE) %>%
        {bind_cols(SF_temp,.)}
      #In case even the crimeVarsWgtAll model fails...
      #11Aug2025: no longer using gencalib() in this situation... instead, 
      #             just using the inverse crime coverage...
      #           because creating the g-weights here, we need to use 1/(b*r),
      #             where b is the base weight and r is the crime coverage
      if (stopInd==0){
        log_debug(paste0("MSA: ",i,". Weight group: ",j,". n SRS Variables: ",1))
        
        log_debug("stopInd==0")
        log_debug("Setting g-weight equal to 1/(r*b),
                  where r is the crime coverage and b is the base weight")
        
        ratio_temp <- ratio %>% 
          filter(MSA_NAME_COUNTY==i & wgtGpMSA==j) %>%
          pull(ratio_totcrime_imp)
        
        wgts_temp <- SF_temp %>%
          mutate(!!paste0("MSAWgt_nVar",1,"_comb",1) := 1/(ratio_temp*baseWgt)) %>%
          select(paste0("MSAWgt_nVar",1,"_comb",1))
      } else {
        #Skipping bc stopInd==1
        wgts_temp <- matrix(nrow=nrow(SF_temp),ncol=1) %>% as.data.frame() %>%
          mutate(!!paste0("MSAWgt_nVar",1,"_comb",1) := rep(NA,nrow(SF_temp))) %>%
          select(paste0("MSAWgt_nVar",1,"_comb",1))
      }
      out_temp <- bind_cols(out_temp,
                            wgts_temp)
      
    } else {
      log_debug("No LEAs in MSA X weighting group")
      return(NULL)
    }
  },simplify=FALSE) %>%
    bind_rows()
  
  #If cell not empty, merge on SF
  #02May2024: issues while merging for some MSAs - tweaking merge
  if (nrow(SF2_wgts_MSA)>0){
    SF2_wgts_MSA <- SF2_wgts_MSA %>%
      select(ORI,county,matches("MSAWgt")) %>%
      #left_join(SF_temp_MSA,by=colnames(SF_temp_MSA))
      left_join(SF_temp_MSA,by=c("ORI","county"))
  }
  
  return(SF2_wgts_MSA)
  
  #print(out_temp)
},simplify=FALSE) %>%
  bind_rows()


#####
#Combination summaries

#Update (28OCT2021): Previously was copy-pasting code chunks by number of variables in model. Create function that will streamline
combs_table_MSA_gps <- function(indat,crimeVarsWgt,crimeVarsWgtAll,crimeVarsWgtRest,inWgtGps,wgtVar,wgtGpVar,wgtGpDescVar,suffix="",nInWgtGps=length(inWgtGps),nVars=length(crimeVarsWgtRest)){
  log_debug("Running function combs_table_MSA_gps")
  inGps <- expand.grid(MSA_NAME_COUNTY=msaGps2,wgtGp=inWgtGps)
  colnames(inGps) <- c("MSA_NAME_COUNTY",wgtGpVar)
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
      
      #Stack row once per MSA X weighting group
      
      temp.out <- temp.out[rep(seq_len(nrow(temp.out)), each = nInGps), ]  %>%
        bind_cols(inGps) %>%
        mutate(!!wgtGpDescVar:=factor(eval(as.symbol(wgtGpVar)),levels=wgtGpsMSA2,labels=wgtGpMSADescs2))
      #Note (09Jan2023): Removing totcrime_imp requirement
      temp.converge <- indat %>%
        subset(resp_ind_m3==1) %>%
        mutate(converge=!is.na(eval(as.symbol(paste0(wgtVar,"_nVar",temp.nVar+length(crimeVarsWgtAll),"_comb",i))))) %>%
        select(MSA_NAME_COUNTY,all_of(wgtGpVar),all_of(wgtGpDescVar),converge) %>%
        group_by_at(.vars=c("MSA_NAME_COUNTY",wgtGpVar,wgtGpDescVar)) %>%
        dplyr::summarize(converge=any(converge),
                         .groups="drop") %>%
        select(MSA_NAME_COUNTY,all_of(wgtGpVar),all_of(wgtGpDescVar),converge)
      
      temp.out <- temp.out %>% 
        left_join(temp.converge,by=c("MSA_NAME_COUNTY",wgtGpVar,wgtGpDescVar)) %>%
        left_join(ratio %>% select(MSA_NAME_COUNTY,wgtGpMSA,N,n,sum_totcrime_imp_all,sum_totcrime_imp_NIBRS))
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
  
  #Stack row once per MSA X weighting group
  
  temp.out <- temp.out[rep(seq_len(nrow(temp.out)), each = nInGps), ]  %>%
    bind_cols(inGps) %>%
    mutate(!!wgtGpDescVar:=factor(eval(as.symbol(wgtGpVar)),levels=wgtGpsMSA2,labels=wgtGpMSADescs2))
  print(temp.out)
  #Note (09Jan2023): Removing totcrime_imp requirement
  temp.converge <- indat %>%
    subset(resp_ind_m3==1) %>%
    mutate(converge=!is.na(eval(as.symbol(paste0(wgtVar,"_nVar",1,"_comb",1))))) %>%
    select(MSA_NAME_COUNTY,all_of(wgtGpVar),all_of(wgtGpDescVar),converge) %>%
    group_by_at(.vars=c("MSA_NAME_COUNTY",wgtGpVar,wgtGpDescVar)) %>%
    dplyr::summarize(converge=any(converge),
                     .groups="drop") %>%
    select(MSA_NAME_COUNTY,all_of(wgtGpVar),all_of(wgtGpDescVar),converge)
  
  out <- temp.out %>% 
    left_join(temp.converge,
              by=c("MSA_NAME_COUNTY",wgtGpVar,wgtGpDescVar)) %>%
    left_join(ratio %>% select(MSA_NAME_COUNTY,wgtGpMSA,N,n,sum_totcrime_imp_all,sum_totcrime_imp_NIBRS)) %>%
    list()
  colnames(out) %>% print()
  names(out) <- paste0("comb",1,"_table_",suffix)
  list2env(out,envir=.GlobalEnv)
  return(NULL)
}

combs_table_MSA_gps(indat=SF2_wgts2_test,crimeVarsWgt,crimeVarsWgtAll,crimeVarsWgtRest,inWgtGps=wgtGpsMSA2,
                    wgtVar="MSAWgt",wgtGpVar="wgtGpMSA",wgtGpDescVar="wgtGpMSADesc",
                    suffix="test")




#Update (20Mar2023): Some groups don't have a model that converges - for now, create row representing 0 variables (N/n)
#Update (05May2023): Adding back in
#Update (11Aug2025): Excluding 0 variable code (this is now done in the 
#                      1-variable case)
# comb0_table_test <- SF2_wgts2_test %>% 
#   select(MSA_NAME_COUNTY,wgtGpMSA,wgtGpMSADesc) %>% 
#   left_join(ratio %>% select(MSA_NAME_COUNTY,wgtGpMSA,N,n,sum_totcrime_imp_all,sum_totcrime_imp_NIBRS)) %>%
#   mutate(nVar=0,
#          comb=1,
#          converge=TRUE)
#Note (08May2023): Since MSAWgt_nVarX_combY is g-weight, need to divide by baseWgt
# SF2_wgts2_test <- SF2_wgts2_test %>%
#   mutate(MSAWgt_nVar0_comb1=ifelse(resp_ind_m3==1 & rowSums(!is.na(select(.,matches("MSAWgt_nVar\\d"))),na.rm=TRUE)==0,
#                                    1/(ratio_totcrime_imp*baseWgt),
#                                    NA_real_))


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
  subset(!is.na(n)) %>% #02May2024: combination convergence has gotten large (e.g., ~200 MB for 2022 rerun) -> only keep weighting groups that actually appear
  arrange(MSA_NAME_COUNTY,wgtGpMSA,wgtGpMSADesc,-converge,-nVar,comb) %>%
  group_by(MSA_NAME_COUNTY,wgtGpMSA,wgtGpMSADesc) %>%
  mutate(Select=ifelse(row_number(wgtGpMSA)==1 & converge==TRUE,"X","")) %>%
  ungroup() %>%
  arrange(MSA_NAME_COUNTY,wgtGpMSA,wgtGpMSADesc,-nVar,comb) %>%
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
  select(MSA_NAME_COUNTY,wgtGpMSA,wgtGpMSADesc,N,n,sum_totcrime_imp_all,sum_totcrime_imp_NIBRS,nVar,comb,
         totcrime_imp,totcrime_violent_imp,
         totcrime_property_imp,totcrime_murder_imp,
         totcrime_rape_imp,
         totcrime_aggAssault_imp,
         totcrime_burglary_imp,totcrime_rob_imp,
         totcrime_larceny_imp,totcrime_vhcTheft_imp,Variables,everything()) %>%
  left_join(msaCrosses2)




#Update (14Jun2022): Switching Excel output functions (fixing overwrite bug)
#combAll_table %>%
#  list("All Combinations"=.) %>%
#  write.xlsx(file=paste0(output_weighting_data_folder,"SRS_Variable_Combination_Convergence_by_MSA_X_Weighting_Group_Automatic.xlsx"))
log_debug("Writing excel workbook SRS_Variable_Combination_Convergence_by_MSA_X_Weighting_Group_AltCombs_Collapsed_Automatic.xlsx")
workbook <- paste0(output_weighting_data_folder,
                   "SRS_Variable_Combination_Convergence_by_MSA_X_Weighting_Group_AltCombs_Collapsed_Automatic.xlsx")
wb <- createWorkbook()
addWorksheet(wb,"All Combinations")
writeData(wb,"All Combinations",combAll_table)
saveWorkbook(wb,workbook,overwrite=TRUE) 


msaCW <- SF %>% 
  select(MSA_NAME_COUNTY) %>% 
  unique() %>% 
  mutate(MSA_CODE=1:nrow(.))

SF2 <- SF2 %>%
  arrange(ORI) %>%
  left_join(msaCrosses2) %>% #20Jun2023: joining to cross list
  select(-matches("^(MSA_CODE|totcrime_agg_rob_imp)$")) %>%
  inner_join(msaCW,by=c("MSA_NAME_COUNTY")) %>%
  mutate(wgtGpMSA2=msaCrossNum,
         totcrime_agg_rob_imp=0)

#choosing best model that converges
ctrlVars <- combAll_table %>% subset(Select=="X")

ctrlVars %>% 
  group_by(nVar) %>% 
  dplyr::summarize(n=n()) %>% 
  DT::datatable()
ctrlVars %>% 
  dplyr::summarize(n=n(),
                   across(matches("^totcrime"),
                          ~sum(.x=="X",na.rm=TRUE))) %>% 
  DT::datatable()
ctrlVars %>% 
  group_by(MSA_NAME_COUNTY) %>% 
  dplyr::summarize(n=n(),
                   nVar10=sum(nVar==10),
                   nVar9=sum(nVar==9),
                   nVar8=sum(nVar==8),
                   nVar7=sum(nVar==7),
                   nVar6=sum(nVar==6),
                   nVar5=sum(nVar==5),
                   nVar4=sum(nVar==4),
                   nVar3=sum(nVar==3),
                   nVar1=sum(nVar==1),
                   nVar0=sum(nVar==0)) %>% 
  DT::datatable()

#16May2024: accounting for addition of new self-reporting weighting group throughout this section
if (nrow(ctrlVars)==SF2 %>% select(MSA_NAME_COUNTY,wgtGpMSA) %>% subset(duplicated(.)==FALSE) %>% nrow()){
  
  #capture.output({
  SF2_wgts2 <- sapply(msaGps2,function(i){#Loop over weight groupings - just gp 1 for test
    print("##############################")
    print(paste0("MSA: ",i))
    SF_MSA <- SF2 %>%
      subset(MSA_NAME_COUNTY==i) #%>%
    #select(-matches("V\\d+_\\w"))
    #Note (10Jan2023): Removing totcrime_imp requirement
    SF_temp_MSA <- SF_MSA %>%
      subset(resp_ind_m3==1)
    
    temp_wgtGp1_code <- ctrlVars %>% subset(MSA_NAME_COUNTY==i & wgtGpMSA==1) %>% pull(msaCrossNum) %>% unique()
    temp_wgtGp2_code <- ctrlVars %>% subset(MSA_NAME_COUNTY==i & wgtGpMSA==2) %>% pull(msaCrossNum) %>% unique()
    temp_wgtGp3_code <- ctrlVars %>% subset(MSA_NAME_COUNTY==i & wgtGpMSA==3) %>% pull(msaCrossNum) %>% unique()
    
    #20Jun2025: automatically handle creation of temp_wgtGpX_code variables
    if (year >= 2022){
      for (j in 4:max(wgtGpsMSA2)){
        temp_code <- ctrlVars %>% 
          subset(MSA_NAME_COUNTY==i & wgtGpMSA==j) %>% 
          pull(msaCrossNum) %>% 
          unique()
        assign(str_c("temp_wgtGp",j,"_code"),
               temp_code)
      }
      rm(j,temp_code)
    }
    #choosing best model that converges
    ctrlInds_MSA <- combAll_table %>% 
      subset(Select=="X" & MSA_NAME_COUNTY==i) %>% 
      rename_at(.vars=vars(matches("^totcrime")),.funs=~paste0(.x,"_ind")) %>%
      mutate(wgtGpMSA2=msaCrossNum) %>%
      select(wgtGpMSA2,matches("_ind")) %>%
      mutate(across(matches("_ind"),~ifelse(.x!="X",0,1))) %>%
      mutate(across(matches("_ind"),~ifelse(is.na(.x),0,.x))) %>%
      arrange(wgtGpMSA2) %>%
      mutate(totcrime_agg_rob_imp_ind=0) %>% #Creating dummy variable to retain same names as national & region
      select(wgtGpMSA2,
             totcrime_imp_ind,totcrime_violent_imp_ind,
             totcrime_property_imp_ind,totcrime_murder_imp_ind,
             totcrime_rape_imp_ind,totcrime_agg_rob_imp_ind,
             totcrime_aggAssault_imp_ind,totcrime_burglary_imp_ind,
             totcrime_rob_imp_ind,totcrime_larceny_imp_ind,
             totcrime_vhcTheft_imp_ind)
    
    
    ctrlIndsM_MSA <- ctrlInds_MSA %>%
      select(colnames(ctrlInds_MSA)) %>%
      select(-wgtGpMSA2) %>%
      as.matrix()
    
    ctrlTtlsM_MSA <- srs_MSA_control_totals %>%
      subset(MSA_NAME_COUNTY==i) %>%
      left_join(msaCrosses2) %>% #20Jun2023: merging on cross number
      mutate(wgtGpMSA2=msaCrossNum) %>%
      arrange(wgtGpMSA) %>%
      mutate(sum_totcrime_agg_rob_imp=0) %>% #Creating dummy variable to retain order
      select(sum_totcrime_imp,sum_totcrime_violent_imp,
             sum_totcrime_property_imp,sum_totcrime_murder_imp,
             sum_totcrime_rape_imp,sum_totcrime_agg_rob_imp,
             sum_totcrime_aggAssault_imp,sum_totcrime_burglary_imp,
             sum_totcrime_rob_imp,sum_totcrime_larceny_imp,
             sum_totcrime_vhcTheft_imp) %>%
      as.matrix()
    #print("ncol(ctrlTtlsM_MSA):")
    #print(ncol(ctrlTtlsM_MSA))
    #print("ncol(ctrlIndsM_MSA):")
    #print(ncol(ctrlIndsM_MSA))
    #print("nrow(ctrlTtlsM_MSA):")
    #print(ncol(ctrlTtlsM_MSA))
    #print("nrow(ctrlIndsM_MSA):")
    #print(nrow(ctrlIndsM_MSA))
    ctrlTtlsM2_MSA <- ctrlTtlsM_MSA*ctrlIndsM_MSA #Element-wise multiplication
    colnames(ctrlTtlsM2_MSA) <- LETTERS[1:ncol(ctrlTtlsM2_MSA)] #Would normally include 'sum_' before, but will add that later
    
    ctrlTtls2_MSA <- ctrlTtlsM2_MSA %>%
      data.frame() %>%
      mutate(wgtGpMSA2=ctrlInds_MSA %>% getElement("wgtGpMSA2")) %>%
      reshape2::melt(id.vars="wgtGpMSA2") %>%
      reshape2::dcast(formula=.~wgtGpMSA2+variable) %>%
      select(-.) #Drop dummy variable
    colnames(ctrlTtls2_MSA) <- paste0("sum_V",colnames(ctrlTtls2_MSA))
    #print("colnames(ctrlTtls2_MSA):")
    #print(colnames(ctrlTtls2_MSA))
    
    colnames(ctrlTtls2_MSA) <- colnames(ctrlTtls2_MSA) %>% str_replace("^(\\w)$","sum_\\1")
    
    #Control variables
    #Note (10Jan2023): Removing totcrime_imp requirement
    ctrlIndsM_MSA <- ctrlInds_MSA %>%
      inner_join(SF_MSA) %>%
      subset(MSA_NAME_COUNTY==i & resp_ind_m3==1) %>%
      arrange(ORI) %>%
      select(colnames(ctrlInds_MSA)) %>%
      select(-wgtGpMSA2) %>%
      as.matrix()
    #Note (10Jan2023): Removing totcrime_imp requirement
    ctrlVarsM_MSA <- SF2%>%
      subset(MSA_NAME_COUNTY==i & resp_ind_m3==1) %>%
      arrange(ORI) %>%
      select(totcrime_imp,totcrime_violent_imp,totcrime_property_imp,
             totcrime_murder_imp,
             totcrime_rape_imp,totcrime_agg_rob_imp,
             totcrime_aggAssault_imp,totcrime_burglary_imp,
             totcrime_rob_imp,totcrime_larceny_imp,
             totcrime_vhcTheft_imp) %>%
      as.matrix()
    
    #print("ncol(ctrlVarsM_MSA):")
    #print(ncol(ctrlVarsM_MSA))
    #print("ncol(ctrlIndsM_MSA):")
    #print(ncol(ctrlIndsM_MSA))
    #print("nrow(ctrlVarsM_MSA):")
    #print(nrow(ctrlVarsM_MSA))
    #print("nrow(ctrlIndsM_MSA):")
    #print(nrow(ctrlIndsM_MSA))
    ctrlVarsM2_MSA <- ctrlVarsM_MSA*ctrlIndsM_MSA
    colnames(ctrlVarsM2_MSA) <- LETTERS[1:ncol(ctrlVarsM2_MSA)]
    
    #print("ctrVars2_MSA")
    ctrlVars2_MSA <- ctrlVarsM2_MSA %>%
      data.frame() %>%
      #Note (10Jan2023): Removing totcrime_imp requirement
      mutate(ORI=SF_MSA %>% arrange(ORI) %>% subset(MSA_NAME_COUNTY==i & resp_ind_m3==1) %>% pull(ORI),
             county=SF_MSA %>% arrange(ORI) %>% subset(MSA_NAME_COUNTY==i & resp_ind_m3==1) %>% pull(county),
             wgtGpMSA2=SF_MSA %>% arrange(ORI) %>% subset(MSA_NAME_COUNTY==i & resp_ind_m3==1) %>% pull(wgtGpMSA2)) 
    
    #Note (20Jun2023): Only create if they exist
    if (length(temp_wgtGp1_code)==1){
      ctrlVars2_MSA <- ctrlVars2_MSA %>%
        mutate(across(matches("^\\w{1}$"),
                      .fns=~.x*ifelse(wgtGpMSA2==temp_wgtGp1_code,1,0),
                      .names=paste0("V",temp_wgtGp1_code,"_{col}")))
    }
    if (length(temp_wgtGp2_code)==1){
      ctrlVars2_MSA <- ctrlVars2_MSA %>%
        mutate(across(matches("^\\w{1}$"),
                      .fns=~.x*ifelse(wgtGpMSA2==temp_wgtGp2_code,1,0),
                      .names=paste0("V",temp_wgtGp2_code,"_{col}")))
    }
    if (length(temp_wgtGp3_code)==1){ 
      ctrlVars2_MSA <- ctrlVars2_MSA %>%
        mutate(across(matches("^\\w{1}$"),
                      .fns=~.x*ifelse(wgtGpMSA2==temp_wgtGp3_code,1,0),
                      .names=paste0("V",temp_wgtGp3_code,"_{col}")))
    }
    #20Jun2025: automatically handle updating ctrlVars2_MSA for remaining groups
    if (year >= 2022){
      for (j in 4:max(wgtGpsMSA2)){
        temp_code <- get(str_c("temp_wgtGp",j,"_code"))
        if (length(temp_code)==1){ 
          ctrlVars2_MSA <- ctrlVars2_MSA %>%
            mutate(across(matches('^\\w{1}$'),
                          .fns=~.x*ifelse(wgtGpMSA2==temp_code,1,0),
                          .names=paste0('V',temp_code,'_{col}')))
        }
      }
    }
    
    
    #Add on the new control totals/variables
    SF_MSA <- SF_MSA %>%
      full_join(ctrlVars2_MSA) %>%
      #select(-matches("^sum_\\w+_imp$")) %>%
      #full_join(ctrlTtls2) %>%
      arrange(ORI)
    #Note (10Jan2023): Removing totcrime_imp requirement
    SF_temp <- SF_MSA%>%
      subset(resp_ind_m3==1)
    
    #21Mar2023: adding requirement that columns are in ctrlTtls2_MSA
    temp.ctrlVars <- colnames(ctrlVars2_MSA) %>% 
      str_subset("^V\\d+_\\w$") %>% 
      subset(. %in% (colnames(ctrlTtls2_MSA) %>% str_remove("sum_")))
    #Update (28OCT2021): Comment out print statement
    #print(temp.ctrlVars)
    if (length(temp.ctrlVars)==0){
      temp.ctrlVars <- "totcrime_imp"
    }
    total_temp <- ctrlTtls2_MSA %>%
      select(all_of(paste0("sum_",temp.ctrlVars))) %>%
      as.numeric()
    #names(total_temp) <- NULL
    vars_temp <- SF_temp %>%
      select(all_of(temp.ctrlVars)) 
    
    ratio_MSA <- ratio %>% subset(MSA_NAME_COUNTY==i)
    #names(vars_temp) <- NULL
    #Update (10Oct2022): Don't redo calibration, juse use weights from earlier
    #print("gencalib(Xs=select(SF_temp,all_of(temp.ctrlVars)), ...:")
    # SF_temp_wgts2 <- gencalib(Xs=vars_temp,
    #                       Zs=vars_temp,
    #                       #d=rep(1,nrow(SF_temp)),
    #                       d=rep(ratio_MSA$baseWgt,nrow(SF_temp)),
    #                       total=total_temp,
    #                       method="logit",
    #                       #bounds=c(low=1,1e6),
    #                       bounds=c(low=ratio_MSAlowBound,maxWgt/ratio_MSA$baseWgt),#1e6),
    #                       max_iter=5*maxIt,#10000
    #                       C=1,
    #                       description=TRUE) %>%
    #   data.frame(gWgt=.) %>%
    #   mutate(MSAWgt=gWgt*ratio_MSA$baseWgt) %>%
    #   {bind_cols(SF_temp,.)} %>%
    #   full_join(SF_MSA,by=colnames(SF_MSA))
    #Note (10Jan2023): Removing totcrime_imp requirement
    SF_temp_wgts2 <- SF2_wgts2_test %>%
      subset(resp_ind_m3==1 & MSA_NAME_COUNTY==i) %>%
      mutate(gWgt=select(.,matches("MSAWgt_nVar\\d")) %>% rowMeans(na.rm=TRUE)) %>%
      mutate(MSAWgt=gWgt*baseWgt) %>%
      select(ORI,county,gWgt,MSAWgt) %>%
      right_join(SF_temp)
    #print("SF_temp_wgts2:")
    #print(SF_temp_wgts2)
    #print("select(SF_temp_wgts2,all_of(temp.ctrlVars)) %>% as.matrix():")
    #print(select(SF_temp_wgts2,all_of(temp.ctrlVars)) %>% as.matrix())
    #print("rep(ratio_MSA$baseWgt,nrow(SF_temp_wgts2)):")
    #print(rep(ratio_MSA$baseWgt,nrow(SF_temp_wgts2)))
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
                     EPS=ifelse(any(total_temp==0),1,1e-6)) #%>% #EPS=1) %>%
    #print()
    temp.wgtGps <- srs_MSA_control_totals %>%
      subset(MSA_NAME_COUNTY==i) %>%
      pull(wgtGpMSA)
    SF2_wgts_MSA <- sapply(temp.wgtGps,function(j){#Loop over weight groupings
      print("##############")
      print(paste0("MSA: ",i,". Weight group: ",j))
      #Take weighting group subset within MSA subset
      #Note (10Jan2023): Removing totcrime_imp requirement
      SF_temp <- SF_temp_wgts2 %>%
        subset(wgtGpMSA==j & resp_ind_m3==1)
      
      if (j==1){
        temp_wgtGp_code <- temp_wgtGp1_code
      } else if (j==2){
        temp_wgtGp_code <- temp_wgtGp2_code
      } else if (j==3){
        temp_wgtGp_code <- temp_wgtGp3_code
      }
      #20Jun2025: automatically handle remaining wgt groups' temp_wgtGp_code
      if (year >= 2022){
        if (j %in% 4:max(wgtGpsMSA2)){
          temp_wgtGp_code <- get(str_c("temp_wgtGp",j,"_code"))
        }
      }
      
      if (nrow(SF_temp)>0){
        #print("hi")
        temp.ctrlVars <- colnames(SF_temp) %>% 
          str_subset(paste0("^V",temp_wgtGp_code,"_\\w$"))
        
        
        total_temp_MSA <- ctrlTtls2_MSA %>%
          select(all_of(paste0("sum_",temp.ctrlVars))) %>%
          as.numeric()
        #print(total_temp_MSA)
        out_temp <- SF_temp
        
        #Update (20AUG2021): Adding requested checks
        #Update (05Jul2022): Switch to table format (1 row per weight group) - commenting out old cold
        #Update (16May2024): added min and max to checks
        
        # #Check calibration
        # print("checkcalibration(Xs=select(SF_temp,all_of(temp.ctrlVars)), ...:")
        # checkcalibration(Xs=select(SF_temp,all_of(temp.ctrlVars)),
        #                  d=rep(1,nrow(SF_temp)),
        #                  total=total_temp,
        #                  g=out_temp$MSAWgt,
        #                  EPS=1) %>%
        #   print()
        # #Weight checks - summary, UWE, etc.
        # print("Distribution of weights:")
        # describe(out_temp$MSAWgt) %>%
        #   print()
        # print("Number of missing weights:")
        # sum(is.na(out_temp$MSAWgt))%>%
        #   print()
        # print("Number of weights equal to 1:")
        # sum(out_temp$MSAWgt == 1, na.rm=TRUE) %>%
        #   print()
        # print("Number of weights greater than 1:")
        # sum(out_temp$MSAWgt > 1, na.rm=TRUE) %>%
        #   print()
        # print("Number of weights less than 1:")
        # sum(out_temp$MSAWgt < 1, na.rm=TRUE) %>%
        #   print()
        # print("Number of weights greater than 100:")
        # sum(out_temp$MSAWgt > 100, na.rm=TRUE) %>%
        #   print()
        # print("UWE:")
        # UWE_MSAWgt <- 1+var(out_temp$MSAWgt,na.rm=TRUE)/(mean(out_temp$MSAWgt,na.rm=TRUE)^2)
        # UWE_MSAWgt %>%
        #   print()
        
        #Calibration worked (T/F)?
        temp.cal <- checkcalibration(Xs=select(SF_temp,all_of(temp.ctrlVars)) %>% as.matrix(),
                                     d=pull(SF_temp,baseWgt),
                                     total=total_temp_MSA,
                                     g=out_temp$gWgt,
                                     EPS=ifelse(any(total_temp_MSA==0),1,1e-6))%>%#EPS=1) %>%
          .$result
        #02May2024: swapping out describe()
        temp.describe <- describe(out_temp$MSAWgt)
        temp.nmiss <- sum(is.na(out_temp$MSAWgt))
        temp.nonmiss <- nrow(out_temp) - temp.nmiss
        temp.mean <- mean(out_temp$MSAWgt, na.rm = TRUE)
        temp.quantiles <- quantile(out_temp$MSAWgt,
                                   probs=c(0,0.05,0.1,0.25,0.5,0.75,0.9,0.95,1),
                                   na.rm=TRUE)
        #Note (26Jul2022): Adding n Eligible LEAs
        temp.nElig <- SF2 %>%
          subset(MSA_NAME_COUNTY==i & wgtGpMSA==j) %>%
          nrow()
        #Note (16May2024): rounding weight to 6 digits before checking if <1 (to avoid false flags)
        temp.nLT1 <- sum(round(out_temp$MSAWgt,digits=6) < 1 & out_temp$MSAWgt>0, na.rm=TRUE)
        #Note (29Jul2022): Switching from >100 to >20
        #temp.nGT100 <- sum(out_temp$MSAWgt > 100, na.rm=TRUE)
        temp.nGT20 <- sum(out_temp$MSAWgt > 20, na.rm=TRUE)
        temp.UWE <- 1+var(out_temp$MSAWgt,na.rm=TRUE)/(mean(out_temp$MSAWgt,na.rm=TRUE)^2)
        temp.out <- data.frame(msaGp=i,
                               wgtGpMSADesc=wgtGpMSADescs2[which(wgtGpsMSA2==j)],
                               calibrated=temp.cal,
                               #Note (26Jul2022): Changing counts - include n Eligible LEAs, n NIBRS LEAs, n NIBRS LEAs missing weights
                               #nOverall=as.numeric(temp.describe$counts["n"])+as.numeric(temp.describe$counts["missing"]),
                               nElig=temp.nElig,
                               #nNIBRS=as.numeric(temp.describe$counts["n"])+as.numeric(temp.describe$counts["missing"]),
                               #nMissing=as.numeric(temp.describe$counts["missing"]),
                               #nLT1=temp.nLT1,
                               nNIBRS=as.numeric(temp.nonmiss)+as.numeric(temp.nmiss),
                               nMissing=as.numeric(temp.nmiss),
                               nLT1=temp.nLT1,
                               #nGT100=temp.nGT100,
                               nGT20=temp.nGT20,
                               UWE=sprintf(temp.UWE,fmt="%1.3f"),
                               #Mean=sprintf(as.numeric(temp.describe$counts["Mean"]),fmt="%1.3f"),
                               Mean=sprintf(as.numeric(temp.mean),fmt="%1.3f"),
                               Min=sprintf(temp.quantiles["0%"],fmt="%1.3f"),
                               pt05=sprintf(temp.quantiles["5%"],fmt="%1.3f"),
                               pt10=sprintf(temp.quantiles["10%"],fmt="%1.3f"),
                               pt25=sprintf(temp.quantiles["25%"],fmt="%1.3f"),
                               pt50=sprintf(temp.quantiles["50%"],fmt="%1.3f"),
                               pt75=sprintf(temp.quantiles["75%"],fmt="%1.3f"),
                               pt90=sprintf(temp.quantiles["90%"],fmt="%1.3f"),
                               pt95=sprintf(temp.quantiles["95%"],fmt="%1.3f"),
                               Max=sprintf(temp.quantiles["100%"],fmt="%1.3f"))
        colnames(temp.out) <- c("MSA","Weight Group","Calibrated",
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
    #02May2024: reducing number of variables to only ID variables plus new variables (gWgt, MSAWgt, and calibration variables
    select(ORI,county,gWgt,MSAWgt,matches("V\\d+_\\w")) %>%
    #full_join(SF2,by=colnames(SF2))
    full_join(SF2,by=c("ORI","county"))
  #},file=paste0(output_weighting_data_folder,'weights_MSA_checks.txt'))
  #Note (JDB 06Jul2022): Combine weight check results
  results_MSA <- #outer(paste0("results_",msaGps2,"_"),wgtGpsMSA,FUN=paste0) %>%
    #as.character() %>% 
    SF2 %>% 
    select(MSA_NAME_COUNTY,wgtGpMSA) %>% 
    subset(duplicated(.)==FALSE) %>% 
    mutate(name=paste0("results_",MSA_NAME_COUNTY,"_",wgtGpMSA)) %>% 
    pull(name) %>%
    mget(envir=.GlobalEnv) %>%
    bind_rows()
  
  
  
  
  ###############
  #Output
  #Note (12Apr2023): Stacking skipped crossings
  #Note (30May2023): Including 2 new skipped crossing sets
  new_weights <- SF2_wgts2 %>%
    bind_rows(SF2_skips,
              SF2_skipsB,
              SF2_skipsC,
              SF2_skipSR)
  
  ### export for others to start writing functions to analyze bias, MSE, etc.
  new_weights[,c("ORI_universe","LEGACY_ORI","county","MSA_NAME_COUNTY","wgtGpMSA","wgtGpMSADesc",
                 #Update (27AUG2021): Add raw weight group variable
                 "wgtGpMSA_raw","wgtGpMSADesc_raw",
                 "MSAWgt")] %>%
    #write.csv(paste0(output_weighting_data_folder,'weights_MSA.csv'),
    fwrite_wrapper(paste0(output_weighting_data_folder,'weights_MSA_cal_srs_altcombs_col.csv'))
  
  #Update (26AUG2021): Add wgtGpMSA and wgtGpMSADesc to SF file from 02_Weights_Data_Setup
  # oldSF <- read_csv(paste0(input_weighting_data_folder,"SF_postN.csv"),
  #                   guess_max=1e6)%>%
  #   #Adding just in case already on file...
  #   select(-matches("wgtGpMSA"))
  calVars <- colnames(SF2_wgts2) %>%
    str_subset("^V\\d+_\\w") %>% #All calibration vars
    str_subset("^V(\\d|1\\d|20)_\\w$",negate=TRUE) #Remove national calibration vars
  calVarsRegEx <- str_flatten(calVars,collapse="|")
  oldSF <- fread(paste0(input_weighting_data_folder,"SF_postJD_cal_srs_altcombs_col.csv")) %>%
    #Adding just in case already on file...
    #02Apr2024: comment out the line below
    #select(-matches(paste0("(wgtGpMSA|",calVars,")")))%>%
    mutate(totcrime_imp=totcrime_violent_imp+totcrime_property_imp) %>%
    mutate(totcrime_agg_rob_imp=totcrime_aggAssault_imp+totcrime_rob_imp)
  #19Jun2023: binding SF2 and SF2_skips in 1st left_join
  #21Jun2023: also binding SF2_skipsB and SF2_skipsC to same part
  newSF <- oldSF %>%
    left_join(bind_rows(SF2,SF2_skips,SF2_skipsB,SF2_skipsC,SF2_skipSR) %>% 
                select(ORI_universe,county,MSA_NAME_COUNTY,wgtGpMSA,wgtGpMSADesc,
                       #Update (27AUG2021): Add raw weight group variable
                       wgtGpMSA_raw,wgtGpMSADesc_raw),
              by=c("ORI_universe","county","MSA_NAME_COUNTY")) %>%
    #Update (18Jan2023): adding new calibration variables
    left_join(SF2_wgts2 %>%
                select(ORI_universe,county,MSA_NAME_COUNTY,all_of(calVars)),
              by=c("ORI_universe","county","MSA_NAME_COUNTY"))
  
  #write_csv(newSF,file=paste0(output_weighting_data_folder,"SF_postS_cal.csv"))
  fwrite_wrapper(newSF,paste0(output_weighting_data_folder,"SF_postMSA_cal_srs_altcombs_col.csv"))
  
  #Note (JDB 06Jul2022): Export weight check results
  #write_csv(results_MSA,
  fwrite_wrapper(results_MSA,
                 paste0(output_weighting_data_folder,"weights_MSA_cal_srs_altcombs_col_checks.csv"))
  #Track list of MSAs
  msa_all <- SF %>%
    subset(!is.na(MSA_NAME_COUNTY)) %>%
    select(MSA_NAME_COUNTY) %>%
    unique() %>%
    arrange(MSA_NAME_COUNTY)
  fwrite_wrapper(msa_all,
                 paste0(output_weighting_data_folder,"msa_all.csv"))
  
} else {
  stop("No calibration model converged for 1+ (MSA X weighting group) crossing")
}
log_info("Finished 03_Weights_Calibration_MSA_SRS_AltCombs_Collapsed.R\n\n")
