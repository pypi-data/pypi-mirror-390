library("rmarkdown")
library("tidyverse")
library(RPostgres)
library(DT)
#memory.limit = 3200000

source(here::here("tasks/logging.R"))

source("dictionaries.R")

checkfunction <- function(data, ...){

  groupbyinput <- rlang:::enquos(...)
  data %>% group_by( !!!(groupbyinput) ) %>% summarise(count = n() ) %>% print()

}
trim_upper <- compose(toupper, partial(trimws, which="both"))

outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
filepathout = paste0(outputPipelineDir, "/artifacts/")
markdownpathout = paste0(outputPipelineDir, "/markdown/")
queried_data_path = paste0(outputPipelineDir, "/initial_tasks_output/database_queries/") # path where queried data is stored
der_bystate_file_path = paste0(outputPipelineDir, "/indicator_table_extracts_bystate/") #output path for data extracts by state

if (! dir.exists(filepathout)) {
  dir.create(filepathout, recursive = TRUE)
}

if (! dir.exists(markdownpathout)) {
  dir.create(markdownpathout, recursive = TRUE)
}


nibrsColTypes <- read_csv(file=paste0(queried_data_path,"nibrs_col_types.csv.gz"))

#Recodes:
# > dbGetQuery(con,
#              +            "SELECT DISTINCT DATA_TYPE,COLUMN_NAME
#              +            from INFORMATION_SCHEMA.COLUMNS
#              +            WHERE TABLE_NAME='nibrs_incident' OR
#              +            TABLE_NAME='nibrs_offender' OR
#              +            TABLE_NAME='nibrs_arrestee' OR
#              +            TABLE_NAME='nibrs_arrest_type' OR
#              +            TABLE_NAME='nibrs_arrestee_weapon' OR
#              +            TABLE_NAME='nibrs_weapon_type' OR
#              +            TABLE_NAME='agencies' OR
#              +            TABLE_NAME='nibrs_bias_motivation' OR
#              +            TABLE_NAME='nibrs_bias_list' OR
#              +            TABLE_NAME='nibrs_weapon' OR
#              +            TABLE_NAME='nibrs_victim' OR
#              +            TABLE_NAME='nibrs_victim_offense' OR
#              +            TABLE_NAME='nibrs_offense' OR
#              +            TABLE_NAME='nibrs_offense_type' OR
#              +            TABLE_NAME='nibrs_cleared_except' OR
#              +            TABLE_NAME='nibrs_month'") %>%
# +   group_by(data_type) %>% summarize(n=n()) %>% arrange(-n)
# # A tibble: 7 x 2
#   data_type                       n
#   <chr>                       <int>
# 1 character varying              48
# 2 integer                        22
# 3 character                      20
# 4 smallint                       19
# 5 bigint                         14
# 6 date                            6
# 7 timestamp without time zone     5



nibrsNamesCrosswalk <- read_csv(file=file.path("Data","nibrs_names_crosswalk.csv"))
derColTypes <- read_csv(file=file.path("Data","der_col_types.csv"))

outColTypes <- nibrsColTypes %>%
  full_join(nibrsNamesCrosswalk,by=c("column_name")) %>%
  mutate(readr_type=case_when(#data_type=="character varying" ~ "character()",
                              #data_type=="integer" ~ "col_integer()",
                              #data_type=="character" ~ "col_character()",
                              #data_type=="smallint" ~ "col_integer()",
                              #data_type=="bigint" ~ "col_integer()",
                              #data_type=="date" ~ "col_date()",
                              #data_type=="timestamp without time zone" ~ "col_datetime()"
                              data_type=="character varying" ~ "c",
                              data_type=="integer" ~ "i",
                              data_type=="character" ~ "c",
                              data_type=="smallint" ~ "i",
                              data_type=="bigint" ~ "i",
                              data_type=="date" ~ "D",
                              data_type=="timestamp without time zone" ~ "T"

  )) %>%
  bind_rows(derColTypes) %>%
  select(output_name,readr_type) %>%
  subset(duplicated(.)==FALSE)



input_state <- Sys.getenv("INPUT_STATE")

log_info(paste0(input_state,": 01_Extract_All.Rmd starting..."))
rmarkdown::render("01_Extract_All.Rmd", output_format=html_document(),
                  output_file = paste0(markdownpathout, "01_Extract_All_", input_state ,".html"),
                  envir = new.env(), quiet = TRUE)
invisible(gc())
knitr::knit_meta(clean = TRUE)
