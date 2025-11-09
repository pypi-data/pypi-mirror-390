#Applying reinforcement learning algorithms to solve complex decision-making problems. 
import numpy as np 
n_states = 5 
actions = [0, 1] 
rewards = [-1, -1, -1, -1, 10] 
goal_state = 4 
alpha = 0.1 
gamma = 0.9 
epsilon = 0.1 
 
q_table = np.zeros((n_states, len(actions))) 
n_episodes = 1000 
 
for episode in range(n_episodes): 
    state = 0 
    while state != goal_state: 
        if np.random.random() < epsilon: 
            action = np.random.choice(actions) 
        else: 
            action = np.argmax(q_table[state]) 
        if action == 1: 
            new_state = state + 1 
        else: 
            new_state = max(0, state - 1) 
        reward = rewards[new_state] 
        q_table[state, action] += alpha * (reward + gamma * np.max(q_table[new_state]) - 
q_table[state, action]) 
        state = new_state 
 
state = 0 
path = [state] 
while state != goal_state: 
    action = np.argmax(q_table[state]) 
    if action == 1: 
        state = state + 1 
    else: 
        state = max(0, state - 1) 
    path.append(state) 
 
print("Q table after training:") 
print(q_table) 
print("\nOptimal path from start to goal:", path)

