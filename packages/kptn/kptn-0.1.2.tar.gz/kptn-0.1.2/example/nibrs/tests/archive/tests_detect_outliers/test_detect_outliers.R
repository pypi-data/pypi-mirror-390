context("NIBRS Run Outlier Detection")

source("../utils.R")
setEnvForTask("../../tasks/detect_outliers")

# Run task main script
system("Rscript 100_run_outlier_detection_scripts.R")

compareOutputToGoldStandard(
  listOfFiles[["outlier_detection"]],
  list(c()),
  output_folder[["outlier_detection"]]
  )