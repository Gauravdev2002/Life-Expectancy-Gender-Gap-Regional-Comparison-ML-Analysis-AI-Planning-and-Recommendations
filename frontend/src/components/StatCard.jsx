// src/components/StatCard.jsx
// A simple KPI / summary card displayed in a grid on the Overview page.

import React from 'react'

/**
 * Props:
 *   label – string – Metric name
 *   value – string – Formatted metric value
 *   sub   – string – Smaller supporting text below value
 *   color – 'blue' | 'green' | 'purple' | 'amber' (default 'blue')
 */
const colorMap = {
  blue:   'bg-blue-50   text-primary',
  green:  'bg-green-50  text-secondary',
  purple: 'bg-purple-50 text-accent',
  amber:  'bg-amber-50  text-warning',
}

export default function StatCard({ label, value, sub, color = 'blue', icon }) {
  return (
    <div className="card flex gap-4 items-start">
      {icon && (
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${colorMap[color]}`}>
          {icon}
        </div>
      )}
      <div>
        <p className="text-xs font-medium text-text-muted uppercase tracking-wide">{label}</p>
        <p className="text-2xl font-bold text-text-primary mt-0.5">{value}</p>
        {sub && <p className="text-xs text-text-secondary mt-0.5">{sub}</p>}
      </div>
    </div>
  )
}
