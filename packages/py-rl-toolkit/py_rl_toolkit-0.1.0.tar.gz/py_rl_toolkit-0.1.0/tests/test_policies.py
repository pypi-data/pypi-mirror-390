"""
Test cases for reinforcement learning policies.
"""

import pytest
import numpy as np
import sys
import os

# Add the parent directory to the path so we can import rltoolkit
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rltoolkit.policies import RandomPolicy, GreedyPolicy, EpsilonGreedyPolicy, SoftmaxPolicy
from rltoolkit.algorithms import QLearning, SARSAAgent


class TestRandomPolicy:
    """Test cases for RandomPolicy."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.policy = RandomPolicy(seed=42)
        self.agent = QLearning(state_space=10, action_space=4)
    
    def test_select_action(self):
        """Test action selection."""
        state = 0
        action = self.policy.select_action(self.agent, state)
        
        assert isinstance(action, int)
        assert 0 <= action < self.agent.action_space
    
    def test_select_action_with_valid_actions(self):
        """Test action selection with valid actions list."""
        state = 0
        valid_actions = [0, 2]
        action = self.policy.select_action(self.agent, state, valid_actions)
        
        assert action in valid_actions
    
    def test_reproducibility(self):
        """Test reproducibility with seed."""
        policy1 = RandomPolicy(seed=42)
        policy2 = RandomPolicy(seed=42)
        
        actions1 = [policy1.select_action(self.agent, 0) for _ in range(10)]
        actions2 = [policy2.select_action(self.agent, 0) for _ in range(10)]
        
        # Both should produce the same sequence of actions
        assert actions1 == actions2


class TestGreedyPolicy:
    """Test cases for GreedyPolicy."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.policy = GreedyPolicy()
        self.agent = QLearning(state_space=10, action_space=4)
    
    def test_select_action_greedy(self):
        """Test greedy action selection."""
        state = 0
        
        # Set Q-values with one clearly best action
        self.agent.set_q_value(state, 0, 1.0)
        self.agent.set_q_value(state, 1, 5.0)  # Best action
        self.agent.set_q_value(state, 2, 2.0)
        self.agent.set_q_value(state, 3, 1.5)
        
        action = self.policy.select_action(self.agent, state)
        assert action == 1  # Should select action with highest Q-value
    
    def test_select_action_with_valid_actions(self):
        """Test greedy action selection with valid actions."""
        state = 0
        
        # Set Q-values
        self.agent.set_q_value(state, 0, 1.0)
        self.agent.set_q_value(state, 1, 5.0)  # Best overall
        self.agent.set_q_value(state, 2, 2.0)
        self.agent.set_q_value(state, 3, 1.5)
        
        # Restrict to actions 0 and 2
        valid_actions = [0, 2]
        action = self.policy.select_action(self.agent, state, valid_actions)
        assert action == 2  # Should select best among valid actions (2.0 > 1.0)
    
    def test_tie_breaking(self):
        """Test tie-breaking when multiple actions have same Q-value."""
        state = 0
        
        # Set equal Q-values for multiple actions
        for action in range(self.agent.action_space):
            self.agent.set_q_value(state, action, 1.0)
        
        # Should select one of the tied actions
        action = self.policy.select_action(self.agent, state)
        assert 0 <= action < self.agent.action_space


class TestEpsilonGreedyPolicy:
    """Test cases for EpsilonGreedyPolicy."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.epsilon = 0.1
        self.policy = EpsilonGreedyPolicy(epsilon=self.epsilon, seed=42)
        self.agent = QLearning(state_space=10, action_space=4)
        
        # Set up Q-values with clear best action
        for state in range(10):
            self.agent.set_q_value(state, 0, 1.0)
            self.agent.set_q_value(state, 1, 5.0)  # Best action
            self.agent.set_q_value(state, 2, 2.0)
            self.agent.set_q_value(state, 3, 1.5)
    
    def test_epsilon_initialization(self):
        """Test epsilon initialization."""
        assert self.policy.epsilon == self.epsilon
    
    def test_greedy_action_selection(self):
        """Test that greedy action is selected with high probability."""
        state = 0
        
        # Select many actions and count frequency
        action_counts = {i: 0 for i in range(self.agent.action_space)}
        num_trials = 1000
        
        for _ in range(num_trials):
            action = self.policy.select_action(self.agent, state)
            action_counts[action] += 1
        
        # Best action (1) should be selected most frequently
        assert action_counts[1] > num_trials * 0.5  # Should be selected majority of time
    
    def test_epsilon_decay(self):
        """Test epsilon decay functionality."""
        initial_epsilon = self.policy.epsilon
        
        # Select actions to trigger decay
        for _ in range(100):
            self.policy.select_action(self.agent, 0)
        
        # Epsilon should have decayed
        assert self.policy.epsilon <= initial_epsilon
        assert self.policy.epsilon >= self.policy.epsilon_min
    
    def test_get_epsilon(self):
        """Test getting current epsilon value."""
        epsilon = self.policy.get_epsilon()
        assert epsilon == self.policy.epsilon


class TestSoftmaxPolicy:
    """Test cases for SoftmaxPolicy."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temperature = 1.0
        self.policy = SoftmaxPolicy(temperature=self.temperature, seed=42)
        self.agent = QLearning(state_space=10, action_space=4)
        
        # Set up Q-values with clear best action
        for state in range(10):
            self.agent.set_q_value(state, 0, 1.0)
            self.agent.set_q_value(state, 1, 5.0)  # Best action
            self.agent.set_q_value(state, 2, 2.0)
            self.agent.set_q_value(state, 3, 1.5)
    
    def test_temperature_initialization(self):
        """Test temperature initialization."""
        assert self.policy.temperature == self.temperature
    
    def test_action_selection_probabilities(self):
        """Test that actions are selected according to softmax probabilities."""
        state = 0
        
        # Select many actions and count frequency
        action_counts = {i: 0 for i in range(self.agent.action_space)}
        num_trials = 1000
        
        for _ in range(num_trials):
            action = self.policy.select_action(self.agent, state)
            action_counts[action] += 1
        
        # Best action should be selected most frequently
        assert action_counts[1] > action_counts[0]
        assert action_counts[1] > action_counts[2]
        assert action_counts[1] > action_counts[3]
    
    def test_temperature_decay(self):
        """Test temperature decay functionality."""
        initial_temperature = self.policy.temperature
        
        # Select actions to trigger decay
        for _ in range(100):
            self.policy.select_action(self.agent, 0)
        
        # Temperature should have decayed
        assert self.policy.temperature <= initial_temperature
        assert self.policy.temperature >= self.policy.temperature_min
    
    def test_get_temperature(self):
        """Test getting current temperature value."""
        temperature = self.policy.get_temperature()
        assert temperature == self.policy.temperature
    
    def test_softmax_calculation(self):
        """Test softmax probability calculation."""
        values = np.array([1.0, 2.0, 3.0])
        probabilities = self.policy._softmax(values)
        
        # Probabilities should sum to 1
        assert abs(np.sum(probabilities) - 1.0) < 1e-6
        
        # Higher values should have higher probabilities
        assert probabilities[2] > probabilities[1]
        assert probabilities[1] > probabilities[0]


class TestPolicyIntegration:
    """Integration tests for policies with agents."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.q_agent = QLearning(state_space=10, action_space=4)
        self.sarsa_agent = SARSAAgent(state_space=10, action_space=4)
        
        # Set up some Q-values for testing
        for state in range(10):
            for action in range(4):
                self.q_agent.set_q_value(state, action, float(action + 1))
                self.sarsa_agent.set_q_value(state, action, float(action + 1))
    
    def test_policies_with_different_agents(self):
        """Test that policies work with different agent types."""
        policies = [
            RandomPolicy(seed=42),
            GreedyPolicy(),
            EpsilonGreedyPolicy(epsilon=0.1),
            SoftmaxPolicy(temperature=1.0)
        ]
        
        agents = [self.q_agent, self.sarsa_agent]
        
        for policy in policies:
            for agent in agents:
                action = policy.select_action(agent, 0)
                assert isinstance(action, int)
                assert 0 <= action < agent.action_space


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__])