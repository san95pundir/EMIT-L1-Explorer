
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

from utils.netcdf_utils import (
    get_variable_catalog,
    get_variable
)


def render_rad_explorer(dataset):

    st.subheader("EMIT RAD Explorer")

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
        "Select RAD variable",
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

    # 3D radiance data
    if variable.ndim == 3:

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
                "Band dimension could not be identified "
                "automatically."
            )
            return

        band_count = variable.shape[band_axis]

        band_index = st.slider(
            "Select band index",
            min_value=0,
            max_value=band_count - 1,
            value=0
        )

        # Read only selected band
        selection = [slice(None)] * variable.ndim
        selection[band_axis] = band_index

        image_data = variable[tuple(selection)]

        image_data = np.ma.filled(
            image_data,
            np.nan
        )

        image_data = np.asarray(
            image_data,
            dtype=np.float32
        )

        # Display downsampled image
        row_step = max(
            1,
            image_data.shape[0] // 500
        )

        col_step = max(
            1,
            image_data.shape[1] // 500
        )

        display_data = image_data[
            ::row_step,
            ::col_step
        ]

        # Radiance image
        st.markdown("### Radiance Image")

        fig, ax = plt.subplots(figsize=(10, 6))

        im = ax.imshow(
            display_data,
            cmap="viridis",
            aspect="auto"
        )

        ax.set_title(
            f"Radiance - Band {band_index}"
        )

        ax.set_xlabel("Crosstrack")
        ax.set_ylabel("Downtrack")

        fig.colorbar(
            im,
            ax=ax,
            label="Radiance"
        )

        st.pyplot(fig)

        plt.close(fig)

        st.caption(
            "The selected band is read from the dataset. "
            "The displayed image is downsampled for visualization."
        )

        # Histogram
        st.markdown("### Radiance Histogram")

        valid_data = image_data[
            np.isfinite(image_data)
        ]

        if valid_data.size > 0:

            fig, ax = plt.subplots(figsize=(8, 4))

            ax.hist(
                valid_data,
                bins=50
            )

            ax.set_title(
                f"Radiance Distribution - Band {band_index}"
            )

            ax.set_xlabel("Radiance")
            ax.set_ylabel("Frequency")

            ax.grid(True)

            st.pyplot(fig)

            plt.close(fig)

        # Numerical sample
        with st.expander("View numerical sample"):

            sample = image_data[:10, :10]

            st.write(sample)

    # 2D variable
    elif variable.ndim == 2:

        image_data = variable[:, :]

        image_data = np.ma.filled(
            image_data,
            np.nan
        )

        image_data = np.asarray(
            image_data,
            dtype=np.float32
        )

        row_step = max(
            1,
            image_data.shape[0] // 500
        )

        col_step = max(
            1,
            image_data.shape[1] // 500
        )

        display_data = image_data[
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
        ax.set_xlabel("Column")
        ax.set_ylabel("Row")

        fig.colorbar(im, ax=ax)

        st.pyplot(fig)

        plt.close(fig)

    # 1D variable
    elif variable.ndim == 1:

        data = variable[:]

        data = np.ma.filled(
            data,
            np.nan
        )

        fig, ax = plt.subplots(figsize=(10, 4))

        ax.plot(data)

        ax.set_title(selected_item["variable"])
        ax.set_xlabel("Index")
        ax.set_ylabel("Value")

        ax.grid(True)

        st.pyplot(fig)

        plt.close(fig)

    else:

        st.info(
            f"Selected variable has {variable.ndim} dimensions. "
            "Automatic visualization is not available."
        )
