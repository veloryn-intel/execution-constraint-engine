from .config import DEFAULT_OUTPUT_TOKENS, MODEL_PRICING


def _get_pricing(model):
    # 1. Custom pricing (user-provided dict)
    if isinstance(model, dict):
        if "input" not in model or "output" not in model:
            raise ValueError("Custom cost_model must contain 'input' and 'output'")
        return model, False

    # 2. Supported models
    if model in MODEL_PRICING:
        return MODEL_PRICING[model], False

    # 3. Fallback to GPT-4o pricing
    fallback_model = "gpt-4o"
    return MODEL_PRICING[fallback_model], True


def _message_text(messages):
    parts = []
    for message in messages:
        content = message.get("content", "")
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    parts.append(item.get("text", ""))
                else:
                    parts.append(str(item))
        else:
            parts.append(str(content))
    return " ".join(parts)


def estimate_cost(messages, model, max_tokens=None):
    pricing, _ = _get_pricing(model)
    text = _message_text(messages)
    input_tokens = max(1, len(text) // 4)
    if max_tokens is None:
        output_tokens = DEFAULT_OUTPUT_TOKENS
    else:
        output_tokens = max_tokens
    return (input_tokens * pricing["input"]) + (output_tokens * pricing["output"])


def actual_cost(usage, model):
    pricing, _ = _get_pricing(model)
    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)
    return (input_tokens * pricing["input"]) + (output_tokens * pricing["output"])