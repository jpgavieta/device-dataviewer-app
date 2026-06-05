import numpy as np
import pandas as pd
import hvplot.pandas  # noqa: F401  — registers .hvplot accessor
import geoviews.tile_sources as gvts
from src.utils import get_color

# ============================================================================================================
# Helpers

def _is_continuous(series: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(series) and series.nunique() > 10

def _map_opacity(series: pd.Series) -> pd.Series:
    min_val, max_val = series.min(), series.max()
    if max_val == min_val:
        return pd.Series(0.6, index=series.index)
    return 0.2 + 0.8 * (series - min_val) / (max_val - min_val)

def _jitter(df: pd.DataFrame, scale: float = 0.0001) -> pd.DataFrame: # 10 m
    rng = np.random.default_rng(seed=42)
    df = df.copy()
    df["longitude"] += rng.uniform(-scale, scale, len(df))
    df["latitude"]  += rng.uniform(-scale, scale, len(df))
    return df

# ============================================================================================================
# Top-level builder — returns raw HoloViews overlay, NOT a Panel pane

def build_map(gis_df: pd.DataFrame, layers: list[tuple], title: str = ""):
    base_df = gis_df.dropna(subset=["latitude", "longitude"])
    base_df = base_df[(base_df["latitude"] != 0.0) & (base_df["longitude"] != 0.0)]

    if base_df.empty:
        raise ValueError("No valid GPS coordinates to plot.")

    overlay = gvts.CartoDark()
    points_added = False                          # ← track whether anything was added

    for data_df, color_col in layers:
        df = base_df.copy()
        if data_df is not None and color_col and color_col in data_df.columns:
            df = pd.merge(df, data_df[["datetime", color_col]], on="datetime", how="left")

        if color_col not in df.columns:
            continue

        color      = get_color(color_col)
        df         = _jitter(df)
        hover_cols = [c for c in ["datetime", color_col] if c in df.columns]

        if _is_continuous(df[color_col].dropna()):
            df["_alpha"] = _map_opacity(df[color_col].fillna(df[color_col].min()))
            alpha = "_alpha"
        else:
            alpha = 0.7

        points = df.hvplot.points(
            x="longitude", y="latitude", geo=True,
            color=color, alpha=alpha, size=30,
            hover_cols=hover_cols,
            xaxis="bottom", yaxis="left", xlabel="", ylabel="",
            tools=["hover", "pan", "wheel_zoom"],
            title=title,
            # ← frame_width/frame_height removed
        )
        overlay = overlay * points
        points_added = True

    if not points_added:                          # ← guard: bare tile source = broken render
        raise ValueError("No valid GPS coordinates to plot.")

    return overlay.opts(
        axiswise=False,                           # ← key fix
        frame_width=900,
        frame_height=500,
        title=title,
    )