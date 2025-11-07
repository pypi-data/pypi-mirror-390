import astropy.units as u

import copy

from IPython import get_ipython

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.contour import ContourSet
import matplotlib.patches as patches
import matplotlib.patheffects as PathEffects
from matplotlib.ticker import MultipleLocator

import numpy as np

import platform

import tkinter as tk

from madcubapy.visualization import add_wcs_axes
from madcubapy.visualization import add_colorbar
from madcubapy.visualization import parse_clabel
from madcubapy.coordinates import pixel_to_world

__all__ = [
    'import_region_contourset',
    'import_region_patch',
    'select_contour_regions',
]


def import_region_contourset(
        ax,
        contour,
        index=0,
        ref_fitsmap=None,
        **kwargs):
    """
    Import one contour region from a contour object into the selected
    axes.

    Parameters
    ----------
    ax : `~matplotlib.axes.Axes` or `~astropy.visualization.wcsaxes.WCSAxes`
        Axes object into which the contour region will be added.
    contour : `~matplotlib.contour.ContourSet`
        Contour object from which to take information.
    index : `int`, default=0
        Index of the contour region to be imported.
    ref_fitsmap : `~madcubapy.io.MadcubaMap` or `~astropy.nddata.CCDData`, \
                  optional
        Used to apply the transform if the fitsmap is different from
        the one plotted in the axes object.

    Returns
    -------
    new_CS : `~matplotlib.contour.ContourSet`
        Contour object containing the indexed contour region.

    Other Parameters
    ----------------
    **kwargs
        Parameters to pass to `~matplotlib.contour.ContourSet`.

    """

    # Create a contour with only one region.
    segment = contour.allsegs[0][index]
    if ref_fitsmap == None:
        new_CS = ContourSet(ax, [0], [[segment.tolist()]], **kwargs)
    else:
        new_CS = ContourSet(
            ax, [0], [[segment.tolist()]], 
            transform=ax.get_transform(ref_fitsmap.wcs.celestial),
            **kwargs,
        )
    
    return new_CS


def import_region_patch(
        ax,
        contour,
        index=0,
        ref_fitsmap=None,
        **kwargs):
    """
    Import one contour region from a contour object into the selected
    axes as a matplotlib patch.

    Parameters
    ----------
    ax : `~matplotlib.axes.Axes` or `~astropy.visualization.wcsaxes.WCSAxes`
        Axes object into which the contour region will be added.
    contour : `~matplotlib.contour.ContourSet`
        Contour object from which to take information.
    index : `int`, default=0
        Index of the contour region to be imported.
    ref_fitsmap : `~madcubapy.io.MadcubaMap` or `~astropy.nddata.CCDData`, \
                  optional
        Used to apply the transform if the fitsmap is different from
        the one plotted in the axes object.

    Returns
    -------
    poly : `~matplotlib.patches.Polygon`
        Polygon patch of the the indexed contour region.

    Other Parameters
    ----------------
    **kwargs
        Parameters to pass to `~matplotlib.patches.Polygon`.

    """

    # Default polygon params
    if ('color' not in kwargs and
        'ec' not in kwargs and
        'edgecolor' not in kwargs):
        kwargs['ec'] = 'white'
    if 'linewidth' not in kwargs:
        kwargs['linewidth'] = 1
    if 'linestyle' not in kwargs:
        kwargs['linestyle'] = 'solid'
    if 'fill' not in kwargs:
        kwargs['fill'] = False

    # Create a contour with only one region.
    segment = contour.allsegs[0][index]
    if ref_fitsmap == None:
        new_CS = ContourSet(ax, [0], [[segment.tolist()]])
    else:
        new_CS = ContourSet(
            ax, [0], [[segment.tolist()]], 
            transform=ax.get_transform(ref_fitsmap.wcs.celestial),
        )

    # The segments of the contourset are still in the original coordinates
    v = new_CS.allsegs[0][0]

    # Manually transform the vertices of the region to the new axes. The
    # ContourSet always stores coordinates in the original data, the transform
    # parameter is only for matplotlib to do a transformation and priont it,
    # not store it.
    if ref_fitsmap:
        world_coords = pixel_to_world(points=v, fitsmap=ref_fitsmap)
        # Finally we can do the same but backwards for the second axes.
        final_world2screen = ax.get_transform('world')
        final_screen2pix = ax.get_transform('pixel').inverted()
        final_screen_coords = final_world2screen.transform(world_coords.value)
        region_points = final_screen2pix.transform(final_screen_coords)
    else:
        region_points = v

    poly = patches.Polygon(xy=region_points, **kwargs)

    new_CS.remove()  # Remove contour from plot
    
    return poly


def select_contour_regions(
        contour,
        fig=None,
        ax=None,
        fitsmap=None,
        **kwargs):
    """
    Shows the regions contained in a contour object in a pop-up window and lets
    the user select closed contours as regions. Returns the indexes of the
    regions that have been clicked.
    
    Parameters
    ----------
    contour : `~matplotlib.contour.ContourSet`
        Contour object to plot as polygons with indexes.
    ax : `~astropy.visualization.wcsaxes.WCSAxes`, optional
        Ax object to use for displaying the contour.
    fig : `~matplotlib.figure.Figure`, optional
        Fig object to use for displaying the contour.
    fitsmap : `~madcubapy.io.MadcubaMap` or `~astropy.nddata.CCDData`, optional
        Map object to use for displaying the contour.

    Returns
    -------
    selected_indexes : `list`
        List with the indexes of the selected Polygons.

    Other Parameters
    ----------------
    **kwargs
        Parameters to pass to the :func:`~matplotlib.pyplot.imshow()` function.

    """

    # Create a Tkinter window
    root = tk.Tk()
    root.title("Check contour")

    # Create a Figure compatible with the input parameters
    if fitsmap != None:
        if ax != None or fig != None:
            raise TypeError(
                f"Only one or none of 'fitsmap', 'ax', and 'fig' can be set"
            )
        else:
            # Create a Matplotlib figure.
            new_fig = Figure(figsize=(7,7))
            if kwargs is None:
                kwargs = {}
            new_ax, new_img = add_wcs_axes(new_fig, 1, 1, 1, fitsmap=fitsmap,
                                           **kwargs)
            new_cbar = add_colorbar(new_ax)
    elif ax != None:
        if fitsmap != None or fig != None:
            raise TypeError(
                f"Only one or none of 'fitsmap', 'ax', and 'fig' can be set"
            )
        else:
            # Create new Figure and plot the image data from input axes
            new_fig = Figure(figsize=(7, 7))
            new_ax = new_fig.add_subplot(1,1,1)
            og_img = ax.get_images()[0]
            data = np.array(og_img.get_array())
            clim = og_img.get_clim()
            if kwargs is None:
                kwargs = {}
                kwargs['vmin'] = clim[0]
                kwargs['vmax'] = clim[1]
            new_img = new_ax.imshow(data, origin='lower', **kwargs)
    elif fig != None:
        if fitsmap != None or ax != None:
            raise TypeError(
                f"Only one or none of 'fitsmap', 'ax', and 'fig' can be set"
            )
        else:
            # Create new Figure and plot the image data from input figure
            new_fig = Figure(figsize=(7, 7))
            new_ax = new_fig.add_subplot(1,1,1)
            ax = fig.get_axes()[0]
            og_img = ax.get_images()[0]
            data = np.array(og_img.get_array())
            clim = og_img.get_clim()
            if kwargs is None:
                kwargs = {}
                kwargs['vmin'] = clim[0]
                kwargs['vmax'] = clim[1]
            new_img = new_ax.imshow(data, origin='lower', **kwargs)
    else:
        # Create a new Figure without a map
        new_fig = Figure(figsize=(7, 7))
        new_ax = new_fig.add_subplot(1,1,1)
        # Arrays to store data for plot limits
        x_maxs = np.array([])
        x_mins = np.array([])
        y_maxs = np.array([])
        y_mins = np.array([])

    # Prettier plots
    if fitsmap != None:
        new_ax.set_title('Check contour', fontsize=15, pad=20)
        new_ax.coords[0].set_axislabel("RA (ICRS)", fontsize=12)
        new_ax.coords[1].set_axislabel("DEC (ICRS)", fontsize=12)
        new_ax.coords[0].tick_params(which="major",
                                     length=5)
        new_ax.coords[0].display_minor_ticks(True)
        new_ax.coords[0].set_ticklabel(size=11, exclude_overlapping=True)
        new_ax.coords[1].tick_params(which="major",
                                     length=5)
        new_ax.coords[1].display_minor_ticks(True)
        new_ax.coords[1].set_ticklabel(size=11, exclude_overlapping=True,
                                       rotation='vertical')
        new_cbar.ax.set_ylabel(parse_clabel(fitsmap), fontsize=12)
        new_cbar.ax.tick_params(labelsize=11)
    else:
        new_ax.set_title('Check contour', fontsize=15, pad=20)
        new_ax.set_xlabel("FITS X", fontsize=12)
        new_ax.set_ylabel("FITS Y", fontsize=12)
        new_ax.tick_params(which='major',
                           length=5,
                           labelsize=11,
                           right=True,
                           top=True)
        new_ax.tick_params(which='minor',
                           right=True,
                           top=True)
        new_ax.xaxis.set_major_locator(MultipleLocator(25))
        new_ax.xaxis.set_minor_locator(MultipleLocator(5))
        new_ax.yaxis.set_major_locator(MultipleLocator(25))
        new_ax.yaxis.set_minor_locator(MultipleLocator(5))

    # Visual options for the contour regions
    if fitsmap == None and ax == None and fig == None:
        ec='blue'
        fc='C0'
        text_color = '0.7'
        text_fg = 'black'
    else:
        ec='white'
        fc=(0.7, 0.7, 0.7, 0.5)
        text_color = 'white'
        text_fg = '0.5'

    # Initialize rrays to store polygons, patches, and indexes
    polygons = []
    selected_artists = []   # List of used patches, needed for the if
                            # condition of the mouse hover event.
    selected_indexes = []
    polygon_texts = []
    return_indexes = None
    # Plot the contour as polygons
    for i in range(len(contour.allsegs[0])):
        v = contour.allsegs[0][i]
        poly = patches.Polygon(xy=v, lw=1, ec=ec, fc=fc,
                               fill=False, closed=True, picker=True)
        new_ax.add_patch(poly)
        polygons.append(poly)
        center = v.mean(axis=0)
        txt = new_ax.text(center[0], center[1], f'{i}', color=text_color,
                      ha = 'center', va='center', visible=False)
        txt.set_path_effects([PathEffects.withStroke(linewidth=1.5,
                                                     foreground=text_fg)])
        polygon_texts.append(txt)
        # Store X and Y info for empty image limits
        if fitsmap == None and ax == None and fig == None:
            x_maxs = np.append(x_maxs, contour.allsegs[0][i][:,0].max())
            x_mins = np.append(x_mins, contour.allsegs[0][i][:,0].min())
            y_maxs = np.append(y_maxs, contour.allsegs[0][i][:,1].max())
            y_mins = np.append(y_mins, contour.allsegs[0][i][:,1].min())

    # Set zoom level at image range +- 5% if no image is provided
    if fitsmap == None and ax == None and fig == None:
        x_lim = (x_mins.min() - (x_maxs.max() - x_mins.min()) * 0.05,
                 x_maxs.max() + (x_maxs.max() - x_mins.min()) * 0.05)
        y_lim = (y_mins.min() - (y_maxs.max() - y_mins.min()) * 0.05, 
                 y_maxs.max() + (y_maxs.max() - y_mins.min()) * 0.05)
        new_ax.set_xlim(x_lim)
        new_ax.set_ylim(y_lim)

    ### Interactive functions ###
    def _save():
        nonlocal return_indexes
        return_indexes = selected_indexes
        root.quit()
        root.destroy()
    def _quit():
        root.quit()
        root.destroy()
    # Save and Quit shortcuts
    def onkeypress(event):
        if event.key == 'q':
            _quit()
        if event.key == 's':
            _save()
    # Store desired polygons with their indexes
    def on_pick(event):
        nonlocal selected_indexes
        nonlocal selected_artists
        nonlocal polygons
        artist = event.artist
        if isinstance(artist, patches.Polygon):
            for i in range(len(polygons)):
                if polygons[i] == artist:
                    artist.set(fill=True)
                    verts = artist.get_xy()
                    center = verts.mean(axis=0)
                    polygon_texts[i].set_position(center)
                    polygon_texts[i].set(visible=True)
                    print(f"Selected the contour with index {i}")
                    # Add the index artist avoiding duplicates
                    if i not in selected_indexes:
                        selected_indexes.append(i)
                    if artist not in selected_artists:
                        selected_artists.append(artist)
        # Refresh the canvas
        canvas.draw()
    # Highlight polygon and show its index on mouseover
    def on_hover(event):
        nonlocal polygons
        nonlocal selected_artists
        nonlocal polygon_texts
        for i in range(len(polygons)):
            # Only highlight non-selected regions
            if polygons[i] not in selected_artists:
                # Check if the mouse is over a polygon
                if polygons[i].contains(event)[0]:
                    polygons[i].set_linewidth(2)
                    text_x = event.xdata + 0.02 \
                             * (new_ax.get_xlim()[1] - new_ax.get_xlim()[0])
                    text_y = event.ydata + 0.02 \
                             * (new_ax.get_ylim()[1] - new_ax.get_ylim()[0])
                    polygon_texts[i].set_position((text_x, text_y))
                    polygon_texts[i].set(visible=True)
                else:
                    polygons[i].set_linewidth(1)
                    polygon_texts[i].set(visible=False)
        # Redraw the figure
        canvas.draw()

    ### tkinter window design ###
    # Create a Matplotlib canvas embedded within the Tkinter window
    canvas = FigureCanvasTkAgg(new_fig, master=root)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    # Show toolbar.
    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    # Buttons
    button_frame = tk.Frame(root)
    button_frame.pack(side=tk.BOTTOM, pady=3)
    abort_button = tk.Button(master=button_frame, text="Abort", command=_quit)
    abort_button.pack(side=tk.RIGHT, padx=5)
    save_button = tk.Button(master=button_frame, text="Save and exit",
                            command=_save)
    save_button.pack(side=tk.LEFT, padx=5)

    # Connect events to the canvas
    canvas.mpl_connect('key_press_event', onkeypress)
    canvas.mpl_connect('pick_event', on_pick)
    canvas.mpl_connect('motion_notify_event', on_hover)

    # Start the Tkinter event loop
    tk.mainloop()

    return return_indexes


def _check_sigma_contours(
        ax,
        fitsmap):
    """
    Disclaimer: Test Function

    Open a window with two main tabs.
    The first one lets the user select polygons in the map that are used
    to calculate the noise (sigma).
    The second one plots the contour of an input level times the desired
    calculated sigma value. The user can then select the desired
    polygons to add them to the image of the input ax object.
    
    Parameters
    ----------
    ax : `~astropy.visualization.wcsaxes.WCSAxes`
        Axes object in which to add the ContourSet object(s).
    fitsmap : `~madcubapy.io.MadcubaMap` or `~astropy.nddata.CCDData`, optional
        Map object to use for calculating sigma and its contours.

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
    left_click = 1

    # Create a Tkinter window
    root = tk.Tk()
    root.title("Check contour")

    ### Functions ###
    # Calculate sigma
    def get_sigma():
        nonlocal sigma
        all_data = np.array([])
        for inside_data in inside_pixels:
            all_data = np.append(all_data, inside_data)
        sigma = np.std(all_data, ddof=0)
        print(f"sigma: {sigma}")
        return sigma
    # Plot a (Quad)ContourSet as polygons
    def plot_contour_polygons(contour):
        nonlocal check_ax
        for i in range(len(contour.allsegs[0])):
            v = contour.allsegs[0][i]
            poly = patches.Polygon(xy=v, lw=1, ec='1', fc=(0.7, 0.7, 0.7, 0.5),
                                   fill=False, closed=True, picker=True)
            check_ax.add_patch(poly)
            polygons.append(poly)
            center = v.mean(axis=0)
            txt = check_ax.text(center[0], center[1], f'{i}', color='white',
                        ha = 'center', va='center', visible=False)
            txt.set_path_effects([PathEffects.withStroke(linewidth=1.5,
                                                        foreground='0.5')])
            polygon_texts.append(txt)
    # Main call to create and plot contours
    def plot_contours(sigma, level):
        nonlocal check_ax
        nonlocal sigma_contour
        sigma_contour = check_ax.contour(fitsmap.data[0, 0, :, :],
                                        [level*sigma], origin=None,
                                        colors=['white'], linewidths=3)
        sigma_contour.remove()
        plot_contour_polygons(sigma_contour)

    # Calculate sigma half
    def calculate_sigma_part():
        nonlocal current_figure
        if current_figure == 'check':
            canvas.figure = sigma_fig
            current_figure = 'sigma'
            canvas.draw()
            # Change bottom frame
            check_frame.pack_forget()
            sigma_frame.pack(side=tk.TOP, pady=10)
            check_button.config(relief=tk.RAISED)
            sigma_button.config(relief=tk.SUNKEN)
        else:
            return
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
        # Lines and scatter points
        for line in sigma_ax.lines:
            line.remove()
        # Patches
        for patch in sigma_ax.patches:
            patch.remove()
        # Texts
        for text in sigma_ax.texts:
            text.remove()
        canvas.draw()
    # Create polygons by hand
    def onclick(event):
        nonlocal polygon_paths
        nonlocal current_polygon
        nonlocal inside_pixels
        if current_figure == 'sigma':
            # Left-click to select points
            if event.button == left_click:
                # Add the clicked point to the current polygon
                current_polygon.append((event.xdata, event.ydata))
                now_polygon = np.array(current_polygon)
                # Draw a small point at the first clicked point
                if len(now_polygon) == 1:
                    sigma_ax.plot(event.xdata, event.ydata,
                                  'white', marker='o', markersize=5)
                # Draw lines
                if len(now_polygon) > 1:
                    sigma_ax.plot(now_polygon[-2:, 0], now_polygon[-2:, 1],
                                  'white', lw=2, alpha=0.9)
                    sigma_ax.plot(event.xdata, event.ydata,
                                  'white', marker='o', markersize=5)
                # Refresh the canvas
                canvas.draw()
            # Right-click to finalize the current polygon
            elif event.button == right_click and current_polygon:
                polygon = np.array(current_polygon)
                # Draw the last side of the polygon
                closed_polygon = np.vstack((polygon, polygon[0]))
                sigma_ax.plot(closed_polygon[-2:, 0], closed_polygon[-2:, 1],
                              'white', lw=2, alpha=0.9)
                # Draw the polygon on the plot
                poly = patches.Polygon(xy=polygon, linewidth=2,
                                       edgecolor='white', facecolor='white',
                                       alpha=0.5)
                new_poly=copy.copy(poly)
                sigma_ax.add_patch(new_poly)
                # Get the shape of the CCDData object
                if fitsmap.header['NAXIS'] == 2:
                    height, width = fitsmap.data.shape
                elif fitsmap.header['NAXIS'] == 3:
                    freq, height, width = fitsmap.data.shape
                elif fitsmap.header['NAXIS'] == 4:
                    freq, stokes, height, width = fitsmap.data.shape
                # Create a meshgrid of coordinates to create mask
                x, y = np.meshgrid(range(width), range(height))
                points = np.vstack((x.flatten(), y.flatten())).T
                mask = poly.contains_points(points, radius=0)
                mask = mask.reshape((height, width))
                # Calculate std
                new_data = copy.copy(fitsmap.data[0,0,:,:])
                std = new_data[mask].std()
                # Paint std inside polygon
                x_text = polygon.T[0].min() \
                        + (polygon.T[0].max() - polygon.T[0].min()) / 2
                y_text = polygon.T[1].min() \
                        + (polygon.T[1].max() - polygon.T[1].min()) / 2
                std_text = sigma_ax.text(x_text, y_text, f'{std:.2f}',
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
        else:
            return

    # Select contour regions half
    def plot_contour_fig():
        nonlocal sigma_contour
        nonlocal polygons
        nonlocal selected_artists
        nonlocal selected_indexes
        nonlocal polygon_texts
        nonlocal level
        checked_contour = True  # For now, always reset contour plotting
        # Reset the check contour figure to start over
        if checked_contour != None:
            # Reset check lists
            polygons = []
            selected_artists = []
            selected_indexes = []
            polygon_texts = []
            # Remove check polygons
            for patch in check_ax.patches:
                patch.remove()
            for text in check_ax.texts:
                text.remove()
            # Reset sigma_contour
            sigma_contour = None
        # Plot contours
        sigma = get_sigma()
        level = float(level_box.get())
        plot_contours(sigma, level)
        canvas.figure = check_fig
        canvas.draw()
    def select_contour_regions_part():
        nonlocal current_figure
        if current_figure == 'sigma':
            plot_contour_fig()
            current_figure = 'check'
            # Reconnect events to current figure, as mpl_connect does not
            # connect it to the canvas, but to the figure in the canvas.
            canvas.mpl_connect('key_press_event', onkeypress)
            canvas.mpl_connect('button_press_event', on_pick_click)
            canvas.mpl_connect("motion_notify_event", on_hover)
            # Change bottom frame
            sigma_frame.pack_forget()
            check_frame.pack(side=tk.TOP, pady=10, fill=tk.X)
            # Set button relief states
            sigma_button.config(relief=tk.RAISED)
            check_button.config(relief=tk.SUNKEN)
        else:
            return
    # Store desired polygons with their indexes
    def on_pick_click(event):
        nonlocal selected_indexes
        nonlocal selected_artists
        nonlocal polygons
        if current_figure == 'check':
            if event.inaxes:
                for i in range(len(polygons)):
                    if polygons[i].contains_point((event.x, event.y)):
                        polygons[i].set(fill=True)
                        verts = polygons[i].get_xy()
                        center = verts.mean(axis=0)
                        polygon_texts[i].set_position(center)
                        polygon_texts[i].set(visible=True)
                        print(f"Selected the contour with index {i}")
                        # Add the index artist avoiding duplicates
                        if i not in selected_indexes:
                            selected_indexes.append(i)
                        if polygons[i] not in selected_artists:
                            selected_artists.append(polygons[i])
                # Refresh the canvas
                canvas.draw()
        else:
            return
    # Highlight polygon and show its index on mouseover
    def on_hover(event):
        nonlocal polygons
        nonlocal selected_artists
        nonlocal polygon_texts
        if current_figure == 'check':
            for i in range(len(polygons)):
                # Highlight non-selected regions on mouseover
                if polygons[i] not in selected_artists:
                    # Check if the mouse is over a polygon
                    if polygons[i].contains_point((event.x, event.y)):
                        polygons[i].set_linewidth(2)
                        text_x = event.xdata + 0.02 \
                                 * (check_ax.get_xlim()[1]
                                   - check_ax.get_xlim()[0])
                        text_y = event.ydata + 0.02 \
                                 * (check_ax.get_ylim()[1]
                                   - check_ax.get_ylim()[0])
                        polygon_texts[i].set_position((text_x, text_y))
                        polygon_texts[i].set(visible=True)
                    else:
                        polygons[i].set_linewidth(1)
                        polygon_texts[i].set(visible=False)
            # Redraw the figure
            canvas.draw()
        else:
            return

    # Add exit pathways
    def _quit():
        root.quit()
        root.destroy()
    # Save and exit
    def _exit_plotting():
        nonlocal ax
        for i in selected_indexes:
            new_contour = import_region_contourset(
                ax=ax, contour=sigma_contour, index=i, colors='white',
                linewidths=[1], linestyles='-'
            )
        root.quit()
        root.destroy()
    # Save and Abort shortcuts
    def onkeypress(event):
        if event.key == 'q':
            _quit()
        if event.key == 's':
            _exit_plotting()

    # Initialize lists to store the polygons, arrays with pixel data...
    # Calculate sigma
    polygon_paths = []
    current_polygon = []
    inside_pixels = []
    sigma = np.nan
    # Check contour
    polygons = []
    selected_artists = []   # List of used patches, needed for the 'if'
                            # condition of the mouse hover event.
    selected_indexes = []
    polygon_texts = []
    level = 5
    # Track current Figure
    current_figure = 'sigma'
    # Default contour
    sigma_contour = None
    
    # Create Matplotlib figures
    sigma_fig = mpl.figure.Figure(figsize=(7,6))
    sigma_ax, sigma_img = add_wcs_axes(sigma_fig, 1, 1, 1,
                                       fitsmap=fitsmap,
                                       vmin=0, vmax=300)
    sigma_cbar = add_colorbar(sigma_ax)
    check_fig = mpl.figure.Figure(figsize=(7,6))
    check_ax, check_img = add_wcs_axes(check_fig, 1, 1, 1,
                                       fitsmap=fitsmap,
                                       vmin=0, vmax=300)
    check_cbar = add_colorbar(check_ax)
    # Prettier plots
    sigma_ax.set_title('Calculate sigma', fontsize=15, pad=20)
    check_ax.set_title('Contour check', fontsize=15, pad=20)
    for axis in [sigma_ax, check_ax]:
        axis.coords[0].set_axislabel("RA (ICRS)", fontsize=12)
        axis.coords[1].set_axislabel("DEC (ICRS)", fontsize=12)
        axis.coords[0].tick_params(which="major",
                                   length=5)
        axis.coords[0].display_minor_ticks(True)
        axis.coords[0].set_ticklabel(size=11, exclude_overlapping=True)
        axis.coords[1].tick_params(which="major",
                                   length=5)
        axis.coords[1].display_minor_ticks(True)
        axis.coords[1].set_ticklabel(size=11, exclude_overlapping=True,
                                     rotation='vertical')
    for colorbar in [sigma_cbar, check_cbar]:
        colorbar.ax.set_ylabel(parse_clabel(fitsmap), fontsize=12)
        colorbar.ax.tick_params(labelsize=11)

    ### tkinter window design ###
    # Create a frame for the main buttons above the figure canvas
    tab_frame = tk.Frame(root)
    tab_frame.pack(side=tk.TOP, pady=10)
    # Main buttons
    sigma_button = tk.Button(tab_frame, text="Calculate sigma",
                             relief='sunken', command=calculate_sigma_part)
    sigma_button.pack(side=tk.LEFT, padx=2)
    check_button = tk.Button(tab_frame, text="Check contour",
                             command=select_contour_regions_part)
    check_button.pack(side=tk.LEFT, padx=2)
    # Create a Matplotlib canvas embedded within the Tkinter window
    canvas = FigureCanvasTkAgg(sigma_fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    # Show toolbar
    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()
    # Create a frame for sigma calculation
    sigma_frame = tk.Frame(root)
    sigma_frame.pack(side=tk.TOP, pady=10)
    clear_button = tk.Button(sigma_frame, text="Clear", command=clear_polygons)
    clear_button.pack(side=tk.LEFT, padx=2)
    abort_button_sigma = tk.Button(sigma_frame, text="Abort", command=_quit)
    abort_button_sigma.pack(side=tk.RIGHT, padx=2)
    # Create a frame for contour checking and do not show it yet
    check_frame = tk.Frame(root)
    # Secondary frame for exit buttons
    # By being in a frame inside the check frame, these two buttons are
    # placed together in the center of the available space by using
    # expand=True. If they are not in the second frame, the buttons use
    # half of the available space each and lay separated.
    check_exit_frame = tk.Frame(check_frame)
    check_exit_frame.pack(side=tk.LEFT, expand=True)
    finish_button = tk.Button(check_exit_frame, text="Save and exit",
                              command=_exit_plotting)
    finish_button.pack(side=tk.LEFT, padx=2)
    abort_button_check = tk.Button(check_exit_frame, text="Abort",
                                   command=_quit)
    abort_button_check.pack(side=tk.RIGHT, padx=2)
    # Select sigma level UI
    plot_contours_button = tk.Button(check_frame, text="Update contour",
                                     command=plot_contour_fig)
    plot_contours_button.pack(side=tk.RIGHT, padx=5)
    sigma_symbol = tk.Label(check_frame, text='σ')
    sigma_symbol.pack(side=tk.RIGHT)
    level_box = tk.Entry(check_frame, width=2)
    level_box.insert(0, 5)
    level_box.pack(side=tk.RIGHT)
    level_label = tk.Label(check_frame, text='Level:')
    level_label.pack(side=tk.RIGHT)

    # Connect shortcut and sigma events to the first canvas
    canvas.mpl_connect('key_press_event', onkeypress)
    canvas.mpl_connect('button_press_event', onclick)

    # Start the Tkinter event loop
    root.mainloop()
