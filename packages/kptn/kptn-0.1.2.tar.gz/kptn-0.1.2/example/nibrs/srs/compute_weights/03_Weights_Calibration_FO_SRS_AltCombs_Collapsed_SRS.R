#This program is for testing variations of the field office weights
#Specifically, this is based on 4 strata with SRS calibration

maxAdj <- 10 #Max adjustment factor
maxIt <- 1000 #Max iterations during variable selection

### Purpose of program is to calibrate field office weights by grouping (e.g., zero pop vs. nonzero pop LEAs)
### Author: JD Bunker
### Last updated: 29OCT2021
#Update (28OCT2021): Commenting out/removing unnecessary print statements and removing no longer needed commented-out code
#Update (29OCT2021): Continuing clean up efforts (commenting out / deleting commented-out code)
#Update (07OCT2022): Adding maxWgt and maxIt values for final weight
#Update (13AUG2025): Removing use of gencalib() with only overall crime if 
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


log_info("Running 03_Weights_Calibration_FO_SRS_AltCombs_Collapsed_SRS.R")

#Note (22Jun2023): Reading in new crossing worksheet
foCrosses <- paste0(input_weighting_data_folder,"Geography_Crossings_SRS.xlsx") %>%
  read_xlsx(sheet="FO") %>%
  rename(FIELD_OFFICE_NAME=foLvl,
         wgtGpFO=foWgtGp)

# read in SF data

SF <- paste0(input_weighting_data_folder,"SF_srs.csv") %>%
  #read.csv(header=TRUE, sep=",") %>%
  fread() %>%
  data.frame() %>%
  mutate(totcrime_imp=totcrime_violent_imp+totcrime_property_imp)
#print("Columns of SF:")
colnames(SF)
crimeVars <- SF %>%
  colnames() %>%
  str_subset("^tot.*_imp")

#Crime variables for weight calibration
#Note (28Apr2023): Splitting into variables for all field office X weighting groups vs. extra crime vars
crimeVarsWgtAll <- c("totcrime_imp",
                     "totcrime_violent_imp",
                     "totcrime_property_imp")
crimeVarsWgtRest <- c("totcrime_murder_imp",
                      "totcrime_rape_imp","totcrime_aggAssault_imp",
                      "totcrime_burglary_imp","totcrime_rob_imp",
                      "totcrime_larceny_imp","totcrime_vhcTheft_imp")
crimeVarsWgt <- c(crimeVarsWgtAll,crimeVarsWgtRest)

foGps <- SF %>%
  pull(FIELD_OFFICE_NAME) %>%
  unique()
nFOGps <- foGps %>%
  length()


#srs_FO_control_totals <- SF %>%
#  group_by(FIELD_OFFICE_NAME) %>%
#  dplyr::summarize(across(.cols=all_of(crimeVarsWgt),.fns=list("sum"=sum),.names="{.fn}_{.col}",na.rm=TRUE))


wgtGpFODescs <-  c("Cities 1,000,000 or over",
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
  mutate(wgtGpFO=case_when(POPULATION_GROUP_DESC_UNIV=="Cities 1,000,000 or over" ~ 1,
                            POPULATION_GROUP_DESC_UNIV=="Cities from 500,000 thru 999,999" ~ 2,
                            POPULATION_GROUP_DESC_UNIV=="Cities from 250,000 thru 499,999" ~ 3,
                            POPULATION_GROUP_DESC_UNIV=="Cities from 100,000 thru 249,999" ~ 4,
                            POPULATION_GROUP_DESC_UNIV=="Cities from 50,000 thru 99,999" ~ 5,
                            POPULATION_GROUP_DESC_UNIV=="Cities from 25,000 thru 49,999" ~ 6,
                            POPULATION_GROUP_DESC_UNIV=="Cities from 10,000 thru 24,999" ~ 7,
                            #Note: splitting out cities under 10K into 2 groups... these were combined in weighting program and thus throw off levels by 1
                            POPULATION_GROUP_DESC_UNIV %in% c("Cities from 2,500 thru 9,999") ~ 8,
                            POPULATION_GROUP_DESC_UNIV=="Cities under 2,500" & POPULATION_UNIV> 0 ~ 9,
                            
                            POPULATION_GROUP_DESC_UNIV=="MSA counties 100,000 or over" ~ 10,
                            POPULATION_GROUP_DESC_UNIV=="MSA counties from 25,000 thru 99,999" ~ 11,
                            POPULATION_GROUP_DESC_UNIV=="MSA counties from 10,000 thru 24,999" ~ 12,
                            POPULATION_GROUP_DESC_UNIV=="MSA counties under 10,000" &  POPULATION_UNIV> 0 ~ 13,
                            POPULATION_GROUP_DESC_UNIV=="MSA State Police" & POPULATION_UNIV>0 ~ 14,
                            #Note: splitting out non-MSA counties 25K and up into 2 groups... these were combined in weighting program and thus throw off levels by 1
                            POPULATION_GROUP_DESC_UNIV %in% c("Non-MSA counties from 25,000 thru 99,999") ~ 15,
                            POPULATION_GROUP_DESC_UNIV=="Non-MSA counties 100,000 or over" ~ 16,
                            POPULATION_GROUP_DESC_UNIV=="Non-MSA counties from 10,000 thru 24,999" ~ 17,
                            POPULATION_GROUP_DESC_UNIV=="Non-MSA counties under 10,000" & POPULATION_UNIV >0 ~ 18,
                            POPULATION_GROUP_DESC_UNIV=="Non-MSA State Police" & POPULATION_UNIV>0 ~ 19,
                            
                            POPULATION_GROUP_DESC_UNIV=="Cities under 2,500" & POPULATION_UNIV==0 ~ 20,
                            POPULATION_GROUP_DESC_UNIV %in% c("MSA counties under 10,000","MSA State Police") & POPULATION_UNIV==0 ~ 21,
                            POPULATION_GROUP_DESC_UNIV %in% c("Non-MSA counties under 10,000","Non-MSA State Police") & POPULATION_UNIV==0 ~ 22),
         wgtGpFODesc=factor(wgtGpFO,levels=1:22,labels=wgtGpFODescs))

foGps2 <- SF2 %>%
  pull(FIELD_OFFICE_NAME) %>%
  unique()
nFOGps2 <- foGps2 %>%
  length()

wgtGpsFO <- SF2 %>%
  pull(wgtGpFO) %>%
  unique()
nWgtGpsFO <- length(wgtGpsFO)


#Detect and perform any necessary collapsing (number of respondents in non-empty field office X grouping is 0)
wgtGpsFO2 <- 1:2
wgtGpFODescs2 <- c("Nonzero population agencies",
                    "Zero population agencies")
SF2 <- SF2 %>%
  mutate(wgtGpFO2=case_when(wgtGpFO %in% 20:22 ~ 2,
                             TRUE ~ 1),
         wgtGpFODesc2=factor(wgtGpFO2,levels=wgtGpsFO2,labels=wgtGpFODescs2))



SF2 <- SF2 %>%
  rename(wgtGpFO_raw=wgtGpFO,
         wgtGpFODesc_raw=wgtGpFODesc) %>%
  rename(wgtGpFO=wgtGpFO2,
         wgtGpFODesc=wgtGpFODesc2)



#Get totals by weighting group
srs_FO_control_totals <- SF2 %>%
  group_by(FIELD_OFFICE_NAME,wgtGpFO) %>%
  dplyr::summarize(across(all_of(crimeVarsWgt),.fns=list("sum"=sum),.names="{fn}_{col}",na.rm=TRUE),
                   .groups="drop")
#Get n NIBRS Reporters and n Eligible - used for base weights and lower bounds
#Note (12Apr2023): adding ratio for totcrime_imp - field office X weighting groups with >=99% will skip weighting and be assigned weights of 1
ratio <- SF2 %>%
  group_by(FIELD_OFFICE_NAME,wgtGpFO) %>%
  dplyr::summarize(n=sum(resp_ind_srs==1),
                   N=n(),
                   sum_totcrime_imp_NIBRS=sum(totcrime_imp*resp_ind_srs),
                   sum_totcrime_imp_all=sum(totcrime_imp),
                   ratio_totcrime_imp=sum_totcrime_imp_NIBRS/sum_totcrime_imp_all) %>%
  mutate(baseWgt=N/n,
         lowBound=n/N)

SF2 <- SF2 %>%
  select(-matches("sum_totcrime")) %>%
  inner_join(srs_FO_control_totals) %>%
  select(-matches("^(n|N|baseWgt|lowBound)$")) %>%
  full_join(ratio,by=c("FIELD_OFFICE_NAME","wgtGpFO"))


#Note (18May2023): Moving collapsing before skips


#Note (17May2023): collapse field offices where 1+ weighting group has ratio_totcrime_imp<
crossings_col <- ratio %>%
  subset(ratio_totcrime_imp<0.2) %>%
  select(FIELD_OFFICE_NAME) %>%
  unique() %>%
  mutate(collapse=TRUE)
SF2 <- SF2 %>%
  #anti_join(crossings_skips) %>%
  left_join(crossings_col) %>%
  mutate(collapse=ifelse(is.na(collapse),0,collapse)) %>%
  mutate(wgtGpFO=ifelse(collapse==TRUE,3,wgtGpFO))


wgtGpsFO2 <- 1:3
wgtGpFODescs2 <- c("Nonzero population agencies",
                    "Zero population agencies",
                    "All agencies")

SF2 <- SF2 %>%
  mutate(wgtGpFODesc=factor(wgtGpFO,levels=wgtGpsFO2,labels=wgtGpFODescs2))


foCrosses2 <- SF2 %>%
  select(FIELD_OFFICE_NAME,wgtGpFO) %>%
  unique() %>%
  inner_join(foCrosses)


#Get totals by (collapsed) weighting group
srs_FO_control_totals <- SF2 %>%
  group_by(FIELD_OFFICE_NAME,wgtGpFO) %>%
  dplyr::summarize(across(all_of(crimeVarsWgt),.fns=list("sum"=sum),.names="{fn}_{col}",na.rm=TRUE),
                   .groups="drop")

#Get n NIBRS Reporters and n Eligible - used for base weights and lower bounds
#Note (12Apr2023): adding ratio for totcrime_imp - field office X weighting groups with >=99% will skip weighting and be assigned weights of 1
ratio <- SF2 %>%
  group_by(FIELD_OFFICE_NAME,wgtGpFO) %>%
  dplyr::summarize(n=sum(resp_ind_srs==1),
                   N=n(),
                   sum_totcrime_imp_NIBRS=sum(totcrime_imp*resp_ind_srs),
                   sum_totcrime_imp_all=sum(totcrime_imp),
                   ratio_totcrime_imp=sum_totcrime_imp_NIBRS/sum_totcrime_imp_all) %>%
  mutate(baseWgt=N/n,
         lowBound=n/N)
SF2 <- SF2 %>%
  select(-matches("sum_totcrime")) %>%
  left_join(srs_FO_control_totals,by=c("FIELD_OFFICE_NAME","wgtGpFO")) %>%
  select(-matches("^(n|N|sum_totcrime_imp_NIBRS|sum_totcrime_imp_all|ratio_totcrime_imp|baseWgt|lowBound)$")) %>%
  left_join(ratio) %>%
  #24May2023: also drop field offices with 0 respondents
  subset(n!=0)
#Note (12Apr2023): Setting aside field office X weighting group crossings with >=99%
#Note (16May2023): Temporarily setting aside crossigns with 0 respondents
crossings_skips <- ratio %>%
  subset(ratio_totcrime_imp>=0.99) %>%
  select(FIELD_OFFICE_NAME,wgtGpFO)
SF2_skips <- SF2 %>%
  inner_join(crossings_skips) %>%
  mutate(FOWgt=ifelse(resp_ind_srs==1,1,NA_real_))



#ratio <- ratio %>%
#  anti_join(crossings_skips)

SF2 <- SF2 %>%
  anti_join(crossings_skips)

#Get totals by weighting group
srs_FO_control_totals <- SF2 %>%
  group_by(FIELD_OFFICE_NAME,wgtGpFO) %>%
  dplyr::summarize(across(all_of(crimeVarsWgt),.fns=list("sum"=sum),.names="{fn}_{col}",na.rm=TRUE),
                   .groups="drop")

foGps2 <- SF2 %>%
  pull(FIELD_OFFICE_NAME) %>%
  unique() %>%
  sort()

#Note (12Apr2023): Dropping skipped crossings from main file
#SF2 %>%
#  group_by(FIELD_OFFICE_NAME,wgtGpFO,wgtGpFODesc) %>%
#  dplyr::summarize(N=n(),
#                   n=sum(resp_ind_srs)) %>%
#  DT::datatable()
#  
#stop()

#Update (28OCT2021): Reducing print statements
#Update (23MAR2022): Stop running after first successful convergence for weighting group
#Update (23MAR2022): Lowering max_iter from 10000 to 1000
#Update (21MAR2023): Reducing number of print and log statements
#Update (13AUG2025): Reducing log statements (only print # of gps if stopInd=0)
#                    Also, updating weights for nVar==1 (don't use gencalib())
SF2_wgts2_test <- sapply(foGps2,function(i){#Loop over weight groupings
  log_debug("Running function SF2_wgts2_test")
  log_debug("##################")
  log_debug(paste0("Field Office: ",i))
  #Note (09Jan2023): Removing totcrime_imp requirement
  SF_temp_FO <- SF2 %>%
    subset(FIELD_OFFICE_NAME==i & resp_ind_srs==1)
  srs_control_totals_temp_FO <- srs_FO_control_totals %>%
    subset(FIELD_OFFICE_NAME==i)
  ratio_FO <- ratio %>% subset(FIELD_OFFICE_NAME==i)
  temp.wgtGps <- srs_control_totals_temp_FO %>% pull(wgtGpFO)
  
  SF2_wgts_FO <- sapply(temp.wgtGps,function(j){#Loop over weight groupingstemp.#wgtGps,function(j){#Loop over weight groupings
    log_debug("#########")
    log_debug(paste0("Field Office: ",i,". Weight group: ",j))
    #Take weighting group subset within field office subset
    #Note (09Jan2023): Removing totcrime_imp requirement
    SF_temp <- SF_temp_FO %>%
      subset(wgtGpFO==j & resp_ind_srs==1)
    if (nrow(SF_temp)>0){
      stopInd <- 0 #Initialize stop indicator to 0
      tempEnv <- environment() #Function environment
      out_temp <- sapply(length(crimeVarsWgtRest):0,function(nVar){#Loop over n control total variables
        if (stopInd==0){
          
          log_debug(paste0("Field Office: ",i,". Weight group: ",j,". n SRS Variables: ",nVar+length(crimeVarsWgtAll)))
        }
        varCombs_nVar <- combn(crimeVarsWgtRest,m=nVar,simplify=FALSE)
        #print(varCombs_nVar)
        nVarCombs <- length(varCombs_nVar) #Number of combinations
        #print(nVarCombs)
        sapply(1:nVarCombs,function(nComb){#Loop over variable combinations
          if (stopInd==0){
            log_debug("stopInd==0")
            ctrlVars <- c(crimeVarsWgtAll,varCombs_nVar[[nComb]])
            #print(paste0("Combination ",nComb,"/",nVarCombs))
            #print(varCombs_nVar)
            #print(ctrlVars)
            
            total_temp <- srs_control_totals_temp_FO %>%
              subset(wgtGpFO==j) %>%
              select(all_of(paste0("sum_",ctrlVars))) %>%
              as.numeric()
            #print(total_temp)
            #Update (28OCT2021): Running invisibly (no messages)
            #Update (04NOV2021): Adding suppressWarnings() 
            suppressWarnings(capture.output(
            wgts_temp <- gencalib(Xs=select(SF_temp,all_of(ctrlVars)),
                                  Zs=select(SF_temp,all_of(ctrlVars)),
                                  #d=rep(1,nrow(SF_temp)),
                                  d=pull(SF_temp,baseWgt),
                                  total=total_temp,
                                  method="logit",
                                  #bounds=c(low=1,1e6),
                                  bounds=c(pull(SF_temp,lowBound) %>% unique(),maxAdj),#1e6),
                                  max_iter=maxIt,#1000,#10000
                                  C=1)))
            
            #Update (27AUG2021): Ensure model converges AND calibration totals can be hit
            if (is.null(wgts_temp)){
              log_debug("No convergence")
              wgts_temp <- matrix(nrow=nrow(SF_temp),ncol=1) %>% as.data.frame() %>%
                mutate(!!paste0("FOWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb) := rep(NA,nrow(SF_temp))) %>%
                select(paste0("FOWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb))
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
                  dplyr::mutate(!!paste0("FOWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb) := .) %>%
                  select(paste0("FOWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb))
              } else {
                log_debug("Convergence, calibration failed")
                wgts_temp <- matrix(nrow=nrow(SF_temp),ncol=1) %>% as.data.frame() %>%
                  mutate(!!paste0("FOWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb) := rep(NA,nrow(SF_temp))) %>%
                  select(paste0("FOWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb))
              }
            }
          } else {
            #Skipping bc stopInd==1
            wgts_temp <- matrix(nrow=nrow(SF_temp),ncol=1) %>% as.data.frame() %>%
              mutate(!!paste0("FOWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb) := rep(NA,nrow(SF_temp))) %>%
              select(paste0("FOWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb))
          }
          return(wgts_temp)
          
        },simplify=FALSE) %>%
          bind_cols()
        
      },simplify=FALSE) %>%
        {bind_cols(SF_temp,.)}
      #In case even the crimeVarsWgtAll model fails... 
      #13Aug2025: no longer using gencalib() in this situation... instead, 
      #             just using the inverse crime coverage...
      #           because creating the g-weights here, we need to use 1/(b*r),
      #             where b is the base weight and r is the crime coverage
      
      if (stopInd==0){
        log_debug(paste0("Field Office: ",i,". Weight group: ",j,". n SRS Variables: ",1))
        
        log_debug("stopInd==0")
        
        log_debug("Setting g-weight equal to 1/(r*b),
                  where r is the crime coverage and b is the base weight")
        
        ratio_temp <- ratio %>% 
          filter(FIELD_OFFICE_NAME==i & wgtGpFO==j) %>%
          pull(ratio_totcrime_imp)
        
        wgts_temp <- SF_temp %>%
          mutate(!!paste0("FOWgt_nVar",1,"_comb",1) := 1/(ratio_temp*baseWgt)) %>%
          select(paste0("FOWgt_nVar",1,"_comb",1))
      } else {
        #Skipping bc stopInd==1
        wgts_temp <- matrix(nrow=nrow(SF_temp),ncol=1) %>% as.data.frame() %>%
          mutate(!!paste0("FOWgt_nVar",1,"_comb",1) := rep(NA,nrow(SF_temp))) %>%
          select(paste0("FOWgt_nVar",1,"_comb",1))
      }
      out_temp <- bind_cols(out_temp,
                            wgts_temp)
      
    } else {
      log_debug("No LEAs in field office X weighting group")
      return(NULL)
    }
  },simplify=FALSE) %>%
    bind_rows()
  #If cell not empty, merge on SF
  #13Mar2024: getting errors when merging in certain FOs... modifying merge (only keep certain variables from SF2_wgts_FO)
  if (nrow(SF2_wgts_FO)>0){
    SF2_wgts_FO <- SF2_wgts_FO %>%
	  select(ORI,county,matches("^FOWgt_")) %>% #13Mar2024: added today
      #left_join(SF_temp_FO,by=colnames(SF_temp_FO))
	  left_join(SF_temp_FO,by=c("ORI","county"))
  }
  
  #print(out_temp)
},simplify=FALSE) %>%
  bind_rows()


#####
#Combination summaries

#Update (28OCT2021): Previously was copy-pasting code chunks by number of variables in model. Create function that will streamline
combs_table_FO_gps <- function(indat,crimeVarsWgt,crimeVarsWgtAll,crimeVarsWgtRest,inWgtGps,wgtVar,wgtGpVar,wgtGpDescVar,suffix="",nInWgtGps=length(inWgtGps),nVars=length(crimeVarsWgtRest)){
  log_debug("Running function combs_table_FO_gps")
  inGps <- expand.grid(FIELD_OFFICE_NAME=foGps2,wgtGp=inWgtGps)
  colnames(inGps) <- c("FIELD_OFFICE_NAME",wgtGpVar)
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
      
      #Stack row once per field office X weighting group
      
      temp.out <- temp.out[rep(seq_len(nrow(temp.out)), each = nInGps), ]  %>%
        bind_cols(inGps) %>%
        mutate(!!wgtGpDescVar:=factor(eval(as.symbol(wgtGpVar)),levels=wgtGpsFO2,labels=wgtGpFODescs2))
      #Note (09Jan2023): Removing totcrime_imp requirement
      temp.converge <- indat %>%
        subset(resp_ind_srs==1) %>%
        mutate(converge=!is.na(eval(as.symbol(paste0(wgtVar,"_nVar",temp.nVar+length(crimeVarsWgtAll),"_comb",i))))) %>%
        select(FIELD_OFFICE_NAME,all_of(wgtGpVar),all_of(wgtGpDescVar),converge) %>%
        group_by_at(.vars=c("FIELD_OFFICE_NAME",wgtGpVar,wgtGpDescVar)) %>%
        dplyr::summarize(converge=any(converge),
                         .groups="drop") %>%
        select(FIELD_OFFICE_NAME,all_of(wgtGpVar),all_of(wgtGpDescVar),converge)
      
      temp.out <- temp.out %>% 
        left_join(temp.converge,by=c("FIELD_OFFICE_NAME",wgtGpVar,wgtGpDescVar)) %>%
        left_join(ratio %>% select(FIELD_OFFICE_NAME,wgtGpFO,N,n,sum_totcrime_imp_all,sum_totcrime_imp_NIBRS))
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
  
  #Stack row once per field office X weighting group
  
  temp.out <- temp.out[rep(seq_len(nrow(temp.out)), each = nInGps), ]  %>%
    bind_cols(inGps) %>%
    mutate(!!wgtGpDescVar:=factor(eval(as.symbol(wgtGpVar)),levels=wgtGpsFO2,labels=wgtGpFODescs2))
  #print(temp.out)
  #Note (09Jan2023): Removing totcrime_imp requirement
  temp.converge <- indat %>%
    subset(resp_ind_srs==1) %>%
    mutate(converge=!is.na(eval(as.symbol(paste0(wgtVar,"_nVar",1,"_comb",1))))) %>%
    select(FIELD_OFFICE_NAME,all_of(wgtGpVar),all_of(wgtGpDescVar),converge) %>%
    group_by_at(.vars=c("FIELD_OFFICE_NAME",wgtGpVar,wgtGpDescVar)) %>%
    dplyr::summarize(converge=any(converge),
                     .groups="drop") %>%
    select(FIELD_OFFICE_NAME,all_of(wgtGpVar),all_of(wgtGpDescVar),converge)
  
  out <- temp.out %>% 
    left_join(temp.converge,
              by=c("FIELD_OFFICE_NAME",wgtGpVar,wgtGpDescVar)) %>%
    left_join(ratio %>% select(FIELD_OFFICE_NAME,wgtGpFO,N,n,sum_totcrime_imp_all,sum_totcrime_imp_NIBRS)) %>%
    list()
  colnames(out) %>% print()
  names(out) <- paste0("comb",1,"_table_",suffix)
  list2env(out,envir=.GlobalEnv)
  return(NULL)
}

combs_table_FO_gps(indat=SF2_wgts2_test,crimeVarsWgt,crimeVarsWgtAll,crimeVarsWgtRest,inWgtGps=wgtGpsFO2,
                    wgtVar="FOWgt",wgtGpVar="wgtGpFO",wgtGpDescVar="wgtGpFODesc",
                    suffix="test")




#Update (20Mar2023): Some groups don't have a model that converges - for now, create row representing 0 variables (N/n)
#Update (05May2023): Adding back in
#Update (13Aug2025): Excluding 0 variable code (this is now done in the 
#                      1-variable case)
# comb0_table_test <- SF2_wgts2_test %>% 
#   select(FIELD_OFFICE_NAME,wgtGpFO,wgtGpFODesc) %>% 
#   left_join(ratio %>% select(FIELD_OFFICE_NAME,wgtGpFO,N,n,sum_totcrime_imp_all,sum_totcrime_imp_NIBRS)) %>%
#   mutate(nVar=0,
#          comb=1,
#          converge=TRUE)
#Note (08May2023): Since FOWgt_nVarX_combY is g-weight, need to divide by baseWgt
# SF2_wgts2_test <- SF2_wgts2_test %>%
#   mutate(FOWgt_nVar0_comb1=ifelse(resp_ind_srs==1 & rowSums(!is.na(select(.,matches("FOWgt_nVar\\d"))),na.rm=TRUE)==0,
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
  arrange(FIELD_OFFICE_NAME,wgtGpFO,wgtGpFODesc,-converge,-nVar,comb) %>%
  group_by(FIELD_OFFICE_NAME,wgtGpFO,wgtGpFODesc) %>%
  mutate(Select=ifelse(row_number(wgtGpFO)==1 & converge==TRUE,"X","")) %>%
  ungroup() %>%
  arrange(FIELD_OFFICE_NAME,wgtGpFO,wgtGpFODesc,-nVar,comb) %>%
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
  select(FIELD_OFFICE_NAME,wgtGpFO,wgtGpFODesc,N,n,sum_totcrime_imp_all,sum_totcrime_imp_NIBRS,nVar,comb,
         totcrime_imp,totcrime_violent_imp,
         totcrime_property_imp,totcrime_murder_imp,
         totcrime_rape_imp,
         totcrime_aggAssault_imp,
         totcrime_burglary_imp,totcrime_rob_imp,
         totcrime_larceny_imp,totcrime_vhcTheft_imp,Variables,everything()) %>%
  left_join(foCrosses2)




#Update (14Jun2022): Switching Excel output functions (fixing overwrite bug)
#combAll_table %>%
#  list("All Combinations"=.) %>%
#  write.xlsx(file=paste0(output_weighting_data_folder,"SRS_Variable_Combination_Convergence_by_FO_X_Weighting_Group_Automatic.xlsx"))
log_debug("Writing excel workbook SRS_Variable_Combination_Convergence_by_FO_X_Weighting_Group_AltCombs_Collapsed_Automatic_SRS.xlsx")
workbook <- paste0(output_weighting_data_folder,
                   "SRS_Variable_Combination_Convergence_by_FO_X_Weighting_Group_AltCombs_Collapsed_Automatic_SRS.xlsx")
wb <- createWorkbook()
addWorksheet(wb,"All Combinations")
writeData(wb,"All Combinations",combAll_table)
saveWorkbook(wb,workbook,overwrite=TRUE) 


foCW <- SF %>% 
  select(FIELD_OFFICE_NAME) %>% 
  unique() %>% 
  mutate(FO_CODE=1:nrow(.))

SF2 <- SF2 %>%
  arrange(ORI) %>%
  left_join(foCrosses2) %>% #20Jun2023: joining to cross list
  select(-matches("^(FO_CODE|totcrime_agg_rob_imp)$")) %>%
  inner_join(foCW,by=c("FIELD_OFFICE_NAME")) %>%
  mutate(wgtGpFO2=foCrossNum,
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
  group_by(FIELD_OFFICE_NAME) %>% 
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

if (nrow(ctrlVars)==SF2 %>% select(FIELD_OFFICE_NAME,wgtGpFO) %>% subset(duplicated(.)==FALSE) %>% nrow()){
  
  #capture.output({
  SF2_wgts2 <- sapply(foGps2,function(i){#Loop over weight groupings - just gp 1 for test
    #print("##############################")
    #print(paste0("Field Office: ",i))
    SF_FO <- SF2 %>%
      subset(FIELD_OFFICE_NAME==i) #%>%
    #select(-matches("V\\d+_\\w"))
    #Note (10Jan2023): Removing totcrime_imp requirement
    SF_temp_FO <- SF_FO %>%
      subset(resp_ind_srs==1)
    
    temp_wgtGp1_code <- ctrlVars %>% subset(FIELD_OFFICE_NAME==i & wgtGpFO==1) %>% pull(foCrossNum) %>% unique()
    temp_wgtGp2_code <- ctrlVars %>% subset(FIELD_OFFICE_NAME==i & wgtGpFO==2) %>% pull(foCrossNum) %>% unique()
    temp_wgtGp3_code <- ctrlVars %>% subset(FIELD_OFFICE_NAME==i & wgtGpFO==3) %>% pull(foCrossNum) %>% unique()
    #choosing best model that converges
    ctrlInds_FO <- combAll_table %>% 
      subset(Select=="X" & FIELD_OFFICE_NAME==i) %>% 
      rename_at(.vars=vars(matches("^totcrime")),.funs=~paste0(.x,"_ind")) %>%
      mutate(wgtGpFO2=foCrossNum) %>%
      select(wgtGpFO2,matches("_ind")) %>%
      mutate(across(matches("_ind"),~ifelse(.x!="X",0,1))) %>%
      mutate(across(matches("_ind"),~ifelse(is.na(.x),0,.x))) %>%
      arrange(wgtGpFO2) %>%
      mutate(totcrime_agg_rob_imp_ind=0) %>% #Creating dummy variable to retain same names as national & region
      select(wgtGpFO2,
             totcrime_imp_ind,totcrime_violent_imp_ind,
             totcrime_property_imp_ind,totcrime_murder_imp_ind,
             totcrime_rape_imp_ind,totcrime_agg_rob_imp_ind,
             totcrime_aggAssault_imp_ind,totcrime_burglary_imp_ind,
             totcrime_rob_imp_ind,totcrime_larceny_imp_ind,
             totcrime_vhcTheft_imp_ind)
    
    
    ctrlIndsM_FO <- ctrlInds_FO %>%
      select(colnames(ctrlInds_FO)) %>%
      select(-wgtGpFO2) %>%
      as.matrix()
    
    ctrlTtlsM_FO <- srs_FO_control_totals %>%
      subset(FIELD_OFFICE_NAME==i) %>%
      left_join(foCrosses2) %>% #22Jun2023: merging on cross number
      mutate(wgtGpFO2=foCrossNum) %>%
      arrange(wgtGpFO) %>%
      mutate(sum_totcrime_agg_rob_imp=0) %>% #Creating dummy variable to retain order
      select(sum_totcrime_imp,sum_totcrime_violent_imp,
             sum_totcrime_property_imp,sum_totcrime_murder_imp,
             sum_totcrime_rape_imp,sum_totcrime_agg_rob_imp,
             sum_totcrime_aggAssault_imp,sum_totcrime_burglary_imp,
             sum_totcrime_rob_imp,sum_totcrime_larceny_imp,
             sum_totcrime_vhcTheft_imp) %>%
      as.matrix()
    #print("ncol(ctrlTtlsM_FO):")
    #print(ncol(ctrlTtlsM_FO))
    #print("ncol(ctrlIndsM_FO):")
    #print(ncol(ctrlIndsM_FO))
    #print("nrow(ctrlTtlsM_FO):")
    #print(ncol(ctrlTtlsM_FO))
    #print("nrow(ctrlIndsM_FO):")
    #print(nrow(ctrlIndsM_FO))
    ctrlTtlsM2_FO <- ctrlTtlsM_FO*ctrlIndsM_FO #Element-wise multiplication
    colnames(ctrlTtlsM2_FO) <- LETTERS[1:ncol(ctrlTtlsM2_FO)] #Would normally include 'sum_' before, but will add that later
    
    #13Aug2025: specifying the reshape2 versions of dcast() and melt()
    ctrlTtls2_FO <- ctrlTtlsM2_FO %>%
      data.frame() %>%
      mutate(wgtGpFO2=ctrlInds_FO %>% getElement("wgtGpFO2")) %>%
      reshape2::melt(id.vars="wgtGpFO2") %>%
      reshape2::dcast(formula=.~wgtGpFO2+variable) %>%
      select(-.) #Drop dummy variable
    colnames(ctrlTtls2_FO) <- paste0("sum_V",colnames(ctrlTtls2_FO))
    #print("colnames(ctrlTtls2_FO):")
    #print(colnames(ctrlTtls2_FO))
    
    colnames(ctrlTtls2_FO) <- colnames(ctrlTtls2_FO) %>% str_replace("^(\\w)$","sum_\\1")
    
    #Control variables
    #Note (10Jan2023): Removing totcrime_imp requirement
    ctrlIndsM_FO <- ctrlInds_FO %>%
      inner_join(SF_FO) %>%
      subset(FIELD_OFFICE_NAME==i & resp_ind_srs==1) %>%
      arrange(ORI) %>%
      select(colnames(ctrlInds_FO)) %>%
      select(-wgtGpFO2) %>%
      as.matrix()
    #Note (10Jan2023): Removing totcrime_imp requirement
    ctrlVarsM_FO <- SF2%>%
      subset(FIELD_OFFICE_NAME==i & resp_ind_srs==1) %>%
      arrange(ORI) %>%
      select(totcrime_imp,totcrime_violent_imp,totcrime_property_imp,
             totcrime_murder_imp,
             totcrime_rape_imp,totcrime_agg_rob_imp,
             totcrime_aggAssault_imp,totcrime_burglary_imp,
             totcrime_rob_imp,totcrime_larceny_imp,
             totcrime_vhcTheft_imp) %>%
      as.matrix()
    
    #print("ncol(ctrlVarsM_FO):")
    #print(ncol(ctrlVarsM_FO))
    #print("ncol(ctrlIndsM_FO):")
    #print(ncol(ctrlIndsM_FO))
    #print("nrow(ctrlVarsM_FO):")
    #print(nrow(ctrlVarsM_FO))
    #print("nrow(ctrlIndsM_FO):")
    #print(nrow(ctrlIndsM_FO))
    ctrlVarsM2_FO <- ctrlVarsM_FO*ctrlIndsM_FO
    colnames(ctrlVarsM2_FO) <- LETTERS[1:ncol(ctrlVarsM2_FO)]
    
    #print("ctrVars2_FO")
    ctrlVars2_FO <- ctrlVarsM2_FO %>%
      data.frame() %>%
      #Note (10Jan2023): Removing totcrime_imp requirement
      mutate(ORI=SF_FO %>% arrange(ORI) %>% subset(FIELD_OFFICE_NAME==i & resp_ind_srs==1) %>% pull(ORI),
             county=SF_FO %>% arrange(ORI) %>% subset(FIELD_OFFICE_NAME==i & resp_ind_srs==1) %>% pull(county),
             wgtGpFO2=SF_FO %>% arrange(ORI) %>% subset(FIELD_OFFICE_NAME==i & resp_ind_srs==1) %>% pull(wgtGpFO2))
      
      #Note (22Jun2023): Only create if they exist
      if (length(temp_wgtGp1_code)==1){
        ctrlVars2_FO <- ctrlVars2_FO %>%
          mutate(across(matches("^\\w{1}$"),
                        .fns=~.x*ifelse(wgtGpFO2==temp_wgtGp1_code,1,0),
                        .names=paste0("V",temp_wgtGp1_code,"_{col}")))
      }
    if (length(temp_wgtGp2_code)==1){
      ctrlVars2_FO <- ctrlVars2_FO %>%
        mutate(across(matches("^\\w{1}$"),
                      .fns=~.x*ifelse(wgtGpFO2==temp_wgtGp2_code,1,0),
                      .names=paste0("V",temp_wgtGp2_code,"_{col}")))
    }
    if (length(temp_wgtGp3_code)==1){ 
      ctrlVars2_FO <- ctrlVars2_FO %>%
        mutate(across(matches("^\\w{1}$"),
                      .fns=~.x*ifelse(wgtGpFO2==temp_wgtGp3_code,1,0),
                      .names=paste0("V",temp_wgtGp3_code,"_{col}")))
    }
    
    
    #Add on the new control totals/variables
    SF_FO <- SF_FO %>%
      full_join(ctrlVars2_FO) %>%
      #select(-matches("^sum_\\w+_imp$")) %>%
      #full_join(ctrlTtls2) %>%
      arrange(ORI)
    #Note (10Jan2023): Removing totcrime_imp requirement
    SF_temp <- SF_FO%>%
      subset(resp_ind_srs==1)
    
    #21Mar2023: adding requirement that columns are in ctrlTtls2_FO
    temp.ctrlVars <- colnames(ctrlVars2_FO) %>% 
      str_subset("^V\\d+_\\w$") %>% 
      subset(. %in% (colnames(ctrlTtls2_FO) %>% str_remove("sum_")))
    #Update (28OCT2021): Comment out print statement
    #print(temp.ctrlVars)
    if (length(temp.ctrlVars)==0){
      temp.ctrlVars <- "totcrime_imp"
    }
    total_temp <- ctrlTtls2_FO %>%
      select(all_of(paste0("sum_",temp.ctrlVars))) %>%
      as.numeric()
    #names(total_temp) <- NULL
    vars_temp <- SF_temp %>%
      select(all_of(temp.ctrlVars)) 
    
    ratio_FO <- ratio %>% subset(FIELD_OFFICE_NAME==i)
    #names(vars_temp) <- NULL
    #Update (10Oct2022): Don't redo calibration, juse use weights from earlier
    #print("gencalib(Xs=select(SF_temp,all_of(temp.ctrlVars)), ...:")
    # SF_temp_wgts2 <- gencalib(Xs=vars_temp,
    #                       Zs=vars_temp,
    #                       #d=rep(1,nrow(SF_temp)),
    #                       d=rep(ratio_FO$baseWgt,nrow(SF_temp)),
    #                       total=total_temp,
    #                       method="logit",
    #                       #bounds=c(low=1,1e6),
    #                       bounds=c(low=ratio_FOlowBound,maxWgt/ratio_FO$baseWgt),#1e6),
    #                       max_iter=5*maxIt,#10000
    #                       C=1,
    #                       description=TRUE) %>%
    #   data.frame(gWgt=.) %>%
    #   mutate(FOWgt=gWgt*ratio_FO$baseWgt) %>%
    #   {bind_cols(SF_temp,.)} %>%
    #   full_join(SF_FO,by=colnames(SF_FO))
    #Note (10Jan2023): Removing totcrime_imp requirement
    SF_temp_wgts2 <- SF2_wgts2_test %>%
      subset(resp_ind_srs==1 & FIELD_OFFICE_NAME==i) %>%
      mutate(gWgt=select(.,matches("FOWgt_nVar\\d")) %>% rowMeans(na.rm=TRUE)) %>%
      mutate(FOWgt=gWgt*baseWgt) %>%
      select(ORI,county,gWgt,FOWgt) %>%
      right_join(SF_temp)
    #print("SF_temp_wgts2:")
    #print(SF_temp_wgts2)
    #print("select(SF_temp_wgts2,all_of(temp.ctrlVars)) %>% as.matrix():")
    #print(select(SF_temp_wgts2,all_of(temp.ctrlVars)) %>% as.matrix())
    #print("rep(ratio_FO$baseWgt,nrow(SF_temp_wgts2)):")
    #print(rep(ratio_FO$baseWgt,nrow(SF_temp_wgts2)))
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
    temp.wgtGps <- srs_FO_control_totals %>%
      subset(FIELD_OFFICE_NAME==i) %>%
      pull(wgtGpFO)
    SF2_wgts_FO <- sapply(temp.wgtGps,function(j){#Loop over weight groupings
      message("##############")
      message(paste0("Field Office: ",i,". Weight group: ",j))
      #Take weighting group subset within FO subset
      #Note (10Jan2023): Removing totcrime_imp requirement
      if (j==1){
        temp_wgtGp_code <- temp_wgtGp1_code
      } else if (j==2){
        temp_wgtGp_code <- temp_wgtGp2_code
      } else if (j==3){
        temp_wgtGp_code <- temp_wgtGp3_code
      }
      SF_temp <- SF_temp_wgts2 %>%
        subset(wgtGpFO==j & resp_ind_srs==1)
      if (nrow(SF_temp)>0){
        #print("hi")
        temp.ctrlVars <- colnames(SF_temp) %>% 
          str_subset(paste0("^V",temp_wgtGp_code,"_\\w$"))
        
        
        total_temp_FO <- ctrlTtls2_FO %>%
          select(all_of(paste0("sum_",temp.ctrlVars))) %>%
          as.numeric()
        #print(total_temp_FO)
        out_temp <- SF_temp
        
        #Update (20AUG2021): Adding requested checks
        #Update (05Jul2022): Switch to table format (1 row per weight group) - commenting out old cold
        #Update (13Aug2025): added min and max to checks
        
        # #Check calibration
        # print("checkcalibration(Xs=select(SF_temp,all_of(temp.ctrlVars)), ...:")
        # checkcalibration(Xs=select(SF_temp,all_of(temp.ctrlVars)),
        #                  d=rep(1,nrow(SF_temp)),
        #                  total=total_temp,
        #                  g=out_temp$FOWgt,
        #                  EPS=1) %>%
        #   print()
        # #Weight checks - summary, UWE, etc.
        # print("Distribution of weights:")
        # describe(out_temp$FOWgt) %>%
        #   print()
        # print("Number of missing weights:")
        # sum(is.na(out_temp$FOWgt))%>%
        #   print()
        # print("Number of weights equal to 1:")
        # sum(out_temp$FOWgt == 1, na.rm=TRUE) %>%
        #   print()
        # print("Number of weights greater than 1:")
        # sum(out_temp$FOWgt > 1, na.rm=TRUE) %>%
        #   print()
        # print("Number of weights less than 1:")
        # sum(out_temp$FOWgt < 1, na.rm=TRUE) %>%
        #   print()
        # print("Number of weights greater than 100:")
        # sum(out_temp$FOWgt > 100, na.rm=TRUE) %>%
        #   print()
        # print("UWE:")
        # UWE_FOWgt <- 1+var(out_temp$FOWgt,na.rm=TRUE)/(mean(out_temp$FOWgt,na.rm=TRUE)^2)
        # UWE_FOWgt %>%
        #   print()
        
        #Calibration worked (T/F)?
        temp.cal <- checkcalibration(Xs=select(SF_temp,all_of(temp.ctrlVars)) %>% 
                                       as.matrix(),
                                     d=pull(SF_temp,baseWgt),
                                     total=total_temp_FO,
                                     g=out_temp$gWgt,
                                     EPS=ifelse(any(total_temp_FO==0),1,1e-6))%>%#EPS=1) %>%
          .$result
        #temp.describe <- describe(out_temp$FOWgt)
        temp.nmiss <- sum(is.na(out_temp$FOWgt))
        temp.nonmiss <- nrow(out_temp) - temp.nmiss
        temp.mean <- mean(out_temp$FOWgt, na.rm = TRUE)
        temp.quantiles <- quantile(out_temp$FOWgt,
                                   probs=c(0,0.05,0.1,0.25,0.5,0.75,0.9,0.95,1),
                                   na.rm=TRUE)
        #Note (26Jul2022): Adding n Eligible LEAs
        temp.nElig <- SF2 %>%
          subset(FIELD_OFFICE_NAME==i & wgtGpFO==j) %>%
          nrow()
        #06Jun2024: round to 6 digits before checking for weights <1
        temp.nLT1 <- sum(round(out_temp$FOWgt,digits=6) < 1 & out_temp$FOWgt>0, na.rm=TRUE)
        #Note (29Jul2022): Switching from >100 to >20
        #temp.nGT100 <- sum(out_temp$FOWgt > 100, na.rm=TRUE)
        temp.nGT20 <- sum(out_temp$FOWgt > 20, na.rm=TRUE)
        temp.UWE <- 1+var(out_temp$FOWgt,na.rm=TRUE)/(mean(out_temp$FOWgt,na.rm=TRUE)^2)
        temp.out <- data.frame(foGp=i,
                               wgtGpFODesc=wgtGpFODescs2[which(wgtGpsFO2==j)],
                               calibrated=temp.cal,
                               #Note (26Jul2022): Changing counts - include n Eligible LEAs, n NIBRS LEAs, n NIBRS LEAs missing weights
                               #nOverall=as.numeric(temp.describe$counts["n"])+as.numeric(temp.describe$counts["missing"]),
                               nElig=temp.nElig,
                               #nNIBRS=as.numeric(temp.describe$counts["n"])+as.numeric(temp.describe$counts["missing"]),
                               #nMissing=as.numeric(temp.describe$counts["missing"]),
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
        colnames(temp.out) <- c("Field Office","Weight Group","Calibrated",
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
	#13Mar2024: issues during merge... reducing number of variables to only ID variables plus new variables (gWgt, FOWgt, and calibration variables
	select(ORI,county,gWgt,FOWgt,matches("V\\d+_\\w")) %>%
    #full_join(SF2,by=colnames(SF2))
	full_join(SF2,by=c("ORI","county"))
  #},file=paste0(output_weighting_data_folder,'weights_FO_checks.txt'))
  #Note (JDB 06Jul2022): Combine weight check results
  results_FO <- #outer(paste0("results_",foGps2,"_"),wgtGpsFO,FUN=paste0) %>%
    #as.character() %>% 
    SF2 %>% 
    select(FIELD_OFFICE_NAME,wgtGpFO) %>% 
    subset(duplicated(.)==FALSE) %>% 
    mutate(name=paste0("results_",FIELD_OFFICE_NAME,"_",wgtGpFO)) %>% 
    pull(name) %>%
    mget(envir=.GlobalEnv) %>%
    bind_rows()
  
  
  
  
  ###############
  #Output
  #Note (12Apr2023): Stacking skipped crossings
  new_weights <- SF2_wgts2 %>%
    bind_rows(SF2_skips)
  
  ### export for others to start writing functions to analyze bias, MSE, etc.
  new_weights[,c("ORI_universe","county","FIELD_OFFICE_NAME","wgtGpFO","wgtGpFODesc",
                 #Update (27AUG2021): Add raw weight group variable
                 "wgtGpFO_raw","wgtGpFODesc_raw",
                 "FOWgt")] %>%
    #write.csv(paste0(output_weighting_data_folder,'weights_FO.csv'),
    fwrite_wrapper(paste0(output_weighting_data_folder,'weights_FO_cal_srs_altcombs_col_srs.csv'))
  
  #Update (26AUG2021): Add wgtGpFO and wgtGpFODesc to SF file from 02_Weights_Data_Setup
  # oldSF <- read_csv(paste0(input_weighting_data_folder,"SF_postN.csv"),
  #                   guess_max=1e6)%>%
  #   #Adding just in case already on file...
  #   select(-matches("wgtGpFO"))
  calVars <- colnames(SF2_wgts2) %>%
    str_subset("^V\\d+_\\w") %>% #All calibration vars
    str_subset("^V(\\d|1\\d|20)_\\w$",negate=TRUE) #Remove national calibration vars
  calVarsRegEx <- str_flatten(calVars,collapse="|")
  oldSF <- fread(paste0(input_weighting_data_folder,"SF_srs.csv"))%>%
    #Adding just in case already on file...
    select(-matches(paste0("(wgtGpFO|",calVars,")")))%>%
    mutate(totcrime_imp=totcrime_violent_imp+totcrime_property_imp) %>%
    mutate(totcrime_agg_rob_imp=totcrime_aggAssault_imp+totcrime_rob_imp)
  
  newSF <- oldSF %>%
    left_join(bind_rows(SF2,SF2_skips) %>% 
                select(ORI_universe,county,FIELD_OFFICE_NAME,wgtGpFO,wgtGpFODesc,
                             #Update (27AUG2021): Add raw weight group variable
                             wgtGpFO_raw,wgtGpFODesc_raw),
              by=c("ORI_universe","county","FIELD_OFFICE_NAME")) %>%
    #Update (18Jan2023): adding new calibration variables
    left_join(SF2_wgts2 %>%
                select(ORI_universe,county,FIELD_OFFICE_NAME,all_of(calVars)),
              by=c("ORI_universe","county","FIELD_OFFICE_NAME"))
  
  #write_csv(newSF,file=paste0(output_weighting_data_folder,"SF_postS_cal.csv"))
  fwrite_wrapper(newSF,paste0(output_weighting_data_folder,"SF_postFO_cal_srs_altcombs_col_srs.csv"))
  
  #Note (JDB 06Jul2022): Export weight check results
  #write_csv(results_FO,
  fwrite_wrapper(results_FO,
         paste0(output_weighting_data_folder,"weights_FO_cal_srs_altcombs_col_checks_srs.csv"))
  #Track list of FOs
  fo_all <- SF %>%
    subset(!is.na(FIELD_OFFICE_NAME)) %>%
    select(FIELD_OFFICE_NAME) %>%
    unique() %>%
    arrange(FIELD_OFFICE_NAME)
  fwrite_wrapper(fo_all,
         paste0(output_weighting_data_folder,"fo_all_srs.csv"))
  
} else {
  stop("No calibration model converged for 1+ (field office X weighting group) crossing")
}
log_info("Finished 03_Weights_Calibration_FO_SRS_AltCombs_Collapsed_SRS.R\n\n")
