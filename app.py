import streamlit as st
import gspread
from openai import OpenAI
from oauth2client.service_account import ServiceAccountCredentials



st.set_page_config(page_title="SmartMeds-AI", layout="centered")
st.title("💊 SmartMeds-AI 用藥建議小幫手")

# Google Sheets 認證
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["GSPREAD_CREDENTIALS"], scope)
gs_client = gspread.authorize(creds)
sheet = gs_client.open("SmartMeds_DB").sheet1

# OpenAI 客戶端（新版 SDK）
openai_client = OpenAI(api_key=st.secrets["OPENAI"]["api_key"])

from openai.error import OpenAIError  # v1.x SDK 例外都在這裡

def get_drug_advice(drug_name, age, condition):
    prompt = (
        f"你是一位藥師。請提供藥品「{drug_name}」的用途、副作用，"
        f"並針對年齡 {age} 歲、有「{condition}」病史者給出注意事項與建議。"
        "回覆請使用繁體中文，並分段清晰陳述。"
    )
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",  # 確定你有權限呼叫
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        return resp.choices[0].message.content
    except OpenAIError as e:
        # 將 HTTP 狀態與錯誤訊息印在 UI 上
        st.error(f"🛑 OpenAI API 調用錯誤：{e}")
        return None


# 使用者介面
drug = st.text_input("🔎 請輸入藥品名稱")
age = st.number_input("👤 年齡", min_value=1, max_value=120, value=65)
condition = st.text_input("🩺 病史或慢性疾病")

if st.button("📋 查詢用藥建議"):
    if not drug:
        st.warning("請先輸入藥品名稱。")
    else:
        with st.spinner("正在查詢中..."):
            advice = get_drug_advice(drug, age, condition)
            if advice:
                st.markdown(advice)
            # 如果 advice 是 None，就代表上面已經用 st.error() 顯示了
if st.button("🚥 測試 OpenAI 連線"):
    try:
        test = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"user","content":"Hello"}],
            max_tokens=5,
        )
        st.success("✅ OpenAI 連線正常，回覆：" + test.choices[0].message.content)
    except OpenAIError as e:
        st.error(f"❌ 測試失敗：{e}")


