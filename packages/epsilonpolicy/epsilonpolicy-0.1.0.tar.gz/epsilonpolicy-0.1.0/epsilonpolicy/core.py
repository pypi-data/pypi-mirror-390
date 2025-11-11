from typing import Dict, Hashable, List
import random

QTable = Dict[Hashable, Dict[Hashable, float]]

def epsilon_greedy(Q: QTable, state: Hashable, actions: List[Hashable], epsilon: float = 0.1):
    """
    Select an action using epsilon-greedy strategy.

    Args:
        Q: Q-table mapping state → action → estimated value.
        state: Current state.
        actions: List of all possible actions available.
        epsilon: Probability of exploring (choosing random action).

    Returns:
        Selected action.
    """
    if epsilon < 0 or epsilon > 1:
        raise ValueError("epsilon must be in [0,1].")

    # Initialize Q[state] if unseen
    if state not in Q:
        Q[state] = {a: 0.0 for a in actions}

    # Exploration
    if random.random() < epsilon:
        return random.choice(actions)

    # Exploitation: choose action with max Q-value
    return max(Q[state], key=Q[state].get)
