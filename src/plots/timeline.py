import pandas as pd
import hvplot.pandas  # noqa: F401  — registers .hvplot accessor
import holoviews as hv
from src.utils import get_color

# ============================================================================================================
# Top-level builder — returns raw HoloViews overlay, NOT a Panel pane

def build_timeline(layers: list[tuple], title: str = "") -> hv.Overlay | None:
    curves = []

    for data_df, color_col in layers:
        if data_df is None or color_col not in data_df.columns:
            continue

        df = data_df[["datetime", color_col]].dropna(subset=[color_col]).copy()
        if df.empty:
            continue

        curve = df.hvplot.line(
            x="datetime", y=color_col,
            color=get_color(color_col),
            line_width=1.5, alpha=0.9,
            label=color_col,
            frame_width=900, frame_height=250,
            xaxis="bottom", yaxis="left", xlabel="", ylabel="",
            grid=True,
            tools=["hover", "pan", "wheel_zoom"],
            title=title,
        )
        curves.append(curve)

    if not curves:
        return None

    return hv.Overlay(curves).opts(
        show_legend=False,
        frame_width=900, frame_height=250,
        title=title, axiswise=True,
    )