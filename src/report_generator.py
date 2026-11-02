
import os
import re
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    PageBreak,
    ListFlowable,
    ListItem
)


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "reports"


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def create_safe_filename(topic):

    safe_topic = re.sub(
        r"[^a-zA-Z0-9]+",
        "_",
        topic
    ).strip("_")

    return safe_topic or "Research_Report"


def format_inline_text(text):
    """
    Convert basic Markdown bold and URLs into ReportLab markup.
    """

    text = escape(text)

    # Convert Markdown bold
    text = re.sub(
        r"\*\*(.+?)\*\*",
        r"<b>\1</b>",
        text
    )

    # Convert URLs into clickable hyperlinks
    url_pattern = r"https?://[^\s<>]+"

    def make_link(match):

        url = match.group(0)

        # Remove trailing punctuation from the link
        clean_url = url.rstrip(".,;:!?)]}")

        trailing = url[len(clean_url):]

        safe_url = escape(clean_url, {'"': "&quot;"})

        return (
            f'<link href="{safe_url}" color="#1769AA">'
            f'<u>{clean_url}</u></link>{trailing}'
        )

    text = re.sub(url_pattern, make_link, text)

    return text


# --------------------------------------------------
# TXT REPORT GENERATOR
# --------------------------------------------------

def generate_report(topic, analysis):

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = (
        f"{create_safe_filename(topic)}_{timestamp}.txt"
    )

    filepath = REPORTS_DIR / filename

    generated_date = datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )

    report_content = f"""
==================================================
                 AI RESEARCH REPORT
==================================================

Research Topic: {topic}

Generated On: {generated_date}

==================================================

{analysis}

==================================================
                 END OF REPORT
==================================================
"""

    with open(filepath, "w", encoding="utf-8") as file:

        file.write(report_content)

    print("TXT report generated:", filepath)

    return str(filepath)


# --------------------------------------------------
# PDF HEADER AND FOOTER
# --------------------------------------------------

def add_page_header_footer(canvas, document):

    canvas.saveState()

    page_width, page_height = A4

    # Header
    if document.page > 1:

        canvas.setFont("Helvetica-Bold", 9)

        canvas.setFillColor(
            colors.HexColor("#17365D")
        )

        canvas.drawString(
            55,
            page_height - 35,
            "AI RESEARCH AGENT"
        )

        canvas.setStrokeColor(
            colors.HexColor("#D9E2F3")
        )

        canvas.line(
            55,
            page_height - 43,
            page_width - 55,
            page_height - 43
        )

    # Footer
    canvas.setFont("Helvetica", 9)

    canvas.setFillColor(colors.grey)

    canvas.drawString(
        55,
        30,
        "AI Research Agent | Research Report"
    )

    canvas.drawRightString(
        page_width - 55,
        30,
        f"Page {document.page}"
    )

    canvas.restoreState()


# --------------------------------------------------
# PDF REPORT GENERATOR
# --------------------------------------------------

def generate_pdf_report(topic, analysis):

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = (
        f"{create_safe_filename(topic)}_{timestamp}.pdf"
    )

    filepath = REPORTS_DIR / filename

    generated_date = datetime.now().strftime(
        "%d %B %Y, %I:%M %p"
    )

    document = SimpleDocTemplate(
        str(filepath),
        pagesize=A4,
        rightMargin=55,
        leftMargin=55,
        topMargin=65,
        bottomMargin=55,
        title=f"AI Research Report - {topic}",
        author="AI Research Agent"
    )

    # --------------------------------------------------
    # STYLES
    # --------------------------------------------------

    styles = getSampleStyleSheet()

    cover_title = ParagraphStyle(
        "CoverTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=27,
        leading=34,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#17365D"),
        spaceAfter=25
    )

    cover_subtitle = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontSize=15,
        leading=22,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#34495E"),
        spaceAfter=20
    )

    topic_style = ParagraphStyle(
        "TopicStyle",
        parent=styles["Normal"],
        fontSize=16,
        leading=23,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#17365D"),
        spaceAfter=15
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=19,
        textColor=colors.HexColor("#17365D"),
        spaceBefore=15,
        spaceAfter=9,
        keepWithNext=True
    )

    subheading_style = ParagraphStyle(
        "SubHeading",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#2874A6"),
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=16,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#333333"),
        spaceAfter=9
    )

    bullet_style = ParagraphStyle(
        "BulletStyle",
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-8,
        spaceAfter=6
    )

    toc_style = ParagraphStyle(
        "TOCStyle",
        parent=body_style,
        fontSize=11,
        leading=20,
        leftIndent=10
    )

    # --------------------------------------------------
    # CREATE PDF CONTENT
    # --------------------------------------------------

    story = []

    # COVER PAGE

    story.append(Spacer(1, 1.4 * inch))

    story.append(
        HRFlowable(
            width="70%",
            thickness=2,
            color=colors.HexColor("#17365D"),
            hAlign="CENTER"
        )
    )

    story.append(Spacer(1, 25))

    story.append(
        Paragraph(
            "AI RESEARCH REPORT",
            cover_title
        )
    )

    story.append(
        Paragraph(
            "Research and Analysis",
            cover_subtitle
        )
    )

    story.append(Spacer(1, 35))

    story.append(
        Paragraph(
            escape(topic),
            topic_style
        )
    )

    story.append(Spacer(1, 35))

    story.append(
        HRFlowable(
            width="50%",
            thickness=1,
            color=colors.HexColor("#AAB7B8"),
            hAlign="CENTER"
        )
    )

    story.append(Spacer(1, 30))

    story.append(
        Paragraph(
            f"<b>Generated On</b><br/>{generated_date}",
            ParagraphStyle(
                "DateStyle",
                parent=styles["Normal"],
                alignment=TA_CENTER,
                fontSize=11,
                leading=18
            )
        )
    )

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "Generated using Python, Gemini, Tavily, "
            "FAISS and Retrieval-Augmented Generation",
            ParagraphStyle(
                "TechStyle",
                parent=styles["Normal"],
                alignment=TA_CENTER,
                fontSize=9,
                textColor=colors.grey
            )
        )
    )

    story.append(PageBreak())

    # TABLE OF CONTENTS

    story.append(
        Paragraph(
            "TABLE OF CONTENTS",
            heading_style
        )
    )

    story.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor("#17365D")
        )
    )

    story.append(Spacer(1, 15))

    headings = []

    for line in analysis.splitlines():

        line = line.strip()

        if line.startswith("#"):

            heading = line.lstrip("#").strip()

            if heading:
                headings.append(heading)

    if headings:

        for heading in headings:

            story.append(
                Paragraph(
                    format_inline_text(heading),
                    toc_style
                )
            )

    else:

        story.append(
            Paragraph(
                "Research Analysis",
                toc_style
            )
        )

    story.append(PageBreak())

    # RESEARCH CONTENT

    story.append(
        Paragraph(
            "RESEARCH ANALYSIS",
            heading_style
        )
    )

    story.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor("#17365D")
        )
    )

    story.append(Spacer(1, 12))

    for line in analysis.splitlines():

        line = line.strip()

        if not line:

            story.append(Spacer(1, 4))

            continue

        # Markdown headings
        if line.startswith("#"):

            heading = line.lstrip("#").strip()

            if heading.lower().startswith("research analysis:"):
                continue

            heading_level = len(line) - len(line.lstrip("#"))

            if heading_level <= 2:

                story.append(
                    Paragraph(
                        format_inline_text(heading),
                        heading_style
                    )
                )

            else:

                story.append(
                    Paragraph(
                        format_inline_text(heading),
                        subheading_style
                    )
                )

        # Bullet points
        elif line.startswith("- ") or line.startswith("* "):

            bullet = line[2:].strip()

            story.append(
                Paragraph(
                    "&bull; " + format_inline_text(bullet),
                    bullet_style
                )
            )

        # Numbered points
        elif re.match(r"^\d+[\.\)]\s+", line):

            story.append(
                Paragraph(
                    format_inline_text(line),
                    body_style
                )
            )

        # Normal paragraphs
        else:

            story.append(
                Paragraph(
                    format_inline_text(line),
                    body_style
                )
            )

    # --------------------------------------------------
    # BUILD PDF
    # --------------------------------------------------

    document.build(
        story,
        onFirstPage=add_page_header_footer,
        onLaterPages=add_page_header_footer
    )

    print("PDF report generated:", filepath)

    return str(filepath)


# --------------------------------------------------
# TESTING
# --------------------------------------------------

if __name__ == "__main__":

    sample_topic = "Generative AI in Healthcare"

    sample_analysis = """
# Research Analysis: Generative AI in Healthcare

## 1. Introduction

Generative AI is transforming healthcare through
advanced artificial intelligence technologies.

## 2. Applications

- Medical documentation
- Drug discovery
- Personalized treatment

## 3. Benefits

- Improved efficiency
- Reduced administrative workload

## 4. Challenges

- Data privacy
- Algorithmic bias

## 5. Conclusion

Generative AI has significant potential in healthcare.

## 6. References

[1] Example Research Source -
https://example.com/research
"""

    generate_report(
        sample_topic,
        sample_analysis
    )

    generate_pdf_report(
        sample_topic,
        sample_analysis
    )
