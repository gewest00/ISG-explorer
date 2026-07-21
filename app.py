import streamlit as st

from modules.utils import (
    load_model,
    load_isg,
    get_species,
    get_cell_lines,
    parse_gene_input,
)

from modules.sidebar import build_sidebar

from modules.depmap import (
    load_expression,
    build_gene_column_map,
    get_expression_matrix,
)

from modules.cvr import (
    get_ifn_annotation
)

from modules.analysis import run_analysis

from modules.display import (
    show_expression_matrix,
    show_ifn_landscape_data,
    show_ifn_plot,
    show_top_cell_lines,
)

from modules.plotting import (
    make_pdf_landscape_plot,
)

from modules.report import generate_pdf_report

from modules.downloads import (
    download_ifn_landscape_csv,
    download_plot_png,
    download_plot_html,
    download_pdf,
)

st.set_page_config(
    page_title="ISG Explorer",
    page_icon="🧬",
    layout="wide"
)

st.title("🧬 ISG Explorer")
st.caption(
    """
Interactive exploration of interferon-stimulated genes across mammalian
cell lines using DepMap basal expression and CVR ISG induction datasets.

Version 1.0
"""
)

st.divider()

st.caption(
    """
    **ISG Explorer v1.0**

    Developed by **Grace West**, Rihn Lab, University of Cambridge.
    
    **Data sources**
    
    Broad Institute DepMap Project: https://depmap.org/
    
    Centre for Virus Research (CVR) ISG Database: https://isg.data.cvr.ac.uk/
    
    This application is intended for research use only.
    """
)

# =====================
# Load data
# =====================

model = load_model()
isg = load_isg()
expr = load_expression()
gene_column_map = build_gene_column_map(expr)

species_options = get_species(isg)
cell_line_options = get_cell_lines(model)

# =====================
# SIDEBAR
# =====================

species, bubble_size, output_options, cell_lines = build_sidebar(
    species_options,
    cell_line_options,
)

# =====================
# GENE INPUT
# =====================

st.header("Genes")

gene_text = st.text_area(
    "Enter genes (comma, space or newline separated)",
    height=150,
    placeholder="e.g. TRIM25, OAS1, LY6E"
)

uploaded_file = st.file_uploader(
    "Or upload genes.txt",
    type=["txt"]
)

# =====================
# RUN
# =====================

run = st.button("🔬 Run Analysis", type="primary")

if run:

    st.write("Gene input:")
    genes = parse_gene_input(
        gene_text,
        uploaded_file
    )
    
    if not genes:
        st.error("Please enter at least one gene.")
        st.stop()

    st.write(f"Found {len(genes)} unique genes")
    
    st.info(
        f"""
    **Species:** {species}

    **Cell lines:** {len(cell_lines)}

    **Genes entered:** {len(genes)}
    """
    )
    
    with st.spinner("Analysing expression data and generating IFN landscape"):

        analysis = run_analysis(
            genes,
            cell_lines,
            species,
            expr,
            model,
            gene_column_map,
            isg,
        )
                
        st.session_state["analysis"] = analysis
        st.session_state["species"] = species
        st.session_state["cell_lines"] = cell_lines
        st.session_state["genes"] = genes
        st.session_state["bubble_size"] = bubble_size
    
if "analysis" not in st.session_state:
    st.stop()

analysis = st.session_state["analysis"]
species = st.session_state["species"]
cell_lines = st.session_state["cell_lines"]
genes = st.session_state["genes"]
bubble_size = st.session_state["bubble_size"]

if analysis["missing"]:

    st.warning(
        f"Genes not found: {', '.join(analysis["missing"])}"
    )

show_expression_matrix(analysis)
    
if "IFN Landscape Data" in output_options:
    ifnlandscape_display = show_ifn_landscape_data(
        analysis
    )

    download_ifn_landscape_csv(
        ifnlandscape_display
    )
    
if "IFN Landscape Plot" in output_options:
    fig, pdf_figure = show_ifn_plot(
        analysis,
        bubble_size,
    )

    download_plot_png(pdf_figure)
    download_plot_html(fig)
    
if "Top 10 Cell Lines" in output_options:

    recommended = show_top_cell_lines(
        analysis
    )   
    
    # =====================
    # PDF REPORT
    # =====================


    pdf = generate_pdf_report(
        species=species,
        cell_lines=cell_lines,
        genes=analysis["genes"],
        missing=analysis["missing"],
        ifnlandscape=analysis["ifnlandscape"],
        expression_matrix=analysis["expression_matrix"],
        recommended=recommended,
        figure=pdf_figure,
    )

    download_pdf(pdf)