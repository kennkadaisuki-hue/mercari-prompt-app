import datetime as dt

import streamlit as st

from utils import nav, storage


st.set_page_config(
    page_title="日記を書く／編集",
    page_icon="✍️",
    layout="centered",
    menu_items=None,
)

nav.sidebar("日記を書く／編集")
st.title("✍️ 日記を書く／編集")

selected_date = st.date_input("日付", value=dt.date.today())
date_str = selected_date.isoformat()
existing = storage.get_diary(date_str)

if existing:
    st.info(f"{date_str} の既存データを読み込みました。")

with st.form("diary_form"):
    cooking = st.text_area("料理", value=existing.get("料理", "") if existing else "", height=120)
    work = st.text_area("仕事", value=existing.get("仕事", "") if existing else "", height=120)
    youtube = st.number_input(
        "YouTube視聴時間（h）",
        min_value=0.0,
        format="%.1f",
        value=float(existing.get("youtube", 0.0)) if existing else 0.0,
        step=0.5,
    )
    yande = st.text_area("やる / できなかった", value=existing.get("やるでき", "") if existing else "", height=80)
    person = st.text_area("人（会った・関わった）", value=existing.get("人", "") if existing else "", height=80)
    reflection = st.text_area("反省・学び", value=existing.get("反省", "") if existing else "", height=120)

    submitted = st.form_submit_button("保存する", use_container_width=True)

if submitted:
    entry = {
        "date": date_str,
        "料理": cooking,
        "仕事": work,
        "youtube": youtube,
        "やるでき": yande,
        "人": person,
        "反省": reflection,
    }
    try:
        storage.upsert_diary(entry)
        st.success("保存しました。")
        st.rerun()
    except storage.StorageError as exc:
        st.error(str(exc))
