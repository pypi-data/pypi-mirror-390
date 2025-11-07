import astropy.units as u
import numpy as np
import pytest
from madcubapy.io.madcubamap import MadcubaMap
from madcubapy.coordinates.conversions import python_to_fits
from madcubapy.coordinates.conversions import fits_to_python
from madcubapy.coordinates.conversions import pixel_to_world
from madcubapy.coordinates.conversions import world_to_pixel
from madcubapy.coordinates.conversions import pixels_to_angle
from madcubapy.coordinates.conversions import angle_to_pixels

@pytest.fixture
def example_map():
    # Create and return a Map instance to be used in tests
    return MadcubaMap.read(
        "examples/data/IRAS16293_SO_2-1_moment0_madcuba.fits"
    )

def test_pixel_conversion_results():
    point = (1, 1)
    assert np.all(fits_to_python(point) == (0, 0))
    assert np.all(python_to_fits(point) == (2, 2))
    assert np.all(python_to_fits(fits_to_python(point)) == point)

def test_pixel_conversion_invalid_type():
    with pytest.raises(ValueError):
        fits_to_python(1)
    with pytest.raises(ValueError):
        python_to_fits(1)
    with pytest.raises(ValueError):
        fits_to_python(1.2)
    with pytest.raises(ValueError):
        python_to_fits(1.2)
    with pytest.raises(ValueError):
        fits_to_python("(1, 2)")
    with pytest.raises(ValueError):
        python_to_fits("(1, 2)")

def test_pixel_conversion_invalid_shape():
    with pytest.raises(ValueError):
        fits_to_python(np.array([1, 2, 3]))
    with pytest.raises(ValueError):
        python_to_fits(np.array([1, 2, 3]))
    with pytest.raises(ValueError):
        fits_to_python(np.array([[1, 2, 3], [3, 4, 5]]))
    with pytest.raises(ValueError):
        python_to_fits(np.array([[1, 2, 3], [3, 4, 5]]))
    with pytest.raises(ValueError):
        fits_to_python(np.array([[1, 2], 3]))
    with pytest.raises(ValueError):
        python_to_fits(np.array([[1, 2], 3]))

# If I test fails it is easier to find by variable name than in one huge,
# or several smaller parametrized test definitions.
def test_world_to_pixel_conversion_results(example_map):
    # Expected results
    result_one_point = np.array([180.17396311, 188.00006171])
    result_two_points = np.array([
        [180.17396311, 188.00006171],
        [180.17396311, 188.00006171]
    ])
    # Simple tuple
    world_simple_tuple = (248.09732664, -24.47798325)
    assert np.allclose(
        world_to_pixel(world_simple_tuple, example_map),
        result_one_point,
    )
    # Simple list
    world_simple_list = [248.09732664, -24.47798325]
    assert np.allclose(
        world_to_pixel(world_simple_list, example_map),
        result_one_point,
    )
    # Simple numpy array
    world_simple_array = np.array([248.09732664, -24.47798325])
    assert np.allclose(
        world_to_pixel(world_simple_array, example_map),
        result_one_point
    )
    # Quantity from array
    world_quantity_from_array = world_simple_array * u.deg
    assert np.allclose(
        world_to_pixel(world_quantity_from_array, example_map),
        result_one_point
    )
    # 2D tuple
    world_2D_tuple = (
        (248.09732664, -24.47798325),
        (248.09732664, -24.47798325),
    )
    assert np.allclose(
        world_to_pixel(world_2D_tuple, example_map),
        result_two_points
    )
    # 2D list
    world_2D_list = [
        [248.09732664, -24.47798325],
        [248.09732664, -24.47798325],
    ]
    assert np.allclose(
        world_to_pixel(world_2D_list, example_map),
        result_two_points
    )
    # 2D array
    world_2D_array = np.array([
        [248.09732664, -24.47798325],
        [248.09732664, -24.47798325],
    ])
    assert np.allclose(
        world_to_pixel(world_2D_array, example_map),
        result_two_points
    )
    # Quantity from 2D array
    world_quantity_from_2D_array = np.array([
        [248.09732664, -24.47798325],
        [248.09732664, -24.47798325],
    ]) * u.deg
    assert np.allclose(
        world_to_pixel(world_quantity_from_2D_array, example_map),
        result_two_points
    )
    # 2D list of Quantities
    world_2D_list_of_quantities = [
        ([248.09732664, -24.47798325] * u.deg).to(u.arcmin),
        [248.09732664, -24.47798325] * u.deg
    ]
    assert np.allclose(
        world_to_pixel(world_2D_list_of_quantities, example_map),
        result_two_points    
    )
    # 2D list of single quantities
    world_2D_list_of_single_quantities = [
        [248.09732664 * u.deg, (-24.47798325 * u.deg).to(u.arcmin)],
        [248.09732664 * u.deg, -24.47798325 * u.deg]
    ]
    assert np.allclose(
        world_to_pixel(world_2D_list_of_single_quantities, example_map),
        result_two_points    
    )
    # 2D list of arrays
    world_2D_list_of_arrays = [
        np.array([248.09732664, -24.47798325]),
        np.array([248.09732664, -24.47798325])
    ]
    assert np.allclose(
        world_to_pixel(world_2D_list_of_arrays, example_map),
        result_two_points
    )
    # Mix different quantity units
    world_mix_different_units = [
        np.array([248.09732664, -24.47798325]) * u.deg,
        (np.array([248.09732664, -24.47798325]) * u.deg).to(u.arcmin)
    ]
    assert np.allclose(
        world_to_pixel(world_mix_different_units, example_map),
        result_two_points
    )

def test_world_to_pixel_conversion_invalid_units(example_map):
    with pytest.raises(ValueError):
        world_to_pixel(np.array([248, -24]) * u.s, example_map)
    with pytest.raises(ValueError):
        world_to_pixel(np.array([248, -24]) * u.Jy, example_map)
    with pytest.raises(ValueError):
        world_to_pixel(
            [np.array([248, -24]) * u.deg,
             np.array([249, -24]) * u.m],
            example_map
        )
    with pytest.raises(ValueError):
        world_to_pixel(
            [np.array([248, -24]) * u.pix,
             np.array([249, -24]) * u.deg],
            example_map
        )

def test_world_to_pixel_conversion_invalid_type(example_map):
    # Invalid single type
    world_invalid_type = 3
    with pytest.raises(ValueError):
        world_to_pixel(world_invalid_type, example_map)
    # List of different types
    world_2D_list_one_quantity = [
        np.array([248.09732664, -24.47798325]) * u.deg,
        np.array([248.09732664, -24.47798325])
    ]
    with pytest.raises(ValueError):
        world_to_pixel(world_2D_list_one_quantity, example_map)
    # List of lists of lists
    world_3D_list = [[[1, 2]]]
    with pytest.raises(ValueError):
        world_to_pixel(world_3D_list, example_map)

# If I test fails it is easier to find by variable name than in one huge,
# or several smaller parametrized test definitions.
def test_pixel_to_world_conversion_results(example_map):
    # Expected results
    result_one_point = np.array([248.09732664, -24.47798325]) * u.deg
    result_two_points = np.array([
        [248.09732664, -24.47798325],
        [248.09732664, -24.47798325]
    ]) * u.deg
    # Simple tuple
    pixel_simple_tuple = (180.17396311, 188.00006171)
    assert np.allclose(
        pixel_to_world(pixel_simple_tuple, example_map),
        result_one_point,
    )
    # Simple list
    pixel_simple_list = [180.17396311, 188.00006171]
    assert np.allclose(
        pixel_to_world(pixel_simple_list, example_map),
        result_one_point,
    )
    # Simple numpy array
    pixel_simple_array = np.array([180.17396311, 188.00006171])
    assert np.allclose(
        pixel_to_world(pixel_simple_array, example_map),
        result_one_point
    )
    # Quantity from array
    pixel_quantity_from_array = pixel_simple_array * u.pix
    assert np.allclose(
        pixel_to_world(pixel_quantity_from_array, example_map),
        result_one_point
    )
    # 2D tuple
    pixel_2D_tuple = (
        (180.17396311, 188.00006171),
        (180.17396311, 188.00006171),
    )
    assert np.allclose(
        pixel_to_world(pixel_2D_tuple, example_map),
        result_two_points
    )
    # 2D list
    pixel_2D_list = [
        [180.17396311, 188.00006171],
        [180.17396311, 188.00006171],
    ]
    assert np.allclose(
        pixel_to_world(pixel_2D_list, example_map),
        result_two_points
    )
    # 2D array
    pixel_2D_array = np.array([
        [180.17396311, 188.00006171],
        [180.17396311, 188.00006171],
    ])
    assert np.allclose(
        pixel_to_world(pixel_2D_array, example_map),
        result_two_points
    )
    # Quantity from 2D array
    pixel_quantity_from_2D_array = np.array([
        [180.17396311, 188.00006171],
        [180.17396311, 188.00006171],
    ]) * u.pix
    assert np.allclose(
        pixel_to_world(pixel_quantity_from_2D_array, example_map),
        result_two_points
    )
    # 2D list of Quantities
    pixel_2D_list_of_quantities = [
        [180.17396311, 188.00006171] * u.pix,
        [180.17396311, 188.00006171] * u.pix
    ]
    assert np.allclose(
        pixel_to_world(pixel_2D_list_of_quantities, example_map),
        result_two_points    
    )
    # 2D list of single quantities
    pixel_2D_list_of_single_quantities = [
        [180.17396311 * u.pix, 188.00006171 * u.pix],
        [180.17396311 * u.pix, 188.00006171 * u.pix]
    ]
    assert np.allclose(
        pixel_to_world(pixel_2D_list_of_single_quantities, example_map),
        result_two_points    
    )
    # 2D list of arrays
    pixel_2D_list_of_arrays = [
        np.array([180.17396311, 188.00006171]),
        np.array([180.17396311, 188.00006171])
    ]
    assert np.allclose(
        pixel_to_world(pixel_2D_list_of_arrays, example_map),
        result_two_points
    )
    # Mix no units with units
    pixel_mix_different_units = [
        np.array([180.17396311, 188.00006171]),
        np.array([180.17396311, 188.00006171]) * u.pix
    ]
    assert np.allclose(
        pixel_to_world(pixel_mix_different_units, example_map),
        result_two_points
    )

def test_pixel_to_world_conversion_invalid_units(example_map):
    with pytest.raises(ValueError):
        pixel_to_world(np.array([248, -24]) * u.deg, example_map)
    with pytest.raises(ValueError):
        pixel_to_world(np.array([248, -24]) * u.Jy, example_map)
    with pytest.raises(ValueError):
        pixel_to_world(
            [np.array([248, -24]) * u.deg,
             np.array([249, -24]) * u.arcsec],
            example_map
        )
    # Mix pix with other units
    with pytest.raises(ValueError):
        pixel_to_world(
            [np.array([248, -24]) * u.pix,
             np.array([249, -24]) * u.deg],
            example_map
        )

def test_pixel_to_world_conversion_invalid_type(example_map):
    # Invalid single type
    pixel_invalid_type = 3
    with pytest.raises(ValueError):
        pixel_to_world(pixel_invalid_type, example_map)
    # List of different types
    pixel_2D_list_one_quantity = [
        [248.09732664, -24.47798325],
        np.array([248.09732664, -24.47798325])
    ]
    with pytest.raises(ValueError):
        pixel_to_world(pixel_2D_list_one_quantity, example_map)
    # List of lists of lists
    pixel_3D_list = [[[1, 2]]]
    with pytest.raises(ValueError):
        pixel_to_world(pixel_3D_list, example_map)

# If I test fails it is easier to find by variable name than in one huge,
# or several smaller parametrized test definitions.
def test_angle_to_pixels_conversion_results(example_map):
    # Expected results
    result_one_length = np.array([4.34782607])
    result_two_lengths = np.array([8.69565215, 4.34782607])
    # Simple length no units, defaults to deg
    angle_simple = 1
    assert np.allclose(
        angle_to_pixels(angle_simple, example_map),
        15652.173864642871,
    )
    # Simple length quantity
    angle_simple_quantity = 1 * u.arcsec
    assert np.allclose(
        angle_to_pixels(angle_simple_quantity, example_map),
        result_one_length,
    )
    # Simple length quantity in pixels
    angle_simple_quantity_pix = 4.34782607 * u.pix
    assert np.allclose(
        angle_to_pixels(angle_simple_quantity_pix, example_map),
        result_one_length,
    )
    # Simple tuple of quantities
    angle_tuple_quantities = (2 * u.arcsec, 1 * u.arcsec)
    assert np.allclose(
        angle_to_pixels(angle_tuple_quantities, example_map),
        result_two_lengths,
    )
    # Simple list of quantities
    angle_list_quantities = [2 * u.arcsec, 1 * u.arcsec]
    assert np.allclose(
        angle_to_pixels(angle_list_quantities, example_map),
        result_two_lengths,
    )
    # Simple list of quantities mixing angular units
    angle_list_quantities_mix_units = [
        2 * u.arcsec,
        (1 * u.arcsec).to(u.deg)
    ]
    assert np.allclose(
        angle_to_pixels(angle_list_quantities_mix_units, example_map),
        result_two_lengths,
    )
    # Quantity of simple array, tuple, or list
    angle_quantity_array = np.array([2, 1])  * u.arcsec
    assert np.allclose(
        angle_to_pixels(angle_quantity_array, example_map),
        result_two_lengths,
    )

def test_angle_to_pixels_conversion_invalid_units(example_map):
    with pytest.raises(ValueError):
        angle_to_pixels(2 * u.s, example_map)
    with pytest.raises(ValueError):
        angle_to_pixels(2 * u.Jy, example_map)
    # Mix pix with other units
    with pytest.raises(ValueError):
        angle_to_pixels([2 * u.arcsec, 1 * u.pix], example_map)

def test_angle_to_pixels_conversion_invalid_type(example_map):
    # Invalid single type
    with pytest.raises(ValueError):
        angle_to_pixels("3", example_map)
    # List of different types
    with pytest.raises(ValueError):
        angle_to_pixels([1, "2"], example_map)
    # List of lists
    with pytest.raises(ValueError):
        angle_to_pixels([[1, 2]], example_map)







# If I test fails it is easier to find by variable name than in one huge,
# or several smaller parametrized test definitions.
def test_pixels_to_angle_conversion_results(example_map):
    # Expected results
    result_one_length = 1 * u.arcsec
    result_two_lengths = np.array([2, 1]) * u.arcsec
    # Simple length no units, defaults to pix
    pixels_simple = 4.34782607
    assert np.allclose(
        pixels_to_angle(pixels_simple, example_map),
        result_one_length,
    )
    # Simple length quantity in pixels
    pixels_simple_quantity = 4.34782607 * u.pix
    assert np.allclose(
        pixels_to_angle(pixels_simple_quantity, example_map),
        result_one_length,
    )
    # Simple tuple of quantities
    pixels_tuple_quantities = (8.69565215 * u.pix, 4.34782607 * u.pix)
    assert np.allclose(
        pixels_to_angle(pixels_tuple_quantities, example_map),
        result_two_lengths,
    )
    # Simple list of quantities
    pixels_list_quantities = [8.69565215 * u.pix, 4.34782607 * u.pix]
    assert np.allclose(
        pixels_to_angle(pixels_list_quantities, example_map),
        result_two_lengths,
    )
    # Quantity of simple array, tuple, or list
    pixels_quantity_array = np.array([8.69565215, 4.34782607])  * u.pix
    assert np.allclose(
        pixels_to_angle(pixels_quantity_array, example_map),
        result_two_lengths,
    )


def test_pixels_to_angle_conversion_invalid_units(example_map):
    with pytest.raises(ValueError):
        pixels_to_angle(2 * u.arcsec, example_map)
    with pytest.raises(ValueError):
        pixels_to_angle(2 * u.Jy, example_map)
    # Mix pix with other units
    with pytest.raises(ValueError):
        pixels_to_angle([2 * u.arcsec, 1 * u.pix], example_map)
    # Mix no units with units
    with pytest.raises(ValueError):
        pixels_to_angle([2 * u.arcsec, 1 * u.pix], example_map)


def test_pixels_to_angle_conversion_invalid_type(example_map):
    # Invalid single type
    with pytest.raises(ValueError):
        pixels_to_angle("3", example_map)
    # List of different types
    with pytest.raises(ValueError):
        pixels_to_angle([1, "2"], example_map)
    # List of lists
    with pytest.raises(ValueError):
        pixels_to_angle([[1, 2]], example_map)
