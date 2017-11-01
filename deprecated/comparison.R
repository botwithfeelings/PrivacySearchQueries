library(stats)

amt_filename <- "./indextrends/amt_data.csv"
index_filename <- "./indextrends/index_data.csv"
amt_dataset <- read.csv(amt_filename)
index_dataset <- read.csv(index_filename)

getWilcoxonTest <- function(indexParam, amtParam, infoParam) 
{
  print(infoParam)  
  mean_index = mean(indexParam, na.rm=TRUE)
  mean_amt  = mean(amtParam, na.rm=TRUE)
  mean_str  = paste0("Index Mean: ",    mean_index, "AMT mean: ", mean_amt)
  print(mean_str)
  print("-------------------------")
  print("H != L")
  t_test_output <- wilcox.test(indexParam, amtParam, alternative="two.sided", var.equal=FALSE, paired=FALSE) 
  print(t_test_output)
  print("-------------------------")  
  print("H > L")  
  t_test_output <- wilcox.test(indexParam, amtParam, alternative="greater", var.equal=FALSE, paired=FALSE) 
  print(t_test_output)
  print("-------------------------")  
  print("H < L")    
  t_test_output <- wilcox.test(indexParam, amtParam, alternative="less", var.equal=FALSE, paired=FALSE) 
  print(t_test_output )
  print("-------------------------")
}

## Run for individual categories

# For Overall
index_vals <- index_dataset$overall
amt_vals <- amt_dataset$overall
getWilcoxonTest(index_vals, amt_vals, "Overall")

# For Overall with AMT equivalent w/o the category that doesn't have data in index.
index_vals <- index_dataset$overall
amt_vals <- amt_dataset$overall_s
getWilcoxonTest(index_vals, amt_vals, "Overall Equivalent")


# For Apps and Privacy
index_vals <- index_dataset$app_priv
amt_vals <- amt_dataset$app_priv
getWilcoxonTest(index_vals, amt_vals, "Apps and Privacy")

# For Communications Privacy
index_vals <- index_dataset$comm_priv
amt_vals <- amt_dataset$comm_priv
getWilcoxonTest(index_vals, amt_vals, "Communications Privacy")

# For Deleting Apps
index_vals <- index_dataset$del_app
amt_vals <- amt_dataset$del_app
getWilcoxonTest(index_vals, amt_vals, "Deleting Apps")

# For Deleting Social Media Connections.
index_vals <- index_dataset$del_soc_acc
amt_vals <- amt_dataset$del_soc_acc
getWilcoxonTest(index_vals, amt_vals, "Deleting Social Media Connections")

# For Search Anonymity
index_vals <- index_dataset$ser_anon
amt_vals <- amt_dataset$ser_anon
getWilcoxonTest(index_vals, amt_vals, "Search Anonymity")

# For Social Media Settings and Privacy
index_vals <- index_dataset$soc_med_sett
amt_vals <- amt_dataset$soc_med_sett
getWilcoxonTest(index_vals, amt_vals, "Social Media Settings and Privacy")

# For Web Anonymity
index_vals <- index_dataset$web_anon
amt_vals <- amt_dataset$web_anon
getWilcoxonTest(index_vals, amt_vals, "Web Anonymity")