import pandas as pd
import streamlit as st

from utils.netcdf_utils import (
    get_variable_catalog,
    get_global_attributes,
    get_dimensions,
    get_group_names,
)


def build_metadata_table(dataset):
    """Create a metadata table for every variable in the NetCDF dataset."""

    catalog = get_variable_catalog(dataset)

    records = []

    for item in catalog:
        attributes = item.get("attributes", {})

        records.append({
            "Group": item.get("group", "/"),
            "Variable": item.get("variable"),
            "Dimensions": ", ".join(item.get("dimensions", ())),
            "Shape": str(item.get("shape")),
            "Number of Dimensions": len(item.get("shape", ())),
            "Data Type": item.get("dtype"),
            "Units": attributes.get("units", ""),
            "Description": attributes.get(
                "long_name",
                attributes.get("description", "")
            ),
        })

    return pd.DataFrame(records)


def render_metadata_explorer(dataset):
    """Display the metadata explorer in Streamlit."""

    st.subheader("NetCDF Metadata Explorer")

    metadata_df = build_metadata_table(dataset)

    if metadata_df.empty:
        st.warning("No variables found in this NetCDF file.")
        return

    # Group selection
    groups = get_group_names(dataset)

    selected_group = st.selectbox(
        "Select NetCDF group",
        options=groups,
        index=0
    )

    # Filter variables by selected group
    filtered_df = metadata_df[
        metadata_df["Group"] == selected_group
    ]

    st.markdown("### Variables")

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    # Variable selection
    variable_names = filtered_df["Variable"].tolist()

    if variable_names:
        selected_variable = st.selectbox(
            "Inspect a variable",
            options=variable_names
        )

        selected_metadata = next(
            item for item in get_variable_catalog(dataset)
            if item["group"] == selected_group
            and item["variable"] == selected_variable
        )

        st.markdown("### Variable Details")

        details = {
            "Variable": selected_metadata["variable"],
            "Group": selected_metadata["group"],
            "Dimensions": selected_metadata["dimensions"],
            "Shape": selected_metadata["shape"],
            "Data Type": selected_metadata["dtype"],
            "Attributes": selected_metadata["attributes"],
        }

        st.json(details)

    # Global attributes
    with st.expander("Global Attributes"):
        st.json(get_global_attributes(dataset))

    # Root-level dimensions
    with st.expander("Root Dimensions"):
        st.json(get_dimensions(dataset))