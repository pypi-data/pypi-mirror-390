#!/usr/bin/env python3

#---------------------------------
# Author: Ankit Anand
# Date: 09/11/25
# Email: ankit0.anand0@gmail.com
#---------------------------------

import numpy as np
import matplotlib.pyplot as plt

class StyleSetter:
    
    def __init__(self):
        pass
        
    @staticmethod
    def ticks(
        axs,
        yticks=None,
        yticklabels=None,
        xticks=None,
        xticklabels=None,
    ):
        """
        
        """

        axs_flattened = np.ravel(np.atleast_1d(axs))
        
        for ax in axs_flattened:
            if yticks is not None:
                ax.set_yticks(yticks)
                if yticklabels is not None:
                    ax.set_yticklabels(yticklabels)
                    
            if xticks is not None:
                ax.set_xticks(xticks)
                if xticklabels is not None:
                    ax.set_xticklabels(xticklabels)
    
    @staticmethod
    def limits(
        axs,
        ylim=None,
        xlim=None,
    ):
        """
        
        """

        axs_flattened = np.ravel(np.atleast_1d(axs))
        
        for ax in axs_flattened:
            if ylim is not None:
                ax.set_ylim(ylim)
            
            if xlim is not None:
                ax.set_xlim(xlim)
    
    @staticmethod
    def labels(
        axs,
        ylabels=None,
        xlabels=None,
    ):

        axs_flattened = np.ravel(np.atleast_1d(axs))
        n = axs_flattened.size
    
        # Normalize inputs
        if isinstance(ylabels, str):
            ylabels = [ylabels] * n
        elif ylabels is None:
            ylabels = [None] * n
    
        if isinstance(xlabels, str):
            xlabels = [xlabels] * n
        elif xlabels is None:
            xlabels = [None] * n
        
        for ax, ylabel, xlabel in zip(axs_flattened, ylabels, xlabels):
            if ylabel is not None:
                ax.set_ylabel(ylabel + "→")
            
            if xlabel is not None:
                ax.set_xlabel(xlabel + "→")
    
    @staticmethod
    def titles(
        axs,
        titles=None,
        s=10,
    ):

        axs_flattened = np.ravel(np.atleast_1d(axs))
        n = axs_flattened.size
    
        # Normalize inputs
        if isinstance(titles, str):
            titles = [titles] * n
        elif titles is None:
            titles = [None] * n

        
        for ax, title in zip(axs_flattened, titles):
            if title is not None:
                ax.set_title(title, size=s, loc="right")
        
    @staticmethod
    def figtitle(
        fig,
        title="",
        s=13,
        y=1.0
    ):

        fig.suptitle(title, size=s, y=y)

    
    def legend(fig, axs, ypos=1.1, inside=True):
        """
        Add legend(s) to the figure.

        Parameters
        ----------
        ypos : float, optional
            Vertical position of the figure-level legend (only if grouped=True).
            > 1 pushes it higher, < 1 pushes it lower. Default is 1.0.
        inside_tile : bool, optional
            If True, add legends to each tile separately.
            If False, combine all legend entries into one canvas-level legend.

        Returns
        -------
        None
        """

        axs = np.ravel(axs)  # works for 1D or 2D grids
        
        if not inside:
            # --- Combine all handles and labels ---
            all_handles, all_labels = [], []
            for ax in axs:
                handles, labels = ax.get_legend_handles_labels()
                all_handles.extend(handles)
                all_labels.extend(labels)
                
                # --- Remove duplicates while preserving order ---
            unique = dict(zip(all_labels, all_handles))
            fig.legend(
                unique.values(),
                unique.keys(),
                loc="upper right",
                bbox_to_anchor=(1, ypos),
                ncol=min(len(axs), 4),  # up to 4 columns or as many as tiles
                frameon=True,
                bbox_transform=fig.transFigure,
            )
            
        else:
            # --- Individual legends per subplot ---
            for ax in axs:
                handles, labels = ax.get_legend_handles_labels()
                if handles:
                    ax.legend(handles, labels, loc="upper right", frameon=True)