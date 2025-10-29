# import the necessary ehrQL functionalities
from ehrql import create_dataset, months, years, case, when
# import the necessary tables from TPP
from ehrql.tables.tpp import (
    patients, medications,
    clinical_events,
    ons_deaths,
    practice_registrations#,
    #addresses 
)
# import variables which are defined in a separate file
from variable_lib import ( 
    has_a_continuous_practice_registration_spanning,
    has_prior_event,
    has_prior_meds,
    last_prior_event,
    med_years
 )
# import the codelists defined in a separate file
import codelists 

# create ehrQL generated dummy dataset
dataset = create_dataset() 

# define start of follow up period
index_date = "2020-03-01" 

# define end of follow up period
end_date = "2022-02-28"

# define the start date for required registration period
registration_date = index_date - months(3) 

# define the patients who have the required continuous registration (in this case 3 months)
registered_patients = (
    has_a_continuous_practice_registration_spanning(registration_date, index_date)
)

# define the patients who are of the correct age
age_of_interest = (
    (patients.age_on(index_date) >= 12) & (patients.age_on(index_date) <= 100)
)

# define the patients with known sex
sex_known = patients.sex.is_in(["female", "male", "intersex"]) 

# define the patients with an inhaler of interest in the two years preceding follow-up
inhaler_date = index_date - years(2)
inhaler_prescribed = (
    medications.where(medications.dmd_code.is_in(codelists.salbutamol))
    .where(medications.date.is_on_or_between(inhaler_date, index_date))
    .exists_for_patient()
)

# define population alive at index date
was_alive = (
    (ons_deaths.date.is_after(index_date))| # first using ONS deaths (best source)
    (ons_deaths.date.is_null())|
    (patients.date_of_death.is_after(index_date))| # then using patient table
    (patients.date_of_death.is_null())
)

# define the population of interest for study
dataset.define_population(
    registered_patients
    & age_of_interest
    & sex_known
    & inhaler_prescribed
    & was_alive
)

## define patient characteristics to extract

# age at start of follow up
dataset.age = patients.age_on(index_date) 

# sex
dataset.sex = patients.sex 

# patient ethnicity (5 groups from 2001 census)
dataset.latest_ethnicity_group = (
    clinical_events.where(clinical_events.snomedct_code.is_in(codelists.ethnicity_codes))
    .where(clinical_events.date.is_on_or_before(index_date))
    .sort_by(clinical_events.date)
    .last_for_patient().snomedct_code
    .to_category(codelists.ethnicity_codes)
)

# potentially add
# dataset.imd_rounded = addresses.for_patient_on(index_date).imd_rounded

## define patient comorbidities to extract

# define medication date to find recent prescriptions
medication_date = index_date - years(1)

# identify whether patient is asthmatic
dataset.asthma = (
    # has a diagnosis code
    (has_prior_event(codelists.asthma_codelist, index_date))
    # and has been prescribed medications in year prior to index
    & (
        (has_prior_meds(codelists.asthma_oral_medications, index_date, # oral medications
            where = medications.date.is_on_or_between(medication_date, index_date)))
         |(has_prior_meds(codelists.asthma_inhaled_medications, index_date, # inhaled medications
            where = medications.date.is_on_or_between(medication_date, index_date)))
    )
)

# identify whether patient had COPD which has been resolved
copd_res = (case(
    # has a resolution code
    when(last_prior_event(codelists.copd_resolved_codelist, index_date).date
    # which is dated after the latest diagnosis code
    .is_on_or_after(last_prior_event(codelists.copd_codelist, index_date).date))
    .then(True),
    # has a resolution code
    when(last_prior_event(codelists.copd_resolved_codelist, index_date).date
    # which is dated after the latest QoF code
    .is_on_or_after(last_prior_event(codelists.copd_qof_codelist, index_date).date))
    .then(True),
    otherwise = False)
)

# identify whether patient has COPD
dataset.copd = (case(
    when(
        (
            # has a copd diagnosis code
            (has_prior_event(codelists.copd_codelist, index_date)) 
            # or has a copd review code
            |(has_prior_event(codelists.copd_qof_codelist, index_date))
        )
        # and does not have COPD which has already been resolved
        & (~copd_res)
    )
    .then(True),
    otherwise = False)
)

## define patient medication information to extract

# define the interval for inhalers for each year of study
med_starts, med_ends = med_years(index_date, end_date, 2)   

# number of inhaler prescriptions in year 1 of study
dataset.salbutamol_quantity_y1 = (
    medications.where(medications.dmd_code.is_in(codelists.salbutamol))
    .where(medications.date.is_on_or_between(med_starts[1], med_ends[1]))
    .count_for_patient()
)

# number of inhaler prescriptions in year 2 of study
dataset.salbutamol_quantity_y2 = (
    medications.where(medications.dmd_code.is_in(codelists.salbutamol))
    .where(medications.date.is_on_or_between(med_starts[2], med_ends[2]))
    .count_for_patient()
)

## get information for censoring

# date of death
dataset.death_date = (case(
    when(ons_deaths.date.is_not_null()).then(ons_deaths.date),
    when(ons_deaths.date.is_null() & patients.date_of_death.is_not_null()).then(patients.date_of_death),
    otherwise = None)
)

# date of derigstration
dataset.deregistration_date = practice_registrations.for_patient_on(index_date).end_date

# define the size of a dummy population
dataset.configure_dummy_data(
    population_size = 100, timeout = 1000, 
    additional_population_constraint = (index_date < dataset.death_date) & (inhaler_prescribed)
) 
