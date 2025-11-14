# import necessary libraries
library(tidyverse)
library(here)
library(arrow)

# import dataset
df <- read_feather(
  here::here("output", "dataset_processed.arrow")
)