#!/usr/bin/env python3

#---------------------------------
# Author: Ankit Anand
# Date: 09/11/25
# Email: ankit0.anand0@gmail.com
#---------------------------------

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.lines as mlines
import numpy as np
import string

class LayoutGenerator:
        
    def _generate_abc(n):
        """
        Generate lowercase labels: a, b, ..., z, aa, ab, ac, ...
        for tiles/axs.
        """
        labels = []
        letters = string.ascii_lowercase
        while len(labels) < n:
            i = len(labels)
            label = ""
            while True:
                label = letters[i % 26] + label
                i = i // 26 - 1
                if i < 0:
                    break
            labels.append(label)
        return labels
    
    @staticmethod
    def tracks(config, fig_width=16, pad=0.5, abc=True, fig_num=""):
        """
        Generate praat-style like canvas based on the configuration.
        
        Parameters
        ----------
        config: str
            A string combination of "a" for auxilary, "s" for signal, "m" for matrix
            Eg. "ams", "aa", "a", "sam" etc.
            Default: None
        fig_width: int
            Figure width
            Default: 16
        abc: bool
            Assign each tier a character for referencing
            Default: True
        fig_num: str | int | float
            Prefix to the "abc"
            Default: ""
    
        Returns
        -------
        Self
            A new Canvas object
        """
        
        fig, axs = None, None
            
        n_aux_tier = config.count("a")
        n_signal_tier = config.count("s")
        n_matrix_tier = config.count("m")
        n_tiers = n_aux_tier + n_signal_tier + n_matrix_tier  # Number of tiers
        
        # Decide heights of different subplots type
        height = {}
        height["a"] = 0.4  # Aux height
        height["s"] = 2.0  # Signal height
        height["m"] = 4.0  # Matrix height
        cbar_width = 0.01  # For second column (for matrix plots)
        
        # Calculate height ratios for each tier
        for char in config:
            height_ratios = [height[char] for char in config]
            
            # Calculate total fig height
        fig_height = ((n_aux_tier * height["a"]) + (n_signal_tier * height["s"]) + (n_matrix_tier * height["m"]))
        
        # Create figure and axs based on the config
        fig, axs = plt.subplots(n_tiers, 2, figsize=(fig_width, fig_height), height_ratios=height_ratios, width_ratios=[1, cbar_width])
        
        axs = np.atleast_2d(axs)  # This is done otherwise axs[i, 0] does not work
        
        for i, char in enumerate(config):  # Loop through each tier and adjust the layout
            if char == "a":  # Remove ticks and labels from all the aux subplots
                axs[i, 0].tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
            elif char == "s":
                axs[i, 0].tick_params(bottom=False, labelbottom=False)
            elif char == "m":
                axs[i, 0].tick_params(bottom=False, labelbottom=False)
            
            axs[i, 1].axis("off")  # Turn off the column 2, only turn it on when matrix is plotted with colorbar
            
            axs[i, 0].sharex(axs[0, 0])  # Share the x-axis to make all the tiers aligned
        
        # Add tags (1a, 4.1c, ...) to each tier for better referencing in research papers.
        if abc is True:
            abc_labels = LayoutGenerator._generate_abc(n_tiers)
            for i in range(n_tiers):
                axs[i, 0].set_title(f"({fig_num}{abc_labels[i]})", fontsize=10, loc="left")
                
        # Turn on the x-label for the last tier
        axs[-1, 0].tick_params(bottom=True, labelbottom=True)
        
        # Make sure layout leaves space for titles
        plt.tight_layout(h_pad=0.4, w_pad=0.05)
        
        return fig, axs
    
    
    @staticmethod
    def collage(config, tile_size=4, pad=3, remove_ticks=False, abc=True, fig_num=""):
        """
        Generate 2D grid-like canvas based on the configuration.

        Parameters
        ----------
        config: tuple[int, int]
            (n_rows, n_cols)
            Eg. (2, 3)
        tile_size: int
            Size of each cell in the grid
            Default: 2
        remove_ticks: bool
            Remove the x-ticks and y-ticks from all the tiles.
            Default: True
        ylim: tuple
            (start, end) of xlim.
            Default: None
        xlim: tuple
            (start, end) of xlim.
            Default: None
        abc: bool
            If True, label each subplot as a, b, c, ...

        Returns
        -------
        Self
            A new Canvas object
        """
        
        n_rows, n_cols = config
        
        fig, axs = plt.subplots(n_rows, n_cols, figsize=(tile_size * n_cols, tile_size * n_rows))
        
        # Flatten axes safely
        axs_flat = np.ravel(np.atleast_1d(axs))
        
        # Remove ticks
        if remove_ticks:
            for ax in axs_flat:
                ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
            
                
        # Add (a), (b), (c), ... as titles
        if abc is True:
            abc_labels = LayoutGenerator._generate_abc(axs_flat.size)
            for i, ax in enumerate(axs_flat):
                axs_flat[i].set_title(f"({fig_num}{abc_labels[i]})", fontsize=10, loc="left")
                
                
        # Make sure layout leaves space for titles
        plt.tight_layout(pad=pad)
        
        return fig, axs
    
    @classmethod
    def deck(cls, config, tile_size=1, overlap=0.3, focus=None, focus_offset=2.0):
        """
        Generate 3D stacks like canvas based on the configuration.
        """
        fig = plt.figure(figsize=(tile_size * 2, tile_size * 2))
        axs = []

        width, height = 0.8, 0.8
        base_positions = [(0.1 + i * overlap * 0.1, 0.1 + i * overlap * 0.1) for i in range(config)]

        for i in range(config):
            left, bottom = base_positions[i]
            ax = fig.add_axes([left, bottom, width, height], facecolor="white", zorder=(config - i))
            ax.patch.set_edgecolor("black")
            ax.patch.set_linewidth(1.5)

            # FIX 1: lock aspect ratio and prevent auto-scaling
            ax.set_aspect("equal", adjustable="box")
            ax.set_autoscale_on(False)
            ax.autoscale(False)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)

            axs.append(ax)

        # FIX 2: Hide ticks consistently
        for i, ax in enumerate(axs):
            if not (focus is not None and i == focus):
                ax.set_xticks([])
                ax.set_yticks([])

        # Handle focus highlight
        if focus is not None and 0 <= focus < config:
            left, bottom = base_positions[focus]
            new_left = left + focus_offset
            new_bottom = bottom

            ghost_rect = Rectangle(
                (left, bottom),
                width, height,
                transform=fig.transFigure,
                facecolor="gray",
                edgecolor="red",
                linewidth=1.0,
                linestyle="-",
                zorder=(config - focus) - 0.5,
            )
            fig.patches.append(ghost_rect)

            x0 = left + width
            y0 = bottom + height * 0.5
            x1 = new_left
            y1 = new_bottom + height * 0.5

            connector = mlines.Line2D(
                [x0, x1],
                [y0, y1],
                transform=fig.transFigure,
                linestyle="--",
                linewidth=1.0,
                color="red",
                zorder=(config - focus) - 0.5,
            )
            fig.lines.append(connector)

            axs[focus].set_position([new_left, new_bottom, width, height])
            axs[focus].patch.set_edgecolor("red")
            axs[focus].patch.set_linewidth(2.5)
            axs[focus].set_zorder(config + 1)

        return fig, np.array(axs)