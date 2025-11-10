from __future__ import annotations
import os
from typing import Optional
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch


def _mid_slices(vol3d: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    z = vol3d.shape[2] // 2
    y = vol3d.shape[1] // 2
    x = vol3d.shape[0] // 2
    return vol3d[:, :, z], vol3d[:, y, :], vol3d[x, :, :]


def _plot_hist(ax, values: np.ndarray, vmin: float, vmax: float, vmean: float, bins: int = 100) -> None:
    """Helper to render a consistent histogram panel with mean marker."""
    ax.hist(values, bins=bins, range=(vmin, vmax), color='gray', edgecolor='none')
    ax.axvline(vmean, color='red', linestyle='--', linewidth=1)
    ax.set_title("Histogram")
    ax.set_xlabel("voxel value"); ax.set_ylabel("count")


def save_triptych(input3d: np.ndarray,
                  mask3d: Optional[np.ndarray],
                  labels3d: Optional[np.ndarray],
                  out_dir: str,
                  prefix: str,
                  gt_mask3d: Optional[np.ndarray] = None,
                  gt_labels3d: Optional[np.ndarray] = None,
                  *,
                  vmin: Optional[float] = None,
                  vmax: Optional[float] = None) -> None:
    os.makedirs(out_dir, exist_ok=True)
    inp = np.squeeze(input3d)
    # Fix contrast: use global volume min/max if not provided
    if vmin is None or vmax is None:
        vmin = float(np.min(inp))
        vmax = float(np.max(inp))
        if vmax <= vmin:
            vmax = vmin + 1e-6
    # Compute summary stats once over the volume (ignore zeros when mostly background)
    nonzero = inp[np.nonzero(inp)]
    vals = nonzero if nonzero.size >= 10 else inp.ravel()
    vmin_stat = float(np.min(vals)) if vals.size else float(np.min(inp))
    vmax_stat = float(np.max(vals)) if vals.size else float(np.max(inp))
    vmean = float(np.mean(vals)) if vals.size else float(np.mean(inp))
    vstd = float(np.std(vals)) if vals.size else float(np.std(inp))

    a, c, s = _mid_slices(inp)
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    axes[0].imshow(a, cmap="gray", vmin=vmin, vmax=vmax); axes[0].set_title("Axial input")
    axes[1].imshow(c, cmap="gray", vmin=vmin, vmax=vmax); axes[1].set_title("Coronal input")
    axes[2].imshow(s, cmap="gray", vmin=vmin, vmax=vmax); axes[2].set_title("Sagittal input")
    for ax in axes[:3]: ax.axis('off')
    # Histogram subplot (ignore zeros when mostly background)
    _plot_hist(axes[3], vals, vmin_stat, vmax_stat, vmean)
    # Add global stats in the figure title
    fig.suptitle(f"stats [min={vmin_stat:.4g}, max={vmax_stat:.4g}, mean±sd={vmean:.4g}±{vstd:.4g}]")
    plt.tight_layout()
    fn = os.path.join(out_dir, f"{prefix}_input.png")
    plt.savefig(fn, bbox_inches='tight'); plt.close(fig)

    if mask3d is not None:
        m = np.squeeze(mask3d)
        a, c, s = _mid_slices(m)
        if gt_mask3d is not None:
            gm = np.squeeze(gt_mask3d)
            ga, gc, gs = _mid_slices(gm)
            fig, axes = plt.subplots(2, 3, figsize=(12, 8))
            axes[0,0].imshow(ga, cmap="viridis"); axes[0,0].set_title("GT Axial SS mask")
            axes[0,1].imshow(gc, cmap="viridis"); axes[0,1].set_title("GT Coronal SS mask")
            axes[0,2].imshow(gs, cmap="viridis"); axes[0,2].set_title("GT Sagittal SS mask")
            axes[1,0].imshow(a, cmap="viridis"); axes[1,0].set_title("Pred Axial SS mask")
            axes[1,1].imshow(c, cmap="viridis"); axes[1,1].set_title("Pred Coronal SS mask")
            axes[1,2].imshow(s, cmap="viridis"); axes[1,2].set_title("Pred Sagittal SS mask")
            for ax in axes.ravel(): ax.axis('off')
            fn = os.path.join(out_dir, f"{prefix}_ssmask_vs_gt.png")
            plt.tight_layout()
            plt.savefig(fn, bbox_inches='tight'); plt.close(fig)
        else:
            fig, axes = plt.subplots(1, 3, figsize=(12, 4))
            axes[0].imshow(a, cmap="viridis"); axes[0].set_title("Axial SS mask")
            axes[1].imshow(c, cmap="viridis"); axes[1].set_title("Coronal SS mask")
            axes[2].imshow(s, cmap="viridis"); axes[2].set_title("Sagittal SS mask")
            for ax in axes: ax.axis('off')
            fn = os.path.join(out_dir, f"{prefix}_ssmask.png")
            plt.tight_layout()
            plt.savefig(fn, bbox_inches='tight'); plt.close(fig)

    if labels3d is not None:
        # Categorical LUT (no overlay): 0=bg black, 1=CSF red, 2=GM green, 3=WM yellow
        lbl = np.squeeze(labels3d)
        a, c, s = _mid_slices(lbl)
        # High-contrast, viridis-inspired shades for GM/WM (user-preferred):
        #  - CSF red (kept)
        #  - GM ~ viridis mid-green/teal
        #  - WM ~ viridis bright yellow
        colors = [
            (0.0, 0.0, 0.0, 1.0),      # 0 background black
            (1.0, 0.0, 0.0, 1.0),      # 1 CSF red
            (0.13, 0.57, 0.55, 1.0),   # 2 GM viridis mid green/teal
            (0.99, 0.91, 0.14, 1.0),   # 3 WM viridis bright yellow
        ]
        lut = ListedColormap(colors)
        bounds = [-0.5, 0.5, 1.5, 2.5, 3.5]
        norm = BoundaryNorm(bounds, lut.N)
        legend_handles = [
            Patch(facecolor=colors[1], edgecolor='none', label='CSF=1'),
            Patch(facecolor=colors[2], edgecolor='none', label='GM=2'),
            Patch(facecolor=colors[3], edgecolor='none', label='WM=3'),
        ]
        if gt_labels3d is not None:
            gl = np.squeeze(gt_labels3d)
            ga, gc, gs = _mid_slices(gl)
            fig, axes = plt.subplots(2, 3, figsize=(12, 8))
            axes[0,0].imshow(ga, cmap=lut, norm=norm, interpolation='nearest'); axes[0,0].set_title("GT Axial Seg")
            axes[0,1].imshow(gc, cmap=lut, norm=norm, interpolation='nearest'); axes[0,1].set_title("GT Coronal Seg")
            axes[0,2].imshow(gs, cmap=lut, norm=norm, interpolation='nearest'); axes[0,2].set_title("GT Sagittal Seg")
            axes[1,0].imshow(a, cmap=lut, norm=norm, interpolation='nearest'); axes[1,0].set_title("Pred Axial Seg")
            axes[1,1].imshow(c, cmap=lut, norm=norm, interpolation='nearest'); axes[1,1].set_title("Pred Coronal Seg")
            axes[1,2].imshow(s, cmap=lut, norm=norm, interpolation='nearest'); axes[1,2].set_title("Pred Sagittal Seg")
            for ax in axes.ravel(): ax.axis('off')
            fig.legend(handles=legend_handles, loc='lower right', frameon=False)
            fn = os.path.join(out_dir, f"{prefix}_seg_vs_gt.png")
            plt.tight_layout()
            plt.savefig(fn, bbox_inches='tight'); plt.close(fig)
        else:
            fig, axes = plt.subplots(1, 3, figsize=(12, 4))
            axes[0].imshow(a, cmap=lut, norm=norm, interpolation='nearest'); axes[0].set_title("Axial Seg")
            axes[1].imshow(c, cmap=lut, norm=norm, interpolation='nearest'); axes[1].set_title("Coronal Seg")
            axes[2].imshow(s, cmap=lut, norm=norm, interpolation='nearest'); axes[2].set_title("Sagittal Seg")
            for ax in axes: ax.axis('off')
            fig.legend(handles=legend_handles, loc='lower right', frameon=False)
            fn = os.path.join(out_dir, f"{prefix}_seg.png")
            plt.tight_layout()
            plt.savefig(fn, bbox_inches='tight'); plt.close(fig)


def save_named_input(input3d: np.ndarray, out_dir: str, prefix: str, name: str) -> None:
    """Save axial/coronal/sagittal slices from input3d with a custom name suffix.

    Writes: f"{prefix}_{name}.png"
    """
    os.makedirs(out_dir, exist_ok=True)
    inp = np.squeeze(input3d)
    # Exact visualization: pick vmin/vmax based on data. If the tensor truly lives in [0,1]
    # (e.g., post-normalization), use that; otherwise use volume min/max so it doesn't look like a mask.
    vmin = float(np.min(inp)); vmax = float(np.max(inp))
    if vmax <= vmin:
        vmax = vmin + 1e-6
    if name.lower() in ("seginput", "seg_input", "seg"):
        if (vmin >= -1e-6) and (vmax <= 1.0 + 1e-6):
            vmin, vmax = 0.0, 1.0
    # Compute stats (ignore zeros when mostly background)
    nonzero = inp[np.nonzero(inp)]
    vals = nonzero if nonzero.size >= 10 else inp.ravel()
    vmin_stat = float(np.min(vals)) if vals.size else float(np.min(inp))
    vmax_stat = float(np.max(vals)) if vals.size else float(np.max(inp))
    vmean = float(np.mean(vals)) if vals.size else float(np.mean(inp))
    vstd = float(np.std(vals)) if vals.size else float(np.std(inp))

    a, c, s = _mid_slices(inp)
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    axes[0].imshow(a, cmap="gray", vmin=vmin, vmax=vmax); axes[0].set_title(f"Axial {name}")
    axes[1].imshow(c, cmap="gray", vmin=vmin, vmax=vmax); axes[1].set_title(f"Coronal {name}")
    axes[2].imshow(s, cmap="gray", vmin=vmin, vmax=vmax); axes[2].set_title(f"Sagittal {name}")
    for ax in axes[:3]: ax.axis('off')
    # Histogram subplot (ignore zeros when mostly background)
    _plot_hist(axes[3], vals, vmin_stat, vmax_stat, vmean)
    # Global stats in the title for auditing intensity mapping
    fig.suptitle(f"{name}: stats [min={vmin_stat:.4g}, max={vmax_stat:.4g}, mean±sd={vmean:.4g}±{vstd:.4g}]")
    plt.tight_layout()
    fn = os.path.join(out_dir, f"{prefix}_{name}.png")
    plt.savefig(fn, bbox_inches='tight'); plt.close(fig)


## Removed histogram comparison helper (no longer used)
