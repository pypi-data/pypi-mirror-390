import astropy.units as u
import numpy as np

__all__ = [
    'get_angular_offset_points',
    'get_angular_separation',
    'get_physical_offset_points',
    'get_physical_separation',
]

def get_angular_offset_points(points, ref_point, fitsmap):
    """
    Get offset coordinates of a point or set of points, with respect to a
    reference point in angular units.

    Parameters
    ----------
    points : `~numpy.ndarray`
        Input point or points.
    ref_point : `~numpy.ndarray`
        Reference point.
    fitsmap : `~madcubapy.io.MadcubaMap` or `~astropy.nddata.CCDData`
        Map from which to get angular size of each pixel (CDELT1, CDELT2).

    Returns
    -------
    angular_offset_points : `~astropy.units.Quantity`
        Points with converted units to angular offset.

    """

    cdelt_deg = fitsmap.wcs.wcs.cdelt[:2] * u.deg
    angular_offset_points = (points - ref_point) * cdelt_deg

    return angular_offset_points


def get_angular_separation(points, ref_point, fitsmap):
    """
    Get separation between a point or set of points, and a reference pixel in
    angular units.

    Parameters
    ----------
    points : `~numpy.ndarray`
        Input point or points.
    ref_point : `~numpy.ndarray`
        Reference point.
    fitsmap : `~madcubapy.io.MadcubaMap` or `~astropy.nddata.CCDData`
        Map from which to get angular size of each pixel (CDELT1, CDELT2).

    Returns
    -------
    angular_separation : `~astropy.units.Quantity`
        Separation between input points and reference point.

    """

    angular_offset_points = get_angular_offset_points(points, ref_point, fitsmap)
    angular_separation = np.linalg.norm(angular_offset_points, axis=-1)

    return angular_separation


def get_physical_offset_points(points, ref_point, fitsmap, distance):
    """
    Get offset coordinates of a point or set of points, with respect to a
    reference point in physical distance units.

    Parameters
    ----------
    points : `~numpy.ndarray`
        Input point or points.
    ref_point : `~numpy.ndarray`
        Reference point.
    fitsmap : `~madcubapy.io.MadcubaMap` or `~astropy.nddata.CCDData`
        Map from which to get angular size of each pixel (CDELT1, CDELT2).
    distance : `~astropy.units.quantity`
        Distance from earth to object.

    Returns
    -------
    physical_offset_points : `~astropy.units.Quantity`
        Points with converted units to physical distance offset.

    """

    angular_offset_points = get_angular_offset_points(points, ref_point, fitsmap)

    physical_offset_points = (angular_offset_points * distance).to(
        u.au, equivalencies=u.dimensionless_angles()
    )

    return physical_offset_points


def get_physical_separation(points, ref_point, fitsmap, distance):
    """
    Get separation between a point or set of points, and a reference pixel in
    physical distance units.

    Parameters
    ----------
    points : `~numpy.ndarray`
        Input point or points.
    ref_point : `~numpy.ndarray`
        Reference point.
    fitsmap : `~madcubapy.io.MadcubaMap` or `~astropy.nddata.CCDData`
        Map from which to get angular size of each pixel (CDELT1, CDELT2).
    distance : `~astropy.units.quantity`
        Distance from earth to object.

    Returns
    -------
    physical_separation : `~astropy.units.Quantity`
        Separation between input points and reference point.

    """

    physical_offset_points = get_physical_offset_points(points, ref_point, fitsmap, distance)
    physical_separation = np.linalg.norm(physical_offset_points, axis=-1)

    return physical_separation
