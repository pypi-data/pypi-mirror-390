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
library(tidyverse)
library(openxlsx)
library(lubridate)
library(sampling)
library(Hmisc)

log_info("Running 03_Weights_Calibration_National.R")

# read in SF data

SF <- paste0(paste0(input_weighting_data_folder,"SF.csv")) %>%
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
  mutate(wgtGp=case_when(POPULATION_GROUP_DESC=="Cities 1,000,000 or over" ~ 1,
                         POPULATION_GROUP_DESC=="Cities from 500,000 thru 999,999" ~ 2,
                         POPULATION_GROUP_DESC=="Cities from 250,000 thru 499,999" ~ 3,
                         POPULATION_GROUP_DESC=="Cities from 100,000 thru 249,999" ~ 4,
                         POPULATION_GROUP_DESC=="Cities from 50,000 thru 99,999" ~ 5,
                         POPULATION_GROUP_DESC=="Cities from 25,000 thru 49,999" ~ 6,
                         POPULATION_GROUP_DESC=="Cities from 10,000 thru 24,999" ~ 7,
                         POPULATION_GROUP_DESC %in% c("Cities from 2,500 thru 9,999","Cities under 2,500") & POPULATION> 0 ~ 8,
                         
                         POPULATION_GROUP_DESC=="MSA counties 100,000 or over" ~ 9,
                         POPULATION_GROUP_DESC=="MSA counties from 25,000 thru 99,999" ~ 10,
                         POPULATION_GROUP_DESC=="MSA counties from 10,000 thru 24,999" ~ 11,
                         POPULATION_GROUP_DESC=="MSA counties under 10,000" &  POPULATION> 0 ~ 12,
                         POPULATION_GROUP_DESC=="MSA State Police" & POPULATION>0 ~ 13,
                         
                         POPULATION_GROUP_DESC %in% c("Non-MSA counties from 25,000 thru 99,999","Non-MSA counties 100,000 or over") ~ 14,
                         POPULATION_GROUP_DESC=="Non-MSA counties from 10,000 thru 24,999" ~ 15,
                         POPULATION_GROUP_DESC=="Non-MSA counties under 10,000" & POPULATION >0 ~ 16,
                         POPULATION_GROUP_DESC=="Non-MSA State Police" & POPULATION>0 ~ 17,
                         
                         POPULATION_GROUP_DESC=="Cities under 2,500" & POPULATION==0 ~ 18,
                         POPULATION_GROUP_DESC %in% c("MSA counties under 10,000","MSA State Police") & POPULATION==0 ~ 19,
                         POPULATION_GROUP_DESC %in% c("Non-MSA counties under 10,000","Non-MSA State Police") & POPULATION==0 ~ 20),
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



#Get totals by weighting group
srs_control_totals <- SF2 %>%
  group_by(wgtGpNational,wgtGpNationalDesc) %>%
  dplyr::summarize(across(all_of(crimeVarsWgt),.fns=list("sum"=sum),.names="{fn}_{col}",na.rm=TRUE),
                   .groups="drop")

SF2 <- SF2 %>%
  left_join(srs_control_totals,by=c("wgtGpNational","wgtGpNationalDesc")) %>%
  mutate(k=sum_totcrime_aggAssault_imp/sum_totcrime_rob_imp) %>%
  mutate(totcrime_agg_rob_imp=totcrime_aggAssault_imp+k*totcrime_rob_imp)

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
ratio <- SF2 %>%
  dplyr::summarize(n=sum(resp_ind_m3==1),
                   N=n()) %>%
  mutate(baseWgt=N/n,
         lowBound=n/N)
SF2 <- SF2 %>%
  select(-matches("sum_totcrime")) %>%
  inner_join(srs_control_totals) %>%
  select(-matches("^(n|N|baseWgt|lowBound)$")) %>%
  bind_cols(ratio)
#######################
#Check convergence

#30Apr2025: switching from a section for 1st weighting group then the rest 
#           to now being a single section


#Note (05May2025): Creating a rolling version of our frame that will have the collapsed weighting groups on it
#                  Also, convert weight group to character here and for our control totals
SF_national_temp <- SF2 %>%
  mutate(wgtGpNational=as.character(wgtGpNational))

srs_control_totals_temp <- srs_control_totals %>%
  mutate(wgtGpNational=as.character(wgtGpNational))

#05May2025: Initialize a rolling list of weight groups
#           For instance, it will track any collapsing done
temp.wgtGpsInfo <- data.frame(wgtGp=as.character(wgtGps2),
                              wgtGpDesc=wgtGpDescs2) %>%
  #Limit to weighting groups that occur
  inner_join(SF_national_temp %>% 
               select(wgtGp=wgtGpNational) %>%
               unique()) %>%
  mutate(#wgtGp=as.character(wgtGp),
    wgtGpSort=as.numeric(wgtGp),
    wgtGpSuper=case_when(
      #This will be super group which we prefer to collapse within
      as.numeric(wgtGp) %in% 1:8 ~ 1, #>0 pop cities
      as.numeric(wgtGp) %in% 9:11 ~ 2, #>0 pop MSA county/SP,
      as.numeric(wgtGp) %in% 14:16 ~ 3, #>0 pop non-MSA county/SP
      as.numeric(wgtGp) %in% 18 ~ 4, #0 pop cities
      as.numeric(wgtGp) %in% 19 ~ 5, #0 pop MSA county/SP
      as.numeric(wgtGp) %in% 20 ~ 6 #0 pop non-MSA county/SP
    ),
    wgtGpSuper=as.character(wgtGpSuper),
    success=FALSE) %>%
  arrange(wgtGpSuper,wgtGpSort)


#15May2025: create text file that will track any allow weights <1
cat("Initializing",
    file=str_c(output_weighting_data_folder,"weights_lt1_tracker_national.txt"))

#Update (28OCT2021): Removing print statements
#Update (23MAR2022): Stop running after first successful convergence for weighting group
#Update (23MAR2022): Lowering max_iter from 10000 to 1000
SF2_wgts2_all <- sapply(wgtGps2,function(j){#Loop over weight groupings
  log_debug("Running function SF2_wgts2_firstGp")
  log_debug("########################")
  log_debug(paste0("Weight group: ",j))
  #Take weighting group subset within weight group subset
  #Note (09Jan2023): Removing totcrime_imp requirement
  #Note (05May2025): Start from our rolling frame
  SF_temp <- get("SF_national_temp",envir=.GlobalEnv) %>%
    subset(wgtGpNational==j & resp_ind_m3==1)
  
  #05May2025: extract info for current weighting group
  temp.wgtGpInfo <- get("temp.wgtGpsInfo",envir=.GlobalEnv) %>%
    subset(wgtGp==j)
  
  #05May2025: adding a condition for if no LEAs in weighting group (e.g., due to collapsing)
  if (nrow(SF_temp)==0){
    log_debug("No LEAs in weighting group")
    return(NULL)
  }
  #05May2025: creating stop indicator for whether group was able to succeed with the full set of SRS variables (will collapse if not)
  stopAll <- FALSE
  while (stopAll==FALSE){
    tempEnv <- environment() #Function environment
    
    #Get weighting group info from relevant environment
    temp.wgtGpsInfo <- get("temp.wgtGpsInfo",envir=tempEnv) %>%
      arrange(wgtGpSuper,wgtGpSort)
    
    SF_temp <- get("SF_national_temp",envir=tempEnv) %>%
      subset(wgtGpNational==j & resp_ind_m3==1)
    
    #30Apr2025: extract info for current weighting group
    temp.wgtGpInfo <- temp.wgtGpsInfo %>%
      subset(wgtGp==j)
    
    temp.wgtGps <- temp.wgtGpsInfo$wgtGp
    
    #15May2024: changing variables to match other weighting groups for 2023 onward
    #30Apr2025: move this from before the calibration function to within
    if (as.numeric(year)<2023 & j=="1"){
      crimeVarsWgtRest <- c("totcrime_imp","totcrime_murder_imp","totcrime_rape_imp",
                            "totcrime_agg_rob_imp","totcrime_burglary_imp",
                            "totcrime_larceny_imp","totcrime_vhcTheft_imp")
    } else {
      crimeVarsWgtRest <- c("totcrime_imp","totcrime_murder_imp","totcrime_rape_imp",
                            "totcrime_aggAssault_imp","totcrime_burglary_imp",
                            "totcrime_rob_imp","totcrime_larceny_imp",  
                            "totcrime_vhcTheft_imp")
    }
    crimeVarsWgtAll <- NULL
    crimeVarsWgt <- c(crimeVarsWgtAll,crimeVarsWgtRest)
    
    stopInd <- 0 #Initialize stop indicator to 0
    #16May2024: changing from looping over (ncol(srs_control_totals)-4):1 to length(crimeVarsWgt):1
    #05May2025: only try # of vars in crimeVarsWgt
    out_temp <- sapply(length(crimeVarsWgt),function(nVar){
      #05May2025: bumping up the max # of iterations to 1K original number
      maxIt2 <- 1e3*maxIt
      log_debug(paste0("Weight group: ",j,". n SRS Variables: ",nVar))
      varCombs_nVar <- combn(crimeVarsWgt,m=nVar,simplify=FALSE)
      print(varCombs_nVar)
      nVarCombs <- length(varCombs_nVar) #Number of combinations
      print(nVarCombs)
      sapply(1:nVarCombs,function(nComb){#Loop over variable combinations
        if (stopInd==0){
          log_debug("stopInd==0")
          ctrlVars <- varCombs_nVar[[nComb]]
          print(ctrlVars)
          
          total_temp <- srs_control_totals_temp %>%
            subset(wgtGpNational==j) %>%
            select(all_of(paste0("sum_",ctrlVars))) %>%
            as.numeric()
          #print(total_temp)
          #10Jan2023: removing totcrime_imp requirement
          #05May2025: we weren't actually using this anyway - commenting out
          #ratio_temp <- SF2 %>%
          #  subset(wgtGpNational==j) %>%
          #  dplyr::summarize(n=sum(1*resp_ind_m3==1),
          #				   N=n()) %>%
          #  mutate(baseWgt=N/n,
          #		 lowBound=n/N)
          
          
          #05May2025: due to # of times we'll try to calibrate the weights (with small tweaks), 
          #             let's create a function that will make this simpler
          calWgts <- function(dat,ctrlVars,totals=total_temp,
                              lowBound=dat$lowBound %>% unique(),
                              upBound=10,maxIter=maxIt){
            gencalib(Xs=select(dat,all_of(ctrlVars)),
                     Zs=select(dat,all_of(ctrlVars)),
                     #d=rep(ratio_temp$baseWgt,nrow(SF_temp)),
                     d=pull(dat,baseWgt),
                     total=totals,
                     method="logit",
                     bounds=c(lowBound,upBound),#1e6),
                     max_iter=maxIter,
                     C=1)
          }
          
          #Update (29OCT2021): Suppress warnings about calibration
          #Update (04JUN2024): Changing lower bound from lowBound to 0.5 for 2022
          #Update (05MAY2025): Actually, let's solve this via collapsing (and attempting various lower/upper bounds)
          #Update (05MAY2025): As a first step, try a max adjustment factor of 2.5 (often works)
          #Update (05May2025): Plugging in new calibration function
          capture.output(
            wgts_temp <- calWgts(SF_temp,ctrlVars,upBound=2.5,maxIter=maxIt2/100)
          )
          #29Dec2024: confirm calibration before proceeding
          if (nVar==length(crimeVarsWgtRest) & !is.null(wgts_temp)){
            test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                     d=pull(SF_temp,baseWgt),
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
          #Update (05May2025): Try max adjustment factor of 1.5
          if (nVar==length(crimeVarsWgtRest) & is.null(wgts_temp)){
            log_debug("No convergence - trying again with upper bound of 1.5")
            cat(str_c("\nWeight group ",j,": Trying weight 1 with upper bound of 1.5 (",maxIt2/100/1000,"K iterations)"),
                file=str_c(output_weighting_data_folder,"weights_lt1_tracker_srs.txt"),
                append=TRUE)
            #Update (05May2025): Plugging in new calibration function
            capture.output(
              wgts_temp <- calWgts(SF_temp,ctrlVars,upBound=1.5,maxIter=maxIt2/100)
            )
            
            #05May2025: confirm calibration before proceeding
            if (nVar==length(crimeVarsWgtRest) & !is.null(wgts_temp)){
              test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                       d=pull(SF_temp,baseWgt),
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
          #Update (05May2025): If above didn't work, try with adj factor of 5
          if (nVar==length(crimeVarsWgtRest) & is.null(wgts_temp)){
            log_debug("No convergence - trying again with upper bound of 5")
            cat(str_c("\nWeight group ",j,": Trying weight 1 with upper bound of 5 (",maxIt2/100/1000,"K iterations)"),
                file=str_c(output_weighting_data_folder,"weights_lt1_tracker_srs.txt"),
                append=TRUE)
            #Update (05May2025): Plugging in new calibration function
            capture.output(
              wgts_temp <- calWgts(SF_temp,ctrlVars,upBound=5,maxIter=maxIt2/100)
            )
            
            #05May2025: confirm calibration before proceeding
            if (nVar==length(crimeVarsWgtRest) & !is.null(wgts_temp)){
              test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                       d=pull(SF_temp,baseWgt),
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
          
          #Update (05May2025): Initializing temp.text to NA_character_
          temp.text <- NA_character_
          
          #Update (05May2025): If above didn't work, then proceed with usual max adj factor (e.g., 10)
          if (nVar==length(crimeVarsWgtRest) & is.null(wgts_temp)){
            log_debug(str_c("No convergence - trying again with upper bound of ",maxAdj))
            cat(str_c("\nWeight group ",j,": Trying weight 1 with upper bound of ",maxAdj," (",maxIt2/100/1000,"K iterations)"),
                file=str_c(output_weighting_data_folder,"weights_lt1_tracker_srs.txt"),
                append=TRUE)
            #Update (05May2025): Plugging in new calibration function
            temp.text <- capture.output(
              wgts_temp <- calWgts(SF_temp,ctrlVars,upBound=maxAdj,maxIter=maxIt2/100)
            )
            #05May2025: confirm calibration before proceeding
            if (nVar==length(crimeVarsWgtRest) & !is.null(wgts_temp)){
              test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                       d=pull(SF_temp,baseWgt),
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
          #05May2025: if that fails (and no bounds were given by last run), try a variety of values bw 10 to 1.1 until we get bounds
          for (temp.maxAdj in seq(10,1.1,by=-0.1) %>% subset(!. %in% c(1.5,2.5,5,10))){
            if (length(temp.text)==0 & is.null(wgts_temp) & nVar==length(crimeVarsWgtRest)){
              log_debug(str_c("No convergence - trying again with upper bound of ",temp.maxAdj))
              cat(str_c("\nWeight group ",j,": Trying weight 1 with upper bound of ",temp.maxAdj," (",maxIt2/100/1000,"K iterations)"),
                  file=str_c(output_weighting_data_folder,"weights_lt1_tracker_srs.txt"),
                  append=TRUE)
              #Update (05May2025): Plugging in new calibration function
              temp.text <- capture.output(
                wgts_temp <- calWgts(SF_temp,ctrlVars,upBound=temp.maxAdj,maxIter=maxIt2/100)
              )
              
              #05May2025: confirm calibration before proceeding
              if (nVar==length(crimeVarsWgtRest) & !is.null(wgts_temp)){
                test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                         d=pull(SF_temp,baseWgt),
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
          
          #05May2025: initialize max adjustment factor variables
          temp.upper <- maxAdj
          maxAdj2 <- maxAdj
          temp.upper2 <- maxAdj
          maxAdj3 <- maxAdj
          temp.upper3 <- maxAdj
          maxAdj4 <- maxAdj
          #05May2025: if convergence fails for full (e.g., 8/8 vars) model, capture bounds of g weights 
          if (nVar==length(crimeVarsWgtRest) & is.null(wgts_temp)){
            log_debug("No convergence - capturing rolling upper bound for adj factor")
            temp.upper <- temp.text[2] %>%
              str_extract("(?<=and\\s{1,2})(\\d|\\.)+(?=(|\\s{1,2})$)") %>%
              as.numeric()
            log_debug(str_c("Rolling upper bound is ",temp.upper))
            #Add a bit of padding to rolling upper bound to get updated upper bound
            #05May2025: adding na.rm=TRUE to min()
            maxAdj2 <- min(maxAdj,temp.upper*1.25,temp.upper+0.5,na.rm=TRUE)
            #05May2025: if maxAdj2==maxAdj, go ahead and set it to half of maxAdj so we can try to find a solution - if it fails to provide even the bounds, revert back to maxAdj
            tempInd <- FALSE #Initialize indicator whether we're trying maxAdj/2
            if (maxAdj==maxAdj2){
              log_debug("Testing convergence with half of maxAdj")
              tempInd <- TRUE
              maxAdj2 <- maxAdj/2
            }
            log_debug(str_c("Updated upper bound is ",maxAdj2))
            #05May2025: if updated upper bound < original upper bound, try again with weights of 1 but updated upper bound
            #           Use full maxIt2 this time
            if (maxAdj2<maxAdj){
              log_debug(str_c("No convergence - trying again with upper bound of ",maxAdj2))
              cat(str_c("\nWeight group ",j,": Trying weight 1 with upper bound of ",maxAdj2," (",maxIt2/10/1000,"K iterations)"),
                  file=str_c(output_weighting_data_folder,"weights_lt1_tracker_srs.txt"),
                  append=TRUE)
              #Update (05May2025): Plugging in new calibration function
              temp.text2 <- capture.output(
                wgts_temp <- calWgts(SF_temp,ctrlVars,upBound=maxAdj2,maxIter=maxIt2/10)
              )
              if (length(temp.text2)>=2){
                temp.upper2 <- temp.text2[2] %>%
                  str_extract("(?<=and\\s{1,2})(\\d|\\.)+(?=(|\\s{1,2})$)") %>%
                  as.numeric()
              } else if (tempInd==TRUE){
                log_debug("Reverting back to original rolling upper bound")
                temp.upper2 <- temp.upper
                #05May2025: adding na.rm=TRUE to min()
                maxAdj2 <- min(maxAdj,temp.upper*1.25,temp.upper+0.5,na.rm=TRUE)
              }
              #05May2025: confirm calibration before proceeding
              if (nVar==length(crimeVarsWgtRest) & !is.null(wgts_temp)){
                test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                         d=pull(SF_temp,baseWgt),
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
            #05May2025: 2nd to last try
            #           also, including 2nd rolling upper bound minus half difference bw it and 1st rolling upper bound
            #           (ensuring maxAdj3 is at least 1.05)
            maxAdj3 <- min(temp.upper2*1.05,temp.upper2+0.1,1.5*temp.upper2-0.5*temp.upper,na.rm=TRUE) %>%
              max(1.05)
            if (nVar==length(crimeVarsWgtRest) & is.null(wgts_temp) & maxAdj3<maxAdj){
              log_debug(str_c("No convergence - trying again with upper bound of ",maxAdj3))
              cat(str_c("\nWeight group ",j,": Trying weight 1 with upper bound of ",maxAdj3," (",maxIt2/10/1000,"K iterations)"),
                  file=str_c(output_weighting_data_folder,"weights_lt1_tracker_srs.txt"),
                  append=TRUE)
              #Update (05May2025): Plugging in new calibration function
              temp.text3 <- capture.output(
                wgts_temp <- calWgts(SF_temp,ctrlVars,upBound=maxAdj3,maxIter=maxIt2/10)
              )
              if (length(temp.text3)>=2){
                temp.upper3 <- temp.text3[2] %>%
                  str_extract("(?<=and\\s{1,2})(\\d|\\.)+(?=(|\\s{1,2})$)") %>%
                  as.numeric()
              } else {
                temp.upper3 <- temp.upper2
              }
              #05May2025: confirm calibration before proceeding
              if (nVar==length(crimeVarsWgtRest) & !is.null(wgts_temp)){
                test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                         d=pull(SF_temp,baseWgt),
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
            #05May2025: adding one last try before moving onto final weights <1...
            maxAdj4 <- min(temp.upper3*0.99,1.5*temp.upper3-0.5*temp.upper2,na.rm=TRUE)
            #05May2025: just to ensure enough wiggle room
            maxAdj4 <- max(maxAdj4,1.02)
            log_debug(str_c("maxAdj4: ",maxAdj4))
            log_debug(str_c("temp.upper3: ",temp.upper3))
            if (nVar==length(crimeVarsWgtRest) & is.null(wgts_temp) & maxAdj4<maxAdj & temp.upper3 != maxAdj){
              
              log_debug(str_c("No convergence - trying again with upper bound of ",maxAdj4))
              cat(str_c("\nWeight group ",j,": Trying weight 1 with upper bound of ",maxAdj4," (",maxIt2/10/1000,"K iterations)"),
                  file=str_c(output_weighting_data_folder,"weights_lt1_tracker_srs.txt"),
                  append=TRUE)
              #Update (05May2025): Plugging in new calibration function
              capture.output(
                wgts_temp <- calWgts(SF_temp,ctrlVars,upBound=maxAdj4,maxIter=maxIt2/10)
              )
              #05May2025: confirm calibration before proceeding
              if (nVar==length(crimeVarsWgtRest) & !is.null(wgts_temp)){
                test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                         d=pull(SF_temp,baseWgt),
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
          #05May2025: if coverage fails again for full model, try 0.998 then 0.99 thru 0.9 min weight in increments of 0.01
          for (temp.minAdj in c(0.998,seq(0.99,0.9,by=-0.01))){
            if (is.null(wgts_temp) & nVar==length(crimeVarsWgtRest)){
              log_debug(str_c("No convergence - trying again with min final weight of ",temp.minAdj,")"))
              cat(str_c("\nWeight group ",j,": Trying weight ",temp.minAdj," (",maxIt2/10/1000,"K iterations)"),
                  file=str_c(output_weighting_data_folder,"weights_lt1_tracker_srs.txt"),
                  append=TRUE)
              #print()
              #Update (05May2025): Plugging in new calibration function
              temp.text2 <- capture.output(
                wgts_temp <- calWgts(SF_temp,ctrlVars,
                                     lowBound=temp.minAdj*pull(SF_temp,
                                                               lowBound) %>% 
                                       unique(),
                                     upBound=maxAdj2,
                                     maxIter=maxIt2/10)
              )
              #05May2025: confirm calibration before proceeding
              if (nVar==length(crimeVarsWgtRest) & !is.null(wgts_temp)){
                test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                         d=pull(SF_temp,baseWgt),
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
          #Update (27AUG2021): Ensure model converges AND calibration totals can be hit
          if (is.null(wgts_temp)){
            log_debug("No convergence")
            wgts_temp <- matrix(nrow=nrow(SF_temp),ncol=1) %>% as.data.frame() %>%
              mutate(!!paste0("NationalWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb) := rep(NA,nrow(SF_temp))) %>%
              select(paste0("NationalWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb))
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
              
              #Update stopAll in designated environment
              list2env(list("stopAll"=TRUE),envir=tempEnv)
              
              #05May2025: update temp.wgtGpsInfo to reflect success
              temp.wgtGpsInfo <- temp.wgtGpsInfo %>%
                mutate(success=ifelse(wgtGp==j,TRUE,success))
              list2env(list("temp.wgtGpsInfo"=temp.wgtGpsInfo),.GlobalEnv)
              list2env(list("temp.wgtGpsInfo"=temp.wgtGpsInfo),tempEnv)
              
              wgts_temp <- wgts_temp %>%
                data.frame() %>%
                dplyr::mutate(!!paste0("NationalWgt_nVar",nVar,"_comb",nComb) := .) %>%
                select(paste0("NationalWgt_nVar",nVar,"_comb",nComb))
              return(wgts_temp)
            } else {
              log_debug("Convergence, calibration failed")
              wgts_temp <- matrix(nrow=nrow(SF_temp),ncol=1) %>% as.data.frame() %>%
                mutate(!!paste0("NationalWgt_nVar",nVar,"_comb",nComb) := rep(NA,nrow(SF_temp))) %>%
                select(paste0("NationalWgt_nVar",nVar,"_comb",nComb))
            }
          }
          
        }  else {
          #Skipping bc stopInd==1
          wgts_temp <- matrix(nrow=nrow(SF_temp),ncol=1) %>% as.data.frame() %>%
            mutate(!!paste0("NationalWgt_nVar",nVar,"_comb",nComb) := rep(NA,nrow(SF_temp))) %>%
            select(paste0("NationalWgt_nVar",nVar,"_comb",nComb))
        }
        return(wgts_temp)
        
      },simplify=FALSE) %>%
        bind_cols()
      
    },simplify=FALSE) %>%
      {bind_cols(SF_temp,.)}
    
    if (stopInd==0){
      #05May2025: Failed - time to collapse
      
      #Identify records in super group - 
      #  Prefer to collapse within same super group
      temp.wgtGpSuper <- temp.wgtGpInfo$wgtGpSuper
      # print("temp.wgtGpSuper:")
      # print(temp.wgtGpSuper)
      # print("temp.wgtGpInfo:")
      # print(temp.wgtGpInfo)
      # print("temp.wgtGpsInfo:")
      # print(temp.wgtGpsInfo)
      
      temp.wgtGpsSuper <- temp.wgtGpsInfo %>%
        subset(wgtGpSuper==temp.wgtGpSuper)
      
      temp.nWgtGpsSuper <- nrow(temp.wgtGpsSuper)
      if (temp.nWgtGpsSuper>1){#1+ other record in super group
        #Identify where the current weighting group falls within super group
        temp.whichGp <- which(temp.wgtGpsSuper$wgtGp == j)
        #If there's a weighting group below it, collapse with that one
        #Otherwise, collapse with one above it
        if (temp.whichGp < temp.nWgtGpsSuper){
          temp.colGpInfo <- temp.wgtGpsSuper[temp.whichGp+1,]
        } else {
          temp.colGpInfo <- temp.wgtGpsSuper[temp.whichGp-1,]
        }
      } else {#No other record in super group
        if (str_detect(temp.wgtGpSuper,"(^| )1($|;)")){#>0 pop city
          #Collapse with zero pop city - if it doesn't exist, fail
          #if ("4" %in% temp.wgtGpsInfo$wgtGpSuper){
          #  temp.colGpInfo <- temp.wgtGpsSuper %>% subset(wgtGpSuper=="4")
          #} if (temp.wgtGpsInfo %>% 
          if (temp.wgtGpsInfo %>% 
              subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
              pull(wgtGpSuper) %>% 
              str_detect("(^| )1($|;)") %>%
              any()){
            temp.colGpInfo <- temp.wgtGpsInfo %>% 
              subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
              subset(str_detect(wgtGpSuper,"(^| )1($|;)")) %>% 
              .[1,]
          } else if (temp.wgtGpsInfo %>% 
                     subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                     pull(wgtGpSuper) %>% 
                     str_detect("(^| )4($|;)") %>%
                     any()){
            temp.colGpInfo <- temp.wgtGpsInfo %>% 
              subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
              subset(str_detect(wgtGpSuper,"(^| )4($|;)")) %>% 
              .[1,]
          } else if (temp.wgtGpsInfo %>% 
                     subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                     pull(wgtGpSuper) %>% 
                     str_detect("(^| )2($|;)") %>%
                     any()){
            temp.colGpInfo <- temp.wgtGpsInfo %>% 
              subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
              subset(str_detect(wgtGpSuper,"(^| )2($|;)")) %>% 
              .[1,]
          } else if (temp.wgtGpsInfo %>% 
                     subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                     pull(wgtGpSuper) %>% 
                     str_detect("(^| )3($|;)") %>%
                     any()){
            temp.colGpInfo <- temp.wgtGpsInfo %>% 
              subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
              subset(str_detect(wgtGpSuper,"(^| )3($|;)")) %>% 
              .[1,]
          } else if (temp.wgtGpsInfo %>% 
                     subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                     pull(wgtGpSuper) %>% 
                     str_detect("(^| )5($|;)") %>%
                     any()){
            temp.colGpInfo <- temp.wgtGpsInfo %>% 
              subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
              subset(str_detect(wgtGpSuper,"(^| )5($|;)")) %>% 
              .[1,]
          } else if (temp.wgtGpsInfo %>% 
                     subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                     pull(wgtGpSuper) %>% 
                     str_detect("(^| )6($|;)") %>%
                     any()){
            temp.colGpInfo <- temp.wgtGpsInfo %>% 
              subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
              subset(str_detect(wgtGpSuper,"(^| )6($|;)")) %>% 
              .[1,]
          }   else {
            stop("Couldn't find group to collapse with",call.=FALSE)
          }
        } else if (str_detect(temp.wgtGpSuper,"(^| )2($|;)")){#>0 pop MSA
          #For now, throw an error... eventually, I'll prob want to pick bw
          #  collapsing 1st with super group 3 or group 5
          if (temp.wgtGpsInfo %>% 
              subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
              pull(wgtGpSuper) %>% 
              str_detect("(^| )3($|;)") %>%
              any()){
            temp.colGpInfo <- temp.wgtGpsInfo %>% 
              subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
              subset(str_detect(wgtGpSuper,"(^| )3($|;)")) %>% 
              .[1,]
          } else if (temp.wgtGpsInfo %>% 
                     subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                     pull(wgtGpSuper) %>% 
                     str_detect("(^| )5($|;)") %>%
                     any()){
            temp.colGpInfo <- temp.wgtGpsInfo %>% 
              subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
              subset(str_detect(wgtGpSuper,"(^| )5($|;)")) %>% 
              .[1,]
          } else if (temp.wgtGpsInfo %>% 
                     subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                     pull(wgtGpSuper) %>% 
                     str_detect("(^| )6($|;)") %>%
                     any()){
            temp.colGpInfo <- temp.wgtGpsInfo %>% 
              subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
              subset(str_detect(wgtGpSuper,"(^| )6($|;)")) %>% 
              .[1,]
          }  else if (temp.wgtGpsInfo %>% 
                      subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                      pull(wgtGpSuper) %>% 
                      str_detect("(^| )4($|;)") %>%
                      any()){
            temp.colGpInfo <- temp.wgtGpsInfo %>% 
              subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
              subset(str_detect(wgtGpSuper,"(^| )4($|;)")) %>% 
              .[1,]
          } else if (temp.wgtGpsInfo %>% 
                     subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                     pull(wgtGpSuper) %>% 
                     str_detect("(^| )1($|;)") %>%
                     any()){
            temp.colGpInfo <- temp.wgtGpsInfo %>% 
              subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
              subset(str_detect(wgtGpSuper,"(^| )1($|;)")) %>% 
              .[1,]
          }else {
            stop("Couldn't find group to collapse with",call.=FALSE)
          }
        } else if (str_detect(temp.wgtGpSuper,"(^| )3($|;)")){#>0 pop non-MSA
          #For now, throw an error... eventually, I'll prob want to pick bw
          #  collapsing 1st with super group 4 or group 6
          if (temp.wgtGpsInfo %>% 
              subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
              pull(wgtGpSuper) %>% 
              str_detect("(^| )2($|;)") %>%
              any()){
            temp.colGpInfo <- temp.wgtGpsInfo %>% 
              subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
              subset(str_detect(wgtGpSuper,"(^| )2($|;)")) %>% 
              .[1,]
          }  else if (temp.wgtGpsInfo %>% 
                      subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                      pull(wgtGpSuper) %>% 
                      str_detect("(^| )6($|;)") %>%
                      any()){
            temp.colGpInfo <- temp.wgtGpsInfo %>% 
              subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
              subset(str_detect(wgtGpSuper,"(^| )6($|;)")) %>% 
              .[1,]
          } else if (temp.wgtGpsInfo %>% 
                     subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                     pull(wgtGpSuper) %>% 
                     str_detect("(^| )5($|;)") %>%
                     any()){
            temp.colGpInfo <- temp.wgtGpsInfo %>% 
              subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
              subset(str_detect(wgtGpSuper,"(^| )5($|;)")) %>% 
              .[1,]
          } else if (temp.wgtGpsInfo %>% 
                     subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                     pull(wgtGpSuper) %>% 
                     str_detect("(^| )4($|;)") %>%
                     any()){
            temp.colGpInfo <- temp.wgtGpsInfo %>% 
              subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
              subset(str_detect(wgtGpSuper,"(^| )4($|;)")) %>% 
              .[1,]
          } else if (temp.wgtGpsInfo %>% 
                     subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                     pull(wgtGpSuper) %>% 
                     str_detect("(^| )1($|;)") %>%
                     any()){
            temp.colGpInfo <- temp.wgtGpsInfo %>% 
              subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
              subset(str_detect(wgtGpSuper,"(^| )1($|;)")) %>% 
              .[1,]
          } else {
            stop("Couldn't find group to collapse with",call.=FALSE)
          }
        } else if (str_detect(temp.wgtGpSuper,"(^| )4($|;)")){#0 pop city
          #Collapse with whichever (other) group has the smallest city group
          #If no group available, fail (for now)
          temp.colGpsInfo <- temp.wgtGpsInfo %>%
            subset(str_detect(wgtGp,j,negate=TRUE) & 
                     wgtGpSuper == "1")
          if (nrow(temp.colGpsInfo)>0){
            temp.colGpInfo <- temp.colGpsInfo[nrow(temp.colGpsInfo),]
          } else {
            stop("Couldn't find group to collapse with",call.=FALSE)
          }
        } else if (str_detect(temp.wgtGpSuper,"(^| )5($|;)")){#0 pop MSA
          #Collapse with super gp 6 if present, then gp 4, otherwise fail
          if ("6" %in% temp.wgtGpsInfo$wgtGpSuper){
            temp.colGpInfo <- temp.wgtGpsInfo %>% subset(wgtGpSuper=="6")
          } else if ("4" %in% temp.wgtGpsInfo$wgtGpSuper){
            temp.colGpInfo <- temp.wgtGpsInfo %>% subset(wgtGpSuper=="4")
          } else {
            stop("Couldn't find group to collapse with",call.=FALSE)
          }
        } else if (str_detect(temp.wgtGpSuper,"(^| )6($|;)")){#0 pop non-MSA
          #Collapse with super gp 5 if present, then gp 4, otherwise fail
          if ("5" %in% temp.wgtGpsInfo$wgtGpSuper){
            temp.colGpInfo <- temp.wgtGpsInfo %>% subset(wgtGpSuper=="5")
          } else if ("4" %in% temp.wgtGpsInfo$wgtGpSuper){
            temp.colGpInfo <- temp.wgtGpsInfo %>% subset(wgtGpSuper=="4")
          } else {
            # log_debug("Current weighting groups:")
            # print(temp.wgtGpsInfo)
            stop("Couldn't find group to collapse with",call.=FALSE)
          }
        }
      }
      
      #Create a new group by combining info from current and collapsing gp
      log_debug(str_c("Collapsing group ",j," with ",temp.colGpInfo$wgtGp))
      # print("j:")
      # print(j)
      temp.wgtGpV <- j %>% str_split_1("; ")
      # print("temp.colGpInfo$wgtGp:")
      # print(temp.colGpInfo$wgtGp)
      temp.colGpV <- temp.colGpInfo$wgtGp %>% str_split_1("; ")
      temp.newGp <- c(temp.wgtGpV,temp.colGpV) %>% 
        unique() 
      #Before we sort this, store the proper order - 
      #  will use this later to make sure order of group descriptions
      #  matches the group numbers
      temp.order <- temp.newGp %>% str_rank(numeric=TRUE)
      temp.newGp <- temp.newGp %>%
        str_sort(numeric=TRUE) %>%
        str_flatten(collapse="; ")
      
      temp.wgtGpDesc <- temp.wgtGpInfo$wgtGpDesc
      # print("temp.wgtGpDesc:")
      # print(temp.wgtGpDesc)
      temp.wgtGpDescV <- temp.wgtGpDesc %>% str_split_1("; ")
      # print("temp.wgtGpDescV:")
      # print(temp.wgtGpDescV)
      temp.colGpDesc <- temp.colGpInfo$wgtGpDesc
      # print("temp.colGpDesc:")
      # print(temp.colGpDesc)
      temp.colGpDescV <- temp.colGpDesc %>% str_split_1("; ")
      # print("temp.colGpDescV:")
      # print(temp.colGpDescV)
      temp.newGpDesc <- c(temp.wgtGpDescV,temp.colGpDescV) %>%
        unique() %>%
        .[temp.order] %>% #Sort to match new group numbers
        str_flatten(collapse="; ")
      
      # print("temp.wgtGpSuper:")
      # print(temp.wgtGpSuper)
      temp.wgtGpSuperV <- temp.wgtGpSuper %>% str_split_1("; ")
      temp.colGpSuper <- temp.colGpInfo$wgtGpSuper
      # print("temp.colGpSuper:")
      # print(temp.colGpSuper)
      temp.colGpSuperV <- temp.colGpSuper %>% str_split_1("; ")
      temp.newGpSuper <- c(temp.wgtGpSuperV,temp.colGpSuperV) %>%
        unique() %>%
        str_sort(numeric=TRUE) %>%
        str_flatten(collapse="; ")
      
      # print("temp.newGp:")
      # print(temp.newGp)
      # print("temp.newGpDesc:")
      # print(temp.newGpDesc)
      # print("temp.newGpSuper:")
      # print(temp.newGpSuper)
      
      #Construct record for our newly formed group
      temp.newGpInfo <- data.frame(wgtGp=temp.newGp,
                                   wgtGpSort=min(as.numeric(temp.wgtGpV),
                                                 as.numeric(temp.colGpV)),
                                   wgtGpDesc=temp.newGpDesc,
                                   skip=FALSE,
                                   wgtGpSuper=temp.newGpSuper,
                                   success=FALSE)
      #Update our rolling weight group list (include new group and drop old)
      temp.wgtGpsInfo <- temp.wgtGpsInfo %>%
        subset(!wgtGp %in% c(j,temp.colGpInfo$wgtGp)) %>%
        bind_rows(temp.newGpInfo) %>%
        arrange(wgtGpSuper,wgtGpSort) %>%
        unique()
      
      #Move this rolling weight group list to our designated environment
      list2env(list("temp.wgtGpsInfo"=temp.wgtGpsInfo),envir=tempEnv)
      list2env(list("temp.wgtGpsInfo"=temp.wgtGpsInfo),envir=.GlobalEnv)
      
      #In addition, let's update the data and control totals to reflect the collapsing
      SF_national_temp <- SF_national_temp %>%
        mutate(
          wgtGpNational=case_when(
            wgtGpNational %in% c(j,temp.colGpInfo$wgtGp) ~ temp.newGp,
            TRUE ~ wgtGpNational),
          wgtGpNationalDesc=case_when(
            wgtGpNationalDesc == temp.wgtGpDesc ~ temp.newGpDesc,
            wgtGpNationalDesc == temp.colGpDesc ~ temp.newGpDesc,
            TRUE ~ wgtGpNationalDesc)
        )
      srs_control_totals_temp <- srs_control_totals_temp %>%
        mutate(wgtGpNational=case_when(
          wgtGpNational %in% c(j,temp.colGpInfo$wgtGp) ~ temp.newGp,
          TRUE ~ wgtGpNational)) %>%
        group_by(wgtGpNational) %>%
        summarize(across(matches("^sum_"),sum),.groups="drop")
      
      #Move both of these objects to the desired environment
      list2env(
        list(
          "SF_national_temp"=SF_national_temp,
          "srs_control_totals_temp"=srs_control_totals_temp),
        envir = tempEnv)
      list2env(
        list(
          "SF_national_temp"=SF_national_temp,
          "srs_control_totals_temp"=srs_control_totals_temp),
        envir = .GlobalEnv)
      
      #Adjust j for next iteration
      j <- temp.newGp
      list2env(list("j"=j),envir=tempEnv)
      
      
      #wgts_temp <- matrix(nrow=nrow(SF_temp),ncol=1) %>% as.data.frame() %>%
      #  mutate(!!paste0("NationalWgt_nVar",1,"_comb",1) := rep(NA,nrow(SF_temp))) %>%
      #  select(paste0("NationalWgt_nVar",1,"_comb",1))
      
      #list2env(list("j"=j),envir=.GlobalEnv)
      #return(NULL)
    }
  }
  
  #05May2025: include the nonrespondents in our output dataset
  out_temp <- out_temp %>%
    select(ORI,matches("^NationalWgt")) %>%
    full_join(SF_national_temp %>%
                subset(wgtGpNational==j))
  return(out_temp)
  
  #print(out_temp)
},simplify=FALSE) %>%
  bind_rows()



#05May2025: compile summaries of weight groups after collapsing
wgtGpsInfo <- get("temp.wgtGpsInfo")

wgtGpsInfo %>%
  select(-wgtGpDesc) %>% #Could be very big - drop for printout
  select(wgtGp,everything()) %>%
  print()

if (wgtGpsInfo %>% subset(success==FALSE) %>% nrow() == 0){
  log_debug("No failures.")
} else {
  stop("Issue with collapsing. Investigate before proceeding.")
}

#05May2025: bc of how the collapsing algorithm works, some ORIs may appear 
#             multiple times... in that case, always choose the last record
SF2_wgts2_all <- SF2_wgts2_all %>%
  slice_tail(n=1,by=ORI)


#04May2025: need to account for any changes brought on by collapsing
SF2 <- SF2 %>%
  select(-c(wgtGpNational,wgtGpNationalDesc)) %>%
  left_join(SF2_wgts2_all %>% select(ORI,wgtGpNational,wgtGpNationalDesc))

#Get totals by weighting group
srs_control_totals <- SF2 %>%
  group_by(wgtGpNational) %>%
  dplyr::summarize(sum_totcrime_imp=sum(totcrime_imp,na.rm=TRUE),
                   sum_totcrime_murder_imp=sum(totcrime_murder_imp,na.rm=TRUE),
                   sum_totcrime_rape_imp=sum(totcrime_rape_imp,na.rm=TRUE),
                   sum_totcrime_aggAssault_imp=sum(totcrime_aggAssault_imp,na.rm=TRUE),
                   sum_totcrime_burglary_imp=sum(totcrime_burglary_imp,na.rm=TRUE),
                   sum_totcrime_rob_imp=sum(totcrime_rob_imp,na.rm=TRUE),
                   sum_totcrime_larceny_imp=sum(totcrime_larceny_imp,na.rm=TRUE),
                   sum_totcrime_vhcTheft_imp=sum(totcrime_vhcTheft_imp,na.rm=TRUE),
                   sum_totcrime_agg_rob_imp=sum(totcrime_agg_rob_imp,na.rm=TRUE),
                   #Note (08Jun2023): Also adding violent and property
                   sum_totcrime_violent_imp=sum(totcrime_violent_imp,na.rm=TRUE),
                   sum_totcrime_property_imp=sum(totcrime_property_imp,na.rm=TRUE),
                   .groups="drop")
SF2 <- SF2 %>%
  select(-matches("sum_totcrime")) %>%
  inner_join(srs_control_totals) %>%
  select(-matches("^(n|N|baseWgt|lowBound)$")) %>%
  bind_cols(ratio)

#ratio <- ratio %>%
#  anti_join(crossings_skips)

#####
#Combination summaries

#Update (27OCT2021): Previously was copy-pasting code chunks by number of variables in model. Create function that will streamline
combs_table_gps <- function(indat,crimeVarsWgt,inWgtGps,wgtVar,wgtGpVar,wgtGpDescVar,suffix="",nInWgtGps=length(inWgtGps),nVars=length(crimeVarsWgt)){
  log_debug("Running function combs_table_gps")
  #05May2025: rather than create all possible weighting groups, 
  #             just use those that exist in indat
  inWgtGpsDF <- indat %>%
    select(wgtGpNational) %>%
    unique() %>%
    arrange(str_rank(wgtGpNational,numeric=TRUE))
  colnames(inWgtGpsDF) <- wgtGpVar
  #05May2025: changing from looping from nVars:1 to just doing nVars
  out <- sapply(nVars,function(temp.nVar){
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
        subset(resp_ind_m3==1) %>%
        mutate(converge=!is.na(eval(as.symbol(paste0(wgtVar,"_nVar",temp.nVar,"_comb",i))))) %>%
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
  
  #05May2025: Changing final value in range from 1 to nVars
  names(out) <- paste0("comb",nVars:nVars,"_table_",suffix)
  list2env(out,envir=.GlobalEnv)
  return(NULL)
}

#Do 1st group
#Set weight variables
if (as.numeric(year)<2023){
  crimeVarsWgtRest <- c("totcrime_imp",
                        "totcrime_murder_imp","totcrime_rape_imp",
                        "totcrime_agg_rob_imp","totcrime_burglary_imp",
                        "totcrime_larceny_imp","totcrime_vhcTheft_imp")
} else {
  crimeVarsWgtRest <- c("totcrime_imp",
                        "totcrime_murder_imp","totcrime_rape_imp",
                        "totcrime_aggAssault_imp","totcrime_burglary_imp",
                        "totcrime_rob_imp","totcrime_larceny_imp",  
                        "totcrime_vhcTheft_imp")
}
crimeVarsWgtAll <- NULL
crimeVarsWgt <- c(crimeVarsWgtAll,crimeVarsWgtRest)
combs_table_gps(indat=SF2_wgts2_all %>% subset(wgtGpNational=="1"),crimeVarsWgt,
                inWgtGps=wgtGps2[1],
                wgtVar="NationalWgt",wgtGpVar="wgtGpNational",
                wgtGpDescVar="wgtGpNationalDesc",
                suffix="firstGp")


#Now repeat for remaining groups
crimeVarsWgtRest <- c("totcrime_imp",
                      "totcrime_murder_imp","totcrime_rape_imp",
                      "totcrime_aggAssault_imp","totcrime_burglary_imp",
                      "totcrime_rob_imp","totcrime_larceny_imp",  
                      "totcrime_vhcTheft_imp")
crimeVarsWgt <- c(crimeVarsWgtAll,crimeVarsWgtRest)

#Update (28OCT2021): Using function from above to streamline combination summaries
combs_table_gps(indat=SF2_wgts2_all %>% subset(wgtGpNational != "1"),crimeVarsWgt,
                inWgtGps=wgtGps2[-1],
                wgtVar="NationalWgt",wgtGpVar="wgtGpNational",
                wgtGpDescVar="wgtGpNationalDesc",
                suffix="rest")

#Splitting out 1st group from all other groups
SF2_wgts2_firstGp <- SF2_wgts2_all %>%
  subset(wgtGpNational == "1")
SF2_wgts2_rest <- SF2_wgts2_all %>%
  subset(wgtGpNational != "1")

#Stack all tables together
#30May2024: realizing I didn't add the 8-variable combination for the 1st weighting group
#05May2025: only need the full versions at this point
if (as.numeric(year)<2023){
  combAll_table <- bind_rows(comb7_table_firstGp,
                             # comb6_table_firstGp,
                             # comb5_table_firstGp,
                             # comb4_table_firstGp,
                             # comb3_table_firstGp,
                             # comb2_table_firstGp,
                             # comb1_table_firstGp,
                             comb8_table_rest#,
                             # comb7_table_rest,
                             # comb6_table_rest,
                             # comb5_table_rest,
                             # comb4_table_rest,
                             # comb3_table_rest,
                             # comb2_table_rest,
                             # comb1_table_rest
  )
} else {
  combAll_table <- bind_rows(comb8_table_firstGp,
                             # comb7_table_firstGp,
                             # comb6_table_firstGp,
                             # comb5_table_firstGp,
                             # comb4_table_firstGp,
                             # comb3_table_firstGp,
                             # comb2_table_firstGp,
                             # comb1_table_firstGp,
                             comb8_table_rest#,
                             # comb7_table_rest,
                             # comb6_table_rest,
                             # comb5_table_rest,
                             # comb4_table_rest,
                             # comb3_table_rest,
                             # comb2_table_rest,
                             # comb1_table_rest
  )
}
combAll_table <- combAll_table %>%
  arrange(wgtGpNational,wgtGpNationalDesc,-converge,-nVar,comb) %>%
  group_by(wgtGpNational,wgtGpNationalDesc) %>%
  mutate(Select=ifelse(row_number(wgtGpNational)==1,"X","")) %>%
  ungroup() %>%
  arrange(str_rank(wgtGpNational,numeric=TRUE),wgtGpNationalDesc,-nVar,comb) %>%
  mutate(Variables=ifelse(
    as.numeric(year)<2023,
    apply(.,FUN=function(i){#2022 and earlier
      c(ifelse(i["totcrime_imp"]=="X","totcrime_imp",""),
        ifelse(i["totcrime_murder_imp"]=="X","totcrime_murder_imp",""),
        ifelse(i["totcrime_rape_imp"]=="X","totcrime_rape_imp",""),
        ifelse(i["totcrime_aggAssault_imp"]=="X","totcrime_aggAssault_imp",""),
        ifelse(i["totcrime_burglary_imp"]=="X","totcrime_burglary_imp",""),
        ifelse(i["totcrime_rob_imp"]=="X","totcrime_rob_imp",""),
        ifelse(i["totcrime_larceny_imp"]=="X","totcrime_larceny_imp",""),
        ifelse(i["totcrime_vhcTheft_imp"]=="X","totcrime_vhcTheft_imp",""),
        ifelse(i["totcrime_agg_rob_imp"]=="X","totcrime_agg_rob_imp","")
      ) %>%
        subset(.!="") %>%
        str_flatten(collapse=",")},MARGIN=1),
    apply(.,FUN=function(i){#2023 and later
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
        str_flatten(collapse=",")},MARGIN=1))) %>%
  select(wgtGpNational,wgtGpNationalDesc,nVar,comb,
         totcrime_imp,totcrime_murder_imp,
         totcrime_rape_imp,matches("^totcrime_agg_rob_imp$"),
         totcrime_aggAssault_imp,
         totcrime_burglary_imp,totcrime_rob_imp,
         totcrime_larceny_imp,totcrime_vhcTheft_imp,Variables,everything())

#Update (14Jun2022): Switching Excel output functions (fixing overwrite bug)
#combAll_table %>%
#  list("All Combinations"=.) %>%
#  write.xlsx(file=paste0(output_weighting_data_folder,"SRS_Variable_Combination_Convergence_by_Weighting_Group_Automatic.xlsx"))
log_debug("Writing excel file SRS_Variable_Combination_Convergence_by_Weighting_Group_Automatic.xlsx")
workbook <- paste0(output_weighting_data_folder,
                   "SRS_Variable_Combination_Convergence_by_Weighting_Group_Automatic.xlsx")
wb <- createWorkbook()
addWorksheet(wb,"All Combinations")
writeData(wb,"All Combinations",combAll_table)
saveWorkbook(wb,workbook,overwrite=TRUE) 

SF2 <- SF2 %>%
  arrange(ORI)

ctrlVars <- combAll_table %>% 
  subset(Select=="X")
if (nrow(ctrlVars)==combAll_table$wgtGpNational %>% unique() %>% length()){
  
  #choosing best model that converges
  ctrlInds <- combAll_table %>% 
    subset(Select=="X") %>% 
    rename_at(.vars=vars(matches("^totcrime")),.funs=~paste0(.x,"_ind")) %>%
    select(wgtGpNational,matches("_ind")) %>%
    mutate(across(matches("_ind"),~ifelse(.x!="X",0,1))) %>%
    mutate(across(matches("_ind"),~ifelse(is.na(.x),0,.x))) %>%
    arrange(str_rank(wgtGpNational,numeric=TRUE)) %>%
    mutate(totcrime_agg_rob_imp_ind=0) %>% #Creating dummy variable to retain same names as national & region
    select(wgtGpNational,
           totcrime_imp_ind,totcrime_murder_imp_ind,
           totcrime_rape_imp_ind,matches("^totcrime_agg_rob_imp_ind$"),
           totcrime_aggAssault_imp_ind,totcrime_burglary_imp_ind,
           totcrime_rob_imp_ind,totcrime_larceny_imp_ind,
           totcrime_vhcTheft_imp_ind)
  
  
  ctrlIndsM <- ctrlInds %>%
    select(colnames(ctrlInds)) %>%
    select(-wgtGpNational) %>%
    as.matrix()
  
  ctrlTtlsM <- srs_control_totals %>%
    arrange(str_rank(wgtGpNational,numeric=TRUE)) %>%
    select(sum_totcrime_imp,sum_totcrime_murder_imp,
           sum_totcrime_rape_imp,matches("^sum_totcrime_agg_rob_imp$"),
           sum_totcrime_aggAssault_imp,sum_totcrime_burglary_imp,
           sum_totcrime_rob_imp,sum_totcrime_larceny_imp,
           sum_totcrime_vhcTheft_imp) %>%
    as.matrix()
  
  ctrlTtlsM2 <- ctrlTtlsM*ctrlIndsM #Element-wise multiplication
  colnames(ctrlTtlsM2) <- LETTERS[1:ncol(ctrlTtlsM2)] #Would normally include 'sum_' before, but will add that later
  ctrlTtls2 <- ctrlTtlsM2 %>%
    data.frame() %>%
    mutate(wgtGpNational=ctrlInds %>% getElement("wgtGpNational")) %>%
    reshape2::melt(id.vars="wgtGpNational") %>%
    reshape2::dcast(formula=.~wgtGpNational+variable) %>%
    select(-.) #Drop dummy variable
  colnames(ctrlTtls2) <- paste0("sum_V",colnames(ctrlTtls2))
  
  
  colnames(ctrlTtls2) <- colnames(ctrlTtls2) %>% str_replace("^(\\w)$","sum_\\1")
  
  #Control variables
  #Note (10Jan2023): Removed totcrime_imp requirement
  ctrlIndsM <- ctrlInds %>%
    inner_join(SF2) %>%
    subset(resp_ind_m3==1) %>%
    arrange(ORI) %>%
    select(colnames(ctrlInds)) %>%
    select(-wgtGpNational) %>%
    as.matrix()
  #Note (10Jan2023): Removed totcrime_imp requirement
  ctrlVarsM <- SF2%>%
    subset(resp_ind_m3==1) %>%
    arrange(ORI) %>%
    select(totcrime_imp,totcrime_murder_imp,
           totcrime_rape_imp,matches("^totcrime_agg_rob_imp$"),
           totcrime_aggAssault_imp,totcrime_burglary_imp,
           totcrime_rob_imp,totcrime_larceny_imp,
           totcrime_vhcTheft_imp) %>%
    as.matrix()
  
  ctrlVarsM2 <- ctrlVarsM*ctrlIndsM
  colnames(ctrlVarsM2) <- LETTERS[1:ncol(ctrlVarsM2)]
  
  ctrlVars2 <- ctrlVarsM2 %>%
    data.frame() %>%
    #Note (10Jan2023): Removed totcrime_imp requirement
    mutate(ORI=SF2 %>% arrange(ORI) %>% subset(resp_ind_m3==1) %>% getElement("ORI"),
           wgtGpNational=SF2 %>% arrange(ORI) %>% subset(resp_ind_m3==1) %>% getElement("wgtGpNational")) %>%
    mutate(across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==1,1,0),.names="V1_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==4,1,0),.names="V4_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==5,1,0),.names="V5_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==6,1,0),.names="V6_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==7,1,0),.names="V7_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==8,1,0),.names="V8_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==9,1,0),.names="V9_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==10,1,0),.names="V10_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==11,1,0),.names="V11_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==14,1,0),.names="V14_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==15,1,0),.names="V15_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==16,1,0),.names="V16_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==18,1,0),.names="V18_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==19,1,0),.names="V19_{col}"),
           across(matches("^\\w{1}$"),.fns=~.x*ifelse(wgtGpNational==20,1,0),.names="V20_{col}"))
  
  
  #Add on the new control totals/variables
  SF2 <- SF2 %>%
    select(-matches("^(V\\d+_|)[A-Z]$")) %>%
    full_join(ctrlVars2) %>%
    select(-matches("^sum_\\w+_imp$")) %>%
    #full_join(ctrlTtls2) %>%
    arrange(ORI)
  
  
  # #par(mar=c(1,1,1,1))
  # #pdf(file=paste0(output_weighting_data_folder,"plots_National_wgtGp",j,".pdf"))
  # #capture.output({
  # SF2_wgts2 <- sapply(wgtGps2,function(j){#Loop over weight groupings
  #   print("##############################")
  #   print(paste0("Weight group: ",j))
  #   #Take weighting group subset within weight group subset
  #   
  #   SF_temp <- SF2 %>%
  #     subset(wgtGpNational==j & resp_ind_m3==1 & !is.na(totcrime_imp))
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
  #     select(all_of(paste0("sum_",temp.ctrlVars))) %>%
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
  #   names(temp.out) <- paste0("results_",j)
  #   list2env(temp.out,.GlobalEnv)
  #   return(out_temp)
  #   
  # },simplify=FALSE) %>%
  #   bind_rows()%>%
  #   full_join(SF2,by=colnames(SF2))
  # #},file=paste0(output_weighting_data_folder,'weights_national_checks.txt'),
  # #type="output")
  #Note (10Jan2023): Removed totcrime_imp requirement
  SF_temp <- SF2 %>%
    subset(resp_ind_m3==1)
  
  
  temp.ctrlVars <- colnames(SF_temp) %>% str_subset("^V\\d+_\\w$")
  #Update (28OCT2021): Comment out print statement
  #print(temp.ctrlVars)
  #05May2025: create set of control variables just for calibration check - 
  #             these will use same variables in the original calibration
  #Always drop the agg assault + robbery derived variable for all but 1st gp
  temp.ctrlVars2 <- temp.ctrlVars %>%
    str_subset(str_c("(",
                     str_c("V",2:20,"_","D") %>%
                       str_flatten(collapse="|"),
                     ")"),
               negate=TRUE)
  if (as.numeric(year)>=2023 | !("1" %in% SF_temp$wgtGpNational)){
    temp.ctrlVars2 <- temp.ctrlVars2 %>% 
      #Drop agg assault + robbery derived variables for even the 1st group
      str_subset("V\\d+_D",negate=TRUE)
  } else {
    temp.ctrlVars2 <- temp.ctrlVars2 %>% 
      #Drop the individual agg assault and robbbery variables for 1st group
      str_subset(str_c("(",
                       str_c("V1_",c("E","G")) %>%
                         str_flatten(collapse="|"),
                       ")"),
                 negate=TRUE)
  }
  #05May2025: use this new set of control variables for the control totals
  total_temp <- ctrlTtls2 %>%
    select(all_of(paste0("sum_",temp.ctrlVars2))) %>%
    as.numeric()
  #names(total_temp) <- NULL
  
  #05May2025: below not actually used for anything - commenting out
  #vars_temp <- SF_temp %>%
  #  select(all_of(temp.ctrlVars)) 
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
    #subset(resp_ind_m3==1) %>%
    mutate(gWgt=select(.,matches("NationalWgt_nVar\\d")) %>% rowMeans(na.rm=TRUE)) %>%
    mutate(NationalWgt=gWgt*baseWgt) %>%
    select(ORI,gWgt,NationalWgt) %>%
    right_join(SF_temp)
  
  SF_temp_wgts <- SF2_wgts2 %>%
    subset(resp_ind_m3==1) 
  
  print("Check calibration on full model")
  #05May2025: use the new set of control variables
  checkcalibration(Xs=select(SF_temp_wgts,all_of(temp.ctrlVars2)) %>% as.matrix(),
                   d=rep(ratio$baseWgt,nrow(SF_temp_wgts)),
                   total=total_temp,
                   g=SF_temp_wgts$gWgt,
                   EPS=ifelse(any(total_temp==0),1,1e-6)) %>% #EPS=1) %>%
    print()
  #05May2025: loop over the weighting groups that occur in data
  temp.wgtGps <- SF2_wgts2 %>% pull(wgtGpNational) %>% unique() %>% str_sort(numeric=TRUE)
  sapply(temp.wgtGps,function(j){#Loop over weight groupings
    print("##############################")
    print(paste0("Weight group: ",j))
    #Take weighting group subset within weight group subset
    #Note (10Jan2023): Removed totcrime_imp requirement
    SF_temp <- SF2_wgts2 %>%
      subset(wgtGpNational==j & resp_ind_m3==1)
    
    
    #05May2025: filter the new set of variables
    temp.ctrlVars3 <- temp.ctrlVars2 %>% str_subset(paste0("^V",j,"_\\w$"))
    #Update (28OCT2021): Comment out print statement
    #print(temp.ctrlVars)
    #05May2025: use new list of variables for group
    total_temp <- ctrlTtls2 %>%
      select(all_of(paste0("sum_",temp.ctrlVars3))) %>%
      as.numeric()
    #print(total_temp)
    out_temp <- SF_temp
    # print(out_temp %>% select(ORI,UCR_AGENCY_NAME,wgtGpNational,matches("totcrime"),matches(paste0("V",j,"_w$"))) %>% head())
    #Update (20AUG2021): Adding requested checks
    #Update (30Jun2022): Switch to table format (1 row per weight group) - commenting out old code
    #Update (16May2024): added min and max to checks
    #Update (14May2025): adding check for weights <0.9
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
    #05May2025: use the new set of variables for group
    temp.cal <- checkcalibration(Xs=select(SF_temp,all_of(temp.ctrlVars3)),
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
    names(temp.out) <- paste0("results_",j)
    list2env(temp.out,.GlobalEnv)
    return(NULL)
    
  })
  
  
  #Note (JDB 06Jul2022): Combine weight check results
  #Note (JDB 05May2025): Use the weight groups that occur within the data
  results_national <- mget(paste0("results_",temp.wgtGps)) %>%
    bind_rows()
  
  
  #dev.off() 
  
  
  
  ###############
  #Output
  
  #03Jul2024: for whatever reason, the nonrepondents have started falling out of the weights - let's add any missing records here
  new_weights <- SF2_wgts2 %>%
    right_join(SF2 %>% 
                 select("ORI_universe","LEGACY_ORI","wgtGpNational","wgtGpNationalDesc"))
  
  ### export for others to start writing functions to analyze bias, MSE, etc.
  new_weights[,c("ORI_universe","LEGACY_ORI","wgtGpNational","wgtGpNationalDesc",
                 "NationalWgt")] %>%
    #write.csv(paste0(output_weighting_data_folder,'weights_national.csv'),
    fwrite_wrapper(paste0(output_weighting_data_folder,'weights_national.csv'))
  
  #Update (26AUG2021): Add wgtGpNational and wgtGpNationalDesc to SF file from 02_Weights_Data_Setup
  #Update (06Oct2022): Switching from read_csv() to fread()
  oldSF <- fread(paste0(input_weighting_data_folder,"SF.csv"))%>%
    #Adding just in case already on file...
    select(-matches("wgtGpNational"))
  newSF <- oldSF %>%
    left_join(SF2 %>% select(ORI_universe,wgtGpNational,wgtGpNationalDesc,matches("^V\\d+_\\w$")),
              by=c("ORI_universe"))
  
  #write_csv(newSF,file=paste0(output_weighting_data_folder,"SF_postN.csv"))
  fwrite_wrapper(newSF,paste0(output_weighting_data_folder,"SF_postN.csv"))
  
  #Note (JDB 06Jul2022): Export weight check results
  #write_csv(results_national,
  fwrite_wrapper(results_national, 
                 paste0(output_weighting_data_folder,"weights_national_checks.csv"))
} else {
  stop("No calibration model converged for 1+ weighting group")
}
log_info("Finished 03_Weights_Calibration_National.R\n\n")