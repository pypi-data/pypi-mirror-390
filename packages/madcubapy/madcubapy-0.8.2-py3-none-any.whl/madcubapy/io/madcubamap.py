import astropy
from astropy.io import fits
from astropy.nddata import CCDData
import astropy.stats as stats
from astropy.table import Table
import astropy.units as u
from copy import deepcopy
import numpy as np
import os
from pathlib import Path
import warnings

from .madcubafits import MadcubaFits

__all__ = [
    'MadcubaMap',
]

class MadcubaMap(MadcubaFits):
    """
    A container for MADCUBA FITS maps, using the `~madcubapy.io.MadcubaFits`
    interface.

    This class is basically a wrapper to read MADCUBA exported FITS maps and
    their history files with astropy.

    Parameters
    ----------
    data : `~numpy.ndarray`
        The data array contained in the FITS file.
    header : `~astropy.io.fits.Header`
        The header object associated with the FITS file.
    wcs : `~astropy.wcs.WCS`
        Object with the world coordinate system for the data.
    unit : `~astropy.units.Unit`
        The unit of the data.
    restfreq : `~astropy.units.Quantity`
        Rest frequency of the FITS file.
    sigma : `~astropy.units.Quantity`
        The noise of the data.
    integrated_range : `~astropy.units.Quantity`
        The range selected for integrating the map.
    hist : `~astropy.table.Table`
        Table containing the history information of the FITS file, which is
        stored in a separate *_hist.csv* file.
    ccddata : `~astropy.nddata.CCDData`
        An astropy CCDData object loaded with astropy as a failsafe.
    filename : `~str`
        Name of the FITS file.

    Methods
    -------
    add_hist(*args)
        Load the history table from a csv file.

    """

    def __init__(
        self,
        data=None,
        header=None,
        wcs=None,
        unit=None,
        restfreq=None,
        sigma=None,
        integrated_range=None,
        hist=None,
        ccddata=None,
        filename=None,
        _update_hist_on_init=True,
        _bypass_ccddata_conflict_check=False,
    ):
        # Inherit hist
        super().__init__(hist.copy() if hist is not None else None)

        # Check input types
        if data is not None and not isinstance(data, np.ndarray):
            raise TypeError("The data must be a numpy array.")
        self._data = deepcopy(data)
        if header is not None and not isinstance(header, astropy.io.fits.Header):
            raise TypeError("The header must be an astropy.io.fits.Header.")
        self._header = deepcopy(header)
        if wcs is not None and not isinstance(wcs, astropy.wcs.WCS):
            raise TypeError("The WCS must be an astropy.wcs.WCS.")
        self._wcs = deepcopy(wcs)
        if unit is not None and not isinstance(unit, astropy.units.UnitBase):
            raise TypeError("The unit must be an astropy unit.")
        self._unit = unit
        if restfreq is not None and not isinstance(restfreq, astropy.units.Quantity):
            raise TypeError("Rest frequency must be an astropy Quantity.")
        self._restfreq = restfreq
        if sigma is not None and not isinstance(sigma, astropy.units.Quantity):
            raise TypeError("Sigma must be an astropy Quantity.")
        self._sigma = sigma
        if (integrated_range is not None
            and not isinstance(integrated_range, astropy.units.Quantity)
            and not isinstance(data, np.ndarray)):
            raise TypeError("Range must be an astropy Quantity or a NumPy array.")
        self._integrated_range = integrated_range
        if ccddata is not None and not isinstance(ccddata, astropy.nddata.CCDData):
            raise TypeError("The ccddata must be a CCDData instance.")
        self._ccddata = deepcopy(ccddata)
        if filename is not None and not isinstance(filename, str):
            raise TypeError("The filename must be a string.")
        self._filename = filename

        # Initialize attributes from CCDData if provided
        hist_updates = []
        if ccddata is not None and not _bypass_ccddata_conflict_check:
            conflicting = [n for n, x in zip(
                ("data", "header", "wcs", "unit", "restfreq"),
                (data, header, wcs, unit, restfreq)) if x is not None]
            if conflicting:
                raise ValueError(
                    f"If 'ccddata' is provided, the following arguments must "
                    + f"not be set: {', '.join(conflicting)}."
                )

            self._data = deepcopy(ccddata.data)
            self._header = deepcopy(ccddata.header)
            self._wcs = deepcopy(ccddata.wcs)
            self._unit = ccddata.unit
            # Try to get rest frequency
            if "RESTFREQ" in ccddata.header:
                freq_value = ccddata.header["RESTFREQ"]
            elif "CRVAL3" in ccddata.header:
                freq_value = ccddata.header["CRVAL3"]
            else:
                try:
                    if (ccddata.wcs is not None
                        and hasattr(ccddata.wcs, "wcs")
                        and len(ccddata.wcs.wcs.crval) >= 3):
                        freq_value = ccddata.wcs.wcs.crval[2]
                except Exception:
                    freq_value = None

            if freq_value is not None:
                if "CUNIT3" in ccddata.header:
                    freq_unit = u.Unit(ccddata.header["CUNIT3"])
                else:
                    try:
                        if (ccddata.wcs is not None
                            and hasattr(ccddata.wcs, "wcs")
                            and len(ccddata.wcs.wcs.cunit) >= 3):
                            freq_unit = ccddata.wcs.wcs.cunit[2]
                    except Exception:
                        warnings.warn(
                            (f"CUNIT3 not found in header, "
                            +"defaulting to Hz for rest frequency"),
                            UserWarning,
                        )
                        freq_unit = u.Hz
                self._restfreq = freq_value * freq_unit
            else:
                self._restfreq = None
            if sigma is None:
                if "SIGMA" in ccddata.header:
                    self._sigma = ccddata.header["SIGMA"] * self._unit
                else:
                    data_no_nan = ccddata.data[~np.isnan(ccddata.data)]
                    mean, median, std = stats.sigma_clipped_stats(data_no_nan,
                                                                  sigma=3.0)
                    self._sigma = std * self._unit
                    # Update sigma header card
                    self._header["SIGMA"] = (self._sigma.value,
                                       'madcubapy read FITS. 3sigma clipped')
                    self._ccddata.header["SIGMA"] = (self._sigma.value,
                                               'madcubapy read FITS. 3sigma clipped')
                    hist_updates.append(
                        f"Update sigma to '{self._sigma.value}' on MadcubaMap init"
                    )
            hist_updates.insert(0, f"Create cube initializing from a CDDData")
        else:
            hist_updates.insert(0, f"Create cube initializing a MadcubaMap")

        if self._hist and _update_hist_on_init:
            for msg in hist_updates:
                self._update_hist(msg)

    @property
    def ccddata(self):
        """
        `~astropy.nddata.CCDData` : An astropy CCDData object loaded with
        astropy as a failsafe.
        """
        return self._ccddata

    @ccddata.setter
    def ccddata(self, value):
        if value is not None and not isinstance(value, CCDData):
            raise TypeError("The ccddata must be a CCDData instance.")
        self._ccddata = deepcopy(value)
        if self._hist:
            self._update_hist(f"Updated CCDData object manually")

    @property
    def filename(self):
        """
        `~str` : Name of the FITS file.
        """
        return self._filename

    @filename.setter
    def filename(self, value):
        if value is not None and not isinstance(value, str):
            raise TypeError("The filename must be a string.")
        self._filename = value
        if self._hist:
            self._update_hist(f"Updated filename path manually")

    @property
    def data(self):
        """
        `~numpy.ndarray` : The data array contained in the FITS file.
        """
        return self._data

    @data.setter
    def data(self, value):
        if value is not None and not isinstance(value, np.ndarray):
            raise TypeError("The data must be a numpy array.")
        self._data = value
        if self._ccddata is not None:
            self._ccddata.data = value.copy()
        if self._hist:
            self._update_hist(f"Updated data object manually")

    @property
    def header(self):
        """
        `~astropy.io.fits.Header` : The header object associated with the FITS.
        file.
        """
        return self._header

    @header.setter
    def header(self, value):
        if value is not None and not isinstance(value, astropy.io.fits.Header):
            raise TypeError("The header must be an astropy.io.fits.Header.")
        self._header = value
        if self._ccddata is not None:
            self._ccddata.header = value.copy()
        if self._hist:
            self._update_hist(f"Updated header object manually")

    @property
    def wcs(self):
        """
        `~astropy.wcs.WCS` : Object with the world coordinate system for the data.
        """
        return self._wcs

    @wcs.setter
    def wcs(self, value):
        if value is not None and not isinstance(value, astropy.wcs.WCS):
            raise TypeError("The WCS must be an astropy.wcs.WCS.")
        self._wcs = value
        if self._ccddata is not None:
            self._ccddata.wcs = deepcopy(value)
        if self._hist:
            self._update_hist(f"Updated WCS object manually")

    @property
    def unit(self):
        """
        `~astropy.units.Unit` : The unit of the data.
        """
        return self._unit

    @unit.setter
    def unit(self, value):
        if value is not None and not isinstance(value, astropy.units.UnitBase):
            raise TypeError("The unit must be an astropy unit.")
        self._unit = value
        if self._ccddata is not None:
            self._ccddata.unit = deepcopy(value)
        if self._hist:
            self._update_hist(f"Updated unit object manually")

    @property
    def restfreq(self):
        """
        `~astropy.units.Quantity` : The rest frequency of the FITS file.
        """
        return self._restfreq

    @restfreq.setter
    def restfreq(self, value):
        if value is not None and not isinstance(value, astropy.units.Quantity):
            raise TypeError("Rest frequency must be an astropy Quantity.")
        self._restfreq = value
        if self._hist:
            self._update_hist(f"Updated restfreq attribute manually")

    @property
    def sigma(self):
        """
        `~astropy.units.Quantity` : The noise of the data.
        """
        return self._sigma

    @sigma.setter
    def sigma(self, value):
        if value is not None and not isinstance(value, astropy.units.Quantity):
            raise TypeError("Sigma must be an astropy Quantity.")
        self._sigma = value
        if self._hist:
            self._update_hist(f"Updated sigma attribute manually")

    @property
    def integrated_range(self):
        """
        `~astropy.units.Quantity` or `~numpy.ndarray` : The range selected for
        integrating the map.
        """
        return self._integrated_range
    
    @integrated_range.setter
    def integrated_range(self, value):
        if (value is not None
            and not isinstance(value, astropy.units.Quantity)
            and not isinstance(value, np.ndarray)):
            raise TypeError("Integrated_range must be an astropy Quantity or a NumPy array.")
        self._integrated_range = value
        if self._hist:
            self._update_hist(f"Updated integrated_range attribute manually")

    @classmethod
    def read(cls, filepath, **kwargs):
        """
        ``Classmethod`` to generate a `~madcubapy.io.MadcubaMap` object from a
        FITS file. This method creates an `~astropy.nddata.CCDData` from the
        FITS file.

        Parameters
        ----------
        filepath : `~str`
            Name of FITS file.

        Other Parameters
        ----------------
        **kwargs
            Additional keyword parameters passed through to the Astropy
            :func:`~astropy.nddata.fits_ccddata_reader` function.

        """
        hist_updates = []
        fits_filepath = filepath
        filename_terms = str(filepath).split('/')
        filename = filename_terms[-1]
        # Check if the fits file exists
        if not os.path.isfile(fits_filepath):
            raise FileNotFoundError(f"File {fits_filepath} not found.")
        # Load the CCDData from the .fits file
        ccddata = CCDData.read(fits_filepath, **kwargs)
        # Load the Table from the .csv file if present
        hist_filepath = os.path.splitext(fits_filepath)[0] + "_hist.csv"
        if not os.path.isfile(hist_filepath):
            print("WARNING: Default history file not found.")
            hist = None
        else:
            hist = Table.read(hist_filepath, format='csv')
            # Set default column types in history table to avoid errors
            hist["Macro"] = np.array(hist["Macro"], dtype='U500')
            hist["Type"] = np.array(hist["Type"], dtype='U5')
            hist["User"] = np.array(hist["User"], dtype='U50')
            hist["Date"] = np.array(hist["Date"], dtype='U23')
        # Store the attributes
        data = ccddata.data
        header = ccddata.header
        # header = fits.getheader(fits_filepath)
        wcs = ccddata.wcs
        unit = ccddata.unit
        # Try to get rest frequency
        if "RESTFREQ" in header:
            freq_value = header["RESTFREQ"]
        elif "CRVAL3" in header:
            freq_value = header["CRVAL3"]
        else:
            try:
                if (wcs is not None
                    and hasattr(wcs, "wcs")
                    and len(wcs.wcs.crval) >= 3):
                    freq_value = wcs.wcs.crval[2]
            except Exception:
                freq_value = None

        if freq_value is not None:
            if "CUNIT3" in header:
                freq_unit = u.Unit(header["CUNIT3"])
            else:
                try:
                    if (wcs is not None
                        and hasattr(wcs, "wcs")
                        and len(wcs.wcs.cunit) >= 3):
                        freq_unit = wcs.wcs.cunit[2]
                except Exception:
                    warnings.warn(
                        (f"CUNIT3 not found in header, "
                        +"defaulting to Hz for rest frequency"),
                        UserWarning,
                    )
                    freq_unit = u.Hz
            restfreq = freq_value * freq_unit
        else:
            restfreq = None
        # Create sigma attribute
        if "SIGMA" in header:
            sigma = ccddata.header["SIGMA"] * unit
        else:
            data_no_nan = data[~np.isnan(data)]
            mean, median, std = stats.sigma_clipped_stats(data_no_nan,
                                                          sigma=3.0)
            sigma = std * unit
            # Update sigma header card
            header["SIGMA"] = (sigma.value,
                               'madcubapy read FITS. 3sigma clipped')
            ccddata.header["SIGMA"] = (sigma.value,
                                       'madcubapy read FITS. 3sigma clipped')
            hist_updates.append(f"Update sigma to '{sigma.value}' on file read")
        # Try to get integrated range
        integrated_range = _get_integrated_range(hist)
        # Return an instance of MadcubaFits
        madcuba_map = cls(
            data=data,
            header=header,
            wcs=wcs,
            unit=unit,
            restfreq=restfreq,
            sigma=sigma,
            integrated_range=integrated_range,
            hist=hist,
            ccddata=ccddata,
            filename=filename,
            _update_hist_on_init=False,
            _bypass_ccddata_conflict_check=True,
        )
        if madcuba_map._hist:
            hist_updates.insert(0, f"Open cube: '{str(filepath)}'")
            for msg in hist_updates:
                madcuba_map._update_hist(msg)

        return madcuba_map

    def write(self, filepath, **kwargs):
        """
        Write a `~madcubapy.io.MadcubaMap` into a FITS file alongside its
        history file.

        Parameters
        ----------
        filepath : `~str`
            Name of output FITS file.

        Other Parameters
        ----------------
        **kwargs
            Additional keyword parameters passed through to the Astropy
            :func:`~astropy.nddata.fits_ccddata_writer` function.

        """
        if not self._ccddata:
            raise TypeError("Cannot export manually created MadcubaMaps (yet)")
        else:
            # Get save directory and file name
            filepath_terms = str(filepath).split('/')
            save_dir = Path("/".join(filepath_terms[:-1]))
            filename = filepath_terms[-1]
            filename_terms = filename.split('.')
            csv_filename = ".".join(filename_terms[:-1]) + "_hist.csv"
            # Write fits
            self._ccddata.write(filepath, **kwargs)
            # Correct units not recognized by madcuba
            with fits.open(filepath, mode="update") as hdul:
                parsed_bunit = _parse_madcuba_friendly_bunit(self.unit)
                hdul[0].header['BUNIT'] = parsed_bunit
                hdul.flush()  # Save changes
            # write hist
            if self._hist:
                update_action = f"Save cube: '{str(filepath)}'"
                self._update_hist(update_action)
                if 'overwrite' in kwargs:
                    overwrite_csv = kwargs['overwrite']
                else:
                    overwrite_csv = False
                self._hist.write(
                    save_dir/csv_filename,
                    format='csv',
                    overwrite=overwrite_csv,
                ) 
            else:
                print("Empty history file has not been saved")
            # Update filename
            self._filename = filename

    def copy(self):
        """
        Create a copy of the `~madcubapy.io.MadcubaMap`.
        """
        if self._hist:
            new_hist = self._hist.copy()
        else:
            new_hist = None
        new_madcubamap =  MadcubaMap(
            data=deepcopy(self._data),
            header=deepcopy(self._header),
            wcs=deepcopy(self._wcs),
            unit=deepcopy(self._unit),
            restfreq=deepcopy(self._restfreq),
            sigma=deepcopy(self._sigma),
            integrated_range=deepcopy(self._integrated_range),
            hist=new_hist,
            ccddata=deepcopy(self._ccddata),
            _update_hist_on_init=False,
            _bypass_ccddata_conflict_check=True,
        )
        # Add to hist
        if new_madcubamap._hist:
            new_madcubamap._update_hist(f"Copied from another MadcubaMap with"
                                        + f" filepath: '{self._filename}'")
        return new_madcubamap

    def show(self, **kwargs):
        """
        Show the map in a pop-up window.

        Other Parameters
        ----------------
        **kwargs
            Additional parameters passed to
            :func:`~madcubapy.visualization.add_wcs_axes`.

        """
        from madcubapy.visualization.quick_plotters import quick_show
        quick_show(self, **kwargs)

    def get_input(self, **kwargs):
        """
        Return mouse click coordinates from this map.

        Other Parameters
        ----------------
        **kwargs
            Additional parameters passed to
            :func:`~madcubapy.visualization.add_wcs_axes`.

        """
        from madcubapy.visualization.interaction import _get_input_from_map
        return _get_input_from_map(self, **kwargs)

    def update_sigma(self, statistic='std', **kwargs):
        """
        Measure the noise (sigma) of the map by calculating the standard
        deviation (std) or root mean square (rms) inside several polygons
        selected by mouse clicks, and store it in the SIGMA header card.

        - Left clicks create polygon vertices.
        - Right click closes the current polygon, and a subsequent left click
          starts a new polygon.

        Parameters
        ----------
        statistic : {'std', 'rms'}, optional
            Statistic to be used as sigma. Defaults to 'std' and can be changed
            at runtime via GUI buttons.

        Other Parameters
        ----------------
        **kwargs
            Additional parameters passed to
            :func:`~madcubapy.visualization.add_wcs_axes`.
        
        """
        from madcubapy.operations.maps.noise import measure_noise
        sigma = measure_noise(self, statistic, **kwargs)
        # Update sigma property
        if np.isnan(sigma.value):
            raise Exception("Measure sigma function aborted.")
        self._sigma = sigma
        # Update sigma header card
        self._header["SIGMA"] = (sigma.value, 'madcubapy update sigma')
        self._ccddata.header["SIGMA"] = (sigma.value, 'madcubapy update sigma')
        # Update hist file
        if self._hist:
            self._update_hist(f"Update sigma to '{sigma.value}'.")

    def update_header_keyword(self, key, value, comment=None):
        """
        Update a single header keyword. This method correctly adds the header key
        to both the `~madcubapy.io.MadcubaMap` object and the ``ccddata``
        attribute.
        
        Parameters
        ----------
        key : `str`
            Header keyword to update.
        value
            Value to assign to the header keyword.
        comment : `str`, optional
            Comment for the header keyword. If None, keep existing comment.

        """
        if comment is None:
            comment = self._header.comments[key] if key in self._header else ""
        # Store new value
        self._header[key] = (value, comment)
        if self._ccddata is not None:
            self._ccddata.header[key] = (value, comment)
        # Update history
        if self._hist:
            self._update_hist(f"Updated header keyword '{key}' to {value}")

    def fix_units(self):
        """
        Tries to fix problems when the units are incorrectly parsed. The user
        should confirm that the new units are correct.
        """
        unit_str = self.header["BUNIT"]
        # Fix CARTA strings
        new_unit_str = _fix_unit_string_multiple_slashes(unit_str)
        # Overwrite units
        self._unit = u.Unit(new_unit_str)
        self._ccddata.unit = u.Unit(new_unit_str)
        self._sigma = self._sigma.value * u.Unit(new_unit_str)
        if self._hist:
            self._update_hist((f"Fixed BUNIT card from '{unit_str}' "
                             + f"to '{new_unit_str}"))

    def convert_unit_to(self, unit):
        """
        Convert the units of the map to other units.
        """
        previous_unit = self.unit
        # Change unit in CCDDdata and copy it into MadcubaMap
        converted_ccddata = self._ccddata.convert_unit_to(unit)
        self._ccddata = converted_ccddata
        self._data = converted_ccddata.data
        # Unit and BUNIT
        self._unit = unit
        unit.to_string(format='fits')
        if "BUNIT" in self.header:
            self.header["BUNIT"] = (unit.to_string(format='fits'),
                                    'madcubapy convert unit')
            self.ccddata.header["BUNIT"] = (unit.to_string(format='fits'),
                                            'madcubapy convert unit')
        # Convert sigma
        if self._sigma:
            self._sigma = self._sigma.to(unit)
        if "SIGMA" in self.header:
            self.header["SIGMA"] = (self._sigma.value,
                                    'madcubapy convert unit')
            self.ccddata.header["SIGMA"] = (self._sigma.value,
                                            'madcubapy convert unit')
        if self._hist:
            self._update_hist((f"Convert units to "
                             + f"'{unit.to_string(format='fits')}'"))

    def __repr__(self):
        # If hist is None, display that it's missing
        if self._hist is None:
            hist_r = "hist=None"
        # If hist is present, display a summary of the table
        else: hist_r = (
            f"hist=<Table length={len(self._hist)} rows, " +
            f"{len(self._hist.columns)} columns>"
        )
        if self._data is None:
            data_r = "data=None"
        else:
            data_r = f"data=<numpy.ndarray shape={self._data.shape}>"
        if self._unit is None:
            unit_r = "unit=None"
        else:
            unit_r = f"unit={self._unit}"

        return f"<MadcubaMap({data_r}, {unit_r}, {hist_r})>"



def _fix_unit_string_multiple_slashes(unit_str):
    """
    This function converts dots to spaces and slashes to '-1' exponents if the
    BUNIT card contains more than one slash.
    """
    result = []
    # Split by slashes
    terms = unit_str.split('/')
    # The entire first term is in the numerator, no correction for a slash must
    # be applied. Split the units and append to a list.
    first_sub_terms = terms[0].split('.')
    result.extend(first_sub_terms)
    # Process terms after slashes
    for term in terms[1:]:
        # Split units and append a -1 to the first one because now it is a unit
        # after a slash and append the rest without changes because they are
        # preceeded by dots.
        sub_terms = term.split('.')
        result.append(f"{sub_terms[0]}-1")
        result.extend(sub_terms[1:])
    # Join all terms with a space
    return ' '.join(result)



def _parse_madcuba_friendly_bunit(unit):
    """
    This function returns a BUNIT card string that MADCUBA can recognize.
    """
    if not isinstance(unit, u.UnitBase):
        raise TypeError("Input value is not an Astropy unit")
    else:
        if unit == u.Jy * u.m / u.beam / u.s:
            return 'Jy beam-1 m s-1'
        elif unit == u.Jy * u.km / u.beam / u.s:
            return 'Jy beam-1 km s-1'
        elif unit == u.mJy * u.m / u.beam / u.s:
            return 'mJy beam-1 m s-1'
        elif unit == u.mJy * u.km / u.beam / u.s:
            return 'mJy beam-1 km s-1'
        elif unit == u.Jy / u.beam:
            return 'Jy beam-1'
        elif unit == u.mJy / u.beam:
            return 'mJy beam-1'
        else:
            return unit.to_string(fraction=False)

def _get_integrated_range(hist):
    """
    This function searches in the history table the range selected for the
    integration of the map.
    """
    if not hist:
        return None
    # Find rows where "Macro" contains the desired substring
    search_str = 'run("INTEGRATED INTENSITY PLUGIN"'
    matching_rows = [row for row in hist if search_str in row['Macro']]
    last_match_row = matching_rows[-1] if matching_rows else None
    if not last_match_row:
        return None
    # If there are more than one matching row, take the last one
    last_match = last_match_row["Macro"]
    # Search for integrated range values
    range_start_index = last_match.find("ranges=") + len("ranges=")
    range_end_index = last_match.find("# axisunit")
    range_string = last_match[range_start_index : range_end_index].strip()
    range_string
    # Convert the strings into floats if the strings are not empty.
    range_values = [float(value) for value in range_string.split('$') if value]
    # Search for unit
    axisunit_start_index = last_match.find("axisunit=") + len("axisunit=")
    axisunit_end_index = last_match.find("interpolate")
    unit_string = last_match[axisunit_start_index:axisunit_end_index].strip()
    # Create integrated range
    try:
        unit = u.Unit(unit_string)
        integrated_range = u.Quantity(range_values, unit=unit)
    except ValueError:
        warnings.warn(
            f"Could not parse unit from string: {unit_string!r}. Integrated"
            "range will be treated as a plain NumPy array without units.",
            UserWarning,
        )
        integrated_range = np.array(range_values)

    return integrated_range
