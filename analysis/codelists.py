# import ehrql function for importing codelists
from ehrql import codelist_from_csv

# asthma diagnosis
ast_diag = codelist_from_csv(
    "codelists/pincer-ast.csv",
    column = "code"
)

# copd diagnosis
copd_diag = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-copd_cod.csv",
    column = "code"
)

# salbutamol prescribing
salbutamol = codelist_from_csv(
    "codelists/opensafely-asthma-inhaler-salbutamol-medication.csv",
    column = "code"
)

# asthma review
ast_review = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-copd_cod.csv",
    column = "code"
)

# potentially add
# # ethnicity codes
# ethnicity_codes = codelist_from_csv(
#   "codelists/opensafely-ethnicity-snomed-0removed.csv",
#   column = "snomedcode",
#   category_column = "Grouping_6",
# )