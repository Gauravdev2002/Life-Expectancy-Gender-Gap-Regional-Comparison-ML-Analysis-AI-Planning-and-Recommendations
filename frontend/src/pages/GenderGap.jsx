// src/pages/GenderGap.jsx
// Dedicated Gender Gap Analysis Page
// Uses actual data from Dataset S9.

import React, { useState, useEffect } from 'react'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import {
  fetchGenderOverview,
  fetchGenderRankings,
  fetchGenderScatter,
  fetchGenderTable,
} from '../services/api'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'

export default function GenderGap() {
  const [year, setYear] = useState(2023)
  const [overview, setOverview] = useState(null)
  const [rankings, setRankings] = useState(null)
  const [scatterData, setScatterData] = useState([])
  const [tableData, setTableData] = useState({ records: [], total: 0, total_pages: 1 })
  const [searchTerm, setSearchTerm] = useState('')
  const [sortBy, setSortBy] = useState('gender_gap')
  const [sortAsc, setSortAsc] = useState(false)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [tableLoading, setTableLoading] = useState(false)
  const [error, setError] = useState(null)

  // Load overview, rankings, and scatter when year changes
  useEffect(() => {
    let isMounted = true
    setLoading(true)
    setError(null)

    Promise.all([
      fetchGenderOverview(year),
      fetchGenderRankings(year, 10),
      fetchGenderScatter(year, 120),
    ])
      .then(([ov, rk, sc]) => {
        if (!isMounted) return
        setOverview(ov)
        setRankings(rk)
        setScatterData(sc.points || [])
        setLoading(false)
      })
      .catch((err) => {
        if (!isMounted) return
        setError(err.message || 'Failed to load gender gap data')
        setLoading(false)
      })

    return () => {
      isMounted = false
    }
  }, [year])

  // Load paginated table
  useEffect(() => {
    let isMounted = true
    setTableLoading(true)

    fetchGenderTable({
      year,
      search: searchTerm,
      sortBy,
      sortAsc,
      page,
      pageSize: 15,
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
  }, [year, searchTerm, sortBy, sortAsc, page])

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value)
    setPage(1)
  }

  const handleSort = (col) => {
    if (sortBy === col) {
      setSortAsc(!sortAsc)
    } else {
      setSortBy(col)
      setSortAsc(false)
    }
    setPage(1)
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <PageHeader
          title="Gender Gap Analysis"
          subtitle="Empirical comparison of Female vs Male Healthy Life Expectancy (HLE) from Dataset S9."
          badge="Verified GBD Data"
        />

        {/* Year Selector */}
        <div className="flex items-center gap-2 bg-white px-3 py-2 rounded-lg border border-slate-200 shadow-xs self-start sm:self-auto">
          <span className="text-xs font-semibold uppercase text-slate-500">Target Year:</span>
          <div className="flex gap-1">
            {[2023, 2020, 2010, 1990].map((y) => (
              <button
                key={y}
                onClick={() => {
                  setYear(y)
                  setPage(1)
                }}
                className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                  year === y
                    ? 'bg-blue-600 text-white shadow-xs'
                    : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                {y}
              </button>
            ))}
          </div>
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
          label={`Global Gender Gap (${year})`}
          value={overview ? `+${overview.global_gender_gap} yrs` : '…'}
          sub={
            overview
              ? `Female: ${overview.global_female_hle} yrs | Male: ${overview.global_male_hle} yrs`
              : 'Calculating…'
          }
          color="blue"
        />
        <StatCard
          label="Parity Ratio (Female / Male)"
          value={overview ? `${overview.global_parity_ratio}` : '…'}
          sub="Ratio > 1.0 indicates female survival advantage"
          color="purple"
        />
        <StatCard
          label="Widest Female Advantage"
          value={
            overview?.country_distribution?.widest_country
              ? `+${overview.country_distribution.widest_country.gap} yrs`
              : '…'
          }
          sub={overview?.country_distribution?.widest_country?.location || '—'}
          color="green"
        />
        <StatCard
          label="Narrowest / Reversed Gap"
          value={
            overview?.country_distribution?.narrowest_country
              ? `${overview.country_distribution.narrowest_country.gap} yrs`
              : '…'
          }
          sub={overview?.country_distribution?.narrowest_country?.location || '—'}
          color="amber"
        />
      </div>

      {/* Trajectory & SDI Gradient Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Historical Gender Gap Trajectory */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="mb-4">
            <h3 className="text-base font-semibold text-slate-800">
              Global HLE Trajectory by Sex (1990–2023)
            </h3>
            <p className="text-xs text-slate-500">
              Evolution of Female HLE, Male HLE, and resulting Gender Gap (yrs).
            </p>
          </div>
          <div className="h-72">
            {overview?.historical_trajectory ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={overview.historical_trajectory}
                  margin={{ top: 10, right: 20, left: 0, bottom: 10 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="year" stroke="#64748b" tick={{ fontSize: 12 }} />
                  <YAxis
                    stroke="#64748b"
                    tick={{ fontSize: 12 }}
                    domain={['dataMin - 5', 'dataMax + 5']}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#ffffff',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '12px',
                    }}
                    formatter={(val, name) => [`${val} years`, name]}
                  />
                  <Legend wrapperStyle={{ fontSize: '12px' }} />
                  <Line
                    type="monotone"
                    dataKey="female_hle"
                    name="Female HLE"
                    stroke="#ec4899"
                    strokeWidth={2.5}
                    dot={{ r: 4 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="male_hle"
                    name="Male HLE"
                    stroke="#3b82f6"
                    strokeWidth={2.5}
                    dot={{ r: 4 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="gender_gap"
                    name="Gender Gap (F - M)"
                    stroke="#8b5cf6"
                    strokeWidth={2}
                    strokeDasharray="4 4"
                    dot={{ r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 text-sm">
                Loading trajectory…
              </div>
            )}
          </div>
        </div>

        {/* SDI Gradient Bar Chart */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="mb-4">
            <h3 className="text-base font-semibold text-slate-800">
              Gender Gap across SDI Quintiles ({year})
            </h3>
            <p className="text-xs text-slate-500">
              Female advantage expands from Low SDI (+1.3 yrs) to High-Middle SDI (+4.1 yrs).
            </p>
          </div>
          <div className="h-72">
            {overview?.sdi_gradient ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={overview.sdi_gradient}
                  margin={{ top: 10, right: 20, left: 0, bottom: 25 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis
                    dataKey="sdi_level"
                    stroke="#64748b"
                    tick={{ fontSize: 11 }}
                    angle={-15}
                    textAnchor="end"
                  />
                  <YAxis stroke="#64748b" tick={{ fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#ffffff',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '12px',
                    }}
                    formatter={(val, name) => [`${val} years`, name]}
                  />
                  <Legend wrapperStyle={{ fontSize: '12px' }} />
                  <Bar dataKey="female_hle" name="Female HLE" fill="#ec4899" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="male_hle" name="Male HLE" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="gender_gap" name="Gap (F - M)" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 text-sm">
                Loading SDI comparison…
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Scatter Plot & Rankings Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Scatter Plot: Female vs Male HLE */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="mb-4">
            <h3 className="text-base font-semibold text-slate-800">
              Female vs. Male HLE Correlation & Parity
            </h3>
            <p className="text-xs text-slate-500">
              Diagonal dashed line represents gender parity ($y = x$). Points above indicate female advantage.
            </p>
          </div>
          <div className="h-80">
            {scatterData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 10, right: 20, left: 0, bottom: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis
                    type="number"
                    dataKey="male_hle"
                    name="Male HLE"
                    unit=" yrs"
                    domain={[40, 75]}
                    stroke="#64748b"
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis
                    type="number"
                    dataKey="female_hle"
                    name="Female HLE"
                    unit=" yrs"
                    domain={[40, 75]}
                    stroke="#64748b"
                    tick={{ fontSize: 12 }}
                  />
                  <Tooltip
                    cursor={{ strokeDasharray: '3 3' }}
                    contentStyle={{
                      backgroundColor: '#ffffff',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '12px',
                    }}
                    formatter={(val, name, item) => {
                      if (name === 'Female HLE') return [`${val} yrs`, 'Female HLE']
                      if (name === 'Male HLE') return [`${val} yrs`, 'Male HLE']
                      return [val, name]
                    }}
                    labelFormatter={(_, payload) => {
                      if (payload && payload.length > 0) {
                        return payload[0].payload.location
                      }
                      return ''
                    }}
                  />
                  {/* Equality diagonal reference line */}
                  <ReferenceLine
                    segment={[{ x: 45, y: 45 }, { x: 75, y: 75 }]}
                    stroke="#94a3b8"
                    strokeDasharray="4 4"
                    label={{ value: 'Parity (y = x)', fill: '#64748b', fontSize: 11, position: 'insideTopLeft' }}
                  />
                  <Scatter
                    name="Countries"
                    data={scatterData}
                    fill="#3b82f6"
                    fillOpacity={0.65}
                  />
                </ScatterChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 text-sm">
                Loading correlation scatter…
              </div>
            )}
          </div>
        </div>

        {/* Top 5 Widest vs Top 5 Narrowest Rankings */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <div className="mb-4">
              <h3 className="text-base font-semibold text-slate-800">
                Extreme Gender Gap Disparities ({year})
              </h3>
              <p className="text-xs text-slate-500">
                Top female advantages (Eastern Europe/Eurasia) vs. narrowest/reversed gaps.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Widest Female Advantage */}
              <div className="border border-green-200 bg-green-50/40 rounded-lg p-3">
                <h4 className="text-xs font-bold text-green-800 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-green-600"></span>
                  Largest Female Advantage
                </h4>
                <div className="space-y-1.5 text-xs">
                  {rankings?.widest_female_advantage?.slice(0, 5).map((r, i) => (
                    <div
                      key={r.location}
                      className="flex items-center justify-between py-1 border-b border-green-100 last:border-0"
                    >
                      <span className="font-medium text-slate-700 truncate max-w-[130px]">
                        {i + 1}. {r.location}
                      </span>
                      <span className="font-semibold text-green-700">
                        +{r.gender_gap} yrs
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Narrowest / Reversed Gap */}
              <div className="border border-amber-200 bg-amber-50/40 rounded-lg p-3">
                <h4 className="text-xs font-bold text-amber-800 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-amber-600"></span>
                  Narrowest / Reversed Gap
                </h4>
                <div className="space-y-1.5 text-xs">
                  {rankings?.narrowest_or_reverse_gap?.slice(0, 5).map((r, i) => (
                    <div
                      key={r.location}
                      className="flex items-center justify-between py-1 border-b border-amber-100 last:border-0"
                    >
                      <span className="font-medium text-slate-700 truncate max-w-[130px]">
                        {i + 1}. {r.location}
                      </span>
                      <span
                        className={`font-semibold ${
                          r.gender_gap < 0 ? 'text-red-600' : 'text-amber-700'
                        }`}
                      >
                        {r.gender_gap > 0 ? `+${r.gender_gap}` : r.gender_gap} yrs
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Academic Explanation Card */}
          <div className="mt-4 p-3.5 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-600 leading-relaxed">
            <span className="font-semibold text-slate-800">Epidemiological Insights: </span>
            Large positive gaps (e.g., Ukraine +7.9 yrs, Russia +7.3 yrs) reflect acute male mortality
            driven by cardiovascular disease, hazardous substance use, and traumatic injuries.
            Conversely, reversed or narrow gaps occur predominantly in regions where high maternal mortality
            or healthcare accessibility barriers constrain female longevity gains.
          </div>
        </div>
      </div>

      {/* Comprehensive Location Table */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
          <div>
            <h3 className="text-base font-semibold text-slate-800">
              Location-Wise Gender Comparison Table ({year})
            </h3>
            <p className="text-xs text-slate-500">
              Showing {tableData.total} countries and subnational locations with 95% uncertainty intervals.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="text"
              placeholder="Search location…"
              value={searchTerm}
              onChange={handleSearchChange}
              className="text-xs px-3 py-1.5 border border-slate-200 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 w-48 sm:w-60"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600">
            <thead className="bg-slate-50 text-slate-700 font-semibold border-b border-slate-200">
              <tr>
                <th
                  className="py-2.5 px-3 cursor-pointer hover:bg-slate-100"
                  onClick={() => handleSort('location')}
                >
                  Location {sortBy === 'location' && (sortAsc ? '↑' : '↓')}
                </th>
                <th
                  className="py-2.5 px-3 cursor-pointer hover:bg-slate-100"
                  onClick={() => handleSort('female_hle')}
                >
                  Female HLE (95% UI) {sortBy === 'female_hle' && (sortAsc ? '↑' : '↓')}
                </th>
                <th
                  className="py-2.5 px-3 cursor-pointer hover:bg-slate-100"
                  onClick={() => handleSort('male_hle')}
                >
                  Male HLE (95% UI) {sortBy === 'male_hle' && (sortAsc ? '↑' : '↓')}
                </th>
                <th
                  className="py-2.5 px-3 cursor-pointer hover:bg-slate-100 text-right"
                  onClick={() => handleSort('gender_gap')}
                >
                  Gender Gap (F - M) {sortBy === 'gender_gap' && (sortAsc ? '↑' : '↓')}
                </th>
                <th
                  className="py-2.5 px-3 cursor-pointer hover:bg-slate-100 text-right"
                  onClick={() => handleSort('parity_ratio')}
                >
                  Parity Ratio {sortBy === 'parity_ratio' && (sortAsc ? '↑' : '↓')}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {tableLoading ? (
                <tr>
                  <td colSpan="5" className="py-8 text-center text-slate-400">
                    Loading table records…
                  </td>
                </tr>
              ) : tableData.records.length === 0 ? (
                <tr>
                  <td colSpan="5" className="py-8 text-center text-slate-400">
                    No matching location records found.
                  </td>
                </tr>
              ) : (
                tableData.records.map((r) => (
                  <tr key={r.location} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-2 px-3 font-medium text-slate-800">{r.location}</td>
                    <td className="py-2 px-3 text-slate-700">
                      <span className="font-semibold text-pink-600">{r.female_hle}</span>
                      <span className="text-[11px] text-slate-400 ml-1">
                        [{r.female_lower}–{r.female_upper}]
                      </span>
                    </td>
                    <td className="py-2 px-3 text-slate-700">
                      <span className="font-semibold text-blue-600">{r.male_hle}</span>
                      <span className="text-[11px] text-slate-400 ml-1">
                        [{r.male_lower}–{r.male_upper}]
                      </span>
                    </td>
                    <td className="py-2 px-3 text-right">
                      <span
                        className={`inline-block px-2 py-0.5 rounded-full font-semibold ${
                          r.gender_gap > 3.0
                            ? 'bg-green-50 text-green-700 border border-green-200'
                            : r.gender_gap >= 0
                            ? 'bg-blue-50 text-blue-700 border border-blue-200'
                            : 'bg-red-50 text-red-700 border border-red-200'
                        }`}
                      >
                        {r.gender_gap > 0 ? `+${r.gender_gap}` : r.gender_gap} yrs
                      </span>
                    </td>
                    <td className="py-2 px-3 text-right font-mono text-slate-600">
                      {r.parity_ratio}
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
            Page {tableData.page} of {tableData.total_pages} ({tableData.total} total)
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
