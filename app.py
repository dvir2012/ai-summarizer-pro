import streamlit as st
from openai import OpenAI

# הגדרת דף ראשונית
st.set_page_config(page_title="Summarizer AI Pro", page_icon="📝")

st.title("הבוט האישי שלי לסיכום טקסטים 🤖")

# --- תפריט צד (Sidebar) להגדרות ---
st.sidebar.header("הגדרות סיכום ⚙️")
language = st.sidebar.selectbox("שפת הסיכום:", ["Hebrew", "English", "Spanish", "French"])
style = st.sidebar.radio("סגנון:", ["נקודות (Bullet Points)", "פסקה (Paragraph)"])
detail_level = st.sidebar.select_slider("רמת פירוט:", options=["תמציתי", "בינוני", "מפורט"])

# חיבור ל-API
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("מפתח ה-API לא נמצא בהגדרות המערכת!")
    st.stop()

# --- אזור הקלט ---
user_text = st.text_area("הדבק כאן את הטקסט שברצונך לסכם:", height=250)

# פיצ'ר: מונה מילים בזמן אמת
word_count = len(user_text.split())
st.caption(f"📊 כמות מילים בטקסט: {word_count}")

# --- לוגיקת הסיכום ---
if st.button("התחל בסיכום ✨"):
    # פיצ'ר: הגנה ובדיקת תקינות
    if word_count == 0:
        st.warning("נא להזין טקסט לסיכום.")
    elif word_count > 2500:
        st.error("הטקסט ארוך מדי (מעל 2500 מילים). נסה לפצל אותו.")
    else:
        with st.spinner('הבינה המלאכותית מעבדת את המידע...'):
            try:
                # בניית פרומפט חכם שמשתמש בבחירות המשתמש
                prompt = (
                    f"Please summarize the following text in {language}. "
                    f"Use a {style} style with a {detail_level} level of detail.\n\n"
                    f"Text: {user_text}"
                )
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                summary = response.choices[0].message.content
                
                # הצגת התוצאה
                st.markdown("---")
                st.subheader("הסיכום המוכן:")
                st.write(summary)
                
                # פיצ'ר: כפתור הורדה
                st.download_button(
                    label="הורד סיכום כקובץ טקסט 📥",
                    data=summary,
                    file_name="summary.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"שגיאה בתקשורת: {e}")
