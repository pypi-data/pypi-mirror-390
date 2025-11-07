import astropy.constants as const
import astropy.units as u
from astropy.units import Quantity
import numpy as np
import pytest
from madcubapy.utils.spectral import create_spectral_array
from madcubapy.utils.spectral import obs_to_rest
from madcubapy.utils.spectral import rest_to_obs
from madcubapy.utils.spectral import obs_to_vel
from madcubapy.utils.spectral import vel_to_obs
from madcubapy.utils.spectral import rest_to_vel
from madcubapy.utils.spectral import vel_to_rest

def test_create_spectral_array_without_units():
    # Test a specific array without units
    assert (create_spectral_array(8, 0.5, -3, 10).all()
         == np.array([11.5, 12, 12.5, 13, 13.5, 14, 14.5, 15]).all())

def test_create_spectral_array_with_units():
    # Test a specific array with units
    a = create_spectral_array(8, 0.5 * u.s, -3, 10)
    b = np.array([11.5, 12, 12.5, 13, 13.5, 14, 14.5, 15]) * u.s
    assert a.value.all() == b.value.all()
    assert a.unit == b.unit

# GLobal precalculated values
rest_array = (266, 267) * u. GHz
rest_single = 266 * u. GHz
obs_array_rad = (263.33815852, 264.3281516) * u.GHz
obs_array_rel = (263.35134466, 264.3413873) * u.GHz
vel_array_rad = (2999.99999999999, 1884.23887969924) * u.km / u.s
vel_array_rel = (2999.99999999999, 1875.14957479892) * u.km / u.s
vel_single = 3000 * u.km / u.s

def test_rest_to_obs_result():
    assert np.allclose(
        rest_to_obs(rest_array, vel_single, "radio").value,
        obs_array_rad.value,
        atol=1e-5, rtol=0
    )
    assert np.allclose(
        rest_to_obs(rest_array, vel_single, "relativistic").value,
        obs_array_rel.value,
        atol=1e-5, rtol=0
    )
    assert not np.allclose(
        rest_to_obs(rest_array, vel_single, "radio").value,
        obs_array_rel.value,
        atol=1e-5, rtol=0
    )
    assert not np.allclose(
        rest_to_obs(rest_array, vel_single, "relativistic").value,
        obs_array_rad.value,
        atol=1e-5, rtol=0
    )

def test_obs_to_rest_result():
    assert np.allclose(
        obs_to_rest(obs_array_rad, vel_single, "radio").value,
        rest_array.value,
        atol=1e-5, rtol=0
    )
    assert np.allclose(
        obs_to_rest(obs_array_rel, vel_single, "relativistic").value,
        rest_array.value,
        atol=1e-5, rtol=0
    )
    assert not np.allclose(
        obs_to_rest(obs_array_rel, vel_single, "radio").value,
        rest_array.value,
        atol=1e-5, rtol=0
    )
    assert not np.allclose(
        obs_to_rest(obs_array_rad, vel_single, "relativistic").value,
        rest_array.value,
        atol=1e-5, rtol=0
    )

def test_obs_to_vel_result():
    assert np.allclose(
        obs_to_vel(obs_array_rad, rest_single, "radio").to(u.km / u.s).value,
        vel_array_rad.to(u.km / u.s).value,
        atol=1e-5, rtol=0
    )
    assert np.allclose(
        obs_to_vel(obs_array_rel, rest_single, "relativistic").to(u.km / u.s).value,
        vel_array_rel.to(u.km / u.s).value,
        atol=1e-5, rtol=0
    )
    assert not np.allclose(
        obs_to_vel(obs_array_rel, rest_single, "radio").to(u.km / u.s).value,
        vel_array_rad.to(u.km / u.s).value,
        atol=1e-5, rtol=0
    )
    assert not np.allclose(
        obs_to_vel(obs_array_rad, rest_single, "relativistic").to(u.km / u.s).value,
        vel_array_rel.to(u.km / u.s).value,
        atol=1e-5, rtol=0
    )

def test_vel_to_obs_result():
    assert np.allclose(
        vel_to_obs(vel_array_rad, rest_single, "radio").to(u.GHz).value,
        obs_array_rad.to(u.GHz).value,
        atol=1e-5, rtol=0
    )
    assert np.allclose(
        vel_to_obs(vel_array_rel, rest_single, "relativistic").to(u.GHz).value,
        obs_array_rel.to(u.GHz).value,
        atol=1e-5, rtol=0
    )
    assert not np.allclose(
        vel_to_obs(vel_array_rel, rest_single, "radio").to(u.GHz).value,
        obs_array_rel.to(u.GHz).value,
        atol=1e-5, rtol=0
    )
    assert not np.allclose(
        vel_to_obs(vel_array_rad, rest_single, "relativistic").to(u.GHz).value,
        obs_array_rad.to(u.GHz).value,
        atol=1e-5, rtol=0
    )

def test_rest_to_vel_result():
    assert np.allclose(
        rest_to_vel(rest_array, vel_single, rest_single, "radio").to(u.km / u.s).value,
        vel_array_rad.to(u.km / u.s).value,
        atol=1e-5, rtol=0
    )
    assert np.allclose(
        rest_to_vel(rest_array, vel_single, rest_single, "relativistic").to(u.km / u.s).value,
        vel_array_rel.to(u.km / u.s).value,
        atol=1e-5, rtol=0
    )
    assert not np.allclose(
        rest_to_vel(rest_array, vel_single, rest_single, "radio").to(u.km / u.s).value,
        vel_array_rel.to(u.km / u.s).value,
        atol=1e-5, rtol=0
    )
    assert not np.allclose(
        rest_to_vel(rest_array, vel_single, rest_single, "relativistic").to(u.km / u.s).value,
        vel_array_rad.to(u.km / u.s).value,
        atol=1e-5, rtol=0
    )

def test_vel_to_rest_result():
    assert np.allclose(
        vel_to_rest(vel_array_rad, vel_single, rest_single, "radio").to(u.GHz).value,
        rest_array.to(u.GHz).value,
        atol=1e-5, rtol=0
    )
    assert np.allclose(
        vel_to_rest(vel_array_rel, vel_single, rest_single, "relativistic").to(u.GHz).value,
        rest_array.to(u.GHz).value,
        atol=1e-5, rtol=0
    )
    assert not np.allclose(
        vel_to_rest(vel_array_rel, vel_single, rest_single, "radio").to(u.GHz).value,
        rest_array.to(u.GHz).value,
        atol=1e-5, rtol=0
    )
    assert not np.allclose(
        vel_to_rest(vel_array_rad, vel_single, rest_single, "relativistic").to(u.GHz).value,
        rest_array.to(u.GHz).value,
        atol=1e-5, rtol=0
    )
