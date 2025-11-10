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

# Initialize environment and Q-table
env = gym.make("FrozenLake-v1")
Q_table = np.zeros((env.observation_space.n, env.action_space.n))
print(f"Environment: {env.observation_space.n} states, {env.action_space.n} actions\n")

# Q-learning parameters
n_episodes = 10000
max_steps = 100
epsilon = 1.0  # exploration rate
epsilon_decay = 0.001
min_epsilon = 0.01
gamma = 0.99  # discount factor
alpha = 0.1   # learning rate

rewards_history = []

print("Training Q-learning agent...")

# Training loop
for episode in range(n_episodes):
    state, _ = env.reset()
    total_reward = 0
    
    for step in range(max_steps):
        # Epsilon-greedy action selection
        if np.random.random() < epsilon:
            action = env.action_space.sample()  # Explore
        else:
            action = np.argmax(Q_table[state])  # Exploit
        
        # Take action and observe result
        next_state, reward, done, truncated, _ = env.step(action)
        
        # Q-learning update: Q(s,a) = Q(s,a) + α[r + γ*max(Q(s',a')) - Q(s,a)]
        Q_table[state, action] += alpha * (reward + gamma * np.max(Q_table[next_state]) - Q_table[state, action])
        
        total_reward += reward
        state = next_state
        
        if done:
            break
    
    # Decay exploration rate
    epsilon = max(min_epsilon, np.exp(-epsilon_decay * episode))
    rewards_history.append(total_reward)

# Print training statistics
print(f"\nTraining complete! Mean reward: {np.mean(rewards_history):.3f}")
print("\nRewards per 1000 episodes:")
for i in range(10):
    mean_reward = np.mean(rewards_history[i*1000:(i+1)*1000])
    print(f"Episodes {i*1000}-{(i+1)*1000}: {mean_reward:.3f}")

env.close()

# Demonstrate trained agent

print("\nDemonstrating trained agent (5 episodes)...\n")


env_demo = gym.make("FrozenLake-v1", render_mode="human")
action_names = ["Left", "Down", "Right", "Up"]

for demo in range(5):
    print(f"\n Demo Episode {demo + 1}")
    state, _ = env_demo.reset()
    total_reward = 0
    
    for step in range(max_steps):
        # Use learned policy (greedy)
        action = np.argmax(Q_table[state])
        print(f"Step {step + 1}: Action = {action_names[action]}")
        
        next_state, reward, done, truncated, _ = env_demo.step(action)
        env_demo.render()
        total_reward += reward
        state = next_state
        
        if done:
            print("🎉 Goal!" if reward > 0 else "💀 Hole!")
            break
        
        time.sleep(0.3)
    
    print(f"Total reward: {total_reward}")
    time.sleep(1)

env_demo.close()






#SARSA 

import numpy as np
import gymnasium as gym

# Initialize environment and Q-table
env = gym.make("FrozenLake-v1", is_slippery=False)
Q_table = np.zeros((env.observation_space.n, env.action_space.n))
print(f"SARSA Training on FrozenLake ({env.observation_space.n} states, {env.action_space.n} actions)\n")

# SARSA parameters
n_episodes = 10000
max_steps = 100
epsilon = 1.0
epsilon_decay = 0.001
min_epsilon = 0.01
gamma = 0.99  # discount factor
alpha = 0.1   # learning rate

# Tracking variables
rewards_history = []
successful_routes = []
best_route = None

def epsilon_greedy_action(state, epsilon):
    """Select action using epsilon-greedy policy"""
    if np.random.random() < epsilon:
        return env.action_space.sample()
    return np.argmax(Q_table[state])

print("Training SARSA agent...")

# SARSA training loop
for episode in range(n_episodes):
    state, _ = env.reset()
    action = epsilon_greedy_action(state, epsilon)  # Choose initial action
    
    total_reward = 0
    route = [state]
    
    for step in range(max_steps):
        # Take action and observe next state
        next_state, reward, done, truncated, _ = env.step(action)
        
        # Choose next action using current policy (SARSA key difference!)
        next_action = epsilon_greedy_action(next_state, epsilon)
        
        # SARSA update: Q(s,a) = Q(s,a) + α[r + γ*Q(s',a') - Q(s,a)]
        Q_table[state, action] += alpha * (reward + gamma * Q_table[next_state, next_action] - Q_table[state, action])
        
        total_reward += reward
        route.append(next_state)
        
        # Move to next state and action
        state, action = next_state, next_action
        
        if done:
            if reward == 1:  # Success
                successful_routes.append((episode + 1, route.copy()))
                if best_route is None or len(route) < len(best_route):
                    best_route = route.copy()
            break
    
    # Decay exploration rate
    epsilon = max(min_epsilon, np.exp(-epsilon_decay * episode))
    rewards_history.append(total_reward)

# Print results
print(f"\nTraining complete! Mean reward: {np.mean(rewards_history):.3f}")
print(f"Total successful episodes: {len(successful_routes)}")

if best_route:
    print(f"\nBest route: {best_route}")
    print(f"Minimum moves: {len(best_route) - 1}")
    
    print(f"\nFirst 5 successful routes:")
    for ep, route in successful_routes[:5]:
        print(f"  Episode {ep}: {route} ({len(route)-1} moves)")

print("\nRewards per 1000 episodes:")
for i in range(10):
    mean_reward = np.mean(rewards_history[i*1000:(i+1)*1000])
    print(f"  Episodes {i*1000}-{(i+1)*1000}: {mean_reward:.3f}")

env.close()



         


#Monte Carlo

import numpy as np
import gymnasium as gym
import matplotlib.pyplot as plt
from collections import defaultdict

env = gym.make('FrozenLake-v1', is_slippery=False) 
Q_table = np.zeros((env.observation_space.n, env.action_space.n))
returns = defaultdict(list) 
print(f"Monte Carlo on FrozenLake ({env.observation_space.n} states, {env.action_space.n} actions)\n")

# Monte Carlo parameters
n_episodes = 1000  
max_steps = 100
epsilon = 1.0
epsilon_decay = 0.995 
min_epsilon = 0.01
gamma = 0.99  

rewards_history = []
success_history = []

print("Training Monte Carlo agent...")

for episode in range(n_episodes):
    state, _ = env.reset()
    episode_data = []  
    
    for step in range(max_steps):
        # Epsilon-greedy action selection
        if np.random.random() < epsilon:
            action = env.action_space.sample()
        else:
            action = np.argmax(Q_table[state])
        
        next_state, reward, done, truncated, _ = env.step(action)
        episode_data.append((state, action, reward))
        state = next_state
        
        if done or truncated:
            break
    
    visited = set()
    G = 0  # Return (cumulative discounted reward)
    
    for state, action, reward in reversed(episode_data):
        G = gamma * G + reward  # Accumulate discounted return
        
        if (state, action) not in visited:
            visited.add((state, action))
            returns[(state, action)].append(G)  # Store this return
            Q_table[state, action] = np.mean(returns[(state, action)])  # Average all returns
    
    epsilon = max(min_epsilon, epsilon * epsilon_decay)
    
    total_reward = sum(r for _, _, r in episode_data)
    rewards_history.append(total_reward)
    success_history.append(1 if total_reward > 0 else 0)

print(f"\nTraining complete!")
print(f"Success rate: {np.mean(success_history):.2%}")
print(f"Mean reward: {np.mean(rewards_history):.3f}")

print("\nRewards per 200 episodes:")
for i in range(5):
    mean_reward = np.mean(rewards_history[i*200:(i+1)*200])
    success_rate = np.mean(success_history[i*200:(i+1)*200])
    print(f"  Episodes {i*200}-{(i+1)*200}: reward={mean_reward:.3f}, success={success_rate:.2%}")

def moving_average(data, window=50):
    return np.convolve(data, np.ones(window)/window, mode='valid')

plt.figure(figsize=(12, 5))

# Rewards plot
plt.subplot(1, 2, 1)
plt.plot(rewards_history, alpha=0.3, color='blue', label='Episode Reward')
plt.plot(moving_average(rewards_history), color='darkblue', linewidth=2, label='Moving Average (50)')
plt.xlabel('Episode')
plt.ylabel('Total Reward')
plt.title('Monte Carlo Learning: Rewards')
plt.legend()
plt.grid(True, alpha=0.3)

# Success rate plot
plt.subplot(1, 2, 2)
plt.plot(success_history, alpha=0.3, color='green', label='Success (1/0)')
plt.plot(moving_average(success_history), color='darkgreen', linewidth=2, label='Success Rate (50)')
plt.xlabel('Episode')
plt.ylabel('Success')
plt.title('Monte Carlo Learning: Success Rate')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

env.close()






#Policy Gradient

import numpy as np
import gymnasium as gym

env = gym.make("FrozenLake-v1", is_slippery=False)
n_states = env.observation_space.n
n_actions = env.action_space.n

policy_weights = np.random.randn(n_states, n_actions) * 0.01
print(f"Policy Gradient on FrozenLake ({n_states} states, {n_actions} actions)\n")

n_episodes = 5000
max_steps = 100
lr = 0.5
gamma = 0.95
baseline = 0

rewards_history = []

def softmax(x):
    exp_x = np.exp(x - np.max(x))
    return exp_x / np.sum(exp_x)

def get_action_probs(state):
    return softmax(policy_weights[state])

def choose_action(state):
    probs = get_action_probs(state)
    return np.random.choice(n_actions, p=probs)

def update_policy(states, actions, rewards):
    global baseline
    
    returns = []
    G = 0
    for r in reversed(rewards):
        G = r + gamma * G
        returns.insert(0, G)
    
    returns = np.array(returns)
    baseline = 0.9 * baseline + 0.1 * np.mean(returns)
    advantages = returns - baseline
    
    for state, action, advantage in zip(states, actions, advantages):
        probs = get_action_probs(state)
        for a in range(n_actions):
            if a == action:
                policy_weights[state, a] += lr * advantage * (1 - probs[a])
            else:
                policy_weights[state, a] -= lr * advantage * probs[a]

print("Training Policy Gradient agent...")

for episode in range(n_episodes):
    state, _ = env.reset()
    states, actions, rewards = [], [], []
    
    for step in range(max_steps):
        action = choose_action(state)
        next_state, reward, done, truncated, _ = env.step(action)
        
        states.append(state)
        actions.append(action)
        
        if done and reward == 1:
            rewards.append(10)
        elif done and reward == 0:
            rewards.append(-1)
        else:
            rewards.append(-0.01)
        
        if done or truncated:
            break
        state = next_state
    
    if len(states) > 0:
        update_policy(states, actions, rewards)
    
    total_reward = 1 if (done and next_state == 15) else 0
    rewards_history.append(total_reward)
    
    if episode % 1000 == 0:
        recent_success = np.sum(rewards_history[-1000:] if len(rewards_history) >= 1000 else rewards_history)
        print(f"Episode {episode}: Successes = {int(recent_success)}")

print(f"\nTraining complete! Mean reward: {np.mean(rewards_history):.3f}")

print("\nSuccesses per 1000 episodes:")
for i in range(10):
    successes = np.sum(rewards_history[i*1000:(i+1)*1000])
    print(f"  Episodes {i*1000}-{(i+1)*1000}: {int(successes)} successes")

print("\nTesting trained policy (100 episodes)...")
test_rewards = []

for episode in range(100):
    state, _ = env.reset()
    total_reward = 0
    
    for step in range(max_steps):
        probs = get_action_probs(state)
        action = np.argmax(probs)
        
        next_state, reward, done, truncated, _ = env.step(action)
        total_reward += reward
        
        if done or truncated:
            break
        state = next_state
    
    test_rewards.append(total_reward)

success_rate = np.sum(test_rewards) / len(test_rewards)
print(f"Test performance: {success_rate:.2%} success rate ({int(np.sum(test_rewards))}/100 successes)")

env.close()







#Neural Network

import numpy as np
import gymnasium as gym

env = gym.make("FrozenLake-v1", is_slippery=False)
n_states = env.observation_space.n
n_actions = env.action_space.n
print(f"Neural Network Q-Learning on FrozenLake ({n_states} states, {n_actions} actions)\n")

W1 = np.random.randn(n_states, 16) * 0.1
b1 = np.zeros(16)
W2 = np.random.randn(16, n_actions) * 0.1
b2 = np.zeros(n_actions)

n_episodes = 10000
max_steps = 100
epsilon = 1.0
min_epsilon = 0.01
gamma = 0.99
lr = 0.05

rewards_history = []

def one_hot(state):
    vec = np.zeros(n_states)
    vec[state] = 1
    return vec

def predict(state):
    x = one_hot(state)
    h = np.tanh(x @ W1 + b1)
    return h @ W2 + b2

def update(state, action, target):
    global W1, b1, W2, b2
    
    x = one_hot(state)
    h = np.tanh(x @ W1 + b1)
    q = h @ W2 + b2
    
    error = q[action] - target
    
    dq = np.zeros(n_actions)
    dq[action] = error
    
    W2 -= lr * np.outer(h, dq)
    b2 -= lr * dq
    
    dh = dq @ W2.T * (1 - h**2)
    
    W1 -= lr * np.outer(x, dh)
    b1 -= lr * dh

print("Training Neural Network Q-Learning...")

for episode in range(n_episodes):
    state, _ = env.reset()
    total_reward = 0
    
    for step in range(max_steps):
        if np.random.random() < epsilon:
            action = env.action_space.sample()
        else:
            action = np.argmax(predict(state))
        
        next_state, reward, done, truncated, _ = env.step(action)
        
        if done:
            target = reward
        else:
            target = reward + gamma * np.max(predict(next_state))
        
        update(state, action, target)
        
        total_reward += reward
        state = next_state
        
        if done or truncated:
            break
    
    epsilon = max(min_epsilon, epsilon * 0.9995)
    rewards_history.append(total_reward)
    
    if episode % 1000 == 0:
        recent = np.mean(rewards_history[-1000:] if len(rewards_history) >= 1000 else rewards_history)
        print(f"Episode {episode}: Reward = {recent:.3f}")

print(f"\nTraining complete! Mean reward: {np.mean(rewards_history):.3f}")

print("\nRewards per 1000 episodes:")
for i in range(10):
    mean_reward = np.mean(rewards_history[i*1000:(i+1)*1000])
    print(f"  Episodes {i*1000}-{(i+1)*1000}: {mean_reward:.3f}")

print("\nTesting (100 episodes)...")
test_rewards = []

for episode in range(100):
    state, _ = env.reset()
    total_reward = 0
    
    for step in range(max_steps):
        action = np.argmax(predict(state))
        next_state, reward, done, truncated, _ = env.step(action)
        total_reward += reward
        
        if done or truncated:
            break
        state = next_state
    
    test_rewards.append(total_reward)

print(f"Test: {np.mean(test_rewards):.2%} success ({int(np.sum(test_rewards))}/100)")

env.close()

         ''')
    
def ml_5():
    print(Fore.RED + '''

#Convolutional Neural Network (CNN)

#MNIST

import tensorflow as tf

from tensorflow.keras import layers, models
from tensorflow.keras.datasets import mnist

import numpy as np

(x_train, y_train), (x_test, y_test) = mnist.load_data()

x_train = x_train.astype('float32') / 255
x_test = x_test.astype('float32') / 255

x_train = x_train.reshape((x_train.shape[0], 28, 28, 1))
x_test = x_test.reshape((x_test.shape[0], 28, 28, 1))

y_train = tf.keras.utils.to_categorical(y_train, 10)
y_test = tf.keras.utils.to_categorical(y_test, 10)

model = models.Sequential()

model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=(28, 28, 1)))
model.add(layers.MaxPooling2D((2, 2)))

model.add(layers.Conv2D(64, (3, 3), activation='relu'))
model.add(layers.MaxPooling2D((2, 2)))

model.add(layers.Conv2D(64, (3, 3), activation='relu'))

model.add(layers.Flatten())

model.add(layers.Dense(64, activation='relu'))

model.add(layers.Dense(10, activation='softmax'))

model.compile(optimizer='adam',  loss='categorical_crossentropy',  metrics=['accuracy'])

model.fit(x_train, y_train, epochs=5, batch_size=64, validation_data=(x_test, y_test))

test_loss, test_acc = model.evaluate(x_test, y_test)
print(f"Test accuracy: {test_acc}")




import matplotlib.pyplot as plt
import numpy as np

pred_probs = model.predict(x_test)
pred_labels = np.argmax(pred_probs, axis=1)
true_labels = np.argmax(y_test, axis=1)

correct_indices = np.where(pred_labels == true_labels)[0]
incorrect_indices = np.where(pred_labels != true_labels)[0]

plt.figure(figsize=(10, 4))
for i, idx in enumerate(correct_indices[:10]):
    plt.subplot(2, 5, i+1)
    plt.imshow(x_test[idx].reshape(28, 28), cmap='gray')
    plt.title(f"True: {true_labels[idx]}\nPred: {pred_labels[idx]}")
    plt.axis('off')
    
plt.suptitle("Correct Predictions")
plt.tight_layout()
plt.show()

plt.figure(figsize=(10, 4))
for i, idx in enumerate(incorrect_indices[:10]):
    plt.subplot(2, 5, i+1)
    plt.imshow(x_test[idx].reshape(28, 28), cmap='gray')
    plt.title(f"True: {true_labels[idx]}\nPred: {pred_labels[idx]}")
    plt.axis('off')
    
plt.suptitle("Incorrect Predictions")
plt.tight_layout()
plt.show()






#CIFAR-10


import tensorflow as tf

from tensorflow.keras import layers, models
from tensorflow.keras.datasets import cifar10

import numpy as np

(x_train, y_train), (x_test, y_test) = cifar10.load_data()

x_train = x_train.astype('float32') / 255
x_test = x_test.astype('float32') / 255

y_train = tf.keras.utils.to_categorical(y_train, 10)
y_test = tf.keras.utils.to_categorical(y_test, 10)

model = models.Sequential()

model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=(32, 32, 3)))
model.add(layers.MaxPooling2D((2, 2)))

model.add(layers.Conv2D(64, (3, 3), activation='relu'))
model.add(layers.MaxPooling2D((2, 2)))

model.add(layers.Conv2D(64, (3, 3), activation='relu'))

model.add(layers.Flatten())

model.add(layers.Dense(64, activation='relu'))

model.add(layers.Dense(10, activation='softmax'))

model.compile(optimizer='adam',  loss='categorical_crossentropy',  metrics=['accuracy'])

model.fit(x_train, y_train, epochs=10, batch_size=64, validation_data=(x_test, y_test))

test_loss, test_acc = model.evaluate(x_test, y_test)
print(f"Test accuracy: {test_acc}")



import numpy as np
import matplotlib.pyplot as plt

pred_probs = model.predict(x_test)
pred_labels = np.argmax(pred_probs, axis=1)
true_labels = np.argmax(y_test, axis=1)

correct_indices = np.where(pred_labels == true_labels)[0]
incorrect_indices = np.where(pred_labels != true_labels)[0]

class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']

plt.figure(figsize=(10, 4))

for i, idx in enumerate(correct_indices[:10]):
    plt.subplot(2, 5, i+1)
    plt.imshow(x_test[idx])
    plt.title(f"True: {class_names[true_labels[idx]]}\nPred: {class_names[pred_labels[idx]]}")
    plt.axis('off')
    
plt.suptitle("Correct Predictions")
plt.tight_layout()
plt.show()

plt.figure(figsize=(10, 4))

for i, idx in enumerate(incorrect_indices[:10]):
    plt.subplot(2, 5, i+1)
    plt.imshow(x_test[idx])
    plt.title(f"True: {class_names[true_labels[idx]]}\nPred: {class_names[pred_labels[idx]]}")
    plt.axis('off')
plt.suptitle("Incorrect Predictions")
plt.tight_layout()
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
    # Graph setup
    vertices = ["A", "B", "C", "D"]
    weights = {"AB": 10, "AC": 10, "AD": 30, "BC": 40, "CD": 20, "BD": 10}
    
    # Initialize pheromones randomly
    pheromone = {edge: randrange(1, 51) for edge in weights}
    print("Initial pheromone:", pheromone)
    
    # ACO parameters
    decay_rate, iterations, alpha, beta, Q = 0.1, 50, 1.0, 2.0, 100
    
    best_path, best_length = None, float('inf')
    
    for iteration in range(iterations):
        print(f"\n{'='*60}\nIteration {iteration+1}")
        
        # Build path
        start = vertices[randrange(len(vertices))]
        path, current, visited = [start], start, {start}
        
        while len(visited) < len(vertices):
            # Calculate scores for unvisited neighbors
            scores = {}
            for next_v in vertices:
                if next_v not in visited:
                    edge = ''.join(sorted([current, next_v]))
                    heuristic = 1.0 / weights[edge]
                    scores[next_v] = (pheromone[edge] ** alpha) * (heuristic ** beta)
            
            # Probabilistic selection
            total = sum(scores.values())
            r, cumulative = random(), 0
            for next_v, score in scores.items():
                cumulative += score / total
                if r <= cumulative:
                    path.append(next_v)
                    visited.add(next_v)
                    current = next_v
                    break
        
        path.append(start)  # Return to start
        
        # Calculate path length
        path_length = sum(weights[''.join(sorted([path[i], path[i+1]]))] 
                         for i in range(len(path)-1))
        
        print(f"Path: {' → '.join(path)}, Length: {path_length}")
        
        # Update best path
        if path_length < best_length:
            best_path, best_length = path, path_length
        
        # Pheromone evaporation
        pheromone = {edge: round(val * (1 - decay_rate), 3) 
                    for edge, val in pheromone.items()}
        
        # Pheromone deposit
        for i in range(len(path)-1):
            edge = ''.join(sorted([path[i], path[i+1]]))
            pheromone[edge] += round(Q / path_length, 3)
        
        print(f"Pheromone: {pheromone}")
    
    print(f"\n{'='*60}")
    print(f"BEST PATH: {' → '.join(best_path)}, Length: {best_length}")
    print(f"{'='*60}")
    
    return pheromone

final_pheromone = aco()

          
          ''')
    
def ml_8():
    print(Fore.RED + '''
        
#PSO for Clustering

import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs

np.random.seed(42)

class PSOClustering:
    def __init__(self, n_clusters=3, n_particles=10, max_iter=100, w=0.5, c1=1.5, c2=1.5):
        self.n_clusters = n_clusters
        self.n_particles = n_particles
        self.max_iter = max_iter
        self.w, self.c1, self.c2 = w, c1, c2
        
    def _fitness(self, centers, data):
        """Calculate sum of distances from points to their nearest cluster center"""
        distances = np.linalg.norm(data[:, None] - centers, axis=2)
        return np.sum(np.min(distances, axis=1))
    
    def fit(self, data):
        n_features = data.shape[1]
        data_min, data_max = data.min(axis=0), data.max(axis=0)
        
        # Initialize particles
        positions = np.random.uniform(data_min, data_max, (self.n_particles, self.n_clusters, n_features))
        velocities = np.random.uniform(-0.1, 0.1, (self.n_particles, self.n_clusters, n_features))
        
        # Initialize personal and global bests
        p_best = positions.copy()
        p_best_fitness = np.array([self._fitness(pos, data) for pos in positions])
        g_best_idx = np.argmin(p_best_fitness)
        g_best = p_best[g_best_idx].copy()
        
        # PSO iterations
        for iteration in range(self.max_iter):
            for i in range(self.n_particles):
                # Update velocity
                r1, r2 = np.random.random(2)
                velocities[i] = (self.w * velocities[i] + 
                                self.c1 * r1 * (p_best[i] - positions[i]) +
                                self.c2 * r2 * (g_best - positions[i]))
                
                # Update position
                positions[i] = np.clip(positions[i] + velocities[i], data_min, data_max)
                
                # Update personal best
                fitness = self._fitness(positions[i], data)
                if fitness < p_best_fitness[i]:
                    p_best[i] = positions[i].copy()
                    p_best_fitness[i] = fitness
                    
                    # Update global best
                    if fitness < p_best_fitness[g_best_idx]:
                        g_best = positions[i].copy()
                        g_best_idx = i
            
            if iteration % 10 == 0:
                print(f"Iteration {iteration}: Best fitness = {p_best_fitness[g_best_idx]:.4f}")
        
        self.cluster_centers = g_best
        return self
    
    def predict(self, data):
        """Assign each point to nearest cluster center"""
        distances = np.linalg.norm(data[:, None] - self.cluster_centers, axis=2)
        return np.argmin(distances, axis=1)


# Generate and cluster data
X, _ = make_blobs(n_samples=300, centers=3, n_features=2, random_state=42)

pso = PSOClustering(n_clusters=3, n_particles=20, max_iter=100)
pso.fit(X)
labels = pso.predict(X)

# Visualize results
plt.figure(figsize=(10, 6))
plt.scatter(X[:, 0], X[:, 1], c=labels, cmap='viridis', alpha=0.7)
plt.scatter(pso.cluster_centers[:, 0], pso.cluster_centers[:, 1],
           c='red', marker='X', s=200, label='Cluster Centers')
plt.title('PSO Clustering Results')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('pso_clustering_results.png')
plt.show()






#PSO for Search Optimization

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

np.random.seed(42)

def rastrigin_function(x):
    """Rastrigin function - Global minimum at f(0,0,...,0) = 0"""
    return 10 * len(x) + np.sum(x**2 - 10 * np.cos(2 * np.pi * x))


class PSOOptimizer:
    def __init__(self, dimensions=2, n_particles=30, max_iter=100, bounds=(-5.12, 5.12), 
                 w=0.7, c1=1.5, c2=1.5):
        self.dimensions = dimensions
        self.n_particles = n_particles
        self.max_iter = max_iter
        self.bounds = bounds
        self.w, self.c1, self.c2 = w, c1, c2
        
    def optimize(self, objective_function):
        # Initialize particles
        positions = np.random.uniform(self.bounds[0], self.bounds[1], 
                                     (self.n_particles, self.dimensions))
        velocities = np.random.uniform(-0.5, 0.5, (self.n_particles, self.dimensions))
        
        # Initialize personal and global bests
        p_best = positions.copy()
        p_best_fitness = np.array([objective_function(pos) for pos in positions])
        g_best_idx = np.argmin(p_best_fitness)
        g_best = p_best[g_best_idx].copy()
        
        self.fitness_history = []
        
        # PSO main loop
        for iteration in range(self.max_iter):
            for i in range(self.n_particles):
                # Update velocity (inertia + cognitive + social)
                r1, r2 = np.random.random(self.dimensions), np.random.random(self.dimensions)
                velocities[i] = (self.w * velocities[i] + 
                                self.c1 * r1 * (p_best[i] - positions[i]) +
                                self.c2 * r2 * (g_best - positions[i]))
                
                # Update position
                positions[i] = np.clip(positions[i] + velocities[i], 
                                      self.bounds[0], self.bounds[1])
                
                # Update personal best
                fitness = objective_function(positions[i])
                if fitness < p_best_fitness[i]:
                    p_best[i] = positions[i].copy()
                    p_best_fitness[i] = fitness
                    
                    # Update global best
                    if fitness < p_best_fitness[g_best_idx]:
                        g_best = positions[i].copy()
                        g_best_idx = i
            
            self.fitness_history.append(p_best_fitness[g_best_idx])
            
            if iteration % 10 == 0:
                print(f"Iteration {iteration}: Best fitness = {p_best_fitness[g_best_idx]:.6f}")
        
        self.positions = positions
        self.g_best = g_best
        self.g_best_fitness = p_best_fitness[g_best_idx]
        
        print(f"\nOptimization finished!")
        print(f"Best solution: {self.g_best}")
        print(f"Best fitness: {self.g_best_fitness:.6f}")
        
        return self.g_best, self.g_best_fitness


def plot_results(pso, objective_function):
    """Plot convergence history and function landscape (2D only)"""
    plt.figure(figsize=(15, 6))
    
    # Plot convergence
    plt.subplot(1, 2, 1)
    plt.plot(pso.fitness_history)
    plt.title('Convergence History')
    plt.xlabel('Iteration')
    plt.ylabel('Best Fitness')
    plt.grid(True)
    
    # Plot 2D landscape
    if pso.dimensions == 2:
        plt.subplot(1, 2, 2)
        
        # Create mesh grid
        x = np.linspace(pso.bounds[0], pso.bounds[1], 100)
        y = np.linspace(pso.bounds[0], pso.bounds[1], 100)
        X, Y = np.meshgrid(x, y)
        Z = np.array([[objective_function(np.array([X[i,j], Y[i,j]])) 
                      for j in range(X.shape[1])] for i in range(X.shape[0])])
        
        plt.contourf(X, Y, Z, 50, cmap=cm.viridis)
        plt.colorbar(label='Function Value')
        plt.scatter(pso.positions[:, 0], pso.positions[:, 1],
                   color='white', alpha=0.5, label='Final Particles')
        plt.scatter(pso.g_best[0], pso.g_best[1],
                   color='red', marker='*', s=200, label='Global Best')
        plt.title('Function Landscape')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.legend()
    
    plt.tight_layout()
    plt.savefig('pso_optimization_results.png')
    plt.show()


# Run optimization
pso = PSOOptimizer(dimensions=2, n_particles=30, max_iter=100, bounds=(-5.12, 5.12))
best_position, best_fitness = pso.optimize(rastrigin_function)
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