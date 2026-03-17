import streamlit as st
import google.generativeai as genai

# הגדרת דף
st.set_page_config(page_title="Summarizer AI Pro", page_icon="📝")
st.title("הבוט האישי שלי לסיכום טקסטים 🤖")

# --- תפריט צד (Sidebar) ---
st.sidebar.header("הגדרות סיכום ⚙️")

# הוספת בחירת מודל מהרשימה שלך
available_models = [
    'gemini-2.0-flash-001',
    'gemini-2.5-flash',
    'gemini-2.5-pro',
    'gemini-pro',
    'gemini-1.5-pro'
]
selected_model_name = st.sidebar.selectbox("בחר מודל בינה מלאכותית:", available_models)

language = st.sidebar.selectbox("שפת הסיכום:", ["Hebrew", "English", "Spanish", "French"])
style = st.sidebar.radio("סגנון:", ["נקודות (Bullet Points)", "פסקה (Paragraph)"])
detail_level = st.sidebar.select_slider("רמת פירוט:", options=["תמציתי", "בינוני", "מפורט"])

# חיבור ל-API
try:
    genai.configure(api_key=st.secrets["OPENAI_API_KEY"])
    # יצירת המודל לפי הבחירה של המשתמש
    model = genai.GenerativeModel(selected_model_name)
except Exception as e:
    st.error(f"שגיאה בהגדרת המפתח: {e}")
    st.stop()

# --- אזור הקלט והלוגיקה (נשאר דומה) ---
user_text = st.text_area("הדבק כאן את הטקסט שברצונך לסכם:", height=250)
word_count = len(user_text.split())
st.caption(f"📊 כמות מילים בטקסט: {word_count} | מודל פעיל: {selected_model_name}")

if st.button("התחל בסיכום ✨"):
    if word_count == 0:
        st.warning("נא להזין טקסט לסיכום.")
    else:
        with st.spinner(f'המודל {selected_model_name} מעבד את המידע...'):
            try:
                prompt = (
                    f"Please summarize the following text in {language}. "
                    f"Use a {style} style with a {detail_level} level of detail.\n\n"
                    f"Text: {user_text}"
                )
                
                response = model.generate_content(prompt)
                
                if response.text:
                    st.markdown("---")
                    st.subheader("הסיכום המוכן:")
                    st.write(response.text)
                    
                    st.download_button(
                        label="הורד סיכום כקובץ טקסט 📥",
                        data=response.text,
                        file_name="summary.txt",
                        mime="text/plain"
                    )
            except Exception as e:
                st.error(f"שגיאה: המודל שנבחר לא זמין או שקיימת בעיית תקשורת. פרטי השגיאה: {e}")
