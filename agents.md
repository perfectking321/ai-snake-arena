# agents.md — Deep Reinforcement Learning Snake Agent
## Global rules for every Antigravity agent

---

## Coding Rules

### Language and framework
- Python 3.11. FastAPI + uvicorn. PyTorch (CPU is fine, no CUDA required).
- Vanilla HTML/CSS/JS for frontend. No React, no Vue, no build step.
- Chart.js loaded from CDN: `https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js`

### Style conventions
- Python: snake_case for variables and functions, PascalCase for classes.
- JS: camelCase for variables and functions, PascalCase for classes.
- 4-space indentation in Python, 2-space in JS/HTML/CSS.
- All Python files must have a module docstring at the top.
- No commented-out code in final output.
- No print statements left in production paths — use them only in training loop console output.

### Patterns to use
- FastAPI `async def` for all WebSocket handlers and endpoints.
- `asyncio.sleep()` for game loop timing — never `time.sleep()` inside async context.
- `collections.deque` for replay buffer.
- `numpy` arrays for state vectors — never plain Python lists passed to torch.
- Each algo solver must be a pure function — no side effects, no global state.
- Solver signature: `solve(snake: list, food: tuple, grid_size: int) → dict`
- Solver return dict always contains: `action`, `explored`, `path`, `algo_stat`

### What to NEVER do
- Never use `time.sleep()` inside an async function.
- Never hardcode grid size — always read from `GRID_SIZE` constant in snake.py.
- Never import from a sibling agent file (bfs.py must not import from astar.py).
- Never write to model/ directory from frontend code.
- Never use `plt.show()` or matplotlib in the backend — charts are frontend only.
- Never commit .pth files — they are gitignored.
- Never put game logic in main.py — it belongs in game/.
- Never put algo logic in main.py — it belongs in agents/.
- Never use `import *`.

### Folder ownership (STRICT)
Each agent owns exactly one folder. Do not create, edit, or delete files outside your folder.

| Agent | Owns |
|---|---|
| Backend Agent | `/game/`, `/agents/`, `main.py`, `requirements.txt` |
| Frontend Agent | `/frontend/` |

`/model/` is written to at runtime by the backend — neither agent touches it directly.

---

## Verification Rules

- After implementing any WebSocket endpoint, test it with a simple Python `websockets` client script before marking done.
- After implementing any solver, add a quick `if __name__ == "__main__"` test at the bottom that runs the solver on a sample board and prints the result. Remove before final commit.
- Frontend agent: after any canvas or chart change, verify in browser that rendering is correct. Attach a screenshot as proof.
- Frontend agent: verify Play/Stop cycle works at least 3 times without WS leak or chart duplication.

---

## task.md Maintenance Rules (CRITICAL)

- Before starting any work: read task.md fully. Understand what is done, what is blocked, what you own.
- After completing each task: immediately update task.md.
  - Change status from 🔲 to ✅
  - Add a one-line note in the Note column describing exactly what was done.
  - Example: `✅ | "Implemented BFS solver, returns action + explored + path dict"`
- Never mark a task ✅ without actually completing and verifying it.
- If a task is blocked: mark 🚫 and note the blocker reason.
- If a task is in progress: mark 🔄
- At end of every session: update ALL in-progress tasks honestly (🔄 for incomplete, ✅ for done).
- Never skip updating task.md — it is the handoff contract between agents and sessions.

---

## Project-Specific Constants

```python
GRID_SIZE = 16
BLOCK_SIZE = 1          # logical units (not pixels — canvas handles px)
MAX_MEMORY = 100_000
BATCH_SIZE = 1_000
LR = 0.001
GAMMA = 0.9
EPSILON_START = 1.0
EPSILON_MIN = 0.01
EPSILON_DECAY_GAMES = 80
HIDDEN_SIZE = 256

VALID_ALGOS = ["dqn", "bfs", "dfs", "ucs", "astar", "bestfirst", "minimax"]

SPEED_FPS = { "1": 5, "2": 10, "10": 50, "50": 200 }
```

---

## WebSocket Contract (backend must match exactly)

Step message shape — backend sends this every game step:
```json
{
  "type": "step",
  "algo": "string",
  "snake": [[x,y], ...],
  "food": [x, y],
  "score": int,
  "game_no": int,
  "record": int,
  "mean_score": float,
  "epsilon": float,
  "explored": [[x,y], ...],
  "path": [[x,y], ...],
  "algo_stat": { "label": "string", "value": number },
  "done": bool
}
```

Client sends these shapes — backend must handle all three:
```json
{ "type": "start", "algo": "string", "speed": int }
{ "type": "stop" }
{ "type": "set_speed", "speed": int }
```

When `done: true` — backend resets game and starts next game automatically. Client does NOT need to send another start.

---

## Accent Color Map (frontend must use exactly these)

```css
--color-dqn:       #7c6ef7;
--color-bfs:       #3b9eff;
--color-dfs:       #ff7043;
--color-ucs:       #26c6a0;
--color-astar:     #ffd740;
--color-bestfirst: #e040fb;
--color-minimax:   #ff4081;
```

These are used for: section dot, tag badge, Play button, chart line, explored cell overlay, path overlay, stat card accent value.

---

## Canvas Rendering Layers (frontend draw order — must be exact)

1. Fill background `#0a0a0c`
2. Draw grid lines (0.5px, `#111118`)
3. Draw explored cells (accent color at 12% opacity)
4. Draw path cells (accent color at 25% opacity)
5. Draw snake body (index 1+): accent color at decreasing opacity (1.0 → 0.4)
6. Draw snake head (index 0): full accent color + 2 white eye dots
7. Draw food: red circle (`#ff4444`) with small highlight dot

---

## Definition of Done Checklist (agent self-check before marking ✅)

Backend tasks:
- [ ] Function runs without exceptions on a fresh game state
- [ ] Returns correct types (check against spec.md data models)
- [ ] No blocking calls inside async functions

Frontend tasks:
- [ ] Renders correctly in Chromium browser
- [ ] No JS console errors
- [ ] Screenshot attached as proof of visual work
