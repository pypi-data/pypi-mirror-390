# RL Toolkit Documentation

## Overview

The RL Toolkit is a comprehensive Python library for reinforcement learning research and education. It provides implementations of popular RL algorithms, environments, and utilities for training, evaluation, and visualization.

## Installation

### From PyPI (Recommended)

```bash
pip install rltoolkit
```

### From Source

```bash
git clone https://github.com/yourusername/rltoolkit.git
cd rltoolkit
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/yourusername/rltoolkit.git
cd rltoolkit
pip install -e .[dev]
```

## Quick Start

### Basic Q-Learning Example

```python
from rltoolkit.algorithms import QLearning
from rltoolkit.environments import SimpleGridWorld
from rltoolkit.policies import EpsilonGreedyPolicy
from rltoolkit.utils import train_agent, evaluate_agent, plot_learning_curve

# Create environment
env = SimpleGridWorld(size=5)

# Create Q-Learning agent
agent = QLearning(state_space=env.state_space, action_space=env.action_space)

# Create epsilon-greedy policy
policy = EpsilonGreedyPolicy(epsilon=0.1)

# Train the agent
rewards = train_agent(env, agent, policy, num_episodes=1000)

# Plot learning curve
plot_learning_curve(rewards)

# Evaluate the trained agent
mean_reward, std_reward, _ = evaluate_agent(env, agent, num_episodes=100)
print(f"Average reward: {mean_reward:.2f} ± {std_reward:.2f}")
```

## Core Components

### Algorithms

#### Q-Learning

Q-Learning is a model-free reinforcement learning algorithm that learns the optimal action-value function Q*(s,a).

```python
from rltoolkit.algorithms import QLearning

# Create Q-Learning agent
agent = QLearning(
    state_space=env.state_space,
    action_space=env.action_space,
    learning_rate=0.1,
    discount_factor=0.99,
    epsilon=0.1
)
```

**Parameters:**
- `state_space`: Number of states
- `action_space`: Number of actions
- `learning_rate`: Learning rate (default: 0.1)
- `discount_factor`: Discount factor for future rewards (default: 0.99)
- `epsilon`: Exploration rate (default: 0.1)

#### SARSA

SARSA (State-Action-Reward-State-Action) is an on-policy reinforcement learning algorithm.

```python
from rltoolkit.algorithms import SARSAAgent

# Create SARSA agent
agent = SARSAAgent(
    state_space=env.state_space,
    action_space=env.action_space,
    learning_rate=0.1,
    discount_factor=0.99,
    epsilon=0.1
)
```

#### Deep Q-Network (DQN)

DQN uses neural networks to approximate the Q-function, suitable for large state spaces.

```python
from rltoolkit.algorithms import DQNAgent

# Create DQN agent
agent = DQNAgent(
    state_space=env.state_space,
    action_space=env.action_space,
    learning_rate=0.001,
    discount_factor=0.99,
    epsilon=0.1,
    hidden_size=64
)
```

### Environments

#### Simple Grid World

A basic grid world environment for testing RL algorithms.

```python
from rltoolkit.environments import SimpleGridWorld

# Create 5x5 grid world
env = SimpleGridWorld(size=5)

# Create custom grid world with specific start and goal positions
env = SimpleGridWorld(
    size=5,
    start_pos=(0, 0),
    goal_pos=(4, 4),
    obstacles=[(1, 1), (2, 2)]
)
```

#### Simple Maze

A maze environment with walls and obstacles.

```python
from rltoolkit.environments import SimpleMaze

# Create maze from 2D array
maze = [
    [0, 0, 1, 0, 0],
    [0, 1, 1, 0, 1],
    [0, 0, 0, 0, 0],
    [1, 1, 0, 1, 0],
    [0, 0, 0, 0, 0]
]
env = SimpleMaze(maze)
```

### Policies

#### Epsilon-Greedy Policy

Balances exploration and exploitation using epsilon parameter.

```python
from rltoolkit.policies import EpsilonGreedyPolicy

# Create epsilon-greedy policy
policy = EpsilonGreedyPolicy(
    epsilon=0.1,
    decay_rate=0.99,  # Optional: decay epsilon over time
    min_epsilon=0.01  # Optional: minimum epsilon value
)
```

#### Softmax Policy (Boltzmann Exploration)

Uses temperature parameter for probabilistic action selection.

```python
from rltoolkit.policies import SoftmaxPolicy

# Create softmax policy
policy = SoftmaxPolicy(
    temperature=1.0,
    decay_rate=0.99,  # Optional: decay temperature over time
    min_temperature=0.1  # Optional: minimum temperature value
)
```

#### Greedy Policy

Always selects the action with the highest Q-value.

```python
from rltoolkit.policies import GreedyPolicy

# Create greedy policy
policy = GreedyPolicy()
```

#### Random Policy

Selects actions uniformly at random.

```python
from rltoolkit.policies import RandomPolicy

# Create random policy
policy = RandomPolicy()
```

### Utilities

#### Training Agents

```python
from rltoolkit.utils import train_agent

# Train agent for specified number of episodes
rewards = train_agent(
    env=env,
    agent=agent,
    policy=policy,
    num_episodes=1000,
    target_reward=10.0,  # Optional: stop when target reward is reached
    max_steps_per_episode=100  # Optional: maximum steps per episode
)
```

#### Evaluating Agents

```python
from rltoolkit.utils import evaluate_agent

# Evaluate agent performance
mean_reward, std_reward, rewards = evaluate_agent(
    env=env,
    agent=agent,
    num_episodes=100,
    render=True  # Optional: render episodes
)
```

#### Plotting Learning Curves

```python
from rltoolkit.utils import plot_learning_curve

# Plot learning curve with moving average
plot_learning_curve(
    rewards=rewards,
    window_size=50,  # Moving average window size
    title="Learning Curve",
    save_path="learning_curve.png"  # Optional: save plot to file
)
```

#### Comparing Algorithms

```python
from rltoolkit.utils import compare_algorithms

# Compare multiple algorithms
algorithms = [
    ("Q-Learning", QLearningAgent(...)),
    ("SARSA", SARSAAgent(...)),
    ("DQN", DQNAgent(...))
]

results = compare_algorithms(
    env=env,
    algorithms=algorithms,
    num_episodes=1000,
    num_runs=5  # Number of runs for statistical significance
)
```

#### Saving and Loading Agents

```python
from rltoolkit.utils import save_agent, load_agent

# Save trained agent
save_agent(agent, "trained_agent.pkl")

# Load saved agent
loaded_agent = load_agent("trained_agent.pkl")
```

## Advanced Usage

### Custom Environments

Create custom environments by implementing the required interface:

```python
class CustomEnvironment:
    def __init__(self):
        self.state_space = 10  # Number of states
        self.action_space = 4  # Number of actions
        
    def reset(self):
        # Reset environment to initial state
        self.state = 0
        return self.state
        
    def step(self, action):
        # Execute action and return (next_state, reward, done, info)
        next_state = self.state + action
        reward = -1.0 if next_state != 9 else 10.0
        done = next_state == 9
        self.state = next_state
        return next_state, reward, done, {}
        
    def render(self):
        # Optional: render current state
        print(f"Current state: {self.state}")
```

### Custom Policies

Implement custom policies by inheriting from the base Policy class:

```python
from rltoolkit.policies import Policy

class CustomPolicy(Policy):
    def __init__(self, custom_param=0.5):
        super().__init__()
        self.custom_param = custom_param
        
    def select_action(self, q_values, state):
        # Implement custom action selection logic
        if np.random.random() < self.custom_param:
            return np.random.randint(len(q_values))
        else:
            return np.argmax(q_values)
            
    def update(self, episode):
        # Optional: update policy parameters
        pass
```

### Hyperparameter Tuning

Example of hyperparameter tuning for Q-Learning:

```python
import numpy as np
from rltoolkit.utils import train_agent, evaluate_agent

def tune_hyperparameters(env, learning_rates, epsilons, num_episodes=500):
    best_params = None
    best_score = -np.inf
    
    for lr in learning_rates:
        for eps in epsilons:
            # Create agent with current hyperparameters
            agent = QLearning(
                state_space=env.state_space,
                action_space=env.action_space,
                learning_rate=lr,
                epsilon=eps
            )
            
            # Train agent
            train_agent(env, agent, policy, num_episodes=num_episodes)
            
            # Evaluate performance
            mean_reward, _, _ = evaluate_agent(env, agent, num_episodes=100)
            
            if mean_reward > best_score:
                best_score = mean_reward
                best_params = (lr, eps)
                
            print(f"LR: {lr}, Epsilon: {eps}, Score: {mean_reward:.2f}")
    
    return best_params, best_score

# Run hyperparameter tuning
learning_rates = [0.1, 0.3, 0.5]
epsilons = [0.1, 0.3, 0.5]
best_params, best_score = tune_hyperparameters(env, learning_rates, epsilons)
print(f"Best parameters: LR={best_params[0]}, Epsilon={best_params[1]}")
print(f"Best score: {best_score:.2f}")
```

## Examples

See the `examples.py` file for comprehensive examples including:

1. Basic Q-Learning on grid world
2. Comparing SARSA and Q-Learning
3. Maze navigation
4. Hyperparameter tuning
5. Custom environments

Run the examples:

```bash
python examples.py
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_algorithms.py

# Run with coverage
pytest tests/ --cov=rltoolkit
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass (`pytest tests/`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Setup

```bash
git clone https://github.com/yourusername/rltoolkit.git
cd rltoolkit
pip install -e .[dev]
```

### Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Add docstrings to all public functions and classes
- Write comprehensive tests for new features

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this library in your research, please cite:

```bibtex
@software{rltoolkit,
  title={RL Toolkit: A Comprehensive Reinforcement Learning Library},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/rltoolkit}
}
```

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation and examples
- Contact: your.email@example.com

## Roadmap

- [ ] Multi-agent reinforcement learning
- [ ] Policy gradient methods (REINFORCE, Actor-Critic)
- [ ] Advanced DQN variants (Double DQN, Dueling DQN)
- [ ] Integration with OpenAI Gym
- [ ] Distributed training support
- [ ] Web-based visualization tools