from astropy.table import Table
import astropy.units as u
from astropy.utils.diff import report_diff_values
import numpy as np
import pytest
from madcubapy.io.slim import import_molecular_parameters_table
from madcubapy.io.slim import format_molecular_parameters_columns
from madcubapy.io.slim import output_latex_molecular_parameters_table

@pytest.fixture
def example_ascii_table():
    return import_molecular_parameters_table("examples/data/molecular_params_ascii.txt")

@pytest.fixture
def example_csv_table():
    return import_molecular_parameters_table("examples/data/molecular_params_csv.csv",
                                             format='csv')

@pytest.mark.parametrize("column", ['Width', 'Velocity', 'Tex/Te', 'N/EM'])
def test_correct_initialization(example_ascii_table, example_csv_table, column):
    assert np.array_equal(example_ascii_table[column],
                          example_csv_table[column],
                          equal_nan=True)

@pytest.mark.parametrize("column, formatted_column", [
    ('Width', 'formatted Width'),
    ('Velocity', 'formatted Velocity'),
    ('Tex/Te', 'formatted Tex/Te'),
    ('N/EM', 'formatted N/EM')
])
def test_correct_formatting(example_ascii_table, example_csv_table, column, formatted_column):
    # Apply the formatting function to both tables
    formatted_ascii = format_molecular_parameters_columns(example_ascii_table)
    formatted_csv = format_molecular_parameters_columns(example_csv_table)
    # Perform the assertion on formatted columns
    assert np.array_equal(formatted_ascii[formatted_column],
                          formatted_csv[formatted_column])
