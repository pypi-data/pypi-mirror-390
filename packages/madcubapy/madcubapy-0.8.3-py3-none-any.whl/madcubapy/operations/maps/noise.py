from astropy.nddata import CCDData
import astropy.units as u
from copy import copy
from IPython import get_ipython
import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.patches as patches
import matplotlib.patheffects as PathEffects
import matplotlib.pyplot as plt
import numpy as np
import platform
import tkinter as tk

from madcubapy.io import MadcubaMap
from madcubapy.visualization import add_wcs_axes
from madcubapy.visualization import insert_colorbar

__all__ = [
    'measure_noise',
]


def measure_noise(
        fitsmap,
        statistic='std',
        **kwargs):
    """
    Measure the noise (sigma) in a map object by calculating the standard
    deviation (std) or root mean square (rms) inside several polygons selected
    by mouse clicks.

    - Left clicks create polygon vertices.
    - Right click closes the current polygon, and a subsequent left click
      starts a new polygon.

    Parameters
    ----------
    fitsmap : `~madcubapy.io.MadcubaMap` or `~astropy.nddata.CCDData`
        Map object to analize.
    statistic : {'std', 'rms'}, optional
        Statistic to be used as sigma. Defaults to 'std' and can be changed at
        runtime via GUI buttons.

    Returns
    -------
    sigma : `~astropy.units.Quantity`
        Measured noise of the image in the same units as the data array.

    Other Parameters
    ----------------
    **kwargs
        Optional map visualization parameters passed to
        :func:`~madcubapy.visualization.add_wcs_axes`.

    Notes
    -----
    The function can be aborted by closing the window or pressing 'q'.

    """

    # OS check and kernel check
    def in_jupyter_notebook():
        try:
            shell = get_ipython()
            return shell and "IPKernelApp" in shell.config
        except Exception:
            return False
    if in_jupyter_notebook() and platform.system() == 'Darwin':
        right_click = 2
        middle_click = 3
    else:
        right_click = 3
        middle_click = 2

    if not isinstance(fitsmap, CCDData) and not isinstance(fitsmap, MadcubaMap):
        raise TypeError(f"Unsupported type: {type(fitsmap)}. "
                        + "Provide a MadcubaMap or CCDData object.")

    if statistic != 'std' and statistic != 'rms':
        raise ValueError(f"Invalid input for statistic: '{statistic}'. "
                         + "Accepted values are 'std' or 'rms'.")

    if ('use_std' not in kwargs and
        'vmin' not in kwargs and
        'vmax' not in kwargs):
        kwargs['use_std'] = True

    # Create a Tkinter window
    root = tk.Tk()
    root.title("Measure noise")

    # Create a Matplotlib figure
    # If I use mpl.pyplot.figure here and this function is used in a
    # notebook, an inline plot of the final figure will be shown.
    fig = Figure(figsize=(7, 6), dpi=100)
    ax, img = add_wcs_axes(fig, 1, 1, 1, fitsmap=fitsmap, **kwargs)
    cbar = insert_colorbar(ax)

    # Prettier plot
    current_title = ax.get_title()
    ax.set_title(current_title, fontsize=13, pad=15)
    ax.coords[0].set_axislabel("RA (ICRS)", fontsize=12)
    ax.coords[1].set_axislabel("DEC (ICRS)", fontsize=12)
    ax.coords[0].tick_params(which="major",
                            length=5)
    ax.coords[0].display_minor_ticks(True)
    ax.coords[0].set_ticklabel(size=11, exclude_overlapping=True)
    ax.coords[1].tick_params(which="major",
                            length=5)
    ax.coords[1].display_minor_ticks(True)
    ax.coords[1].set_ticklabel(size=11, exclude_overlapping=True,
                               rotation='vertical')
    cbar.ax.yaxis.label.set_fontsize(12)
    cbar.ax.tick_params(labelsize=11)

    # Lists to store the polygons and arrays with pixel data
    polygon_paths = []
    current_polygon = []
    inside_pixels = []
    sigma = np.nan

    # Create a callback function for mouse clicks
    def onclick(event):
        nonlocal polygon_paths, current_polygon
        # Left-click to select points
        if event.button == 1:
            # Add the clicked point to the current polygon
            current_polygon.append((event.xdata, event.ydata))
            now_polygon = np.array(current_polygon)
            # Draw a small point at the first clicked point
            if len(now_polygon) == 1:
                ax.plot(event.xdata, event.ydata,
                        'white', marker='o', markersize=5)
            # Draw lines
            if len(now_polygon) > 1:
                ax.plot(now_polygon[-2:, 0], now_polygon[-2:, 1],
                        'white', lw=2, alpha=0.9)
                ax.plot(event.xdata, event.ydata,
                        'white', marker='o', markersize=5)
            # Refresh the canvas
            canvas.draw()
        # Right-click to finalize the current polygon
        elif event.button == right_click and current_polygon:
            polygon = np.array(current_polygon)
            # Draw the last side of the polygon
            closed_polygon = np.vstack((polygon, polygon[0]))
            ax.plot(closed_polygon[-2:, 0], closed_polygon[-2:, 1],
                    'white', lw=2, alpha=0.9)
            # Draw the polygon on the plot
            poly = patches.Polygon(xy=polygon, linewidth=2,
                                   edgecolor='white', facecolor='white',
                                   alpha=0.5)
            new_poly = copy(poly)
            ax.add_patch(new_poly)
            # Get the shape of the CCDData object
            if fitsmap.header['NAXIS'] == 2:
                height, width = fitsmap.data.shape
                fitsmap_data = fitsmap.data
            elif fitsmap.header['NAXIS'] == 3:
                freq, height, width = fitsmap.data.shape
                fitsmap_data = fitsmap.data[0,:,:]
            elif fitsmap.header['NAXIS'] == 4:
                freq, stokes, height, width = fitsmap.data.shape
                fitsmap_data = fitsmap.data[0,0,:,:]
            # Create a meshgrid of coordinates to create mask
            x, y = np.meshgrid(range(width), range(height))
            points = np.vstack((x.flatten(), y.flatten())).T
            mask = poly.contains_points(points, radius=0)
            mask = mask.reshape((height, width))
            # Calculate std
            new_data = copy(fitsmap_data)
            std = new_data[mask].std(ddof=1)
            # Paint std inside polygon
            x_text = polygon.T[0].min() + (polygon.T[0].max()
                                           - polygon.T[0].min()) / 2
            y_text = polygon.T[1].min() + (polygon.T[1].max() 
                                           - polygon.T[1].min()) / 2
            std_text = ax.text(x_text, y_text, f'{std:.2f}',
                               va='center', ha='center',
                               color='white', fontsize=13)
            std_text.set_path_effects(
                [PathEffects.withStroke(linewidth=1.5, foreground="0.5")]
            )
            # Add info on lists
            polygon_paths.append(polygon)
            inside_pixels.append(new_data[mask])
            # Reset the current polygon
            current_polygon = []
            # Refresh the canvas
            canvas.draw()

    # Abort function
    def _abort():
        print("\nFunction aborted")
        root.quit()
        root.destroy()

    # Close function
    def _quit():
        sigma = get_sigma()
        if not np.isnan(sigma):
            root.quit()
            root.destroy()
        else:
            root.quit()
            root.destroy()

    # Close shortcut
    def onkeypress(event):
        if event.key == 'q':
            _abort()

    # Clear all drawn and selected polygons
    def clear_polygons():
        nonlocal polygon_paths
        nonlocal current_polygon
        nonlocal inside_pixels
        nonlocal sigma
        # Reset sigma lists
        polygon_paths = []
        current_polygon = []
        inside_pixels = []
        sigma = np.nan
        # Remove sigma painted objects
        # Remove lines and scatter points
        for line in ax.lines:
            line.remove()
        # Remove patches
        for patch in ax.patches:
            patch.remove()
        # Remove texts
        for text in ax.texts:
            text.remove()
        canvas.draw()

    # Calculate sigma
    def get_sigma():
        nonlocal sigma
        all_data = np.array([])
        for inside_data in inside_pixels:
            all_data = np.append(all_data, inside_data)
        if statistic == 'std':
            sigma = np.std(all_data, ddof=1)
        elif statistic == 'rms':
            sigma = np.sqrt(np.mean(np.square(all_data)))
        return sigma

    # Change sigma statistic
    def change_to_std():
        nonlocal statistic
        statistic = 'std'
        sigma_button.config(relief=tk.SUNKEN)
        check_button.config(relief=tk.RAISED)
    def change_to_rms():
        nonlocal statistic
        statistic = 'rms'
        sigma_button.config(relief=tk.RAISED)
        check_button.config(relief=tk.SUNKEN)

    # Create a Matplotlib canvas embedded within the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Show toolbar
    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Create a frame for the statistic buttons
    stat_frame = tk.Frame(root)
    stat_frame.pack(side=tk.TOP, pady=5)
    if statistic == 'std':
        sigma_button = tk.Button(stat_frame, text="STD",
                                relief='sunken', command=change_to_std)
        sigma_button.pack(side=tk.LEFT, padx=3)
        check_button = tk.Button(stat_frame, text="RMS",
                                command=change_to_rms)
        check_button.pack(side=tk.LEFT, padx=3)
    elif statistic == 'rms':
        sigma_button = tk.Button(stat_frame, text="STD",
                                command=change_to_std)
        sigma_button.pack(side=tk.LEFT, padx=3)
        check_button = tk.Button(stat_frame, text="RMS",
                                relief='sunken', command=change_to_rms)
        check_button.pack(side=tk.LEFT, padx=3)

    # Create a frame for main buttons
    sigma_frame = tk.Frame(root)
    sigma_frame.pack(side=tk.BOTTOM)
    clear_button = tk.Button(sigma_frame, text="Clear", command=clear_polygons)
    clear_button.pack(side=tk.LEFT, padx=3)
    finish_button_sigma = tk.Button(sigma_frame, text="Finish", command=_quit)
    finish_button_sigma.pack(side=tk.RIGHT, padx=3)
    abort_button_sigma = tk.Button(sigma_frame, text="Abort", command=_abort)
    abort_button_sigma.pack(side=tk.RIGHT, padx=3)

    # Connect the onclick and onkeypress events to the canvas
    canvas.mpl_connect('button_press_event', onclick)
    canvas.mpl_connect('key_press_event', onkeypress)
    
    # Start the Tkinter event loop
    tk.mainloop()

    return sigma * fitsmap.unit
