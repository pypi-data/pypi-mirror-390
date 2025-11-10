# PyPiRL - Python Reinforcement Learning Toolkit

A comprehensive, easy-to-use Python toolkit for reinforcement learning research and education. Built with clean APIs, extensive documentation, and thorough testing.

## 🚀 Features

### Core Algorithms
- **Q-Learning**: Tabular off-policy value-based algorithm
- **SARSA**: Tabular on-policy value-based algorithm  
- **DQN**: Deep Q-Network with PyTorch neural networks

### Environments
- **SimpleGridWorld**: Configurable grid environment with obstacles and goals
- **SimpleMaze**: Customizable maze environment with walls

### Policies
- **RandomPolicy**: Uniform random action selection
- **GreedyPolicy**: Always selects best action
- **EpsilonGreedyPolicy**: Balances exploration/exploitation with decay
- **SoftmaxPolicy**: Boltzmann exploration with temperature

### Utility Functions
- **Training**: `train_agent()` with progress tracking and early stopping
- **Evaluation**: `evaluate_agent()` with performance metrics
- **Visualization**: `plot_learning_curve()` and `plot_comparison()`
- **Persistence**: `save_agent()` and `load_agent()` for model saving
- **Episode Running**: `run_episode()` for single episode execution
- **Algorithm Comparison**: `compare_algorithms()` for benchmarking

## 📦 Installation

### From PyPI (when published)
```bash
pip install py-rl-toolkit
```

### From Source
```bash
git clone https://github.com/Nits1627/PyPiRL.git
cd PyPiRL
pip install -e .
```

### From Wheel
```bash
pip install dist/rltoolkit-0.1.0-py3-none-any.whl
```

## 🎯 Quick Start

```python
from rltoolkit import QLearning, SimpleGridWorld, EpsilonGreedyPolicy

# Create environment and agent
env = SimpleGridWorld(size=5)
agent = QLearning(env.state_space_size, env.action_space_size)
policy = EpsilonGreedyPolicy(agent, epsilon=0.1)

# Train the agent
from rltoolkit import train_agent
rewards = train_agent(env, agent, policy, episodes=100)

# Evaluate performance
from rltoolkit import evaluate_agent
avg_reward = evaluate_agent(env, agent, policy, episodes=10)
print(f"Average reward: {avg_reward}")
```

## 📚 Examples

See `examples.py` for comprehensive usage examples including:
- Training different algorithms
- Comparing algorithm performance
- Visualizing learning curves
- Custom environment creation

## 🧪 Testing

Run the comprehensive test suite:
```bash
python -m pytest tests/ -v
```

## 📖 Documentation

Detailed documentation is available in `docs.md` including:
- API reference for all classes and functions
- Algorithm explanations
- Environment specifications
- Policy implementations

## 🔧 Requirements

- Python ≥ 3.7
- NumPy
- Matplotlib
- PyTorch (for DQN)
- TQDM (for progress bars)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📊 Package Status

- ✅ All 58 tests passing
- ✅ Package successfully built
- ✅ Ready for PyPI publication
- ✅ GitHub Actions workflow configured for automated publishing