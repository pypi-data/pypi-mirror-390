import astropy.units as u
import matplotlib.patches as patches
import numpy as np

from madcubapy.utils.numeric import _is_number
from madcubapy.coordinates import world_to_pixel
from madcubapy.coordinates import angle_to_pixels

__all__ = [
]


def _parse_crtf_coord_string(
        coord_string):
    """
    Extract a coordinate and its units from a crtf string.

    Parameters
    ----------
    coord_string : `str`
        String containing data from a .crtf ROI file.

    Returns
    -------
    quantity : `~astropy.units.Quantity`
        Singular coordinate with unit.

    """

    coords_units = ["pix", "deg", "arcmin", "arcsec", "rad", "hdms"]
    units_found = False
    quantity = None
    for i in range(len(coords_units)):
        if coord_string.endswith(coords_units[i]):
            units_found = True
            units = coords_units[i]
            match units:
                case "pix":
                    quantity = float(coord_string[:-3]) * u.pix
                case "deg":
                    quantity = float(coord_string[:-3]) * u.deg
                case "arcmin":
                    quantity = float(coord_string[:-6]) * u.arcmin
                case "arcsec":
                    quantity = float(coord_string[:-6]) * u.arcsec
                case "rad":
                    quantity = float(coord_string[:-3]) * u.rad
                case "hdms":
                    quantity = float(coord_string[:-4])

    if units_found == False:
        if _is_number(coord_string):
            print("Units were not found. Defaulting to fits pixel coords.")
            quantity = float(coord_string) * u.pix
        else:
            raise ValueError("Incorrect string for units.")

    return quantity


def _parse_crtf_angle_string(
        angle_string):
    """
    Extract an angle from a string and convert its units to degrees.

    Parameters
    ----------
    angle_string : `str`
        String containing the angle value followed by its units.

    Returns
    -------
    angle : `~astropy.units.Quantity`
        Angle as a quantity object.

    """

    coords_units = ["pix", "deg", "arcmin", "arcsec", "rad"]
    units_found = False
    angle = None
    for i in range(len(coords_units)):
        if angle_string.endswith(coords_units[i]):
            units_found = True
            units = coords_units[i]
            match units:
                case "pix":
                    angle = float(angle_string[:-3]) * u.pix
                case "deg":
                    angle = float(angle_string[:-3]) * u.deg
                case "arcmin":
                    angle = float(angle_string[:-6]) * u.arcmin
                case "arcsec":
                    angle = float(angle_string[:-6]) * u.arcsec
                case "rad":
                    angle = float(angle_string[:-3]) * u.rad

    if units_found == False:
        if _is_number(angle_string):
            print("Units were not found. Defaulting to fits pixel coords.")
            angle = float(angle_string) * u.pix
        else:
            raise ValueError("Incorrect string for units.")

    return angle


def _import_crtf_roi(data, fitsmap, **kwargs):
    """Parse a crtf data list and return a matplotlib patch."""

    match data[0]:
        case 'symbol':
            point_X = _parse_crtf_coord_string(data[1])
            point_Y = _parse_crtf_coord_string(data[2])
            point = np.array([
                point_X.value,
                point_Y.to(point_X.unit).value,
            ]) * point_X.unit
            python_point = world_to_pixel(point, fitsmap)
            point = patches.Circle(xy=python_point, radius=0.2, **kwargs)
            return point

        case 'line' | 'polyline':
            x_points = np.array([])
            y_points = np.array([])
            # Read the data jumping by 2
            for i in range(1, len(data), 2):
                # End loop if vertices end
                if data[i].startswith('coord='):
                    break
                # Parse vertices coordinates and add them to arrays
                vertex_X = _parse_crtf_coord_string(data[i])
                vertex_Y = _parse_crtf_coord_string(data[i+1])
                vertex = np.array([
                    vertex_X.value,
                    vertex_Y.to(vertex_X.unit).value,
                ]) * vertex_X.unit
                python_vertex = world_to_pixel(vertex, fitsmap)
                x_points = np.append(x_points, python_vertex[0])
                y_points = np.append(y_points, python_vertex[1])
            # Transpose to have each point in a dimension
            points = np.array([x_points, y_points]).T
            line = patches.Polygon(xy=points, closed=False, fill=False,
                                    **kwargs)
            return line
        
        case 'box':  # CASA rectangle
            # Lower-left corner
            x1 = _parse_crtf_coord_string(data[1])
            y1 = _parse_crtf_coord_string(data[2])
            x1y1 = np.array([
                x1.value,
                y1.to(x1.unit).value,
            ]) * x1.unit
            python_x1y1 = world_to_pixel(x1y1, fitsmap)
            # Upper-right corner
            x2 = _parse_crtf_coord_string(data[3])
            y2 = _parse_crtf_coord_string(data[4])
            x2y2 = np.array([
                x2.value,
                y2.to(x2.unit).value,
            ]) * x2.unit
            python_x2y2 = world_to_pixel(x2y2, fitsmap)
            # Widths
            width_pix = python_x2y2[0] - python_x1y1[0]
            height_pix = python_x2y2[1] - python_x1y1[1]
            rectangle = patches.Rectangle(python_x1y1, width_pix,
                                            height_pix, angle=0, **kwargs)
            return rectangle

        case 'centerbox':  # CARTA Rectangle
            # Center
            center_X = _parse_crtf_coord_string(data[1])
            center_Y = _parse_crtf_coord_string(data[2])
            center = np.array([
                center_X.value,
                center_Y.to(center_X.unit).value,
            ]) * center_X.unit
            python_center = world_to_pixel(center, fitsmap)
            # Widths
            width = _parse_crtf_coord_string(data[3])
            width_pix = angle_to_pixels(width, fitsmap)
            height = _parse_crtf_coord_string(data[4])
            height_pix = angle_to_pixels(height, fitsmap)
            xy = np.array([python_center[0] - width_pix/2,
                            python_center[1] - height_pix/2])
            rectangle = patches.Rectangle(xy, width_pix, height_pix,
                                            angle=0, **kwargs)
            return rectangle

        case 'rotbox':
            # Center
            center_X = _parse_crtf_coord_string(data[1])
            center_Y = _parse_crtf_coord_string(data[2])
            center = np.array([
                center_X.value,
                center_Y.to(center_X.unit).value,
            ]) * center_X.unit
            python_center = world_to_pixel(center, fitsmap)
            # Widths
            width = _parse_crtf_coord_string(data[3])
            width_pix = angle_to_pixels(width, fitsmap)
            height = _parse_crtf_coord_string(data[4])
            height_pix = angle_to_pixels(height, fitsmap)
            xy = np.array([python_center[0] - width_pix/2,
                            python_center[1] - height_pix/2])
            # Angle
            angle = _parse_crtf_angle_string(data[5])
            angle = angle.to(u.deg).value
            rotated_rectangle = patches.Rectangle(xy, width_pix, height_pix,
                                                    angle=angle,
                                                    rotation_point='center',
                                                    **kwargs)
            return rotated_rectangle

        case 'circle':
            # Center
            center_X = _parse_crtf_coord_string(data[1])
            center_Y = _parse_crtf_coord_string(data[2])
            center = np.array([
                center_X.value,
                center_Y.to(center_X.unit).value,
            ]) * center_X.unit
            python_center = world_to_pixel(center, fitsmap)
            # Radius
            radius = _parse_crtf_coord_string(data[3])
            radius_pix = angle_to_pixels(radius, fitsmap)
            circle = patches.Circle(xy=python_center, radius=radius_pix,
                                    **kwargs)
            return circle
        
        case 'ellipse':
            # Center
            center_X = _parse_crtf_coord_string(data[1])
            center_Y = _parse_crtf_coord_string(data[2])
            center = np.array([
                center_X.value,
                center_Y.to(center_X.unit).value,
            ]) * center_X.unit
            python_center = world_to_pixel(center, fitsmap)
            # Width
            ax_x = _parse_crtf_coord_string(data[4])
            ax_x_pix = angle_to_pixels(ax_x, fitsmap)
            width = ax_x_pix * 2
            # Height
            ax_y = _parse_crtf_coord_string(data[3])
            ax_y_pix = angle_to_pixels(ax_y, fitsmap)
            height = ax_y_pix * 2
            # Angle
            angle = _parse_crtf_angle_string(data[5])
            angle = angle.to(u.deg).value
            ellipse = patches.Ellipse(xy=python_center, width=width,
                                        height=height, angle=angle, **kwargs)
            return ellipse

        case 'poly':
            x_points = np.array([])
            y_points = np.array([])
            # Read the data jumping by 2
            for i in range(1, len(data), 2):
                # End loop if vertices end
                if data[i].startswith('coord='):
                    break
                # Parse vertices coordinates and add them to arrays
                vertex_X = _parse_crtf_coord_string(data[i])
                vertex_Y = _parse_crtf_coord_string(data[i+1])
                vertex = np.array([
                    vertex_X.value,
                    vertex_Y.to(vertex_X.unit).value,
                ]) * vertex_X.unit
                python_vertex = world_to_pixel(vertex, fitsmap)
                x_points = np.append(x_points, python_vertex[0])
                y_points = np.append(y_points, python_vertex[1])
            # Transpose to have each point in a dimension
            points = np.array([x_points, y_points]).T
            polygon = patches.Polygon(xy=points, closed=True, **kwargs)
            return polygon

        case _:
            print("ROI type not valid")
