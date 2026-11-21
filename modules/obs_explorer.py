
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from utils.netcdf_utils import (
    get_variable_catalog,
    get_variable
)


def render_obs_explorer(dataset):

    st.subheader("EMIT OBS Explorer")

    catalog = get_variable_catalog(dataset)

    numeric_items = [
        item for item in catalog
        if np.issubdtype(np.dtype(item["dtype"]), np.number)
    ]

    if not numeric_items:
        st.warning("No numeric variables found.")
        return

    variable_options = {
    f"{item['group']} | {item['variable']} | {item['shape']}": item
    for item in numeric_items
   }

    selected_label = st.selectbox(
        "Select OBS variable",
        list(variable_options.keys())
    )

    selected_item = variable_options[selected_label]

    variable = get_variable(
        dataset,
        selected_item["variable"],
        selected_item["group"]
    )

    st.write("**Variable:**", selected_item["variable"])
    st.write("**Dimensions:**", variable.dimensions)
    st.write("**Shape:**", variable.shape)
    st.write("**Data type:**", variable.dtype)

    st.divider()

    # 3D variable
    if variable.ndim == 3:

        band_index = st.slider(
            "Select parameter index",
            min_value=0,
            max_value=variable.shape[2] - 1,
            value=0
        )

        data = variable[
            :20,
            :20,
            band_index
        ]

        data = np.ma.filled(
            data,
            np.nan
        )

        st.markdown("### Data Preview")

        st.dataframe(
            pd.DataFrame(data),
            use_container_width=True
        )

        # Visualization
        st.markdown("### Parameter Visualization")

        display_data = variable[
            :,
            :,
            band_index
        ]

        display_data = np.ma.filled(
            display_data,
            np.nan
        )

        row_step = max(
            1,
            display_data.shape[0] // 500
        )

        col_step = max(
            1,
            display_data.shape[1] // 500
        )

        display_data = display_data[
            ::row_step,
            ::col_step
        ]

        fig, ax = plt.subplots(figsize=(10, 6))

        im = ax.imshow(
            display_data,
            cmap="viridis",
            aspect="auto"
        )

        ax.set_title(
            f"{selected_item['variable']} - Parameter {band_index}"
        )

        ax.set_xlabel("Crosstrack")
        ax.set_ylabel("Downtrack")

        fig.colorbar(im, ax=ax)

        st.pyplot(fig)

        plt.close(fig)

    # 2D variable
    elif variable.ndim == 2:

        data = variable[:20, :20]

        data = np.ma.filled(
            data,
            np.nan
        )

        st.markdown("### Data Preview")

        st.dataframe(
            pd.DataFrame(data),
            use_container_width=True
        )

        display_data = variable[:, :]

        display_data = np.ma.filled(
            display_data,
            np.nan
        )

        row_step = max(
            1,
            display_data.shape[0] // 500
        )

        col_step = max(
            1,
            display_data.shape[1] // 500
        )

        display_data = display_data[
            ::row_step,
            ::col_step
        ]

        fig, ax = plt.subplots(figsize=(10, 6))

        im = ax.imshow(
            display_data,
            cmap="viridis",
            aspect="auto"
        )

        ax.set_title(selected_item["variable"])

        fig.colorbar(im, ax=ax)

        st.pyplot(fig)

        plt.close(fig)

    # 1D variable
    elif variable.ndim == 1:

        data = variable[:]

        st.write(data)

    # Other structures
    else:

        st.info(
            f"Variable has {variable.ndim} dimensions."
        )

    # Numerical sample
    with st.expander("View numerical sample"):

        if variable.ndim == 0:
            sample = variable[()]

        elif variable.ndim == 1:
            sample = variable[:20]

        elif variable.ndim == 2:
            sample = variable[:10, :10]

        elif variable.ndim == 3:
            sample = variable[:10, :10, 0]

        else:
            sample = variable[
                tuple(
                    slice(0, min(5, size))
                    for size in variable.shape
                )
            ]

        sample = np.ma.filled(
            sample,
            np.nan
        )

        st.write(sample)
