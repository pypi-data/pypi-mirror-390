library(logger)
library(RPostgres)
library(data.table)

logging_level = Sys.getenv("LOG_THRESHOLD", unset = "DEBUG")
log_threshold(logging_level)

log_info(paste0("Setting logging level to ",logging_level))

log_formatter(formatter_glue)
logger_gen <- layout_glue_generator(format = 'PID:{pid} <{time}> [{level}] {call}: {msg}')
log_layout(logger_gen)
log_file <- Sys.getenv("LOG_FILE")
if (log_file != "") {
  log_appender(appender_tee(log_file))
}


time_query <- function(con, query){
  temp_output <- system.time(df <- dbGetQuery(con, query))
  log_debug(paste0("Time for query (user/system/elapsed):",toString(summary(temp_output))))
  return(df)
}


log_dim <- function(df){
  log_debug(toString(dim(df)))
}

log_free <- function() {
  log_debug(system("free -mh", intern = FALSE))
}

twodlist_tostring <- function(two_d_list){
  out_l <- list()
  for(i in two_d_list){
    out_l <- append(out_l,paste(i,collapse=", "))
  }
  return (paste(out_l,collapse="\n"))
}

read_csv_logging <- function(file_path, ...){
  log_debug(paste0("Reading in ",file_path))
  if(endsWith(file_path,".gz")){
    df <- read_csv(gzfile(file_path), ...)
  } else {
    df <- read_csv(file_path, ...)
  }
  log_debug("Finished read")
  return(df)
}

fread_logging <- function(file_path, ...){
  log_debug(paste0("Reading in ",file_path))
  df <- fread(file_path, ...)
  log_debug("Finished read")
  return(df)
}

write_csv_logging <- function(df, file_path, ...){
  log_debug(paste0("Writing out ",file_path))
  if(endsWith(file_path,".gz")){
    write_csv(df, gzfile(file_path), ...)
  } else {
    write_csv(df, file_path, ...)
  }
  log_debug("Finished write")
}

write_xlsx_logging <- function(df, file_path, ...){
  log_debug(paste0("Writing out ",file_path))
  write_xlsx(df, file_path, ...)
  log_debug("Finished write")
}

read_dot_csv_logging <- function(file_path, ...){
  log_debug(paste0("Reading in ",file_path))
  df <- read.csv(file_path, ...)
  log_debug("Finished read")
  return(df)
}

write_dot_csv_logging <- function(df, file_path, ...){
  log_debug(paste0("Writing out ",file_path))
  write.csv(df, file_path, ...)
  log_debug("Finished write")
}

fwrite_wrapper <- function(df, file_path, ...) {
  if (nrow(df) > 0) {
    log_debug(paste0("Using fwrite() for ", file_path))
    fwrite(df, file_path, ...)
  } else {
    log_debug(paste0("Using write_csv() for ", file_path))
    write_csv(df, file_path, ...)
  }
  log_debug("Finished writing.")
}