import astropy.constants as const
from astropy.coordinates import SpectralCoord
import astropy.units as u
import numpy as np
from madcubapy.utils import rest_to_obs

__all__ = [
    'SpectralData',
]

class SpectralData(SpectralCoord):
    """
    Wrapper for `~astropy.coordinates.SpectralCoord` that adds support for
    rest-frame frequencies input.
    
    .. note:: Frame conversion between observed and rest frequencies always
              uses the relativistic convention (matching Astropy behavior).
              For expressing spectral coordinates as velocities, the
              doppler_convention can be 'radio' or 'relativistic'.

    Parameters
    ----------
    value : `int`, `float`, `~numpy.ndarray`, or `~astropy.units.Quantity`
        Spectral values (wavelength, frequency, energy, wavenumber,
        or velocity)
    unit : `~astropy.units.Unit`
        Unit for the given spectral values. Mandatory if value is not a
        `~astropy.units.Quantity`.
    frame_type : {"observed", "rest"}, default: "observed"
        Reference frame for input data.
    radial_velocity : `~astropy.units.Quantity`, optional
        Radial velocity of the source.
    doppler_rest : `~astropy.units.Quantity`, optional
        Reference rest frequency (for velocity calculations).
    doppler_convention : {"radio", "relativistic"}, optional
        The Doppler convention to use when expressing the spectral value as
        velocity.

    Other parameters
    ----------------
    **kwargs
        Additional arguments passed to `~astropy.coordinates.SpectralCoord`.

    """

    def __new__(
        cls,
        value,
        unit=None,
        frame_type="observed",
        radial_velocity=None,
        doppler_rest=None,
        doppler_convention=None,
        **kwargs
    ):
        if isinstance(value, u.Quantity):
            if unit is not None:
                raise ValueError(
                    "Cannot specify value as a Quantity and also specify unit"
                )
            value, unit = value.value, value.unit
        else:
            if not unit:
                raise ValueError(
                    "SpectralCoord instances require units equivalent to "
                    "Hz, m, J, 1/m, or km/s, but no unit was given."
                )

        # If input is velocities skip frame_type logic
        if unit.is_equivalent(u.km/u.s):
            if frame_type != "observed":
                raise ValueError(
                    "rest frame_type is ncompatible with velocity input."
                )
            return super().__new__(
                cls,
                value,
                unit=unit,
                radial_velocity=radial_velocity,
                doppler_rest=doppler_rest,
                doppler_convention=doppler_convention,
                **kwargs
            )
        else:
            if frame_type not in ["observed", "rest"]:
                raise ValueError('frame_type must be "observed" or "rest"')
        
        # Determine spectral type and convert to frequency
        if unit.is_equivalent(u.Hz):  # Frequency
            unit_freq = unit
            frequency = value
        elif unit.is_equivalent(u.m):  # Wavelength
            frequency = (const.c / (value * unit)).to(u.Hz)
            value, unit_freq = frequency.value, frequency.unit
        elif unit.is_equivalent(u.eV):  # Energy
            frequency = (value * unit / const.h).to(u.Hz)
            value, unit_freq = frequency.value, frequency.unit
        elif unit.is_equivalent(u.m**-1):  # Wavenumber
            frequency = (value * unit * const.c).to(u.Hz)
            value, unit_freq = frequency.value, frequency.unit
        else:
            raise u.UnitsError(
                'Input units must be equivalent to Hz, m, J, 1/m, or km/s.'
            )

        # Create observed array if rest is provided
        if frame_type == "rest":
            if radial_velocity is None:
                raise ValueError(
                    "radial_velocity required for frame_type='rest'")
            else:
                frequency = rest_to_obs(value * unit_freq, radial_velocity, "relativistic")
                value, unit_freq = frequency.value, frequency.unit

        # Create SpectralCoord with obs frequency and return in OG units
        return super().__new__(
            cls,
            value,
            unit=unit_freq,
            radial_velocity=radial_velocity,
            doppler_rest=doppler_rest,
            doppler_convention=doppler_convention,
            **kwargs,
        ).to(unit)
