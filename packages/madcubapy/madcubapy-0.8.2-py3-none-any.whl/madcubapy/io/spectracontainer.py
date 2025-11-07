import astropy
from astropy.table import Table
import astropy.units as u
import numpy as np
import os
from pathlib import Path
import zipfile

from .madcubafits import MadcubaFits
from madcubapy.utils.spectral import create_spectral_array

__all__ = [
    'SpectraContainer',
    'parse_row_spectral_axis',
]

class SpectraContainer(MadcubaFits):
    """
    A container for MADCUBA spectra, using the
    `~madcubapy.io.madcubafits.MadcubaFits` interface.

    This class is basically a wrapper to read MADCUBA exported spectra and
    their history files with astropy.

    Parameters
    ----------
    bintable : `~astropy.table.Table`
        Table containing the data of every spectra inside the *.spec* file
        alongside the info of their headers.
    hist : `~astropy.table.Table`
        Table containing the history information of the FITS file, which is
        stored in a separate *_hist.csv* file.
    filename : `~str`
        Name of the *.spec* file.

    Methods
    -------
    add_hist(*args)
        Load the history table from a csv file.

    """

    def __init__(
        self,
        bintable=None,
        hist=None,
        filename=None,
    ):
        # inherit hist
        super().__init__(hist)

        if bintable is not None and not isinstance(bintable, Table):
            raise TypeError(
                "The bintable must be an astropy Table")
        self._bintable = bintable

        if filename is not None and not isinstance(filename, str):
            raise TypeError("The filename must be a string.")
        self._filename = filename

    @property
    def bintable(self):
        """
        `~astropy.table.Table` : Table containing the data of every spectra
        inside the *.spec* file.
        """
        return self._bintable

    @bintable.setter
    def bintable(self, value):
        if value is not None and not isinstance(value, Table):
            raise TypeError(
                "The bintable must be an astropy Table")
        self._bintable = value

    @property
    def filename(self):
        """
        `~str` : Name of the *.spec* file.
        """
        return self._filename

    @filename.setter
    def filename(self, value):
        if value is not None and not isinstance(value, str):
            raise TypeError("The filename must be a string.")
        self._filename = value

    @classmethod
    def read(cls, filepath):
        """
        ``Classmethod`` to generate a
        `~madcubapy.io.spectracontainer.SpectraContainer` from a *.spec* file.

        Parameters
        ----------
        filepath : `~str`
            Name of spec file.

        """
        spec_filepath = filepath
        # Check if the spec file exists
        if not os.path.isfile(spec_filepath):
            raise FileNotFoundError(f"File {spec_filepath} not found.")
        # Open the ZIP file
        with zipfile.ZipFile(spec_filepath, "r") as zip_file:
            fits_files = [
                name for name in zip_file.namelist() if name.endswith(".fits")
            ]
            with zip_file.open(fits_files[0]) as internal_fits_file:
                bintable = Table.read(internal_fits_file, hdu=1)
            hist_files = [
                name for name in zip_file.namelist() if name.endswith("_hist.csv")
            ]
            with zip_file.open(hist_files[0]) as internal_hist_file:
                hist = Table.read(internal_hist_file, format='csv')
        filename_terms = str(filepath).split('/')
        filename = filename_terms[-1]
        # Return an instance of MadcubaFits
        spectra_container = cls(
            bintable=bintable,
            hist=hist,
            filename=filename,
        )
        spectra_container._generate_spectral_axes()
        spectra_container._parse_data_units()
        return spectra_container

    def copy(self):
        """
        Create a copy of the `~madcubapy.io.SpectraContainer`.
        """
        if self._bintable:
            new_bintable = self._bintable.copy()
        else:
            new_bintable = None
        if self._hist:
            new_hist = self._hist.copy()
        else:
            new_hist = None
        return SpectraContainer(
            bintable=new_bintable,
            hist=new_hist,
        )

    def _generate_spectral_axes(self):
        """
        Generate arrays for the spectral axes of every spectra inside the
        `~madcubapy.io.SpectraContainer` and add them as a new table column.
        """
        data = []
        for i in range(len(self.bintable)):
            spectral_axis = parse_row_spectral_axis(self.bintable[i])
            if isinstance(data, u.Quantity):
                data.append(spectral_axis.value)
            else: data.append(spectral_axis)
        self.bintable['XAXIS'] = data
        self.bintable['XAXIS'].unit = self.bintable['RESTFRQ'].unit
        
    def _parse_data_units(self):
        """
        Parse the BUNIT column values. If all are equal, set it as the unit for
        the DATA column.
        """
        if np.all(self.bintable["BUNIT"] == self.bintable["BUNIT"][0]):
            unit_code = self.bintable["BUNIT"][0]
            try: 
                unit = astropy.units.Unit(unit_code)
            except ValueError:
                print("Unit string for data could not be parsed")
                unit = unit_code
            finally:
                self.bintable["DATA"].unit = unit
        else: self.bintable["DATA"].unit = None
        
    def __repr__(self):
        # If hist is None, display that it's missing
        if self._hist is None:
            hist_repr = "hist=None"
        # If hist is present, display a summary of the table
        else:
            hist_repr = (
                f"hist=<Table length={len(self._hist)} rows, "
                + f"{len(self._hist.columns)} columns>"
            )
        if self._bintable is None:
            bintable_repr = "bintable=None"
        # If hist is present, display a summary of the table
        else:
            bintable_repr = (
                f"bintable=<Table length={len(self._hist)} rows, "
                + f"{len(self._hist.columns)} columns>"
            )

        return f"<SpectraContainer({bintable_repr}, {hist_repr})>"


def parse_row_spectral_axis(table_row):
    """
    Generate an array for the spectral axis of a spectrum inside a
    `~madcubapy.io.SpectraContainer`.

    Parameters
    ----------
    table_row : `astropy.table.Row`
        Row of a `~madcubapy.io.SpectraContainer`'s bintable. This is the data
        for a spectrum inside a MADCUBA FITS file.
    
    Returns
    -------
    spectral_array : `~numpy.ndarray` or `~astropy.units.Quantity`
        Returned spectral axis array with units if correctly parsed from the
        FITS file.

    """
    
    # Get spectrum data
    nchan = table_row['CHANNELS']
    cdelt3 = table_row['CDELT3']
    crval3 = table_row['CRVAL3']
    crpix3 = table_row['CRPIX3'] - 1  # fits to numpy
    if isinstance(table_row.table['RESTFRQ'].unit, astropy.units.UnitBase):
        spectral_unit = table_row.table['RESTFRQ'].unit
    else:
        spectral_unit = None
    spectral_array = create_spectral_array(nchan,cdelt3,crpix3,crval3)
    if spectral_unit:
        spectral_array = spectral_array * spectral_unit

    return spectral_array
