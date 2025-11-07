import astropy.units as u
import numpy as np
import pytest
from madcubapy.regions.carta import _parse_crtf_coord_string
from madcubapy.regions.carta import _parse_crtf_angle_string
from madcubapy.regions.ds9 import _parse_ds9_coord_string
from madcubapy.regions.ds9 import _parse_ds9_angle_string
from madcubapy.regions.madcuba import _parse_mcroi_coord_string


# CRTF
@pytest.mark.parametrize(
    "input_str, expected_value, expected_unit",
    [
        ("103.3", 103.3, u.pix),
        ("103.3pix", 103.3, u.pix),
        ("1.23deg", 1.23, u.deg),
        ("45.6rad", 45.6, u.rad),
        ("103.8931arcmin",103.8931, u.arcmin),
        ("103.8931arcsec",103.8931, u.arcsec),
    ]
)
def test_crtf_coord_parser_results(input_str, expected_value, expected_unit):
    parsed_quantity = _parse_crtf_coord_string(input_str)
    # Assert value avoiding floating-point issues
    assert np.isclose(parsed_quantity.value, expected_value)
    # Assert unit matches expected unit
    assert parsed_quantity.unit == expected_unit

def test_crtf_coord_parser_invalid_string():
    with pytest.raises(ValueError):
        _parse_crtf_coord_string("1.23pox")
        _parse_crtf_coord_string("1,23pix")

@pytest.mark.parametrize(
    "input_str, expected_value, expected_unit",
    [
        ("103.3", 103.3, u.pix),
        ("103.3pix", 103.3, u.pix),
        ("1.23deg", 1.23, u.deg),
        ("45.6rad", 45.6, u.rad),
        ("103.8931arcmin",103.8931, u.arcmin),
        ("103.8931arcsec",103.8931, u.arcsec),
    ]
)
def test_crtf_angle_parser_results(input_str, expected_value, expected_unit):
    parsed_quantity = _parse_crtf_angle_string(input_str)
    # Assert value avoiding floating-point issues
    assert np.isclose(parsed_quantity.value, expected_value)
    # Assert unit matches expected unit
    assert parsed_quantity.unit == expected_unit

def test_crtf_angle_parser_invalid_string():
    with pytest.raises(ValueError):
        _parse_crtf_angle_string("1.23pox")
        _parse_crtf_angle_string("1,23pix")


# DS9
@pytest.mark.parametrize(
    "input_str, input_system, expected_value, expected_unit",
    [
        ("103.3", "image", 103.3, u.pix),
        ("1.23", "icrs", 1.23, u.deg),
        ("103.8931'", "icrs",103.8931, u.arcmin),
        ('103.8931"', "icrs",103.8931, u.arcsec),
    ]
)
def test_ds9_coord_parser_results(input_str, input_system, expected_value, expected_unit):
    parsed_quantity = _parse_ds9_coord_string(input_str, input_system)
    # Assert value avoiding floating-point issues
    assert np.isclose(parsed_quantity.value, expected_value)
    # Assert unit matches expected unit
    assert parsed_quantity.unit == expected_unit

def test_ds9_coord_parser_invalid_number_string():
    with pytest.raises(ValueError):
        _parse_ds9_coord_string("1,23", "image")

def test_ds9_coord_parser_invalid_coord_string():
    parsed_quantity = _parse_ds9_coord_string("1.23", "pixels")
    assert np.isclose(parsed_quantity.value, 1)
    assert parsed_quantity.unit == u.deg


@pytest.mark.parametrize(
    "input_str, expected_value, expected_unit",
    [
        ("1.23", 1.23, u.deg),
        ("103.8931'",103.8931, u.arcmin),
        ('103.8931"',103.8931, u.arcsec),
    ]
)
def test_ds9_angle_parser_results(input_str, expected_value, expected_unit):
    parsed_quantity = _parse_ds9_angle_string(input_str)
    # Assert value avoiding floating-point issues
    assert np.isclose(parsed_quantity.value, expected_value)
    # Assert unit matches expected unit
    assert parsed_quantity.unit == expected_unit


# MADCUBA
@pytest.mark.parametrize(
    "input_str, input_frame, input_system, expected_value, expected_unit",
    [
        ("103.3", "Pixel", "icrs", 103.3, u.pix),
        ("103.3", "World", "icrs", 103.3, u.pix),
        ("1.23deg", "World", "icrs", 1.23, u.deg),
        ("12.43rad", "World", "icrs", 12.43, u.rad),
        ("103.8931arcmin", "World", "icrs",103.8931, u.arcmin),
        ("103.8931arcsec", "World", "icrs",103.8931, u.arcsec),
    ]
)
def test_mcroi_coord_parser_results(input_str, input_frame, input_system, expected_value, expected_unit):
    parsed_quantity = _parse_mcroi_coord_string(input_str, input_frame, input_system)
    # Assert value avoiding floating-point issues
    assert np.isclose(parsed_quantity.value, expected_value)
    # Assert unit matches expected unit
    assert parsed_quantity.unit == expected_unit

def test_mcroi_coord_parser_invalid_string():
    with pytest.raises(ValueError):
        # Invalid unit string
        _parse_mcroi_coord_string("1.23pixels", "Image", "icrs")
        # invalid frame string
        _parse_mcroi_coord_string("1.23pix", "image", "icrs")
        # Invalid number with comma
        _parse_mcroi_coord_string("1,23pix", "Image", "icrs")
