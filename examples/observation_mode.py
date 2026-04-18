# examples/observation_mode.py

from veloryn import execute, print_summary
from openai import OpenAI

client = OpenAI()

TASK_ID = "observation-mode"


def run_task():

    response = client.responses.create(
        model="gpt-4o",
        input="Generate 5 marketing ideas for a SaaS product",
        max_output_tokens=250,
    )

    return {
        "output": response.output_text,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        },
    }


for _ in range(8):
    execute(
        task_id=TASK_ID,
        run_task=run_task,
        input_data="Marketing ideation",
        model="gpt-4o",
        max_cost=None,  # observation mode
    )


print_summary(TASK_ID)