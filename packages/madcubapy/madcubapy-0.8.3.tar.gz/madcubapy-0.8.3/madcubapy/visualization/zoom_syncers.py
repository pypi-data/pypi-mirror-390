from astropy.visualization.wcsaxes import WCSAxes
import numpy as np
from madcubapy.coordinates import transform_coords_axes
from madcubapy.coordinates import transform_coords_fitsmap

__all__ = [
    'copy_zoom_fitsmap',
    'copy_zoom_axes',
    'sync_zoom',
]


def copy_zoom_fitsmap(
        ref_fitsmap,
        target_fitsmap,
        x_lim,
        y_lim,
        origin=0):
    """
    Copy a map's limits to another map.

    Parameters
    ----------
    ref_fitsmap : `~madcubapy.io.MadcubaMap` or `~astropy.nddata.CCDData`
        Reference mape.
    target_fitsmap : `~madcubapy.io.MadcubaMap` or `~astropy.nddata.CCDData`
        Map into which limits are transformed.
    x_lim : array-like
        X axis limits from ref_fitsmap.
    y_lim : array-like
        Y axis limits from ref_fitsmap.
    origin : int
        Origin of the coordinates of the image. 0 for numpy standards,
        and 1 for FITS standards.

    Returns
    -------
    new_x_lim : `list`
        Transformed X axis limits.
    new_y_lim : `list`
        Transformed Y axis limits.

    """

    if len(x_lim) != 2 or len(y_lim) != 2:
        raise TypeError(f"Limits need to be delimited by two coordinates " 
                        + "each (min, max)")

    # Image corners
    bottom_left = np.array([x_lim[0], y_lim[0]])
    top_right = np.array([x_lim[1], y_lim[1]])
    # Transform limits
    new_bottom_left = transform_coords_fitsmap(ref_fitsmap=ref_fitsmap,
                                               target_fitsmap=target_fitsmap,
                                               points=bottom_left,
                                               origin=origin)
    new_top_right = transform_coords_fitsmap(ref_fitsmap=ref_fitsmap,
                                             target_fitsmap=target_fitsmap,
                                             points=top_right,
                                             origin=origin)
    # Return new limits
    new_x_lim = [new_bottom_left[0], new_top_right[0]]
    new_y_lim = [new_bottom_left[1], new_top_right[1]]

    return new_x_lim, new_y_lim


def copy_zoom_axes(
        ref_ax,
        target_ax):
    """
    Copy a `~astropy.visualization.wcsaxes.WCSAxes` limits to another
    `~astropy.visualization.wcsaxes.WCSAxes`.

    Parameters
    ----------
    ref_ax : `~astropy.visualization.wcsaxes.WCSAxes`
        Reference Axes.
    target_ax : `~astropy.visualization.wcsaxes.WCSAxes`
        Axes into which limits are transformed.

    """

    # Read limits
    x_lim = ref_ax.get_xlim()
    y_lim = ref_ax.get_ylim()
    # Image corners
    bottom_left = np.array([x_lim[0], y_lim[0]])
    top_right = np.array([x_lim[1], y_lim[1]])
    # Transform limits
    new_bottom_left = transform_coords_axes(ref_ax=ref_ax,
                                            target_ax=target_ax,
                                            points=bottom_left)
    new_top_right = transform_coords_axes(ref_ax=ref_ax,
                                          target_ax=target_ax,
                                          points=top_right)
    # Set new limits
    target_ax.set_xlim(new_bottom_left[0], new_top_right[0])
    target_ax.set_ylim(new_bottom_left[1], new_top_right[1])


def sync_zoom(
        *axes):
    """
    Synchronize X and Y limits between any number of
    `~astropy.visualization.wcsaxes.WCSAxes` objects.

    Parameters
    ----------
    *axes : `~astropy.visualization.wcsaxes.WCSAxes`
        WCSAxes objects to synchronize.

    Notes
    _____
    Do not use this function too many times. It seems that python stores
    every axes object connected in a given jupyter kernel run. If the
    session runs for too long, the program will slow down considerably.

    """

    # Check that all provided axes are instances of WCSAxes
    if not all(isinstance(ax, WCSAxes) for ax in axes):
        raise TypeError("All arguments must be instances of WCSAxes.")

    class LimitSyncer:
        def __init__(self):
            # Shared state to prevent recursion
            self.updating = False

        def sync_x_limits(self, ax):
            if self.updating:
                return
            self.updating = True
            try:
                # Read limits from reference axes
                x_lim = ax.get_xlim()
                y_lim = ax.get_ylim()
                # Image corners
                bottom_left = np.array([x_lim[0], y_lim[0]])
                top_right = np.array([x_lim[1], y_lim[1]])
                for axis in axes:
                    if axis != ax:
                        # Transform limits
                        new_bottom_left = transform_coords_axes(
                            ref_ax=ax,
                            target_ax=axis,
                            points=bottom_left
                        )
                        new_top_right = transform_coords_axes(
                            ref_ax=ax,
                            target_ax=axis,
                            points=top_right
                        )
                        # Set new limits in target axes
                        axis.set_xlim(new_bottom_left[0], new_top_right[0])
            finally:
                self.updating = False

        def sync_y_limits(self, ax):
            if self.updating:
                return
            self.updating = True
            try:
                # Read limits from reference axes
                x_lim = ax.get_xlim()
                y_lim = ax.get_ylim()
                # Image corners
                bottom_left = np.array([x_lim[0], y_lim[0]])
                top_right = np.array([x_lim[1], y_lim[1]])
                for axis in axes:
                    if axis != ax:
                        # Transform limits
                        new_bottom_left = transform_coords_axes(
                            ref_ax=ax,
                            target_ax=axis,
                            points=bottom_left
                        )
                        new_top_right = transform_coords_axes(
                            ref_ax=ax,
                            target_ax=axis,
                            points=top_right
                        )
                        # Set new limits in target axes
                        axis.set_ylim(new_bottom_left[1], new_top_right[1])
            finally:
                self.updating = False

    # Create an instance of the limit syncer
    syncer = LimitSyncer()

    # Connect the limit change events to the syncer methods
    # For this loop, it is needed to pass ax to the lambda function
    for ax in axes:
        ax.callbacks.connect('xlim_changed',
                             lambda event, ax=ax : syncer.sync_x_limits(ax))
        ax.callbacks.connect('ylim_changed',
                             lambda event, ax=ax : syncer.sync_y_limits(ax))
