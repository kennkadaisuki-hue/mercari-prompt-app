import json

import streamlit as st

from utils import nav, storage


st.set_page_config(
    page_title="AIへ",
    page_icon="🤖",
    layout="centered",
    menu_items=None,
)

nav.sidebar("AIへ")
st.title("🤖 AIへ（コピー用プロンプト生成）")

diaries = storage.load_diaries()
mindmap = storage.load_mindmap()

if not diaries:
    st.info("日記データがまだありません。先に日記を登録してください。")
    st.stop()

# シート全件をそのままテキスト化
diary_text = json.dumps(diaries, ensure_ascii=False, indent=2)

prompt_template = f"""#役割
目標達成までの伴奏してくれるアドバイザーです。
#命令
今までのアドバイスをもとにマインドマップを作成し、取り組み始めました。
昨日までの結果もふくめ、よくできたことを上げたり、もっと効率的にできたことなど気がついたことがあればアドバイスを箇条書きにしてください。
#文脈
マインドマップ
{mindmap.get('content','')}
日記
{diary_text}
""".strip()

st.subheader("生成されたプロンプト")
st.code(prompt_template, language="text")
st.download_button(
    label="テキストをダウンロード",
    data=prompt_template,
    file_name="ai_prompt.txt",
    mime="text/plain",
    use_container_width=True,
)

st.caption("上のコピーアイコンまたはダウンロードボタンでAIに貼り付けてください。")
