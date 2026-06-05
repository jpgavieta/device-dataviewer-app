import pandas as pd
import hvplot.pandas  # noqa
import holoviews as hv
import panel as pn

hv.extension('bokeh')

# ============================================================================================================

def build_covariance(df: pd.DataFrame, columns: list):
    """
    Build a correlation/covariance heatmap for selected columns.

    Parameters
    ----------
    df      : pd.DataFrame — data source
    columns : list of str  — numeric columns to correlate

    Returns
    -------
    holoviews heatmap object
    """
    columns = [c for c in columns if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
    if len(columns) < 2:
        return hv.Text(0, 0, 'Select at least 2 numeric columns').opts(xaxis=None, yaxis=None)

    corr = df[columns].corr().round(2)

    return corr.hvplot.heatmap(
        cmap='coolwarm',
        clim=(-1, 1),
        colorbar=True,
        xaxis='top',
        rot=45,
        responsive=True,
        min_height=250,
        title='Correlation matrix',
    ).opts(toolbar='above')


def build_histogram(df: pd.DataFrame, columns: list):
    """
    Build overlaid histograms over time for selected columns.

    Parameters
    ----------
    df      : pd.DataFrame — data source, must have 'datetime' column
    columns : list of str  — numeric columns to plot

    Returns
    -------
    holoviews Overlay object
    """
    columns = [c for c in columns if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
    if not columns:
        return hv.Text(0, 0, 'No numeric columns selected').opts(xaxis=None, yaxis=None)

    plots = [
        df[col].dropna().hvplot.hist(
            bins=30,
            alpha=0.5,
            label=col,
            responsive=True,
            min_height=250,
        )
        for col in columns
    ]

    return hv.Overlay(plots).opts(
        hv.opts.Overlay(
            legend_position='top_right',
            toolbar='above',
            responsive=True,
            min_height=250,
            title='Histogram',
        )
    )


def build_heatmap_tabs(df: pd.DataFrame, columns: list):
    """
    Build a tabbed Panel with covariance heatmap and histogram.

    Parameters
    ----------
    df      : pd.DataFrame — filtered data source
    columns : list of str  — selected columns

    Returns
    -------
    pn.Tabs object
    """
    return pn.Tabs(
        ('Covariance',  pn.pane.HoloViews(build_covariance(df, columns),  sizing_mode='stretch_both')),
        ('Histogram',   pn.pane.HoloViews(build_histogram(df, columns),   sizing_mode='stretch_both')),
    )

# Example: build_heatmap_tabs(dfs["pm"], columns=["pm2_5_ugm3_atm", "temp_c"])