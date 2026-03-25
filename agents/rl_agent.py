"""
DQN Agent — based on patrickloeber/snake-ai-pytorch
MIT License. Proven to score 10-15 within 50 games.
"""
import torch
import random
import numpy as np
import os
import json
import datetime
from collections import deque
from game.state import build_state
from game.snake import SnakeGame

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F


class Linear_QNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, hidden_size)
        self.linear3 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = F.relu(self.linear2(x))
        x = self.linear3(x)
        return x


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
                Q_new = reward[idx] + self.gamma * torch.max(
                    self.model(next_state[idx]))
            target[idx][torch.argmax(action[idx]).item()] = Q_new

        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()
        self.optimizer.step()


class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)
        # EXACT patrickloeber architecture: 11→256→256→3 (2 hidden layers)
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

        self.record = 0
        self.total_score = 0
        self.mean_score = 0.0
        self.algo_stat = {"label": "epsilon", "value": 0}

        self.load()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = list(self.memory)
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards,
                                next_states, dones)

    def train_short_memory(self, state, action, reward,
                           next_state, done):
        self.trainer.train_step(state, action, reward,
                                next_state, done)

    def get_action(self, state):
        # EXACT patrickloeber epsilon:
        # epsilon = 80 - n_games
        # explore if randint(0,200) < epsilon
        self.epsilon = 80 - self.n_games
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        # update display stat (show as 0-1 ratio)
        display_eps = max(0, self.epsilon) / 200
        self.algo_stat["value"] = round(display_eps, 3)
        return final_move

    def save(self, algo_name="dqn"):
        folder_path = './model'
        os.makedirs(folder_path, exist_ok=True)
        torch.save(self.model.state_dict(),
                   os.path.join(folder_path,
                                f'model_{algo_name}.pth'))
        metadata = {
            "algo": algo_name,
            "record": self.record,
            "n_games": self.n_games,
            "mean_score": self.mean_score,
            "timestamp": datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S")
        }
        with open(os.path.join(folder_path,
                               f'metadata_{algo_name}.json'),
                  'w') as f:
            json.dump(metadata, f)

    def load(self, algo_name="dqn"):
        folder_path = './model'
        pth = os.path.join(folder_path, f'model_{algo_name}.pth')
        meta = os.path.join(folder_path,
                            f'metadata_{algo_name}.json')
        if os.path.exists(pth):
            self.model.load_state_dict(
                torch.load(pth, weights_only=True))
            self.model.train()
        if os.path.exists(meta):
            try:
                with open(meta) as f:
                    d = json.load(f)
                self.record = d.get("record", 0)
                # n_games PERSISTS across sessions
                # so epsilon keeps decaying
                self.n_games = d.get("n_games", 0)
                self.mean_score = d.get("mean_score", 0.0)
                self.total_score = int(
                    self.mean_score * self.n_games)
            except Exception:
                pass
