# examples/multi_agent_without_ece.py

import os
from openai import OpenAI
from veloryn.cost import actual_cost

client = OpenAI()

MODEL = "gpt-4o"
TASK = "Design an AI infra product for enterprise compliance"

shared_memory = []
total_cost = 0.0

agents = [
    ("Generator", "Generate full system design"),
    ("Critic", "Critique for gaps, risks, scalability"),
    ("Refiner", "Improve with enterprise-grade detail"),
]

for cycle in range(1, 5):
    for name, role in agents:
        context = "\n\n".join(shared_memory[-3:])

        prompt = f"""
TASK: {TASK}

Context:
{context}

ROLE:
{name} - {role}

Be detailed and technical.
"""

        response = client.responses.create(
            model=MODEL,
            input=prompt,
            max_output_tokens=900,
        )

        output = response.output_text
        usage = {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        }

        cost = actual_cost(usage, MODEL)
        total_cost += cost

        shared_memory.append(output)

        print(f"{name} | Cost: {cost:.4f} | Total: {total_cost:.4f}")

print("Final cost:", total_cost)