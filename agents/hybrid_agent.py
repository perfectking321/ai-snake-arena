from agents.rl_agent import Agent

import agents.bfs as bfs
import agents.dfs as dfs
import agents.ucs as ucs
import agents.astar as astar
import agents.best_first as best_first
import agents.minimax as minimax

class HybridAgent:
    def __init__(self, algo_name):
        self.algo_name = algo_name
        self.rl = Agent()
        
        self.rl.save = self._custom_save
        self.rl.load = self._custom_load
        self.rl.load()
        
        self.solvers = {
            "bfs": bfs.solve,
            "dfs": dfs.solve,
            "ucs": ucs.solve,
            "astar": astar.solve,
            "bestfirst": best_first.solve,
            "minimax": minimax.solve
        }
        
    def _custom_save(self):
        import os, json, datetime, torch
        folder_path = './model'
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, f'model_{self.algo_name}.pth')
        torch.save(self.rl.model.state_dict(), file_path)
        
        metadata = {
            "algo": self.algo_name,
            "record": self.rl.record,
            "n_games": self.rl.n_games,
            "mean_score": self.rl.mean_score,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        json_path = os.path.join(folder_path, f'metadata_{self.algo_name}.json')
        with open(json_path, 'w') as f:
            json.dump(metadata, f)
            
    def _custom_load(self):
        import os, json, torch
        folder_path = './model'
        pth_path = os.path.join(folder_path, f'model_{self.algo_name}.pth')
        json_path = os.path.join(folder_path, f'metadata_{self.algo_name}.json')
        
        if os.path.exists(pth_path):
            self.rl.model.load_state_dict(torch.load(pth_path, weights_only=True))
            self.rl.model.train()
            
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r') as f:
                    meta = json.load(f)
                self.rl.record = meta.get("record", 0)
                self.rl.n_games = meta.get("n_games", 0)
                self.rl.mean_score = meta.get("mean_score", 0.0)
                self.rl.total_score = int(self.rl.mean_score * self.rl.n_games)
            except: pass
        self.rl.update_epsilon()

    def get_action(self, game, state):
        dqn_action = self.rl.get_action(state)
        
        if self.algo_name == "dqn" or self.algo_name not in self.solvers:
            return dqn_action, [], [], self.rl.algo_stat
            
        snake_coords = [tuple(p) for p in game.snake]
        food_coord = tuple(game.food)
        
        solver_res = self.solvers[self.algo_name](snake_coords, food_coord, game.GRID_SIZE)
        
        action = solver_res.get('action', [1,0,0])
        path = solver_res.get('path', [])
        
        if self.algo_name == "minimax" or len(path) > 0:
            final_action = action
        else:
            final_action = dqn_action
            
        return final_action, solver_res.get('explored', []), path, solver_res.get('algo_stat', self.rl.algo_stat)
    
    @property
    def n_games(self): return self.rl.n_games
    @n_games.setter
    def n_games(self, v): self.rl.n_games = v
    @property
    def record(self): return self.rl.record
    @record.setter
    def record(self, v): self.rl.record = v
    @property
    def mean_score(self): return self.rl.mean_score
    @mean_score.setter
    def mean_score(self, v): self.rl.mean_score = v
    @property
    def epsilon(self): return self.rl.epsilon
    @property
    def algo_stat(self): return self.rl.algo_stat
    @property
    def total_score(self): return self.rl.total_score
    @total_score.setter
    def total_score(self, v): self.rl.total_score = v
    
    def train_short_memory(self, *args): self.rl.train_short_memory(*args)
    def remember(self, *args): self.rl.remember(*args)
    def train_long_memory(self): self.rl.train_long_memory()
    def save(self): self.rl.save()
