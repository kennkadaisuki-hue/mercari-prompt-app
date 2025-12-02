import streamlit as st


def sidebar(active: str = "") -> None:
    st.sidebar.subheader("メニュー")
    st.sidebar.page_link("main.py", label="🏠 ホーム")
    st.sidebar.page_link("pages/01_diary.py", label="✍️ 日記を書く／編集")
    st.sidebar.page_link("pages/02_diary_list.py", label="📜 日記一覧／検索")
    st.sidebar.page_link("pages/03_mindmap.py", label="🧠 マインドマップ管理")
    st.sidebar.page_link("pages/04_ai_export.py", label="🤖 AIへ")
    if active:
        st.sidebar.caption(f"現在: {active}")
