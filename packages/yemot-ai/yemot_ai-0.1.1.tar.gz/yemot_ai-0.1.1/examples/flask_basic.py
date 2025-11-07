"""
דוגמת שימוש בסיסית של yemot-ai עם Flask ו-yemot-flow.

דוגמה זו מראה איך ליצור מערכת IVR פשוטה שמחברת למשתמש סוכן AI
באמצעות Codex CLI. המערכת כוללת:

1. שלוחה ראשית עם תפריט בחירה
2. שלוחת AI שמנהלת שיחה רציפה עם הסוכן
3. טיפול אוטומטי בסשנים וניקוי בסיום שיחה

הערות חשובות:
- הדוגמה מניחה שיש מנגנון ASR (Speech-to-Text) שמחזיר טקסט בפרמטר RecordingText
- בפועל תצטרך להשלים את החלק הזה או להשתמש ב-DTMF במקום דיבור חופשי
- ודא שCodex CLI מותקן ונגיש ב-PATH לפני הרצת הדוגמה
"""

from flask import Flask, request, Response
from yemot_flow import Flow
from yemot_ai import AI, handle_yemot_hangup, JSONSessionStore
import logging

# הגדרת לוגים
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# יצירת אובייקט Flow עם timeout מוגדל עבור AI
flow = Flow(timeout=45000, print_log=True)

# יצירת מנהל AI עם אחסון JSON (נשאר בין הפעלות שרת)
ai_manager = AI.create_codex_ai(
    session_store=JSONSessionStore("ai_sessions.json")
)

# או אלטרנטיבה עם אחסון בזיכרון בלבד:
# ai_manager = AI.create_codex_ai()

# לבדיקות ללא Codex, ניתן להשתמש ב-MockAI:
# ai_manager = AI.create_mock_ai()


@flow.get("")  # שלוחה ראשית
def welcome(call):
    """שלוחה ראשית - תפריט בחירה למשתמש."""
    call.play_message([
        ("text", "שלום וברוך הבא למערכת הסיוע החכמה של ימות המשיח!"),
        ("text", "הקש 1 כדי לדבר עם סוכן ה-AI החכם"),
        ("text", "הקש 2 כדי לשמוע מידע כללי"),
        ("text", "הקש 0 כדי לסיים את השיחה")
    ])
    
    call.read([("text", "אנא בחר אפשרות")], max_digits=1, block_asterisk=True)
    
    choice = call.params.get("Digits", "")
    
    if choice == "1":
        call.goto("/ai_chat")
    elif choice == "2":
        call.goto("/info")
    elif choice == "0":
        call.play_message([("text", "תודה שפנית אלינו. יום טוב!")])
        call.hangup()
    else:
        call.play_message([("text", "בחירה לא חוקית. אנא נסה שוב.")])
        call.goto("")


@flow.get("info")
def info(call):
    """מידע כללי על המערכת."""
    call.play_message([
        ("text", "זוהי מערכת ניסיונית לשיחה עם סוכן AI."),
        ("text", "הסוכן יכול לעזור לך עם שאלות שונות, לספק מידע, ולנהל איתך שיחה טבעיית."),
        ("text", "לחזרה לתפריט הראשי הקש כוכבית.")
    ])
    
    call.read([("text", "הקש כוכבית לחזרה לתפריט")], max_digits=1)
    call.goto("")


@flow.get("ai_chat")
def ai_chat_start(call):
    """התחלת שיחת AI - הסבר והנחיות למשתמש."""
    call_id = call.params.get("ApiCallId")
    
    # בדיקה האם יש כבר שיחה פעילה
    if ai_manager.has_active_conversation(call_id):
        call.play_message([
            ("text", "נמשיך את השיחה מהמקום שבו הפסקנו."),
            ("text", "מה תרצה לומר?")
        ])
    else:
        call.play_message([
            ("text", "נהדר! אתה עומד להתחיל שיחה עם הסוכן החכם שלנו."),
            ("text", "הסוכן יוכל לענות על שאלות, לעזור עם בעיות, ולנהל איתך שיחה טבעית."),
            ("text", "דבר בבירור לאחר הצפצוף. בסיום ההודעה שלך, המתן לתשובת הסוכן."),
            ("text", "כדי לחזור לתפריט הראשי, אמור 'תפריט ראשי' או הקש כוכבית ואפס.")
        ])
    
    # מעבר לשיחה עצמה
    call.goto("/ai_conversation")


@flow.get("ai_conversation")
def ai_conversation(call):
    """
    הליבה של שיחת ה-AI.
    
    מטפל בהקלטת דיבור המשתמש, שליחה לסוכן AI, והשמעת התשובה.
    """
    call_id = call.params.get("ApiCallId")
    user_text = call.params.get("RecordingText")  # טקסט מזוהה מההקלטה
    
    # אם זוהי הקריאה הראשונה ואין עדיין הקלטה
    if not user_text:
        call.play_message([("text", "דבר עכשיו אחרי הצפצוף")])
        call.record(
            max_seconds=10,      # מקסימום 10 שניות הקלטה
            silence_timeout=3,   # סיום אוטומטי אחרי 3 שניות שקט
            speech_timeout=1     # התחלת מדידת שקט אחרי שנייה אחת של דיבור
        )
        return
    
    # בדיקת פקודות מיוחדות
    user_text_lower = user_text.lower().strip()
    
    if "תפריט ראשי" in user_text_lower or "תפריט" in user_text_lower:
        call.play_message([("text", "חוזר לתפריט הראשי")])
        call.goto("")
        return
    
    if "סיום" in user_text_lower or "להתראות" in user_text_lower or "ביי" in user_text_lower:
        call.play_message([("text", "תודה על השיחה! יום טוב!")])
        ai_manager.end_conversation(call_id)  # ניקוי סשן
        call.hangup()
        return
    
    # שליחת ההודעה לסוכן AI וקבלת תשובה
    try:
        logger.info(f"שולח לסוכן AI ({call_id}): {user_text[:50]}...")
        ai_response = ai_manager.reply(call_id, user_text)
        logger.info(f"תשובת AI ({call_id}): {ai_response[:50]}...")
        
        # השמעת תשובת ה-AI
        call.play_message([("text", ai_response)])
        
        # בקשת הודעה נוספת מהמשתמש
        call.play_message([("text", "יש לך עוד שאלה? דבר אחרי הצפצוף, או אמור 'סיום' לסיום השיחה.")])
        call.record(
            max_seconds=10,
            silence_timeout=3,
            speech_timeout=1
        )
        
    except Exception as e:
        logger.error(f"שגיאה בטיפול בהודעת AI עבור {call_id}: {e}")
        
        call.play_message([
            ("text", "מצטער, אירעה שגיאה זמנית בחיבור לסוכן החכם."),
            ("text", "אנא נסה שוב בעוד מעט, או חזור לתפריט הראשי.")
        ])
        
        call.read([("text", "הקש כוכבית לתפריט הראשי")], max_digits=1)
        call.goto("")


# טיפול בדפי שגיאה (אופציונלי)
@flow.get("error")
def error_handler(call):
    """טיפול כללי בשגיאות."""
    call.play_message([
        ("text", "אירעה שגיאה במערכת."),
        ("text", "אנא נסה שוב מאוחר יותר או פנה לתמיכה.")
    ])
    call.hangup()


# נתיב Flask ראשי לטיפול בבקשות מימות המשיח
@app.route("/yemot", methods=["GET", "POST"])
def yemot_handler():
    """
    נקודת הכניסה הראשית לבקשות מימות המשיח.
    
    מעבד את הבקשה באמצעות yemot-flow ומטפל בניקוי סשנים.
    """
    params = request.values.to_dict()
    
    try:
        # עיבוד הבקשה באמצעות yemot-flow
        xml_response = flow.handle_request(params)
        
        # טיפול בסיום שיחה (ניקוי סשנים)
        handle_yemot_hangup(ai_manager, params)
        
        return Response(xml_response, mimetype="text/xml")
        
    except Exception as e:
        logger.error(f"שגיאה בעיבוד בקשת ימות: {e}")
        
        # החזרת תשובת שגיאה בפורמט XML של ימות
        error_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say>אירעה שגיאה במערכת. אנא נסה שוב מאוחר יותר.</Say>
            <Hangup/>
        </Response>'''
        
        return Response(error_xml, mimetype="text/xml")


# נתיב לבדיקת תקינות המערכת
@app.route("/health", methods=["GET"])
def health_check():
    """בדיקת תקינות המערכת."""
    try:
        # בדיקה בסיסית שהמערכת עובדת
        session_info = ai_manager.get_session_info("health_check")
        
        return {
            "status": "healthy",
            "ai_provider": session_info.get("provider_type"),
            "session_store": session_info.get("session_store_type"),
            "message": "המערכת פועלת תקין"
        }
        
    except Exception as e:
        logger.error(f"שגיאה בבדיקת תקינות: {e}")
        return {
            "status": "error", 
            "message": f"שגיאה: {e}"
        }, 500


# נתיב לניהול סשנים (לצרכי debugging - להסיר בפרודקשן)
@app.route("/admin/sessions", methods=["GET"])
def list_sessions():
    """רשימת סשנים פעילים (לצרכי debugging בלבד)."""
    try:
        if hasattr(ai_manager.session_store, 'get_all_sessions'):
            sessions = ai_manager.session_store.get_all_sessions()
            return {
                "active_sessions": len(sessions),
                "sessions": sessions
            }
        else:
            return {"message": "לא ניתן להציג סשנים עם סוג אחסון זה"}
            
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/admin/clear_sessions", methods=["POST"])
def clear_all_sessions():
    """ניקוי כל הסשנים (לצרכי תחזוקה)."""
    try:
        ai_manager.clear_all_sessions()
        return {"message": "כל הסשנים נוקו בהצלחה"}
    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == "__main__":
    # הרצת השרת בסביבת פיתוח
    print("מפעיל שרת yemot-ai...")
    print("נקודת כניסה לימות המשיח: http://localhost:5000/yemot")
    print("בדיקת תקינות: http://localhost:5000/health")
    
    app.run(
        debug=True,      # מצב debug (להסיר בפרודקשן)
        host="0.0.0.0",  # מאפשר גישה מהרשת
        port=5000        # פורט השרת
    )