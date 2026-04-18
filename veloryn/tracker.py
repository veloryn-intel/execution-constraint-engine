import math
from .storage import get_task, save_task


def initialize_task(task_id, limit):
    # Validate limit parameter
    if limit is not None:
        if (
            not isinstance(limit, (int, float))
            or limit < 0
            or math.isnan(limit)
            or math.isinf(limit)
        ):
            raise ValueError("Invalid budget limit")

    state = get_task(task_id)
    if state is None:
        state = {
            "task_id": task_id,
            "steps": [],
            "current_cost": 0.0,
            "step_count": 0,
            "limit": limit,
            "observed_patterns": [],
            "blocked": False,
            "primary_reason": None,
            "last_estimated_cost": None,
            "summary_logged": False,
            "recommendation_level": 0,
        }
    else:
        state["limit"] = limit
        state.setdefault("observed_patterns", [])
        state.setdefault("blocked", False)
        state.setdefault("primary_reason", None)
        state.setdefault("last_estimated_cost", None)
        state.setdefault("summary_logged", False)
        state.setdefault("recommendation_level", 0)
    return save_task(task_id, state)


def get_tracker_state(task_id):
    state = get_task(task_id)
    if state is None:
        raise ValueError(f"Unknown task_id: {task_id}")
    return state


def add_step(task_id, step_input, step_output, estimated_cost, actual_cost):
    state = get_tracker_state(task_id)
    state["steps"].append(
        {
            "input": step_input,
            "output": step_output,
            "estimated_cost": estimated_cost,
            "actual_cost": actual_cost,
        }
    )
    state["current_cost"] += actual_cost
    state["step_count"] += 1
    state["last_estimated_cost"] = estimated_cost
    return save_task(task_id, state)


def add_patterns(task_id, patterns):
    if not patterns:
        return get_tracker_state(task_id)

    state = get_tracker_state(task_id)
    for pattern in patterns:
        if pattern not in state["observed_patterns"]:
            state["observed_patterns"].append(pattern)
    return save_task(task_id, state)


def mark_blocked(task_id, primary_reason, patterns=None, estimated_cost=None):
    state = get_tracker_state(task_id)
    state["blocked"] = True
    state["primary_reason"] = primary_reason
    state["last_estimated_cost"] = estimated_cost
    for pattern in patterns or []:
        if pattern not in state["observed_patterns"]:
            state["observed_patterns"].append(pattern)
    return save_task(task_id, state)


def mark_summary_logged(task_id):
    state = get_tracker_state(task_id)
    state["summary_logged"] = True
    return save_task(task_id, state)


def set_recommendation_level(task_id, level):
    state = get_tracker_state(task_id)
    state["recommendation_level"] = level
    return save_task(task_id, state)
