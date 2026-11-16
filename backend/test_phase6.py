"""
test_phase6.py
--------------
Verification test suite for Phase 6: AI Planning Implementation (HTN & STRIPS).
Tests:
  1. HTN Planner: Compound goals decompose into different task plans.
  2. STRIPS Engine: Preconditions, add effects, delete effects, and applicability checks.
  3. Frame Problem Resolution: Untouched predicates persist without modification.
  4. Real Plan Execution: Connected to Dataset S9 analytics and ML functions.
  5. Error Handling: Inapplicable actions are prevented from executing.
"""

import sys
import os
import io

# Ensure UTF-8 output encoding on Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(__file__))

from planning.strips import StripsAction, WorldState
from planning.htn import HtnPlanner, PRIMITIVE_ACTIONS, COMPOUND_GOALS
from planning.executor import PlanExecutor

SEP = "=" * 70

def section(title):
    print(f"\n{SEP}\n  {title}\n{SEP}")

def test_phase6():
    planner = HtnPlanner()
    executor = PlanExecutor()

    # 1. Supported Goals Inspection
    section("1. HTN Compound Goals Registry")
    goals = planner.get_supported_goals()
    print(f"Total supported compound goals: {len(goals)}")
    for g in goals:
        print(f"  • {g['goal_id']:<28}: {g['title']} ({g['task_count']} steps)")
        print(f"    Tasks: {' -> '.join(g['tasks'])}")

    assert len(goals) == 5, "Should support 5 compound analytical goals"

    # 2. Verify Different Goals Produce Different Plans
    section("2. Plan Differentiation Verification")
    plans = {}
    for g in goals:
        plan = planner.decompose(g["goal_id"])
        task_seq = tuple(step["action"] for step in plan["plan"])
        plans[g["goal_id"]] = task_seq
        print(f"  {g['goal_id']}: {len(task_seq)} tasks -> {list(task_seq)}")

    # Verify that different goals do NOT produce identical sequences
    unique_plans = set(plans.values())
    print(f"\nUnique plan sequences generated: {len(unique_plans)} out of {len(plans)}")
    assert len(unique_plans) == len(plans), "Every compound goal must decompose into a unique task plan!"
    print("  ✓ Proven: Planner does NOT use a single hardcoded sequence. Different goals yield different plans.")

    # 3. STRIPS Engine & Frame Problem Test
    section("3. STRIPS State Transition & Frame Problem Test")
    state = WorldState(initial_predicates={"DATASET_AVAILABLE", "BACKGROUND_NOTE_PRESENT"})
    print("Initial State:", state.predicates)

    load_action = PRIMITIVE_ACTIONS["LOAD_DATASET"]
    assert load_action.is_applicable(state.predicates), "LOAD_DATASET should be applicable initially"
    new_state = state.transition(load_action, step_num=1)
    print("State after LOAD_DATASET:", new_state)

    # Verify Frame Problem: BACKGROUND_NOTE_PRESENT was not mentioned in delete_effects, so it MUST persist
    assert "BACKGROUND_NOTE_PRESENT" in new_state, "Frame Problem violation! Untouched fact disappeared."
    assert "DATA_LOADED" in new_state, "Add effect not present!"
    print("  ✓ Frame Problem verified: Untouched facts persist unchanged across state transitions.")

    # 4. Inapplicable Action Precondition Check
    section("4. Precondition Protection Test")
    clean_state = {"DATASET_AVAILABLE"} # DATA_LOADED is missing
    clean_action = PRIMITIVE_ACTIONS["CLEAN_DATA"]
    assert not clean_action.is_applicable(clean_state), "CLEAN_DATA should NOT be applicable without DATA_LOADED"
    try:
        clean_action.apply(clean_state)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"  ✓ Precondition guard active: Action correctly rejected -> {e}")

    # 5. Full Real Plan Execution — ANALYZE_HEALTH_INEQUALITY
    section("5. Real Plan Execution: ANALYZE_HEALTH_INEQUALITY")
    exec_res1 = executor.execute_goal("ANALYZE_HEALTH_INEQUALITY")
    print(f"Goal: {exec_res1['goal_title']} (Status: {exec_res1['status']})")
    print(f"Execution time: {exec_res1['execution_time_ms']} ms")
    print("Execution steps trace:")
    for st in exec_res1["execution_steps"]:
        print(f"  Step {st['step']}: {st['action']:<25} [{st['duration_ms']} ms] -> State size: {len(st['state_after'])}")
        print(f"    Summary: {st['summary']}")

    print("\nFinal State Predicates:", exec_res1["final_state"])
    assert "REPORT_GENERATED" in exec_res1["final_state"]
    assert "CLUSTERS_GENERATED" in exec_res1["final_state"]
    print("  ✓ Plan executed successfully with live data and ML pipeline!")

    # 6. Full Real Plan Execution — COMPARE_REGIONAL_HLE
    section("6. Real Plan Execution: COMPARE_REGIONAL_HLE")
    exec_res2 = executor.execute_goal("COMPARE_REGIONAL_HLE")
    print(f"Goal: {exec_res2['goal_title']} (Status: {exec_res2['status']})")
    print(f"Total steps: {exec_res2['total_steps']}")
    assert "REGIONAL_COMPARISON_COMPLETED" in exec_res2["final_state"]
    assert "CLUSTERS_GENERATED" not in exec_res2["final_state"], "Clustering should not run for regional comparison"
    print("  ✓ Distinct execution confirmed: Regional plan only executes regional subtasks.")

    # 7. Final Report Synthesis
    section("7. Generated Intelligence Brief")
    rep = exec_res1["report"]
    print(f"Title: {rep['title']}")
    print(f"Executive Summary: {rep['executive_summary']}")
    print("Key Synthesized Findings:")
    for f in rep["key_findings"]:
        print(f"  • {f}")

    print(f"\n{SEP}\n  ALL PHASE 6 AI PLANNING TESTS PASSED!\n{SEP}")

if __name__ == "__main__":
    test_phase6()
