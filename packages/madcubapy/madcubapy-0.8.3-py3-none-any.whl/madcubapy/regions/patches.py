import astropy.units as u
import matplotlib.patches as patches
import numpy as np

from madcubapy.coordinates import pixel_to_world
from madcubapy.coordinates import pixels_to_angle

__all__ = [
]


# from regions/02_patches.ipynb
def _export_roi_as_pyroi(
        patch,
        output,
        coord_frame="image",
        fitsmap=None,
        patch_info=None):
    """
    Export a RoI as a .pyroi file

    Parameters
    ----------
    patch : `~matplotlib.patches.Patch`
        Patch object to export.
    output : `str` or `~pathlib.Path`
        Path of the .pyroi file to be created.
    coord_frame : `str`
        Coordinate system to be used.
    fitsmap : `~madcubapy.io.MadcubaMap` or ~astropy.nddata.CCDData`
        Map object used to transform coordinates.
    patch_info : `str`
        Custom information text to add to the .pyroi file.

    """

    if not isinstance(patch, patches.Patch):
        raise TypeError("Input object type is not a Patch. " +
            f"Type of input object: {type(patch)}")

    # In the type of a matplotlib Patch the name starts at index 27
    patch_type = str(type(patch))[27:-2]
    if not patch_info: overwrite_info = True
    else: overwrite_info = False

    match patch_type:
        case 'Rectangle':
            xy = patch.get_xy()
            width = patch.get_width()
            height = patch.get_height()
            angle = patch.get_angle()
            if coord_frame == "world":
                xy = pixel_to_world(np.array(xy), fitsmap).to(u.deg).value
                width = pixels_to_angle(np.array(width), fitsmap).to(u.arcsec).value
                height = pixels_to_angle(np.array(height), fitsmap).to(u.arcsec).value
                patch_data = f'({xy[0]:.8f}deg, {xy[1]:.8f}deg), ' \
                             + f'{width:.5f}arcsec, {height:.5f}arcsec'
            else:
                patch_data = f'({xy[0]}pix, {xy[1]}pix), {width}pix, {height}pix'
            if overwrite_info: patch_info = 'Rectangle((x1, y1), width, height)'
            # For rotated rectangle
            if angle != 0:
                patch_type = 'Rotated' + patch_type
                if overwrite_info: patch_info = 'Rotated' + patch_info[:-1] + ', angle)'
                patch_data = patch_data + f', {angle}deg'

        case 'Circle':
            center = patch.get_center()
            radius = patch.get_radius()
            if coord_frame == "world":
                center = pixel_to_world(np.array(center), fitsmap).to(u.deg).value
                radius = pixels_to_angle(np.array(radius), fitsmap).to(u.arcsec).value
                patch_data = f'({center[0]:.8f}deg, {center[1]:.8f}deg), ' \
                             + f'{radius:.5f}arcsec'
            else:
                patch_data = f'({center[0]}pix, {center[1]}pix), {radius}pix'
            if overwrite_info: patch_info = 'Circle((x, y), radius)'

        case 'Ellipse':
            center = patch.get_center()
            width = patch.get_width()
            height = patch.get_height()
            angle = patch.get_angle() # Anti-clockwise angle of vertical axis
            if coord_frame == "world":
                center = pixel_to_world(np.array(center), fitsmap).to(u.deg).value
                width = pixels_to_angle(np.array(width), fitsmap).to(u.arcsec).value
                height = pixels_to_angle(np.array(height), fitsmap).to(u.arcsec).value
                patch_data = f'({center[0]:.8f}deg, {center[1]:.8f}deg), ' \
                             + f'{width:.5f}arcsec, {height:.5f}arcsec, {angle}deg'
            else:
                patch_data = f'({center[0]}pix, {center[1]}pix), ' \
                             + f'{width}pix, {height}pix, {angle}deg'
            if overwrite_info: patch_info = 'Ellipse((x, y), width, height, angle)'
        
        case 'Annulus':
            center = patch.get_center()
            radii = patch.get_radii() # Semi-major and semi-minor outer radius
            width = patch.get_width()
            r2 = radii[0]  # Outer radius
            r1 = r2 - width  # Inner radius
            if radii[0] == radii[1]: # If circular shape
                if coord_frame == "world":
                    center = pixel_to_world(np.array(center), fitsmap).to(u.deg).value
                    r2 = pixels_to_angle(np.array(r2), fitsmap).to(u.arcsec).value
                    r1 = pixels_to_angle(np.array(r1), fitsmap).to(u.arcsec).value
                    patch_data = f'({center[0]:.8f}deg, {center[1]:.8f}deg), ' \
                                 + f'{r1:.5f}arcsec, {r2:.5f}arcsec'
                else:
                    patch_data = f'({center[0]}pix, {center[1]}pix), ' \
                                 + f'{r1}pix, {r2}pix'
                if overwrite_info: patch_info = 'Annulus((x, y), r1, r2)'

        case 'Polygon':
            verts = patch.get_xy()
            patch_data = ''
            for vertex in verts:
                if coord_frame == "world":
                    vertex = pixel_to_world(np.array(vertex), fitsmap).to(u.deg).value
                    string = f'{vertex[0]:.8f}deg, {vertex[1]:.8f}deg, '
                else:
                    string = f'{vertex[0]}pix, {vertex[1]}pix, '
                patch_data = patch_data + string
            patch_data = patch_data[:-2]  # Delete last comma and space
            if overwrite_info: patch_info = 'Polygon(x1, y1, x2, y2, x3, y3, ... )'
        
        case _:
            print("Patch type not coded")
    
    # Write patch into .pyroi file
    with open(output, 'w') as f:
        f.write('# Matplotlib ROI: ' + patch_info)
        f.write('\n')
        f.write(f'{patch_type}({patch_data})')


# from regions/02_patches.ipynb
def _export_roi_as_crtf(
        patch,
        output,
        coord_frame="image",
        fitsmap=None,
        patch_info=None):
    """
    Export a RoI as a .crtf file

    Parameters
    ----------
    patch : `~matplotlib.patches.Patch`
        Patch object to export.
    output : `str` or `~pathlib.Path`
        Path of the .pyroi file to be created.
    coord_frame : `str`
        "world" or "image" (pixels) coordinates.
    fitsmap : `~madcubapy.io.MadcubaMap` or ~astropy.nddata.CCDData`
        Map object used to transform coordinates.
    patch_info : `str`
        Custom information text to add to the .crtf file.

    """

    if not isinstance(patch, patches.Patch):
        raise TypeError("Input object type is not a Patch. " + \
            f"Type of input object: {type(patch)}")

    # In the type of a matplotlib Patch the name starts at index 27
    patch_type = str(type(patch))[27:-2]
    if not patch_info: overwrite_info = True
    else: overwrite_info = False

    match patch_type:
        case 'Rectangle':
            roi_name = 'centerbox'
            center = patch.get_center()
            width = patch.get_width()
            height = patch.get_height()
            angle = patch.get_angle()
            if coord_frame == "world":
                center = pixel_to_world(np.array(center), fitsmap).to(u.deg).value
                width = pixels_to_angle(np.array(width), fitsmap).to(u.arcsec).value
                height = pixels_to_angle(np.array(height), fitsmap).to(u.arcsec).value
                patch_data = f'[{center[0]:.8f}deg, {center[1]:.8f}deg], ' \
                             + f'[{width:.4f}arcsec, {height:.4f}arcsec]'
            else:
                patch_data = f'[{center[0]}pix, {center[1]}pix], ' \
                             + f'[{width}pix, {height}pix]'
            if overwrite_info: patch_info = 'centerbox [[x1, y1], [width, height]] ' \
                         + 'coord=..., params...'
            # For rotated rectangle
            if angle != 0:
                roi_name = 'rotbox'
                if overwrite_info: patch_info = 'rotbox [[x1, y1], [width, height], angle] ' \
                             + 'coord=..., params...'
                patch_data = patch_data + f', {angle}deg'

        case 'Circle':
            roi_name = 'circle'
            center = patch.get_center()
            radius = patch.get_radius()
            if coord_frame == "world":
                center = pixel_to_world(np.array(center), fitsmap).to(u.deg).value
                radius = pixels_to_angle(np.array(radius), fitsmap).to(u.arcsec).value
                patch_data = f'[{center[0]:.8f}deg, {center[1]:.8f}deg], ' \
                             + f'{radius:.4f}arcsec'
            else:
                patch_data = f'[{center[0]}pix, {center[1]}pix], {radius}pix'
            if overwrite_info: patch_info = 'Circle [[x1, y1], radius] coord=..., params...'

        case 'Ellipse':
            roi_name = 'ellipse'
            center = patch.get_center()
            width = patch.get_width()/2
            height = patch.get_height()/2
            angle = patch.get_angle() # Anti-clockwise angle of vertical axis
            if coord_frame == "world":
                center = pixel_to_world(np.array(center), fitsmap).to(u.deg).value
                width = pixels_to_angle(np.array(width), fitsmap).to(u.arcsec).value
                height = pixels_to_angle(np.array(height), fitsmap).to(u.arcsec).value
                patch_data = f'[{center[0]:.8f}deg, {center[1]:.8f}deg], ' \
                             + f'[{height:.5f}arcsec, {width:.5f}arcsec], ' \
                             + f'{angle}deg'
            else:
                patch_data = f'[{center[0]}pix, {center[1]}pix], ' \
                             + f'[{height}pix, {width}pix], {angle}deg'
            if overwrite_info:
                patch_info = 'ellipse [[x1, y1], [height, width], angle] ' \
                           + 'coord=..., params...'

        case 'Polygon':
            roi_name = 'poly'
            verts = patch.get_xy()
            patch_data = ''
            for vertex in verts:
                if coord_frame == "world":
                    vertex = pixel_to_world(np.array(vertex), fitsmap).to(u.deg).value
                    string = f'[{vertex[0]:.8f}deg, {vertex[1]:.8f}deg], '
                else:
                    string = f'[{vertex[0]}pix, {vertex[1]}pix], '
                patch_data = patch_data + string
            patch_data = patch_data[:-2]  # Delete last comma and space
            if overwrite_info: 
                patch_info = 'poly [[x1, y1], [x2, y2], [x3, y3], ... ] ' \
                           + 'coord=..., params...'
        
        case _:
            print("Patch type not coded")
    
    # Write patch into .pyroi file
    with open(output, 'w') as f:
        f.write('#CRTFv0 CASA Region Text Format version 0')
        f.write('\n')
        f.write(f'{roi_name} [{patch_data}] coord=ICRS, corr=[I]')
