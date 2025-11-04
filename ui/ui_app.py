# ui/ui_app.py 置き換え版（最小修正＋堅牢化）
import os
import requests
import pandas as pd
import streamlit as st

DEFAULT_API = "http://127.0.0.1:8000"  # ← ここを定義してから使う

st.set_page_config(page_title="Ad Bandit Dashboard", layout="wide")
st.title("📈 Ad Bandit Dashboard (Thompson Sampling)")

# --- Sidebar: API設定（環境変数 API_BASE があればそれを初期値に）
with st.sidebar:
    st.header("Settings")
    API_BASE = st.text_input("API base URL", os.environ.get("API_BASE", DEFAULT_API))
    st.caption("例) http://127.0.0.1:8000")

def safe_get_json(url: str, timeout: float = 3.0):
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.JSONDecodeError:
        st.error(f"APIがJSONを返していません: {url}\n本文: {r.text[:200]} ...")
    except requests.exceptions.RequestException as e:
        st.warning(f"APIに接続できません: {url}\n{e}")
    return None

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Current Posterior Means (α/(α+β))")
    stats = safe_get_json(f"{API_BASE}/stats")
    if stats:
        df = pd.DataFrame(stats["arms"]).sort_values("arm_id")
        st.bar_chart(df.set_index("label")["posterior_mean"])
        st.dataframe(
            df[["arm_id","label","impressions","conversions","posterior_mean","empirical_ctr"]],
            use_container_width=True
        )
    else:
        st.info("APIが未起動かエラーです。APIを起動してから再読み込みしてください。")

with col2:
    st.subheader("Get Next Ad")
    if st.button("🎯 Recommend Next Ad"):
        next_ad = safe_get_json(f"{API_BASE}/next_ad")
        if next_ad:
            st.success(f"Recommend: {next_ad['label']} (arm_id={next_ad['arm_id']})")
            st.caption("※ impressions は +1 済み。結果を /report で反映してください。")

            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ 成果あり (reward=1)"):
                    r = requests.post(f"{API_BASE}/report", json={"arm_id": next_ad["arm_id"], "reward": 1}).json()
                    st.write(r)
            with c2:
                if st.button("❌ 成果なし (reward=0)"):
                    r = requests.post(f"{API_BASE}/report", json={"arm_id": next_ad["arm_id"], "reward": 0}).json()
                    st.write(r)

st.divider()
st.caption("実運用: /next_ad で配信 → 結果を /report に送信。")
