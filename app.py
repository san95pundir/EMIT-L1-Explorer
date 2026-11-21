
import streamlit as st
from pathlib import Path

from utils.netcdf_utils import open_netcdf, close_netcdf
from modules.metadata_explorer import render_metadata_explorer
from modules.rad_explorer import render_rad_explorer
from modules.obs_explorer import render_obs_explorer
from modules.spectral_explorer import render_spectral_explorer

st.set_page_config(
    page_title="EMIT L1 Framework",
    page_icon="🛰️",
    layout="wide"
)

st.title("🛰️ EMIT L1 Data Exploration Framework")
st.caption("Interactive exploration of EMIT Level-1 RAD and OBS NetCDF files")

# --------------------------------------------------
# FILE SELECTION
# --------------------------------------------------

st.sidebar.header("Select EMIT File")

emit_folder = Path(r"E:\EMIT_L1")

if not emit_folder.exists():
    st.sidebar.error("EMIT data directory not found.")
    st.stop()

nc_files = list(emit_folder.glob("*.nc"))

selected_file = st.sidebar.selectbox(
    "Choose an EMIT NetCDF file",
    nc_files,
    format_func=lambda x: x.name
)

if selected_file is None:
    st.info("No NetCDF files found.")
    st.stop()

file_name = selected_file.name

st.sidebar.success(f"Selected: {file_name}")

file_type = "RAD" if "RAD" in file_name.upper() else (
    "OBS" if "OBS" in file_name.upper() else "UNKNOWN"
)

st.sidebar.write("Detected File Type:", file_type)

# --------------------------------------------------
# LOAD SELECTED FILE
# --------------------------------------------------

dataset = open_netcdf(selected_file)

# --------------------------------------------------
# NAVIGATION
# --------------------------------------------------

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Metadata Explorer",
        "RAD Explorer",
        "OBS Explorer",
        "Spectral Explorer"
    ]
)

# --------------------------------------------------
# HOME
# --------------------------------------------------

if page == "Home":

    st.header("File Overview")

    col1, col2 = st.columns(2)

    col1.metric("Selected File", file_name)
    col2.metric("File Type", file_type)

    st.markdown("### File Information")

    st.write("**File Name:**", file_name)
    st.write("**File Type:**", file_type)
    st.write(
        "**File Size:**",
        f"{selected_file.stat().st_size / (1024 * 1024):.2f} MB"
    )

    st.markdown("""
    ### Available Exploration

    Use the sidebar to explore the selected file.

    | Module | Function |
    |---|---|
    | Metadata Explorer | File structure, variables, dimensions, attributes |
    | RAD Explorer | Radiance visualization |
    | OBS Explorer | Observation data exploration |
    | Spectral Explorer | Pixel spectral extraction |
    """)

# --------------------------------------------------
# METADATA EXPLORER
# --------------------------------------------------

elif page == "Metadata Explorer":

    render_metadata_explorer(dataset)

# --------------------------------------------------
# RAD EXPLORER
# --------------------------------------------------

elif page == "RAD Explorer":

    if file_type != "RAD":
        st.warning("Please select an EMIT RAD file to use the RAD Explorer.")
    else:
        render_rad_explorer(dataset)

# --------------------------------------------------
# OBS EXPLORER
# --------------------------------------------------

elif page == "OBS Explorer":

    if file_type != "OBS":
        st.warning("Please select an EMIT OBS file to use the OBS Explorer.")
    else:
        render_obs_explorer(dataset)

# --------------------------------------------------
# SPECTRAL EXPLORER
# --------------------------------------------------

elif page == "Spectral Explorer":

    if file_type != "RAD":
        st.warning("Please select an EMIT RAD file for spectral exploration.")
    else:
        render_spectral_explorer(dataset)

# --------------------------------------------------
# CLOSE FILE
# --------------------------------------------------

close_netcdf(dataset)
