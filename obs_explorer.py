
import streamlit as st
import numpy as np
import pandas as pd
from utils.netcdf_utils import get_variable_catalog, get_variable


def render_obs_explorer(dataset):
    st.subheader("EMIT OBS Explorer")

    catalog = get_variable_catalog(dataset)

    if not catalog:
        st.warning("No variables found in this OBS file.")
        return

    variable_options = {
        f'{item["group"]} | {item["variable"]} | {item["shape"]}': item
        for item in catalog
    }

    selected_label = st.selectbox(
        "Select OBS variable",
        list(variable_options.keys()),
        key="obs_variable_selection"
    )

    selected_item = variable_options[selected_label]

    variable = get_variable(
        dataset,
        selected_item["variable"],
        selected_item["group"]
    )

    st.markdown("## Variable Information")

    st.json({
        "Variable": selected_item["variable"],
        "Group": selected_item["group"],
        "Dimensions": variable.dimensions,
        "Shape": variable.shape,
        "Data Type": str(variable.dtype),
        "Attributes": {
            attr: variable.getncattr(attr)
            for attr in variable.ncattrs()
        }
    })

    st.markdown("## Data Preview")

    # 3D array: select one parameter to convert into a 2D preview
    if variable.ndim == 3:

        parameter_index = st.selectbox(
            "Select observation parameter",
            range(variable.shape[2]),
            format_func=lambda i: f"Parameter {i}",
            key="obs_parameter"
        )

        preview = variable[:20, :20, parameter_index]

        preview = np.ma.asarray(preview)
        preview = preview.astype(float).filled(np.nan)

        st.dataframe(
            pd.DataFrame(preview),
            use_container_width=True
        )

    # 2D array
    elif variable.ndim == 2:

        preview = variable[:20, :20]
        preview = np.ma.asarray(preview)
        preview = preview.astype(float).filled(np.nan)

        st.dataframe(
            pd.DataFrame(preview),
            use_container_width=True
        )

    # 1D array
    elif variable.ndim == 1:

        preview = variable[:20]

        st.dataframe(
            pd.DataFrame({"Value": preview}),
            use_container_width=True
        )

    # Scalar
    elif variable.ndim == 0:

        st.write(variable[()])

    else:

        st.info("Preview is not available for this variable.")

