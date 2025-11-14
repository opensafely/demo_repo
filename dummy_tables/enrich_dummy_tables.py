# import necessary python libraries
import pandas as pd
import numpy as np

# suppress scientific notation - this will prevent changes to clinical codes
pd.options.display.float_format = '{:.0f}'.format

# import the data you want to enrich
meds = pd.read_csv('dummy_tables/medications.csv')

## first we need to change the *codes*

# import codelist which you want codes from
inhaler_codes = pd.read_csv('codelists/nhs-drug-refsets-gensalbdpinhdrug_cod.csv')
inhaler_codes.head() # to display the first 5 lines of loaded data

# transform the codes to ones that match the desired codelist - these are selected randomly
meds['dmd_code'] = np.random.choice(
    inhaler_codes['code'], 
    size = len(meds), 
    replace = True
)

## then we need to change the *dates*

# define the date range for the codes of interest
start = np.datetime64("2018-03-01")
end   = np.datetime64("2022-02-28")

# get the number of days between start and end
days = (end - start).astype(int)

# pick a random number of days to add to the start - for each row in the csv
random_days = np.random.randint(0, days + 1, size = len(meds))

# now assign dates within the range needed
meds['date'] = start + random_days

## now we can repeat the rows we want - in this case, all the inhalers after indexing (we need some before indexing as the same table is used to identify patients)

# define the date range of interest
repeat_start = np.datetime64("2020-03-01")
repeat_end   = np.datetime64("2022-02-28")

# filter the eligible rows
eligible = meds[(meds['date'] >= repeat_start) & (meds['date'] <= repeat_end)]

# repeat the eligible rows 10 times
eligible_repeated = pd.concat([eligible] * 2, ignore_index = True)

# Combine with original data (if you want that)
meds_expanded = pd.concat([meds, eligible_repeated], ignore_index = True)

# save the changes made 
meds_expanded.to_csv('dummy_tables/medications.csv', index = False)