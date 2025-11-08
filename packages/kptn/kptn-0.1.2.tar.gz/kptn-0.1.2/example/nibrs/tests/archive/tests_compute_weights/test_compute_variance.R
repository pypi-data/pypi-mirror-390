context("NIBRS Create Weights Tests - Variance")

source("../utils.R")
setEnvForTask("../../tasks/compute_weights")

# Run the task main script
system("Rscript Create_Variance_Analysis_Dataset.R")


r_fields <- list(
  c()
)
compareOutputToGoldStandard(
  listOfFiles[["variance"]],
  r_fields,
  output_folder[["variance"]]
  )
