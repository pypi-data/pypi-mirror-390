#Step 3: Ratio Adjustment

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
statusStep2 <- file.path(output_copula_data_folder,
                         paste0("Table_",temp.table,"_Imputation_Step2_Summary_Perm_",temp.perm,"_ColNum_",temp.colnum,"_",temp.subsetSuffix,"_Rates_",temp.stratVar,"_",temp.stratLvl,"_SRS.csv")) %>%
  fread()
#Tweaking step 3 routing (e.g., only run step 3 if nrow(statusStep2)>0)
#Note (JDB 10May2022): Create temp3 in event that nrow(statusStep2)==0
if (nrow(statusStep2)>0 & !any(statusStep2$failInd==TRUE)){
  load(file.path(output_copula_temp_folder,paste0("temp2_",temp.uid,".Rdata")))
  load(file.path(output_copula_temp_folder,paste0("columns_",temp.uid,".Rdata")))
  #Update (07Mar2022): Add source indicator (NIBRS/SRS)
  #Note (JDB 09May2022): Comment out sourceInd join
  #inner_join(sourceInd)
  #log_debug("nrow(temp3) [After merging with sourceInd]")
  #log_debug(nrow(temp3))
  #log_debug("nrow(sourceInd)")
  #log_debug(nrow(sourceInd))
  
  temp3 <- temp2 #Initialize step 3 results
  save(temp3,file=file.path(output_copula_temp_folder,
                            paste0("temp3_",temp.uid,".Rdata")))
  log_debug("Step 3: Ratio Adjustment")
  log_debug(system("free -mh", intern = FALSE))
  
  
  source("Copula_Imputation_Functions_SRS.R")
  #load("temp3.Rdata")
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
  
  
  statusStep3 <- sapply(1:length(columns),function(temp.colnum2){#15#14
    log_debug(paste0("Column ",columns[temp.colnum2]))
    temp.statusStep3 <- sapply(1:2,function(temp.tier){#1
      if (temp.tier==1){
        getRatAdj(dat=temp3,
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
        getRatAdj(temp3,
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
  
  #statusStep3 %>%
  #  data.frame() %>%
  #  print()
  #Note (JDB 20APR2022): Only update status table if not empty + reorganize variables
  if (nrow(statusStep3)>0){
    statusStep3 <- statusStep3 %>%
      mutate(permutation=temp.perm) %>%
      dplyr::select(table,permutation,tier,column,section,everything())
    
  }
  
  save(temp3,file=file.path(output_copula_temp_folder,
                            paste0("temp3_",temp.uid,".Rdata")))
  
  #Output Step 3 results
  outName <- paste0("Table_",temp.table,"_Ratio_Adjustment_Summary_Perm_",temp.perm,"_ColNum_",temp.colnum,"_",temp.subsetSuffix,"_Rates_",temp.stratVar,"_",temp.stratLvl,"_SRS")
  
  fwrite_wrapper(statusStep3,
         file.path(output_copula_data_folder,
                        paste0(outName,".csv")))
} else {
  load(file.path(output_copula_temp_folder,paste0("temp2_",temp.uid,".Rdata")))
  
  log_debug("Skip step 3 programs.")
  
  temp3 <- temp2
  save(temp3,file=file.path(output_copula_temp_folder,paste0("temp3_",temp.uid,".Rdata")))
  
}
#list2env(list("temp"=temp,"temp2"=temp2,"temp3"=temp3),.GlobalEnv)


