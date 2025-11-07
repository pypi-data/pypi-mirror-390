import re

from madcubapy.regions.carta import _import_crtf_roi
from madcubapy.regions.madcuba import _import_mcroi_roi
from madcubapy.regions.ds9 import _import_ds9_roi
from madcubapy.regions.pyroi import _import_pyroi_roi
from madcubapy.regions.patches import _export_roi_as_pyroi
from madcubapy.regions.patches import _export_roi_as_crtf

__all__ = [
    'export_roi',
    'import_roi',
]


def export_roi(
        patch,
        filename,
        format="pyroi",
        coord_frame="image",
        fitsmap=None,
        patch_info=None):
    """
    Export a region of interest (ROI) to a specified file format.

    Parameters
    ----------
    patch : `~matplotlib.patches.Patch`
        Patch object to export.
    filename : `str` or `~pathlib.Path`
        Path of the output file.
    format : `str`, optional
        The export format. Options: ``'pyroi'`` (default), ``'crtf'``.
    coord_frame : `str`
        Coordinate frame to use.  Options: ``'world'`` and ``'image'``.
    fitsmap : `~madcubapy.io.MadcubaMap` or `~astropy.nddata.CCDData`
        Map object used to transform coordinates.
    patch_info : `str`
        Custom information text to add to the roi file.

    """

    match format:
        case "pyroi":
            _export_roi_as_pyroi(patch, filename, coord_frame, fitsmap, patch_info)
        case "crtf":
            _export_roi_as_crtf(patch, filename, coord_frame, fitsmap, patch_info)
        case _:
            raise ValueError(f"Unsupported export format: {format}")


def import_roi(
        input_file,
        fitsmap=None,
        log=False,
        **kwargs):
    """
    Import a RoI file as a matplotlib patch.

    Parameters
    ----------
    input_file : `str` or `pathlib.Path`
        Path of the .pyroi file to be imported.
    fitsmap : `~madcubapy.io.MadcubaMap` or `~astropy.nddata.ccddata.CCDData`
        Map object used to transform coordinates.
    log : `bool`
        If True, print parsed RoI info onscreen.

    Returns
    -------
    patch : `~matplotlib.patches.Patch`
        Patch object.

    Other Parameters
    ----------------
    **kwargs
        Parameters to pass to the `~matplotlib.patches.Patch` class.

    """

    # if fitsmap == None:
    #     print(f"If no CCDData file is set with the fitsmap argument, " \
    #           + "the ROI parameters will be assumed to be pixels.")

    with open(input_file) as f:
        lines = f.readlines()
    
    # Matplotlib ROIs
    if lines[0].startswith('# Matplotlib'):
        # lines[1] for now because there is only one roi per file
        data = re.split(r"[(,) ]+", lines[1])
        if log: print(data)
        patch = _import_pyroi_roi(data, fitsmap, **kwargs)

    # MADCUBA ROIs
    if lines[0].startswith('// MADCUBA'):
        # lines[1] for now because there is only one roi per file
        frame = re.split(r"//", lines[1])[1].strip()
        system = re.split(r"//", lines[2])[1].strip()
        data = re.split(r"[(,) ]+", lines[3])
        if log:
            print(frame)
            print(system)
            print(data)
        patch = _import_mcroi_roi(data, frame, system, fitsmap, **kwargs)

    # CARTA ROIs
    if lines[0].startswith('#CRTF'):
        # lines[1] for now because there is only one roi per file
        data = re.split(r"[\[,\] ]+", lines[1])
        if log: print(data)
        patch = _import_crtf_roi(data, fitsmap, **kwargs)

    # DS9 ROIs
    if lines[0].startswith('# Region file format: DS9'):
        system = lines[2].strip()
        # lines[3] for now because there is only one roi per file
        data = re.split(r"[\(),\) ]+", lines[3])
        if log:
            print(system)
            print(data)
        patch = _import_ds9_roi(data, system, fitsmap, **kwargs)

    return patch
