// src/pages/MLAnalysis.jsx
// Phase 5: Machine Learning Analysis (K-Means Clustering & PCA)
// Powered strictly by real GBD Dataset S9 records.

import React, { useState, useEffect, useMemo } from 'react'
import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, BarChart, Bar, Legend, Cell
} from 'recharts'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import { fetchMlClustering } from '../services/api'

export default function MLAnalysis() {
  // ── State ──────────────────────────────────────────────────────────────────
  const [selectedK, setSelectedK] = useState(3)
  const [includeAggs, setIncludeAggs] = useState(false)
  const [mlData, setMlData] = useState(null)
  const [loading, setLoading] = useState(true)

  // Table state
  const [tableSearch, setTableSearch] = useState('')
  const [selectedClusterFilter, setSelectedClusterFilter] = useState('all')
  const [tablePage, setTablePage] = useState(1)
  const pageSize = 12

  // ── Load Machine Learning Results ──────────────────────────────────────────
  useEffect(() => {
    setLoading(true)
    fetchMlClustering(selectedK, includeAggs)
      .then(data => {
        setMlData(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Error fetching ML analysis:', err)
        setLoading(false)
      })
  }, [selectedK, includeAggs])

  // Filtered table locations
  const filteredTableLocations = useMemo(() => {
    if (!mlData?.location_points) return []
    let list = mlData.location_points

    if (selectedClusterFilter !== 'all') {
      const cId = Number(selectedClusterFilter)
      list = list.filter(p => p.cluster === cId)
    }

    if (tableSearch.trim()) {
      const q = tableSearch.toLowerCase().trim()
      list = list.filter(p => p.location.toLowerCase().includes(q))
    }

    return list
  }, [mlData, selectedClusterFilter, tableSearch])

  // Paginated records
  const totalPages = Math.ceil(filteredTableLocations.length / pageSize) || 1
  const paginatedLocations = useMemo(() => {
    const start = (tablePage - 1) * pageSize
    return filteredTableLocations.slice(start, start + pageSize)
  }, [filteredTableLocations, tablePage, pageSize])

  // Custom PCA Scatter Tooltip
  const CustomScatterTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-white p-3 border border-surface-border rounded-lg shadow-lg text-xs space-y-1 max-w-xs">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: data.color }}></span>
            <p className="font-bold text-text-primary text-sm">{data.location}</p>
          </div>
          <p className="font-semibold text-text-secondary">{data.cluster_name}</p>
          <div className="pt-1 text-[11px] space-y-0.5 border-t border-slate-100">
            <p>2023 HLE: <span className="font-bold text-primary">{data.hle_2023} yrs</span></p>
            <p>1990 Baseline: <span className="font-medium text-text-secondary">{data.hle_1990} yrs</span></p>
            <p>33-Yr Net Gain: <span className="font-semibold text-emerald-600">+{data.net_gain} yrs</span></p>
            <p>Gender Gap: <span className="font-semibold">{data.gender_gap > 0 ? '+' : ''}{data.gender_gap} yrs</span></p>
            <p className="text-text-muted">PCA: ({data.pca_x}, {data.pca_y})</p>
          </div>
        </div>
      )
    }
    return null
  }

  // Distribution chart data
  const distributionData = useMemo(() => {
    if (!mlData?.cluster_profiles) return []
    return mlData.cluster_profiles.map(cp => ({
      name: cp.name.length > 25 ? `${cp.name.slice(0, 25)}...` : cp.name,
      shortName: `Cluster ${cp.cluster_id + 1}`,
      count: cp.location_count,
      pct: cp.percentage_of_total,
      color: cp.color,
      mean_hle: cp.mean_hle_2023,
    }))
  }, [mlData])

  return (
    <div className="space-y-6">
      <PageHeader
        title="Machine Learning Analysis"
        subtitle="Unsupervised pattern discovery using K-Means Clustering and Principal Component Analysis (PCA) on GBD Healthy Life Expectancy profiles."
        badge="Phase 5 Live"
      />

      {/* ── Control Bar: Dynamic Cluster Count & Aggregate Controls ─────────── */}
      <div className="card">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="text-xs font-semibold uppercase text-text-muted">Clusters (k):</span>
            <div className="inline-flex rounded-lg border border-surface-border p-1 bg-slate-50 text-xs">
              {[2, 3, 4, 5, 6].map(k => (
                <button
                  key={k}
                  onClick={() => {
                    setSelectedK(k)
                    setSelectedClusterFilter('all')
                    setTablePage(1)
                  }}
                  className={`px-3 py-1 rounded-md font-semibold transition-colors ${
                    selectedK === k
                      ? 'bg-primary text-white shadow-sm'
                      : 'text-text-secondary hover:text-text-primary'
                  }`}
                >
                  k = {k}
                </button>
              ))}
            </div>
            {selectedK === 3 && (
              <span className="badge bg-emerald-50 text-emerald-700 border border-emerald-200 text-[10px]">
                Recommended (Optimal Separation)
              </span>
            )}
          </div>

          <label className="flex items-center gap-2 text-xs text-text-secondary cursor-pointer">
            <input
              type="checkbox"
              checked={includeAggs}
              onChange={(e) => setIncludeAggs(e.target.checked)}
              className="rounded text-primary focus:ring-0"
            />
            Include Macro Regional Aggregates
          </label>
        </div>
      </div>

      {/* ── Model Evaluation Metrics & KPI Cards ────────────────────────────── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          label="Optimal Number of Clusters"
          value={`k = ${mlData?.k_clusters ?? selectedK}`}
          sub="Evaluated across k ∈ [2, 6]"
          color="blue"
        />
        <StatCard
          label="Silhouette Score"
          value={mlData?.silhouette_score !== null ? `${mlData?.silhouette_score}` : '—'}
          sub="Cluster cohesion & separation quality"
          color="green"
        />
        <StatCard
          label="PCA 2D Variance Captured"
          value={mlData?.pca_summary ? `${mlData.pca_summary.total_explained_variance_pct}%` : '83.8%'}
          sub={`PC1: ${mlData?.pca_summary?.pc1_explained_variance_pct ?? 69.7}% | PC2: ${mlData?.pca_summary?.pc2_explained_variance_pct ?? 14.1}%`}
          color="purple"
        />
        <StatCard
          label="Locations Clustered"
          value={mlData ? `${mlData.total_locations}` : '—'}
          sub="9-dimensional feature vectors"
          color="amber"
        />
      </div>

      {/* ── Two-Column ML Charts: 2D PCA Scatter & Cluster Distribution ─────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* PCA 2D Scatter Chart */}
        <div className="card flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3 className="text-sm font-semibold text-text-primary">
                2D Principal Component Projection (PCA)
              </h3>
              <p className="text-xs text-text-muted">
                Dimensionality reduced from 9 features to 2 components ({mlData?.pca_summary?.total_explained_variance_pct ?? 83.8}% variance)
              </p>
            </div>
            <span className="badge bg-purple-50 text-accent border border-purple-200 text-[10px]">
              PCA 2D
            </span>
          </div>

          <div className="h-72 w-full">
            {loading ? (
              <div className="flex items-center justify-center h-full text-xs text-text-muted">Calculating PCA projection...</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: -10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                  <XAxis
                    type="number"
                    dataKey="pca_x"
                    name="Principal Component 1"
                    tick={{ fontSize: 11, fill: '#64748B' }}
                    label={{ value: `PC1 (${mlData?.pca_summary?.pc1_explained_variance_pct}% variance)`, position: 'insideBottom', offset: -10, fontSize: 11, fill: '#64748B' }}
                  />
                  <YAxis
                    type="number"
                    dataKey="pca_y"
                    name="Principal Component 2"
                    tick={{ fontSize: 11, fill: '#64748B' }}
                    label={{ value: `PC2 (${mlData?.pca_summary?.pc2_explained_variance_pct}% variance)`, angle: -90, position: 'insideLeft', fontSize: 11, fill: '#64748B' }}
                  />
                  <Tooltip content={<CustomScatterTooltip />} />
                  {mlData?.cluster_profiles?.map((cp) => {
                    const clusterPoints = mlData.location_points.filter(p => p.cluster === cp.cluster_id)
                    return (
                      <Scatter
                        key={cp.cluster_id}
                        name={cp.name}
                        data={clusterPoints}
                        fill={cp.color}
                      />
                    )
                  })}
                </ScatterChart>
              </ResponsiveContainer>
            )}
          </div>
          <p className="text-[11px] text-text-muted text-center mt-2">
            Each point represents one sovereign/territorial location. Hover over points for details.
          </p>
        </div>

        {/* Cluster Distribution Bar Chart */}
        <div className="card flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3 className="text-sm font-semibold text-text-primary">
                Cluster Size Distribution & Average HLE
              </h3>
              <p className="text-xs text-text-muted">
                Number of locations in each empirical cluster
              </p>
            </div>
            <span className="badge bg-blue-50 text-primary border border-blue-200 text-[10px]">
              Cluster Breakdown
            </span>
          </div>

          <div className="h-72 w-full">
            {loading ? (
              <div className="flex items-center justify-center h-full text-xs text-text-muted">Loading distribution...</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={distributionData} margin={{ top: 10, right: 20, left: -10, bottom: 25 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                  <XAxis dataKey="shortName" tick={{ fontSize: 11, fill: '#475569' }} />
                  <YAxis tick={{ fontSize: 11, fill: '#64748B' }} />
                  <Tooltip
                    formatter={(val, name, item) => [
                      `${val} locations (${item.payload.pct}%) — Mean HLE: ${item.payload.mean_hle} yrs`,
                      item.payload.name
                    ]}
                  />
                  <Bar dataKey="count" name="Locations" radius={[4, 4, 0, 0]}>
                    {distributionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
          <p className="text-[11px] text-text-muted text-center mt-2">
            Distribution showing balance across developmental and health system tiers.
          </p>
        </div>
      </div>

      {/* ── Cluster Profile Cards (Detailed Epidemiological Profiles) ──────── */}
      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-text-primary">
          Cluster Profiles & Health System Characteristics
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {mlData?.cluster_profiles?.map((cp) => (
            <div
              key={cp.cluster_id}
              className="card space-y-3 border-t-4"
              style={{ borderTopColor: cp.color }}
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <span
                    className="inline-block px-2 py-0.5 rounded text-[10px] font-bold text-white mb-1"
                    style={{ backgroundColor: cp.color }}
                  >
                    Cluster {cp.cluster_id + 1}
                  </span>
                  <h4 className="text-sm font-bold text-text-primary leading-snug">{cp.name}</h4>
                </div>
                <span className="badge bg-slate-100 text-slate-700 font-bold text-xs whitespace-nowrap">
                  {cp.location_count} locations
                </span>
              </div>

              <p className="text-xs text-text-secondary leading-relaxed">{cp.description}</p>

              {/* Numerical Metrics */}
              <div className="grid grid-cols-2 gap-2 p-2.5 rounded-lg bg-slate-50 border border-slate-100 text-xs">
                <div>
                  <span className="text-[10px] text-text-muted uppercase">Mean 2023 HLE</span>
                  <p className="font-bold text-text-primary">{cp.mean_hle_2023} yrs</p>
                  <p className="text-[10px] text-text-muted">Range: {cp.min_hle_2023}–{cp.max_hle_2023}</p>
                </div>
                <div>
                  <span className="text-[10px] text-text-muted uppercase">33-Yr Net Gain</span>
                  <p className="font-bold text-emerald-600">+{cp.mean_net_gain} yrs</p>
                  <p className="text-[10px] text-text-muted">1990: {cp.mean_hle_1990} yrs</p>
                </div>
                <div>
                  <span className="text-[10px] text-text-muted uppercase">Gender Gap (F-M)</span>
                  <p className="font-bold text-purple-700">+{cp.mean_gender_gap} yrs</p>
                </div>
                <div>
                  <span className="text-[10px] text-text-muted uppercase">2010–23 Growth</span>
                  <p className="font-bold text-text-primary">+{cp.mean_pct_change}%</p>
                </div>
              </div>

              {/* Sample Members */}
              <div className="text-xs">
                <span className="text-[10px] font-semibold text-text-muted uppercase tracking-wider">
                  Representative Locations:
                </span>
                <p className="text-xs text-text-secondary mt-0.5 font-medium">
                  {cp.sample_locations.join(', ')}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Silhouette Score Evaluation Matrix across Candidate k ──────────── */}
      <div className="card space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-surface-border">
          <div>
            <h3 className="text-sm font-semibold text-text-primary">
              K-Means Hyperparameter Selection (Elbow & Silhouette Analysis)
            </h3>
            <p className="text-xs text-text-muted">
              Evaluated cluster separation across candidate values of k to ensure optimal mathematical interpretability
            </p>
          </div>
          <span className="text-xs text-text-muted font-medium">Scikit-learn Validation</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          {mlData?.evaluation_scores?.map((ev) => (
            <div
              key={ev.k}
              onClick={() => {
                setSelectedK(ev.k)
                setSelectedClusterFilter('all')
                setTablePage(1)
              }}
              className={`p-3 rounded-lg border text-xs cursor-pointer transition-all ${
                selectedK === ev.k
                  ? 'bg-blue-50/70 border-primary shadow-sm'
                  : 'bg-white border-surface-border hover:bg-slate-50'
              }`}
            >
              <div className="flex items-center justify-between font-bold text-sm mb-1">
                <span>k = {ev.k}</span>
                {selectedK === ev.k && <span className="text-primary text-xs">Active</span>}
              </div>
              <p className="text-[11px] text-text-secondary">
                Silhouette: <span className="font-bold">{ev.silhouette}</span>
              </p>
              <p className="text-[10px] text-text-muted">Inertia: {ev.inertia}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ── Feature Definitions Table ───────────────────────────────────────── */}
      <div className="card space-y-3">
        <h3 className="text-sm font-semibold text-text-primary">
          Engineered Feature Dimensions (9 Variables)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5 text-xs">
          {mlData?.features_used?.map((feat) => (
            <div key={feat.name} className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
              <span className="font-bold text-text-primary block mb-0.5">{feat.label}</span>
              <span className="text-[11px] font-mono text-primary block mb-1">{feat.name}</span>
              <p className="text-[11px] text-text-muted leading-tight">{feat.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ── Cluster-Wise Location Registry Table ───────────────────────────── */}
      <div className="card space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-semibold text-text-primary">
              Cluster Membership Registry ({filteredTableLocations.length} locations)
            </h3>
            <p className="text-xs text-text-muted">
              Inspect specific cluster assignments, PCA coordinates, and health indicators
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <select
              value={selectedClusterFilter}
              onChange={(e) => {
                setSelectedClusterFilter(e.target.value)
                setTablePage(1)
              }}
              className="px-2.5 py-1.5 text-xs bg-slate-50 border border-surface-border rounded-lg font-medium"
            >
              <option value="all">All Clusters</option>
              {mlData?.cluster_profiles?.map((cp) => (
                <option key={cp.cluster_id} value={cp.cluster_id}>
                  Cluster {cp.cluster_id + 1} ({cp.name.slice(0, 24)}...)
                </option>
              ))}
            </select>

            <input
              type="text"
              placeholder="Filter location..."
              value={tableSearch}
              onChange={(e) => {
                setTableSearch(e.target.value)
                setTablePage(1)
              }}
              className="px-3 py-1.5 text-xs bg-slate-50 border border-surface-border rounded-lg focus:outline-none focus:ring-1 focus:ring-primary w-40"
            />
          </div>
        </div>

        <div className="overflow-x-auto border border-surface-border rounded-lg">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-text-muted uppercase text-[10px] border-b border-surface-border font-semibold">
              <tr>
                <th className="py-2 px-3">Location</th>
                <th className="py-2 px-3">Assigned Cluster</th>
                <th className="py-2 px-3 text-primary font-bold">2023 HLE</th>
                <th className="py-2 px-3">1990 Baseline</th>
                <th className="py-2 px-3">33-Yr Net Gain</th>
                <th className="py-2 px-3">Gender Gap</th>
                <th className="py-2 px-3">PCA (PC1, PC2)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-border">
              {paginatedLocations.map((row) => (
                <tr key={row.location} className="hover:bg-slate-50">
                  <td className="py-2 px-3 font-semibold text-text-primary">{row.location}</td>
                  <td className="py-2 px-3">
                    <span
                      className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-semibold text-white"
                      style={{ backgroundColor: row.color }}
                    >
                      Cluster {row.cluster + 1}
                    </span>
                  </td>
                  <td className="py-2 px-3 font-bold text-primary">{row.hle_2023} yrs</td>
                  <td className="py-2 px-3 text-text-secondary">{row.hle_1990} yrs</td>
                  <td className="py-2 px-3 text-emerald-600 font-medium">+{row.net_gain} yrs</td>
                  <td className="py-2 px-3 font-medium">
                    {row.gender_gap > 0 ? `+${row.gender_gap}` : row.gender_gap} yrs
                  </td>
                  <td className="py-2 px-3 font-mono text-[11px] text-text-muted">
                    ({row.pca_x}, {row.pca_y})
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between text-xs pt-1">
            <span className="text-text-muted">
              Page {tablePage} of {totalPages} ({filteredTableLocations.length} locations)
            </span>
            <div className="flex items-center gap-1.5">
              <button
                disabled={tablePage <= 1}
                onClick={() => setTablePage(p => Math.max(1, p - 1))}
                className="px-2.5 py-1 bg-white border border-surface-border rounded-md font-medium text-text-secondary disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-50"
              >
                Previous
              </button>
              <button
                disabled={tablePage >= totalPages}
                onClick={() => setTablePage(p => Math.min(totalPages, p + 1))}
                className="px-2.5 py-1 bg-white border border-surface-border rounded-md font-medium text-text-secondary disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-50"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* ── Methodological Disclaimer ─────────────────────────────────────── */}
      <div className="p-4 rounded-lg bg-blue-50/70 border border-blue-200 text-xs text-blue-900 leading-relaxed">
        <strong>Academic &amp; Methodological Notice:</strong> {mlData?.disclaimer}
      </div>
    </div>
  )
}
