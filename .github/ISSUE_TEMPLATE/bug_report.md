---
name: Bug report
about: Report a reproducible issue in execution or enforcement
title: "[BUG] "
labels: bug

---

## What happened
Describe the issue clearly.

## Expected behavior
What should have happened?

## Steps to reproduce
1. exact command / script run
2. input used
3. observed output / error

   
## Minimal code snippet
```python
# paste minimal reproducible example

```
## Note:


`run_task` must return:    
```text
{
"output": Any,
"usage": {
"input_tokens": int,
"output_tokens": int
 }
}
```
Missing or invalid `usage` will cause execution to fail.

---

## Model / setup
- model:
- provider:
- python version:
- OS:

---

## Additional context

Logs, errors, screenshots if relevant.
