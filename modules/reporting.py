"""PDF report generation using ReportLab."""
from __future__ import annotations
import io
import re
from datetime import datetime
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether,
)


BRAND = colors.HexColor("#22d3ee")
TEXT = colors.HexColor("#0f172a")
MUTED = colors.HexColor("#475569")


def _styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", parent=base["Title"], fontName="Helvetica-Bold",
                                fontSize=22, textColor=TEXT, spaceAfter=4),
        "subtitle": ParagraphStyle("subtitle", parent=base["Normal"], fontSize=10,
                                   textColor=MUTED, spaceAfter=8),
        "h1": ParagraphStyle("h1", parent=base["Heading1"], fontName="Helvetica-Bold",
                              fontSize=13, textColor=TEXT, spaceBefore=8, spaceAfter=4),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontName="Helvetica-Bold",
                              fontSize=11, textColor=TEXT, spaceBefore=6, spaceAfter=3),
        "body": ParagraphStyle("body", parent=base["Normal"], fontSize=9.5,
                               textColor=TEXT, leading=13, spaceAfter=3),
        "muted": ParagraphStyle("muted", parent=base["Normal"], fontSize=9,
                                textColor=MUTED, leading=12),
    }


def _kpi_table(rows: list[list[str]]) -> Table:
    t = Table(rows, colWidths=[5*cm, 4*cm, 4*cm, 4*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), BRAND),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#f8fafc"), colors.HexColor("#eef2f7")]),
        ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0,0), (-1,-1), 0.25, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 5),
    ]))
    return t


def _md_to_rl(text: str) -> str:
    return re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)


def build_report(
    df: pd.DataFrame,
    dataset_name: str,
    kind: str,
    metrics: dict,
    insights: list[str],
    health: tuple[int, dict],
    kpis: dict[str, dict],
    recommendations: list[str],
) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm,
        title=f"DataLens AI Report — {dataset_name}",
    )
    s = _styles()
    story = []
    now = datetime.now().strftime("%B %d, %Y · %H:%M")

    # Cover
    story.append(Paragraph("DataLens <font color='#22d3ee'>AI</font> — Executive Report", s["title"]))
    story.append(Paragraph(f"Dataset: <b>{dataset_name}</b> &nbsp;|&nbsp; Type: {kind} &nbsp;|&nbsp; Generated: {now}", s["subtitle"]))
    story.append(Spacer(1, 0.2*cm))

    # Executive summary
    story.append(Paragraph("1. Executive Summary", s["h1"]))
    summary = (
        f"This report analyzes <b>{dataset_name}</b>, a {kind.lower()} containing "
        f"<b>{metrics['rows']:,}</b> records across <b>{metrics['columns']}</b> attributes. "
        f"Overall data health is <b>{health[0]}/100</b>. The findings below outline key "
        f"patterns, anomalies, and actionable recommendations."
    )
    story.append(Paragraph(summary, s["body"]))
    story.append(Spacer(1, 0.1*cm))

    # Dataset overview
    story.append(Paragraph("2. Dataset Overview", s["h1"]))
    overview_rows = [
        ["Metric", "Value", "Metric", "Value"],
        ["Rows", f"{metrics['rows']:,}", "Columns", f"{metrics['columns']}"],
        ["Missing values", f"{metrics['missing']:,} ({metrics['missing_pct']}%)",
         "Duplicates", f"{metrics['duplicates']:,}"],
        ["Memory", f"{metrics['memory_mb']} MB", "Health score", f"{health[0]}/100"],
    ]
    story.append(_kpi_table(overview_rows))
    story.append(Spacer(1, 0.15*cm))

    # KPI summary
    if kpis:
        story.append(Paragraph("3. KPI Summary", s["h1"]))
        kpi_rows = [["Metric", "Sum", "Mean", "Min / Max"]]
        for name, k in list(kpis.items())[:8]:
            kpi_rows.append([
                name,
                f"{k['sum']:,.2f}",
                f"{k['mean']:,.2f}",
                f"{k['min']:,.2f} / {k['max']:,.2f}",
            ])
        story.append(_kpi_table(kpi_rows))
        story.append(Spacer(1, 0.15*cm))

    # Key findings
    story.append(Paragraph("4. Key Findings", s["h1"]))
    findings = []
    if insights:
        for i, ins in enumerate(insights, 1):
            clean = _md_to_rl(ins)
            findings.append(Paragraph(f"{i}. {clean}", s["body"]))
    else:
        findings.append(Paragraph("No insights generated.", s["muted"]))
    story.append(KeepTogether(findings))
    story.append(Spacer(1, 0.15*cm))

    # Recommendations + Appendix kept together if possible
    rec_and_appendix = []
    rec_and_appendix.append(Paragraph("5. Recommendations", s["h1"]))
    for rec in recommendations:
        rec_and_appendix.append(Paragraph(f"• {rec}", s["body"]))
    rec_and_appendix.append(Spacer(1, 0.3*cm))

    # Appendix
    rec_and_appendix.append(Paragraph("Appendix — Column Summary", s["h1"]))
    col_rows = [["Column", "Type", "Missing", "Unique"]]
    for c in df.columns[:30]:
        col_rows.append([
            str(c)[:32],
            str(df[c].dtype),
            f"{int(df[c].isna().sum())}",
            f"{int(df[c].nunique(dropna=True))}",
        ])
    t = Table(col_rows, colWidths=[7*cm, 4*cm, 3*cm, 3*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), BRAND),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#f8fafc"), colors.HexColor("#eef2f7")]),
        ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0,0), (-1,-1), 0.25, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 4),
    ]))
    rec_and_appendix.append(t)
    rec_and_appendix.append(Spacer(1, 0.4*cm))
    rec_and_appendix.append(Paragraph(
        f"Generated by DataLens AI · {now}. This report was produced automatically "
        "from the active dataset and is intended for informational purposes.",
        s["muted"],
    ))

    for item in rec_and_appendix:
        story.append(item)

    doc.build(story)
    pdf = buf.getvalue()
    buf.close()
    return pdf