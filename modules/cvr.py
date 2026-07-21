import pandas as pd


def get_ifn_annotation(genes, isg_df, species):
    """
    Return IFN inducibility annotation
    for a list of genes.
    """

    # Filter selected species
    species_df = isg_df[
        isg_df["Species"].str.upper() == species.upper()
    ].copy()

    species_df["Gene Name"] = (
        species_df["Gene Name"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    genes = [
        g.strip().upper()
        for g in genes
    ]
    
    duplicates = species_df[
        species_df["Gene Name"].duplicated(keep=False)
    ]

    print(duplicates.sort_values("Gene Name"))

    print(species_df.columns)
    print(species_df.head())
    print(species_df[species_df["Gene Name"].str.contains("GADD", na=False)])
    print(species_df[species_df["Gene Name"].str.contains("RETREG", na=False)])
    print(species_df[species_df["Gene Name"].str.contains("FAM134", na=False)])
    print(species_df.columns.tolist())

    # Dictionary lookup
    isg_map = dict(
        zip(
            species_df["Gene Name"],
            species_df["Log2FC"]
        )
    )

    rows = []

    for gene in genes:

        if gene in isg_map:

            rows.append({
                "Gene": gene,
                "In_CVR": True,
                "IFN_Log2FC": isg_map[gene]
            })

        else:

            rows.append({
                "Gene": gene,
                "In_CVR": False,
                "IFN_Log2FC": None
            })

    return pd.DataFrame(rows)