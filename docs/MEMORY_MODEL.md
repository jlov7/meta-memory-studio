# Memory model (conceptual)

## Why “memory of memory”
Traditional agent memory focuses on storage and retrieval.
MetaMemory Studio focuses on:
- **write-path governance**: what becomes persistent vs transient
- **retrieval governance**: which memories are eligible, diverse, non-redundant
- **credit assignment**: did a memory help or hurt?

## Memory types
- In-context: ephemeral, high-fidelity, expensive at scale
- Vector retrieval: persistent, fuzzy, can be redundant
- Episodic: structured logs of actions/outcomes (auditable)
- Parametric: baked into weights (fast, expensive to update)

## Our approach
- Raw trace is immutable truth.
- Episodic tables provide queryable structure.
- Experience Bank stores reusable “cases”.
- Meta-Guideline Bank stores reusable “how to use cases”.
- Evolution updates weights and encourages selective forgetting.

