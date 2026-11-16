// src/pages/LifeExpectancy.jsx
// Phase 3: Healthy Life Expectancy Analytics Dashboard
// Powered strictly by real GBD Dataset S9 records.

import React, { useState, useEffect } from 'react'
import {
  LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import {
  fetchHleLocations,
  fetchHleTrend,
  fetchHleComparison,
  fetchHleRankings,
  fetchHleTable
} from '../services/api'

// Benchmark quick-select buttons
const QUICK_LOCATIONS = [
  'Global',
  'High SDI',
  'Middle SDI',
  'Low SDI',
  'Japan',
  'Singapore',
  'United States of America',
  'India',
  'China',
  'Nigeria',
  'Brazil',
]

export default function LifeExpectancy() {
  // ── State ──────────────────────────────────────────────────────────────────
  const [locations, setLocations] = useState([])
  const [selectedLocation, setSelectedLocation] = useState('Global')
  const [trendData, setTrendData] = useState(null)
  const [trendLoading, setTrendLoading] = useState(true)

  // Comparison chart state
  const [compYear, setCompYear] = useState(2023)
  const [compSex, setCompSex] = useState('both')
  const [comparisonData, setComparisonData] = useState([])
  const [compLoading, setCompLoading] = useState(true)

  // Rankings state
  const [rankings, setRankings] = useState(null)
  const [rankingLoading, setRankingLoading] = useState(true)

  // Table state
  const [tableSearch, setTableSearch] = useState('')
  const [includeAggs, setIncludeAggs] = useState(true)
  const [tableSort, setTableSort] = useState('hle_2023')
  const [tableSortAsc, setTableSortAsc] = useState(false)
  const [tablePage, setTablePage] = useState(1)
  const [tableData, setTableData] = useState(null)
  const [tableLoading, setTableLoading] = useState(true)

  // ── Load Locations List on Mount ───────────────────────────────────────────
  useEffect(() => {
    fetchHleLocations(true)
      .then(res => setLocations(res.locations || []))
      .catch(err => console.error('Error fetching locations:', err))
  }, [])

  // ── Load Trend & Summary for Selected Location ─────────────────────────────
  useEffect(() => {
    setTrendLoading(true)
    fetchHleTrend(selectedLocation)
      .then(data => {
        setTrendData(data)
        setTrendLoading(false)
      })
      .catch(err => {
        console.error('Error fetching trend:', err)
        setTrendLoading(false)
      })
  }, [selectedLocation])

  // ── Load Comparison Chart Data ─────────────────────────────────────────────
  useEffect(() => {
    setCompLoading(true)
    fetchHleComparison(null, compYear, compSex)
      .then(data => {
        setComparisonData(data || [])
        setCompLoading(false)
      })
      .catch(err => {
        console.error('Error fetching comparison:', err)
        setCompLoading(false)
      })
  }, [compYear, compSex])

  // ── Load Top/Bottom Rankings ───────────────────────────────────────────────
  useEffect(() => {
    setRankingLoading(true)
    fetchHleRankings(2023, 'both', false, 5)
      .then(data => {
        setRankings(data)
        setRankingLoading(false)
      })
      .catch(err => {
        console.error('Error fetching rankings:', err)
        setRankingLoading(false)
      })
  }, [])

  // ── Load Comprehensive Table Data ──────────────────────────────────────────
  useEffect(() => {
    setTableLoading(true)
    fetchHleTable({
      search: tableSearch,
      includeAggregates: includeAggs,
      sortBy: tableSort,
      sortAsc: tableSortAsc,
      page: tablePage,
      pageSize: 12,
    })
      .then(data => {
        setTableData(data)
        setTableLoading(false)
      })
      .catch(err => {
        console.error('Error fetching table:', err)
        setTableLoading(false)
      })
  }, [tableSearch, includeAggs, tableSort, tableSortAsc, tablePage])

  const summary = trendData?.summary

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

  return (
    <div className="space-y-6">
      <PageHeader
        title="Life Expectancy Analysis"
        subtitle="Historical trends, demographic differentials, and cross-national Healthy Life Expectancy (HLE) benchmarks from GBD Study data."
        badge="Phase 3 Live"
      />

      {/* ── Control Bar: Location Selection & Fast Benchmarking ────────────── */}
      <div className="card space-y-3">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <label htmlFor="loc-select" className="text-xs font-semibold uppercase text-text-muted">
              Select Location:
            </label>
            <select
              id="loc-select"
              value={selectedLocation}
              onChange={(e) => setSelectedLocation(e.target.value)}
              className="bg-slate-50 border border-surface-border text-sm font-medium rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-primary"
            >
              {locations.map((loc) => (
                <option key={loc} value={loc}>
                  {loc}
                </option>
              ))}
            </select>
          </div>

          <div className="flex flex-wrap items-center gap-1.5 text-xs">
            <span className="text-text-muted font-medium">Quick benchmarks:</span>
            {QUICK_LOCATIONS.map((loc) => (
              <button
                key={loc}
                onClick={() => setSelectedLocation(loc)}
                className={`px-2.5 py-1 rounded-md text-xs font-medium border transition-colors ${
                  selectedLocation.toLowerCase() === loc.toLowerCase()
                    ? 'bg-primary text-white border-primary'
                    : 'bg-white text-text-secondary border-surface-border hover:bg-slate-100'
                }`}
              >
                {loc}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ── Summary Stat Cards for Selected Location ──────────────────────── */}
      {trendLoading ? (
        <div className="card py-8 text-center text-sm text-text-muted">Loading location indicators...</div>
      ) : summary ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          <StatCard
            label="2023 HLE (Both)"
            value={`${summary.hle_2023_mean ?? '—'} yrs`}
            sub={`95% UI: [${summary.hle_2023_lower ?? '—'}, ${summary.hle_2023_upper ?? '—'}]`}
            color="blue"
          />
          <StatCard
            label="1990 Baseline"
            value={`${summary.hle_1990_mean ?? '—'} yrs`}
            sub={`Net: ${summary.net_change_1990_2023 > 0 ? '+' : ''}${summary.net_change_1990_2023 ?? '—'} yrs`}
            color="green"
          />
          <StatCard
            label="2023 Female HLE"
            value={`${summary.female_hle_2023 ?? '—'} yrs`}
            sub="Female population mean"
            color="purple"
          />
          <StatCard
            label="2023 Male HLE"
            value={`${summary.male_hle_2023 ?? '—'} yrs`}
            sub="Male population mean"
            color="purple"
          />
          <StatCard
            label="Gender HLE Gap"
            value={`${summary.gender_gap_2023 > 0 ? '+' : ''}${summary.gender_gap_2023 ?? '—'} yrs`}
            sub={summary.gender_gap_2023 >= 0 ? 'Female advantage' : 'Male advantage'}
            color={summary.gender_gap_2023 >= 0 ? 'green' : 'amber'}
          />
          <StatCard
            label="2010–23 % Change"
            value={`${summary.pct_change_2010_2023_mean > 0 ? '+' : ''}${summary.pct_change_2010_2023_mean ?? '—'}%`}
            sub={`UI: [${summary.pct_change_2010_2023_lower}%, ${summary.pct_change_2010_2023_upper}%]`}
            color={summary.pct_change_2010_2023_mean >= 0 ? 'green' : 'amber'}
          />
        </div>
      ) : null}

      {/* ── Two-Column Charts: Historical Trend & Gender Comparison ───────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Trend Chart */}
        <div className="card flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-text-primary">
                Year-Wise HLE Trajectory — {trendData?.location ?? selectedLocation}
              </h3>
              <p className="text-xs text-text-muted">Tracking HLE in 1990, 2010, 2020, and 2023</p>
            </div>
            <span className="badge bg-blue-50 text-primary border border-blue-200">
              {trendData?.is_aggregate ? 'Aggregate Region' : 'Sovereign/Territorial'}
            </span>
          </div>

          <div className="h-64 w-full">
            {trendLoading ? (
              <div className="flex items-center justify-center h-full text-xs text-text-muted">Loading chart...</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendData?.trend || []} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                  <XAxis dataKey="year" tick={{ fontSize: 12, fill: '#64748B' }} />
                  <YAxis domain={['auto', 'auto']} tick={{ fontSize: 12, fill: '#64748B' }} unit=" yrs" />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend wrapperStyle={{ fontSize: 12, paddingTop: 10 }} />
                  <Line type="monotone" dataKey="both_mean" name="Both Sexes" stroke="#1D4ED8" strokeWidth={2.5} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                  <Line type="monotone" dataKey="female_mean" name="Female" stroke="#059669" strokeWidth={2} strokeDasharray="4 4" dot={{ r: 3 }} />
                  <Line type="monotone" dataKey="male_mean" name="Male" stroke="#7C3AED" strokeWidth={2} strokeDasharray="2 2" dot={{ r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
          <p className="text-[11px] text-text-muted text-center mt-2">
            Values indicate mean Healthy Life Expectancy at birth (years).
          </p>
        </div>

        {/* Female vs Male Bar Chart & Gap */}
        <div className="card flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-text-primary">
                Gender Disaggregation — {trendData?.location ?? selectedLocation}
              </h3>
              <p className="text-xs text-text-muted">Side-by-side Female vs. Male HLE and Gender Gap (F - M)</p>
            </div>
            <span className="badge bg-purple-50 text-accent border border-purple-200">
              Gender Gap
            </span>
          </div>

          <div className="h-64 w-full">
            {trendLoading ? (
              <div className="flex items-center justify-center h-full text-xs text-text-muted">Loading chart...</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={trendData?.trend || []} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                  <XAxis dataKey="year" tick={{ fontSize: 12, fill: '#64748B' }} />
                  <YAxis domain={['auto', 'auto']} tick={{ fontSize: 12, fill: '#64748B' }} unit=" yrs" />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend wrapperStyle={{ fontSize: 12, paddingTop: 10 }} />
                  <Bar dataKey="female_mean" name="Female HLE" fill="#059669" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="male_mean" name="Male HLE" fill="#7C3AED" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="gender_gap" name="Gender Gap (F - M)" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
          <p className="text-[11px] text-text-muted text-center mt-2">
            Gender Gap is calculated as: Female HLE minus Male HLE.
          </p>
        </div>
      </div>

      {/* ── Cross-Location Comparison Chart ──────────────────────────────── */}
      <div className="card">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <div>
            <h3 className="text-sm font-semibold text-text-primary">Regional & Country HLE Comparison</h3>
            <p className="text-xs text-text-muted">Comparing benchmark cohorts sorted by Healthy Life Expectancy</p>
          </div>
          <div className="flex items-center gap-3 text-xs">
            <div className="flex items-center gap-1.5">
              <span className="text-text-muted font-medium">Year:</span>
              <select
                value={compYear}
                onChange={(e) => setCompYear(Number(e.target.value))}
                className="bg-slate-50 border border-surface-border text-xs rounded-md px-2 py-1 font-medium"
              >
                <option value={1990}>1990</option>
                <option value={2010}>2010</option>
                <option value={2020}>2020</option>
                <option value={2023}>2023</option>
              </select>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-text-muted font-medium">Sex:</span>
              <select
                value={compSex}
                onChange={(e) => setCompSex(e.target.value)}
                className="bg-slate-50 border border-surface-border text-xs rounded-md px-2 py-1 font-medium"
              >
                <option value="both">Both Sexes</option>
                <option value="female">Females</option>
                <option value="male">Males</option>
              </select>
            </div>
          </div>
        </div>

        <div className="h-72 w-full">
          {compLoading ? (
            <div className="flex items-center justify-center h-full text-xs text-text-muted">Loading comparison...</div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={comparisonData} margin={{ top: 10, right: 20, left: -10, bottom: 35 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                <XAxis dataKey="location" angle={-30} textAnchor="end" interval={0} tick={{ fontSize: 11, fill: '#475569' }} />
                <YAxis domain={['auto', 'auto']} tick={{ fontSize: 11, fill: '#64748B' }} unit=" yrs" />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="hle_mean" name="Healthy Life Expectancy" fill="#1D4ED8" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* ── Rankings Section: Top 5 Highest vs Top 5 Lowest ────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Highest HLE */}
        <div className="card">
          <div className="flex items-center justify-between pb-3 mb-3 border-b border-surface-border">
            <h3 className="text-sm font-semibold text-text-primary flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              Top 5 Highest HLE (2023, Sovereign/Territorial)
            </h3>
            <span className="text-xs text-text-muted font-medium">Both Sexes</span>
          </div>
          {rankingLoading ? (
            <p className="text-xs text-text-muted py-4 text-center">Loading rankings...</p>
          ) : (
            <div className="space-y-2.5">
              {rankings?.highest?.map((item) => (
                <div key={item.location} className="flex items-center justify-between p-2.5 rounded-lg bg-emerald-50/50 border border-emerald-100/60 text-xs">
                  <div className="flex items-center gap-2.5">
                    <span className="w-5 h-5 rounded-full bg-emerald-600 text-white font-bold flex items-center justify-center text-[10px]">
                      {item.rank}
                    </span>
                    <span className="font-semibold text-text-primary">{item.location}</span>
                  </div>
                  <div className="text-right">
                    <span className="font-bold text-emerald-700 text-sm">{item.hle_mean} yrs</span>
                    <p className="text-[10px] text-text-muted">95% UI: [{item.hle_lower}, {item.hle_upper}]</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Lowest HLE */}
        <div className="card">
          <div className="flex items-center justify-between pb-3 mb-3 border-b border-surface-border">
            <h3 className="text-sm font-semibold text-text-primary flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-rose-500"></span>
              Lowest 5 HLE Locations (2023, Sovereign/Territorial)
            </h3>
            <span className="text-xs text-text-muted font-medium">Both Sexes</span>
          </div>
          {rankingLoading ? (
            <p className="text-xs text-text-muted py-4 text-center">Loading rankings...</p>
          ) : (
            <div className="space-y-2.5">
              {rankings?.lowest?.map((item) => (
                <div key={item.location} className="flex items-center justify-between p-2.5 rounded-lg bg-rose-50/50 border border-rose-100/60 text-xs">
                  <div className="flex items-center gap-2.5">
                    <span className="w-5 h-5 rounded-full bg-rose-600 text-white font-bold flex items-center justify-center text-[10px]">
                      {item.rank}
                    </span>
                    <span className="font-semibold text-text-primary">{item.location}</span>
                  </div>
                  <div className="text-right">
                    <span className="font-bold text-rose-700 text-sm">{item.hle_mean} yrs</span>
                    <p className="text-[10px] text-text-muted">95% UI: [{item.hle_lower}, {item.hle_upper}]</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* ── Comprehensive Location Data Table ────────────────────────────── */}
      <div className="card space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-semibold text-text-primary">Comprehensive Location Registry</h3>
            <p className="text-xs text-text-muted">
              Displaying {tableData?.total_records ?? 0} locations from GBD S9 with complete uncertainty intervals
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <input
              type="text"
              placeholder="Search location..."
              value={tableSearch}
              onChange={(e) => {
                setTableSearch(e.target.value)
                setTablePage(1)
              }}
              className="px-3 py-1.5 text-xs bg-slate-50 border border-surface-border rounded-lg focus:outline-none focus:ring-1 focus:ring-primary w-48"
            />
            <label className="flex items-center gap-1.5 text-xs text-text-secondary cursor-pointer">
              <input
                type="checkbox"
                checked={includeAggs}
                onChange={(e) => {
                  setIncludeAggs(e.target.checked)
                  setTablePage(1)
                }}
                className="rounded text-primary focus:ring-0"
              />
              Include Macro Aggregates
            </label>
          </div>
        </div>

        {/* Table container */}
        <div className="overflow-x-auto border border-surface-border rounded-lg">
          <table className="w-full text-left text-xs border-collapse">
            <thead className="bg-slate-50 text-text-muted uppercase font-semibold text-[11px] border-b border-surface-border">
              <tr>
                <th className="py-2.5 px-3">Location</th>
                <th className="py-2.5 px-3">1990 HLE</th>
                <th className="py-2.5 px-3">2010 HLE</th>
                <th className="py-2.5 px-3">2020 HLE</th>
                <th className="py-2.5 px-3 text-primary font-bold">2023 HLE [95% UI]</th>
                <th className="py-2.5 px-3">2023 Female</th>
                <th className="py-2.5 px-3">2023 Male</th>
                <th className="py-2.5 px-3">Gender Gap</th>
                <th className="py-2.5 px-3">2010–23 % Change</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-border">
              {tableLoading ? (
                <tr>
                  <td colSpan={9} className="py-6 text-center text-text-muted">Loading registry records...</td>
                </tr>
              ) : tableData?.records?.length ? (
                tableData.records.map((r) => (
                  <tr key={r.location} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-2.5 px-3 font-semibold text-text-primary">
                      {r.location}
                      {r.is_aggregate && (
                        <span className="ml-1.5 px-1.5 py-0.5 rounded text-[9px] bg-slate-100 text-slate-500 font-normal">
                          Aggregate
                        </span>
                      )}
                    </td>
                    <td className="py-2.5 px-3">{r.hle_1990 ?? '—'}</td>
                    <td className="py-2.5 px-3">{r.hle_2010 ?? '—'}</td>
                    <td className="py-2.5 px-3">{r.hle_2020 ?? '—'}</td>
                    <td className="py-2.5 px-3 font-semibold text-primary">
                      {r.hle_2023 ? `${r.hle_2023} [${r.hle_2023_lower}, ${r.hle_2023_upper}]` : '—'}
                    </td>
                    <td className="py-2.5 px-3 text-emerald-600 font-medium">{r.female_hle_2023 ?? '—'}</td>
                    <td className="py-2.5 px-3 text-purple-600 font-medium">{r.male_hle_2023 ?? '—'}</td>
                    <td className="py-2.5 px-3 font-semibold">
                      {r.gender_gap_2023 !== null ? (
                        <span className={r.gender_gap_2023 >= 0 ? 'text-emerald-600' : 'text-amber-600'}>
                          {r.gender_gap_2023 > 0 ? '+' : ''}{r.gender_gap_2023} yrs
                        </span>
                      ) : '—'}
                    </td>
                    <td className="py-2.5 px-3">
                      {r.pct_change_2010_2023 !== null ? (
                        <span className={r.pct_change_2010_2023 >= 0 ? 'text-emerald-600' : 'text-amber-600'}>
                          {r.pct_change_2010_2023 > 0 ? '+' : ''}{r.pct_change_2010_2023}%
                        </span>
                      ) : '—'}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={9} className="py-6 text-center text-text-muted">No matching location records found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination controls */}
        {tableData && tableData.total_pages > 1 && (
          <div className="flex items-center justify-between text-xs pt-1">
            <span className="text-text-muted">
              Page {tableData.page} of {tableData.total_pages} ({tableData.total_records} total locations)
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
                disabled={tablePage >= tableData.total_pages}
                onClick={() => setTablePage(p => Math.min(tableData.total_pages, p + 1))}
                className="px-2.5 py-1 bg-white border border-surface-border rounded-md font-medium text-text-secondary disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-50"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
