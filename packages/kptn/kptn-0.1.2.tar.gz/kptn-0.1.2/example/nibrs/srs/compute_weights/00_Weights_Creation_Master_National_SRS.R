set.seed(1)

source("01_Create_Clean_Frame_SRS.R")

source("02_Weights_Data_Setup_National_SRS.R")

source("02b_Geography_Crossings_National_SRS.R")

system.time(source("03_Weights_Calibration_National_SRS.R"))

source("04_TableShell_Groupings_National_SRS.R")

source("05_Populate_TableA_Groupings_National_SRS.R")

rmarkdown::render(input="06_Weight_Checks_National_SRS.Rmd",
                  output_format="html_document",
                  output_file="weights_checks_srs",
                  output_dir=output_weighting_data_folder) # < 10 seconds

source("08_Create_Agency_Level_Calibration_Variable_File_SRS.R")