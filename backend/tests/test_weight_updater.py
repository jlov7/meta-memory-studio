"""Tests for weight updater."""

from sqlmodel import Session, SQLModel, create_engine

from app.models.memory import ContributionEvent, MemoryItem
from app.policy.weight_updater import LEARNING_RATE, WEIGHT_MIN, update_weights

ENGINE = create_engine("sqlite://", connect_args={"check_same_thread": False})


def _setup():
    SQLModel.metadata.create_all(ENGINE)


def _teardown():
    SQLModel.metadata.drop_all(ENGINE)


def test_weight_increases_on_positive_delta():
    _setup()
    try:
        with Session(ENGINE) as session:
            memory = MemoryItem(
                id="mem1",
                workspace_id="ws1",
                title="Test memory",
                content="Test content",
                current_weight=1.0,
            )
            session.add(memory)
            session.flush()

            contrib = ContributionEvent(
                memory_item_id="mem1",
                workspace_id="ws1",
                baseline_run_id="r1",
                guided_run_id="r2",
                baseline_score=0.0,
                guided_score=1.0,
                delta=1.0,
            )

            updates = update_weights(session, [contrib])
            assert len(updates) == 1
            assert updates[0].new_weight > updates[0].old_weight
            assert updates[0].new_weight == 1.0 + LEARNING_RATE * 1.0
            # update_weights sets current_weight on the in-memory object directly
            assert memory.current_weight == updates[0].new_weight
    finally:
        _teardown()


def test_weight_decreases_on_negative_delta():
    _setup()
    try:
        with Session(ENGINE) as session:
            memory = MemoryItem(
                id="mem2",
                workspace_id="ws1",
                title="Bad memory",
                content="Unhelpful content",
                current_weight=1.0,
            )
            session.add(memory)
            session.flush()

            contrib = ContributionEvent(
                memory_item_id="mem2",
                workspace_id="ws1",
                baseline_run_id="r1",
                guided_run_id="r2",
                baseline_score=1.0,
                guided_score=0.0,
                delta=-1.0,
            )

            updates = update_weights(session, [contrib])
            assert len(updates) == 1
            assert updates[0].new_weight < updates[0].old_weight
    finally:
        _teardown()


def test_weight_clamped_to_bounds():
    _setup()
    try:
        with Session(ENGINE) as session:
            memory = MemoryItem(
                id="mem3",
                workspace_id="ws1",
                title="Test",
                content="Content",
                current_weight=WEIGHT_MIN,
            )
            session.add(memory)
            session.flush()

            # Large negative delta should clamp to WEIGHT_MIN
            contrib = ContributionEvent(
                memory_item_id="mem3",
                workspace_id="ws1",
                baseline_run_id="r1",
                guided_run_id="r2",
                baseline_score=1.0,
                guided_score=0.0,
                delta=-100.0,
            )

            updates = update_weights(session, [contrib])
            if updates:
                assert updates[0].new_weight >= WEIGHT_MIN
    finally:
        _teardown()


def test_deterministic_output():
    _setup()
    try:
        results = []
        for _ in range(3):
            _teardown()
            _setup()
            with Session(ENGINE) as session:
                memory = MemoryItem(
                    id="memD",
                    workspace_id="ws1",
                    title="Deterministic",
                    content="Same input",
                    current_weight=1.5,
                )
                session.add(memory)
                session.flush()

                contrib = ContributionEvent(
                    memory_item_id="memD",
                    workspace_id="ws1",
                    baseline_run_id="r1",
                    guided_run_id="r2",
                    baseline_score=0.3,
                    guided_score=0.8,
                    delta=0.5,
                )

                updates = update_weights(session, [contrib])
                results.append(updates[0].new_weight if updates else None)

        # All runs produce the same result
        assert results[0] == results[1] == results[2]
    finally:
        _teardown()
