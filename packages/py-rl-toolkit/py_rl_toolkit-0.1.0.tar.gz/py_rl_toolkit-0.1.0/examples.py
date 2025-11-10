"""
Example usage of the RL Toolkit.

This example demonstrates how to use the RL Toolkit to train and evaluate
reinforcement learning agents on different environments.
"""

import numpy as np
import matplotlib.pyplot as plt
from rltoolkit.algorithms import QLearning, SARSAAgent
from rltoolkit.environments import SimpleGridWorld, SimpleMaze
from rltoolkit.policies import EpsilonGreedyPolicy, SoftmaxPolicy
from rltoolkit.utils import train_agent, evaluate_agent, plot_learning_curve, compare_algorithms


def example_1_basic_q_learning():
    """Example 1: Basic Q-Learning on a simple grid world."""
    print("=== Example 1: Basic Q-Learning ===")
    
    # Create environment
    env = SimpleGridWorld(size=5)
    
    # Create Q-Learning agent
    agent = QLearning(state_space=env.state_space, action_space=env.action_space)
    
    # Create epsilon-greedy policy
    policy = EpsilonGreedyPolicy(epsilon=0.1, decay_rate=0.99)
    
    # Train the agent
    print("Training Q-Learning agent...")
    rewards = train_agent(env, agent, policy, num_episodes=1000)
    
    # Plot learning curve
    plot_learning_curve(rewards, window_size=50, title="Q-Learning on Grid World")
    
    # Evaluate the trained agent
    mean_reward, std_reward, _ = evaluate_agent(env, agent, num_episodes=100, render=False)
    print(f"Average reward after training: {mean_reward:.2f} ± {std_reward:.2f}")
    
    return agent, rewards


def example_2_sarsa_vs_q_learning():
    """Example 2: Comparing SARSA and Q-Learning."""
    print("\n=== Example 2: SARSA vs Q-Learning ===")
    
    # Create environment
    env = SimpleGridWorld(size=5)
    
    # Create agents
    q_learning_agent = QLearning(state_space=env.state_space, action_space=env.action_space)
    sarsa_agent = SARSAAgent(state_space=env.state_space, action_space=env.action_space)
    
    # Create policies
    policy = EpsilonGreedyPolicy(epsilon=0.1, decay_rate=0.99)
    
    # Compare algorithms
    algorithms = [
        ("Q-Learning", q_learning_agent),
        ("SARSA", sarsa_agent)
    ]
    
    print("Comparing Q-Learning and SARSA...")
    results = compare_algorithms(env, algorithms, num_episodes=1000, policy=policy)
    
    # Plot comparison
    plt.figure(figsize=(10, 6))
    for name, rewards in results.items():
        # Calculate moving average
        window_size = 50
        moving_avg = np.convolve(rewards, np.ones(window_size)/window_size, mode='valid')
        plt.plot(moving_avg, label=name)
    
    plt.xlabel('Episode')
    plt.ylabel('Moving Average Reward')
    plt.title('Q-Learning vs SARSA Performance')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    return results


def example_3_maze_navigation():
    """Example 3: Navigation in a maze environment."""
    print("\n=== Example 3: Maze Navigation ===")
    
    # Create maze environment
    maze = [
        [0, 0, 1, 0, 0],
        [0, 1, 1, 0, 1],
        [0, 0, 0, 0, 0],
        [1, 1, 0, 1, 0],
        [0, 0, 0, 0, 0]
    ]
    env = SimpleMaze(maze)
    
    # Create Q-Learning agent
    agent = QLearning(state_space=env.state_space, action_space=env.action_space)
    
    # Create policy (use softmax for more exploration)
    policy = SoftmaxPolicy(temperature=1.0, decay_rate=0.99)
    
    # Train the agent
    print("Training agent on maze...")
    rewards = train_agent(env, agent, policy, num_episodes=2000)
    
    # Plot learning curve
    plot_learning_curve(rewards, window_size=100, title="Q-Learning on Maze")
    
    # Evaluate the trained agent
    mean_reward, std_reward, _ = evaluate_agent(env, agent, num_episodes=100, render=False)
    print(f"Average reward after training: {mean_reward:.2f} ± {std_reward:.2f}")
    
    # Show a sample episode
    print("\nSample episode:")
    evaluate_agent(env, agent, num_episodes=1, render=True)
    
    return agent, rewards


def example_4_hyperparameter_tuning():
    """Example 4: Hyperparameter tuning for Q-Learning."""
    print("\n=== Example 4: Hyperparameter Tuning ===")
    
    # Create environment
    env = SimpleGridWorld(size=4)
    
    # Test different learning rates
    learning_rates = [0.1, 0.3, 0.5, 0.7]
    results = {}
    
    for lr in learning_rates:
        print(f"Testing learning rate: {lr}")
        
        # Create agent with specific learning rate
        agent = QLearning(state_space=env.state_space, action_space=env.action_space, 
                         learning_rate=lr)
        policy = EpsilonGreedyPolicy(epsilon=0.1, decay_rate=0.99)
        
        # Train agent
        rewards = train_agent(env, agent, policy, num_episodes=500)
        
        # Evaluate final performance
        mean_reward, _, _ = evaluate_agent(env, agent, num_episodes=100, render=False)
        results[lr] = mean_reward
        
        print(f"  Average reward: {mean_reward:.2f}")
    
    # Plot results
    plt.figure(figsize=(10, 6))
    plt.bar(results.keys(), results.values())
    plt.xlabel('Learning Rate')
    plt.ylabel('Average Reward')
    plt.title('Q-Learning Performance vs Learning Rate')
    plt.grid(True)
    plt.show()
    
    return results


def example_5_custom_environment():
    """Example 5: Creating a custom environment."""
    print("\n=== Example 5: Custom Environment ===")
    
    class CustomEnvironment:
        """A simple custom environment for demonstration."""
        
        def __init__(self):
            self.state = 0
            self.state_space = 3  # 3 states: 0, 1, 2
            self.action_space = 2  # 2 actions: 0 (left), 1 (right)
            self.goal_state = 2
            self.start_state = 0
            
        def reset(self):
            self.state = self.start_state
            return self.state
            
        def step(self, action):
            # Simple dynamics: move left or right
            if action == 0:  # left
                self.state = max(0, self.state - 1)
            else:  # right
                self.state = min(2, self.state + 1)
            
            # Reward structure
            if self.state == self.goal_state:
                reward = 10.0
                done = True
            else:
                reward = -1.0
                done = False
                
            return self.state, reward, done, {}
            
        def render(self):
            print(f"State: {self.state}")
    
    # Create custom environment
    env = CustomEnvironment()
    
    # Create agent
    agent = QLearning(state_space=env.state_space, action_space=env.action_space)
    policy = EpsilonGreedyPolicy(epsilon=0.1, decay_rate=0.99)
    
    # Train agent
    print("Training agent on custom environment...")
    rewards = train_agent(env, agent, policy, num_episodes=500)
    
    # Plot learning curve
    plot_learning_curve(rewards, window_size=50, title="Q-Learning on Custom Environment")
    
    # Evaluate the trained agent
    mean_reward, std_reward, _ = evaluate_agent(env, agent, num_episodes=100, render=False)
    print(f"Average reward after training: {mean_reward:.2f} ± {std_reward:.2f}")
    
    return agent, rewards


def main():
    """Run all examples."""
    print("RL Toolkit Examples")
    print("===================\n")
    
    # Run examples (you can comment out the ones you don't want to run)
    try:
        # Example 1: Basic Q-Learning
        agent1, rewards1 = example_1_basic_q_learning()
        
        # Example 2: SARSA vs Q-Learning
        results2 = example_2_sarsa_vs_q_learning()
        
        # Example 3: Maze Navigation
        agent3, rewards3 = example_3_maze_navigation()
        
        # Example 4: Hyperparameter Tuning
        results4 = example_4_hyperparameter_tuning()
        
        # Example 5: Custom Environment
        agent5, rewards5 = example_5_custom_environment()
        
        print("\nAll examples completed successfully!")
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user.")
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()