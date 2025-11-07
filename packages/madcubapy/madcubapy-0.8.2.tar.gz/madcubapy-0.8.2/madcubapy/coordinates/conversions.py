import astropy.units as u
import copy
import numpy as np

__all__ = [
    'fits_to_python',
    'python_to_fits',
    'world_to_pixel',
    'pixel_to_world',
    'angle_to_pixels',
    'pixels_to_angle',
]


def fits_to_python(
        points):
    """
    Simple function to convert one or more points from FITS coordinates to
    python coordinates (numpy and matplotlib image).

    Parameters
    ----------
    points : `~numpy.ndarray`, `tuple`, or `list`.
        Input Points.

    Returns
    -------
    python_points : `~numpy.ndarray`
        Points converted to python coordinates.

    """

    if (isinstance(points, np.ndarray) or
            isinstance(points, tuple) or
            isinstance(points, list)):
        fits_points = np.array(points)
    else:
        raise ValueError(f'Invalid type for points: {type(points)}.')

    # Check if input parameter is one point or an array with the last
    # dimension being 2 = array of points.
    if ((isinstance(fits_points, np.ndarray) and fits_points.shape[-1] == 2) or
            (isinstance(fits_points, int) and fits_points.shape == 2)):
        python_points = fits_points - 1
    else:
        raise ValueError(f'Invalid shape: {fits_points.shape}. '
                         + 'Last dimension has to be 2: (..., 2).')

    return python_points


def python_to_fits(
        points):
    """
    Simple function to convert one or more points from python coordinates
    (numpy and matplotlib image) to FITS coordinates.

    Parameters
    ----------
    points : `~numpy.ndarray`, `tuple`, or `list`.
        Input points.

    Returns
    -------
    fits_points : `~numpy.ndarray`
        Points converted to fits coordinates.

    """

    if (isinstance(points, np.ndarray) or
            isinstance(points, tuple) or
            isinstance(points, list)):
        python_points = np.array(points)
    else:
        raise ValueError(f'Invalid type for points: {type(points)}.')

    # Check if input parameter is one point or an array with the last
    # dimension being 2 = array of points.
    if ((isinstance(python_points, np.ndarray) and python_points.shape[-1] == 2) or
            (isinstance(python_points, int) and python_points.shape == 2)):
        fits_points = python_points + 1
    else:
        raise ValueError(f'Invalid shape: {python_points.shape}. '
                         + 'Last dimension has to be 2: (..., 2).')

    return fits_points


def world_to_pixel(
        points,
        fitsmap,
        origin=0,
        log=False):
    """
    Convert a set of points in world coordinates to pixel coordinates (python
    or FITS).

    Parameters
    ----------
    points : `~astropy.units.Quantity` or `numpy.ndarray` or `tuple` or `list`.
        Input points.
    fitsmap : `~madcubapy.io.MadcubaMap` or `~astropy.nddata.CCDData`.
        Map object used to get WCS data.
    origin : `int`, optional, default=0
        Starting coordinate for image data: 0 for python pixel coordinates,
        1 for FITS coordinates.
    log : `bool`, optional
        If True, print on screen information messages on how the data is
        parsed.

    Returns
    -------
    pixel_points : `~numpy.ndarray`
        Points converted to pixel coordinates.

    """

    # Create a deepcopy because for a list of lists [:] and copy() fails
    pts = copy.deepcopy(points)
    # If it is a quantity, continue the function to step 2 with correct units
    if isinstance(pts, u.Quantity):
        unit = pts.unit
        if unit == u.pix:
            if log: print("Input units are pixels, returning pixels.")
            return pts.value
        elif (unit == u.rad or unit == u.deg or
              unit == u.arcmin or unit == u.arcsec):
            pts = pts.to(u.deg)
        else:
            raise ValueError(
                f'"Only "{u.pix}" or angle units are allowed: "{u.rad}", '
                + f'""{u.deg}", "{u.arcmin}", or "{u.arcsec}"'
            )
    # If it is a list first check if the list has a point (quantities or
    # numbers), or a list of points (arrays, or other lists or tuples)
    elif isinstance(pts, list) or isinstance(pts, tuple):
        # Convert tuple to list
        if isinstance(pts, tuple):
            pts = list(pts)
        # Raise error for a mix of types in list
        if not all(isinstance(elem, type(pts[0])) for elem in pts):
            raise ValueError(f'A list of different types is not supported.')
        # List of quantities
        elif all(isinstance(elem, u.Quantity) for elem in pts):
            # Return pixels
            if all((elem.unit == u.pix) for elem in pts):
                if log: print("Input units are pixels, returning pixels.")
                for j in range(len(pts)):
                    pts[j] = pts[j].value
                pts = pts * u.pix
            # Angular units
            elif all((elem.unit != u.pix) for elem in pts):
                raise_error = False
                for elem in pts:
                    unit = elem.unit
                    if (unit != u.rad and unit != u.deg and
                            unit != u.arcmin and unit != u.arcsec):
                        raise_error = True
                # Raise an error if at least one unit is not angular
                if raise_error:
                    raise ValueError(
                        f'"Only "{u.pix}" or angle units are allowed: '
                        + f'"{u.rad}", ""{u.deg}", "{u.arcmin}", or "{u.arcsec}"'
                    )
                # Convert angular units to degrees
                for j in range(len(pts)):
                    pts[j] = pts[j].to(u.deg).value
                pts = pts * u.deg
            # Raise an error if there is a mix with pixels and other units
            else:
                raise ValueError(f'"Cannot mix "{u.pix}" with other units')
        # List of arrays
        elif all(isinstance(elem, np.ndarray) for elem in pts):
            if log: print("Input point is a list of a arrays without units")
            if log: print("Defaulting to degrees")
            pts = np.array(pts) * u.deg
        # List of lists (several points)
        elif (all(isinstance(elem, list) for elem in pts) or
              all(isinstance(elem, tuple) for elem in pts)):
            # Convert tuples to lists
            if all(isinstance(elem, tuple) for elem in pts):
                pts = [list(i) for i in pts]
            # Check if dimensions in list are coherent (same dimensions on
            # each sublist)
            num = 0
            lengths_list = []
            for i in range(len(pts)):
                num = len(pts[i])
                lengths_list.append(num)
            # If dimensions are coherent continue
            if len(np.unique(lengths_list)) == 1:
                # Raise error for a mix of types in list
                if not all(isinstance(elem, type(pts[0][0]))
                           for point in pts for elem in point):
                    raise ValueError(
                        f'A list of different types is not supported.'
                    )
                # List of lists of quantities
                elif all(isinstance(elem, u.Quantity)
                         for point in pts for elem in point):
                    # Return pixels
                    if all((elem.unit == u.pix)
                           for point in pts for elem in point):
                        if log:
                            print(f'Input unit is "{u.pix}", returning pixels.')
                        for j in range(len(pts)):
                            for k in range(len(pts[j])):
                                pts[j][k] = pts[j][k].value
                        pts = pts * u.pix
                    # Angular units
                    elif all((elem.unit != u.pix)
                             for point in pts for elem in point):
                        raise_error = False
                        for point in pts:
                            for elem in point:
                                unit = elem.unit
                                if unit != u.rad and unit != u.deg \
                                and unit != u.arcmin and unit != u.arcsec:
                                    raise_error = True
                        # Raise an error if at least one unit is not angular
                        if raise_error:
                            raise ValueError(
                                f'"Only "{u.pix}" or angle units are '
                                + f'allowed: "{u.rad}", ""{u.deg}", '
                                + f'"{u.arcmin}", or "{u.arcsec}"'
                            )
                        # Convert angular units to degrees
                        for j in range(len(pts)):
                            for k in range(len(pts[j])):
                                pts[j][k] = pts[j][k].to(u.deg).value
                        pts = pts * u.deg
                    # Raise an error if there is a mix with pixels and other units
                    else:
                        raise ValueError(
                            f'"Cannot mix "{u.pix}" with other units'
                        )
                # List of lists of numbers
                elif all((isinstance(elem, int) or isinstance(elem, float))
                         for point in pts for elem in point):
                    if log: print("Input is a list of lists of non-quantities")
                    if log: print("Defaulting to degrees")
                    pts = pts * u.deg
                # Raise error for further lists
                elif all(isinstance(elem, list)
                         for point in pts for elem in point):
                    raise ValueError(
                        f'Input is a list of lists of lists. '
                        + f'At most it can be a list of lists to represent '
                        + f'a series of points.'
                    )
                # Raise error for invalid types
                else:
                    raise ValueError(
                        f'Input is a list of lists with an invalid type: '
                        + f'{type(pts[0][0])}. \n'
                        + f'Supported types inside a nested sublist are: \n'
                        + f'{u.Quantity}, {int}, {float}'
                    )
            # Raise error for not coherent dimensions
            else:
                raise ValueError(
                    f'Input is a list of lists with uneven dimensions. '
                    + 'Each sublist must have the same dimension.'
                )
        # List of numbers
        elif all((isinstance(elem, int) or isinstance(elem, float))
                 for elem in pts):
            if log: print("Input is a list of non-quantities")
            if log: print("Defaulting to degrees")
            pts = pts * u.deg
        # Raise error for invalid types
        else:
            raise ValueError(
                f'Input is a list with an invalid type: {type(pts[0])}. \n'
                + f'Supported types inside a list are: \n'
                + f'{u.Quantity}, {int}, {float}'
                + f'sublists of {u.Quantity}, {int}, or {float} objects'
            )
    # Array of points
    elif isinstance(pts, np.ndarray):
        if log: print("Input point is an array without units")
        if log: print("Defaulting to degrees")
        pts = pts * u.deg
    # Raise error for invalid types
    else:
        raise ValueError(
            f'Input is an invalid type: {type(pts)}. \n'
            + f"Supported types for 'points' are: \n"
            + f'{u.Quantity}, {np.ndarray}, {tuple} or {list}'
        )

    # Check if input parameter is one point or an array with the last
    # dimension being 2 = array of points.
    if not pts.size > 1:
        raise ValueError(f'Invalid shape: ({1},). '
                         + 'The Last (or only) dimension has to be 2 (X, 2).')
    elif not pts.shape[-1] == 2:
        raise ValueError(f'Invalid shape: {pts.shape}. '
                         + 'The Last (or only) dimension has to be 2 (X, 2).')

    if pts.unit == u.pix:
        return pts.value
    else:
        if fitsmap.header['NAXIS'] == 2:
            fits_x, fits_y = \
                fitsmap.wcs.wcs_world2pix(pts.T[0], pts.T[1], origin)
        elif fitsmap.header['NAXIS'] == 4:
            fits_x, fits_y, dum1, dum2 = \
                fitsmap.wcs.wcs_world2pix(pts.T[0], pts.T[1], 1, 1, origin)
        
        pixel_points = np.array([fits_x, fits_y]).T

        return pixel_points


def pixel_to_world(
        points,
        fitsmap,
        origin=0,
        log=False):
    """
    Convert a set of points in pixel coordinates (python or FITS) to world
    coordinates.

    Parameters
    ----------
    points : `~numpy.ndarray`, `tuple`, or `list`.
        Input points.
    fitsmap : `~madcubapy.io.MadcubaMap` or `~astropy.nddata.CCDData`.
        Map object used to get WCS data.
    origin : `int`, optional, default=0
        Starting coordinate for image data: 0 for python pixel coordinates,
        1 for FITS coordinates.
    log : `bool`, optional
        If True, print on screen information messages on how the data is
        parsed.

    Returns
    -------
    fits_points : `~astropy.units.Quantity`
        Points converted to world coordinates with units.

    """

    # Create a deepcopy because for a list of lists [:] and copy() fail
    pts = copy.deepcopy(points)
    # If it is a quantity, continue the function to step 2 with correct units
    if isinstance(pts, u.Quantity):
        if not pts.unit == u.pix:
            raise ValueError(
                f'"{pts.unit}" not supported. Only unit allowed is "{u.pix}"'
            )
    # If it is a list first check if the list has a point (quantities or
    # numbers), or a list of points (arrays, or other lists or tuples)
    elif isinstance(pts, list) or isinstance(pts, tuple):
        # Convert tuple to list
        if isinstance(pts, tuple):
            pts = list(pts)
        # Raise error for a mix of types in list
        if not all(isinstance(elem, type(pts[0])) for elem in pts):
            raise ValueError(f'A list of different types is not supported.')
        # List of quantities
        elif all(isinstance(elem, u.Quantity) for elem in pts):
            # Only pixel units
            if not all((elem.unit == u.pix) for elem in pts):
                raise ValueError(
                    f'Input unit not supported. Only unit allowed is "{u.pix}"'
                )
            for j in range(len(pts)):
                pts[j] = pts[j].value
            pts = pts * u.pix
        # List of arrays
        elif all(isinstance(elem, np.ndarray) for elem in pts):
            if log: print("Input point is a list of a arrays without units")
            if log: print("Defaulting to degrees")
            pts = np.array(pts) * u.deg
        # # List of lists (several points)
        elif (all(isinstance(elem, list) for elem in pts) or
              all(isinstance(elem, tuple) for elem in pts)):
            # Convert tuples to lists
            if all(isinstance(elem, tuple) for elem in pts):
                pts = [list(i) for i in pts]
            # Check if dimensions in list are coherent (same dimensions on
            # each sublist)
            num = 0
            lengths_list = []
            for i in range(len(pts)):
                num = len(pts[i])
                lengths_list.append(num)
            # If dimensions are coherent continue 
            if len(np.unique(lengths_list)) == 1:
                # Raise error for a mix of types in list
                if not all(isinstance(elem, type(pts[0][0]))
                           for point in pts for elem in point):
                    raise ValueError(
                        f'A list of different types is not supported.'
                    )
                # List of lists of quantities
                elif all(isinstance(elem, u.Quantity)
                         for point in pts for elem in point):
                    # Only pixel units
                    if not all((elem.unit == u.pix)
                               for point in pts for elem in point):
                        raise ValueError(
                            f'"Input unit not supported. '
                            + f'Only unit allowed is "{u.pix}"'
                        )
                    for j in range(len(pts)):
                        for k in range(len(pts[j])):
                            pts[j][k] = pts[j][k].value
                    pts = pts * u.pix
                # List of lists of numbers
                elif all((isinstance(elem, int) or isinstance(elem, float))
                         for point in pts for elem in point):
                    if log: print("Input is a list of lists of non-quantities")
                    if log: print("Defaulting to pixels")
                    pts = pts * u.pix
                # Raise error for further lists
                elif all(isinstance(elem, list)
                         for point in pts for elem in point):
                    raise ValueError(
                        f'Input is a list of lists of lists. '
                        + f'At most it can be a list of lists to represent '
                        + f'a series of points.'
                    )
                # Raise error for invalid types
                else:
                    raise ValueError(
                        f'Input is a list of lists with an invalid type: '
                        + f'{type(pts[0][0])}. \n'
                        + f'Supported types inside a nested sublist are: \n'
                        + f'{u.Quantity}, {int}, {float}'
                    )
            # Raise error for not coherent dimensions
            else:
                raise ValueError(
                    f'Input is a list of lists with uneven dimensions. '
                    + 'Each sublist must have the same dimension.'
                )
        # List of numbers
        elif all((isinstance(elem, int) or isinstance(elem, float))
                 for elem in pts):
            if log: print("Input is a list of non-quantities")
            if log: print("Defaulting to pixel coordinates")
            pts = pts * u.pix
        # Raise error for invalid types
        else:
            raise ValueError(
                f'Input is a list with an invalid type: {type(pts[0])}. \n'
                + f'Supported types inside a list are: \n'
                + f'{u.Quantity}, {int}, {float}'
                + f'sublists of {u.Quantity}, {int}, or {float} objects'
            )
    # Array of points
    elif isinstance(pts, np.ndarray):
        if log: print("Input point is an array without units")
        if log: print("Defaulting to pixel coordinates")
        pts = pts * u.pix
    # Raise error for invalid types
    else:
        raise ValueError(
            f'Input is an invalid type: {type(pts)}. \n'
            + f"Supported types for 'points' are: \n"
            + f'{u.Quantity}, {np.ndarray}, {tuple} or {list}'
        )

    # Check if input parameter is one point or an array with the last
    # dimension being 2 = array of points.
    if not pts.size > 1:
        raise ValueError(f'Invalid shape: ({1},). '
                         + 'The Last (or only) dimension has to be 2 (X, 2).')
    elif not pts.shape[-1] == 2:
        raise ValueError(f'Invalid shape: {pts.shape}. '
                         + 'The Last (or only) dimension has to be 2 (X, 2).')
    
    if fitsmap.header['NAXIS'] == 2:
        world_x, world_y = \
            fitsmap.wcs.wcs_pix2world(pts.T[0], pts.T[1], origin)
    elif fitsmap.header['NAXIS'] == 4:
        world_x, world_y, dum1, dum2 = \
            fitsmap.wcs.wcs_pix2world(pts.T[0], pts.T[1], 1, 1, origin)
    
    world_points = np.array([world_x, world_y]).T * u.deg

    return world_points


def angle_to_pixels(
        length,
        fitsmap,
        axis='y',
        log=False):
    """
    Convert a length value (or values) in angular units to data pixels.

    Parameters
    ----------
    length : `~astropy.units.Quantity`, `~numpy.ndarray`, `list`, `tuple`, \
             `int` or `float`
        Length (or list of lengths) separating two points.
    fitsmap : `~madcubapy.io.MadcubaMap` or `~astropy.nddata.CCDData`
        Map object used to get CDELT value.
    axis : `str`, optional
        Axis in which to calculate angle deviation. Useful for images with
        non-square pixels. Possible values are ``'x'`` and ``'y'``.
    log : `bool`, optional
        If True, print on screen information messages on how the data is
        parsed.

    Returns
    -------
    pix_length : `~numpy.ndarray`
        Length in pixels.

    """

    # Quantity
    if isinstance(length, u.Quantity):
        unit = length.unit
        # Raise an error if at least one unit is not angular or pixels
        if (unit != u.pix and unit != u.rad and unit != u.deg and
                unit != u.arcmin and unit != u.arcsec):
            raise ValueError(
                f'"Only angle units are allowed: "{u.rad}", '
                + f'"{u.deg}", "{u.arcmin}", or "{u.arcsec}"'
            )
        match unit:
            case u.pix:
                if log: print("Input length in pixels, returning pixels.")
            case u.deg | u.arcmin | u.arcsec | u.rad :
                length = length.to(u.deg)
    # Array of lengths
    elif isinstance(length, np.ndarray):
        if log: print("No input units found. Defaulting to degrees.")
        length = length * u.pix
    # Length as a number
    elif isinstance(length, int) or isinstance(length, float):
        if log: print("No input units found. Defaulting to degrees.")
        length = length * u.deg
    # Several options for a list
    elif isinstance(length, list) or isinstance(length, tuple):
        # List of numbers
        if all((isinstance(elem, int) or isinstance(elem, float))
               for elem in length):
            if log: print("No input units found. Defaulting to degrees.")
            length = np.array(length) * u.deg
        # Raise error for further lists or tuples
        elif any((isinstance(elem, list) or isinstance(elem, tuple))
                 for elem in length):
            raise ValueError(
                f'Lists or tuples with more than one dimension not supported'
            )
        # List of quantities
        elif all(isinstance(elem, u.Quantity) for elem in length):
            # Convert tuple to list
            if isinstance(length, tuple):
                length = list(length)
            # Return pixels
            if all((elem.unit == u.pix) for elem in length):
                if log: print("Input units are pixels, returning pixels.")
                for j in range(len(length)):
                    length[j] = length[j].value
                length = length * u.pix
            # Angular units
            elif all((elem.unit != u.pix) for elem in length):
                raise_error = False
                for elem in length:
                    unit = elem.unit
                    if (unit != u.rad and unit != u.deg and
                            unit != u.arcmin and unit != u.arcsec):
                        raise_error = True
                # If at least one unit is not angular raise an error
                if raise_error:
                    raise ValueError(
                        f'"Only "{u.pix}" or angle units are allowed: '
                        + f'"{u.rad}", ""{u.deg}", "{u.arcmin}", or "{u.arcsec}"'
                    )
                for j in range(len(length)):
                    length[j] = length[j].to(u.deg).value
                length = length * u.deg
            # Raise an error if there is a mix with pixels and other units
            else:
                raise ValueError(f'"Cannot mix "{u.pix}" with other units')
        # Raise error for a mix of types
        elif not all(isinstance(elem, type(length[0])) for elem in length):
            raise ValueError(f'A list of different types is not supported.')
    # Raise error for invalid types
    else:
        raise ValueError(
            f'Input is an invalid type: {type(length)}. \n'
            + f"Supported types for 'points' are: \n"
            + f'{u.Quantity}, {int}, {float}, {np.ndarray}, {list}, or {tuple}'
        )
    
    if axis == 'x':
        cdelt = fitsmap.wcs.wcs.cdelt[0]
    elif axis == 'y':
        cdelt = fitsmap.wcs.wcs.cdelt[1]
    else:
        raise ValueError(f'Axis can only be "x" or "y"')

    if length.unit == u.pix:
        pix_length = length.value
    elif length.unit == u.deg:
        pix_length = length.value / cdelt

    return pix_length


def pixels_to_angle(
        pix_length,
        fitsmap,
        axis='y',
        log=False):
    """
    Convert an angle value (or values) in pixels to an angular quantity.

    Parameters
    ----------
    pix_length : `~astropy.units.Quantity`, `~numpy.ndarray`, `list`, `tuple` \
                 `int`, or `float`
        Length (or list of lengths) in pixels separating two points.
    fitsmap : `~madcubapy.io.MadcubaMap` or `~astropy.nddata.CCDData`
        Map object used to get CDELT value.
    axis : `str`, optional
        Axis in which to calculate angle deviation. Useful for images with
        non-square pixels. Possible values are ``'x'`` and ``'y'``.
    log : `bool`, optional
        If True, print on screen information messages on how the data is
        parsed.

    Returns
    -------
    length : `astropy.units.Quantity`
        Length as an angular quantity.

    """

    # Quantity, only pixels
    if isinstance(pix_length, u.Quantity):
        unit = pix_length.unit
        if unit != u.pix:
            raise ValueError(f'The only unit allowed is "{u.pix}"')
    # Array of lengths
    elif isinstance(pix_length, np.ndarray):
        if log: print("No input units found. Defaulting to pixels.")
        pix_length = pix_length * u.pix
    # Length as a number
    elif isinstance(pix_length, int) or isinstance(pix_length, float):
        if log: print("No input units found. Defaulting to pixels.")
        pix_length = pix_length * u.pix
    # Several options for a list
    elif isinstance(pix_length, list) or isinstance(pix_length, tuple):
        # List of numbers
        if all((isinstance(elem, int) or isinstance(elem, float))
               for elem in pix_length):
            if log: print("No input units found. Defaulting to pixels.")
            pix_length = np.array(pix_length) * u.pix
        # Raise error for further lists or tuples
        elif any((isinstance(elem, list) or isinstance(elem, tuple))
                 for elem in pix_length):
            raise ValueError(
                f'Lists or tuples with more than one dimension not supported'
            )
        # List of quantities (only pix supported)
        elif all(isinstance(elem, u.Quantity) for elem in pix_length):
            # Convert tuple to list
            if isinstance(pix_length, tuple):
                pix_length = list(pix_length)
            if not all((elem.unit == u.pix) for elem in pix_length):
                raise ValueError(
                    f'Input unit not supported. Only unit allowed is "{u.pix}"'
                )
            for j in range(len(pix_length)):
                pix_length[j] = pix_length[j].value
            pix_length = pix_length * u.pix
        # Raise error for a mix of types
        elif not all(isinstance(elem, type(pix_length[0]))
                     for elem in pix_length):
            raise ValueError(f'A list of different types is not supported.')
    # Raise error for invalid types
    else:
        raise ValueError(
            f'Input is an invalid type: {type(pix_length)}. \n'
            + f"Supported types for 'points' are: \n"
            + f'{u.Quantity}, {int}, {float}, {np.ndarray}, {list}, or {tuple}'
        )
    
    if axis == 'x':
        cdelt = fitsmap.wcs.wcs.cdelt[0]
    elif axis == 'y':
        cdelt = fitsmap.wcs.wcs.cdelt[1]
    else:
        raise ValueError(f'Axis can only be "x" or "y"')

    length = pix_length.value * cdelt * u.deg

    return length
