import astropy.units as u
import matplotlib.patches as patches
import numpy as np

from madcubapy.coordinates import world_to_pixel
from madcubapy.coordinates import angle_to_pixels
from madcubapy.regions.carta import _parse_crtf_coord_string
from madcubapy.regions.carta import _parse_crtf_angle_string

__all__ = [
]


def _import_pyroi_roi(data, fitsmap, **kwargs):
    """Parse a matplotlib data list and return a matplotlib patch."""
    
    match data[0]:

        case 'Rectangle':
            x = _parse_crtf_coord_string(data[1])
            y = _parse_crtf_coord_string(data[2])
            xy = np.array([
                x.value,
                y.to(x.unit).value,
            ]) * x.unit
            python_xy = world_to_pixel(xy, fitsmap)
            width = _parse_crtf_coord_string(data[3])
            width_pix = angle_to_pixels(width, fitsmap)
            height = _parse_crtf_coord_string(data[4])
            height_pix = angle_to_pixels(height, fitsmap)
            rectangle = patches.Rectangle(python_xy, width_pix, height_pix,
                                          angle=0, **kwargs)
            return rectangle

        case 'RotatedRectangle':
            x = _parse_crtf_coord_string(data[1])
            y = _parse_crtf_coord_string(data[2])
            xy = np.array([
                x.value,
                y.to(x.unit).value,
            ]) * x.unit
            python_xy = world_to_pixel(xy, fitsmap)
            width = _parse_crtf_coord_string(data[3])
            width_pix = angle_to_pixels(width, fitsmap)
            height = _parse_crtf_coord_string(data[4])
            height_pix = angle_to_pixels(height, fitsmap)
            angle = _parse_crtf_angle_string(data[5])
            angle = angle.to(u.deg).value
            rotated_rectangle = patches.Rectangle(xy=python_xy, width=width_pix, 
                                                height=height_pix, angle=angle, 
                                                **kwargs)
            return rotated_rectangle

        case 'Circle':
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

        case 'Ellipse':
            # Center
            center_X = _parse_crtf_coord_string(data[1])
            center_Y = _parse_crtf_coord_string(data[2])
            center = np.array([
                center_X.value,
                center_Y.to(center_X.unit).value,
            ]) * center_X.unit
            python_center = world_to_pixel(center, fitsmap)
            # Width
            width = _parse_crtf_coord_string(data[3])
            width_pix = angle_to_pixels(width, fitsmap)
            # Height
            height = _parse_crtf_coord_string(data[4])
            height_pix = angle_to_pixels(height, fitsmap)
            # Angle
            angle = _parse_crtf_angle_string(data[5])
            angle = angle.to(u.deg).value
            ellipse = patches.Ellipse(xy=python_center, width=width_pix,
                                      height=height_pix, angle=angle, **kwargs)
            return ellipse

        case 'Annulus':
            # Center
            center_X = _parse_crtf_coord_string(data[1])
            center_Y = _parse_crtf_coord_string(data[2])
            center = np.array([
                center_X.value,
                center_Y.to(center_X.unit).value,
            ]) * center_X.unit
            python_center = world_to_pixel(center, fitsmap)
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

        case 'Polygon':
            i = 1
            x_points = np.array([])
            y_points = np.array([])
            # -1 because there is a space at the end that adds to the
            # length and without the -1, it gets read as a point and fails
            for i in range(1, len(data)-1, 2):
                # Center
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