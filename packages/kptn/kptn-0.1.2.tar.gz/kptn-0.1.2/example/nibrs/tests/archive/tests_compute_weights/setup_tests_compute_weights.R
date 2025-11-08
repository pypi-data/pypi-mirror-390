list_of_tests <- c("weighting","variance")

output_folder <- list()
listOfFiles <- list()

output_folder[["weighting"]] <- "/weighting/Data/"
output_folder[["variance"]] <- "/variance_analysis_dataset/Data/"

listOfFiles[["weighting"]] <- c(
  "cleanframe.csv",
  "SF.csv",
  "weights_national.csv",
  "SF_postN.csv",
  "weights_region.csv",
  "SF_postR.csv",
  "weights_state.csv",
  "SF_postS.csv",
  "weights_tribal.csv",
  "weights_university.csv",
  "SF_postSP.csv"
)
listOfFiles[["variance"]] <- c(
  "varAnalysisDF.csv"
)
