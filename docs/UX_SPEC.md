# UX Spec — MetaMemory Studio (non-bland)

## North-star UX principle
The product is about **trust** and **control**:
- Trust: “I believe what I’m seeing.”
- Control: “I can change memory policy and watch it evolve.”

## Visual identity (implementation guidance)
- Use a typographic scale with clear hierarchy.
- Prefer dense-but-readable layouts (like modern observability tools).
- Use subtle motion:
  - expand/collapse transitions
  - hover affordances
  - “verified” animations (but minimal).

## Key journeys

### Journey A — First-run onboarding (60 seconds to wow)
1) Landing page:
   - Title: “MetaMemory Studio”
   - Subtitle: “See which memories helped, hurt, and how your agent evolves.”
   - CTA buttons:
     - “Import sample trace”
     - “Upload your trace”
2) User clicks “Import sample trace”
3) Auto-navigate to Demo Workspace → Run Report:
   - Big status pill: “IMPORTED”
   - Highlight: “3 memories created” and “1 weight updated”
4) User clicks “View timeline”
5) Timeline shows the moment memory retrieval happened and the side-by-side compare.

### Journey B — Investigation workflow (power user)
Goal: debug a failure.
1) Select Run
2) Use filters:
   - only errors
   - only tool calls
   - only memory retrieval
3) Open “Contribution” panel:
   - baseline output vs memory-guided output
   - diff viewer
4) Open “Memory lineage”:
   - which episode created which memory
   - when memory was retrieved
   - net utility score

### Journey C — Weekly memory review (governance)
Goal: what should we prune/fix?
1) Open “Memory Health”
2) View:
   - Top helpful memories (high utility, high retrieval)
   - Top harmful memories (negative utility)
   - Stale memories (decayed, not used)
3) Export:
   - “Memory Review Pack” (zip) with:
     - summary markdown
     - charts
     - redacted memory items
     - raw-trace commitments (optional)

## Screens & components

### 1) Workspace selector
- Left rail with Workspaces
- Workspace has:
  - name
  - tags (demo / prod)
  - retention policy indicator

### 2) Runs table
Columns:
- Run ID
- Timestamp
- Outcome (success/fail/unknown)
- Tool count
- Memory retrieval count
- “Memory helped?” (delta)

Row click opens Run Report.

### 3) Run Report (hero view)
Layout:
- Top: VERIFIED/UNVERIFIED (for raw trace integrity)
- Tabs:
  - Overview
  - Timeline
  - Contribution
  - Memory used
  - Raw events

Key widget: **Contribution Compare**
- Two cards:
  - Baseline (no memory)
  - Memory-guided
- A “Delta” ribbon:
  - +X% score / or “Improved” label
- A diff viewer (inline, not full-screen)

### 4) Timeline
Vertical timeline with event types:
- user message
- assistant response
- tool call
- tool result
- memory retrieval
- memory write
- feedback

Each node expands:
- payload
- provenance
- “copy as JSON”
- “link to memory item”

### 5) Memory Library
Grid/list toggle.
Memory card fields:
- Title
- Type: Experience / Guideline / Fact
- Utility score (sparkline)
- Retrieval count
- Last helped date
- Controls:
  - Pin
  - Edit
  - Deprecate
  - Delete (with confirmation)

### 6) Memory item detail
Sections:
- Summary
- Source episodes (clickable)
- Retrieval history
- Weight evolution graph
- Redactions / PII tags
- “Openings” (if you do commitment-based disclosure)

## Empty states (must be designed)
- No workspaces: show import CTA
- No runs: show upload CTA
- No memories: explain why and how they get created
- Error state: show actionable fixes

## Accessibility and ergonomics
- Keyboard shortcuts:
  - `/` open command palette
  - `g r` go runs
  - `g m` go memory
  - `f` focus filters
- High contrast mode optional.

