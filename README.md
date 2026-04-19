# Execution Constraint Engine (ECE)

Runtime decision layer for enforcing cost constraints in multi-step LLM execution.

LLM workflows can accumulate cost across steps without a global constraint.
Execution Constraint Engine (ECE) provides a deterministic enforcement decision based on projected cost.

## Install

```bash
pip install veloryn
```



## Beta (v1)

ECE (v1) is a deterministic execution control layer.   
It evaluates execution state between steps and returns a `BLOCK` decision when projected cost exceeds the defined budget.  
ECE does not rely on heuristics, patterns, or learned behavior. 

Current scope: cost-based enforcement.  

Future versions extend enforcement using behavioral signals and execution patterns.


---

## Core Concept

ECE separates execution from control.

| Layer | Responsibility |
|---------|------------------|
| Your system | Executes workflow |
| ECE | Evaluates execution state and returns enforcement decisions |
| Your system | Applies enforcement decisions |



ECE operates between execution steps, evaluating state after each model response and determining whether execution is allowed to continue.

It provides a deterministic boundary for otherwise unbounded execution flows.


---

## Enforcement Model

ECE returns a deterministic decision:

ALLOW → continue execution  
BLOCK → stop execution

Blocking is triggered only when the next step would exceed the defined cost limit.

ECE does not terminate execution directly.
The calling system must enforce the decision.

## What it does

- Tracks execution cost across steps

- Evaluates execution state between steps

- Returns deterministic `ALLOW / BLOCK` decisions

- Limits execution within a defined budget using predictive enforcement (may overshoot by one step).

---


## What it does NOT do

- Does not execute your workflow
- Does not replace your agent framework
- Does not automatically terminate execution
- Does not collect token usage automatically (must be provided by user)
- Does not enforce limits without correct integration

---


## Observation Mode (Recommended Starting Point)

ECE runs in observation mode when no `max_cost` is provided.

If `max_cost` is not provided:
- Execution is never blocked
- Cost is tracked across steps
- No enforcement is applied

Use this mode to understand cost behavior before introducing constraints.


Typical workflow:


1. Run your system with ECE in observation mode

2. Review execution summaries

3. Identify inefficiencies or runaway behavior

4. Introduce budget constraints 

Progression  

Observation → Analysis → Constraint → Enforcement

---

## Cost Model
ECE computes cost locally using token usage and pricing.  

Pre-step → estimated cost (used for enforcement)

Post-step → actual cost (from usage)

### Supported Models
gpt-4o  
gpt-4o-mini  
claude-3-sonnet  
claude-3-haiku  

### Fallback Behavior

If the model is not in the supported pricing list:

- Falls back to GPT-4o pricing  
- Warning is displayed once per task  

```text
[WARN] MODEL_UNSUPPORTED
model=<model_name>
fallback=gpt-4o
note=estimates_may_deviate
```

### Custom Cost Model  

```python
cost_model = {  
    "input": 0.000003,  
    "output": 0.000015 
}

execute(..., cost_model=cost_model)
```
Overrides built-in pricing.

### When to use

Use a custom `cost_model` when:
- your model is not in the supported pricing list
- you are using a provider-specific or newer model
- you need accurate enforcement aligned with actual billing

### Notes

- If not provided, ECE uses predefined pricing (or fallback)
- Incorrect pricing → incorrect enforcement decisions
- ECE does not validate or fetch pricing externally

### Design Principle

ECE enforces execution deterministically over a defined cost function.

It does NOT:
- auto-detect pricing
- fetch provider billing
- assume model behavior

You define the cost model. ECE enforces execution.

---

## Execution Constraints (v1)

- Sequential execution per task_id
- Each step must follow PRE → EXEC → POST

Not supported:

- Parallel execution for same `task_id`
- Concurrent agent branches

---

## Get Started

### 1. Minimal Integration
```python

from veloryn import execute, print_summary
from openai import OpenAI

client = OpenAI()

TASK_ID = "basic-enforcement"
MAX_COST = 0.05


def run_task():

    response = client.responses.create(
        model="gpt-4o",
        input="Analyze this startup idea: AI-powered fitness coach",
        max_output_tokens=300,
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

```

### 2. Execution Flow
ECE evaluates execution around each step:    
PRE  → estimate cost  
EXEC → run function  
POST → compute actual cost  

If the next step is likely to exceed budget → a BLOCK decision is returned.  

### 3. Required Contract

`run_task` must return:
```
{
    "output": Any,
    "usage": {
        "input_tokens": int,
        "output_tokens": int
    }
}
```
Missing or invalid `usage` → execution fails (`RuntimeError`)

ECE does not infer usage.

### 4. Failure Conditions
ECE will stop execution if:
- Budget exceeded
- Usage missing
- Invalid usage format
- PRE/POST contract broken



### 5. Sample Output

```text
Step 3
Cost: $0.0040 / $0.0500
Status: ALLOWED

Step 4
Cost: $0.0116 / $0.0500
Status: ALLOWED

Step 5
Cost: $0.0236 / $0.0500
Status: ALLOWED

Step 6
Cost: $0.0399 / $0.0500
Status: BLOCKED
Execution stopped: Budget threshold reached
Projected cost: $0.0536 / $0.0500

══════════ EXECUTION SUMMARY ══════════

Total cost (actual): $0.04
Steps executed: 5
Status: Blocked (budget threshold reached)

```


### 6. Examples

Run:
```bash
python examples/basic_enforcement.py

```
See:  
- [examples/basic_enforcement.py](examples/basic_enforcement.py)  
- [examples/looping_with_ece.py](examples/looping_with_ece.py)  
- [examples/looping_without_ece_observation_mode.py](examples/looping_without_ece_observation_mode.py)  
- [examples/fallback_mode.py](examples/fallback_mode.py)  
- [examples/multi_agent_with_ece.py](examples/multi_agent_with_ece.py)  
- [examples/multi_agent_without_ece.py](examples/multi_agent_without_ece.py)

---


## Privacy

ECE is local-first:

- No data is sent externally

- No telemetry or remote tracking

- All execution data remains within your environment (logs are written locally to `veloryn_logs.jsonl`)

	
---

## When to Use

Use ECE when execution is not bounded by design:

- Iterative refinement loops

- Multi-agent workflows

- Tool-calling systems

- Cost-sensitive environments


Especially useful for:

- High-frequency execution
- Strict cost constraints
- Debugging agent behavior

## Why not just use model limits?

Model limits apply to individual calls (e.g. max tokens per request).

They do not enforce cumulative cost across multi-step workflows.

ECE tracks total cost across steps and returns a stop decision when the defined budget threshold is reached.

---

## Known Limitations (v1)

- Cost estimation is heuristic  
    Cost estimation is approximate (not tokenizer-accurate)

- Budget enforcement is predictive  
    May overshoot by one step  

- Usage is mandatory  
     Missing usage causes failure  

- Pre/Post contract is strict  
     Missing post-phase breaks tracking  

- Sequential execution only  
     Not safe for concurrent execution  

- Local state only  
     No persistence across processes  

- Fallback pricing drift  
     Unsupported models use GPT-4o baseline  

- Limited cost model coverage  

- No recovery guarantees  

- Behavioral signals are non-enforcing  


---


## Disclaimer

Execution Constraint Engine is a decision and evaluation system.

ECE does not execute workflows.

Enforcement depends on integration.


ECE does not guarantee:

- cost control

- system behavior

- prevention of undesired outcomes


Incorrect or incomplete integration may result in uncontrolled execution.

This is a beta release and should not be relied upon as a sole control mechanism in critical systems without additional safeguards.

Veloryn Intelligence is not responsible for execution outcomes, costs incurred, or system behavior resulting from the use or non-enforcement of decisions produced by this system.

---

## Summary

Execution Constraint Engine evaluates execution state between steps and returns deterministic enforcement decisions that enable bounded execution when correctly integrated.

This version (v1) introduces cost-based constraints as the first enforcement primitive in a broader execution constraint stack.

It aligns with the Agent Accountability Stack (AAS), part of Veloryn Intelligence’s Autonomy Accountability Framework (AAF), which defines execution-layer accountability in autonomous systems.

---


## Roadmap Direction



ECE (v1) introduces cost-based execution constraints.

Future versions will expand enforcement beyond cost into:

- behavior-aware constraints

- adaptive execution control

- multi-dimensional constraints

These capabilities will be introduced incrementally as part of a broader execution constraint stack.

The long-term goal is a runtime control layer for managing execution behavior in model-driven systems.


### Built by Veloryn Intelligence
