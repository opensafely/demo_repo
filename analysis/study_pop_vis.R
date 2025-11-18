# import necessary libraries
library(tidyverse)
library(here)
library(arrow)
library(lubridate)

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
    ), ref = "Adolescent (12-17)"),
    year_start = case_when(
      year == 1 ~ ymd("2020-03-01"),
      year == 2 ~ ymd("2021-03-01")
    )
  ) %>% 
  group_by(year) %>% 
  mutate(
    decile = ntile(salbutamol_quantity, 10)/10
  )

##--- create some decile charts ? 

# ---- compute summary (median + each decile) -----------------
plot_df <- df %>% 
  group_by(year_start, decile) %>% 
  summarise(
    decile_value = quantile(salbutamol_quantity, probs = unique(decile), na.rm = T),
    .groups = "drop"
  )

median_df <- df %>% 
  group_by(year_start) %>% 
  summarise(
    median_value = median(salbutamol_quantity, na.rm = T),
    .groups = "drop"
  )

# ---- plotting ------------------------------------------------
ggplot() +
  # decile dashed lines
  geom_line(
    data = plot_df,
    aes(x = year_start, y = decile_value, group = decile),
    color = "blue",
    linetype = "dashed",
    alpha = 0.7
  ) +
  # median line
  geom_line(
    data = median_df,
    aes(x = year_start, y = median_value),
    color = "blue",
    linewidth = 0.9
  ) +
  scale_x_date(
    date_breaks = "3 months",
    date_labels = "%B %Y"
  ) +
  theme_minimal(base_size = 14) +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1),
    legend.position = "top"
  ) +
  labs(
    x = NULL, y = NULL, 
    linetype = "",
    title = "Median and Deciles Over Time"
  ) +
  scale_linetype_manual(
    values = c("median" = "solid", "decile" = "dashed")
  )

# --- Compute decile points ---
decile_df <- df %>%
  group_by(year_start, decile) %>%
  summarise(
    value = quantile(salbutamol_quantity, probs = unique(decile), na.rm = T),
    .groups = "drop"
  ) %>%
  mutate(type = "decile")

# --- Compute median points ---
median_df <- df %>%
  group_by(year_start) %>%
  summarise(
    value = median(salbutamol_quantity, na.rm = T),
    .groups = "drop"
  ) %>%
  mutate(type = "median")

# --- Combine ---
plot_df <- bind_rows(decile_df, median_df)

# ---- PLOT ----------------------------------------------------
ggplot(plot_df, aes(x = factor(year_start), y = value, group = interaction(type, decile))) +
  geom_point(
    aes(shape = type, fill = type),
    color = "blue",
    size = 3,
    alpha = 0.9
  ) +
  scale_shape_manual(values = c(median = 21, decile = 1),
                     labels = c(median = "Median", decile = "Decile"))  +
  scale_fill_manual(values = c(median = "blue", decile = NA),
                    labels = c(median = "Median", decile = "Decile")) +
  # scale_x_date(date_breaks = "3 months",
  #              date_labels = "%B %Y") +
  theme_minimal(base_size = 14) +
  theme(legend.position = "top") +
  labs(
    x = NULL,
    y = NULL,
    shape = "",
    fill = ""
  )
