from astropy.nddata import CCDData
import astropy.stats as stats
import astropy.units as u
import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import tkinter as tk
import sys

from madcubapy.io import MadcubaFits
from madcubapy.io import MadcubaMap
from .wcsaxes_helpers import add_wcs_axes
from .wcsaxes_helpers import insert_colorbar

__all__ = [
    'quick_show',
    'are_equal',
]

def quick_show(
        fitsmap,
        **kwargs):
    """
    Show a map on a separate window.

    Parameters
    ----------
    fitsmap : `~madcubapy.io.MadcubaMap` or `~astropy.nddata.CCDData`
        Map to be displayed.

    Other Parameters
    ----------------
    **kwargs
        Parameters to pass to :func:`matplotlib.pyplot.imshow`.

    """

    # Create tkinter window
    root = tk.Tk()
    root.wm_title("Quick map plot")

    # Create a Matplotlib figure
    fig = mpl.figure.Figure(figsize=(6,5), dpi=100)
    ax, img = add_wcs_axes(fig, 1, 1, 1, fitsmap=fitsmap, **kwargs)
    cbar = insert_colorbar(ax)
    
    # Display minor ticks
    ax.coords[0].display_minor_ticks(True)
    ax.coords[1].display_minor_ticks(True)

    # Exit function to close the window
    def _quit():
        root.quit()
        root.destroy()

    # Add close shortcut
    def onkeypress(event):
        if event.key == 'q':
            root.quit()
            root.destroy()
    
    # Create a Matplotlib canvas embedded within the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Add matplotlib tk toolbar
    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Create a frame for buttons
    control_frame = tk.Frame(root)
    control_frame.pack(side=tk.BOTTOM, pady=5)
    #Exit button
    clear_button = tk.Button(control_frame, text="Quit", command=_quit)
    clear_button.pack(side=tk.LEFT)

    # Connect the onclick and onkeypress events to the canvas
    canvas.mpl_connect('key_press_event', onkeypress)

    # Start the Tkinter event loop
    root.mainloop()


def are_equal(
        fitsmap_1,
        fitsmap_2,
        show_maps=False):
    """
    Compare two maps to check if they are equal.

    Parameters
    ----------
    fitsmap_1 : `~madcubapy.io.MadcubaMap` or `~astropy.nddata.CCDData`
        Map object to compare.
    fitsmap_2 : `~madcubapy.io.MadcubaMap` or `~astropy.nddata.CCDData`
        Map object to compare.
    show_maps : `~bool`, default: False
        If true both maps are plotted alongside the residuals of their
        substraction.

    Returns
    -------
    `~bool`
        Returns True if the two maps are the same map.

    """
    
    print('Checking if the two maps are equal\n')
    # Check fitsmap types
    if not (isinstance(fitsmap_1, (MadcubaMap, CCDData)) and
            isinstance(fitsmap_2, (MadcubaMap, CCDData))):
        raise TypeError(f"Input maps must be {MadcubaMap} or {CCDData}")
    # Copy fitsmaps to avoid changing input objects attributes
    map_1 = fitsmap_1.copy()
    map_2 = fitsmap_2.copy()
    # Slice extra dimensions from data
    if map_1.header['NAXIS'] == 3:
        data_1 = map_1.data[0, :, :]
    elif map_1.header['NAXIS'] == 4:
        data_1 = map_1.data[0, 0, :, :]
    else:
        data_1 = map_1.data
    if map_2.header['NAXIS'] == 3:
        data_2 = map_2.data[0, :, :]
    elif map_2.header['NAXIS'] == 4:
        data_2 = map_2.data[0, 0, :, :]
    else:
        data_2 = map_2.data
    # Shape check to avoid errors trying to plot residuals
    if data_1.shape != data_2.shape:
        raise ValueError("Cannot compare images with different resolutions")
    # Convert map 2 to units of map 1 if possible
    if isinstance(map_2, MadcubaMap):
        try:
            map_2.convert_unit_to(map_1.unit)
        except u.UnitConversionError:
            raise u.UnitConversionError(
                (
                    f"Cannot compare images with unconvertible units: "
                    + f"'{map_1.unit}' and '{map_2.unit}'"
                )
            )
    else:
        try:
            map_2 = map_2.convert_unit_to(map_1.unit)
        except u.UnitConversionError:
            raise u.UnitConversionError(
                (
                    f"Cannot compare images with unconvertible units: "
                    + f"'{map_1.unit}' and '{map_2.unit}'"
                )
            )
    # Show maps
    if show_maps:
        # Create figure
        fig = plt.figure(figsize=(15,6))
        # Map 1
        ax1, img1 = add_wcs_axes(fig, 1, 3, 1, fitsmap=map_1, use_std=True)
        cbar1 = insert_colorbar(ax1, 'top')
        ax1.set_title('MAP 1', pad=60)
        ax1.coords[1].set_ticklabel(
            rotation=90,
            rotation_mode='default',
            va='center'
        )
        # Map 2
        ax2, img2 = add_wcs_axes(fig, 1, 3, 2, fitsmap=map_2, use_std=True)
        cbar2 = insert_colorbar(ax2, 'top')
        ax2.set_title('MAP 2', pad=60)
        ax2.coords[1].set_ticklabel(
            rotation=90,
            rotation_mode='default',
            va='center'
        )
        # Diff map
        data = data_1 - data_2
        wcs = map_1.wcs.celestial
        mean, median, std = stats.sigma_clipped_stats(data, sigma=3.0)
        vmin = median - 3 * std
        vmax = median + 3 * std
        norm = 'linear'
        # Figure calling
        ax3 = plt.subplot(1, 3, 3, projection=wcs)
        img3 = ax3.imshow(data, vmin=vmin, vmax=vmax, cmap='viridis',
                        origin='lower', norm=norm)
        ax3.coords[1].set_ticklabel(
            rotation=90,
            rotation_mode='default',
            va='center'
        )
        ax3.set_xlabel('RA (ICRS)')
        ax3.set_ylabel('DEC (ICRS)')
        cbar3 = insert_colorbar(ax3, 'top')
        ax3.set_title('Residuals (1-2)', pad=60)
    # Check
    if np.array_equal(data_1, data_2, equal_nan=True):
        return True
    else:
        return False
