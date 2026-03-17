import streamlit as st
import google.generativeai as genai
import pandas as pd
from PyPDF2 import PdfReader
import io
import time

# --- הגדרות דף ועיצוב (UI/UX) ---
st.set_page_config(page_title="Summarizer Elite Pro", page_icon="🛡️", layout="wide")

def apply_custom_design():
    st.markdown("""
        <style>
        .main { background-color: #f0f2f6; }
        .stButton>button {
            border-radius: 12px;
            height: 3em;
            background: linear-gradient(45deg, #007bff, #00d4ff);
            color: white;
            font-weight: bold;
            border: none;
        }
        .summary-card {
            background-color: white;
            padding: 20px;
            border-radius: 15px;
            border-right: 5px solid #007bff;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

apply_custom_design()

# --- ניהול זיכרון (Session State) ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- פונקציות עזר לעיבוד טקסט ---
def extract_text_from_pdf(file):
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

def clean_text(text):
    # הסרת רווחים כפולים ותווים לא רצויים
    return " ".join(text.split())

# --- לוגיקת AI ---
def get_ai_summary(model_name, prompt, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        start_time = time.time()
        response = model.generate_content(prompt)
        end_time = time.time()
        
        return {
            "model": model_name,
            "text": response.text,
            "time": round(end_time - start_time, 2),
            "status": "Success"
        }
    except Exception as e:
        return {"model": model_name, "text": str(e), "time": 0, "status": "Failed"}

# --- ממשק משתמש מרכזי ---
st.title("Summarizer Elite Pro v3.0 🚀")
st.write("מערכת סיכום מתקדמת עם תמיכה בריבוי מודלים וקבצים.")

# תפריט צד להגדרות
with st.sidebar:
    st.header("הגדרות מערכת ⚙️")
    api_key = st.text_input("הזן מפתח API (אם לא הוגדר ב-Secrets):", type="password")
    if not api_key:
        api_key = st.secrets.get("OPENAI_API_KEY", "")
    
    selected_models = st.multiselect(
        "בחר מודלים להשוואה:",
        ['gemini-2.0-flash-001', 'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro'],
        default=['gemini-1.5-flash']
    )
    
    language = st.selectbox("שפה:", ["Hebrew", "English", "French"])
    detail = st.select_slider("רמת פירוט:", ["תמציתי", "מאוזן", "מפורט"])

# אזור קלט
tab1, tab2 = st.tabs(["📝 הזנת טקסט/קובץ", "📜 היסטוריית סיכומים"])

with tab1:
    col_input, col_info = st.columns([2, 1])
    
    with col_input:
        uploaded_file = st.file_uploader("העלה קובץ PDF או TXT", type=["pdf", "txt"])
        raw_input = st.text_area("או הדבק טקסט כאן:", height=200)
        
        final_text = ""
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                final_text = extract_text_from_pdf(uploaded_file)
            else:
                final_text = str(uploaded_file.read(), "utf-8")
        else:
            final_text = raw_input

    with col_info:
        st.info("סטטיסטיקת קלט")
        words = len(final_text.split())
        st.metric("כמות מילים", words)
        if words > 10000:
            st.warning("טקסט ארוך מאוד - ייתכן זמן עיבוד ממושך.")

    if st.button("בצע סיכום והשוואה ✨"):
        if not final_text:
            st.error("נא להזין טקסט או להעלות קובץ.")
        else:
            results = []
            prompt = f"Summarize the following text in {language} with {detail} detail. Text: {final_text}"
            
            progress_bar = st.progress(0)
            for i, m_name in enumerate(selected_models):
                res = get_ai_summary(m_name, prompt, api_key)
                results.append(res)
                progress_bar.progress((i + 1) / len(selected_models))
            
            # הצגת תוצאות
            for res in results:
                with st.container():
                    st.markdown(f'<div class="summary-card">', unsafe_allow_html=True)
                    st.subheader(f"מודל: {res['model']}")
                    if res['status'] == "Success":
                        st.write(res['text'])
                        st.caption(f"⏱️ זמן עיבוד: {res['time']} שניות")
                        
                        # שמירה להיסטוריה
                        st.session_state.history.append({
                            "זמן": time.strftime("%H:%M:%S"),
                            "מודל": res['model'],
                            "סיכום": res['text'][:100] + "..."
                        })
                    else:
                        st.error(f"שגיאה: {res['text']}")
                    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.table(df)
        if st.button("נקה היסטוריה"):
            st.session_state.history = []
            st.rerun()
    else:
        st.write("אין עדיין היסטוריה להצגה.")
