import pandas as pd
import numpy as np


def create_gene_landscape(
    expr,
    model,
    isg,
    genes,
    species,
    cell_lines
):

    # --------------------
    # Prepare ISG dataset
    # --------------------

    isg = isg.copy()

    isg["Gene Name"] = (
        isg["Gene Name"]
        .str.upper()
    )

    isg = isg[
        isg["Species"].str.upper()
        ==
        species.upper()
    ]

    isg_map = dict(
        zip(
            isg["Gene Name"],
            isg["Log2FC"]
        )
    )


    # --------------------
    # Merge expression + metadata
    # --------------------

    df = expr.merge(
        model[
            [
                "ModelID",
                "StrippedCellLineName"
            ]
        ],
        on="ModelID",
        how="left"
    )


    df = df[
        df["StrippedCellLineName"]
        .str.upper()
        .isin(
            [
                c.upper()
                for c in cell_lines
            ]
        )
    ]


    # --------------------
    # Find gene columns
    # --------------------

    col_map = {}

    for col in df.columns:

        if "(" in col and ")" in col:

            gene = (
                col.split(" (")[0]
                .strip()
                .upper()
            )

            col_map[gene] = col


    resolved = []

    missing = []

    for gene in genes:

        gene = gene.upper()

        if gene in col_map:
            resolved.append(gene)

        else:
            missing.append(gene)


    if len(resolved) == 0:
        return pd.DataFrame()


    # --------------------
    # Create expression matrix
    # --------------------

    selected = df[
        [
            "StrippedCellLineName"
        ]
        +
        [
            col_map[g]
            for g in resolved
        ]
    ]


    long = selected.melt(
        id_vars=[
            "StrippedCellLineName"
        ],
        var_name="Gene",
        value_name="Expression"
    )


    long["Gene"] = (
        long["Gene"]
        .str.replace(
            r"\s*\(.*\)",
            "",
            regex=True
        )
    )


    long["Expression"] = pd.to_numeric(
        long["Expression"],
        errors="coerce"
    )


    # --------------------
    # Calculate summaries
    # --------------------

    summary = (
        long
        .groupby("Gene")
        ["Expression"]
        .agg(
            Mean_Expression="mean",
            Max_Expression="max",
            Expr_variance="var"
        )
        .reset_index()
    )


    # top expressing cell lines

    top_cells = (
        long
        .sort_values(
            "Expression",
            ascending=False
        )
        .groupby("Gene")
        .head(3)
        .groupby("Gene")
        .apply(
            lambda x:
            "; ".join(
                [
                    f"{r.StrippedCellLineName}: {r.Expression:.2f}"
                    for _, r in x.iterrows()
                ]
            )
        )
        .rename("Top_Cell_Lines")
        .reset_index()
    )


    summary = summary.merge(
        top_cells,
        on="Gene",
        how="left"
    )


    # add IFN

    summary["IFN_Log2FC"] = (
        summary["Gene"]
        .map(isg_map)
    )


    # remove genes without CVR data

    summary = summary.dropna(
        subset=[
            "IFN_Log2FC"
        ]
    )


    summary["Expr_variance"] = (
        summary["Expr_variance"]
        .fillna(0)
    )


    return summary