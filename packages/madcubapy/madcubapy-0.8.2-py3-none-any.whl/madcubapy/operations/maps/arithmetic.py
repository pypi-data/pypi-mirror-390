from astropy.nddata import CCDData
import astropy.units as u
import matplotlib.pyplot as plt
import numpy as np

from madcubapy.io import MadcubaMap

__all__ = [
    'stack_maps',
]


def stack_maps(*fitsmaps):
    """
    Adds the data of multiple map objects (`~madcubapy.io.MadcubaMap` or
    `~astropy.nddata.CCDData`) together and returns the result as a new map
    object with the metadata of the first input map.
    
    Parameters
    ----------
    *fitsmaps : `~madcubapy.io.MadcubaMap` or `~astropy.nddata.CCDData`
        Any number of map objects to be added together.
    
    Returns
    -------
    combined_fitsmap : `~madcubapy.io.MadcubaMap` or `~astropy.nddata.CCDData`
        A new map object containing the sum of the data of the input maps.
    
    """

    # Ensure the input is not empty
    if not fitsmaps:
        raise ValueError("At least one map object must be provided.")
    # Check map object type
    first_type = type(fitsmaps[0])
    if not all(type(obj) == first_type for obj in fitsmaps):
        raise TypeError("Input parameters must be of the same type.")
    elif (type(fitsmaps[0]) != MadcubaMap and type(fitsmaps[0]) != CCDData):
        raise TypeError(
            f"Input parameters must be {MadcubaMap} or {CCDData} types."
        )
    # Ensure all CCDData objects have the same shape
    shape = fitsmaps[0].data.shape
    for fitsmap in fitsmaps[1:]:
        if fitsmap.data.shape != shape:
            raise ValueError("All maps must have the same shape.")
    # Ensure all CCDData objects have the same unit
    unit = fitsmaps[0].unit
    for fitsmap in fitsmaps[1:]:
        if fitsmap.unit != unit:
            fitsmap = fitsmap.to(unit)
    # Create and return the new map object with combined data and the metadata
    # from the first map object
    combined_data = sum(fitsmap.data for fitsmap in fitsmaps)
    if type(fitsmaps[0]) == MadcubaMap:
        # Create new CCDData if present
        if fitsmaps[0].ccddata:
            new_ccddata = CCDData(
                data=combined_data,
                unit=unit,
                meta=fitsmaps[0].ccddata.meta,
                wcs=fitsmaps[0].ccddata.wcs,
            )
        else:
            new_ccddata = None
        # Use history table from first object if present
        if fitsmaps[0].hist:
            new_hist = fitsmaps[0].hist.copy()
        else:
            new_hist = None
        # Create new madcubaMap
        new_madcubamap = MadcubaMap(
            data=combined_data,
            header=fitsmaps[0].header,
            wcs=fitsmaps[0].wcs,
            unit=unit,
            hist=new_hist,
            ccddata=new_ccddata,
            filename=fitsmaps[0].filename,
            _update_hist_on_init=False,
            _bypass_ccddata_conflict_check=True,
        )
        # Create history action
        if all(obj.filename is not None for obj in fitsmaps):
            stacked_maps_names = [obj.filename for obj in fitsmaps]
            update_action = ("Stack maps. Files: '" +
                             "', '".join(stacked_maps_names) + "'")
        else:
            update_action = (
                "Stack maps. Manually created objects with no files"
            )
        # Update history if present
        if new_madcubamap.hist:
            new_madcubamap._update_hist(update_action)
        return new_madcubamap
    else:
        return CCDData(combined_data, unit=unit,
                       meta=fitsmaps[0].meta, wcs=fitsmaps[0].wcs)

    return combined_fitsmap
