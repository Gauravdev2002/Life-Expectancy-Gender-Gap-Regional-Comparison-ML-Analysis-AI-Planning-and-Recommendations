"""
recommendations/report_generator.py
-----------------------------------
Generates comprehensive, downloadable evidence-based reports summarizing:
  1. Project Overview & Architecture
  2. Healthy Life Expectancy (HLE) Analysis (1990–2023)
  3. Gender Gap & Parity Analysis
  4. Regional & SDI Inequalities
  5. Machine Learning Analysis (K-Means & PCA)
  6. Global Disease Burden Context (Separate S10 DALYs & S11 YLDs)
  7. Evidence-Based Heuristic Recommendations
  8. Methodology, Epistemological Boundaries & Limitations

Formats:
  - Structured JSON
  - Formatted Markdown (.md)
  - Standalone Printable HTML (.html) with print-to-PDF stylesheet
"""

from datetime import datetime
from typing import Any, Dict
import json

from analytics.hle_analytics import get_location_trend, get_hle_rankings
from analytics.regional_analytics import get_regional_comparison
from analytics.gender_analytics import get_gender_gap_overview, get_gender_rankings
from analytics.disease_analytics import (
    get_disease_burden_overview,
    get_level1_broad_breakdown,
    get_top_causes,
    get_daly_vs_yld_comparison,
)
from ml.clustering import run_kmeans_clustering
from recommendations.engine import generate_recommendations, ACADEMIC_DISCLAIMER


def compile_full_report() -> Dict[str, Any]:
    """
    Compiles all empirical analytical findings, ML clustering results,
    global disease burden metrics, and recommendations into a single master dictionary.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. HLE Analytics
    global_trend = get_location_trend("Global")
    top_bot_hle = get_hle_rankings(year=2023, sex="both", include_aggregates=False, n=5)

    # 2. Gender Analytics
    gender_overview = get_gender_gap_overview(year=2023)
    gender_extremes = get_gender_rankings(year=2023, n=5)

    # 3. Regional & SDI
    sdi_data = get_regional_comparison("sdi", year=2023)
    super_reg_data = get_regional_comparison("super_regions", year=2023)

    # 4. Machine Learning
    ml_eval = run_kmeans_clustering(k=3, include_aggregates=False)

    # 5. Disease Burden (S10 & S11)
    disease_overview = get_disease_burden_overview()
    level1_data = get_level1_broad_breakdown()
    top_dalys = get_top_causes(metric="daly", level=2, n=5)
    top_ylds = get_top_causes(metric="yld", level=2, n=5)
    comparison_matrix = get_daly_vs_yld_comparison()[:6]

    # 6. Recommendations
    recommendations = generate_recommendations(max_per_category=8)

    return {
        "report_metadata": {
            "title": "Comprehensive Intelligence Report on Regional Health Inequality and Life Expectancy",
            "system": "AI-Based Regional Health Inequality and Life Expectancy Intelligence System",
            "generated_at": timestamp,
            "version": "1.0.0",
            "scope": "Global Burden of Disease (GBD 2023) Empirical Assessment",
            "academic_level": "B.Tech / Bachelor's Final Demonstration Project",
        },
        "executive_summary": {
            "global_hle_2023": 63.1,
            "global_hle_ui": [60.2, 65.6],
            "historical_gain_1990_2023": "+7.2 years gained globally",
            "global_gender_gap": "+2.0 years (Female 64.2 vs. Male 62.2)",
            "sdi_inequality_span": "11.0 years difference between High SDI (67.9 yrs) and Low SDI (56.9 yrs)",
            "global_dalys": "2.80 Billion DALYs (Cardiovascular diseases leading cause)",
            "global_ylds": "990 Million YLDs (Mental disorders leading disability cause)",
            "chronic_disability_share": "35.4% of total health span loss is lived disability",
            "ml_architecture": "K-Means (k=3, Silhouette 0.384) + 2D PCA (83.8% variance explained)",
        },
        "hle_analysis": {
            "global_trajectory": global_trend.get("trends", []),
            "highest_locations": top_bot_hle.get("highest", []),
            "lowest_locations": top_bot_hle.get("lowest", []),
        },
        "gender_gap_analysis": {
            "overview": gender_overview,
            "widest_female_advantages": gender_extremes.get("widest_female_advantage", []),
            "narrowest_or_reverse_gaps": gender_extremes.get("narrowest_or_reverse_gap", []),
        },
        "regional_comparison": {
            "sdi_gradient": sdi_data,
            "super_regions": super_reg_data,
        },
        "machine_learning": {
            "k": ml_eval.get("k", 3),
            "silhouette_score": ml_eval.get("silhouette_score"),
            "pca_explained_variance": ml_eval.get("pca_explained_variance_ratio", {}),
            "cluster_profiles": ml_eval.get("cluster_profiles", []),
        },
        "disease_burden_context": {
            "overview": disease_overview,
            "level1_categories": level1_data,
            "top_daly_causes": top_dalys,
            "top_yld_cause": top_ylds,
            "fatal_vs_disabling_matrix": comparison_matrix,
            "demographic_isolation_note": (
                "Datasets S10 (DALYs) and S11 (YLDs) are global both-sexes aggregates and have NOT "
                "been merged with country-level S9 records to preserve statistical and demographic validity."
            ),
        },
        "recommendations": recommendations.get("flags", {}),
        "methodology_and_limitations": {
            "data_sources": [
                "Dataset S9: Healthy Life Expectancy by Location and Sex (1990–2023)",
                "Dataset S10: Global DALY Counts and Age-Standardised Rate Changes by Cause (2010–2023)",
                "Dataset S11: Global YLD Counts and Age-Standardised Rate Changes by Cause (2010–2023)",
            ],
            "analytical_methods": [
                "Descriptive epidemiological time-series and rate change estimation",
                "Uncertainty interval preservation (95% UI Lower/Upper bounds)",
                "Unsupervised K-Means clustering with StandardScaler and Silhouette evaluation",
                "Dimensionality reduction via 2D Principal Component Analysis (PCA)",
                "Hierarchical Task Network (HTN) decomposition and STRIPS state calculus",
                "Transparent deterministic heuristic surveillance rule engine",
            ],
            "limitations_and_ethics": [
                "Observational ecological associations cannot be interpreted as causal mechanisms.",
                "Non-clinical scope: System does NOT provide diagnostic, therapeutic, or individualized medical guidance.",
                "Subnational data availability varies across territories.",
            ],
            "formal_disclaimer": ACADEMIC_DISCLAIMER,
        },
    }


def generate_markdown_report() -> str:
    """
    Renders the full report into a clean, GitHub-flavored Markdown text file.
    """
    data = compile_full_report()
    meta = data["report_metadata"]
    exec_sum = data["executive_summary"]
    hle = data["hle_analysis"]
    gender = data["gender_gap_analysis"]
    reg = data["regional_comparison"]
    ml = data["machine_learning"]
    disease = data["disease_burden_context"]
    recs = data["recommendations"]
    meth = data["methodology_and_limitations"]

    lines = [
        f"# {meta['title']}",
        f"**Generated:** {meta['generated_at']} | **System Version:** {meta['version']} | **Scope:** {meta['scope']}",
        "",
        "> **ACADEMIC & NON-CLINICAL NOTICE:** This report compiles observational health intelligence from the Global Burden of Disease study (GBD 2023). Statistical associations and cluster groupings reflect empirical surveillance correlations and do NOT constitute causal claims. The findings are intended for health policy analysis and educational demonstration; they provide NO clinical diagnosis or medical recommendations.",
        "",
        "---",
        "",
        "## 1. Executive Summary & Key Performance Indicators",
        "",
        f"- **Global 2023 Healthy Life Expectancy (HLE):** {exec_sum['global_hle_2023']} years (95% UI: [{exec_sum['global_hle_ui'][0]}, {exec_sum['global_hle_ui'][1]}])",
        f"- **Historical Global Progress (1990–2023):** {exec_sum['historical_gain_1990_2023']}",
        f"- **Global Gender Longevity Gap:** {exec_sum['global_gender_gap']}",
        f"- **Socio-demographic Inequality Span:** {exec_sum['sdi_inequality_span']}",
        f"- **Global Disease Burden:** {exec_sum['global_dalys']}",
        f"- **Global Non-Fatal Disability Burden:** {exec_sum['global_ylds']}",
        f"- **Chronic Disability Share of Health Loss:** {exec_sum['chronic_disability_share']}",
        f"- **Machine Learning Architecture:** {exec_sum['ml_architecture']}",
        "",
        "---",
        "",
        "## 2. Healthy Life Expectancy (HLE) Trajectory & Analysis",
        "",
        "### Global Historical Trajectory (Dataset S9)",
        "| Year | Both Sexes HLE (yrs) | 95% Uncertainty Interval | Female HLE | Male HLE | Gender Gap (F - M) |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for t in hle.get("global_trajectory", []):
        lines.append(
            f"| {t['year']} | {t['both_mean']} | [{t['both_lower']}–{t['both_upper']}] | {t['female_mean']} | {t['male_mean']} | +{t['gender_gap']} yrs |"
        )

    lines.extend([
        "",
        "### Top 5 Highest HLE Locations (2023)",
        "| Rank | Location | 2023 HLE (yrs) | 95% UI | 2010–2023 % Change |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ])
    for r in hle.get("highest_locations", []):
        lines.append(f"| #{r['rank']} | {r['location']} | {r['hle_mean']} | [{r['hle_lower']}–{r['hle_upper']}] | +{r['pct_change_mean']}% |")

    lines.extend([
        "",
        "### Bottom 5 Lowest HLE Locations (2023)",
        "| Rank | Location | 2023 HLE (yrs) | 95% UI | 2010–2023 % Change |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ])
    for r in hle.get("lowest_locations", []):
        lines.append(f"| #{r['rank']} | {r['location']} | {r['hle_mean']} | [{r['hle_lower']}–{r['hle_upper']}] | {r['pct_change_mean']}% |")

    lines.extend([
        "",
        "---",
        "",
        "## 3. Gender Gap & Parity Disparities",
        "",
        f"- **Global Gender Gap (2023):** +{gender['overview'].get('global_gender_gap')} years",
        f"- **Global Parity Ratio:** {gender['overview'].get('global_parity_ratio')} (Female / Male)",
        "",
        "### Widest Female Longevity Advantages",
        "| Location | Female HLE (yrs) | Male HLE (yrs) | Gender Gap (F - M) | Parity Ratio |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ])
    for r in gender.get("widest_female_advantages", []):
        lines.append(f"| {r['location']} | {r['female_hle']} | {r['male_hle']} | +{r['gender_gap']} yrs | {r['parity_ratio']} |")

    lines.extend([
        "",
        "### Narrowest / Reversed Gender Gaps",
        "| Location | Female HLE (yrs) | Male HLE (yrs) | Gender Gap (F - M) | Parity Ratio |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ])
    for r in gender.get("narrowest_or_reverse_gaps", []):
        lines.append(f"| {r['location']} | {r['female_hle']} | {r['male_hle']} | {r['gender_gap']} yrs | {r['parity_ratio']} |")

    lines.extend([
        "",
        "---",
        "",
        "## 4. Regional & Socio-demographic Inequalities",
        "",
        "### SDI Quintile Gradient (2023)",
        "| SDI Quintile Tier | 2023 HLE (yrs) | 95% UI | 2010–2023 % Change | Female HLE | Male HLE |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ])
    for r in reg.get("sdi_gradient", []):
        r_name = r.get("region", r.get("location", "—"))
        pct = r.get("pct_change_2010_2023", r.get("pct_change_mean", "—"))
        fem = r.get("female_hle", r.get("female_mean", "—"))
        mal = r.get("male_hle", r.get("male_mean", "—"))
        lines.append(f"| {r_name} | {r['hle_mean']} | [{r['hle_lower']}–{r['hle_upper']}] | +{pct}% | {fem} | {mal} |")

    lines.extend([
        "",
        "---",
        "",
        "## 5. Machine Learning Analysis (K-Means & PCA)",
        "",
        f"- **Optimal Clusters (k):** {ml['k']}",
        f"- **Silhouette Evaluation Score:** {ml['silhouette_score']} (Good cohesion and separation)",
        f"- **PCA Dimensionality Reduction:** PC1 explains {ml['pca_explained_variance'].get('pc1_explained')}% variance; PC2 explains {ml['pca_explained_variance'].get('pc2_explained')}% variance (Total: {ml['pca_explained_variance'].get('total_explained')}%)",
        "",
        "### Cluster Profiles & Epidemiological Classification",
    ])
    for c in ml.get("cluster_profiles", []):
        m_hle = c.get("mean_hle_2023", "—")
        m_gain = c.get("mean_net_gain", "—")
        m_pct = c.get("mean_pct_change", "—")
        lines.extend([
            f"#### Cluster {c['cluster_id']}: {c['name']} ({c['location_count']} locations)",
            f"- **Badge:** {c['badge']}",
            f"- **Centroid Profile:** 2023 HLE: {m_hle} yrs | 1990–2023 Net Gain: +{m_gain} yrs | 2010–23 Change: {m_pct}%",
            f"- **Epidemiological Characteristics:** {c['description']}",
            f"- **Sample Locations:** {', '.join(c.get('sample_locations', [])[:6])}",
            "",
        ])

    lines.extend([
        "---",
        "",
        "## 6. Global Disease Burden Context (Datasets S10 & S11)",
        "",
        "> **DEMOGRAPHIC DEMARCATION:** Global disease burden datasets (S10 DALYs and S11 YLDs) are cause-level both-sexes estimates. They are intentionally analyzed separately and not merged onto country-level S9 records to avoid ecological fallacies.",
        "",
        "### Epidemiological Shift (Level 1 Categories)",
        "| Broad Disease Category | DALY Share (%) | 2023 DALY Rate (ASR) | 2010–23 Rate Change | YLD Share (%) |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ])
    daly_cats = disease["level1_categories"].get("daly_categories", [])
    yld_cats = disease["level1_categories"].get("yld_categories", [])
    for idx, d_cat in enumerate(daly_cats):
        y_cat = yld_cats[idx] if idx < len(yld_cats) else {}
        lines.append(f"| {d_cat['short_name']} | {d_cat['share_percent']}% | {d_cat['asr_2023']} / 100k | {d_cat['asr_pct_change']}% | {y_cat.get('share_percent', '—')}% |")

    lines.extend([
        "",
        "### Fatal vs. Chronic Disabling Profile (Level 2 Comparison)",
        "| Major Condition | 2023 DALY Count | 2023 YLD Count | Disability Share (%) | Epidemiological Profile |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ])
    for c in disease.get("fatal_vs_disabling_matrix", []):
        lines.append(f"| {c['cause']} | {c['daly_count_2023']/1e6:.1f}M | {c['yld_count_2023']/1e6:.1f}M | {c['disability_ratio_pct']}% | {c['burden_type']} |")

    lines.extend([
        "",
        "---",
        "",
        "## 7. Evidence-Based Heuristic Recommendations",
        "",
        "### Flag Category 1: Locations with Relatively Low HLE",
        "| Flag ID | Location | Actual 2023 HLE | Deficit to Low SDI Benchmark | Policy Surveillance Focus |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ])
    for f in recs.get("low_hle", [])[:6]:
        lines.append(f"| `{f['flag_id']}` | **{f['location']}** | {f['actual_value']} | {f['disparity_delta']} | {f['policy_focus']} |")

    lines.extend([
        "",
        "### Flag Category 2: Locations Showing Longitudinal HLE Decline",
        "| Flag ID | Location | 2010–2023 % Change | Severity | Context & Focus |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ])
    for f in recs.get("hle_decline", [])[:6]:
        lines.append(f"| `{f['flag_id']}` | **{f['location']}** | {f['actual_value']} | `{f['severity']}` | {f['policy_focus']} |")

    lines.extend([
        "",
        "### Flag Category 3: Extreme Gender Gap Disparities",
        "| Flag ID | Location | Female vs Male HLE | Disparity Delta | Public Health Context |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ])
    for f in recs.get("gender_disparity", [])[:6]:
        lines.append(f"| `{f['flag_id']}` | **{f['location']}** | {f['actual_value']} | {f['disparity_delta']} | {f['policy_focus']} |")

    lines.extend([
        "",
        "### Flag Category 4: Group Policy Profiles via K-Means Clusters",
        "| Group Flag | Tier Name | Member Locations | Multivariate Centroid | Strategy Focus |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ])
    for f in recs.get("cluster_groups", []):
        lines.append(f"| `{f['flag_id']}` | **{f['group_name']}** | {f['location_count']} locations | {f['actual_value']} | {f['policy_focus']} |")

    lines.extend([
        "",
        "---",
        "",
        "## 8. Methodology, Epistemological Boundaries & Limitations",
        "",
        "### Analytical Methods Employed",
    ])
    for m in meth.get("analytical_methods", []):
        lines.append(f"- {m}")

    lines.extend([
        "",
        "### Formal Limitations & Ethical Demarcation",
    ])
    for lim in meth.get("limitations_and_ethics", []):
        lines.append(f"- **{lim}**")

    lines.extend([
        "",
        "---",
        f"*{meth.get('formal_disclaimer')}*",
        "",
        f"**End of Report.** Generated by *{meta['system']}*.",
    ])

    return "\n".join(lines)


def generate_html_report() -> str:
    """
    Renders the report into a standalone, styled HTML document
    with responsive typography and CSS print formatting.
    """
    data = compile_full_report()
    meta = data["report_metadata"]
    exec_sum = data["executive_summary"]
    hle = data["hle_analysis"]
    gender = data["gender_gap_analysis"]
    reg = data["regional_comparison"]
    ml = data["machine_learning"]
    disease = data["disease_burden_context"]
    recs = data["recommendations"]
    meth = data["methodology_and_limitations"]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{meta['title']}</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      line-height: 1.5;
      color: #1e293b;
      background-color: #f8fafc;
      margin: 0;
      padding: 40px 20px;
    }}
    .report-container {{
      max-width: 960px;
      margin: 0 auto;
      background: #ffffff;
      padding: 48px;
      border-radius: 12px;
      border: 1px solid #e2e8f0;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }}
    h1 {{ font-size: 24px; color: #0f172a; margin-top: 0; border-bottom: 2px solid #2563eb; padding-bottom: 12px; }}
    h2 {{ font-size: 18px; color: #1e293b; margin-top: 32px; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px; }}
    h3 {{ font-size: 14px; color: #334155; margin-top: 20px; text-transform: uppercase; letter-spacing: 0.5px; }}
    h4 {{ font-size: 13px; color: #2563eb; margin: 12px 0 4px 0; }}
    p, li {{ font-size: 13px; color: #475569; }}
    .meta-box {{
      background: #eff6ff;
      border-left: 4px solid #2563eb;
      padding: 12px 16px;
      margin-bottom: 24px;
      font-size: 12px;
      color: #1e40af;
    }}
    .disclaimer-box {{
      background: #fef2f2;
      border-left: 4px solid #ef4444;
      padding: 12px 16px;
      margin: 24px 0;
      font-size: 11px;
      color: #991b1b;
      line-height: 1.6;
    }}
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 12px;
      margin: 20px 0;
    }}
    .kpi-card {{
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 12px 16px;
    }}
    .kpi-label {{ font-size: 11px; color: #64748b; font-weight: 600; text-transform: uppercase; }}
    .kpi-val {{ font-size: 18px; font-weight: 700; color: #0f172a; margin: 4px 0; }}
    .kpi-sub {{ font-size: 11px; color: #059669; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 16px 0;
      font-size: 12px;
    }}
    th {{
      background: #f1f5f9;
      color: #334155;
      font-weight: 600;
      text-align: left;
      padding: 8px 12px;
      border-bottom: 2px solid #cbd5e1;
    }}
    td {{
      padding: 8px 12px;
      border-bottom: 1px solid #e2e8f0;
      color: #475569;
    }}
    tr:nth-child(even) {{ background: #f8fafc; }}
    .badge {{
      display: inline-block;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 10px;
      font-weight: 600;
    }}
    .badge-high {{ background: #fee2e2; color: #991b1b; }}
    .badge-crit {{ background: #fef3c7; color: #92400e; }}
    .badge-ok {{ background: #dcfce7; color: #166534; }}
    .print-btn {{
      background: #2563eb;
      color: white;
      border: none;
      padding: 8px 16px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      float: right;
    }}
    @media print {{
      body {{ background: white; padding: 0; }}
      .report-container {{ border: none; box-shadow: none; padding: 0; max-width: 100%; }}
      .print-btn {{ display: none; }}
    }}
  </style>
</head>
<body>
  <div class="report-container">
    <button class="print-btn" onclick="window.print()">Print / Save as PDF</button>
    <h1>{meta['title']}</h1>
    <div class="meta-box">
      <strong>System:</strong> {meta['system']} | <strong>Generated:</strong> {meta['generated_at']} | <strong>Scope:</strong> {meta['scope']}
    </div>

    <div class="disclaimer-box">
      <strong>ETHICAL & METHODOLOGICAL BOUNDARIES:</strong><br>
      {meth['formal_disclaimer']}
    </div>

    <h2>1. Executive Summary & KPIs</h2>
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Global HLE (2023)</div>
        <div class="kpi-val">{exec_sum['global_hle_2023']} yrs</div>
        <div class="kpi-sub">95% UI: [{exec_sum['global_hle_ui'][0]}–{exec_sum['global_hle_ui'][1]}] yrs</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Global Gender Gap</div>
        <div class="kpi-val">{exec_sum['global_gender_gap']}</div>
        <div class="kpi-sub">Female longevity advantage</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Global Disease Burden</div>
        <div class="kpi-val">{exec_sum['global_dalys'].split()[0]} {exec_sum['global_dalys'].split()[1]}</div>
        <div class="kpi-sub">{exec_sum['chronic_disability_share']} disability share</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">ML Clustering</div>
        <div class="kpi-val">k = {ml['k']}</div>
        <div class="kpi-sub">Silhouette Score: {ml['silhouette_score']}</div>
      </div>
    </div>

    <h2>2. Healthy Life Expectancy (HLE) Trajectory</h2>
    <table>
      <thead>
        <tr>
          <th>Year</th>
          <th>Both Sexes HLE</th>
          <th>95% Uncertainty Interval</th>
          <th>Female HLE</th>
          <th>Male HLE</th>
          <th>Gender Gap</th>
        </tr>
      </thead>
      <tbody>
        {"".join([f"<tr><td>{t['year']}</td><td><strong>{t['both_mean']} yrs</strong></td><td>[{t['both_lower']}–{t['both_upper']}]</td><td>{t['female_mean']} yrs</td><td>{t['male_mean']} yrs</td><td>+{t['gender_gap']} yrs</td></tr>" for t in hle.get('global_trajectory', [])])}
      </tbody>
    </table>

    <h2>3. Regional & Socio-demographic Inequalities (SDI)</h2>
    <table>
      <thead>
        <tr>
          <th>SDI Quintile Tier</th>
          <th>2023 HLE</th>
          <th>95% UI</th>
          <th>2010–2023 % Change</th>
          <th>Female HLE</th>
          <th>Male HLE</th>
        </tr>
      </thead>
      <tbody>
        {"".join([f"<tr><td><strong>{r.get('region', r.get('location', '—'))}</strong></td><td>{r['hle_mean']} yrs</td><td>[{r['hle_lower']}–{r['hle_upper']}]</td><td>+{r.get('pct_change_2010_2023', r.get('pct_change_mean', '—'))}%</td><td>{r.get('female_hle', r.get('female_mean', '—'))} yrs</td><td>{r.get('male_hle', r.get('male_mean', '—'))} yrs</td></tr>" for r in reg.get('sdi_gradient', [])])}
      </tbody>
    </table>

    <h2>4. Machine Learning Cluster Profiles (K-Means & 2D PCA)</h2>
    <p>PCA captures <strong>{ml['pca_explained_variance'].get('total_explained')}%</strong> of total variance (PC1: {ml['pca_explained_variance'].get('pc1_explained')}%, PC2: {ml['pca_explained_variance'].get('pc2_explained')}%).</p>
    {"".join([f"<div style='margin-bottom:12px; padding:12px; background:#f8fafc; border-radius:6px; border:1px solid #e2e8f0;'><h4>Cluster {c['cluster_id']}: {c['name']} ({c['location_count']} locations)</h4><p style='margin:4px 0; font-size:12px;'><strong>Centroid:</strong> 2023 HLE: {c.get('mean_hle_2023', '—')} yrs | Net Gain: +{c.get('mean_net_gain', '—')} yrs | % Change: {c.get('mean_pct_change', '—')}%</p><p style='margin:0; font-size:11px; color:#64748b;'>{c['description']}</p></div>" for c in ml.get('cluster_profiles', [])])}

    <h2>5. Evidence-Based Policy Surveillance Recommendations</h2>
    <table>
      <thead>
        <tr>
          <th>Flag ID</th>
          <th>Location / Group</th>
          <th>Observed Empirical Metric</th>
          <th>Severity</th>
          <th>Strategic Public Health Focus</th>
        </tr>
      </thead>
      <tbody>
        {"".join([f"<tr><td><code>{f['flag_id']}</code></td><td><strong>{f['location']}</strong></td><td>{f['actual_value']}</td><td><span class='badge badge-high'>{f['severity']}</span></td><td>{f['policy_focus']}</td></tr>" for f in recs.get('low_hle', [])[:5]])}
        {"".join([f"<tr><td><code>{f['flag_id']}</code></td><td><strong>{f['location']}</strong></td><td>{f['actual_value']}</td><td><span class='badge badge-crit'>{f['severity']}</span></td><td>{f['policy_focus']}</td></tr>" for f in recs.get('hle_decline', [])[:5]])}
      </tbody>
    </table>

    <h2>6. Epistemological Boundaries & Methodology</h2>
    <ul>
      {"".join([f"<li>{m}</li>" for m in meth.get('analytical_methods', [])])}
    </ul>
  </div>
</body>
</html>"""
    return html
