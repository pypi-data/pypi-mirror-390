from astropy.wcs import WCS
from astropy.io.fits import Header
from astropy.nddata import CCDData
from astropy.table import Table
import astropy.units as u
from astropy.utils.diff import report_diff_values
import numpy as np
import pytest
from madcubapy.io.madcubamap import MadcubaMap

@pytest.fixture
def example_madcuba_ccddata():
    # Create and return a Map instance to be used in tests
    return CCDData.read(
        "examples/data/IRAS16293_SO_2-1_moment0_madcuba.fits"
    )

@pytest.fixture
def example_carta_ccddata():
    # Create and return a Map instance to be used in tests
    return CCDData.read(
        "examples/data/IRAS16293_SO2c_moment0_carta.fits"
    )

@pytest.fixture
def example_madcuba_madcubamap():
    # Create and return a Map instance to be used in tests
    return MadcubaMap.read(
        "examples/data/IRAS16293_SO_2-1_moment0_madcuba.fits"
    )

@pytest.fixture
def example_carta_madcubamap():
    # Create and return a Map instance to be used in tests
    return MadcubaMap.read(
        "examples/data/IRAS16293_SO2c_moment0_carta.fits"
    )

def test_read_madcuba_map(example_madcuba_madcubamap):
    # Test if the obligatory attributes are correctly initialized
    assert example_madcuba_madcubamap.ccddata is not None
    assert example_madcuba_madcubamap.data is not None
    assert example_madcuba_madcubamap.header is not None
    assert example_madcuba_madcubamap.filename is not None
    assert (example_madcuba_madcubamap.hist is None or
            isinstance(example_madcuba_madcubamap.hist, Table))
    assert np.array_equal(
        example_madcuba_madcubamap.data,
        example_madcuba_madcubamap.ccddata.data,
        equal_nan=True,
    )
    assert (example_madcuba_madcubamap.hist[-1]["Macro"] ==
        "//PYTHON: Open cube: "
        + "'examples/data/IRAS16293_SO_2-1_moment0_madcuba.fits'"
    )
    assert (example_madcuba_madcubamap.restfreq == 
            (example_madcuba_madcubamap.header["RESTFREQ"] *
             example_madcuba_madcubamap.wcs.wcs.cunit[2]))
    assert np.all(example_madcuba_madcubamap.integrated_range == 
                  np.array([500, 5500]) * u.m / u.s)

    assert (example_madcuba_madcubamap.sigma == 
            (example_madcuba_madcubamap.header["SIGMA"] *
             example_madcuba_madcubamap.unit))

def test_invalid_file():
    with pytest.raises(FileNotFoundError):
        MadcubaMap.read("nonexistent_file.fits")

@pytest.mark.parametrize(
    "parameter, value",
    [
        ("data", 3),
        ("data", 3.14),
        ("data", "not an array"),
        ("data", CCDData(np.ones((5,5)), unit="Jy")),

        ("header", 42),
        ("header", "not a header"),
        ("header", np.array([1, 2, 3])),

        ("wcs", 3),
        ("wcs", "not a wcs"),

        ("unit", 42),
        ("unit", np.array([1])),

        ("restfreq", 42),
        ("restfreq", np.array([1])),
        ("restfreq", "not quantity"),

        ("integrated_range", 42),
        ("integrated_range", np.array([1])),
        ("integrated_range", "not quantity"),

        ("sigma", 42),
        ("sigma", "not quantity"),
    ],
)
def test_invalid_init_types(parameter, value):
    with pytest.raises(TypeError):
        MadcubaMap(**{parameter: value})

@pytest.mark.parametrize(
    "parameter, value",
    [
        ("data", np.zeros((10, 10))),
        ("header", Header()),
        ("wcs", WCS(naxis=2)),
        ("unit", u.Jy),
        ("sigma", 1.2 * u.K),
    ],
)
def test_valid_init_types(parameter, value):
    try:
        MadcubaMap(**{parameter: value})
    except TypeError as e:
        pytest.fail(f"Unexpected TypeError for {parameter}={value!r}: {e}")

def test_write_madcuba_map(example_madcuba_madcubamap):
    # Assert filename and hist change after writing
    assert (example_madcuba_madcubamap.filename ==
            "IRAS16293_SO_2-1_moment0_madcuba.fits")
    example_madcuba_madcubamap.write(
        "examples/data/IRAS16293_SO_2-1_moment0_madcuba_write.fits",
        overwrite=True,
    )
    # Assert filename
    assert (example_madcuba_madcubamap.filename ==
            "IRAS16293_SO_2-1_moment0_madcuba_write.fits")
    assert (example_madcuba_madcubamap.hist[-1]["Macro"] ==
        "//PYTHON: Save cube: "
        + "'examples/data/IRAS16293_SO_2-1_moment0_madcuba_write.fits'"
    )
    # Read back the written file
    example_madcuba_madcubamap_write = MadcubaMap.read(
        "examples/data/IRAS16293_SO_2-1_moment0_madcuba_write.fits"
    )
    # Assert BUNIT was written correctly
    assert (example_madcuba_madcubamap_write.header["BUNIT"] ==
            'Jy beam-1 m s-1')
    # Assert written map is correctly read
    assert 0 == 0
    assert example_madcuba_madcubamap_write.ccddata is not None
    assert example_madcuba_madcubamap_write.data is not None
    assert example_madcuba_madcubamap_write.header is not None
    assert example_madcuba_madcubamap_write.filename is not None
    assert example_madcuba_madcubamap_write.sigma is not None
    assert (example_madcuba_madcubamap_write.hist is None or
            isinstance(example_madcuba_madcubamap_write.hist, Table))
    # Assert written map is equal to original map
    assert np.array_equal(
        example_madcuba_madcubamap.data,
        example_madcuba_madcubamap_write.data,
        equal_nan=True,
    )
    assert (example_madcuba_madcubamap.unit ==
            example_madcuba_madcubamap_write.unit)
    assert (example_madcuba_madcubamap.hist[0]["Macro"] ==
        example_madcuba_madcubamap_write.hist[0]["Macro"]
    )
    # Check filename and hist file with expected content
    assert (example_madcuba_madcubamap_write.filename ==
            "IRAS16293_SO_2-1_moment0_madcuba_write.fits")
    assert (example_madcuba_madcubamap_write.hist[-2]["Macro"] ==
        "//PYTHON: Save cube: "
        + "'examples/data/IRAS16293_SO_2-1_moment0_madcuba_write.fits'"
    )
    assert (example_madcuba_madcubamap_write.hist[-1]["Macro"] ==
        "//PYTHON: Open cube: "
        + "'examples/data/IRAS16293_SO_2-1_moment0_madcuba_write.fits'"
    )

def test_sigma_creation_at_init(example_carta_ccddata,
                                example_madcuba_madcubamap):
    histi = example_madcuba_madcubamap.hist.copy()
    madcubamap_carta_test_hist = MadcubaMap(ccddata=example_carta_ccddata,
                                            hist=histi)
    # Previously known sigma calculation
    assert (madcubamap_carta_test_hist.hist[-1]["Macro"] == 
            "//PYTHON: Update sigma to '1.5514508485794067' on MadcubaMap init")

def test_madcubamap_init_ccddata(example_madcuba_ccddata):
    madcubamap_from_ccddata = MadcubaMap(ccddata=example_madcuba_ccddata)
    # Check equal attributes 
    assert np.array_equal(
        madcubamap_from_ccddata.data,
        example_madcuba_ccddata.data,
        equal_nan=True,
    )
    assert madcubamap_from_ccddata.header == example_madcuba_ccddata.header
    assert madcubamap_from_ccddata.unit == example_madcuba_ccddata.unit

def test_input_params_inmutability(example_madcuba_ccddata):
    madcubamap_from_ccddata = MadcubaMap(ccddata=example_madcuba_ccddata)
    # data
    madcubamap_from_ccddata.ccddata.data = np.array([8])
    assert not np.array_equal(
        madcubamap_from_ccddata.ccddata.data,
        example_madcuba_ccddata.data,
        equal_nan=True,
    )
    # unit
    madcubamap_from_ccddata.ccddata.unit = u.s
    assert madcubamap_from_ccddata.ccddata.unit == u.s
    assert example_madcuba_ccddata.unit == u.Jy * u.m / u.beam / u.s
    # header
    hedi = madcubamap_from_ccddata.header
    hedi["NAXIS"] = (34, "update")
    madcubamap_from_ccddata.header = hedi
    assert example_madcuba_ccddata.header != madcubamap_from_ccddata.header

def test_hist_inmutability(example_madcuba_madcubamap,
                           example_madcuba_ccddata):
    histi = example_madcuba_madcubamap.hist.copy()
    madcubamap_test_hist = MadcubaMap(ccddata=example_madcuba_ccddata,
                                      hist=histi)
    # Init via CCDData added one line at the end, check this
    assert (madcubamap_test_hist.hist[-2] ==
        example_madcuba_madcubamap.hist[-1]
    )
    # A change in the hist is not reflected outwards
    previous_histi_last_row = histi[-1]["Macro"]
    madcubamap_test_hist.data = np.array([9])
    assert (madcubamap_test_hist.hist[-1]["Macro"] != histi[-1]["Macro"]
            and madcubamap_test_hist.hist[-1]["Macro"] ==
                "//PYTHON: Updated data object manually"
            and histi[-1]["Macro"] == previous_histi_last_row)

def test_fix_units_correct(example_madcuba_madcubamap):
    assert example_madcuba_madcubamap.unit == u.Jy * u.m / u.beam / u.s
    example_madcuba_madcubamap.fix_units()
    assert example_madcuba_madcubamap.unit == u.Jy * u.m / u.beam / u.s

def test_fix_units_incorrect(example_carta_madcubamap):
    assert example_carta_madcubamap.unit == u.Jy / u.beam / u.km / u.s
    example_carta_madcubamap.fix_units()
    assert example_carta_madcubamap.unit == u.Jy * u.km / u.beam / u.s

def test_copy_madcuba(example_madcuba_madcubamap):
    madcuba_map_copy = example_madcuba_madcubamap.copy()
    assert np.array_equal(
        madcuba_map_copy.data, example_madcuba_madcubamap.data, equal_nan=True
    )
    assert madcuba_map_copy.header == example_madcuba_madcubamap.header
    assert madcuba_map_copy.unit == example_madcuba_madcubamap.unit
    assert report_diff_values(example_madcuba_madcubamap.hist,
                              madcuba_map_copy.hist[:-1])
    assert (madcuba_map_copy.ccddata.meta ==
            example_madcuba_madcubamap.ccddata.meta)

def test_convert_units_madcuba(example_madcuba_madcubamap):
    example_madcuba_madcubamap_mJy = example_madcuba_madcubamap.copy()
    example_madcuba_madcubamap_mJy.convert_unit_to(u.mJy * u.m / u.beam / u.s)
    assert example_madcuba_madcubamap_mJy.unit == u.mJy * u.m / u.beam / u.s
    assert (example_madcuba_madcubamap_mJy.ccddata.unit ==
            u.mJy * u.m / u.beam / u.s)
    assert example_madcuba_madcubamap_mJy.hist[-1]["Macro"] == (
        "//PYTHON: Convert units to 'm mJy beam-1 s-1'"
    )

def test_convert_units_carta(example_carta_madcubamap):
    example_carta_madcubamap_mJy = example_carta_madcubamap.copy()
    example_carta_madcubamap_mJy.fix_units()
    example_carta_madcubamap_mJy.convert_unit_to(u.mJy * u.m / u.beam / u.s)
    assert example_carta_madcubamap_mJy.unit == u.mJy * u.m / u.beam / u.s
    assert (example_carta_madcubamap_mJy.ccddata.unit ==
            u.mJy * u.m / u.beam / u.s)
    assert example_carta_madcubamap_mJy.hist == None
