# import necessary libraries
library(tidyverse)
library(here)
library(arrow)
library(gtsummary)

# import dataset
df <- read_feather(
  here::here("output", "dataset_processed.arrow")
) %>% 
  #set all NA categories to "Unknown"
  mutate_if(is.factor,
            forcats::fct_explicit_na,
            na_level = "Unknown") %>% 
  mutate(
    age_group = relevel(factor(
      case_when(age_group == "Adolescent" ~ "Adolescent (12-17)",
                age_group == "Adult" ~ "Adult (18-59)",
                age_group == "Older Adult" ~ "Older Adult (60-110)")
    ), ref = "Adolescent (12-17)")
  )

tbl <- tbl_summary(
  df,
  include = c(age_group, sex, ethnicity, asthma, copd,
              salbutamol_quantity, year),
  by = year,
  label = c(age_group = "Age (Grouped)", sex = "Sex", ethnicity = "Ethnicity",
            asthma = "Has Asthma", copd = "Has COPD",
            salbutamol_quantity = "Inhaler Quanity")
) %>% 
  modify_spanning_header(all_stat_cols() ~ "**Year of Study Period**") %>% 
  modify_footnote_header(
    footnote = "2020-03-01 - 2021-02-28",
    columns = matches("1"),
    replace = FALSE
  ) %>% 
  modify_footnote_header(
    footnote = "2021-03-01 - 2022-02-28",
    columns = matches("2"),
    replace = FALSE
  ) %>% 
  modify_footnote_body(
    footnote = "Quantity of salbutamol inhalers prescribed",
    columns = "label",
    rows = variable == "salbutamol_quantity" & row_type == "label"
)
