from difflib import SequenceMatcher

STOP_KEYWORDS = ["final answer", "done", "completed"]


def _similarity(left, right):
    return SequenceMatcher(None, left.lower(), right.lower()).ratio()


def _all_similar(inputs, threshold=0.8):
    if len(inputs) < 3:
        return False
    return (
        _similarity(inputs[0], inputs[1]) > threshold
        and _similarity(inputs[1], inputs[2]) > threshold
        and _similarity(inputs[0], inputs[2]) > threshold
    )


def evaluate_pre_rules(tracker_state):
    flags = []
    steps = tracker_state.get("steps", [])
    pending_input = tracker_state.get("pending_input", "")

    recent_inputs = [step["input"] for step in steps[-2:]]
    if pending_input:
        recent_inputs.append(pending_input)
    if _all_similar(recent_inputs):
        flags.append("Repeated prompt pattern detected")

    searchable_text = " ".join(
        [step["output"] for step in steps] + ([pending_input] if pending_input else [])
    ).lower()
    if tracker_state.get("step_count", 0) > 5 and not any(
        keyword in searchable_text for keyword in STOP_KEYWORDS
    ):
        flags.append("No termination signal after multiple steps")

    return flags


def evaluate_post_rules(tracker_state):
    flags = []
    steps = tracker_state.get("steps", [])

    if len(steps) >= 2:
        previous_cost = steps[-2].get("actual_cost", 0.0)
        current_cost = steps[-1].get("actual_cost", 0.0)
        if (
            previous_cost > 0
            and current_cost > previous_cost
            and ((current_cost - previous_cost) / previous_cost) > 0.3
        ):
            flags.append("Cost increasing rapidly")

    if len(steps) >= 3:
        earlier_output = steps[-3].get("output", "")
        previous_output = steps[-2].get("output", "")
        last_output = steps[-1].get("output", "")

        earlier_length = len(earlier_output)
        previous_length = len(previous_output)
        last_length = len(last_output)

        if earlier_length > 0 and previous_length > 0:
            previous_growth = (previous_length - earlier_length) / earlier_length
            current_growth = (last_length - previous_length) / previous_length
            if previous_growth > 0.2 and current_growth > 0.2:
                flags.append("Output expanding aggressively")

    return flags
