import os
import json
import random
import datetime
from collections import deque
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

MAX_MEMORY = 100_000
BATCH_SIZE = 1_000
LR = 0.001
GAMMA = 0.9
EPSILON_START = 1.0
EPSILON_MIN = 0.01
EPSILON_DECAY_GAMES = 80
HIDDEN_SIZE = 256

class Linear_QNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, hidden_size)
        self.linear3 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = F.relu(self.linear2(x))
        return self.linear3(x)

class QTrainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(np.array(state), dtype=torch.float)
        next_state = torch.tensor(np.array(next_state), dtype=torch.float)
        action = torch.tensor(np.array(action), dtype=torch.long)
        reward = torch.tensor(np.array(reward), dtype=torch.float)

        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done,)

        pred = self.model(state)

        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))
            target[idx][torch.argmax(action[idx]).item()] = Q_new

        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()
        self.optimizer.step()

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = EPSILON_START
        self.gamma = GAMMA
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(28, HIDDEN_SIZE, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        
        self.record = 0
        self.total_score = 0
        self.mean_score = 0.0
        
        self.algo_stat = {"label": "epsilon", "value": round(self.epsilon, 3)}
        
        self.load()

    def update_epsilon(self):
        decay_rate = (EPSILON_START - EPSILON_MIN) / EPSILON_DECAY_GAMES
        self.epsilon = max(EPSILON_MIN, EPSILON_START - self.n_games * decay_rate)
        self.algo_stat["value"] = round(self.epsilon, 3)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = list(self.memory)

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        self.update_epsilon()  # ensure updated
        final_move = [0, 0, 0]
        if random.random() < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move

    def save(self):
        folder_path = './model'
        os.makedirs(folder_path, exist_ok=True)
        
        file_path = os.path.join(folder_path, 'model_dqn.pth')
        torch.save(self.model.state_dict(), file_path)
        
        metadata = {
            "algo": "dqn",
            "record": self.record,
            "n_games": self.n_games,
            "mean_score": self.mean_score,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        json_path = os.path.join(folder_path, 'metadata_dqn.json')
        with open(json_path, 'w') as f:
            json.dump(metadata, f)

    def load(self):
        folder_path = './model'
        pth_path = os.path.join(folder_path, 'model_dqn.pth')
        json_path = os.path.join(folder_path, 'metadata_dqn.json')
        
        if os.path.exists(pth_path):
            self.model.load_state_dict(torch.load(pth_path, weights_only=True))
            self.model.train() # Continue training online
            
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r') as f:
                    meta = json.load(f)
                self.record = meta.get("record", 0)
                self.n_games = meta.get("n_games", 0)
                self.mean_score = meta.get("mean_score", 0.0)
                self.total_score = int(self.mean_score * self.n_games)
            except (json.JSONDecodeError, IOError):
                pass
                
        self.update_epsilon()
