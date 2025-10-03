from ehrql import create_dataset, months, years # import the necessary ehrQL functionalities
from ehrql.tables.tpp import patients, medications #,addresses # import the necessary tables from TPP
from variable_lib import ( # import variables which are defined in a separate file
    has_a_continuous_practice_registration_spanning,
    has_prior_event
 )
import codelists # import the codelists defined in a separate file

dataset = create_dataset() # create ehrQL generated dummy dataset

index_date = "2020-03-01" # define start of follow up period

registration_date = index_date - months(3) # define the start date for required registration period

# define the patients who have the required continuous registration (in this case 3 months)
registered_patients = (
    has_a_continuous_practice_registration_spanning(registration_date, index_date)
)

# define the patients who are of the correct age
age_of_interest = (
    patients.age_on(index_date) >= 12 & patients.age_on(index_date) <= 100
)

# define the population of interest for study
dataset.define_population(
    registered_patients
    & age_of_interest
)

## define patient info to extract
dataset.sex = patients.sex # sex
dataset.age = patients.age_on(index_date) # age at start of follow up
dataset.asthma = has_prior_event(codelists.ast_diag, index_date) # whether the patient has been diagnosed with asthma - this can be made more complex by looking at prescriptions etc
dataset.copd = has_prior_event(codelists.copd_diag, index_date) # whether the patient has been diagnosed with COPD - this can be made more complex by looking for resolution codes
dataset.salbutamol_quantity_y1 = ( # number of inhalers prescribed in first year of follow up 
    medications.where(
        medications.dmd_code.is_in(codelists.salbutamol)
    ).where(
        medications.date.is_on_or_between(index_date, index_date + years(1))
    ).count_for_patient()
)
dataset.salbutamol_quantity_y2 = ( # number of inhalers prescribed in second year of follow up 
    medications.where(
        medications.dmd_code.is_in(codelists.salbutamol)
    ).where(
        medications.date.is_on_or_between(index_date + years(1), index_date + years(2))
    ).count_for_patient()
)

# potentially add
# dataset.imd_rounded = addresses.for_patient_on(index_date).imd_rounded
# dataset..latest_ethnicity_group = (
#   clinical_events.where(clinical_events.snomedct_code.is_in(codelists.ethnicity_codes))
#   .where(clinical_events.date.is_on_or_before(index_date))
#   .sort_by(clinical_events.date)
#   .last_for_patient().snomedct_code
#   .to_category(codelists.ethnicity_codes)
# )
