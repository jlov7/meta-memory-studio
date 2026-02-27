"""Build Run / Episode / Step / ToolCall rows from normalized events."""

import json
from collections import defaultdict

from app.models.runs import Episode, Run, Step, ToolCall


def build_episodes(
    workspace_id: str,
    events: list[dict],  # type: ignore[type-arg]
    raw_event_ids: list[str],
) -> tuple[list[Run], list[Episode], list[Step], list[ToolCall]]:
    """Group normalized events by run_id and build structured rows."""
    # Track current run contextually — run_id only appears in payload for
    # run_start/run_end events; all other events belong to the current run.
    runs_map: dict[str, list[tuple[dict, str]]] = defaultdict(list)  # type: ignore[type-arg]
    current_run_id = ""
    for event, raw_id in zip(events, raw_event_ids, strict=True):
        event_type = event.get("type", "")
        if event_type == "run_start":
            current_run_id = event.get("run_id", "")
        if current_run_id:
            runs_map[current_run_id].append((event, raw_id))
        if event_type == "run_end":
            current_run_id = ""

    all_runs: list[Run] = []
    all_episodes: list[Episode] = []
    all_steps: list[Step] = []
    all_tool_calls: list[ToolCall] = []

    for external_id, event_pairs in runs_map.items():
        run = Run(workspace_id=workspace_id, external_id=external_id)

        # Single episode per run for MVP
        episode = Episode(run_id=run.id, sequence=0)

        timestamps = []
        outcome = "unknown"
        score: float | None = None

        for seq, (event, raw_id) in enumerate(event_pairs):
            ts = event.get("ts")
            if ts:
                timestamps.append(ts)

            payload = event.get("payload", {})
            event_type = event.get("type", "")

            # Detect outcome from run_end events (demo uses "status", others use "outcome")
            if event_type == "run_end":
                outcome = payload.get("status", payload.get("outcome", outcome))
                score_val = payload.get("score")
                if score_val is not None:
                    score = float(score_val)

            # Determine actor
            actor = "system"
            if event_type in ("user_message", "user_feedback"):
                actor = "user"
            elif event_type in ("agent_message", "agent_action", "tool_call", "tool_result"):
                actor = "agent"

            step = Step(
                episode_id=episode.id,
                run_id=run.id,
                sequence=seq,
                event_type=event_type,
                timestamp=ts,
                actor=actor,
                content=json.dumps(payload),
                raw_event_id=raw_id,
            )
            all_steps.append(step)

            # Extract tool calls
            if event_type == "tool_call":
                tc = ToolCall(
                    step_id=step.id,
                    run_id=run.id,
                    tool_name=payload.get("tool", ""),
                    arguments=json.dumps(payload.get("arguments", {})),
                    result=json.dumps(payload.get("result", {})),
                    duration_ms=payload.get("duration_ms"),
                )
                all_tool_calls.append(tc)

        # Set run metadata
        if timestamps:
            run.started_at = min(timestamps)
            run.ended_at = max(timestamps)
        run.outcome = outcome
        run.score = score
        run.episode_count = 1
        run.step_count = len([e for e, _ in event_pairs])

        episode.started_at = run.started_at
        episode.ended_at = run.ended_at
        episode.title = f"Episode for {external_id}"

        all_runs.append(run)
        all_episodes.append(episode)

    return all_runs, all_episodes, all_steps, all_tool_calls
