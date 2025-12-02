import streamlit as st

from utils import nav, storage


st.set_page_config(
    page_title="マインドマップ管理",
    page_icon="🧠",
    layout="centered",
    menu_items=None,
)

nav.sidebar("マインドマップ管理")
st.title("🧠 マインドマップ管理")

mindmap = storage.load_mindmap()

st.caption(f"最終更新: {mindmap.get('updated_at') or '未設定'}")

with st.form("mindmap_form"):
    content = st.text_area(
        "理想の自分 マインドマップ（テキスト）",
        value=mindmap.get("content", ""),
        height=400,
        placeholder="- 健康\n- 仕事\n- 家族\n- 学び\n...",
    )
    submitted = st.form_submit_button("更新する", use_container_width=True)

if submitted:
    try:
        updated = storage.save_mindmap(content)
        st.success(f"保存しました（{updated['updated_at']}）")
    except storage.StorageError as exc:
        st.error(str(exc))
