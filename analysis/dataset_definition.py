# import the necessary ehrQL functionalities
from ehrql import create_dataset, months, years, case, when, minimum_of, weeks

# import the necessary tables from TPP
from ehrql.tables.tpp import (
    patients, medications,
    clinical_events,
    ons_deaths,
    practice_registrations,
    addresses 
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

# Stub code to let us use the `check()` function before we've actually written it
try:
    from ehrql import check
except ImportError:

    def check(*args, **kwargs):
        pass


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

# define patients status: alive/dead: use ONS record if present, otherwise use GP record
death_date = ons_deaths.date.when_null_then(patients.date_of_death)
was_alive = death_date.is_after(index_date) | death_date.is_null()

# define the population of interest for study
dataset.define_population(
    registered_patients
    & age_of_interest
    & sex_known
    & inhaler_prescribed
    & was_alive
)

# configure the dummy data
dataset.configure_dummy_data(
    # requiring 250 patients matching the above define_population constraints
    population_size = 250
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

# patient IMD - from the LSOA associated with their address
dataset.imd_quintile = addresses.for_patient_on(index_date).imd_quintile

## get information for censoring

# date of death
dataset.death_date = (case(
    when(ons_deaths.date.is_not_null())
    .then(ons_deaths.date),
    when((ons_deaths.date.is_null()) & (patients.date_of_death.is_not_null()))
    .then(patients.date_of_death),
    otherwise = None)
)

# date of derigstration
dataset.deregistration_date = practice_registrations.for_patient_on(index_date).end_date

# define censoring date - earliest of death, deregistration or end of study period
dataset.censor_date = minimum_of(dataset.death_date, dataset.deregistration_date, end_date)

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

check(
    query=copd_res,
    given={
        clinical_events: [
            # COPD resolved
            {
                "date": index_date - years(2),
                "snomedct_code": codelists.copd_resolved_codelist[0],
            },
            # Has COPD code after resolved code
            {
                "date": index_date - years(1),
                "snomedct_code": codelists.copd_codelist[0],
            },
        ],
    },
    expect=False,
)

check(
    query=copd_res,
    given={
        clinical_events: [
            # COPD resolved
            {
                "date": index_date - years(2),
                "snomedct_code": codelists.copd_resolved_codelist[0],
            },
            # Has QoF COPD review code after resolved code
            {
                "date": index_date - years(1),
                "snomedct_code": codelists.copd_qof_codelist[0],
            },
        ],
    },
    expect=False,
)

check(
    query=copd_res,
    given={
        clinical_events: [
            {
                "date": index_date - years(3),
                "snomedct_code": codelists.copd_codelist[0],
            },
            {
                "date": index_date - years(2),
                "snomedct_code": codelists.copd_qof_codelist[0],
            },
            # Resolved code comes after previous COPD codes
            {
                "date": index_date - years(1),
                "snomedct_code": codelists.copd_resolved_codelist[0],
            },
        ],
    },
    expect=True,
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

check(
    query=dataset.copd,
    given={
        clinical_events: [
            # No relevant codes
            {
                "date": index_date - years(1),
                "snomedct_code": "1234567890",
            },
        ],
    },
    expect=False,
)

check(
    query=dataset.copd,
    given={
        clinical_events: [
            # Has COPD code
            {
                "date": index_date - years(1),
                "snomedct_code": codelists.copd_codelist[0],
            },
        ],
    },
    expect=True,
)

check(
    query=dataset.copd,
    given={
        clinical_events: [
            # Has COPD code
            {
                "date": index_date - years(2),
                "snomedct_code": codelists.copd_codelist[0],
            },
            # But since resolved
            {
                "date": index_date - years(1),
                "snomedct_code": codelists.copd_resolved_codelist[0],
            },
        ],
    },
    expect=False,
)


## define patient medication information to extract

# define the interval for inhalers for each year of study
med_starts, med_ends = med_years(index_date, end_date, 2)   

# number of inhaler prescriptions in year 1 of study
dataset.salbutamol_quantity_y1 = (
    medications.where(medications.dmd_code.is_in(codelists.salbutamol))
    .where(medications.date.is_on_or_between(
        # only find medications up until censoring - if it occurs
        med_starts[1], minimum_of(med_ends[1], dataset.censor_date)
    )
    ).count_for_patient()
)

check(
    query=dataset.salbutamol_quantity_y1,
    given={
        medications: [
            # Before year start
            {"dmd_code": codelists.salbutamol[0], "date": med_starts[1] - weeks(6)},
            # Should be counted
            {"dmd_code": codelists.salbutamol[0], "date": med_starts[1] + weeks(6)},
            # Wrong drug
            {"dmd_code": "123456789", "date": med_starts[1] + weeks(6)},
            # Should be counted
            {"dmd_code": codelists.salbutamol[0], "date": med_ends[1] - weeks(6)},
            # After year end
            {"dmd_code": codelists.salbutamol[0], "date": med_ends[1] + weeks(6)},
        ],
    },
    expect=2,
)


# number of inhaler prescriptions in year 2 of study
dataset.salbutamol_quantity_y2 = (case(
    # if censored in year 1, then inhaler quanitity should be null
    when(minimum_of(med_ends[1], dataset.censor_date) != med_ends[1])
    .then(None),
    otherwise = (
        medications.where(medications.dmd_code.is_in(codelists.salbutamol))
        .where(medications.date.is_on_or_between(
            # again, only find medications up until censoring - if it occurs
            med_starts[2], minimum_of(med_ends[2], dataset.censor_date)
        )
        ).count_for_patient()
    )
))
check(
    query=dataset.salbutamol_quantity_y2,
    given={
        # Censored in year 1
        patients: [
            {"date_of_death": med_ends[1] - weeks(6)},
        ],
        medications: [
            # Year 2 medication (implausible given death but it tests the censoring logic!)
            {"dmd_code": codelists.salbutamol[0], "date": med_starts[2] + weeks(6)},
        ],
    },
    expect=None,
)

check(
    query=dataset.salbutamol_quantity_y2,
    given={
        # Censored before end of year 2
        patients: [
            {"date_of_death": med_ends[2] - weeks(6)},
        ],
        medications: [
            # Should be counted
            {"dmd_code": codelists.salbutamol[0], "date": med_starts[2] + weeks(6)},
            # After censoring date
            {"dmd_code": codelists.salbutamol[0], "date": med_ends[2] - weeks(3)},
        ],
    },
    expect=1,
)
