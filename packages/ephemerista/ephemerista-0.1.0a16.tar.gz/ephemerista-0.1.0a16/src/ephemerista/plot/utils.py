"""The utils.py module.

This module contains utility functions for plotting.
"""

import numpy as np
import plotly.graph_objects as go


def ensure_3d_cube_aspect_ratio(fig: go.Figure) -> go.Figure:
    """Ensure that a plotly 3D figure has a correct cube 1:1:1 aspect ratio.

    The function inspects all traces, edits the figure's layout in place, and returns the modified figure.
    """
    axes_names = ["x", "y", "z"]
    global_min = np.inf
    global_max = -np.inf
    axis_range_dict = {axis: [global_min, global_max] for axis in axes_names}

    # Explore all traces in figure and collect the axes' min and max values
    for trace in fig.select_traces():
        for axis in axes_names:
            if axis in trace:
                axis_range_dict[axis][0] = min(axis_range_dict[axis][0], np.min(trace[axis]))
                axis_range_dict[axis][1] = max(axis_range_dict[axis][1], np.max(trace[axis]))
                global_min = min(global_min, axis_range_dict[axis][0])
                global_max = max(global_max, axis_range_dict[axis][1])

    # Check if all min and max per axis are valid, then rescale and recenter the axes' min and max
    all_axes_ranges_valid = False
    global_range = global_max - global_min
    if not np.isinf(global_range):
        for axis in axes_names:
            axis_range = axis_range_dict[axis][1] - axis_range_dict[axis][0]
            if np.isinf(axis_range):
                continue
            all_axes_ranges_valid = True

            axis_range_delta = global_range - axis_range

            axis_range_dict[axis][0] = axis_range_dict[axis][0] - axis_range_delta / 2
            axis_range_dict[axis][1] = axis_range_dict[axis][1] + axis_range_delta / 2

    if all_axes_ranges_valid:
        fig.update_layout(
            scene={
                "aspectmode": "cube",
                "xaxis": {"range": axis_range_dict["x"]},
                "yaxis": {"range": axis_range_dict["y"]},
                "zaxis": {"range": axis_range_dict["z"]},
            },
        )

    return fig
