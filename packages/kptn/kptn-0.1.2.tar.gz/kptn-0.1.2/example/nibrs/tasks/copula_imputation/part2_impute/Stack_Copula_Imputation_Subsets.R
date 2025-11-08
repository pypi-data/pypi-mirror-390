#This program will...
#	(a) stack together the 3 subsets:
#1) Nonzero population, not missing demographic variables (Nonzero_Pop)
#2) Nonzero population, missing demographic variables (Missing_Demo)
#3) Zero population
#	(b) create any necessary agency-level table variables or other direct mapping variables
#Creation date: April 18, 2022
#Note (28Jun2023): Switching from agency-level pop to (agency X county)-level pop
library(data.table)
log_debug("Start of stack file. This includes temp solution.")
source("Copula_Imputation_Functions.R")
#Subsets of data
subsets <- c("popResidAgcyCounty_cbi>0 & nDemoMissing==0",
             "popResidAgcyCounty_cbi>0 & nDemoMissing>0",
             "popResidAgcyCounty_cbi==0")
#21May2024: reverting from fread() back to read_csv() [issues with 'special' column] 
temp.rowSpecs <- read_csv("../data/Indicator_Table_Row_Specs.csv") %>%
  filter(table==temp.table)
temp.special <- temp.rowSpecs$special %>% unique()

temp.step1Specs <- temp.rowSpecs %>%
  subset(type==0)
temp.step1Rows <- temp.step1Specs$rows
temp.step1RowsRegEx <- str_flatten(temp.step1Rows,col="|")

temp.step2Specs <- temp.rowSpecs %>%
  subset(tier %in% 1:2)
temp.step2Sects <- temp.step2Specs %>%
  .$section
temp.step2Rows <- temp.step2Specs %>%
  .$rows

#Note (JDB 04May2022): Supporting column sets
temp.colsets <- temp.rowSpecs %>%
  subset(table==temp.table) %>%
  .$columns %>%
  unique() %>%
  str_split(pattern=",") %>%
  unlist()

permutations <- paste0(filepathin_initial, "POP_TOTALS_PERM_", year, ".csv") %>%
  read_csv() #13Oct2022: Trouble when trying fread() ... leaving as read_csv() for now

temp.ttlPop <- permutations %>%
  subset(PERMUTATION_NUMBER==temp.perm) %>%
  .$POP_TOTAL_WEIGHTED
########
########
#Get row specs for tier 3 (97=direct row-to-variable mapping, 98=pop group, 99=agency indicator)

#Direct mapping
temp.tier3Specs <- temp.rowSpecs %>%
  subset(tier==3)
temp.tier3Type97Specs <- temp.tier3Specs %>%
  subset(type==97)

if (nrow(temp.tier3Type97Specs)>0){
  temp.tier3Type97Sects <- temp.tier3Type97Specs$section
  temp.tier3Type97Rows <- temp.tier3Type97Specs$rows
  temp.tier3Type97Maps <- temp.tier3Type97Specs$mapping
}
#Population group
temp.tier3Type98Specs <- temp.tier3Specs %>%
  subset(type==98)
if (nrow(temp.tier3Type98Specs)>0){
  temp.popGpPrefix <- paste0("t_",temp.table,"_",temp.tier3Type98Specs$section)
  #Note (18APR2022): # of population groups vary as of note
  temp.popGpRows <- parse(text=temp.tier3Type98Specs$rows) %>% eval() %>% as.numeric()
  #log_debug("length(temp.popGpRows)")
  #print(length(temp.popGpRows))
  log_debug("temp.popGpList")
  if (length(temp.popGpRows)==6){
    temp.popGpList <- list(c("Cities from 250,000 thru 499,999",
                             "Cities from 100,000 thru 249,999",
                             "Cities from 500,000 thru 999,999",
                             "Cities 1,000,000 or over",
                             "MSA counties 100,000 or over",
                             "Non-MSA counties 100,000 or over"),
                           c("Cities from 25,000 thru 49,999",
                             "Cities from 50,000 thru 99,999",
                             "MSA counties from 25,000 thru 99,999",
                             "Non-MSA counties from 25,000 thru 99,999"),
                           c("Cities from 10,000 thru 24,999",
                             "MSA counties from 10,000 thru 24,999",
                             "Non-MSA counties from 10,000 thru 24,999"),
                           c("Cities from 2,500 thru 9,999",
                             "Cities under 2,500",
                             "Non-MSA counties under 10,000",
                             "MSA counties under 10,000"),
                           c("MSA State Police",
                             "Non-MSA State Police"),
                           "Possessions (Puerto Rico, Guam, Canal Zone, Virgin Islands, and American Samoa)")
  } else if (length(temp.popGpRows)==5){
    temp.popGpList <- list(c("Cities from 250,000 thru 499,999",
                             "Cities from 100,000 thru 249,999",
                             "Cities from 500,000 thru 999,999",
                             "Cities 1,000,000 or over",
                             "MSA counties 100,000 or over",
                             "Non-MSA counties 100,000 or over"),
                           c("Cities from 25,000 thru 49,999",
                             "Cities from 50,000 thru 99,999",
                             "MSA counties from 25,000 thru 99,999",
                             "Non-MSA counties from 25,000 thru 99,999"),
                           c("Cities from 10,000 thru 24,999",
                             "MSA counties from 10,000 thru 24,999",
                             "Non-MSA counties from 10,000 thru 24,999"),
                           c("Cities from 2,500 thru 9,999",
                             "Cities under 2,500",
                             "Non-MSA counties under 10,000",
                             "MSA counties under 10,000"),
                           c("MSA State Police",
                             "Non-MSA State Police"))
  }
}
#print(temp.popGpList)
temp.tier3Type99Specs <- temp.tier3Specs %>%
  subset(type==99)

if (nrow(temp.tier3Type99Specs)>0){
  temp.agcyIndPrefix <- paste0("t_",temp.table,"_",temp.tier3Type99Specs$section)
  #Note (18APR2022): # of agency types vary as of note
  temp.agcyIndRows <- parse(text=temp.tier3Type99Specs$rows) %>% eval() %>% as.numeric()
  if (length(temp.agcyIndRows)==7){
    temp.agcyIndList <- list("City",
                             "County",
                             "University or College",
                             "State Police",
                             "Other State Agency",
                             "Tribal",
                             "Federal")
  } else if (length(temp.agcyIndRows)==6){
    temp.agcyIndList <- list("City",
                             "County",
                             "University or College",
                             "State Police",
                             "Other State Agency",
                             "Tribal")
  }
}
#Note (JDB 04MAY2022): Support special case
temp.tier4Type96Specs <- temp.rowSpecs %>%
  subset(tier==4)

#Note (20APR2022): Only edit variables if nrow>0
#Note (JDB 04MAY2022): Support column sets
#Note (JDB 09MAY2023): Supporting stratification
final <- data.frame()
tempEnv <- environment()
sapply(1:length(temp.colsets),function(temp.colnum){
  #Note (JDB 15May2022): Attempt to handle occassional incompatible types issue - start finalA/B/C as empty dataframes and add 'else' for cases where nrow=0
  sapply(temp.stratVars,function(temp.stratVar){
    sapply(temp.stratLvls,function(temp.stratLvl){
      finalA <- data.frame()
      finalB <- data.frame()
      finalC <- data.frame()
      tempEnvB <- environment()
      if (file.exists(file.path(output_copula_data_folder,
                                paste0("Table_",temp.table,"_Final_Agency_File_Perm_",temp.perm,"_ColNum_",temp.colnum,"_Nonzero_Pop_Rates_",temp.stratVar,"_",temp.stratLvl,".csv")))){
        finalA <- fread(file=file.path(output_copula_data_folder,
                                       paste0("Table_",temp.table,"_Final_Agency_File_Perm_",temp.perm,"_ColNum_",temp.colnum,"_Nonzero_Pop_Rates_",temp.stratVar,"_",temp.stratLvl,".csv"))) %>%
          data.frame()
        if (nrow(finalA)>0){
          finalA <- finalA %>%
            mutate(across(matches("^popResidAgcy"),as.numeric,.names="{.col}")) %>%
            mutate(across(matches("^totcrime"),as.numeric,.names="{.col}")) %>%
            mutate(across(matches("^(age|race|sex)",ignore.case=FALSE),as.numeric,.names="{.col}"))%>%
            mutate(across(matches("^t_"),as.numeric,.names="{.col}")) %>%
            mutate(weight=as.numeric(weight))%>%
            mutate(AGENCY_TYPE_NAME=as.character(AGENCY_TYPE_NAME))%>%
            mutate(PARENT_POP_GROUP_CODE=as.numeric(PARENT_POP_GROUP_CODE)) %>%
            mutate(REGION_CODE=as.numeric(REGION_CODE))%>%
            mutate(PE_MALE_OFFICER_COUNT=as.numeric(PE_MALE_OFFICER_COUNT))%>%
            mutate(PE_FEMALE_OFFICER_COUNT=as.numeric(PE_FEMALE_OFFICER_COUNT))%>%
            mutate(TOT_OFFICER_COUNT=as.numeric(TOT_OFFICER_COUNT))%>%
            mutate(nDemoMissing=as.numeric(nDemoMissing)) %>%
            mutate(der_national=as.numeric(der_national)) %>%
            #03Jul2023: ensuring county is character
            mutate(county=str_pad(county,side="left",pad="0",width=3))
          
          #JDB 28Aug2022: Temporary fix - handle issues with constant values
          #JDB 28Aug2024: Rather than loop over every variable, let's first get a list of variables with issues, and only loop over the problematic ones
          temp.issueVars <- finalA %>%
            summarize(across(matches("^t_"),~any(is.na(.x)))) %>%
            mutate(one=1) %>%
            reshape2::melt(id.vars="one") %>%
            subset(value==TRUE) %>%
            pull(variable)
          sapply(1:length(temp.step2Sects),function(j){
            temp.envLoop <- environment()
            temp.sect <- temp.step2Sects[j]
            temp.rows <- temp.step2Rows[j]
            temp.vars <- colnames(finalA) %>% 
			  str_subset(paste0("^t_",temp.table,"_",temp.sect,"_",temp.rows)) %>%
              #28Aug2024: added subset
              subset(. %in% temp.issueVars)
            if (length(temp.vars)>0){#28Aug2024: adding if() just in case temp.vars now empty
              #06Jun2025: create a dataset with limited # of variables
              finalA2 <- data.frame(finalA) %>%
                select(ORI,county,sourceInd,matches(str_c("^t_",temp.table,"_\\d+_",temp.step1RowsRegEx,"_\\d+$")),all_of(temp.vars))
              sapply(temp.vars,function(temp.var){
                temp.col <- temp.var %>%
                  str_extract("(?<=_)\\d+$") %>%
                  as.numeric()
                temp.step1Var <- colnames(finalA2) %>% str_subset(paste0("t_",temp.table,"_\\d+_",temp.step1RowsRegEx,"_",temp.col))
                if(any(finalA2 %>% select(all_of(temp.var)) %>% is.na())){
                  log_debug(paste0("Fixing ",temp.var," for finalA column set ",temp.colnum))
                  
                  if(nrow(finalA2 %>% subset(sourceInd=="NIBRS" & eval(as.symbol(temp.step1Var))>0))>0){
                    temp.constVal <- finalA2 %>% 
                      subset(sourceInd=="NIBRS" & eval(as.symbol(temp.step1Var))>0) %>% 
                      getElement(temp.var) %>%
                      mean()
                  } else {
                    temp.constVal <- 0
                  }
                  finalA2 <- finalA2 %>%
                    mutate(!!temp.var := ifelse(sourceInd=="SRS" & eval(as.symbol(temp.step1Var))>0,
                                                min(temp.constVal,eval(as.symbol(temp.step1Var))),
                                                eval(as.symbol(temp.var))))%>%
                    mutate(!!temp.var := ifelse(sourceInd=="SRS" & eval(as.symbol(temp.step1Var))==0,
                                                0,
                                                eval(as.symbol(temp.var))))
                  list2env(list("finalA2"=finalA2),envir=temp.envLoop)
                }
                
                return(NULL)
              })
              #06Jun2025: now, merge & add on the fixed columns
              finalA2 <- finalA2 %>%
                select(ORI,county,all_of(temp.vars))
              finalA <- finalA %>%
                select(-all_of(temp.vars)) %>%
                full_join(finalA2,by=c("ORI","county"))
            }
            list2env(list("finalA"=finalA),envir=tempEnvB)
            return(NULL)
          })
          if ("p" %in% colnames(finalA)){
            finalA <- finalA %>%
              mutate(p=as.numeric(p))
          }
          if ("den" %in% colnames(finalA)){
            finalA <- finalA %>%
              mutate(den=as.numeric(den))
          }
        } else {
          finalA <- data.frame()
        }
      } else {
        finalA <- data.frame()
      }
      if (file.exists(file.path(output_copula_data_folder,
                                paste0("Table_",temp.table,"_Final_Agency_File_Perm_",temp.perm,"_ColNum_",temp.colnum,"_Missing_Demo_Rates_",temp.stratVar,"_",temp.stratLvl,".csv")))){
        finalB <- fread(file=file.path(output_copula_data_folder,
                                       paste0("Table_",temp.table,"_Final_Agency_File_Perm_",temp.perm,"_ColNum_",temp.colnum,"_Missing_Demo_Rates_",temp.stratVar,"_",temp.stratLvl,".csv"))) %>%
          data.frame()
        if (nrow(finalB)>0){
          finalB <- finalB %>%
            mutate(across(matches("^popResidAgcy"),as.numeric,.names="{.col}")) %>%
            mutate(across(matches("^totcrime"),as.numeric,.names="{.col}")) %>%
            mutate(across(matches("^(age|race|sex)",ignore.case=FALSE),as.numeric,.names="{.col}")) %>%
            mutate(across(matches("^t_"),as.numeric,.names="{.col}")) %>%
            mutate(weight=as.numeric(weight)) %>%
            mutate(AGENCY_TYPE_NAME=as.character(AGENCY_TYPE_NAME)) %>%
            mutate(PARENT_POP_GROUP_CODE=as.numeric(PARENT_POP_GROUP_CODE)) %>%
            mutate(REGION_CODE=as.numeric(REGION_CODE))%>%
            mutate(PE_MALE_OFFICER_COUNT=as.numeric(PE_MALE_OFFICER_COUNT))%>%
            mutate(PE_FEMALE_OFFICER_COUNT=as.numeric(PE_FEMALE_OFFICER_COUNT))%>%
            mutate(TOT_OFFICER_COUNT=as.numeric(TOT_OFFICER_COUNT)) %>%
            mutate(nDemoMissing=as.numeric(nDemoMissing)) %>%
            mutate(der_national=as.numeric(der_national)) %>%
            #03Jul2023: ensuring county is character
            mutate(county=str_pad(county,side="left",pad="0",width=3))
          #JDB 28Aug2022: Temporary fix - handle issues with constant values
          #JDB 28Aug2024: Rather than loop over every variable, let's first get a list of variables with issues, and only loop over the problematic ones
          temp.issueVars <- finalB %>%
            summarize(across(matches("^t_"),~any(is.na(.x)))) %>%
            mutate(one=1) %>%
            reshape2::melt(id.vars="one") %>%
            subset(value==TRUE) %>%
            pull(variable)
          sapply(1:length(temp.step2Sects),function(j){
            temp.envLoop <- environment()
            temp.sect <- temp.step2Sects[j]
            temp.rows <- temp.step2Rows[j]
            temp.vars <- colnames(finalB) %>% 
			  str_subset(paste0("t_",temp.table,"_",temp.sect,"_",temp.rows)) %>%
              #28Aug2024: added subset
              subset(. %in% temp.issueVars)
            if (length(temp.vars)>0){#28Aug2024: adding if() just in case temp.vars now empty
              #06Jun2025: create a dataset with limited # of variables
              finalB2 <- data.frame(finalB) %>%
                select(ORI,county,sourceInd,matches(str_c("^t_",temp.table,"_\\d+_",temp.step1RowsRegEx,"_\\d+$")),all_of(temp.vars))
              sapply(temp.vars,function(temp.var){
                temp.col <- temp.var %>%
                  str_extract("(?<=_)\\d+$") %>%
                  as.numeric()
                temp.step1Var <- colnames(finalB2) %>% str_subset(paste0("t_",temp.table,"_\\d+_",temp.step1RowsRegEx,"_",temp.col))
                if(any(finalB2 %>% select(all_of(temp.var)) %>% is.na())){
                  log_debug(paste0("Fixing ",temp.var," for finalB column set ",temp.colnum))
                  if(nrow(finalB2 %>% subset(sourceInd=="NIBRS" & eval(as.symbol(temp.step1Var))>0))>0){
                    temp.constVal <- finalB2 %>% 
                      subset(sourceInd=="NIBRS" & eval(as.symbol(temp.step1Var))>0) %>% 
                      getElement(temp.var) %>%
                      mean()
                  } else {
                    temp.constVal <- 0
                  }
                  finalB2 <- finalB2 %>%
                    mutate(!!temp.var := ifelse(sourceInd=="SRS" & eval(as.symbol(temp.step1Var))>0,
                                                min(temp.constVal,eval(as.symbol(temp.step1Var))),
                                                eval(as.symbol(temp.var))))%>%
                    mutate(!!temp.var := ifelse(sourceInd=="SRS" & eval(as.symbol(temp.step1Var))==0,
                                                0,
                                                eval(as.symbol(temp.var))))
                  list2env(list("finalB2"=finalB2),envir=temp.envLoop)
                }
                return(NULL)
              })
              #06Jun2025: now, merge & add on the fixed columns
              finalB2 <- finalB2 %>%
                select(ORI,county,all_of(temp.vars))
              finalB <- finalB %>%
                select(-all_of(temp.vars)) %>%
                full_join(finalB2,by=c("ORI","county"))
            }
            list2env(list("finalB"=finalB),envir=tempEnvB)
            return(NULL)
          })
          if ("p" %in% colnames(finalB)){
            finalB <- finalB %>%
              mutate(p=as.numeric(p))
          }
          if ("den" %in% colnames(finalB)){
            finalB <- finalB %>%
              mutate(den=as.numeric(den))
          }
        } else {
          finalB <- data.frame()
        }
      } else {
        finalB <- data.frame()
      }
      if (file.exists(file.path(output_copula_data_folder,
                                paste0("Table_",temp.table,"_Final_Agency_File_Perm_",temp.perm,"_ColNum_",temp.colnum,"_Zero_Pop_Rates_",temp.stratVar,"_",temp.stratLvl,".csv")))){
        finalC <- fread(file=file.path(output_copula_data_folder,
                                       paste0("Table_",temp.table,"_Final_Agency_File_Perm_",temp.perm,"_ColNum_",temp.colnum,"_Zero_Pop_Rates_",temp.stratVar,"_",temp.stratLvl,".csv"))) %>%
          data.frame()			
        if (nrow(finalC)>0){
          finalC <- finalC %>%
            mutate(across(matches("^popResidAgcy"),as.numeric,.names="{.col}")) %>%
            mutate(across(matches("^totcrime"),as.numeric,.names="{.col}")) %>%
            mutate(across(matches("^(age|race|sex)",ignore.case=FALSE),as.numeric,.names="{.col}")) %>%
            mutate(across(matches("^t_"),as.numeric,.names="{.col}")) %>%
            mutate(weight=as.numeric(weight)) %>%
            mutate(AGENCY_TYPE_NAME=as.character(AGENCY_TYPE_NAME)) %>%
            mutate(PARENT_POP_GROUP_CODE=as.numeric(PARENT_POP_GROUP_CODE)) %>%
            mutate(REGION_CODE=as.numeric(REGION_CODE))%>%
            mutate(PE_MALE_OFFICER_COUNT=as.numeric(PE_MALE_OFFICER_COUNT))%>%
            mutate(PE_FEMALE_OFFICER_COUNT=as.numeric(PE_FEMALE_OFFICER_COUNT))%>%
            mutate(TOT_OFFICER_COUNT=as.numeric(TOT_OFFICER_COUNT))  %>%
            mutate(nDemoMissing=as.numeric(nDemoMissing)) %>%
            mutate(der_national=as.numeric(der_national)) %>%
            #03Jul2023: ensuring county is character
            mutate(county=str_pad(county,side="left",pad="0",width=3))
          #JDB 28Aug2022: Temporary fix - handle issues with constant values
          #JDB 28Aug2024: Rather than loop over every variable, let's first get a list of variables with issues, and only loop over the problematic ones
          temp.issueVars <- finalC %>%
            summarize(across(matches("^t_"),~any(is.na(.x)))) %>%
            mutate(one=1) %>%
            reshape2::melt(id.vars="one") %>%
            subset(value==TRUE) %>%
            pull(variable)
          sapply(1:length(temp.step2Sects),function(j){
            temp.envLoop <- environment()
            temp.sect <- temp.step2Sects[j]
            temp.rows <- temp.step2Rows[j]
            temp.vars <- colnames(finalC) %>% 
			  str_subset(paste0("t_",temp.table,"_",temp.sect,"_",temp.rows)) %>%
              #28Aug2024: added subset
              subset(. %in% temp.issueVars)
            if (length(temp.vars)>0){#28Aug2024: adding if() just in case temp.vars now empty
              #06Jun2025: create a dataset with limited # of variables
              finalC2 <- data.frame(finalC) %>%
                select(ORI,county,sourceInd,matches(str_c("^t_",temp.table,"_\\d+_",temp.step1RowsRegEx,"_\\d+$")),all_of(temp.vars))
              sapply(temp.vars,function(temp.var){
                temp.col <- temp.var %>%
                  str_extract("(?<=_)\\d+$") %>%
                  as.numeric()
                temp.step1Var <- colnames(finalC2) %>% str_subset(paste0("t_",temp.table,"_\\d+_",temp.step1RowsRegEx,"_",temp.col))
                if(any(finalC2 %>% select(all_of(temp.var)) %>% is.na())){
                  log_debug(paste0("Fixing ",temp.var," for finalC column set ",temp.colnum))
                  if(nrow(finalC2 %>% subset(sourceInd=="NIBRS" & eval(as.symbol(temp.step1Var))>0))>0){
                    temp.constVal <- finalC2 %>% 
                      subset(sourceInd=="NIBRS" & eval(as.symbol(temp.step1Var))>0) %>% 
                      getElement(temp.var) %>%
                      mean()
                  } else {
                    temp.constVal <- 0
                  }
                  finalC2 <- finalC2 %>%
                    mutate(!!temp.var := ifelse(sourceInd=="SRS" & eval(as.symbol(temp.step1Var))>0,
                                                min(temp.constVal,eval(as.symbol(temp.step1Var))),
                                                eval(as.symbol(temp.var)))) %>%
                    mutate(!!temp.var := ifelse(sourceInd=="SRS" & eval(as.symbol(temp.step1Var))==0,
                                                0,
                                                eval(as.symbol(temp.var))))
                  list2env(list("finalC2"=finalC2),envir=temp.envLoop)
                }
                return(NULL)
              })
              #06Jun2025: now, merge & add on the fixed columns
              finalC2 <- finalC2 %>%
                select(ORI,county,all_of(temp.vars))
              finalC <- finalC %>%
                select(-all_of(temp.vars)) %>%
                full_join(finalC2,by=c("ORI","county"))
            }
            list2env(list("finalC"=finalC),envir=tempEnvB)
            return(NULL)
          })
          if ("p" %in% colnames(finalC)){
            finalC <- finalC %>%
              mutate(p=as.numeric(p))
          }
          if ("den" %in% colnames(finalC)){
            finalC <- finalC %>%
              mutate(den=as.numeric(den))
          }
        } else {
          finalC <- data.frame()
        }
      } else {
        finalC <- data.frame()
      }
      #Note (21APR2022): Only proceed after stacking if nrow(final)>0
      print("Stack individual files")
      temp.final <- rbindlist(list(finalA,finalB,finalC),
                              use.names=TRUE,fill=TRUE) %>%
        data.frame() %>%
        select(-matches("^(p|den)$")) #p and den changes for each column set -> drop
      #Note (JDB 04MAY2022): Inner join with existing dataset if not empty
      #Note (JDB 06JUN2025): Only do a merge if there are multiple column sets;
      #                        otherwise, just stack them
      if (nrow(temp.final)>0 & nrow(final)>0){
        final <- data.table(final)
        temp.final <- data.table(temp.final)
        if (length(temp.colsets)>1){
          temp.byVars <- intersect(colnames(final),colnames(temp.final))
          final <- merge.data.table(final,temp.final,by=temp.byVars,all=TRUE)
        } else {
          final <- rbindlist(list(final,temp.final),
                             use.names=TRUE,fill=TRUE)
        }
        final <- data.frame(final)
      } else if (nrow(temp.final)>0){
        final <- temp.final
      }
      list2env(list("final"=final),envir=tempEnv)
      return(NULL)
    })
    return(NULL)
  })
  return(NULL)
},simplify=FALSE)
final <- data.frame(final)
nSRS <- final %>% subset(sourceInd=="SRS") %>% nrow()
if (nSRS>0 & nrow(temp.tier4Type96Specs)>0){
  nstacks <- 10
  temp.special <- temp.tier4Type96Specs$special
  temp.type96Sect <- temp.tier4Type96Specs$section
  temp.type96Rows <- temp.tier4Type96Specs$rows
  #Get 1 column per column group
  temp.type96Vars <-  colnames(final) %>% 
    str_subset(paste0("t_",temp.table,"_",temp.type96Sect,"_",temp.type96Rows,"_\\d+$"))
  temp.step1Specs <- temp.rowSpecs %>%
    subset(tier==0)
  temp.step1Sect <- 2#temp.step1Specs$section
  temp.step1Rows <- temp.step1Specs$ttlRow
  temp.step1Vars <- colnames(final) %>% 
    str_subset(paste0("t_",temp.table,"_",temp.step1Sect,"_",temp.step1Rows,"_(1|7|13|19|25|31|37|43|49)$"))
  if (temp.special=="X"){
    final <- sapply(subsets,function(temp.subset){
      
      if (temp.subset=="popResidAgcyCounty_cbi>0 & nDemoMissing==0"){
        temp.popVar <- "popResidAgcyCounty_cbi"
        temp.demoVars <- c("ageLT5"
                           ,"age5to14"
                           ,"age15"
                           ,"age16"
                           ,"age17"
                           ,"age18to24"
                           ,"age25to34"
                           #,age35to64
                           ,"ageGTE65"
                           #,sexMale
                           ,"sexFemale"
                           #,raceWhite
                           ,"raceBlack"
                           ,"raceAIAN"
                           ,"raceAsian"
                           ,"raceNHPI")
        temp.subsetSuffix <- "Nonzero_Pop" #Used for file name at end
        #Note (JDB 12MAY2023): Adding support for other ACS vars
        temp.othACSVars <- c("incomeRatioLT1",
                             #"incomeRatio1to2",
                             "incomeRatioGTE2")
        
      } else if (temp.subset=="popResidAgcyCounty_cbi>0 & nDemoMissing>0"){
        temp.popVar <- "popResidAgcyCounty_cbi"
        temp.demoVars <- NULL
        temp.subsetSuffix <- "Missing_Demo" #Used for file name at end
        #Note (JDB 12MAY2023): Adding support for other ACS vars
        temp.othACSVars <- NULL
        
      } else if (temp.subset=="popResidAgcyCounty_cbi==0"){
        temp.popVar <- "TOT_OFFICER_COUNT_COUNTY"
        temp.demoVars <- NULL
        temp.subsetSuffix <- "Zero_Pop" #Used for file name at end
        #Note (JDB 12MAY2023): Adding support for other ACS vars
        temp.othACSVars <- NULL
        
      }
      tempEnv2 <- environment()
      temp.final <- final %>%
        filter(eval(parse(text=temp.subset))) %>%
        mutate(den=ifelse(sourceInd=="NIBRS",
                          dplyr::select(.,temp.step1Vars) %>% 
                            rowSums(),
                          NA_real_)) %>%
        mutate(p=if_else(den==0,0,eval(as.symbol(temp.type96Vars[1]))/den))
      #table(temp.final$p,useNA="ifany") %>% print()
      #table(temp.final$den,useNA="ifany") %>% print()
      #table(temp.final[,temp.step1Vars[1]],useNA="ifany") %>% print()
      temp.nSRS <- temp.final %>% subset(sourceInd=="SRS") %>% nrow()
      if (temp.nSRS>0){
        statusStep4 <- getStep1Imp(temp.final,
                                   table=temp.table,
                                   popVar=temp.popVar,
                                   demoVars=temp.demoVars,
                                   othACSVars=temp.othACSVars,#JDB 12MAY2023: Added support today
                                   lhsTOCs=NULL,
                                   impVars=c("p"),
                                   stacks=nstacks,
                                   outEnv=tempEnv2) %>%
          mutate(row=temp.step1Rows,
                 permutation=temp.perm,
                 collapseInd=FALSE)
        temp.final <- temp.final %>%
          mutate(across(.cols=matches(temp.type96Vars),
                        .fns=function(x){
                          ifelse(sourceInd=="SRS",
                                 p*rowSums(dplyr::select(.,all_of(temp.step1Vars)),
                                           na.rm=TRUE),
                                 x)
                        }))
      }
      return(temp.final)
      
    },simplify=FALSE) %>% 
      rbindlist(use.names=TRUE,fill=TRUE) %>%
      data.frame()
  }
}
if (nSRS>0){
  final <- final %>%
    mutate(POP_TOTAL_WEIGHTED=temp.ttlPop)
  #Create the tier 3 variables for SRS-only LEAs
  columns <- colnames(final) %>%
    str_subset(paste0("t_",temp.table,"_1_1_\\d+")) %>%
    str_extract("(?<=_)\\d+$") %>%
    as.numeric()
  nCol <- columns %>% length()
  sapply(columns,function(i){#Loop over columns
    if (is.na(temp.special)){
      ttlVar <- final %>% colnames() %>% subset(.==paste0("t_",temp.table,"_1_1_",i))
    } else {
      temp.step1Sect <- temp.step1Specs$section
      temp.step1Rows <- temp.step1Specs$rows
      temp.step1Vars <- colnames(final) %>% 
        str_subset(paste0("t_",temp.table,"_",temp.step1Sect,"_",temp.step1Rows,"_\\d+$"))
      ttlVar <- temp.step1Vars %>% str_subset(paste0("(?<=_)",i,"$"))
      #print(ttlVar)
    }
    if (nrow(temp.tier3Type97Specs)>0){
      #log_debug("temp.tier3Type97Specs")
      #print(temp.tier3Type97Specs)
      #log_debug("temp.tier3Type97Rows")
      #print(temp.tier3Type97Rows)
      #log_debug("temp.tier3Type97Maps")
      #print(temp.tier3Type97Maps)
      #log_debug("temp.tier3Type97Vars")
      temp.tier3Type97RegEx <- paste0("^t_",temp.table,"_(",
                                      str_flatten(paste0(temp.tier3Type97Sects,"_",temp.tier3Type97Rows),col="|"),
                                      ")_",i,"$")
      temp.tier3Type97Vars <- colnames(final) %>% str_subset(temp.tier3Type97RegEx)
      #print(temp.tier3Type97Vars)
      #log_debug("temp.tier3Type97MapVars")
      temp.tier3Type97MapRegEx <- paste0("^t_",temp.table,"_(",
                                         str_flatten(paste0(temp.tier3Type97Sects,"_",temp.tier3Type97Maps),col="|"),
                                         ")_",i,"$")
      temp.tier3Type97MapVars <- colnames(final) %>% str_subset(temp.tier3Type97MapRegEx)
      #print(temp.tier3Type97MapVars)
      #print(typeof(temp.tier3Type97Vars))
      for (j in 1:length(temp.tier3Type97Vars)){
        #print(paste0("j: ",j))
        #print(temp.tier3Type97Vars[j])
        final <- final %>%
          mutate(!!temp.tier3Type97Vars[j] := eval(as.symbol(temp.tier3Type97MapVars[j])))
      }
    }
    log_debug("Population group variables")
    if (nrow(temp.tier3Type98Specs)>0){
      names(temp.popGpList) <- paste0(temp.popGpPrefix,"_",temp.popGpRows,"_",i)
      #print(sPopList)
      #print(sAgcyIndList)
      if (names(temp.popGpList)[1] %in% colnames(final)){
        final <- final %>%
          mutate(!!names(temp.popGpList)[1] := ifelse(sourceInd=="SRS",
                                                      ifelse(POPULATION_GROUP_DESC %in% temp.popGpList[[1]],
                                                             eval(as.symbol(ttlVar)),
                                                             0),
                                                      eval(as.symbol(names(temp.popGpList)[1])))
          )
      }
      if (names(temp.popGpList)[2] %in% colnames(final)){
        final <- final %>%
          mutate(!!names(temp.popGpList)[2] := ifelse(sourceInd=="SRS",
                                                      ifelse(POPULATION_GROUP_DESC %in% temp.popGpList[[2]],
                                                             eval(as.symbol(ttlVar)),
                                                             0),
                                                      eval(as.symbol(names(temp.popGpList)[2])))
          )
      }
      if (names(temp.popGpList)[3] %in% colnames(final)){
        final <- final %>%
          mutate(!!names(temp.popGpList)[3] := ifelse(sourceInd=="SRS",
                                                      ifelse(POPULATION_GROUP_DESC %in% temp.popGpList[[3]],
                                                             eval(as.symbol(ttlVar)),
                                                             0),
                                                      eval(as.symbol(names(temp.popGpList)[3])))
          )
      }
      if (names(temp.popGpList)[4] %in% colnames(final)){
        final <- final %>%
          mutate(!!names(temp.popGpList)[4] := ifelse(sourceInd=="SRS",
                                                      ifelse(POPULATION_GROUP_DESC %in% temp.popGpList[[4]],
                                                             eval(as.symbol(ttlVar)),
                                                             0),
                                                      eval(as.symbol(names(temp.popGpList)[4])))
          )
      }
      if (names(temp.popGpList)[5] %in% colnames(final)){
        final <- final %>%
          mutate(!!names(temp.popGpList)[5] := ifelse(sourceInd=="SRS",
                                                      ifelse(POPULATION_GROUP_DESC %in% temp.popGpList[[5]],
                                                             eval(as.symbol(ttlVar)),
                                                             0),
                                                      eval(as.symbol(names(temp.popGpList)[5])))
          )
      }
      # !!names(temp.popGpList)[6] := ifelse(sourceInd=="SRS",
      #                                        ifelse(POPULATION_GROUP_DESC==sPopList[[6]],
      #                                               eval(as.symbol(ttlVar)),
      #                                               0),
      #                                        eval(as.symbol(names(temp.popGpList)[6]))),
    }
    log_debug("Agency indicator variables")
    if (nrow(temp.tier3Type99Specs)>0){
      names(temp.agcyIndList) <- paste0(temp.agcyIndPrefix,"_",temp.agcyIndRows,"_",i)
      if (!!names(temp.agcyIndList)[1] %in% colnames(final)){
        final <- final %>%
          mutate(!!names(temp.agcyIndList)[1] := ifelse(sourceInd=="SRS",
                                                        ifelse(AGENCY_TYPE_NAME==temp.agcyIndList[[1]],
                                                               eval(as.symbol(ttlVar)),
                                                               0),
                                                        eval(as.symbol(names(temp.agcyIndList)[1])))
          )
      }
      if (!!names(temp.agcyIndList)[2] %in% colnames(final)){
        final <- final %>%
          mutate(!!names(temp.agcyIndList)[2] := ifelse(sourceInd=="SRS",
                                                        ifelse(AGENCY_TYPE_NAME==temp.agcyIndList[[2]],
                                                               eval(as.symbol(ttlVar)),
                                                               0),
                                                        eval(as.symbol(names(temp.agcyIndList)[2])))
          )
      }
      if (!!names(temp.agcyIndList)[3] %in% colnames(final)){
        final <- final %>%
          mutate(!!names(temp.agcyIndList)[3] := ifelse(sourceInd=="SRS",
                                                        ifelse(AGENCY_TYPE_NAME==temp.agcyIndList[[3]],
                                                               eval(as.symbol(ttlVar)),
                                                               0),
                                                        eval(as.symbol(names(temp.agcyIndList)[3])))
          )
      }
      if (!!names(temp.agcyIndList)[4] %in% colnames(final)){
        final <- final %>%
          mutate(!!names(temp.agcyIndList)[4] := ifelse(sourceInd=="SRS",
                                                        ifelse(AGENCY_TYPE_NAME==temp.agcyIndList[[4]],
                                                               eval(as.symbol(ttlVar)),
                                                               0),
                                                        eval(as.symbol(names(temp.agcyIndList)[4])))
          )
      }
      if (names(temp.agcyIndList)[5] %in% colnames(final)){
        final <- final %>%
          mutate(!!names(temp.agcyIndList)[5] := ifelse(sourceInd=="SRS",
                                                        ifelse(AGENCY_TYPE_NAME==temp.agcyIndList[[5]],
                                                               eval(as.symbol(ttlVar)),
                                                               0),
                                                        eval(as.symbol(names(temp.agcyIndList)[5])))
          )
      }
      if (names(temp.agcyIndList)[6] %in% colnames(final)){
        final <- final %>%
          mutate(!!names(temp.agcyIndList)[6] := ifelse(sourceInd=="SRS",
                                                        ifelse(AGENCY_TYPE_NAME==temp.agcyIndList[[6]],
                                                               eval(as.symbol(ttlVar)),
                                                               0),
                                                        eval(as.symbol(names(temp.agcyIndList)[6])))#,
          )
      }
    }
    list2env(list("final"=final),tempEnv)
    return(NULL)
  },simplify=FALSE)
}
#28Aug2022: Temp fix part 2 (may not even be necessary at time)...
temp.tocVars <- colnames(final) %>% str_subset("^t_")
final <- final %>%
  mutate(across(temp.tocVars,
                ~ifelse(is.na(.),0,.)))


outName <- paste0("Table_",temp.table,"_Final_Agency_File_Perm_",temp.perm,"_Rates_",temp.stratVar)
#Update (03Mar2022): If file already exists - move that version to boneyard before writing new version
#if (file.exists(file.path(output_copula_data_folder,
#				paste0(outName,".csv")))){
#  fDate <- file.info(file.path(output_copula_data_folder,
#				paste0(outName,".csv"))) %>%
#    .$mtime %>%
#    format("%d%b%y")
#  file.copy(from=file.path(output_copula_data_folder,
#				paste0(outName,".csv")),
#            to=file.path(output_copula_data_folder,
#				"boneyard",
#				paste0(outName,".csv")),
#            copy.date=TRUE)
#}
fwrite_wrapper(final,
               file.path(output_copula_data_folder,
                         paste0(outName,".csv")))
