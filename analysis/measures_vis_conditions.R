# import necessary libraries
library(tidyverse)
library(here)
library(lubridate)
library(ggplot2)

# create directory for outputs
fs::dir_create("output", "measures")

# define study start and end
study_start_date <- ymd("2020-03-01")
study_end_date <- ymd("2022-02-28")

## yearly measure

# import measure - when using dummy data some modifications may be needed
df_year <- read_csv(
  here::here("output", "demo_measures_conditions.csv")
)

# change the data when it's dummy - so there are things to visualise
df_year <- df_year %>%
  mutate(
    numerator = ceiling(denominator/runif(12, 1.24, 3.09)),
    ratio = numerator/denominator
  )

# plot the measures
plot_year <- df_year %>%
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

# save the plot
ggsave(here::here("output", "measures", "measures_by_conditions.png"),
       plot_year, height = 12, width = 14)

## monthly measure

# import measure - when using dummy data some modifications may be needed
df_month <- read_csv(
  here::here("output", "demo_measures_conditions_monthly.csv")
)

# change the data when it's dummy - so there are things to visualise
df_month <- df_month %>%
  mutate(
    numerator = ceiling(denominator/runif(18, 1.24, 3.09)),
    ratio = numerator/denominator
  )

# plot the measures
plot_month <- df_month %>%
  # add a variable indicating the year
  mutate(
    start = case_when(
      interval_start >= study_start_date & interval_start < study_start_date + years(1)
      ~ paste0(year(study_start_date), "-03"),
      interval_start >= study_start_date + years(1) & interval_start < study_end_date
      ~ paste0(year(study_start_date + years(1)), "-03")
    ),
    measure_label = case_when(
      str_detect(measure, "multiple") ~ "Had Multiple Inhalers",
      str_detect(measure, "prescription") ~ "Had Any Inhalers"
    ),
    condition = if_else(condition == "copd", "COPD", str_to_title(condition))
  ) %>% 
  ggplot() +
  geom_line(aes(x = interval_start, y = ratio, colour = condition),
            linewidth = 1) + facet_wrap(~measure_label) + 
  scale_colour_brewer(palette = "Dark2") +
  labs(x = "Month", y = "Proportion of Population", colour = "Condition") +
  theme_bw(base_size = 18) + theme(legend.position = "top")

# save the plot
ggsave(here::here("output", "measures", "measures_by_conditions_monthly.png"),
       plot_month, height = 12, width = 14)
