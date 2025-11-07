import astropy.units as u
import numpy as np
import pytest
from madcubapy.io.madcubamap import MadcubaMap
from madcubapy.coordinates.offsets import get_angular_offset_points
from madcubapy.coordinates.offsets import get_physical_offset_points
from madcubapy.coordinates.offsets import get_angular_separation
from madcubapy.coordinates.offsets import get_physical_separation

@pytest.fixture
def example_madcuba_map():
    # Create and return a Map instance to be used in tests
    return MadcubaMap.read(
        "examples/data/IRAS16293_SO_2-1_moment0_madcuba.fits"
    )

def test_get_angular_offset_points(example_madcuba_map):
    # Test a specific array of points
    points = np.array([[120, 250], [140, 250], [160,250], [180,250]])
    point_B = (370, 300)
    points_angle = get_angular_offset_points(
        points, point_B, example_madcuba_map)
    assert np.allclose(
        points_angle,
        np.array([[0.01597222, -0.00319444],
                  [0.01469444, -0.00319444],
                  [0.01341667, -0.00319444],
                  [0.01213889, -0.00319444]]) * u.deg
    )

def test_get_physical_offset_points(example_madcuba_map):
    # Test a specific array of points
    points = np.array([[120, 250], [140, 250], [160,250], [180,250]])
    point_B = (370, 300)
    distance = 141 * u.pc
    points_physical = get_physical_offset_points(
        points, point_B, example_madcuba_map, distance)
    assert np.allclose(
        points_physical,
        np.array([[8107.50002507, -1621.50000501],
                  [7458.90002306, -1621.50000501],
                  [6810.30002106, -1621.50000501],
                  [6161.70001905, -1621.50000501]]) * u.au
    )

def test_get_angular_separation(example_madcuba_map):
    # Test a specific array of points
    points = np.array([[120, 250], [140, 250], [160,250], [180,250]])
    point_B = (370, 300)
    separation_angle = get_angular_separation(
        points, point_B, example_madcuba_map)
    assert np.allclose(
        separation_angle,
        np.array([0.01628853, 0.01503766, 0.01379172, 0.01255218]) * u.deg
    )

def test_get_physical_separation(example_madcuba_map):
    # Test a specific array of points
    points = np.array([[120, 250], [140, 250], [160,250], [180,250]])
    point_B = (370, 300)
    distance = 141 * u.pc
    separation_physical = get_physical_separation(
        points, point_B, example_madcuba_map, distance)
    assert np.allclose(
        separation_physical,
        np.array([8268.06016686,
                  7633.11547275,
                  7000.67487055,
                  6371.48408074]) * u.au
    )
