"""
test_phase5.py
--------------
Verification test suite for Phase 5: Machine Learning Analysis (K-Means & PCA).
"""

import sys
import os
import io

# Ensure UTF-8 output encoding on Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(__file__))

from ml.clustering import (
    FEATURE_DEFINITIONS,
    build_ml_feature_matrix,
    run_kmeans_clustering,
)

SEP = "=" * 70

def section(title):
    print(f"\n{SEP}\n  {title}\n{SEP}")

def test_phase5():
    # 1. Feature Definitions
    section("1. Machine Learning Feature Matrix")
    print(f"Total engineered features: {len(FEATURE_DEFINITIONS)}")
    for f in FEATURE_DEFINITIONS:
        print(f"  • {f['name']:<20}: {f['label']} ({f['description']})")

    feat_df = build_ml_feature_matrix(include_aggregates=False)
    print(f"\nExtracted matrix shape: {feat_df.shape[0]} locations × {feat_df.shape[1]} columns")
    assert feat_df.shape[0] > 150, "Should have over 150 non-aggregate locations"
    assert feat_df.isna().sum().sum() == 0, "No missing values should remain in feature matrix"
    print("  ✓ Feature matrix constructed with zero missing values.")

    # 2. Run K-Means Clustering (k=3)
    section("2. K-Means Clustering (k=3)")
    res = run_kmeans_clustering(k=3, include_aggregates=False)
    print(f"Number of clusters: {res['k_clusters']}")
    print(f"Total locations clustered: {res['total_locations']}")
    print(f"Silhouette Score (k=3): {res['silhouette_score']}")
    print(f"Inertia: {res['inertia']}")

    assert res['silhouette_score'] > 0.3, "Silhouette score should be above 0.3 for good separation"

    print("\nCandidate k Evaluation Scores:")
    for c in res['evaluation_scores']:
        print(f"  k={c['k']}: Silhouette = {c['silhouette']}, Inertia = {c['inertia']}")

    # 3. Cluster Profiles
    section("3. Cluster Profiles & Interpretations")
    for cp in res['cluster_profiles']:
        print(f"\nCluster {cp['cluster_id']}: {cp['name']} ({cp['badge']})")
        print(f"  Color: {cp['color']} | Locations: {cp['location_count']} ({cp['percentage_of_total']}%)")
        print(f"  2023 HLE: Mean = {cp['mean_hle_2023']} yrs [Min: {cp['min_hle_2023']}, Max: {cp['max_hle_2023']}]")
        print(f"  1990 Baseline: {cp['mean_hle_1990']} yrs | 33-yr Net Gain: +{cp['mean_net_gain']} yrs")
        print(f"  Gender Gap (F - M): {cp['mean_gender_gap']} yrs | 2010-23 % Change: +{cp['mean_pct_change']}%")
        print(f"  Sample Locations: {', '.join(cp['sample_locations'])}")
        print(f"  Description: {cp['description']}")

    # 4. Principal Component Analysis (PCA)
    section("4. Principal Component Analysis (PCA 2D)")
    pca_info = res['pca_summary']
    print(f"PC1 Explained Variance: {pca_info['pc1_explained_variance_pct']}%")
    print(f"PC2 Explained Variance: {pca_info['pc2_explained_variance_pct']}%")
    print(f"Total 2D Explained Variance: {pca_info['total_explained_variance_pct']}%")

    assert pca_info['total_explained_variance_pct'] > 75.0, "2D PCA should capture >75% of variance"
    print(f"  ✓ High 2D fidelity: Captures {pca_info['total_explained_variance_pct']}% of total variance!")

    print("\nTop Feature Contributions to Principal Components:")
    for ld in pca_info['loadings'][:5]:
        print(f"  {ld['label']:<22}: PC1 Loading = {ld['pc1_loading']:<6} | PC2 Loading = {ld['pc2_loading']}")

    # 5. Scatter Points Sample
    section("5. 2D Coordinate Scatter Sample")
    sample_pts = res['location_points'][:6]
    for pt in sample_pts:
        print(f"  {pt['location']:<25} -> Cluster {pt['cluster']} ({pt['cluster_name'][:20]}...) | (x={pt['pca_x']}, y={pt['pca_y']}) | 2023 HLE: {pt['hle_2023']} yrs")

    # 6. Disclaimer
    section("6. Academic & Methodological Disclaimer")
    print(res['disclaimer'])

    print(f"\n{SEP}\n  ALL PHASE 5 MACHINE LEARNING TESTS PASSED!\n{SEP}")

if __name__ == "__main__":
    test_phase5()
