import pandas as pd
import streamlit as st


@st.cache_data
def load_expression(
    genes,
    model,
    gene_column_map,
    path="data/OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv",
):
    """
    Load only the requested gene columns from DepMap.
    """

    usecols = [
        "ModelID",
    ]

    for gene in genes:
        if gene in gene_column_map:
            usecols.append(gene_column_map[gene])

    df = pd.read_csv(
        path,
        usecols=usecols,
    )

    expression_cols = [
        c for c in df.columns
        if c != "ModelID"
    ]

    df[expression_cols] = (
        df[expression_cols]
        .astype("float32")
    )

    df = df.merge(
        model[
            [
                "ModelID",
                "StrippedCellLineName",
                "OncotreeLineage",
            ]
        ],
        on="ModelID",
        how="left",
    )

    return df

@st.cache_data
def build_gene_column_map(
    path="data/OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv",
):
    """
    Read only the header of the DepMap file and
    build a gene → column lookup.
    """

    columns = pd.read_csv(
        path,
        nrows=0,
    ).columns

    return {
        col.split(" (")[0].strip().upper(): col
        for col in columns
        if "(" in col
    }
    
def get_expression_matrix(
    genes,
    cell_lines,
    expr,
    col_map
):
    """
    Return expression matrix for selected genes
    and selected cell lines.
    """

    df = expr

    df = df[
        df["StrippedCellLineName"]
        .str.upper()
        .isin([c.upper() for c in cell_lines])
    ]

    missing = [
        gene
        for gene in genes
        if gene not in col_map
    ]

    resolved = [
        "StrippedCellLineName",
        *[
            col_map[g]
            for g in genes
            if g in col_map
        ],
    ]

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
    col_map,
    n=50,
):
    """
    Return the top expressing cell lines in DepMap
    for each gene.
    """

    df = expr

    results = []

    for gene in genes:

        if gene not in col_map:
            continue

        column = col_map[gene]

        temp = df[
            [
                "StrippedCellLineName",
                "OncotreeLineage",
                column,
            ]
        ]

        temp = temp.rename(
            columns={column: "Expression"}
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