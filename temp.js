
    // --- Configuration ---
    const ALGOS = [
      { id: 'dqn', name: 'Pure DQN', badge: 'Deep Q-Network', statLabel: 'epsilon', desc: 'A neural network learning strictly via random exploration and delayed rewards. Fails often early on.' },
      { id: 'bfs', name: 'DQN + BFS', badge: 'Breadth-First Search', statLabel: 'nodes', desc: 'DQN guided by an optimal unweighted shortest-path solver. Explores in all directions equally.' },
      { id: 'dfs', name: 'DQN + DFS', badge: 'Depth-First Search', statLabel: 'nodes', desc: 'DQN guided by an aggressive solver diving deep before backtracking. Often finds sub-optimal twisted paths.' },
      { id: 'ucs', name: 'DQN + UCS', badge: 'Uniform Cost Search', statLabel: 'cost', desc: 'DQN guided by Dijkstra\'s algorithm equivalent on uniform grid.' },
      { id: 'astar', name: 'DQN + A*', badge: 'A* Search', statLabel: 'path', desc: 'DQN guided by A* using Manhattan distance heuristic. Extremely efficient and optimal.' },
      { id: 'bestfirst', name: 'DQN + Best-First', badge: 'Greedy Best-First', statLabel: 'h', desc: 'DQN guided purely by Manhattan distance to food. Can get trapped in concave shapes.' },
      { id: 'minimax', name: 'DQN + Minimax', badge: 'Alpha-Beta Pruning', statLabel: 'depth', desc: 'DQN guided by adversarial search treating the board as a game against a phantom blocker.' }
    ];

    const ACCENTS = {
      'dqn': '#7c6ef7',
      'bfs': '#3b9eff',
      'dfs': '#ff7043',
      'ucs': '#26c6a0',
      'astar': '#ffd740',
      'bestfirst': '#e040fb',
      'minimax': '#ff4081'
    };

    const GRID_SIZE = 16;
    const CANVAS_PX = 400; // 16 * 25
    const CELL_PX = CANVAS_PX / GRID_SIZE;

    // --- Generate Sections ---
    const container = document.getElementById('sections-container');
    
    ALGOS.forEach(algo => {
      const section = document.createElement('section');
      section.id = `sec-${algo.id}`;
      section.className = 'algo-section';
      section.dataset.algo = algo.id;
      
      section.innerHTML = `
        <div class="section-header">
          <div class="algo-dot"></div>
          <div class="section-title-wrap">
            <h2>${algo.name} <span class="algo-badge">${algo.badge}</span></h2>
            <p>${algo.desc}</p>
          </div>
        </div>
        <div class="split-layout">
          <div class="panel">
            <div class="panel-header">Performance History</div>
            <div class="chart-container">
              <canvas id="chart-${algo.id}"></canvas>
            </div>
          </div>
          <div class="panel">
            <div class="panel-header">Live Simulation</div>
            <div class="game-container">
              <canvas id="canvas-${algo.id}" width="${CANVAS_PX}" height="${CANVAS_PX}" class="game-canvas"></canvas>
            </div>
            <div class="controls">
              <button class="btn btn-play" id="play-${algo.id}" onclick="window.startAlgo('${algo.id}')">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg> Play
              </button>
              <button class="btn btn-stop" id="stop-${algo.id}" onclick="window.stopAlgo('${algo.id}')" disabled>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M6 6h12v12H6z"/></svg> Stop
              </button>
              <select class="speed-select" id="speed-${algo.id}" onchange="window.setSpeed('${algo.id}', this.value)">
                <option value="1">1x Speed</option>
                <option value="2">2x Speed</option>
                <option value="10" selected>10x Speed</option>
                <option value="50">50x Speed</option>
              </select>
            </div>
            <div class="stat-cards">
              <div class="stat-card">
                <div class="stat-label">Game No</div>
                <div class="stat-value" id="stat-game-${algo.id}">0</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">Score</div>
                <div class="stat-value" id="stat-score-${algo.id}">0</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">Record</div>
                <div class="stat-value" id="stat-record-${algo.id}">0</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">${algo.statLabel}</div>
                <div class="stat-value accent" id="stat-algostat-${algo.id}">0</div>
              </div>
            </div>
          </div>
        </div>
      `;
      container.appendChild(section);
    });

    // --- Canvas Renderer ---
    function hexToRgba(hex, alpha) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    function renderFrame(ctx, frameData, accentColor) {
        // 1. Fill background #0a0a0c
        ctx.fillStyle = '#0a0a0c';
        ctx.fillRect(0, 0, CANVAS_PX, CANVAS_PX);
        
        // 2. Draw grid lines (0.5px, #111118)
        ctx.strokeStyle = '#111118';
        ctx.lineWidth = 0.5;
        for (let i = 0; i <= GRID_SIZE; i++) {
            const pos = i * CELL_PX;
            ctx.beginPath(); ctx.moveTo(pos, 0); ctx.lineTo(pos, CANVAS_PX); ctx.stroke();
            ctx.beginPath(); ctx.moveTo(0, pos); ctx.lineTo(CANVAS_PX, pos); ctx.stroke();
        }

        const drawCell = (x, y, color) => {
            if (x < 0 || x >= GRID_SIZE || y < 0 || y >= GRID_SIZE) return; // boundary safeguard
            ctx.fillStyle = color;
            ctx.fillRect(x * CELL_PX + 1, y * CELL_PX + 1, CELL_PX - 2, CELL_PX - 2);
        };

        // 3. Draw explored cells (accent color at 12% opacity)
        if (frameData.explored && frameData.explored.length > 0) {
            const clr = hexToRgba(accentColor, 0.12);
            frameData.explored.forEach(([x, y]) => drawCell(x, y, clr));
        }

        // 4. Draw path cells (accent color at 25% opacity)
        if (frameData.path && frameData.path.length > 0) {
            const clr = hexToRgba(accentColor, 0.25);
            frameData.path.forEach(([x, y]) => drawCell(x, y, clr));
        }

        // 5. & 6. Draw snake
        if (frameData.snake && frameData.snake.length > 0) {
            const len = frameData.snake.length;
            frameData.snake.forEach(([x, y], i) => {
                if (i === 0) {
                    // Head: full accent + 2 white eye dots
                    drawCell(x, y, accentColor);
                    
                    // compute eye positions based on body direction
                    const cx = x * CELL_PX + CELL_PX/2;
                    const cy = y * CELL_PX + CELL_PX/2;
                    ctx.fillStyle = 'white';
                    ctx.beginPath(); ctx.arc(cx - 3, cy - 3, 2, 0, Math.PI * 2); ctx.fill();
                    ctx.beginPath(); ctx.arc(cx + 3, cy - 3, 2, 0, Math.PI * 2); ctx.fill();
                } else {
                    // Body: accent color at decreasing opacity (1.0 -> 0.4)
                    const op = 1.0 - (0.6 * (Number(i) / (len - 1 || 1)));
                    drawCell(x, y, hexToRgba(accentColor, op));
                }
            });
        }

        // 7. Draw food: red circle (#ff4444) with small highlight dot
        if (frameData.food) {
            const [x, y] = frameData.food;
            const cx = x * CELL_PX + CELL_PX / 2;
            const cy = y * CELL_PX + CELL_PX / 2;
            ctx.fillStyle = '#ff4444';
            ctx.beginPath(); ctx.arc(cx, cy, CELL_PX / 2 - 2, 0, Math.PI * 2); ctx.fill();
            
            ctx.fillStyle = 'white';
            ctx.beginPath(); ctx.arc(cx - 3, cy - 3, 2, 0, Math.PI * 2); ctx.fill();
        }
    }

    // --- Chart & WebSocket Managers ---
    const charts = {};
    const wsConnections = {};

    function initChart(algoId, accentColor) {
        const ctx = document.getElementById(`chart-${algoId}`).getContext('2d');
        charts[algoId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Score',
                        data: [],
                        borderColor: accentColor,
                        backgroundColor: hexToRgba(accentColor, 0.1),
                        borderWidth: 2,
                        fill: true,
                        tension: 0.2, // smoother line
                        pointRadius: 0
                    },
                    {
                        label: 'Mean Score',
                        data: [],
                        borderColor: hexToRgba(accentColor, 0.6),
                        borderWidth: 2,
                        borderDash: [5, 5],
                        fill: false,
                        tension: 0.2,
                        pointRadius: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                scales: {
                    x: {
                        title: { display: true, text: 'Games', color: '#888899' },
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: '#888899', maxTicksLimit: 10 }
                    },
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'Score', color: '#888899' },
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: '#888899' },
                        suggestedMax: 50 // initial scale up to sensible number
                    }
                },
                plugins: { legend: { labels: { color: '#e2e2ec' } } }
            }
        });
    }

    class WSManager {
        constructor(algoId) {
            this.algoId = algoId;
            this.ws = null;
            this.accentColor = ACCENTS[algoId];
            this.canvasCtx = document.getElementById(`canvas-${algoId}`).getContext('2d');
            this.chart = charts[algoId];
            this.gameDataBuffer = [];
        }

        connect(speed) {
            const url = `ws://${window.location.host}/ws/${this.algoId}`;
            this.ws = new WebSocket(url);

            this.ws.onopen = () => {
                const msg = { type: "start", algo: this.algoId, speed: parseInt(speed) };
                this.ws.send(JSON.stringify(msg));
                this.updateUI(true);
            };

            this.ws.onmessage = (e) => {
                const data = JSON.parse(e.data);
                if (data.type === 'step') {
                    // 1. Draw frame
                    renderFrame(this.canvasCtx, data, this.accentColor);
                    
                    // 2. Update stats
                    document.getElementById(`stat-game-${this.algoId}`).textContent = data.game_no;
                    document.getElementById(`stat-score-${this.algoId}`).textContent = data.score;
                    document.getElementById(`stat-record-${this.algoId}`).textContent = data.record;
                    if(data.algo_stat) {
                        let v = data.algo_stat.value;
                        if (typeof v === 'number' && !Number.isInteger(v)) v = v.toFixed(2);
                        document.getElementById(`stat-algostat-${this.algoId}`).textContent = v;
                    }

                    // 3. Update chart if game done
                    if (data.done) {
                        const scoreData = this.chart.data.datasets[0].data;
                        const meanData = this.chart.data.datasets[1].data;
                        const labels = this.chart.data.labels;

                        labels.push(data.game_no);
                        scoreData.push(data.score);
                        meanData.push(data.mean_score);

                        // keep last 150 points for performance
                        if (labels.length > 150) {
                            labels.shift(); scoreData.shift(); meanData.shift();
                        }
                        this.chart.update();
                    }
                }
            };

            this.ws.onclose = () => { this.updateUI(false); this.ws = null; };
            this.ws.onerror = (err) => console.error(`[${this.algoId}] WS Error:`, err);
        }

        disconnect() {
            if (this.ws) {
                this.ws.send(JSON.stringify({ type: "stop" }));
                this.ws.close();
            }
        }

        setSpeed(newSpeed) {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({ type: "set_speed", speed: parseInt(newSpeed) }));
            }
        }

        updateUI(isPlaying) {
            document.getElementById(`play-${this.algoId}`).disabled = isPlaying;
            document.getElementById(`stop-${this.algoId}`).disabled = !isPlaying;
        }
    }

    // Attach to window so buttons can trigger them
    window.startAlgo = (algoId) => {
        if (!wsConnections[algoId]) wsConnections[algoId] = new WSManager(algoId);
        const speed = document.getElementById(`speed-${algoId}`).value;
        wsConnections[algoId].connect(speed);
    };

    window.stopAlgo = (algoId) => {
        if (wsConnections[algoId]) wsConnections[algoId].disconnect();
    };

    window.setSpeed = (algoId, speed) => {
        if (wsConnections[algoId]) wsConnections[algoId].setSpeed(speed);
    };

    // --- Init: Render blank boards, setup observers ---
    ALGOS.forEach(algo => {
        initChart(algo.id, ACCENTS[algo.id]);
        const ctx = document.getElementById(`canvas-${algo.id}`).getContext('2d');
        renderFrame(ctx, {}, ACCENTS[algo.id]);
    });

    // Sub-Task M3-03: IntersectionObserver for Sticky Nav highlighting
    const navPills = document.querySelectorAll('.nav-pill');
    const sections = document.querySelectorAll('.algo-section');
    const observer = new IntersectionObserver((entries) => {
      let isAnyIntersecting = false;
      entries.forEach(entry => {
        if (entry.isIntersecting) {
            navPills.forEach(p => p.classList.remove('active'));
            const activePill = document.querySelector(`.nav-pill[data-algo="${entry.target.dataset.algo}"]`);
            if (activePill) activePill.classList.add('active');
            isAnyIntersecting = true;
        }
      });
      // Fallback: If at very top, highlight pure-dqn.
      if (!isAnyIntersecting && window.scrollY < 200) {
          navPills.forEach(p => p.classList.remove('active'));
          document.querySelector('.nav-pill[data-algo="dqn"]').classList.add('active');
      }
    }, { threshold: 0.5, rootMargin: '-10% 0px -40% 0px' });
    sections.forEach(sec => observer.observe(sec));


    // --- Sub-Task M3-02: Hero Canvas Animation (Procedural Crawling Snake) ---
    const heroCanvas = document.getElementById('hero-canvas');
    const hctx = heroCanvas.getContext('2d');
    
    function resizeHero() {
      heroCanvas.width = heroCanvas.clientWidth;
      heroCanvas.height = heroCanvas.clientHeight;
    }
    window.addEventListener('resize', resizeHero);
    resizeHero();

    const particles = [];
    const pColors = Object.values(ACCENTS);
    for(let i=0; i<15; i++) {
        particles.push({
            x: Math.random() * innerWidth,
            y: Math.random() * innerHeight,
            vx: (Math.random() - 0.5) * 4,
            vy: (Math.random() - 0.5) * 4,
            color: pColors[i % pColors.length],
            history: [] // snake body tail
        });
    }

    function drawHero() {
      hctx.clearRect(0, 0, heroCanvas.width, heroCanvas.height);
      
      // Draw grid
      hctx.strokeStyle = 'rgba(255,255,255,0.015)';
      hctx.lineWidth = 1;
      const size = 30;
      for(let x=0; x<heroCanvas.width; x+=size) {
        hctx.beginPath(); hctx.moveTo(x,0); hctx.lineTo(x, heroCanvas.height); hctx.stroke();
      }
      for(let y=0; y<heroCanvas.height; y+=size) {
        hctx.beginPath(); hctx.moveTo(0,y); hctx.lineTo(heroCanvas.width, y); hctx.stroke();
      }

      // Draw snakes
      particles.forEach(p => {
         p.history.unshift({x: p.x, y: p.y});
         if(p.history.length > 20) p.history.pop();
         
         // bounce logic
         if(p.x <= 0 || p.x >= heroCanvas.width) { p.vx *= -1; }
         if(p.y <= 0 || p.y >= heroCanvas.height) { p.vy *= -1; }
         // minor wandering
         p.vx += (Math.random() - 0.5) * 0.2;
         p.vy += (Math.random() - 0.5) * 0.2;
         // clamp speed
         const spd = Math.hypot(p.vx, p.vy);
         if (spd > 3) { p.vx = (p.vx/spd)*3; p.vy = (p.vy/spd)*3;}

         p.x += p.vx;
         p.y += p.vy;
         
         // draw path line
         hctx.beginPath();
         for(let i=0; i<p.history.length; i++) {
           const pt = p.history[i];
           if(i===0) hctx.moveTo(pt.x, pt.y);
           else hctx.lineTo(pt.x, pt.y);
         }
         hctx.strokeStyle = p.color;
         hctx.lineWidth = 4;
         hctx.lineCap = 'round';
         hctx.lineJoin = 'round';
         hctx.globalAlpha = 0.5;
         hctx.stroke();
         
         // draw head
         hctx.globalAlpha = 1.0;
         hctx.beginPath();
         hctx.arc(p.x, p.y, 4, 0, Math.PI*2);
         hctx.fillStyle = p.color;
         hctx.fill();
      });
      requestAnimationFrame(drawHero);
    }
    drawHero();

  