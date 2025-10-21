import os
from pathlib import Path

# ad-bandit/ をルートとして固定
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = str(PROJECT_ROOT / "bandit.db")

N_ARMS = 10
AD_LABELS = [f"Ad-{i}" for i in range(N_ARMS)]