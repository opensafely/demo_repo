# import the necessary ehrQL functionalities
from ehrql import create_measures, years, case, when, months
# import the measures functionality
from ehrql.measures import INTERVAL
# import the necessary tables from TPP
from ehrql.tables.tpp import patients, medications, ons_deaths
# import variables which are defined in a separate file
from variable_lib import (
    has_a_continuous_practice_registration_spanning,
    has_prior_event,
    has_prior_meds,
    last_prior_event
)
# import the codelists defined in a separate file
import codelists

# define start of follow up period
index_date = "2020-03-01" 

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

# define population alive at start of interval of interest
was_alive = (
    (ons_deaths.date.is_after(INTERVAL.start_date))| # first using ONS deaths (best source)
    (ons_deaths.date.is_null())|
    (patients.date_of_death.is_after(INTERVAL.start_date))| # then using patient table
    (patients.date_of_death.is_null())
)

# define the interevals to be used for the measures
intervals = years(2).starting_on(index_date)

# create ehrQL generated dummy measures
measures = create_measures()

# define the size of a dummy population
measures.configure_dummy_data(population_size = 250)

# restrict prescriptions to those within intervals
prescriptions_in_interval = medications.where(medications.date.is_during(INTERVAL))

# now subset these to only be those for salbutamol
relevant_prescriptions_in_interval = (
    prescriptions_in_interval.where(medications.dmd_code.is_in(codelists.salbutamol))
)

# define the patients who fit this measure
had_prescription = relevant_prescriptions_in_interval.exists_for_patient()

# define medication date to find recent prescriptions
medication_date = index_date - years(1)

# get the age of particpants
age = patients.age_on(index_date)

# classify ages
age_group = (case(
    when((age >= 12) & (age < 18)).then("adolescent"),
    when((age >= 18) & (age < 65)).then("adult"),
    when((age >= 65) & (age <= 100)).then("older_adult"),
    otherwise = "unknown"
))

# define the measure of interest: those with salbutamol inhalers prescribed, by age group
measures.define_measure(
    "had_prescription_by_age",
    numerator = (
        had_prescription
        & age_of_interest
        & sex_known
        & was_alive
        & had_prescription
    ),
    denominator = (
        registered_patients
        & age_of_interest
        & sex_known
        & was_alive
    ),
    group_by = {"age_group": age_group},
    intervals = intervals,
)

# define the quantity of prescriptions of salbutamol in interval
salbutamol_quantity = (
    relevant_prescriptions_in_interval.count_for_patient()
)

# define the patients who received multiple prescriptions in the interval
had_multiple = (case(
    when(salbutamol_quantity > 1).then(True),
    otherwise = False
))

# define the measure of interest: those with multiple salbutamol inhalers prescribed, by age group
measures.define_measure(
    "had_multiple_inhalers_by_age",
    numerator = (
        had_multiple
        & age_of_interest
        & sex_known
        & was_alive
        & had_prescription
    ),
    denominator = (
        registered_patients
        & age_of_interest
        & sex_known
        & was_alive
    ),
    group_by = {"age_group": age_group},
    intervals = intervals,
)
## define medication date to find recent prescriptions
medication_date = index_date - years(1)

# identify whether patient is asthmatic
asthma = (
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
copd = (case(
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

# define whether the patient has asthma, copd, or none of the conditions of interest
has_asthma_copd = (case(
    when(asthma).then(True),
    when(copd).then(True),
    otherwise = False
))

# define the measure of interest: those with asthma or copd, by age group
measures.define_measure(
    "has_asthma_copd_by_age",
    numerator = (
        has_asthma_copd
        & age_of_interest
        & sex_known
        & was_alive
        & had_prescription
    ),
    denominator = (
        registered_patients
        & age_of_interest
        & sex_known
        & was_alive
    ),
    group_by = {"age_group": age_group},
    intervals = intervals,
)
