
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

from utils.netcdf_utils import (
    get_variable_catalog,
    get_variable
)


def render_spectral_explorer(dataset):

    st.subheader("EMIT Spectral Explorer")

    catalog = get_variable_catalog(dataset)

    radiance_items = [
        item for item in catalog
        if "radiance" in item["variable"].lower()
        and len(item["shape"]) == 3
    ]

    if not radiance_items:

        st.warning(
            "No 3D radiance variable found in this dataset."
        )

        return

    variable_options = {
        f'{item["group"]} | {item["variable"]} | {item["shape"]}': item
        for item in radiance_items
    }

    selected_label = st.selectbox(
        "Select radiance variable",
        list(variable_options.keys())
    )

    selected_item = variable_options[selected_label]

    variable = get_variable(
        dataset,
        selected_item["variable"],
        selected_item["group"]
    )

    dimensions = variable.dimensions

    band_axis = next(
        (
            i for i, dim in enumerate(dimensions)
            if "band" in dim.lower()
        ),
        None
    )

    if band_axis is None:

        st.warning(
            "Band dimension could not be identified."
        )

        return

    spatial_axes = [
        i for i in range(variable.ndim)
        if i != band_axis
    ]

    rows = variable.shape[spatial_axes[0]]
    cols = variable.shape[spatial_axes[1]]
    bands = variable.shape[band_axis]

    st.write("**Shape:**", variable.shape)
    st.write("**Dimensions:**", variable.dimensions)

    st.divider()

    # Pixel selection
    st.markdown("### Select Pixel")

    row_index = st.slider(
        "Downtrack / Row",
        min_value=0,
        max_value=rows - 1,
        value=rows // 2
    )

    col_index = st.slider(
        "Crosstrack / Column",
        min_value=0,
        max_value=cols - 1,
        value=cols // 2
    )

    # Extract spectrum from selected pixel
    selection = [0] * variable.ndim

    selection[spatial_axes[0]] = row_index
    selection[spatial_axes[1]] = col_index
    selection[band_axis] = slice(None)

    spectrum = variable[tuple(selection)]

    spectrum = np.ma.filled(
        spectrum,
        np.nan
    )

    spectrum = np.asarray(
        spectrum,
        dtype=np.float32
    )

    st.write(
        f"Selected pixel: Row {row_index}, "
        f"Column {col_index}"
    )

    st.divider()

    # Spectral plot
    st.markdown("### Pixel Spectrum")

    band_indices = np.arange(len(spectrum))

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(
        band_indices,
        spectrum
    )

    ax.set_title(
        f"Radiance Spectrum - Pixel ({row_index}, {col_index})"
    )

    ax.set_xlabel("Band Index")
    ax.set_ylabel("Radiance")

    ax.grid(True)

    st.pyplot(fig)

    plt.close(fig)

    # Numerical values
    with st.expander("View spectral values"):

        st.write({
            "Selected Row": row_index,
            "Selected Column": col_index,
            "Number of Bands": len(spectrum)
        })

        st.dataframe(
            {
                "Band Index": band_indices,
                "Radiance": spectrum
            },
            use_container_width=True
        )
