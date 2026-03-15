"""
b→dash CS支援 - マルチエージェント Streamlit Web UI
要件定義Agent → 実装Agent を1画面で連続利用
"""

import streamlit as st
import os
import yaml
import json
import io
from anthropic import Anthropic

# ページ設定
st.set_page_config(
    page_title="b→dash CS支援",
    page_icon="🚀",
    layout="wide",
)

# ========================================
# カスタムCSS（b→dash風デザイン）
# ========================================
st.markdown("""
<style>
/* --- ライトモード強制 & 全体 --- */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans JP', 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', 'Meiryo', sans-serif !important;
}

/* --- ライトモード --- */
[data-theme="light"] [data-testid="stAppViewContainer"],
[data-theme="light"] [data-testid="stApp"],
[data-theme="light"] .main {
    color: #2c3e50 !important;
    background-color: #f0f8ff !important;
}
[data-theme="light"] [data-testid="stHeader"] {
    background-color: #f0f8ff !important;
}

/* --- ダークモード --- */
[data-theme="dark"] [data-testid="stAppViewContainer"],
[data-theme="dark"] [data-testid="stApp"],
[data-theme="dark"] .main {
    color: #e8e8e8 !important;
    background-color: #0f0f0f !important;
}
[data-theme="dark"] [data-testid="stHeader"] {
    background-color: #0f0f0f !important;
}

/* --- サイドバー --- */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div {
    background: #38BDF8 !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #fff !important;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stMarkdown p {
    color: rgba(255,255,255,0.9) !important;
}
[data-testid="stSidebar"] .stDivider {
    border-color: rgba(255,255,255,0.3) !important;
}

/* --- サイドバーボタン --- */
[data-testid="stSidebar"] .stButton > button {
    border-radius: 8px;
    font-weight: 500;
    font-size: 14px;
    transition: all 0.2s ease;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: rgba(255,255,255,0.95) !important;
    border: none !important;
    color: #0284C7 !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.1);
}
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    background: #fff !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.2) !important;
    border: 1px solid rgba(255,255,255,0.4) !important;
    color: #fff !important;
}
[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.3) !important;
}

/* --- サイドバーinfoボックス --- */
[data-testid="stSidebar"] [data-testid="stAlert"] {
    background: rgba(255,255,255,0.9) !important;
    border: none !important;
    color: #0C4A6E !important;
}

/* --- サイドバー入力欄 --- */
[data-testid="stSidebar"] input {
    background: rgba(255,255,255,0.9) !important;
    color: #2c3e50 !important;
    border: 1px solid rgba(255,255,255,0.5) !important;
    border-radius: 6px !important;
}

/* --- サイドバー ファイルアップローダー --- */
[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.9) !important;
    border-radius: 8px !important;
    padding: 8px !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploader"] p,
[data-testid="stSidebar"] [data-testid="stFileUploader"] span,
[data-testid="stSidebar"] [data-testid="stFileUploader"] div,
[data-testid="stSidebar"] [data-testid="stFileUploader"] small,
[data-testid="stSidebar"] [data-testid="stFileUploader"] section {
    color: #2c3e50 !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploader"] button {
    color: #0284C7 !important;
    border-color: #0284C7 !important;
}

/* --- サイドバー セレクトボックス --- */
[data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb] {
    background: rgba(255,255,255,0.9) !important;
    color: #2c3e50 !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb] * {
    color: #2c3e50 !important;
}

/* --- メインエリア --- */
.main .block-container {
    padding-top: 2rem;
    max-width: 960px;
}

/* --- チャットメッセージ --- */
[data-testid="stChatMessage"] {
    background: #fff !important;
    border: 1px solid #d6ecf9 !important;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 1px 4px rgba(91,184,232,0.08);
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div {
    color: #2c3e50 !important;
}

/* --- ユーザーメッセージ --- */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: #eaf5fc !important;
    border-color: #c5e2f2 !important;
}

/* --- テーブル --- */
table {
    border-collapse: collapse;
    width: 100%;
    font-size: 14px;
    margin: 0.75rem 0;
    background: #fff;
    border-radius: 8px;
    overflow: hidden;
}
th {
    background: #5bb8e8 !important;
    color: #fff !important;
    font-weight: 500;
    padding: 10px 14px;
    text-align: left;
    border: none;
}
td {
    padding: 9px 14px;
    border-bottom: 1px solid #e8f4fd;
    color: #2c3e50 !important;
}
tr:nth-child(even) td {
    background: #f5fafd;
}
tr:hover td {
    background: #eaf5fc;
}

/* --- 入力欄エリア（外側含む全面） --- */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottom"] > div > div {
    background: #1B6478 !important;
    padding: 0 !important;
    margin: 0 !important;
    border: none !important;
}
[data-testid="stBottom"] {
    padding: 12px 16px !important;
}
[data-testid="stChatInput"] {
    background: #1B6478 !important;
    border-radius: 12px !important;
    border: none !important;
    padding: 4px !important;
}
[data-testid="stChatInput"] textarea,
[data-testid="stBottom"] textarea {
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    font-size: 15px;
    padding: 12px 16px;
    background: rgba(255,255,255,0.95) !important;
    color: #1a1a1a !important;
}
[data-testid="stChatInput"] textarea::placeholder,
[data-testid="stBottom"] textarea::placeholder {
    color: #6b7280 !important;
}
[data-testid="stChatInput"] textarea:focus,
[data-testid="stBottom"] textarea:focus {
    border: 1px solid rgba(255,255,255,0.5) !important;
    background: #fff !important;
    box-shadow: none !important;
    color: #1a1a1a !important;
}
[data-testid="stChatInput"] button,
[data-testid="stBottom"] button {
    color: #fff !important;
    background: rgba(255,255,255,0.2) !important;
    border-radius: 8px !important;
}

/* --- 引き継ぎexpander --- */
.streamlit-expanderHeader {
    background: #eaf5fc !important;
    border-radius: 8px;
    font-weight: 500;
    color: #1a6b9c !important;
}

/* --- info/warning ボックス --- */
[data-testid="stAlert"] {
    border-radius: 8px;
    font-size: 14px;
}

/* --- スピナー --- */
.stSpinner > div {
    border-top-color: #5bb8e8 !important;
}

/* --- h1タイトル --- */
h1 {
    font-weight: 700 !important;
    color: #1a6b9c !important;
    letter-spacing: -0.02em;
}
h2, h3 {
    color: #2c7fb0 !important;
}

/* --- リセットボタン --- */
[data-testid="stSidebar"] .stButton:last-child > button {
    background: rgba(255,255,255,0.15) !important;
    color: #fff !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
}
[data-testid="stSidebar"] .stButton:last-child > button:hover {
    background: rgba(255,80,80,0.2) !important;
    border-color: rgba(255,80,80,0.4) !important;
}

/* --- ダークモード: サイドバー --- */
[data-theme="dark"] [data-testid="stSidebar"],
[data-theme="dark"] [data-testid="stSidebar"] > div {
    background: #38BDF8 !important;
}

/* --- ダークモード: チャットメッセージ --- */
[data-theme="dark"] [data-testid="stChatMessage"] {
    background: #1a1a1a !important;
    border-color: #333 !important;
}
[data-theme="dark"] [data-testid="stChatMessage"] p,
[data-theme="dark"] [data-testid="stChatMessage"] li,
[data-theme="dark"] [data-testid="stChatMessage"] span,
[data-theme="dark"] [data-testid="stChatMessage"] div {
    color: #e8e8e8 !important;
}
[data-theme="dark"] [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: #1f2937 !important;
    border-color: #374151 !important;
}

/* --- ダークモード: テーブル --- */
[data-theme="dark"] table {
    background: #1a1a1a;
}
[data-theme="dark"] td {
    color: #e8e8e8 !important;
    border-bottom-color: #333 !important;
}
[data-theme="dark"] tr:nth-child(even) td {
    background: #222 !important;
}
[data-theme="dark"] tr:hover td {
    background: #2a2a2a !important;
}

/* --- ダークモード: 見出し --- */
[data-theme="dark"] h1 {
    color: #7dd3fc !important;
}
[data-theme="dark"] h2,
[data-theme="dark"] h3 {
    color: #93c5fd !important;
}

/* --- ダークモード: 入力欄 --- */
[data-theme="dark"] [data-testid="stChatInput"] {
    background: #1B6478 !important;
}

/* --- ダークモード: expander --- */
[data-theme="dark"] .streamlit-expanderHeader {
    background: #1f2937 !important;
    color: #7dd3fc !important;
}
</style>
""", unsafe_allow_html=True)

# ========================================
# 知識ファイル読み込み（GitHub優先、ローカルフォールバック）
# ========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# GitHub連携設定（環境変数 or Streamlit secrets）
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "")  # 例: "username/bdash-cs-agent"
GITHUB_BRANCH = os.environ.get("GITHUB_BRANCH", "main")

# Streamlit Cloud対応: st.secretsからも取得
try:
    if not GITHUB_TOKEN and hasattr(st, "secrets"):
        GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
        GITHUB_REPO = st.secrets.get("GITHUB_REPO", "")
        GITHUB_BRANCH = st.secrets.get("GITHUB_BRANCH", "main")
except Exception:
    pass

# トークンが有効なAPIキー形式かチェック（日本語等が入っていたら無効）
def _is_valid_token(token):
    try:
        token.encode("latin-1")
        return bool(token.strip())
    except (UnicodeEncodeError, AttributeError):
        return False

USE_GITHUB = bool(_is_valid_token(GITHUB_TOKEN) and GITHUB_REPO)


def _github_api(method, path, data=None):
    """GitHub API呼び出し"""
    import requests
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    if method == "GET":
        r = requests.get(url, headers=headers, params={"ref": GITHUB_BRANCH})
    elif method == "PUT":
        r = requests.put(url, headers=headers, json=data)
    return r


def load_yaml(filename):
    """YAMLファイルを読み込む（GitHub優先）"""
    if USE_GITHUB:
        try:
            r = _github_api("GET", filename)
            if r.status_code == 200:
                import base64
                content = base64.b64decode(r.json()["content"]).decode("utf-8")
                return content
        except Exception:
            pass
    # ローカルフォールバック
    path = os.path.join(BASE_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_yaml_parsed(filename):
    """YAMLファイルをパースして読み込む"""
    content = load_yaml(filename)
    return yaml.safe_load(content)


def save_yaml(filename, data):
    """YAMLファイルを保存（GitHub優先）"""
    yaml_content = yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)

    if USE_GITHUB:
        try:
            import base64
            # 既存ファイルのSHAを取得（更新に必要）
            r = _github_api("GET", filename)
            sha = r.json().get("sha", "") if r.status_code == 200 else ""

            put_data = {
                "message": f"[Agent FB] {filename} を更新",
                "content": base64.b64encode(yaml_content.encode("utf-8")).decode("utf-8"),
                "branch": GITHUB_BRANCH,
            }
            if sha:
                put_data["sha"] = sha

            r = _github_api("PUT", filename, put_data)
            if r.status_code in (200, 201):
                return  # GitHub保存成功
        except Exception as e:
            st.warning(f"GitHub保存エラー: {e}（ローカルに保存します）")

    # ローカルフォールバック
    path = os.path.join(BASE_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(yaml_content)


# ========================================
# スプレッドシートから企業一覧を取得
# ========================================
# 方式1: Google Sheets API（推奨）— Service AccountでOrgのスプシを非公開のまま読み込み
# 方式2: CSV公開（簡易）— スプシを「ウェブに公開」→ CSV形式
SPREADSHEET_CSV_URL = os.environ.get("COMPANY_SPREADSHEET_URL", "")
if not SPREADSHEET_CSV_URL:
    try:
        SPREADSHEET_CSV_URL = st.secrets.get("COMPANY_SPREADSHEET_URL", "")
    except Exception:
        pass

# Google Sheets API用の設定
GSHEET_SPREADSHEET_ID = ""
GSHEET_SHEET_NAME = ""
try:
    GSHEET_SPREADSHEET_ID = st.secrets.get("GSHEET_SPREADSHEET_ID", "")
    GSHEET_SHEET_NAME = st.secrets.get("GSHEET_SHEET_NAME", "Sheet1")
except Exception:
    pass

USE_GSHEET_API = bool(GSHEET_SPREADSHEET_ID)


def _get_gsheet_client():
    """Google Sheets APIクライアントを取得（Service Account認証）"""
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        # st.secretsからService Account情報を取得
        sa_info = dict(st.secrets["gcp_service_account"])
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets.readonly",
        ]
        credentials = Credentials.from_service_account_info(sa_info, scopes=scopes)
        return gspread.authorize(credentials)
    except Exception as e:
        st.warning(f"Google Sheets API認証エラー: {e}")
        return None


@st.cache_data(ttl=300)  # 5分キャッシュ
def fetch_companies_from_spreadsheet():
    """スプレッドシートから企業一覧を取得する。
    スプシの列: company_key, name, industry
    方式1: Google Sheets API（Service Account）
    方式2: CSV公開URL
    """
    # 方式1: Google Sheets API
    if USE_GSHEET_API:
        try:
            gc = _get_gsheet_client()
            if gc:
                sh = gc.open_by_key(GSHEET_SPREADSHEET_ID)
                ws = sh.worksheet(GSHEET_SHEET_NAME)
                records = ws.get_all_records()
                companies = []
                for row in records:
                    companies.append({
                        "key": str(row.get("company_key", "")).strip(),
                        "name": str(row.get("name", "")).strip(),
                        "industry": str(row.get("industry", "")).strip(),
                    })
                return companies if companies else None
        except Exception as e:
            st.warning(f"Google Sheets API読み込みエラー: {e}")

    # 方式2: CSV公開URL
    if SPREADSHEET_CSV_URL:
        try:
            import pandas as pd
            df = pd.read_csv(SPREADSHEET_CSV_URL)
            companies = []
            for _, row in df.iterrows():
                companies.append({
                    "key": str(row.get("company_key", "")).strip(),
                    "name": str(row.get("name", "")).strip(),
                    "industry": str(row.get("industry", "")).strip(),
                })
            return companies
        except Exception as e:
            st.warning(f"スプシ読み込みエラー: {e}")

    return None


def get_company_list():
    """企業一覧を取得（スプシ優先、なければローカル）"""
    # スプシから取得を試みる
    spreadsheet_companies = fetch_companies_from_spreadsheet()
    if spreadsheet_companies:
        return spreadsheet_companies

    # ローカルのcustomers/配下から取得
    customers_dir = os.path.join(BASE_DIR, "customers")
    companies = []
    if os.path.isdir(customers_dir):
        for d in sorted(os.listdir(customers_dir)):
            full_path = os.path.join(customers_dir, d)
            profile_path = os.path.join(full_path, "customer_profile.yml")
            if os.path.isdir(full_path) and os.path.exists(profile_path):
                try:
                    with open(profile_path, "r", encoding="utf-8") as f:
                        profile = yaml.safe_load(f)
                    name = profile.get("company", {}).get("name", d) if profile else d
                    industry = profile.get("company", {}).get("industry", "") if profile else ""
                except Exception:
                    name = d
                    industry = ""
                companies.append({
                    "key": f"customers/{d}",
                    "name": name,
                    "industry": industry,
                })
    return companies


# ========================================
# 共通ツール定義
# ========================================
COMMON_TOOLS = [
    {
        "name": "read_data_definition",
        "description": "データ定義ファイル(data_definition.yml)を読み込む。テーブル定義、カラム情報、リレーション情報を取得する。",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "read_customer_profile",
        "description": "顧客プロファイル(customer_profile.yml)を読み込む。企業固有の運用ルール、データ取得方式、global_exclusions、過去施策を取得する。",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_dir": {
                    "type": "string",
                    "description": "顧客ディレクトリパス（例: customers/template_ec）",
                    "default": "customers/template_ec",
                }
            },
            "required": [],
        },
    },
    {
        "name": "read_output_samples",
        "description": "過去の施策サンプル(output_sample.yml)を読み込む。要件定義の形式・粒度の基準、および類似施策の検索に使用する。",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]

# データ検索ツール（共通） - アップロード済みデータ or Snowflake
DATA_SEARCH_TOOL = {
    "name": "search_data_schema",
    "description": "アップロード済みデータやSnowflakeからテーブル名・カラム名を検索する。data_definition.ymlに載っていないデータが必要な場合に使用する。",
    "input_schema": {
        "type": "object",
        "properties": {
            "search_keyword": {
                "type": "string",
                "description": "検索キーワード（テーブル名やカラム名の一部）",
            },
        },
        "required": ["search_keyword"],
    },
}

# 要件定義Agent専用ツール
REQUIREMENTS_TOOLS = COMMON_TOOLS + [DATA_SEARCH_TOOL] + [
    {
        "name": "save_campaign_requirement",
        "description": "完成した要件定義をYAML形式で保存する。output_sample.ymlに新しい施策として追加する。",
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_yaml": {
                    "type": "string",
                    "description": "保存する施策のYAML文字列",
                }
            },
            "required": ["campaign_yaml"],
        },
    },
    {
        "name": "add_customer_feedback",
        "description": "顧客固有のフィードバックをcustomer_profile.ymlのpast_campaignsに追加する。",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_dir": {
                    "type": "string",
                    "description": "顧客ディレクトリパス",
                    "default": "customers/template_ec",
                },
                "feedback_entry": {
                    "type": "string",
                    "description": "フィードバック内容のYAML文字列",
                },
            },
            "required": ["feedback_entry"],
        },
    },
    {
        "name": "add_cross_company_knowledge",
        "description": "企業横断のナレッジをoutput_sample.ymlに新しい施策パターンとして追加する（AI自律更新）。",
        "input_schema": {
            "type": "object",
            "properties": {
                "knowledge_yaml": {
                    "type": "string",
                    "description": "追加するナレッジのYAML文字列",
                }
            },
            "required": ["knowledge_yaml"],
        },
    },
]

# 実装Agent専用ツール
IMPLEMENTATION_TOOLS = COMMON_TOOLS + [DATA_SEARCH_TOOL] + [
    {
        "name": "read_bdash_operations",
        "description": "b→dash構築操作ガイド(bdash_operations.yml)を読み込む。データパレット、セグメント、シナリオの全操作手順・制約を取得する。",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "read_requirements_output",
        "description": "要件定義Agentで作成された要件定義を読み込む。実装手順の入力として使用する。",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "save_implementation_feedback",
        "description": "実装フェーズでのフィードバックを顧客プロファイルに蓄積する。手順の修正・補足・注意点など、今後の実装に活かすべき情報を保存する。",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_dir": {
                    "type": "string",
                    "description": "顧客ディレクトリパス",
                    "default": "customers/template_ec",
                },
                "feedback_entry": {
                    "type": "string",
                    "description": "フィードバック内容のYAML文字列",
                },
            },
            "required": ["feedback_entry"],
        },
    },
]


# ========================================
# ツール実行
# ========================================
def execute_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "read_data_definition":
        return load_yaml("data_definition.yml")

    elif tool_name == "read_customer_profile":
        company_dir = tool_input.get("company_dir", st.session_state.get("selected_company", "customers/template_ec"))
        path = os.path.join(company_dir, "customer_profile.yml")
        return load_yaml(path)

    elif tool_name == "read_output_samples":
        return load_yaml("output_sample.yml")

    elif tool_name == "read_bdash_operations":
        return load_yaml("bdash_operations.yml")

    elif tool_name == "read_requirements_output":
        # 要件定義の結果をセッションから取得
        req_output = st.session_state.get("last_requirements_output", "")
        if req_output:
            return req_output
        return "要件定義の出力がまだありません。先に要件定義Agentで施策を定義してください。"

    elif tool_name == "save_campaign_requirement":
        campaign_yaml = tool_input["campaign_yaml"]
        data = load_yaml_parsed("output_sample.yml")
        new_campaign = yaml.safe_load(campaign_yaml)
        if "samples" not in data:
            data["samples"] = []
        data["samples"].append(new_campaign)
        save_yaml("output_sample.yml", data)
        return "施策を保存しました。"

    elif tool_name == "add_customer_feedback":
        company_dir = tool_input.get("company_dir", st.session_state.get("selected_company", "customers/template_ec"))
        feedback_yaml = tool_input["feedback_entry"]
        path = os.path.join(company_dir, "customer_profile.yml")
        data = load_yaml_parsed(path)
        entry = yaml.safe_load(feedback_yaml)
        if not data.get("past_campaigns"):
            data["past_campaigns"] = []
        data["past_campaigns"].append(entry)
        save_yaml(path, data)
        return "顧客FBを保存しました。"

    elif tool_name == "add_cross_company_knowledge":
        knowledge_yaml = tool_input["knowledge_yaml"]
        data = load_yaml_parsed("output_sample.yml")
        new_entry = yaml.safe_load(knowledge_yaml)
        if "samples" not in data:
            data["samples"] = []
        data["samples"].append(new_entry)
        save_yaml("output_sample.yml", data)
        return "企業横断ナレッジを保存しました。"

    elif tool_name == "search_data_schema":
        keyword = tool_input["search_keyword"].lower()
        results = []
        source_used = []

        # ① アップロード済みデータから検索
        uploaded = st.session_state.get("uploaded_data_schemas", {})
        if uploaded:
            source_used.append("アップロードデータ")
            for table_name, schema in uploaded.items():
                if keyword in table_name.lower():
                    cols = schema.get("columns", [])
                    col_lines = "\n".join([f"  - {c['name']} ({c['type']})" for c in cols])
                    results.append(f"[アップロード] テーブル: {table_name}\nカラム数: {len(cols)}\n{col_lines}")
                    continue
                matched_cols = [c for c in schema.get("columns", []) if keyword in c["name"].lower()]
                if matched_cols:
                    col_lines = "\n".join([f"  - {c['name']} ({c['type']})" for c in matched_cols])
                    results.append(f"[アップロード] テーブル: {table_name} マッチカラム:\n{col_lines}")

        # ② Snowflakeから検索（接続設定がある場合）
        sf_account = os.environ.get("SNOWFLAKE_ACCOUNT", "")
        sf_user = os.environ.get("SNOWFLAKE_USER", "")
        sf_password = os.environ.get("SNOWFLAKE_PASSWORD", "")
        if all([sf_account, sf_user, sf_password]):
            source_used.append("Snowflake")
            try:
                import snowflake.connector
                conn = snowflake.connector.connect(
                    account=sf_account, user=sf_user, password=sf_password,
                    database=os.environ.get("SNOWFLAKE_DATABASE", ""),
                    warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE", ""),
                )
                cur = conn.cursor()
                cur.execute(
                    f"SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE "
                    f"FROM INFORMATION_SCHEMA.COLUMNS "
                    f"WHERE TABLE_NAME ILIKE '%{keyword}%' OR COLUMN_NAME ILIKE '%{keyword}%' "
                    f"LIMIT 30"
                )
                rows = cur.fetchall()
                cur.close()
                conn.close()
                for row in rows:
                    results.append(f"[Snowflake] {row[0]}.{row[1]} ({row[2]})")
            except ImportError:
                pass  # snowflake-connector未インストール
            except Exception as e:
                results.append(f"[Snowflake検索エラー] {str(e)}")

        if results:
            header = f"検索元: {', '.join(source_used)}\n\n"
            return header + "\n\n".join(results)

        # どちらもない場合
        msg = f"'{keyword}' の検索結果: 0件\n\n"
        if not uploaded:
            msg += "・アップロードデータ: なし（サイドバーからCSV/Excelをアップロードしてください）\n"
        else:
            msg += f"・アップロードデータ: {', '.join(uploaded.keys())}（一致なし）\n"
        if not all([sf_account, sf_user, sf_password]):
            msg += "・Snowflake: 未接続（環境変数 SNOWFLAKE_ACCOUNT 等を設定すると検索可能）"
        return msg

    elif tool_name == "save_implementation_feedback":
        company_dir = tool_input.get("company_dir", st.session_state.get("selected_company", "customers/template_ec"))
        feedback_yaml = tool_input["feedback_entry"]
        path = os.path.join(company_dir, "customer_profile.yml")
        data = load_yaml_parsed(path)
        entry = yaml.safe_load(feedback_yaml)
        if not data.get("implementation_feedback"):
            data["implementation_feedback"] = []
        data["implementation_feedback"].append(entry)
        save_yaml(path, data)
        return "実装FBを保存しました。"

    return f"不明なツール: {tool_name}"


# ========================================
# システムプロンプト
# ========================================
REQUIREMENTS_SYSTEM_PROMPT = """あなたは「要件定義Agent」です。b→dashのカスタマーサクセス業務において、
施策の要件定義を構造化し、使用するデータテーブル・カラムのマッピングまで行います。

# 動作フロー（厳守）

フェーズ1（確認） → ユーザー回答 → (不明点あれば)フェーズ1追加 → ユーザー回答 → フェーズ2（生成）

**絶対にフェーズ1（確認）とフェーズ2（生成）を混ぜないでください。**
フェーズ1で質問を返しているのに同時に要件定義を出力してはいけません。

## フェーズ1: 確認事項の洗い出し

ユーザーが施策概要を入力したら、以下を必ずチェックしてください：
1. 配信対象条件（誰に送るか）
2. 配信タイミング（いつ送るか）
3. コンテンツ差込項目（何を動的に入れるか）
4. 除外条件（誰を除くか）

上記に加え、データ実装上の曖昧さ（時間の定義、判定タイミング等）を検出してください。
顧客プロファイル（customer_profile.yml）を参照し、企業固有の運用ルールとの矛盾がないか確認してください。

不足・曖昧な点はopen_questionsとして以下の形式で返してください：

### 確認事項

| # | 質問 | 影響範囲 |
|---|------|----------|
| 1 | 質問内容 | この回答がどこに影響するか |

## フェーズ1.5: 類似施策の提案

フェーズ1の解析中に、過去の施策（output_sample.yml）や顧客のpast_campaignsに
類似する施策が見つかった場合、以下の形式で提示してください：

### 類似する過去施策

| 項目 | 施策A | 施策B |
|------|-------|-------|
| 施策名 | ... | ... |
| 類似点 | ... | ... |
| 今回との差分 | ... | ... |

**選択肢を必ず提示してください：**
- 「施策Aをベースにする」
- 「施策Bをベースにする」
- 「新規で作る」

勝手に選ばないでください。必ずユーザーに判断を委ねてください。

## フェーズ2: 要件定義の生成

全ての確認事項が解消されたら、以下の形式で要件定義を生成してください。

### 施策概要
施策名と概要を1〜2行で表示

### 配信対象条件
| # | 条件 | 使用データ | ロジック |
|---|------|-----------|---------|

### 配信タイミング
| 配信回 | タイミング | 配信時間帯 | 補足 |
|--------|-----------|-----------|------|

### コンテンツ差込項目
| # | 差込内容 | 使用データ | 備考 |
|---|---------|-----------|------|

### 除外条件
| # | 除外条件 | 使用データ | ロジック |
|---|---------|-----------|---------|
※ 全施策共通の除外条件（メルマガ未許諾等）は自動適用されます

### データ結合パス
テーブル結合を矢印で表示：
customers → orders → order_details → products

技術的な詳細（カラム型、FK定義等）はユーザーに見せないでください。
「テーブル名.カラム名」は表示しますが、それ以上の内部構造は隠してください。

## フェーズ3: FB収集・蓄積

要件定義完了後、ユーザーからFBがあった場合：
- 企業固有のFB → add_customer_feedbackツールで顧客プロファイルに蓄積
- 企業横断のFB → add_cross_company_knowledgeツールで自律的に蓄積

# ルール

## データマッピング
- テーブル名・カラム名はdata_definition.ymlに定義されたものを正確に使うこと
- リレーション項目はcustomer_profile.ymlのrelation_mappingを参照すること
- FK関係を考慮し、正しいJOINパスを設計すること
- カラムが存在しない場合は「データ不足」として明示すること

## データ選択（重複テーブル対応）
同じ意味を持つテーブル/カラムが複数存在する場合、Agentは勝手に選ばないでください。
候補をすべて提示し、ユーザーに選択を委ねてください。

## global_exclusions
- customer_profile.ymlのglobal_exclusionsは全施策に自動適用する
- ユーザーが施策固有の除外条件で「なし」と言ってもglobal_exclusionsは適用される
- global_exclusionsと重複する条件をユーザーが指定した場合、重複適用しない

## 品質チェック
- 配信対象条件と除外条件に矛盾がないか確認する
- 差込項目に必要なテーブルがJOINパスに含まれているか確認する
- タイミング指定に時間帯制約がある場合、繰り越しルールを明示する
- 複数回配信がある場合、各回の条件差分を明確にする

## 確認事項
- 不明点は推測で埋めず、必ずopen_questionsとして返す
- data_definition.ymlやcustomer_profile.ymlから自明に判断できるものは自動解決する
- open_questionsにはimpact（その回答がどこに影響するか）を必ず付ける

# 初期動作

**会話開始時、まず以下のツールを使って知識ファイルを読み込んでください：**
1. read_data_definition — テーブル定義の取得
2. read_customer_profile — 顧客プロファイルの取得（選択中の企業が自動で読み込まれます）
3. read_output_samples — 過去施策サンプルの取得

読み込み完了後、ユーザーに施策概要の入力を促してください。
"""

IMPLEMENTATION_SYSTEM_PROMPT = """あなたは「実装Agent」です。b→dashのカスタマーサクセス業務において、
要件定義Agentが生成した要件定義をもとに、b→dash上での具体的な構築手順書を作成します。

# 入力

要件定義Agentが生成した要件定義（配信対象条件、配信タイミング、コンテンツ差込項目、除外条件、データ結合パス）を
read_requirements_outputツールで取得します。

# 動作フロー（厳守）

ステップ1（要件確認） → ステップ2（手順書生成） → ステップ3（FB収集） → ステップ4（最終Fix版出力）

## ステップ1: 要件定義の確認

要件定義を読み込み、以下を確認してください：
1. 要件定義の内容をユーザーに提示し、正しいか確認する
2. 実装上の追加確認事項があれば質問する（b→dash固有の設定に関するもの）

## ステップ2: 構築手順書の生成

bdash_operations.ymlの操作手順に基づいて、以下の順番で具体的な構築手順を生成してください。

### 手順1: データパレット/加工

要件定義のデータ結合パスとカラムマッピングから：

#### 1-1. データ統合（横統合/縦統合）
| # | 操作 | ファイル1 | ファイル2 | 統合方法 | 統合キー | 保持カラム |
|---|------|----------|----------|---------|---------|-----------|

#### 1-2. クレンジング
| # | 操作 | 対象ファイル | 加工種類 | 設定内容 | 出力カラム名 |
|---|------|-------------|---------|---------|-------------|

各操作では、bdash_operations.ymlに記載された制約（例：横統合は2ファイルまで、四則演算は整数型/小数型のみ等）を必ず考慮してください。

### 手順2: セグメント作成
| # | セグメント名 | タイプ | データファイル | 顧客IDカラム | 抽出条件 |
|---|-------------|-------|--------------|-------------|---------|

除外条件用のセグメントも含め、必要なセグメントをすべてリストしてください。
複合セグメント（AND/OR/除外）が必要な場合は明示してください。

### 手順3: メール作成
| # | 設定項目 | 内容 |
|---|---------|------|

差込項目のマッピング（どのカラムをどの差込箇所に設定するか）を明示してください。

### 手順4: シナリオ設定
| # | 設定項目 | 内容 |
|---|---------|------|

以下を含めてください：
- 配信データの選択（セグメント、配信先カラム、除外データ）
- 配信タイミング（トリガー種類、スケジュール）
- ワークフロー（アクション/ウェイト/分岐タスクの構成）
- 運用期間

### 手順5: テスト配信
テスト配信の確認ポイントを列挙してください。

# ルール

## b→dash操作の正確性
- bdash_operations.ymlに記載された操作手順・制約に厳密に従うこと
- 操作の制約（例：横統合は2ファイルまで、IF文の出力はテキスト型）を手順に反映すること
- 操作が複数ステップに分かれる場合は明示すること（例：3テーブルJOINは横統合を2回実行）

## データ整合性
- data_definition.ymlのカラム型と、加工操作の対応データ型が一致しているか確認すること
- NULL値が含まれる可能性があるカラムの演算では注意事項を付記すること

## 更新設定
- 各データパレット操作の更新設定（自動実行タイミング）を提案すること
- セグメントの定期更新設定を提案すること
- データ更新とセグメント更新のタイミング競合に注意すること

## 不明点の扱い
- 実装上の不明点は推測で埋めず、必ずユーザーに確認すること
- b→dashの操作で複数の実現方法がある場合、選択肢を提示すること

## 未知データの検索
- data_definition.ymlに載っていないテーブル/カラムが必要になった場合、search_data_schemaツールで検索すること
- ユーザーがCSV/Excelでアップロードしたデータのスキーマを検索できる
- 検索結果をユーザーに提示し、どのテーブル/カラムを使うか確認すること

## フィードバックの蓄積（必須）
ユーザーから手順に対する修正・補足・注意点のFBがあった場合、必ずsave_implementation_feedbackツールで蓄積すること。
蓄積すべき情報の例：
- 手順の順番や内容の修正
- b→dash操作の補足情報（UIの注意点、隠れた制約等）
- 特定データに対する加工のコツ
- 「次回からこうしてほしい」というユーザーの要望
蓄積したことをユーザーに通知すること（例：「このFBを蓄積しました」）。

## ステップ4: 最終Fix版手順書の出力（必須）

ステップ3のFB収集が完了したら（ユーザーが「OK」「問題ない」「完了」等と言ったら）、
**必ず全手順を統合した最終Fix版の手順書を出力してください。**

最終Fix版には以下を含めてください：
1. ステップ2で生成した手順書の全内容
2. ステップ3で受けたFBによる修正をすべて反映済み
3. 各手順に番号を振り、順番通りに実行すれば完了する形式にする

出力形式：

---
## 📋 最終Fix版 構築手順書

**施策名**: （要件定義から取得）
**作成日**: （当日の日付）
**対象企業**: （選択中の企業名）

### 手順1: データパレット/加工
（統合・クレンジングの全操作を順番に）

### 手順2: セグメント作成
（全セグメントの設定）

### 手順3: メール作成
（差込設定含む）

### 手順4: シナリオ設定
（配信データ・タイミング・ワークフロー）

### 手順5: テスト配信
（確認ポイント）

### 更新設定まとめ
（全操作の更新タイミング一覧）

### 注意事項
（FB反映で追加された注意点）
---

**最終Fix版を出力する前に、ユーザーに「FBは以上ですか？最終版を出力します」と確認してください。**
**最終Fix版を出力したら、その旨をユーザーに伝えてください（例：「以上が最終Fix版の手順書です。この手順通りにb→dashで構築してください。」）**

# 初期動作

**会話開始時、まず以下のツールを使って知識ファイルを読み込んでください：**
1. read_requirements_output — 要件定義Agentの出力を取得
2. read_bdash_operations — b→dash構築操作ガイドの取得
3. read_data_definition — テーブル定義の取得
4. read_customer_profile — 顧客プロファイルの取得

読み込み完了後、要件定義の内容を簡潔に提示し、構築手順の生成に入ってよいか確認してください。
"""


# ========================================
# エージェント設定
# ========================================
AGENTS = {
    "requirements": {
        "name": "要件定義Agent",
        "icon": "📋",
        "system_prompt": REQUIREMENTS_SYSTEM_PROMPT,
        "tools": REQUIREMENTS_TOOLS,
        "init_message": "知識ファイルを読み込んで、準備ができたらユーザーに施策概要の入力を促してください。",
        "placeholder": "施策の概要を入力してください...",
        "description": "施策の要件定義を構造化します",
    },
    "implementation": {
        "name": "実装Agent",
        "icon": "🔧",
        "system_prompt": IMPLEMENTATION_SYSTEM_PROMPT,
        "tools": IMPLEMENTATION_TOOLS,
        "init_message": "知識ファイルと要件定義の出力を読み込んで、構築手順の生成準備をしてください。",
        "placeholder": "実装に関する質問や指示を入力してください...",
        "description": "要件定義をもとにb→dashの構築手順書を作成します",
    },
}


# ========================================
# Claude APIクライアント
# ========================================
def get_client():
    api_key = (
        os.environ.get("ANTHROPIC_API_KEY", "")
    )
    # Streamlit Cloud対応: st.secretsからも取得
    if not api_key:
        try:
            api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
        except Exception:
            pass
    if not api_key:
        st.error("APIキーが設定されていません。Streamlit Cloudのsecretsに ANTHROPIC_API_KEY を設定してください。")
        st.stop()
    return Anthropic(api_key=api_key)


def call_agent(client, messages, agent_key):
    """Claude APIを呼び出し、ツール使用ループを処理する。"""
    agent = AGENTS[agent_key]
    while True:
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8192,
                system=agent["system_prompt"],
                tools=agent["tools"],
                thinking={"type": "enabled", "budget_tokens": 5000},
                messages=messages,
            )
        except Exception as e:
            st.error(f"API呼び出しエラー: {str(e)}")
            return f"エラーが発生しました: {str(e)}", messages

        # レスポンス内容を処理
        assistant_content = response.content
        messages.append({"role": "assistant", "content": assistant_content})

        # ツール呼び出しがなければ終了
        if response.stop_reason != "tool_use":
            text_parts = []
            for block in assistant_content:
                if block.type == "text":
                    text_parts.append(block.text)
            return "\n".join(text_parts), messages

        # ツール呼び出しを実行
        tool_results = []
        for block in assistant_content:
            if block.type == "tool_use":
                with st.spinner(f"🔧 {block.name} を実行中..."):
                    result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

        messages.append({"role": "user", "content": tool_results})


# ========================================
# セッション初期化
# ========================================
if "current_agent" not in st.session_state:
    st.session_state.current_agent = "requirements"
if "selected_company" not in st.session_state:
    st.session_state.selected_company = "customers/template_ec"
# 旧セッション（リスト型）が残っている場合はリセット
if "messages" not in st.session_state or not isinstance(st.session_state.messages, dict):
    st.session_state.messages = {}
if "chat_history" not in st.session_state or not isinstance(st.session_state.chat_history, dict):
    st.session_state.chat_history = {}
if "initialized" not in st.session_state or not isinstance(st.session_state.initialized, dict):
    st.session_state.initialized = {}
if "last_requirements_output" not in st.session_state:
    st.session_state.last_requirements_output = ""
if "uploaded_data_schemas" not in st.session_state:
    st.session_state.uploaded_data_schemas = {}
if "handoff_in_progress" not in st.session_state:
    st.session_state.handoff_in_progress = False


def switch_agent(agent_key):
    """エージェントを切り替える"""
    st.session_state.current_agent = agent_key


def reset_current_agent():
    """現在のエージェントの会話をリセット"""
    agent_key = st.session_state.current_agent
    st.session_state.messages[agent_key] = []
    st.session_state.chat_history[agent_key] = []
    st.session_state.initialized[agent_key] = False


def check_requirements_completeness():
    """要件定義の完成度をチェック。不足している項目リストを返す。空なら完成。"""
    agent_key = "requirements"
    chat_hist = st.session_state.chat_history.get(agent_key, [])

    # 最後のassistant出力を取得
    last_output = ""
    for msg in reversed(chat_hist):
        if msg["role"] == "assistant":
            last_output = msg["content"]
            break

    if not last_output:
        return ["要件定義がまだ開始されていません"]

    # 必須セクションのチェック
    required_sections = {
        "配信対象条件": ["配信対象", "対象条件", "ターゲット"],
        "配信タイミング": ["配信タイミング", "タイミング", "配信時間"],
        "コンテンツ差込項目": ["コンテンツ差込", "差込項目", "差込"],
        "除外条件": ["除外条件", "除外"],
        "データ結合パス": ["データ結合", "結合パス", "JOIN"],
    }

    missing = []
    for section_name, keywords in required_sections.items():
        found = any(kw in last_output for kw in keywords)
        if not found:
            missing.append(section_name)

    return missing


def handoff_to_implementation():
    """要件定義の出力を保存して実装Agentに引き継ぐ"""
    # 要件定義の最後のassistant出力を保存
    agent_key = "requirements"
    chat_hist = st.session_state.chat_history.get(agent_key, [])
    for msg in reversed(chat_hist):
        if msg["role"] == "assistant":
            st.session_state.last_requirements_output = msg["content"]
            break
    # 引き継ぎフラグを立てる（ローディング表示用）
    st.session_state.handoff_in_progress = True
    # 実装Agentに切り替え
    st.session_state.current_agent = "implementation"


# ========================================
# サイドバー
# ========================================
with st.sidebar:
    st.title("🚀 b→dash CS支援")
    st.caption("マルチエージェント業務支援ツール")
    st.divider()

    # エージェント切り替え
    st.markdown("### エージェント選択")
    current = st.session_state.current_agent

    col1, col2 = st.columns(2)
    with col1:
        req_style = "primary" if current == "requirements" else "secondary"
        if st.button("📋 要件定義", use_container_width=True, type=req_style):
            switch_agent("requirements")
            st.rerun()
    with col2:
        impl_style = "primary" if current == "implementation" else "secondary"
        # 要件定義が完了していない場合は実装Agentに直接切り替え不可
        has_requirements = bool(st.session_state.get("last_requirements_output", ""))
        impl_disabled = (current != "implementation" and not has_requirements)
        if st.button("🔧 実装", use_container_width=True, type=impl_style, disabled=impl_disabled):
            if has_requirements:
                switch_agent("implementation")
                st.rerun()
            else:
                st.warning("先に要件定義を完了してください")
        if impl_disabled:
            st.caption("⚠️ 要件定義完了後に有効化")

    # 実装Agentへの引き継ぎボタン（要件定義画面のみ）
    if current == "requirements":
        st.divider()
        missing = check_requirements_completeness()
        if missing:
            st.button("➡️ 実装Agentに引き継ぐ", use_container_width=True, type="primary", disabled=True)
            st.caption(f"⚠️ 未完了: {', '.join(missing)}")
        else:
            if st.button("➡️ 実装Agentに引き継ぐ", use_container_width=True, type="primary"):
                handoff_to_implementation()
                st.rerun()

    st.divider()

    # 対象企業選択
    st.markdown("### 対象企業")
    companies = get_company_list()

    if companies:
        company_keys = [c["key"] for c in companies]
        company_labels = {c["key"]: f"{c['name']}（{c['industry']}）" if c.get("industry") else c["name"] for c in companies}
        current_idx = company_keys.index(st.session_state.selected_company) if st.session_state.selected_company in company_keys else 0
        selected = st.selectbox(
            "企業を選択",
            company_keys,
            index=current_idx,
            format_func=lambda x: company_labels.get(x, x),
        )
        if selected != st.session_state.selected_company:
            st.session_state.selected_company = selected
            st.session_state.messages = {}
            st.session_state.chat_history = {}
            st.session_state.initialized = {}
            st.session_state.last_requirements_output = ""
            st.rerun()

        if SPREADSHEET_CSV_URL:
            st.caption("📊 スプレッドシートから取得")
    else:
        st.warning("企業データがありません")

    # 現在のエージェントのフェーズ表示
    st.markdown(f"### 現在: {AGENTS[current]['name']}")
    st.caption(AGENTS[current]["description"])

    if current == "requirements":
        phases = {
            "Phase 1": "確認事項の洗い出し",
            "Phase 1.5": "類似施策の提案",
            "Phase 2": "要件定義の生成",
            "Phase 3": "FB収集・蓄積",
        }
    else:
        phases = {
            "Step 1": "要件定義の確認",
            "Step 2": "構築手順書の生成",
            "Step 3": "FB収集",
            "Step 4": "最終Fix版出力",
        }
    for phase, desc in phases.items():
        st.markdown(f"**{phase}**: {desc}")

    st.divider()

    # データアップロード
    st.markdown("### データアップロード")
    uploaded_files = st.file_uploader(
        "CSV / Excelをアップロード",
        type=["csv", "xlsx", "xls"],
        accept_multiple_files=True,
        key="data_uploader",
    )
    if uploaded_files:
        import pandas as pd
        for uf in uploaded_files:
            table_name = os.path.splitext(uf.name)[0]
            try:
                if uf.name.endswith(".csv"):
                    df = pd.read_csv(uf, nrows=100)
                else:
                    df = pd.read_excel(uf, nrows=100)
                columns = []
                for col in df.columns:
                    dtype = str(df[col].dtype)
                    # pandasのdtypeを分かりやすく変換
                    if "int" in dtype:
                        col_type = "整数型"
                    elif "float" in dtype:
                        col_type = "小数型"
                    elif "datetime" in dtype:
                        col_type = "日時型"
                    elif "bool" in dtype:
                        col_type = "真偽型"
                    else:
                        col_type = "テキスト型"
                    # サンプル値を取得
                    sample = df[col].dropna().head(3).tolist()
                    columns.append({
                        "name": str(col),
                        "type": col_type,
                        "sample": [str(s) for s in sample],
                    })
                st.session_state.uploaded_data_schemas[table_name] = {
                    "columns": columns,
                    "row_count": len(df),
                }
            except Exception as e:
                st.error(f"{uf.name}: {e}")

    # アップロード済みデータ一覧
    if st.session_state.uploaded_data_schemas:
        st.caption(f"📁 {len(st.session_state.uploaded_data_schemas)}件のデータ読込済")
        for tname in st.session_state.uploaded_data_schemas:
            cols_count = len(st.session_state.uploaded_data_schemas[tname]["columns"])
            st.caption(f"  ・{tname}（{cols_count}列）")

    st.divider()
    if st.button("🔄 会話をリセット", use_container_width=True):
        reset_current_agent()
        st.rerun()


# ========================================
# メインエリア
# ========================================
current_agent = st.session_state.current_agent
agent_config = AGENTS[current_agent]

st.title(f"{agent_config['icon']} {agent_config['name']}")
st.caption(agent_config["description"])

# 引き継ぎローディング表示
if current_agent == "implementation" and st.session_state.get("handoff_in_progress", False):
    handoff_container = st.empty()
    with handoff_container:
        st.markdown("""
        <div style="text-align: center; padding: 3rem 1rem;">
            <div style="font-size: 48px; margin-bottom: 1rem;">📋 ➡️ 🔧</div>
            <h2 style="color: #1a6b9c;">実装Agentに引き継いでいます...</h2>
            <p style="color: #6b7280; font-size: 16px;">要件定義の内容を実装Agentに渡しています。しばらくお待ちください。</p>
        </div>
        """, unsafe_allow_html=True)
    import time
    time.sleep(2)
    handoff_container.empty()
    st.session_state.handoff_in_progress = False

# 引き継ぎ状態の表示
if current_agent == "implementation" and st.session_state.last_requirements_output:
    with st.expander("📋 引き継いだ要件定義", expanded=False):
        st.markdown(st.session_state.last_requirements_output)

# エージェント別のメッセージ履歴を初期化
if current_agent not in st.session_state.messages:
    st.session_state.messages[current_agent] = []
if current_agent not in st.session_state.chat_history:
    st.session_state.chat_history[current_agent] = []
if current_agent not in st.session_state.initialized:
    st.session_state.initialized[current_agent] = False

# チャット履歴の表示
for msg in st.session_state.chat_history[current_agent]:
    avatar = "🧑‍💼" if msg["role"] == "user" else agent_config["icon"]
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"], unsafe_allow_html=True)

# 初期化（知識ファイル読み込み）
if not st.session_state.initialized.get(current_agent, False):
    with st.chat_message("assistant", avatar=agent_config["icon"]):
        with st.spinner("知識ファイルを読み込んでいます..."):
            client = get_client()
            init_messages = [
                {"role": "user", "content": agent_config["init_message"]}
            ]
            response_text, updated_messages = call_agent(client, init_messages, current_agent)
            st.session_state.messages[current_agent] = updated_messages
            st.session_state.initialized[current_agent] = True
            st.session_state.chat_history[current_agent].append(
                {"role": "assistant", "content": response_text}
            )
            st.markdown(response_text, unsafe_allow_html=True)

# ユーザー入力
if user_input := st.chat_input(agent_config["placeholder"]):
    # ユーザーメッセージ表示
    with st.chat_message("user", avatar="🧑‍💼"):
        st.markdown(user_input)
    st.session_state.chat_history[current_agent].append(
        {"role": "user", "content": user_input}
    )

    # API呼び出し
    with st.chat_message("assistant", avatar=agent_config["icon"]):
        with st.spinner("考えています..."):
            client = get_client()
            st.session_state.messages[current_agent].append(
                {"role": "user", "content": user_input}
            )
            response_text, updated_messages = call_agent(
                client, st.session_state.messages[current_agent], current_agent
            )
            st.session_state.messages[current_agent] = updated_messages
            st.session_state.chat_history[current_agent].append(
                {"role": "assistant", "content": response_text}
            )
            st.markdown(response_text, unsafe_allow_html=True)
