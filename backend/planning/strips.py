"""
planning/strips.py
------------------
Classical STRIPS (Stanford Research Institute Problem Solver) Planning Engine.

Formal Elements:
  1. Predicates: Boolean propositions describing the world state.
  2. WorldState: A set of active predicates.
  3. Action Schema:
     - Name: Unique identifier.
     - Preconditions: Set of predicates required to be TRUE before execution.
     - Add Effects: Set of predicates asserted to be TRUE after execution.
     - Delete Effects: Set of predicates retracted to FALSE after execution.

Frame Problem Resolution:
  In accordance with classical STRIPS semantics:
    State_{t+1} = (State_t \\ Delete_Effects) ∪ Add_Effects
  All predicates not explicitly listed in Delete_Effects persist unchanged.
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Set, Any


@dataclass(frozen=True)
class StripsAction:
    """Representation of an atomic STRIPS action."""
    name: str
    description: str
    preconditions: Set[str]
    add_effects: Set[str]
    delete_effects: Set[str] = field(default_factory=set)

    def is_applicable(self, current_state: Set[str]) -> bool:
        """Action is applicable if and only if all preconditions are satisfied."""
        return self.preconditions.issubset(current_state)

    def apply(self, current_state: Set[str]) -> Set[str]:
        """
        Applies state transition preserving the Frame Axiom:
        Untouched facts remain strictly unchanged.
        """
        if not self.is_applicable(current_state):
            missing = self.preconditions - current_state
            raise ValueError(
                f"Action '{self.name}' cannot be executed. Missing preconditions: {missing}"
            )
        # Frame problem resolution: copy untouched facts, remove deleted, add new
        new_state = (current_state - self.delete_effects) | self.add_effects
        return new_state

    def to_dict(self) -> Dict[str, Any]:
        """Serializes action definition for API and frontend display."""
        return {
            "name": self.name,
            "description": self.description,
            "preconditions": sorted(list(self.preconditions)),
            "add_effects": sorted(list(self.add_effects)),
            "delete_effects": sorted(list(self.delete_effects)),
        }


class WorldState:
    """Manages active truth values and state-based progression."""
    def __init__(self, initial_predicates: Optional[Set[str]] = None):
        self._predicates: Set[str] = set(initial_predicates or ["DATASET_AVAILABLE"])
        self._history: List[Dict[str, Any]] = [
            {
                "step": 0,
                "action": "INITIAL_STATE",
                "state": sorted(list(self._predicates)),
                "added": sorted(list(self._predicates)),
                "deleted": [],
            }
        ]

    @property
    def predicates(self) -> Set[str]:
        return set(self._predicates)

    def has(self, predicate: str) -> bool:
        return predicate in self._predicates

    def transition(self, action: StripsAction, step_num: int) -> Set[str]:
        """Executes action and logs state transition."""
        prior = set(self._predicates)
        self._predicates = action.apply(self._predicates)
        added = sorted(list(action.add_effects))
        deleted = sorted(list(action.delete_effects))

        self._history.append({
            "step": step_num,
            "action": action.name,
            "state": sorted(list(self._predicates)),
            "added": added,
            "deleted": deleted,
            "untouched_count": len(prior - action.delete_effects),
        })
        return self._predicates

    def get_history(self) -> List[Dict[str, Any]]:
        return self._history
