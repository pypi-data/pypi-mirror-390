#Step 4: Write results
#Note (28Jun2023): Switching from agency-level pop to (agency X county)-level pop
#Instance...
rm(list=ls() %>% 
     subset(!. %in% c("outputPipelineDir","inputPipelineDir","external_path",
                      "output_folder","input_folder","input_estimate_folder",
                      "input_extract_folder","output_copula_folder",
                      "output_copula_data_folder","output_copula_temp_folder","directories",
                      "file_locs","year","temp.table","temp.perm","d","subsets",
                      "temp.colnum","temp.colnum","temp.perm","temp.subset","temp.stratVar","temp.stratLvl")))
if (temp.subset=="popResidAgcyCounty_cbi>0 & nDemoMissing==0"){
  temp.subsetSuffix <- "Nonzero_Pop" #Used for file name at end
  
} else if (temp.subset=="popResidAgcyCounty_cbi>0 & nDemoMissing>0"){
  temp.subsetSuffix <- "Missing_Demo" #Used for file name at end
  
} else if (temp.subset=="popResidAgcyCounty_cbi==0"){
  temp.subsetSuffix <- "Zero_Pop" #Used for file name at end
  
}

temp.uid <- paste0(temp.table,"_",temp.perm,"_",temp.colnum,"_",temp.subsetSuffix,"_Rates_",temp.stratVar,"_",temp.stratLvl) #Unique ID (table X perm X col set # X subset X "Rates" X strat var X strat lvl) for temp files

load(file.path(output_copula_temp_folder,paste0("temp3_",temp.uid,".Rdata")))

# load("temp.step2Tier1Rows.Rdata")
# load("temp.step2Tier2Rows.Rdata")
# load("tempEnv.Rdata")
load(file.path(output_copula_temp_folder,paste0("columns_",temp.uid,".Rdata")))
# load("nCol.Rdata")
# load("nstacks.R")
# load("temp.benchmarks.Rdata")
# load("temp.demoVars.Rdata")
load(file.path(output_copula_temp_folder,paste0("temp.permDesc_",temp.uid,".Rdata")))
# load("temp.popVar.Rdata")
load(file.path(output_copula_temp_folder,paste0("temp.step1RowsRegEx_",temp.uid,".Rdata")))
# load("temp.step2Tier1Sects.Rdata")
# load("temp.step2Tier1Types.Rdata")
# load("temp.step2Tier2Sects.Rdata")
# load("temp.step2Tier2Types.Rdata")
load(file.path(output_copula_temp_folder,paste0("temp.subsetSuffix_",temp.uid,".Rdata")))


if (nrow(temp3)>0){
    #Note (20APR2022): Organizing final dataset columns...
    # 1) Non estimate variables
    # 2) Top row estimate variables
    # 3) Remaining estimate variables
    colsAll <- temp3 %>% colnames()
    cols1 <- colsAll %>% str_subset(paste0("^t_",temp.table),negate=TRUE)
    cols2 <- colsAll %>% str_subset(paste0("^t_",temp.table,"_\\d+_",temp.step1RowsRegEx,"_")) %>% str_sort(numeric=TRUE)
    cols3 <- sapply(columns,function(col){
      colsAll %>%
        str_subset(paste0("^t_",temp.table,"_\\d+_",temp.step1RowsRegEx,"_"),negate=TRUE) %>%
        str_subset(paste0("^t_",temp.table,"_\\d+_\\d+_",col,"$")) %>%
        str_sort(numeric=TRUE)
    },simplify=FALSE) %>%
      unlist()
    temp4 <- temp3 %>%
      subset(eval(temp.permDesc)) %>%
      dplyr::select(all_of(cols1),all_of(cols2),all_of(cols3))
} else {
  temp4 <- data.frame()
}
  
log_debug(system("free -mh", intern = FALSE))

outName <- paste0("Table_",temp.table,"_Final_Agency_File_Perm_",temp.perm,"_ColNum_",temp.colnum,"_",temp.subsetSuffix,"_Rates_",temp.stratVar,"_",temp.stratLvl)
#Update (03Mar2022): If file already exists - move that version to boneyard before writing new version

# file.remove(file=file.path(output_copula_data_folder,
#                            paste0(outName,".csv")))

if (nrow(temp4) > 0) {
  fwrite(temp4,
       file=file.path(output_copula_data_folder,
                         paste0(outName,".csv")))
} else {
  write_csv(temp4,
       file.path(output_copula_data_folder,
                         paste0(outName,".csv")))
}

