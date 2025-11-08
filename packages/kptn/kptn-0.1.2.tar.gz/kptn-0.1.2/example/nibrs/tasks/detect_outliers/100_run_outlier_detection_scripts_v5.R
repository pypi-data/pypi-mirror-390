#This will run V5 (addition of color coding)

library("rmarkdown")
library("tidyverse")
library(DT)

#Read in the common functions to be used in R
source(here::here("tasks/logging.R"))

#SET UP ALL THE NECESSARY INPUT/OUTPUT PATHS
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
filepathout = paste0(outputPipelineDir, "/markdown/") #output path for markdown files

if (! dir.exists(filepathout)) {
  dir.create(filepathout, recursive = TRUE)
}

mainpath = paste0(outputPipelineDir, "/outlier_data/") #output path for data

if (! dir.exists(mainpath)) {
  dir.create(mainpath, recursive = TRUE)
}

#output location of create_NIBRS_extracts
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
mainpathdata = paste0(inputPipelineDir, "/artifacts/") #input path

if (as.numeric(Sys.getenv("DATA_YEAR")) < 1995) {
  log_info("Data year is less than 1995. Make a dummy file.")
  test <- data.frame(matrix(nrow=1,ncol=13))
  colnames(test) <- c("ori", str_c(month.abb,"-",as.numeric(Sys.getenv("DATA_YEAR"))-floor(as.numeric(Sys.getenv("DATA_YEAR"))/100)*100))
  test <- test %>%
          mutate(ori = "AK0000000",
          across(matches("\\w{3}-\\d{2}"), ~"green"))

  write_csv(test, paste0(mainpath, "outlier_data_file.csv"))
} else {
  #Read in the common functions to be used in R
  log_info("Starting 00_Load_Data_Pipeline_v2.R....")
  source("00_Load_Data_Pipeline_v2.R")

  log_info("Starting runNovelMethod_v5.R....")
  source("runNovelMethod_v5.R")

  log_info("Starting getPlot_v5.R....")
  source("getPlot_v5.R")

  log_info("Starting Novel_Method-Mean_Crime_Count_GTE_50_LEAs-v5.Rmd....")
  rmarkdown::render("Novel_Method-Mean_Crime_Count_GTE_50_LEAs-v5.Rmd", output_format = html_document(),
                    output_file = paste0(filepathout, "Novel_Method-Mean_Crime_Count_GTE_50_LEAs-v5.html"),
                    envir = new.env(), quiet = TRUE)
  invisible(gc())
  knitr::knit_meta(clean = TRUE)

  log_info("Starting outlier_data_file_pipeline_v5.R....")
  source("outlier_data_file_pipeline_v5.R")

  log_info("Starting Outlier_Detection_Longitudinal_Analysis_Summary_Tables_Pipeline_v5.R....")
  source("Outlier_Detection_Longitudinal_Analysis_Summary_Tables_Pipeline_v5.R")
  #source("Outlier_Detection_Single_Year_Analysis_Summary_Tables_Pipeline_v2.R")
}