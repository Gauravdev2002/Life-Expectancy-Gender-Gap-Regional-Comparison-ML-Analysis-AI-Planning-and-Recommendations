// src/components/PageHeader.jsx
// Reusable section header used at the top of each page.

import React from 'react'

/**
 * Props:
 *   title   – string  – Page/section title
 *   subtitle – string – Short description shown below the title
 *   badge   – string  – Optional status badge text (e.g. "Phase 2")
 */
export default function PageHeader({ title, subtitle, badge }) {
  return (
    <div className="mb-6">
      <div className="flex items-center gap-3">
        <h2 className="text-xl font-semibold text-text-primary">{title}</h2>
        {badge && (
          <span className="badge bg-warning-light text-warning border border-amber-200">
            {badge}
          </span>
        )}
      </div>
      {subtitle && (
        <p className="mt-1 text-sm text-text-secondary">{subtitle}</p>
      )}
    </div>
  )
}
