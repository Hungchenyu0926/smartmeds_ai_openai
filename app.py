import streamlit as st
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="SmartMeds-AI", layout="centered")
st.title("💊 SmartMeds-AI 用藥建議與交互作用小幫手")

# Google Sheets 認證
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["GSPREAD_CREDENTIALS"], scope)
client = gspread.authorize(creds)
sheet = client.open("SmartMeds_DB").sheet1

# OpenAI 設定
openai.api_key = st.secrets["OPENAI"]["api_key"]

# 用藥建議產生器
def get_drug_advice(drug_name, age, condition):
    prompt = f"""你是一位藥師。請提供藥品「{drug_name}」的用途、副作用，並針對年齡 {age} 歲、有「{condition}」病史者給出注意事項與建議。
回覆請使用繁體中文，並分段清晰陳述。"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )
    return response.choices[0].message.content

# 使用者互動介面
drug = st.text_input("🔎 請輸入藥品名稱")
age = st.number_input("👤 年齡", min_value=1, max_value=120, value=65)
condition = st.text_input("🩺 病史或慢性疾病")

if st.button("📋 查詢用藥建議"):
    if drug:
        with st.spinner("正在查詢中..."):
            result = get_drug_advice(drug, age, condition)
            st.markdown(result)
    else:
        st.warning("請輸入藥品名稱。")
