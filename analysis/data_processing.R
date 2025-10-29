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
    latest_ethnicity_group = relevel(factor(latest_ethnicity_group,
                                            levels = c("1", "2", "3", "4", "5"),
                                            labels = c("White", "Mixed",
                                                       "Asian or Asian British",
                                                       "Black or Black British",
                                                       "Other Ethnic Groups"),
                                            ordered = FALSE), ref = "White"),
    # turn sex into a factor for models
    sex = relevel(factor(
      str_to_title(sex),
      levels = c("Female", "Male", "Intersex")
    ), ref = "Female"),
    # create censor date
    censor_date = pmin(
      death_date, deregistration_date, study_end_date, na.rm = TRUE
    ),
    # create censoring variable
    censor = if_else(
      censor_date < study_end_date, 1, 0
    )
)

# pivot the data to have multiple rows per patient
df_long <- df %>% 
  pivot_longer(
    cols = starts_with("salbutamol"),
    names_to = "year",
    names_prefix = "salbutamol_quantity_y",
    values_to = "salbutamol_quantity"
  )
