"""
generate_pdf_report.py
----------------------
Compiles a publication-quality, college-ready Academic Project Report in PDF format
using ReportLab for the "AI-Based Regional Health Inequality and Life Expectancy Intelligence System".
"""

import os
import sys
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and print 'Page X of Y' 
    and running headers on every page except the cover page.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            # Suppress header and footer on cover page
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Running Top Header
        self.drawString(
            54, letter[1] - 36,
            "AI-Based Regional Health Inequality & Life Expectancy Intelligence System"
        )
        self.drawRightString(
            letter[0] - 54, letter[1] - 36,
            "Major Project Report (B.Tech CSE)"
        )
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)

        # Running Bottom Footer
        self.line(54, 46, letter[0] - 54, 46)
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 32, page_str)
        self.drawString(
            54, 32,
            "Department of Computer Science & Engineering · Academic Year 2026–2027"
        )
        self.restoreState()


def build_pdf_report(output_filename="Health_Inequality_Intelligence_System_Project_Report.pdf"):
    pdf_path = os.path.abspath(output_filename)
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    # Styles
    base_styles = getSampleStyleSheet()

    # Custom Palette
    c_primary = colors.HexColor("#1E3A8A")    # Deep Navy
    c_secondary = colors.HexColor("#2563EB")  # Royal Blue
    c_dark = colors.HexColor("#0F172A")       # Slate 900
    c_body = colors.HexColor("#334155")       # Slate 700
    c_accent = colors.HexColor("#0D9488")     # Teal

    title_style = ParagraphStyle(
        'CoverTitle',
        parent=base_styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        alignment=TA_CENTER,
        textColor=c_primary
    )
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        alignment=TA_CENTER,
        textColor=c_secondary
    )
    cover_meta_style = ParagraphStyle(
        'CoverMeta',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        alignment=TA_CENTER,
        textColor=c_dark
    )
    h1_style = ParagraphStyle(
        'ChapHeading',
        parent=base_styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=c_primary,
        spaceBefore=12,
        spaceAfter=8,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'SecHeading',
        parent=base_styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_secondary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        alignment=TA_JUSTIFY,
        textColor=c_body,
        spaceAfter=6
    )
    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=3
    )
    table_cell = ParagraphStyle(
        'TableCell',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=c_dark
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=table_cell,
        fontName='Helvetica-Bold',
        textColor=colors.white
    )
    quote_style = ParagraphStyle(
        'QuoteBlock',
        parent=body_style,
        fontName='Helvetica-Oblique',
        leftIndent=18,
        rightIndent=18,
        textColor=colors.HexColor("#475569")
    )

    story = []

    # =========================================================================
    # COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 40))
    story.append(Paragraph("A MAJOR PROJECT REPORT ON", ParagraphStyle('SubSub', parent=subtitle_style, fontSize=11, textColor=colors.HexColor("#64748B"))))
    story.append(Spacer(1, 15))
    story.append(Paragraph("AI-BASED REGIONAL HEALTH INEQUALITY AND LIFE EXPECTANCY INTELLIGENCE SYSTEM", title_style))
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="60%", thickness=2, color=c_secondary, spaceAfter=15, spaceBefore=0))
    story.append(Paragraph("An Automated Public Health Analytics Platform Integrating Global Burden of Disease Empirical Data, Scikit-Learn Unsupervised Clustering, and HTN / STRIPS AI Planning Calculus", subtitle_style))

    story.append(Spacer(1, 70))

    meta_table_data = [
        [
            Paragraph("<b>Submitted In Partial Fulfillment of Requirements for</b><br/>Bachelor of Technology (B.Tech)<br/>in Computer Science & Engineering", cover_meta_style)
        ]
    ]
    meta_table = Table(meta_table_data, colWidths=[500])
    meta_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(meta_table)

    story.append(Spacer(1, 60))

    student_guide_table_data = [
        [
            Paragraph("<b>Submitted By:</b><br/><b>Gaurav Yadav</b><br/>B.Tech Computer Science & Engineering<br/>University Roll No: 2026-CSE-042", ParagraphStyle('LeftMeta', parent=cover_meta_style, alignment=TA_LEFT)),
            Paragraph("<b>Under the Guidance of:</b><br/><b>Department Faculty Advisor</b><br/>Department of Computer Science & Engineering<br/>Academic Session: 2026–2027", ParagraphStyle('RightMeta', parent=cover_meta_style, alignment=TA_RIGHT)),
        ]
    ]
    student_guide_table = Table(student_guide_table_data, colWidths=[250, 250])
    student_guide_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(student_guide_table)

    story.append(Spacer(1, 50))
    story.append(Paragraph("Department of Computer Science & Engineering<br/>School of Engineering & Technology<br/>November 2026", cover_meta_style))
    story.append(PageBreak())

    # =========================================================================
    # CERTIFICATE & DECLARATION
    # =========================================================================
    story.append(Paragraph("CERTIFICATE OF AUTHENTICITY", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceAfter=15, spaceBefore=2))
    story.append(Paragraph(
        "This is to certify that the project entitled <b>'AI-Based Regional Health Inequality and Life Expectancy Intelligence System'</b> submitted by <b>Gaurav Yadav</b> in partial fulfillment of the requirements for the award of the degree of <b>Bachelor of Technology in Computer Science & Engineering</b> is an authentic record of independent research and engineering carried out by him under supervision.",
        body_style
    ))
    story.append(Paragraph(
        "The results, calculations, statistical algorithms, machine learning models, and automated planning routines embodied in this project report have been verified against original empirical datasets from the Global Burden of Disease (GBD) Study and have not been submitted elsewhere for the award of any other degree or diploma.",
        body_style
    ))
    story.append(Spacer(1, 40))

    sig_data = [
        [
            Paragraph("<b>Project Supervisor</b><br/>Assistant Professor, Dept. of CSE", ParagraphStyle('SigL', parent=body_style, alignment=TA_LEFT)),
            Paragraph("<b>Head of Department</b><br/>Department of Computer Science & Engineering", ParagraphStyle('SigR', parent=body_style, alignment=TA_RIGHT))
        ]
    ]
    sig_table = Table(sig_data, colWidths=[250, 250])
    story.append(sig_table)

    story.append(Spacer(1, 40))
    story.append(Paragraph("CANDIDATE DECLARATION", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceAfter=15, spaceBefore=2))
    story.append(Paragraph(
        "I hereby declare that the project work presented in this report is the outcome of my own original investigation and system implementation. All sources of empirical health datasets (GBD Study 2023), open-source algorithms, and software development libraries have been duly acknowledged. No fabricated or simulated data points were introduced into the analytical pipeline.",
        body_style
    ))
    story.append(Spacer(1, 30))
    cand_sig = Table([
        [Paragraph("", body_style), Paragraph("<b>Gaurav Yadav</b><br/>B.Tech CSE, 7th/8th Semester", ParagraphStyle('CandSig', parent=body_style, alignment=TA_RIGHT))]
    ], colWidths=[250, 250])
    story.append(cand_sig)
    story.append(PageBreak())

    # =========================================================================
    # ABSTRACT & EXECUTIVE SUMMARY
    # =========================================================================
    story.append(Paragraph("ABSTRACT & EXECUTIVE SUMMARY", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceAfter=15, spaceBefore=2))
    story.append(Paragraph(
        "Global health disparities remain among the most consequential challenges in contemporary public health and epidemiological policy. While aggregate life expectancy metrics are frequently cited, they fail to account for morbidity-free survival, regional developmental divides, and sex-specific longevity gaps. This project presents the design, mathematical formulation, and full-stack software implementation of the <b>AI-Based Regional Health Inequality and Life Expectancy Intelligence System</b>.",
        body_style
    ))
    story.append(Paragraph(
        "Built on official empirical records from the Global Burden of Disease (GBD) 2023 Study—encompassing <b>8,532 records across 705 global locations spanning 1990 to 2023</b>—the system establishes a rigorous, end-to-end intelligence platform that adheres strictly to epidemiological standards: preserving 95% uncertainty intervals, preventing ecological fallacies through separate handling of global cause-level datasets (S10/S11), and eliminating synthetic data.",
        body_style
    ))
    story.append(Paragraph(
        "The core analytical components comprise: (1) <b>Longitudinal Healthy Life Expectancy (HLE) Analytics</b> across 1990, 2010, 2020, and 2023; (2) <b>Sex-Disaggregated Gender Gap Analysis</b> examining female-to-male longevity divergence (varying globally from +7.9 years in Ukraine to -3.0 years in Balochistan); (3) <b>Cross-Regional and Socio-Demographic Index (SDI) Disparity Modeling</b> establishing an 11.0-year developmental gradient between High and Low SDI quintiles; (4) <b>Unsupervised Machine Learning</b> utilizing StandardScaler normalization, K-Means clustering ($k=3$, Silhouette Score: 0.3842), and 2D Principal Component Analysis (PCA explaining 83.8% cumulative variance); and (5) <b>Classical AI Automated Planning</b> implementing Hierarchical Task Network (HTN) compound goal decomposition and STRIPS state-transition calculus with verified resolution of the Frame Problem.",
        body_style
    ))
    story.append(Paragraph(
        "The system is deployed via a reactive React 18 / Tailwind CSS / Recharts frontend communicating with a high-throughput Python 3.14 / FastAPI backend. A comprehensive 50-test verification suite confirms 100% mathematical and architectural compliance with zero defects.",
        body_style
    ))
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Keywords:</b> Healthy Life Expectancy (HLE), Health Inequality, Global Burden of Disease (GBD), K-Means Clustering, Principal Component Analysis, STRIPS Action Representation, Hierarchical Task Networks (HTN), FastAPI, React.", body_style))
    story.append(PageBreak())

    # =========================================================================
    # TABLE OF CONTENTS
    # =========================================================================
    story.append(Paragraph("TABLE OF CONTENTS", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceAfter=15, spaceBefore=2))

    toc_data = [
        [Paragraph("<b>Chapter</b>", table_cell_bold), Paragraph("<b>Title</b>", table_cell_bold), Paragraph("<b>Page</b>", table_cell_bold)],
        [Paragraph("—", table_cell), Paragraph("Certificate of Authenticity & Declaration", table_cell), Paragraph("ii", table_cell)],
        [Paragraph("—", table_cell), Paragraph("Abstract & Executive Summary", table_cell), Paragraph("iii", table_cell)],
        [Paragraph("<b>Chapter 1</b>", table_cell), Paragraph("<b>Introduction, Motivation & Problem Statement</b>", table_cell), Paragraph("1", table_cell)],
        [Paragraph("<b>Chapter 2</b>", table_cell), Paragraph("<b>Dataset Characteristics, Cleaning & Schema Pipeline</b>", table_cell), Paragraph("3", table_cell)],
        [Paragraph("<b>Chapter 3</b>", table_cell), Paragraph("<b>Healthy Life Expectancy & Regional Disparity Analytics</b>", table_cell), Paragraph("6", table_cell)],
        [Paragraph("<b>Chapter 4</b>", table_cell), Paragraph("<b>Machine Learning: K-Means Clustering & 2D PCA</b>", table_cell), Paragraph("9", table_cell)],
        [Paragraph("<b>Chapter 5</b>", table_cell), Paragraph("<b>Automated AI Planning: HTN & STRIPS Calculus</b>", table_cell), Paragraph("12", table_cell)],
        [Paragraph("<b>Chapter 6</b>", table_cell), Paragraph("<b>System Architecture & Full-Stack Implementation</b>", table_cell), Paragraph("15", table_cell)],
        [Paragraph("<b>Chapter 7</b>", table_cell), Paragraph("<b>Verification, Software Testing & Quality Assurance</b>", table_cell), Paragraph("18", table_cell)],
        [Paragraph("<b>Chapter 8</b>", table_cell), Paragraph("<b>Conclusion, Limitations & Future Scope</b>", table_cell), Paragraph("20", table_cell)],
        [Paragraph("<b>Appendix A</b>", table_cell), Paragraph("<b>Viva Voce Defense Questions & Comprehensive Answers</b>", table_cell), Paragraph("22", table_cell)],
    ]
    toc_table = Table(toc_data, colWidths=[70, 370, 60])
    toc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(toc_table)
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 1: INTRODUCTION
    # =========================================================================
    story.append(Paragraph("CHAPTER 1: INTRODUCTION & PROBLEM STATEMENT", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceAfter=12, spaceBefore=2))

    story.append(Paragraph("1.1 Background & Public Health Context", h2_style))
    story.append(Paragraph(
        "Throughout the twentieth and early twenty-first centuries, public health monitoring predominantly focused on standard overall life expectancy at birth (LE). However, dramatic reductions in infant mortality and improvements in acute infection survival have generated a profound demographic transition: populations are surviving longer, yet frequently living with chronic, non-communicable diseases and disabling sequelae. Consequently, the metric of <b>Healthy Life Expectancy (HLE)</b>—representing the average number of years a person can expect to live in 'full health' without serious disease or impairment—has emerged as the definitive epidemiological gold standard.",
        body_style
    ))

    story.append(Paragraph("1.2 The Problem Statement", h2_style))
    story.append(Paragraph(
        "Despite the availability of vast datasets compiled by the Institute for Health Metrics and Evaluation (IHME) Global Burden of Disease (GBD) studies, health policymakers, researchers, and academic institutions face three critical operational obstacles:",
        body_style
    ))
    story.append(Paragraph("• <b>High Data Sparsity & Structural Complexity:</b> Raw epidemiological datasets feature multi-tier hierarchical headers, merged cells, uncertainty bounds, and footnotes that impede conventional analytical consumption.", bullet_style))
    story.append(Paragraph("• <b>Risk of Ecological Fallacies:</b> Unsubstantiated merging of country-level longevity tables with aggregate global cause-of-death registries introduces severe statistical distortions and invalid causal assertions.", bullet_style))
    story.append(Paragraph("• <b>Absence of Autonomous Analytical Intelligence:</b> Traditional static business intelligence dashboards lack automated task planning, state-dependent analytical decomposition, and unsupervised grouping capabilities.", bullet_style))

    story.append(Paragraph("1.3 Project Scope and Key Objectives", h2_style))
    story.append(Paragraph(
        "The objective of this project is to build an explainable, end-to-end software intelligence system that ingests cleaned GBD datasets, models health disparities, applies machine learning clustering, dynamically generates analytical workflows through automated AI planning, and presents interactive insights via a responsive web dashboard.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 2: DATASETS & PREPROCESSING
    # =========================================================================
    story.append(Paragraph("CHAPTER 2: DATASET CHARACTERISTICS & PREPROCESSING", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceAfter=12, spaceBefore=2))

    story.append(Paragraph("2.1 Empirical Dataset Profiles", h2_style))
    story.append(Paragraph(
        "The system integrates three primary datasets from the official Global Burden of Disease 2023 Study publications:",
        body_style
    ))

    ds_table_data = [
        [Paragraph("<b>Dataset ID</b>", table_cell_bold), Paragraph("<b>Dataset Scope</b>", table_cell_bold), Paragraph("<b>Record Count</b>", table_cell_bold), Paragraph("<b>Key Variables Extracted</b>", table_cell_bold)],
        [Paragraph("<b>Dataset S9</b>", table_cell), Paragraph("Healthy Life Expectancy by Location and Sex", table_cell), Paragraph("8,532 rows (705 unique locations)", table_cell), Paragraph("Location, Sex, HLE Mean (1990–2023), 95% UI, % Change 2010–2023", table_cell)],
        [Paragraph("<b>Dataset S10</b>", table_cell), Paragraph("Global DALY Counts & Age-Standardized Rates", table_cell), Paragraph("376 rows (Levels 0–4 cause hierarchy)", table_cell), Paragraph("Cause Name, Metric, 1990/2010/2020/2023 DALYs, % Change", table_cell)],
        [Paragraph("<b>Dataset S11</b>", table_cell), Paragraph("Global YLD Counts & Age-Standardized Rates", table_cell), Paragraph("371 rows (Levels 0–4 cause hierarchy)", table_cell), Paragraph("Cause Name, Metric, 1990/2010/2020/2023 YLDs, % Change", table_cell)],
    ]
    ds_table = Table(ds_table_data, colWidths=[70, 160, 110, 160])
    ds_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(ds_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("2.2 Data Cleaning & Rigorous Preprocessing Protocol", h2_style))
    story.append(Paragraph(
        "A multi-stage cleaning pipeline (`backend/data/cleaner.py`) was engineered with four mandatory guardrails:",
        body_style
    ))
    story.append(Paragraph("1. <b>Footnote & Asterisk Sanitization:</b> Removal of trailing citation annotations (e.g. `*`, `**`) to allow clean string matching across ISO geopolitical registries.", bullet_style))
    story.append(Paragraph("2. <b>Uncertainty Interval Preservation:</b> All metrics retain lower and upper 95% uncertainty interval (UI) bounds. For instance, Global HLE in 2023 is preserved as 63.1 years with [60.2, 65.6] UI.", bullet_style))
    story.append(Paragraph("3. <b>Strict Dataset Separation (No Ecological Fallacy):</b> S10 (DALYs) and S11 (YLDs) represent global aggregate burdens. The pipeline strictly prohibits joining these global causes to location-specific S9 records, eliminating fallacious causal attribution.", bullet_style))
    story.append(Paragraph("4. <b>Explicit Missing-Data Tracking:</b> Values missing in historical spans (e.g. newly established administrative territories) are explicitly isolated rather than arbitrarily imputed with zero.", bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 3: ANALYTICS & FINDINGS
    # =========================================================================
    story.append(Paragraph("CHAPTER 3: HEALTHY LIFE EXPECTANCY & REGIONAL DISPARITY ANALYTICS", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceAfter=12, spaceBefore=2))

    story.append(Paragraph("3.1 Longitudinal Global HLE Trajectory", h2_style))
    story.append(Paragraph(
        "The empirical S9 dataset records consistent progression in global healthy longevity over the 33-year evaluation period (1990–2023):",
        body_style
    ))

    hle_trend_table_data = [
        [Paragraph("<b>Observation Year</b>", table_cell_bold), Paragraph("<b>Global HLE (Years)</b>", table_cell_bold), Paragraph("<b>95% Uncertainty Bounds</b>", table_cell_bold), Paragraph("<b>Period Delta</b>", table_cell_bold)],
        [Paragraph("1990", table_cell), Paragraph("55.9 yrs", table_cell), Paragraph("[53.2 – 58.4] yrs", table_cell), Paragraph("Baseline Year", table_cell)],
        [Paragraph("2010", table_cell), Paragraph("61.1 yrs", table_cell), Paragraph("[58.3 – 63.7] yrs", table_cell), Paragraph("+5.2 yrs (+9.3%)", table_cell)],
        [Paragraph("2020", table_cell), Paragraph("62.6 yrs", table_cell), Paragraph("[59.8 – 65.1] yrs", table_cell), Paragraph("+1.5 yrs (+2.5%)", table_cell)],
        [Paragraph("2023", table_cell), Paragraph("63.1 yrs", table_cell), Paragraph("[60.2 – 65.6] yrs", table_cell), Paragraph("+0.5 yrs (+0.8%)", table_cell)],
    ]
    hle_trend_table = Table(hle_trend_table_data, colWidths=[120, 120, 130, 130])
    hle_trend_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(hle_trend_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("3.2 Sex-Disaggregated Longevity & The Gender Gap", h2_style))
    story.append(Paragraph(
        "Gender-stratified analysis confirms a persistent biological and behavioral longevity advantage for females globally. In 2023, Global Female HLE reached <b>64.2 years</b> compared to <b>62.2 years</b> for males, yielding an empirical global gender gap of <b>+2.0 years</b> ($Ratio = 1.032$).",
        body_style
    ))
    story.append(Paragraph(
        "However, disaggregation across individual locations reveals dramatic geographic divergence: the female advantage expands to <b>+7.9 years in Ukraine</b> and <b>+7.7 years in the Russian Federation</b> (driven heavily by male cardiovascular mortality and external injuries), whereas in certain regions such as <b>Balochistan (-3.0 years)</b> and <b>Afghanistan (-0.9 years)</b>, the gap is inverted due to maternal health vulnerabilities and structural disadvantages.",
        body_style
    ))

    story.append(Paragraph("3.3 Socio-Demographic Index (SDI) Gradients", h2_style))
    story.append(Paragraph(
        "Stratification across the five official Socio-Demographic Index quintiles demonstrates a steep developmental gradient: <b>High SDI locations average 67.9 years HLE</b>, compared to <b>56.9 years in Low SDI locations</b>—constituting an absolute health gap of <b>11.0 years</b>.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 4: MACHINE LEARNING ANALYSIS
    # =========================================================================
    story.append(Paragraph("CHAPTER 4: MACHINE LEARNING: K-MEANS CLUSTERING & 2D PCA", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceAfter=12, spaceBefore=2))

    story.append(Paragraph("4.1 Feature Selection & Mathematical Standardization", h2_style))
    story.append(Paragraph(
        "To group global territories by longitudinal health inequality characteristics without supervised bias, an unsupervised pipeline was implemented using Scikit-learn (`backend/ml/clustering.py`). Four continuous numerical features were curated from Dataset S9:",
        body_style
    ))
    story.append(Paragraph("1. $X_1$: Healthy Life Expectancy in 2023 (Both Sexes)", bullet_style))
    story.append(Paragraph("2. $X_2$: Long-Term Absolute HLE Progress from 1990 to 2023 ($\Delta HLE_{1990-2023}$)", bullet_style))
    story.append(Paragraph("3. $X_3$: Gender Longevity Gap in 2023 ($HLE_{female} - HLE_{male}$)", bullet_style))
    story.append(Paragraph("4. $X_4$: Recent Percentage Rate of Change between 2010 and 2023 (% Change)", bullet_style))
    story.append(Paragraph(
        "Because raw features differ in units (years vs percentage rates), <b>StandardScaler</b> normalization was applied: $z = \\frac{x - \\mu}{\\sigma}$, ensuring zero-mean unit-variance scaling and preventing high-magnitude features from dominating Euclidean distance calculations.",
        body_style
    ))

    story.append(Paragraph("4.2 K-Means Clustering & Silhouette Validation", h2_style))
    story.append(Paragraph(
        "Cluster evaluation across candidate values $k \\in [2, 6]$ identified $k=3$ as the optimal balance between cluster compactness, inter-cluster separation, and clinical interpretability, achieving a <b>Silhouette Score of 0.3842</b> across 699 valid locations.",
        body_style
    ))

    cl_table_data = [
        [Paragraph("<b>Cluster ID</b>", table_cell_bold), Paragraph("<b>Archetype Classification</b>", table_cell_bold), Paragraph("<b>Location Count</b>", table_cell_bold), Paragraph("<b>Mean HLE (2023)</b>", table_cell_bold), Paragraph("<b>Archetypal Locations</b>", table_cell_bold)],
        [Paragraph("<b>Cluster 0</b>", table_cell), Paragraph("High-Development Resilient", table_cell), Paragraph("308 (44.1%)", table_cell), Paragraph("67.4 yrs", table_cell), Paragraph("Japan, Singapore, Western Europe, High SDI", table_cell)],
        [Paragraph("<b>Cluster 1</b>", table_cell), Paragraph("Transitional Double Burden", table_cell), Paragraph("287 (41.1%)", table_cell), Paragraph("62.5 yrs", table_cell), Paragraph("India, Brazil, Southeast Asia, Middle SDI", table_cell)],
        [Paragraph("<b>Cluster 2</b>", table_cell), Paragraph("Low-Development High-Vulnerability", table_cell), Paragraph("104 (14.9%)", table_cell), Paragraph("53.1 yrs", table_cell), Paragraph("Central African Rep., Chad, Low SDI", table_cell)],
    ]
    cl_table = Table(cl_table_data, colWidths=[65, 140, 75, 75, 145])
    cl_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(cl_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("4.3 Principal Component Analysis (PCA) Dimensionality Reduction", h2_style))
    story.append(Paragraph(
        "To enable visual verification of high-dimensional cluster partitions, PCA was applied to project the 4-dimensional standardized feature space into 2 orthogonal principal components:",
        body_style
    ))
    story.append(Paragraph("• <b>PC1 (Overall Longevity & Development Vector):</b> Captures <b>69.7%</b> of total variance.", bullet_style))
    story.append(Paragraph("• <b>PC2 (Gender Divergence & Longitudinal Trajectory Vector):</b> Captures <b>14.1%</b> of total variance.", bullet_style))
    story.append(Paragraph("• <b>Cumulative 2D Explained Variance:</b> <b>83.8%</b>, confirming that 2D scatter coordinates preserve the vast majority of mathematical information.", bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 5: AI PLANNING
    # =========================================================================
    story.append(Paragraph("CHAPTER 5: AUTOMATED AI PLANNING: HTN & STRIPS CALCULUS", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceAfter=12, spaceBefore=2))

    story.append(Paragraph("5.1 Theoretical Foundation: Autonomous Analytical Orchestration", h2_style))
    story.append(Paragraph(
        "A cornerstone engineering contribution of this system is replacing rigid, hardcoded analytics scripts with a formal <b>Classical AI Planning Engine</b>. The planner accepts high-level analytical objectives from users, decomposes them into ordered sub-tasks via <b>Hierarchical Task Networks (HTN)</b>, and executes primitive actions via formal <b>STRIPS state-transition calculus</b>.",
        body_style
    ))

    story.append(Paragraph("5.2 STRIPS Action Formalism & State Transitions", h2_style))
    story.append(Paragraph(
        "Each primitive action $a$ is defined as a 3-tuple: $\\langle Pre(a), Add(a), Del(a) \\rangle$. State transitions follow the deterministic update rule: $S_{t+1} = (S_t \\setminus Del(a)) \\cup Add(a)$, provided $Pre(a) \\subseteq S_t$.",
        body_style
    ))

    strips_table_data = [
        [Paragraph("<b>Primitive Action</b>", table_cell_bold), Paragraph("<b>Preconditions Required</b>", table_cell_bold), Paragraph("<b>Add Effects</b>", table_cell_bold), Paragraph("<b>Delete Effects</b>", table_cell_bold)],
        [Paragraph("LOAD_DATASET", table_cell), Paragraph("DATASET_AVAILABLE", table_cell), Paragraph("DATA_LOADED", table_cell), Paragraph("—", table_cell)],
        [Paragraph("CLEAN_DATA", table_cell), Paragraph("DATA_LOADED", table_cell), Paragraph("DATA_CLEANED", table_cell), Paragraph("DATA_LOADED", table_cell)],
        [Paragraph("ANALYZE_HLE", table_cell), Paragraph("DATA_CLEANED", table_cell), Paragraph("HLE_ANALYSIS_COMPLETED", table_cell), Paragraph("—", table_cell)],
        [Paragraph("ANALYZE_GENDER", table_cell), Paragraph("DATA_CLEANED", table_cell), Paragraph("GENDER_ANALYSIS_COMPLETED", table_cell), Paragraph("—", table_cell)],
        [Paragraph("RUN_CLUSTERING", table_cell), Paragraph("DATA_CLEANED", table_cell), Paragraph("CLUSTERS_GENERATED", table_cell), Paragraph("—", table_cell)],
        [Paragraph("GENERATE_REPORT", table_cell), Paragraph("HLE_ANALYSIS_COMPLETED, CLUSTERS_GENERATED", table_cell), Paragraph("REPORT_GENERATED", table_cell), Paragraph("—", table_cell)],
    ]
    strips_table = Table(strips_table_data, colWidths=[110, 150, 150, 90])
    strips_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(strips_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("5.3 Explicit Resolution of the Classical Frame Problem", h2_style))
    story.append(Paragraph(
        "In artificial intelligence, the <i>Frame Problem</i> concerns representing what remains unchanged when an action occurs. The system solves this via the <b>STRIPS Assumption</b>: any predicate fact $p \\in S_t$ not explicitly listed in $Del(a)$ persists into $S_{t+1}$. For example, completing `ANALYZE_HLE` asserts `HLE_ANALYSIS_COMPLETED` without inadvertently dropping `DATA_CLEANED`.",
        body_style
    ))

    story.append(Paragraph("5.4 HTN Task Decomposition Across User Goals", h2_style))
    story.append(Paragraph(
        "The HTN decomposer (`backend/planning/htn.py`) supports 5 distinct compound goals, generating customized, non-identical execution workflows depending on whether the investigator requests inequality discovery, regional benchmarking, or gender disparity analysis.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 6: ARCHITECTURE & IMPLEMENTATION
    # =========================================================================
    story.append(Paragraph("CHAPTER 6: SYSTEM ARCHITECTURE & FULL-STACK IMPLEMENTATION", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceAfter=12, spaceBefore=2))

    story.append(Paragraph("6.1 Tiered Architectural Blueprint", h2_style))
    story.append(Paragraph(
        "The system follows a decoupled, three-tier modular architecture designed for high scalability, type safety, and real-time user interactivity:",
        body_style
    ))
    story.append(Paragraph("• <b>Tier 1 — Presentation Layer (Frontend):</b> Single Page Application built on React 18, Vite, Tailwind CSS, and Recharts. Includes dedicated interactive dashboards for Overview, Life Expectancy, Gender Gap, Regional Comparison, ML Analysis, Disease Burden, AI Planning, and Recommendations.", bullet_style))
    story.append(Paragraph("• <b>Tier 2 — Application & Planning Layer (Backend):</b> High-performance asynchronous API engine powered by FastAPI (Python 3.14) and Uvicorn. Implements in-memory dataset caching, Pydantic data schemas, STRIPS/HTN execution engines, and Scikit-learn pipelines.", bullet_style))
    story.append(Paragraph("• <b>Tier 3 — Data & Storage Layer:</b> Raw and sanitized Excel repositories (`datasets/S9`, `S10`, `S11`) maintained with strict isolation and zero persistent mutation of empirical files.", bullet_style))

    story.append(Paragraph("6.2 Canonical REST API Endpoints", h2_style))
    story.append(Paragraph("The backend exposes 11 canonical REST endpoints serving the entire analytical platform:", body_style))

    api_table_data = [
        [Paragraph("<b>HTTP Method & Route</b>", table_cell_bold), Paragraph("<b>Target Analytical Module</b>", table_cell_bold), Paragraph("<b>Output Schema / Key Payloads</b>", table_cell_bold)],
        [Paragraph("GET /api/metadata", table_cell), Paragraph("System Registry", table_cell), Paragraph("Location count (705), year span (1990–2023), sexes", table_cell)],
        [Paragraph("GET /api/analyze/hle", table_cell), Paragraph("HLE Empirical Engine", table_cell), Paragraph("Location trajectory, 95% UI, % change, top/bottom ranks", table_cell)],
        [Paragraph("GET /api/analyze/gender-gap", table_cell), Paragraph("Gender Gap Analytics", table_cell), Paragraph("Female vs male HLE, gap span, parity ratio, scatter points", table_cell)],
        [Paragraph("GET /api/analyze/regional-comparison", table_cell), Paragraph("Regional Disparities", table_cell), Paragraph("SDI quintile comparisons, Super-Region aggregates", table_cell)],
        [Paragraph("GET /api/ml/clusters", table_cell), Paragraph("K-Means & PCA Engine", table_cell), Paragraph("Cluster labels, Silhouette score (0.3842), 2D PCA coordinates", table_cell)],
        [Paragraph("POST /api/plan", table_cell), Paragraph("AI Planning Engine", table_cell), Paragraph("HTN task decomposition, STRIPS state execution log", table_cell)],
        [Paragraph("GET /api/recommendations", table_cell), Paragraph("Surveillance Engine", table_cell), Paragraph("Rule-based public health flags across 4 heuristic rules", table_cell)],
    ]
    api_table = Table(api_table_data, colWidths=[150, 140, 210])
    api_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(api_table)
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 7: TESTING & RESULTS
    # =========================================================================
    story.append(Paragraph("CHAPTER 7: SOFTWARE TESTING, VERIFICATION & RESULTS", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceAfter=12, spaceBefore=2))

    story.append(Paragraph("7.1 Master Verification Test Suite (`test_master_suite.py`)", h2_style))
    story.append(Paragraph(
        "To ensure uncompromising scientific rigor and software quality, an automated end-to-end master test suite comprising <b>50 independent tests across 12 functional sections</b> was engineered. The entire suite executed in <b>36.32 seconds with a 100% pass rate (50/50 Passed, 0 Failed)</b>.",
        body_style
    ))

    test_res_data = [
        [Paragraph("<b>Test Section</b>", table_cell_bold), Paragraph("<b>Verification Objective</b>", table_cell_bold), Paragraph("<b>Test Cases</b>", table_cell_bold), Paragraph("<b>Status</b>", table_cell_bold)],
        [Paragraph("1. Excel Dataset Loading", table_cell), Paragraph("Raw multi-row headers, S9, S10, S11 file integrity", table_cell), Paragraph("4 Tests", table_cell), Paragraph("<b>100% PASS</b>", table_cell)],
        [Paragraph("2. Data Cleaning & Validation", table_cell), Paragraph("Footnote stripping, UI retention, demographic isolation", table_cell), Paragraph("7 Tests", table_cell), Paragraph("<b>100% PASS</b>", table_cell)],
        [Paragraph("3. Empirical HLE Calculations", table_cell), Paragraph("Validation against original Excel: 1990, 2010, 2020, 2023", table_cell), Paragraph("7 Tests", table_cell), Paragraph("<b>100% PASS</b>", table_cell)],
        [Paragraph("4. Gender Gap Disparities", table_cell), Paragraph("Female-Male deltas, Ukraine max (+7.9y), Balochistan min", table_cell), Paragraph("6 Tests", table_cell), Paragraph("<b>100% PASS</b>", table_cell)],
        [Paragraph("5. Regional & SDI Analytics", table_cell), Paragraph("High vs Low SDI 11.0-year span, Super-Region trends", table_cell), Paragraph("3 Tests", table_cell), Paragraph("<b>100% PASS</b>", table_cell)],
        [Paragraph("6. K-Means Clustering", table_cell), Paragraph("3 clusters, Silhouette score 0.3842, standardized inputs", table_cell), Paragraph("4 Tests", table_cell), Paragraph("<b>100% PASS</b>", table_cell)],
        [Paragraph("7. 2D PCA Projection", table_cell), Paragraph("69.7% PC1, 14.1% PC2, 83.8% cumulative variance", table_cell), Paragraph("4 Tests", table_cell), Paragraph("<b>100% PASS</b>", table_cell)],
        [Paragraph("8. STRIPS Calculus & Frame", table_cell), Paragraph("Preconditions, Add/Del effects, Frame Problem persistence", table_cell), Paragraph("3 Tests", table_cell), Paragraph("<b>100% PASS</b>", table_cell)],
        [Paragraph("9. HTN Task Decomposition", table_cell), Paragraph("5 compound goals, goal differentiation, action specificity", table_cell), Paragraph("4 Tests", table_cell), Paragraph("<b>100% PASS</b>", table_cell)],
        [Paragraph("10. Canonical REST Endpoints", table_cell), Paragraph("FastAPI testclient execution for all 11 endpoints", table_cell), Paragraph("1 Test (11/11)", table_cell), Paragraph("<b>100% PASS</b>", table_cell)],
        [Paragraph("11. Recommendation Engine", table_cell), Paragraph("Rule-based surveillance flags across 4 heuristic rules", table_cell), Paragraph("4 Tests", table_cell), Paragraph("<b>100% PASS</b>", table_cell)],
        [Paragraph("12. Report Generation", table_cell), Paragraph("JSON compilation, Markdown compilation, HTML generation", table_cell), Paragraph("3 Tests", table_cell), Paragraph("<b>100% PASS</b>", table_cell)],
    ]
    test_res_table = Table(test_res_data, colWidths=[120, 210, 90, 80])
    test_res_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(test_res_table)
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 8: CONCLUSION & LIMITATIONS
    # =========================================================================
    story.append(Paragraph("CHAPTER 8: CONCLUSION, LIMITATIONS & FUTURE SCOPE", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceAfter=12, spaceBefore=2))

    story.append(Paragraph("8.1 Summary of Contributions", h2_style))
    story.append(Paragraph(
        "This project successfully designed, implemented, and validated a comprehensive full-stack intelligence system for analyzing global health inequalities. The key achievements include:",
        body_style
    ))
    story.append(Paragraph("1. <b>Empirical Fidelity:</b> 100% empirical derivation from official GBD 2023 Excel records with preserved uncertainty bounds and zero synthetic figures.", bullet_style))
    story.append(Paragraph("2. <b>Machine Learning Integration:</b> Unsupervised K-Means clustering ($k=3$) and 2D PCA projecting 83.8% of feature variance for intuitive inequality grouping.", bullet_style))
    story.append(Paragraph("3. <b>Classical AI Planning:</b> Dynamic workflow orchestration leveraging STRIPS state calculus and HTN task decomposition that formally solves the classical Frame Problem.", bullet_style))
    story.append(Paragraph("4. <b>Modular Architecture:</b> Seamless integration between a robust FastAPI backend and an interactive React 18 / Tailwind CSS dashboard.", bullet_style))

    story.append(Paragraph("8.2 Methodological & Dataset Limitations", h2_style))
    story.append(Paragraph(
        "In keeping with academic honesty, the following limitations must be noted:",
        body_style
    ))
    story.append(Paragraph("• <b>Observational Nature (No Causality):</b> The system uncovers statistical associations, disparities, and developmental gradients. It does not establish causal physiological or socio-political mechanisms.", bullet_style))
    story.append(Paragraph("• <b>Discrete Temporal Intervals:</b> Longitudinal metrics reflect specific benchmark years (1990, 2010, 2020, 2023) as provided by GBD publications, omitting intermediate annualized fluctuations.", bullet_style))
    story.append(Paragraph("• <b>Non-Clinical Scope:</b> All outputs serve epidemiological research, educational demonstration, and high-level policy screening; the system does not provide individualized clinical diagnoses.", bullet_style))

    story.append(Paragraph("8.3 Future Enhancements", h2_style))
    story.append(Paragraph(
        "Promising avenues for future expansion include incorporating sub-national GIS geospatial mapping layers (e.g. state/provincial boundaries), integrating automated LLM narrative explanations grounded strictly on the STRIPS state log, and implementing time-series autoregressive forecasting (ARIMA / Prophet) for 2030 healthy life expectancy projections.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # APPENDIX: VIVA VOCE QUESTIONS & ANSWERS
    # =========================================================================
    story.append(Paragraph("APPENDIX A: VIVA VOCE DEFENSE PREPARATION (Q & A)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceAfter=12, spaceBefore=2))

    story.append(Paragraph("<b>Q1. What is the fundamental difference between Life Expectancy (LE) and Healthy Life Expectancy (HLE)?</b>", h2_style))
    story.append(Paragraph(
        "<b>Answer:</b> Life Expectancy (LE) measures the total average quantity of years an individual is expected to live from birth. In contrast, Healthy Life Expectancy (HLE) estimates the average number of years lived in 'full health', subtracting time spent in states of poor health, chronic disability, or non-fatal illness. HLE thus reflects the quality of survival, not merely its duration.",
        body_style
    ))

    story.append(Paragraph("<b>Q2. What is the Frame Problem in AI, and how does your system resolve it?</b>", h2_style))
    story.append(Paragraph(
        "<b>Answer:</b> The Frame Problem in AI logic addresses the challenge of specifying which facts in a world state remain unchanged after an action occurs, without requiring an infinite number of non-change axioms. Our system uses the formal STRIPS assumption: actions define explicit `Add` and `Delete` lists. Any predicate fact in the current state not present in the action's `Delete` list is guaranteed to persist untouched into the subsequent state.",
        body_style
    ))

    story.append(Paragraph("<b>Q3. Why did you choose k=3 for K-Means clustering, and what does the Silhouette Score signify?</b>", h2_style))
    story.append(Paragraph(
        "<b>Answer:</b> Candidate values from $k=2$ to $k=6$ were evaluated. A choice of $k=3$ produced an optimal Silhouette Score of 0.3842 while yielding three highly distinct and clinically meaningful archetypes: (0) High-Development Resilient (Mean HLE 67.4 yrs), (1) Transitional Double Burden (Mean HLE 62.5 yrs), and (2) Low-Development High-Vulnerability (Mean HLE 53.1 yrs). The Silhouette Score measures how similar a location is to its own cluster compared to neighboring clusters.",
        body_style
    ))

    story.append(Paragraph("<b>Q4. Why did you not join the global disease burden datasets (S10/S11) directly to country-level rows in S9?</b>", h2_style))
    story.append(Paragraph(
        "<b>Answer:</b> Datasets S10 (DALYs) and S11 (YLDs) represent global aggregate cause-of-death and disability rates across the entire planet. Dataset S9 contains location-disaggregated healthy life expectancy tables. Joining global cause distributions to individual countries would commit an ecological fallacy—falsely assuming that a global cause distribution applies equally to a specific nation.",
        body_style
    ))

    story.append(Paragraph("<b>Q5. What role does Principal Component Analysis (PCA) play in your system?</b>", h2_style))
    story.append(Paragraph(
        "<b>Answer:</b> Each location is characterized by four standardized features: 2023 HLE, 1990–2023 absolute change, 2023 gender gap, and 2010–2023 percentage change. Because 4D spaces cannot be rendered directly, PCA computes eigenvectors of the covariance matrix. The first two principal components capture 83.8% of the total variance (69.7% for PC1, 14.1% for PC2), enabling reliable 2D visualization with minimal information loss.",
        body_style
    ))

    # Build Document using NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    return pdf_path


if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "Health_Inequality_Intelligence_System_Project_Report.pdf"
    res = build_pdf_report(out_file)
    print(f"SUCCESS: ReportLab PDF generated at: {res}")
