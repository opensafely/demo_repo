# import necessary libraries
library(here)
library(arrow)
library(tidyverse)
library(ggplot2)

# import processed dataset
df <- read_feather(
  here::here("output", "dataset_processed.arrow")
)

## frequency tables for categorical variables

# create an empty list for tables
tables <- list()

# define the categorical variables you wish to look at 
vars <- c("age_group", "sex", "ethnicity", "imd_quintile")

# loop through variables
for (var in vars) {
  
  # use table() to get frequency tables for categorical variables
  tables[[var]] <- table(df[[var]], df$year)
  
}

# return the tables
print(tables)

## histograms for continuous variables and dates

# create an empty list for histograms
hists <- list()

# define the continuous/date variables you wish to look at 
vars <- c("age", "salbutamol_quantity", "deregistration_date", "death_date", "censor_date")

# loop through variables
for (var in vars) {
  
  # use ggplot() to get histograms for variables of interest
  hists[[var]] <- ggplot(data = df, aes(.data[[var]])) +
    geom_histogram(stat = "count") +
    facet_wrap(~year)
  
}

print(hists)

## check missing values

## check date orders
