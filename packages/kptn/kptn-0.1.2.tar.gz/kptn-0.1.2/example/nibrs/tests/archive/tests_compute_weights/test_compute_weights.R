context("NIBRS Create Weights Tests")

source("../utils.R")
setEnvForTask("../../tasks/compute_weights")

# Run the task main script
system("Rscript 00_Weights_Creation_Master.R")

# 01_Create_Clean_Frame.R -> cleanframe.csv
# 02_Weights_Data_Setup.R -> SF.csv
# 03_Weights_Calibration_National.R -> weights_national.csv, SF_postN.csv
# 03_Weights_Calibration_Region.R -> weights_region.csv, SF_postR.csv
# 03_Weights_Calibration_State.R -> weights_state.csv, SF_postS.csv
# 03_Weights_Calibration_Special.R -> weights_tribal.csv, weights_university.csv, SF_postSP.csv


r_fields <- list(
  c(),
  c(),
  c(),
  c(),
  c("RegionWgt"),
  c(),
  c(),
  c(),
  c(),
  c(),
  c()
)

compareOutputToGoldStandard(listOfFiles[["weighting"]], r_fields, output_folder[["weighting"]])
