#!/usr/bin/env python3

#---------------------------------
# Author: Ankit Anand
# Date: 06/11/25
# Email: ankit0.anand0@gmail.com
#---------------------------------

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import fnmatch

class Painter:
	"""
	A Painter class that paints the data
	on a given canvas.
	"""
	
	def __init__(self, _canvas):
		
		self._canvas = _canvas
		self._fig = _canvas.fig
		self._axs = _canvas.axs
		self._xlim = _canvas._xlim  # This will be used while plotting annotations as we need to know how much to plot
		self._canvas_type = _canvas.type
		self._curr_tile_idx = 0
		self._curr_color_idx = 0  # Choosing color for each stroke of painting
		
	def _get_curr_tile(self):
		"""
		Returns the current tile on which
		painting should be done.
		"""
		try:
			if self._canvas.type == "tiers":
				curr_tile = self._axs[self._curr_tile_idx, 0]
				self._curr_tile_idx += 1
			elif self._canvas.type == "grids":
				curr_tile = self._axs.ravel()[self._curr_tile_idx]
				self._curr_tile_idx += 1
			elif self._canvas.type == "stacks":
				curr_tile = self._axs[self._curr_tile_idx]
				self._curr_tile_idx += 1
			elif self._canvas.type == "cartesian2D":
				curr_tile = self._axs
			else:
				raise ValueError(f"Invalid canvas type {self._canvas.type}")
		except IndexError as e:
			raise IndexError("There are not enough tiles to paint your data.")
		return curr_tile
	
	def _get_cbar_tile(self):
		"""
		Returns the tile on which color
		bar should be painted.
		"""
		cbar_tile = self._axs[self._curr_tile_idx - 1, 1]
		
		return cbar_tile
	
	def _get_new_color(self):
		"""
		Returns new color for each
		stroke of painting.
		"""
		
		colors = plt.cm.tab20.colors
		self._curr_color_idx += 1
		
		return colors[self._curr_color_idx % len(colors)]
	
	def _tier_xlabel(self, xlabel):
		"""
		Set shared x-label to the tiles.

		Parameters
		----------
		xlabel: str | None
			- xlabel for the figure.
		"""
		axs = self._axs
		last_ax = axs[-1, 0]  # X-label is added to the last subplot
		if xlabel is not None:
			last_ax.set_xlabel(xlabel)
			
	def signal(
		self,
		y,
		x=None,
		c=None,
		ls=None,
		lw=None,
		m=None,
		ms=3,
		label=None,
		ylabel=None,
		ylim=None,
		yticks=None,
		yticklabels=None,
		xlabel=None,
		xticks=None,
		xticklabels=None,
		grid=True,
		same_tile=False
	):
		"""
		Paint 1D array/signal to the current tile.

		Parameters
		----------
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
		label: str
			Label for the plot.
			Legend will use this.
			Default: None
		ylabel: str
			y-label for the plot.
			Default: None
		ylim: tuple
			y-lim for the plot.
			Default: None
		yticks: Arraylike
			Positions at which to place y-axis ticks.
		yticklabels : list of str, optional
			Labels corresponding to `yticks`. Must be the same length as `yticks`.
		xlabel: str
			x-label for the plot.
			Default: None
		xticks: Arraylike
			Positions at which to place x-axis ticks.
		xticklabels : list of str, optional
			Labels corresponding to `xticks`. Must be the same length as `xticks`.
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
		if same_tile is False:
			tile = self._get_curr_tile()
		else:
			self._curr_tile_idx -= 1  # Go to the last tile that was painted
			tile = self._get_curr_tile()  # Grab it to paint on it again
			
		if x is None:
			x = np.arange(y.size)
		if c is None:
			c = self._get_new_color()
			
		tile.plot(
			x,
			y,
			color=c,
			linestyle=ls,
			linewidth=lw,
			marker=m,
			markersize=ms,
			label=label,
		)
		
		if ylabel is not None:
			tile.set_ylabel(ylabel)
			
		if xlabel is not None:
			if self._canvas_type == "grids":
				tile.set_xlabel(xlabel)
			elif self._canvas_type == "tiers":
				self._tier_xlabel(xlabel)
				
		if ylim is not None:
			tile.set_ylim(ylim)
			
		if yticks is not None:
			tile.set_yticks(yticks)
			if yticklabels is not None:
				tile.set_yticklabels(yticklabels)
				
		if xticks is not None:
			tile.set_xticks(xticks)
			if xticklabels is not None:
				tile.set_xticklabels(xticklabels)
				
		if grid is True:
			tile.grid(True, linestyle="--", linewidth=0.7, color="lightgray", alpha=0.6)
			
			
	def image(
		self,
		M,
		y=None,
		x=None,
		c="viridis",
		o="upper",
		label=None,
		ylabel=None,
		ylim=None,
		yticks=None,
		yticklabels=None,
		xlabel=None,
		xticks=None,
		xticklabels=None,
		cbar=True,
		grid=True,
		alpha=1,
		same_tile=False,
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
		cbar: bool
			- Show colorbar
			- Default: True
		grid: bool
			- Do you want the grid?
			- Default: True
		alpha: float (0 to 1)
			- Transparency level
			- 1 being opaque and 0 being completely transparent
			- Default: 1
		same_tile: bool
			- True if you want to paint it in the same tile (meaning the last tile).
			- False

		Returns
		-------
		None
		"""
		
		if same_tile is False:
			tile = self._get_curr_tile()
		else:
			self._curr_tile_idx -= 1  # Go to the last tile that was painted
			tile = self._get_curr_tile()  # Grab it to paint on it again
			
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
		
		im = tile.imshow(M, aspect="auto", origin=o, cmap=c, extent=extent, alpha=alpha)
		
		if ylabel is not None:
			tile.set_ylabel(ylabel)
			
		if xlabel is not None:
			if self._canvas.type == "grids":
				tile.set_xlabel(xlabel)
			elif self._canvas.type == "tiers":
				self._tier_xlabel(xlabel)
				
		if ylim is not None:
			if o == "lower":
				tile.set_ylim(ylim)
			elif o == "upper":
				tile.set_ylim(ylim[::-1])
				
		# Colorbar
		if cbar is True:
			if self._canvas.type == "tiers":
				cbar_tile = self._get_cbar_tile()
				cbar_tile.axis("on")
				cbar = plt.colorbar(im, cax=cbar_tile)
			elif self._canvas.type == "grids":
				cbar = plt.colorbar(im)
			if label is not None:
				cbar.set_label(label, labelpad=5)
				
		if yticks is not None:
			tile.set_yticks(yticks)
			if yticklabels is not None:
				tile.set_yticklabels(yticklabels)
				
		if xticks is not None:
			tile.set_xticks(xticks)
			if xticklabels is not None:
				tile.set_xticklabels(xticklabels)
				
		if grid is True:
			tile.grid(True, linestyle="--", linewidth=0.7, color="lightgray", alpha=0.6)
			
	def annotation(
		self,
		ann,
		patterns=None,
		ylim=(0, 1),
		text_loc="m",
		grid=True,
		same_tile=False
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
		grid: bool
			- Do you want the grid?
			- Default: True
		same_tile: bool
			- True if you want to paint it in the same tile (meaning the last tile).
			- False
		Returns
		-------
		None
		"""
		if same_tile is False:
			tile = self._get_curr_tile()
		else:
			self._curr_tile_idx -= 1  # Go to the last tile that was painted
			tile = self._get_curr_tile()  # Grab it to paint on it again
			
		xlim = self._xlim
		
		if isinstance(patterns, str):
			patterns = [patterns]
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
				rect = Rectangle((start, ylim[0]), width, ylim[1] - ylim[0], facecolor=box_color, edgecolor="black", alpha=0.7)
				tile.add_patch(rect)
				
				text_obj = tile.text((start + end) / 2, text_yloc, tag, ha="center", va="center", fontsize=9, color="black", zorder=10, clip_on=True)
				
				text_obj.set_clip_path(rect)
			else:
				if group is not None:
					box_color = colors[group]
				else:
					box_color = "lightgray"
					
				width = end - start
				rect = Rectangle((start, ylim[0]), width, ylim[1] - ylim[0], facecolor=box_color, edgecolor="black", alpha=0.7)
				tile.add_patch(rect)
				
				text_obj = tile.text((start + end) / 2, text_yloc, tag, ha="center", va="center", fontsize=10, color="black", zorder=10, clip_on=True)
				
				text_obj.set_clip_path(rect)
				
		if grid is True:
			tile.grid(True, linestyle="--", linewidth=0.7, color="lightgray", alpha=0.6)
			
	def events(self, events, c=None, ls=None, lw=None, label=None, grid=True, same_tile=False):
		"""
		Paint events (vertical lines at discrete points) to the current tile.

		Parameters
		----------
		events: np.ndarray
			- All the event marker values.
		c: str
			- Color of the event marker.
			- Default: "k"
		ls: str
			- Line style.
			- Default: "-"
		lw: float
			- Linewidth.
			- Default: 1.5
		label: str
			- Label for the event type.
			- This will appear in the legend.
			- Default: None
		grid: bool
			- Do you want the grid?
			- Default: True
		same_tile: bool
			- True if you want to paint it in the same tile (meaning the last tile).
			- False

		Returns
		-------
		None
		"""
		
		if same_tile is False:
			tile = self._get_curr_tile()
		else:
			self._curr_tile_idx -= 1  # Go to the last tile that was painted
			tile = self._get_curr_tile()  # Grab it to paint on it again
			
		if c is None:
			c = self._get_new_color()
			
		xlim = self._xlim
		
		for i, event in enumerate(events):
			if xlim is not None:
				if xlim[0] <= event <= xlim[1]:
					if i == 0:  # Label should be set only once for all the events
						tile.axvline(x=event, color=c, linestyle=ls, linewidth=lw, label=label)
					else:
						tile.axvline(x=event, color=c, linestyle=ls, linewidth=lw)
			else:
				if i == 0:  # Label should be set only once for all the events
					tile.axvline(x=event, color=c, linestyle=ls, linewidth=lw, label=label)
				else:
					tile.axvline(x=event, color=c, linestyle=ls, linewidth=lw)
					
		if grid is True:
			tile.grid(True, linestyle="--", linewidth=0.7, color="lightgray", alpha=0.6)
			
	def callouts(
		self,
		xys,
		labels,
		text_offset=(0, 0),
		c="r",
		fontsize=12,
		same_tile=True
	):
		"""
		Paint multiple callouts pointing to specific points 
		with boxed labels at the tails in the last tile.

		Parameters
		----------
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
		same_tile: bool
			True if you want to paint it in the same tile (meaning the last tile).
			Default: True

		Returns
		-------
		None
		"""
		
		if same_tile is False:
			tile = self._get_curr_tile()
		else:
			self._curr_tile_idx -= 1  # Go to the last tile that was painted
			tile = self._get_curr_tile()  # Grab it to paint on it again
			
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
			
			tile.annotate(label, xy=xy, xycoords="data", xytext=(text_x, text_y), textcoords="data", arrowprops=arrowprops, fontsize=fs, color=color, ha="center", va="center", bbox=bbox)
			
	def arrow(self, start, end, color="black", head_size=0.05, start_label=None, end_label=None, arrow_label=None, label_offset=0.05, same_tile=True):
		"""
		Paint a clean, labeled arrow from start to end with auto label positioning.

		Parameters
		----------
		start: tuple[float, float]
			Coordinates of the starting point `(x_start, y_start)`.
		end: tuple[float, float]
			Coordinates of the ending point `(x_end, y_end)`.
		color: str, optional
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
		same_tile: bool, optional
			Whether to paint on the same tile as the previous plot element.
			If `False`, the next available tile is used. Default is `True`.

		Returns
		-------
		None
		"""
		
		# Get the current tile
		if same_tile is False:
			tile = self._get_curr_tile()
		else:
			self._curr_tile_idx -= 1
			tile = self._get_curr_tile()
			
		x_start, y_start = start
		x_end, y_end = end
		
		# Compute direction vector (for auto label offset)
		dx = x_end - x_start
		dy = y_end - y_start
		mag = np.hypot(dx, dy)
		if mag == 0:
			return tile  # skip zero-length arrow
		
		# Normalized direction and perpendicular vectors
		ux, uy = dx / mag, dy / mag
		px, py = -uy, ux  # perpendicular vector (for label offsets)
		# Offset magnitude in data units
		ox, oy = px * label_offset, py * label_offset
		
		# Draw arrow
		tile.annotate(
			"",
			xy=(x_end, y_end),
			xytext=(x_start, y_start),
			arrowprops=dict(
				arrowstyle=f"->,head_length={head_size*20},head_width={head_size*10}",
				color=color,
				lw=1.5,
			),
		)
		
		# Draw points
		tile.scatter(*start, color=color, s=20, zorder=3)
		tile.scatter(*end, color=color, s=20, zorder=3)
		
		# Label start and end points
		text_offset = 8 # offset in display coordinates (pixels)
		
		if start_label:
			tile.annotate(start_label, xy=start, xycoords="data", xytext=(-ux * text_offset, -uy * text_offset), textcoords="offset points", ha="center", va="center", color=color, fontsize=10, arrowprops=None)
			
		if end_label:
			tile.annotate(end_label, xy=end, xycoords="data", xytext=(ux * text_offset, uy * text_offset), textcoords="offset points", ha="center", va="center", color=color, fontsize=10, arrowprops=None)
			
			
		# Label arrow at midpoint (also offset)
		if arrow_label:
			xm, ym = (x_start + x_end) / 2, (y_start + y_end) / 2
			tile.text(xm + ox, ym + oy, arrow_label, color=color, fontsize=10, ha="center")