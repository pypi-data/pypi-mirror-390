import astropy.units as u
import matplotlib.patches as patches
import numpy as np

from madcubapy.utils.numeric import _is_number
from madcubapy.coordinates import fits_to_python
from madcubapy.coordinates import world_to_pixel
from madcubapy.coordinates import angle_to_pixels
from madcubapy.regions.carta import _parse_crtf_coord_string

__all__ = [
]


def _parse_mcroi_coord_string(
        coord_string,
        frame,
        system):
    """
    Extract a coordinate and its units from a mcroi string.

    Parameters
    ----------
    coord_string : `str`
        String containing data from a .crtf ROI file.
    frame : `str`
        String containing the coordinates frame used.
    system : `str`
        String containing the coordinates system used.

    Returns
    -------
    quantity : `~astropy.units.Quantity`
        Singular coordinate with unit.

    """

    if frame == "Pixel" or frame == "Pixel\n":
        quantity = float(coord_string) * u.pix
    elif frame == "World" or frame == "World\n":
        coords_units = ["deg", "arcmin", "arcsec", "rad"]
        units_found = False
        quantity = None
        for i in range(len(coords_units)):
            if coord_string.endswith(coords_units[i]):
                units_found = True
                units = coords_units[i]
                match units:
                    case "deg":
                        quantity = float(coord_string[:-3]) * u.deg
                    case "arcmin":
                        quantity = float(coord_string[:-6]) * u.arcmin
                    case "arcsec":
                        quantity = float(coord_string[:-6]) * u.arcsec
                    case "rad":
                        quantity = float(coord_string[:-3]) * u.rad
        if units_found == False:
            if _is_number(coord_string):
                print("Units were not found for frame World. "
                    + "Defaulting to fits pixel coordinates.")
                quantity = float(coord_string) * u.pix
            else:
                raise ValueError("Incorrect string for units.")
    else:
        raise ValueError("Incorrect string for frame.")

    return quantity


def _import_mcroi_roi(data, frame, system, fitsmap, **kwargs):
    """Parse a madcuba data list and return a matplotlib patch."""

    match data[0]:
        case 'makePoint':
            point_X = _parse_mcroi_coord_string(data[1], frame, system)
            point_Y = _parse_mcroi_coord_string(data[2], frame, system)
            point = np.array([
                point_X.value,
                point_Y.to(point_X.unit).value,
            ]) * point_X.unit
            fits_point = world_to_pixel(point, fitsmap, origin=1)
            python_point = fits_to_python(fits_point)
            point = patches.Circle(xy=python_point, radius=0.2, **kwargs)
            return point

        case 'makeLine' | 'makePolyline':
            x_points = np.array([])
            y_points = np.array([])
            # Read the data jumping by 2
            for i in range(1, len(data), 2):
                # End loop if vertices end
                if data[i].startswith(';'):
                    break
                # Parse vertices coordinates and add them to arrays
                vertex_X = _parse_mcroi_coord_string(data[i], frame, system)
                vertex_Y = _parse_mcroi_coord_string(data[i+1], frame, system)
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

        case 'makeRectangle':
            # Lower left corner
            x1 = _parse_mcroi_coord_string(data[1], frame, system)
            y1 = _parse_mcroi_coord_string(data[2], frame, system)
            xy = np.array([
                x1.value,
                y1.to(x1.unit).value,
            ]) * x1.unit
            fits_xy = world_to_pixel(xy, fitsmap, origin=1)
            python_xy = fits_to_python(fits_xy)
            # Widths
            width = _parse_mcroi_coord_string(data[3], frame, system)
            width_pix = angle_to_pixels(width, fitsmap)
            height = _parse_mcroi_coord_string(data[4], frame, system)
            height_pix = angle_to_pixels(height, fitsmap)
            # MADCUBA codes the entire integer pixel for the corner of the box,
            # but the integer value is in the center, we have to shift to the
            # lower left corner of the pixel for matplotlib (-0.5).
            xy = python_xy - 0.5
            rectangle = patches.Rectangle(xy, width_pix, height_pix, **kwargs)
            return rectangle

        case 'makeOval':
            # Lower left corner
            x1 = _parse_mcroi_coord_string(data[1], frame, system)
            y1 = _parse_mcroi_coord_string(data[2], frame, system)
            xy = np.array([
                x1.value,
                y1.to(x1.unit).value,
            ]) * x1.unit
            fits_xy = world_to_pixel(xy, fitsmap, origin=1)
            python_xy = fits_to_python(fits_xy)
            # Widths
            width = _parse_mcroi_coord_string(data[3], frame, system)
            width_pix = angle_to_pixels(width, fitsmap)
            height = _parse_mcroi_coord_string(data[4], frame, system)
            height_pix = angle_to_pixels(height, fitsmap)
            # MADCUBA codes the entire integer pixel for the corner of the box,
            # but the integer value is in the center, we have to shift to the
            # lower left corner of the pixel for matplotlib (-0.5).
            python_center = np.array([python_xy[0] + width_pix/2,
                                      python_xy[1] + height_pix/2]) - 0.5
            oval = patches.Ellipse(xy=python_center, width=width_pix,
                                        height=height_pix, angle=0, **kwargs)
            return oval

        case 'makeEllipse':
            # XY1
            x1 = _parse_mcroi_coord_string(data[1], frame, system)
            y1 = _parse_mcroi_coord_string(data[2], frame, system)
            xy1 = np.array([
                x1.value,
                y1.to(x1.unit).value,
            ]) * x1.unit
            fits_xy1 = world_to_pixel(xy1, fitsmap, origin=1)
            python_xy1 = fits_to_python(fits_xy1)
            # XY3
            x3 = _parse_mcroi_coord_string(data[3], frame, system)
            y3 = _parse_mcroi_coord_string(data[4], frame, system)
            xy3 = np.array([
                x3.value,
                y3.to(x3.unit).value,
            ]) * x3.unit
            fits_xy3 = world_to_pixel(xy3, fitsmap, origin=1)
            python_xy3 = fits_to_python(fits_xy3)
            # Aspect Ratio
            aspect = float(data[5])
            # Calculate mpl parameters
            python_center = np.array([(python_xy1[0] + python_xy3[0]) / 2,
                                      (python_xy1[1] + python_xy3[1]) / 2])
            delta_x = python_xy3[0] - python_xy1[0]
            delta_y = python_xy3[1] - python_xy1[1]
            bmaj = np.sqrt((delta_x)**2 + (delta_y)**2)
            bmin = aspect * bmaj
            # -delta_x because mpl works with anti-clockwise angles
            angle = np.arcsin((-delta_x) / bmaj) * u.rad
            if delta_y < 0: angle = np.pi * u.rad - angle
            # convert negative angle to positive angle for first quadrant
            if angle < 0: angle = 2*np.pi * u.rad + angle
            angle_deg = angle.to(u.deg).value
            ellipse = patches.Ellipse(xy=python_center, width=bmin,
                                      height=bmaj, angle=angle_deg, **kwargs)
            return ellipse

        case 'makePolygon':
            x_points = np.array([])
            y_points = np.array([])
            # Read the data jumping by 2
            for i in range(1, len(data), 2):
                # End loop if vertices end
                if data[i].startswith(';'):
                    break
                # Parse vertices coordinates and add them to arrays
                vertex_X = _parse_mcroi_coord_string(data[i], frame, system)
                vertex_Y = _parse_mcroi_coord_string(data[i+1], frame, system)
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

        case 'makeAnnulus':
            # The Annulus was coded to accept any units separately for the
            # parameters, this is why it uses the Crtf parse function.
            # Center
            center_X = _parse_crtf_coord_string(data[1])
            center_Y = _parse_crtf_coord_string(data[2])
            center = np.array([
                center_X.value,
                center_Y.to(center_X.unit).value,
            ]) * center_X.unit
            # Change Fits pix to ImageJ pix because the PIX in the madcuba
            # annulus file are fits pixels
            fits_center = world_to_pixel(center, fitsmap, origin=1)
            python_center = fits_to_python(fits_center)
            # Radii
            inner_radius = _parse_crtf_coord_string(data[3])
            outer_radius = _parse_crtf_coord_string(data[4])
            if inner_radius > outer_radius:
                raise ValueError(
                    f"Inner radius (r1={inner_radius}) cannot be "
                    + f"larger than the outer radius (r2={outer_radius})")
            inner_radius_pix = angle_to_pixels(inner_radius, fitsmap)
            outer_radius_pix = angle_to_pixels(outer_radius, fitsmap)
            width_pix = outer_radius_pix - inner_radius_pix
            annulus = patches.Annulus(xy=python_center, r=outer_radius_pix,
                                        width=width_pix, angle=0, **kwargs)
            return annulus
        case _:
            print("ROI type not valid")