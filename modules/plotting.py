import plotly.express as px


def make_ifnlandscape_plot(
    ifnlandscape,
    bubble_size="Variance",
):
    """
    Create the IFN Landscape plot.
    """
    size_column = {
        "Variance": "Variance",
        "Maximum Expression": "Maximum Expression in Selected Cell Lines",
    }[bubble_size]

    fig = px.scatter(

        ifnlandscape,

        x="Mean Expression",

        y="IFN_Log2FC",

        hover_name="Gene",

        hover_data={
            "Gene": False,
            "IFN_Log2FC": False,
            "Mean Expression": False,
            "Maximum Expression in Selected Cell Lines": False,
            "Top Cell Line": False,
            "Top Expression": False,
        },

        size=size_column,

    )


    fig.update_traces(

        customdata=ifnlandscape[
            [
                "IFN_Log2FC",
                "Mean Expression",
                "Maximum Expression in Selected Cell Lines",
                "Top Cell Line",
                "Top Expression",
            ]
        ],

        hovertemplate=
        "<b>%{hovertext}</b><br><br>"
        "IFN induction: %{customdata[0]:.2f} log₂FC<br>"
        "Mean expression: %{customdata[1]:.2f}<br>"
        "Highest selected expression: %{customdata[2]:.2f}<br><br>"
        "<b>Highest expressing DepMap cell line</b><br>"
        "%{customdata[3]}<br>"
        "Expression: %{customdata[4]:.2f}"
        "<extra></extra>",

    )
    
    
    fig.update_layout(

        template="plotly_white",

        height=650,

        hoverlabel=dict(
            bgcolor="white",
            font_color="black",
            font_size=14,
            font_family="Arial",
        ),
        
        xaxis_title="Mean expression across selected cell lines",

        yaxis_title="IFN induction (log₂FC)",

    )

    fig.update_traces(
        marker=dict(
            sizemin=8
        )
    )
    

    return fig
    
def make_pdf_landscape_plot(
    ifnlandscape,
    bubble_size="Variance",
):
    """
    Static version of the IFN Landscape for the PDF report.
    """

    size_column = {
        "Variance": "Variance",
        "Maximum Expression": "Maximum Expression in Selected Cell Lines",
    }[bubble_size]

    fig = px.scatter(
        ifnlandscape,
        x="Mean Expression",
        y="IFN_Log2FC",
        size=size_column,
        text="Gene",
    )

    fig.update_traces(
        textposition="top center",
        textfont_size=10,
        marker=dict(
            opacity=0.8,
            line=dict(width=1, color="black"),
        ),
    )

    fig.update_layout(
        template="plotly_white",
        height=700,
        xaxis_title="Mean expression across selected cell lines",
        yaxis_title="IFN induction (log₂FC)",
        showlegend=False,
    )

    return fig