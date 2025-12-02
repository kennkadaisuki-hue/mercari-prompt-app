import json
from typing import Dict

import streamlit as st
from openai import OpenAI


def _client() -> OpenAI:
    api_key = st.secrets.get("openai", {}).get("api_key")
    if not api_key:
        raise ValueError("OpenAI APIキーが設定されていません (.streamlit/secrets.toml を確認してください)。")
    return OpenAI(api_key=api_key)


def build_prompt(mindmap: Dict, diary: Dict) -> str:
    mindmap_text = mindmap.get("content") or "未入力"
    diary_text = json.dumps(diary, ensure_ascii=False, indent=2)
    return f"""
あなたは目標達成まで伴走するアドバイザーです。
以下のマインドマップと日記データをもとに、
・よくできたこと
・もっと効率的にできたこと
・改善ポイント
・明日のアドバイス
・理想の自分に対する進歩
を簡潔に箇条書きでまとめてください。

# マインドマップ
{mindmap_text}

# 日記データ
{diary_text}
""".strip()


def generate_reflection(mindmap: Dict, diary: Dict, model: str = "gpt-4o-mini") -> str:
    prompt = build_prompt(mindmap, diary)
    client = _client()
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "あなたは思慮深く具体的な日本語のコーチです。"},
                {"role": "user", "content": prompt},
            ],
        )
        return resp.choices[0].message.content or ""
    except Exception as exc:
        raise RuntimeError(f"AI振り返りの生成に失敗しました: {exc}") from exc
