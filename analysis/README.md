# Analysis folder

The 'analysis' folder is one which is created automatically when you create a project from the OpenSAFELY template. The folder should be used for the `dataset_definition.py` file, in addition to any processing and analytical files. Additional file structuring with further folders may be useful for larger projects.

# What have we included?

In this folder are three definitions querying the TPP database:

- `dataset_definition.py` which is the query for getting study information
- `inclusion_definition.py` which is the query for getting information for patient inclusion/exclusion numbers (e.g. for a [patient inclusion flow chart](https://www.nature.com/articles/s41586-020-2521-4/figures/1))
- `measures_definition.py` which is a query which gets information about ratios of measures of interest for defined populations

There are additional files which are used for these definitions:

- `codelists.py` which is a script which importants necessary codelists and assigns them to objects which can be called; this is common convention aross OpenSAFELY projects but not a requirement
- `variable_lib.py` which is a script which variables which are used within the queries, this is a way of keeping your queuries cleaner and easier to navigate - you can also use the variables across multiple query files
- `test_dataset_definition.py` which is a script which contains three example patients which we define the information for, and therefore know whether we expect them to be in our dataset; this can then be used in [assurance testing](https://docs.opensafely.org/ehrql/how-to/test-dataset-definition/)

There are then files which are used downstream from the queries:

- `inclusion_processing.R` which is a script which can be used to aggregate the inclusion/exclusion information for release
- `redaction.R` which is a script containing a function to be used for statistical disclosure control
- `data_processing.R` which is a script which reformats the data into how it will be used for analysis
- `table1.R` which is a script which aggregates information about the study population
- `model.R` which is a script in which the analysis is performed
- `deciles_charts.py` which is a script which can be used to create decile charts, and the underlying tables, for measures