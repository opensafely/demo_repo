# load necessary libraries
library(lubridate)

# create output directories
fs::dir_create(here::here("analysis", "design"))

# define key dates
study_dates <- tibble::lst(
  pre_pandemic_start = ymd("2017-03-01"), #start of first period
  pre_pandemic_end_date = ymd("2020-02-29"), #end of first period
  pandemic_start_date = ymd("2020-03-01"), #start of second period
  pandemic_end_date = ymd("2022-02-28"), #end of second period
  post_pandemic_start_date = ymd("2022-03-01"), #start of third period
  post_pandemic_end_date = ymd("2025-02-28"), #end of third period
)

jsonlite::write_json(study_dates, path = here::here("analysis",
                     "design", "study-dates.json"), auto_unbox = TRUE,
                     pretty = TRUE)
