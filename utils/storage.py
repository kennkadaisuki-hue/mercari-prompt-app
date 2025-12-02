import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import streamlit as st
except ImportError:  # pragma: no cover - only for non-streamlit contexts
    st = None  # type: ignore


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DIARY_FILE = DATA_DIR / "diaries.json"
MINDMAP_FILE = DATA_DIR / "mindmap.json"

SHEETS_CONFIG = {}
if st is not None:
    SHEETS_CONFIG = st.secrets.get("gcp", {})  # type: ignore[attr-defined]
SHEET_KEY = SHEETS_CONFIG.get("sheet_key") or SHEETS_CONFIG.get("sheet_id")
SHEETS_ENABLED = bool(SHEET_KEY)

HEADERS = ["date", "料理", "仕事", "youtube", "やるでき", "人", "反省", "updated_at"]


class StorageError(Exception):
    """Raised when persistence failed."""


def _now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def load_diaries() -> List[Dict[str, Any]]:
    if SHEETS_ENABLED:
        try:
            return _load_diaries_from_sheet()
        except Exception as exc:  # pragma: no cover - Google Sheets optional
            raise StorageError(f"Google Sheets からの読み込みに失敗しました: {exc}") from exc

    if not DIARY_FILE.exists():
        return []
    try:
        with DIARY_FILE.open("r", encoding="utf-8") as f:
            diaries = json.load(f)
            if not isinstance(diaries, list):
                return []
            return sorted(diaries, key=lambda x: x.get("date", ""))
    except Exception as exc:  # pragma: no cover - defensive
        raise StorageError(f"日記データの読み込みに失敗しました: {exc}") from exc


def save_diaries(diaries: List[Dict[str, Any]]) -> None:
    if SHEETS_ENABLED:
        # Sheets運用時はローカル保存しない
        return
    try:
        with DIARY_FILE.open("w", encoding="utf-8") as f:
            json.dump(diaries, f, ensure_ascii=False, indent=2)
    except Exception as exc:
        raise StorageError(f"日記データの保存に失敗しました: {exc}") from exc


def get_diary(date_str: str) -> Optional[Dict[str, Any]]:
    return next((d for d in load_diaries() if d.get("date") == date_str), None)


def upsert_diary(entry: Dict[str, Any]) -> Dict[str, Any]:
    entry = {**entry, "updated_at": _now_str()}
    if SHEETS_ENABLED:
        try:
            _upsert_sheet(entry)
        except Exception as exc:  # pragma: no cover - Google Sheets optional
            raise StorageError(f"Google Sheets への書き込みに失敗しました: {exc}") from exc
        return entry

    diaries = load_diaries()
    existing_idx = next((i for i, d in enumerate(diaries) if d.get("date") == entry["date"]), None)
    if existing_idx is None:
        diaries.append(entry)
    else:
        diaries[existing_idx] = entry
    diaries = sorted(diaries, key=lambda x: x["date"])
    save_diaries(diaries)
    if SHEETS_ENABLED:
        try:
            _sync_to_sheet(entry)
        except Exception as exc:  # pragma: no cover - Google Sheets optional
            if st:
                st.warning(f"Google Sheets への同期に失敗しました: {exc}")
    return entry


def list_missing_dates(diaries: List[Dict[str, Any]], lookback_days: int = 30) -> List[str]:
    existing_dates = {d.get("date") for d in diaries}
    today = date.today()
    missing: List[str] = []
    for i in range(lookback_days + 1):
        d = today - timedelta(days=i)
        ds = d.isoformat()
        if ds not in existing_dates:
            missing.append(ds)
    missing.sort()
    return missing


def search_diaries(keyword: str) -> List[Dict[str, Any]]:
    keyword_lower = keyword.lower()
    results: List[Dict[str, Any]] = []
    for diary in load_diaries():
        for key, value in diary.items():
            if key == "updated_at":
                continue
            if keyword_lower in str(value).lower():
                results.append(diary)
                break
    return sorted(results, key=lambda x: x["date"], reverse=True)


def load_mindmap() -> Dict[str, Any]:
    if not MINDMAP_FILE.exists():
        return {"content": "", "updated_at": ""}
    try:
        with MINDMAP_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return {"content": "", "updated_at": ""}
            return data
    except Exception as exc:  # pragma: no cover - defensive
        raise StorageError(f"マインドマップの読み込みに失敗しました: {exc}") from exc


def save_mindmap(content: str) -> Dict[str, Any]:
    mindmap = {"content": content, "updated_at": _now_str()}
    try:
        with MINDMAP_FILE.open("w", encoding="utf-8") as f:
            json.dump(mindmap, f, ensure_ascii=False, indent=2)
    except Exception as exc:
        raise StorageError(f"マインドマップの保存に失敗しました: {exc}") from exc
    return mindmap


def _sheet_client():
    import gspread  # type: ignore

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_json = SHEETS_CONFIG.get("service_account_json")
    if not creds_json:
        raise StorageError("Google Sheets 用の service_account_json が secrets にありません。")
    return gspread.service_account_from_dict(creds_json, scopes=scope)


def _ensure_header(ws) -> None:
    values = ws.get_all_values()
    if not values:
        ws.append_row(HEADERS)
        return
    if values[0] != HEADERS:
        ws.update("A1:H1", [HEADERS])


def _load_diaries_from_sheet() -> List[Dict[str, Any]]:
    gc = _sheet_client()
    sh = gc.open_by_key(SHEET_KEY)
    ws = sh.sheet1
    _ensure_header(ws)
    records = ws.get_all_records()
    diaries: List[Dict[str, Any]] = []
    for row in records:
        # 既存シートのキーを安全に取り出し、型を調整
        diary = {h: row.get(h, "") for h in HEADERS}
        diary["date"] = str(diary.get("date", ""))
        try:
            diary["youtube"] = float(diary.get("youtube", 0)) if diary.get("youtube") != "" else 0.0
        except Exception:
            diary["youtube"] = 0.0
        diaries.append(diary)
    return sorted(diaries, key=lambda x: x.get("date", ""), reverse=True)


def _upsert_sheet(entry: Dict[str, Any]) -> None:
    gc = _sheet_client()
    sh = gc.open_by_key(SHEET_KEY)
    ws = sh.sheet1
    _ensure_header(ws)

    records = ws.get_all_records()
    dates = [row.get("date") for row in records]
    row_values = [entry.get(h, "") for h in HEADERS]

    if entry["date"] in dates:
        idx = dates.index(entry["date"]) + 2  # 1-based, header is row 1
        ws.update(f"A{idx}:H{idx}", [row_values])
    else:
        # 新規はヘッダー直下に挿入して最新を上に
        ws.insert_row(row_values, index=2, value_input_option="USER_ENTERED")
