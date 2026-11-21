import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

from utils.netcdf_utils import get_variable_catalog, get_variable


def render_spectral_explorer(dataset):
    """Extract and visualize a pixel spectrum from a 3D RAD variable."""

    st.subheader("EMIT Spectral Explorer")

    catalog = get_variable_catalog(dataset)

    # Find numeric 3D variables
    spectral_candidates = []

    for item in catalog:
        try:
            dtype = np.dtype(item["dtype"])

            if (
                len(item["shape"]) == 3
                and np.issubdtype(dtype, np.number)
            ):
                spectral_candidates.append(item)

        except (TypeError, ValueError):
            continue

    if not spectral_candidates:
        st.warning(
            "No numeric 3D variables were found. "
            "Select a suitable 3D RAD variable after inspecting its metadata."
        )
        return

    # Variable selection
    variable_options = {
        f'{item["group"]} | {item["variable"]} | {item["shape"]}': item
        for item in spectral_candidates
    }

    selected_label = st.selectbox(
        "Select 3D spectral variable",
        list(variable_options.keys()),
        key="spectral_variable_selection"
    )

    selected_item = variable_options[selected_label]

    variable = get_variable(
        dataset,
        selected_item["variable"],
        selected_item["group"]
    )

    st.write("Dimensions:", variable.dimensions)
    st.write("Shape:", variable.shape)

    # Choose the spectral axis instead of assuming its position
    axis_options = [
        f"Axis {i} — {variable.dimensions[i]} — {variable.shape[i]} elements"
        for i in range(variable.ndim)
    ]

    suggested_axis = next(
        (
            i for i, dim in enumerate(variable.dimensions)
            if any(term in dim.lower()
                   for term in ["band", "spect", "wave"])
        ),
        variable.ndim - 1
    )

    spectral_axis = st.selectbox(
        "Select spectral / band axis",
        options=list(range(variable.ndim)),
        format_func=lambda i: axis_options[i],
        index=suggested_axis,
        key="spectral_axis_selection"
    )

    spatial_axes = [
        axis for axis in range(variable.ndim)
        if axis != spectral_axis
    ]

    st.markdown("### Select Pixel")

    pixel_indices = {}

    for axis in spatial_axes:
        dim_name = variable.dimensions[axis]
        dim_size = variable.shape[axis]

        pixel_indices[axis] = st.slider(
            f"Index along {dim_name} (Axis {axis})",
            min_value=0,
            max_value=dim_size - 1,
            value=dim_size // 2,
            key=f"spectral_pixel_axis_{axis}"
        )

    # Extract only one pixel's spectrum
    selection = []

    for axis in range(variable.ndim):
        if axis == spectral_axis:
            selection.append(slice(None))
        else:
            selection.append(pixel_indices[axis])

    spectrum = variable[tuple(selection)]

    spectrum = np.ma.filled(
        np.ma.asarray(spectrum, dtype=float),
        np.nan
    )

    # Display spectrum
    band_indices = np.arange(len(spectrum))

    st.markdown("### Pixel Spectrum")

    fig, ax = plt.subplots(figsize=(11, 5))

    ax.plot(band_indices, spectrum)

    ax.set_xlabel("Band Index")
    ax.set_ylabel("Radiance")
    ax.set_title("EMIT Pixel Spectral Signature")
    ax.grid(True)

    st.pyplot(fig)
    plt.close(fig)

    # Statistics
    valid_values = spectrum[np.isfinite(spectrum)]

    if valid_values.size > 0:
        col1, col2, col3 = st.columns(3)

        col1.metric("Valid Bands", int(valid_values.size))
        col2.metric("Minimum Radiance", f"{np.min(valid_values):.5f}")
        col3.metric("Maximum Radiance", f"{np.max(valid_values):.5f}")

    # Numerical data
    with st.expander("View extracted spectral values"):

        st.dataframe(
            {
                "Band Index": band_indices,
                "Radiance": spectrum
            },
            use_container_width=True
        )

        csv_data = (
            "Band Index,Radiance\n"
            + "\n".join(
                f"{i},{v}" for i, v in zip(band_indices, spectrum)
            )
        )

        st.download_button(
            "Download spectrum as CSV",
            data=csv_data,
            file_name="emit_pixel_spectrum.csv",
            mime="text/csv"
        )

    st.caption(
        "This extracts a spectrum for one selected pixel. "
        "The full hyperspectral cube is not loaded into memory."
    )