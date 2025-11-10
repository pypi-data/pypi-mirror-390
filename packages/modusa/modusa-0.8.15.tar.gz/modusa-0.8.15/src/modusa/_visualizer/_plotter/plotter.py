#!/usr/bin/env python3

#---------------------------------
# Author: Ankit Anand
# Date: 09/11/25
# Email: ankit0.anand0@gmail.com
#---------------------------------

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from collections.abc import Iterable

import fnmatch

class Plotter:
    
    def __init__(self):
        pass
        
    @staticmethod
    def signal(
        ax,
        y,
        x=None,
        c=None,
        ls=None,
        lw=None,
        m=None,
        ms=3,
        label=None
    ):
        """
        Paint 1D array/signal to the current tile.
    
        Parameters
        ----------
        ax: plt.Axes
            Which axis to plot the signal on.
        y: np.ndarray
            Signal y values.
        x: np.ndarray | None
            Signal x values.
            Default: None (indices will be used)
        c: str
            Color of the line.
            Default: None
        ls: str
            Linestyle
            Default: None
        lw: Number
            Linewidth
            Default: None
        m: str
            Marker
            Default: None
        ms: number
            Markersize
            Default: 3

        Returns
        -------
        None
        """
            
        if x is None: x = np.arange(y.size)
            
        ax.plot(x, y, color=c, linestyle=ls, linewidth=lw, marker=m, markersize=ms, label=label)
        
    @staticmethod
    def image(
        ax,
        M,
        y=None,
        x=None,
        c="gray_r",
        o="upper",
        clabel=None,
        cax=None,
        alpha=1,
    ):
        """
        Paint image (2D matrix / 2D grayscale image / 3D RGB image)
        to the current tile.
    
        Parameters
        ----------
        M: np.ndarray
            - Matrix (2D) array
        y: np.ndarray | None
            - y axis values.
        x: np.ndarray | None (indices will be used)
            - x axis values.
            - Default: None (indices will be used)
        c: str
            - cmap for the matrix.
            - Default: None
        o: str
            - origin
            - Default: "lower"
        label: str
            - Label for the plot.
            - Legend will use this.
            - Default: None
        ylabel: str
            - y-label for the plot.
            - Default: None
        ylim: tuple
            - y-lim for the plot.
            - Default: None
        yticks: Arraylike
            - Positions at which to place y-axis ticks.
        yticklabels : list of str, optional
            - Labels corresponding to `yticks`. Must be the same length as `yticks`.
        xlabel: str
            - x-label for the plot.
            - Default: None
        xticks: Arraylike
            - Positions at which to place x-axis ticks.
        xticklabels : list of str, optional
            - Labels corresponding to `xticks`. Must be the same length as `xticks`.
        cax: plt.Axes
            - Which ax to put colorbar on
            - Default: None
        alpha: float (0 to 1)
            - Transparency level
            - 1 being opaque and 0 being completely transparent
            - Default: 1
    
        Returns
        -------
        None
        """
    
        if x is None:
            x = np.arange(M.shape[1])
        if y is None:
            y = np.arange(M.shape[0])
            
        def _calculate_extent(x, y, o):
            """
            Calculate x and y axis extent for the
            2D matrix.
            """
            # Handle spacing safely
            if len(x) > 1:
                dx = x[1] - x[0]
            else:
                dx = 1  # Default spacing for single value
            if len(y) > 1:
                dy = y[1] - y[0]
            else:
                dy = 1  # Default spacing for single value
                
            if o == "lower":
                return [x[0] - dx / 2, x[-1] + dx / 2, y[0] - dy / 2, y[-1] + dy / 2]
            else:
                return [x[0] - dx / 2, x[-1] + dx / 2, y[-1] + dy / 2, y[0] - dy / 2]
            
        extent = _calculate_extent(x, y, o)
        
        im = ax.imshow(M, aspect="auto", origin=o, cmap=c, extent=extent, alpha=alpha)
                
        # Colorbar
        if cax is not None:
            cax.axis("on")
            cbar = plt.colorbar(im, cax=cax)
            if clabel is not None:
                cbar.set_label(clabel, labelpad=5)
                
            
    @staticmethod
    def annotation(
        ax,
        ann,
        patterns=None,
        text_loc="m",
        alpha=0.7,
    ):
        """
        Paint annotation to the current tile.
        Use modusa.load_ann() output.
    
        Parameters
        ----------
        ann : list[tuple[Number, Number, str]] | None
            - A list of annotation spans. Each tuple should be (start, end, label).
            - Default: None (no annotations).
        patterns: list[str]
            - Patterns to group annotations
            - E.g., "*R" or "<tag>*" or ["A*", "*B"]
            - All elements in a group will have same color.
        ylim: tuple[number, number]
            - Y-limit for the annotation.
            - Default: (0, 1)
        text_loc: str
            - Location of text relative to the box. (b for bottom, m for middle, t for top)
            - Default: "m"
        alpha
        grid: bool
            - Do you want the grid?
            - Default: True
    
        Returns
        -------
        None
        """
        
        # Get the xlim as we will only be plotting for the region defined by xlim
        xlim: tuple[float, float] = ax.get_xlim()
        ylim: tuple[float, float] = ax.get_ylim()
        
        if isinstance(patterns, str): patterns = [patterns]
        ann_copy = ann.copy()
        
        if patterns is not None:
            for i, (start, end, tag) in enumerate(ann_copy):
                group = None
                for j, pattern in enumerate(patterns):
                    if fnmatch.fnmatch(tag, pattern):
                        group = j
                        break
                ann_copy[i] = (start, end, tag, group)
        else:
            for i, (start, end, tag) in enumerate(ann_copy):
                ann_copy[i] = (start, end, tag, None)
                
        colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        
        # Text Location
        if text_loc in ["b", "bottom", "lower", "l"]:
            text_yloc = ylim[0] + 0.1 * (ylim[1] - ylim[0])
        elif text_loc in ["t", "top", "u", "upper"]:
            text_yloc = ylim[1] - 0.1 * (ylim[1] - ylim[0])
        else:
            text_yloc = (ylim[1] + ylim[0]) / 2
            
        for i, (start, end, tag, group) in enumerate(ann_copy):
            # We make sure that we only plot annotation that are within the x range of the current view
            if xlim is not None:
                if start >= xlim[1] or end <= xlim[0]:
                    continue
                
                # Clip boundaries to xlim
                start = max(start, xlim[0])
                end = min(end, xlim[1])
                
                if group is not None:
                    box_color = colors[group]
                else:
                    box_color = "lightgray"
                    
                width = end - start
                rect = Rectangle((start, ylim[0]), width, ylim[1] - ylim[0], facecolor=box_color, edgecolor="black", alpha=alpha)
                ax.add_patch(rect)
                
                text_obj = ax.text((start + end) / 2, text_yloc, tag, ha="center", va="center", fontsize=12, color="black", zorder=10, clip_on=True)
                
                text_obj.set_clip_path(rect)
            else:
                if group is not None:
                    box_color = colors[group]
                else:
                    box_color = "lightgray"
                    
                width = end - start
                rect = Rectangle((start, ylim[0]), width, ylim[1] - ylim[0], facecolor=box_color, edgecolor="black", alpha=alpha)
                ax.add_patch(rect)
                
                text_obj = ax.text((start + end) / 2, text_yloc, tag, ha="center", va="center", fontsize=12, color="black", zorder=10, clip_on=True)
                
                text_obj.set_clip_path(rect)

            
    @staticmethod
    def vlines(
        ax,
        xs,
        y0=None,
        y1=None,
        c=None,
        ls="-",
        lw=None,
        label=None,
    ):
        """
        Paint events (vertical lines at discrete points) to the current tile.
    
        Parameters
        ----------
        xs: np.ndarray
            All the event marker values.
        c: str
            Color of the event marker.
            Default: "k"
        ls: str
            Line style.
            Default: "-"
        lw: float
            Linewidth.
            Default: 1.5
        label: str
            Label for the event type.
            This will appear in the legend.
            Default: None
        grid: bool
            Do you want the grid?
            Default: True
        same_tile: bool
            True if you want to paint it in the same tile (meaning the last tile).
            False
    
        Returns
        -------
        None
        """
            
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        if y0 is None: y0 = ylim[0]
        if y1 is None: y1 = ylim[1]
        
        for i, x in enumerate(xs):
            if xlim is not None:
                if xlim[0] <= x <= xlim[1]:
                    if i == 0:  # Label should be set only once for all the events
                        ax.vlines(x, y0, y1, color=c, linestyle=ls, linewidth=lw, label=label)
                    else:
                        ax.vlines(x, y0, y1, color=c, linestyle=ls, linewidth=lw)
            else:
                if i == 0:  # Label should be set only once for all the events
                    ax.vlines(x, y0, y1, color=c, linestyle=ls, linewidth=lw, label=label)
                else:
                    ax.vlines(x, y0, y1, color=c, linestyle=ls, linewidth=lw)
    
        ax.set_ylim(ylim)
        ax.set_xlim(xlim)
    
    @staticmethod
    def callouts(
        ax,
        xys,
        labels,
        text_offset=(0, 0),
        c="r",
        fontsize=12,
    ):
        """
        Paint multiple callouts pointing to specific points 
        with boxed labels at the tails in the last tile.

        Parameters
        ----------
        ax:
        xys : list[tuple[float, float]] | tuple[float, float]
            List of target points (x, y) for the arrow heads.
        labels : list[str] | str
            List of text labels at the arrow tails.
            If str, the same label is used for all points.
        text_offset : tuple[float, float] | list[tuple[float, float]]
            Offset(s) (dx, dy) for label positions from arrow tails.
            If single tuple, same offset is applied to all.
        c : str | list[str]
            Color(s) for arrow and text.
            If str, same color is applied to all.
        fontsize : int | list[int]
            Font size(s) of the label text.
            If int, same size is applied to all.
        grid: bool
            Do you want the grid?
            Default: True
        same_tile: bool
            True if you want to paint it in the same tile (meaning the last tile).
            Default: True

        Returns
        -------
        None
        """
        
        # Normalize single values into lists
        if isinstance(xys, tuple):
            xys = [xys]
        n = len(xys)
        if isinstance(labels, str):
            labels = [labels] * n
        if isinstance(text_offset, tuple):
            text_offset = [text_offset] * n
        if isinstance(c, str):
            c = [c] * n
        if isinstance(fontsize, int):
            fontsize = [fontsize] * n
            
        for xy, label, offset, color, fs in zip(xys, labels, text_offset, c, fontsize):
            arrowprops = dict(arrowstyle="->", color=color, lw=2)
            bbox = dict(boxstyle="round,pad=0.3", fc="white", ec=color, lw=1.2)
            
            text_x, text_y = xy[0] + offset[0], xy[1] + offset[1]
            
            ax.annotate(label, xy=xy, xycoords="data", xytext=(text_x, text_y), textcoords="data", arrowprops=arrowprops, fontsize=fs, color=color, ha="center", va="center", bbox=bbox)
            

    def arrow(
        ax,
        start,
        end,
        c="black",
        head_size=0.05,
        head_label=None,
        tail_label=None,
        arrow_label=None,
        offset=0.05,
    ):
        """
        Paint a clean, labeled arrow from start to end with auto label positioning.

        Parameters
        ----------
        start: tuple[float, float]
            Coordinates of the starting point `(x_start, y_start)`.
        end: tuple[float, float]
            Coordinates of the ending point `(x_end, y_end)`.
        c: str, optional
            Color of the arrow and point markers (default is `"black"`).
        head_size: float, optional
            Relative size of the arrowhead. Larger values make the arrowhead
            more prominent. Default is `0.05`.
        start_label: str or None, optional
            Optional text label to display near the start point.
        end_label: str or None, optional
            Optional text label to display near the end point.
        arrow_label: str or None, optional
            Optional text label to display near the midpoint of the arrow.
        label_offset: float, optional
            Offset distance (in data units) for label placement perpendicular
            to the arrow direction. Default is `0.05`.
        grid: bool
            Do you want the grid?
            Default: True
        same_tile: bool, optional
            Whether to paint on the same tile as the previous plot element.
            If `False`, the next available tile is used. Default is `True`.

        Returns
        -------
        None
        """
        
        x_start, y_start = start
        x_end, y_end = end
        
        # Compute direction vector (for auto label offset)
        dx = x_end - x_start
        dy = y_end - y_start
        mag = np.hypot(dx, dy)
        if mag == 0:
            return  # skip zero-length arrow
        
        # Normalized direction and perpendicular vectors
        ux, uy = dx / mag, dy / mag
        px, py = -uy, ux  # perpendicular vector (for label offsets)
        # Offset magnitude in data units
        ox, oy = px * offset, py * offset
        
        # Draw arrow
        ax.annotate(
            "",
            xy=(x_end, y_end),
            xytext=(x_start, y_start),
            arrowprops=dict(
                arrowstyle=f"->,head_length={head_size*20},head_width={head_size*10}",
                color=c,
                lw=1.5,
            ),
        )
        
        # Draw points
        ax.scatter(*start, color=c, s=10, zorder=3)
        
        # Label start and end points
        text_offset = 8 # offset in display coordinates (pixels)
        
        if tail_label:
            ax.annotate(tail_label, xy=start, xycoords="data", xytext=(-ux * text_offset, -uy * text_offset), textcoords="offset points", ha="center", va="center", color=c, fontsize=10, arrowprops=None)
            
        if head_label:
            ax.annotate(head_label, xy=end, xycoords="data", xytext=(ux * text_offset, uy * text_offset), textcoords="offset points", ha="center", va="center", color=c, fontsize=10, arrowprops=None)
            
            
            # Label arrow at midpoint (also offset)
        if arrow_label:
            xm, ym = (x_start + x_end) / 2, (y_start + y_end) / 2
            ax.text(xm + ox, ym + oy, arrow_label, color=c, fontsize=10, ha="center")

            
    def polygon(
        ax,
        points,
        c=None,
        ec="black",
        alpha=0.5,
        lw=1.0,
        fill=True,
    ):
        """
        Paint the area enclosed by a set of 2D points (polygon) on the current tile.
    
        Parameters
        ----------
        points : np.ndarray of shape (n_points, 2)
            Array of 2D points representing vertices of the polygon in order.
        c : str
            Fill color for the polygon.
            Default: "lightblue"
        ec : str
            Color of the polygon edges.
            Default: "black"
        alpha : float
            Transparency level of the fill (0 fully transparent, 1 fully opaque).
            Default: 0.5
        lw : float
            Width of polygon edges.
            Default: 1.0
        fill : bool
            Whether to fill the polygon.
            Default: True
        grid: bool
            Do you want the grid?
            Default: True
        same_tile : bool
            True if you want to paint on the last tile.
            Default: False
    
        Returns
        -------
        None
        """
            
        points = np.asarray(points)
        
        # Close the polygon if not already closed
        if not np.all(points[0] == points[-1]):
            points = np.vstack([points, points[0]])
            
        if fill:
            ax.fill(points[:, 0], points[:, 1], color=c, alpha=alpha, edgecolor=ec, linewidth=lw)
        else:
            ax.plot(points[:, 0], points[:, 1], color=ec, linewidth=lw)