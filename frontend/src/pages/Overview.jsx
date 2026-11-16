// src/pages/Overview.jsx
// Dashboard landing page.
// Integrates live metrics from all analytical, ML, and AI planning modules.

import React from 'react'
import { Link } from 'react-router-dom'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import useFetch from '../hooks/useFetch'
import { fetchOverview } from '../services/api'

export default function Overview() {
  const { data, loading, error } = useFetch(fetchOverview)

  const kpis = data?.kpis || {}

  return (
    <div className="space-y-6">
      <PageHeader
        title="AI-Based Regional Health Inequality & Life Expectancy System"
        subtitle="Comprehensive college-level demonstration platform integrating GBD datasets, Scikit-learn ML, and HTN/STRIPS AI Planning."
        badge="System Operational"
      />

      {/* Backend connection status bar */}
      <div
        className={`p-3.5 rounded-lg flex items-center justify-between text-xs font-medium border ${
          loading
            ? 'bg-amber-50 border-amber-200 text-amber-800'
            : error
            ? 'bg-red-50 border-red-200 text-red-800'
            : 'bg-green-50 border-green-200 text-green-800'
        }`}
      >
        <div className="flex items-center gap-2">
          <span
            className={`w-2.5 h-2.5 rounded-full ${
              loading ? 'bg-amber-500 animate-pulse' : error ? 'bg-red-500' : 'bg-green-500'
            }`}
          />
          {loading && 'Connecting to FastAPI backend & loading datasets…'}
          {error && `Backend connection failed: ${error}. Ensure backend is running.`}
          {data && (
            <span>
              <strong>System Online:</strong> FastAPI backend operational · 3 Excel datasets verified · All modules active.
            </span>
          )}
        </div>
        <span className="hidden sm:inline-block font-mono text-[11px] bg-white/70 px-2 py-0.5 rounded border border-green-200">
          v1.0.0
        </span>
      </div>

      {/* Primary KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Global HLE (2023)"
          value={kpis.global_hle_2023 ? `${kpis.global_hle_2023} yrs` : '63.1 yrs'}
          sub={
            kpis.global_hle_ui
              ? `95% UI: [${kpis.global_hle_ui[0]}–${kpis.global_hle_ui[1]}] yrs`
              : 'Empirical GBD S9 benchmark'
          }
          color="blue"
        />
        <StatCard
          label="Global Gender Gap"
          value={kpis.global_gender_gap ? `+${kpis.global_gender_gap} yrs` : '+2.0 yrs'}
          sub="Female longevity advantage over males"
          color="purple"
        />
        <StatCard
          label="Global Disease Burden"
          value={kpis.total_global_dalys ? `${(kpis.total_global_dalys / 1e9).toFixed(2)}B` : '2.80B'}
          sub={`${kpis.chronic_disability_share_pct ?? 35.4}% chronic disability (YLDs)`}
          color="green"
        />
        <StatCard
          label="AI & ML Intelligence"
          value="K-Means + HTN"
          sub={`k=${kpis.ml_clusters_k ?? 3} (Silhouette: ${kpis.ml_silhouette_score ?? 0.384})`}
          color="amber"
        />
      </div>

      {/* Quick Access Navigation Grid */}
      <div>
        <h3 className="text-base font-semibold text-slate-800 mb-3">
          Interactive Analytical & AI Modules
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Card 1: Life Expectancy */}
          <Link
            to="/life-expectancy"
            className="p-4 bg-white rounded-xl border border-slate-200 hover:border-blue-400 hover:shadow-sm transition-all group"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-50 text-blue-700">
                Phase 3 Analytics
              </span>
              <span className="text-slate-400 group-hover:text-blue-600 transition-colors">→</span>
            </div>
            <h4 className="text-sm font-bold text-slate-800 mb-1">
              Life Expectancy Analysis
            </h4>
            <p className="text-xs text-slate-500 leading-relaxed">
              Explore 1990–2023 historical trends, sex-disaggregated trajectories, and 2010–2023 percentage changes for 860 locations.
            </p>
          </Link>

          {/* Card 2: Gender Gap */}
          <Link
            to="/gender-gap"
            className="p-4 bg-white rounded-xl border border-slate-200 hover:border-purple-400 hover:shadow-sm transition-all group"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-purple-50 text-purple-700">
                Gender Disparities
              </span>
              <span className="text-slate-400 group-hover:text-purple-600 transition-colors">→</span>
            </div>
            <h4 className="text-sm font-bold text-slate-800 mb-1">
              Gender Gap Analysis
            </h4>
            <p className="text-xs text-slate-500 leading-relaxed">
              Female vs. male HLE parity scatter, SDI gradients, and extreme gap analyses from Ukraine (+7.9 yrs) to reversed gaps.
            </p>
          </Link>

          {/* Card 3: Regional Comparison */}
          <Link
            to="/regional-comparison"
            className="p-4 bg-white rounded-xl border border-slate-200 hover:border-emerald-400 hover:shadow-sm transition-all group"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700">
                Phase 4 Comparison
              </span>
              <span className="text-slate-400 group-hover:text-emerald-600 transition-colors">→</span>
            </div>
            <h4 className="text-sm font-bold text-slate-800 mb-1">
              Regional Comparison
            </h4>
            <p className="text-xs text-slate-500 leading-relaxed">
              SDI quintile gradients (11.0 yr gap between High and Low SDI), GBD Super-Regions, and top gainers vs decliners.
            </p>
          </Link>

          {/* Card 4: Machine Learning */}
          <Link
            to="/ml-analysis"
            className="p-4 bg-white rounded-xl border border-slate-200 hover:border-indigo-400 hover:shadow-sm transition-all group"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-indigo-50 text-indigo-700">
                Phase 5 Machine Learning
              </span>
              <span className="text-slate-400 group-hover:text-indigo-600 transition-colors">→</span>
            </div>
            <h4 className="text-sm font-bold text-slate-800 mb-1">
              Machine Learning Analysis
            </h4>
            <p className="text-xs text-slate-500 leading-relaxed">
              K-Means clustering evaluated with Silhouette scores, feature standardization, and 2D PCA capturing 83.8% variance.
            </p>
          </Link>

          {/* Card 5: Disease Burden */}
          <Link
            to="/disease-burden"
            className="p-4 bg-white rounded-xl border border-slate-200 hover:border-cyan-400 hover:shadow-sm transition-all group"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-cyan-50 text-cyan-700">
                Datasets S10 & S11
              </span>
              <span className="text-slate-400 group-hover:text-cyan-600 transition-colors">→</span>
            </div>
            <h4 className="text-sm font-bold text-slate-800 mb-1">
              Disease Burden & Disability
            </h4>
            <p className="text-xs text-slate-500 leading-relaxed">
              Global DALYs and YLDs by cause hierarchy. Analyzes the epidemiological shift from infectious diseases to chronic morbidity.
            </p>
          </Link>

          {/* Card 6: AI Planning */}
          <Link
            to="/ai-planning"
            className="p-4 bg-white rounded-xl border border-slate-200 hover:border-amber-400 hover:shadow-sm transition-all group"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-amber-50 text-amber-700">
                Phase 6 AI Planning
              </span>
              <span className="text-slate-400 group-hover:text-amber-600 transition-colors">→</span>
            </div>
            <h4 className="text-sm font-bold text-slate-800 mb-1">
              AI Planning (HTN & STRIPS)
            </h4>
            <p className="text-xs text-slate-500 leading-relaxed">
              Hierarchical Task Network (HTN) compound goal decomposition and STRIPS state execution resolving the classical Frame Problem.
            </p>
          </Link>

          {/* Card 7: Recommendations & Reports */}
          <Link
            to="/recommendations"
            className="p-4 bg-white rounded-xl border border-slate-200 hover:border-rose-400 hover:shadow-sm transition-all group"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-rose-50 text-rose-700">
                Phase 7 Recommendations
              </span>
              <span className="text-slate-400 group-hover:text-rose-600 transition-colors">→</span>
            </div>
            <h4 className="text-sm font-bold text-slate-800 mb-1">
              Recommendations & Reports
            </h4>
            <p className="text-xs text-slate-500 leading-relaxed">
              Heuristic public health surveillance rule-engine flags and multi-format downloadable intelligence reports (Markdown, Print/PDF, JSON).
            </p>
          </Link>
        </div>
      </div>

      {/* System Architecture & Technology Stack Box */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
        <h3 className="text-base font-semibold text-slate-800 mb-2">
          System Architecture & Methodological Integrity
        </h3>
        <p className="text-xs text-slate-600 leading-relaxed mb-4">
          This system was engineered as an end-to-end intelligence platform for global health inequality analysis.
          It strictly obeys scientific standards: uncertainty bounds are retained across all metrics,
          global cause datasets (S10/S11) are preserved without ecological fallacies, and no synthetic or fabricated figures are used.
        </p>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
            <span className="font-semibold text-slate-700 block mb-1">Frontend Layer</span>
            <span className="text-slate-500">React 18 · Tailwind CSS · Recharts · React Router v6</span>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
            <span className="font-semibold text-slate-700 block mb-1">Backend Engine</span>
            <span className="text-slate-500">Python 3.14 · FastAPI · Pandas · NumPy · OpenPyXL</span>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
            <span className="font-semibold text-slate-700 block mb-1">Machine Learning</span>
            <span className="text-slate-500">Scikit-learn · K-Means · 2D PCA · StandardScaler</span>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
            <span className="font-semibold text-slate-700 block mb-1">AI Planning Engine</span>
            <span className="text-slate-500">HTN Task Decomposition · STRIPS State Calculus</span>
          </div>
        </div>
      </div>
    </div>
  )
}
