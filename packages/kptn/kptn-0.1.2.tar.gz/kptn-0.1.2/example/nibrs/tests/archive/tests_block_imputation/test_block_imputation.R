context("NIBRS Run Block Imputation")

source("../utils.R")
setEnvForTask("../../tasks/impute_blocks")

# Run task main script
system("Rscript 100_Run_Block_Imputation.R")

imputed_fields <- list(
  c("ori.don"),
  c("ct.don","ori.don","pred.don","jan_v.don","jan_p.don","jan_o.don",	"feb_v.don",	"feb_p.don",	"feb_o.don",	"mar_v.don",	
    "mar_p.don",	"mar_o.don",	"apr_v.don",	"apr_p.don",	"apr_o.don",	"may_v.don",	"may_p.don",	
    "may_o.don",	"jun_v.don",	"jun_p.don",	"jun_o.don",	"jul_v.don",	"jul_p.don",	"jul_o.don",	
    "aug_v.don",	"aug_p.don",	"aug_o.don",	"sep_v.don",	"sep_p.don",	"sep_o.don",	"oct_v.don",	
    "oct_p.don",	"oct_o.don",	"nov_v.don",	"nov_p.don",	"nov_o.don",	"dec_v.don",	"dec_p.don",
    "dec_o.don",	"jan_v.c",	"jan_p.c",	"jan_o.c",	"feb_v.c",	"feb_p.c",	"feb_o.c",	"mar_v.c",	
    "mar_p.c",	"mar_o.c",	"apr_v.c",	"apr_p.c",	"apr_o.c",	"may_v.c",	"may_p.c",	"may_o.c",	"jun_v.c",	"jun_p.c",	"jun_o.c",	
    "jul_v.c",	"jul_p.c",	"jul_o.c",	"aug_v.c",	"aug_p.c",	"aug_o.c",	"sep_v.c",	"sep_p.c",	"sep_o.c",	"oct_v.c",	"oct_p.c",	
    "oct_o.c",	"nov_v.c",	"nov_p.c",	"nov_o.c",	"dec_v.c",	"dec_p.c",	"dec_o.c",	"jan_v.i",	"jan_p.i",	"jan_o.i",	"feb_v.i",	
    "feb_p.i",	"feb_o.i",	"mar_v.i",	"mar_p.i",	"mar_o.i",	"apr_v.i",	"apr_p.i",	"apr_o.i",	"may_v.i",	"may_p.i",	"may_o.i",	
    "jun_v.i",	"jun_p.i",	"jun_o.i",	"jul_v.i",	"jul_p.i",	"jul_o.i",	"aug_v.i",	"aug_p.i",	"aug_o.i",	"sep_v.i",	"sep_p.i",	
    "sep_o.i",	"oct_v.i",	"oct_p.i",	"oct_o.i",	"nov_v.i",	"nov_p.i",	"nov_o.i",	"dec_v.i",	"dec_p.i",	"dec_o.i",
    "total_v","total_p",	"total_o",	"total_v.i",	"total_p.i",	"total_o.i",	"total_v.c",	"total_p.c",	"total_o.c","ct.c"
  ),
  c())

#"row.names"
compareOutputToGoldStandard(
  listOfFiles[["block_imputation"]],
  imputed_fields,
  output_folder[["block_imputation"]]
  )

