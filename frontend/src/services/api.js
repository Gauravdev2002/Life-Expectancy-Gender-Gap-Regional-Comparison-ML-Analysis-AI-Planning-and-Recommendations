// src/services/api.js
// Centralised API helpers – all fetch calls go through here.
// This makes it easy to swap the base URL or add auth headers later.

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

/**
 * Generic GET helper.
 * Returns parsed JSON or throws an error with a readable message.
 */
async function get(path) {
  const res = await fetch(`${BASE_URL}${path}`)
  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${res.statusText}`)
  }
  const contentType = res.headers.get('content-type') || ''
  if (!contentType.includes('application/json')) {
    throw new Error('Backend server is not running on port 8000. Start backend using start_system.bat or python -m uvicorn main:app')
  }
  return res.json()
}

/**
 * Generic POST helper.
 */
async function post(path, body = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}))
    throw new Error(errorData.detail || `API error ${res.status}: ${res.statusText}`)
  }
  const contentType = res.headers.get('content-type') || ''
  if (!contentType.includes('application/json')) {
    throw new Error('Backend server is not running on port 8000. Start backend using start_system.bat or python -m uvicorn main:app')
  }
  return res.json()
}

// ── Exported API functions ────────────────────────────────────────────────────

/** Ping the backend health endpoint */
export const fetchHealth = () => get('/health/')

/** Fetch system metadata */
export const fetchMetadata = () => get('/metadata')

/** Fetch the overview / project metadata */
export const fetchOverview = () => get('/overview/')

// ── Phase 8 Canonical Integration Helpers ─────────────────────────────────────

/** Canonical HLE analysis endpoint: GET /api/analyze/hle */
export const fetchAnalyzeHle = (location = 'Global', year = 2023, sex = 'both', nRankings = 10) =>
  get(`/analyze/hle?location=${encodeURIComponent(location)}&year=${year}&sex=${sex}&n_rankings=${nRankings}`)

/** Canonical Gender Gap analysis endpoint: GET /api/analyze/gender-gap */
export const fetchAnalyzeGenderGap = (year = 2023, n = 10, maxScatterPoints = 100) =>
  get(`/analyze/gender-gap?year=${year}&n=${n}&max_scatter_points=${maxScatterPoints}`)

/** Canonical trends analysis endpoint: GET /api/analyze/trends */
export const fetchAnalyzeTrends = (grouping = 'sdi', includeGainersDecliners = true, n = 5) =>
  get(`/analyze/trends?grouping=${grouping}&include_gainers_decliners=${includeGainersDecliners}&n=${n}`)

/** Canonical regional comparison endpoint: GET /api/analyze/regional-comparison */
export const fetchAnalyzeRegionalComparison = (grouping = 'sdi', year = 2023, sex = 'both', nRankings = 5) =>
  get(`/analyze/regional-comparison?grouping=${grouping}&year=${year}&sex=${sex}&n_rankings=${nRankings}`)

/** Canonical ML clusters endpoint: GET /api/ml/clusters */
export const fetchMlClusters = (k = 3, includeAggregates = false) =>
  get(`/ml/clusters?k=${k}&include_aggregates=${includeAggregates}`)

/** Canonical Global DALY endpoint: GET /api/global-burden/daly */
export const fetchGlobalBurdenDaly = (level = 2, topN = 10, sortBy = 'count') =>
  get(`/global-burden/daly?level=${level}&top_n=${topN}&sort_by=${sortBy}`)

/** Canonical Global YLD endpoint: GET /api/global-burden/yld */
export const fetchGlobalBurdenYld = (level = 2, topN = 10, sortBy = 'count') =>
  get(`/global-burden/yld?level=${level}&top_n=${topN}&sort_by=${sortBy}`)

/** Canonical AI Plan endpoint: POST /api/plan */
export const postPlan = (goalId) =>
  post('/plan', { goal_id: goalId })

/** Canonical Recommendations endpoint: GET /api/recommendations */
export const fetchSystemRecommendations = (lowHleThreshold = 56.9, genderGapThreshold = 5.0, maxPerCategory = 15) =>
  get(`/recommendations?low_hle_threshold=${lowHleThreshold}&gender_gap_threshold=${genderGapThreshold}&max_per_category=${maxPerCategory}`)

/** Canonical Master Reports endpoint: GET /api/reports */
export const fetchMasterReports = () =>
  get('/reports')

// ── HLE Analytics (Phase 3) ───────────────────────────────────────────────────

/** Fetch list of locations */
export const fetchHleLocations = (includeAggregates = true) =>
  get(`/analytics/hle/locations?include_aggregates=${includeAggregates}`)

/** Fetch historical trend and summary for a single location */
export const fetchHleTrend = (location = 'Global') =>
  get(`/analytics/hle/trend?location=${encodeURIComponent(location)}`)

/** Compare HLE across multiple locations */
export const fetchHleComparison = (locations = null, year = 2023, sex = 'both') => {
  const locQuery = locations && locations.length > 0 ? `&locations=${encodeURIComponent(locations.join(','))}` : ''
  return get(`/analytics/hle/comparison?year=${year}&sex=${sex}${locQuery}`)
}

/** Fetch highest and lowest HLE rankings */
export const fetchHleRankings = (year = 2023, sex = 'both', includeAggregates = false, n = 10) =>
  get(`/analytics/hle/rankings?year=${year}&sex=${sex}&include_aggregates=${includeAggregates}&n=${n}`)

/** Fetch gender gap analysis */
export const fetchGenderGapAnalysis = (year = 2023, includeAggregates = false, n = 10) =>
  get(`/analytics/hle/gender-gap?year=${year}&include_aggregates=${includeAggregates}&n=${n}`)

/** Fetch paginated, searchable location table */
export const fetchHleTable = ({
  search = '',
  includeAggregates = true,
  sortBy = 'hle_2023',
  sortAsc = false,
  page = 1,
  pageSize = 15,
} = {}) => {
  const sq = search ? `&search=${encodeURIComponent(search)}` : ''
  return get(
    `/analytics/hle/table?page=${page}&page_size=${pageSize}&sort_by=${sortBy}&sort_asc=${sortAsc}&include_aggregates=${includeAggregates}${sq}`
  )
}

// ── Regional Comparison & Trends (Phase 4) ────────────────────────────────────

/** Fetch available regional grouping categories */
export const fetchRegionalGroupings = () =>
  get('/analytics/regional/groupings')

/** Compare HLE across regional tiers or SDI quintiles */
export const fetchRegionalComparison = (grouping = 'sdi', year = 2023, sex = 'both') =>
  get(`/analytics/regional/comparison?grouping=${grouping}&year=${year}&sex=${sex}`)

/** Multi-year time-series trajectory across regional tiers */
export const fetchRegionalTrends = (grouping = 'sdi') =>
  get(`/analytics/regional/trends?grouping=${grouping}`)

/** Locations with largest increases and decreases between 2010 and 2023 */
export const fetchIncreaseDecreaseAnalysis = (includeAggregates = false, n = 5) =>
  get(`/analytics/regional/increase-decrease?include_aggregates=${includeAggregates}&n=${n}`)

/** Top 5 and Bottom 5 location rankings with hydrated indicators */
export const fetchTopBottomLocations = (year = 2023, includeAggregates = false, n = 5) =>
  get(`/analytics/regional/top-bottom?year=${year}&include_aggregates=${includeAggregates}&n=${n}`)

// ── Machine Learning (Phase 5) ────────────────────────────────────────────────

/** Fetch engineered feature definitions */
export const fetchMlFeatures = () =>
  get('/ml/features')

/** Run K-Means Clustering and PCA on Dataset S9 */
export const fetchMlClustering = (k = 3, includeAggregates = false) =>
  get(`/ml/clustering?k=${k}&include_aggregates=${includeAggregates}`)

// ── AI Planning (Phase 6) ─────────────────────────────────────────────────────

/** Fetch supported compound goals */
export const fetchPlanningGoals = () =>
  get('/planning/goals')

/** Fetch primitive STRIPS actions with preconditions/effects */
export const fetchPlanningActions = () =>
  get('/planning/actions')

/** Generate an HTN decomposition plan */
export const fetchGeneratedPlan = (goalId) =>
  post('/planning/plan', { goal_id: goalId })

/** Execute the HTN/STRIPS plan and get real execution trace and report */
export const executePlanningGoal = (goalId) =>
  post('/planning/execute', { goal_id: goalId })

// ── Gender Gap Analytics (Dedicated) ──────────────────────────────────────────

/** Fetch gender gap overview (Global benchmark, SDI gradient, trajectory) */
export const fetchGenderOverview = (year = 2023) =>
  get(`/analytics/gender/overview?year=${year}`)

/** Fetch top widest female advantages and narrowest/reversed gaps */
export const fetchGenderRankings = (year = 2023, n = 10) =>
  get(`/analytics/gender/rankings?year=${year}&n=${n}`)

/** Fetch Female vs Male HLE scatter data with equality reference line */
export const fetchGenderScatter = (year = 2023, maxPoints = 200) =>
  get(`/analytics/gender/scatter?year=${year}&max_points=${maxPoints}`)

/** Fetch paginated, searchable gender comparison table */
export const fetchGenderTable = ({
  year = 2023,
  search = '',
  sortBy = 'gender_gap',
  sortAsc = false,
  page = 1,
  pageSize = 15,
} = {}) => {
  const sq = search ? `&search=${encodeURIComponent(search)}` : ''
  return get(
    `/analytics/gender/table?year=${year}&page=${page}&page_size=${pageSize}&sort_by=${sortBy}&sort_asc=${sortAsc}${sq}`
  )
}

// ── Disease Burden Analytics (Datasets S10 & S11) ─────────────────────────────

/** Fetch global DALY/YLD totals and non-fatal burden share */
export const fetchDiseaseOverview = () =>
  get('/analytics/disease/overview')

/** Fetch Level 1 broad categories breakdown (Communicable vs NCDs vs Injuries) */
export const fetchDiseaseBreakdown = () =>
  get('/analytics/disease/breakdown')

/** Fetch top causes for DALYs or YLDs at Level 2 */
export const fetchTopCauses = (metric = 'daly', level = 2, n = 10, sortBy = 'count') =>
  get(`/analytics/disease/top-causes?metric=${metric}&level=${level}&n=${n}&sort_by=${sortBy}`)

/** Fetch DALY vs YLD comparison matrix (Fatal vs Disabling profiles) */
export const fetchDalyVsYldComparison = () =>
  get('/analytics/disease/comparison')

/** Fetch paginated, searchable disease cause table */
export const fetchDiseaseTable = ({
  metric = 'daly',
  level = null,
  search = '',
  sortBy = 'count_2023_mean',
  sortAsc = false,
  page = 1,
  pageSize = 15,
} = {}) => {
  const lq = level !== null ? `&level=${level}` : ''
  const sq = search ? `&search=${encodeURIComponent(search)}` : ''
  return get(
    `/analytics/disease/table?metric=${metric}&page=${page}&page_size=${pageSize}&sort_by=${sortBy}&sort_asc=${sortAsc}${lq}${sq}`
  )
}

// ── Evidence-Based Recommendations & Reports (Phase 7) ────────────────────────

/** Fetch categorized rule-based policy surveillance recommendations */
export const fetchRecommendations = (
  lowHleThreshold = 56.9,
  genderGapThreshold = 5.0,
  maxPerCategory = 15
) =>
  get(
    `/reports/recommendations?low_hle_threshold=${lowHleThreshold}&gender_gap_threshold=${genderGapThreshold}&max_per_category=${maxPerCategory}`
  )

/** Fetch full consolidated report JSON */
export const fetchFullReport = () =>
  get('/reports/full')

/** Download links */
export const getReportMarkdownUrl = () => `${BASE_URL}/reports/download/markdown`
export const getReportHtmlUrl = () => `${BASE_URL}/reports/download/html`


