# examples/fallback_mode.py

from veloryn import execute, print_summary
import anthropic

client = anthropic.Anthropic()

TASK_ID = "fallback-claude"
MAX_COST = 0.08


def run_task():

    response = client.messages.create(
        model="claude-sonnet-4-6",  # actual execution model
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": "Explain how AI agents are changing software development workflows"
            }
        ],
    )

    output = response.content[0].text

    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }

    return {
        "output": output,
        "usage": usage,
    }


for _ in range(5):
    execute(
        task_id=TASK_ID,
        run_task=run_task,
        input_data="AI agents workflow",
        model="claude-sonnet-4-6",  # NOT in supported list → triggers fallback
        max_cost=MAX_COST,
    )


print_summary(TASK_ID)