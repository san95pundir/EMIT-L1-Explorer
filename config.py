from pathlib import Path

# EMIT source data (original files remain untouched)
EMIT_DATA_DIR = Path(r"E:\EMIT_L1")

# Framework root directory
PROJECT_DIR = Path(__file__).resolve().parent

# Output directories (stored on laptop)
OUTPUT_DIR = PROJECT_DIR / "outputs"
EXPORT_DIR = OUTPUT_DIR / "exports"
PLOT_DIR = OUTPUT_DIR / "plots"

# Ensure output directories exist
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
PLOT_DIR.mkdir(parents=True, exist_ok=True)