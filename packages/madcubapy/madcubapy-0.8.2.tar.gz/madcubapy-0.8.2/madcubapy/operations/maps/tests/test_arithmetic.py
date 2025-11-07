import numpy as np
import pytest
from madcubapy.io.madcubamap import MadcubaMap
from madcubapy.operations.maps import stack_maps

@pytest.fixture
def example_madcuba_map():
    # Create and return a Map instance to be used in tests
    return MadcubaMap.read(
        "examples/data/IRAS16293_SO_2-1_moment0_madcuba.fits"
    )

def test_stack_maps(example_madcuba_map):
    sum_map = stack_maps(example_madcuba_map, example_madcuba_map)
    assert np.array_equal(sum_map.data, example_madcuba_map.data*2, equal_nan=True)
    assert (sum_map.hist[-1]["Macro"] ==
        "//PYTHON: Stack maps. Files: 'IRAS16293_SO_2-1_moment0_madcuba.fits', 'IRAS16293_SO_2-1_moment0_madcuba.fits'"
    )
    assert sum_map.unit is not None
    assert sum_map.unit == example_madcuba_map.unit
