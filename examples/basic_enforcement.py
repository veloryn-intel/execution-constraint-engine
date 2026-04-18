# examples/basic_enforcement.py

from veloryn import execute, print_summary
from openai import OpenAI

client = OpenAI()

TASK_ID = "basic-enforcement"
MAX_COST = 0.1


def run_task():

    response = client.responses.create(
        model="gpt-4o",
        input="Analyze this startup idea: AI-powered fitness coach",
        max_output_tokens=800,
    )

    return {
        "output": response.output_text,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        },
    }


while True:
    try:
        execute(
            task_id=TASK_ID,
            run_task=run_task,
            input_data="Startup analysis",
            model="gpt-4o",
            max_cost=MAX_COST,
        )
    except RuntimeError:
        break


print_summary(TASK_ID)