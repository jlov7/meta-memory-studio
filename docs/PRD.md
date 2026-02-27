# PRD — MetaMemory Studio

## 1. Summary

MetaMemory Studio is a **memory-of-memory** system for LLM agents.

It provides:
1) **Structured episodic memory**: a queryable database of what the agent did (plans, tool calls, errors, outcomes).
2) **Memory of memory** (meta-memory): a learning loop that measures whether retrieved memories helped and updates memory weights & retention accordingly.
3) A polished UI for:
   - investigating failures,
   - reviewing memory health,
   - spotting drift,
   - and exporting governance-ready reports.

## 2. Problem

Enterprise agent deployments often have:
- short-term in-context state,
- vector retrieval over unstructured text,
- little to no **structured episodic memory** of actions and outcomes,
- and no way to tell whether “memory” is helping or making behavior worse.

Without episodic memory + meta-memory:
- agents repeat mistakes,
- retrieval returns stale/duplicative spans,
- tool parameter grounding fails,
- drift goes undetected,
- governance has nothing concrete to audit.

## 3. Goals

### G1 — Make episodic memory first-class
- Ingest traces from multiple agent frameworks.
- Normalize into a stable schema for episodes, steps, tool calls, outcomes, and feedback.

### G2 — Implement meta-memory (memory of memory)
- Track retrieval events: query, candidates, chosen set, scoring/ranking.
- Track downstream contribution: success metrics and “with memory vs baseline” comparison.
- Update memory weights (reinforcement/decay) with safeguards.

### G3 — Provide a world-class UX
- First run: user imports a sample trace and gets “wow” insight in < 60 seconds.
- Power-user: keyboard-driven investigation workflow.

### G4 — Governance-ready
- Immutable raw trace store.
- Mutable derived memory layer with:
  - versioning,
  - retention/TTL,
  - deletion (“forget”),
  - PII tagging/redaction.

## 4. Non-goals (v1)
- Real-time runtime “memory controller” for production agents (v1 focuses on analysis + memory policy evolution; controller API is optional).
- Full ZK proofs (optional extension; commitments supported, proofs later).

## 5. Users & Use-cases

### U1 — Agent platform engineer
- “Why did the agent fail last week?”
- “Which memories were used and were they helpful?”
- “Which tool parameters drifted over time?”

### U2 — Governance / risk reviewer
- “Show me what was logged for this run.”
- “Show retention policy and deletion requests.”
- “Prove raw traces weren’t mutated.”

### U3 — Product owner
- “Is memory improving outcomes or causing regressions?”
- “Where is the ROI? What should we fix next?”

## 6. Success metrics

- Import-to-insight time: < 60 seconds for demo trace.
- At least 3 distinct memory items are created from demo trace.
- At least 1 memory item weight changes due to outcome feedback.
- UI enables answering:
  - “What happened?”
  - “Which memories were used?”
  - “Did memory help?”
  - “What changed over time?”

## 7. Key requirements

### R1 — Trace ingestion
- JSONL upload (drag-and-drop).
- Validate schema; produce human-friendly error messages.
- Store raw events append-only.

### R2 — Episode reconstruction
- Group events into runs/threads/episodes.
- Extract steps, tool calls, errors, outputs.
- Derive “episode summary” and “memory candidates”.

### R3 — Memory banks
- Experience Bank: reusable experiences (structured).
- Meta-Guideline Bank: guidance for compiling experiences into task-specific instructions.

### R4 — Contribution measurement
- Provide baseline vs memory-guided compare:
  - exact match (where possible),
  - judge LLM (optional),
  - or heuristic scoring (day 1).

### R5 — Weight updates + forgetting
- Update rule must be deterministic and logged.
- Decay stale or harmful experiences.
- Soft-deletion and hard-deletion.

### R6 — UI polish
- Not bland. Must look designed.
- Excellent empty states, skeleton loaders, and inline explanations.

## 8. Milestones (overnight build)

MVP (night):
- Trace import
- Episode timeline UI
- Memory card UI
- Contribution compare for one run
- Weight updates visible
- Basic retention / delete memory item
- Tests + e2e smoke

Stretch:
- Hierarchical de-dup retrieval (theme → episode → raw)
- Drift detection dashboard
- Export “Memory Review Pack” (zip) for sharing

