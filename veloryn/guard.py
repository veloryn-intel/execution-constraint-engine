from . import cost, enforcer, logger, rules, tracker
from .logger_local import append_log
from .config import MODEL_PRICING

DEFAULT_MODEL = "gpt-4o"
MIN_COST_THRESHOLD = 0.02

_OBSERVATION_NOTIFIED: set[str] = set()
_DEFAULT_MODEL_NOTIFIED: set[str] = set()
_PENDING_PRECHECKS: dict[str, dict] = {}
_UNSUPPORTED_MODEL_WARNED: set[str] = set()


def _message_text(input_text):
    if input_text is None:
        return ""
    return str(input_text)


def _estimate_messages(input_text):
    return [{"role": "user", "content": _message_text(input_text)}]


def _normalize_usage(input_text, tokens):
    if isinstance(tokens, dict):
        return {
            "input_tokens": int(tokens.get("input_tokens", 0) or 0),
            "output_tokens": int(tokens.get("output_tokens", 0) or 0),
        }

    input_tokens = max(1, len(_message_text(input_text)) // 4) if input_text else 0
    output_tokens = int(tokens or 0)
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }

    # NOTE:
    # Model normalization and warnings are handled in execute().
    # guard assumes cost_model is already resolved.

    # existing logic using cost_model below

def check(
    phase,
    task_id,
    current_cost=None,
    max_cost=None,
    input_text=None,
    response_text=None,
    tokens=None,
    cost_model=None,
):
    # Tracker is the single source of truth
    state = tracker.get_tracker_state(task_id)
    current_cost = state["current_cost"]

    if state.get("blocked"):
        raise RuntimeError(
            f"Task {task_id} is already blocked. No further execution allowed."
        )

    resolved_cost_model = cost_model if cost_model is not None else DEFAULT_MODEL

    if phase == "pre":
        estimated_cost = cost.estimate_cost(
            _estimate_messages(input_text),
            resolved_cost_model,
        )

        pre_rule_flags = rules.evaluate_pre_rules(
            {
                **state,
                "pending_input": _message_text(input_text),
                "pending_estimated_cost": estimated_cost,
            }
        )

        effective_limit = (
            max_cost if max_cost is not None else state.get("limit")
        )

        blocked = (
            False
            if effective_limit is None
            else enforcer.should_block(current_cost, estimated_cost, effective_limit)
        )

        final_action = "BLOCK" if blocked else "ALLOW"
        reason = "Budget threshold reached" if blocked else ""
        risk_level = "HIGH" if blocked else "LOW"

        if task_id in _PENDING_PRECHECKS:
            raise RuntimeError(
                f"Unresolved pre-check exists for task_id={task_id}. post phase was not completed."
            )

        if blocked:
            _PENDING_PRECHECKS.pop(task_id, None)
            tracker.mark_blocked(
                task_id,
                reason,
                pre_rule_flags,
                estimated_cost=estimated_cost,
            )
        else:
            _PENDING_PRECHECKS[task_id] = {
                "estimated_cost": estimated_cost,
                "cost_model": resolved_cost_model,
            }

        logger.log_step(
            task_id=task_id,
            step_number=state["step_count"] + 1,
            cost_so_far=current_cost,
            limit=max_cost if max_cost is not None else float("inf"),
            next_estimate=estimated_cost,
            allowed=not blocked,
        )

        append_log(
            {
                "phase": "pre",
                "task_id": task_id,
                "step_number": state["step_count"] + 1,
                "current_cost": current_cost,
                "estimated_cost": estimated_cost,
                "final_action": final_action,
            }
        )


        return {
            "status": "BLOCKED" if blocked else "ALLOWED",
            "final_action": final_action,
            "risk_level": risk_level,
            "reason": reason,
            "message": f"Status: {'BLOCKED' if blocked else 'ALLOWED'}",
            "estimated_cost": estimated_cost,
        }

    if phase == "post":
        usage = _normalize_usage(input_text, tokens)

        if task_id not in _PENDING_PRECHECKS:
            raise RuntimeError(
                f"No pre-check state found for task_id={task_id}. pre phase must be called before post."
            )

        pending = _PENDING_PRECHECKS.pop(task_id)

        if "cost_model" not in pending:
            raise RuntimeError(
                f"Pre-check state for task_id={task_id} is missing 'cost_model'. State corruption detected."
            )

        resolved_cost_model = pending["cost_model"]

        actual_step_cost = cost.actual_cost(usage, resolved_cost_model)

        if "estimated_cost" not in pending:
            raise RuntimeError(
                f"Pre-check state for task_id={task_id} is missing 'estimated_cost'. State corruption detected."
            )

        estimated_cost = pending["estimated_cost"]

        # POST-PHASE ENFORCEMENT (unchanged)
        effective_limit = max_cost if max_cost is not None else state.get("limit")

        if effective_limit is not None:
            updated_total = state["current_cost"] + actual_step_cost

            if updated_total >= effective_limit:
                tracker.mark_blocked(
                    task_id,
                    "Budget threshold reached",
                    [],
                    estimated_cost=estimated_cost,
                )

        tracker_state = tracker.add_step(
            task_id=task_id,
            step_input=_message_text(input_text),
            step_output=_message_text(response_text),
            estimated_cost=estimated_cost,
            actual_cost=actual_step_cost,
        )

        append_log(
            {
                "phase": "post",
                "task_id": task_id,
                "step_number": tracker_state["step_count"],
                "current_cost": tracker_state["current_cost"],
                "actual_cost": actual_step_cost,
                "final_action": "ALLOW",
            }
        )

        return {
            "final_action": "ALLOW",
            "cost": actual_step_cost,
            "step": tracker_state["step_count"],
        }

    raise ValueError(f"Unsupported phase: {phase}")


def render_summary(task_id):
    state = tracker.get_tracker_state(task_id)

    blocked = state.get("blocked", False)
    steps = state.get("step_count", 0)
    total_cost = round(state.get("current_cost", 0.0), 2)

    if blocked and steps == 0:
        return "\n".join(
            [
                "══════════ EXECUTION SUMMARY ══════════",
                f"Total cost (actual): ${total_cost:.2f}",
                f"Steps executed: {steps}",
                "Status: Blocked before execution",
                "──────────────────────────────────────",
                "",
                "Impact:",
                "- Execution prevented before first step",
                "- Estimated cost exceeded budget",
                "──────────────────────────────────────",
                "· Veloryn Intelligence",
            ]
        )

    if blocked:
        impact = [
            "- Next step would exceed budget threshold",
            "- Execution blocked before exceeding budget",
        ]
        reason = "- Budget threshold reached"
        status = "Blocked (budget threshold reached)"
    else:
        impact = [
            "- Execution completed within defined constraints",
        ]
        reason = "- None"
        status = "Completed"

    lines = [
        "══════════ EXECUTION SUMMARY ══════════",
        f"Total cost (actual): ${total_cost:.2f}",
        f"Steps executed: {steps}",
        f"Status: {status}",
        "──────────────────────────────────────",
        "",
        "Impact:",
        *impact,
        "",
        "──────────────────────────────────────",
        "Reason:",
        reason,
        "──────────────────────────────────────",
        "· Veloryn Intelligence",
    ]

    return "\n".join(lines)


def print_summary(task_id):
    print(render_summary(task_id))
    tracker.mark_summary_logged(task_id)