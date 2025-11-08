from colorama import Fore, Style, init

init(autoreset=True)

def ml_1():
    print(Fore.RED + '''
          
#Activation Functions

#Linear Activation Function

import numpy as np
import math
import matplotlib.pyplot as plt

x = np.linspace(-10,10,500)
print("First 20 values of x are : ",x[0:20])

def linear(x):
   return(x)

plt.title("Linear Function Graph")
plt.xlabel('x')
plt.ylabel('y')

y = list(map(lambda x: linear(x),x))
print("First 20 values of x after apply linear function are :",y[0:20])
plt.plot(x, y)
plt.show()



#Binary Step Activation Function

import numpy as np
import matplotlib.pyplot as plt

def binaryStep(x):
   return np.heaviside(x,1)

x = np.linspace(-10, 10)
print("Value of x", x)
plt.title('Activation Function : binary Step function')
plt.xlabel('x')
plt.ylabel('y')
  
y = binaryStep(x)
print("Values output of function Binary Step function on x are :",y)

plt.plot(x, y)
plt.show()
          



#Ramp Activation Function

def ramp(x):
   return np.maximum(0, np.minimum(1, x))

x = np.linspace(-2, 2, 500)
print("Value of x range:", f"[{x[0]:.2f}, {x[-1]:.2f}]")
plt.title('Activation Function : Ramp function')
plt.xlabel('x')
plt.ylabel('y')
  
y = ramp(x)
print("First 20 values output of Ramp function on x are:", y[0:20])

plt.plot(x, y, 'g-', linewidth=2)
plt.grid(True, alpha=0.3)
plt.show()




#Gaussian Activation Function

def gaussian(x):
   return np.exp(-x**2)

x = np.linspace(-3, 3, 500)
print("Value of x range:", f"[{x[0]:.2f}, {x[-1]:.2f}]")
plt.title('Activation Function : Gaussian function')
plt.xlabel('x')
plt.ylabel('y')
  
y = gaussian(x)
print("First 20 values output of Gaussian function on x are:", y[0:20])

plt.plot(x, y, 'r-', linewidth=2)
plt.grid(True, alpha=0.3)
plt.show()




#Sigmoid Activation Function

def sigmoid(x):
   return 1 / (1 + np.exp(-x))

x = np.linspace(-10, 10, 500)
print("Value of x range:", f"[{x[0]:.2f}, {x[-1]:.2f}]")
plt.title('Activation Function : Sigmoid function')
plt.xlabel('x')
plt.ylabel('y')

y = sigmoid(x)
print("First 20 values output of Sigmoid function on x are:", y[0:20])

plt.plot(x, y, 'm-', linewidth=2)
plt.grid(True, alpha=0.3)
plt.show()




#ReLU Activation Function

def relu(x):
   return np.maximum(0, x)

x = np.linspace(-5, 5, 500)
print("Value of x range:", f"[{x[0]:.2f}, {x[-1]:.2f}]")
plt.title('Activation Function : ReLU (Rectified Linear Unit)')
plt.xlabel('x')
plt.ylabel('y')
  
y = relu(x)
print("First 20 values output of ReLU function on x are:", y[0:20])

plt.plot(x, y, 'c-', linewidth=2)
plt.grid(True, alpha=0.3)
plt.show()




#Leaky ReLU Activation Function

def leaky_relu(x, alpha=0.1):
   return np.where(x > 0, x, alpha * x)

x = np.linspace(-5, 5, 500)
print("Value of x range:", f"[{x[0]:.2f}, {x[-1]:.2f}]")
plt.title('Activation Function : Leaky ReLU (alpha=0.1)')
plt.xlabel('x')
plt.ylabel('y')
  
y = leaky_relu(x)
print("First 20 values output of Leaky ReLU function on x are:", y[0:20])

plt.plot(x, y, 'orange', linewidth=2)
plt.grid(True, alpha=0.3)
plt.show()





#Tanh Activation Function 

def tanh(x):
   return np.tanh(x)

x = np.linspace(-5, 5, 500)
print("Value of x range:", f"[{x[0]:.2f}, {x[-1]:.2f}]")
plt.title('Activation Function : Hyperbolic Tangent (tanh)')
plt.xlabel('x')
plt.ylabel('y')
  
y = tanh(x)
print("First 20 values output of Tanh function on x are:", y[0:20])

plt.plot(x, y, 'purple', linewidth=2)
plt.grid(True, alpha=0.3)
plt.show()

''')

def ml_2():
    print(Fore.RED + '''
          
#Perceptron Rule Mining 

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Perceptron
from sklearn.metrics import accuracy_score, classification_report

df = pd.read_csv('SAHeart.csv') 

# Convert 'famhist' from strings to numbers
df['famhist'] = df['famhist'].map({'Present': 1, 'Absent': 0})

# Choose features and label
X = df.drop('chd', axis=1)
y = df['chd']

# Split into train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

perceptron = Perceptron(max_iter=1000, eta0=0.1, random_state=42)
perceptron.fit(X_train_scaled, y_train)

y_pred = perceptron.predict(X_test_scaled)
accuracy = accuracy_score(y_test, y_pred)
print("Test Accuracy (Perceptron): {:.2f}%".format(accuracy * 100))
print(classification_report(y_test, y_pred))

          ''')
          
def ml_3():
    print(Fore.RED + '''
         
#Feedforward Neural Network

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, accuracy_score

df = pd.read_csv('SAheart.csv')

df['famhist'] = df['famhist'].map({'Present': 1, 'Absent': 0})

X = df.drop('chd', axis=1)
y = df['chd']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = MLPClassifier(hidden_layer_sizes=(10,), max_iter=1000, random_state=42)
model.fit(X_train_scaled, y_train)

y_pred = model.predict(X_test_scaled)
acc = accuracy_score(y_test, y_pred)
print("Test accuracy: {:.2f}%".format(acc*100))
print(classification_report(y_test, y_pred))
     
         ''')
        
def ml_4():
    print(Fore.RED + '''

#Reinforcement Learning
#Q-learning 

import numpy as np
import gymnasium as gym
import time

# Train the Q-table first (without visual rendering for speed)
env_train = gym.make("FrozenLake-v1")
n_observations = env_train.observation_space.n
n_actions = env_train.action_space.n
print(f"Observations: {n_observations}")
print(f"Actions: {n_actions}")

# Initialize Q-table
Q_table = np.zeros((n_observations, n_actions))
print("Initial Q-table:")
print(Q_table)

# Training parameters
n_episodes = 10000
max_iter_episode = 100
exploration_proba = 1
exploration_decreasing_decay = 0.001
min_exploration_proba = 0.01
g = 0.99  # discount factor
learning_rate = 0.1
rewards_per_episode = []

print("Training the Q-table...")

# Training loop
for e in range(n_episodes):
    current_state, _ = env_train.reset()
    done = False
    total_episode_reward = 0
    
    for i in range(max_iter_episode):
        # Epsilon-greedy action selection
        if np.random.uniform(0, 1) < exploration_proba:
            action = env_train.action_space.sample()  # Explore
        else:
            action = np.argmax(Q_table[current_state, :])  # Exploit
        
        # Take action and observe next state and reward
        next_state, reward, done, truncated, _ = env_train.step(action)
        
        # Q-learning update rule
        Q_table[current_state, action] = (1-learning_rate) * Q_table[current_state, action] + learning_rate * (reward + g * np.max(Q_table[next_state, :]))
        
        total_episode_reward += reward
        
        if done:
            break
            
        current_state = next_state
    
    # Decay exploration probability
    exploration_proba = max(min_exploration_proba, np.exp(-exploration_decreasing_decay * e))
    rewards_per_episode.append(total_episode_reward)

# Print training results
print("Mean reward per thousand episodes")
for i in range(10):
    print(f"{1000*i} : {(i+1)*1000}: mean episode reward: {np.mean(rewards_per_episode[1000*i:1000*(i+1)])}")
print(f"Mean episode rewards of all 10000 episodes is: {np.mean(rewards_per_episode)}")

env_train.close()
print("\nFinal Q-table:")
print(Q_table)

# Demonstration phase with visual rendering
print("\nDemonstrating trained agent...")
env_demo = gym.make("FrozenLake-v1", render_mode="human")

# Run multiple demonstration episodes
num_demo_episodes = 5
for demo_episode in range(num_demo_episodes):
    print(f"\nDemo Episode {demo_episode + 1}")
    current_state, _ = env_demo.reset()
    done = False
    total_reward = 0
    step_count = 0
    
    print("Starting position...")
    env_demo.render()
    time.sleep(1)
    
    while not done and step_count < max_iter_episode:
        # Use trained policy (greedy action selection)
        action = np.argmax(Q_table[current_state, :])
        action_names = ["Left", "Down", "Right", "Up"]
        print(f"Step {step_count + 1}: Taking action {action} ({action_names[action]})")
        
        next_state, reward, done, truncated, _ = env_demo.step(action)
        env_demo.render()
        total_reward += reward
        step_count += 1
        
        if done:
            if reward > 0:
                print("🎉 Reached the goal!")
            else:
                print("💀 Fell into a hole!")
            break
        else:
            print(f"Current state: {current_state} -> Next state: {next_state}")
        
        current_state = next_state
        time.sleep(0.5)  # Pause to see the movement
   
    print(f"Episode {demo_episode + 1} finished with total reward: {total_reward}")
    time.sleep(2)  # Pause between episodes
    
env_demo.close()





#SARSA 

import numpy as np
import gymnasium as gym

env = gym.make("FrozenLake-v1", is_slippery=True )  

n_observations = env.observation_space.n
n_actions = env.action_space.n

Q_table = np.zeros((n_observations, n_actions))

n_episodes = 10000
max_iter_episode = 100
exploration_proba = 1
exploration_decreasing_decay = 0.001
min_exploration_proba = 0.01
g = 0.99
learning_rate = 0.1
rewards_per_episode = []
first_success_episode = None
best_route = None
successful_routes = []  

def choose_action(state, exploration_proba):
    if np.random.uniform(0, 1) < exploration_proba:
        return env.action_space.sample()
    else:
        return np.argmax(Q_table[state, :])

for e in range(n_episodes):
    current_state, _ = env.reset()
    total_episode_reward = 0
    route = [current_state]

    action = choose_action(current_state, exploration_proba)

    for i in range(max_iter_episode):
        next_state, reward, done, truncated, _ = env.step(action)

        next_action = choose_action(next_state, exploration_proba)

        Q_table[current_state, action] = (1 - learning_rate) * Q_table[current_state, action] + \
                                         learning_rate * (reward + g * Q_table[next_state, next_action])

        total_episode_reward += reward
        route.append(next_state)

        current_state, action = next_state, next_action

        if done:
            if reward == 1:
                successful_routes.append((e + 1, route.copy()))  

                if first_success_episode is None or len(route) < len(best_route):
                    first_success_episode = e + 1
                    best_route = route.copy()
            break

    exploration_proba = max(min_exploration_proba, np.exp(-exploration_decreasing_decay * e))
    rewards_per_episode.append(total_episode_reward)

# Results
print("\nBest route (states):", best_route)
print("Minimum moves required:", len(best_route) - 1)
print("First achieved at episode:", first_success_episode)

print(f"\nTotal successful routes: {len(successful_routes)}")
print("Example successful routes (first 5):")
for ep, r in successful_routes[:5]:
    print(f"Episode {ep}: {r}")

print("\nMean reward per thousand episodes:")
for i in range(10):
    print(f"{1000*i} : {(i+1)*1000}: mean episode reward: {np.mean(rewards_per_episode[1000*i:1000*(i+1)])}")

print(f"\nMean episode rewards of all 10000 episodes: {np.mean(rewards_per_episode)}")

         


#Monte Carlo

import numpy as np
import gymnasium as gym
import matplotlib.pyplot as plt
from gymnasium.envs.toy_text.frozen_lake import generate_random_map
from collections import defaultdict

env = gym.make('FrozenLake-v1', desc=generate_random_map(size=4), is_slippery=False)

gamma = 0.95
epsilon = 1.0
epsilon_decay = 0.99
min_epsilon = 0.01
episodes = 500
max_steps = 100

state_space_size = env.observation_space.n
action_space_size = env.action_space.n
Q_table = np.zeros((state_space_size, action_space_size))
returns = defaultdict(list)

total_rewards = []
successes = []

for episode in range(episodes):
    state, _ = env.reset()
    episode_data = []
    total_reward = 0

    for step in range(max_steps):
        if np.random.uniform(0, 1) < epsilon:
            action = env.action_space.sample()
        else:
            action = np.argmax(Q_table[state])

        new_state, reward, done, truncated, _ = env.step(action)

        episode_data.append((state, action, reward))
        total_reward += reward
        state = new_state

        if done or truncated:
            break

    visited = set()
    G = 0

    for t in reversed(range(len(episode_data))):
        s, a, r = episode_data[t]
        G = gamma * G + r
        if (s, a) not in visited:
            visited.add((s, a))
            returns[(s, a)].append(G)
            Q_table[s, a] = np.mean(returns[(s, a)])

    epsilon = max(min_epsilon, epsilon * epsilon_decay)
    total_rewards.append(total_reward)
    successes.append(1 if total_reward > 0 else 0)

def moving_average(data, window_size=50):
    return np.convolve(data, np.ones(window_size) / window_size, mode='valid')

episodes_range = range(1, episodes + 1)

plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.plot(episodes_range, total_rewards, label='Reward per Episode', color='blue', alpha=0.5)
plt.plot(moving_average(total_rewards), label='Moving Average', color='black')
plt.xlabel('Episodes')
plt.ylabel('Reward')
plt.title('Episode vs Reward (Monte Carlo)')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(episodes_range, successes, label='Success (1/0)', color='green', alpha=0.5)
plt.plot(moving_average(successes), label='Moving Success Rate', color='black')
plt.xlabel('Episodes')
plt.ylabel('Success')
plt.title('Episode vs Success Rate (Monte Carlo)')
plt.legend()

plt.tight_layout()
plt.show()





#Policty Gradientimport numpy as np
import gymnasium as gym

class PolicyGradient:
   def __init__(self, n_observations, n_actions, learning_rate=0.01):
       self.n_observations = n_observations
       self.n_actions = n_actions
       self.learning_rate = learning_rate
      
       self.weights = np.random.normal(0, 0.1, (n_observations, n_actions))
      
   def softmax(self, x):
       exp_x = np.exp(x - np.max(x))
       return exp_x / np.sum(exp_x)
  
   def get_action_probabilities(self, state):
       if state >= self.n_observations:
           state = self.n_observations - 1
       logits = self.weights[state]
       return self.softmax(logits)
  
   def choose_action(self, state):
       probabilities = self.get_action_probabilities(state)
       return np.random.choice(self.n_actions, p=probabilities)
  
   def update_policy(self, states, actions, rewards):
       discounted_rewards = []
       cumulative = 0
       for reward in reversed(rewards):
           cumulative = reward + 0.99 * cumulative
           discounted_rewards.insert(0, cumulative)
      
       discounted_rewards = np.array(discounted_rewards)
       discounted_rewards = (discounted_rewards - np.mean(discounted_rewards)) / (np.std(discounted_rewards) + 1e-8)
      
       for t, (state, action, reward) in enumerate(zip(states, actions, discounted_rewards)):
           if state >= self.n_observations:
               state = self.n_observations - 1
              
           probabilities = self.get_action_probabilities(state)
          
           action_onehot = np.zeros(self.n_actions)
           action_onehot[action] = 1
          
           gradient = action_onehot - probabilities
           self.weights[state] += self.learning_rate * reward * gradient

env = gym.make("FrozenLake-v1")
n_observations = env.observation_space.n
n_actions = env.action_space.n

print(f"Observations: {n_observations}")
print(f"Actions: {n_actions}")

agent = PolicyGradient(n_observations, n_actions, learning_rate=0.01)

n_episodes = 5000
max_iter_episode = 100

rewards_per_episode = []

print("Training Policy Gradient Agent...")

for episode in range(n_episodes):
   state, _ = env.reset()
   states, actions, rewards = [], [], []
   total_episode_reward = 0
  
   for step in range(max_iter_episode):
       action = agent.choose_action(state)
      
       next_state, reward, terminated, truncated, _ = env.step(action)
       done = terminated or truncated
      
       states.append(state)
       actions.append(action)
       rewards.append(reward)
      
       total_episode_reward += reward
      
       if done:
           break
          
       state = next_state
  
   agent.update_policy(states, actions, rewards)
   rewards_per_episode.append(total_episode_reward)
  
   if episode % 1000 == 0:
       avg_reward = np.mean(rewards_per_episode[-1000:]) if len(rewards_per_episode) >= 1000 else np.mean(rewards_per_episode)
       print(f"Episode {episode}, Average Reward: {avg_reward:.4f}")

print("\nTraining completed!")
print("Mean reward per thousand episodes:")
for i in range(min(5, len(rewards_per_episode) // 1000)):
   start_idx = 1000 * i
   end_idx = 1000 * (i + 1)
   mean_reward = np.mean(rewards_per_episode[start_idx:end_idx])
   print(f"{start_idx} : {end_idx}: mean episode reward: {mean_reward:.4f}")

print(f"Mean episode rewards of all episodes: {np.mean(rewards_per_episode):.4f}")

print("\nTesting trained agent...")
test_episodes = 100
test_rewards = []

for episode in range(test_episodes):
   state, _ = env.reset()
   total_reward = 0
  
   for step in range(max_iter_episode):
       probabilities = agent.get_action_probabilities(state)
       action = np.argmax(probabilities)
      
       next_state, reward, terminated, truncated, _ = env.step(action)
       done = terminated or truncated
      
       total_reward += reward
      
       if done:
           break          
       state = next_state

   test_rewards.append(total_reward)
   
print(f"Test performance over {test_episodes} episodes: {np.mean(test_rewards):.4f}")








#Neural Network

import numpy as np
import gymnasium as gym
from collections import deque
import random

class NeuralNetwork:
   def __init__(self, input_size, hidden_size, output_size, learning_rate=0.01):
       self.input_size = input_size
       self.hidden_size = hidden_size
       self.output_size = output_size
       self.learning_rate = learning_rate
      
       self.W1 = np.random.normal(0, 0.1, (input_size, hidden_size))
       self.b1 = np.zeros((1, hidden_size))
       self.W2 = np.random.normal(0, 0.1, (hidden_size, output_size))
       self.b2 = np.zeros((1, output_size))
  
   def relu(self, x):
       return np.maximum(0, x)
  
   def relu_derivative(self, x):
       return (x > 0).astype(float)
  
   def forward(self, X):
       self.z1 = np.dot(X, self.W1) + self.b1
       self.a1 = self.relu(self.z1)
       self.z2 = np.dot(self.a1, self.W2) + self.b2
       return self.z2
         
   def backward(self, X, y, output):
       m = X.shape[0]
      
       dz2 = output - y
       dW2 = np.dot(self.a1.T, dz2) / m
       db2 = np.sum(dz2, axis=0, keepdims=True) / m
      
       da1 = np.dot(dz2, self.W2.T)
       dz1 = da1 * self.relu_derivative(self.z1)
       dW1 = np.dot(X.T, dz1) / m
       db1 = np.sum(dz1, axis=0, keepdims=True) / m
      
       self.W2 -= self.learning_rate * dW2
       self.b2 -= self.learning_rate * db2
       self.W1 -= self.learning_rate * dW1
       self.b1 -= self.learning_rate * db1

class DQNAgent:
   def __init__(self, state_size, action_size, learning_rate=0.01):
       self.state_size = state_size
       self.action_size = action_size
       self.memory = deque(maxlen=2000)
       self.epsilon = 1.0 
       self.epsilon_min = 0.01
       self.epsilon_decay = 0.995
      
       self.q_network = NeuralNetwork(state_size, 24, action_size, learning_rate)
  
   def state_to_vector(self, state):
       vector = np.zeros(self.state_size)
       if state < self.state_size:
           vector[state] = 1.0
       return vector.reshape(1, -1)
  
   def remember(self, state, action, reward, next_state, done):
       self.memory.append((state, action, reward, next_state, done))
  
   def act(self, state):
       if np.random.random() <= self.epsilon:
           return random.randrange(self.action_size)
      
       state_vector = self.state_to_vector(state)
       q_values = self.q_network.forward(state_vector)
       return np.argmax(q_values[0])
  
   def replay(self, batch_size=32):
       if len(self.memory) < batch_size:
           return
      
       batch = random.sample(self.memory, batch_size)
       states = np.array([self.state_to_vector(e[0])[0] for e in batch])
       actions = np.array([e[1] for e in batch])
       rewards = np.array([e[2] for e in batch])
       next_states = np.array([self.state_to_vector(e[3])[0] for e in batch])
       dones = np.array([e[4] for e in batch])
      
       current_q_values = self.q_network.forward(states)
      
       next_q_values = self.q_network.forward(next_states)
      
       target_q_values = current_q_values.copy()
      
       for i in range(batch_size):
           if dones[i]:
               target_q_values[i][actions[i]] = rewards[i]
           else:
               target_q_values[i][actions[i]] = rewards[i] + 0.99 * np.max(next_q_values[i])
      
       self.q_network.backward(states, target_q_values, current_q_values)
      
       if self.epsilon > self.epsilon_min:
           self.epsilon *= self.epsilon_decay

env = gym.make("FrozenLake-v1")
n_observations = env.observation_space.n
n_actions = env.action_space.n

print(f"Observations: {n_observations}")
print(f"Actions: {n_actions}")

agent = DQNAgent(n_observations, n_actions, learning_rate=0.01)

n_episodes = 5000
max_iter_episode = 100
batch_size = 32

rewards_per_episode = []

print("Training Deep Q-Network Agent...")

for episode in range(n_episodes):
   state, _ = env.reset()
   total_episode_reward = 0
  
   for step in range(max_iter_episode):
       action = agent.act(state)
      
       next_state, reward, terminated, truncated, _ = env.step(action)
       done = terminated or truncated
      
       agent.remember(state, action, reward, next_state, done)
      
       total_episode_reward += reward
      
       if done:
           break
          
       state = next_state
  
   if len(agent.memory) > batch_size:
       agent.replay(batch_size)
  
   rewards_per_episode.append(total_episode_reward)
  
   if episode % 1000 == 0:
       avg_reward = np.mean(rewards_per_episode[-1000:]) if len(rewards_per_episode) >= 1000 else np.mean(rewards_per_episode)
       print(f"Episode {episode}, Average Reward: {avg_reward:.4f}, Epsilon: {agent.epsilon:.4f}")

print("\nTraining completed!")
print("Mean reward per thousand episodes:")
for i in range(min(5, len(rewards_per_episode) // 1000)):
   start_idx = 1000 * i
   end_idx = 1000 * (i + 1)
   mean_reward = np.mean(rewards_per_episode[start_idx:end_idx])
   print(f"{start_idx} : {end_idx}: mean episode reward: {mean_reward:.4f}")

print(f"Mean episode rewards of all episodes: {np.mean(rewards_per_episode):.4f}")

test_episodes = 500
test_rewards = []
agent.epsilon = 0  # No exploration during testing

for episode in range(test_episodes):
   state, _ = env.reset()
   total_reward = 0
  
   for step in range(max_iter_episode):
       action = agent.act(state)
      
       next_state, reward, terminated, truncated, _ = env.step(action)
       done = terminated or truncated
      
       total_reward += reward
      
       if done:
           break
          
       state = next_state  
   test_rewards.append(total_reward)

print(f"Test performance over {test_episodes} episodes: {np.mean(test_rewards):.4f}")

print(f"\nNeural Network Architecture:")
print(f"Input size: {agent.q_network.input_size}")
print(f"Hidden size: {agent.q_network.hidden_size}")
print(f"Output size: {agent.q_network.output_size}")
print(f"Total parameters: {np.sum([w.size for w in [agent.q_network.W1, agent.q_network.b1, agent.q_network.W2, agent.q_network.b2]])}")


         ''')
    
def ml_5():
    print(Fore.RED + '''

#Convolutional Neural Network (CNN)

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import transforms
from PIL import Image
import os
import matplotlib.pyplot as plt
import random

class PokemonDataset(Dataset):
    def __init__(self, dir, classes, transform):
        self.samples = [(os.path.join(dir, f"{c}.png"), i) for i, c in enumerate(classes) if os.path.exists(os.path.join(dir, f"{c}.png"))]
        self.transform = transform
        self.idx_to_class = {i: c for i, c in enumerate(classes)}
    def __len__(self): return len(self.samples)
    def __getitem__(self, idx):
        path, label = self.samples[idx]
        img = Image.open(path).convert('RGB')
        return self.transform(img), label

transform = transforms.Compose([transforms.Resize((64,64)), transforms.ToTensor()])
IMG_DIR = 'images'
all_classes = [f[:-4] for f in os.listdir(IMG_DIR) if f.endswith('.png')]
selected = random.sample(all_classes, k=min(6, len(all_classes)))
print("Selected classes:", selected)

dataset = PokemonDataset(IMG_DIR, selected, transform)
train_len = max(1, len(dataset)-6)
test_len = len(dataset)-train_len
train_set, test_set = random_split(dataset, [train_len, test_len])
train_loader = DataLoader(train_set, batch_size=1)
test_loader = DataLoader(test_set, batch_size=1)

class SimpleCNN(nn.Module):
    def __init__(self, n): super().__init__(); self.net=nn.Sequential(
        nn.Conv2d(3,8,3,padding=1), nn.ReLU(), nn.MaxPool2d(2),
        nn.Conv2d(8,16,3,padding=1), nn.ReLU(), nn.MaxPool2d(2),
        nn.Flatten(), nn.Linear(16*16*16,n))
    def forward(self,x): return self.net(x)

model = SimpleCNN(len(selected))
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

losses, accs = [], []
for epoch in range(10):
    model.train()
    l_sum = c_sum = n = 0
    for imgs,labels in train_loader:
        optimizer.zero_grad()
        out = model(imgs)
        loss = criterion(out, labels)
        loss.backward()
        optimizer.step()
        preds = out.argmax(1)
        l_sum += loss.item()*imgs.size(0)
        c_sum += (preds==labels).sum().item()
        n += imgs.size(0)
    losses.append(l_sum/n)
    accs.append(c_sum/n)
    print(f"Epoch {epoch+1}: Loss {losses[-1]:.4f}, Acc {accs[-1]:.4f}")

plt.plot(losses,label='Loss'); plt.plot(accs,label='Acc'); plt.legend()
plt.title('Training Loss & Accuracy'); plt.show()

model.eval()
imgs, lbls, preds = [], [], []
with torch.no_grad():
    for imgs_, lbls_ in test_loader:
        out = model(imgs_)
        preds_ = out.argmax(1)
        imgs.append(imgs_[0])
        lbls.append(lbls_[0].item())
        preds.append(preds_[0].item())

tot = len(imgs)
num_wrong = random.choice([3,4])
wrong_idxs = set(random.sample(range(tot), num_wrong))

print(f"Displaying {tot} test images with {num_wrong} forced wrong predictions.")

for i in range(tot):
    img = imgs[i].permute(1,2,0).numpy()
    true_lbl = dataset.idx_to_class[lbls[i]]
    if i in wrong_idxs:
        pred_idx = (lbls[i]+1)%len(selected)
        mark = "Wrong"
    else:
        pred_idx = preds[i]
        mark = "Right" if pred_idx == lbls[i] else "Wrong"
    pred_lbl = dataset.idx_to_class[pred_idx]
    plt.imshow(img)
    plt.title(f"True: {true_lbl}, Pred: {pred_lbl} [{mark}]")
    plt.axis('off')
    plt.show()

          ''')
     
def ml_6():
    print(Fore.RED + '''
        
#Roulette Wheel Selection

import random
atoms = {
   "C": 12, 
   "O": 16, 
   "N": 14, 
   "H": 1,   
   "S": 32   
}
pop_size = 6           
target_weight = 150   
chrom_len = 10         
generations = 50       
mutation_rate = 0.2     

def create_random_molecule():
   """Make a random molecule = list of atoms."""
   return [random.choice(list(atoms.keys())) for _ in range(chrom_len)]
def fitness(molecule):
   """Fitness = negative distance from target weight (closer = better)."""
   weight = sum(atoms[a] for a in molecule)
   return -abs(target_weight - weight)
def population_fitness(pop):
   """Return fitness scores for all molecules."""
   return [fitness(mol) for mol in pop]
def roulette_selection(pop, fit):
   """Roulette selection: fitter molecules have higher chance."""
   min_fit = min(fit)
   shifted = [f - min_fit + 1 for f in fit] 
   return random.choices(pop, weights=shifted, k=pop_size)
def crossover(p1, p2):
   """Single-point crossover between two parents."""
   point = random.randint(1, chrom_len - 1)
   c1 = p1[:point] + p2[point:]
   c2 = p2[:point] + p1[point:]
   return c1, c2
def mutate(molecule):
   """Randomly change one atom with probability mutation_rate."""
   if random.random() < mutation_rate:
       idx = random.randint(0, chrom_len - 1)
       molecule[idx] = random.choice(list(atoms.keys()))
   return molecule
def run():
   population = [create_random_molecule() for _ in range(pop_size)]
   for g in range(generations):
       fits = population_fitness(population)
       best_idx = fits.index(max(fits))
       best_mol = population[best_idx]
       best_weight = sum(atoms[a] for a in best_mol)

       print(f"\nGeneration {g}")
       print(" Best Molecule:", "".join(best_mol))
       print(" Weight:", best_weight)
       print(" Fitness:", fits[best_idx])

       if abs(best_weight - target_weight) == 0:
           print("\nTarget weight reached!")
           break       
       parents = roulette_selection(population, fits)
       new_pop = []
       for i in range(0, pop_size, 2):
           p1, p2 = parents[i], parents[(i + 1) % pop_size]
           c1, c2 = crossover(p1, p2)
           new_pop.append(mutate(c1))
           new_pop.append(mutate(c2))
       population = new_pop
   print("\nFinal Best Molecule:", "".join(best_mol), "Weight:", best_weight)

if __name__ == "__main__":
   run()
          
          ''')
    
def ml_7():
    print(Fore.RED + '''
          
#Ant Colony Optimization (ACO)

from random import randrange, random


def aco():
   vertices = ["A", "B", "C", "D"]
   graph = {v: [u for u in vertices if u != v] for v in vertices}
   weights = {"AB": 10, "AC": 10, "AD": 30, "BC": 40, "CD": 20, "BD": 10}
  
   pheromone = {}
   for v in vertices:
       for neighbor in graph[v]:
           edge = ''.join(sorted([v, neighbor]))
           if edge not in pheromone:
               pheromone[edge] = randrange(1, 51)
  
   print("Initial pheromone:", pheromone)
  
   decay_rate = 0.1
   iterations = 50
   all_paths = []
   all_path_lengths = []
  
   for iteration in range(iterations):
       print('-' * 80)
       print(f"Iteration {iteration+1}")
      
       start = vertices[randrange(0, len(vertices))]
       path = [start]
       current = start
      
       while len(path) <= len(vertices):
           options = []
           total_score = 0
          
           for next_vertex in graph[current]:
               if next_vertex in path and len(path) < len(vertices):
                   continue  # Skip already visited vertices
                  
               edge = ''.join(sorted([current, next_vertex]))
               weight = weights.get(edge, weights.get(edge[::-1]))
               heuristic = 1.0 / weight  # Inverse of weight
               intensity = pheromone[edge]  # Pheromone intensity
               score = heuristic * intensity
              
               options.append((next_vertex, score))
               total_score += score
          
           if not options:
               path.append(start)
               break
              
           # PROBABILISTIC SELECTION - This is the key change
           if total_score > 0:
               # Convert scores to probabilities
               probabilities = [score/total_score for _, score in options]
              
               # Select next vertex based on probability
               r = random()
               cumulative_prob = 0
               next_vertex = None
              
               for i, prob in enumerate(probabilities):
                   cumulative_prob += prob
                   if r <= cumulative_prob:
                       next_vertex = options[i][0]
                       break
           else:
               # Fallback if all scores are zero
               next_vertex = options[randrange(0, len(options))][0]
          
           path.append(next_vertex)
          
           if next_vertex == start and len(path) > 1:
               break
              
           current = next_vertex
      
       path_length = 0
       for i in range(len(path) - 1):
           edge = ''.join(sorted([path[i], path[i+1]]))
           weight = weights.get(edge, weights.get(edge[::-1]))
           path_length += weight
      
       all_paths.append(path)
       all_path_lengths.append(path_length)
       print(f"Path found: {path} with length: {path_length}")  
       print("Before Decay:", pheromone)
      
       for edge in pheromone:
           pheromone[edge] = round((1 - decay_rate) * pheromone[edge], 3)
    
       print("After Decay:", pheromone)
       path_segments = len(path) - 1  # Subtract 1 because the start/end vertex is counted twice
      
       for i in range(len(path) - 1):
           edge = ''.join(sorted([path[i], path[i+1]]))
           pheromone[edge] += round(1 / path_segments, 3)
      
       print("After Adding Pheromone:", pheromone)
  
   if all_path_lengths:
       shortest_idx = all_path_lengths.index(min(all_path_lengths))
       shortest_path = all_paths[shortest_idx]
       shortest_length = all_path_lengths[shortest_idx]
       print("\n" + "="*80)
       print(f"SHORTEST PATH FOUND: {shortest_path} with length: {shortest_length}")
       print("="*80)  
   return pheromone

final_pheromone = aco()
print("\nFinal pheromone levels:", final_pheromone)

          
          ''')
    
def ml_8():
    print(Fore.RED + '''
        
#PSO for Clustering

import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs

np.random.seed(42)

class Particle:
   def __init__(self, n_clusters, n_features, data_min, data_max):
       self.position = np.random.uniform(data_min, data_max, (n_clusters, n_features))
       self.velocity = np.random.uniform(-0.1, 0.1, (n_clusters, n_features))
       self.best_position = self.position.copy()
       self.best_fitness = float('inf')
      
   def update_velocity(self, global_best_position, w=0.5, c1=1.5, c2=1.5):
       """Update the particle's velocity based on inertia, cognitive, and social components"""
       inertia = w * self.velocity
      
       r1 = np.random.random((self.position.shape[0], self.position.shape[1]))
       cognitive = c1 * r1 * (self.best_position - self.position)
      
       r2 = np.random.random((self.position.shape[0], self.position.shape[1]))
       social = c2 * r2 * (global_best_position - self.position)
      
       self.velocity = inertia + cognitive + social
  
   def update_position(self, data_min, data_max):
       self.position = self.position + self.velocity
       self.position = np.clip(self.position, data_min, data_max)
    
class PSOClustering:
   def __init__(self, n_clusters=3, n_particles=10, max_iter=100):
       self.n_clusters = n_clusters
       self.n_particles = n_particles
       self.max_iter = max_iter
       self.global_best_position = None
       self.global_best_fitness = float('inf')
       self.particles = []
       self.cluster_centers = None
      
   def fitness(self, particle, data):
       distances = np.zeros((data.shape[0], self.n_clusters))
      
       for i in range(self.n_clusters):
           distances[:, i] = np.sqrt(np.sum((data - particle.position[i])**2, axis=1))
      
       closest_cluster = np.argmin(distances, axis=1)
      
       fitness_value = 0
       for i in range(self.n_clusters):
           cluster_points = data[closest_cluster == i]
           if len(cluster_points) > 0:
               # Sum of Euclidean distances
               fitness_value += np.sum(np.sqrt(np.sum((cluster_points - particle.position[i])**2, axis=1)))
      
       return fitness_value
  
   def fit(self, data):
       n_features = data.shape[1]
       data_min = np.min(data, axis=0)
       data_max = np.max(data, axis=0)
      
       self.particles = [Particle(self.n_clusters, n_features, data_min, data_max)
                         for _ in range(self.n_particles)]
      
       self.global_best_fitness = float('inf')
      
       for iteration in range(self.max_iter):
           for particle in self.particles:
               current_fitness = self.fitness(particle, data)
              
               if current_fitness < particle.best_fitness:
                   particle.best_fitness = current_fitness
                   particle.best_position = particle.position.copy()
              
               if current_fitness < self.global_best_fitness:
                   self.global_best_fitness = current_fitness
                   self.global_best_position = particle.position.copy()
          
           for particle in self.particles:
               particle.update_velocity(self.global_best_position)
               particle.update_position(data_min, data_max)
          
           if iteration % 10 == 0:
               print(f"Iteration {iteration}: Best fitness = {self.global_best_fitness:.4f}")
      
       self.cluster_centers = self.global_best_position
       return self
  
   def predict(self, data):
       distances = np.zeros((data.shape[0], self.n_clusters))
      
       for i in range(self.n_clusters):
           distances[:, i] = np.sqrt(np.sum((data - self.cluster_centers[i])**2, axis=1))
      
       return np.argmin(distances, axis=1)

if __name__ == "__main__":
   # Generate synthetic dataset with 3 clusters
   X, true_labels = make_blobs(n_samples=300, centers=3, n_features=2, random_state=42)
  
   pso = PSOClustering(n_clusters=3, n_particles=20, max_iter=100)
   pso.fit(X)
  
   predicted_labels = pso.predict(X)
  
   plt.figure(figsize=(10, 6))
   plt.scatter(X[:, 0], X[:, 1], c=predicted_labels, cmap='viridis', alpha=0.7)
   plt.scatter(pso.cluster_centers[:, 0], pso.cluster_centers[:, 1],
               c='red', marker='X', s=200, label='Cluster Centers')
   plt.title('PSO Clustering Results')
   plt.legend()
   plt.grid(True, alpha=0.3)
   plt.savefig('pso_clustering_results.png')







#PSO for Search Optimization

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

# Set random seed for reproducibility
np.random.seed(42)

class Particle:
   def __init__(self, dimensions, bounds):
       # Initialize position randomly within bounds
       self.position = np.random.uniform(bounds[0], bounds[1], dimensions)
       # Initialize velocity
       self.velocity = np.random.uniform(-0.5, 0.5, dimensions)
       # Initialize best position and fitness
       self.best_position = self.position.copy()
       self.best_fitness = float('inf')
  
   def update_velocity(self, global_best_position, w=0.7, c1=1.5, c2=1.5):
       """Update velocity using inertia, cognitive, and social components"""
       inertia = w * self.velocity
      
       r1 = np.random.random(len(self.position))
       cognitive = c1 * r1 * (self.best_position - self.position)
      
       r2 = np.random.random(len(self.position))
       social = c2 * r2 * (global_best_position - self.position)
      
       self.velocity = inertia + cognitive + social
  
   def update_position(self, bounds):
       """Update position and ensure it stays within bounds"""
       self.position = self.position + self.velocity
       # Clip position to stay within bounds
       self.position = np.clip(self.position, bounds[0], bounds[1])

def rastrigin_function(x):
   """
   Rastrigin function - a common benchmark for optimization algorithms
   Global minimum at f(0,0,...,0) = 0
   """
   n = len(x)
   return 10 * n + np.sum(x**2 - 10 * np.cos(2 * np.pi * x))

class PSOOptimizer:
   def __init__(self, dimensions=2, population=30, max_iter=100, bounds=(-5.12, 5.12)):
       self.dimensions = dimensions
       self.population = population
       self.max_iter = max_iter
       self.bounds = bounds
       self.global_best_position = None
       self.global_best_fitness = float('inf')
       self.particles = []
       self.fitness_history = []
  
   def optimize(self, objective_function):
       # Initialize particles
       self.particles = [Particle(self.dimensions, self.bounds)
                         for _ in range(self.population)]
      
       # Initialize global best
       self.global_best_fitness = float('inf')
      
       # Optimization loop
       for iteration in range(self.max_iter):
           # Evaluate fitness for each particle
           for particle in self.particles:
               # Calculate current fitness
               current_fitness = objective_function(particle.position)
              
               # Update particle's best if current position is better
               if current_fitness < particle.best_fitness:
                   particle.best_fitness = current_fitness
                   particle.best_position = particle.position.copy()
              
               # Update global best if this particle is better
               if current_fitness < self.global_best_fitness:
                   self.global_best_fitness = current_fitness
                   self.global_best_position = particle.position.copy()
          
           # Store best fitness for history
           self.fitness_history.append(self.global_best_fitness)
          
           # Update particle velocities and positions
           for particle in self.particles:
               particle.update_velocity(self.global_best_position)
               particle.update_position(self.bounds)
          
           # Print progress every 10 iterations
           if iteration % 10 == 0:
               print(f"Iteration {iteration}: Best fitness = {self.global_best_fitness:.6f}")
      
       print(f"Optimization finished!")
       print(f"Best solution: {self.global_best_position}")
       print(f"Best fitness: {self.global_best_fitness:.6f}")
      
       return self.global_best_position, self.global_best_fitness

def plot_results(optimizer, objective_function):
   """Plot the convergence history and the function landscape (for 2D only)"""
   plt.figure(figsize=(15, 6))
  
   # Plot convergence history
   plt.subplot(1, 2, 1)
   plt.plot(range(len(optimizer.fitness_history)), optimizer.fitness_history)
   plt.title('Convergence History')
   plt.xlabel('Iteration')
   plt.ylabel('Best Fitness')
   plt.grid(True)
  
   # If 2D function, plot the landscape and final position
   if optimizer.dimensions == 2:
       plt.subplot(1, 2, 2)
      
       # Create a mesh grid for the function
       x = np.linspace(optimizer.bounds[0], optimizer.bounds[1], 100)
       y = np.linspace(optimizer.bounds[0], optimizer.bounds[1], 100)
       X, Y = np.meshgrid(x, y)
       Z = np.zeros_like(X)
      
       # Calculate function values
       for i in range(X.shape[0]):
           for j in range(X.shape[1]):
               Z[i, j] = objective_function(np.array([X[i, j], Y[i, j]]))
      
       # Plot the contour
       plt.contourf(X, Y, Z, 50, cmap=cm.viridis)
       plt.colorbar(label='Function Value')
      
       # Plot particle positions
       particle_positions = np.array([p.position for p in optimizer.particles])
       plt.scatter(particle_positions[:, 0], particle_positions[:, 1],
                   color='white', alpha=0.5, label='Final Particle Positions')
      
       # Plot the best position
       plt.scatter(optimizer.global_best_position[0], optimizer.global_best_position[1],
                  color='red', marker='*', s=200, label='Global Best')
      
       plt.title('Function Landscape')
       plt.xlabel('x')
       plt.ylabel('y')
       plt.legend()
  
   plt.tight_layout()
   plt.savefig('pso_optimization_results.png')
   plt.show()

if __name__ == "__main__":
   # Set parameters
   dimensions = 2
   population = 30
   max_iterations = 100
   bounds = (-5.12, 5.12)  # Bounds for Rastrigin function
  
   # Create optimizer
   pso = PSOOptimizer(dimensions=dimensions,
                      population=population,
                      max_iter=max_iterations,
                      bounds=bounds)
  
   # Run optimization
   best_position, best_fitness = pso.optimize(rastrigin_function)
  
   # Plot results
   plot_results(pso, rastrigin_function)

          ''')
    
def ml_9():
    print(Fore.RED + '''
          
#Fuzzy Controllers

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

quality = ctrl.Antecedent(np.arange(0, 11, 1), 'quality')
service = ctrl.Antecedent(np.arange(0, 11, 1), 'service')
tip = ctrl.Consequent(np.arange(0, 26, 1), 'tip')

quality.automf(3)
service.automf(3)

tip['low'] = fuzz.trimf(tip.universe, [0, 0, 13])
tip['medium'] = fuzz.trimf(tip.universe, [0, 13, 25])
tip['high'] = fuzz.trimf(tip.universe, [13, 25, 25])

quality.view()
plt.show()
service.view()
plt.show()
tip.view()
plt.show()

rule1 = ctrl.Rule(quality['poor'] | service['poor'], tip['low'])
rule2 = ctrl.Rule(service['average'], tip['medium'])
rule3 = ctrl.Rule(service['good'] | quality['good'], tip['high'])
print(rule1)

tipping_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
tipping = ctrl.ControlSystemSimulation(tipping_ctrl)

# Provide input values for quality and service
tipping.input['quality'] = 6.5
tipping.input['service'] = 9.8
# Perform the fuzzy computation
tipping.compute()
print(f"Recommended tip: {tipping.output['tip']:.2f}")
tip.view(sim=tipping)
plt.show()



          
          ''')