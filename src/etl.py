import pandas as pd
from io import StringIO

from src.parsers import atmotube, ponyopi


# ============================================================================================================
# Device Registry

PARSER_REGISTRY = {
    "Atmotube Pro/Pro 2": atmotube,
    "PonyoPi": ponyopi,
}

AVAILABLE_DEVICES = list(PARSER_REGISTRY.keys())


# ============================================================================================================
# ETL Functions

def load_csv(file_bytes: bytes) -> pd.DataFrame:
    """Decode uploaded CSV bytes into a raw DataFrame."""
    return pd.read_csv(StringIO(file_bytes.decode("utf-8", errors="replace")))

def apply_parser(df: pd.DataFrame, device_type: str) -> dict:
    """Apply the device-specific parser to a raw DataFrame.
    
    Parameters
    ----------
    df : pd.DataFrame
        Raw DataFrame from load_csv.
    device_type : str
        Device name selected from the dashboard dropdown.

    Returns
    -------
    dict — always includes "all" (merged DataFrame) plus device-specific keys.
    """
    return PARSER_REGISTRY[device_type].parse(df)
        # 1. PARSER_REGISTRY[device_type] --> gets the parser module for the selected device
        # 2. `.parse` --> calls and applies the selected module's parse() function to the raw df

def get_data(file_bytes: bytes, device_type: str) -> dict:
    """Load, parse, and return all DataFrames with their available variables for a given device.

    Parameters
    ----------
    file_bytes : bytes
        Raw CSV bytes from the Panel FileInput widget.
    device_type : str
        Device name selected from the dashboard dropdown.

    Returns
    -------
    dict with two keys:
        "gis"  : pd.DataFrame          — always loaded, used for map
        "data" : dict                   — df key → { "df": DataFrame, "vars": list of columns }
    """
    df   = load_csv(file_bytes)
    dfs  = apply_parser(df, device_type)
    return {
        "gis": dfs["gis"],
        "data": {
            df_key: {
                "df":   df,
                "vars": [col for col in df.columns if col != "datetime"]
            }
            for df_key, df in dfs.items()
            if df_key not in ("gis", "all")
        }
    }

# Example usage:
# data = get_data(file_bytes, device_type="Atmotube Pro/Pro 2")
# data["gis"]              --> GIS DataFrame, always available for map
# data["data"]["pm"]["df"] --> PM DataFrame
# data["data"]["pm"]["vars"] --> ['pm2_5_ugm3_atm', 'pm10_ugm3_atm', ...]

def clean_data(data: dict, selected: dict[str, list[str]]) -> dict:
    all_selected_cols = [col for cols in selected.values() for col in cols]
    if not all_selected_cols:
        return data

    merged = None
    for df_key, cols in selected.items():
        if not cols:
            continue
        df = data[df_key]["df"][["datetime"] + cols]
        merged = df if merged is None else pd.merge(merged, df, on="datetime", how="outer")

    if merged is None:
        return data

    valid_datetimes = set(merged.dropna(subset=all_selected_cols)["datetime"])

    cleaned = {}
    for df_key, contents in data.items():
        df = contents["df"]
        clean_df = df[df["datetime"].isin(valid_datetimes)].copy()
        # ← drop any remaining NaNs in all columns, not just selected
        clean_df = clean_df.dropna()
        cleaned[df_key] = {
            "df":   clean_df,
            "vars": contents["vars"]
        }
    return cleaned

# Example usage:
# selected = {"pm": ["pm2_5_ugm3_atm", "pm10_ugm3_atm"], "weather": ["temp_c"]}
# cleaned  = clean_data(data, selected)
# cleaned["pm"]["df"]   --> PM DataFrame with no missing rows for selected vars