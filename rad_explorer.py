
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

from utils.netcdf_utils import get_variable_catalog, get_variable


def find_wavelength_variable(dataset):
    """Search NetCDF variables/groups for wavelength information."""

    candidates = [
        "wavelength",
        "wavelengths",
        "band_wavelength",
        "band_wavelengths",
        "center_wavelength",
        "center_wavelengths"
    ]

    def search_group(group):
        for name in group.variables:
            if name.lower() in candidates:
                return group.variables[name]

        for group_name in group.groups:
            result = search_group(group.groups[group_name])
            if result is not None:
                return result

        return None

    return search_group(dataset)


def render_rad_explorer(dataset):
    """Interactive memory-conscious EMIT RAD explorer."""

    st.subheader("EMIT RAD Explorer")

    catalog = get_variable_catalog(dataset)

    # Filter numeric variables
    numeric_items = [
        item for item in catalog
        if np.issubdtype(np.dtype(item["dtype"]), np.number)
    ]

    if not numeric_items:
        st.warning("No numeric variables found.")
        return

    # Build variable labels
    variable_options = {
        f'{item["group"]} | {item["variable"]} | {item["shape"]}': item
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

    # --------------------------------------------------
    # 3D DATA
    # --------------------------------------------------

    if variable.ndim == 3:

        # Identify band axis using dimension names
        band_axis = None

        for i, dim in enumerate(variable.dimensions):
            if "band" in dim.lower():
                band_axis = i
                break

        # Fallback: assume the smallest dimension is the band axis
        if band_axis is None:
            band_axis = int(np.argmin(variable.shape))

        band_count = variable.shape[band_axis]

        band_index = st.slider(
            "Select band index",
            min_value=0,
            max_value=band_count - 1,
            value=0
        )

        # --------------------------------------------------
        # WAVELENGTH DISPLAY
        # --------------------------------------------------

        wavelength_var = find_wavelength_variable(dataset)

        wavelength = None

        if wavelength_var is not None:

            try:
                wavelength_values = np.asarray(wavelength_var[:]).squeeze()

                if wavelength_values.ndim == 1 and len(wavelength_values) == band_count:
                    wavelength = float(wavelength_values[band_index])

            except Exception:
                wavelength = None

        if wavelength is not None:

            st.metric(
                "Selected Wavelength",
                f"{wavelength:.2f} nm"
            )

        else:

            st.info(
                "Wavelength information was not automatically found "
                "in this NetCDF file."
            )

        # --------------------------------------------------
        # READ ONLY SELECTED BAND
        # --------------------------------------------------

        selection = [slice(None)] * 3
        selection[band_axis] = band_index

        image_data = variable[tuple(selection)]

        image_data = np.ma.filled(image_data, np.nan)
        image_data = np.asarray(image_data, dtype=np.float32)

        # --------------------------------------------------
        # VALID DATA
        # --------------------------------------------------

        valid_data = image_data[
            np.isfinite(image_data)
        ]

        # --------------------------------------------------
        # RADIANCE HEATMAP
        # --------------------------------------------------

        row_step = max(1, image_data.shape[0] // 500)
        col_step = max(1, image_data.shape[1] // 500)

        display_data = image_data[::row_step, ::col_step]

        fig, ax = plt.subplots(figsize=(10, 6))

        im = ax.imshow(
            display_data,
            cmap="viridis",
            aspect="auto"
        )

        title = f"Radiance - Band {band_index}"

        if wavelength is not None:
            title += f" ({wavelength:.2f} nm)"

        ax.set_title(title)
        ax.set_xlabel("Sample")
        ax.set_ylabel("Line")

        fig.colorbar(im, ax=ax, label="Radiance")

        st.pyplot(fig)
        plt.close(fig)

        st.caption(
            "Only the selected band was read. "
            "The image was downsampled for visualization."
        )

        # --------------------------------------------------
        # RADIANCE HISTOGRAM
        # --------------------------------------------------

        st.subheader("Radiance Histogram")

        if valid_data.size > 0:

            fig, ax = plt.subplots(figsize=(10, 4))

            ax.hist(
                valid_data,
                bins=100,
                color="steelblue",
                edgecolor="black",
                linewidth=0.3
            )

            ax.set_title(f"Radiance Distribution - Band {band_index}")
            ax.set_xlabel("Radiance")
            ax.set_ylabel("Pixel Frequency")
            ax.grid(alpha=0.3)

            st.pyplot(fig)
            plt.close(fig)

            st.write("**Radiance Statistics**")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Minimum", f"{np.min(valid_data):.4f}")
            col2.metric("Maximum", f"{np.max(valid_data):.4f}")
            col3.metric("Mean", f"{np.mean(valid_data):.4f}")
            col4.metric("Median", f"{np.median(valid_data):.4f}")

        else:

            st.warning("No valid radiance values available for histogram.")

    # --------------------------------------------------
    # 2D DATA
    # --------------------------------------------------

    elif variable.ndim == 2:

        image_data = variable[:, :]

        image_data = np.ma.filled(image_data, np.nan)

        row_step = max(1, image_data.shape[0] // 500)
        col_step = max(1, image_data.shape[1] // 500)

        image_data = image_data[::row_step, ::col_step]

        fig, ax = plt.subplots(figsize=(10, 6))

        im = ax.imshow(
            image_data,
            cmap="viridis",
            aspect="auto"
        )

        ax.set_title(selected_item["variable"])
        ax.set_xlabel("Column")
        ax.set_ylabel("Row")

        fig.colorbar(im, ax=ax)
        st.pyplot(fig)

        plt.close(fig)

    # --------------------------------------------------
    # 1D DATA
    # --------------------------------------------------

    elif variable.ndim == 1:

        data = variable[:]
        data = np.ma.filled(data, np.nan)

        fig, ax = plt.subplots(figsize=(10, 4))

        ax.plot(data)
        ax.set_title(selected_item["variable"])
        ax.set_xlabel("Index")
        ax.set_ylabel("Value")
        ax.grid(True)

        st.pyplot(fig)
        plt.close(fig)

    # --------------------------------------------------
    # OTHER DATA
    # --------------------------------------------------

    else:

        st.info(
            f"This variable has {variable.ndim} dimensions. "
            "Automatic visualization is not available for this structure."
        )

    # --------------------------------------------------
    # NUMERICAL SAMPLE
    # --------------------------------------------------

    with st.expander("View numerical sample"):

        if variable.ndim == 0:

            sample_data = variable[()]

        elif variable.ndim == 1:

            sample_data = variable[:min(20, variable.shape[0])]

        elif variable.ndim == 2:

            sample_data = variable[
                :min(10, variable.shape[0]),
                :min(10, variable.shape[1])
            ]

        elif variable.ndim == 3:

            sample_data = variable[
                0,
                :min(10, variable.shape[1]),
                :min(10, variable.shape[2])
            ]

        else:

            sample_data = variable[tuple(
                slice(0, min(5, size))
                for size in variable.shape
            )]

        sample_data = np.ma.filled(sample_data, np.nan)

        st.write(sample_data)
