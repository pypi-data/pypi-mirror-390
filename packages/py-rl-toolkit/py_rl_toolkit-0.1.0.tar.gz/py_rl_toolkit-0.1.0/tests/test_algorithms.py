"""
Test cases for reinforcement learning algorithms.
"""

import pytest
import numpy as np
import sys
import os

# Add the parent directory to the path so we can import rltoolkit
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rltoolkit.algorithms import QLearning, SARSAAgent, DQNAgent


class TestQLearning:
    """Test cases for Q-Learning algorithm."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.state_space = 10
        self.action_space = 4
        self.agent = QLearning(self.state_space, self.action_space)
    
    def test_initialization(self):
        """Test Q-Learning agent initialization."""
        assert self.agent.state_space == self.state_space
        assert self.agent.action_space == self.action_space
        assert self.agent.q_table.shape == (self.state_space, self.action_space)
        assert np.all(self.agent.q_table == 0.0)  # Default initial value
    
    def test_q_value_access(self):
        """Test Q-value get and set methods."""
        state, action = 0, 0
        value = 5.0
        
        # Test setting Q-value
        self.agent.set_q_value(state, action, value)
        assert self.agent.get_q_value(state, action) == value
        
        # Test getting Q-value
        retrieved_value = self.agent.get_q_value(state, action)
        assert retrieved_value == value
    
    def test_update_q_value(self):
        """Test Q-value update method."""
        state, action = 0, 0
        reward = 1.0
        next_state = 1
        
        # Initial Q-value should be 0
        assert self.agent.get_q_value(state, action) == 0.0
        
        # Update Q-value
        self.agent.update(state, action, reward, next_state, done=False)
        
        # Q-value should have changed
        new_q_value = self.agent.get_q_value(state, action)
        assert new_q_value != 0.0
        
        # Expected Q-value calculation
        # Q(s,a) = Q(s,a) + alpha * [r + gamma * max Q(s',a') - Q(s,a)]
        # Q(s,a) = 0 + 0.1 * [1 + 0.99 * max Q(s',a') - 0]
        max_next_q = np.max(self.agent.q_table[next_state])
        expected_q = 0 + 0.1 * (reward + 0.99 * max_next_q - 0)
        assert abs(new_q_value - expected_q) < 1e-6
    
    def test_update_terminal_state(self):
        """Test Q-value update for terminal state."""
        state, action = 0, 0
        reward = 10.0
        next_state = 1
        
        # Update for terminal state (done=True)
        self.agent.update(state, action, reward, next_state, done=True)
        
        # For terminal state, target = reward (no future value)
        new_q_value = self.agent.get_q_value(state, action)
        expected_q = 0 + 0.1 * (reward - 0)  # No future value for terminal state
        assert abs(new_q_value - expected_q) < 1e-6
    
    def test_get_best_action(self):
        """Test getting the best action for a state."""
        state = 0
        
        # Set different Q-values for different actions
        self.agent.set_q_value(state, 0, 1.0)
        self.agent.set_q_value(state, 1, 3.0)
        self.agent.set_q_value(state, 2, 2.0)
        self.agent.set_q_value(state, 3, 0.5)
        
        # Best action should be action 1 (highest Q-value)
        best_action = self.agent.get_best_action(state)
        assert best_action == 1
    
    def test_get_policy(self):
        """Test getting the greedy policy."""
        # Set some Q-values
        for s in range(self.state_space):
            self.agent.set_q_value(s, 0, 1.0)
            self.agent.set_q_value(s, 1, 2.0)
            self.agent.set_q_value(s, 2, 0.5)
            self.agent.set_q_value(s, 3, 1.5)
        
        policy = self.agent.get_policy()
        
        # Policy should select action 1 for all states (highest Q-value)
        assert len(policy) == self.state_space
        assert np.all(policy == 1)


class TestSARSAAgent:
    """Test cases for SARSA algorithm."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.state_space = 10
        self.action_space = 4
        self.agent = SARSAAgent(self.state_space, self.action_space)
    
    def test_initialization(self):
        """Test SARSA agent initialization."""
        assert self.agent.state_space == self.state_space
        assert self.agent.action_space == self.action_space
        assert self.agent.q_table.shape == (self.state_space, self.action_space)
    
    def test_sarsa_update(self):
        """Test SARSA update method."""
        state, action = 0, 0
        reward = 1.0
        next_state, next_action = 1, 1
        
        # Update Q-value
        self.agent.update(state, action, reward, next_state, next_action, done=False)
        
        # Q-value should have changed
        new_q_value = self.agent.get_q_value(state, action)
        assert new_q_value != 0.0
        
        # Expected Q-value calculation for SARSA
        # Q(s,a) = Q(s,a) + alpha * [r + gamma * Q(s',a') - Q(s,a)]
        next_q = self.agent.get_q_value(next_state, next_action)
        expected_q = 0 + 0.1 * (reward + 0.99 * next_q - 0)
        assert abs(new_q_value - expected_q) < 1e-6
    
    def test_sarsa_terminal_update(self):
        """Test SARSA update for terminal state."""
        state, action = 0, 0
        reward = 10.0
        next_state, next_action = 1, 1
        
        # Update for terminal state (done=True)
        self.agent.update(state, action, reward, next_state, next_action, done=True)
        
        # For terminal state, target = reward (no future value)
        new_q_value = self.agent.get_q_value(state, action)
        expected_q = 0 + 0.1 * (reward - 0)  # No future value for terminal state
        assert abs(new_q_value - expected_q) < 1e-6


class TestDQNAgent:
    """Test cases for DQN algorithm."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.state_dim = 4
        self.action_dim = 2
        try:
            self.agent = DQNAgent(self.state_dim, self.action_dim)
            self.torch_available = True
        except ImportError:
            self.torch_available = False
            pytest.skip("PyTorch not available")
    
    def test_initialization(self):
        """Test DQN agent initialization."""
        if not self.torch_available:
            pytest.skip("PyTorch not available")
        
        assert self.agent.state_dim == self.state_dim
        assert self.agent.action_dim == self.action_dim
        assert hasattr(self.agent, 'q_network')
        assert hasattr(self.agent, 'target_network')
        assert hasattr(self.agent, 'memory')
    
    def test_act_method(self):
        """Test action selection method."""
        if not self.torch_available:
            pytest.skip("PyTorch not available")
        
        state = np.random.random(self.state_dim)
        action = self.agent.act(state)
        
        assert isinstance(action, int)
        assert 0 <= action < self.action_dim
    
    def test_get_q_values(self):
        """Test getting Q-values for a state."""
        if not self.torch_available:
            pytest.skip("PyTorch not available")
        
        state = np.random.random(self.state_dim)
        q_values = self.agent.get_q_values(state)
        
        assert isinstance(q_values, np.ndarray)
        assert q_values.shape == (self.action_dim,)
    
    def test_remember_and_replay(self):
        """Test experience replay functionality."""
        if not self.torch_available:
            pytest.skip("PyTorch not available")
        
        # Add some experiences to memory
        for _ in range(50):
            state = np.random.random(self.state_dim)
            action = np.random.randint(0, self.action_dim)
            reward = np.random.random()
            next_state = np.random.random(self.state_dim)
            done = np.random.choice([True, False])
            
            self.agent.remember(state, action, reward, next_state, done)
        
        # Check that memory has experiences
        assert len(self.agent.memory) == 50
        
        # Try to replay (should not crash)
        self.agent.replay()
    
    def test_epsilon_decay(self):
        """Test epsilon decay functionality."""
        if not self.torch_available:
            pytest.skip("PyTorch not available")
        
        initial_epsilon = self.agent.epsilon
        
        # Perform some updates to trigger epsilon decay
        for _ in range(10):
            state = np.random.random(self.state_dim)
            action = np.random.randint(0, self.action_dim)
            reward = np.random.random()
            next_state = np.random.random(self.state_dim)
            done = False
            
            self.agent.update(state, action, reward, next_state, done)
        
        # Epsilon should have decayed
        assert self.agent.epsilon <= initial_epsilon
        assert self.agent.epsilon >= self.agent.epsilon_min


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__])