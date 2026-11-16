// src/App.jsx
// Root component – lays out the sidebar + main content area side by side.

import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'

import Sidebar from './components/Sidebar'
import TopBar  from './components/TopBar'

// Pages (one file per navigation item)
import Overview           from './pages/Overview'
import LifeExpectancy     from './pages/LifeExpectancy'
import GenderGap          from './pages/GenderGap'
import RegionalComparison from './pages/RegionalComparison'
import MLAnalysis         from './pages/MLAnalysis'
import DiseaseBurden      from './pages/DiseaseBurden'
import AIPlanning         from './pages/AIPlanning'
import Recommendations    from './pages/Recommendations'

export default function App() {
  return (
    <div className="flex h-screen overflow-hidden bg-surface">
      {/* ── Left sidebar ── */}
      <Sidebar />

      {/* ── Right: top-bar + scrollable page content ── */}
      <div className="flex flex-col flex-1 overflow-hidden">
        <TopBar />
        <main className="flex-1 overflow-y-auto p-6 bg-slate-50">
          <Routes>
            <Route path="/"                   element={<Navigate to="/overview" replace />} />
            <Route path="/overview"           element={<Overview />} />
            <Route path="/life-expectancy"    element={<LifeExpectancy />} />
            <Route path="/gender-gap"         element={<GenderGap />} />
            <Route path="/regional"           element={<RegionalComparison />} />
            <Route path="/regional-comparison" element={<Navigate to="/regional" replace />} />
            <Route path="/ml-analysis"        element={<MLAnalysis />} />
            <Route path="/disease-burden"     element={<DiseaseBurden />} />
            <Route path="/ai-planning"        element={<AIPlanning />} />
            <Route path="/recommendations"    element={<Recommendations />} />
            <Route path="/reports"            element={<Navigate to="/recommendations" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}
