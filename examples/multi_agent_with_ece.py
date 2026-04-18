# examples/multi_agent_with_ece.py

from veloryn import execute, print_summary
from openai import OpenAI

client = OpenAI()

TASK_ID = "multi-agent-ece"
MAX_COST = 0.1

shared_memory = []

agents = [
    ("Generator", "Generate full system design"),
    ("Critic", "Critique for gaps, risks, scalability"),
    ("Refiner", "Improve with enterprise-grade detail"),
]

def run_task(agent_name, role):
    context = "\n\n".join(shared_memory[-3:])

    prompt = f"""
Design an AI infra product for enterprise compliance

Context:
{context}

Role:
{agent_name} - {role}

Be detailed and technical.
"""

    response = client.responses.create(
        model="gpt-4o",
        input=prompt,
        max_output_tokens=900,
    )

    output = response.output_text

    shared_memory.append(output)

    return {
        "output": output,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        },
    }


for cycle in range(10):
    for name, role in agents:
        try:
            execute(
                task_id=TASK_ID,
                run_task=lambda n=name, r=role: run_task(n, r),
                input_data="multi-agent",
                model="gpt-4o",
                max_cost=MAX_COST,
            )
        except RuntimeError:
            break

print_summary(TASK_ID)