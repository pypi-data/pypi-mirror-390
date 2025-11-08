###-------------------------------------------------------------------------------
### Calculate imputed values based on donor
###-------------------------------------------------------------------------------

impvals <- function(data){
  
  #Keep order of dataset  
  variable_order <- syms(colnames(data)) 
  
  temp <- data %>% 
    mutate(jan_v.c=NA, jan_p.c=NA, jan_o.c=NA, feb_v.c=NA, feb_p.c=NA, feb_o.c=NA, mar_v.c=NA, mar_p.c=NA, mar_o.c=NA, apr_v.c=NA, apr_p.c=NA, apr_o.c=NA,
           may_v.c=NA, may_p.c=NA, may_o.c=NA, jun_v.c=NA, jun_p.c=NA, jun_o.c=NA, jul_v.c=NA, jul_p.c=NA, jul_o.c=NA, aug_v.c=NA, aug_p.c=NA, aug_o.c=NA,
           sep_v.c=NA, sep_p.c=NA, sep_o.c=NA, oct_v.c=NA, oct_p.c=NA, oct_o.c=NA, nov_v.c=NA, nov_p.c=NA, nov_o.c=NA, dec_v.c=NA, dec_p.c=NA, dec_o.c=NA,
           jan_v.i=NA, jan_p.i=NA, jan_o.i=NA, feb_v.i=NA, feb_p.i=NA, feb_o.i=NA, mar_v.i=NA, mar_p.i=NA, mar_o.i=NA, apr_v.i=NA, apr_p.i=NA, apr_o.i=NA,
           may_v.i=NA, may_p.i=NA, may_o.i=NA, jun_v.i=NA, jun_p.i=NA, jun_o.i=NA, jul_v.i=NA, jul_p.i=NA, jul_o.i=NA, aug_v.i=NA, aug_p.i=NA, aug_o.i=NA,
           sep_v.i=NA, sep_p.i=NA, sep_o.i=NA, oct_v.i=NA, oct_p.i=NA, oct_o.i=NA, nov_v.i=NA, nov_p.i=NA, nov_o.i=NA, dec_v.i=NA, dec_p.i=NA, dec_o.i=NA           
           ) %>%
    select(
      # 36 variables original variables                    
      jan_v, jan_p, jan_o, feb_v, feb_p, feb_o, mar_v, mar_p, mar_o, apr_v, apr_p, apr_o,
      may_v, may_p, may_o, jun_v, jun_p, jun_o, jul_v, jul_p, jul_o, aug_v, aug_p, aug_o,
      sep_v, sep_p, sep_o, oct_v, oct_p, oct_o, nov_v, nov_p, nov_o, dec_v, dec_p, dec_o,
      # 36 variables from donors
      jan_v.don, jan_p.don, jan_o.don, feb_v.don, feb_p.don, feb_o.don, mar_v.don, mar_p.don, mar_o.don, apr_v.don, apr_p.don, apr_o.don,
      may_v.don, may_p.don, may_o.don, jun_v.don, jun_p.don, jun_o.don, jul_v.don, jul_p.don, jul_o.don, aug_v.don, aug_p.don, aug_o.don,
      sep_v.don, sep_p.don, sep_o.don, oct_v.don, oct_p.don, oct_o.don, nov_v.don, nov_p.don, nov_o.don, dec_v.don, dec_p.don, dec_o.don,
      # 36 variables complete variables
      jan_v.c, jan_p.c, jan_o.c, feb_v.c, feb_p.c, feb_o.c, mar_v.c, mar_p.c, mar_o.c, apr_v.c, apr_p.c, apr_o.c,
      may_v.c, may_p.c, may_o.c, jun_v.c, jun_p.c, jun_o.c, jul_v.c, jul_p.c, jul_o.c, aug_v.c, aug_p.c, aug_o.c,
      sep_v.c, sep_p.c, sep_o.c, oct_v.c, oct_p.c, oct_o.c, nov_v.c, nov_p.c, nov_o.c, dec_v.c, dec_p.c, dec_o.c,
      # low outlier variables (1=Low outlier, 0=Not low outlier)
      xp1_v, xp1_p, xp1_o, xp2_v, xp2_p, xp2_o, xp3_v, xp3_p, xp3_o, xp4_v, xp4_p, xp4_o, xp5_v, xp5_p, xp5_o, xp6_v, xp6_p, xp6_o,
      xp7_v, xp7_p, xp7_o, xp8_v, xp8_p, xp8_o, xp9_v, xp9_p, xp9_o, xp10_v, xp10_p, xp10_o, xp11_v, xp11_p, xp11_o, xp12_v, xp12_p, xp12_o,
      # 36 variables imputed variables
      jan_v.i, jan_p.i, jan_o.i, feb_v.i, feb_p.i, feb_o.i, mar_v.i, mar_p.i, mar_o.i, apr_v.i, apr_p.i, apr_o.i,
      may_v.i, may_p.i, may_o.i, jun_v.i, jun_p.i, jun_o.i, jul_v.i, jul_p.i, jul_o.i, aug_v.i, aug_p.i, aug_o.i,
      sep_v.i, sep_p.i, sep_o.i, oct_v.i, oct_p.i, oct_o.i, nov_v.i, nov_p.i, nov_o.i, dec_v.i, dec_p.i, dec_o.i,      
      #Keep the remaining variables
      everything()
    )
  
  # loop through row
  for (x in 1:nrow(temp)){
    # loop through column
    for (y in 1:36){
      
      # Use observed value      
      if ( !is.na(temp[x, y]) & temp[x, y+108]!=1) 
      {
        temp[x, y+72] = temp[x, y]
      }
      
      # Use donor value if value is missing or low outlier
      if( is.na(temp[x, y]) | temp[x, y+108]==1)
      {
        temp[x, y+72] = temp[x, y+36]
      }
      
      # Create only imputed variables
      if( (is.na(temp[x, y]) | temp[x, y+108]==1)& !is.na(temp[x, y+72]) )
      {
        temp[x, y+144] = temp[x, y+72]
      }
    }
  }
  
  #Keep the order of the original dataset
  temp2 <- temp %>% select(!!!variable_order, everything())
  
  
  temp2 <- temp2 %>% mutate(total_v = rowSums(select(., jan_v, feb_v, mar_v, apr_v, may_v, jun_v, jul_v, aug_v, sep_v, oct_v, nov_v, dec_v),na.rm=T))
  temp2 <- temp2 %>% mutate(total_p = rowSums(select(., jan_p, feb_p, mar_p, apr_p, may_p, jun_p, jul_p, aug_p, sep_p, oct_p, nov_p, dec_p),na.rm=T))
  temp2 <- temp2 %>% mutate(total_o = rowSums(select(., jan_o, feb_o, mar_o, apr_o, may_o, jun_o, jul_o, aug_o, sep_o, oct_o, nov_o, dec_o),na.rm=T))
  temp2 <- temp2 %>% mutate(total_v.i = rowSums(select(., jan_v.i, feb_v.i, mar_v.i, apr_v.i, may_v.i, jun_v.i, jul_v.i, aug_v.i, sep_v.i, oct_v.i, nov_v.i, dec_v.i),na.rm=T))
  temp2 <- temp2 %>% mutate(total_p.i = rowSums(select(., jan_p.i, feb_p.i, mar_p.i, apr_p.i, may_p.i, jun_p.i, jul_p.i, aug_p.i, sep_p.i, oct_p.i, nov_p.i, dec_p.i),na.rm=T))
  temp2 <- temp2 %>% mutate(total_o.i = rowSums(select(., jan_o.i, feb_o.i, mar_o.i, apr_o.i, may_o.i, jun_o.i, jul_o.i, aug_o.i, sep_o.i, oct_o.i, nov_o.i, dec_o.i),na.rm=T))
  temp2 <- temp2 %>% mutate(total_v.c = rowSums(select(., jan_v.c, feb_v.c, mar_v.c, apr_v.c, may_v.c, jun_v.c, jul_v.c, aug_v.c, sep_v.c, oct_v.c, nov_v.c, dec_v.c),na.rm=T))
  temp2 <- temp2 %>% mutate(total_p.c = rowSums(select(., jan_p.c, feb_p.c, mar_p.c, apr_p.c, may_p.c, jun_p.c, jul_p.c, aug_p.c, sep_p.c, oct_p.c, nov_p.c, dec_p.c),na.rm=T))
  temp2 <- temp2 %>% mutate(total_o.c = rowSums(select(., jan_o.c, feb_o.c, mar_o.c, apr_o.c, may_o.c, jun_o.c, jul_o.c, aug_o.c, sep_o.c, oct_o.c, nov_o.c, dec_o.c),na.rm=T))
  temp2 <- temp2 %>% mutate(ct.c = rowSums(select(., total_v.c, total_p.c, total_o.c),na.rm=T))
  
  return(temp2)
}

