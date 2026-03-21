# spec.md — Deep Reinforcement Learning Snake Agent

## Project Overview

A web application demonstrating Reinforcement Learning and Classical AI algorithms through a live Snake game. A Deep Q-Network agent learns to play Snake in real time — the user watches it fail, improve, and eventually master the game. Below the hero, 6 additional sections each show a hybrid agent (DQN + one classical algorithm): BFS, DFS, UCS, A*, Best-First Search, and Minimax with Alpha-Beta Pruning. Each section is visually independent with its own live score graph and snake grid.

**Problem statement:** Make AI/ML algorithms tangible and visual for an academic review — not theory, but a running demo where behavioral differences between algorithms are directly observable.

---

## Tech Stack

| Layer | Choice | Justification |
|---|---|---|
| Backend | Python 3.11 + FastAPI | Course requirement, async, WebSocket native |
| ML | PyTorch | DQN, Linear_QNet, model save/load |
| Realtime | WebSocket (FastAPI) | Streams game state at game speed |
| Frontend | Vanilla HTML + CSS + JS | Zero build step, single file, runs anywhere |
| Canvas | HTML5 Canvas API | Smooth 2D grid rendering |
| Charts | Chart.js via CDN | Live score vs games line chart |
| Persistence | .pth + metadata JSON | Survives server restarts |

---

## Folder Structure

```
ai-snake-arena/
├── main.py
├── game/
│   ├── __init__.py
│   ├── snake.py               # Grid, snake, food, collision, reset
│   └── state.py               # 27-input state vector builder
├── agents/
│   ├── __init__.py
│   ├── rl_agent.py            # Pure DQN: Q-network, epsilon-greedy, replay buffer
│   ├── bfs.py                 # BFS solver → next action + explored cells
│   ├── dfs.py                 # DFS solver → next action + explored cells
│   ├── ucs.py                 # UCS solver → next action + path cost
│   ├── astar.py               # A* solver (f=g+h) → next action + path
│   ├── best_first.py          # Greedy Best-First → next action
│   ├── minimax.py             # Minimax + alpha-beta pruning → next action
│   └── hybrid_agent.py        # DQN + any solver, arbitration logic
├── model/
│   ├── model_dqn.pth
│   ├── model_bfs.pth
│   ├── model_dfs.pth
│   ├── model_ucs.pth
│   ├── model_astar.pth
│   ├── model_bestfirst.pth
│   ├── model_minimax.pth
│   └── metadata_{algo}.json   # Per-algo: games, record, mean score
├── frontend/
│   └── index.html             # Single file: hero + 7 sections
├── requirements.txt
└── README.md
```

---

## Data Models

### State vector — 27 inputs

```
[0-2]   danger straight, danger right, danger left          (bool → 0/1)
[3-6]   direction LEFT, RIGHT, UP, DOWN                     (bool → 0/1)
[7-10]  food left, food right, food up, food down           (bool → 0/1)
[11-18] wall distance in 8 directions (N NE E SE S SW W NW) (float 0–1)
[19-26] nearest body distance in 8 directions               (float 0–1, 1.0 = no body)
```

### Q-Network

```
Linear(27 → 256) → ReLU → Linear(256 → 256) → ReLU → Linear(256 → 3)
Output actions: [go straight, turn right, turn left]
```

### WebSocket — server → client (each game step)

```json
{
  "type": "step",
  "algo": "bfs",
  "snake": [[8,8],[7,8],[6,8]],
  "food": [12,5],
  "score": 3,
  "game_no": 47,
  "record": 31,
  "mean_score": 8.4,
  "epsilon": 0.33,
  "explored": [[9,8],[10,8],[9,9]],
  "path": [[9,8],[10,8],[11,8],[12,5]],
  "algo_stat": { "label": "nodes", "value": 38 },
  "done": false
}
```

### WebSocket — client → server

```json
{ "type": "start", "algo": "dqn", "speed": 10 }
{ "type": "stop" }
{ "type": "set_speed", "speed": 50 }
```

### metadata_{algo}.json

```json
{ "algo": "bfs", "record": 42, "n_games": 23, "mean_score": 14.2, "timestamp": "2026-03-25 10:00:00" }
```

---

## API Contracts

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Serves frontend/index.html |
| `/ws/{algo}` | WebSocket | Live game stream for given algo |
| `/model/reset/{algo}` | POST | Deletes weights + resets metadata |
| `/model/status` | GET | Returns all algo metadata |

Valid algo values: `dqn`, `bfs`, `dfs`, `ucs`, `astar`, `bestfirst`, `minimax`

---

## Algorithm Specs

### Pure DQN
- 27 inputs, hidden 256×2, 3 outputs
- Memory: deque(100,000), batch: 1,000, LR: 0.001, gamma: 0.9
- Epsilon: 1.0 → 0.01 over 80 games
- algo_stat: `{ label: "epsilon", value: 0.33 }`

### Hybrid arbitration (hybrid_agent.py)
1. Run algo solver → get `path` and `explored`
2. If valid path exists → follow algo's next step as primary action
3. DQN evaluates same state → if DQN disagrees strongly, override
4. DQN trains every step regardless (experience still collected)
5. algo_stat varies per algo (see below)

### Per-algo stat labels
- BFS: `{ label: "nodes", value: N }` — cells explored
- DFS: `{ label: "nodes", value: N }` — cells explored
- UCS: `{ label: "cost", value: N }` — path cost
- A*: `{ label: "path", value: N }` — path length
- Best-First: `{ label: "h", value: N }` — heuristic at current head
- Minimax: `{ label: "depth", value: N }` — search depth reached

### Minimax
- Snake = maximiser, phantom blocker agent = minimiser
- Depth limit: 4 (keeps real-time performance)
- Alpha-beta pruning enabled

---

## Frontend Architecture

`frontend/index.html` — single file, no build step.

```
hero section        animated snake canvas bg, title, chips, scroll CTA
nav strip           sticky: Pure DQN | DQN+BFS | DQN+DFS | DQN+UCS | DQN+A* | DQN+Best-First | DQN+Minimax
algo-section × 7    identical layout per section:
  left panel        Chart.js: score line + running mean dashed line
  right panel       canvas grid + Play/Stop + speed select + 4 stat cards
```

Per-section JS:
- Play → open `/ws/{algo}`, send start message, render loop begins
- Stop → send stop, close WS
- Each `step` message → redraw canvas + Chart.js push + update stat cards
- Speed select → send `set_speed`
- Canvas layers: grid → explored cells (dim) → path (bright) → snake → food

Accent colors:
```
dqn:       #7c6ef7  purple
bfs:       #3b9eff  blue
dfs:       #ff7043  orange
ucs:       #26c6a0  teal
astar:     #ffd740  amber
bestfirst: #e040fb  magenta
minimax:   #ff4081  pink-red
```

---

## Constraints

- Grid: 16×16
- Game loop runs server-side in Python
- Speed: 1x=5fps, 2x=10fps, 10x=50fps, 50x=200fps
- Each algo section has independent game loop and WS connection
- Model saves only when new record is set
- No database — .pth + .json only
- Runs locally: `python main.py` → `localhost:8000`

---

## Non-Goals (v1)

- No auth, no user accounts
- No CSP graph coloring (removed per user decision)
- No cloud deployment
- No CNN state (27-input flat vector only)
- No mobile layout

---

## Definition of Done

- [ ] `python main.py` → browser opens, hero visible
- [ ] All 7 sections render on scroll
- [ ] Play/Stop works on every section independently
- [ ] Score graph updates live as games run
- [ ] Speed selector changes game pace
- [ ] Pure DQN visibly improves over 50–100 games
- [ ] Hybrid sections show explored cell overlay
- [ ] Model persists across server restart
- [ ] All 7 algorithms run without crashes
