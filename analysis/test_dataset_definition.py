from datetime import date
from dataset_definition import dataset # import the dataset generation mechanism

# here we create three patients with which we can test our dataset definition
# they have various values of age, sex, asthma/copd diagnosis and inhaler quantity

test_data = {
    # Expected in population with some quantity of inhalers each year
    1: {
        "practice_registrations": [
            {
                "start_date": date(2017, 2, 13),
                "end_date": None
            }
       ],
        "patients": [
            {
                "date_of_birth": date(1946, 2, 1),
                "sex": "female"
            }
        ],
        "clinical_events": [
            #Ethnicity
            {
                "date": date(2017, 2, 13),
                "snomedct_code": "733446001"
            },
            # Asthma diagnosis
            {
                "date": date(2012, 8, 12),
                "snomedct_code": "195967001",
            }
        ],
        "medications": [
            # Relevant Asthma Steroid Medication
            {
                "date": date(2019, 12, 1),
                "dmd_code": "10983311000001107"
            },

            # First year of inhalers
            {
                "date": date(2020, 4, 1),
                "dmd_code" : "3214311000001108",
            },
            {
                "date": date(2020, 6, 6),
                "dmd_code" : "3214311000001108",
            },
            {
                "date": date(2020, 8, 12),
                "dmd_code" : "3214311000001108",
            },
            {
                "date": date(2020, 10, 1),
                "dmd_code" : "3214311000001108",
            },
            {
                "date": date(2021, 2, 1),
                "dmd_code" : "3214311000001108",
            },
            # Second year of inhalers
            {
                "date": date(2021, 4, 1),
                "dmd_code" : "3214311000001108",
            },
            {
                "date": date(2021, 5, 1),
                "dmd_code" : "3214311000001108",
            },
            {
                "date": date(2021, 6, 6),
                "dmd_code" : "3214311000001108",
            },
            {
                "date": date(2021, 8, 12),
                "dmd_code" : "3214311000001108",
            },
            {
                "date": date(2021, 10, 1),
                "dmd_code" : "3214311000001108",
            },
            {
                "date": date(2021, 12, 1),
                "dmd_code" : "3214311000001108",
            },
            {
                "date": date(2022, 1, 15),
                "dmd_code" : "3214311000001108",
            },
            {
                "date": date(2022, 2, 21),
                "dmd_code" : "3214311000001108",
            },
        ],
        "expected_in_population": True,
        "expected_columns": {
            "age": 74,
            "sex": "female",
            "latest_ethnicity_group": "1", # White
            "asthma": True, # Asthma diagnosis
            "copd": False, # COPD diagnosis not present
            "salbutamol_quantity_y1": 5, # First year of inhalers
            "salbutamol_quantity_y2": 8 # Second year of inhalers
        },
    },
    # Expected in population without asthma or COPD but with an inhaler in first year
    2: {
        "practice_registrations": [
            {
                "start_date": date(2019, 8, 10),
                "end_date": date(2021, 1, 1)
            }
       ],
        "patients": [
            {
                "date_of_birth": date(1980, 1, 1),
                "sex": "male"
            }
        ],
        "clinical_events": [
            # Ethnicity
            {
                "date": date(2019, 8, 10),
                "snomedct_code": "85371009"
            }
        ],
        "medications": [
            {
                "date": date(2020, 6, 21),
                "dmd_code" : "3214311000001108", 
            }
        ],
        "expected_in_population": True,
        "expected_columns": {
            "age": 40,
            "sex": "male",
            "latest_ethnicity_group": "4", # Black or Black British
            "asthma": False,
            "copd": False,
            "salbutamol_quantity_y1": 1, # First year of inhalers
            "salbutamol_quantity_y2": 0 # Second year of inhalers
        },
    },
    # Not expected in population
    3: {
        "practice_registrations": [
            {
                "start_date": date(2010, 12, 10),
                "end_date": None
            }
       ],
        "patients": [
            {
                "date_of_birth": date(2010, 1, 1),
                "sex": "female"
            }
        ],
        "clinical_events": [],
        "medications": [],
        "expected_in_population": False,
    },
}
