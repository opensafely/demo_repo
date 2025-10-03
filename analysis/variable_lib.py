from ehrql.tables.tpp import practice_registrations, clinical_events # import necessary tables from TPP

# create a function to extract a continuous registration period
def _registrations_overlapping_period(start_date, end_date):
    regs = practice_registrations
    return regs.where(
        regs.start_date.is_on_or_before(start_date)
        & (regs.end_date.is_after(end_date) | regs.end_date.is_null())
    )

# create a function to return when a patient has a continous registration for a defined interval
def has_a_continuous_practice_registration_spanning(start_date, end_date):
    return _registrations_overlapping_period(start_date, end_date).exists_for_patient()

#events occurring before index date
def prior_events(index_date):
  return (
      clinical_events.where(clinical_events.date.is_on_or_before(index_date))
)

#query prior_events for existence of event-in-codelist
def has_prior_event(codelist, index_date, where = True):
    return (
        prior_events(index_date).where(where)
        .where(prior_events(index_date).snomedct_code.is_in(codelist))
        .exists_for_patient()
    )