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
  here::here("output", "demo_measures_ages.csv")
)

# change the data when it's dummy - so there are things to visualise
df_year <- df_year %>%
  mutate(
    numerator = ceiling(denominator/runif(18, 1.24, 3.09)),
    ratio = numerator/denominator
  )

# plot the measures
plot_year <- df_year %>%
  # add a variable indicating the year
  mutate(
    start = factor(format(interval_start, "%Y-%m")),
    measure_label = case_when(
      str_detect(measure, "multiple") ~ "Had Multiple Inhalers",
      str_detect(measure, "prescription") ~ "Had Any Inhalers",
      str_detect(measure, "asthma") ~ "Diagnosis of Asthma or COPD"
    ),
    age_group = str_to_title(gsub("_", " ", age_group))
  ) %>% 
  ggplot() +
  geom_bar(aes(x = age_group, y = ratio, group = start, fill = start),
           stat = "identity", position = "dodge") + facet_wrap(~measure_label) +
  scale_fill_brewer(palette = "Set2") + theme_bw(base_size = 18) +
  labs(x = "Age Group", y = "Proportion of Population",
       fill = "Interval Start")

# save the plot
ggsave(here::here("output", "measures", "measures_by_age_groups.png"),
       plot_year, height = 12, width = 14)

## monthly measure

# import measure - when using dummy data some modifications may be needed
df_month <- read_csv(
  here::here("output", "demo_measures_ages_monthly.csv")
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
      str_detect(measure, "prescription") ~ "Had Any Inhalers",
      str_detect(measure, "asthma") ~ "Diagnosis of Asthma or COPD"
    ),
    age_group = str_to_title(gsub("_", " ", age_group))
  ) %>% 
  ggplot() +
  geom_line(aes(x = interval_start, y = ratio, colour = measure_label),
            linewidth = 1) + facet_wrap(~age_group) + 
  scale_colour_brewer(palette = "Accent") +
  labs(x = "Month", y = "Proportion of Population", colour = "Measure") +
  theme_bw(base_size = 18) + theme(legend.position = "top")

# save the plot
ggsave(here::here("output", "measures", "measures_by_age_groups_monthly.png"),
       plot_month, height = 12, width = 14)
