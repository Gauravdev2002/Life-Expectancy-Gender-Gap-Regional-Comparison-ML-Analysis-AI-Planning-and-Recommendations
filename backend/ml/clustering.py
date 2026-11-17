"""
ml/clustering.py
----------------
Machine Learning module implementing K-Means Clustering and Principal Component Analysis (PCA)
on real Healthy Life Expectancy data from Dataset S9.

Features:
  1. Feature engineering of real epidemiological indicators:
     - 1990, 2010, 2020, and 2023 HLE values
     - Sex-disaggregated indicators: Female 2023, Male 2023, and Gender Gap (F - M)
     - Longitudinal gains: 33-year Net Gain (1990-2023) and 13-year % Change (2010-2023)
  2. StandardScaler normalization across all features.
  3. Dynamic K-Means clustering with automated evaluation across k in [2, 6].
  4. Silhouette score and inertia computation.
  5. Principal Component Analysis (PCA) reducing the multi-dimensional space to 2 components.
  6. Explained variance calculation for 2D visualization.
  7. Cluster profile generation and human-interpretable epidemiological labeling.
"""

import math
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from data.pipeline import get_s9

FEATURE_DEFINITIONS = [
    {"name": "hle_1990", "label": "1990 Baseline HLE", "description": "Historical health baseline from 1990."},
    {"name": "hle_2010", "label": "2010 HLE", "description": "Mid-period health assessment."},
    {"name": "hle_2020", "label": "2020 HLE", "description": "Pre/early pandemic health status."},
    {"name": "hle_2023", "label": "2023 Latest HLE", "description": "Current Healthy Life Expectancy."},
    {"name": "female_hle_2023", "label": "2023 Female HLE", "description": "Female-specific healthy life expectancy."},
    {"name": "male_hle_2023", "label": "2023 Male HLE", "description": "Male-specific healthy life expectancy."},
    {"name": "gender_gap_2023", "label": "2023 Gender Gap", "description": "Differential in health: Female HLE minus Male HLE."},
    {"name": "net_gain_1990_2023", "label": "1990–2023 Net Gain", "description": "Absolute healthy years gained over 33 years."},
    {"name": "pct_change_2010_2023", "label": "2010–2023 % Change", "description": "Relative percentage progress over the last 13 years."},
]

FEATURE_COLS = [f["name"] for f in FEATURE_DEFINITIONS]


def _safe_float(val: Any, decimals: int = 2) -> Optional[float]:
    """Helper to ensure JSON-compliant float."""
    if val is None:
        return None
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return None
        return round(f, decimals)
    except (ValueError, TypeError):
        return None


def build_ml_feature_matrix(include_aggregates: bool = False) -> pd.DataFrame:
    """
    Constructs a clean, non-null numerical feature matrix per location from Dataset S9.
    Returns a DataFrame with 1 row per location and 9 engineered features.
    """
    s9 = get_s9()
    if not include_aggregates:
        s9 = s9[~s9["is_aggregate"]]

    # Drop duplicate location entries (keeping sovereign/first)
    locs = s9["location"].drop_duplicates().tolist()

    records = []
    for loc in locs:
        sub = s9[s9["location"] == loc]
        is_agg = bool(sub["is_aggregate"].iloc[0])

        def _val(y, s):
            m = sub[(sub["year"] == y) & (sub["sex"] == s)]
            return m["hle_mean"].iloc[0] if not m.empty else np.nan

        h90 = _val(1990, "both")
        h10 = _val(2010, "both")
        h20 = _val(2020, "both")
        h23 = _val(2023, "both")
        hf = _val(2023, "female")
        hm = _val(2023, "male")

        pct_row = sub[sub["sex"] == "both"]
        pct = pct_row["pct_change_mean"].iloc[0] if not pct_row.empty else np.nan

        gap = (hf - hm) if (not np.isnan(hf) and not np.isnan(hm)) else np.nan
        gain = (h23 - h90) if (not np.isnan(h23) and not np.isnan(h90)) else np.nan

        records.append({
            "location": loc,
            "is_aggregate": is_agg,
            "hle_1990": h90,
            "hle_2010": h10,
            "hle_2020": h20,
            "hle_2023": h23,
            "female_hle_2023": hf,
            "male_hle_2023": hm,
            "gender_gap_2023": gap,
            "net_gain_1990_2023": gain,
            "pct_change_2010_2023": pct,
        })

    df = pd.DataFrame(records).dropna().drop_duplicates(subset=["location"])
    return df


_ML_CACHE: Dict[str, Any] = {}


def run_kmeans_clustering(
    k: int = 3,
    include_aggregates: bool = False
) -> Dict[str, Any]:
    """
    Executes K-Means Clustering and PCA on Dataset S9.
    Uses in-memory cache to ensure instantaneous response times.
    """
    cache_key = f"{k}_{include_aggregates}"
    if cache_key in _ML_CACHE:
        return _ML_CACHE[cache_key]

    df = build_ml_feature_matrix(include_aggregates=include_aggregates)

    if len(df) < k:
        k = max(2, len(df))

    X_raw = df[FEATURE_COLS].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)

    # ── Evaluate silhouette scores across candidate k ─────────────────────────
    candidate_scores = []
    for candidate_k in range(2, min(7, len(df))):
        km_test = KMeans(n_clusters=candidate_k, random_state=42, n_init=10)
        test_labels = km_test.fit_predict(X_scaled)
        score = silhouette_score(X_scaled, test_labels)
        candidate_scores.append({
            "k": candidate_k,
            "silhouette": _safe_float(score, 4),
            "inertia": _safe_float(km_test.inertia_, 1),
        })

    # ── Fit targeted K-Means ──────────────────────────────────────────────────
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    raw_labels = kmeans.fit_predict(X_scaled)
    sil_score = silhouette_score(X_scaled, raw_labels)

    # ── Order clusters by average 2023 HLE so Cluster 0 is lowest, Cluster K-1 is highest
    df["raw_cluster"] = raw_labels
    cluster_order = (
        df.groupby("raw_cluster")["hle_2023"]
        .mean()
        .sort_values(ascending=True)
        .index.tolist()
    )
    remap = {old_c: new_c for new_c, old_c in enumerate(cluster_order)}
    df["cluster"] = df["raw_cluster"].map(remap)

    # ── Standard cluster labels and colors based on health tiers ──────────────
    cluster_meta_templates = {
        0: {
            "name": "High Vulnerability & Developing Infrastructure",
            "badge": "Vulnerable Tier",
            "color": "#DC2626", # Red
            "description": (
                "Locations exhibiting lowest healthy life expectancies (<58 yrs), "
                "often confronting high communicable and maternal disease burdens, "
                "yet showing strong potential for rapid catch-up improvements."
            ),
        },
        1: {
            "name": "Transitional & Emerging Health Systems",
            "badge": "Transitional Tier",
            "color": "#D97706", # Amber
            "description": (
                "Locations with intermediate healthy life expectancy (58–66 yrs) "
                "experiencing substantial longitudinal health gains (+7 to +11 years gained since 1990) "
                "and transitioning epidemiological profiles."
            ),
        },
        2: {
            "name": "High Life Expectancy & Resilient Health Systems",
            "badge": "Advanced Tier",
            "color": "#059669", # Emerald
            "description": (
                "Locations characterized by highest healthy life expectancies (>67 yrs), "
                "advanced primary healthcare delivery, mature disease prevention systems, "
                "and narrower relative growth (ceiling effect)."
            ),
        },
        3: {
            "name": "Exceptional Longevity Tier",
            "badge": "Peak Longevity",
            "color": "#1D4ED8", # Blue
            "description": "Elite global locations with healthy life expectancies exceeding 72 years and high health capital.",
        },
        4: {
            "name": "Moderate-High Stability Tier",
            "badge": "Upper Middle Tier",
            "color": "#7C3AED", # Purple
            "description": "Stable regional health systems with steady progress and low mortality volatility.",
        },
    }

    # ── Generate Cluster Profiles ─────────────────────────────────────────────
    cluster_profiles = []
    for c_id in range(k):
        c_df = df[df["cluster"] == c_id]
        meta = cluster_meta_templates.get(c_id, {
            "name": f"Health Cluster {c_id + 1}",
            "badge": f"Tier {c_id + 1}",
            "color": "#4F46E5",
            "description": f"Statistical cluster of {len(c_df)} locations based on HLE trajectory.",
        })

        sample_locs = c_df["location"].head(6).tolist()

        cluster_profiles.append({
            "cluster_id": c_id,
            "name": meta["name"],
            "badge": meta["badge"],
            "color": meta["color"],
            "description": meta["description"],
            "location_count": len(c_df),
            "percentage_of_total": _safe_float(len(c_df) / len(df) * 100, 1),
            "mean_hle_2023": _safe_float(c_df["hle_2023"].mean()),
            "min_hle_2023": _safe_float(c_df["hle_2023"].min()),
            "max_hle_2023": _safe_float(c_df["hle_2023"].max()),
            "mean_hle_1990": _safe_float(c_df["hle_1990"].mean()),
            "mean_net_gain": _safe_float(c_df["net_gain_1990_2023"].mean()),
            "mean_female_hle": _safe_float(c_df["female_hle_2023"].mean()),
            "mean_male_hle": _safe_float(c_df["male_hle_2023"].mean()),
            "mean_gender_gap": _safe_float(c_df["gender_gap_2023"].mean()),
            "mean_pct_change": _safe_float(c_df["pct_change_2010_2023"].mean()),
            "sample_locations": sample_locs,
        })

    # ── Principal Component Analysis (PCA) ───────────────────────────────────
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    df["pca_x"] = np.round(X_pca[:, 0], 3)
    df["pca_y"] = np.round(X_pca[:, 1], 3)

    pc1_var = _safe_float(pca.explained_variance_ratio_[0] * 100, 1)
    pc2_var = _safe_float(pca.explained_variance_ratio_[1] * 100, 1)
    total_var = _safe_float((pca.explained_variance_ratio_[0] + pca.explained_variance_ratio_[1]) * 100, 1)

    # ── Prepare Location Scatter Points for Visualization ─────────────────────
    location_points = []
    for _, row in df.iterrows():
        c_id = int(row["cluster"])
        c_name = cluster_profiles[c_id]["name"]
        c_color = cluster_profiles[c_id]["color"]

        location_points.append({
            "location": row["location"],
            "cluster": c_id,
            "cluster_name": c_name,
            "color": c_color,
            "pca_x": float(row["pca_x"]),
            "pca_y": float(row["pca_y"]),
            "hle_2023": _safe_float(row["hle_2023"]),
            "hle_1990": _safe_float(row["hle_1990"]),
            "gender_gap": _safe_float(row["gender_gap_2023"]),
            "net_gain": _safe_float(row["net_gain_1990_2023"]),
            "pct_change": _safe_float(row["pct_change_2010_2023"]),
        })

    # ── Feature Contribution / PCA Loadings ───────────────────────────────────
    loadings = []
    for idx, col in enumerate(FEATURE_COLS):
        loadings.append({
            "feature": col,
            "label": FEATURE_DEFINITIONS[idx]["label"],
            "pc1_loading": _safe_float(pca.components_[0, idx], 3),
            "pc2_loading": _safe_float(pca.components_[1, idx], 3),
        })

    res = {
        "k_clusters": k,
        "total_locations": len(df),
        "silhouette_score": _safe_float(sil_score, 4),
        "inertia": _safe_float(kmeans.inertia_, 1),
        "evaluation_scores": candidate_scores,
        "pca_summary": {
            "pc1_explained_variance_pct": pc1_var,
            "pc2_explained_variance_pct": pc2_var,
            "total_explained_variance_pct": total_var,
            "loadings": loadings,
        },
        "features_used": FEATURE_DEFINITIONS,
        "cluster_profiles": cluster_profiles,
        "location_points": location_points,
        "disclaimer": (
            "Machine learning clustering groups locations according to empirical statistical similarities "
            "in health trajectories. Clustering demonstrates data-driven associations and does not establish "
            "direct medical or clinical causation."
        ),
    }
    _ML_CACHE[cache_key] = res
    return res
