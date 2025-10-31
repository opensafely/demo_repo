# import necessary libraries
library(tidyverse)
library(here)
library(arrow)
library(lubridate)

# import dataset
df <- read_feather(
    here::here("output", "dataset.arrow")
)

# define study dates
study_start_date <- ymd("2020-03-01")
study_end_date <- ymd("2022-02-28")

# reformat some of the data
df <- df %>% 
  mutate(
    # add labels to ethnicity
    ethnicity = relevel(factor(latest_ethnicity_group, 
                               levels = c("1", "2", "3", "4", "5"),
                               labels = c("White", "Mixed", 
                                          "Asian or Asian British",
                                          "Black or Black British",
                                          "Other Ethnic Groups"),
                               ordered = FALSE), ref = "White"),
    # turn sex into a factor for models
    sex = relevel(
      factor(str_to_title(sex), levels = c("Female", "Male", "Intersex")),
      ref = "Female"),
    # create censoring variable
    censor = if_else(
      censor_date < study_end_date, 1, 0
    )
) %>% select(-latest_ethnicity_group)

# pivot the data to have multiple rows per patient
df_long <- df %>% 
  pivot_longer(
    # select columns relating to salbutamol quantity
    cols = starts_with("salbutamol"),
    # create column containing the year number
    names_to = "year", 
    # removes the prefix from the column names so year = {1, 2} etc
    names_prefix = "salbutamol_quantity_y", 
    # create column of corresponding inhaler quantities for each year
    values_to = "salbutamol_quantity" 
  )

# reorder the columns in a way that is logical for future work
col_order <- c("patient_id", "age", "sex", "ethnicity", "asthma", "copd",
               "year", "salbutamol_quantity", "censor", "censor_date",
               "deregistration_date", "death_date")
df_long <- df_long[, col_order]

# save the processed data
write_feather(
  df_long, here::here("output", "dataset_processed.arrow")
)
