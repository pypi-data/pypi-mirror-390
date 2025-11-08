set.seed(1)

source("01_Create_Clean_Frame_SRS.R")

source("02_Weights_Data_Setup_SRS.R")

source("02b_Geography_Crossings_SRS.R")

source("03_Weights_Calibration_FO_SRS_AltCombs_Collapsed_SRS.R")

source("03_Weights_Calibration_JD_SRS_AltCombs_Collapsed_SRS.R")

source("03_Weights_Calibration_MSA_SRS_AltCombs_Collapsed_SRS.R")

source("04_TableShell_FO_SRS.R")

source("04_TableShell_JD_SRS.R")

source("04_TableShell_MSA_SRS.R")

source("05_Populate_TableA_FO_SRS_AltCombs_Collapsed_SRS.R")

source("05_Populate_TableA_JD_SRS_AltCombs_Collapsed_SRS.R")

source("05_Populate_TableA_MSA_SRS_AltCombs_Collapsed_SRS.R")

rmarkdown::render(input="06_Weight_Checks_SRS.Rmd",
                  output_format="html_document",
                  output_file="weights_checks_srs",
                  output_dir=output_weighting_data_folder) # < 10 seconds

source("07_Adjust_Substate_Weights_SRS.R")

source("08_Create_County_Level_Calibration_Variable_File_SRS.R")
