# import necessary libraries
library(tidyverse)
library(here)
library(ggplot2)

# import measure - when using dummy data some modifications may be needed
df <- read_csv(
  here::here("output", "demo_measures_conditions.csv")
)

# change the data when it's dummy - so there are things to visualise
df <- df %>%
  mutate(
    numerator = ceiling(denominator/runif(12, 1.24, 3.09)),
    ratio = numerator/denominator
  )

# plot the measures
plot <- df %>%
  # add a variable indicating the year
  mutate(
    start = factor(format(interval_start, "%Y-%m")),
    measure_label = case_when(
      str_detect(measure, "multiple") ~ "Had Multiple Inhalers",
      str_detect(measure, "prescription") ~ "Had Any Inhalers"
    ),
    condition = if_else(condition == "copd", "COPD", str_to_title(condition))
  ) %>% 
  ggplot() +
  geom_bar(aes(x = condition, y = ratio, group = start, fill = start),
           stat = "identity", position = "dodge") + facet_wrap(~measure_label) +
  scale_fill_brewer(palette = "Set2") + theme_bw(base_size = 18) +
  labs(x = "Condition", y = "Proportion of Population", 
       fill = "Interval Start")

# create directory for saving
fs::dir_create("output", "measures")

# save the plot
ggsave(here::here("output", "measures", "measures_by_conditions.png"), plot,
                  height = 12, width = 14)
