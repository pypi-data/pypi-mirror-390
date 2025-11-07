import numpy as np

__all__ = [
    'transform_coords_fitsmap',
    'transform_coords_axes',
]

def transform_coords_fitsmap(
        ref_fitsmap,
        target_fitsmap,
        points,
        origin=0):
    """
    Transform the pixel coordinates of one or more points between two maps.

    Parameters
    ----------
    ref_fitsmap : `~madcubapy.io.MadcubaMap` or `~astropy.nddata.CCDData`
        Reference map.
    target_fitsmap : `~madcubapy.io.MadcubaMap` or `~astropy.nddata.CCDData`
        Map into which the points are transformed.
    points : `~numpy.ndarray`
        Points from ref_fitsmap to transform.
    origin : `int`, default:0
        Origin of the coordinates of the image. 0 for numpy standards, and 1
        for FITS standards.

    Returns
    -------
    new_points : `~numpy.ndarray`
        Transformed points in the second image. 

    """

    if isinstance(points, tuple):
        points = np.array(points)

    if ref_fitsmap.header['NAXIS'] == 2:
        # Pixels to coordinates
        ra, dec = \
            ref_fitsmap.wcs.wcs_pix2world(points.T[0], points.T[1], origin)
        # Coordinates to pixels from second image
        new_x, new_y = \
            target_fitsmap.wcs.wcs_world2pix(ra, dec, origin)
    elif ref_fitsmap.header['NAXIS'] == 4:
        # Pixels to coordinates
        ra, dec, frec_world, pol_world = \
            ref_fitsmap.wcs.wcs_pix2world(
                points.T[0], points.T[1], 1, 1, origin
            )
        # Coordinates to pixels from second image
        new_x, new_y, nul_frec_pix, nul_pol_pix = \
            target_fitsmap.wcs.wcs_world2pix(
                ra, dec, frec_world, pol_world, origin
            )
    
    new_points = np.array([new_x, new_y]).T

    return new_points


def transform_coords_axes(
        ref_ax,
        target_ax,
        points):
    """
    Transform the pixel coordinates of one or more points between two
    `~astropy.visualization.wcsaxes.WCSAxes`.

    Parameters
    ----------
    ref_ax : `~astropy.visualization.wcsaxes.WCSAxes`
        Reference axes.
    target_ax : `~astropy.visualization.wcsaxes.WCSAxes`
        Axes into which the points are transformed.
    points : `~numpy.ndarray`
        Points from ref_axes to transform.

    Returns
    -------
    new_points : `~numpy.ndarray`
        Transformed points in the second image. 

    """

    # Astropy does not provide a straightforward method to get world
    # coordinates from an image pixel. It does however provide
    # transformations between pixel or world coordinates and the screen
    # coordinates. To get the world coordinates using only the WCSAxes
    # object, we must convert from pixels to screen, and then screen to
    # pixels.
    reference_pix2screen = ref_ax.get_transform('pixel')
    reference_screen2world = ref_ax.get_transform('world').inverted()
    reference_screen_coords = reference_pix2screen.transform(points)
    world_coords = reference_screen2world.transform(reference_screen_coords)
    # Finally we can do the same but backwards for the second axes.
    final_world2screen = target_ax.get_transform('world')
    final_screen2pix = target_ax.get_transform('pixel').inverted()
    final_screen_coords = final_world2screen.transform(world_coords)
    new_points = final_screen2pix.transform(final_screen_coords)

    return new_points
