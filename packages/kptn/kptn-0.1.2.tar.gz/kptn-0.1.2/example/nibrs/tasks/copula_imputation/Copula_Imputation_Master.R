library(reshape2)
library(tidyverse)
library(openxlsx)
library(copula)
library(rjson)

outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")

output_folder <- sprintf("%s", outputPipelineDir)
input_folder <- sprintf("%s", inputPipelineDir)

input_estimate_folder <- paste0(inputPipelineDir, "/indicator_table_estimates/")
input_extract_folder <- paste0(inputPipelineDir, "/indicator_table_extracts/")

output_copula_folder <- file.path(outputPipelineDir, "copula_imputation")
output_copula_data_folder <- file.path(output_copula_folder, "Data")
filepathin_initial = paste0(inputPipelineDir, "/initial_tasks_output/")


directories <- c(input_estimate_folder, input_extract_folder, output_copula_folder, output_copula_data_folder)

for (d in directories) {
  if (! dir.exists(d)) {
    dir.create(d, recursive = TRUE)
  }
}

file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", input_folder))

year <- Sys.getenv("DATA_YEAR")


rowSpecs <- read_csv("./data/Indicator_Table_Row_Specs.csv")
permutations <- paste0(filepathin_initial, "POP_TOTALS_PERM_", year, ".csv") %>%
  read_csv()


tables <- rowSpecs$table %>% unique()
#Subsets of data 
subsets <- c("popResidAgcy_cbi>0 & nDemoMissing==0",
             "popResidAgcy_cbi>0 & nDemoMissing>0",
             "popResidAgcy_cbi==0")
library(parallel)
library(furrr)
#plan(multisession,workers=detectCores()/2)
#future_map(tables,function(temp.table){
sapply(tables,function(temp.table){
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
  source("table_ori_all.R",local=TRUE)
  
  temp.colsets <- rowSpecs %>% 
    subset(table==temp.table) %>% 
    .$columns %>% 
    unique() %>%
    str_split(pattern=",") %>%
    unlist()
  
  #future_map(1:nrow(permutations),function(temp.perm){#c(12,13,56,1001,1012,1056,10001,10012,10056,12001,12012,12056)
  sapply(permutations$PERMUTATION_NUMBER[2],function(temp.perm){#c(12,13,56,1001,1012,1056,10001,10012,10056,12001,12012,12056)
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
      #plan(multisession,workers=detectCores()/2)
      print(paste0("Current column set: ",temp.colnum))
      #plan(multisession,workers=detectCores()/2)
      #future_map(subsets,function(temp.subset){
      sapply(subsets,function(temp.subset){
        #library(tidyverse)
        #library(openxlsx)
        #library(copula)
        #library(rjson)
        paste0("Current subset: ",temp.subset) %>%
          print()
        
        Sys.setenv(table=temp.table)
        Sys.setenv(permutation=temp.perm)
        Sys.setenv(colnum=temp.colnum)
        Sys.setenv(subset=temp.subset)
        source("Copula_Imputation_Instance.R",local=TRUE)
        return(NULL)
      })
      
      #},.options=furrr_options(globals=c("input_estimate_folder","input_extract_folder","external_path","file_locs","output_copula_data_folder","permutations","subsets","temp.table","temp.permutation")))
      
      return(NULL)
      
    })
    
    #Stack a table X permutation after all column sets and subsets
    source("Stack_Copula_Imputation_Subsets.R",local=TRUE)
    
    #},.options=furrr_options(globals=c("input_estimate_folder","input_extract_folder","external_path","file_locs","output_copula_data_folder","permutations","subsets","temp.table","rowSpecs")))
    return(NULL)
  })
  
  
  return(NULL)
})
#},.options=furrr_options(globals=c("input_estimate_folder","input_extract_folder","external_path","file_locs","output_copula_data_folder","permutations","subsets")))
