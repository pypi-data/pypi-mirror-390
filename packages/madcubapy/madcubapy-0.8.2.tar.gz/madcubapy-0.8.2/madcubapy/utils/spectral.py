import astropy.constants as const
import astropy.units as u
from astropy.units import Quantity
import numpy as np

__all__ = [
    'create_spectral_array',
    'obs_to_rest',
    'rest_to_obs',
    'obs_to_vel',
    'vel_to_obs',
    'rest_to_vel',
    'vel_to_rest',
]

def create_spectral_array(nchan, cdelt, crpix, crval):
    """
    Create a spectral axis array.

    Parameters
    ----------
    nchan : `~int`
        Number of channels in the spectrum.
    cdelt : `~float` or `~astropy.units.Quantity`
        Width of a channel.
    crpix : `~float`
        Reference channel of the spectrum.
    crval : `~float`
        Value of the reference channel.
    
    Returns
    -------
    spectral_array : `~numpy.ndarray` or `~astropy.units.Quantity`
        Returned spectral axis array with units if cdelt is a quantity.

    """

    # if cdelt has units
    if isinstance(cdelt, Quantity):
        first_chan = crval - (cdelt.value * crpix)
        last_chan = crval + (cdelt.value * (nchan-1 - crpix))
        spectral_array = np.linspace(first_chan, last_chan, nchan) * cdelt.unit
    # if cdelt is adimensional
    else:
        first_chan = crval - (cdelt * crpix)
        last_chan = crval + (cdelt * (nchan-1 - crpix))
        spectral_array = np.linspace(first_chan, last_chan, nchan)

    return spectral_array


def obs_to_rest(obs_freq, radial_velocity, doppler_convention):
    """
    Convert observed frequency to rest frequency.

    Parameters
    ----------
    obs_freq : `~astropy.units.Quantity`
        Observed frequency.
    radial_velocity : `~astropy.units.Quantity`
        Radial velocity of the source relative to the observer.
    doppler_convention : {"radio", "relativistic"}, optional
        The Doppler convention to use.

    Returns
    -------
    rest_freq : `~astropy.units.Quantity`
        Rest frequency.

    """

    if not isinstance(obs_freq, u.Quantity):
        raise TypeError("obs_freq must be an astropy Quantity.")
    if not isinstance(radial_velocity, u.Quantity):
        raise TypeError("vel must be an astropy Quantity.")
    
    if doppler_convention == "radio":
        rest_freq = _obs_to_rest_radio(obs_freq, radial_velocity)
    elif doppler_convention == "relativistic":
        rest_freq = _obs_to_rest_rel(obs_freq, radial_velocity)
    else:
        raise ValueError(
            "Doppler convention can only be radio or relativistic.")

    return rest_freq


def rest_to_obs(rest_freq, radial_velocity, doppler_convention):
    """
    Convert rest frequency to observed frequency.

    Parameters
    ----------
    rest_freq : `~astropy.units.Quantity`
        Rest frequency.
    radial_velocity : `~astropy.units.Quantity`
        Radial velocity of the source relative to the observer.
    doppler_convention : {"radio", "relativistic"}, optional
        The Doppler convention to use.

    Returns
    -------
    obs_freq : `~astropy.units.Quantity`
        Observed frequency.

    """

    if not isinstance(rest_freq, u.Quantity):
        raise TypeError("rest_freq must be an astropy Quantity.")
    if not isinstance(radial_velocity, u.Quantity):
        raise TypeError("vel must be an astropy Quantity.")
    
    if doppler_convention == "radio":
        obs_freq = _rest_to_obs_radio(rest_freq, radial_velocity)
    elif doppler_convention == "relativistic":
        obs_freq = _rest_to_obs_rel(rest_freq, radial_velocity)
    else:
        raise ValueError(
            "Doppler convention can only be radio or relativistic.")

    return obs_freq


def obs_to_vel(obs_freq, doppler_rest, doppler_convention):
    """
    Convert observed frequency to velocity.

    Parameters
    ----------
    obs_freq : `~astropy.units.Quantity`
        Observed frequency.
    doppler_rest : `~astropy.units.Quantity`
        Rest frequency of the line.
    doppler_convention : {"radio", "relativistic"}, optional
        The Doppler convention to use.

    Returns
    -------
    vel : `~astropy.units.Quantity`
        Velocity.

    """

    if not isinstance(obs_freq, u.Quantity):
        raise TypeError("obs_freq must be an astropy Quantity.")
    if not isinstance(doppler_rest, u.Quantity):
        raise TypeError("doppler_rest must be an astropy Quantity.")
    
    if doppler_convention == "radio":
        vel = _obs_to_vel_radio(obs_freq, doppler_rest)
    elif doppler_convention == "relativistic":
        vel = _obs_to_vel_rel(obs_freq, doppler_rest)
    else:
        raise ValueError(
            "Doppler convention can only be radio or relativistic.")

    return vel


def vel_to_obs(vel, doppler_rest, doppler_convention):
    """
    Convert velocity to observed frequency.

    Parameters
    ----------
    vel : `~astropy.units.Quantity`
        Velocity.
    doppler_rest : `~astropy.units.Quantity`
        Rest frequency of the line.
    doppler_convention : {"radio", "relativistic"}, optional
        The Doppler convention to use.

    Returns
    -------
    obs_freq : `~astropy.units.Quantity`
        Observed frequency.

    """

    if not isinstance(vel, u.Quantity):
        raise TypeError("vel must be an astropy Quantity.")
    if not isinstance(doppler_rest, u.Quantity):
        raise TypeError("doppler_rest must be an astropy Quantity.")
    
    if doppler_convention == "radio":
        obs_freq = _vel_to_obs_radio(vel, doppler_rest)
    elif doppler_convention == "relativistic":
        obs_freq = _vel_to_obs_rel(vel, doppler_rest)
    else:
        raise ValueError(
            "Doppler convention can only be radio or relativistic.")

    return obs_freq


def rest_to_vel(rest_freq, radial_velocity, doppler_rest, doppler_convention):
    """
    Convert rest frequency to velocity.

    Parameters
    ----------
    rest_freq : `~astropy.units.Quantity`
        Observed frequency.
    radial_velocity : `~astropy.units.Quantity`
        Radial velocity of the source relative to the observer.
    doppler_rest : `~astropy.units.Quantity`
        Rest frequency of the line.
    doppler_convention : {"radio", "relativistic"}, optional
        The Doppler convention to use.

    Returns
    -------
    vel : `~astropy.units.Quantity`
        Velocity.

    """

    if not isinstance(rest_freq, u.Quantity):
        raise TypeError("rest_freq must be an astropy Quantity.")
    if not isinstance(radial_velocity, u.Quantity):
        raise TypeError("radial_velocity must be an astropy Quantity.")
    if not isinstance(doppler_rest, u.Quantity):
        raise TypeError("doppler_rest must be an astropy Quantity.")
    
    if doppler_convention not in ["radio", "relativistic"]:
        raise ValueError(
            "Doppler convention can only be radio or relativistic.")
    
    obs_freq = rest_to_obs(rest_freq, radial_velocity, doppler_convention)
    vel = obs_to_vel(obs_freq, doppler_rest, doppler_convention)

    return vel


def vel_to_rest(vel, radial_velocity, doppler_rest, doppler_convention):
    """
    Convert velocty to rest frequency.

    Parameters
    ----------
    vel : `~astropy.units.Quantity`
        Velocity.
    radial_velocity : `~astropy.units.Quantity`
        Radial velocity of the source relative to the observer.
    doppler_rest : `~astropy.units.Quantity`
        Rest frequency of the line.
    doppler_convention : {"radio", "relativistic"}, optional
        The Doppler convention to use.

    Returns
    -------
    rest_freq : `~astropy.units.Quantity`
        Rest frequency.

    """

    if not isinstance(vel, u.Quantity):
        raise TypeError("vel must be an astropy Quantity.")
    if not isinstance(radial_velocity, u.Quantity):
        raise TypeError("radial_velocity must be an astropy Quantity.")
    if not isinstance(doppler_rest, u.Quantity):
        raise TypeError("doppler_rest must be an astropy Quantity.")
    
    if doppler_convention not in ["radio", "relativistic"]:
        raise ValueError(
            "Doppler convention can only be radio or relativistic.")
    
    obs_freq = vel_to_obs(vel, doppler_rest, doppler_convention)
    rest_freq = obs_to_rest(obs_freq, radial_velocity, doppler_convention)

    return rest_freq


def _obs_to_rest_radio(obs_freq, vel):
    return obs_freq / (1 - vel / const.c)

def _obs_to_rest_rel(obs_freq, vel):
    beta = vel / const.c
    return obs_freq * np.sqrt((1 + beta) / (1 - beta))

def _rest_to_obs_radio(rest_freq, vel):
    return rest_freq * (1 - vel / const.c)

def _rest_to_obs_rel(rest_freq, vel):
    beta = vel / const.c
    return rest_freq * ((1 - beta) / (1 + beta))**0.5

def _obs_to_vel_radio(obs_freq, rest_freq):
    return const.c * ((rest_freq - obs_freq) / rest_freq)

def _obs_to_vel_rel(obs_freq, rest_freq):
    R = obs_freq / rest_freq
    beta = (1 - R**2) / (1 + R**2)
    return beta * const.c

def _vel_to_obs_radio(vel, rest_freq):
    return rest_freq * (1 - vel / const.c)

def _vel_to_obs_rel(vel, rest_freq):
    beta = (vel / const.c)
    return rest_freq * ((1 - beta) / (1 + beta))**0.5