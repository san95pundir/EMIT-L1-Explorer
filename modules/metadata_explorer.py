
import streamlit as st

from utils.netcdf_utils import (
    get_global_attributes,
    get_dimensions,
    get_group_names,
    get_variable_catalog
)


def render_metadata_explorer(dataset):

    st.subheader("EMIT Metadata Explorer")

    # Global attributes
    st.markdown("### Global Attributes")

    global_attributes = get_global_attributes(dataset)

    if global_attributes:

        for key, value in global_attributes.items():

            st.write(f"**{key}:**", value)

    else:
        st.info("No global attributes found.")

    st.divider()

    # Root dimensions
    st.markdown("### Dimensions")

    dimensions = get_dimensions(dataset)

    if dimensions:

        st.dataframe(
            dimensions,
            use_container_width=True
        )

    else:
        st.info("No dimensions found.")

    st.divider()

    # Groups
    st.markdown("### Groups")

    groups = get_group_names(dataset)

    if groups:

        for group in groups:
            st.write(group)

    else:
        st.write("No groups found.")

    st.divider()

    # Variable catalog
    st.markdown("### Variable Catalog")

    catalog = get_variable_catalog(dataset)

    if catalog:

        st.dataframe(
            catalog,
            use_container_width=True
        )

    else:
        st.info("No variables found.")
