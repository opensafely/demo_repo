# import necessary libraries
library(tidyverse)
library(here)
library(arrow)
library(broom)
library(broom.helpers)

# import dataset
df <- read_feather(
  here::here("output", "dataset_processed.arrow")
) 

# model quantity
model <- lm(
  salbutamol_quantity ~ age + sex + ethnicity + imd_quintile + asthma + copd + year,
  data = df
)

# tidy the model
model_tidy <- model %>%
  tidy_and_attach() %>% 
  tidy_add_reference_rows() %>% 
  tidy_add_estimate_to_reference_rows(conf.level = 0.95) %>% 
  tidy_add_term_labels(labels = c(age = "Age (Years)")) %>%
  tidy_remove_intercept() %>% 
  mutate(
    label = case_when(
      label %in% c("TRUE", "FALSE") ~ paste0(var_label, "(", label, ")"),
      var_label == "year" ~ paste0("Study Year ", label),
      TRUE ~ label)
  )

# create forest plot
model_tidy %>% 
  ggplot(aes(y = label, x = estimate, xmin = conf.low, xmax = conf.high)) +
  geom_vline(xintercept = 0, linetype = 2) +
  coord_cartesian(xlim = c(-4, 4)) +
  geom_pointrange(position = position_dodge(width = 0.75), size = 0.5) +
  theme_bw()
