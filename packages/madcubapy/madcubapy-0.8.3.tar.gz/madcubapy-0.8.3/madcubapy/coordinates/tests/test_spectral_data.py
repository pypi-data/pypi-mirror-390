import astropy.constants as const
from astropy.coordinates import SpectralCoord
import astropy.units as u
import numpy as np
import pytest
from madcubapy.coordinates import SpectralData
from madcubapy.utils import rest_to_obs
from madcubapy.utils import obs_to_rest
from madcubapy.utils import vel_to_obs
from madcubapy.utils import obs_to_vel

rest_freq = (266, 267) * u.GHz
obs_freq = (265.95563967, 266.95547291) * u.GHz
vel = (1183.81062007, 61.22172014) * u.km / u.s
radial_velocity = 50 * u.km / u.s
doppler_rest = 267.01 * u.GHz

@pytest.fixture
def example_spectral_data_rest():
    return SpectralData(
        rest_freq,
        frame_type="rest",
        radial_velocity=50 * u.km / u.s,
        doppler_rest=doppler_rest,
        doppler_convention="radio",
    )

@pytest.fixture
def example_spectral_data_obs():
    return SpectralData(
        obs_freq,
        frame_type="observed",
        radial_velocity=50 * u.km / u.s,
        doppler_rest=doppler_rest,
        doppler_convention="radio",
    )

@pytest.fixture
def example_spectral_data_vel():
    return SpectralData(
        vel,
        radial_velocity=50 * u.km / u.s,
        doppler_rest=doppler_rest,
        doppler_convention="radio",
    )

def test_equal_fixtures(example_spectral_data_rest,
                        example_spectral_data_obs,
                        example_spectral_data_vel):
    assert np.allclose(
        example_spectral_data_rest.value,
        example_spectral_data_obs.value,
        atol=1e-5, rtol=0
    )
    assert np.allclose(
        example_spectral_data_rest.to(u.GHz).value,
        example_spectral_data_vel.to(u.GHz).value,
        atol=1e-5, rtol=0
    )
    assert np.allclose(
        example_spectral_data_rest.to_rest().value,
        example_spectral_data_obs.to_rest().value,
        atol=1e-5, rtol=0
    )
    assert np.allclose(
        example_spectral_data_rest.to(u.GHz).to_rest().value,
        example_spectral_data_vel.to(u.GHz).to_rest().value,
        atol=1e-5, rtol=0
    )
    assert np.allclose(
        example_spectral_data_rest.to(u.km / u.s).value,
        example_spectral_data_obs.to(u.km / u.s).value,
        atol=1e-5, rtol=0
    )
    assert np.allclose(
        example_spectral_data_rest.to(u.km / u.s).value,
        example_spectral_data_vel.to(u.km / u.s).value,
        atol=1e-5, rtol=0
    )

def test_initial_rest_obs_conversion(example_spectral_data_rest):
    assert np.allclose(
        rest_to_obs(rest_freq, radial_velocity, "relativistic").value,
        example_spectral_data_rest.value,
        atol=1e-5, rtol=0
    )

def test_to_rest(example_spectral_data_rest):
    assert np.allclose(
        rest_freq.value,
        example_spectral_data_rest.to_rest().value,
        atol=1e-5, rtol=0
    )

def test_to_velocity_conversion(example_spectral_data_rest):
    assert np.allclose(
        vel.value,
        example_spectral_data_rest.to(u.km / u.s).value,
        atol=1e-5, rtol=0
    )

def test_specify_quantity_and_unit_error():
    with pytest.raises(ValueError):
        SpectralData(3 * u.GHz, unit=u.GHz)

def test_specify_no_quantity_no_unit_error():
    with pytest.raises(ValueError):
        SpectralData(3)

def test_rest_with_velocity_input_error():
    with pytest.raises(ValueError):
        SpectralData(3 * u.km / u.s, frame_type="rest")

def test_incompatible_frame_error():
    with pytest.raises(ValueError):
        SpectralData(3 * u.GHz, frame_type="obs")

def test_incompatible_units_error():
    with pytest.raises(u.UnitsError):
        SpectralData(3 * u.s)
    with pytest.raises(u.UnitsError):
        SpectralData(3 * u.s / u.km)
    with pytest.raises(u.UnitsError):
        SpectralData(3 * u.Jy)

def test_empty_velocity_rest_frame():
    with pytest.raises(ValueError):
        SpectralData(3 * u.GHz, frame_type="rest")
