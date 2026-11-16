// src/pages/AIPlanning.jsx
// Phase 6: AI Planning Implementation using HTN and STRIPS
// Powered by real backend HTN decomposition, STRIPS state transitions, and S9 execution.

import React, { useState, useEffect } from 'react'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import {
  fetchPlanningGoals,
  fetchPlanningActions,
  fetchGeneratedPlan,
  executePlanningGoal
} from '../services/api'

export default function AIPlanning() {
  // ── State ──────────────────────────────────────────────────────────────────
  const [goals, setGoals] = useState([])
  const [selectedGoalId, setSelectedGoalId] = useState('ANALYZE_HEALTH_INEQUALITY')
  const [activePlan, setActivePlan] = useState(null)
  const [planLoading, setPlanLoading] = useState(true)

  // Execution state
  const [isExecuting, setIsExecuting] = useState(false)
  const [executionResult, setExecutionResult] = useState(null)
  const [activeStepTab, setActiveStepTab] = useState(null)

  // STRIPS Action library modal / inspect
  const [actionsLibrary, setActionsLibrary] = useState([])
  const [selectedActionModal, setSelectedActionModal] = useState(null)

  // ── Load Goals & Actions on Mount ──────────────────────────────────────────
  useEffect(() => {
    fetchPlanningGoals()
      .then(res => {
        setGoals(res.goals || [])
        if (res.goals?.length > 0) {
          setSelectedGoalId(res.goals[0].goal_id)
        }
      })
      .catch(err => console.error('Error fetching planning goals:', err))

    fetchPlanningActions()
      .then(res => setActionsLibrary(res.actions || []))
      .catch(err => console.error('Error fetching actions library:', err))
  }, [])

  // ── Decompose Plan when Goal Changes ───────────────────────────────────────
  useEffect(() => {
    if (!selectedGoalId) return
    setPlanLoading(true)
    setExecutionResult(null)
    setActiveStepTab(null)

    fetchGeneratedPlan(selectedGoalId)
      .then(plan => {
        setActivePlan(plan)
        setPlanLoading(false)
        if (plan?.plan?.length > 0) {
          setActiveStepTab(plan.plan[0])
        }
      })
      .catch(err => {
        console.error('Error generating plan:', err)
        setPlanLoading(false)
      })
  }, [selectedGoalId])

  // ── Execute Plan ───────────────────────────────────────────────────────────
  const handleExecute = async () => {
    if (!selectedGoalId || isExecuting) return
    setIsExecuting(true)
    setExecutionResult(null)

    try {
      const res = await executePlanningGoal(selectedGoalId)
      setExecutionResult(res)
    } catch (err) {
      console.error('Execution error:', err)
      alert(`Execution failed: ${err.message}`)
    } finally {
      setIsExecuting(false)
    }
  }

  const selectedGoalMeta = goals.find(g => g.goal_id === selectedGoalId)

  return (
    <div className="space-y-6">
      <PageHeader
        title="AI Planning Engine (HTN & STRIPS)"
        subtitle="Automated analytical task decomposition and state-based workflow execution over GBD Dataset S9."
        badge="Phase 6 Live"
      />

      {/* ── Goal Selector: Compound Tasks ─────────────────────────────────── */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-text-primary">
            Select High-Level Analytical Goal (HTN Compound Task)
          </h3>
          <span className="text-xs text-text-muted font-medium">5 Distinct Workflows</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {goals.map((g) => {
            const isSelected = g.goal_id === selectedGoalId
            return (
              <div
                key={g.goal_id}
                onClick={() => setSelectedGoalId(g.goal_id)}
                className={`card p-3.5 cursor-pointer transition-all border text-xs flex flex-col justify-between ${
                  isSelected
                    ? 'border-primary ring-2 ring-primary/20 bg-blue-50/40 shadow-sm'
                    : 'border-surface-border hover:border-slate-300 hover:bg-slate-50'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="badge bg-slate-100 text-slate-700 text-[10px] font-bold">
                      {g.category}
                    </span>
                    <span className="text-[10px] text-text-muted font-semibold">
                      {g.task_count} Steps
                    </span>
                  </div>
                  <h4 className="font-bold text-text-primary text-xs leading-snug">{g.title}</h4>
                  <p className="text-[11px] text-text-muted mt-1 leading-tight line-clamp-3">
                    {g.description}
                  </p>
                </div>
                <div className="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between">
                  <span className="text-[10px] font-mono text-primary font-medium">{g.goal_id}</span>
                  {isSelected && (
                    <span className="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* ── Planning Summary KPI Cards ────────────────────────────────────── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          label="Active Goal Target"
          value={selectedGoalMeta?.title ? selectedGoalMeta.title.slice(0, 18) + '...' : 'Health Inequality'}
          sub={`Goal ID: ${selectedGoalId}`}
          color="blue"
        />
        <StatCard
          label="Decomposed Steps"
          value={activePlan ? `${activePlan.total_steps} Tasks` : '—'}
          sub="HTN Method Decomposition"
          color="purple"
        />
        <StatCard
          label="STRIPS State Axioms"
          value={activePlan ? `${activePlan.final_expected_state.length} Predicates` : '—'}
          sub="Frame Problem compliant"
          color="green"
        />
        <StatCard
          label="Execution Status"
          value={isExecuting ? 'Executing...' : executionResult ? 'Goal Achieved' : 'Plan Ready'}
          sub={executionResult ? `Completed in ${executionResult.execution_time_ms} ms` : 'Click Execute below'}
          color={executionResult ? 'green' : isExecuting ? 'amber' : 'blue'}
        />
      </div>

      {/* ── Generated HTN Task Plan & Execution Action Bar ────────────────── */}
      <div className="card space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-surface-border">
          <div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-primary"></span>
              <h3 className="text-sm font-semibold text-text-primary">
                HTN Task Decomposition Plan: {activePlan?.title}
              </h3>
            </div>
            <p className="text-xs text-text-muted mt-0.5">
              Goal decomposed into an ordered total sequence of verified STRIPS actions
            </p>
          </div>

          <button
            onClick={handleExecute}
            disabled={isExecuting || planLoading}
            className={`px-4 py-2 rounded-lg text-xs font-bold text-white shadow-sm flex items-center gap-2 transition-all ${
              isExecuting
                ? 'bg-amber-600 cursor-not-allowed'
                : 'bg-primary hover:bg-primary-dark active:scale-[0.98]'
            }`}
          >
            {isExecuting ? (
              <>
                <svg className="animate-spin h-3.5 w-3.5 text-white" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                </svg>
                Executing Live Pipeline...
              </>
            ) : (
              <>
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Execute Plan Live
              </>
            )}
          </button>
        </div>

        {/* Visual Workflow Steps Pipeline */}
        {planLoading ? (
          <p className="text-xs text-text-muted py-6 text-center">Decomposing compound task...</p>
        ) : (
          <div className="overflow-x-auto pb-2">
            <div className="flex items-center gap-2 min-w-max">
              {activePlan?.plan?.map((step, idx) => {
                const isSelected = activeStepTab?.action === step.action
                const isDone = Boolean(executionResult)
                return (
                  <React.Fragment key={step.action}>
                    <div
                      onClick={() => setActiveStepTab(step)}
                      className={`p-3 rounded-lg border text-xs cursor-pointer transition-all w-48 flex-shrink-0 ${
                        isSelected
                          ? 'bg-blue-50 border-primary ring-1 ring-primary'
                          : 'bg-white border-surface-border hover:bg-slate-50'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-bold text-text-muted text-[10px]">Step {step.step}</span>
                        {isDone ? (
                          <span className="w-3.5 h-3.5 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-[9px] font-bold">
                            ✓
                          </span>
                        ) : (
                          <span className="w-2 h-2 rounded-full bg-slate-300"></span>
                        )}
                      </div>
                      <p className="font-bold text-text-primary text-xs truncate">{step.action}</p>
                      <p className="text-[10px] text-text-muted mt-0.5 line-clamp-2">
                        {step.description}
                      </p>
                    </div>

                    {idx < activePlan.plan.length - 1 && (
                      <svg className="w-4 h-4 text-slate-300 flex-shrink-0" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                      </svg>
                    )}
                  </React.Fragment>
                )
              })}
            </div>
          </div>
        )}
      </div>

      {/* ── Two-Column STRIPS Inspector & State Transition Tracker ─────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* STRIPS Action Inspector */}
        <div className="card space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-surface-border">
            <div>
              <h3 className="text-sm font-semibold text-text-primary">
                STRIPS Action Specification
              </h3>
              <p className="text-xs text-text-muted">
                Preconditions, Add Effects, and Delete Effects for: <span className="font-bold text-primary">{activeStepTab?.action}</span>
              </p>
            </div>
            <span className="badge bg-blue-50 text-primary border border-blue-200 text-[10px]">
              STRIPS Schema
            </span>
          </div>

          {activeStepTab ? (
            <div className="space-y-3 text-xs">
              <p className="text-xs text-text-secondary font-medium">
                {activeStepTab.description}
              </p>

              {/* Preconditions */}
              <div className="p-2.5 rounded-lg bg-amber-50/60 border border-amber-200/70">
                <span className="font-bold text-amber-900 block mb-1 text-[11px] uppercase tracking-wide">
                  Preconditions (Required Truths to Execute):
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {activeStepTab.preconditions.map((p) => (
                    <span key={p} className="px-2 py-0.5 rounded font-mono text-[10px] bg-white border border-amber-300 text-amber-900 font-semibold">
                      {p}
                    </span>
                  ))}
                </div>
              </div>

              {/* Add Effects */}
              <div className="p-2.5 rounded-lg bg-emerald-50/60 border border-emerald-200/70">
                <span className="font-bold text-emerald-900 block mb-1 text-[11px] uppercase tracking-wide">
                  Add Effects (Asserted True Upon Execution):
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {activeStepTab.add_effects.map((p) => (
                    <span key={p} className="px-2 py-0.5 rounded font-mono text-[10px] bg-white border border-emerald-300 text-emerald-900 font-semibold">
                      + {p}
                    </span>
                  ))}
                </div>
              </div>

              {/* Delete Effects */}
              <div className="p-2.5 rounded-lg bg-rose-50/60 border border-rose-200/70">
                <span className="font-bold text-rose-900 block mb-1 text-[11px] uppercase tracking-wide">
                  Delete Effects (Retracted Truths):
                </span>
                {activeStepTab.delete_effects.length > 0 ? (
                  <div className="flex flex-wrap gap-1.5">
                    {activeStepTab.delete_effects.map((p) => (
                      <span key={p} className="px-2 py-0.5 rounded font-mono text-[10px] bg-white border border-rose-300 text-rose-900 font-semibold">
                        - {p}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-[11px] text-text-muted italic">∅ No delete effects (monotonic state expansion)</p>
                )}
              </div>
            </div>
          ) : (
            <p className="text-xs text-text-muted py-8 text-center">Click a plan step above to inspect STRIPS schema.</p>
          )}
        </div>

        {/* Frame Problem & State Evolution Monitor */}
        <div className="card space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-surface-border">
            <div>
              <h3 className="text-sm font-semibold text-text-primary">
                Frame Problem Resolution Monitor
              </h3>
              <p className="text-xs text-text-muted">
                Mathematical State Transition: State<sub>t+1</sub> = (State<sub>t</sub> \ Delete) ∪ Add
              </p>
            </div>
            <span className="badge bg-emerald-50 text-emerald-700 border border-emerald-200 text-[10px]">
              Frame Axiom Verified
            </span>
          </div>

          <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-xs space-y-1.5 leading-relaxed text-text-secondary">
            <p>
              <strong>Frame Problem Guarantee:</strong> Actions modify <em>only</em> the predicates specified in their Add/Delete sets.
              All existing facts in the world state not explicitly revoked remain strictly true and untouched.
            </p>
          </div>

          {/* World State Predicates View */}
          <div className="space-y-1.5 text-xs">
            <span className="font-semibold text-text-primary text-[11px] uppercase tracking-wide">
              {executionResult ? 'Final Achieved World State Predicates:' : 'Expected State after Step ' + (activeStepTab?.step || 1) + ':'}
            </span>
            <div className="flex flex-wrap gap-1.5 p-2.5 rounded-lg border border-surface-border bg-white min-h-[80px]">
              {(executionResult ? executionResult.final_state : activeStepTab?.expected_state_after)?.map((pred) => (
                <span
                  key={pred}
                  className="px-2 py-0.5 rounded font-mono text-[10px] bg-blue-50 border border-blue-200 text-primary font-semibold flex items-center gap-1"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                  {pred}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* ── Real Execution Trace & Generated Intelligence Report ──────────── */}
      {executionResult && (
        <div className="card space-y-4 border-2 border-emerald-500/40 bg-emerald-50/20">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-emerald-200">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-emerald-500 flex items-center justify-center text-white text-[9px] font-bold">
                ✓
              </span>
              <h3 className="text-sm font-bold text-emerald-950">
                Plan Execution Complete: {executionResult.goal_title}
              </h3>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <span className="badge bg-emerald-100 text-emerald-800 border border-emerald-300 font-bold">
                Goal Satisfied in {executionResult.execution_time_ms} ms
              </span>
            </div>
          </div>

          {/* Key Synthesized Findings from Actual Dataset S9 */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold text-text-primary uppercase tracking-wide">
              Evidence-Backed Intelligence Brief (Synthesized from Real Dataset S9):
            </h4>
            <div className="space-y-2">
              {executionResult.report?.key_findings?.map((finding, idx) => (
                <div key={idx} className="flex items-start gap-2.5 p-3 rounded-lg bg-white border border-emerald-100 shadow-sm text-xs">
                  <span className="w-5 h-5 rounded-full bg-emerald-600 text-white font-bold flex items-center justify-center text-[10px] flex-shrink-0 mt-0.5">
                    {idx + 1}
                  </span>
                  <p className="text-text-primary leading-relaxed font-medium">{finding}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Step Execution Log Table */}
          <div className="space-y-2 pt-2">
            <h4 className="text-xs font-bold text-text-primary uppercase tracking-wide">
              Step-by-Step STRIPS Execution Audit:
            </h4>
            <div className="overflow-x-auto border border-surface-border rounded-lg bg-white">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-text-muted uppercase text-[10px] border-b border-surface-border">
                  <tr>
                    <th className="py-2 px-3">Step</th>
                    <th className="py-2 px-3">Action</th>
                    <th className="py-2 px-3">Duration</th>
                    <th className="py-2 px-3">Execution Summary</th>
                    <th className="py-2 px-3">Added Predicate</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-surface-border">
                  {executionResult.execution_steps?.map((step) => (
                    <tr key={step.step} className="hover:bg-slate-50">
                      <td className="py-2 px-3 font-bold text-text-muted">#{step.step}</td>
                      <td className="py-2 px-3 font-semibold text-text-primary">{step.action}</td>
                      <td className="py-2 px-3 font-mono text-[11px] text-text-muted">{step.duration_ms} ms</td>
                      <td className="py-2 px-3 text-text-secondary">{step.summary}</td>
                      <td className="py-2 px-3 font-mono text-[10px] text-emerald-700 font-semibold">
                        {step.added_effects.join(', ')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
