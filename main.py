import asyncio
import json
import os
import glob
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

from game.snake import SnakeGame
from game.state import build_state
from agents.hybrid_agent import HybridAgent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SPEED_FPS = { "1": 5, "2": 10, "10": 50, "50": 200 }

@app.get("/")
async def get_index():
    return FileResponse("frontend/index.html")

@app.get("/model/status")
async def get_model_status():
    status = []
    for file in glob.glob("model/metadata_*.json"):
        with open(file, "r") as f:
            try:
                status.append(json.load(f))
            except json.JSONDecodeError:
                pass
    return status

@app.post("/model/reset/{algo}")
async def reset_model(algo: str):
    pth = f"model/model_{algo}.pth"
    json_path = f"model/metadata_{algo}.json"
    if os.path.exists(pth):
        os.remove(pth)
    if os.path.exists(json_path):
        os.remove(json_path)
    return {"status": "ok", "algo": algo}

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}
        
    async def connect(self, ws: WebSocket, algo: str):
        await ws.accept()
        self.active_connections[algo] = ws
        
    def disconnect(self, algo: str):
        if algo in self.active_connections:
            del self.active_connections[algo]

manager = ConnectionManager()

async def game_loop(ws: WebSocket, algo: str, speed_ref: dict):
    agent = HybridAgent(algo)
    game = SnakeGame()
    
    while True:
        try:
            fps = SPEED_FPS[str(speed_ref.get("speed", 10))]
            delay = 1.0 / fps
            
            state_old = build_state(game, extended=True)
            
            final_move, explored, path, algo_stat = agent.get_action(game, state_old)
            
            reward, done, score = game.play_step(final_move)
            state_new = build_state(game, extended=True)
            
            agent.train_short_memory(state_old, final_move, reward, state_new, done)
            agent.remember(state_old, final_move, reward, state_new, done)
            
            msg = {
                "type": "step",
                "algo": algo,
                "snake": [[pt.x, pt.y] for pt in game.snake],
                "food": [game.food.x, game.food.y],
                "score": score,
                "game_no": agent.n_games,
                "record": agent.record,
                "mean_score": round(agent.mean_score, 2),
                "epsilon": round(agent.epsilon, 3),
                "explored": explored,
                "path": path,
                "algo_stat": algo_stat,
                "done": done
            }
            
            await ws.send_json(msg)
            
            if done:
                game.reset()
                agent.n_games += 1
                try:
                    agent.rl.lifetime_games += 1
                except AttributeError:
                    pass
                agent.train_long_memory()
                
                if score > agent.record:
                    agent.record = score
                    agent.save()
                    
                agent.total_score += score
                agent.mean_score = agent.total_score / agent.n_games
            
            await asyncio.sleep(delay)
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            import traceback
            print(f"Game loop error (recovering): {e}")
            traceback.print_exc()
            try:
                game.reset()
            except Exception:
                game = SnakeGame()
            continue

@app.websocket("/ws/{algo}")
async def websocket_endpoint(websocket: WebSocket, algo: str):
    await manager.connect(websocket, algo)
    speed_ref = {"speed": 10}
    loop_task = None
    
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")
            
            if msg_type == "start":
                if loop_task is not None and not loop_task.done():
                    loop_task.cancel()
                speed_ref["speed"] = data.get("speed", 10)
                loop_task = asyncio.create_task(game_loop(websocket, algo, speed_ref))
                
            elif msg_type == "stop":
                if loop_task is not None:
                    loop_task.cancel()
                    loop_task = None
                    
            elif msg_type == "set_speed":
                speed_ref["speed"] = data.get("speed", 10)
                
    except WebSocketDisconnect:
        manager.disconnect(algo)
        if loop_task is not None:
            loop_task.cancel()
