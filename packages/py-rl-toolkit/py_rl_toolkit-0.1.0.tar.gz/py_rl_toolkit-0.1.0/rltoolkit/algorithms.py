"""
Core reinforcement learning algorithms implementation.
"""

import numpy as np
from typing import Union, Tuple, Optional
import random

try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class QLearning:
    """
    Q-Learning algorithm implementation.
    
    A model-free off-policy reinforcement learning algorithm that learns
    the optimal action-value function Q*(s,a).
    """
    
    def __init__(self, state_space: int, action_space: int, 
                 learning_rate: float = 0.1, discount_factor: float = 0.99,
                 initial_q_value: float = 0.0):
        """
        Initialize Q-Learning agent.
        
        Args:
            state_space: Number of states in the environment
            action_space: Number of actions in the environment
            learning_rate: Learning rate (alpha) for Q-value updates
            discount_factor: Discount factor (gamma) for future rewards
            initial_q_value: Initial value for Q-table
        """
        self.state_space = state_space
        self.action_space = action_space
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        
        # Initialize Q-table
        self.q_table = np.full((state_space, action_space), initial_q_value, dtype=float)
        
    def get_q_value(self, state: int, action: int) -> float:
        """Get Q-value for state-action pair."""
        return self.q_table[state, action]
    
    def set_q_value(self, state: int, action: int, value: float):
        """Set Q-value for state-action pair."""
        self.q_table[state, action] = value
        
    def update(self, state: int, action: int, reward: float, 
               next_state: int, done: bool = False):
        """
        Update Q-value using Q-Learning update rule.
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode is done
        """
        current_q = self.get_q_value(state, action)
        
        if done:
            target = reward
        else:
            # Get maximum Q-value for next state
            max_next_q = np.max(self.q_table[next_state])
            target = reward + self.discount_factor * max_next_q
            
        # Update Q-value
        new_q = current_q + self.learning_rate * (target - current_q)
        self.set_q_value(state, action, new_q)
        
    def get_action_values(self, state: int) -> np.ndarray:
        """Get all action values for a given state."""
        return self.q_table[state].copy()
    
    def get_best_action(self, state: int) -> int:
        """Get the action with highest Q-value for a given state."""
        return int(np.argmax(self.q_table[state]))
    
    def get_policy(self) -> np.ndarray:
        """Get the greedy policy derived from Q-values."""
        return np.array([self.get_best_action(s) for s in range(self.state_space)])


class SARSAAgent:
    """
    SARSA (State-Action-Reward-State-Action) algorithm implementation.
    
    A model-free on-policy reinforcement learning algorithm that learns
    the action-value function Q(s,a) for the current policy.
    """
    
    def __init__(self, state_space: int, action_space: int,
                 learning_rate: float = 0.1, discount_factor: float = 0.99,
                 initial_q_value: float = 0.0):
        """
        Initialize SARSA agent.
        
        Args:
            state_space: Number of states in the environment
            action_space: Number of actions in the environment
            learning_rate: Learning rate (alpha) for Q-value updates
            discount_factor: Discount factor (gamma) for future rewards
            initial_q_value: Initial value for Q-table
        """
        self.state_space = state_space
        self.action_space = action_space
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        
        # Initialize Q-table
        self.q_table = np.full((state_space, action_space), initial_q_value, dtype=float)
        
    def get_q_value(self, state: int, action: int) -> float:
        """Get Q-value for state-action pair."""
        return self.q_table[state, action]
    
    def set_q_value(self, state: int, action: int, value: float):
        """Set Q-value for state-action pair."""
        self.q_table[state, action] = value
        
    def update(self, state: int, action: int, reward: float, 
               next_state: int, next_action: int, done: bool = False):
        """
        Update Q-value using SARSA update rule.
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            next_action: Next action (from current policy)
            done: Whether episode is done
        """
        current_q = self.get_q_value(state, action)
        
        if done:
            target = reward
        else:
            # Get Q-value for next state-action pair
            next_q = self.get_q_value(next_state, next_action)
            target = reward + self.discount_factor * next_q
            
        # Update Q-value
        new_q = current_q + self.learning_rate * (target - current_q)
        self.set_q_value(state, action, new_q)
        
    def get_action_values(self, state: int) -> np.ndarray:
        """Get all action values for a given state."""
        return self.q_table[state].copy()
    
    def get_best_action(self, state: int) -> int:
        """Get the action with highest Q-value for a given state."""
        return int(np.argmax(self.q_table[state]))


class DQNNetwork(nn.Module):
    """Simple neural network for DQN (used when PyTorch is available)."""
    
    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 128):
        super(DQNNetwork, self).__init__()
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required for DQN. Install with: pip install torch")
            
        self.network = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, action_dim)
        )
        
    def forward(self, x):
        return self.network(x)


class DQNAgent:
    """
    Deep Q-Network (DQN) algorithm implementation.
    
    A deep reinforcement learning algorithm that uses a neural network
    to approximate the Q-function for environments with continuous state spaces.
    """
    
    def __init__(self, state_dim: int, action_dim: int, 
                 learning_rate: float = 0.001, discount_factor: float = 0.99,
                 epsilon: float = 1.0, epsilon_min: float = 0.01,
                 epsilon_decay: float = 0.995, memory_size: int = 10000,
                 batch_size: int = 32, hidden_dim: int = 128):
        """
        Initialize DQN agent.
        
        Args:
            state_dim: Dimension of state space
            action_dim: Number of actions
            learning_rate: Learning rate for neural network
            discount_factor: Discount factor for future rewards
            epsilon: Initial exploration rate
            epsilon_min: Minimum exploration rate
            epsilon_decay: Decay rate for epsilon
            memory_size: Size of experience replay buffer
            batch_size: Batch size for training
            hidden_dim: Hidden layer dimension
        """
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required for DQN. Install with: pip install torch")
            
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.memory_size = memory_size
        self.batch_size = batch_size
        
        # Neural network
        self.q_network = DQNNetwork(state_dim, action_dim, hidden_dim)
        self.target_network = DQNNetwork(state_dim, action_dim, hidden_dim)
        self.optimizer = torch.optim.Adam(self.q_network.parameters(), lr=learning_rate)
        
        # Experience replay buffer
        self.memory = []
        self.memory_counter = 0
        
        # Update target network
        self.update_target_network()
        
    def update_target_network(self):
        """Update target network with current network weights."""
        self.target_network.load_state_dict(self.q_network.state_dict())
        
    def remember(self, state: np.ndarray, action: int, reward: float, 
                 next_state: np.ndarray, done: bool):
        """Store experience in replay buffer."""
        experience = (state, action, reward, next_state, done)
        
        if len(self.memory) < self.memory_size:
            self.memory.append(experience)
        else:
            self.memory[self.memory_counter % self.memory_size] = experience
            
        self.memory_counter += 1
        
    def act(self, state: np.ndarray) -> int:
        """Select action using epsilon-greedy policy."""
        if np.random.random() <= self.epsilon:
            return random.randint(0, self.action_dim - 1)
        
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        q_values = self.q_network(state_tensor)
        return int(torch.argmax(q_values).item())
    
    def replay(self):
        """Train the network on a batch of experiences."""
        if len(self.memory) < self.batch_size:
            return
            
        # Sample batch from memory
        batch = random.sample(self.memory, self.batch_size)
        
        states = torch.FloatTensor([e[0] for e in batch])
        actions = torch.LongTensor([e[1] for e in batch])
        rewards = torch.FloatTensor([e[2] for e in batch])
        next_states = torch.FloatTensor([e[3] for e in batch])
        dones = torch.BoolTensor([e[4] for e in batch])
        
        # Current Q values
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1))
        
        # Next Q values from target network
        next_q_values = self.target_network(next_states).max(1)[0].detach()
        target_q_values = rewards + (self.discount_factor * next_q_values * ~dones)
        
        # Compute loss
        loss = nn.MSELoss()(current_q_values.squeeze(), target_q_values)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
            
    def update(self, state: np.ndarray, action: int, reward: float, 
               next_state: np.ndarray, done: bool):
        """
        Store experience and train the network.
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode is done
        """
        self.remember(state, action, reward, next_state, done)
        self.replay()
        
    def get_q_values(self, state: np.ndarray) -> np.ndarray:
        """Get Q-values for a given state."""
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        with torch.no_grad():
            q_values = self.q_network(state_tensor)
        return q_values.numpy().squeeze()