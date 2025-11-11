#!/usr/bin/env python3
"""
Sine-curve "Venn" diagrams up to N=8, plus a "cogwheel" circular variant.

- `sine_diagram(...)` draws the rectangular version over [0,  2π] × [-H, H].
- `cogwheel(...)` does the same, but if `radius` is not None it maps the
  half-plane picture onto a circle:
    * y = 0  →  circle of radius `radius`
    * y > 0  →  inside the circle
    * y < 0  →  outside the circle
"""

from typing import Sequence, Optional, Union, Tuple, Dict, Callable, List
import itertools

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.colors import to_rgb
from scipy.ndimage import distance_transform_edt


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _disjoint_region_masks(masks_list: Sequence[np.ndarray]) -> Dict[Tuple[int, ...], np.ndarray]:
    """
    Given a list of boolean membership masks for N sets (each shaped HxW),
    return a dict mapping every binary tuple key of length N (e.g., (1,0,1,0))
    to the corresponding disjoint region mask.
    """
    memb = np.stack(masks_list, axis=-1).astype(bool)  # (H,W,N)
    N = memb.shape[-1]
    keys = list(itertools.product((0, 1), repeat=N))   # all 2^N keys
    key_arr = np.array(keys, dtype=bool)               # (K,N)

    maskK = (memb[..., None, :] == key_arr[None, None, :, :]).all(axis=-1)
    return {tuple(map(int, k)): maskK[..., i] for i, k in enumerate(keys)}


def _visual_center(mask: np.ndarray, X: np.ndarray, Y: np.ndarray):
    """Visual center via Euclidean distance transform (SciPy)."""
    if not mask.any():
        return None
    dist = distance_transform_edt(mask)
    yy, xx = np.unravel_index(np.argmax(dist), dist.shape)
    return float(X[yy, xx]), float(Y[yy, xx])


def _centroid(mask: np.ndarray, X: np.ndarray, Y: np.ndarray):
    """Simple centroid of True pixels in mask."""
    if not mask.any():
        return None
    yy, xx = np.where(mask)
    return float(X[yy, xx].mean()), float(Y[yy, xx].mean())


def _visual_center_margin(mask: np.ndarray, X: np.ndarray, Y: np.ndarray, margin_frac: float = 0.05):
    """
    Visual center, but ignore a small margin near the rectangular box edges.
    """
    if not mask.any():
        return None

    H, W = mask.shape
    margin_y = max(1, int(margin_frac * H))
    margin_x = max(1, int(margin_frac * W))

    m2 = mask.copy()
    m2[:margin_y, :] = False
    m2[-margin_y:, :] = False
    m2[:, :margin_x] = False
    m2[:, -margin_x:] = False

    if not m2.any():
        return _visual_center(mask, X, Y)

    dist = distance_transform_edt(m2)
    yy, xx = np.unravel_index(np.argmax(dist), dist.shape)
    return float(X[yy, xx]), float(Y[yy, xx])


def _rgb(color: Union[str, tuple]) -> np.ndarray:
    """Convert any Matplotlib color into an RGB float array in [0,1]."""
    return np.array(to_rgb(color), float)


def _color_mix_average(colors: Sequence[np.ndarray]) -> np.ndarray:
    """Simple average of the provided RGB colors."""
    if not colors:
        return np.zeros(3, float)
    arr = np.stack([np.array(c, float) for c in colors], axis=0)
    return arr.mean(axis=0)


def _color_mix_subtractive(colors: Sequence[np.ndarray]) -> np.ndarray:
    """Subtractive color mixing (same idea as in your Venn script)."""
    if not colors:
        return np.zeros(3, float)
    arr = np.stack([np.array(c, float) for c in colors], axis=0)
    return np.abs(1.0 - (np.prod(1 - arr, axis=0)) * (len(colors) ** 0.25))


def _auto_text_color_from_rgb(rgb: np.ndarray) -> str:
    """Choose black or white text based on background luminance."""
    lum = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
    return "white" if lum < 0.5 else "black"


def _normalize_angle_90(deg: float) -> float:
    """Map any angle (deg) to an equivalent in about [-90, +90] for legible text."""
    a = float(deg)
    while a > 95.0:
        a -= 180.0
    while a < -85.0:
        a += 180.0
    return a


def _region_label_orientation(
    mask: np.ndarray,
    X: np.ndarray,
    Y: np.ndarray,
    anchor_x: float,
    anchor_y: float,
    n_angles: int = 72,
    seg_frac: float = 0.25,
) -> float:
    """
    For N>5: choose rotation by finding the direction along which a line segment
    centered at (anchor_x, anchor_y) intersects the region the longest.
    """
    if not mask.any():
        return 0.0

    H, W = mask.shape
    xs = X[0, :]
    ys = Y[:, 0]
    if xs.size < 2 or ys.size < 2:
        return 0.0

    dx = xs[1] - xs[0]
    dy = ys[1] - ys[0]
    if dx == 0 or dy == 0:
        return 0.0

    span_x = xs[-1] - xs[0]
    span_y = ys[-1] - ys[0]
    L = seg_frac * max(abs(span_x), abs(span_y))  # half-length of segment

    best_count = -1
    best_theta = 0.0

    num_samples = 200
    t_vals = np.linspace(-L, L, num_samples)

    for k in range(n_angles):
        theta = np.pi * k / n_angles  # 0..π
        ct = np.cos(theta)
        st = np.sin(theta)

        x_s = anchor_x + t_vals * ct
        y_s = anchor_y + t_vals * st

        ix = np.round((x_s - xs[0]) / dx).astype(int)
        iy = np.round((y_s - ys[0]) / dy).astype(int)

        valid = (ix >= 0) & (ix < W) & (iy >= 0) & (iy < H)
        if not np.any(valid):
            continue

        inside = mask[iy[valid], ix[valid]]
        count = int(inside.sum())
        if count > best_count:
            best_count = count
            best_theta = theta

    if best_count <= 0:
        return 0.0

    deg = np.degrees(best_theta)
    return _normalize_angle_90(deg)


# ---------------------------------------------------------------------------
# Curve helper
# ---------------------------------------------------------------------------

def get_curve(
    X,
    harmonic,
    height_scale,
    max_harmonic=None,
    curve_exponent: float = 0.33,
    amp_decay_base: float = 0.75,
):
    """
    Nonlinear sine-like curve for class boundary (π-shifted).

    Parameters
    ----------
    curve_exponent : float
        Exponent applied to |sin|, default 0.33.
    amp_decay_base : float
        Base for amplitude decay: amp = amp_decay_base ** log2(harmonic).
    """
    X = np.asarray(X, float)
    harmonic = float(harmonic)

    base = np.sin(harmonic * X + np.pi)  # SHIFT BY π
    shaped = np.sign(base) * np.abs(base) ** curve_exponent
    amp = amp_decay_base ** np.log2(harmonic)
    return height_scale * shaped * amp


# ---------------------------------------------------------------------------
# Main rectangular plotting function
# ---------------------------------------------------------------------------

def sine_diagram(
    values,
    class_names: Sequence[str],
    colors: Optional[Sequence[Union[str, tuple]]] = None,
    title: Optional[str] = None,
    outfile: Optional[str] = None,
    dpi: int = 100,
    color_mixing: Union[str, Callable[[Sequence[np.ndarray]], np.ndarray]] = "subtractive",
    text_color: Optional[str] = None,
    region_label_fontsize: int = 10,
    class_label_fontsize: int = 12,
    sample_res_x: int = 900,
    sample_res_y: int = 900,
    height_scale: float = 2.0,
    include_constant_last: bool = True,
    curve_exponent: float = 0.33,
    amp_decay_base: float = 0.75,
) -> Optional[Figure]:
    """
    Draw a "Venn-style" diagram for up to N=8 sets defined by shaped sine curves
    on a rectangle [0, 2π] × [-height_scale*1.2, +height_scale*1.2].

    If include_constant_last=True (default), the last class is the constant term
    y >= 0; otherwise all classes are sine-like.

    curve_exponent and amp_decay_base control the shaping in get_curve().
    """
    arr = np.asarray(values, dtype=object)
    if arr.ndim < 1 or arr.ndim > 8:
        raise ValueError("Only N in {1,2,...,8} are supported.")
    N = arr.ndim
    expected_shape = (2,) * N
    if arr.shape != expected_shape:
        raise ValueError(f"values must have shape {expected_shape}, got {arr.shape}.")
    if len(class_names) != N:
        raise ValueError(f"class_names must have length {N}.")
    if N > 8:
        raise ValueError("N>8 not supported.")

    # Colors (cycle if not provided)
    if colors is None:
        default_cycle = [
            "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
            "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
        ]
        colors = [default_cycle[i % len(default_cycle)] for i in range(N)]
    rgbs = list(map(_rgb, colors))

    # Color mixing callback
    if isinstance(color_mixing, str):
        if color_mixing == "subtractive":
            mixing_cb = _color_mix_subtractive
        elif color_mixing == "average":
            mixing_cb = _color_mix_average
        else:
            raise ValueError(f"Unrecognized color_mixing string: {color_mixing!r}")
    elif callable(color_mixing):
        mixing_cb = color_mixing
    else:
        raise TypeError("color_mixing must be either a string or a callable.")

    # Sampling grid in the universe rectangle
    x_min, x_max = 0.0, 2.0 * np.pi
    y_min, y_max = -float(height_scale) * 1.2, float(height_scale) * 1.2
    xs = np.linspace(x_min, x_max, int(sample_res_x))
    ys = np.linspace(y_min, y_max, int(sample_res_y))
    X, Y = np.meshgrid(xs, ys)

    # Membership masks
    membership: List[np.ndarray] = []

    def _harmonic_info(i: int) -> Tuple[Optional[float], Optional[float]]:
        """Return (harmonic, max_harmonic) or (None, None) for constant."""
        if include_constant_last and N >= 1 and i == N - 1:
            # Last class is constant term
            return None, None
        exp = i
        if include_constant_last:
            max_exp = max(N - 2, 0)
        else:
            max_exp = max(N - 1, 0)
        harmonic = 2.0 ** exp
        max_harmonic = 2.0 ** max_exp if max_exp > 0 else harmonic
        return harmonic, max_harmonic

    for i in range(N):
        harmonic, max_harmonic = _harmonic_info(i)
        if harmonic is None:
            mask = Y >= 0.0
        else:
            curve = get_curve(
                X,
                harmonic,
                height_scale,
                max_harmonic,
                curve_exponent=curve_exponent,
                amp_decay_base=amp_decay_base,
            )
            mask = Y >= curve
        membership.append(mask)

    # Disjoint region masks and region colors
    region_masks = _disjoint_region_masks(membership)
    H, W = X.shape
    rgba = np.zeros((H, W, 4), float)
    region_rgbs: Dict[Tuple[int, ...], np.ndarray] = {}

    for key, mask in region_masks.items():
        if not any(key):
            continue
        if not mask.any():
            continue
        colors_for_key = [rgbs[i] for i, bit in enumerate(key) if bit]
        mixed_rgb = np.asarray(mixing_cb(colors_for_key), float)
        if mixed_rgb.shape != (3,):
            raise ValueError("color_mixing callback must return an RGB array of shape (3,).")
        region_rgbs[key] = mixed_rgb
        rgba[mask, 0] = mixed_rgb[0]
        rgba[mask, 1] = mixed_rgb[1]
        rgba[mask, 2] = mixed_rgb[2]
        rgba[mask, 3] = 1.0

    # Figure and axes
    fig, ax = plt.subplots(figsize=(15, 5 * height_scale))
    ax.imshow(
        rgba,
        origin="lower",
        extent=[x_min, x_max, y_min, y_max],
        interpolation="nearest",
        zorder=1,
    )
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_aspect("auto")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.margins(0.0, 0.0)

    # Bounding box in black
    ax.add_patch(
        Rectangle(
            (x_min, y_min),
            x_max - x_min,
            y_max - y_min,
            fill=False,
            edgecolor="black",
            linewidth=1.5,
            zorder=3,
        )
    )

    # Class boundaries (store curves)
    x_plot = np.linspace(x_min, x_max, 1200)
    curves: List[np.ndarray] = []
    harmonics_for_class: List[Optional[float]] = []

    for i in range(N):
        harmonic, max_harmonic = _harmonic_info(i)
        harmonics_for_class.append(harmonic)

        if harmonic is None:
            y_plot = np.zeros_like(x_plot)
        else:
            y_plot = get_curve(
                x_plot,
                harmonic,
                height_scale,
                max_harmonic,
                curve_exponent=curve_exponent,
                amp_decay_base=amp_decay_base,
            )

        curves.append(y_plot)

        ax.plot(
            x_plot,
            y_plot,
            color=colors[i],
            linewidth=2.0,
            zorder=4,
        )

    # Last local maximum for last non-constant class
    last_max_x = None
    non_const_indices = [i for i, h in enumerate(harmonics_for_class) if h is not None]
    if non_const_indices:
        last_idx = non_const_indices[-1]
        y_last = curves[last_idx]
        dy_last = np.diff(y_last)
        sign_last = np.sign(dy_last)

        idx_max = None
        for j in range(1, len(sign_last)):
            if sign_last[j - 1] > 0 and sign_last[j] < 0:
                idx_max = j
        if idx_max is None:
            idx_max = int(np.argmax(y_last))
        last_max_x = x_plot[idx_max]

    zeros = (0,) * N
    ones = (1,) * N

    # Generic region labels
    for key, mask in region_masks.items():
        if key == zeros or key == ones:
            continue
        value = arr[key]
        if value is None or not mask.any():
            continue

        pos = _visual_center(mask, X, Y)
        if pos is None:
            continue

        if text_color is None:
            if key in region_rgbs:
                rgb = region_rgbs[key]
                this_color = _auto_text_color_from_rgb(rgb)
            else:
                this_color = "black"
        else:
            this_color = text_color

        if N > 5:
            rot = _region_label_orientation(mask, X, Y, pos[0], pos[1])
        else:
            rot = 0.0

        ax.text(
            pos[0],
            pos[1],
            f"{value}",
            ha="center",
            va="center",
            fontsize=region_label_fontsize,
            color=this_color,
            zorder=5,
            rotation=rot,
            rotation_mode="anchor",
        )

    # All-sets intersection
    all_mask = np.logical_and.reduce(membership)
    if all_mask.any():
        val_all = arr[ones]
        if val_all is not None:
            pos = _visual_center_margin(all_mask, X, Y, margin_frac=0.05)
            if pos is not None:
                if text_color is None:
                    rgb = region_rgbs.get(ones)
                    this_color = _auto_text_color_from_rgb(rgb) if rgb is not None else "black"
                else:
                    this_color = text_color

                if N > 5:
                    rot = _region_label_orientation(all_mask, X, Y, pos[0], pos[1])
                else:
                    rot = 0.0

                ax.text(
                    pos[0],
                    pos[1],
                    f"{val_all}",
                    ha="center",
                    va="center",
                    fontsize=region_label_fontsize,
                    color=this_color,
                    zorder=5,
                    rotation=rot,
                    rotation_mode="anchor",
                )

    # Complement
    comp_mask = np.logical_not(np.logical_or.reduce(membership))
    if comp_mask.any():
        val_comp = arr[zeros]
        if val_comp is not None:
            pos = _visual_center_margin(comp_mask, X, Y, margin_frac=0.05)
            if pos is not None:
                if text_color is None:
                    this_color = "black"
                else:
                    this_color = text_color

                if N > 5:
                    rot = _region_label_orientation(comp_mask, X, Y, pos[0], pos[1])
                else:
                    rot = 0.0

                ax.text(
                    pos[0],
                    pos[1],
                    f"{val_comp}",
                    ha="center",
                    va="center",
                    fontsize=region_label_fontsize,
                    color=this_color,
                    zorder=5,
                    rotation=rot,
                    rotation_mode="anchor",
                )

    # Class labels
    for i, (name, col) in enumerate(zip(class_names, rgbs)):
        y_plot = curves[i]
        harmonic = harmonics_for_class[i]

        if harmonic is None:
            if last_max_x is None:
                x_lab = 0.5 * (x_min + x_max)
            else:
                x_lab = last_max_x
            y_lab = -0.1 * height_scale
        else:
            dy = np.diff(y_plot)
            sign = np.sign(dy)
            i_min_loc = None
            for j in range(1, len(sign)):
                if sign[j - 1] < 0 and sign[j] > 0:
                    i_min_loc = j
            if i_min_loc is None:
                i_min_loc = int(np.argmin(y_plot))
            x_lab = x_plot[i_min_loc]
            y_lab = y_plot[i_min_loc] - 0.1 * height_scale
            if y_lab < y_min + 0.05 * height_scale:
                y_lab = y_min + 0.05 * height_scale

        ax.text(
            x_lab,
            y_lab,
            name,
            ha="center",
            va="top",
            fontsize=class_label_fontsize,
            color=tuple(col),
            fontweight="bold",
            zorder=6,
        )

    if title:
        ax.set_title(title)

    if outfile:
        fig.savefig(outfile, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
        return None

    return fig


# ---------------------------------------------------------------------------
# Half-plane → disc mapping
# ---------------------------------------------------------------------------

def _halfplane_to_disc(
    x: np.ndarray,
    y: np.ndarray,
    radius: float,
    y_min: float,
    y_max: float,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Map (x,y) in the rectangular half-plane to (u,v) in the cogwheel plane.

    - y = 0 maps to radius = R.
    - y > 0 maps inside the circle (radius < R).
    - y < 0 maps outside the circle (radius > R, up to 2R).
    """
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    R = float(radius)
    R_out = 2.0 * R

    y_pos_max = float(max(0.0, y_max))
    y_neg_min = float(min(0.0, y_min))  # negative

    rho = np.empty_like(y)

    pos = (y >= 0.0)
    neg = ~pos

    rho[pos] = R * (1.0 - y[pos] / y_pos_max)

    denom = (R_out - R)
    rho[neg] = R + denom * (y[neg] / y_neg_min)

    theta = x
    u = rho * np.cos(theta)
    v = rho * np.sin(theta)
    return u, v


# ---------------------------------------------------------------------------
# Cogwheel version
# ---------------------------------------------------------------------------

def cogwheel(
    values,
    class_names: Sequence[str],
    colors: Optional[Sequence[Union[str, tuple]]] = None,
    title: Optional[str] = None,
    outfile: Optional[str] = None,
    dpi: int = 100,
    color_mixing: Union[str, Callable[[Sequence[np.ndarray]], np.ndarray]] = "subtractive",
    text_color: Optional[str] = None,
    region_label_fontsize: int = 10,
    class_label_fontsize: int = 12,
    sample_res_x: int = 900,
    sample_res_y: int = 900,
    height_scale: float = 2.0,
    include_constant_last: bool = True,
    radius: Optional[float] = None,
    curve_exponent: float = 0.33,
    amp_decay_base: float = 0.75,
) -> Optional[Figure]:
    """
    Cogwheel variant of the sine diagram.

    - If radius is None: identical to `sine_diagram(...)` (rectangular).
    - If radius is a positive number:
        * The constant line y=0 becomes a circle of radius `radius`.
        * y>0 maps inside the circle (disc).
        * y<0 maps outside the circle (complement of the disc).
    """
    if radius is None:
        return sine_diagram(
            values,
            class_names,
            colors=colors,
            title=title,
            outfile=outfile,
            dpi=dpi,
            color_mixing=color_mixing,
            text_color=text_color,
            region_label_fontsize=region_label_fontsize,
            class_label_fontsize=class_label_fontsize,
            sample_res_x=sample_res_x,
            sample_res_y=sample_res_y,
            height_scale=height_scale,
            include_constant_last=include_constant_last,
            curve_exponent=curve_exponent,
            amp_decay_base=amp_decay_base,
        )

    arr = np.asarray(values, dtype=object)
    if arr.ndim < 1 or arr.ndim > 8:
        raise ValueError("Only N in {1,2,...,8} are supported.")
    N = arr.ndim
    expected_shape = (2,) * N
    if arr.shape != expected_shape:
        raise ValueError(f"values must have shape {expected_shape}, got {arr.shape}.")
    if len(class_names) != N:
        raise ValueError(f"class_names must have length {N}.")
    if N > 8:
        raise ValueError("N>8 not supported.")

    # Colors
    if colors is None:
        default_cycle = [
            "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
            "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
        ]
        colors = [default_cycle[i % len(default_cycle)] for i in range(N)]
    rgbs = list(map(_rgb, colors))

    # Color mixing callback
    if isinstance(color_mixing, str):
        if color_mixing == "subtractive":
            mixing_cb = _color_mix_subtractive
        elif color_mixing == "average":
            mixing_cb = _color_mix_average
        else:
            raise ValueError(f"Unrecognized color_mixing string: {color_mixing!r}")
    elif callable(color_mixing):
        mixing_cb = color_mixing
    else:
        raise TypeError("color_mixing must be either a string or a callable.")

    x_min, x_max = 0.0, 2.0 * np.pi
    y_min, y_max = -float(height_scale) * 1.2, float(height_scale) * 1.2

    R = float(radius)
    R_out = 2.0 * R
    us = np.linspace(-R_out, R_out, int(sample_res_x))
    vs = np.linspace(-R_out, R_out, int(sample_res_y))
    U, V = np.meshgrid(us, vs)

    rho = np.sqrt(U * U + V * V)
    theta = np.arctan2(V, U)
    theta = np.mod(theta, 2.0 * np.pi)

    x_old = theta.copy()
    y_old = np.full_like(U, y_min - 1.0)

    y_pos_max = float(max(0.0, y_max))
    y_neg_min = float(min(0.0, y_min))

    inside_disc = (rho <= R)
    ring = (rho > R) & (rho <= R_out)

    t_in = np.zeros_like(rho)
    t_in[inside_disc] = rho[inside_disc] / R
    y_old[inside_disc] = y_pos_max * (1.0 - t_in[inside_disc])

    t_out = np.zeros_like(rho)
    denom = (R_out - R)
    t_out[ring] = (rho[ring] - R) / denom
    y_old[ring] = y_neg_min * t_out[ring]

    membership: List[np.ndarray] = []

    def _harmonic_info(i: int) -> Tuple[Optional[float], Optional[float]]:
        if include_constant_last and N >= 1 and i == N - 1:
            return None, None
        exp = i
        if include_constant_last:
            max_exp = max(N - 2, 0)
        else:
            max_exp = max(N - 1, 0)
        harmonic = 2.0 ** exp
        max_harmonic = 2.0 ** max_exp if max_exp > 0 else harmonic
        return harmonic, max_harmonic

    for i in range(N):
        harmonic, max_harmonic = _harmonic_info(i)
        if harmonic is None:
            mask = y_old >= 0.0
        else:
            curve = get_curve(
                x_old,
                harmonic,
                height_scale,
                max_harmonic,
                curve_exponent=curve_exponent,
                amp_decay_base=amp_decay_base,
            )
            mask = y_old >= curve
        membership.append(mask)

    region_masks = _disjoint_region_masks(membership)
    H, W = U.shape
    rgba = np.zeros((H, W, 4), float)
    region_rgbs: Dict[Tuple[int, ...], np.ndarray] = {}

    for key, mask in region_masks.items():
        if not any(key):
            continue
        if not mask.any():
            continue
        colors_for_key = [rgbs[i] for i, bit in enumerate(key) if bit]
        mixed_rgb = np.asarray(mixing_cb(colors_for_key), float)
        if mixed_rgb.shape != (3,):
            raise ValueError("color_mixing callback must return an RGB array of shape (3,).")
        region_rgbs[key] = mixed_rgb
        rgba[mask, 0] = mixed_rgb[0]
        rgba[mask, 1] = mixed_rgb[1]
        rgba[mask, 2] = mixed_rgb[2]
        rgba[mask, 3] = 1.0

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(
        rgba,
        origin="lower",
        extent=[-R_out, R_out, -R_out, R_out],
        interpolation="nearest",
        zorder=1,
    )
    ax.set_xlim(-R_out, R_out)
    ax.set_ylim(-R_out, R_out)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.margins(0.0, 0.0)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Class boundaries in cogwheel plane
    x_plot = np.linspace(x_min, x_max, 1200)
    curves: List[np.ndarray] = []
    harmonics_for_class: List[Optional[float]] = []

    for i in range(N):
        harmonic, max_harmonic = _harmonic_info(i)
        harmonics_for_class.append(harmonic)

        if harmonic is None:
            y_plot = np.zeros_like(x_plot)
        else:
            y_plot = get_curve(
                x_plot,
                harmonic,
                height_scale,
                max_harmonic,
                curve_exponent=curve_exponent,
                amp_decay_base=amp_decay_base,
            )

        curves.append(y_plot)

        u_curve, v_curve = _halfplane_to_disc(x_plot, y_plot, R, y_min, y_max)
        ax.plot(
            u_curve,
            v_curve,
            color=colors[i],
            linewidth=2.0,
            zorder=4,
        )

    # Last local max for last non-constant (in half-plane x)
    last_max_x = None
    non_const_indices = [i for i, h in enumerate(harmonics_for_class) if h is not None]
    if non_const_indices:
        last_idx = non_const_indices[-1]
        y_last = curves[last_idx]
        dy_last = np.diff(y_last)
        sign_last = np.sign(dy_last)
        idx_max = None
        for j in range(1, len(sign_last)):
            if sign_last[j - 1] > 0 and sign_last[j] < 0:
                idx_max = j
        if idx_max is None:
            idx_max = int(np.argmax(y_last))
        last_max_x = x_plot[idx_max]

    zeros = (0,) * N
    ones = (1,) * N

    # Generic region labels
    for key, mask in region_masks.items():
        if key == zeros or key == ones:
            continue
        value = arr[key]
        if value is None or not mask.any():
            continue

        pos = _visual_center(mask, U, V)
        if pos is None:
            continue

        if text_color is None:
            if key in region_rgbs:
                rgb = region_rgbs[key]
                this_color = _auto_text_color_from_rgb(rgb)
            else:
                this_color = "black"
        else:
            this_color = text_color

        if N > 5:
            rot = _region_label_orientation(mask, U, V, pos[0], pos[1])
        else:
            rot = 0.0

        ax.text(
            pos[0],
            pos[1],
            f"{value}",
            ha="center",
            va="center",
            fontsize=region_label_fontsize,
            color=this_color,
            zorder=5,
            rotation=rot,
            rotation_mode="anchor",
        )

    # All-sets intersection
    all_mask = np.logical_and.reduce(membership)
    if all_mask.any():
        val_all = arr[ones]
        if val_all is not None:
            pos = _visual_center_margin(all_mask, U, V, margin_frac=0.05)
            if pos is not None:
                if text_color is None:
                    rgb = region_rgbs.get(ones)
                    this_color = _auto_text_color_from_rgb(rgb) if rgb is not None else "black"
                else:
                    this_color = text_color

                if N > 5:
                    rot = _region_label_orientation(all_mask, U, V, pos[0], pos[1])
                else:
                    rot = 0.0

                ax.text(
                    pos[0],
                    pos[1],
                    f"{val_all}",
                    ha="center",
                    va="center",
                    fontsize=region_label_fontsize,
                    color=this_color,
                    zorder=5,
                    rotation=rot,
                    rotation_mode="anchor",
                )

    # Complement
    comp_mask = np.logical_not(np.logical_or.reduce(membership))
    if comp_mask.any():
        val_comp = arr[zeros]
        if val_comp is not None:
            pos = _visual_center_margin(comp_mask, U, V, margin_frac=0.05)
            if pos is not None:
                if text_color is None:
                    this_color = "black"
                else:
                    this_color = text_color

                if N > 5:
                    rot = _region_label_orientation(comp_mask, U, V, pos[0], pos[1])
                else:
                    rot = 0.0

                ax.text(
                    pos[0],
                    pos[1],
                    f"{val_comp}",
                    ha="center",
                    va="center",
                    fontsize=region_label_fontsize,
                    color=this_color,
                    zorder=5,
                    rotation=rot,
                    rotation_mode="anchor",
                )

    # Class labels on cogwheel
    for i, (name, col) in enumerate(zip(class_names, rgbs)):
        y_plot = curves[i]
        harmonic = harmonics_for_class[i]

        if harmonic is None:
            # constant line y=0
            if last_max_x is None:
                x_lab = 0.5 * (x_min + x_max)
            else:
                x_lab = last_max_x
            y_lab = -0.1 * height_scale
        else:
            dy = np.diff(y_plot)
            sign = np.sign(dy)
            i_min_loc = None
            for j in range(1, len(sign)):
                if sign[j - 1] < 0 and sign[j] > 0:
                    i_min_loc = j
            if i_min_loc is None:
                i_min_loc = int(np.argmin(y_plot))
            x_lab = x_plot[i_min_loc]
            y_lab = y_plot[i_min_loc] - 0.1 * height_scale
            if y_lab < y_min + 0.05 * height_scale:
                y_lab = y_min + 0.05 * height_scale

        u_lab, v_lab = _halfplane_to_disc(
            np.array([x_lab]),
            np.array([y_lab]),
            R,
            y_min,
            y_max,
        )
        u_lab = float(u_lab[0])
        v_lab = float(v_lab[0])

        if harmonic is None and N > 4:
            # Infinity label: keep horizontal if N>4
            rot = 0.0
        else:
            theta_lab = np.arctan2(v_lab, u_lab)
            tangent_angle_deg = np.degrees(theta_lab + np.pi / 2.0)
            rot = _normalize_angle_90(tangent_angle_deg)

        ax.text(
            u_lab,
            v_lab,
            name,
            ha="center",
            va="top",
            fontsize=class_label_fontsize,
            color=tuple(col),
            fontweight="bold",
            rotation=rot,
            rotation_mode="anchor",
            zorder=6,
        )

    if title:
        ax.set_title(title)

    if outfile:
        fig.savefig(outfile, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
        return None

    return fig


# ---------------------------------------------------------------------------
# Simple self-test / demo
# ---------------------------------------------------------------------------

def _make_demo_values(N: int) -> np.ndarray:
    """
    Label each region by which sets it belongs to, e.g. "", "A", "BC", "ABCDE", etc.
    For testing, the complement (all zeros) is labeled "None".
    """
    letters = [chr(ord("A") + i) for i in range(N)]
    shape = (2,) * N
    arr = np.empty(shape, dtype=object)
    for idx in np.ndindex(shape):
        s = "".join(letters[i] for i, bit in enumerate(idx) if bit)
        arr[idx] = s
    arr[(0,) * N] = "None"
    return arr


if __name__ == "__main__":
    greek_names = [
        "Alpha", "Beta", "Gamma", "Delta",
        "Epsilon", "Zeta", "Eta", "Theta",
    ]

    # Rectangular version
    # for N in range(6, 8):
    #     values = _make_demo_values(N)
    #     class_names = greek_names[:N]
    #     outfile = f"sine_diagram_N{N}.png"
    #     sine_diagram(
    #         values,
    #         class_names,
    #         outfile=outfile,
    #         height_scale=2.0,
    #         include_constant_last=True,
    #         color_mixing="average",
    #     )

    # Cogwheel version with custom shape parameters
    for N in range(6, 8):
        values = _make_demo_values(N)
        class_names = greek_names[:N]
        
        if N == 6:
            colors6 = ["#D926D9", "#3939D4", "#26D9D9", "#26D926", "#D9D926", "#D92626"]
            outlines6 = ["#A112A1", "#1212A1", "#12A1A1", "#12A112", "#A1A112", "#A11212"]
        else:
            colors6 = None
            outlines6 = None
        outfile = f"cogwheel_N{N}_r4.png"
        cogwheel(
            values,
            class_names,
            outfile=outfile,
            height_scale=2.0,
            include_constant_last=True,
            color_mixing="average",
            region_label_fontsize=9,
            radius=4.0,
            text_color="black",
            curve_exponent=0.2,
            amp_decay_base=0.8,
            region_radial_offset_inside=0.02,
            region_radial_offset_outside=0.02,
        )
