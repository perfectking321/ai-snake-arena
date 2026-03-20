#!/bin/bash
source venv/bin/activate
echo "--- 1. Installing basics ---"
pip install fastapi uvicorn websockets numpy
echo "--- 2. Installing torch ---"
pip install torch --index-url https://download.pytorch.org/whl/cpu || pip install torch --index-url https://download.pytorch.org/whl/cpu --no-cache-dir
echo "--- 3. Verify installs ---"
python -c "import torch; print('torch OK:', torch.__version__)"
python -c "import fastapi; print('fastapi OK')"
python -c "import uvicorn; print('uvicorn OK')"
echo "--- 4. Verify imports ---"
python -c "import game.snake; print('snake OK')"
python -c "import game.state; print('state OK')"
python -c "import agents.rl_agent; print('rl_agent OK')"
python -c "import main; print('main OK')"
echo "--- 5. Starting server ---"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
