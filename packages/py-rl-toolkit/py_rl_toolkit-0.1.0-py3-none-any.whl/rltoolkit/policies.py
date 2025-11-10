"""
Policy implementations for action selection in reinforcement learning.
"""

import numpy as np
import random
from typing import Optional, Union
from .algorithms import QLearning, SARSAAgent, DQNAgent


class Policy:
    """Base class for all policies."""
    
    def select_action(self, agent: Union[QLearning, SARSAAgent, DQNAgent], 
                     state: Union[int, np.ndarray], 
                     valid_actions: Optional[list] = None) -> int:
        """
        Select action based on policy.
        
        Args:
            agent: The RL agent
            state: Current state
            valid_actions: List of valid actions (optional)
            
        Returns:
            Selected action
        """
        raise NotImplementedError("Subclasses must implement select_action method")


class RandomPolicy(Policy):
    """Random policy that selects actions uniformly at random."""
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize random policy.
        
        Args:
            seed: Random seed for reproducibility
        """
        self._random = random.Random(seed) if seed is not None else random.Random()
        self._np_random = np.random.RandomState(seed) if seed is not None else np.random.RandomState()
    
    def select_action(self, agent: Union[QLearning, SARSAAgent, DQNAgent], 
                     state: Union[int, np.ndarray], 
                     valid_actions: Optional[list] = None) -> int:
        """Select random action."""
        if valid_actions:
            return self._random.choice(valid_actions)
        else:
            # Assume action space is available from agent
            if hasattr(agent, 'action_space'):
                return self._random.randint(0, agent.action_space - 1)
            else:
                # For DQN agent
                if hasattr(agent, 'action_dim'):
                    return self._random.randint(0, agent.action_dim - 1)
                else:
                    raise ValueError("Cannot determine action space")


class GreedyPolicy(Policy):
    """Greedy policy that always selects the action with highest Q-value."""
    
    def select_action(self, agent: Union[QLearning, SARSAAgent, DQNAgent], 
                     state: Union[int, np.ndarray], 
                     valid_actions: Optional[list] = None) -> int:
        """Select action with highest Q-value."""
        if isinstance(agent, (QLearning, SARSAAgent)):
            # Tabular agents
            q_values = agent.get_action_values(state)
            
            if valid_actions:
                # Filter Q-values for valid actions only
                valid_q_values = [q_values[a] for a in valid_actions]
                best_valid_idx = int(np.argmax(valid_q_values))
                return valid_actions[best_valid_idx]
            else:
                return agent.get_best_action(state)
                
        elif isinstance(agent, DQNAgent):
            # DQN agent
            q_values = agent.get_q_values(state)
            
            if valid_actions:
                # Filter Q-values for valid actions only
                valid_q_values = [q_values[a] for a in valid_actions]
                best_valid_idx = int(np.argmax(valid_q_values))
                return valid_actions[best_valid_idx]
            else:
                return int(np.argmax(q_values))
        else:
            raise ValueError(f"Unknown agent type: {type(agent)}")


class EpsilonGreedyPolicy(Policy):
    """
    Epsilon-greedy policy that balances exploration and exploitation.
    
    With probability epsilon, selects a random action (exploration).
    With probability (1-epsilon), selects the greedy action (exploitation).
    """
    
    def __init__(self, epsilon: float = 0.1, epsilon_decay: float = 1.0,
                 epsilon_min: float = 0.01, seed: Optional[int] = None):
        """
        Initialize epsilon-greedy policy.
        
        Args:
            epsilon: Initial exploration rate (0 <= epsilon <= 1)
            epsilon_decay: Decay factor for epsilon after each action
            epsilon_min: Minimum value for epsilon
            seed: Random seed for reproducibility
        """
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
    
    def select_action(self, agent: Union[QLearning, SARSAAgent, DQNAgent], 
                     state: Union[int, np.ndarray], 
                     valid_actions: Optional[list] = None) -> int:
        """Select action using epsilon-greedy strategy."""
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        # Choose between exploration and exploitation
        if random.random() < self.epsilon:
            # Exploration: random action
            if valid_actions:
                return random.choice(valid_actions)
            else:
                # Determine action space
                if hasattr(agent, 'action_space'):
                    return random.randint(0, agent.action_space - 1)
                elif hasattr(agent, 'action_dim'):
                    return random.randint(0, agent.action_dim - 1)
                else:
                    raise ValueError("Cannot determine action space")
        else:
            # Exploitation: greedy action
            greedy_policy = GreedyPolicy()
            return greedy_policy.select_action(agent, state, valid_actions)
    
    def get_epsilon(self) -> float:
        """Get current epsilon value."""
        return self.epsilon


class SoftmaxPolicy(Policy):
    """
    Softmax policy (Boltzmann exploration) that selects actions
    based on their Q-values using a softmax distribution.
    """
    
    def __init__(self, temperature: float = 1.0, temperature_decay: float = 1.0,
                 temperature_min: float = 0.1, seed: Optional[int] = None):
        """
        Initialize softmax policy.
        
        Args:
            temperature: Temperature parameter for softmax (higher = more exploration)
            temperature_decay: Decay factor for temperature
            temperature_min: Minimum temperature value
            seed: Random seed for reproducibility
        """
        self.temperature = temperature
        self.temperature_decay = temperature_decay
        self.temperature_min = temperature_min
        
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
    
    def select_action(self, agent: Union[QLearning, SARSAAgent, DQNAgent], 
                     state: Union[int, np.ndarray], 
                     valid_actions: Optional[list] = None) -> int:
        """Select action using softmax policy."""
        # Decay temperature
        if self.temperature > self.temperature_min:
            self.temperature *= self.temperature_decay
        
        if isinstance(agent, (QLearning, SARSAAgent)):
            q_values = agent.get_action_values(state)
        elif isinstance(agent, DQNAgent):
            q_values = agent.get_q_values(state)
        else:
            raise ValueError(f"Unknown agent type: {type(agent)}")
        
        if valid_actions:
            # Filter Q-values for valid actions only
            valid_q_values = np.array([q_values[a] for a in valid_actions])
            probabilities = self._softmax(valid_q_values)
            return np.random.choice(valid_actions, p=probabilities)
        else:
            probabilities = self._softmax(q_values)
            return int(np.random.choice(len(q_values), p=probabilities))
    
    def _softmax(self, values: np.ndarray) -> np.ndarray:
        """Compute softmax probabilities."""
        # Subtract max for numerical stability
        max_val = np.max(values)
        exp_values = np.exp((values - max_val) / self.temperature)
        return exp_values / np.sum(exp_values)
    
    def get_temperature(self) -> float:
        """Get current temperature value."""
        return self.temperature