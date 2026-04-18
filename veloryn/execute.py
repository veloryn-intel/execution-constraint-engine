from .guard import check
from .tracker import get_tracker_state, initialize_task
from .config import MODEL_PRICING


_DEFAULT_MODEL = "gpt-4o"
_UNSUPPORTED_MODEL_WARNED: set[str] = set()


def execute(
    *,
    task_id: str,
    run_task,
    input_data=None,
    model: str = None,
    cost_model=None,
    max_cost: float = None,
):
    # ---------------- VALIDATION ----------------

    if not task_id:
        raise ValueError("task_id is required")

    if run_task is None:
        raise ValueError("run_task is required")

    # ---------------- AUTO INIT ----------------

    try:
        state = get_tracker_state(task_id)
    except ValueError:
        initialize_task(task_id, limit=max_cost)
        state = get_tracker_state(task_id)

   
    # ---------------- MODEL RESOLUTION ----------------

    resolved_cost_model = cost_model if cost_model is not None else model

    # fallback if model missing or unsupported
    if not isinstance(resolved_cost_model, dict):
        if resolved_cost_model not in MODEL_PRICING:
            if task_id not in _UNSUPPORTED_MODEL_WARNED:
                print(
                    "[WARN] MODEL_UNSUPPORTED\n"
                    f"model={resolved_cost_model}\n"
                    "fallback=gpt-4o\n"
                    "note=estimates_may_deviate"
                )
                _UNSUPPORTED_MODEL_WARNED.add(task_id)

            resolved_cost_model = _DEFAULT_MODEL

    # ---------------- PRE CHECK ----------------

    pre = check(
        phase="pre",
        task_id=task_id,
        input_text=input_data,
        cost_model=resolved_cost_model,
        max_cost=max_cost,
    )

    if pre["status"] == "BLOCKED":
        raise RuntimeError("Execution blocked by cost enforcement")

    # ---------------- EXECUTION ----------------

    response = run_task()

    if not isinstance(response, dict):
        raise RuntimeError("run_task must return a dict with 'output' and 'usage'")

    if "usage" not in response:
        raise RuntimeError("run_task must return 'usage' for cost tracking")

    usage = response["usage"]
    output = response.get("output")

    if not isinstance(usage, dict):
        raise RuntimeError("'usage' must be a dict")

    if "input_tokens" not in usage or "output_tokens" not in usage:
        raise RuntimeError(
            "'usage' must contain 'input_tokens' and 'output_tokens'"
        )

    # ---------------- POST CHECK ----------------

    check(
        phase="post",
        task_id=task_id,
        input_text=input_data,
        response_text=output,
        tokens=usage,
        cost_model=resolved_cost_model,
        max_cost=max_cost,
    )

    # ---------------- RETURN ----------------

    return response