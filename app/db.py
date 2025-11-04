import sqlite3
from typing import List, Tuple
from .config import DB_PATH, N_ARMS, AD_LABELS

DDL_ARMS = """
CREATE TABLE IF NOT EXISTS arms (
  arm_id INTEGER PRIMARY KEY,
  label TEXT NOT NULL,
  alpha INTEGER NOT NULL,
  beta  INTEGER NOT NULL,
  impressions INTEGER NOT NULL,
  conversions INTEGER NOT NULL
);
"""

DDL_EVENTS = """
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts DATETIME DEFAULT CURRENT_TIMESTAMP,
  arm_id INTEGER NOT NULL,
  reward INTEGER NOT NULL,
  FOREIGN KEY(arm_id) REFERENCES arms(arm_id)
);
"""

# SQLite 接続
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# データベース初期化
def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(DDL_ARMS)
    cur.execute(DDL_EVENTS)
    # 初期レコードがなければ投入（Beta(1,1)）
    cur.execute("SELECT COUNT(*) FROM arms")
    (cnt,) = cur.fetchone()
    if cnt == 0:
        rows = [(i, AD_LABELS[i], 1, 1, 0, 0) for i in range(N_ARMS)]
        cur.executemany(
            "INSERT INTO arms(arm_id,label,alpha,beta,impressions,conversions) VALUES (?,?,?,?,?,?)",
            rows
        )

    conn.commit()
    conn.close()

# SELECT 一覧
def fetch_arms() -> List[Tuple[int, str, int, int, int, int]]:
  conn = get_conn()
  cur = conn.cursor()
  
  cur.execute("SELECT arm_id, label, alpha, beta, impressions, conversions FROM arms ORDER BY arm_id")
  rows = cur.fetchall()
  conn.close()
  
  return rows

# アップデート
def update_arm(arm_id: int, alpha_delta: int, beta_delta: int, imp_delta: int, conv_delta: int):
  conn = get_conn()
  cur = conn.cursor()
  
  cur.execute("""
        UPDATE arms
        SET alpha = alpha + ?, beta = beta + ?,
            impressions = impressions + ?, conversions = conversions + ?
        WHERE arm_id = ?
    """, (alpha_delta, beta_delta, imp_delta, conv_delta, arm_id))
  
  conn.commit()
  conn.close()
  
# 挿入
def insert_event(arm_id: int, reward: int):
  conn = get_conn()
  cur = conn.cursor()
  cur.execute("INSERT INTO events(arm_id) VALUES (?, ?)", (arm_id, reward))
  conn.commit()
  conn.close()
  
