import streamlit as st
import google.generativeai as genai
import pandas as pd
from PyPDF2 import PdfReader
from docx import Document
import io
import time
import datetime
import plotly.express as px

# --- 1. הגדרות דף ועיצוב CSS מקיף ---
st.set_page_config(
    page_title="Summarizer Elite Pro 2026",
    page_icon="🧬",
    layout="wide"
)

def inject_custom_css():
    st.markdown("""
        <style>
        /* אנימציית רקע טכנולוגי זז - Deep Space Flow */
        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .stApp {
            background: linear-gradient(-45deg, #0f172a, #1e293b, #1e3a8a, #020617) !important;
            background-size: 400% 400% !important;
            animation: gradientBG 15s ease infinite !important;
            color: #f8fafc !important;
        }

        /* עיצוב כותרת טכנולוגית */
        h1 {
            color: #38bdf8 !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-weight: 800 !important;
            text-transform: uppercase;
            letter-spacing: 2px;
            text-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
            text-align: center;
        }

        /* כרטיסיות זכוכית (Glassmorphism) */
        .result-card {
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(15px) !important;
            -webkit-backdrop-filter: blur(15px);
            padding: 30px;
            border-radius: 20px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-right: 10px solid #38bdf8 !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5) !important;
            margin-bottom: 25px;
        }

        /* כפתור "מנוע AI" עם אפקט זהירה */
        .stButton>button {
            width: 100%;
            border-radius: 12px !important;
            height: 3.8em;
            background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%) !important;
            color: white !important;
            font-weight: bold !important;
            border: none !important;
            box-shadow: 0 0 20px rgba(37, 99, 235, 0.4) !important;
            transition: 0.4s !important;
        }
        .stButton>button:hover {
            transform: scale(1.02) translateY(-2px) !important;
            box-shadow: 0 0 30px rgba(14, 165, 233, 0.6) !important;
        }

        /* תיבות סטטיסטיקה מעוצבות */
        .stats-box {
            background: rgba(15, 23, 42, 0.8) !important;
            padding: 20px;
            border-radius: 15px !important;
            text-align: center;
            border: 1px solid #38bdf8 !important;
            color: #38bdf8 !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }

        /* עיצוב Sidebar (פאנל ניהול) */
        [data-testid="stSidebar"] {
            background: rgba(15, 23, 42, 0.9) !important;
            backdrop-filter: blur(10px) !important;
            border-right: 1px solid rgba(56, 189, 248, 0.2) !important;
        }

        /* התאמת צבעי טקסט כלליים */
        .stMarkdown, p, span, label {
            color: #e2e8f0 !important;
        }
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# --- 2. אתחול זיכרון (Session State) ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

# --- 3. פונקציות עזר (קבצים, ניתוח, ייצוא) ---

def get_text_from_pdf(file):
    reader = PdfReader(file)
    return "".join([page.extract_text() for page in reader.pages if page.extract_text()])

def create_docx(text, model_name):
    doc = Document()
    doc.add_heading(f'Summary Report - {model_name}', 0)
    doc.add_paragraph(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    doc.add_heading('Summary Content:', level=1)
    doc.add_paragraph(text)
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def perform_sentiment_analysis(text):
    positive_words = ['good', 'great', 'excellent', 'positive', 'success', 'טוב', 'מעולה', 'הצלחה']
    negative_words = ['bad', 'poor', 'error', 'negative', 'failure', 'רע', 'גרוע', 'כישלון']
    
    pos_score = sum(1 for word in positive_words if word in text.lower())
    neg_score = sum(1 for word in negative_words if word in text.lower())
    
    if pos_score > neg_score: return "Positive 😊", "#10b981"
    if neg_score > pos_score: return "Negative 😟", "#ef4444"
    return "Neutral 😐", "#38bdf8"

# --- 4. ממשק משתמש (UI) ---
st.markdown("<h1>Summarizer Elite Pro v5.0 🧬</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ פאנל ניהול")
    
    model_list = [
        'models/gemini-2.0-flash-001',
        'models/gemini-2.5-flash',
        'models/gemini-2.5-pro',
        'models/gemini-pro',
        'models/gemini-1.5-pro'
    ]
    
    selected_models = st.multiselect("בחר מודלים להרצה (לפי סדר עדיפות):", model_list, default=[model_list[0]])
    lang = st.selectbox("שפת הסיכום:", ["Hebrew", "English", "Spanish", "Russian"])
    detail = st.select_slider("רמת פירוט:", ["תמציתי", "מאוזן", "מפורט"])
    
    st.markdown("---")
    api_key = st.text_input("מפתח API:", type="password")
    final_api_key = api_key if api_key else st.secrets.get("OPENAI_API_KEY", "")

# חלוקה לטאבים
tab1, tab2, tab3 = st.tabs(["🚀 מרכז עיבוד", "📜 היסטוריה", "📊 סטטיסטיקה"])

with tab1:
    col_in, col_stats = st.columns([2, 1])
    
    with col_in:
        uploaded_file = st.file_uploader("העלה מסמך (PDF/TXT):", type=["pdf", "txt"])
        raw_text = st.text_area("או הדבק טקסט:", height=200)
        
        content = ""
        if uploaded_file:
            content = get_text_from_pdf(uploaded_file) if uploaded_file.type == "application/pdf" else str(uploaded_file.read(), "utf-8")
        else:
            content = raw_text

    with col_stats:
        if content:
            words = len(content.split())
            st.markdown(f'<div class="stats-box"><h3>כמות מילים</h3><h2 style="color:#38bdf8">{words}</h2></div>', unsafe_allow_html=True)
            sentiment, color = perform_sentiment_analysis(content)
            st.markdown(f'<br><div class="stats-box" style="border-top: 5px solid {color}"><h3>סנטימנט משוער</h3><h2 style="color:{color}">{sentiment}</h2></div>', unsafe_allow_html=True)

    if st.button("הפעל מנוע AI משולב ✨"):
        if not content or not final_api_key:
            st.error("חובה להזין תוכן ומפתח API.")
        else:
            genai.configure(api_key=final_api_key)
            st.session_state.analysis_results = []
            any_success = False
            
            for m_name in selected_models:
                with st.spinner(f"מעבד נתונים בטכנולוגיית {m_name.split('/')[-1]}..."):
                    try:
                        model = genai.GenerativeModel(m_name)
                        prompt = f"Summarize this in {lang} with {detail} detail: {content}"
                        start = time.time()
                        resp = model.generate_content(prompt)
                        end = time.time()
                        
                        res_data = {
                            "model": m_name, "text": resp.text,
                            "time": round(end-start, 2), "date": datetime.datetime.now().strftime("%H:%M")
                        }
                        st.session_state.analysis_results.append(res_data)
                        st.session_state.history.append(res_data)
                        any_success = True
                        st.success(f"הצלחה עם מודל: {m_name}")
                        break 
                    except Exception as e:
                        continue
            
            if not any_success:
                st.error("כל המודלים חרגו מהמכסה. נסה שוב בעוד מספר רגעים.")

    if st.session_state.analysis_results:
        for res in st.session_state.analysis_results:
            st.markdown(f'<div class="result-card">', unsafe_allow_html=True)
            st.subheader(f"🤖 מודל: {res['model']}")
            st.write(res['text'])
            st.caption(f"⏱️ זמן עיבוד: {res['time']} שניות")
            
            c1, c2 = st.columns(2)
            c1.download_button("📥 הורד כ-TXT", res['text'], file_name=f"{res['model'].replace('/','_')}.txt", key=f"t_{res['model']}")
            docx_data = create_docx(res['text'], res['model'])
            c2.download_button("📄 הורד כ-Word", docx_data, file_name=f"{res['model'].replace('/','_')}.docx", key=f"d_{res['model']}")
            st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    if st.session_state.history:
        st.table(pd.DataFrame(st.session_state.history))
        if st.button("נקה הכל"):
            st.session_state.history = []
            st.rerun()

with tab3:
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        fig = px.bar(df, x="model", y="time", title="זמני עיבוד לפי מודל (שניות)", color="model", template="plotly_dark")
        st.plotly_chart(fig)
