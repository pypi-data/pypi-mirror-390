#Note (07Oct2022): This will be the version with a max adjustment factor of 10
maxAdj <- 10
maxIt <- 1000
### Purpose of program is to calibrate national weights by grouping (e.g., All cities 250,000 or over)
### Author: JD Bunker
### Last updated: 28OCT2021
#Update (27OCT2021): Commenting out/removing unnecessary print statements and removing no longer needed commented-out code
#Update (28OCT2021): Continuing to comment out/remove unnecessary print statements and remove no longer needed commented-out code
#Update (29OCT2021): Continuing cleaning.
#Update (23MAR2022): Reduce number of calibration models attempted. Stop after 1st success for weighting group.
#Update (29SEP2022): Switching to N/n base weights and n/N lower bounds
#Update (04JUN2024): Changing lower bound from lowBound to 0.5 for 2022
#Update (12NOV2024): Creating national SRS calibration program (heavily based on NIBRS equivalent)
#					 We'll bump the lowBound back to 1 for 2022
library(tidyverse)
library(openxlsx)
library(lubridate)
library(sampling)
library(Hmisc)

log_info("Running 03_Weights_Calibration_National_SRS.R")

# read in SF data

SF <- str_c(str_c(input_weighting_data_folder,"SF_national_srs.csv")) %>%
  #read.csv(header=TRUE, sep=",") %>%
  fread() %>%
  mutate(totcrime_imp=totcrime_violent_imp+totcrime_property_imp)

#colnames(SF)
crimeVars <- SF %>%
  colnames() %>%
  str_subset("^tot.*_imp")
#Crime variables for weight calibration
crimeVarsWgt <- c("totcrime_imp","totcrime_murder_imp",
                  "totcrime_rape_imp","totcrime_aggAssault_imp",
                  "totcrime_burglary_imp","totcrime_rob_imp",
                  "totcrime_larceny_imp","totcrime_vhcTheft_imp")



SF2 <- SF


wgtGpDescs <-  c("All cities 1,000,000 or over",
                 "All cities 500,000 or over",
                 "All cities 250,000-499,999",
                 "Cities from 100,000 thru 249,999",
                 "Cities from 50,000 thru 99,999",
                 "Cities from 25,000 thru 49,999",
                 "Cities from 10,000 thru 24,999",
                 "Cities under 10,000",
                 "MSA counties 100,000 or over",
                 "MSA counties from 25,000 thru 99,999",
                 "MSA counties from 10,000 thru 24,999",
                 "MSA counties under 10,000",
                 "MSA State Police",
                 "Non-MSA counties 25,000 or over",
                 "Non-MSA counties from 10,000 thru 24,999",
                 "Non-MSA counties under 10,000",
                 "Non-MSA State Police",
                 "CITY AGENCY-ZERO POP",
                 "MSA COUNTY/STATE AGENCY-ZERO POP",
                 "NON-MSA COUNTY/STATE AGENCY-ZERO POP")
SF2 <- SF2 %>%
  mutate(totcrime_agg_rob_imp=totcrime_aggAssault_imp+totcrime_rob_imp)%>%
  #12Nov2024: switching references of 'POPULATION_GROUP_DESC' to 'POPULATION_GROUP_DESC_UNIV'
  #           also, switching references of 'POPULATION' to 'POPULATION_UNIV'
  mutate(wgtGp=case_when(POPULATION_GROUP_DESC_UNIV=="Cities 1,000,000 or over" ~ 1,
                         POPULATION_GROUP_DESC_UNIV=="Cities from 500,000 thru 999,999" ~ 2,
                         POPULATION_GROUP_DESC_UNIV=="Cities from 250,000 thru 499,999" ~ 3,
                         POPULATION_GROUP_DESC_UNIV=="Cities from 100,000 thru 249,999" ~ 4,
                         POPULATION_GROUP_DESC_UNIV=="Cities from 50,000 thru 99,999" ~ 5,
                         POPULATION_GROUP_DESC_UNIV=="Cities from 25,000 thru 49,999" ~ 6,
                         POPULATION_GROUP_DESC_UNIV=="Cities from 10,000 thru 24,999" ~ 7,
                         POPULATION_GROUP_DESC_UNIV %in% c("Cities from 2,500 thru 9,999","Cities under 2,500") & POPULATION_UNIV> 0 ~ 8,
                         
                         POPULATION_GROUP_DESC_UNIV=="MSA counties 100,000 or over" ~ 9,
                         POPULATION_GROUP_DESC_UNIV=="MSA counties from 25,000 thru 99,999" ~ 10,
                         POPULATION_GROUP_DESC_UNIV=="MSA counties from 10,000 thru 24,999" ~ 11,
                         POPULATION_GROUP_DESC_UNIV=="MSA counties under 10,000" &  POPULATION_UNIV> 0 ~ 12,
                         POPULATION_GROUP_DESC_UNIV=="MSA State Police" & POPULATION_UNIV>0 ~ 13,
                         
                         POPULATION_GROUP_DESC_UNIV %in% c("Non-MSA counties from 25,000 thru 99,999","Non-MSA counties 100,000 or over") ~ 14,
                         POPULATION_GROUP_DESC_UNIV=="Non-MSA counties from 10,000 thru 24,999" ~ 15,
                         POPULATION_GROUP_DESC_UNIV=="Non-MSA counties under 10,000" & POPULATION_UNIV >0 ~ 16,
                         POPULATION_GROUP_DESC_UNIV=="Non-MSA State Police" & POPULATION_UNIV>0 ~ 17,
                         
                         POPULATION_GROUP_DESC_UNIV=="Cities under 2,500" & POPULATION_UNIV==0 ~ 18,
                         POPULATION_GROUP_DESC_UNIV %in% c("MSA counties under 10,000","MSA State Police") & POPULATION_UNIV==0 ~ 19,
                         POPULATION_GROUP_DESC_UNIV %in% c("Non-MSA counties under 10,000","Non-MSA State Police") & POPULATION_UNIV==0 ~ 20),
         wgtGpDesc=factor(wgtGp,levels=1:20,labels=wgtGpDescs),
         totcrime_imp=totcrime_violent_imp+totcrime_property_imp)

wgtGps <- SF2 %>%
  select(wgtGp) %>%
  unique() %>%
  .$wgtGp %>%
  sort()
nWgtGps <- SF2 %>%
  select(wgtGp) %>%
  unique() %>%
  nrow()

#Collapsing
SF2 <- SF2 %>%
  mutate(wgtGpNational=case_when(wgtGp==2 ~ 1,
                                 wgtGp==3 ~ 1,
                                 wgtGp==12 ~ 11,
                                 TRUE ~ wgtGp))
wgtGps2 <- SF2 %>%
  select(wgtGpNational) %>%
  unique() %>%
  .$wgtGpNational %>%
  sort()
nWgtGps2 <- SF2 %>%
  select(wgtGpNational) %>%
  unique() %>%
  nrow()

#colnames(SF2)
wgtGpDescs2 <- wgtGpDescs %>%
  as.character() %>%
  data.frame(wgtGpDesc=.) %>%
  inner_join(SF2 %>% select(wgtGpDesc),by=c("wgtGpDesc")) %>%
  #Update (27AUG2021): Convert to character
  mutate(wgtGpDesc=as.character(wgtGpDesc)) %>%
  mutate(wgtGpNationalDesc=case_when(wgtGpDesc=="All cities 1,000,000 or over" ~ "All cities 250,000 or over",
                                     wgtGpDesc=="All cities 500,000 or over" ~ "All cities 250,000 or over",
                                     wgtGpDesc=="All cities 250,000-499,999" ~ "All cities 250,000 or over",
                                     wgtGpDesc=="MSA counties from 10,000 thru 24,999" ~ "MSA counties under 25,000",
                                     wgtGpDesc=="MSA counties under 10,000" ~ "MSA counties under 25,000",
                                     
                                     TRUE ~ wgtGpDesc))

wgtGpDescs2 <- wgtGpDescs2 %>%
  .$wgtGpNationalDesc %>%
  unique()

SF2 <- SF2 %>%
  mutate(wgtGpNationalDesc=factor(wgtGpNational,levels=wgtGps2,labels=wgtGpDescs2),
         totcrime_agg_rob_imp=totcrime_aggAssault_imp+totcrime_rob_imp)

#22Nov2024: including additional collapsing for necessary years, and a check that no cells have 1+ nonrespondent and 0 respondents
#24Nov2024: also, require collapsing if only 1 respondent and >0 nonrespondent
respProbs <- SF2 %>%
  group_by(wgtGpNational) %>%
  dplyr::summarize(nResp=sum(resp_ind_srs==1),
                   nNR=sum(resp_ind_srs==0)) %>%
  subset((nResp==0 & nNR>0)|(nResp==1 & nNR>0))

cat("Initializing",
    file=str_c(output_weighting_data_folder,"collapsing_tracker_srs.txt"))
#06Dec2024: no longer collapsing group 20 for 2010:2012
if (nrow(respProbs)>0){#|as.numeric(year) %in% 2010:2012){
  if (nrow(respProbs>0)){
    log_debug("1+ weighting group has >0 nonrespondents and 0 respondents. Will need to collapse weighting groups. See below.")
    print(respProbs)
  } 
  if (as.numeric(year) %in% c(1997,1998,1999,2000,2001)){
    log_debug("Collapsing Non-MSA State Police into NON-MSA COUNTY/STATE AGENCY-ZERO POP")
    cat("\nCollapsing groups 17 and 20 together",
        file=str_c(output_weighting_data_folder,"collapsing_tracker_srs.txt"),
        append=TRUE)
    
    SF2 <- SF2 %>%
      mutate(wgtGpNational=case_when(wgtGpNational==17 ~ 20,
                                     TRUE ~ wgtGpNational))
    wgtGps2 <- SF2 %>%
      select(wgtGpNational) %>%
      unique() %>%
      pull(wgtGpNational) %>%
      sort()
    nWgtGps2 <- SF2 %>%
      select(wgtGpNational) %>%
      unique() %>%
      nrow()
    
    wgtGpDescs2 <- SF2 %>% 
      select(wgtGpNational,wgtGpNationalDesc) %>%
      unique() %>%
      arrange(wgtGpNational) %>%
      mutate(wgtGpNationalDesc=case_when(wgtGpNational==20 ~ "Non-MSA State Police and NON-MSA COUNTY/STATE AGENCY-ZERO POP",
                                         TRUE ~ wgtGpNationalDesc)) %>%
      unique() %>%
      pull(wgtGpNationalDesc)
    
    SF2 <- SF2 %>%
      mutate(wgtGpNationalDesc=factor(wgtGpNational,levels=wgtGps2,labels=wgtGpDescs2))
  } #else if (as.numeric(year) %in% 2010:2011){
  # log_debug("\nCollapsing zero pop county/state police groups together")
  # #04Dec2024: collapse 19,20 together
  # cat("Collapsing groups 19 and 20 together",
  # file=str_c(output_weighting_data_folder,"collapsing_tracker_srs.txt"),
  # append=TRUE)
  # SF2 <- SF2 %>%
  # mutate(wgtGpNational=case_when(#wgtGpNational==18 ~ 20,
  # wgtGpNational==19 ~ 20,
  # TRUE ~ wgtGpNational))
  # wgtGps2 <- SF2 %>%
  # select(wgtGpNational) %>%
  # unique() %>%
  # pull(wgtGpNational) %>%
  # sort()
  # nWgtGps2 <- SF2 %>%
  # select(wgtGpNational) %>%
  # unique() %>%
  # nrow()
  
  # wgtGpDescs2 <- SF2 %>% 
  # select(wgtGpNational,wgtGpNationalDesc) %>%
  # unique() %>%
  # arrange(wgtGpNational) %>%
  # mutate(wgtGpNationalDesc=case_when(wgtGpNational==20 ~ "County/State Police-ZERO POP AGENCIES",
  # TRUE ~ wgtGpNationalDesc)) %>%
  # unique() %>%
  # pull(wgtGpNationalDesc)
  
  # SF2 <- SF2 %>%
  # mutate(wgtGpNationalDesc=factor(wgtGpNational,levels=wgtGps2,labels=wgtGpDescs2))
  # } else if (as.numeric(year) %in% 2012){
  # log_debug("\nCollapsing all zero pop groups together")
  # #05Dec2024: collapse 18,19,20 together
  # cat("Collapsing groups 18, 19, and 20 together",
  # file=str_c(output_weighting_data_folder,"collapsing_tracker_srs.txt"),
  # append=TRUE)
  # SF2 <- SF2 %>%
  # mutate(wgtGpNational=case_when(wgtGpNational==18 ~ 20,
  # wgtGpNational==19 ~ 20,
  # TRUE ~ wgtGpNational))
  # wgtGps2 <- SF2 %>%
  # select(wgtGpNational) %>%
  # unique() %>%
  # pull(wgtGpNational) %>%
  # sort()
  # nWgtGps2 <- SF2 %>%
  # select(wgtGpNational) %>%
  # unique() %>%
  # nrow()
  
  # wgtGpDescs2 <- SF2 %>% 
  # select(wgtGpNational,wgtGpNationalDesc) %>%
  # unique() %>%
  # arrange(wgtGpNational) %>%
  # mutate(wgtGpNationalDesc=case_when(wgtGpNational==20 ~ "ZERO POP AGENCIES",
  # TRUE ~ wgtGpNationalDesc)) %>%
  # unique() %>%
  # pull(wgtGpNationalDesc)
  
  # SF2 <- SF2 %>%
  # mutate(wgtGpNationalDesc=factor(wgtGpNational,levels=wgtGps2,labels=wgtGpDescs2))
  # }
  #Post collapsing - do we still have issues?
  respProbs2 <- SF2 %>%
    group_by(wgtGpNational) %>%
    dplyr::summarize(nResp=sum(resp_ind_srs==1),
                     nNR=sum(resp_ind_srs==0)) %>%
    subset((nResp==0 & nNR>0)|(nResp==1 & nNR>0))
  if (nrow(respProbs2)>0){
    log_debug("Problematic weighting group(s):")
    print(respProbs2)
    stop("1+ weighting group still has >0 nonrespondents and 0 respondents. Additional collapsing necessary before rerunning. See above.")
  } else {
    log_debug("Resolved issue via collapsing. Proceeding with rest of program.")
  }
}



#Get totals by weighting group
srs_control_totals <- SF2 %>%
  group_by(wgtGpNational,wgtGpNationalDesc) %>%
  dplyr::summarize(across(all_of(crimeVarsWgt),.fns=list("sum"=~sum(.x,na.rm=TRUE)),.names="{fn}_{col}"),
                   .groups="drop")

SF2 <- SF2 %>%
  left_join(srs_control_totals,by=c("wgtGpNational","wgtGpNationalDesc")) %>%
  mutate(k=sum_totcrime_aggAssault_imp/sum_totcrime_rob_imp) %>%
  mutate(totcrime_agg_rob_imp=totcrime_aggAssault_imp+k*totcrime_rob_imp)

#Note (12Nov2024): Setting aside weighting groups with >=99% crime coverage
#Note (26Nov2024): Also skipping those with total crimes of 0 among eligible LEAs
crossings_skips <- SF2 %>%group_by(wgtGpNational,wgtGpNationalDesc) %>%
  dplyr::summarize(ratio_totcrime_imp=ifelse(sum(totcrime_imp)>0,
                                             sum(ifelse(resp_ind_srs==1,1,0)*totcrime_imp)/sum(totcrime_imp),
                                             1)) %>%
  subset(ratio_totcrime_imp>=0.99) %>%
  select(wgtGpNational)
SF2_skips <- SF2 %>%
  inner_join(crossings_skips) %>%
  mutate(NationalWgt=ifelse(resp_ind_srs==1,1,NA_real_))

SF2 <- SF2 %>%
  anti_join(crossings_skips)

#Get totals by weighting group
srs_control_totals <- SF2 %>%
  group_by(wgtGpNational,wgtGpNationalDesc) %>%
  dplyr::summarize(sum_totcrime_imp=sum(totcrime_imp,na.rm=TRUE),
                   sum_totcrime_murder_imp=sum(totcrime_murder_imp,na.rm=TRUE),
                   sum_totcrime_rape_imp=sum(totcrime_rape_imp,na.rm=TRUE),
                   sum_totcrime_aggAssault_imp=sum(totcrime_aggAssault_imp,na.rm=TRUE),
                   sum_totcrime_burglary_imp=sum(totcrime_burglary_imp,na.rm=TRUE),
                   sum_totcrime_rob_imp=sum(totcrime_rob_imp,na.rm=TRUE),
                   sum_totcrime_larceny_imp=sum(totcrime_larceny_imp,na.rm=TRUE),
                   sum_totcrime_vhcTheft_imp=sum(totcrime_vhcTheft_imp,na.rm=TRUE),
                   sum_totcrime_agg_rob_imp=sum(totcrime_agg_rob_imp,na.rm=TRUE),
                   .groups="drop")

#Get n NIBRS Reporters and n Eligible - used for base weights and lower bounds
#12Nov2024: adding ratio_totcrime_imp
ratio <- SF2 %>% #group_by(wgtGpNational,wgtGpNationalDesc) %>%
  dplyr::summarize(n=sum(resp_ind_srs==1),
                   N=n(),
                   #mean_totcrime_imp=mean(totcrime_imp) %>% round(digits=2)
                   ratio_totcrime_imp=sum(ifelse(resp_ind_srs==1,1,0)*totcrime_imp)/sum(totcrime_imp)
  ) %>%
  mutate(baseWgt=N/n,
         lowBound=n/N) #%>% 
#DT::datatable()
SF2 <- SF2 %>%
  select(-matches("sum_totcrime")) %>%
  inner_join(srs_control_totals) %>%
  select(-matches("^(n|N|baseWgt|lowBound)$")) %>%
  bind_cols(ratio)
#left_join(ratio,by=c("wgtGpNational","wgtGpNationalDesc"))

#22Nov2024: create text file that will track any allow weights <1
cat("Initializing",
    file=str_c(output_weighting_data_folder,"weights_lt1_tracker_srs.txt"))

#######################
#Check convergence
#First, largest city LEAs

#15May2024: changing variables to match other weighting groups for 2023 onward
#15Nov2024: actually, since SRS coverage high every year except 2021 (where only have NIBRS converted SRS) - let's only use reduced set of variables for 2021 (and full otherwise)
#if (as.numeric(year)<2023){
#if (as.numeric(year)==2021){
#  crimeVarsWgt <- c("totcrime_imp","totcrime_murder_imp",
#                    "totcrime_rape_imp","totcrime_agg_rob_imp",
#                    "totcrime_burglary_imp",
#                    "totcrime_larceny_imp","totcrime_vhcTheft_imp")
#} else {
crimeVarsWgt <- c("totcrime_imp","totcrime_murder_imp",
                  "totcrime_rape_imp","totcrime_aggAssault_imp",
                  "totcrime_burglary_imp","totcrime_rob_imp",
                  "totcrime_larceny_imp","totcrime_vhcTheft_imp")
#}
#Update (28OCT2021): Removing print statements
#Update (23MAR2022): Stop running after first successful convergence for weighting group
#Update (23MAR2022): Lowering max_iter from 10000 to 1000
#Update (12NOV2024): Only run if 1st weighting group is not in skipped weighting groups
if (!1 %in% crossings_skips$wgtGpNational){
  SF2_wgts2_firstGp <- sapply(wgtGps2[1],function(j){#Loop over weight groupings
    log_debug("Running function SF2_wgts2_firstGp")
    log_debug("########################")
    log_debug(str_c("Weight group: ",j))
    #Take weighting group subset within weight group subset
    #Note (09Jan2023): Removing totcrime_imp requirement
    SF_temp <- SF2 %>%
      subset(wgtGpNational==j & resp_ind_srs==1)
    stopInd <- 0 #Initialize stop indicator to 0
    tempEnv <- environment() #Function environment
    #16May2024: changing from looping over (ncol(srs_control_totals)-4):1 to length(crimeVarsWgt):1
    sapply(length(crimeVarsWgt):1,function(nVar){#Loop over n control total variables
      #14Nov2024: vary max # of iterations by number of variables (1-7=1K, 8=1M)
      if (nVar==length(crimeVarsWgt)){
        maxIt2 <- 1e3*maxIt
      } else {
        maxIt2 <- maxIt
      }
      log_debug(str_c("Weight group: ",j,". n SRS Variables: ",nVar))
      varCombs_nVar <- combn(crimeVarsWgt,m=nVar,simplify=FALSE)
      nVarCombs <- length(varCombs_nVar) #Number of combinations
      sapply(1:nVarCombs,function(nComb){#Loop over variable combinations
        if (stopInd==0){
          log_debug("stopInd==0")
          ctrlVars <- varCombs_nVar[[nComb]]
          print(ctrlVars)
          total_temp <- srs_control_totals %>%
            subset(wgtGpNational==j) %>%
            select(all_of(str_c("sum_",ctrlVars))) %>%
            as.numeric()
          print(total_temp)
          #Note (09Jan2023): removing totcrime_imp requirement
          temp.ratio <- SF2 %>%
            subset(wgtGpNational==j) %>%
            dplyr::summarize(n=sum(1*resp_ind_srs==1),
                             N=n()) %>%
            mutate(baseWgt=N/n,
                   lowBound=n/N)
          #Update (02DEC2024): Updating max number of iterations to a 10th of maxIt2
          #Update (05Dec2024): As a first step, try a max adjustment factor of 2.5 (often works)
          capture.output(
            wgts_temp <- gencalib(Xs=select(SF_temp,all_of(ctrlVars)),
                                  Zs=select(SF_temp,all_of(ctrlVars)),
                                  #d=rep(ratio_temp$baseWgt,nrow(SF_temp)),
                                  d=rep(ratio$baseWgt,nrow(SF_temp)),
                                  total=total_temp,
                                  method="logit",
                                  bounds=c(low=ratio$lowBound,2.5),#1e6),
                                  max_iter=maxIt2/100,#1000,#10000
                                  C=1)
          )
          #29Dec2024: confirm calibration before proceeding
          if (nVar==length(crimeVarsWgt) & !is.null(wgts_temp)){
            test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                     d=rep(ratio$baseWgt,nrow(SF_temp)),
                                     total=total_temp,
                                     g=wgts_temp,
                                     EPS=ifelse(any(total_temp==0),1,1e-6))#EPS=1)
            if (test$result!=TRUE){
              log_debug("Convergence, calibration failed")
              wgts_temp <- NULL
            } else {
              log_debug("Calibration succeeded")
            }
          }
          #Update (06Dec2024): Adding new step - try max adjustment factor of 1.5
          if (nVar==length(crimeVarsWgt) & is.null(wgts_temp)){
            log_debug("No convergence - trying again with upper bound of 1.5")
            cat(str_c("\nWeight group ",j,": Trying weight 1 with upper bound of 1.5 (",maxIt2/100/1000,"K iterations)"),
                file=str_c(output_weighting_data_folder,"weights_lt1_tracker_srs.txt"),
                append=TRUE)
            capture.output(
              wgts_temp <- gencalib(Xs=select(SF_temp,all_of(ctrlVars)),
                                    Zs=select(SF_temp,all_of(ctrlVars)),
                                    #d=rep(ratio_temp$baseWgt,nrow(SF_temp)),
                                    d=rep(ratio$baseWgt,nrow(SF_temp)),
                                    total=total_temp,
                                    method="logit",
                                    bounds=c(low=ratio$lowBound,1.5),#1e6),
                                    max_iter=maxIt2/100,#1000,#10000
                                    C=1)
            )
            #02Jan2025: confirm calibration before proceeding
            if (nVar==length(crimeVarsWgt) & !is.null(wgts_temp)){
              test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                       d=rep(ratio$baseWgt,nrow(SF_temp)),
                                       total=total_temp,
                                       g=wgts_temp,
                                       EPS=ifelse(any(total_temp==0),1,1e-6))#EPS=1)
              if (test$result!=TRUE){
                log_debug("Convergence, calibration failed")
                wgts_temp <- NULL
              } else {
                log_debug("Calibration succeeded")
              }
            }
          }
          #Update (05Dec2024): If above didn't work, try with adj factor of 5
          if (nVar==length(crimeVarsWgt) & is.null(wgts_temp)){
            log_debug("No convergence - trying again with upper bound of 5")
            cat(str_c("\nWeight group ",j,": Trying weight 1 with upper bound of 5 (",maxIt2/100/1000,"K iterations)"),
                file=str_c(output_weighting_data_folder,"weights_lt1_tracker_srs.txt"),
                append=TRUE)
            capture.output(
              wgts_temp <- gencalib(Xs=select(SF_temp,all_of(ctrlVars)),
                                    Zs=select(SF_temp,all_of(ctrlVars)),
                                    #d=rep(ratio_temp$baseWgt,nrow(SF_temp)),
                                    d=rep(ratio$baseWgt,nrow(SF_temp)),
                                    total=total_temp,
                                    method="logit",
                                    bounds=c(low=ratio$lowBound,5),#1e6),
                                    max_iter=maxIt2/100,#1000,#10000
                                    C=1)
            )
            #02Jan2025: confirm calibration before proceeding
            if (nVar==length(crimeVarsWgt) & !is.null(wgts_temp)){
              test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                       d=rep(ratio$baseWgt,nrow(SF_temp)),
                                       total=total_temp,
                                       g=wgts_temp,
                                       EPS=ifelse(any(total_temp==0),1,1e-6))#EPS=1)
              if (test$result!=TRUE){
                log_debug("Convergence, calibration failed")
                wgts_temp <- NULL
              } else {
                log_debug("Calibration succeeded")
              }
            }
          }
          
          #Update (06Feb2025): Initializing temp.text to NA_character_
          temp.text <- NA_character_
          
          #Update (05Dec2024): If above didn't work, then proceed with usual max adj factor (e.g., 10)
          if (nVar==length(crimeVarsWgt) & is.null(wgts_temp)){
            log_debug(str_c("No convergence - trying again with upper bound of ",maxAdj))
            cat(str_c("\nWeight group ",j,": Trying weight 1 with upper bound of ",maxAdj," (",maxIt2/100/1000,"K iterations)"),
                file=str_c(output_weighting_data_folder,"weights_lt1_tracker_srs.txt"),
                append=TRUE)
            temp.text <- capture.output(
              wgts_temp <- gencalib(Xs=select(SF_temp,all_of(ctrlVars)),
                                    Zs=select(SF_temp,all_of(ctrlVars)),
                                    #d=rep(ratio_temp$baseWgt,nrow(SF_temp)),
                                    d=rep(ratio$baseWgt,nrow(SF_temp)),
                                    total=total_temp,
                                    method="logit",
                                    bounds=c(low=ratio$lowBound,maxAdj),#1e6),
                                    max_iter=maxIt2/100,#1000,#10000
                                    C=1)
            )
            #02Jan2025: confirm calibration before proceeding
            if (nVar==length(crimeVarsWgt) & !is.null(wgts_temp)){
              test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                       d=rep(ratio$baseWgt,nrow(SF_temp)),
                                       total=total_temp,
                                       g=wgts_temp,
                                       EPS=ifelse(any(total_temp==0),1,1e-6))#EPS=1)
              if (test$result!=TRUE){
                log_debug("Convergence, calibration failed")
                wgts_temp <- NULL
              } else {
                log_debug("Calibration succeeded")
              }
            }
          }
          #06Feb2025: if that fails (and no bounds were given by last run), try a variety of values bw 10 to 1.1 until we get bounds
          for (temp.maxAdj in seq(10,1.1,by=-0.1) %>% subset(!. %in% c(1.5,2.5,5,10))){
            if (length(temp.text)==0 & is.null(wgts_temp) & nVar==length(crimeVarsWgt)){
              log_debug(str_c("No convergence - trying again with upper bound of ",temp.maxAdj))
              cat(str_c("\nWeight group ",j,": Trying weight 1 with upper bound of ",temp.maxAdj," (",maxIt2/100/1000,"K iterations)"),
                  file=str_c(output_weighting_data_folder,"weights_lt1_tracker_srs.txt"),
                  append=TRUE)
              temp.text <- capture.output(
                wgts_temp <- gencalib(Xs=select(SF_temp,all_of(ctrlVars)),
                                      Zs=select(SF_temp,all_of(ctrlVars)),
                                      d=rep(ratio$baseWgt,nrow(SF_temp)),
                                      total=total_temp,
                                      method="logit",
                                      bounds=c(low=ratio$lowBound,temp.maxAdj),#1e6),
                                      max_iter=maxIt2/100,#1000,#10000
                                      C=1)
              )
              #02Jan2025: confirm calibration before proceeding
              if (nVar==length(crimeVarsWgt) & !is.null(wgts_temp)){
                test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                         d=rep(ratio$baseWgt,nrow(SF_temp)),
                                         total=total_temp,
                                         g=wgts_temp,
                                         EPS=ifelse(any(total_temp==0),1,1e-6))#EPS=1)
                if (test$result!=TRUE){
                  log_debug("Convergence, calibration failed")
                  wgts_temp <- NULL
                } else {
                  log_debug("Calibration succeeded")
                }
              }
            }
          }
          
          #02Jan2025: initialize max adjustment factor variables
          temp.upper <- maxAdj
          maxAdj2 <- maxAdj
          temp.upper2 <- maxAdj
          maxAdj3 <- maxAdj
          temp.upper3 <- maxAdj
          maxAdj4 <- maxAdj
          #02Dec2024: if convergence fails for full (e.g., 8/8 vars) model, capture bounds of g weights 
          if (nVar==length(crimeVarsWgt) & is.null(wgts_temp)){
            log_debug("No convergence - capturing rolling upper bound for adj factor")
            temp.upper <- temp.text[2] %>%
              str_extract("(?<=and\\s{1,2})(\\d|\\.)+(?=(|\\s{1,2})$)") %>%
              as.numeric()
            log_debug(str_c("Rolling upper bound is ",temp.upper))
            #Add a bit of padding to rolling upper bound to get updated upper bound
            maxAdj2 <- min(maxAdj,temp.upper*1.25,temp.upper+0.5)
            #02Jan2024: if maxAdj2==maxAdj, go ahead and set it to half of maxAdj so we can try to find a solution - if it fails to provide even the bounds, revert back to maxAdj
            tempInd <- FALSE #Initialize indicator whether we're trying maxAdj/2
            if (maxAdj==maxAdj2){
              log_debug("Testing convergence with half of maxAdj")
              tempInd <- TRUE
              maxAdj2 <- maxAdj/2
            }
            log_debug(str_c("Updated upper bound is ",maxAdj2))
            #02Dec2024: if updated upper bound < original upper bound, try again with weights of 1 but updated upper bound
            #           Use full maxIt2 this time
            if (maxAdj2<maxAdj){
              log_debug(str_c("No convergence - trying again with upper bound of ",maxAdj2))
              cat(str_c("\nWeight group ",j,": Trying weight 1 with upper bound of ",maxAdj2," (",maxIt2/10/1000,"K iterations)"),
                  file=str_c(output_weighting_data_folder,"weights_lt1_tracker_srs.txt"),
                  append=TRUE)
              temp.text2 <- capture.output(
                wgts_temp <- gencalib(Xs=select(SF_temp,all_of(ctrlVars)),
                                      Zs=select(SF_temp,all_of(ctrlVars)),
                                      #d=rep(ratio_temp$baseWgt,nrow(SF_temp)),
                                      d=rep(ratio$baseWgt,nrow(SF_temp)),
                                      total=total_temp,
                                      method="logit",
                                      bounds=c(low=ratio$lowBound,maxAdj2),#1e6),
                                      max_iter=maxIt2/10,#1000,#10000
                                      C=1)
              ) 
              if (length(temp.text2)>=2){
                temp.upper2 <- temp.text2[2] %>%
                  str_extract("(?<=and\\s{1,2})(\\d|\\.)+(?=(|\\s{1,2})$)") %>%
                  as.numeric()
              } else if (tempInd==TRUE){
                log_debug("Reverting back to original rolling upper bound")
                temp.upper2 <- temp.upper
                maxAdj2 <- min(maxAdj,temp.upper*1.25,temp.upper+0.5)
              }
              #02Jan2025: confirm calibration before proceeding
              if (nVar==length(crimeVarsWgt) & !is.null(wgts_temp)){
                test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                         d=rep(ratio$baseWgt,nrow(SF_temp)),
                                         total=total_temp,
                                         g=wgts_temp,
                                         EPS=ifelse(any(total_temp==0),1,1e-6))#EPS=1)
                if (test$result!=TRUE){
                  log_debug("Convergence, calibration failed")
                  wgts_temp <- NULL
                } else {
                  log_debug("Calibration succeeded")
                }
              }
            }
            #05Dec2024: one last try before moving onto final weights <1
            #02Jan2025: this is now the 2nd last try (added extra step today)
            #           also, including 2nd rolling upper bound minus half difference bw it and 1st rolling upper bound
            maxAdj3 <- min(temp.upper2*1.05,temp.upper2+0.1,1.5*temp.upper2-0.5*temp.upper)
            if (nVar==length(crimeVarsWgt) & is.null(wgts_temp) & maxAdj3<maxAdj){
              log_debug(str_c("No convergence - trying again with upper bound of ",maxAdj3))
              cat(str_c("\nWeight group ",j,": Trying weight 1 with upper bound of ",maxAdj3," (",maxIt2/10/1000,"K iterations)"),
                  file=str_c(output_weighting_data_folder,"weights_lt1_tracker_srs.txt"),
                  append=TRUE)
              temp.text3 <- capture.output(
                wgts_temp <- gencalib(Xs=select(SF_temp,all_of(ctrlVars)),
                                      Zs=select(SF_temp,all_of(ctrlVars)),
                                      #d=rep(ratio_temp$baseWgt,nrow(SF_temp)),
                                      d=rep(ratio$baseWgt,nrow(SF_temp)),
                                      total=total_temp,
                                      method="logit",
                                      bounds=c(low=ratio$lowBound,maxAdj3),#1e6),
                                      max_iter=maxIt2/10,#1000,#10000
                                      C=1)
              )
              if (length(temp.text3)>=2){
                temp.upper3 <- temp.text3[2] %>%
                  str_extract("(?<=and\\s{1,2})(\\d|\\.)+(?=(|\\s{1,2})$)") %>%
                  as.numeric()
              } else {
                temp.upper3 <- temp.upper2
              }
              #02Jan2025: confirm calibration before proceeding
              if (nVar==length(crimeVarsWgt) & !is.null(wgts_temp)){
                test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                         d=rep(ratio$baseWgt,nrow(SF_temp)),
                                         total=total_temp,
                                         g=wgts_temp,
                                         EPS=ifelse(any(total_temp==0),1,1e-6))#EPS=1)
                if (test$result!=TRUE){
                  log_debug("Convergence, calibration failed")
                  wgts_temp <- NULL
                } else {
                  log_debug("Calibration succeeded")
                }
              }
            }
            #02Jan2025: adding one last try before moving onto final weights <1...
            maxAdj4 <- min(temp.upper3*0.99,1.5*temp.upper3-0.5*temp.upper2)
            #02Jan2025: just to ensure enough wiggle room
            maxAdj4 <- max(maxAdj4,1.02)
            log_debug(str_c("maxAdj4: ",maxAdj4))
            log_debug(str_c("temp.upper3: ",temp.upper3))
            if (nVar==length(crimeVarsWgt) & is.null(wgts_temp) & maxAdj4<maxAdj & temp.upper3 != maxAdj){
              
              log_debug(str_c("No convergence - trying again with upper bound of ",maxAdj4))
              cat(str_c("\nWeight group ",j,": Trying weight 1 with upper bound of ",maxAdj4," (",maxIt2/10/1000,"K iterations)"),
                  file=str_c(output_weighting_data_folder,"weights_lt1_tracker_srs.txt"),
                  append=TRUE)
              capture.output(
                wgts_temp <- gencalib(Xs=select(SF_temp,all_of(ctrlVars)),
                                      Zs=select(SF_temp,all_of(ctrlVars)),
                                      #d=rep(ratio_temp$baseWgt,nrow(SF_temp)),
                                      d=rep(ratio$baseWgt,nrow(SF_temp)),
                                      total=total_temp,
                                      method="logit",
                                      bounds=c(low=ratio$lowBound,maxAdj4),#1e6),
                                      max_iter=maxIt2/10,#1000,#10000
                                      C=1)
              )
              #02Jan2025: confirm calibration before proceeding
              if (nVar==length(crimeVarsWgt) & !is.null(wgts_temp)){
                test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                         d=rep(ratio$baseWgt,nrow(SF_temp)),
                                         total=total_temp,
                                         g=wgts_temp,
                                         EPS=ifelse(any(total_temp==0),1,1e-6))#EPS=1)
                if (test$result!=TRUE){
                  log_debug("Convergence, calibration failed")
                  wgts_temp <- NULL
                } else {
                  log_debug("Calibration succeeded")
                }
              }
            }
          }
          #21Nov2024: if coverage fails again for full model, try 0.998 then 0.99 thru 0.9 min weight in increments of 0.01
          for (temp.minAdj in c(0.998,seq(0.99,0.9,by=-0.01))){
            if (is.null(wgts_temp) & nVar==length(crimeVarsWgt)){
              log_debug(str_c("No convergence - trying again with min final weight of ",temp.minAdj,")"))
              cat(str_c("\nWeight group ",j,": Trying weight ",temp.minAdj," (",maxIt2/10/1000,"K iterations)"),
                  file=str_c(output_weighting_data_folder,"weights_lt1_tracker_srs.txt"),
                  append=TRUE)
              capture.output(
                wgts_temp <- gencalib(Xs=select(SF_temp,all_of(ctrlVars)),
                                      Zs=select(SF_temp,all_of(ctrlVars)),
                                      d=rep(ratio$baseWgt,nrow(SF_temp)),
                                      total=total_temp,
                                      method="logit",
                                      bounds=c(low=temp.minAdj*ratio$lowBound,maxAdj2),#1e6),
                                      max_iter=maxIt2/10,#1000,#10000
                                      C=1)
              )
              #02Jan2025: confirm calibration before proceeding
              if (nVar==length(crimeVarsWgt) & !is.null(wgts_temp)){
                test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                         d=rep(ratio$baseWgt,nrow(SF_temp)),
                                         total=total_temp,
                                         g=wgts_temp,
                                         EPS=ifelse(any(total_temp==0),1,1e-6))#EPS=1)
                if (test$result!=TRUE){
                  log_debug("Convergence, calibration failed")
                  wgts_temp <- NULL
                } else {
                  log_debug("Calibration succeeded")
                }
              }
            }
          }
          #Update (27AUG2021): Ensure model converges AND calibration totals hit
          if (is.null(wgts_temp)){
            log_debug("No convergence")
            wgts_temp <- matrix(nrow=nrow(SF_temp),ncol=1) %>% as.data.frame() %>%
              mutate(!!str_c("NationalWgt_nVar",nVar,"_comb",nComb) := rep(NA,nrow(SF_temp))) %>%
              select(str_c("NationalWgt_nVar",nVar,"_comb",nComb))
          } else {
            test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                     #d=rep(ratio_temp$baseWgt,nrow(SF_temp)),
                                     d=rep(ratio$baseWgt,nrow(SF_temp)),
                                     total=total_temp,
                                     g=wgts_temp,
                                     EPS=ifelse(any(total_temp==0),1,1e-6))#EPS=1)
            
            if (test$result==TRUE){
              log_debug("Success!")
              stopInd <- 1
              list2env(list("stopInd"=stopInd),tempEnv) #Update stopInd in function environment
              wgts_temp <- wgts_temp %>%
                data.frame() %>%
                dplyr::mutate(!!str_c("NationalWgt_nVar",nVar,"_comb",nComb) := .) %>%
                select(str_c("NationalWgt_nVar",nVar,"_comb",nComb))
            } else {
              log_debug("Convergence, calibration failed")
              wgts_temp <- matrix(nrow=nrow(SF_temp),ncol=1) %>% as.data.frame() %>%
                mutate(!!str_c("NationalWgt_nVar",nVar,"_comb",nComb) := rep(NA,nrow(SF_temp))) %>%
                select(str_c("NationalWgt_nVar",nVar,"_comb",nComb))
            }
          }
          
        }  else {
          #Skipping bc stopInd==1
          wgts_temp <- matrix(nrow=nrow(SF_temp),ncol=1) %>% as.data.frame() %>%
            mutate(!!str_c("NationalWgt_nVar",nVar,"_comb",nComb) := rep(NA,nrow(SF_temp))) %>%
            select(str_c("NationalWgt_nVar",nVar,"_comb",nComb))
        }
        return(wgts_temp)
        
      },simplify=FALSE) %>%
        bind_cols()
      
    },simplify=FALSE) %>%
      {bind_cols(SF_temp,.)}
    
    
    #print(out_temp)
  },simplify=FALSE) %>%
    bind_rows()
} else {#13Nov2024: added else condition
  #Create dataframe with 1 row and columns matching main frame
  #The reason we're using 1 row (vs. 0) is to make it easier to modify the dataset
  tempEnv <- environment()
  SF_temp <- data.frame(SF2_skips) %>% subset(wgtGpNational==1) %>% head(n=1)
  #Add weight columns (e.g., NationalWgt_nVar7_comb1)
  sapply(length(crimeVarsWgt):1,function(nVar){#Loop over n control total variables
    
    
    varCombs_nVar <- combn(crimeVarsWgt,m=nVar,simplify=FALSE)
    #print(varCombs_nVar)
    nVarCombs <- length(varCombs_nVar) #Number of combinations
    SF_temp[,str_c("NationalWgt_nVar",nVar,"_comb",1:nVarCombs)] <- NA_real_
    
    list2env(list("SF_temp"=SF_temp),tempEnv)
    return(NULL)
  })
  SF2_wgts2_firstGp <- inner_join(SF_temp,
                                  SF2,
                                  by=intersect(colnames(SF_temp),colnames(SF2)))
}

#####
#Combination summaries

#Update (27OCT2021): Previously was copy-pasting code chunks by number of variables in model. Create function that will streamline
combs_table_gps <- function(indat,crimeVarsWgt,inWgtGps,wgtVar,wgtGpVar,wgtGpDescVar,suffix="",nInWgtGps=length(inWgtGps),nVars=length(crimeVarsWgt)){
  log_debug("Running function combs_table_gps")
  inWgtGpsDF <- data.frame(inWgtGps)
  colnames(inWgtGpsDF) <- wgtGpVar
  out <- sapply(nVars:1,function(temp.nVar){ #Loop over number of variables from nVars down to 1
    #Combinations of crimeVarsWgt of size i
    temp.combs <- combn(crimeVarsWgt,m=temp.nVar,simplify=FALSE)
    
    temp.dat <- matrix(ncol=nVars,nrow=length(temp.combs)) %>%
      data.frame()
    colnames(temp.dat) <- crimeVarsWgt
    temp.dat <- temp.dat %>%
      mutate(nVar=temp.nVar,comb=1:length(temp.combs)) %>%
      select(nVar,comb,everything())
    #Create table
    temp.table <- sapply(1:length(temp.combs),function(i){#Loop over each combination in temp.combs
      temp.out <- temp.dat[i,]
      temp.env <- environment()
      sapply(crimeVarsWgt,function(temp.var){
        temp.out <- temp.out %>%
          mutate(!! temp.var:=case_when(temp.var %in% temp.combs[[i]] ~ "X",
                                        TRUE ~ ""))
        list2env(list("temp.out"=temp.out),temp.env)
        return(NULL)
      })
      
      #Stack row once per weighting group
      
      temp.out <- temp.out[rep(seq_len(nrow(temp.out)), each = nInWgtGps), ]  %>%
        bind_cols(inWgtGpsDF) %>%
        mutate(!!wgtGpDescVar:=factor(eval(as.symbol(wgtGpVar)),levels=wgtGps2,labels=wgtGpDescs2))
      #Note (09Jan2023): Removing totcrime_imp requirement
      temp.converge <- indat %>%
        subset(resp_ind_srs==1) %>%
        mutate(converge=!is.na(eval(as.symbol(str_c(wgtVar,"_nVar",temp.nVar,"_comb",i))))) %>%
        select(all_of(wgtGpVar),all_of(wgtGpDescVar),converge) %>%
        group_by_at(.vars=c(wgtGpVar,wgtGpDescVar)) %>%
        dplyr::summarize(converge=any(converge),
                         .groups="drop") %>%
        select(all_of(wgtGpVar),all_of(wgtGpDescVar),converge)
      
      temp.out <- temp.out %>% left_join(temp.converge,by=c(wgtGpVar,wgtGpDescVar))
    },simplify=FALSE) %>%
      bind_rows()
    return(temp.table)
  },simplify=FALSE)
  
  names(out) <- str_c("comb",nVars:1,"_table_",suffix)
  list2env(out,envir=.GlobalEnv)
  return(NULL)
}

combs_table_gps(indat=SF2_wgts2_firstGp,crimeVarsWgt,inWgtGps=wgtGps2[1],
                wgtVar="NationalWgt",wgtGpVar="wgtGpNational",wgtGpDescVar="wgtGpNationalDesc",
                suffix="firstGp")




#####
#Now, all other groups

#Switch back to 8 SRS crime variables
crimeVarsWgt <- c("totcrime_imp","totcrime_murder_imp",
                  "totcrime_rape_imp","totcrime_aggAssault_imp",
                  "totcrime_burglary_imp","totcrime_rob_imp",
                  "totcrime_larceny_imp","totcrime_vhcTheft_imp")
#Update (28OCT2021): Removing print statements
#Update (23MAR2022): Stop running after first successful convergence for weighting group
#Update (23MAR2022): Lowering max_iter from 10000 to 1000
#Update (12NOV2024): Only run for non-skipped weighting groups
temp.wgtGps <- srs_control_totals %>% pull(wgtGpNational) %>% subset(. != 1)
#SF2_wgts2_rest <- sapply(wgtGps2[2:(length(wgtGps2))],function(j){#Loop over weight groupings
SF2_wgts2_rest <- sapply(temp.wgtGps,function(j){#Loop over weight groupings
  log_debug("########################")
  log_debug(str_c("Weight group: ",j))
  #Take weighting group subset within weight group subset
  #Note (09Jan2023): Removing totcrime_imp requirement
  SF_temp <- SF2 %>%
    subset(wgtGpNational==j & resp_ind_srs==1)
  stopInd <- 0 #Initialize stop indicator to 0
  tempEnv <- environment() #Function environment
  #16May2024: changing from looping over (ncol(srs_control_totals)-3):1 to length(crimeVarsWgt):1
  sapply(length(crimeVarsWgt):1,function(nVar){#Loop over n control total variables
    #14Nov2024: vary max # of iterations by number of variables (1-7=1K, 8=1M)
    if (nVar==length(crimeVarsWgt)){
      maxIt2 <- 1e3*maxIt
    } else {
      maxIt2 <- maxIt
    }
    log_debug(str_c("Weight group: ",j,". n SRS Variables: ",nVar))
    varCombs_nVar <- combn(crimeVarsWgt,m=nVar,simplify=FALSE)
    nVarCombs <- length(varCombs_nVar) #Number of combinations
    sapply(1:nVarCombs,function(nComb){#Loop over variable combinations
      if (stopInd==0){
        log_debug("stopInd==0")
        ctrlVars <- varCombs_nVar[[nComb]]
        print(ctrlVars)
        total_temp <- srs_control_totals %>%
          subset(wgtGpNational==j) %>%
          select(all_of(str_c("sum_",ctrlVars))) %>%
          as.numeric()
        print(total_temp)
        #Note (09Jan2023): removing totcrime_imp requirement
        temp.ratio <- SF2 %>%
          subset(wgtGpNational==j) %>%
          dplyr::summarize(n=sum(1*resp_ind_srs==1),
                           N=n()) %>%
          mutate(baseWgt=N/n,
                 lowBound=n/N)
        #Update (02DEC2024): Updating max number of iterations to a 10th of maxIt2
        #Update (05Dec2024): As a first step, try a max adjustment factor of 2.5 (often works)
        capture.output(
          wgts_temp <- gencalib(Xs=select(SF_temp,all_of(ctrlVars)),
                                Zs=select(SF_temp,all_of(ctrlVars)),
                                #d=rep(ratio_temp$baseWgt,nrow(SF_temp)),
                                d=rep(ratio$baseWgt,nrow(SF_temp)),
                                total=total_temp,
                                method="logit",
                                bounds=c(low=ratio$lowBound,2.5),#1e6),
                                max_iter=maxIt2/100,#1000,#10000
                                C=1)
        )
        #29Dec2024: confirm calibration before proceeding
        if (nVar==length(crimeVarsWgt) & !is.null(wgts_temp)){
          test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                   d=rep(ratio$baseWgt,nrow(SF_temp)),
                                   total=total_temp,
                                   g=wgts_temp,
                                   EPS=ifelse(any(total_temp==0),1,1e-6))#EPS=1)
          if (test$result!=TRUE){
            log_debug("Convergence, calibration failed")
            wgts_temp <- NULL
          } else {
            log_debug("Calibration succeeded")
          }
        }
        #Update (06Dec2024): Adding new step - try max adjustment factor of 1.5
        if (nVar==length(crimeVarsWgt) & is.null(wgts_temp)){
          log_debug("No convergence - trying again with upper bound of 1.5")
          cat(str_c("\nWeight group ",j,": Trying weight 1 with upper bound of 1.5 (",maxIt2/100/1000,"K iterations)"),
              file=str_c(output_weighting_data_folder,"weights_lt1_tracker_srs.txt"),
              append=TRUE)
          capture.output(
            wgts_temp <- gencalib(Xs=select(SF_temp,all_of(ctrlVars)),
                                  Zs=select(SF_temp,all_of(ctrlVars)),
                                  #d=rep(ratio_temp$baseWgt,nrow(SF_temp)),
                                  d=rep(ratio$baseWgt,nrow(SF_temp)),
                                  total=total_temp,
                                  method="logit",
                                  bounds=c(low=ratio$lowBound,1.5),#1e6),
                                  max_iter=maxIt2/100,#1000,#10000
                                  C=1)
          )
          #02Jan2025: confirm calibration before proceeding
          if (nVar==length(crimeVarsWgt) & !is.null(wgts_temp)){
            test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                     d=rep(ratio$baseWgt,nrow(SF_temp)),
                                     total=total_temp,
                                     g=wgts_temp,
                                     EPS=ifelse(any(total_temp==0),1,1e-6))#EPS=1)
            if (test$result!=TRUE){
              log_debug("Convergence, calibration failed")
              wgts_temp <- NULL
            } else {
              log_debug("Calibration succeeded")
            }
          }
        }
        #Update (05Dec2024): If above didn't work, try with adj factor of 5
        if (nVar==length(crimeVarsWgt) & is.null(wgts_temp)){
          log_debug("No convergence - trying again with upper bound of 5")
          cat(str_c("\nWeight group ",j,": Trying weight 1 with upper bound of 5 (",maxIt2/100/1000,"K iterations)"),
              file=str_c(output_weighting_data_folder,"weights_lt1_tracker_srs.txt"),
              append=TRUE)
          capture.output(
            wgts_temp <- gencalib(Xs=select(SF_temp,all_of(ctrlVars)),
                                  Zs=select(SF_temp,all_of(ctrlVars)),
                                  #d=rep(ratio_temp$baseWgt,nrow(SF_temp)),
                                  d=rep(ratio$baseWgt,nrow(SF_temp)),
                                  total=total_temp,
                                  method="logit",
                                  bounds=c(low=ratio$lowBound,5),#1e6),
                                  max_iter=maxIt2/100,#1000,#10000
                                  C=1)
          )
          #02Jan2025: confirm calibration before proceeding
          if (nVar==length(crimeVarsWgt) & !is.null(wgts_temp)){
            test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                     d=rep(ratio$baseWgt,nrow(SF_temp)),
                                     total=total_temp,
                                     g=wgts_temp,
                                     EPS=ifelse(any(total_temp==0),1,1e-6))#EPS=1)
            if (test$result!=TRUE){
              log_debug("Convergence, calibration failed")
              wgts_temp <- NULL
            } else {
              log_debug("Calibration succeeded")
            }
          }
        }
        #Update (06Feb2025): Initializing temp.text to NA_character_
        temp.text <- NA_character_
        
        #Update (05Dec2024): If above didn't work, then proceed with usual max adj factor (e.g., 10)
        if (nVar==length(crimeVarsWgt) & is.null(wgts_temp)){
          log_debug(str_c("No convergence - trying again with upper bound of ",maxAdj))
          cat(str_c("\nWeight group ",j,": Trying weight 1 with upper bound of ",maxAdj," (",maxIt2/100/1000,"K iterations)"),
              file=str_c(output_weighting_data_folder,"weights_lt1_tracker_srs.txt"),
              append=TRUE)
          temp.text <- capture.output(
            wgts_temp <- gencalib(Xs=select(SF_temp,all_of(ctrlVars)),
                                  Zs=select(SF_temp,all_of(ctrlVars)),
                                  #d=rep(ratio_temp$baseWgt,nrow(SF_temp)),
                                  d=rep(ratio$baseWgt,nrow(SF_temp)),
                                  total=total_temp,
                                  method="logit",
                                  bounds=c(low=ratio$lowBound,maxAdj),#1e6),
                                  max_iter=maxIt2/100,#1000,#10000
                                  C=1)
          )
          #02Jan2025: confirm calibration before proceeding
          if (nVar==length(crimeVarsWgt) & !is.null(wgts_temp)){
            test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                     d=rep(ratio$baseWgt,nrow(SF_temp)),
                                     total=total_temp,
                                     g=wgts_temp,
                                     EPS=ifelse(any(total_temp==0),1,1e-6))#EPS=1)
            if (test$result!=TRUE){
              log_debug("Convergence, calibration failed")
              wgts_temp <- NULL
            } else {
              log_debug("Calibration succeeded")
            }
          }
        }
        #06Feb2025: if that fails (and no bounds were given by last run), try a variety of values bw 10 to 1.1 until we get bounds
        for (temp.maxAdj in seq(10,1.1,by=-0.1) %>% subset(!. %in% c(1.5,2.5,5,10))){
          if (length(temp.text)==0 & is.null(wgts_temp) & nVar==length(crimeVarsWgt)){
            log_debug(str_c("No convergence - trying again with upper bound of ",temp.maxAdj))
            cat(str_c("\nWeight group ",j,": Trying weight 1 with upper bound of ",temp.maxAdj," (",maxIt2/100/1000,"K iterations)"),
                file=str_c(output_weighting_data_folder,"weights_lt1_tracker_srs.txt"),
                append=TRUE)
            temp.text <- capture.output(
              wgts_temp <- gencalib(Xs=select(SF_temp,all_of(ctrlVars)),
                                    Zs=select(SF_temp,all_of(ctrlVars)),
                                    d=rep(ratio$baseWgt,nrow(SF_temp)),
                                    total=total_temp,
                                    method="logit",
                                    bounds=c(low=ratio$lowBound,temp.maxAdj),#1e6),
                                    max_iter=maxIt2/100,#1000,#10000
                                    C=1)
            )
            #02Jan2025: confirm calibration before proceeding
            if (nVar==length(crimeVarsWgt) & !is.null(wgts_temp)){
              test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                       d=rep(ratio$baseWgt,nrow(SF_temp)),
                                       total=total_temp,
                                       g=wgts_temp,
                                       EPS=ifelse(any(total_temp==0),1,1e-6))#EPS=1)
              if (test$result!=TRUE){
                log_debug("Convergence, calibration failed")
                wgts_temp <- NULL
              } else {
                log_debug("Calibration succeeded")
              }
            }
          }
        }
        
        #02Jan2025: initialize max adjustment factor variables
        temp.upper <- maxAdj
        maxAdj2 <- maxAdj
        temp.upper2 <- maxAdj
        maxAdj3 <- maxAdj
        temp.upper3 <- maxAdj
        maxAdj4 <- maxAdj
        #02Dec2024: if convergence fails for full (e.g., 8/8 vars) model, capture bounds of g weights 
        if (nVar==length(crimeVarsWgt) & is.null(wgts_temp)){
          log_debug("No convergence - capturing rolling upper bound for adj factor")
          temp.upper <- temp.text[2] %>%
            str_extract("(?<=and\\s{1,2})(\\d|\\.)+(?=(|\\s{1,2})$)") %>%
            as.numeric()
          log_debug(str_c("Rolling upper bound is ",temp.upper))
          #Add a bit of padding to rolling upper bound to get updated upper bound
          maxAdj2 <- min(maxAdj,temp.upper*1.25,temp.upper+0.5)
          #02Jan2024: if maxAdj2==maxAdj, go ahead and set it to half of maxAdj so we can try to find a solution - if it fails to provide even the bounds, revert back to maxAdj
          tempInd <- FALSE #Initialize indicator whether we're trying maxAdj/2
          if (maxAdj==maxAdj2){
            log_debug("Testing convergence with half of maxAdj")
            tempInd <- TRUE
            maxAdj2 <- maxAdj/2
          }
          log_debug(str_c("Updated upper bound is ",maxAdj2))
          #02Dec2024: if updated upper bound < original upper bound, try again with weights of 1 but updated upper bound
          #           Use full maxIt2 this time
          if (maxAdj2<maxAdj){
            log_debug(str_c("No convergence - trying again with upper bound of ",maxAdj2))
            cat(str_c("\nWeight group ",j,": Trying weight 1 with upper bound of ",maxAdj2," (",maxIt2/10/1000,"K iterations)"),
                file=str_c(output_weighting_data_folder,"weights_lt1_tracker_srs.txt"),
                append=TRUE)
            temp.text2 <- capture.output(
              wgts_temp <- gencalib(Xs=select(SF_temp,all_of(ctrlVars)),
                                    Zs=select(SF_temp,all_of(ctrlVars)),
                                    #d=rep(ratio_temp$baseWgt,nrow(SF_temp)),
                                    d=rep(ratio$baseWgt,nrow(SF_temp)),
                                    total=total_temp,
                                    method="logit",
                                    bounds=c(low=ratio$lowBound,maxAdj2),#1e6),
                                    max_iter=maxIt2/10,#1000,#10000
                                    C=1)
            ) 
            if (length(temp.text2)>=2){
              temp.upper2 <- temp.text2[2] %>%
                str_extract("(?<=and\\s{1,2})(\\d|\\.)+(?=(|\\s{1,2})$)") %>%
                as.numeric()
            } else if (tempInd==TRUE){
              log_debug("Reverting back to original rolling upper bound")
              temp.upper2 <- temp.upper
              maxAdj2 <- min(maxAdj,temp.upper*1.25,temp.upper+0.5)
            }
            #02Jan2025: confirm calibration before proceeding
            if (nVar==length(crimeVarsWgt) & !is.null(wgts_temp)){
              test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                       d=rep(ratio$baseWgt,nrow(SF_temp)),
                                       total=total_temp,
                                       g=wgts_temp,
                                       EPS=ifelse(any(total_temp==0),1,1e-6))#EPS=1)
              if (test$result!=TRUE){
                log_debug("Convergence, calibration failed")
                wgts_temp <- NULL
              } else {
                log_debug("Calibration succeeded")
              }
            }
          }
          #05Dec2024: one last try before moving onto final weights <1
          #02Jan2025: this is now the 2nd last try (added extra step today)
          #           also, including 2nd rolling upper bound minus half difference bw it and 1st rolling upper bound
          maxAdj3 <- min(temp.upper2*1.05,temp.upper2+0.1,1.5*temp.upper2-0.5*temp.upper)
          if (nVar==length(crimeVarsWgt) & is.null(wgts_temp) & maxAdj3<maxAdj){
            log_debug(str_c("No convergence - trying again with upper bound of ",maxAdj3))
            cat(str_c("\nWeight group ",j,": Trying weight 1 with upper bound of ",maxAdj3," (",maxIt2/10/1000,"K iterations)"),
                file=str_c(output_weighting_data_folder,"weights_lt1_tracker_srs.txt"),
                append=TRUE)
            temp.text3 <- capture.output(
              wgts_temp <- gencalib(Xs=select(SF_temp,all_of(ctrlVars)),
                                    Zs=select(SF_temp,all_of(ctrlVars)),
                                    #d=rep(ratio_temp$baseWgt,nrow(SF_temp)),
                                    d=rep(ratio$baseWgt,nrow(SF_temp)),
                                    total=total_temp,
                                    method="logit",
                                    bounds=c(low=ratio$lowBound,maxAdj3),#1e6),
                                    max_iter=maxIt2/10,#1000,#10000
                                    C=1)
            )
            if (length(temp.text3)>=2){
              temp.upper3 <- temp.text3[2] %>%
                str_extract("(?<=and\\s{1,2})(\\d|\\.)+(?=(|\\s{1,2})$)") %>%
                as.numeric()
            } else {
              temp.upper3 <- temp.upper2
            }		
            #02Jan2025: confirm calibration before proceeding
            if (nVar==length(crimeVarsWgt) & !is.null(wgts_temp)){
              test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                       d=rep(ratio$baseWgt,nrow(SF_temp)),
                                       total=total_temp,
                                       g=wgts_temp,
                                       EPS=ifelse(any(total_temp==0),1,1e-6))#EPS=1)
              if (test$result!=TRUE){
                log_debug("Convergence, calibration failed")
                wgts_temp <- NULL
              } else {
                log_debug("Calibration succeeded")
              }
            }
          }
          
          #02Jan2025: adding one last try before moving onto final weights <1...
          maxAdj4 <- min(temp.upper3*0.99,1.5*temp.upper3-0.5*temp.upper2)
          #02Jan2025: just to ensure enough wiggle room
          maxAdj4 <- max(maxAdj4,1.02)
          log_debug(str_c("maxAdj4: ",maxAdj4))
          log_debug(str_c("temp.upper3: ",temp.upper3))
          if (nVar==length(crimeVarsWgt) & is.null(wgts_temp) & maxAdj4<maxAdj & temp.upper3 != maxAdj){
            
            log_debug(str_c("No convergence - trying again with upper bound of ",maxAdj4))
            cat(str_c("\nWeight group ",j,": Trying weight 1 with upper bound of ",maxAdj4," (",maxIt2/10/1000,"K iterations)"),
                file=str_c(output_weighting_data_folder,"weights_lt1_tracker_srs.txt"),
                append=TRUE)
            capture.output(
              wgts_temp <- gencalib(Xs=select(SF_temp,all_of(ctrlVars)),
                                    Zs=select(SF_temp,all_of(ctrlVars)),
                                    #d=rep(ratio_temp$baseWgt,nrow(SF_temp)),
                                    d=rep(ratio$baseWgt,nrow(SF_temp)),
                                    total=total_temp,
                                    method="logit",
                                    bounds=c(low=ratio$lowBound,maxAdj4),#1e6),
                                    max_iter=maxIt2/10,#1000,#10000
                                    C=1)
            )
            #02Jan2025: confirm calibration before proceeding
            if (nVar==length(crimeVarsWgt) & !is.null(wgts_temp)){
              test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                       d=rep(ratio$baseWgt,nrow(SF_temp)),
                                       total=total_temp,
                                       g=wgts_temp,
                                       EPS=ifelse(any(total_temp==0),1,1e-6))#EPS=1)
              if (test$result!=TRUE){
                log_debug("Convergence, calibration failed")
                wgts_temp <- NULL
              } else {
                log_debug("Calibration succeeded")
              }
            }
          }
        }
        #21Nov2024: if coverage fails again for full model, try 0.998 then 0.99 thru 0.9 min weight in increments of 0.01
        for (temp.minAdj in c(0.998,seq(0.99,0.9,by=-0.01))){
          if (is.null(wgts_temp) & nVar==length(crimeVarsWgt)){
            log_debug(str_c("No convergence - trying again with min final weight of ",temp.minAdj,")"))
            cat(str_c("\nWeight group ",j,": Trying weight ",temp.minAdj," (",maxIt2/10/1000,"K iterations)"),
                file=str_c(output_weighting_data_folder,"weights_lt1_tracker_srs.txt"),
                append=TRUE)
            capture.output(
              wgts_temp <- gencalib(Xs=select(SF_temp,all_of(ctrlVars)),
                                    Zs=select(SF_temp,all_of(ctrlVars)),
                                    d=rep(ratio$baseWgt,nrow(SF_temp)),
                                    total=total_temp,
                                    method="logit",
                                    bounds=c(low=temp.minAdj*ratio$lowBound,maxAdj2),#1e6),
                                    max_iter=maxIt2/10,#1000,#10000
                                    C=1)
            )
          }
        }
        #Update (27AUG2021): Ensure model converges AND calibration totals can be hit
        if (is.null(wgts_temp)){
          log_debug("No convergence")
          wgts_temp <- matrix(nrow=nrow(SF_temp),ncol=1) %>% as.data.frame() %>%
            mutate(!!str_c("NationalWgt_nVar",nVar,"_comb",nComb) := rep(NA,nrow(SF_temp))) %>%
            select(str_c("NationalWgt_nVar",nVar,"_comb",nComb))
        } else {
          test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                   d=rep(ratio$baseWgt,nrow(SF_temp)),
                                   total=total_temp,
                                   g=wgts_temp,
                                   EPS=ifelse(any(total_temp==0),1,1e-6))#EPS=1)
          if (test$result==TRUE){
            log_debug("Success!")
            stopInd <- 1
            list2env(list("stopInd"=stopInd),tempEnv)
            wgts_temp <- wgts_temp %>%
              data.frame() %>%
              dplyr::mutate(!!str_c("NationalWgt_nVar",nVar,"_comb",nComb) := .) %>%
              select(str_c("NationalWgt_nVar",nVar,"_comb",nComb))
          } else {
            log_debug("Convergence, calibration failed")
            wgts_temp <- matrix(nrow=nrow(SF_temp),ncol=1) %>% as.data.frame() %>%
              mutate(!!str_c("NationalWgt_nVar",nVar,"_comb",nComb) := rep(NA,nrow(SF_temp))) %>%
              select(str_c("NationalWgt_nVar",nVar,"_comb",nComb))
          }
        }
      } else {
        
        #Skipping bc stopInd==1
        wgts_temp <- matrix(nrow=nrow(SF_temp),ncol=1) %>% as.data.frame() %>%
          mutate(!!str_c("NationalWgt_nVar",nVar,"_comb",nComb) := rep(NA,nrow(SF_temp))) %>%
          select(str_c("NationalWgt_nVar",nVar,"_comb",nComb))
      }
      return(wgts_temp)
      
    },simplify=FALSE) %>%
      bind_cols()
  },simplify=FALSE) %>%
    {bind_cols(SF_temp,.)}
  
  
  #print(out_temp)
},simplify=FALSE) %>%
  bind_rows()

#####
#Combination summaries

#Update (28OCT2021): Using function from above to streamline combination summaries
#13Nov2024: switching to temp.wgtGps
combs_table_gps(indat=SF2_wgts2_rest,crimeVarsWgt,inWgtGps=wgtGps2[-1],
                wgtVar="NationalWgt",wgtGpVar="wgtGpNational",wgtGpDescVar="wgtGpNationalDesc",
                suffix="rest")

#Update (12Nov2024): Some groups don't have a model that converges - for now, create row representing 0 variables (N/n)
#For first group
comb0_table_firstGp <- SF2_wgts2_firstGp %>% 
  select(wgtGpNational,wgtGpNationalDesc) %>% 
  mutate(nVar=0,
         comb=1,
         converge=TRUE)
#Since NationalWgt_nVarX_combY is g-weight, need to divide by baseWgt
SF2_wgts2_firstGp <- SF2_wgts2_firstGp %>%
  mutate(NationalWgt_nVar0_comb1=ifelse(resp_ind_srs==1 & rowSums(!is.na(select(.,matches("NationalWgt_nVar\\d"))),na.rm=TRUE)==0,
                                        1/(ratio_totcrime_imp*baseWgt),
                                        NA_real_))
#For remaining groups
comb0_table_rest <- SF2_wgts2_rest %>% 
  select(wgtGpNational,wgtGpNationalDesc) %>% 
  mutate(nVar=0,
         comb=1,
         converge=TRUE)
#Since NationalWgt_nVarX_combY is g-weight, need to divide by baseWgt
SF2_wgts2_rest <- SF2_wgts2_rest %>%
  mutate(NationalWgt_nVar0_comb1=ifelse(resp_ind_srs==1 & rowSums(!is.na(select(.,matches("NationalWgt_nVar\\d"))),na.rm=TRUE)==0,
                                        1/(ratio_totcrime_imp*baseWgt),
                                        NA_real_))

#Stack all tables together
#30May2024: realizing I didn't add the 8-variable combination for the 1st weighting group
#12Nov2024: adding size 0 combination datasets
#15Nov2024: again, only use agg_rob for 2021 (see similar comment above)
#if (as.numeric(year)<2023){
# if (as.numeric(year)==2021){
# combAll_table <- bind_rows(comb7_table_firstGp,
# comb6_table_firstGp,
# comb5_table_firstGp,
# comb4_table_firstGp,
# comb3_table_firstGp,
# comb2_table_firstGp,
# comb1_table_firstGp,
# comb0_table_firstGp,
# comb8_table_rest,
# comb7_table_rest,
# comb6_table_rest,
# comb5_table_rest,
# comb4_table_rest,
# comb3_table_rest,
# comb2_table_rest,
# comb1_table_rest,
# comb0_table_rest)
# } else {
combAll_table <- bind_rows(comb8_table_firstGp,
                           comb7_table_firstGp,
                           comb6_table_firstGp,
                           comb5_table_firstGp,
                           comb4_table_firstGp,
                           comb3_table_firstGp,
                           comb2_table_firstGp,
                           comb1_table_firstGp,
                           comb0_table_firstGp,
                           comb8_table_rest,
                           comb7_table_rest,
                           comb6_table_rest,
                           comb5_table_rest,
                           comb4_table_rest,
                           comb3_table_rest,
                           comb2_table_rest,
                           comb1_table_rest,
                           comb0_table_rest)
#}
combAll_table <- combAll_table %>%
  arrange(wgtGpNational,wgtGpNationalDesc,-converge,-nVar,comb) %>%
  group_by(wgtGpNational,wgtGpNationalDesc) %>%
  #13Nov2024: adding converge==TRUE requirement
  mutate(Select=ifelse(row_number(wgtGpNational)==1 & converge==TRUE,"X","")) %>%
  ungroup() %>%
  arrange(wgtGpNational,wgtGpNationalDesc,-nVar,comb) %>%
  mutate(Variables=#ifelse(
           #15Nov2024: switch condition from <2023 to only 2021 (see similar comment above)
           #as.numeric(year)<2023,
           # as.numeric(year)==2021,
           # apply(.,FUN=function(i){#2022 and earlier 15Nov2024: update, actually, only 2021
           # c(ifelse(i["totcrime_imp"]=="X","totcrime_imp",""),
           # ifelse(i["totcrime_murder_imp"]=="X","totcrime_murder_imp",""),
           # ifelse(i["totcrime_rape_imp"]=="X","totcrime_rape_imp",""),
           # ifelse(i["totcrime_aggAssault_imp"]=="X","totcrime_aggAssault_imp",""),
           # ifelse(i["totcrime_burglary_imp"]=="X","totcrime_burglary_imp",""),
           # ifelse(i["totcrime_rob_imp"]=="X","totcrime_rob_imp",""),
           # ifelse(i["totcrime_larceny_imp"]=="X","totcrime_larceny_imp",""),
           # ifelse(i["totcrime_vhcTheft_imp"]=="X","totcrime_vhcTheft_imp",""),
           # ifelse(i["totcrime_agg_rob_imp"]=="X","totcrime_agg_rob_imp","")
           # ) %>%
           # subset(.!="") %>%
           # str_flatten(collapse=",")},MARGIN=1),
           apply(.,FUN=function(i){#2023 and later #15Nov2024: actually, now just for 2021
             c(ifelse(i["totcrime_imp"]=="X","totcrime_imp",""),
               ifelse(i["totcrime_murder_imp"]=="X","totcrime_murder_imp",""),
               ifelse(i["totcrime_rape_imp"]=="X","totcrime_rape_imp",""),
               ifelse(i["totcrime_aggAssault_imp"]=="X","totcrime_aggAssault_imp",""),
               ifelse(i["totcrime_burglary_imp"]=="X","totcrime_burglary_imp",""),
               ifelse(i["totcrime_rob_imp"]=="X","totcrime_rob_imp",""),
               ifelse(i["totcrime_larceny_imp"]=="X","totcrime_larceny_imp",""),
               ifelse(i["totcrime_vhcTheft_imp"]=="X","totcrime_vhcTheft_imp","")#,
               #ifelse(i["totcrime_agg_rob_imp"]=="X","totcrime_agg_rob_imp","")
             ) %>%
               subset(.!="") %>%
               str_flatten(collapse=",")},MARGIN=1)) %>% #) %>%
  select(wgtGpNational,wgtGpNationalDesc,nVar,comb,
         totcrime_imp,totcrime_murder_imp,
         totcrime_rape_imp,matches("^totcrime_agg_rob_imp$"),
         totcrime_aggAssault_imp,
         totcrime_burglary_imp,totcrime_rob_imp,
         totcrime_larceny_imp,totcrime_vhcTheft_imp,Variables,everything())

#Update (14Jun2022): Switching Excel output functions (fixing overwrite bug)
#combAll_table %>%
#  list("All Combinations"=.) %>%
#  write.xlsx(file=str_c(output_weighting_data_folder,"SRS_Variable_Combination_Convergence_by_Weighting_Group_Automatic.xlsx"))
log_debug("Writing excel file SRS_Variable_Combination_Convergence_by_Weighting_Group_Automatic_SRS.xlsx")
workbook <- str_c(output_weighting_data_folder,
                  "SRS_Variable_Combination_Convergence_by_Weighting_Group_Automatic_SRS.xlsx")
wb <- createWorkbook()
addWorksheet(wb,"All Combinations")
writeData(wb,"All Combinations",combAll_table)
saveWorkbook(wb,workbook,overwrite=TRUE) 

SF2 <- SF2 %>%
  arrange(ORI)

ctrlVars <- combAll_table %>% 
  subset(Select=="X")

#21Nov2024: break if any weighting groups have less than the full list of variables
probs <- ctrlVars %>%
  mutate(prob=case_when(as.numeric(year)==2021 & wgtGpNational==1 & nVar<7 ~ TRUE,
                        nVar<8 ~ TRUE,
                        TRUE ~ FALSE)) %>%
  subset(prob==TRUE) %>%
  select(wgtGpNational,wgtGpNationalDesc,nVar,comb,
         totcrime_imp,totcrime_murder_imp,
         totcrime_rape_imp,matches("^totcrime_agg_rob_imp$"),
         totcrime_aggAssault_imp,
         totcrime_burglary_imp,totcrime_rob_imp,
         totcrime_larceny_imp,totcrime_vhcTheft_imp)
if (nrow(probs)>0){
  log_debug("1+ weighting group couldn't include all variables. See below.")
  print(probs)
  stop("Breaking program. Investigate problem weighting group(s).")
}       

#13Nov2024: changing condition for proceeding  
#if (nrow(ctrlVars)==combAll_table$wgtGpNational %>% unique() %>% length()){
if (nrow(ctrlVars)==SF2 %>% select(wgtGpNational) %>% unique() %>% nrow()){
  
  #choosing best model that converges
  ctrlInds <- combAll_table %>% 
    subset(Select=="X") %>% 
    rename_at(.vars=vars(matches("^totcrime")),.funs=~str_c(.x,"_ind")) %>%
    select(wgtGpNational,matches("_ind")) %>%
    mutate(across(matches("_ind"),~ifelse(.x!="X",0,1))) %>%
    mutate(across(matches("_ind"),~ifelse(is.na(.x),0,.x))) %>%
    arrange(wgtGpNational) %>%
    #15Nov2024: commenting out line below
    #mutate(totcrime_agg_rob_imp_ind=0) %>% #Creating dummy variable to retain same names as national & region
    #15Nov2024: switching how we handle selection of sum_totcrime_agg_rob_imp
    #           Note that by selecting rape 2x, it'll actually just select it once 
    #           (effectively not selecting anything else if outside year condition)
    select(wgtGpNational,
           totcrime_imp_ind,totcrime_murder_imp_ind,
           totcrime_rape_imp_ind,#matches("^totcrime_agg_rob_imp_ind$"),
           #ifelse(as.numeric(year)==2021,"totcrime_agg_rob_imp_ind","totcrime_rape_imp_ind"),
           totcrime_aggAssault_imp_ind,totcrime_burglary_imp_ind,
           totcrime_rob_imp_ind,totcrime_larceny_imp_ind,
           totcrime_vhcTheft_imp_ind)
  
  ctrlIndsM <- ctrlInds %>%
    select(colnames(ctrlInds)) %>%
    select(-wgtGpNational) %>%
    as.matrix()
  
  ctrlTtlsM <- srs_control_totals %>%
    arrange(wgtGpNational) %>%
    #15Nov2024: switching how we handle selection of sum_totcrime_agg_rob_imp
    #           Note that by selecting rape 2x, it'll actually just select it once 
    #           (effectively not selecting anything else if outside year condition)
    select(sum_totcrime_imp,sum_totcrime_murder_imp,
           sum_totcrime_rape_imp,#matches("^sum_totcrime_agg_rob_imp$"),
           #ifelse(as.numeric(year)==2021,"sum_totcrime_agg_rob_imp","sum_totcrime_rape_imp"),
           sum_totcrime_aggAssault_imp,sum_totcrime_burglary_imp,
           sum_totcrime_rob_imp,sum_totcrime_larceny_imp,
           sum_totcrime_vhcTheft_imp) %>%
    as.matrix()
  dim(ctrlTtlsM) %>% print()
  dim(ctrlIndsM) %>% print()
  ctrlTtlsM2 <- ctrlTtlsM*ctrlIndsM #Element-wise multiplication
  colnames(ctrlTtlsM2) <- LETTERS[1:ncol(ctrlTtlsM2)] #Would normally include 'sum_' before, but will add that later
  ctrlTtls2 <- ctrlTtlsM2 %>%
    data.frame() %>%
    mutate(wgtGpNational=ctrlInds %>% getElement("wgtGpNational")) %>%
    melt(id.vars="wgtGpNational") %>%
    dcast(formula=.~wgtGpNational+variable) %>%
    select(-.) #Drop dummy variable
  colnames(ctrlTtls2) <- str_c("sum_V",colnames(ctrlTtls2))
  
  
  colnames(ctrlTtls2) <- colnames(ctrlTtls2) %>% str_replace("^(\\w)$","sum_\\1")
  
  #Control variables
  #Note (10Jan2023): Removed totcrime_imp requirement
  ctrlIndsM <- ctrlInds %>%
    inner_join(SF2) %>%
    subset(resp_ind_srs==1) %>%
    arrange(ORI) %>%
    select(colnames(ctrlInds)) %>%
    select(-wgtGpNational) %>%
    as.matrix()
  #Note (10Jan2023): Removed totcrime_imp requirement
  ctrlVarsM <- SF2%>%
    subset(resp_ind_srs==1) %>%
    arrange(ORI) %>%
    #15Nov2024: switching how we handle selection of sum_totcrime_agg_rob_imp
    #           Note that by selecting rape 2x, it'll actually just select it once 
    #           (effectively not selecting anything else if outside year condition)
    select(totcrime_imp,totcrime_murder_imp,
           totcrime_rape_imp,#matches("^totcrime_agg_rob_imp$"),
           #ifelse(as.numeric(year)==2021,"totcrime_agg_rob_imp","totcrime_rape_imp"),
           totcrime_aggAssault_imp,totcrime_burglary_imp,
           totcrime_rob_imp,totcrime_larceny_imp,
           totcrime_vhcTheft_imp) %>%
    as.matrix()
  
  ctrlVarsM2 <- ctrlVarsM*ctrlIndsM
  colnames(ctrlVarsM2) <- LETTERS[1:ncol(ctrlVarsM2)]
  #26Nov2024: adding variables for weighting groups 13 and 17
  ctrlVars2 <- ctrlVarsM2 %>%
    data.frame() %>%
    #Note (10Jan2023): Removed totcrime_imp requirement
    mutate(ORI=SF2 %>% arrange(ORI) %>% subset(resp_ind_srs==1) %>% getElement("ORI"),
           wgtGpNational=SF2 %>% arrange(ORI) %>% subset(resp_ind_srs==1) %>% getElement("wgtGpNational")) %>%
    mutate(across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==1,1,0),.names="V1_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==4,1,0),.names="V4_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==5,1,0),.names="V5_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==6,1,0),.names="V6_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==7,1,0),.names="V7_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==8,1,0),.names="V8_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==9,1,0),.names="V9_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==10,1,0),.names="V10_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==11,1,0),.names="V11_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==13,1,0),.names="V13_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==14,1,0),.names="V14_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==15,1,0),.names="V15_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==16,1,0),.names="V16_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==17,1,0),.names="V17_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==18,1,0),.names="V18_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==19,1,0),.names="V19_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==20,1,0),.names="V20_{col}"))
  
  
  #Add on the new control totals/variables
  SF2 <- SF2 %>%
    select(-matches("^[A-Z]$")) %>%
    full_join(ctrlVars2) %>%
    select(-matches("^sum_\\w+_imp$")) %>%
    #full_join(ctrlTtls2) %>%
    arrange(ORI)
  
  
  # #par(mar=c(1,1,1,1))
  # #pdf(file=str_c(output_weighting_data_folder,"plots_National_wgtGp",j,".pdf"))
  # #capture.output({
  # SF2_wgts2 <- sapply(wgtGps2,function(j){#Loop over weight groupings
  #   print("##############################")
  #   print(str_c("Weight group: ",j))
  #   #Take weighting group subset within weight group subset
  #   
  #   SF_temp <- SF2 %>%
  #     subset(wgtGpNational==j & resp_ind_srs==1 & !is.na(totcrime_imp))
  #   
  #   
  #   temp.ctrlVars <- ctrlVars %>%
  #     subset(wgtGpNational==j) %>%
  #     .$Variables %>%
  #     str_split(pattern=",") %>%
  #     .[[1]]
  #   #Update (28OCT2021): Comment out print statement
  #   #print(temp.ctrlVars)
  #   total_temp <- srs_control_totals %>%
  #     subset(wgtGpNational==j) %>%
  #     select(all_of(str_c("sum_",temp.ctrlVars))) %>%
  #     as.numeric()
  #   print("gencalib(Xs=select(SF_temp,all_of(temp.ctrlVars)), ...:")
  #   out_temp <- gencalib(Xs=select(SF_temp,all_of(temp.ctrlVars)),
  #                        Zs=select(SF_temp,all_of(temp.ctrlVars)),
  #                        d=SF_temp$baseWgt,
  #                        total=total_temp,
  #                        method="logit",
  #                        bounds=c(low=SF_temp$lowBound,1e6),
  #                        max_iter=1000,#10000
  #                        C=2,
  #                        description=TRUE
  #   ) %>%
  #     data.frame(NationalWgt=.) %>%
  #     {bind_cols(SF_temp,.)}
  #   
  #   #Update (20AUG2021): Adding requested checks
  #   #Update (30Jun2022): Switch to table format (1 row per weight group) - commenting out old code
  #   # #Check calibration
  #   # print("checkcalibration(Xs=select(SF_temp,all_of(temp.ctrlVars)), ...:")
  #   # 
  #   # checkcalibration(Xs=select(SF_temp,all_of(temp.ctrlVars)),
  #   #                  d=rep(1,nrow(SF_temp)),
  #   #                  total=total_temp,
  #   #                  g=out_temp$NationalWgt) %>%
  #   #   print()
  #   # #Weight checks - summary, UWE, etc.
  #   # print("Distribution of weights:")
  #   # describe(out_temp$NationalWgt) %>%
  #   #   print()
  #   # print("Number of missing weights:")
  #   # sum(is.na(out_temp$NationalWgt))%>%
  #   #   print()
  #   # print("Number of weights equal to 1:")
  #   # sum(out_temp$NationalWgt == 1, na.rm=TRUE) %>%
  #   #   print()
  #   # print("Number of weights greater than 1:")
  #   # sum(out_temp$NationalWgt > 1, na.rm=TRUE) %>%
  #   #   print()
  #   # print("Number of weights less than 1:")
  #   # sum(out_temp$NationalWgt < 1, na.rm=TRUE) %>%
  #   #   print()
  #   # print("Number of weights greater than 100:")
  #   # sum(out_temp$NationalWgt > 100, na.rm=TRUE) %>%
  #   #   print()
  #   # print("UWE:")
  #   # UWE_NationalWgt <- 1+var(out_temp$NationalWgt,na.rm=TRUE)/(mean(out_temp$NationalWgt,na.rm=TRUE)^2)
  #   # UWE_NationalWgt %>%
  #   #   print()
  #   #Calibration worked (T/F)?
  #   temp.cal <- checkcalibration(Xs=select(SF_temp,all_of(temp.ctrlVars)),
  #                                d=rep(1,nrow(SF_temp)),
  #                                total=total_temp,
  #                                g=out_temp$NationalWgt) %>%
  #     .$result
  #   temp.describe <- describe(out_temp$NationalWgt)
  #   temp.quantiles <- quantile(out_temp$NationalWgt,
  #                              probs=c(0.05,0.1,0.25,0.5,0.75,0.9,0.95),
  #                              na.rm=TRUE)
  #   #Note (26Jul2022): Adding n Eligible LEAs
  #   temp.nElig <- SF2 %>%
  #     subset(wgtGpNational==j) %>%
  #     nrow()
  #   temp.nLT1 <- sum(out_temp$NationalWgt < 1 & out_temp$NationalWgt>0, na.rm=TRUE)
  #   #Note (29Jul2022): Switching from >100 to >20
  #   #temp.nGT100 <- sum(out_temp$NationalWgt > 100, na.rm=TRUE)
  #   temp.nGT20 <- sum(out_temp$NationalWgt > 20, na.rm=TRUE)
  #   temp.UWE <- 1+var(out_temp$NationalWgt,na.rm=TRUE)/(mean(out_temp$NationalWgt,na.rm=TRUE)^2)
  #   temp.out <- data.frame(wgtGpDesc=wgtGpDescs2[which(wgtGps2==j)],
  #                          calibrated=temp.cal,
  #                          #Note (26Jul2022): Changing counts - include n Eligible LEAs, n NIBRS LEAs, n NIBRS LEAs missing weights
  #                          #nOverall=as.numeric(temp.describe$counts["n"])+as.numeric(temp.describe$counts["missing"]),
  #                          nElig=temp.nElig,
  #                          nNIBRS=as.numeric(temp.describe$counts["n"])+as.numeric(temp.describe$counts["missing"]),
  #                          nMissing=as.numeric(temp.describe$counts["missing"]),
  #                          nLT1=temp.nLT1,
  #                          #nGT100=temp.nGT100,
  #                          nGT20=temp.nGT20,
  #                          UWE=sprintf(temp.UWE,fmt="%1.3f"),
  #                          Mean=sprintf(as.numeric(temp.describe$counts["Mean"]),fmt="%1.3f"),
  #                          pt05=sprintf(temp.quantiles["5%"],fmt="%1.3f"),
  #                          pt10=sprintf(temp.quantiles["10%"],fmt="%1.3f"),
  #                          pt25=sprintf(temp.quantiles["25%"],fmt="%1.3f"),
  #                          pt50=sprintf(temp.quantiles["50%"],fmt="%1.3f"),
  #                          pt75=sprintf(temp.quantiles["75%"],fmt="%1.3f"),
  #                          pt90=sprintf(temp.quantiles["90%"],fmt="%1.3f"),
  #                          pt95=sprintf(temp.quantiles["95%"],fmt="%1.3f"))
  #   colnames(temp.out) <- c("Weight Group","Calibrated",
  #                           "n Eligible LEAs","n NIBRS LEAs, Overall","n NIBRS LEAs, Missing Weight",
  #                           "n LT 1","n GT 20","UWE",#"n GT 100","UWE",
  #                           "Mean","5th Pctl","10th Pctl","25th Pctl","50th Pctl",
  #                           "75th Pctl","90th Pctl","95th Pctl")
  #   temp.out <- temp.out %>%
  #     list()
  #   names(temp.out) <- str_c("results_",j)
  #   list2env(temp.out,.GlobalEnv)
  #   return(out_temp)
  #   
  # },simplify=FALSE) %>%
  #   bind_rows()%>%
  #   full_join(SF2,by=colnames(SF2))
  # #},file=str_c(output_weighting_data_folder,'weights_national_checks.txt'),
  # #type="output")
  #Note (10Jan2023): Removed totcrime_imp requirement
  SF_temp <- SF2 %>%
    subset(resp_ind_srs==1)
  
  #13Nov2024: adding requirement that columns are in ctrlTtls2
  temp.ctrlVars <- colnames(SF_temp) %>% 
    str_subset("^V\\d+_\\w$") %>% 
    intersect(colnames(ctrlTtls2) %>% str_remove("sum_"))
  #Update (28OCT2021): Comment out print statement
  #print(temp.ctrlVars)
  total_temp <- ctrlTtls2 %>%
    select(all_of(str_c("sum_",temp.ctrlVars))) %>%
    as.numeric()
  #names(total_temp) <- NULL
  vars_temp <- SF_temp %>%
    select(all_of(temp.ctrlVars)) 
  #names(vars_temp) <- NULL
  
  #Update (04Jun2024): Don't redo calibration, just use weights from earlier
  # print("gencalib(Xs=select(SF_temp,all_of(temp.ctrlVars)), ...:")
  # SF2_wgts2 <- gencalib(Xs=vars_temp,
  # Zs=vars_temp,
  # #d=rep(1,nrow(SF_temp)),
  # d=rep(ratio$baseWgt,nrow(SF_temp)),
  # total=total_temp,
  # method="logit",
  # #bounds=c(low=1,1e6),
  # bounds=c(low=ratio$lowBound,maxAdj),#1e6),
  # max_iter=5*maxIt,#1000,#10000
  # C=1,
  # description=TRUE
  # ) %>%
  # data.frame(gWgt=.) %>%
  # mutate(NationalWgt=gWgt*ratio$baseWgt) %>%
  # {bind_cols(SF_temp,.)} %>%
  # full_join(SF2,by=colnames(SF2))
  
  #03Jul2024: Splitting out into SF2_wgts2 (which contains nonrespondents) and SF_temp_wgts2 (which doesn't contain nonrespondents)
  SF2_wgts2 <- SF2_wgts2_firstGp %>%
    bind_rows(SF2_wgts2_rest) %>%
    #subset(resp_ind_srs==1) %>%
    mutate(gWgt=select(.,matches("NationalWgt_nVar\\d")) %>% rowMeans(na.rm=TRUE)) %>%
    mutate(NationalWgt=gWgt*baseWgt) %>%
    select(ORI,gWgt,NationalWgt) %>%
    right_join(SF_temp)
  
  SF_temp_wgts <- SF2_wgts2 %>%
    subset(resp_ind_srs==1) 
  
  print("Check calibration on full model")
  checkcalibration(Xs=select(SF2_wgts2,all_of(temp.ctrlVars)) %>% as.matrix(),
                   d=rep(ratio$baseWgt,nrow(SF2_wgts2)),
                   total=total_temp,
                   g=SF2_wgts2$gWgt,
                   EPS=ifelse(any(total_temp==0),1,1e-6)) %>% #EPS=1) %>%
    print()
  #13Nov2024: switch from looping over every weighting group (which may be skipped) to only those that aren't skipped
  temp.wgtGps <- srs_control_totals %>%
    pull(wgtGpNational)
  #sapply(wgtGps2,function(j){#Loop over weight groupings
  sapply(temp.wgtGps,function(j){#Loop over weight groupings
    print("##############################")
    print(str_c("Weight group: ",j))
    #Take weighting group subset within weight group subset
    #Note (10Jan2023): Removed totcrime_imp requirement
    SF_temp <- SF2_wgts2 %>%
      subset(wgtGpNational==j & resp_ind_srs==1)
    
    
    temp.ctrlVars <- colnames(SF_temp) %>% str_subset(str_c("^V",j,"_\\w$"))
    #Update (28OCT2021): Comment out print statement
    #print(temp.ctrlVars)
    total_temp <- ctrlTtls2 %>%
      select(all_of(str_c("sum_",temp.ctrlVars))) %>%
      as.numeric()
    #print(total_temp)
    out_temp <- SF_temp
    # print(out_temp %>% select(ORI,UCR_AGENCY_NAME,wgtGpNational,matches("totcrime"),matches(str_c("V",j,"_w$"))) %>% head())
    #Update (20AUG2021): Adding requested checks
    #Update (30Jun2022): Switch to table format (1 row per weight group) - commenting out old code
    #Update (16May2024): added min and max to checks
    # #Check calibration
    # print("checkcalibration(Xs=select(SF_temp,all_of(temp.ctrlVars)), ...:")
    # 
    # checkcalibration(Xs=select(SF_temp,all_of(temp.ctrlVars)),
    #                  d=rep(1,nrow(SF_temp)),
    #                  total=total_temp,
    #                  g=out_temp$NationalWgt) %>%
    #   print()
    # #Weight checks - summary, UWE, etc.
    # print("Distribution of weights:")
    # describe(out_temp$NationalWgt) %>%
    #   print()
    # print("Number of missing weights:")
    # sum(is.na(out_temp$NationalWgt))%>%
    #   print()
    # print("Number of weights equal to 1:")
    # sum(out_temp$NationalWgt == 1, na.rm=TRUE) %>%
    #   print()
    # print("Number of weights greater than 1:")
    # sum(out_temp$NationalWgt > 1, na.rm=TRUE) %>%
    #   print()
    # print("Number of weights less than 1:")
    # sum(out_temp$NationalWgt < 1, na.rm=TRUE) %>%
    #   print()
    # print("Number of weights greater than 100:")
    # sum(out_temp$NationalWgt > 100, na.rm=TRUE) %>%
    #   print()
    # print("UWE:")
    # UWE_NationalWgt <- 1+var(out_temp$NationalWgt,na.rm=TRUE)/(mean(out_temp$NationalWgt,na.rm=TRUE)^2)
    # UWE_NationalWgt %>%
    #   print()
    #Calibration worked (T/F)?
    temp.cal <- checkcalibration(Xs=select(SF_temp,all_of(temp.ctrlVars)),
                                 #d=rep(1,nrow(SF_temp)),
                                 d=rep(ratio$baseWgt,nrow(SF_temp)),
                                 total=total_temp,
                                 g=out_temp$gWgt,
                                 EPS=ifelse(any(total_temp==0),1,1e-6)) %>%
      .$result
    temp.describe <- describe(out_temp$NationalWgt)
    temp.quantiles <- quantile(out_temp$NationalWgt,
                               probs=c(0,0.05,0.1,0.25,0.5,0.75,0.9,0.95,1),
                               na.rm=TRUE)
    #Note (26Jul2022): Adding n Eligible LEAs
    temp.nElig <- SF2 %>%
      subset(wgtGpNational==j) %>%
      nrow()
    #Note (16May2024): rounding weight to 6 digits before checking if <1 (to avoid false flags)
    temp.nLT1 <- sum(round(out_temp$NationalWgt,digits=6) < 1 & out_temp$NationalWgt>0, na.rm=TRUE)
    #Note (02Jan2025): Adding n LEAs with weights < 0.9
    temp.nLT0pt9 <- sum(round(out_temp$NationalWgt,digits=6) < 0.9 & out_temp$NationalWgt>0, na.rm=TRUE)
    #Note (29Jul2022): Switching from >100 to >20
    #temp.nGT100 <- sum(out_temp$NationalWgt > 100, na.rm=TRUE)
    temp.nGT20 <- sum(out_temp$NationalWgt > 20, na.rm=TRUE)
    temp.UWE <- 1+var(out_temp$NationalWgt,na.rm=TRUE)/(mean(out_temp$NationalWgt,na.rm=TRUE)^2)
    temp.out <- data.frame(wgtGpDesc=wgtGpDescs2[which(wgtGps2==j)],
                           calibrated=temp.cal,
                           #Note (26Jul2022): Changing counts - include n Eligible LEAs, n NIBRS LEAs, n NIBRS LEAs missing weights
                           #nOverall=as.numeric(temp.describe$counts["n"])+as.numeric(temp.describe$counts["missing"]),
                           nElig=temp.nElig,
                           nNIBRS=as.numeric(temp.describe$counts["n"])+as.numeric(temp.describe$counts["missing"]),
                           nMissing=as.numeric(temp.describe$counts["missing"]),
                           nLT1=temp.nLT1,
                           nLT0pt9=temp.nLT0pt9,
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
    colnames(temp.out) <- c("Weight Group","Calibrated",
                            "n Eligible LEAs","n NIBRS LEAs, Overall","n NIBRS LEAs, Missing Weight",
                            "n LT 1","n LT 0.9","n GT 20","UWE",#"n GT 100","UWE",
                            "Mean","Minimum","5th Pctl","10th Pctl","25th Pctl","50th Pctl",
                            "75th Pctl","90th Pctl","95th Pctl","Maximum")
    temp.out <- temp.out %>%
      list()
    names(temp.out) <- str_c("results_",j)
    list2env(temp.out,.GlobalEnv)
    return(NULL)
    
  })
  
  
  #Note (JDB 06Jul2022): Combine weight check results
  #Note (JDB 13Nov2024): Only get for non-skipped weight groups
  results_national <- mget(str_c("results_",temp.wgtGps)) %>% #wgtGps2)) %>%
    bind_rows()
  
  
  #dev.off() 
  
  
  
  ###############
  #Output
  
  #03Jul2024: for whatever reason, the nonrepondents have started falling out of the weights - let's add any missing records here
  #12Nov2024: adding skipped weighting groups back in
  new_weights <- bind_rows(SF2_wgts2)  %>%
    right_join(SF2 %>% 
                 select("ORI_universe","wgtGpNational","wgtGpNationalDesc")) %>%
    bind_rows(SF2_skips)
  
  ### export for others to start writing functions to analyze bias, MSE, etc.
  new_weights[,c("ORI_universe","wgtGpNational","wgtGpNationalDesc",
                 "NationalWgt")] %>%
    #write.csv(str_c(output_weighting_data_folder,'weights_national.csv'),
    fwrite_wrapper(str_c(output_weighting_data_folder,'weights_national_srs.csv'))
  
  #Update (26AUG2021): Add wgtGpNational and wgtGpNationalDesc to SF file from 02_Weights_Data_Setup
  #Update (06Oct2022): Switching from read_csv() to fread()
  oldSF <- fread(str_c(input_weighting_data_folder,"SF_national_srs.csv"))%>%
    #Adding just in case already on file...
    select(-matches("wgtGpNational"))
  newSF <- oldSF %>%
    left_join(bind_rows(SF2,SF2_skips) %>% 
                select(ORI_universe,wgtGpNational,wgtGpNationalDesc,matches("^V\\d+_\\w$")),
              by=c("ORI_universe"))
  
  #write_csv(newSF,file=str_c(output_weighting_data_folder,"SF_postN.csv"))
  fwrite_wrapper(newSF,str_c(output_weighting_data_folder,"SF_national_postN_srs.csv"))
  
  #Note (JDB 06Jul2022): Export weight check results
  #write_csv(results_national,
  fwrite_wrapper(results_national, 
                 str_c(output_weighting_data_folder,"weights_national_checks_srs.csv"))
} else {
  stop("No calibration model converged for 1+ weighting group")
}
log_info("Finished 03_Weights_Calibration_National_SRS.R\n\n")