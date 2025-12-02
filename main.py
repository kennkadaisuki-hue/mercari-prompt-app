import datetime as dt

import streamlit as st

from utils import nav, storage


st.set_page_config(
    page_title="日記 × 目標管理",
    page_icon="📝",
    layout="centered",
    menu_items=None,
)

nav.sidebar("ホーム")

st.title("日記 × 目標管理")
st.caption("スマホで完結する日記と目標の伴走アプリ")

diaries = storage.load_diaries()
missing = storage.list_missing_dates(diaries, lookback_days=14)

st.header("メニュー", divider=True)
cols = st.columns(2)
cols[0].page_link("pages/01_diary.py", label="✍️ 日記を書く／編集", use_container_width=True)
cols[1].page_link("pages/03_mindmap.py", label="🧠 マインドマップ管理", use_container_width=True)
cols = st.columns(2)
cols[0].page_link("pages/02_diary_list.py", label="📜 日記一覧／検索", use_container_width=True)
cols[1].page_link("pages/04_ai_export.py", label="🤖 AIへ（コピー用）", use_container_width=True)

if missing:
    st.warning(f"未記入日があります: {', '.join(missing)}")
else:
    st.success("直近2週間はすべて記入済みです。")

st.header("最新の記録", divider="rainbow")
if diaries:
    latest = sorted(diaries, key=lambda x: x["date"], reverse=True)[0]
    st.write(f"日付: {latest['date']}（更新: {latest.get('updated_at', 'N/A')}）")
    st.markdown(
        f"""
        - 料理: {latest.get('料理', '')}
        - 仕事: {latest.get('仕事', '')}
        - YouTube: {latest.get('youtube', 0)} 時間
        - やる/でき: {latest.get('やるでき', '')}
        - 人: {latest.get('人', '')}
        - 反省: {latest.get('反省', '')}
        """.strip()
    )
else:
    st.info("まだ日記がありません。まずは「日記を書く／編集」から始めましょう。")

st.header("最近のアクティビティ", divider=True)
recent = sorted(diaries, key=lambda x: x["date"], reverse=True)[:5]
for entry in recent:
    st.write(
        f"{entry['date']}｜料理: {entry.get('料理', '')}｜仕事: {entry.get('仕事', '')}｜YouTube: {entry.get('youtube', 0)}h"
    )

st.caption("OpenAI APIキーは .streamlit/secrets.toml に設定してください。")
