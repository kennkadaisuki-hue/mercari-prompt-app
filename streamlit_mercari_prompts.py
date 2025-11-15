# streamlit_mercari_prompts.py
import json
from textwrap import dedent

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="メルカリ出品サポート", layout="centered")
st.title("メルカリ出品サポート")
st.caption("モードを選んで必要事項を入力し、生成されたプロンプトをコピーしてください。")

MODE_OPTIONS = [
    ("unknown", "1. 不明商品モード"),
    ("name_lookup", "2. 商品名探索モード"),
    ("known_name", "3. 商品名がわかる出品サポート"),
    ("known_code", "4. 型番/JANがわかる出品サポート"),
]

if "prompts" not in st.session_state:
    st.session_state.prompts = {key: "" for key, _ in MODE_OPTIONS}

COPY_INSTRUCTION = (
    "それぞれ個別のコピー操作をするため、各項目のテキストが単独で使えるようコピー専用ブロックで出力してください。"
)


def store_prompt(mode_key: str, prompt: str) -> None:
    """Keep the latest prompt per mode so it survives reruns."""
    st.session_state.prompts[mode_key] = prompt
    st.toast("プロンプトを生成しました。下でコピーできます。")


def render_copy_button(prompt: str) -> None:
    """Custom HTML button so the clipboard copy also works on mobile."""
    safe_text = json.dumps(prompt)
    components.html(
        f"""
        <div style="display:flex; justify-content:flex-end; width:100%; margin-bottom:0.3rem;">
          <button
            style="background-color:#ff6b6b;border:none;border-radius:8px;
                   color:white;font-size:1rem;padding:0.55rem 1.4rem;cursor:pointer;"
            onclick='navigator.clipboard.writeText({safe_text}).then(() => {{
              const toast = document.createElement("div");
              toast.textContent = "コピーしました";
              toast.style.position = "fixed";
              toast.style.bottom = "24px";
              toast.style.left = "50%";
              toast.style.transform = "translateX(-50%)";
              toast.style.background = "#323232";
              toast.style.color = "#fff";
              toast.style.padding = "0.6rem 1.2rem";
              toast.style.borderRadius = "999px";
              toast.style.zIndex = "9999";
              document.body.appendChild(toast);
              setTimeout(() => toast.remove(), 1800);
            }})'>
            コピー
          </button>
        </div>
        """,
        height=70,
        scrolling=False,
    )


NAME_LOOKUP_PROMPT = dedent(
    """
    アップロードされた画像（2枚程度）をもとにできるだけ正確な商品名を探し出す。
    （プロンプト: この商品の商品名を教えて下さい。確証がない場合は候補を3つ程度上げてください。
    そのときJANコードも教えてほしいです。）
    """
).strip()


def render_unknown_mode() -> None:
    st.write("商品情報がほとんど無いときに使うテンプレートです。")
    notes = st.text_area(
        "特徴・注意事項",
        placeholder="例: 付属品の欠品、動作確認済み内容など",
        key="unknown-notes",
    )
    if st.button("プロンプトを表示", use_container_width=True, key="btn-unknown"):
        notes_instruction = (
            f"商品説明の冒頭には次の特徴・注意事項を丁寧に書いてください: {notes.strip()}"
            if notes.strip()
            else "商品説明の冒頭で購入者が知りたい特徴・注意事項を丁寧に説明してください。"
        )
        prompt = dedent(
            f"""
            メルカリに商品を出品します。画像などをもとに商品名～最低価格までをAIに検索し、
            以下の項目について類似の商品から購入しやすいようにそれぞれシンプルにまとめてください。
            以下のように表示してください。
            商品説明は写真を参考に売れやすい文句を考えてください
            商品名:
            カテゴリー:
            型番:
            商品の説明:
            最低価格:
            あと、同様の商品が売れていたら最低販売済み価格を表示してください。
            {notes_instruction}
            {COPY_INSTRUCTION}
            絵文字は登録できません。
            """
        ).strip()
        store_prompt("unknown", prompt)


def render_name_lookup_mode() -> None:
    st.write("画像から商品名やJAN候補を洗い出したいときに利用します。")
    if st.button("プロンプトを表示", use_container_width=True, key="btn-name-lookup"):
        store_prompt("name_lookup", NAME_LOOKUP_PROMPT)


def render_known_name_mode() -> None:
    st.write("商品名が決まっている場合の簡易入力モードです。")
    manufacturer = st.text_input("メーカー名", key="known-name-maker")
    product_name = st.text_input("商品名", key="known-name-product")
    notes = st.text_area(
        "特徴・注意事項",
        placeholder="例: 使用回数、キズ有無、付属品など",
        key="known-name-notes",
    )

    if st.button("プロンプトを表示", use_container_width=True, key="btn-known-name"):
        if not product_name.strip():
            st.warning("商品名を入力してください。")
            return
        maker_label = f"{manufacturer.strip()}の" if manufacturer.strip() else ""
        notes_instruction = (
            f"商品説明の最初に以下の特徴・注意事項を丁寧に記載してください: {notes.strip()}"
            if notes.strip()
            else "商品説明の最初に商品の状態や注意点を丁寧に記載してください。"
        )
        prompt = dedent(
            f"""
            メルカリに商品を出品します。以下の項目について類似の商品から購入しやすいようにそれぞれ
            シンプルにまとめてもらいたいと思います。出品の商品は{maker_label}{product_name.strip()}です。
            以下のように表示してください【商品名】【カテゴリー】【型番】【商品説明】【最低価格】
            あと、同様の商品が売れていたら最低販売済み価格を表示してください。
            {notes_instruction}
            {COPY_INSTRUCTION}
            """
        ).strip()
        store_prompt("known_name", prompt)


def render_known_code_mode() -> None:
    st.write("型番やJANコードまで把握しているときの詳細モードです。")
    manufacturer = st.text_input("メーカー名", key="known-code-maker")
    product_name = st.text_input("商品名", key="known-code-product")
    model_code = st.text_input("型番", key="known-code-model")
    jan_code = st.text_input("JANコード", key="known-code-jan")
    notes = st.text_area(
        "特徴・注意事項",
        placeholder="例: コンディション、付属品、注意すべきポイントなど",
        key="known-code-notes",
    )

    if st.button("プロンプトを表示", use_container_width=True, key="btn-known-code"):
        missing = [label for label, value in [
            ("商品名", product_name),
            ("型番", model_code),
            ("JANコード", jan_code),
        ] if not value.strip()]
        if missing:
            st.warning(" / ".join(missing) + " を入力してください。")
            return

        maker_label = f"{manufacturer.strip()}の" if manufacturer.strip() else ""
        notes_instruction = (
            f"商品説明の最初に以下の特徴・注意事項を丁寧に記載してください: {notes.strip()}"
            if notes.strip()
            else "商品説明の最初に商品の状態や注意点を丁寧に記載してください。"
        )
        prompt = dedent(
            f"""
            メルカリに商品を出品します。以下の項目について類似の商品から購入しやすいようにそれぞれ
            シンプルにまとめてもらいたいと思います。出品の商品は{maker_label}{product_name.strip()}で、
            型番は{model_code.strip()}です。JANコードは{jan_code.strip()}です。
            以下のように表示してください【商品名】【カテゴリー】【型番】【商品説明】【最低価格】
            あと、同様の商品が売れていたら最低販売済み価格を表示してください。
            {notes_instruction}
            {COPY_INSTRUCTION}
            """
        ).strip()
        store_prompt("known_code", prompt)


mode_labels = [label for _, label in MODE_OPTIONS]
selected_label = st.selectbox("モードを選択", mode_labels)
current_mode = next(key for key, label in MODE_OPTIONS if label == selected_label)

with st.container():
    if current_mode == "unknown":
        render_unknown_mode()
    elif current_mode == "name_lookup":
        render_name_lookup_mode()
    elif current_mode == "known_name":
        render_known_name_mode()
    else:
        render_known_code_mode()

current_prompt = st.session_state.prompts.get(current_mode, "")

st.divider()
if current_prompt:
    st.markdown("#### 生成されたプロンプト")
    render_copy_button(current_prompt)
    text_height = min(500, max(220, len(current_prompt) // 2))
    st.text_area(
        "生成されたプロンプト",
        value=current_prompt,
        height=text_height,
        label_visibility="collapsed",
    )
else:
    st.info("各モードのボタンを押すとプロンプトが表示されます。")
