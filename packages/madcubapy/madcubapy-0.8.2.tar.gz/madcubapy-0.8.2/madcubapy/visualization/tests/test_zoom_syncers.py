from astropy.visualization.wcsaxes import WCSAxes
from astropy.wcs import WCS
from madcubapy.io import MadcubaMap
from madcubapy.visualization import add_wcs_axes
from madcubapy.visualization import copy_zoom_axes
from madcubapy.visualization import copy_zoom_fitsmap
from madcubapy.visualization import sync_zoom
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import numpy as np
import pytest

@pytest.fixture
def example_madcuba_map_tm1():
    # Create and return a Map instance to be used in tests
    return MadcubaMap.read(
        "examples/data/IRAS16293_SO2a_tm1.fits"
    )

@pytest.fixture
def example_madcuba_map_tm2():
    # Create and return a Map instance to be used in tests
    return MadcubaMap.read(
        "examples/data/IRAS16293_SO2a_tm2.fits"
    )


@pytest.mark.parametrize("invalid_input", [
    None, 123, "string", [], {}, set(), object(), plt.figure().add_subplot(111)
])
def test_sync_zoom_incorrent_types(invalid_input):
    with pytest.raises(TypeError):
        sync_zoom(invalid_input)


def test_limits_results(example_madcuba_map_tm1, example_madcuba_map_tm2):
    # Fitsmap
    xlim1 = (200, 350)
    ylim1 = (200, 350)
    xlim_fitsmap, ylim_fitsmap = copy_zoom_fitsmap(
        ref_fitsmap=example_madcuba_map_tm1,
        target_fitsmap=example_madcuba_map_tm2,
        x_lim=(xlim1), 
        y_lim=(ylim1)
    )
    # Axes
    fig1 = plt.figure(figsize=(3,2))
    ax1, img1 = add_wcs_axes(fig1, 1, 2, 1, fitsmap=example_madcuba_map_tm1)
    ax2, img2 = add_wcs_axes(fig1, 1, 2, 2, fitsmap=example_madcuba_map_tm2)
    # Copy zoom
    ax1.set_xlim(xlim1)
    ax1.set_ylim(ylim1)
    copy_zoom_axes(ref_ax=ax1, target_ax=ax2)
    xlim_axes = ax2.get_xlim()
    ylim_axes = ax2.get_ylim()
    # Sync zoom
    fig2 = plt.figure(figsize=(3,2))
    ax3, img3 = add_wcs_axes(fig2, 1, 3, 1, fitsmap=example_madcuba_map_tm1)
    ax4, img4 = add_wcs_axes(fig2, 1, 3, 2, fitsmap=example_madcuba_map_tm2)
    # Sync zoom
    sync_zoom(ax3, ax4)
    ax3.set_xlim(xlim1)
    xlim_sync = ax4.get_xlim()
    ylim_sync = ax4.get_ylim()
    
    np.testing.assert_allclose(xlim_fitsmap, xlim_axes)
    np.testing.assert_allclose(xlim_fitsmap, xlim_sync)
