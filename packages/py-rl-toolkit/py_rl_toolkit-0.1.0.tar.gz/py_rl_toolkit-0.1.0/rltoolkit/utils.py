"""
Utility functions for reinforcement learning experiments.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional, Union
from tqdm import tqdm
import time

from .algorithms import QLearning, SARSAAgent, DQNAgent
from .environments import SimpleGridWorld, SimpleMaze
from .policies import Policy, EpsilonGreedyPolicy


def run_episode(env: Union[SimpleGridWorld, SimpleMaze], 
                agent: Union[QLearning, SARSAAgent, DQNAgent],
                policy: Policy,
                max_steps: int = 1000,
                render: bool = False) -> Tuple[float, int]:
    """
    Run a single episode in the environment.
    
    Args:
        env: Environment to interact with
        agent: RL agent
        policy: Action selection policy
        max_steps: Maximum steps per episode
        render: Whether to render environment
        
    Returns:
        Tuple of (total_reward, steps_taken)
    """
    state = env.reset()
    total_reward = 0.0
    steps = 0
    
    while steps < max_steps:
        # Get valid actions for current state
        valid_actions = env.get_valid_actions(state)
        
        # Select action
        action = policy.select_action(agent, state, valid_actions)
        
        # Take action
        next_state, reward, done = env.step(action)
        
        # Update agent (different for different algorithms)
        if isinstance(agent, QLearning):
            agent.update(state, action, reward, next_state, done)
        elif isinstance(agent, SARSAAgent):
            # For SARSA, we need the next action
            next_action = policy.select_action(agent, next_state, env.get_valid_actions(next_state))
            agent.update(state, action, reward, next_state, next_action, done)
        elif isinstance(agent, DQNAgent):
            # Convert state to numpy array if needed
            state_array = np.array(state) if not isinstance(state, np.ndarray) else state
            next_state_array = np.array(next_state) if not isinstance(next_state, np.ndarray) else next_state
            agent.update(state_array, action, reward, next_state_array, done)
        
        # Update state and reward
        state = next_state
        total_reward += reward
        steps += 1
        
        if render:
            print(f"Step {steps}:")
            print(env.render())
            print(f"Action: {action}, Reward: {reward}, Total Reward: {total_reward}")
            print("-" * 30)
        
        if done:
            break
    
    return total_reward, steps


def train_agent(env: Union[SimpleGridWorld, SimpleMaze],
                agent: Union[QLearning, SARSAAgent, DQNAgent],
                policy: Policy,
                num_episodes: int = 1000,
                max_steps_per_episode: int = 1000,
                target_reward: Optional[float] = None,
                verbose: bool = True) -> List[float]:
    """
    Train an RL agent for multiple episodes.
    
    Args:
        env: Environment to train in
        agent: RL agent to train
        policy: Action selection policy
        num_episodes: Number of training episodes
        max_steps_per_episode: Maximum steps per episode
        target_reward: Stop training if this reward is achieved
        verbose: Whether to show progress bar
        
    Returns:
        List of episode rewards
    """
    episode_rewards = []
    
    # Training loop
    episode_range = tqdm(range(num_episodes), desc="Training") if verbose else range(num_episodes)
    
    for episode in episode_range:
        reward, steps = run_episode(env, agent, policy, max_steps_per_episode)
        episode_rewards.append(reward)
        
        # Update progress bar
        if verbose:
            episode_range.set_postfix({
                'Avg Reward': f"{np.mean(episode_rewards[-100:]):.2f}",
                'Last Reward': f"{reward:.2f}",
                'Steps': steps
            })
        
        # Check if target reward is achieved
        if target_reward is not None and len(episode_rewards) >= 100:
            if np.mean(episode_rewards[-100:]) >= target_reward:
                if verbose:
                    print(f"Target reward {target_reward} achieved after {episode + 1} episodes!")
                break
    
    return episode_rewards


def evaluate_agent(env: Union[SimpleGridWorld, SimpleMaze],
                   agent: Union[QLearning, SARSAAgent, DQNAgent],
                   num_episodes: int = 100,
                   max_steps_per_episode: int = 1000,
                   render: bool = False) -> Tuple[float, float, List[float]]:
    """
    Evaluate a trained RL agent.
    
    Args:
        env: Environment to evaluate in
        agent: Trained RL agent
        num_episodes: Number of evaluation episodes
        max_steps_per_episode: Maximum steps per episode
        render: Whether to render environment
        
    Returns:
        Tuple of (mean_reward, std_reward, all_rewards)
    """
    # Use greedy policy for evaluation
    from .policies import GreedyPolicy
    policy = GreedyPolicy()
    
    rewards = []
    
    for episode in range(num_episodes):
        reward, steps = run_episode(env, agent, policy, max_steps_per_episode, render)
        rewards.append(reward)
    
    mean_reward = np.mean(rewards)
    std_reward = np.std(rewards)
    
    return mean_reward, std_reward, rewards


def plot_learning_curve(rewards: List[float], window_size: int = 100,
                         title: str = "Learning Curve", figsize: Tuple[int, int] = (10, 6),
                         save_path: Optional[str] = None) -> None:
    """
    Plot the learning curve of rewards over episodes.
    
    Args:
        rewards: List of episode rewards
        window_size: Size of moving average window
        title: Plot title
        figsize: Figure size
        save_path: Path to save plot (optional)
    """
    plt.figure(figsize=figsize)
    
    # Plot raw rewards
    plt.subplot(2, 1, 1)
    plt.plot(rewards, alpha=0.3, color='blue', label='Episode Reward')
    
    # Plot moving average
    if len(rewards) >= window_size:
        moving_avg = np.convolve(rewards, np.ones(window_size)/window_size, mode='valid')
        plt.plot(range(window_size-1, len(rewards)), moving_avg, 
                color='red', linewidth=2, label=f'{window_size}-Episode Moving Average')
    
    plt.xlabel('Episode')
    plt.ylabel('Reward')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot episode statistics
    plt.subplot(2, 1, 2)
    episodes = list(range(len(rewards)))
    
    # Calculate cumulative average
    cumulative_avg = np.cumsum(rewards) / np.arange(1, len(rewards) + 1)
    plt.plot(episodes, cumulative_avg, color='green', linewidth=2, label='Cumulative Average')
    
    plt.xlabel('Episode')
    plt.ylabel('Cumulative Average Reward')
    plt.title('Cumulative Average Reward')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def compare_algorithms(env: Union[SimpleGridWorld, SimpleMaze],
                      algorithms: List[Tuple[str, Union[QLearning, SARSAAgent, DQNAgent]]],
                      num_episodes: int = 1000,
                      max_steps_per_episode: int = 1000,
                      verbose: bool = True) -> dict:
    """
    Compare different RL algorithms on the same environment.
    
    Args:
        env: Environment to test in
        algorithms: List of (algorithm_name, agent) tuples
        num_episodes: Number of episodes per algorithm
        max_steps_per_episode: Maximum steps per episode
        verbose: Whether to show progress
        
    Returns:
        Dictionary with algorithm names as keys and reward lists as values
    """
    results = {}
    
    for alg_name, agent in algorithms:
        if verbose:
            print(f"Training {alg_name}...")
        
        # Use epsilon-greedy policy for training
        policy = EpsilonGreedyPolicy(epsilon=0.1, epsilon_decay=0.995, epsilon_min=0.01)
        
        # Train agent
        rewards = train_agent(env, agent, policy, num_episodes, 
                            max_steps_per_episode, verbose=verbose)
        
        results[alg_name] = rewards
        
        if verbose:
            print(f"{alg_name} completed. Final average reward: {np.mean(rewards[-100:]):.2f}")
    
    return results


def plot_comparison(results: dict, window_size: int = 100, 
                   title: str = "Algorithm Comparison", figsize: Tuple[int, int] = (12, 6),
                   save_path: Optional[str] = None) -> None:
    """
    Plot comparison of different algorithms.
    
    Args:
        results: Dictionary with algorithm names as keys and reward lists as values
        window_size: Size of moving average window
        title: Plot title
        figsize: Figure size
        save_path: Path to save plot (optional)
    """
    plt.figure(figsize=figsize)
    
    for alg_name, rewards in results.items():
        # Plot moving average
        if len(rewards) >= window_size:
            moving_avg = np.convolve(rewards, np.ones(window_size)/window_size, mode='valid')
            plt.plot(range(window_size-1, len(rewards)), moving_avg, 
                    linewidth=2, label=f'{alg_name}')
        else:
            plt.plot(rewards, alpha=0.7, label=f'{alg_name}')
    
    plt.xlabel('Episode')
    plt.ylabel('Reward')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def save_agent(agent: Union[QLearning, SARSAAgent, DQNAgent], filepath: str) -> None:
    """
    Save a trained agent to file.
    
    Args:
        agent: Trained RL agent
        filepath: Path to save the agent
    """
    import pickle
    
    with open(filepath, 'wb') as f:
        pickle.dump(agent, f)
    
    print(f"Agent saved to {filepath}")


def load_agent(filepath: str) -> Union[QLearning, SARSAAgent, DQNAgent]:
    """
    Load a trained agent from file.
    
    Args:
        filepath: Path to load the agent from
        
    Returns:
        Loaded RL agent
    """
    import pickle
    
    with open(filepath, 'rb') as f:
        agent = pickle.load(f)
    
    print(f"Agent loaded from {filepath}")
    return agent