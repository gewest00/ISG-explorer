import streamlit as st

def download_ifn_landscape_csv(ifnlandscape_display):

    st.download_button(
        "⬇ Download IFN Landscape CSV",
        data=ifnlandscape_display.to_csv(index=False),
        file_name="ifn_landscape.csv",
        mime="text/csv",
    )
    
def download_plot_png(fig):

    try:
        png = fig.to_image(
            format="png",
            width=1600,
            height=900,
            scale=2,
        )
    
        st.download_button(
            "🖼 Download PNG",
            data=png,
            file_name="IFN_landscape.png",
            mime="image/png",
        )

    except Exception as e:
        st.warning(
            "PNG export is temporarily unavailable. "
            "The interactive plot and other results are unaffected."
        )
    
def download_plot_html(fig):

    html = fig.to_html(
        include_plotlyjs="cdn"
    )

    st.download_button(
        "🌐 Download Interactive HTML",
        data=html,
        file_name="IFN_landscape.html",
        mime="text/html",
    )
    
def download_pdf(pdf):

    st.download_button(
        "📄 Download PDF Report",
        data=pdf,
        file_name="ISG_Explorer_Report.pdf",
        mime="application/pdf",
    )
