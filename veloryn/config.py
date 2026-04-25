MODEL_PRICING = {
    "gpt-4o": {
        "input": 0.0000025,  # $2.5 / 1M
        "output": 0.00001    # $10 / 1M
    },
    "gpt-4o-mini": {
        "input": 0.00000015,
        "output": 0.0000006
    },
    "claude-sonnet-4-6": {
        "input": 0.000003,
        "output": 0.000015
    },
    "claude-haiku-4-5-20251001": {
        "input": 0.000001,
        "output": 0.000005
    }
}

DEFAULT_OUTPUT_TOKENS = 300
