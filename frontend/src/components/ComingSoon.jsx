// src/components/ComingSoon.jsx
// Placeholder shown for pages not yet implemented.

import React from 'react'

/**
 * Props:
 *   phase – string – Which phase will implement this page (e.g. "Phase 2")
 *   features – string[] – Bullet list of what will be built
 */
export default function ComingSoon({ phase = 'Phase 2', features = [] }) {
  return (
    <div className="card flex flex-col items-center text-center py-16 max-w-lg mx-auto">
      {/* Clock icon */}
      <div className="w-14 h-14 rounded-full bg-blue-50 flex items-center justify-center mb-4">
        <svg className="w-7 h-7 text-primary" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>

      <h3 className="text-lg font-semibold text-text-primary">Coming in {phase}</h3>
      <p className="text-sm text-text-secondary mt-2 mb-5">
        This module is planned and will be implemented in the next phase of development.
      </p>

      {features.length > 0 && (
        <ul className="text-left space-y-2 w-full">
          {features.map((f) => (
            <li key={f} className="flex items-start gap-2 text-sm text-text-secondary">
              <svg className="w-4 h-4 mt-0.5 flex-shrink-0 text-primary" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {f}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
