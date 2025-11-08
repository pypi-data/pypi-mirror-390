#!/usr/bin/env python3

#---------------------------------
# Author: Ankit Anand
# Date: 06/11/25
# Email: ankit0.anand0@gmail.com
#---------------------------------

import numpy as np
import string
from IPython import get_ipython

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.lines as mlines

from functools import cached_property

from ._utils import load_devanagari_font
from ._painter import Painter

class CanvasGenerator:
	"""
	Provides user-friendly APIs to generate
	different canvas to paint data on it.
	"""
	
	def __init__(self):
		
		load_devanagari_font()
		
		self.fig = None
		self.axs = None
		self.type = None
		self._xlim = None # This is specifically to be passed to painter for painting annotation not beyond the limit
		self.ntiles = 0 # Number of tiles in the canvas
		
	@cached_property
	def paint(self):
		return Painter(_canvas=self)
	
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
	
	@classmethod
	def tiers(cls, config, xlim=None, fig_width=16, abc=True, fig_num="", annotate=False):
		"""
		Generate tiers like canvas based on the configuration.

		Parameters
		----------
		config: str
			A string combination of "a" for auxilary, "s" for signal, "m" for matrix
			Eg. "ams", "aa", "a", "sam" etc.
		xlim: tuple | None
			(start, end) of xlim.
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
		annotate: bool
			Make the plot interactive. (Experimental)
			Using matplotwidget, you can annotate.

		Returns
		-------
		Self
			A new Canvas object
		"""
		
		if annotate is True:
			ip = get_ipython()
			ip.run_line_magic("matplotlib", "widget")  # Switch backend first
			plt.close("all")
			fig_width = 14
			abc = False
		else:
			ip = get_ipython()
			ip.run_line_magic("matplotlib", "inline")
			plt.close("all")
		
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
			abc_labels = cls._generate_abc(n_tiers)
			for i in range(n_tiers):
				axs[i, 0].text(-0.08, 0.5, f"({fig_num}{abc_labels[i]})", transform=axs[i, 0].transAxes, fontsize=10, va="center", ha="right")
				
				# Turn on the x-label for the last tier
		axs[-1, 0].tick_params(bottom=True, labelbottom=True)
		
		# xlim should be applied on reference subplot, rest all subplots will automatically adjust
		if xlim is not None:
			axs[0, 0].set_xlim(xlim)
			
		fig.subplots_adjust(hspace=0.2, wspace=0.05)
		
		# Returning the class object
		canvas_obj = cls()
		canvas_obj.type = "tiers"
		canvas_obj.fig = fig
		canvas_obj.axs = axs
		canvas_obj._xlim = xlim
		canvas_obj.ntiles = len(config)
		
		if annotate is True:
			from modusa._annotator._annotator import annotate
			canvas_obj.annotation = annotate(canvas_obj)
		
		return canvas_obj
	
	@classmethod
	def grids(cls, config, tile_size=2, remove_ticks=True, ylim=None, xlim=None, abc=True,):
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
				
		# Apply limits
		for ax in axs_flat:
			if xlim is not None:
				ax.set_xlim(xlim)
			if ylim is not None:
				ax.set_ylim(ylim)
				
		# Add (a), (b), (c), ... as titles
		if abc is True:
			abc_labels = cls._generate_abc(axs_flat.size)
			for i, ax in enumerate(axs_flat):
				ax.set_title(f"({abc_labels[i]})", fontsize=10, loc="center")
				
		# Make sure layout leaves space for titles
		plt.tight_layout()
		
		# Returning the class object
		canvas_obj = cls()
		canvas_obj.type = "grids"
		canvas_obj.fig = fig
		canvas_obj.axs = axs
		canvas_obj._xlim = xlim
		canvas_obj.ntiles = axs_flat.size
		
		return canvas_obj
	
	@classmethod
	def stacks(cls, config, tile_size=1, overlap=0.3, remove_ticks=True, focus=None, focus_offset=2.0):
		"""
		Generate 3D stacks like canvas based on the configuration.

		Parameters
		----------
		config: int
			Number of tiles
		tile_size: number
			Size of each tile
		overlap: float
			Fraction of overlap between consecutive tiles.
		remove_ticks: bool
			If True, hides all axis ticks and labels for a cleaner stacked appearance.
		focus: int | None
			Index of the tile to highlight.
			The focused tile is offset outward (to the right) by `offset` units.
		focus_offset: float, optional, default=2.0
			Horizontal displacement for the focused tile.
			Determines how far the focused tile "pops out" from the stack.

		Returns
		-------
		Self
			A new Canvas object
		"""
		
		fig = plt.figure(figsize=(tile_size * 2, tile_size * 2))
		axs = []
		
		width, height = 0.8, 0.8
		
		# Base positions (first tile on top, stack grows top-right)
		base_positions = [(0.1 + i * overlap * 0.1, 0.1 + i * overlap * 0.1) for i in range(config)]
		
		# Create all tiles first
		for i in range(config):
			left, bottom = base_positions[i]
			ax = fig.add_axes([left, bottom, width, height], facecolor="white", zorder=(config - i))
			ax.patch.set_edgecolor("black")
			ax.patch.set_linewidth(1.5)
			ax.set_aspect("equal", adjustable="box")
			axs.append(ax)
			
			
		# Removing ticks from all the tiles expect the focussed tile if requested
		for i in range(len(axs)):
			if remove_ticks is False and focus is not None: # Means keep the ticks only for focussed tile
				if i == focus:
					continue
			axs[i].set_xticks([])
			axs[i].set_yticks([])
			
		# Handle focus highlighting, ghost, and connector
		if focus is not None and 0 <= focus < config:
			left, bottom = base_positions[focus]
			new_left = left + focus_offset
			new_bottom = bottom
			
			# Ghost rectangle (beneath upper layers)
			ghost_rect = Rectangle((left, bottom), width, height, transform=fig.transFigure, facecolor="gray", edgecolor="red", linewidth=1.0, linestyle="-", zorder=(config - focus) - 0.5)
			fig.patches.append(ghost_rect)
			
			# Connector from right edge to new popped tile
			x0 = left + width
			y0 = bottom + height * 0.5
			x1 = new_left
			y1 = new_bottom + height * 0.5
			
			connector = mlines.Line2D([x0, x1], [y0, y1], transform=fig.transFigure, linestyle="--", linewidth=1.0, color="red", zorder=(config - focus) - 0.5)
			fig.lines.append(connector)
			
			# Move focused tile to new position and highlight
			axs[focus].set_position([new_left, new_bottom, width, height])
			axs[focus].patch.set_edgecolor("red")
			axs[focus].patch.set_linewidth(2.5)
			axs[focus].set_zorder(config + 1)
			
		# Returning the class object
		canvas_obj = cls()
		canvas_obj.type = "stacks"
		canvas_obj.fig = fig
		canvas_obj.axs = axs
		canvas_obj.ntiles = len(axs)
		
		return canvas_obj
	
	@classmethod
	def cartesian2D(cls, tile_size=5, ylim=None, xlim=None, grid=True):
		"""
		Generate 2D-cartesian like canvas.
		
		Parameters
		----------
		tile_size: int
			Size of the cartesian tile
		remove_ticks: bool
			Remove the x-ticks and y-ticks from all the tiles.
		xlim: tuple
			(start, end) of xlim.
		ylim: tuple
			(start, end) of xlim.
		grid: bool
			Do you want the grid?

		Returns
		-------
		Self
			A new Canvas object

		"""
		
		# Create figure and axes
		fig, axs = plt.subplots(1, 1, figsize=(tile_size, tile_size))
		
		axs.grid(grid)
		axs.set_ylim(ylim)
		axs.set_xlim(xlim)
		
		# Returning the class object
		canvas_obj = cls()
		canvas_obj.type = "cartesian2D"
		canvas_obj.fig = fig
		canvas_obj.axs = axs
		canvas_obj._xlim = xlim
		canvas_obj.ntiles = 1
		
		return canvas_obj
	
	def save(self, fp, pad=0.5):
		"""
		Save the canvas.

		Parameters
		----------
		fp: str | PathLike
			File path to save the canvas.
		pad: float
			Add padding to the canvas.
		"""
		
		self.fig.savefig(fp, bbox_inches='tight', pad_inches=pad)
		
		
		
	def legend(self, ypos=1.0, inside_tile=False):
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
		fig = self.fig
		axs = np.ravel(self.axs)  # works for 1D or 2D grids
		
		if not inside_tile:
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
					
	def title(self, title=None, s=12, offset=0.05):
		"""
		Set the title of the canvas.

		Parameters
		----------
		title: str | None
			Title of the figure.
			Default: None
		s: Number
			Font size.
			Default: None
		offset: float
			Shift the title.
		"""
		if title is not None:
			self.fig.suptitle(title, fontsize=s, y=offset+1.0)
			