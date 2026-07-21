from io import BytesIO
from datetime import datetime
import tempfile
import os

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
    Flowable,
)

class VerticalText(Flowable):
    """
    Draw vertically rotated text for ReportLab tables.
    """

    def __init__(self, text, fontName="Helvetica-Bold", fontSize=6):
        Flowable.__init__(self)
        self.text = str(text)
        self.fontName = fontName
        self.fontSize = fontSize

        self.width = fontSize + 2
        self.height = max(20, len(self.text) * fontSize * 0.6)

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        self.canv.saveState()

        # White bold text to match table header
        self.canv.setFillColor(colors.white)
        self.canv.setFont(self.fontName, self.fontSize)

        # Rotate 90 degrees anticlockwise
        self.canv.rotate(90)

        self.canv.drawString(
            0,
            -self.width,
            self.text
        )

        self.canv.restoreState()


def dataframe_table(
    df,
    max_width=25*cm,
    wrap_all=False,
    vertical_headers=False,
    skip_first_header=False,
    header_font_size=7,
):
    """
    Convert a pandas DataFrame into a ReportLab table
    that fits within the page width.
    """

    df = df.copy()

    df.columns = [
        str(c).replace("_", " ")
        for c in df.columns
    ]

    styles = getSampleStyleSheet()

    header_style = styles["Normal"].clone("table_header")
    header_style.fontSize = header_font_size
    header_style.leading = header_font_size + 1
    header_style.textColor = colors.white
    header_style.fontName = "Helvetica-Bold"

    cell_style = styles["Normal"].clone("table_cell")
    cell_style.fontSize = 8
    cell_style.leading = 9
    
    if vertical_headers:

        headers = []

        for i, col in enumerate(df.columns):

            if skip_first_header and i == 0:

                headers.append(
                    Paragraph(
                        str(col),
                        header_style,
                    )
                )

            else:

                headers.append(
                    VerticalText(
                        col,
                        fontSize=header_font_size,
                    )
                )

    else:

        headers = [
            Paragraph(
                str(col),
                header_style,
            )
            for col in df.columns
        ]

    if wrap_all:

        data = [headers] + [
            [
                Paragraph(str(cell), cell_style)
                for cell in row
            ]
            for row in df.astype(str).values.tolist()
        ]

    else:

        data = [headers] + df.astype(str).values.tolist()


    # Estimate column widths
    n_cols = len(df.columns)

    if n_cols <= 5:
        font_size = 9
    elif n_cols <= 10:
        font_size = 7
    else:
        font_size = 6


    col_width = max_width / n_cols

    table = Table(
        data,
        repeatRows=1,
        colWidths=[col_width] * n_cols,
    )
    
    if vertical_headers:
        table._argH[0] = 3*cm

    style = [

        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#2C7FB8")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),

        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),

        ("ROWBACKGROUNDS", (0,1), (-1,-1),
         [colors.white, colors.HexColor("#F5F8FC")]),

        ("ALIGN", (1,1), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]

    table.setStyle(TableStyle(style))

    return table


def generate_pdf_report(

    species,
    cell_lines,
    genes,
    missing,
    ifnlandscape,
    figure,
    expression_matrix,
    recommended,

):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=1*cm,
        leftMargin=1*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm,
    )

    styles = getSampleStyleSheet()

    story = []

    # -----------------------------
    # TITLE
    # -----------------------------

    story.append(
        Paragraph(
            "<b><font size=20>ISG Explorer Report</font></b>",
            styles["Title"],
        )
    )

    story.append(
        Paragraph(
            datetime.now().strftime("%d %B %Y  %H:%M"),
            styles["Normal"],
        )
    )

    story.append(Spacer(1,0.6*cm))

    # -----------------------------
    # PARAMETERS
    # -----------------------------

    story.append(
        Paragraph("<b>Analysis Parameters</b>", styles["Heading2"])
    )

    story.append(
        Paragraph(f"<b>Species:</b> {species}", styles["Normal"])
    )

    story.append(
        Paragraph(
            f"<b>Cell lines ({len(cell_lines)}):</b> "
            + ", ".join(cell_lines),
            styles["Normal"],
        )
    )

    story.append(
        Paragraph(
            f"<b>Genes searched:</b> {len(genes)}",
            styles["Normal"],
        )
    )

    if missing:

        story.append(
            Paragraph(
                "<b>Genes not found:</b> "
                + ", ".join(missing),
                styles["Normal"],
            )
        )

    story.append(Spacer(1,0.5*cm))

    # -----------------------------
    # IFNLANDSCAPE
    # -----------------------------

    tmp = tempfile.NamedTemporaryFile(
        suffix=".png",
        delete=False,
    )

    try:
        figure.write_image(
            tmp.name,
            width=1600,
            height=900,
            scale=2,
        )
    except Exception as e:
        print(f"Could not export plot image: {e}")

    story.append(
        Paragraph(
            "<b>IFN Landscape</b>",
            styles["Heading2"],
        )
    )

    story.append(
        Image(
            tmp.name,
            width=18*cm,
            height=10*cm,
        )
    )

    story.append(Spacer(1,0.2*cm))

    story.append(
        Paragraph(
            "<b>IFN Landscape Summary</b>",
            styles["Heading2"],
        )
    )

    story.append(
        dataframe_table(
            ifnlandscape.round(2),
            header_font_size=10,
        )
    )

    story.append(Spacer(1,0.5*cm))

    # -----------------------------
    # EXPRESSION
    # -----------------------------

    story.append(
        Paragraph(
            "<b>Expression Matrix</b>",
            styles["Heading2"],
        )
    )

    expression_matrix_pdf = expression_matrix.copy()

    expression_matrix_pdf.index.name = "Cell Line"

    expression_matrix_pdf = expression_matrix_pdf.reset_index()

    story.append(
        dataframe_table(
            expression_matrix_pdf.round(2),
            vertical_headers=True,
            skip_first_header=True,
            header_font_size=10,
        )
    )
    
    story.append(Spacer(0.5,0.5*cm))

    # -----------------------------
    # RECOMMENDED CELL LINES
    # -----------------------------

    story.append(
        Paragraph(
            "<b>Recommended Cell Lines</b>",
            styles["Heading2"],
        )
    )

    # Reformat recommended table for PDF
    recommended_pdf = recommended.T.reset_index()

    recommended_pdf.columns = [
        "Gene",
        "Top 1",
        "Top 2",
        "Top 3",
        "Top 4",
        "Top 5",
        "Top 6",
        "Top 7",
        "Top 8",
        "Top 9",
        "Top 10",
    ]

    story.append(
        dataframe_table(
            recommended_pdf,
            wrap_all=True,
            header_font_size=10,
        )
    )

    doc.build(story)

    # Remove temporary plot image after PDF has been created
    if os.path.exists(tmp.name):
        os.unlink(tmp.name)

    pdf = buffer.getvalue()

    buffer.close()

    return pdf