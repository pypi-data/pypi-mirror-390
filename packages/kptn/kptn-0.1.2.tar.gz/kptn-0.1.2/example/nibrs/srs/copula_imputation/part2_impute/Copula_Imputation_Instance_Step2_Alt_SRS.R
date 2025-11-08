#Step 2

#Note (26May2023): Creating SRS pipeline version. Heavily basing off equivalent NIBRS pipeline program. Any dates referred to prior to today are a result of copy-pasting. Tweaks include adding "_SRS" to all output and changing NIBRS/SRS split for sourceInd to "SRS Reporter"/"SRS Non-reporter".
#Instance...
rm(list=ls() %>% 
     subset(!. %in% c("outputPipelineDir","inputPipelineDir","external_path",
                      "output_folder","input_folder","input_estimate_folder",
                      "input_extract_folder","output_copula_folder",
                      "output_copula_data_folder","output_copula_temp_folder","directories",
                      "file_locs","year","temp.table","temp.perm","d","subsets",
                      "temp.colnum","temp.colnum","temp.perm","temp.subset","temp.stratVar","temp.stratLvl")))

source(here::here("tasks/logging.R"))
if (temp.subset=="popResidAgcyCounty_cbi>0 & nDemoMissing==0"){
  temp.subsetSuffix <- "Nonzero_Pop" #Used for file name at end
  
} else if (temp.subset=="popResidAgcyCounty_cbi>0 & nDemoMissing>0"){
  temp.subsetSuffix <- "Missing_Demo" #Used for file name at end
  
} else if (temp.subset=="popResidAgcyCounty_cbi==0"){
  temp.subsetSuffix <- "Zero_Pop" #Used for file name at end
  
}

temp.uid <- paste0(temp.table,"_",temp.perm,"_",temp.colnum,"_",temp.subsetSuffix,"_Rates_",temp.stratVar,"_",temp.stratLvl,"_SRS") #Unique ID (table X perm X col set # X subset X "Rates" X strat var X strat lvl) for temp files
statusStep1 <- file.path(output_copula_data_folder,
                         paste0("Table_",temp.table,"_Imputation_Step1_Summary_Perm_",temp.perm,"_ColNum_",temp.colnum,"_",temp.subsetSuffix,"_Rates_",temp.stratVar,"_",temp.stratLvl,"_SRS.csv")) %>%
  fread()
#statusStep2 <- file.path(output_copula_data_folder,
#                         paste0("Table_",temp.table,"_Imputation_Step2_Summary_Perm_",temp.perm,"_ColNum_",temp.colnum,"_",temp.subsetSuffix,".csv")) %>%
#  fread()

#Note (JDB 02May2022): Tweaking routing (e.g., only go to step 2 if nrow(statusStep1)>0)
if (nrow(statusStep1)>0 & statusStep1 %>% subset(failInd==TRUE) %>% nrow() == 0){
  load(file.path(output_copula_temp_folder,paste0("temp_",temp.uid,".Rdata")))
  load(file.path(output_copula_temp_folder,paste0("columns_",temp.uid,".Rdata")))
  
  temp2 <- temp #Initialize step 2 results
  log_debug("Step 2")
  log_debug(system("free -mh", intern = FALSE))
  
  source("Copula_Imputation_Functions_SRS.R")
  #load("temp2.Rdata")
  load(file.path(output_copula_temp_folder,paste0("temp.step2Tier1Rows_",temp.uid,".Rdata")))
  load(file.path(output_copula_temp_folder,paste0("temp.step2Tier2Rows_",temp.uid,".Rdata")))
  #load(file.path(output_copula_temp_folder,paste0("tempEnv_",temp.uid,".Rdata")))
  tempEnv <- environment()
  load(file.path(output_copula_temp_folder,paste0("columns_",temp.uid,".Rdata")))
  # load("nCol.Rdata")
  load(file.path(output_copula_temp_folder,paste0("nstacks_",temp.uid,".Rdata")))
  load(file.path(output_copula_temp_folder,paste0("temp.benchmarks_",temp.uid,".Rdata")))
  load(file.path(output_copula_temp_folder,paste0("temp.demoVars_",temp.uid,".Rdata")))
  # load("temp.permDesc.Rdata")
  load(file.path(output_copula_temp_folder,paste0("temp.popVar_",temp.uid,".Rdata")))
  # load("temp.step1RowsRegEx.Rdata")
  load(file.path(output_copula_temp_folder,paste0("temp.step2Tier1Sects_",temp.uid,".Rdata")))
  load(file.path(output_copula_temp_folder,paste0("temp.step2Tier1Types_",temp.uid,".Rdata")))
  load(file.path(output_copula_temp_folder,paste0("temp.step2Tier2Sects_",temp.uid,".Rdata")))
  load(file.path(output_copula_temp_folder,paste0("temp.step2Tier2Types_",temp.uid,".Rdata")))
  #Note (JDB 31Mar2023): Adding support for other ACS vars
  load(file.path(output_copula_temp_folder,paste0("temp.othACSVars_",temp.uid,".Rdata")))
  
  #temp2$t_1c_2_4_1 %>% is.na() %>% table()
  
  
  statusStep2 <- sapply(1:length(columns),function(temp.colnum2){#14
    log_debug(paste0("Column ",columns[temp.colnum2]))
    temp.statusStep2 <- sapply(1:2,function(temp.tier){
      if (temp.tier==1){
        getStep2Imp(dat=temp2,
                    tier=1,
                    types=temp.step2Tier1Types,#3,
                    table=temp.table,
                    sections=temp.step2Tier1Sects,#14,
                    rows=temp.step2Tier1Rows,
                    popVar=temp.popVar,
                    demoVars=temp.demoVars,
					othACSVars=temp.othACSVars,#JDB 31MAR2023: Adding support today
                    benchmark=temp.benchmarks[temp.colnum2],
                    outEnv=tempEnv,
                    stacks=nstacks)
      } else if (temp.tier==2){
        getStep2Imp(temp2,
                    tier=2,
                    types=temp.step2Tier2Types,
                    table=temp.table,
                    sections=temp.step2Tier2Sects,
                    rows=temp.step2Tier2Rows,
                    popVar=temp.popVar,
                    demoVars=temp.demoVars,
					othACSVars=temp.othACSVars,#JDB 31MAR2023: Adding support today
                    benchmark=temp.benchmarks[temp.colnum2],
                    outEnv=tempEnv,
                    stacks=nstacks)#paste0("t_1c_2_4_",i))#
      }
    },simplify=FALSE) %>% 
      rbindlist(use.names=TRUE,fill=TRUE) %>%
      data.frame()
  },simplify=FALSE) %>% 
    rbindlist(use.names=TRUE,fill=TRUE) %>% 
    data.frame()
  
  #temp2$t_1c_2_4_1 %>% is.na() %>% table() %>% print()
  #temp2$t_1c_2_p_14 %>% is.na() %>% table() %>% print()
  
  #Note (JDB 20APR2022): Only update status table if not empty + reorganize variables
  if (nrow(statusStep2)>0){
    statusStep2 <- statusStep2 %>%
      mutate(permutation=temp.perm)%>%
      dplyr::select(table,permutation,tier,column,section,everything())
  }
  
  #Output Step 2 results
  outName <- paste0("Table_",temp.table,"_Imputation_Step2_Summary_Perm_",temp.perm,"_ColNum_",temp.colnum,"_",temp.subsetSuffix,"_Rates_",temp.stratVar,"_",temp.stratLvl,"_SRS")
  
  fwrite_wrapper(statusStep2,
         file.path(output_copula_data_folder,
                        paste0(outName,".csv")))
  
  save(temp2,file=file.path(output_copula_temp_folder,
                            paste0("temp2_",temp.uid,".Rdata")))
  
} else if (statusStep1 %>%
           select(.,tryFullLHS,tryRedLHS,tryIndTOCa,tryIndTOCb,tryIndTOCc) %>%
           sum() != 0){
  load(file.path(output_copula_temp_folder,
                 paste0("temp_",temp.uid,".Rdata")))
  
  temp2 <- temp
  log_debug("Skip step 2 programs.")
  
  #Note (20APR2022): Tweaking status table for skips
  statusStep2 <- data.frame(table=temp.table,
                            permutation=temp.perm,
                            column=c(rep(columns,each=length(temp.step2Tier1Sects)),
                                     rep(columns,each=length(temp.step2Tier2Sects))) %>%
                              as.character(),
                            tier=c(rep.int(1,nCol*length(temp.step2Tier1Sects)),
                                   rep.int(2,nCol*length(temp.step2Tier2Sects))),
                            section=c(rep(temp.step2Tier1Sects,times=nCol),
                                      rep(temp.step2Tier2Sects,times=nCol)),
                            zeroColInd=FALSE,
                            constRowGpInd=FALSE,
                            tryFullLHS=FALSE,
                            tryRedLHS=FALSE,
                            tryIndRowGp=FALSE,
                            tryIndRowGpa=FALSE,
                            tryIndRowGpb=FALSE,
                            failInd=TRUE)
  
  #Output Step 2 results
  outName <- paste0("Table_",temp.table,"_Imputation_Step2_Summary_Perm_",temp.perm,"_ColNum_",temp.colnum,"_",temp.subsetSuffix,"_Rates_",temp.stratVar,"_",temp.stratLvl,"_SRS")
  
  fwrite_wrapper(statusStep2,
         file.path(output_copula_data_folder,
                        paste0(outName,".csv")))
  save(temp2,file=file.path(output_copula_temp_folder,
                            paste0("temp2_",temp.uid,".Rdata")))
} else if (nrow(statusStep1)==0){
  load(file.path(output_copula_temp_folder,paste0("temp_",temp.uid,".Rdata")))
  temp2 <- temp
  log_debug("Skip step 2 programs.")
  save(temp2,file=file.path(output_copula_temp_folder,
                            paste0("temp2_",temp.uid,".Rdata")))
  
} else {
  load(file.path(output_copula_temp_folder,paste0("temp_",temp.uid,".Rdata")))
  temp2 <- temp
  log_debug("Skip step 2 programs.")
  save(temp2,file=file.path(output_copula_temp_folder,
                            paste0("temp2_",temp.uid,".Rdata")))
}
#statusStep2 <- data.frame()
#log_debug("statusStep2")
#print(statusStep2)

