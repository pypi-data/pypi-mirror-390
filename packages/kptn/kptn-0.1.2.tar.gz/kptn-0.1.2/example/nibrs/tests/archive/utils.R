setEnvForTask <- function(taskPath){
  setwd(taskPath)

  levels <- length(gregexpr("/", taskPath)[[1]]) - 1
  dir_level <- paste(replicate(levels, "../"), collapse = "")

  # fix the input and output paths so they can be accessed from within the task folder
  outputPipelineDir <- paste0(dir_level,"tests/test_output_files")
  externalFilePath <- paste0(outputPipelineDir,"/externals")
  inputPipelineDir <- paste0(dir_level,"tests/",Sys.getenv("INPUT_PIPELINE_DIR_NAME"))

  # set these paths as environment variables to be accessed within the task
  Sys.setenv(
    OUTPUT_PIPELINE_DIR = outputPipelineDir,
    EXTERNAL_FILE_PATH = externalFilePath,
    INPUT_PIPELINE_DIR = inputPipelineDir
  )
}


compareOutputToGoldStandard <- function(listOfFiles, listOfFieldsToSkip, subFolder) {
  test_that("output files equal gold standard output", {
    for (i in 1:length(listOfFiles)) {
      output_file_name <- listOfFiles[i]
      drop_columns <- listOfFieldsToSkip[[i]]

      output_df <- read_csv(file = paste0(Sys.getenv("OUTPUT_PIPELINE_DIR"),subFolder,output_file_name))
      df_gs <- read_csv(file = paste0(Sys.getenv("INPUT_PIPELINE_DIR"),subFolder,output_file_name))
      if(length(drop_columns) > 0){
        output_df <- output_df[ , !(names(output_df) %in% drop_columns)]
        df_gs <- df_gs[ , !(names(df_gs) %in% drop_columns)]
      }

      # sort the files
      df_gs <- df_gs[do.call(order, df_gs),]
      row.names(df_gs) = NULL
      output_df <- output_df[do.call(order, output_df),]
      row.names(output_df) = NULL
      expect_true(all.equal(df_gs,output_df),info=print(paste0("Differences were found between the output and gold standard for: ",output_file_name)))
    }
  })
}
