"""
Renders section data into a PDF using reportlab (chosen over WeasyPrint/wkhtmltopdf to
avoid native system library install failures on Windows). One Helvetica family
throughout — titles bold and modestly larger than body, not a different typeface.
Justified text. Placeholder paragraphs are skipped entirely. Page numbers via a
two-pass NumberedCanvas ("Page X of Y").
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image,
)

INK = colors.HexColor("#1a2332")
ACCENT = colors.HexColor("#8c1d2b")
MUTED = colors.HexColor("#5b6472")
TINT = colors.HexColor("#f4f5f7")

STYLES = {
    "kicker": ParagraphStyle("kicker", fontName="Helvetica-Bold", fontSize=9,
                              textColor=ACCENT, spaceAfter=6, tracking=1),
    "title": ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=20,
                             textColor=INK, spaceAfter=4, leading=24),
    "subtitle": ParagraphStyle("subtitle", fontName="Helvetica", fontSize=11,
                                textColor=MUTED, spaceAfter=10, leading=14),
    "meta": ParagraphStyle("meta", fontName="Helvetica", fontSize=8,
                            textColor=MUTED, spaceAfter=16),
    "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=13,
                          textColor=INK, spaceBefore=18, spaceAfter=8,
                          borderColor=ACCENT, borderWidth=0, leftIndent=8),
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=10, textColor=INK,
                            leading=15, spaceAfter=9, alignment=TA_JUSTIFY),
    "new_trend_label": ParagraphStyle("new_trend_label", fontName="Helvetica-Bold", fontSize=8,
                                       textColor=colors.white, spaceAfter=6),
    "source_item": ParagraphStyle("source_item", fontName="Helvetica", fontSize=8,
                                   textColor=MUTED, leading=11),
    "disclaimer": ParagraphStyle("disclaimer", fontName="Helvetica", fontSize=7.5,
                                  textColor=MUTED, leading=10, alignment=TA_JUSTIFY),
}


class _NumberedCanvas(pdfcanvas.Canvas):
    """Standard reportlab two-pass pattern: buffers pages, then stamps each with
    'Page X of Y' once the total page count is known."""
    def __init__(self, *args, doc_title="", **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_states = []
        self._doc_title = doc_title

    def showPage(self):
        self._saved_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved_states)
        for state in self._saved_states:
            self.__dict__.update(state)
            self._draw_footer(total)
            super().showPage()
        super().save()

    def _draw_footer(self, total):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(MUTED)
        self.drawRightString(A4[0] - 22 * mm, 12 * mm, f"Page {self._pageNumber} of {total}")
        self.drawString(22 * mm, 12 * mm, self._doc_title)
        self.restoreState()


def _body_flowables(text: str) -> list:
    import re
    flowables = []
    for para in [p.strip() for p in text.split("\n\n") if p.strip()]:
        if re.fullmatch(r"\[DATA SOURCE NOT CONNECTED:.*?\]", para, re.DOTALL):
            continue
        escaped = para.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        flowables.append(Paragraph(escaped, STYLES["body"]))
    return flowables


def render_pdf(title: str, subtitle: str, kicker: str,
                sections: list[dict], disclaimer: str, out_path: str,
                new_trend_section_ids: list[str] | None = None) -> str:
    new_trend_section_ids = new_trend_section_ids or []
    doc = SimpleDocTemplate(
        out_path, pagesize=A4,
        topMargin=20 * mm, bottomMargin=20 * mm, leftMargin=22 * mm, rightMargin=22 * mm,
    )

    story = []
    story.append(Paragraph(kicker.upper(), STYLES["kicker"]))
    story.append(Paragraph(title, STYLES["title"]))
    story.append(Paragraph(subtitle, STYLES["subtitle"]))
    from datetime import date
    story.append(Paragraph(f"Generated {date.today().isoformat()} · Claude-drafted, RAG-grounded",
                            STYLES["meta"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=INK, spaceAfter=14))

    all_sources: dict[str, str] = {}

    for sec in sections:
        if sec["heading"] in new_trend_section_ids:
            story.append(Table([[Paragraph("★ NEW TREND", STYLES["new_trend_label"])]],
                                colWidths=[160 * mm],
                                style=TableStyle([
                                    ("BACKGROUND", (0, 0), (-1, -1), ACCENT),
                                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                                ])))
            story.append(Spacer(1, 4))

        story.append(Paragraph(sec["heading"], STYLES["h2"]))
        story.extend(_body_flowables(sec["body"]))

        chart_path = sec.get("chart_path")
        if chart_path and Path(chart_path).exists():
            from PIL import Image as PILImage
            with PILImage.open(chart_path) as im:
                w, h = im.size
            max_width = 155 * mm
            display_w = min(max_width, w)
            display_h = display_w * (h / w)
            story.append(Spacer(1, 4))
            story.append(Image(chart_path, width=display_w, height=display_h))
            story.append(Spacer(1, 8))

        for chunk in sec.get("chunks", []):
            all_sources[chunk["source_name"]] = chunk.get("source_url", "")

    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#d8dce1"),
                             spaceBefore=16, spaceAfter=10))

    story.append(Paragraph("SOURCES CITED", STYLES["kicker"]))
    for name, url in sorted(all_sources.items()):
        line = f"{name}" + (f" — {url}" if url else "")
        escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        story.append(Paragraph(escaped, STYLES["source_item"]))

    story.append(Spacer(1, 12))
    story.append(Paragraph(disclaimer, STYLES["disclaimer"]))

    doc.build(story, canvasmaker=lambda *a, **kw: _NumberedCanvas(*a, doc_title=title, **kw))
    return out_path


if __name__ == "__main__":
    demo = render_pdf(
        title="Demo Report", subtitle="A quick reportlab rendering check",
        kicker="Test", sections=[{
            "heading": "Sample Section",
            "body": "This is a grounded claim: vacancy fell below 10% in late 2024 "
                    "(Source: CBRE, 2026-01-01).\n\n"
                    "[DATA SOURCE NOT CONNECTED: this part needs a paid feed.]",
            "fact_check": {"n_claims_checked": 1, "n_grounded": 1, "coverage_score": 1.0},
            "chunks": [{"source_name": "CBRE", "source_url": "https://www.cbre.com"}],
        }],
        disclaimer="Test disclaimer.",
        out_path="/tmp/demo.pdf",
    )
    print(f"Wrote {demo}")
