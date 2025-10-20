from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Dict, Any
from .db import init_db, fetch_arms, update_arm, insert_event
from .bandit import BernoulliThompsonBandit

app = FastAPI(title="advertisement_API", version="1.0")

class ReportIn(BaseModel):
    arm_id: int = Field(..., ge=0)
    reward: int = Field(..., ge=0, le=1)
    
@app.on_event("startup")
def startup():
    init_db() # Sqllite 初期化処理
    
@app.get("/next_ad")
def next_ad() -> Dict[str, Any]:
    bandit = BernoulliThompsonBandit()
    arm_id, thetas = bandit.sample_thetas()
      # 露出1回をカウント（impressions +1）。rewardは後ほどreportで反映。
    update_arm(arm_id=arm_id, alpha_delta=0, beta_delta=0, imp_delta=1, conv_delta=0)
    rows = fetch_arms()
    label = next(r[1] for r in rows if r[0] == arm_id)
    return {"arm_id": arm_id, "label": label, "debug_thetas": thetas}

@app.post("/report")
def report(inp: ReportIn) -> Dict[str, Any]:
    reward = int(inp.reward)
    # 報告イベントを保存
    insert_event(arm_id=inp.arm_id, reward=reward)
    # ベイズ更新（reward=1ならalpha+1、0ならbeta+1）
    alpha_delta = 1 if reward == 1 else 0
    beta_delta  = 1 if reward == 0 else 0
    update_arm(inp.arm_id, alpha_delta=alpha_delta, beta_delta=beta_delta, imp_delta=0, conv_delta=reward)
    return {"status": "ok", "updated_arm": inp.arm_id, "reward": reward}

@app.get("/stats")
def stats() -> Dict[str, Any]:
    rows = fetch_arms()
    # 便利なサマリ
    data = []
    for (arm_id, label, alpha, beta, imp, conv) in rows:
        mean = alpha / (alpha + beta)
        data.append({
            "arm_id": arm_id,
            "label": label,
            "alpha": alpha,
            "beta": beta,
            "posterior_mean": mean,
            "impressions": imp,
            "conversions": conv,
            "empirical_ctr": (conv/imp) if imp > 0 else None
        })
    best = max(data, key=lambda d: d["posterior_mean"])
    return {"arms": data, "best_by_posterior": best}