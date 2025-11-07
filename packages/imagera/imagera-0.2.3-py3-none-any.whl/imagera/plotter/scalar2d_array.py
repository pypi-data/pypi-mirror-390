from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from imagera.plotter import Scalar2d
from matplotlib.colors import Normalize, BoundaryNorm
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from dataclasses import replace
from typing import Optional
from imagera.plotter.plot_params import PlotParams
from imagera.plotter.cmap import resolve_cmap


def scalar2d_array(grid: np.ndarray, values_array: np.ndarray, *,
                   params: Optional[PlotParams] = None,
                   mosaic_title: Optional[str] = None,
                   **param_overrides) -> np.ndarray:

    # 1️⃣ Validate shapes
    if values_array.shape != grid.shape:
        raise ValueError(f"sensor_grid and psf_array shapes must match; got {grid.shape} vs {values_array.shape}")
    R, C = values_array.shape

    # 2️⃣  Extract function-only flags; pass only PlotParams fields into replace(...)
    tile_titles = bool(param_overrides.pop("tile_titles", False))
    with_colorbar = bool(param_overrides.pop("with_colorbar", True))
    mosaic_title = param_overrides.pop("mosaic_title", mosaic_title)

    base = params if params is not None else PlotParams()
    p = replace(base, **param_overrides)  # only PlotParams fields should remain here
    cmap, _ = resolve_cmap(p.cmap)

    # 3️ Global normalization (vmin/vmax or levels)
    vmins, vmaxs = [], []
    for i in range(R):
        for j in range(C):
            cell = values_array[i, j]
            if cell is None:
                continue
            values = np.asarray(cell, dtype=float)
            if np.isfinite(values).any():
                vmins.append(np.nanmin(values))
                vmaxs.append(np.nanmax(values))
    if not vmins:
        raise ValueError("No valid PSF grids to render.")

    vmin = p.v_min if getattr(p, "v_min", None) is not None else float(min(vmins))
    vmax = p.v_max if getattr(p, "v_max", None) is not None else float(max(vmaxs))

    if p.use_levels:
        n_levels = max(2, int(p.n_levels))
        levels = np.linspace(vmin, vmax, n_levels)
        ncolors = getattr(cmap, "N", 256)
        norm = BoundaryNorm(levels, ncolors=ncolors, clip=True)
    else:
        norm = Normalize(vmin=vmin, vmax=vmax)

    # 4️ Figure / GridSpec layout
    tile_w_in, tile_h_in = p.size_in
    extra_w = 0.6 if with_colorbar else 0.0
    fig_w_in = C * tile_w_in + extra_w
    fig_h_in = R * tile_h_in

    fig = plt.figure(figsize=(fig_w_in, fig_h_in), dpi=p.dpi)
    if with_colorbar:
        gs = gridspec.GridSpec(R, C + 1, figure=fig, width_ratios=[1] * C + [0.05])
        last_col_index = -1
    else:
        gs = gridspec.GridSpec(R, C, figure=fig, width_ratios=[1] * C)
        last_col_index = None  # no colorbar column

    # 5️ Render tiles using Plotter2D.render_into (shared logic)
    mappable = None
    for i in range(R):
        for j in range(C):
            ax = fig.add_subplot(gs[i, j])
            g = values_array[i, j]
            if g is None:
                ax.text(0.5, 0.5, "No PSF", ha="center", va="center")
                ax.set_axis_off()
                continue
            dp = Scalar2d(g, params=p)
            annotate_xy = (
                None if getattr(p, "annotate_xy", None) is not None
                else tuple(map(float, grid[i, j]))
            )
            plot_label = ("\u00A0" if not tile_titles else None)

            im, _ = dp.render_into(ax, norm=norm, annotate_xy=annotate_xy, plot_label=plot_label)
            if mappable is None:
                mappable = im

    # 6️ Colorbar axis
    if with_colorbar and (mappable is not None) and (last_col_index is not None):
        cax = fig.add_subplot(gs[:, last_col_index])
        cbar = fig.colorbar(mappable, cax=cax)
        # prefer PlotParams.value_label; else try to read from first non-None PSF
        label = getattr(p, "value_label", None)
        if not label:
            for i in range(R):
                for j in range(C):
                    g = values_array[i, j]
                    if g is not None:
                        label = getattr(g, "value_label", None)
                        if label:
                            break
                if label:
                    break
        if label:
            cbar.set_label(str(label), fontsize=12)

    # 7️ Mosaic title & rasterize to RGBA
    if mosaic_title:
        fig.suptitle(str(mosaic_title), y=0.995, fontsize=14)
    fig.tight_layout()
    canvas = FigureCanvas(fig)
    canvas.draw()
    rgba = np.asarray(canvas.buffer_rgba()).copy()
    plt.close(fig)
    return rgba
