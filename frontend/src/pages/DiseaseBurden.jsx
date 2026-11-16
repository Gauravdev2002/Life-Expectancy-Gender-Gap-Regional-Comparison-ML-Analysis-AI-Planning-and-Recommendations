// src/pages/DiseaseBurden.jsx
// Specialized Global Disease Burden Analytics
// Uses Datasets S10 (DALYs) and S11 (YLDs).
// Strictly keeps global cause data separate from country-level S9 records.

import React, { useState, useEffect } from 'react'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import {
  fetchDiseaseOverview,
  fetchDiseaseBreakdown,
  fetchTopCauses,
  fetchDalyVsYldComparison,
  fetchDiseaseTable,
} from '../services/api'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts'

export default function DiseaseBurden() {
  const [metric, setMetric] = useState('daly') // 'daly' or 'yld'
  const [overview, setOverview] = useState(null)
  const [breakdown, setBreakdown] = useState(null)
  const [topCauses, setTopCauses] = useState([])
  const [comparison, setComparison] = useState([])
  const [tableData, setTableData] = useState({ records: [], total: 0, total_pages: 1 })
  const [levelFilter, setLevelFilter] = useState(2) // default Level 2 major categories
  const [searchTerm, setSearchTerm] = useState('')
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [tableLoading, setTableLoading] = useState(false)
  const [error, setError] = useState(null)

  // Load high-level analytics
  useEffect(() => {
    let isMounted = true
    setLoading(true)

    Promise.all([
      fetchDiseaseOverview(),
      fetchDiseaseBreakdown(),
      fetchDalyVsYldComparison(),
    ])
      .then(([ov, bd, cp]) => {
        if (!isMounted) return
        setOverview(ov)
        setBreakdown(bd)
        setComparison(cp.causes || [])
        setLoading(false)
      })
      .catch((err) => {
        if (!isMounted) return
        setError(err.message || 'Failed to load disease burden data')
        setLoading(false)
      })

    return () => {
      isMounted = false
    }
  }, [])

  // Load top causes whenever metric changes
  useEffect(() => {
    let isMounted = true
    fetchTopCauses(metric, 2, 8, 'count')
      .then((data) => {
        if (!isMounted) return
        setTopCauses(data)
      })
      .catch(() => {})

    return () => {
      isMounted = false
    }
  }, [metric])

  // Load table data
  useEffect(() => {
    let isMounted = true
    setTableLoading(true)

    fetchDiseaseTable({
      metric,
      level: levelFilter === -1 ? null : levelFilter,
      search: searchTerm,
      page,
      pageSize: 12,
    })
      .then((res) => {
        if (!isMounted) return
        setTableData(res)
        setTableLoading(false)
      })
      .catch(() => {
        if (!isMounted) return
        setTableLoading(false)
      })

    return () => {
      isMounted = false
    }
  }, [metric, levelFilter, searchTerm, page])

  const formatMillions = (val) => {
    if (!val) return '—'
    const millions = val / 1_000_000
    if (millions >= 1000) {
      return `${(millions / 1000).toFixed(2)}B`
    }
    return `${millions.toFixed(1)}M`
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <PageHeader
          title="Disease Burden & Disability Analytics"
          subtitle="Premature mortality (DALYs) vs. Chronic disability (YLDs) across cause hierarchies (Datasets S10 & S11)."
          badge="Global Cause Data"
        />

        {/* Metric Switcher */}
        <div className="flex items-center gap-1 bg-white p-1 rounded-lg border border-slate-200 shadow-xs self-start sm:self-auto">
          <button
            onClick={() => {
              setMetric('daly')
              setPage(1)
            }}
            className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-colors ${
              metric === 'daly'
                ? 'bg-blue-600 text-white shadow-xs'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            DALYs (Fatal + Disability)
          </button>
          <button
            onClick={() => {
              setMetric('yld')
              setPage(1)
            }}
            className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-colors ${
              metric === 'yld'
                ? 'bg-indigo-600 text-white shadow-xs'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            YLDs (Living with Disability)
          </button>
        </div>
      </div>

      {/* Methodological Demarcation Alert */}
      <div className="p-3.5 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-800 flex items-start gap-2.5">
        <span className="font-bold text-amber-700 uppercase tracking-wider text-[10px] mt-0.5 bg-amber-200/70 px-1.5 py-0.5 rounded">
          Demographic Integrity Note
        </span>
        <div className="leading-relaxed">
          Datasets <strong>S10 (DALYs)</strong> and <strong>S11 (YLDs)</strong> provide global, both-sexes cause-level aggregates.
          To maintain strict scientific validity and prevent ecological fallacies, these global totals are preserved as standalone context
          and are <strong>not merged</strong> with location-level HLE records from S9.
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
          label="Total Global DALYs (2023)"
          value={overview?.daly_summary ? formatMillions(overview.daly_summary.count_2023_mean) : '…'}
          sub={`ASR: ${overview?.daly_summary?.asr_2023_mean?.toLocaleString() ?? '…'} per 100k`}
          color="blue"
        />
        <StatCard
          label="Total Global YLDs (2023)"
          value={overview?.yld_summary ? formatMillions(overview.yld_summary.count_2023_mean) : '…'}
          sub={`ASR: ${overview?.yld_summary?.asr_2023_mean?.toLocaleString() ?? '…'} per 100k`}
          color="purple"
        />
        <StatCard
          label="Chronic Disability Share"
          value={overview?.disability_share_percent ? `${overview.disability_share_percent}%` : '…'}
          sub="Fraction of total health loss lived with disability"
          color="green"
        />
        <StatCard
          label="Leading Disability Cause"
          value={overview?.yld_summary?.leading_cause ? 'Mental Disorders' : '…'}
          sub="171M YLDs (+25.0% surge in ASR)"
          color="amber"
        />
      </div>

      {/* Charts Section: Level 1 Breakdown & Top Causes */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Level 1 Epidemiological Transition */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="mb-4">
            <h3 className="text-base font-semibold text-slate-800">
              Broad Epidemiological Categories (Level 1)
            </h3>
            <p className="text-xs text-slate-500">
              Comparison of burden share between Non-Communicable Diseases, Communicable & Maternal, and Injuries.
            </p>
          </div>

          <div className="h-72">
            {breakdown?.daly_categories ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={
                    metric === 'daly'
                      ? breakdown.daly_categories
                      : breakdown.yld_categories
                  }
                  margin={{ top: 10, right: 20, left: 0, bottom: 20 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis
                    dataKey="short_name"
                    stroke="#64748b"
                    tick={{ fontSize: 11 }}
                  />
                  <YAxis
                    stroke="#64748b"
                    tick={{ fontSize: 12 }}
                    unit="%"
                    domain={[0, 85]}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#ffffff',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '12px',
                    }}
                    formatter={(val, name, item) => [
                      `${val}% (ASR: ${item.payload.asr_2023}, 2010–23: ${item.payload.asr_pct_change}%)`,
                      'Share of Burden',
                    ]}
                  />
                  <Bar
                    dataKey="share_percent"
                    name="Burden Share %"
                    radius={[6, 6, 0, 0]}
                  >
                    {(metric === 'daly'
                      ? breakdown.daly_categories
                      : breakdown.yld_categories
                    ).map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={
                          index === 0
                            ? '#0284c7' // Communicable
                            : index === 1
                            ? '#7c3aed' // NCDs
                            : '#f59e0b' // Injuries
                        }
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 text-sm">
                Loading categories…
              </div>
            )}
          </div>
          <div className="mt-2 flex items-center justify-center gap-6 text-xs text-slate-500">
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-purple-600"></span> NCDs (Dominant)
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-sky-600"></span> Communicable & Maternal
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span> Injuries
            </span>
          </div>
        </div>

        {/* Top 8 Leading Causes Chart */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="mb-4">
            <h3 className="text-base font-semibold text-slate-800">
              Leading {metric.toUpperCase()} Causes (Level 2 Major Categories)
            </h3>
            <p className="text-xs text-slate-500">
              Ranked by 2023 total count. Values displayed in Millions.
            </p>
          </div>

          <div className="h-72">
            {topCauses.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={topCauses.map((c) => ({
                    ...c,
                    count_millions: Number((c.count_2023_mean / 1_000_000).toFixed(1)),
                  }))}
                  layout="vertical"
                  margin={{ top: 5, right: 30, left: 90, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis
                    type="number"
                    stroke="#64748b"
                    tick={{ fontSize: 11 }}
                    unit="M"
                  />
                  <YAxis
                    type="category"
                    dataKey="cause"
                    stroke="#64748b"
                    tick={{ fontSize: 10 }}
                    width={95}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#ffffff',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '12px',
                    }}
                    formatter={(val, name, item) => [
                      `${val}M (ASR: ${item.payload.asr_2023_mean}, 2010–23: ${item.payload.asr_pct_change}%)`,
                      '2023 Count',
                    ]}
                  />
                  <Bar
                    dataKey="count_millions"
                    name="2023 Count (M)"
                    fill={metric === 'daly' ? '#3b82f6' : '#8b5cf6'}
                    radius={[0, 4, 4, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 text-sm">
                Loading top causes…
              </div>
            )}
          </div>
          <div className="mt-2 text-center text-xs text-slate-400">
            Horizontal bars represent global population-level counts.
          </div>
        </div>
      </div>

      {/* Fatal vs Chronic Disability Matrix */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
        <div className="mb-4">
          <h3 className="text-base font-semibold text-slate-800">
            Epidemiological Divergence: Premature Mortality vs Chronic Disability
          </h3>
          <p className="text-xs text-slate-500">
            Direct comparison showing the proportion of health loss lived with disability (YLD / DALY) for major conditions.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className="p-3 bg-red-50/50 border border-red-200 rounded-lg">
            <span className="text-xs font-bold text-red-800 uppercase tracking-wide block mb-1">
              Predominantly Fatal (&lt; 30% YLD)
            </span>
            <p className="text-xs text-slate-600 mb-2">
              Driven almost entirely by premature mortality.
            </p>
            <div className="space-y-1 text-xs">
              {comparison
                .filter((c) => c.disability_ratio_pct < 30)
                .slice(0, 4)
                .map((c) => (
                  <div key={c.cause} className="flex justify-between font-medium">
                    <span className="text-slate-700 truncate max-w-[170px]">{c.cause}</span>
                    <span className="text-red-700 font-bold">{c.disability_ratio_pct}% YLD</span>
                  </div>
                ))}
            </div>
          </div>

          <div className="p-3 bg-amber-50/50 border border-amber-200 rounded-lg">
            <span className="text-xs font-bold text-amber-800 uppercase tracking-wide block mb-1">
              Mixed Fatal & Disabling (30%–79% YLD)
            </span>
            <p className="text-xs text-slate-600 mb-2">
              Causes both early death and chronic living disability.
            </p>
            <div className="space-y-1 text-xs">
              {comparison
                .filter((c) => c.disability_ratio_pct >= 30 && c.disability_ratio_pct < 80)
                .slice(0, 4)
                .map((c) => (
                  <div key={c.cause} className="flex justify-between font-medium">
                    <span className="text-slate-700 truncate max-w-[170px]">{c.cause}</span>
                    <span className="text-amber-700 font-bold">{c.disability_ratio_pct}% YLD</span>
                  </div>
                ))}
            </div>
          </div>

          <div className="p-3 bg-purple-50/50 border border-purple-200 rounded-lg">
            <span className="text-xs font-bold text-purple-800 uppercase tracking-wide block mb-1">
              Predominantly Disabling (&ge; 80% YLD)
            </span>
            <p className="text-xs text-slate-600 mb-2">
              Causes long-term morbidity and impairs quality of life.
            </p>
            <div className="space-y-1 text-xs">
              {comparison
                .filter((c) => c.disability_ratio_pct >= 80)
                .slice(0, 4)
                .map((c) => (
                  <div key={c.cause} className="flex justify-between font-medium">
                    <span className="text-slate-700 truncate max-w-[170px]">{c.cause}</span>
                    <span className="text-purple-700 font-bold">{c.disability_ratio_pct}% YLD</span>
                  </div>
                ))}
            </div>
          </div>
        </div>
      </div>

      {/* Comprehensive Cause Hierarchy Table */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
          <div>
            <h3 className="text-base font-semibold text-slate-800">
              Global Cause Hierarchy Table ({metric.toUpperCase()})
            </h3>
            <p className="text-xs text-slate-500">
              Complete data from Dataset {metric === 'daly' ? 'S10' : 'S11'} with 2010–2023 rate trajectories.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-1 text-xs">
              <span className="text-slate-500 font-medium">Level:</span>
              <select
                value={levelFilter}
                onChange={(e) => {
                  setLevelFilter(Number(e.target.value))
                  setPage(1)
                }}
                className="px-2 py-1 border border-slate-200 rounded-md bg-white focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value={-1}>All Levels (0–4)</option>
                <option value={1}>Level 1 (Broad Groups)</option>
                <option value={2}>Level 2 (Major Categories)</option>
                <option value={3}>Level 3 (Sub-Categories)</option>
                <option value={4}>Level 4 (Detailed Causes)</option>
              </select>
            </div>

            <input
              type="text"
              placeholder="Search cause…"
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value)
                setPage(1)
              }}
              className="text-xs px-3 py-1 border border-slate-200 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 w-44"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600">
            <thead className="bg-slate-50 text-slate-700 font-semibold border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-3">Cause Name</th>
                <th className="py-2.5 px-3">Level</th>
                <th className="py-2.5 px-3">2023 Count (95% UI)</th>
                <th className="py-2.5 px-3">Count Change (%)</th>
                <th className="py-2.5 px-3">2023 ASR (per 100k)</th>
                <th className="py-2.5 px-3 text-right">ASR Change (%)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {tableLoading ? (
                <tr>
                  <td colSpan="6" className="py-8 text-center text-slate-400">
                    Loading cause records…
                  </td>
                </tr>
              ) : tableData.records.length === 0 ? (
                <tr>
                  <td colSpan="6" className="py-8 text-center text-slate-400">
                    No matching cause records found.
                  </td>
                </tr>
              ) : (
                tableData.records.map((r, idx) => (
                  <tr key={`${r.cause}-${idx}`} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-2 px-3 font-medium text-slate-800">
                      <span style={{ paddingLeft: `${r.level * 10}px` }}>
                        {r.level > 0 && <span className="text-slate-300 mr-1.5">↳</span>}
                        {r.cause}
                      </span>
                    </td>
                    <td className="py-2 px-3">
                      <span className="px-1.5 py-0.5 rounded text-[10px] bg-slate-100 text-slate-600 font-mono">
                        L{r.level}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-slate-700 font-mono">
                      {formatMillions(r.count_2023_mean)}
                      <span className="text-[10px] text-slate-400 ml-1">
                        [{formatMillions(r.count_2023_lower)}–{formatMillions(r.count_2023_upper)}]
                      </span>
                    </td>
                    <td className="py-2 px-3">
                      <span
                        className={`font-semibold ${
                          r.count_pct_change > 0 ? 'text-red-600' : 'text-green-600'
                        }`}
                      >
                        {r.count_pct_change > 0 ? `+${r.count_pct_change}` : r.count_pct_change}%
                      </span>
                    </td>
                    <td className="py-2 px-3 font-mono text-slate-700">
                      {r.asr_2023_mean?.toLocaleString() ?? '—'}
                    </td>
                    <td className="py-2 px-3 text-right">
                      <span
                        className={`inline-block px-2 py-0.5 rounded font-semibold ${
                          r.asr_pct_change > 0
                            ? 'bg-red-50 text-red-700'
                            : 'bg-green-50 text-green-700'
                        }`}
                      >
                        {r.asr_pct_change > 0 ? `+${r.asr_pct_change}` : r.asr_pct_change}%
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination controls */}
        <div className="flex items-center justify-between pt-4 mt-2 border-t border-slate-100 text-xs text-slate-500">
          <span>
            Page {tableData.page} of {tableData.total_pages} ({tableData.total} causes)
          </span>
          <div className="flex gap-1">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="px-2.5 py-1 border border-slate-200 rounded-md hover:bg-slate-50 disabled:opacity-40 disabled:hover:bg-white"
            >
              Previous
            </button>
            <button
              onClick={() => setPage((p) => Math.min(tableData.total_pages, p + 1))}
              disabled={page >= tableData.total_pages}
              className="px-2.5 py-1 border border-slate-200 rounded-md hover:bg-slate-50 disabled:opacity-40 disabled:hover:bg-white"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
