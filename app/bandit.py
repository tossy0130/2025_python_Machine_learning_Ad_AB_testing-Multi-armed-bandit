import numpy as np
from typing import List, Tuple
from .db import fetch_arms

class BernoulliThompsonBandit:
    """ 報酬のトンプソンサンプリング（10アーム） """
    def __init__(self):
        pass
    
    def sample_thetas(self) -> Tuple[int, List[float]]:
        rows = fetch_arms()
        
        alphas = np.array([r[2] for r in rows], dtype=float)
        betas = np.array([r[3] for r in rows], dtype=float)
        thetas = np.random.beta(alphas, betas)
        best_idx = int(np.argmax(thetas)) 
        best_arm_id = rows[best_idx][0]
        
        return best_arm_id, thetas.tolist()
        
    @staticmethod
    def posterior_means() -> List[float]:
        rows = fetch_arms()
        means = [(r[2]) / (r[2] + r[3]) for r in rows]
        
        return means