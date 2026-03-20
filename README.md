# AI Snake Arena

A Snake game where AI algorithms learn to play by themselves.
Watch the agent go from dying in 2 moves to scoring 30+ over 100 games.

Built for FT3 Application Development — SRMIST 2026.

---

## How It Works

A Deep Q-Network (DQN) agent observes the game through 28 sensor inputs and decides whether to go straight, turn left, or turn right. It learns purely from trial and error — no rules, no hardcoded logic.

Each section of the app pairs the DQN with a different classical search algorithm. The algorithm finds a path to food, the DQN decides whether to follow it or override it based on safety. This shows how the same RL agent behaves differently depending on the guidance it receives.

---

## Algorithms

| Algorithm | Type | How It Guides the Snake | Expected Score (100 games) |
|---|---|---|---|
| Pure DQN | Reinforcement Learning | Learns entirely from rewards and penalties | 15 – 30 |
| DQN + BFS | Informed Search | Shortest path to food, explores level by level | 25 – 45 |
| DQN + DFS | Uninformed Search | Dives deep before backtracking, finds non-optimal paths | 20 – 35 |
| DQN + UCS | Uninformed Search | Optimal path by cumulative cost (uniform grid = same as BFS) | 25 – 45 |
| DQN + A* | Informed Search | Optimal path using Manhattan distance heuristic | 35 – 60 |
| DQN + Best-First | Informed Search | Greedy — goes straight toward food, can get trapped | 20 – 40 |
| DQN + Minimax | Adversarial Search | Treats board as a game vs a phantom blocker, alpha-beta pruning | 30 – 50 |

---

## State Vector — 28 Inputs

The agent sees the world through 28 numbers:

```
[0–3]   Distance to wall in 4 directions        (float 0–1)
[4–11]  Food visible in 8 directions            (bool 0/1)
[12–19] Distance to own body in 8 directions    (float 0–1)
[20–23] Current head direction                  (one-hot)
[24–27] Current tail direction                  (one-hot)
```

Sensor logic adapted from SnakeQ by ludius0 (MIT License).

---

## Tech Stack

- **Backend** — Python 3.11, FastAPI, WebSocket
- **AI/ML** — PyTorch (DQN, Linear Q-Network)
- **Frontend** — Vanilla HTML/CSS/JS, Chart.js, Canvas API
- **Persistence** — `.pth` model weights + JSON metadata

---

## Run Locally

```bash
git clone https://github.com/YOUR_USERNAME/ai-snake-arena
cd ai-snake-arena

python -m venv venv
source venv/bin/activate

pip install fastapi uvicorn websockets numpy
pip install torch --index-url https://download.pytorch.org/whl/cpu

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open `http://localhost:8000` in your browser.

Click **Play** on any section. The agent starts dumb and gets smarter each game.
Use **50x Speed** to train fast, then drop to **1x** to watch it play properly.

---

## Project Structure

```
ai-snake-arena/
├── main.py               FastAPI app + WebSocket game loop
├── game/
│   ├── snake.py          16×16 grid, snake logic, collision
│   ├── state.py          28-input state vector builder
│   └── snake_sensors.py  8-direction vision rays
├── agents/
│   ├── rl_agent.py       DQN agent, Q-network, replay buffer
│   ├── hybrid_agent.py   DQN + algorithm arbitration
│   ├── bfs.py            Breadth-First Search solver
│   ├── dfs.py            Depth-First Search solver
│   ├── ucs.py            Uniform Cost Search solver
│   ├── astar.py          A* Search solver
│   ├── best_first.py     Greedy Best-First solver
│   └── minimax.py        Minimax with alpha-beta pruning
├── model/                Saved weights + training metadata
└── frontend/
    └── index.html        Single-file web UI
```

---

Made by Iyad — SRMIST B.Tech CSE (AI & ML) 2028
