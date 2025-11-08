#This program will create the full list of potential geography crossings
#12Nov2024: creating national version for 30 years of SRS run (only running national)
library(tidyverse)
library(readxl)
library(openxlsx) #22Jun2023: Added due to errors during output step

CONST_YEAR <- Sys.getenv("DATA_YEAR")


log_info("Started 02b_Geography_Crossings_National_SRS.R\n\n")



#First, define the weighting groups by geography type
#Note (22Jun2023): Even though not using national/region/state crossings directly in SRS, include to ensure mappings align
natWgtGps <- 1:20 #National
natLvls <- "National"
natCrossings <- expand.grid(natLvl=natLvls,
                            natWgtGp=natWgtGps) %>%
  mutate(natCrossNum=1:nrow(.))


#Export
workbook<-paste0(output_weighting_data_folder,"Geography_Crossings_National_SRS.xlsx")

wb<-createWorkbook()
addWorksheet(wb,"National")

writeData(wb,"National",
          natCrossings,
          rowNames=FALSE)

saveWorkbook(wb, workbook, overwrite = TRUE)

log_info("Finished 02b_Geography_Crossings_National_SRS.R\n\n")
