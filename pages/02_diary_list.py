import streamlit as st

from utils import nav, storage


st.set_page_config(
    page_title="日記一覧／検索",
    page_icon="📜",
    layout="centered",
    menu_items=None,
)

nav.sidebar("日記一覧／検索")
st.title("📜 日記一覧／検索")

diaries = storage.load_diaries()

if not diaries:
    st.info("まだ日記がありません。")
    st.stop()

keyword = st.text_input("キーワード検索（人名・出来事など）", placeholder="例: 石田くん, 料理")

filtered = diaries
if keyword:
    filtered = storage.search_diaries(keyword)
    st.caption(f"{len(filtered)} 件ヒット")

for entry in sorted(filtered, key=lambda x: x["date"], reverse=True):
    with st.expander(f"{entry['date']} ｜ {entry.get('仕事', '')[:20]}"):
        st.write(f"更新: {entry.get('updated_at', 'N/A')}")
        st.write(f"料理: {entry.get('料理', '')}")
        st.write(f"仕事: {entry.get('仕事', '')}")
        st.write(f"YouTube: {entry.get('youtube', 0)} 時間")
        st.write(f"やる/でき: {entry.get('やるでき', '')}")
        st.write(f"人: {entry.get('人', '')}")
        st.write(f"反省: {entry.get('反省', '')}")

st.page_link("pages/01_diary.py", label="✍️ この日記を編集するには「日付」を指定して保存してください", use_container_width=True)
