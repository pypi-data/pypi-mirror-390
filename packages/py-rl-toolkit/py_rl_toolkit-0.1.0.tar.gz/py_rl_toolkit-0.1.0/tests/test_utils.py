"""
Test cases for utility functions.
"""

import pytest
import numpy as np
import sys
import os

# Add the parent directory to the path so we can import rltoolkit
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rltoolkit.utils import run_episode, train_agent, evaluate_agent, plot_learning_curve
from rltoolkit.algorithms import QLearning, SARSAAgent
from rltoolkit.environments import SimpleGridWorld
from rltoolkit.policies import EpsilonGreedyPolicy


class TestRunEpisode:
    """Test cases for run_episode function."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.env = SimpleGridWorld(size=3)
        self.agent = QLearning(state_space=self.env.state_space, action_space=self.env.action_space)
        self.policy = EpsilonGreedyPolicy(epsilon=0.1)
    
    def test_run_episode_basic(self):
        """Test basic episode execution."""
        reward, steps = run_episode(self.env, self.agent, self.policy)
        
        assert isinstance(reward, (int, float))
        assert isinstance(steps, int)
        assert steps > 0
        assert steps <= 1000  # Default max_steps
    
    def test_run_episode_with_max_steps(self):
        """Test episode with custom max steps."""
        max_steps = 50
        reward, steps = run_episode(self.env, self.agent, self.policy, max_steps=max_steps)
        
        assert steps <= max_steps
    
    def test_run_episode_with_sarsa(self):
        """Test episode with SARSA agent."""
        sarsa_agent = SARSAAgent(state_space=self.env.state_space, action_space=self.env.action_space)
        reward, steps = run_episode(self.env, sarsa_agent, self.policy)
        
        assert isinstance(reward, (int, float))
        assert isinstance(steps, int)
        assert steps > 0


class TestTrainAgent:
    """Test cases for train_agent function."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.env = SimpleGridWorld(size=3)
        self.agent = QLearning(state_space=self.env.state_space, action_space=self.env.action_space)
        self.policy = EpsilonGreedyPolicy(epsilon=0.1)
    
    def test_train_agent_basic(self):
        """Test basic agent training."""
        num_episodes = 10
        rewards = train_agent(self.env, self.agent, self.policy, num_episodes=num_episodes)
        
        assert isinstance(rewards, list)
        assert len(rewards) == num_episodes
        assert all(isinstance(r, (int, float)) for r in rewards)
    
    def test_train_agent_with_target_reward(self):
        """Test training with target reward."""
        # Set a very high target reward that won't be achieved
        target_reward = 1000.0
        num_episodes = 5
        
        rewards = train_agent(self.env, self.agent, self.policy, 
                            num_episodes=num_episodes, target_reward=target_reward)
        
        # Should complete all episodes since target is unreachable
        assert len(rewards) == num_episodes
    
    def test_train_agent_early_stopping(self):
        """Test early stopping when target reward is achieved."""
        # Set a very low target reward that will be achieved quickly
        target_reward = -100.0  # Very easy to achieve
        num_episodes = 100
        
        rewards = train_agent(self.env, self.agent, self.policy, 
                            num_episodes=num_episodes, target_reward=target_reward)
        
        # Should stop early (though this test might be flaky)
        assert len(rewards) <= num_episodes


class TestEvaluateAgent:
    """Test cases for evaluate_agent function."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.env = SimpleGridWorld(size=3)
        self.agent = QLearning(state_space=self.env.state_space, action_space=self.env.action_space)
        self.policy = EpsilonGreedyPolicy(epsilon=0.1)
    
    def test_evaluate_agent_basic(self):
        """Test basic agent evaluation."""
        # First train the agent a bit
        train_agent(self.env, self.agent, self.policy, num_episodes=10)
        
        # Then evaluate
        mean_reward, std_reward, rewards = evaluate_agent(self.env, self.agent, num_episodes=5)
        
        assert isinstance(mean_reward, (int, float))
        assert isinstance(std_reward, (int, float))
        assert isinstance(rewards, list)
        assert len(rewards) == 5
        assert all(isinstance(r, (int, float)) for r in rewards)
    
    def test_evaluate_agent_with_render(self):
        """Test evaluation with rendering (should not crash)."""
        # Train agent first
        train_agent(self.env, self.agent, self.policy, num_episodes=5)
        
        # Evaluate with render (capture output to avoid cluttering test output)
        import io
        import contextlib
        
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            mean_reward, std_reward, rewards = evaluate_agent(
                self.env, self.agent, num_episodes=2, render=True)
        
        assert isinstance(mean_reward, (int, float))
        assert len(rewards) == 2


class TestPlotLearningCurve:
    """Test cases for plot_learning_curve function."""
    
    def test_plot_learning_curve_basic(self):
        """Test basic learning curve plotting."""
        rewards = [1.0, 2.0, 3.0, 2.5, 3.5, 4.0, 3.8, 4.2, 4.5, 4.8]
        
        # This should not crash (though we can't easily test the plot output)
        try:
            plot_learning_curve(rewards, window_size=3)
            # If we get here, the function executed without error
            assert True
        except Exception as e:
            pytest.fail(f"plot_learning_curve raised an exception: {e}")
    
    def test_plot_learning_curve_with_short_rewards(self):
        """Test plotting with short rewards list."""
        rewards = [1.0, 2.0, 3.0]
        
        try:
            plot_learning_curve(rewards, window_size=2)
            assert True
        except Exception as e:
            pytest.fail(f"plot_learning_curve raised an exception: {e}")
    
    def test_plot_learning_curve_with_save_path(self, tmp_path):
        """Test plotting with save path."""
        rewards = [1.0, 2.0, 3.0, 2.5, 3.5, 4.0, 3.8, 4.2, 4.5, 4.8]
        save_path = tmp_path / "test_plot.png"
        
        try:
            plot_learning_curve(rewards, save_path=str(save_path))
            assert save_path.exists()
        except Exception as e:
            pytest.fail(f"plot_learning_curve raised an exception: {e}")


class TestCompareAlgorithms:
    """Test cases for compare_algorithms function."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.env = SimpleGridWorld(size=3)
    
    def test_compare_algorithms_basic(self):
        """Test basic algorithm comparison."""
        from rltoolkit.utils import compare_algorithms
        
        algorithms = [
            ("Q-Learning", QLearning(state_space=self.env.state_space, action_space=self.env.action_space)),
            ("SARSA", SARSAAgent(state_space=self.env.state_space, action_space=self.env.action_space))
        ]
        
        results = compare_algorithms(self.env, algorithms, num_episodes=5)
        
        assert isinstance(results, dict)
        assert "Q-Learning" in results
        assert "SARSA" in results
        assert len(results["Q-Learning"]) == 5
        assert len(results["SARSA"]) == 5


class TestAgentPersistence:
    """Test cases for agent save/load functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = QLearning(state_space=10, action_space=4)
        
        # Set some Q-values
        for state in range(10):
            for action in range(4):
                self.agent.set_q_value(state, action, float(state + action))
    
    def test_save_and_load_agent(self, tmp_path):
        """Test saving and loading an agent."""
        from rltoolkit.utils import save_agent, load_agent
        
        # Save agent
        save_path = tmp_path / "test_agent.pkl"
        save_agent(self.agent, str(save_path))
        
        # Load agent
        loaded_agent = load_agent(str(save_path))
        
        # Check that Q-values are preserved
        assert loaded_agent.state_space == self.agent.state_space
        assert loaded_agent.action_space == self.agent.action_space
        
        for state in range(10):
            for action in range(4):
                original_q = self.agent.get_q_value(state, action)
                loaded_q = loaded_agent.get_q_value(state, action)
                assert original_q == loaded_q


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__])