from typing import Any, Dict, Hashable

QTable = Dict[Hashable, Dict[Hashable, float]]

def q_update(
    Q: QTable,
    state: Hashable,
    action: Hashable,
    reward: float,
    next_state: Hashable,
    alpha: float = 0.1,
    gamma: float = 0.99,
) -> QTable:
    """
    Perform a single Q-learning update on a Q-table.

    Args:
        Q: Nested dict Q[state][action] = value (modified in place).
        state: Current state.
        action: Action taken in 'state'.
        reward: Immediate reward received after 'action'.
        next_state: State reached after the action.
        alpha: Learning rate in (0,1].
        gamma: Discount factor in [0,1].

    Returns:
        The same Q table (for convenience).
    """
    if alpha <= 0 or alpha > 1:
        raise ValueError("alpha must be in (0, 1].")
    if gamma < 0 or gamma > 1:
        raise ValueError("gamma must be in [0, 1].")

    # Ensure keys exist
    if state not in Q:
        Q[state] = {}
    if action not in Q[state]:
        Q[state][action] = 0.0

    # Best future value from next_state
    future_best = 0.0
    next_actions = Q.get(next_state, {})
    if next_actions:
        future_best = max(next_actions.values())

    # Q-learning update
    old = Q[state][action]
    target = reward + gamma * future_best
    Q[state][action] = old + alpha * (target - old)
    return Q
