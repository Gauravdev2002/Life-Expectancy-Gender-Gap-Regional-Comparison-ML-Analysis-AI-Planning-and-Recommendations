"""
planning/htn.py
---------------
Hierarchical Task Network (HTN) Planner for health intelligence workflows.

HTN Principles:
  1. Compound Tasks: High-level analytical goals submitted by the user.
  2. Task Decomposition Methods: Rules that break down compound tasks into ordered subtasks.
  3. Primitive Tasks: Executable STRIPS actions with verified preconditions and effects.
  4. Goal-Driven Differentiation: Distinct compound goals produce distinct, tailored plans.
"""

from typing import Any, Dict, List, Set
from planning.strips import StripsAction

# ── STRIPS Primitive Action Registry ──────────────────────────────────────────

PRIMITIVE_ACTIONS: Dict[str, StripsAction] = {
    "LOAD_DATASET": StripsAction(
        name="LOAD_DATASET",
        description="Load raw GBD Dataset S9 into pipeline memory.",
        preconditions={"DATASET_AVAILABLE"},
        add_effects={"DATA_LOADED"},
        delete_effects=set(),
    ),
    "CLEAN_DATA": StripsAction(
        name="CLEAN_DATA",
        description="Filter headers, normalize data types, handle missing values, and flag macro aggregates.",
        preconditions={"DATA_LOADED"},
        add_effects={"DATA_CLEANED"},
        delete_effects=set(),
    ),
    "ANALYZE_HLE": StripsAction(
        name="ANALYZE_HLE",
        description="Compute Healthy Life Expectancy trends and trajectories across 1990, 2010, 2020, and 2023.",
        preconditions={"DATA_CLEANED"},
        add_effects={"HLE_ANALYSIS_COMPLETED"},
        delete_effects=set(),
    ),
    "COMPARE_REGIONS": StripsAction(
        name="COMPARE_REGIONS",
        description="Evaluate socio-demographic index (SDI) gradient and GBD continental super-region disparities.",
        preconditions={"DATA_CLEANED"},
        add_effects={"REGIONAL_COMPARISON_COMPLETED"},
        delete_effects=set(),
    ),
    "COMPUTE_GENDER_DIFFERENTIALS": StripsAction(
        name="COMPUTE_GENDER_DIFFERENTIALS",
        description="Calculate Gender Gap = Female HLE - Male HLE across all reporting locations.",
        preconditions={"DATA_CLEANED"},
        add_effects={"GENDER_GAP_COMPUTED"},
        delete_effects=set(),
    ),
    "RANK_LOCATIONS": StripsAction(
        name="RANK_LOCATIONS",
        description="Rank locations by Healthy Life Expectancy and isolate extremes.",
        preconditions={"DATA_CLEANED"},
        add_effects={"LOCATIONS_RANKED"},
        delete_effects=set(),
    ),
    "IDENTIFY_VULNERABILITIES": StripsAction(
        name="IDENTIFY_VULNERABILITIES",
        description="Detect regions experiencing critical HLE decline or severe inequality stagnation.",
        preconditions={"LOCATIONS_RANKED"},
        add_effects={"VULNERABILITIES_IDENTIFIED"},
        delete_effects=set(),
    ),
    "RUN_CLUSTERING": StripsAction(
        name="RUN_CLUSTERING",
        description="Execute StandardScaler, K-Means clustering, and 2D PCA dimensionality reduction.",
        preconditions={"DATA_CLEANED"},
        add_effects={"CLUSTERS_GENERATED"},
        delete_effects=set(),
    ),
    "GENERATE_INSIGHTS": StripsAction(
        name="GENERATE_INSIGHTS",
        description="Synthesize quantitative findings and health system disparity patterns.",
        preconditions={"DATA_CLEANED"}, # At execution time, specific analytics are checked
        add_effects={"INSIGHTS_SYNTHESIZED"},
        delete_effects=set(),
    ),
    "GENERATE_REPORT": StripsAction(
        name="GENERATE_REPORT",
        description="Compile structured analytical brief with evidence-backed indicators.",
        preconditions={"DATA_CLEANED"},
        add_effects={"REPORT_GENERATED"},
        delete_effects=set(),
    ),
}


# ── HTN Compound Task Methods (Decompositions) ────────────────────────────────

COMPOUND_GOALS: Dict[str, Dict[str, Any]] = {
    "ANALYZE_HEALTH_INEQUALITY": {
        "title": "Analyze Health Inequality",
        "category": "Inequality & Clustering",
        "description": "Decomposes the goal of discovering global health disparities through HLE analysis and K-Means clustering.",
        "primitive_tasks": [
            "LOAD_DATASET",
            "CLEAN_DATA",
            "ANALYZE_HLE",
            "RUN_CLUSTERING",
            "GENERATE_INSIGHTS",
            "GENERATE_REPORT",
        ],
        "expected_effects": {"REPORT_GENERATED", "CLUSTERS_GENERATED", "HLE_ANALYSIS_COMPLETED"},
    },
    "COMPARE_REGIONAL_HLE": {
        "title": "Compare Regional HLE",
        "category": "Regional Analytics",
        "description": "Decomposes the goal of benchmarking health trajectories across SDI quintiles and GBD super-regions.",
        "primitive_tasks": [
            "LOAD_DATASET",
            "CLEAN_DATA",
            "COMPARE_REGIONS",
            "GENERATE_INSIGHTS",
            "GENERATE_REPORT",
        ],
        "expected_effects": {"REPORT_GENERATED", "REGIONAL_COMPARISON_COMPLETED"},
    },
    "ANALYZE_GENDER_GAP": {
        "title": "Analyze Gender Gap",
        "category": "Demographic Analytics",
        "description": "Decomposes the goal of analyzing sex-specific life expectancy differentials and gap dynamics.",
        "primitive_tasks": [
            "LOAD_DATASET",
            "CLEAN_DATA",
            "COMPUTE_GENDER_DIFFERENTIALS",
            "GENERATE_INSIGHTS",
            "GENERATE_REPORT",
        ],
        "expected_effects": {"REPORT_GENERATED", "GENDER_GAP_COMPUTED"},
    },
    "IDENTIFY_LOW_HLE_LOCATIONS": {
        "title": "Identify Low HLE Locations",
        "category": "Vulnerability Assessment",
        "description": "Decomposes the goal of ranking lowest-performing health territories and identifying acute vulnerability factors.",
        "primitive_tasks": [
            "LOAD_DATASET",
            "CLEAN_DATA",
            "RANK_LOCATIONS",
            "IDENTIFY_VULNERABILITIES",
            "GENERATE_REPORT",
        ],
        "expected_effects": {"REPORT_GENERATED", "VULNERABILITIES_IDENTIFIED"},
    },
    "GENERATE_HEALTH_REPORT": {
        "title": "Generate Comprehensive Health Report",
        "category": "Executive Intelligence",
        "description": "Decomposes a full multi-dimensional executive intelligence pipeline synthesizing trends, regions, gender gaps, and ML clusters.",
        "primitive_tasks": [
            "LOAD_DATASET",
            "CLEAN_DATA",
            "ANALYZE_HLE",
            "COMPARE_REGIONS",
            "COMPUTE_GENDER_DIFFERENTIALS",
            "RUN_CLUSTERING",
            "GENERATE_INSIGHTS",
            "GENERATE_REPORT",
        ],
        "expected_effects": {
            "REPORT_GENERATED",
            "HLE_ANALYSIS_COMPLETED",
            "REGIONAL_COMPARISON_COMPLETED",
            "GENDER_GAP_COMPUTED",
            "CLUSTERS_GENERATED",
        },
    },
}


class HtnPlanner:
    """Hierarchical Task Network planner generating verified STRIPS action plans."""

    def __init__(self):
        self.compound_goals = COMPOUND_GOALS
        self.primitive_actions = PRIMITIVE_ACTIONS

    def get_supported_goals(self) -> List[Dict[str, Any]]:
        """Returns metadata for all available compound goals."""
        results = []
        for goal_id, g in self.compound_goals.items():
            results.append({
                "goal_id": goal_id,
                "title": g["title"],
                "category": g["category"],
                "description": g["description"],
                "task_count": len(g["primitive_tasks"]),
                "tasks": g["primitive_tasks"],
            })
        return results

    def decompose(self, goal_id: str) -> Dict[str, Any]:
        """
        Decomposes a compound goal into an ordered sequence of STRIPS actions.
        Validates precondition chaining from initial state {"DATASET_AVAILABLE"}.
        """
        goal_id_clean = goal_id.strip().upper()
        if goal_id_clean not in self.compound_goals:
            valid_keys = list(self.compound_goals.keys())
            raise ValueError(f"Unknown goal '{goal_id}'. Valid compound goals: {valid_keys}")

        goal_spec = self.compound_goals[goal_id_clean]
        task_names: List[str] = goal_spec["primitive_tasks"]

        # Validate and build action plan with STRIPS specifications
        actions_plan: List[Dict[str, Any]] = []
        simulated_state: Set[str] = {"DATASET_AVAILABLE"}

        for idx, task_name in enumerate(task_names, start=1):
            if task_name not in self.primitive_actions:
                raise ValueError(f"Primitive task '{task_name}' is not in STRIPS registry.")

            action = self.primitive_actions[task_name]

            # Validate applicability under simulated STRIPS state
            if not action.is_applicable(simulated_state):
                missing = action.preconditions - simulated_state
                raise ValueError(
                    f"Plan generation failed at step {idx} ({task_name}). "
                    f"Preconditions not satisfied: {missing}"
                )

            # Advance simulated state (Frame Problem compliant)
            simulated_state = action.apply(simulated_state)

            actions_plan.append({
                "step": idx,
                "action": action.name,
                "description": action.description,
                "preconditions": sorted(list(action.preconditions)),
                "add_effects": sorted(list(action.add_effects)),
                "delete_effects": sorted(list(action.delete_effects)),
                "expected_state_after": sorted(list(simulated_state)),
            })

        return {
            "goal_id": goal_id_clean,
            "title": goal_spec["title"],
            "description": goal_spec["description"],
            "total_steps": len(actions_plan),
            "initial_state": ["DATASET_AVAILABLE"],
            "final_expected_state": sorted(list(simulated_state)),
            "plan": actions_plan,
        }
