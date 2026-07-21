import pandas as pd
import streamlit as st


@st.cache_data
def load_expression(path="data/OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv"):
    """Load DepMap expression matrix."""
    return pd.read_csv(path)

@st.cache_data
def build_gene_column_map(expr):
    """
    Create a dictionary mapping
    GENE -> DepMap column name.

    This only runs once thanks to caching.
    """

    col_map = {}

    for col in expr.columns:
        if "(" in col:
            gene = col.split(" (")[0].strip().upper()
            col_map[gene] = col

    return col_map
    
def get_expression_matrix(
    genes,
    cell_lines,
    expr,
    model,
    col_map
):
    """
    Return expression matrix for selected genes
    and selected cell lines.
    """

    df = expr.merge(
        model[
            ["ModelID",
             "CellLineName",
             "StrippedCellLineName"]
        ],
        on="ModelID",
        how="left"
    )

    df = df[
        df["StrippedCellLineName"]
        .str.upper()
        .isin([c.upper() for c in cell_lines])
    ]

    resolved = ["StrippedCellLineName"]

    missing = []

    for gene in genes:

        if gene in col_map:

            resolved.append(col_map[gene])

        else:

            missing.append(gene)

    df = df[resolved]

    df_long = df.melt(
        id_vars="StrippedCellLineName",
        var_name="Gene",
        value_name="Expression"
    )

    df_long["Gene"] = (
        df_long["Gene"]
        .str.replace(r"\s*\(.*\)", "", regex=True)
    )

    df_long["Expression"] = pd.to_numeric(
        df_long["Expression"],
        errors="coerce"
    )

    expr_matrix = df_long.pivot_table(
        index="StrippedCellLineName",
        columns="Gene",
        values="Expression",
        aggfunc="mean"
    )

    return expr_matrix, missing
    
def get_top_expression_cell_lines(
    genes,
    expr,
    model,
    col_map,
    n=10,
):
    """
    Return the top expressing cell lines in DepMap
    for each gene.
    """

    df = expr.merge(
        model[["ModelID", "StrippedCellLineName"]],
        on="ModelID",
        how="left",
    )

    results = []

    for gene in genes:

        if gene not in col_map:
            continue

        column = col_map[gene]

        temp = df[
            ["StrippedCellLineName", column]
        ].copy()

        temp = temp.rename(
            columns={column: "Expression"}
        )

        temp["Expression"] = pd.to_numeric(
            temp["Expression"],
            errors="coerce",
        )

        temp = temp.dropna()

        temp = temp.sort_values(
            "Expression",
            ascending=False,
        )

        temp = temp.head(n)

        temp["Gene"] = gene

        temp["Rank"] = range(1, len(temp) + 1)

        results.append(temp)

    if len(results) == 0:
        return pd.DataFrame()

    return pd.concat(results, ignore_index=True)