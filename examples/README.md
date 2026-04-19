# Examples

These scripts show how Execution Constraint Engine (ECE) behaves in real multi-step workflows.

Each scenario is provided in two modes:
- without enforcement (unbounded execution)
- with ECE (cost-constrained execution)

## Scenarios

### 1. Basic Enforcement
Single-agent loop improving output across steps.
```bash
python examples/basic_enforcement.py
```
#### Output
![Execution Output](examples/demo/basic-enforcement.png)  

---

### 2. Looping Agent
Self-refining loop.  

- observation mode → shows cost growth without enforcement  
- with ECE → execution stops before cost escalation
    
```bash
python examples/looping_without_ece_observation_mode.py  
```
```bash
python examples/looping_with_ece.py
```
#### Output

![Execution Output](examples/demo/looping-with-ece.png)  

---

### 3. Multi-Agent Workflow

Generator → critic → refiner loop.  

without ECE → agents continue interacting, cost grows  
with ECE → execution stops when constraint is triggered  

Run:
```bash
python examples/multi_agent_without_ece.py
```
```bash
python examples/multi_agent_with_ece.py
```

#### Output
![Without ECE](examples/demo/multi-agent-without-ece.png)

![With ECE](examples/demo/multi-agent-with-ece.png)


### 4. Fallback Behavior

Execution using an unsupported model.

ECE falls back to GPT-4o pricing while continuing execution.

- execution uses actual model (e.g. Claude)
- cost estimation uses fallback pricing
- warning displayed once per task

Run:  
```bash
python examples/fallback_mode.py
```

![Execution Output](examples/demo/fallback_mode.png)


---

## Output Samples

Sample outputs for each scenario are available in:  
examples/demo/

These are captured from real runs of the scripts.

Each image shows:  
- step-by-step cost progression
- enforcement decisions (ALLOW / BLOCK)
- final execution summary

---

## Notes

- All examples use real model calls  
- `usage` must be returned from each step  
- Cost is computed locally from token usage
  
For accurate pricing, pass a custom `cost_model` where needed.
