# app.py
import os
from dotenv import load_dotenv
import streamlit as st

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# === 環境変数 (.env / Secrets) ===
load_dotenv()
if "OPENAI_API_KEY" not in os.environ:
    try:
        os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass

st.set_page_config(page_title="LLM Expert App", page_icon="💬", layout="centered")
st.title("💬 LLM Expert App (Streamlit × LangChain)")
st.caption("選んだ“専門家”の視点で回答します。ラジオで専門家を選び、テキストを送信してください。")

with st.expander("📝 このアプリの使い方 / 概要", expanded=True):
    st.markdown(
        """
**操作**  
1) 右のラジオで専門家を選ぶ  
2) 入力欄に相談内容を記入  
3) 「回答を生成」を押す

**技術**  
- Streamlit / LangChain（ChatOpenAI）  
- APIキー: `.env`（ローカル） or **Secrets**（Cloud）
        """
    )

EXPERT_ROLES = {
    "ヘルスコーチ": "あなたはプロのヘルスコーチです。生活習慣改善、睡眠、運動、栄養の観点から、具体的で実行しやすいアドバイスを日本語で200〜400文字で提案してください。",
    "ビジネスストラテジスト": "あなたは新規事業と収益化に強いビジネスストラテジストです。課題を構造化し、3つの実行アクションと1週間の短期KPIを日本語で200〜400文字で提案してください。",
    "英語学習コーチ": "あなたはCEFRに基づく英語学習コーチです。学習目的やレベルを推定し、1週間の具体的学習プラン（毎日のメニュー）を日本語で200〜400文字で提示してください。"
}

BASE_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "{system_msg}"),
        ("user", "{user_input}"),
    ]
)

def generate_response(user_text: str, expert_choice: str) -> str:
    if not user_text.strip():
        return "入力テキストが空です。内容を入力してください。"
    system_msg = EXPERT_ROLES.get(expert_choice, list(EXPERT_ROLES.values())[0])
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5, max_tokens=600)
    chain = BASE_PROMPT | llm | StrOutputParser()
    return chain.invoke({"system_msg": system_msg, "user_input": user_text})

with st.sidebar:
    st.header("⚙️ 設定")
    expert_choice = st.radio("専門家の種類を選択", list(EXPERT_ROLES.keys()), index=0)
    st.markdown("---")
    st.markdown("**Python 3.11 推奨**（CloudのAdvanced settingsで指定）")
    st.markdown("APIキーは `.env` または Secrets に `OPENAI_API_KEY` を設定")

user_text = st.text_area(
    "相談内容 / 質問を入力",
    placeholder="例）最近よく眠れません。仕事のパフォーマンスを保ちながら、睡眠の質を上げる方法を教えてください。",
    height=180,
)
if st.button("回答を生成", type="primary"):
    with st.spinner("生成中..."):
        try:
            ans = generate_response(user_text, expert_choice)
        except Exception as e:
            ans = f"エラーが発生しました。APIキーやネットワーク設定をご確認ください。\n\n詳細: {e}"
    st.markdown("### 🔎 回答")
    st.write(ans)
