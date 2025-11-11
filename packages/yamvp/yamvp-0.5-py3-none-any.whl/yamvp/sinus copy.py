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
# Per-N color palettes (up to 10 sets)
# Explicit lists of hex strings per N, no shared master palette.
# High-ish frequency magenta → red along the spectrum.
# N=6 EXACTLY matches your example for fills & outlines.
# ---------------------------------------------------------------------------

DEFAULT_FILL_COLORS_BY_N: Dict[int, List[str]] = {
    1: ["#42FF42"],
    2: ["#42FFFF", "#FF4242"],
    3: ["#42FFFF", "#FFFF42", "#FF4242"],
    4: ["#5858FF", "#42FF42", "#FFFF42", "#FF4242"],
    5: ["#5858FF", "#42FFFF", "#42FF42", "#FFFF42", "#FF4242"],
    6: ["#8872FF", "#78D0FC", "#77FDBA", "#A0FA73", "#FEE774", "#F97575"],
    7: ["#743BFF", "#3B8FFF", "#3BFFE3", "#3BFF58", "#AAFF3B", "#FFC73B", "#FF3B3B"],
    8: ["#8E48FF", "#507BFF", "#3EE6FF", "#3BFF9D", "#54FF3B", "#CFFF45", "#FFB53E", "#FF4B4B"],
    9: ["#913BFF", "#3B51FF", "#3BBCFF", "#3BFFD3", "#3EFF67", "#7DFF3B", "#E8FF3B", "#FFA83B", "#FF3B3B"],
    10: [
        "#A042FF",  # purple
        "#4242FF",  # blue
        "#42A0FF",  # sky blue
        "#42FFFF",  # cyan
        "#42FFA0",  # spring green
        "#42FF42",  # green
        "#A0FF42",  # yellow-green
        "#FFFF42",  # yellow
        "#FFA042",  # orange
        "#FF4242",  # red
    ],
}

DEFAULT_OUTLINE_COLORS_BY_N: Dict[int, List[str]] = {
    1: ["#0D730D"],
    2: ["#0E7373", "#730D0D"],
    3: ["#0E7373", "#73730D", "#730D0D"],
    4: ["#0D0D73", "#0D730D", "#73730D", "#730D0D"],
    5: ["#0D0D73", "#0D7373", "#0D730D", "#73730D", "#730D0D"],
    6: ["#110067", "#004669", "#006332", "#256E01", "#715E00", "#6D0000"],
    7: ["#2D1173", "#113B73", "#127364", "#11731F", "#497311", "#735711", "#731111"],
    8: ["#361173", "#112973", "#116773", "#117342", "#1B730F", "#5A7311", "#734E11", "#731111"],
    9: ["#3D1173", "#111C73", "#115373", "#12735E", "#117327", "#327311", "#687311", "#734711", "#731111"],
    10: [
        "#421173",  # purple
        "#111173",  # deep blue
        "#114273",  # teal-blue
        "#117373",  # teal
        "#117342",  # green
        "#117311",  # yellow-green
        "#427311",  # olive-ish
        "#737311",  # dark yellow
        "#734211",  # brownish orange
        "#731111",  # dark red
    ],
}
def _default_palette_for_n(N: int) -> Tuple[List[str], List[str]]:
    """
    Return (fill_colors, outline_colors) for a given N, using explicit
    per-N lists. If N not in dict, clamp to nearest defined N.
    """
    if not DEFAULT_FILL_COLORS_BY_N:
        raise RuntimeError("No default color palettes defined.")

    keys = sorted(DEFAULT_FILL_COLORS_BY_N.keys())
    N_clamped = max(keys[0], min(keys[-1], N))

    fills = DEFAULT_FILL_COLORS_BY_N.get(N_clamped)
    outlines = DEFAULT_OUTLINE_COLORS_BY_N.get(N_clamped)

    if fills is None or outlines is None:
        raise RuntimeError(f"No palette defined for N={N_clamped}.")

    if len(fills) != N_clamped or len(outlines) != N_clamped:
        raise RuntimeError(f"Palette length mismatch for N={N_clamped}.")

    # If N != N_clamped, map to N colors by index interpolation
    if N != N_clamped:
        idxs = np.linspace(0, N_clamped - 1, N).round().astype(int)
        fills = [fills[i] for i in idxs]
        outlines = [outlines[i] for i in idxs]
    else:
        fills = list(fills)
        outlines = list(outlines)

    return fills, outlines


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


def _color_mix_subtractive(colors):
    """
    Mix colors by subtracive mixing.
    """
    if not colors:
        return np.zeros(3, float)
    arr = np.stack([np.array(c, float) for c in colors], axis=0)
    return np.abs(1.0 - (np.prod(1-arr, axis=0))*(len(colors)**0.25))


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
    (Used only by rectangular version now.)
    Choose rotation by maximizing product of in-region segment lengths from anchor.
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
    L = seg_frac * max(abs(span_x), abs(span_y))

    num_samples = 201
    t_vals = np.linspace(-L, L, num_samples)
    center_idx = num_samples // 2

    best_score = -1.0
    best_theta = 0.0

    for k in range(n_angles):
        theta = np.pi * k / n_angles
        ct = np.cos(theta)
        st = np.sin(theta)

        x_s = anchor_x + t_vals * ct
        y_s = anchor_y + t_vals * st

        ix = np.round((x_s - xs[0]) / dx).astype(int)
        iy = np.round((y_s - ys[0]) / dy).astype(int)

        valid = (ix >= 0) & (ix < W) & (iy >= 0) & (iy < H)
        inside = np.zeros_like(valid, dtype=bool)
        inside[valid] = mask[iy[valid], ix[valid]]

        if not inside[center_idx]:
            continue

        len_pos = 0
        for j in range(center_idx, num_samples):
            if inside[j]:
                len_pos += 1
            else:
                break

        len_neg = 0
        for j in range(center_idx, -1, -1):
            if inside[j]:
                len_neg += 1
            else:
                break

        score = float(len_pos * len_neg)
        if score > best_score:
            best_score = score
            best_theta = theta

    if best_score <= 0:
        return 0.0

    deg = np.degrees(best_theta)
    return _normalize_angle_90(deg)


def _arc_angle_for_region(
    mask: np.ndarray,
    circle_band: np.ndarray,
    theta: np.ndarray,
    U: np.ndarray,
    V: np.ndarray,
    n_bins: int = 720,
) -> Optional[float]:
    """
    Robust angle on the main circle for a region.

    Strategy:
      - Take mask & circle_band (pixels near radius R).
      - Bin their angles into `n_bins` bins around [0, 2π).
      - Find the longest contiguous segment of bins (circularly) that are True.
      - Use the center of that segment as the label angle.
      - If no band pixels or degenerate, fall back to angle of visual center.
    """
    if mask is None or not mask.any():
        return None

    arc_mask = mask & circle_band
    if arc_mask.any():
        angs = theta[arc_mask]
        if angs.size > 0:
            # Map to bins
            two_pi = 2.0 * np.pi
            idx = np.floor(angs / two_pi * n_bins).astype(int)
            idx = np.clip(idx, 0, n_bins - 1)
            bins = np.zeros(n_bins, dtype=bool)
            bins[idx] = True

            if bins.any():
                # Find circular segments on duplicated array
                segments: List[Tuple[int, int]] = []
                in_seg = False
                start = 0
                for i in range(n_bins * 2):
                    b = bins[i % n_bins]
                    if b and not in_seg:
                        in_seg = True
                        start = i
                    elif not b and in_seg:
                        end = i
                        segments.append((start, end))
                        in_seg = False
                if in_seg:
                    segments.append((start, n_bins * 2))

                # Choose longest segment (in first turn around the circle)
                best_len = -1
                best_center = None
                for s, e in segments:
                    length = e - s
                    if length <= 0:
                        continue
                    # Only consider segments that actually intersect the base [0, n_bins) once
                    if s >= n_bins and e <= n_bins * 2:
                        # This is the "wrapped" part; skip to avoid duplicates
                        continue
                    if length > best_len:
                        best_len = length
                        best_center = 0.5 * (s + e)

                if best_center is not None and best_len > 0:
                    center_idx = best_center % n_bins
                    angle = two_pi * center_idx / n_bins
                    return float(angle)

    # Fallback: angle of visual center
    pos_vc = _visual_center(mask, U, V)
    if pos_vc is None:
        return None
    return float(np.arctan2(pos_vc[1], pos_vc[0]))


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

def get_curve_linear(
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
    amp = 1-(np.log2(harmonic)/np.log2(max_harmonic*2))
    return height_scale * shaped * amp


# ---------------------------------------------------------------------------
# Main rectangular plotting function
# ---------------------------------------------------------------------------

def sine_diagram(
    values,
    class_names: Sequence[str],
    colors: Optional[Sequence[Union[str, tuple]]] = None,
    outline_colors: Optional[Sequence[Union[str, tuple]]] = None,
    title: Optional[str] = None,
    outfile: Optional[str] = None,
    dpi: int = 600,
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
    last_constant_label_offset: Tuple[float, float] = (0.0, 0.0),
    linewidth: float = 2.0,
) -> Optional[Figure]:
    """
    Rectangular version.
    """
    arr = np.asarray(values, dtype=object)
    if arr.ndim < 1 or arr.ndim > 10:
        raise ValueError("Only N in {1,2,...,10} are supported.")
    N = arr.ndim
    expected_shape = (2,) * N
    if arr.shape != expected_shape:
        raise ValueError(f"values must have shape {expected_shape}, got {arr.shape}.")
    if len(class_names) != N:
        raise ValueError(f"class_names must have length {N}.")
    if N > 10:
        raise ValueError("N>10 not supported.")

    # Default palette for this N
    default_fills, default_outlines = _default_palette_for_n(N)

    # Fill colors for regions
    if colors is None:
        colors = default_fills
    elif len(colors) < N:
        colors = [colors[i % len(colors)] for i in range(N)]
    rgbs = list(map(_rgb, colors))

    # Outline colors for curves + class labels
    if outline_colors is None:
        outline_colors = default_outlines

    if len(outline_colors) < N:
        line_colors = [outline_colors[i % len(outline_colors)] for i in range(N)]
    else:
        line_colors = list(outline_colors)
    label_rgbs = [_rgb(c) for c in line_colors]

    # Color mixing callback (uses fill colors)
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
            color=line_colors[i],
            linewidth=linewidth,
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
        if value is None:
            continue
        if not mask.any():
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

    # Complement (no rotation)
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

                rot = 0.0  # no rotation for complement

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
    label_offset = 0.18 * height_scale
    dx_const, dy_const = last_constant_label_offset
    for i, (name, label_col) in enumerate(zip(class_names, label_rgbs)):
        y_plot = curves[i]
        harmonic = harmonics_for_class[i]

        if harmonic is None:
            if last_max_x is None:
                x_lab = 0.5 * (x_min + x_max)
            else:
                x_lab = last_max_x
            y_lab = -label_offset
            if N > 4:
                x_lab += dx_const
                y_lab += dy_const
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
            y_lab = y_plot[i_min_loc] - label_offset
            if y_lab < y_min + 0.05 * height_scale:
                y_lab = y_min + 0.05 * height_scale

        ax.text(
            x_lab,
            y_lab,
            name,
            ha="center",
            va="top",
            fontsize=class_label_fontsize,
            color=tuple(label_col),
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
    outline_colors: Optional[Sequence[Union[str, tuple]]] = None,
    title: Optional[str] = None,
    outfile: Optional[str] = None,
    dpi: Optional[int] = None,
    color_mixing: Union[str, Callable[[Sequence[np.ndarray]], np.ndarray]] = "average",
    text_color: Optional[str] = "black",
    region_label_fontsize: int = 10,
    class_label_fontsize: int = 12,
    height_scale: float = 2.0,
    include_constant_last: bool = True,
    radius: Optional[float] = 4.0,
    curve_exponent: float = 0.2,
    amp_decay_base: float = 0.8,
    last_constant_label_offset: Tuple[float, float] = (0.0, 0.0),
    region_radial_offset_inside: float = 0.05,
    region_radial_offset_outside: float = 0.05,
    linewidth: float = 2.0,
) -> Optional[Figure]:
    """
    Cogwheel variant of the sine diagram.

    - If radius is None: identical to `sine_diagram(...)` (rectangular).
    - If radius is a positive number:
        * The constant line y=0 becomes a circle of radius `radius`.
        * y>0 maps inside the circle (disc).
        * y<0 maps outside the circle (complement of the disc).

    last_constant_label_offset: (dx, dy) applied in half-plane coordinates
    before mapping for the constant class label when N>4.

    region_radial_offset_inside / outside:
        Control how far labels are from the circle:
          inside:  r = R*(1 - region_radial_offset_inside)
          outside: r = R*(1 + region_radial_offset_outside)
    """
    if radius is None:
        return sine_diagram(
            values,
            class_names,
            colors=colors,
            outline_colors=outline_colors,
            title=title,
            outfile=outfile,
            dpi=dpi if dpi is not None else 600,
            color_mixing=color_mixing,
            text_color=text_color,
            region_label_fontsize=region_label_fontsize,
            class_label_fontsize=class_label_fontsize,
            sample_res_x=900,
            sample_res_y=900,
            height_scale=height_scale,
            include_constant_last=include_constant_last,
            curve_exponent=curve_exponent,
            amp_decay_base=amp_decay_base,
            last_constant_label_offset=last_constant_label_offset,
            linewidth=linewidth,
        )

    arr = np.asarray(values, dtype=object)
    if arr.ndim < 1 or arr.ndim > 10:
        raise ValueError("Only N in {1,2,...,9} are supported.")
    N = arr.ndim
    if dpi is None:
        dpi = 100 * N
    expected_shape = (2,) * N
    if arr.shape != expected_shape:
        raise ValueError(f"values must have shape {expected_shape}, got {arr.shape}.")
    if len(class_names) != N:
        raise ValueError(f"class_names must have length {N}.")
    if N > 10:
        raise ValueError("N>9 not supported.")

    # Default palette for this N
    default_fills, default_outlines = _default_palette_for_n(N)

    # Region fill colors
    if colors is None:
        colors = default_fills
    elif len(colors) < N:
        colors = [colors[i % len(colors)] for i in range(N)]
    rgbs = list(map(_rgb, colors))

    # Outline & label colors
    if outline_colors is None:
        outline_colors = default_outlines

    if len(outline_colors) < N:
        line_colors = [outline_colors[i % len(outline_colors)] for i in range(N)]
    else:
        line_colors = list(outline_colors)
    label_rgbs = [_rgb(c) for c in line_colors]

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
    us = np.linspace(-R_out, R_out, N*150)
    vs = np.linspace(-R_out, R_out, N*150)
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
    fig.set_dpi(dpi)
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
    x_plot = np.linspace(x_min, x_max, 1000*N)
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
            color=line_colors[i],
            linewidth=linewidth,
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

    rho = np.sqrt(U * U + V * V)
    circle_band = np.abs(rho - R) <= (0.03 * R)
    theta = np.mod(np.arctan2(V, U), 2.0 * np.pi)

    # --- Radial region labels ---
    for key, mask in region_masks.items():
        if not mask.any():
            continue
        if key == zeros:
            continue  # complement handled separately

        value = arr[key]
        if value is None:
            continue

        last_bit = key[-1]

        angle_raw = _arc_angle_for_region(mask, circle_band, theta, U, V)
        if angle_raw is None:
            continue

        v_out = np.array([np.cos(angle_raw), np.sin(angle_raw)], float)

        if last_bit == 1:
            r_lab = R * (1.0 - float(region_radial_offset_inside))
        else:
            r_lab = R * (1.0 + float(region_radial_offset_outside))

        u_lab = r_lab * v_out[0]
        v_lab = r_lab * v_out[1]

        deg_raw = np.degrees(angle_raw)
        rot = _normalize_angle_90(deg_raw)
        rot_rad = np.deg2rad(rot)
        v_base = np.array([np.cos(rot_rad), np.sin(rot_rad)], float)

        if last_bit == 1:
            v_circle = v_out
        else:
            v_circle = -v_out

        d = float(np.dot(v_circle, v_base))
        ha = "right" if d >= 0 else "left"
        va = "center"

        if text_color is None:
            rgb = region_rgbs.get(key)
            this_color = _auto_text_color_from_rgb(rgb) if rgb is not None else "black"
        else:
            this_color = text_color

        ax.text(
            u_lab,
            v_lab,
            f"{value}",
            ha=ha,
            va=va,
            fontsize=region_label_fontsize,
            color=this_color,
            zorder=5,
            rotation=rot,
            rotation_mode="anchor",
        )

    # Complement (all zeros) – visual center, no rotation
    comp_mask = region_masks.get(zeros)
    if comp_mask is not None and comp_mask.any():
        val_comp = arr[zeros]
        if val_comp is not None:
            pos = _visual_center_margin(comp_mask, U, V, margin_frac=0.05)
            if pos is not None:
                if text_color is None:
                    this_color = "black"
                else:
                    this_color = text_color

                ax.text(
                    pos[0],
                    pos[1],
                    f"{val_comp}",
                    ha="center",
                    va="center",
                    fontsize=region_label_fontsize,
                    color=this_color,
                    zorder=5,
                    rotation=0.0,
                    rotation_mode="anchor",
                )

    # --- Class labels on cogwheel ---
    label_offset = 0.18 * height_scale
    dx_const, dy_const = last_constant_label_offset

    for i, (name, label_col) in enumerate(zip(class_names, label_rgbs)):
        harmonic = harmonics_for_class[i]

        # First 3 classes: same min-based anchor mapped to disc, tangent-oriented
        if i < 3:
            y_plot = curves[i]
            if harmonic is None:
                if last_max_x is None:
                    x_lab = 0.5 * (x_min + x_max)
                else:
                    x_lab = last_max_x
                y_lab = -label_offset
                if N > 4:
                    x_lab += dx_const
                    y_lab += dy_const
            else:
                dyc = np.diff(y_plot)
                signc = np.sign(dyc)
                i_min_loc = None
                for j in range(1, len(signc)):
                    if signc[j - 1] < 0 and signc[j] > 0:
                        i_min_loc = j
                if i_min_loc is None:
                    i_min_loc = int(np.argmin(y_plot))
                x_lab = x_plot[i_min_loc]
                y_lab = y_plot[i_min_loc] - label_offset
                if y_lab < y_min + 0.05 * height_scale:
                    y_lab = y_min + 0.05 * height_scale

            u_lab_arr, v_lab_arr = _halfplane_to_disc(
                np.array([x_lab]),
                np.array([y_lab]),
                R,
                y_min,
                y_max,
            )
            u_lab = float(u_lab_arr[0])
            v_lab = float(v_lab_arr[0])

            theta_lab = np.arctan2(v_lab, u_lab)
            tangent_angle_deg = np.degrees(theta_lab + np.pi / 2.0)
            rot_cls = _normalize_angle_90(tangent_angle_deg)

            ax.text(
                u_lab,
                v_lab,
                name,
                ha="center",
                va="top",
                fontsize=class_label_fontsize,
                color=tuple(label_col),
                fontweight="bold",
                rotation=rot_cls,
                rotation_mode="anchor",
                zorder=6,
            )
            continue

        # From 4th class onward (i >= 3): radial label placement

        if harmonic is not None:
            # Anchor from last local minimum in half-plane, then mapped outwards
            y_plot = curves[i]
            dyc = np.diff(y_plot)
            signc = np.sign(dyc)
            i_min = None
            for j in range(1, len(signc)):
                if signc[j - 1] < 0 and signc[j] > 0:
                    i_min = j
            if i_min is None:
                i_min = int(np.argmin(y_plot))

            x_anchor = x_plot[i_min]
            y_anchor = y_plot[i_min]

            u_anchor_arr, v_anchor_arr = _halfplane_to_disc(
                np.array([x_anchor]),
                np.array([y_anchor]),
                R,
                y_min,
                y_max,
            )
            u_anchor = float(u_anchor_arr[0])
            v_anchor = float(v_anchor_arr[0])

            angle_anchor = float(np.arctan2(v_anchor, u_anchor))
            v_out = np.array([np.cos(angle_anchor), np.sin(angle_anchor)], float)

            r_anchor = float(np.sqrt(u_anchor * u_anchor + v_anchor * v_anchor))
            r_lab = r_anchor + float(region_radial_offset_outside) * R

            u_lab = r_lab * v_out[0]
            v_lab = r_lab * v_out[1]

            deg_raw = np.degrees(angle_anchor)
            rot_cls = _normalize_angle_90(deg_raw)
            rot_rad = np.deg2rad(rot_cls)
            v_base = np.array([np.cos(rot_rad), np.sin(rot_rad)], float)

            v_circle = -v_out  # circle lies inward of label
            d = float(np.dot(v_circle, v_base))
            ha = "right" if d >= 0 else "left"
            va = "center"

        else:
            # Constant (infinity) class: anchor via exclusive-region arc bisector
            key_excl = tuple(1 if j == i else 0 for j in range(N))
            mask_excl = region_masks.get(key_excl)
            angle_anchor = _arc_angle_for_region(mask_excl, circle_band, theta, U, V)
            if angle_anchor is None:
                angle_anchor = 0.0

            v_out = np.array([np.cos(angle_anchor), np.sin(angle_anchor)], float)
            r_lab = R * (1.0 + float(region_radial_offset_outside))

            u_lab = r_lab * v_out[0]
            v_lab = r_lab * v_out[1]

            deg_raw = np.degrees(angle_anchor)
            rot_cls = _normalize_angle_90(deg_raw)
            rot_rad = np.deg2rad(rot_cls)
            v_base = np.array([np.cos(rot_rad), np.sin(rot_rad)], float)

            v_circle = -v_out
            d = float(np.dot(v_circle, v_base))
            ha = "right" if d >= 0 else "left"
            va = "center"

        ax.text(
            u_lab,
            v_lab,
            name,
            ha=ha,
            va=va,
            fontsize=class_label_fontsize,
            color=tuple(label_col),
            fontweight="bold",
            rotation=rot_cls,
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
    For testing, the complement (all zeros) is labeled None.
    """
    letters = [chr(ord("A") + i) for i in range(N)]
    shape = (2,) * N
    arr = np.empty(shape, dtype=object)
    for idx in np.ndindex(shape):
        s = "".join(letters[i] for i, bit in enumerate(idx) if bit)
        arr[idx] = s
    arr[(0,) * N] = None
    return arr


if __name__ == "__main__":
    greek_names = [
        "Alpha", "Beta", "Gamma", "Delta", "Epsilon",
        "Zeta", "Eta", "Theta", "Iota", "Kappa"
    ]

    # # Rectangular version (N=6..7) using default per-N palettes
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

    # Cogwheel version with your standard defaults (including radius=4)
    fontsizes = {
        2: (16, 20),
        3: (14, 18),
        4: (12, 14),
        5: (11, 13),
        6: (9, 12),
        7: (6, 10),
        8: (4, 6),
        9: (2, 3),
        10: (0.5, 1),
    }
    linewidths = {
        2: 4.0,
        3: 3.5,
        4: 3.0,
        5: 2.5,
        6: 2.0,
        7: 1.5,
        8: 1.2,
        9: 0.8,
        10: 0.3
    }
    for N in range(2, 11):
        print(f"Generating cogwheel diagram for N={N}...")
        values = _make_demo_values(N)
        class_names = greek_names[:N]
        class_names = ["" for _ in range(N)]

        outfile = f"cogwheel_N{N}_r4.png"
        cogwheel(
            values,
            class_names,
            outfile=outfile,
            height_scale=2.0,
            include_constant_last=True,
            #color_mixing="average",
            region_label_fontsize=fontsizes[N][0],
            class_label_fontsize=fontsizes[N][1],
            radius=4.0,
            text_color="black",
            curve_exponent=0.33,
            amp_decay_base=0.8,
            region_radial_offset_inside=0.02,
            region_radial_offset_outside=0.02,
            linewidth=linewidths[N],
        )

    for N in range(6, 11):
        print(f"Generating cogwheel diagram for N={N}...")
        shape = (2,) * N
        values = np.empty(shape, dtype=object)
        class_names = ["" for _ in range(N)]

        outfile = f"cogwheel_N{N}.png"
        cogwheel(
            values,
            class_names,
            outfile=outfile,
            height_scale=2.0,
            include_constant_last=True,
            #color_mixing="average",
            region_label_fontsize=fontsizes[N][0],
            class_label_fontsize=fontsizes[N][1],
            radius=1.0,
            text_color="black",
            curve_exponent=0.33,
            amp_decay_base=0.75,
            region_radial_offset_inside=0.02,
            region_radial_offset_outside=0.02,
            linewidth=linewidths[N],
        )