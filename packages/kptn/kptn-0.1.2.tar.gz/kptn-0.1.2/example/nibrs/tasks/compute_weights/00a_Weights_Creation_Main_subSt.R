set.seed(1)
Sys.setenv(VROOM_CONNECTION_SIZE=500072*2)

#14May2025: setting warn option to give warnings as they occur, rather than after a call (e.g., no longer report in bunches after a source() call
options(warn=1)
# weights to state level
source("01_Create_Clean_Frame.R") #3 minutes

source("02_Weights_Data_Setup.R") #3 minutes

# weights for sub-state
source("02_Weights_Data_Setup_County.R")

source("02b_Geography_Crossings.R") #Get list of geography crossings

source("03_Weights_Calibration_National.R")# 9 minutes

source("03_Weights_Calibration_Region_AltCombs.R")# 32 minutes

source("03_Weights_Calibration_State_SRS_AltCombs.R")# 6 minutes

source("03_Weights_Calibration_Special.R")# 6 minutes

source("03_Weights_Calibration_FO_SRS_AltCombs_Collapsed.R")

source("03_Weights_Calibration_JD_SRS_AltCombs_Collapsed.R")

source("03_Weights_Calibration_MSA_SRS_AltCombs_Collapsed.R")

rmarkdown::render(input="06_Weight_Checks.Rmd",
                  output_format="html_document",
                  output_file="weights_checks",
                  output_dir=output_weighting_data_folder) # < 10 seconds

source("04_TableShell_National.R") # < 10 seconds

source("04_TableShell_Region.R") 

source("04_TableShell_State.R") 

source("04_TableShell_Groupings_National.R") # < 10 seconds

source("04_TableShell_Groupings_Region.R") # < 10 seconds

source("04_TableShell_University.R") # < 10 seconds

source("04_TableShell_Tribal.R") #  < 10 seconds

source("04_TableShell_FO.R")

source("04_TableShell_JD.R")

source("04_TableShell_MSA.R")

source("05_Populate_TableA_National.R") # 6 minutes

source("05_Populate_TableA_Region.R")

source("05_Populate_TableA_State.R") 

source("05_Populate_TableA_Groupings_National.R") # 7 minutes

source("05_Populate_TableA_Groupings_Region.R") #

source("05_Populate_TableA_University.R") # 5 minutes

source("05_Populate_TableA_Tribal.R") # 6 minutes

source("05_Populate_TableA_FO_SRS_AltCombs_Collapsed.R")

source("05_Populate_TableA_JD_SRS_AltCombs_Collapsed.R")

source("05_Populate_TableA_MSA_SRS_AltCombs_Collapsed.R")

source("07_Adjust_Substate_Weights.R") #Adjust weights for later tasks

source("08_Create_Remaining_County_Level_Weights.R") #Create county-level version of national/region/state/university/tribal weights

source("09_Create_County_Level_Calibration_Variable_File.R")
