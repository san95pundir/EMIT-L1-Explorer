
from pathlib import Path


def classify_emit_file(file_path):
    """Classify EMIT NetCDF file as RAD, OBS, or OTHER."""

    filename = Path(file_path).name.upper()

    if "RAD" in filename:
        return "RAD"

    if "OBS" in filename:
        return "OBS"

    return "OTHER"


def get_file_size_mb(file_path):
    """Return file size in MB."""

    file_path = Path(file_path)

    if not file_path.exists():
        return 0

    return round(file_path.stat().st_size / (1024 * 1024), 2)


def scan_emit_files(folder_path):
    """Scan a folder for EMIT NetCDF files."""

    folder_path = Path(folder_path)

    if not folder_path.exists():
        return []

    files = list(folder_path.glob("*.nc"))

    file_info = []

    for file_path in files:
        file_info.append({
            "name": file_path.name,
            "path": str(file_path),
            "type": classify_emit_file(file_path),
            "size_mb": get_file_size_mb(file_path)
        })

    return file_info


def get_file_summary(files):
    """Generate summary of scanned EMIT files."""

    total_files = len(files)

    rad_files = sum(
        1 for file in files
        if file["type"] == "RAD"
    )

    obs_files = sum(
        1 for file in files
        if file["type"] == "OBS"
    )

    other_files = total_files - rad_files - obs_files

    total_size = sum(
        file["size_mb"] for file in files
    )

    return {
        "total_files": total_files,
        "rad_files": rad_files,
        "obs_files": obs_files,
        "other_files": other_files,
        "total_size_mb": round(total_size, 2)
    }
