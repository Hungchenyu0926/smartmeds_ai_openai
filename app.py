import streamlit as st
import gspread
from openai import OpenAI
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="SmartMeds-AI", layout="centered")
st.title("💊 SmartMeds-AI 用藥建議與交互作用小幫手")

# Google Sheets 認證
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["GSPREAD_CREDENTIALS"], scope)
gs_client = gspread.authorize(creds)
sheet = gs_client.open("SmartMeds_DB").sheet1

# OpenAI 認證
openai_client = OpenAI(api_key=st.secrets["OPENAI"]["api_key"])

# 用藥建議產生器
def get_drug_advice(drug_name, age, condition):
    prompt = (
        f"你是一位藥師。請提供藥品「{drug_name}」的用途、副作用，"
        f"並針對年齡 {age} 歲、有「{condition}」病史者給出注意事項與建議。"
        "回覆請使用繁體中文，並分段清晰陳述。"
    )
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        return resp.choices[0].message.content
    except Exception as e:
        # 印出錯誤訊息到畫面，方便你知道具體原因
        st.error(f"🛑 OpenAI 呼叫失敗：{e}")
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




