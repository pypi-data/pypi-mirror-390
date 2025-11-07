from astropy.nddata import CCDData
from IPython import get_ipython
import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import matplotlib.pyplot as plt
import numpy as np
import platform
import tkinter as tk

from madcubapy.io import MadcubaMap
from .wcsaxes_helpers import add_wcs_axes
from .wcsaxes_helpers import insert_colorbar

__all__ = [
    'get_input',
]


def get_input(obj, **kwargs):
    """
    Get the pixel coordinates of points selected by mouse clicks in a
    previously plotted figure or a map object.

    Parameters
    ----------
    obj : `~matplotlib.figure.Figure`, \
          `~astropy.nddata.CCDData`, or \
          `~madcubapy.io.MadcubaMap` object.
        Figure or Map object to show and from which to get coordinates.

    Returns
    -------
    selected_points : `numpy.array`
        Coordinates of the clicked points.

    Other Parameters
    ----------------    
    **kwargs
        Optional map visualization parameters passed to
        :func:`~madcubapy.visualization.add_wcs_axes` only if `obj` is a
        `~astropy.nddata.CCDData` or `~madcubapy.io.MadcubaMap` object.
        
    """
    
    if isinstance(obj, plt.Figure):
        return _get_input_from_figure(obj)
    elif isinstance(obj, CCDData) or isinstance(obj, MadcubaMap):
        return _get_input_from_map(obj, **kwargs)
    else:
        raise TypeError("Unsupported type. " +
            "Provide a Matplotlib Figure, MadcubaMap, or CCDData object.")


def _get_input_from_figure(fig):
    """
    Returns mouse click coordinates using a previously created figure.

    Parameters
    ----------
    fig : `~matplotlib.figure.Figure`
        Figure object to show and from which to get coordinates.

    Returns
    -------
    selected_points : `numpy.array`
        Coordinates of the clicked points.

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
    
    original_backend = mpl.get_backend()

    try:
        # Change matplotlib backend to tkinter
        mpl.use("TkAgg", force=True)  # Switch to TkAgg
        # Bring figure back from the dead
        new_fig = plt.figure()
        new_manager = new_fig.canvas.manager
        new_manager.canvas.figure = fig
        fig.set_canvas(new_manager.canvas)
        # Get input from clicks
        selected_points = fig.ginput(
            n=0, timeout=0,
            mouse_add=1, mouse_pop=middle_click, mouse_stop=right_click,
        )
        # Close figure to prevent issues
        plt.close('all')
    except Exception as e:
        raise RuntimeError(
            f"Failed to execute operation with TkAgg backend: {e}"
        )
    finally:
        try:
            # Change matplotlib backend back to inline
            mpl.use(original_backend, force=True)  # Restore original backend
            plt.close("all")  # Close any figures to prevent issues
        except Exception as e:
            raise RuntimeError(
                f"Failed to restore original backend ({original_backend}): {e}"
            )

    return np.array(selected_points)


def _get_input_from_map(fitsmap, **kwargs):
    """
    Returns mouse click coordinates using a `~astropy.nddata.CCDData` or
    `~madcubapy.io.madcubaMap` object.

    Parameters
    ----------
    fitsmap : `~astropy.nddata.CCDData` or `~madcubapy.io.MadcubaMap`
        Map object to show and from which to get coordinates.

    Returns
    -------
    selected_points : `numpy.array`
        Coordinates of the clicked points.

    Other Parameters
    ----------------
    **kwargs
        Parameters to pass to :func:`~madcubapy.visualization.add_wcs_axes`.

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

    # Create a Tkinter window
    root = tk.Tk()
    root.title("Sigma calculation")

    # Create a Matplotlib figure
    fig = mpl.figure.Figure(figsize=(7, 6), dpi=100)
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

    # Lists to store selected points and plot markers
    selected_points = []
    plot_markers = []

    # Create a callback function for mouse clicks
    def onclick(event):
        nonlocal selected_points, plot_markers
        # Left-click to select points
        if event.button == 1:
            if event.xdata is not None and event.ydata is not None:
                # Add the clicked point to the current polygon
                selected_points.append((event.xdata, event.ydata))
                # Draw the clicked point and add it to the list
                marker = ax.plot(event.xdata, event.ydata,
                                 'red', marker='+', markersize=6)
                plot_markers.append(marker)
                # Refresh the canvas
                canvas.draw()
        # Middle-click to remove last selected point
        elif event.button == middle_click:
            if selected_points:
                # Remove last selected point
                selected_points.pop()
                # Remove last painted point from plot and list
                marker = plot_markers[-1][0]
                marker.remove()
                plot_markers.pop()
                # Refresh the canvas
                canvas.draw()
        # Right-click to finalize the current polygon
        elif event.button == right_click:
            # Refresh the canvas
            _quit()

    # Function to clear all selected points
    def clear_points():
        nonlocal selected_points, plot_markers
        # Remove all selected points
        selected_points.clear()
        # Remove all painted points
        while plot_markers:
            marker = plot_markers[-1][0]
            marker.remove()
            plot_markers.pop()
        canvas.draw()

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
    # "Clear All" button
    clear_button = tk.Button(control_frame, text="Clear All", command=clear_points)
    clear_button.pack(side=tk.LEFT, padx=5)
    # "Finish" button
    finish_button = tk.Button(control_frame, text="Finish", command=_quit)
    finish_button.pack(side=tk.RIGHT, padx=5)

    # Connect the onclick and onkeypress events to the canvas
    canvas.mpl_connect('button_press_event', onclick)
    canvas.mpl_connect('key_press_event', onkeypress)
    
    # Start the Tkinter event loop
    root.mainloop()

    return np.array(selected_points)
