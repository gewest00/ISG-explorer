import pandas as pd

from modules.depmap import (
    get_expression_matrix,
    get_top_expression_cell_lines,
)
from modules.cvr import get_ifn_annotation
from modules.ifnlandscape import build_ifnlandscape


def run_analysis(
    genes,
    cell_lines,
    species,
    expr,
    model,
    gene_column_map,
    isg,
):
    """
    Run the complete ISG Explorer analysis.

    Returns a dictionary containing
    all analysis outputs.
    """

    # -------------------------
    # Expression matrix
    # -------------------------

    expr_matrix, missing = get_expression_matrix(
        genes,
        cell_lines,
        expr,
        model,
        gene_column_map,
    )

    # -------------------------
    # Top expression
    # -------------------------

    top_expression = get_top_expression_cell_lines(
        genes,
        expr,
        model,
        gene_column_map,
    )

    top_expression = top_expression.merge(
        model[
            [
                "StrippedCellLineName",
                "OncotreeLineage",
            ]
        ].drop_duplicates(),
        on="StrippedCellLineName",
        how="left",
    )

    # -------------------------
    # IFN annotation
    # -------------------------

    ifn_table = get_ifn_annotation(
        genes,
        isg,
        species,
    )

    # -------------------------
    # IFN Landscape
    # -------------------------

    ifnlandscape = build_ifnlandscape(
        expr_matrix,
        ifn_table,
        top_expression,
    )

    return {
        "genes": genes,
        "expression_matrix": expr_matrix,
        "top_expression": top_expression,
        "ifn_table": ifn_table,
        "ifnlandscape": ifnlandscape,
        "missing": missing,
    }