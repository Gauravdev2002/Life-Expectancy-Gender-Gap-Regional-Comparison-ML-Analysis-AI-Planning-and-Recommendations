"""
api/routes/planning.py
----------------------
FastAPI routes exposing the HTN and STRIPS AI Planning services.
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from planning.htn import HtnPlanner, PRIMITIVE_ACTIONS
from planning.executor import PlanExecutor

router = APIRouter(prefix="/planning", tags=["AI Planning"])

planner = HtnPlanner()
executor = PlanExecutor()


class GoalRequest(BaseModel):
    goal_id: str


@router.get("/goals")
async def get_goals():
    """Returns list of supported high-level analytical goals (HTN compound tasks)."""
    try:
        return {"goals": planner.get_supported_goals()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/actions")
async def get_actions():
    """Returns all primitive STRIPS actions with preconditions and add/delete effects."""
    try:
        actions_list = [a.to_dict() for a in PRIMITIVE_ACTIONS.values()]
        return {"actions": actions_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/plan")
async def generate_plan(request: GoalRequest):
    """
    Decomposes a compound goal into an ordered sequence of STRIPS actions.
    Returns simulated world states and verified preconditions without executing.
    """
    try:
        plan = planner.decompose(request.goal_id)
        return plan
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute")
async def execute_plan(request: GoalRequest):
    """
    Executes the full HTN plan for the requested goal.
    Connects to real dataset analytics, executes state transitions,
    respects the Frame Problem, and synthesizes intelligence reports.
    """
    try:
        result = executor.execute_goal(request.goal_id)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
