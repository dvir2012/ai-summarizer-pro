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
        .main { background-color: #f4f7f6; }
        .stButton>button {
            width: 100%;
            border-radius: 12px;
            height: 3.5em;
            background: linear-gradient(135deg, #4b6cb7 0%, #182848 100%);
            color: white; font-weight: bold; border: none;
            transition: 0.3s;
        }
        .stButton>button:hover { transform: scale(1.02); }
        .result-card {
            background: white; padding: 25px; border-radius: 15px;
            border-right: 10px solid #4b6cb7; box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }
        .stats-box {
            background: #ffffff; padding: 15px; border-radius: 10px;
            text-align: center; border: 1px solid #e0e0e0;
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
    
    if pos_score > neg_score: return "Positive 😊", "#28a745"
    if neg_score > pos_score: return "Negative 😟", "#dc3545"
    return "Neutral 😐", "#6c757d"

# --- 4. ממשק משתמש (UI) ---
st.title("Summarizer Elite Pro v5.0 🧬")

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
            st.markdown(f'<div class="stats-box"><h3>כמות מילים</h3><h2>{words}</h2></div>', unsafe_allow_html=True)
            sentiment, color = perform_sentiment_analysis(content)
            st.markdown(f'<div class="stats-box" style="border-top: 5px solid {color}"><h3>סנטימנט משוער</h3><h2 style="color:{color}">{sentiment}</h2></div>', unsafe_allow_html=True)

    if st.button("הפעל מנוע AI משולב ✨"):
        if not content or not final_api_key:
            st.error("חובה להזין תוכן ומפתח API.")
        else:
            genai.configure(api_key=final_api_key)
            st.session_state.analysis_results = []
            any_success = False
            
            # לולאת Fallback חכמה
            for m_name in selected_models:
                with st.spinner(f"מנסה לעבד במודל {m_name}..."):
                    try:
                        model = genai.GenerativeModel(m_name)
                        prompt = f"Summarize this in {lang} with {detail} detail: {content}"
                        start = time.time()
                        resp = model.generate_content(prompt)
                        end = time.time()
                        
                        # אם הגענו לכאן סימן שהצלחנו
                        res_data = {
                            "model": m_name, "text": resp.text,
                            "time": round(end-start, 2), "date": datetime.datetime.now().strftime("%H:%M")
                        }
                        st.session_state.analysis_results.append(res_data)
                        st.session_state.history.append(res_data)
                        any_success = True
                        st.success(f"הצלחה עם מודל: {m_name}")
                        break # מפסיקים לנסות מודלים אחרים ברגע שאחד הצליח
                    except Exception as e:
                        # התעלמות שקטה מהשגיאה ומעבר למודל הבא
                        continue
            
            if not any_success:
                st.error("כל המודלים שנבחרו נכשלו או חרגו ממכסת השימוש. נסה שוב בעוד דקה או בחר מודלים אחרים.")

    # הצגת תוצאות
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
        fig = px.bar(df, x="model", y="time", title="זמני עיבוד לפי מודל (שניות)", color="model")
        st.plotly_chart(fig)
