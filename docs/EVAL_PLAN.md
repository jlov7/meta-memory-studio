# Evaluation plan

## What we measure

1) Retrieval quality
- Are retrieved memories relevant?
- Do we avoid redundancy?

2) Memory contribution
- Did memory improve score vs baseline?

3) Test-time learning / evolution
- Do weights converge toward helpful memories?
- Do harmful memories decay?

4) Selective forgetting
- Are stale memories removed or deprioritized without breaking performance?

## How we measure (MVP)

- Use the demo trace and a curated set of prompts in `examples/demo_prompts.md`.
- Implement a deterministic scoring harness:
  - exact match / regex checks for constrained outputs
  - simple rubric for tool arguments
- Optional: LLM judge (feature flag).

## Benchmarks to integrate later (stretch)
- MemoryAgentBench (multi-turn memory competencies)
- Mem2ActBench (memory-grounded tool parameterization)

## Required automated tests
- Trace import parse correctness
- Hash chain verification
- Memory weight update rule determinism
- Redaction pipeline does not leak raw payloads in “public export”

