import pandas as pd


def build_ifnlandscape(
        expression_matrix,
        ifn_table,
        top_expression,
    ):
    """
    Build dataframe used for the IFN Landscape plot.
    """

    mean_expression = expression_matrix.mean(axis=0)

    variance = expression_matrix.var(axis=0).fillna(0)

    maximum = expression_matrix.max(axis=0)
    
    # Highest expressing cell line in ALL of DepMap
    best_hits = (
        top_expression
        .sort_values("Rank")
        .drop_duplicates("Gene")
    )
    
    ifnlandscape = pd.DataFrame({

        "Gene": expression_matrix.columns,

        "Mean Expression": mean_expression.values,

        "Variance": variance.values,

        "Maximum Expression in Selected Cell Lines": maximum.values,

    })
    
    ifnlandscape = ifnlandscape.merge(

        best_hits[
            [
                "Gene",
                "StrippedCellLineName",
                "Expression",
            ]
        ],

        on="Gene",

        how="left",

    )

    ifnlandscape = ifnlandscape.rename(
        columns={
            "StrippedCellLineName": "Top Cell Line",
            "Expression": "Top Expression",
        }
)

    ifnlandscape = ifnlandscape.merge(
        ifn_table,
        on="Gene",
        how="left"
    )

    return ifnlandscape