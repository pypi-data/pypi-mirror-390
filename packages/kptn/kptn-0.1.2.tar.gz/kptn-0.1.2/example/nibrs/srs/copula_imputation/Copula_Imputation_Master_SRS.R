#This program is intended to serve as the master program for SRS copula
#As of 08Jun2023, we will be using gun violence data since SRS copula inputs aren't available yet

# Set working directory
setwd("C:/Users/jbunker/Documents/GitHub/nibrs-estimation-pipeline/srs/copula_imputation")
library(reshape2)
library(tidyverse)
library(openxlsx)
library(copula)
library(rjson)
library(logger)
library(data.table)

outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")

output_folder <- sprintf("%s", outputPipelineDir)
input_folder <- sprintf("%s", inputPipelineDir)

input_estimate_folder <- paste0(inputPipelineDir, "/srs/indicator_table_estimates/")
input_extract_folder <- paste0(inputPipelineDir, "/srs/indicator_table_extracts/")

output_copula_folder <- file.path(outputPipelineDir, "srs","copula_imputation")
output_copula_data_folder <- file.path(output_copula_folder, "Data")
output_copula_temp_folder <- file.path(output_copula_folder, "Temp")
filepathin_initial = paste0(inputPipelineDir, "/initial_tasks_output/")


directories <- c(input_estimate_folder, input_extract_folder, output_copula_folder, output_copula_data_folder)

for (d in directories) {
  if (! dir.exists(d)) {
    dir.create(d, recursive = TRUE)
  }
}

file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", input_folder))

year <- Sys.getenv("DATA_YEAR")


if (str_detect(getwd(),"part(1|2)")){
  setwd("..")
}
rowSpecs <- fread("./data/Indicator_Table_Row_Specs_SRS.csv")
permutations <- paste0(filepathin_initial, "POP_TOTALS_PERM_", year, "_SRS.csv") %>%
  read_csv()


tables <- rowSpecs$table %>% unique()
#Subsets of data 
subsets <- c("popResidAgcyCounty_cbi>0 & nDemoMissing==0",
             "popResidAgcyCounty_cbi>0 & nDemoMissing>0",
             "popResidAgcyCounty_cbi==0")
library(parallel)
library(furrr)

rm(list=ls() %>% 
     str_subset("^(external_path|file_locs|output_copula_folder|output_copula_data_folder|output_copula_temp_folder|input_estimate_folder|input_extract_folder)$",#Non-instance-specific path objects
                negate=TRUE) %>%
     str_subset("^(tables|rowSpecs|permutations|subsets|year|tableSample)$",#Non-instance-specific misc objects
                negate=TRUE)
)
tablesRun <- c("SRS1a")#c("GV1a")#c("1a")
permsRun <- permutations %>% pull(PERMUTATION_NUMBER) %>% subset(. %% 1000==1)
stratVarsRun <- list("PARENT_POP_GROUP_CODE2")#"PARENT_POP_GROUP_CODE")
stratLvlsRun <- list(1:8)#9)

temp.stratVars <- stratVarsRun
temp.stratLvls <- stratLvlsRun
sapply(tablesRun,function(temp.table){#tables
  
  rm(list=ls() %>% 
       str_subset("^(external_path|file_locs|output_copula_folder|output_copula_data_folder|output_copula_temp_folder|input_estimate_folder|input_extract_folder)$",#Non-instance-specific path objects
                  negate=TRUE) %>%
       str_subset("^(tables|rowSpecs|permutations|subsets|year|tableSample)$",#Non-instance-specific misc objects
                  negate=TRUE) %>%
       str_subset("^(temp.table)$",#Instance-specific objects
                  negate=TRUE)
  )
  library(tidyverse)
  library(openxlsx)
  library(copula)
  library(rjson)
  library(parallel)
  library(furrr)
  
  paste0("Current table: ",temp.table) %>%
    print()
  Sys.setenv(table=temp.table)
  
  if (str_detect(getwd(),"part(1|2)",negate=TRUE)){
    setwd('./part1_prep_data')
  } else if (str_detect(getwd(),"part2_impute")){
    setwd("../part1_prep_data")
  }
  #if (!file.exists(file.path(output_copula_data_folder,paste0("Table_",temp.table,"_ORI_all.csv")))){
    timeORI <- system.time(source("table_ori_all_SRS.R",local=TRUE,echo=TRUE))
    timeORI <- data.frame(user.self=timeORI[1] %>% as.numeric(),
                          sys.self=timeORI[2] %>% as.numeric(),
                          elapsed=timeORI[3] %>% as.numeric())
    write_csv(timeORI,
              paste0(output_copula_folder,"/Time_to_Run_ORI_",temp.table,".csv"))
    
  #}
  
  temp.colsets <- rowSpecs %>% 
    subset(table==temp.table) %>% 
    .$columns %>% 
    unique() %>%
    str_split(pattern=",") %>%
    unlist()
  temp.rowSpecs <- fread("../data/Indicator_Table_Row_Specs_SRS.csv") %>%
    filter(table==temp.table)
  
  temp.demographics <- temp.rowSpecs %>%
    .$demographics %>%
    unique()
  
  temp.stratVar <- stratVarsRun[[1]]
  temp.stratLvls <- stratLvlsRun[[1]]
  
  permSample <- 1#c(89)#9#1054#1064#1001#1068
  
  #permSample <- "14061"
  #future_map(1:nrow(permutations),function(temp.perm){#c(12,13,56,1001,1012,1056,10001,10012,10056,12001,12012,12056)
  sapply(permsRun,function(temp.perm){#c(12,13,56,1001,1012,1056,10001,10012,10056,12001,12012,12056)#permutations$PERMUTATION_NUMBER[c(1,50,100,1002,1025,1075)]
    
    rm(list=ls() %>% 
         str_subset("^(external_path|file_locs|output_copula_folder|output_copula_data_folder|output_copula_temp_folder|input_estimate_folder|input_extract_folder)$",#Non-instance-specific path objects
                    negate=TRUE) %>%
         str_subset("^(tables|rowSpecs|permutations|subsets|year|tableSample|temp.colsets|temp.stratLvls)$",#Non-instance-specific misc objects
                    negate=TRUE) %>%
         str_subset("^(temp.table|temp.perm|temp.stratVar)$",#Instance-specific objects
                    negate=TRUE)
    )
    
    #library(tidyverse)
    #library(openxlsx)
    #library(copula)
    #library(rjson)
    #library(parallel)
    #library(furrr)
    
    paste0("Current permutation: ",temp.perm) %>%
      print()
    Sys.setenv(permutation=temp.perm)
    
    if (str_detect(getwd(),"part1_prep_data")){
      setwd("../part2_impute")
    }
    sapply(1:length(temp.colsets),function(temp.colnum){
      
      rm(list=ls() %>% 
           str_subset("^(external_path|file_locs|output_copula_folder|output_copula_data_folder|output_copula_temp_folder|input_estimate_folder|input_extract_folder)$",#Non-instance-specific path objects
                      negate=TRUE) %>%
           str_subset("^(tables|rowSpecs|permutations|subsets|year|tableSample|temp.colsets|permSample|temp.stratLvls)$",#Non-instance-specific misc objects
                      negate=TRUE) %>%
           str_subset("^(temp.table|temp.perm|temp.colnum|temp.stratVar)$",#Instance-specific objects
                      negate=TRUE)
      )
      #plan(multisession,workers=detectCores()/2)
      print(paste0("Current column set: ",temp.colnum))
      
      
      #plan(multisession,workers=detectCores()/2)
      #future_map(subsets,function(temp.subset){
      #lapply(1:length(stratVarsRun),function(temp.stratVarNum){
      #paste0("Start stratification variable ",temp.stratVar) %>% 
      #  print()
      
      sapply(temp.stratLvls,function(temp.stratLvl){
        
        sapply(subsets,function(temp.subset){
          rm(list=ls() %>% 
               str_subset("^(external_path|file_locs|output_copula_folder|output_copula_data_folder|output_copula_temp_folder|input_estimate_folder|input_extract_folder)$",#Non-instance-specific path objects
                          negate=TRUE) %>%
               str_subset("^(tables|rowSpecs|permutations|subsets|year|tableSample|permSample|temp.stratLvls)$",#Non-instance-specific misc objects
                          negate=TRUE) %>%
               str_subset("^(temp.table|temp.perm|temp.colnum|temp.stratVar|temp.stratLvl|temp.subset)$",#Instance-specific objects
                          negate=TRUE)
          )
          #library(tidyverse)
          #library(openxlsx)
          #library(copula)
          #library(rjson)
          paste0("Current table: ",temp.subset) %>%
            print()
          paste0("Current permutation: ",temp.perm) %>%
            print()
          paste0("Current column set: ",temp.colnum) %>%
            print()
          paste0("Current stratification variable: ",temp.stratVar) %>%
            print()
          paste0("Current stratification level: ",temp.stratLvl) %>%
            print()
          paste0("Current subset: ",temp.subset) %>%
            print()
          
          Sys.setenv(table=temp.table)
          Sys.setenv(permutation=temp.perm)
          Sys.setenv(colnum=temp.colnum)
          
          
          Sys.setenv(subset=temp.subset)
          
          temp.subsetSuffix <- case_when(temp.subset==subsets[1] ~ "Nonzero_Pop",
                                         temp.subset==subsets[2] ~ "Missing_Demo",
                                         temp.subset==subsets[3] ~ "Zero_Pop")
          file.path(output_copula_data_folder,paste0("Table_",temp.table,"_Final_Agency_File_Perm_",temp.perm,"_ColNum_",temp.colnum,"_",temp.subsetSuffix,"_Rates_",temp.stratVar,"_",temp.stratLvl,".csv")) %>%
            print()
          #if (!file.exists(file.path(output_copula_data_folder,paste0("Table_",temp.table,"_Final_Agency_File_Perm_",temp.perm,"_ColNum_",temp.colnum,"_",temp.subsetSuffix,"_Rates_",temp.stratVar,"_",temp.stratLvl,".csv")))){
          
          timeS1 <- system.time(source("Copula_Imputation_Instance_Step1_SRS.R",local=TRUE,echo=TRUE))
          timeS1 <- data.frame(user.self=timeS1[1] %>% as.numeric(),
                               sys.self=timeS1[2] %>% as.numeric(),
                               elapsed=timeS1[3] %>% as.numeric())
          write_csv(timeS1,
                    paste0(output_copula_folder,"/Time_to_Run_S1_",temp.table,"_",temp.table,"_Perm",temp.perm,"_",temp.subsetSuffix,"_",temp.stratVar,"_",temp.stratLvl,"_SRS.csv"))
          
          timeS2 <- system.time(source("Copula_Imputation_Instance_Step2_Alt_SRS.R",local=TRUE,echo=TRUE))
          timeS2 <- data.frame(user.self=timeS2[1] %>% as.numeric(),
                               sys.self=timeS2[2] %>% as.numeric(),
                               elapsed=timeS2[3] %>% as.numeric())
          write_csv(timeS2,
                    paste0(output_copula_folder,"/Time_to_Run_S2_",temp.table,"_",temp.table,"_Perm",temp.perm,"_",temp.subsetSuffix,"_",temp.stratVar,"_",temp.stratLvl,"_SRS.csv"))
          
          timeS3 <- system.time(source("Copula_Imputation_Instance_Step3_Alt_SRS.R",local=TRUE,echo=TRUE))
          timeS3 <- data.frame(user.self=timeS3[1] %>% as.numeric(),
                               sys.self=timeS3[2] %>% as.numeric(),
                               elapsed=timeS3[3] %>% as.numeric())
          write_csv(timeS3,
                    paste0(output_copula_folder,"/Time_to_Run_S3_",temp.table,"_",temp.table,"_Perm",temp.perm,"_",temp.subsetSuffix,"_",temp.stratVar,"_",temp.stratLvl,"_SRS.csv"))
          
          timeS4 <- system.time(source("Copula_Imputation_Instance_Step4_SRS.R",local=TRUE,echo=TRUE))
          timeS4 <- data.frame(user.self=timeS4[1] %>% as.numeric(),
                               sys.self=timeS4[2] %>% as.numeric(),
                               elapsed=timeS4[3] %>% as.numeric())
          write_csv(timeS4,
                    paste0(output_copula_folder,"/Time_to_Run_S4_",temp.table,"_Perm",temp.perm,"_",temp.subsetSuffix,"_",temp.stratVar,"_",temp.stratLvl,"_SRS.csv"))
          # }
          return(NULL)
        })
        return(NULL)
      })
      #},.options=furrr_options(globals=c("input_estimate_folder","input_extract_folder","external_path","file_locs","output_copula_data_folder","permutations","subsets","temp.table","temp.permutation")))
      
      return(NULL)
      
    })
    #Stack a table X permutation after all column sets and subsets
    source("Stack_Copula_Imputation_Subsets_SRS.R",local=TRUE,echo=TRUE)
    
    return(NULL)
    
  })
  
  #},.options=furrr_options(globals=c("input_estimate_folder","input_extract_folder","external_path","file_locs","output_copula_data_folder","permutations","subsets","temp.table","rowSpecs")))
  return(NULL)
})

