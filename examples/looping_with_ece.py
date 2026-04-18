# examples/looping_with_ece.py

from veloryn import execute, print_summary
import anthropic

client = anthropic.Anthropic()

TASK_ID = "claude-loop"
MAX_COST = 0.1

# Custom pricing (claude-sonnet-4-6)
COST_MODEL = {
    "input": 0.000003,
    "output": 0.000015,
}

previous_output = ""

def run_task():
    global previous_output

    prompt = f"""
You are improving a customer support automation system for an e-commerce platform.

Previous version:
{previous_output}

Refine the system with:
- Better handling of edge cases (refund abuse, delayed shipping)
- Improved escalation logic to human agents
- More realistic customer scenarios
- Clear decision flows

Make it more detailed and production-ready.
"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    output = response.content[0].text

    previous_output = output

    return {
        "output": output,
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
            input_data="customer support system refinement",
            model="claude-sonnet-4-6",   
            cost_model=COST_MODEL,       # overrides pricing
            max_cost=MAX_COST,
        )
    except RuntimeError:
        break

print_summary(TASK_ID)