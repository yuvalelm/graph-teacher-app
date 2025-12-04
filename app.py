import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- הגדרת עמוד ---
st.set_page_config(page_title="מייצר הפעילויות הגרפיות", page_icon="📊", layout="wide")

# --- כותרת ועיצוב ---
st.title("📊 מייצר הפעילויות הגרפיות למורים")
st.markdown("""
**ברוכים הבאים!** אני העוזר האישי שלך לבניית שיעורי מדעים מבוססי גרפים.
1. העלו תמונה של גרף.
2. אני אנתח אותו.
3. בחרו משחק ורמה - ואני אצור לכם מערך שיעור מושלם.
""")

# --- סרגל צד למפתח ---
with st.sidebar:
    st.header("הגדרות")
    api_key = st.text_input("הכנס מפתח Google Gemini API", type="password")
    st.info("כדי להשתמש באפליקציה, יש להכניס מפתח API (ניתן להשיג בחינם מ-Google AI Studio).")
    st.markdown("---")
    st.markdown("**רשימת המשחקים:**\n1. 🎨 צייר לי גרף\n2. 🚶 יצאתי לטייל\n3. 🗣️ מי אמר את זה?\n4. 🔬 מה קורה פה?")

# --- פונקציות עזר ---
def analyze_image(image, key):
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-1.5-flash-
    prompt = """
    נתח את הגרף הזה עבור מורה למדעים.
    התייחס ל: כותרת, צירים (X,Y) ויחידות, מגמות עיקריות (עלייה/ירידה), נקודות קיצון וחיתוכים בולטים.
    כתוב את הניתוח בעברית, בשפה ברורה, כרשימת תבליטים.
    """
    response = model.generate_content([prompt, image])
    return response.text

def generate_activity(image, game_type, level, analysis_text, key):
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    base_prompt = f"""
    אתה עוזר פדגוגי מומחה.
    המשתמש בחר את המשחק: "{game_type}" ברמת קושי: "{level}".
    
    הנה ניתוח הגרף שעליו מתבססים:
    {analysis_text}
    
    עליך לייצר מצגת מלאה (טקסט בלבד) לפי המבנה הבא:
    Slide 1: כותרת המשחק ונושא.
    Slide 2: הסבר על הגרף (מבוסס על הניתוח).
    Slides 3-7: 5 שאלות/חידות/טענות המותאמות למשחק שנבחר ולרמה שנבחרה.
    Slide 8: פתרונות מלאים ונימוקים.
    Slide 9: שאלות לדיון מדעי (אלא אם זה משחק "מה קורה פה" - אז אין צורך).
    
    כללי משחקים:
    - "צייר לי גרף": תיאור מילולי שהתלמיד צריך לצייר.
    - "יצאתי לטייל": סיפור מסלול על הגרף.
    - "מי אמר את זה?": טענות נכונות/שגויות של דמויות.
    - "מה קורה פה?": שאלות חקר מדעי (משתנים, בקרה, השערות).
    
    השתמש בפורמט כימי פשוט (H2O). כתוב בעברית, בפורמט Markdown יפה וקריא.
    """
    
    response = model.generate_content([base_prompt, image])
    return response.text

# --- לוגיקה ראשית ---
uploaded_file = st.file_uploader("העלה תמונה של גרף (PNG, JPG)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='הגרף שהועלה', use_column_width=True)
    
    if api_key:
        if 'analysis' not in st.session_state or st.session_state.uploaded_file_name != uploaded_file.name:
            with st.spinner('מנתח את הגרף...'):
                try:
                    analysis = analyze_image(image, api_key)
                    st.session_state.analysis = analysis
                    st.session_state.uploaded_file_name = uploaded_file.name
                except Exception as e:
                    st.error(f"שגיאה בניתוח: {e}")

        if 'analysis' in st.session_state:
            st.success("הניתוח הושלם!")
            st.subheader("🔍 ניתוח הגרף:")
            st.markdown(st.session_state.analysis)
            
            st.markdown("---")
            st.subheader("⚙️ יצירת הפעילות")
            
            col1, col2 = st.columns(2)
            with col1:
                game = st.selectbox("בחר משחק:", 
                                    ["צייר לי גרף", "יצאתי לטייל — לאן הגעתי?", "מי אמר את זה?", "מה קורה פה?"])
            with col2:
                level = st.select_slider("רמת קושי:", options=["בסיסית", "בינונית", "גבוהה"])
            
            if st.button("צור מצגת שיעור 🚀"):
                with st.spinner('כותב את המצגת... זה לוקח כמה שניות...'):
                    try:
                        lesson_plan = generate_activity(image, game, level, st.session_state.analysis, api_key)
                        st.session_state.lesson_plan = lesson_plan
                    except Exception as e:
                        st.error(f"שגיאה ביצירה: {e}")

            if 'lesson_plan' in st.session_state:
                st.markdown("---")
                st.subheader("📝 המצגת המוכנה שלך:")
                st.markdown(st.session_state.lesson_plan)
                st.download_button("הורד את המצגת כקובץ טקסט", st.session_state.lesson_plan, file_name="lesson.md")
    else:
        st.warning("נא להזין מפתח API בסרגל הצד כדי להמשיך.")
