import random

def epsilon_greedy_action(Q_values, epsilon=0.1):
    """
    Epsilon-greedy action selection for Reinforcement Learning.
    
    Args:
        Q_values (list): List of Q-values for each action.
        epsilon (float): Exploration probability (0 to 1).
    
    Returns:
        int: Selected action index.
    """
    if random.random() < epsilon:
        return random.randint(0, len(Q_values) - 1)
    else:
        return Q_values.index(max(Q_values))


def calculate_td_error(reward, gamma, current_value, next_value):
    """
    Calculate Temporal Difference (TD) error.
    
    Args:
        reward (float): Immediate reward
        gamma (float): Discount factor
        current_value (float): Current state value
        next_value (float): Next state value
    
    Returns:
        float: TD error
    """
    return reward + gamma * next_value - current_value
