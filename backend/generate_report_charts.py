"""
generate_report_charts.py
-------------------------
Generates clean, publication-ready vector-styled PNG charts for the
Academic Project Report using actual empirical data and machine learning results.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from data.pipeline import get_s9
from ml.clustering import run_kmeans_clustering

CHARTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "report_charts"))
os.makedirs(CHARTS_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Visual Styling Config
# ---------------------------------------------------------------------------
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#CBD5E1'
plt.rcParams['axes.linewidth'] = 0.8


def generate_architecture_diagram():
    """Generates the System Architecture Diagram."""
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=200)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')

    # Color Palette
    c_blue = '#1E3A8A'
    c_light_blue = '#EFF6FF'
    c_teal = '#0D9488'
    c_light_teal = '#F0FDFA'
    c_purple = '#7C3AED'
    c_light_purple = '#FAF5FF'
    c_slate = '#334155'

    # Title
    ax.text(5, 5.65, "Health Inequality Intelligence System Architecture", 
            ha='center', va='center', fontsize=12, fontweight='bold', color=c_blue)

    # Box 1: Presentation Layer
    rect1 = plt.Rectangle((0.5, 3.8), 9, 1.3, facecolor=c_light_blue, edgecolor='#3B82F6', linewidth=1.2)
    ax.add_patch(rect1)
    ax.text(0.8, 4.85, "PRESENTATION TIER (React 18 Single Page Application)", fontsize=9, fontweight='bold', color=c_blue)
    ax.text(5, 4.25, 
            "Overview Dashboard  |  Life Expectancy Trends  |  Gender Disparity Scatter\n"
            "Regional SDI Comparisons  |  K-Means & PCA Visualization  |  HTN Planning Inspector",
            ha='center', va='center', fontsize=8, color=c_slate)

    # Arrow 1 <-> 2
    ax.annotate('', xy=(5, 3.8), xytext=(5, 3.2),
                arrowprops=dict(arrowstyle='<->', color='#3B82F6', lw=1.5))
    ax.text(5.2, 3.5, "REST API JSON (Port 8000)", fontsize=7.5, color='#2563EB', fontweight='bold')

    # Box 2: Application & AI Engine Layer
    rect2 = plt.Rectangle((0.5, 1.8), 9, 1.4, facecolor=c_light_purple, edgecolor=c_purple, linewidth=1.2)
    ax.add_patch(rect2)
    ax.text(0.8, 2.95, "APPLICATION & AI INTELLIGENCE TIER (Python 3.14 FastAPI Engine)", fontsize=9, fontweight='bold', color=c_purple)
    
    # Sub-modules inside Box 2
    sub1 = plt.Rectangle((0.7, 1.95), 2.7, 0.75, facecolor='#FFFFFF', edgecolor='#DDD6FE', linewidth=0.8)
    ax.add_patch(sub1)
    ax.text(2.05, 2.32, "FastAPI REST Engine\n11 Canonical Endpoints", ha='center', va='center', fontsize=7, color=c_slate)

    sub2 = plt.Rectangle((3.65, 1.95), 2.7, 0.75, facecolor='#FFFFFF', edgecolor='#DDD6FE', linewidth=0.8)
    ax.add_patch(sub2)
    ax.text(5.0, 2.32, "Scikit-Learn ML\nK-Means (k=3) & 2D PCA", ha='center', va='center', fontsize=7, color=c_slate)

    sub3 = plt.Rectangle((6.6, 1.95), 2.7, 0.75, facecolor='#FFFFFF', edgecolor='#DDD6FE', linewidth=0.8)
    ax.add_patch(sub3)
    ax.text(7.95, 2.32, "Classical AI Planning\nHTN Decomposer & STRIPS", ha='center', va='center', fontsize=7, color=c_slate)

    # Arrow 2 <-> 3
    ax.annotate('', xy=(5, 1.8), xytext=(5, 1.2),
                arrowprops=dict(arrowstyle='<->', color=c_teal, lw=1.5))
    ax.text(5.2, 1.5, "In-Memory Data Pipeline (No mutation)", fontsize=7.5, color=c_teal, fontweight='bold')

    # Box 3: Data Tier
    rect3 = plt.Rectangle((0.5, 0.2), 9, 1.0, facecolor=c_light_teal, edgecolor=c_teal, linewidth=1.2)
    ax.add_patch(rect3)
    ax.text(0.8, 0.95, "DATA & STORAGE TIER (GBD 2023 Empirical Study Datasets)", fontsize=9, fontweight='bold', color=c_teal)
    ax.text(5, 0.55, 
            "Dataset S9: 8,532 Location Records (95% UI)  |  Dataset S10: Global DALYs (Levels 0-4)  |  Dataset S11: Global YLDs\n"
            "Strict Demographic Isolation: Global cause datasets are preserved separately to eliminate Ecological Fallacies",
            ha='center', va='center', fontsize=7.2, color=c_slate)

    out_path = os.path.join(CHARTS_DIR, "fig1_architecture.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close()
    return out_path


def generate_hle_trends_chart():
    """Generates the Longitudinal Global HLE Trajectory Chart."""
    fig, ax = plt.subplots(figsize=(6, 3.2), dpi=200)

    years = [1990, 2010, 2020, 2023]
    hle_both = [55.9, 61.1, 62.6, 63.1]
    hle_lower = [53.2, 58.3, 59.8, 60.2]
    hle_upper = [58.4, 63.7, 65.1, 65.6]

    hle_female = [57.1, 62.2, 63.7, 64.2]
    hle_male = [54.8, 60.1, 61.6, 62.2]

    # Uncertainty Bound Fill
    ax.fill_between(years, hle_lower, hle_upper, color='#DBEAFE', alpha=0.6, label='95% Uncertainty Interval')

    # Lines
    ax.plot(years, hle_both, marker='o', color='#1D4ED8', linewidth=2.2, label='Global HLE (Both Sexes)')
    ax.plot(years, hle_female, marker='^', color='#9333EA', linewidth=1.8, linestyle='--', label='Female HLE')
    ax.plot(years, hle_male, marker='s', color='#059669', linewidth=1.8, linestyle=':', label='Male HLE')

    for x, y in zip(years, hle_both):
        ax.annotate(f"{y}y", (x, y), textcoords="offset points", xytext=(0, 7), ha='center', fontsize=7.5, fontweight='bold', color='#1D4ED8')

    ax.set_title("Longitudinal Global Healthy Life Expectancy (1990–2023)", fontsize=9.5, fontweight='bold', color='#0F172A', pad=8)
    ax.set_xlabel("Observation Year", fontsize=8, color='#334155')
    ax.set_ylabel("HLE at Birth (Years)", fontsize=8, color='#334155')
    ax.set_ylim(50, 70)
    ax.set_xticks(years)
    ax.grid(True, linestyle='--', alpha=0.5, color='#E2E8F0')
    ax.legend(loc='lower right', fontsize=7, frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1')

    out_path = os.path.join(CHARTS_DIR, "fig2_hle_trends.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close()
    return out_path


def generate_sdi_gradient_chart():
    """Generates the Socio-Demographic Index (SDI) Disparity Bar Chart."""
    fig, ax = plt.subplots(figsize=(6, 3.2), dpi=200)

    categories = ['High SDI', 'High-Middle', 'Middle SDI', 'Low-Middle', 'Low SDI']
    values = [67.9, 64.2, 61.8, 58.4, 56.9]
    colors_list = ['#059669', '#0D9488', '#2563EB', '#D97706', '#DC2626']

    bars = ax.bar(categories, values, color=colors_list, width=0.55, edgecolor='#CBD5E1', linewidth=0.6)

    # Annotate bar values
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{h:.1f}y",
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=8, fontweight='bold', color='#0F172A')

    # Draw span line High vs Low
    ax.annotate('', xy=(4, 56.9), xytext=(0, 67.9),
                arrowprops=dict(arrowstyle='<->', color='#B91C1C', lw=1.2, linestyle='--'))
    ax.text(2, 65.5, "11.0-Year Developmental Divide", ha='center', fontsize=8, fontweight='bold', color='#B91C1C', backgroundcolor='#FEF2F2')

    ax.set_title("Healthy Life Expectancy Across SDI Quintiles (2023)", fontsize=9.5, fontweight='bold', color='#0F172A', pad=8)
    ax.set_ylabel("HLE (Years)", fontsize=8, color='#334155')
    ax.set_ylim(45, 75)
    ax.grid(axis='y', linestyle='--', alpha=0.5, color='#E2E8F0')

    out_path = os.path.join(CHARTS_DIR, "fig3_sdi_gradient.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close()
    return out_path


def generate_pca_clusters_chart():
    """Generates the Machine Learning 2D PCA Cluster Scatter Plot."""
    fig, ax = plt.subplots(figsize=(6, 3.2), dpi=200)

    ml_data = run_kmeans_clustering(k=3)
    pts = ml_data["location_points"]

    c0_x = [p["pca_x"] for p in pts if p["cluster"] == 0]
    c0_y = [p["pca_y"] for p in pts if p["cluster"] == 0]

    c1_x = [p["pca_x"] for p in pts if p["cluster"] == 1]
    c1_y = [p["pca_y"] for p in pts if p["cluster"] == 1]

    c2_x = [p["pca_x"] for p in pts if p["cluster"] == 2]
    c2_y = [p["pca_y"] for p in pts if p["cluster"] == 2]

    ax.scatter(c0_x, c0_y, c='#DC2626', alpha=0.6, s=16, label='Cluster 0: High Vulnerability (<58y)')
    ax.scatter(c1_x, c1_y, c='#D97706', alpha=0.6, s=16, label='Cluster 1: Transitional Systems (58-66y)')
    ax.scatter(c2_x, c2_y, c='#059669', alpha=0.6, s=16, label='Cluster 2: Resilient Advanced (>67y)')

    # Mark cluster centers
    ax.scatter([np.mean(c0_x)], [np.mean(c0_y)], c='#7F1D1D', s=70, marker='X', edgecolors='white', linewidth=1)
    ax.scatter([np.mean(c1_x)], [np.mean(c1_y)], c='#78350F', s=70, marker='X', edgecolors='white', linewidth=1)
    ax.scatter([np.mean(c2_x)], [np.mean(c2_y)], c='#064E3B', s=70, marker='X', edgecolors='white', linewidth=1)

    pc1_pct = ml_data["pca_summary"]["pc1_explained_variance_pct"]
    pc2_pct = ml_data["pca_summary"]["pc2_explained_variance_pct"]
    tot_pct = ml_data["pca_summary"]["total_explained_variance_pct"]

    ax.set_title(f"2D PCA Projection of K-Means Health Clusters (k=3, Var: {tot_pct}%)", fontsize=9.5, fontweight='bold', color='#0F172A', pad=8)
    ax.set_xlabel(f"Principal Component 1 — Overall Longevity ({pc1_pct}%)", fontsize=8, color='#334155')
    ax.set_ylabel(f"Principal Component 2 — Gender Differential ({pc2_pct}%)", fontsize=8, color='#334155')
    ax.grid(True, linestyle='--', alpha=0.5, color='#E2E8F0')
    ax.legend(loc='lower left', fontsize=6.8, frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1')

    out_path = os.path.join(CHARTS_DIR, "fig4_pca_clusters.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close()
    return out_path


def generate_htn_planning_chart():
    """Generates the HTN Planning & STRIPS Workflow Diagram."""
    fig, ax = plt.subplots(figsize=(8, 2.5), dpi=200)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis('off')

    c_blue = '#1E3A8A'
    c_slate = '#334155'

    ax.text(5, 2.7, "Autonomous AI Planning Pipeline (Compound Goal Decomposition)", 
            ha='center', va='center', fontsize=9.5, fontweight='bold', color=c_blue)

    steps = [
        ("Compound Goal", "ANALYZE_HEALTH\nINEQUALITY", "#EFF6FF", "#2563EB"),
        ("HTN Decomposer", "Resolves Methods\n& Task Network", "#FAF5FF", "#7C3AED"),
        ("STRIPS Action", "Precondition Check\n& Frame Calculus", "#FFFBEB", "#D97706"),
        ("Execution", "Runs K-Means\n& S9 Analytics", "#F0FDF4", "#059669"),
        ("Synthesized Output", "Structured Report\n& Live KPIs", "#F8FAFC", "#475569")
    ]

    for i, (title, sub, bg, border) in enumerate(steps):
        x = 0.3 + i * 1.95
        rect = plt.Rectangle((x, 0.4), 1.6, 1.8, facecolor=bg, edgecolor=border, linewidth=1.2)
        ax.add_patch(rect)
        ax.text(x + 0.8, 1.85, f"Step {i+1}", ha='center', va='center', fontsize=7, fontweight='bold', color=border)
        ax.text(x + 0.8, 1.45, title, ha='center', va='center', fontsize=7.5, fontweight='bold', color='#0F172A')
        ax.text(x + 0.8, 0.85, sub, ha='center', va='center', fontsize=6.8, color=c_slate)

        if i < 4:
            ax.annotate('', xy=(x + 1.95, 1.3), xytext=(x + 1.6, 1.3),
                        arrowprops=dict(arrowstyle='->', color='#94A3B8', lw=1.2))

    out_path = os.path.join(CHARTS_DIR, "fig5_htn_workflow.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close()
    return out_path


def generate_all_charts():
    p1 = generate_architecture_diagram()
    p2 = generate_hle_trends_chart()
    p3 = generate_sdi_gradient_chart()
    p4 = generate_pca_clusters_chart()
    p5 = generate_htn_planning_chart()
    print("Generated all 5 report charts successfully:")
    print("1.", p1)
    print("2.", p2)
    print("3.", p3)
    print("4.", p4)
    print("5.", p5)


if __name__ == "__main__":
    generate_all_charts()
