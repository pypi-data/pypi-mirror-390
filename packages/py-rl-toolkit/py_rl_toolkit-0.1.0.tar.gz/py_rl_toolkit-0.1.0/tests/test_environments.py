"""
Test cases for reinforcement learning environments.
"""

import pytest
import numpy as np
import sys
import os

# Add the parent directory to the path so we can import rltoolkit
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rltoolkit.environments import SimpleGridWorld, SimpleMaze


class TestSimpleGridWorld:
    """Test cases for SimpleGridWorld environment."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.env = SimpleGridWorld(size=5)
    
    def test_initialization(self):
        """Test environment initialization."""
        assert self.env.size == 5
        assert self.env.state_space == 25  # 5x5 grid
        assert self.env.action_space == 4  # up, down, left, right
        assert self.env.start_pos == (0, 0)
        assert self.env.goal_pos == (4, 4)
    
    def test_reset(self):
        """Test environment reset."""
        # Take some steps to change state
        self.env.step(1)  # down
        self.env.step(3)  # right
        
        # Reset should return to start position
        initial_state = self.env.reset()
        assert initial_state == 0  # (0,0) -> state 0
        assert self.env.agent_pos == [0, 0]
    
    def test_step_valid_actions(self):
        """Test valid step actions."""
        # Start at (0,0)
        self.env.reset()
        
        # Test moving down
        next_state, reward, done = self.env.step(1)  # down
        assert next_state == 5  # (1,0) -> state 5
        assert self.env.agent_pos == [1, 0]
        assert reward == self.env.reward_step
        assert not done
        
        # Test moving right
        next_state, reward, done = self.env.step(3)  # right
        assert next_state == 6  # (1,1) -> state 6
        assert self.env.agent_pos == [1, 1]
        assert reward == self.env.reward_step
        assert not done
    
    def test_step_boundary_conditions(self):
        """Test stepping at boundaries."""
        # Move to corner (0,4)
        self.env.agent_pos = [0, 4]
        
        # Try to move right (should stay in place)
        next_state, reward, done = self.env.step(3)  # right
        assert next_state == 4  # (0,4) -> state 4
        assert self.env.agent_pos == [0, 4]
        assert reward == self.env.reward_obstacle
        assert not done
        
        # Try to move up (should stay in place)
        next_state, reward, done = self.env.step(0)  # up
        assert next_state == 4  # (0,4) -> state 4
        assert self.env.agent_pos == [0, 4]
        assert reward == self.env.reward_obstacle
        assert not done
    
    def test_reach_goal(self):
        """Test reaching the goal."""
        # Move agent to position adjacent to goal
        self.env.agent_pos = [3, 4]
        
        # Move down to reach goal
        next_state, reward, done = self.env.step(1)  # down
        assert next_state == 24  # (4,4) -> state 24
        assert self.env.agent_pos == [4, 4]
        assert reward == self.env.reward_goal
        assert done
    
    def test_obstacles(self):
        """Test obstacle functionality."""
        # Create environment with obstacles
        obstacles = [(1, 1), (2, 2), (3, 3)]
        env_with_obstacles = SimpleGridWorld(size=5, obstacles=obstacles)
        
        # Move to position adjacent to obstacle
        env_with_obstacles.agent_pos = [1, 0]
        
        # Try to move right into obstacle
        next_state, reward, done = env_with_obstacles.step(3)  # right
        assert env_with_obstacles.agent_pos == [1, 0]  # Should not move
        assert reward == env_with_obstacles.reward_obstacle
        assert not done
    
    def test_get_valid_actions(self):
        """Test getting valid actions for different positions."""
        # Corner position (0,0)
        self.env.reset()
        valid_actions = self.env.get_valid_actions(0)
        assert set(valid_actions) == {1, 3}  # down, right
        
        # Edge position (0,2)
        self.env.agent_pos = [0, 2]
        valid_actions = self.env.get_valid_actions(2)
        assert set(valid_actions) == {1, 2, 3}  # down, left, right
        
        # Center position (2,2)
        self.env.agent_pos = [2, 2]
        valid_actions = self.env.get_valid_actions(12)
        assert set(valid_actions) == {0, 1, 2, 3}  # all actions
    
    def test_render(self):
        """Test environment rendering."""
        self.env.reset()
        render_output = self.env.render()
        
        # Check that render output contains expected elements
        lines = render_output.split('\n')
        assert len(lines) == self.env.size
        assert 'A' in render_output  # Agent should be present
        assert 'G' in render_output  # Goal should be present


class TestSimpleMaze:
    """Test cases for SimpleMaze environment."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Simple 3x3 maze with some walls
        maze_map = [
            [0, 0, 0],
            [0, 1, 0],  # Wall in center
            [0, 0, 0]
        ]
        self.env = SimpleMaze(maze_map)
    
    def test_initialization(self):
        """Test environment initialization."""
        assert self.env.rows == 3
        assert self.env.cols == 3
        assert self.env.state_space == 9  # 3x3 maze
        assert self.env.action_space == 4
        assert self.env.start_pos == (0, 0)
        assert self.env.goal_pos == (2, 2)  # Default goal position
    
    def test_reset(self):
        """Test environment reset."""
        # Take some steps
        self.env.step(1)  # down
        
        # Reset should return to start
        initial_state = self.env.reset()
        assert initial_state == 0  # (0,0) -> state 0
        assert self.env.agent_pos == [0, 0]
    
    def test_step_with_walls(self):
        """Test stepping with walls in the maze."""
        # Move to position adjacent to wall
        self.env.agent_pos = [0, 1]
        
        # Try to move down into wall
        next_state, reward, done = self.env.step(1)  # down
        assert self.env.agent_pos == [0, 1]  # Should not move
        assert reward == self.env.reward_wall
        assert not done
    
    def test_step_valid_moves(self):
        """Test valid moves in maze."""
        # Start at (0,0)
        self.env.reset()
        
        # Move right (valid)
        next_state, reward, done = self.env.step(3)  # right
        assert next_state == 1  # (0,1) -> state 1
        assert self.env.agent_pos == [0, 1]
        assert reward == self.env.reward_step
        assert not done
        
        # Move down (should hit wall at (1,1))
        next_state, reward, done = self.env.step(1)  # down
        # Position should not change when hitting wall
        assert self.env.agent_pos == [0, 1]  # Should not move into wall
        assert reward == self.env.reward_wall
        assert not done
    
    def test_reach_goal_maze(self):
        """Test reaching goal in maze."""
        # Move agent to position adjacent to goal
        self.env.agent_pos = [1, 2]
        
        # Move down to reach goal
        next_state, reward, done = self.env.step(1)  # down
        assert next_state == 8  # (2,2) -> state 8
        assert self.env.agent_pos == [2, 2]
        assert reward == self.env.reward_goal
        assert done
    
    def test_get_valid_actions_maze(self):
        """Test getting valid actions in maze."""
        # Position (0,0)
        self.env.reset()
        valid_actions = self.env.get_valid_actions(0)
        assert set(valid_actions) == {1, 3}  # down, right (can't go up/left or into wall)
        
        # Position (0,1)
        self.env.agent_pos = [0, 1]
        valid_actions = self.env.get_valid_actions(1)
        assert set(valid_actions) == {2, 3}  # left, right (can't go up/down into walls)
    
    def test_render_maze(self):
        """Test maze rendering."""
        self.env.reset()
        render_output = self.env.render()
        
        # Check render output
        lines = render_output.split('\n')
        assert len(lines) == self.env.rows
        assert 'A' in render_output  # Agent
        assert 'G' in render_output  # Goal
        assert '#' in render_output  # Wall


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__])