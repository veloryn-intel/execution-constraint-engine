def _money_step(value: float) -> str:
    return f"${value:.4f}"


def _format_limit(limit):
    if limit in (None, float("inf")):
        return "No budget"
    return _money_step(limit)


def log_step(
    task_id,
    step_number,
    cost_so_far,
    limit,
    next_estimate,
    allowed,
    primary_reason=None,
    context=None,
    recommendation=None,
    emit=True,
):
    if not emit:
        return

    print(f"Step {step_number}")

    if limit not in (None, float("inf")) and cost_so_far > limit:
        print(
            f"Cost: {_money_step(cost_so_far)} / {_format_limit(limit)} (limit exceeded)"
        )
    else:
        print(f"Cost: {_money_step(cost_so_far)} / {_format_limit(limit)}")

    if allowed:
        print("Status: ALLOWED")
    else:
        print("Status: BLOCKED")
        print("Execution stopped: Budget threshold reached")
        if limit not in (None, float("inf")):
            projected_total = cost_so_far + next_estimate
            print(
                f"Projected cost: {_money_step(projected_total)} / {_money_step(limit)}"
            )

    print("")
