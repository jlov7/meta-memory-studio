"""Deterministic weight update rule for memory items."""

from sqlmodel import Session

from app.models.memory import ContributionEvent, MemoryItem, WeightUpdate

LEARNING_RATE = 0.1
WEIGHT_MIN = 0.01
WEIGHT_MAX = 5.0


def update_weights(
    session: Session,
    contributions: list[ContributionEvent],
) -> list[WeightUpdate]:
    """Apply weight updates based on contribution deltas.

    Rule: w_new = clamp(w_old + lr * delta, WEIGHT_MIN, WEIGHT_MAX)
    """
    updates: list[WeightUpdate] = []

    for contrib in contributions:
        memory = session.get(MemoryItem, contrib.memory_item_id)
        if not memory or memory.status != "active":
            continue

        old_weight = memory.current_weight
        raw_new = old_weight + LEARNING_RATE * contrib.delta
        new_weight = round(max(WEIGHT_MIN, min(WEIGHT_MAX, raw_new)), 4)

        if new_weight == old_weight:
            continue

        memory.current_weight = new_weight
        session.add(memory)

        update = WeightUpdate(
            memory_item_id=memory.id,
            old_weight=old_weight,
            new_weight=new_weight,
            delta=round(new_weight - old_weight, 4),
            reason="evolution",
        )
        updates.append(update)
        session.add(update)

    return updates
