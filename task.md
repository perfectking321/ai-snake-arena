# task.md — AI Snake Arena

## Milestone M1 — Foundation

| ID | Title | Description | Tag | Depends On | Status | Note |
|----|-------|-------------|-----|------------|--------|------|
| M1-01 | Project scaffold | Create folder structure: game/, agents/, model/, frontend/. Add __init__.py files. Create requirements.txt with torch, fastapi, uvicorn, numpy. | [devops] | — | ✅ | Created game and agents folders, backend __init__.py files, and requirements.txt |
| M1-02 | Snake game core | Implement game/snake.py: 16×16 grid, snake body list, food placement, collision detection (wall + self), reset(), play_step(action) returns (reward, done, score). Rewards: +10 eat, -10 die, +1 closer, -1 farther. | [backend] | M1-01 | ✅ | Implemented SnakeGame class with correct 16x16 grid and RL rewards |
| M1-03 | State vector builder | Implement game/state.py: build_state(game) returns np.array of 27 floats. Inputs 0-10: danger/direction/food bools. Inputs 11-18: wall distances 8 dirs normalised. Inputs 19-26: body distances 8 dirs normalised. | [backend] | M1-02 | ✅ | Updated to 28-input SnakeQ state vector (wall×4, food×8, body×8, head×4, tail×4) |
| M1-04 | Q-Network + Trainer | Implement agents/rl_agent.py: Linear_QNet(27→256→256→3), QTrainer with Adam + MSE + Bellman update, Agent class with memory deque(100000), batch 1000, LR 0.001, gamma 0.9, epsilon decay 1.0→0.01 over 80 games. | [backend] | M1-03 | ✅ | Implemented PyTorch model, Bellman update logic logic, and Agent |
| M1-05 | Model persistence | In rl_agent.py: save() writes model_dqn.pth + metadata_dqn.json (record, n_games, mean_score, timestamp). load() restores on init if file exists. | [backend] | M1-04 | ✅ | Created robust load/save integration creating `model/` dynamically |
| M1-06 | FastAPI app skeleton | Implement main.py: FastAPI app, serve frontend/index.html at GET /, /model/status GET endpoint returning all metadata JSONs, /model/reset/{algo} POST endpoint. | [backend] | M1-01 | ✅ | "FastAPI server running, all imports resolved" |
| M1-07 | WebSocket endpoint | In main.py: /ws/{algo} WebSocket endpoint. Accepts start/stop/set_speed messages. Runs game loop in asyncio, sends step messages. Loop: get state → get action → play_step → send JSON → await sleep(1/fps). | [backend] | M1-04, M1-06 | ✅ | "WebSocket endpoint verified, server starts clean" |

---

## Milestone M2 — Algorithm Solvers

| ID | Title | Description | Tag | Depends On | Status | Note |
|----|-------|-------------|-----|------------|--------|------|
| M2-01 | BFS solver | Implement agents/bfs.py: solve(snake, food, grid_size) → returns (next_action, explored_cells, path). Queue-based BFS on 16×16 grid avoiding snake body. Returns None path if no route. | [backend] | M1-02 | ✅ | Completed queue BFS |
| M2-02 | DFS solver | Implement agents/dfs.py: solve(snake, food, grid_size) → returns (next_action, explored_cells, path). Stack-based DFS. May return non-optimal path. | [backend] | M1-02 | ✅ | Completed stack DFS |
| M2-03 | UCS solver | Implement agents/ucs.py: solve(snake, food, grid_size) → returns (next_action, explored_cells, path, cost). Priority queue ordered by cumulative cost (uniform cost=1). | [backend] | M1-02 | ✅ | Completed UCS pathfinder |
| M2-04 | A* solver | Implement agents/astar.py: solve(snake, food, grid_size) → returns (next_action, explored_cells, path). f=g+h, h=Manhattan distance. Priority queue on f. | [backend] | M1-02 | ✅ | Completed A* pathfinder |
| M2-05 | Best-First solver | Implement agents/best_first.py: solve(snake, food, grid_size) → returns (next_action, explored_cells, path). Priority queue on h only (greedy). | [backend] | M1-02 | ✅ | Completed BestFirst pathfinder |
| M2-06 | Minimax solver | Implement agents/minimax.py: minimax(state, depth=4, alpha, beta, maximising) → best action. Snake=maximiser, phantom blocker=minimiser. Alpha-beta pruning. Returns (next_action, depth_reached). | [backend] | M1-02 | ✅ | Completed Alpha-Beta solver |
| M2-07 | Hybrid agent | Implement agents/hybrid_agent.py: HybridAgent(algo_name). Wraps DQN agent + selected solver. get_action(game, state): run solver → if valid path use solver action, else use DQN action. Always train DQN. Per-algo save/load with model_{algo}.pth. | [backend] | M1-04, M2-01... | ✅ | Completed arbiter combining RL with classical approaches dynamically |
| M2-08 | WebSocket step payload | Update main.py WebSocket to send full step payload: snake, food, score, game_no, record, mean_score, epsilon, explored, path, algo_stat, done. Wire each algo to correct solver. | [backend] | M1-07, M2-07 | ✅ | Integrated in main.py |

---

## Milestone M3 — Frontend

| ID | Title | Description | Tag | Depends On | Status | Note |
|----|-------|-------------|-----|------------|--------|------|
| M3-01 | HTML skeleton | Create frontend/index.html: dark base styles, CSS variables for all 7 accent colors, font imports, hero section, nav strip, 7 algo-section divs with correct IDs and data-algo attributes. | [frontend] | M1-01 | ✅ | Implemented single file index.html with theme CSS variables |
| M3-02 | Hero section | Build hero: full-width dark section, animated snake canvas background (snake crawls across grid using JS setInterval), title "AI Snake Arena", subtitle, tech chips (PyTorch, DQN, 27-input, FastAPI, WebSocket, BFS, A*, Minimax), scroll CTA arrow. | [frontend] | M3-01 | ✅ | Added Hero section with procedural animated snake crawling background |
| M3-03 | Nav strip | Sticky nav below hero: 7 pill buttons (Pure DQN, DQN+BFS, etc.). Click scrolls to section. Active pill highlights as user scrolls (IntersectionObserver). | [frontend] | M3-01 | ✅ | Added sticky Nav strip and IntersectionObserver for highlight |
| M3-04 | Algo section layout | Each of 7 sections: section header (colored dot + algo name + tag badge + description), 50/50 split layout (left=chart panel, right=snake panel). All 7 sections share same CSS classes, differentiated by accent color CSS variable. | [frontend] | M3-01 | ✅ | Generated 7 sections locally styled correctly |
| M3-05 | Snake canvas renderer | JS function renderFrame(ctx, frameData, accentColor): draws grid lines, explored cells (dim accent overlay), path cells (brighter overlay), snake body (head distinct, body fading opacity), food (circle). Called on every step message. | [frontend] | M3-04 | ✅ | Implemented `renderFrame()` executing all 7 distinct layer drawings |
| M3-06 | Chart.js score graph | Per section: Chart.js line chart, score dataset (solid accent color) + mean score dataset (dashed, 50% opacity). updateChart(sectionId, gameNo, score, mean) appends data point and calls chart.update(). X-axis: games. Y-axis: score. | [frontend] | M3-04 | ✅ | Initialized isolated Chart.js on every section with dynamic dataset append |
| M3-07 | Play/Stop/Speed controls | Per section: Play button opens WS to /ws/{algo}, sends start message, begins render loop. Stop sends stop message, closes WS. Speed select sends set_speed message. Disable Play if already running, re-enable on Stop. | [frontend] | M3-05, M3-06 | ✅ | Added play/stop disable states |
| M3-08 | Stat cards update | 4 stat cards per section: Game No, Score, Record, algo_stat (label+value from server). Update on every step message. algo_stat card label changes per algo (epsilon / nodes / cost / path / h / depth). | [frontend] | M3-07 | ✅ | DOM manip logic updating stat cards implemented |
| M3-09 | WebSocket manager | JS class WSManager: manages one WS per section. Handles open/message/close/error. Dispatches frame data to renderFrame + updateChart + updateStats. Reconnect on unexpected close. | [frontend] | M3-07 | ✅ | Completed `WSManager` mapping to FastAPI endpoints |

---

## Milestone M4 — Polish + Testing

| ID | Title | Description | Tag | Depends On | Status | Note |
|----|-------|-------------|-----|------------|--------|------|
| M4-01 | End-to-end smoke test | Start server, open browser, click Play on DQN section, verify snake moves, graph updates, stats update. Run for 10 games. | [test] | M3-09, M2-08 | 🔲 | |
| M4-02 | Test all 7 algos | Click Play on each of the 7 sections. Verify no crashes, explored overlay visible on hybrid sections, algo_stat card shows correct label per algo. | [test] | M4-01 | 🔲 | |
| M4-03 | Persistence test | Run DQN for 20 games. Note record. Restart server. Click Play again. Verify game_no and record resume from saved values. | [test] | M4-01 | 🔲 | |
| M4-04 | Speed test | On any section, cycle through 1x/2x/10x/50x. Verify game visibly speeds up at each step. 50x should be fast enough to train 100 games quickly. | [test] | M4-01 | 🔲 | |
| M4-05 | Fix bugs from testing | Address any crashes, rendering glitches, WS errors, or chart issues found in M4-01 through M4-04. | [backend] [frontend] | M4-02, M4-03, M4-04 | 🔲 | |
| M4-06 | README | Write README.md: project description, setup instructions (pip install, python main.py), screenshot, algo descriptions table, state vector explanation. | [devops] | M4-05 | 🔲 | |
