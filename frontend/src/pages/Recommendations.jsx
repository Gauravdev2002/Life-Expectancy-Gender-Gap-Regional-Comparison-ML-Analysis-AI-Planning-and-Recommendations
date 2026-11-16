// src/pages/Recommendations.jsx
// Evidence-Based Recommendations & Automated Report Generation.
// Phase 7: Rule-based heuristic surveillance and multi-format downloadable reports.

import React, { useState, useEffect } from 'react'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import {
  fetchRecommendations,
  fetchFullReport,
  getReportMarkdownUrl,
  getReportHtmlUrl,
} from '../services/api'

export default function Recommendations() {
  const [activeTab, setActiveTab] = useState('all') // 'all', 'low_hle', 'decline', 'gender', 'clusters'
  const [recsData, setRecsData] = useState(null)
  const [reportData, setReportData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [downloadingJson, setDownloadingJson] = useState(false)

  useEffect(() => {
    let isMounted = true
    setLoading(true)
    setError(null)

    Promise.all([fetchRecommendations(), fetchFullReport()])
      .then(([recs, rep]) => {
        if (!isMounted) return
        setRecsData(recs)
        setReportData(rep)
        setLoading(false)
      })
      .catch((err) => {
        if (!isMounted) return
        setError(err.message || 'Failed to load recommendations and report data')
        setLoading(false)
      })

    return () => {
      isMounted = false
    }
  }, [])

  const handleDownloadJson = () => {
    if (!reportData) return
    setDownloadingJson(true)
    const jsonStr = JSON.stringify(reportData, null, 2)
    const blob = new Blob([jsonStr], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'regional_health_inequality_report.json'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    setDownloadingJson(false)
  }

  const flags = recsData?.flags || {}
  const lowHleFlags = flags.low_hle || []
  const declineFlags = flags.hle_decline || []
  const genderFlags = flags.gender_disparity || []
  const clusterFlags = flags.cluster_groups || []

  const totalFlags =
    lowHleFlags.length + declineFlags.length + genderFlags.length + clusterFlags.length

  const getFilteredFlags = () => {
    if (activeTab === 'low_hle') return { lowHle: lowHleFlags }
    if (activeTab === 'decline') return { decline: declineFlags }
    if (activeTab === 'gender') return { gender: genderFlags }
    if (activeTab === 'clusters') return { clusters: clusterFlags }
    return {
      lowHle: lowHleFlags,
      decline: declineFlags,
      gender: genderFlags,
      clusters: clusterFlags,
    }
  }

  const filtered = getFilteredFlags()

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <PageHeader
          title="Evidence-Based Recommendations & Reports"
          subtitle="Transparent heuristic surveillance rule-engine and automated comprehensive intelligence reports."
          badge="Phase 7 Operational"
        />

        {/* Download Actions */}
        <div className="flex flex-wrap items-center gap-2 self-start sm:self-auto">
          <a
            href={getReportHtmlUrl()}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-xs transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
            </svg>
            Print / PDF Report
          </a>

          <a
            href={getReportMarkdownUrl()}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 text-xs font-semibold rounded-lg shadow-xs transition-colors"
          >
            <svg className="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Download Markdown (.md)
          </a>

          <button
            onClick={handleDownloadJson}
            disabled={downloadingJson || !reportData}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 text-xs font-semibold rounded-lg shadow-xs transition-colors disabled:opacity-50"
          >
            <svg className="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
            </svg>
            Download JSON
          </button>
        </div>
      </div>

      {/* Academic & Non-Clinical Disclaimer Banner */}
      <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-900 leading-relaxed flex items-start gap-3">
        <div className="p-1.5 bg-amber-200/80 rounded-md text-amber-800 font-bold flex-shrink-0">
          ⚠️
        </div>
        <div>
          <span className="font-bold uppercase tracking-wider text-[11px] block mb-0.5 text-amber-800">
            Epistemological & Non-Clinical Boundaries
          </span>
          {recsData?.disclaimer ||
            'These recommendations are generated via transparent heuristic decision rules applied to observational epidemiological data. Statistical associations do NOT establish causal relationships. This tool serves public health policy surveillance and does NOT provide clinical medical diagnoses or clinical recommendations.'}
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
          {error}
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Total Surveillance Flags"
          value={recsData ? String(totalFlags) : '…'}
          sub="Across 4 heuristic categories"
          color="blue"
        />
        <StatCard
          label="Low HLE Alert Locations"
          value={recsData ? String(lowHleFlags.length) : '…'}
          sub="HLE strictly < 56.9 yrs (Low SDI)"
          color="red"
        />
        <StatCard
          label="HLE Longitudinal Declines"
          value={recsData ? String(declineFlags.length) : '…'}
          sub="Negative change (2010–2023)"
          color="amber"
        />
        <StatCard
          label="Cluster Policy Groups"
          value={recsData ? String(clusterFlags.length) : '…'}
          sub="K-Means developmental tiers"
          color="purple"
        />
      </div>

      {/* Flag Category Filter Tabs */}
      <div className="flex flex-wrap items-center gap-1.5 border-b border-slate-200 pb-2">
        {[
          { id: 'all', label: `All Flags (${totalFlags})` },
          { id: 'low_hle', label: `Low HLE (${lowHleFlags.length})` },
          { id: 'decline', label: `HLE Decline (${declineFlags.length})` },
          { id: 'gender', label: `Gender Gaps (${genderFlags.length})` },
          { id: 'clusters', label: `ML Clusters (${clusterFlags.length})` },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors ${
              activeTab === tab.id
                ? 'bg-blue-600 text-white shadow-xs'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Flags Feed */}
      <div className="space-y-6">
        {/* Category 1: Low HLE Flags */}
        {filtered.lowHle && filtered.lowHle.length > 0 && (
          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h3 className="text-base font-semibold text-slate-800 flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-red-600"></span>
                  Category 1: Locations with Relatively Low HLE (&lt; 56.9 yrs)
                </h3>
                <p className="text-xs text-slate-500">
                  Locations experiencing structural primary care vulnerabilities falling below the Low SDI benchmark.
                </p>
              </div>
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-red-50 text-red-700 border border-red-200">
                {filtered.lowHle.length} flagged
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filtered.lowHle.map((f) => (
                <div
                  key={f.flag_id}
                  className="p-3.5 bg-slate-50/70 border border-slate-200 rounded-lg flex flex-col justify-between hover:border-red-300 transition-colors"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white text-slate-600 border border-slate-200">
                        {f.flag_id}
                      </span>
                      <span className="text-[10px] font-bold text-red-700 bg-red-100/70 px-1.5 py-0.5 rounded">
                        {f.disparity_delta}
                      </span>
                    </div>

                    <h4 className="text-sm font-bold text-slate-800 mb-1">{f.location}</h4>
                    <p className="text-xs text-slate-600 mb-2">
                      <strong className="text-slate-700">Actual Value:</strong> {f.actual_value}
                    </p>
                    <p className="text-xs text-slate-500 mb-2 leading-relaxed">
                      <strong>Reason:</strong> {f.reason}
                    </p>
                  </div>

                  <div className="pt-2 border-t border-slate-200 text-[11px] text-slate-600">
                    <strong className="text-slate-800 block mb-0.5">Policy Strategy:</strong>
                    {f.policy_focus}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Category 2: HLE Decline Alerts */}
        {filtered.decline && filtered.decline.length > 0 && (
          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h3 className="text-base font-semibold text-slate-800 flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-600"></span>
                  Category 2: Locations with Longitudinal HLE Declines (2010–2023)
                </h3>
                <p className="text-xs text-slate-500">
                  Alerts where health progress reversed over the past 13 years despite global average growth (+3.2%).
                </p>
              </div>
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200">
                {filtered.decline.length} flagged
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filtered.decline.map((f) => (
                <div
                  key={f.flag_id}
                  className="p-3.5 bg-slate-50/70 border border-slate-200 rounded-lg flex flex-col justify-between hover:border-amber-300 transition-colors"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white text-slate-600 border border-slate-200">
                        {f.flag_id}
                      </span>
                      <span
                        className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                          f.severity === 'CRITICAL'
                            ? 'text-red-700 bg-red-100'
                            : 'text-amber-700 bg-amber-100'
                        }`}
                      >
                        {f.severity}
                      </span>
                    </div>

                    <h4 className="text-sm font-bold text-slate-800 mb-1">{f.location}</h4>
                    <p className="text-xs text-slate-600 mb-2">
                      <strong className="text-slate-700">Contraction:</strong> {f.actual_value}
                    </p>
                    <p className="text-xs text-slate-500 mb-2 leading-relaxed">
                      <strong>Reason:</strong> {f.reason}
                    </p>
                  </div>

                  <div className="pt-2 border-t border-slate-200 text-[11px] text-slate-600">
                    <strong className="text-slate-800 block mb-0.5">Surveillance Focus:</strong>
                    {f.policy_focus}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Category 3: Gender Disparities */}
        {filtered.gender && filtered.gender.length > 0 && (
          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h3 className="text-base font-semibold text-slate-800 flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-purple-600"></span>
                  Category 3: Extreme Female-Male Disparities (&ge; 5.0 yrs or Reversed)
                </h3>
                <p className="text-xs text-slate-500">
                  Identifies locations where sex-specific mortality severely departs from global benchmarks (+2.0 yrs).
                </p>
              </div>
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-purple-50 text-purple-700 border border-purple-200">
                {filtered.gender.length} flagged
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filtered.gender.map((f) => (
                <div
                  key={f.flag_id}
                  className="p-3.5 bg-slate-50/70 border border-slate-200 rounded-lg flex flex-col justify-between hover:border-purple-300 transition-colors"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white text-slate-600 border border-slate-200">
                        {f.flag_id}
                      </span>
                      <span className="text-[10px] font-semibold text-purple-700 bg-purple-50 px-1.5 py-0.5 rounded border border-purple-200">
                        {f.category}
                      </span>
                    </div>

                    <h4 className="text-sm font-bold text-slate-800 mb-1">{f.location}</h4>
                    <p className="text-xs text-slate-600 mb-2">
                      <strong className="text-slate-700">Observed Gap:</strong> {f.actual_value}
                    </p>
                    <p className="text-xs text-slate-500 mb-2 leading-relaxed">
                      <strong>Reason:</strong> {f.reason}
                    </p>
                  </div>

                  <div className="pt-2 border-t border-slate-200 text-[11px] text-slate-600">
                    <strong className="text-slate-800 block mb-0.5">Policy Strategy:</strong>
                    {f.policy_focus}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Category 4: Cluster Policy Groups */}
        {filtered.clusters && filtered.clusters.length > 0 && (
          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
            <div className="mb-4">
              <h3 className="text-base font-semibold text-slate-800 flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-indigo-600"></span>
                Category 4: Groups of Locations with Similar HLE Profiles (ML Clusters)
              </h3>
              <p className="text-xs text-slate-500">
                Macro-level developmental strategies derived from unsupervised K-Means clustering ($k=3$).
              </p>
            </div>

            <div className="space-y-4">
              {filtered.clusters.map((c) => (
                <div
                  key={c.flag_id}
                  className="p-4 bg-slate-50 rounded-xl border border-slate-200 flex flex-col md:flex-row md:items-start justify-between gap-4"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1.5">
                      <span className="text-xs font-bold px-2 py-0.5 rounded bg-indigo-100 text-indigo-800 font-mono">
                        {c.badge}
                      </span>
                      <h4 className="text-sm font-bold text-slate-800">{c.group_name}</h4>
                      <span className="text-xs text-slate-500">({c.location_count} locations)</span>
                    </div>
                    <p className="text-xs text-slate-600 mb-2 font-mono">
                      <strong>Centroid:</strong> {c.actual_value}
                    </p>
                    <p className="text-xs text-slate-600 mb-2">
                      <strong>Reason:</strong> {c.reason}
                    </p>
                    <p className="text-xs text-slate-500">
                      <strong>Sample Locations:</strong> {c.sample_locations?.join(', ')}
                    </p>
                  </div>

                  <div className="md:w-80 p-3 bg-white rounded-lg border border-slate-200 text-xs text-slate-700 shadow-2xs">
                    <strong className="text-slate-800 block mb-1">Tailored Macro Strategy:</strong>
                    {c.policy_focus}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Report Structure Preview Card */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
        <h3 className="text-base font-semibold text-slate-800 mb-2">
          Report Structure & Methodology (Available for Export)
        </h3>
        <p className="text-xs text-slate-600 leading-relaxed mb-4">
          The downloadable report consolidates data across all analytical and AI planning modules:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
            <span className="font-semibold text-slate-700 block mb-1">1. HLE Trajectory</span>
            <span className="text-slate-500">
              1990–2023 multi-year trends, top/bottom rankings, and 2010–23 % changes with 95% UI.
            </span>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
            <span className="font-semibold text-slate-700 block mb-1">2. Gender & SDI</span>
            <span className="text-slate-500">
              Female-male parity index, widest/reversed gaps, and the 11.0 yr SDI quintile disparity.
            </span>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
            <span className="font-semibold text-slate-700 block mb-1">3. ML & Disease Context</span>
            <span className="text-slate-500">
              K-Means ($k=3$) + 2D PCA (83.8% var), plus separate S10 (DALYs) and S11 (YLDs) cause hierarchies.
            </span>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
            <span className="font-semibold text-slate-700 block mb-1">4. Heuristic Flags & Ethics</span>
            <span className="text-slate-500">
              Transparent rule-based policy flags, explicit non-causal caveats, and non-clinical limitations.
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
