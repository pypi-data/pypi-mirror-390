import astropy.units as u
import matplotlib.patches as patches
import numpy as np

from madcubapy.coordinates import fits_to_python
from madcubapy.coordinates import world_to_pixel
from madcubapy.coordinates import angle_to_pixels

__all__ = [
]


def _parse_ds9_coord_string(
        coord,
        system):
    """
    Extract a coordinate and its units from a ds9 string.

    Parameters
    ----------
    coord : `str`
        String containing data from a .ds9 ROI file.
    system : `str`
        String containing the coordinates system used.

    Returns
    -------
    quantity : `~astropy.units.Quantity`
        Singular coordinate with its unit.

    """

    if system == "image" or system == "image\n":
        quantity = float(coord) * u.pix
    elif system == "icrs" or system == "icrs\n":
        coords_units = ["'", '"', "rad", "hdms"]
        units_found = False
        quantity = None
        for i in range(len(coords_units)):
            if coord.endswith(coords_units[i]):
                units_found = True
                units = coords_units[i]
                match units:
                    case "'":
                        quantity = float(coord[:-1]) * u.arcmin
                    case '"':
                        quantity = float(coord[:-1]) * u.arcsec
        if not units_found:
            quantity = float(coord[:]) * u.deg
    else:
        quantity = 1 * u.deg

    return quantity


def _parse_ds9_angle_string(
        angle_string):
    """
    Extract an angle from a ds9 string and convert its units to
    degrees.

    Parameters
    ----------
    angle_string : `str`
        String containing the angle value followed by its units.

    Returns
    -------
    angle : `~astropy.units.Quantity`
        Angle as a quantity object.

    """

    coords_units = ["'", '"', "rad", "hdms"]
    units_found = False
    angle = None
    for i in range(len(coords_units)):
        if angle_string.endswith(coords_units[i]):
            units_found = True
            units = coords_units[i]
            match units:
                case "'":
                    angle = float(angle_string[:-1]) * u.arcmin
                case '"':
                    angle = float(angle_string[:-1]) * u.arcsec
    if not units_found:
        angle = float(angle_string[:]) * u.deg

    return angle


def _import_ds9_roi(data, system, fitsmap, **kwargs):
    """Parse a ds9 data list and return a matplotlib patch."""

    match data[0]:
        case 'point':
            point_X = _parse_ds9_coord_string(data[1], system)
            point_Y = _parse_ds9_coord_string(data[2], system)
            point = np.array([
                point_X.value,
                point_Y.to(point_X.unit).value,
            ]) * point_X.unit
            fits_point = world_to_pixel(point, fitsmap, origin=1)
            python_point = fits_to_python(fits_point)
            point = patches.Circle(xy=python_point, radius=0.2, **kwargs)
            return point
        
        case 'line' | 'polyline':
            x_points = np.array([])
            y_points = np.array([])
            # Read the data jumping by 2
            for i in range(1, len(data), 2):
                # End loop if vertices end
                if data[i].startswith('#'):
                    break
                # Parse vertices coordinates and add them to arrays
                vertex_X = _parse_ds9_coord_string(data[i], system)
                vertex_Y = _parse_ds9_coord_string(data[i+1], system)
                vertex = np.array([
                    vertex_X.value,
                    vertex_Y.to(vertex_X.unit).value,
                ]) * vertex_X.unit
                fits_vertex = world_to_pixel(vertex, fitsmap, origin=1)
                python_vertex = fits_to_python(fits_vertex)
                x_points = np.append(x_points, python_vertex[0])
                y_points = np.append(y_points, python_vertex[1])
            # Transpose to have each point in a dimension
            points = np.array([x_points, y_points]).T
            line = patches.Polygon(xy=points, closed=False, fill=False,
                                    **kwargs)
            return line

        case 'box':  # Box and Rotated box are the same in ds9
            # Center
            center_X = _parse_ds9_coord_string(data[1], system)
            center_Y = _parse_ds9_coord_string(data[2], system)
            center = np.array([
                center_X.value,
                center_Y.to(center_X.unit).value,
            ]) * center_X.unit
            fits_center = world_to_pixel(center, fitsmap, origin=1)
            python_center = fits_to_python(fits_center)
            # Widths
            width = _parse_ds9_coord_string(data[3], system)
            width_pix = angle_to_pixels(width, fitsmap)
            height = _parse_ds9_coord_string(data[4], system)
            height_pix = angle_to_pixels(height, fitsmap)
            xy = np.array([python_center[0] - width_pix/2,
                            python_center[1] - height_pix/2])
            # Angle
            angle = _parse_ds9_angle_string(data[5])
            angle = angle.to(u.deg).value
            rotated_rectangle = patches.Rectangle(xy, width_pix, height_pix,
                                                    angle=angle,
                                                    rotation_point='center',
                                                    **kwargs)
            return rotated_rectangle

        case 'circle':
            # Center
            center_X = _parse_ds9_coord_string(data[1], system)
            center_Y = _parse_ds9_coord_string(data[2], system)
            center = np.array([
                center_X.value,
                center_Y.to(center_X.unit).value,
            ]) * center_X.unit
            fits_center = world_to_pixel(center, fitsmap, origin=1)
            python_center = fits_to_python(fits_center)
            # Radius
            radius = _parse_ds9_coord_string(data[3], system)
            radius_pix = angle_to_pixels(radius, fitsmap)
            circle = patches.Circle(xy=python_center, radius=radius_pix,
                                    **kwargs)
            return circle

        case 'ellipse':
            # Center
            center_X = _parse_ds9_coord_string(data[1], system)
            center_Y = _parse_ds9_coord_string(data[2], system)
            center = np.array([
                center_X.value,
                center_Y.to(center_X.unit).value,
            ]) * center_X.unit
            fits_center = world_to_pixel(center, fitsmap, origin=1)
            python_center = fits_to_python(fits_center)
            # Width
            ax_x = _parse_ds9_coord_string(data[4], system)
            ax_x_pix = angle_to_pixels(ax_x, fitsmap)
            width = ax_x_pix * 2
            # Height
            ax_y = _parse_ds9_coord_string(data[3], system)
            ax_y_pix = angle_to_pixels(ax_y, fitsmap)
            height = ax_y_pix * 2
            # Angle
            angle = _parse_ds9_angle_string(data[5])
            # angle of ellipse in ds9 is offset by 90 deg
            angle = angle.to(u.deg).value - 90
            ellipse = patches.Ellipse(xy=python_center, width=width,
                                        height=height, angle=angle, **kwargs)
            return ellipse

        case 'polygon':
            x_points = np.array([])
            y_points = np.array([])
            # Read the data jumping by 2
            for i in range(1, len(data), 2):
                # End loop if vertices end
                if data[i].startswith('#'):
                    break
                # Parse vertices coordinates and add them to arrays
                vertex_X = _parse_ds9_coord_string(data[i], system)
                vertex_Y = _parse_ds9_coord_string(data[i+1], system)
                vertex = np.array([
                    vertex_X.value,
                    vertex_Y.to(vertex_X.unit).value,
                ]) * vertex_X.unit
                fits_vertex = world_to_pixel(vertex, fitsmap, origin=1)
                python_vertex = fits_to_python(fits_vertex)
                x_points = np.append(x_points, python_vertex[0])
                y_points = np.append(y_points, python_vertex[1])
            # Transpose to have each point in a dimension
            points = np.array([x_points, y_points]).T
            polygon = patches.Polygon(xy=points, closed=True, **kwargs)
            return polygon