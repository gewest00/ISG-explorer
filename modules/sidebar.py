import streamlit as st


def build_sidebar(
    species_options,
    cell_line_options,
):
    """
    Build the sidebar and return all user selections.
    """

    st.sidebar.header("Analysis Settings")

    species = st.sidebar.selectbox(
        "Species",
        species_options,
    )

    bubble_size = st.sidebar.radio(
        "Bubble Size",
        [
            "Variance",
            "Maximum Expression",
        ],
    )

    output_options = st.sidebar.multiselect(
        "Outputs",
        [
            "IFN Landscape Plot",
            "IFN Landscape Data",
            "Expression Matrix",
            "Top 10 Cell Lines",
        ],
        default=[
            "IFN Landscape Plot",
            "Expression Matrix",
        ],
    )

    st.sidebar.header("Cell Lines")

    cell_lines = st.sidebar.multiselect(
        "Choose cell lines",
        cell_line_options,
        default=[
            "HEK293",
            "A549",
            "CALU3",
        ],
    )

    return (
        species,
        bubble_size,
        output_options,
        cell_lines,
    )