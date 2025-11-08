#!/usr/bin/env python3

#---------------------------------
# Author: Ankit Anand
# Date: 07/11/25
# Email: ankit0.anand0@gmail.com
#---------------------------------

#!/usr/bin/env python3
#---------------------------------
# Author: Ankit Anand
# Date: 07/11/25
# Email: ankit0.anand0@gmail.com
#---------------------------------

import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
from ipywidgets import VBox, HBox, Button, Label, FloatText
from IPython.display import display

def annotate(canvas):
    """
    Make a Matplotlib figure interactive inside JupyterLab with:
        1. Left-click to create events or regions
        2. Right-click to delete events or regions
        3. Segment-based navigation
    """
    
    if canvas.type == "tiers":
        fig, axs = canvas.fig, canvas.axs[:,0]
    else:
        raise RuntimeError("Annotation only allowed for `tiers` type canvas")
    
    try:
        iter(axs)
    except TypeError:
        axs = [axs]
        
    coord_label = Label(value="Hover over the plot...")
    status_label = Label(value="Tool: None")
    
    mode = {"tool": None}
    regions, region_patches = [], []
    events, event_lines = [], []
    ann = []
    
    btn_event = Button(description="Mark Event")
    btn_region = Button(description="Select Region")
    btn_prev = Button(description="<<")
    btn_next = Button(description=">>")
    segment_box = FloatText(value=0.0, description="View Size:", step=10)
    
    # Hover
    def hover(event):
        if event.inaxes in axs and event.xdata is not None and event.ydata is not None:
            coord_label.value = f"x = {event.xdata:.3f}, y = {event.ydata:.3f}"
        else:
            coord_label.value = "Hover over the plot..."
            
    # Click handling for events
    def onclick(event):
        if event.inaxes not in axs or mode["tool"] != "event" or event.xdata is None:
            return
        
        ax = event.inaxes
        x = event.xdata
        
        if event.button == 3:
            for i, (x_old, line) in enumerate(zip(events, event_lines)):
                if abs(x - x_old) < 0.02 * segment_box.value:
                    line.remove()
                    del events[i]
                    del event_lines[i]
                    ann[:] = [(a, b, c) for (a, b, c) in ann if a != x_old or b != x_old]
                    fig.canvas.draw_idle()
                    status_label.value = f"Deleted event near x={x_old:.3f}"
                    return
            return
        
        if event.button == 1:
            line = ax.axvline(x, color="orange", linestyle="--", alpha=0.7)
            events.append(x)
            event_lines.append(line)
            ann.append((x, x, ""))
            fig.canvas.draw_idle()
            status_label.value = f"Marked event at x={x:.3f}"
            
    # Region handling
    span_selectors = []
    
    def make_onselect(ax):
        def onselect(xmin, xmax):
            if mode["tool"] != "region":
                return
            if plt.get_current_fig_manager().canvas.manager.toolbar.mode != '':
                return
            if xmin == xmax:
                return
            
            patch = ax.axvspan(xmin, xmax, color="orange", alpha=0.3)
            regions.append((xmin, xmax))
            region_patches.append(patch)
            ann.append((xmin, xmax, ""))
            fig.canvas.draw_idle()
            status_label.value = f"Selected region: {xmin:.3f} – {xmax:.3f}"
        return onselect
    
    for ax in axs:
        selector = SpanSelector(
                ax,
                make_onselect(ax),
                direction="horizontal",
                useblit=True,
                props=dict(alpha=0.2, facecolor="orange"),
                interactive=False,
                button=1
        )
        selector.set_active(False)
        span_selectors.append(selector)
        
    # Right-click delete
    def on_right_click(event):
        if event.button != 3 or event.inaxes not in axs or mode["tool"] != "region" or event.xdata is None:
            return
        x = event.xdata
        for i, ((rmin, rmax), patch) in enumerate(zip(regions, region_patches)):
            if rmin <= x <= rmax:
                patch.remove()
                del regions[i]
                del region_patches[i]
                ann[:] = [(a, b, c) for (a, b, c) in ann if not (abs(a - rmin) < 1e-6 and abs(b - rmax) < 1e-6)]
                fig.canvas.draw_idle()
                status_label.value = f"Deleted region {rmin:.3f}–{rmax:.3f}"
                return
            
    # Tool switching
    def activate_event(_):
        mode["tool"] = "event"
        for s in span_selectors:
            s.set_active(False)
        status_label.value = "Tool: Event Marker (Left click: add, Right click: delete)"
        
    def activate_region(_):
        mode["tool"] = "region"
        for s in span_selectors:
            s.set_active(True)
        status_label.value = "Tool: Region Selector (Left-drag: add, Right click: delete)"
        
    # Navigation
    def get_xlim():
        return axs[0].get_xlim()
    
    def set_xlim(xmin, xmax):
        for ax in axs:
            ax.set_xlim(xmin, xmax)
        fig.canvas.draw_idle()
        
    def update_segment_width(_):
        width = segment_box.value
        xmin, _ = get_xlim()
        xmax = xmin + width
        set_xlim(xmin, xmax)
        status_label.value = f"Segment width changed to {width:.2f}s"
        
    def go_prev(_):
        width = segment_box.value
        xmin, xmax = get_xlim()
        new_start = xmin - width
        set_xlim(new_start, new_start + width)
        status_label.value = f"Moved to previous segment ({new_start:.2f}s)"
        
    def go_next(_):
        width = segment_box.value
        xmin, xmax = get_xlim()
        new_start = xmax
        set_xlim(new_start, new_start + width)
        status_label.value = f"Moved to next segment ({new_start:.2f}s)"
        
    # Bind
    fig.canvas.mpl_connect("motion_notify_event", hover)
    fig.canvas.mpl_connect("button_press_event", onclick)
    fig.canvas.mpl_connect("button_press_event", on_right_click)
    btn_event.on_click(activate_event)
    btn_region.on_click(activate_region)
    btn_prev.on_click(go_prev)
    btn_next.on_click(go_next)
    segment_box.observe(update_segment_width, names="value")
    
    # Layout
    tool_row = HBox([btn_event, btn_region, btn_prev, btn_next, segment_box])
    ui = VBox([tool_row, coord_label, status_label, fig.canvas])
    display(ui)
    
    return ann
