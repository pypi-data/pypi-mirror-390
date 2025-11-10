"""
Simple environments for reinforcement learning experiments.
"""

import numpy as np
from typing import Tuple, List, Optional


class SimpleGridWorld:
    """
    Simple grid world environment for reinforcement learning.
    
    A basic grid where an agent can move up, down, left, or right
    to reach a goal while avoiding obstacles.
    """
    
    def __init__(self, size: int = 5, start_pos: Tuple[int, int] = (0, 0),
                 goal_pos: Tuple[int, int] = None, obstacles: List[Tuple[int, int]] = None,
                 reward_goal: float = 10.0, reward_step: float = -0.1, reward_obstacle: float = -1.0):
        """
        Initialize grid world environment.
        
        Args:
            size: Size of the square grid
            start_pos: Starting position (row, col)
            goal_pos: Goal position (row, col)
            obstacles: List of obstacle positions
            reward_goal: Reward for reaching goal
            reward_step: Reward for each step
            reward_obstacle: Reward for hitting obstacle
        """
        self.size = size
        self.start_pos = start_pos
        self.goal_pos = goal_pos if goal_pos else (size - 1, size - 1)
        self.obstacles = obstacles if obstacles else []
        self.reward_goal = reward_goal
        self.reward_step = reward_step
        self.reward_obstacle = reward_obstacle
        
        # State and action spaces
        self.state_space = size * size
        self.action_space = 4  # up, down, left, right
        
        # Action mapping
        self.actions = {
            0: (-1, 0),  # up
            1: (1, 0),   # down
            2: (0, -1),  # left
            3: (0, 1)    # right
        }
        
        self.reset()
        
    def reset(self) -> int:
        """Reset environment to initial state."""
        self.agent_pos = list(self.start_pos)
        return self._pos_to_state(self.agent_pos)
    
    def _pos_to_state(self, pos: List[int]) -> int:
        """Convert position to state index."""
        return pos[0] * self.size + pos[1]
    
    def _state_to_pos(self, state: int) -> List[int]:
        """Convert state index to position."""
        return [state // self.size, state % self.size]
    
    def _is_valid_pos(self, pos: List[int]) -> bool:
        """Check if position is within grid bounds."""
        return 0 <= pos[0] < self.size and 0 <= pos[1] < self.size
    
    def _is_obstacle(self, pos: List[int]) -> bool:
        """Check if position has an obstacle."""
        return tuple(pos) in self.obstacles
    
    def _is_goal(self, pos: List[int]) -> bool:
        """Check if position is the goal."""
        return tuple(pos) == self.goal_pos
    
    def step(self, action: int) -> Tuple[int, float, bool]:
        """
        Take action in environment.
        
        Args:
            action: Action to take (0=up, 1=down, 2=left, 3=right)
            
        Returns:
            Tuple of (next_state, reward, done)
        """
        # Get action delta
        delta = self.actions[action]
        new_pos = [self.agent_pos[0] + delta[0], self.agent_pos[1] + delta[1]]
        
        # Check bounds
        if not self._is_valid_pos(new_pos):
            # Stay in current position if invalid move
            reward = self.reward_obstacle
            done = False
        elif self._is_obstacle(new_pos):
            # Hit obstacle
            reward = self.reward_obstacle
            done = False
            # Optionally, don't move when hitting obstacle
            # new_pos = self.agent_pos
        elif self._is_goal(new_pos):
            # Reached goal
            reward = self.reward_goal
            done = True
            self.agent_pos = new_pos
        else:
            # Valid move
            reward = self.reward_step
            done = False
            self.agent_pos = new_pos
        
        next_state = self._pos_to_state(self.agent_pos)
        return next_state, reward, done
    
    def render(self) -> str:
        """Render the current state of the grid."""
        grid = [['.' for _ in range(self.size)] for _ in range(self.size)]
        
        # Place obstacles
        for obs in self.obstacles:
            grid[obs[0]][obs[1]] = 'X'
        
        # Place goal
        grid[self.goal_pos[0]][self.goal_pos[1]] = 'G'
        
        # Place agent
        grid[self.agent_pos[0]][self.agent_pos[1]] = 'A'
        
        return '\n'.join([' '.join(row) for row in grid])
    
    def get_valid_actions(self, state: int) -> List[int]:
        """Get list of valid actions for a given state."""
        pos = self._state_to_pos(state)
        valid_actions = []
        
        for action, delta in self.actions.items():
            new_pos = [pos[0] + delta[0], pos[1] + delta[1]]
            if self._is_valid_pos(new_pos):
                valid_actions.append(action)
        
        return valid_actions


class SimpleMaze:
    """
    Simple maze environment for reinforcement learning.
    
    A maze with walls, start position, and goal position.
    """
    
    def __init__(self, maze_map: List[List[int]], start_pos: Tuple[int, int] = (0, 0),
                 goal_pos: Tuple[int, int] = None, reward_goal: float = 10.0,
                 reward_step: float = -0.1, reward_wall: float = -1.0):
        """
        Initialize maze environment.
        
        Args:
            maze_map: 2D array where 0=empty, 1=wall
            start_pos: Starting position (row, col)
            goal_pos: Goal position (row, col)
            reward_goal: Reward for reaching goal
            reward_step: Reward for each step
            reward_wall: Reward for hitting wall
        """
        self.maze_map = np.array(maze_map)
        self.rows, self.cols = self.maze_map.shape
        self.start_pos = start_pos
        self.goal_pos = goal_pos if goal_pos else (self.rows - 1, self.cols - 1)
        self.reward_goal = reward_goal
        self.reward_step = reward_step
        self.reward_wall = reward_wall
        
        # State and action spaces
        self.state_space = self.rows * self.cols
        self.action_space = 4  # up, down, left, right
        
        # Action mapping
        self.actions = {
            0: (-1, 0),  # up
            1: (1, 0),   # down
            2: (0, -1),  # left
            3: (0, 1)    # right
        }
        
        self.reset()
        
    def reset(self) -> int:
        """Reset environment to initial state."""
        self.agent_pos = list(self.start_pos)
        return self._pos_to_state(self.agent_pos)
    
    def _pos_to_state(self, pos: List[int]) -> int:
        """Convert position to state index."""
        return pos[0] * self.cols + pos[1]
    
    def _state_to_pos(self, state: int) -> List[int]:
        """Convert state index to position."""
        return [state // self.cols, state % self.cols]
    
    def _is_valid_pos(self, pos: List[int]) -> bool:
        """Check if position is within maze bounds."""
        return 0 <= pos[0] < self.rows and 0 <= pos[1] < self.cols
    
    def _is_wall(self, pos: List[int]) -> bool:
        """Check if position has a wall."""
        return self.maze_map[pos[0], pos[1]] == 1
    
    def _is_goal(self, pos: List[int]) -> bool:
        """Check if position is the goal."""
        return tuple(pos) == self.goal_pos
    
    def step(self, action: int) -> Tuple[int, float, bool]:
        """
        Take action in environment.
        
        Args:
            action: Action to take (0=up, 1=down, 2=left, 3=right)
            
        Returns:
            Tuple of (next_state, reward, done)
        """
        # Get action delta
        delta = self.actions[action]
        new_pos = [self.agent_pos[0] + delta[0], self.agent_pos[1] + delta[1]]
        
        # Check bounds and walls
        if not self._is_valid_pos(new_pos) or self._is_wall(new_pos):
            # Invalid move (hit wall or boundary)
            reward = self.reward_wall
            done = False
        elif self._is_goal(new_pos):
            # Reached goal
            reward = self.reward_goal
            done = True
            self.agent_pos = new_pos
        else:
            # Valid move
            reward = self.reward_step
            done = False
            self.agent_pos = new_pos
        
        next_state = self._pos_to_state(self.agent_pos)
        return next_state, reward, done
    
    def render(self) -> str:
        """Render the current state of the maze."""
        maze_str = ""
        for i in range(self.rows):
            row = ""
            for j in range(self.cols):
                if [i, j] == self.agent_pos:
                    row += "A "
                elif (i, j) == self.goal_pos:
                    row += "G "
                elif self.maze_map[i, j] == 1:
                    row += "# "
                else:
                    row += ". "
            maze_str += row + "\n"
        return maze_str.strip()
    
    def get_valid_actions(self, state: int) -> List[int]:
        """Get list of valid actions for a given state."""
        pos = self._state_to_pos(state)
        valid_actions = []
        
        for action, delta in self.actions.items():
            new_pos = [pos[0] + delta[0], pos[1] + delta[1]]
            if self._is_valid_pos(new_pos) and not self._is_wall(new_pos):
                valid_actions.append(action)
        
        return valid_actions