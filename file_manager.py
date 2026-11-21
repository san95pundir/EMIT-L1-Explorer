from pathlib import Path
import pandas as pd

from config import EMIT_DATA_DIR


def classify_emit_file(filepath):
    """Classify EMIT files based on filename."""
    name = filepath.name.upper()

    if "RAD" in name:
        return "RAD"
    elif "OBS" in name:
        return "OBS"
    else:
        return "OTHER"


def get_file_size_mb(filepath):
    """Return file size in MB."""
    return round(filepath.stat().st_size / (1024 * 1024), 2)


def scan_emit_files(folder=None):
    """
    Scan the EMIT data directory for NetCDF files.
    This scans file metadata only, not the contents of large arrays.
    """
    folder = Path(folder) if folder else EMIT_DATA_DIR

    if not folder.exists():
        return pd.DataFrame(), f"Folder does not exist: {folder}"

    files = list(folder.rglob("*.nc"))

    if not files:
        return pd.DataFrame(), "No NetCDF (.nc) files found."

    records = []

    for filepath in files:
        records.append({
            "File Name": filepath.name,
            "File Type": classify_emit_file(filepath),
            "Size (MB)": get_file_size_mb(filepath),
            "Full Path": str(filepath),
        })

    df = pd.DataFrame(records)

    # Display RAD and OBS files first
    order = {"RAD": 0, "OBS": 1, "OTHER": 2}
    df["_order"] = df["File Type"].map(order)
    df = df.sort_values(["_order", "File Name"]).drop(columns="_order")
    df = df.reset_index(drop=True)

    return df, None


def get_file_summary(df):
    """Return summary statistics for detected files."""
    if df.empty:
        return {
            "Total Files": 0,
            "RAD Files": 0,
            "OBS Files": 0,
            "Other Files": 0,
            "Total Size (MB)": 0,
        }

    return {
        "Total Files": len(df),
        "RAD Files": int((df["File Type"] == "RAD").sum()),
        "OBS Files": int((df["File Type"] == "OBS").sum()),
        "Other Files": int((df["File Type"] == "OTHER").sum()),
        "Total Size (MB)": round(df["Size (MB)"].sum(), 2),
    }