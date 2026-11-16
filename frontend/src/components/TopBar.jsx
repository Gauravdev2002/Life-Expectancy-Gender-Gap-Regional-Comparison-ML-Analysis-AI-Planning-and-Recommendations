// src/components/TopBar.jsx
// Horizontal bar at the top of every page – shows the current page title.

import React from 'react'
import { useLocation } from 'react-router-dom'

// Map route paths to human-readable page titles
const PAGE_TITLES = {
  '/overview':        'Overview',
  '/life-expectancy': 'Life Expectancy Analysis',
  '/gender-gap':      'Gender Gap Analysis',
  '/regional':        'Regional Comparison',
  '/ml-analysis':     'Machine Learning Analysis',
  '/disease-burden':  'Disease Burden',
  '/ai-planning':     'AI Planning',
  '/recommendations': 'Recommendations & Reports',
}

export default function TopBar() {
  const { pathname } = useLocation()
  const title = PAGE_TITLES[pathname] ?? 'Dashboard'

  return (
    <header className="h-14 bg-white border-b border-surface-border flex items-center justify-between px-6 flex-shrink-0">
      {/* Page title */}
      <h1 className="text-base font-semibold text-text-primary">{title}</h1>

      {/* Right side – project label badge */}
      <div className="flex items-center gap-3">
        <span className="badge bg-blue-50 text-primary border border-blue-100">
          AI Health Intelligence
        </span>
        <span className="badge bg-success-light text-success border border-green-200">
          Phase 1
        </span>
      </div>
    </header>
  )
}
