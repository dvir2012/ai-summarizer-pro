import streamlit as st
import google.generativeai as genai  # החלפנו את openai בספרייה של גוגל

# הגדרת דף ראשונית
st.set_page_config(page_title="Summarizer AI Pro", page_icon="📝")

st.title("הבוט האישי שלי לסיכום טקסטים 🤖")

# --- תפריט צד (Sidebar) להגדרות ---
st.sidebar.header("הגדרות סיכום ⚙️")
language = st.sidebar.selectbox("שפת הסיכום:", ["Hebrew", "English", "Spanish", "French"])
style = st.sidebar.radio("סגנון:", ["נקודות (Bullet Points)", "פסקה (Paragraph)"])
detail_level = st.sidebar.select_slider("רמת פירוט:", options=["תמציתי", "בינוני", "מפורט"])

# חיבור ל-API של גוגל
try:
    # שליפת המפתח מה-Secrets (נשתמש באותו שם מפתח כדי שלא תצטרך לשנות הגדרות ב-Streamlit)
    genai.configure(api_key=st.secrets["OPENAI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash') # שימוש במודל מהיר ויעיל
except Exception as e:
    st.error(f"שגיאה בהגדרת המפתח: {e}")
    st.stop()

# --- אזור הקלט ---
user_text = st.text_area("הדבק כאן את הטקסט שברצונך לסכם:", height=250)

# פיצ'ר: מונה מילים בזמן אמת
word_count = len(user_text.split())
st.caption(f"📊 כמות מילים בטקסט: {word_count}")

# --- לוגיקת הסיכום ---
if st.button("התחל בסיכום ✨"):
    if word_count == 0:
        st.warning("נא להזין טקסט לסיכום.")
    elif word_count > 10000: # Gemini תומך בטקסטים הרבה יותר ארוכים!
        st.error("הטקסט ארוך מדי. נסה לקצר מעט.")
    else:
        with st.spinner('הבינה המלאכותית של גוגל מעבדת את המידע...'):
            try:
                # בניית פרומפט מותאם ל-Gemini
                prompt = (
                    f"Please summarize the following text in {language}. "
                    f"Use a {style} style with a {detail_level} level of detail.\n\n"
                    f"Text: {user_text}"
                )
                
                # קריאה ל-Gemini
                response = model.generate_content(prompt)
                summary = response.text
                
                # הצגת התוצאה
                st.markdown("---")
                st.subheader("הסיכום המוכן:")
                st.write(summary)
                
                # כפתור הורדה
                st.download_button(
                    label="הורד סיכום כקובץ טקסט 📥",
                    data=summary,
                    file_name="summary.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"שגיאה בתקשורת עם Gemini: {e}")
