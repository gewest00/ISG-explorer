import pandas as pd
import streamlit as st

import re


def parse_gene_input(text, uploaded_file=None):
    """
    Parse genes from either textbox or uploaded txt file.
    Returns a cleaned list of unique gene symbols.
    """

    genes = []

    if uploaded_file is not None:
        contents = uploaded_file.read().decode("utf-8")
        genes.extend(contents.splitlines())

    if text:
        genes.extend(
            re.split(r"[,\s]+", text)
        )

    genes = [
        g.strip().upper()
        for g in genes
        if g.strip()
    ]

    # remove duplicates while preserving order
    genes = list(dict.fromkeys(genes))

    return genes


@st.cache_data
def load_model(path="data/Model.csv"):
    """Load DepMap model metadata."""
    return pd.read_csv(path)


@st.cache_data
def load_isg(path="data/ISG_signature.csv"):
    """Load CVR ISG database."""
    return pd.read_csv(path)


def get_species(isg_df):
    """Return sorted list of available species."""
    species = sorted(isg_df["Species"].dropna().unique())
    return species


def get_cell_lines(model_df):
    """Return sorted list of DepMap cell lines."""
    cell_lines = (
        model_df["StrippedCellLineName"]
        .dropna()
        .sort_values()
        .unique()
    )
    return list(cell_lines)
    
    
LINEAGE_GROUPS = {
    "Lung": ("🔵", "Lung"),

    "Haematopoietic and Lymphoid": ("🟢", "Blood / Immune"),

    "Colon": ("🟠", "Gastrointestinal"),
    "Colorectal": ("🟠", "Gastrointestinal"),
    "Stomach": ("🟠", "Gastrointestinal"),
    "Esophagus": ("🟠", "Gastrointestinal"),
    "Small Intestine": ("🟠", "Gastrointestinal"),

    "Central Nervous System": ("🟣", "Brain / Neural"),
    "Peripheral Nervous System": ("🟣", "Brain / Neural"),

    "Liver": ("🔴", "Liver"),
    "Biliary Tract": ("🔴", "Liver"),

    "Breast": ("🟡", "Breast"),

    "Kidney": ("🟤", "Kidney / Urinary"),
    "Bladder": ("🟤", "Kidney / Urinary"),

    "Ovary": ("🩷", "Reproductive"),
    "Endometrium": ("🩷", "Reproductive"),
    "Uterus": ("🩷", "Reproductive"),
    "Cervix": ("🩷", "Reproductive"),
    "Prostate": ("🩷", "Reproductive"),
    "Testis": ("🩷", "Reproductive"),

    "Skin": ("⚫", "Skin / Connective"),
    "Soft Tissue": ("⚫", "Skin / Connective"),
    "Bone": ("⚫", "Skin / Connective"),
}

def lineage_info(lineage):
    return LINEAGE_GROUPS.get(lineage, ("⚪", "Other"))
    
def lineage_category(lineage):
    """
    Return the simplified lineage category only.
    """
    return lineage_info(lineage)[1]