import requests
import pandas as pd
import streamlit as st

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="アドバンディットダッシュボード", layout="wide")
st.title("📈 アドバンディットダッシュボード (トンプソンサンプリング)")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Current Posterior Means (α/(α+β))")
    stats = requests.get(f"{API_BASE}/stats").json()
    df = pd.DataFrame(stats["arms"]).sort_values("arm_id")
    st.bar_chart(df.set_index("label")["posterior_mean"])
    st.dataframe(df[["arm_id","label","impressions","conversions","posterior_mean","empirical_ctr"]], use_container_width=True)

with col2:
    st.subheader("Get Next Ad")
    if st.button("🎯 Recommend Next Ad"):
        next_ad = requests.get(f"{API_BASE}/next_ad").json()
        st.success(f"Recommend: {next_ad['label']} (arm_id={next_ad['arm_id']})")
        st.caption("※ impressions は +1 済み。結果を報告してください。")
        
        # 成果報告UI（学習テスト用）
        success = st.button("✅ 成果あり (reward=1)")
        fail    = st.button("❌ 成果なし (reward=0)")
        if success:
            r = requests.post(f"{API_BASE}/report", json={"arm_id": next_ad["arm_id"], "reward": 1}).json()
            st.write(r)
        if fail:
            r = requests.post(f"{API_BASE}/report", json={"arm_id": next_ad["arm_id"], "reward": 0}).json()
            st.write(r)
            
st.divider()
# 実運用では、/next_ad で選ばれた広告を配信 → その結果を /report に送る流れで統合する。
st.caption("OKOKOK")