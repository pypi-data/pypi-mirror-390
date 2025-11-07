import matplotlib.pyplot as plt
import numpy as np
import pytest
from madcubapy.coordinates import transform_coords_axes
from madcubapy.coordinates import transform_coords_fitsmap
from madcubapy.io.madcubamap import MadcubaMap
from madcubapy.visualization import add_wcs_axes

@pytest.fixture
def example_madcuba_map_m0():
    # Create and return a Map instance to be used in tests
    return MadcubaMap.read(
        "examples/data/IRAS16293_SO_2-1_moment0_madcuba.fits"
    )

@pytest.fixture
def example_madcuba_map_cont():
    # Create and return a Map instance to be used in tests
    return MadcubaMap.read(
        "examples/data/IRAS16293_band_7_tm2_cont.fits"
    )


def test_both_transforms(example_madcuba_map_m0, example_madcuba_map_cont):
    # Test if both functions yield the same points for the same plotted maps
    # Create fig
    fig = plt.figure(figsize=(3,3))
    ax1, img = add_wcs_axes(fig, 1, 2, 1, fitsmap=example_madcuba_map_m0)
    ax2, img = add_wcs_axes(fig, 1, 2, 2, fitsmap=example_madcuba_map_cont)
    # Original points
    points = np.array([[300, 350], [300, 400], [300, 450]])
    # Transform points from ccddata
    new_points_ccddata = transform_coords_fitsmap(
        ref_fitsmap=example_madcuba_map_m0,
        target_fitsmap=example_madcuba_map_cont,
        points=points
    )
    # Transform points from axes
    new_points_axes = transform_coords_axes(
        ref_ax=ax1,
        target_ax=ax2,
        points=points
    )
    assert np.allclose(new_points_ccddata, new_points_axes)
