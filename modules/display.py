import streamlit as st
import pandas as pd

from modules.utils import lineage_info
from modules.plotting import (
    make_ifnlandscape_plot,
    make_pdf_landscape_plot,
)


def show_expression_matrix(
    analysis,
):
    """
    Display the expression matrix.
    """

    st.subheader("Expression Matrix")
    
    st.caption(
        "TPM = transcripts per million"
    )
    st.caption(
        "Guide for selecting cell lines for knockouts: >5 = excellent! 3-5 = acceptable. >3 = avoid if possible."
    )

    styled_matrix = (
        analysis["expression_matrix"]
        .style
        .background_gradient(
            cmap="YlGnBu",
            axis=None,
        )
        .format("{:.2f}")
    )

    st.dataframe(
        styled_matrix,
        width="stretch",
    )
    
def show_ifn_landscape_data(
    analysis,
):
    """
    Display the IFN landscape summary table.

    Returns the formatted dataframe for downloads.
    """

    st.subheader("IFN Landscape Data")

    df = analysis["ifnlandscape"].copy()

    df = df[
        [
            "Gene",
            "IFN_Log2FC",
            "Mean Expression",
            "Maximum Expression in Selected Cell Lines",
            "Variance",
            "Top Cell Line",
            "Top Expression",
        ]
    ]

    df = df.rename(
        columns={
            "IFN_Log2FC": "IFN Induction (log₂FC)",
            "Top Expression": "Highest DepMap Expression",
        }
    )

    numeric = df.select_dtypes("number").columns

    df[numeric] = df[numeric].round(2)

    st.dataframe(
        df,
        width="stretch",
    )

    return df


def show_ifn_plot(
    analysis,
    bubble_size,
):
    """
    Display the interactive IFN landscape plot.

    Returns
    -------
    fig : interactive Plotly figure
    pdf_fig : labelled Plotly figure for PNG/PDF export
    """

    st.subheader("IFN Landscape")
    
    st.caption(
        "Y = Interferon induction. Higher scores indicate stronger association with the interferon-stimulated gene signature."
    )
    
    st.caption(
        "X = Basal expression in selected cell lines."
    )

    fig = make_ifnlandscape_plot(
        analysis["ifnlandscape"],
        bubble_size,
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )

    pdf_fig = make_pdf_landscape_plot(
        analysis["ifnlandscape"],
        bubble_size,
    )

    return fig, pdf_fig
    
    
def show_top_cell_lines(analysis):
    
    st.subheader("Recommended Cell Lines")

    st.caption(
        "Top fifty DepMap cell lines ranked by basal expression."
    )

    top_df = analysis["top_expression"]

    genes = analysis["genes"]
    
    rows = []
    
    for gene in genes:

        gene_df = top_df[
            top_df["Gene"] == gene
        ].sort_values("Rank")

        if gene_df.empty:
            continue

        row = {
            "Gene": gene
        }

        for _, hit in gene_df.iterrows():

            rank = int(hit["Rank"])

            icon, category = lineage_info(hit["OncotreeLineage"])

            row[f"Top {rank}"] = (
                f'{icon} '
                f'{hit["StrippedCellLineName"]} '
                f'({hit["Expression"]:.2f})'
            )

        rows.append(row)
        
    recommended = pd.DataFrame(rows)
    
    recommended = recommended.set_index("Gene").T

    recommended.index.name = "Rank"

    recommended = recommended.reset_index()
    
    st.dataframe(
        recommended,
        width="stretch"
    )

    used_categories = {}

    for lineage in top_df["OncotreeLineage"].dropna():

        icon, category = lineage_info(lineage)

        used_categories[category] = icon

    st.markdown("#### Cell Type:")

    preferred_order = [
        "Lung",
        "Blood / Immune",
        "Gastrointestinal",
        "Brain / Neural",
        "Liver",
        "Breast",
        "Kidney / Urinary",
        "Reproductive",
        "Skin / Connective",
        "Other",
    ]

    legend = []

    for category in preferred_order:

        if category in used_categories:

            legend.append(
                f"{used_categories[category]} {category}"
            )

    st.write("  ".join(legend))
    
    return recommended