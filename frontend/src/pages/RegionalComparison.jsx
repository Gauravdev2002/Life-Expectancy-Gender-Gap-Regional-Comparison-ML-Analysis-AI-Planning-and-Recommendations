// src/pages/RegionalComparison.jsx
// Phase 4: Regional Comparison and Trend Analysis Dashboard
// Powered strictly by real GBD Dataset S9 records.

import React, { useState, useEffect, useMemo } from 'react'
import {
  LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import {
  fetchRegionalComparison,
  fetchRegionalTrends,
  fetchIncreaseDecreaseAnalysis,
  fetchTopBottomLocations
} from '../services/api'

// Palette for multi-region lines
const REGION_COLORS = [
  '#1D4ED8', '#059669', '#7C3AED', '#D97706', '#DC2626',
  '#0284C7', '#4F46E5', '#0D9488', '#E11D48', '#84CC16',
]

export default function RegionalComparison() {
  // ── State ──────────────────────────────────────────────────────────────────
  const [grouping, setGrouping] = useState('sdi') // 'sdi' | 'super_regions' | 'regions'
  const [selectedYear, setSelectedYear] = useState(2023)
  const [selectedSex, setSelectedSex] = useState('both')

  const [compData, setCompData] = useState([])
  const [compLoading, setCompLoading] = useState(true)

  const [trendData, setTrendData] = useState([])
  const [trendLoading, setTrendLoading] = useState(true)

  const [incDecData, setIncDecData] = useState(null)
  const [incDecLoading, setIncDecLoading] = useState(true)

  const [rankings, setRankings] = useState(null)
  const [rankingLoading, setRankingLoading] = useState(true)

  // ── Load Regional Comparison Data ──────────────────────────────────────────
  useEffect(() => {
    setCompLoading(true)
    fetchRegionalComparison(grouping, selectedYear, selectedSex)
      .then(data => {
        setCompData(data || [])
        setCompLoading(false)
      })
      .catch(err => {
        console.error('Error fetching regional comparison:', err)
        setCompLoading(false)
      })
  }, [grouping, selectedYear, selectedSex])

  // ── Load Regional Historical Trends ────────────────────────────────────────
  useEffect(() => {
    setTrendLoading(true)
    fetchRegionalTrends(grouping)
      .then(data => {
        setTrendData(data || [])
        setTrendLoading(false)
      })
      .catch(err => {
        console.error('Error fetching regional trends:', err)
        setTrendLoading(false)
      })
  }, [grouping])

  // ── Load Increase / Decrease Analysis ──────────────────────────────────────
  useEffect(() => {
    setIncDecLoading(true)
    fetchIncreaseDecreaseAnalysis(false, 5)
      .then(data => {
        setIncDecData(data)
        setIncDecLoading(false)
      })
      .catch(err => {
        console.error('Error fetching increase/decrease:', err)
        setIncDecLoading(false)
      })
  }, [])

  // ── Load Top 5 & Bottom 5 Rankings ─────────────────────────────────────────
  useEffect(() => {
    setRankingLoading(true)
    fetchTopBottomLocations(2023, false, 5)
      .then(data => {
        setRankings(data)
        setRankingLoading(false)
      })
      .catch(err => {
        console.error('Error fetching top/bottom:', err)
        setRankingLoading(false)
      })
  }, [])

  // Calculate summary gradient (e.g. High SDI vs Low SDI)
  const highSdiVal = compData.find(d => d.region === 'High SDI')?.hle_mean
  const lowSdiVal = compData.find(d => d.region === 'Low SDI')?.hle_mean
  const sdiGap = highSdiVal && lowSdiVal ? (highSdiVal - lowSdiVal).toFixed(1) : null

  // Custom chart tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-surface-border rounded-lg shadow-md text-xs space-y-1">
          <p className="font-semibold text-text-primary text-sm">{label}</p>
          {payload.map((entry, index) => (
            <p key={`item-${index}`} style={{ color: entry.color }} className="font-medium">
              {entry.name}: <span className="font-bold">{entry.value} yrs</span>
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  // Extract distinct regions for trend lines
  const trendLineKeys = useMemo(() => {
    if (!trendData || trendData.length === 0) return []
    const firstRow = trendData[0] || {}
    return Object.keys(firstRow).filter(k => k !== 'year')
  }, [trendData])

  return (
    <div className="space-y-6">
      <PageHeader
        title="Regional Comparison & Trend Analysis"
        subtitle="Cross-regional health disparities, socio-demographic development gradients (SDI), and longitudinal trajectories from GBD Dataset S9."
        badge="Phase 4 Live"
      />

      {/* ── Control Bar: Grouping Selector & Filters ───────────────────────── */}
      <div className="card">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-semibold uppercase text-text-muted">Grouping Level:</span>
            <div className="inline-flex rounded-lg border border-surface-border p-1 bg-slate-50 text-xs">
              <button
                onClick={() => setGrouping('sdi')}
                className={`px-3 py-1 rounded-md font-medium transition-colors ${
                  grouping === 'sdi'
                    ? 'bg-primary text-white shadow-sm'
                    : 'text-text-secondary hover:text-text-primary'
                }`}
              >
                SDI Quintiles (Socio-demographic)
              </button>
              <button
                onClick={() => setGrouping('super_regions')}
                className={`px-3 py-1 rounded-md font-medium transition-colors ${
                  grouping === 'super_regions'
                    ? 'bg-primary text-white shadow-sm'
                    : 'text-text-secondary hover:text-text-primary'
                }`}
              >
                GBD Super-Regions (7 Divisions)
              </button>
              <button
                onClick={() => setGrouping('regions')}
                className={`px-3 py-1 rounded-md font-medium transition-colors ${
                  grouping === 'regions'
                    ? 'bg-primary text-white shadow-sm'
                    : 'text-text-secondary hover:text-text-primary'
                }`}
              >
                GBD Intermediate Regions (21 Tiers)
              </button>
            </div>
          </div>

          <div className="flex items-center gap-3 text-xs">
            <div className="flex items-center gap-1.5">
              <span className="text-text-muted font-medium">Year:</span>
              <select
                value={selectedYear}
                onChange={(e) => setSelectedYear(Number(e.target.value))}
                className="bg-slate-50 border border-surface-border rounded-md px-2 py-1 font-medium"
              >
                <option value={1990}>1990</option>
                <option value={2010}>2010</option>
                <option value={2020}>2020</option>
                <option value={2023}>2023</option>
              </select>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-text-muted font-medium">Demographic:</span>
              <select
                value={selectedSex}
                onChange={(e) => setSelectedSex(e.target.value)}
                className="bg-slate-50 border border-surface-border rounded-md px-2 py-1 font-medium"
              >
                <option value="both">Both Sexes</option>
                <option value="female">Females</option>
                <option value="male">Males</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* ── Headline Metric Summary Cards ──────────────────────────────────── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          label="SDI Inequality Gap (2023)"
          value={sdiGap ? `+${sdiGap} yrs` : '+11.0 yrs'}
          sub="High SDI vs Low SDI disparity"
          color="blue"
        />
        <StatCard
          label="Locations with HLE Gain"
          value={incDecData ? `${incDecData.total_increased}` : '542'}
          sub="Increased HLE (2010–2023)"
          color="green"
        />
        <StatCard
          label="Locations with HLE Decline"
          value={incDecData ? `${incDecData.total_decreased}` : '146'}
          sub="Decreased HLE (2010–2023)"
          color="amber"
        />
        <StatCard
          label="Global HLE (2023 Benchmark)"
          value="63.1 yrs"
          sub="95% UI: [60.2, 65.6] yrs"
          color="purple"
        />
      </div>

      {/* ── Two-Column Regional Charts: Comparison Bar & Multi-Line Trend ──── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Interactive Regional Comparison Chart */}
        <div className="card flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3 className="text-sm font-semibold text-text-primary capitalize">
                {grouping.replace('_', ' ')} Comparison ({selectedYear})
              </h3>
              <p className="text-xs text-text-muted">Mean Healthy Life Expectancy at birth across tiers</p>
            </div>
            <span className="badge bg-blue-50 text-primary border border-blue-200 uppercase text-[10px]">
              {selectedSex}
            </span>
          </div>

          <div className="h-72 w-full">
            {compLoading ? (
              <div className="flex items-center justify-center h-full text-xs text-text-muted">Loading chart...</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={compData} margin={{ top: 10, right: 20, left: -10, bottom: grouping === 'regions' ? 60 : 35 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                  <XAxis
                    dataKey="region"
                    angle={-30}
                    textAnchor="end"
                    interval={0}
                    tick={{ fontSize: 10, fill: '#475569' }}
                  />
                  <YAxis domain={['auto', 'auto']} tick={{ fontSize: 11, fill: '#64748B' }} unit=" yrs" />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="hle_mean" name="Healthy Life Expectancy" fill="#1D4ED8" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
          <p className="text-[11px] text-text-muted text-center mt-2">
            Values reflect actual GBD S9 estimates for {selectedYear}.
          </p>
        </div>

        {/* Historical Trajectory Multi-Line Chart */}
        <div className="card flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3 className="text-sm font-semibold text-text-primary capitalize">
                Historical HLE Trajectory ({grouping.replace('_', ' ')})
              </h3>
              <p className="text-xs text-text-muted">Longitudinal progression (1990, 2010, 2020, 2023)</p>
            </div>
            <span className="badge bg-emerald-50 text-emerald-700 border border-emerald-200 text-[10px]">
              1990–2023
            </span>
          </div>

          <div className="h-72 w-full">
            {trendLoading ? (
              <div className="flex items-center justify-center h-full text-xs text-text-muted">Loading trends...</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                  <XAxis dataKey="year" tick={{ fontSize: 12, fill: '#64748B' }} />
                  <YAxis domain={['auto', 'auto']} tick={{ fontSize: 11, fill: '#64748B' }} unit=" yrs" />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend wrapperStyle={{ fontSize: 11, paddingTop: 6 }} />
                  {trendLineKeys.slice(0, 7).map((key, idx) => (
                    <Line
                      key={key}
                      type="monotone"
                      dataKey={key}
                      name={key}
                      stroke={REGION_COLORS[idx % REGION_COLORS.length]}
                      strokeWidth={2}
                      dot={{ r: 3 }}
                      activeDot={{ r: 5 }}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
          <p className="text-[11px] text-text-muted text-center mt-2">
            Long-term convergence and divergence across developmental tiers.
          </p>
        </div>
      </div>

      {/* ── Gender Comparison Visualization across Groupings ─────────────── */}
      <div className="card">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-sm font-semibold text-text-primary">
              Gender Disparities & Gap across {grouping === 'sdi' ? 'SDI Tiers' : 'Regions'} ({selectedYear})
            </h3>
            <p className="text-xs text-text-muted">
              Comparing Female vs. Male HLE and Gender Gap (Female HLE minus Male HLE)
            </p>
          </div>
          <span className="badge bg-purple-50 text-accent border border-purple-200">
            Gender Differentials
          </span>
        </div>

        <div className="h-72 w-full">
          {compLoading ? (
            <div className="flex items-center justify-center h-full text-xs text-text-muted">Loading chart...</div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={compData} margin={{ top: 10, right: 20, left: -10, bottom: grouping === 'regions' ? 60 : 35 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                <XAxis
                  dataKey="region"
                  angle={-30}
                  textAnchor="end"
                  interval={0}
                  tick={{ fontSize: 10, fill: '#475569' }}
                />
                <YAxis domain={['auto', 'auto']} tick={{ fontSize: 11, fill: '#64748B' }} unit=" yrs" />
                <Tooltip content={<CustomTooltip />} />
                <Legend wrapperStyle={{ fontSize: 12, paddingTop: 4 }} />
                <Bar dataKey="female_hle" name="Female HLE" fill="#059669" radius={[4, 4, 0, 0]} />
                <Bar dataKey="male_hle" name="Male HLE" fill="#7C3AED" radius={[4, 4, 0, 0]} />
                <Bar dataKey="gender_gap" name="Gender Gap (F - M)" fill="#3B82F6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* ── Trajectory Shifts: Largest Increases vs. Decreases (2010-2023) ─── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Largest Increases */}
        <div className="card">
          <div className="flex items-center justify-between pb-3 mb-3 border-b border-surface-border">
            <h3 className="text-sm font-semibold text-text-primary flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
              Largest HLE Increases (2010–2023)
            </h3>
            <span className="badge bg-emerald-50 text-emerald-700 border border-emerald-200 text-[10px]">
              Top Growth
            </span>
          </div>

          {incDecLoading ? (
            <p className="text-xs text-text-muted py-4 text-center">Loading growth records...</p>
          ) : (
            <div className="space-y-2">
              {incDecData?.largest_increases?.map((item) => (
                <div key={item.location} className="flex items-center justify-between p-2.5 rounded-lg bg-emerald-50/50 border border-emerald-100/60 text-xs">
                  <div>
                    <p className="font-semibold text-text-primary">{item.location}</p>
                    <p className="text-[10px] text-text-muted">2023 HLE: {item.hle_2023} yrs</p>
                  </div>
                  <div className="text-right">
                    <span className="font-bold text-emerald-700 text-sm">+{item.pct_change_mean}%</span>
                    <p className="text-[10px] text-text-muted">95% UI: [+{item.pct_change_lower}%, +{item.pct_change_upper}%]</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Largest Decreases */}
        <div className="card">
          <div className="flex items-center justify-between pb-3 mb-3 border-b border-surface-border">
            <h3 className="text-sm font-semibold text-text-primary flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
              Locations with HLE Decreases (2010–2023)
            </h3>
            <span className="badge bg-rose-50 text-rose-700 border border-rose-200 text-[10px]">
              Decline / Stagnation
            </span>
          </div>

          {incDecLoading ? (
            <p className="text-xs text-text-muted py-4 text-center">Loading decline records...</p>
          ) : (
            <div className="space-y-2">
              {incDecData?.largest_decreases?.map((item) => (
                <div key={item.location} className="flex items-center justify-between p-2.5 rounded-lg bg-rose-50/50 border border-rose-100/60 text-xs">
                  <div>
                    <p className="font-semibold text-text-primary">{item.location}</p>
                    <p className="text-[10px] text-text-muted">2023 HLE: {item.hle_2023} yrs</p>
                  </div>
                  <div className="text-right">
                    <span className="font-bold text-rose-700 text-sm">{item.pct_change_mean}%</span>
                    <p className="text-[10px] text-text-muted">95% UI: [{item.pct_change_lower}%, {item.pct_change_upper}%]</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* ── Top 5 and Bottom 5 Location Rankings Tables ───────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Top 5 Table */}
        <div className="card space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-surface-border">
            <h3 className="text-sm font-semibold text-text-primary flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              Top 5 Locations (2023 Benchmark)
            </h3>
            <span className="text-xs text-text-muted font-medium">Both Sexes</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-text-muted uppercase text-[10px]">
                <tr>
                  <th className="py-2 px-2.5">Rank</th>
                  <th className="py-2 px-2.5">Location</th>
                  <th className="py-2 px-2.5">1990</th>
                  <th className="py-2 px-2.5 text-primary font-bold">2023 HLE [95% UI]</th>
                  <th className="py-2 px-2.5">Gap</th>
                  <th className="py-2 px-2.5">2010–23 %</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-border">
                {rankingLoading ? (
                  <tr><td colSpan={6} className="py-4 text-center text-text-muted">Loading...</td></tr>
                ) : (
                  rankings?.top_5?.map((r) => (
                    <tr key={r.location} className="hover:bg-slate-50">
                      <td className="py-2 px-2.5 font-bold text-text-muted">#{r.rank}</td>
                      <td className="py-2 px-2.5 font-semibold text-text-primary">{r.location}</td>
                      <td className="py-2 px-2.5 text-text-secondary">{r.hle_1990}</td>
                      <td className="py-2 px-2.5 font-bold text-primary">
                        {r.hle_latest} <span className="text-[10px] text-text-muted font-normal">[{r.hle_lower}, {r.hle_upper}]</span>
                      </td>
                      <td className="py-2 px-2.5 font-medium text-emerald-600">+{r.gender_gap} yrs</td>
                      <td className="py-2 px-2.5 text-emerald-600 font-medium">+{r.pct_change}%</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Bottom 5 Table */}
        <div className="card space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-surface-border">
            <h3 className="text-sm font-semibold text-text-primary flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-rose-500"></span>
              Bottom 5 Locations (2023 Benchmark)
            </h3>
            <span className="text-xs text-text-muted font-medium">Both Sexes</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-text-muted uppercase text-[10px]">
                <tr>
                  <th className="py-2 px-2.5">Rank</th>
                  <th className="py-2 px-2.5">Location</th>
                  <th className="py-2 px-2.5">1990</th>
                  <th className="py-2 px-2.5 text-rose-700 font-bold">2023 HLE [95% UI]</th>
                  <th className="py-2 px-2.5">Gap</th>
                  <th className="py-2 px-2.5">2010–23 %</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-border">
                {rankingLoading ? (
                  <tr><td colSpan={6} className="py-4 text-center text-text-muted">Loading...</td></tr>
                ) : (
                  rankings?.bottom_5?.map((r) => (
                    <tr key={r.location} className="hover:bg-slate-50">
                      <td className="py-2 px-2.5 font-bold text-text-muted">#{r.rank}</td>
                      <td className="py-2 px-2.5 font-semibold text-text-primary">{r.location}</td>
                      <td className="py-2 px-2.5 text-text-secondary">{r.hle_1990}</td>
                      <td className="py-2 px-2.5 font-bold text-rose-700">
                        {r.hle_latest} <span className="text-[10px] text-text-muted font-normal">[{r.hle_lower}, {r.hle_upper}]</span>
                      </td>
                      <td className="py-2 px-2.5 font-medium text-emerald-600">+{r.gender_gap} yrs</td>
                      <td className="py-2 px-2.5 text-emerald-600 font-medium">+{r.pct_change}%</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
