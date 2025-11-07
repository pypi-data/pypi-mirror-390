"""
דוגמת שימוש מתקדמת עם FastAPI ו-yemot-ai.

דוגמה זו מראה:
1. שימוש ב-FastAPI במקום Flask
2. שימוש ב-OpenAI API במקום Codex CLI  
3. אחסון סשנים ב-Redis (אופציונלי)
4. הגדרות תצורה מקובץ
5. לוגים מתקדמים
6. API endpoints לניהול
"""

import os
import logging
from typing import Dict, Any
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
from yemot_flow import Flow
from yemot_ai import AI, handle_yemot_hangup, JSONSessionStore

# הגדרת לוגים
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# יצירת אפליקציה
app = FastAPI(
    title="Yemot AI Advanced Example",
    description="דוגמה מתקדמת לשימוש ב-yemot-ai עם FastAPI",
    version="1.0.0"
)

# הגדרות תצורה (ניתן להעביר למשתני סביבה או קובץ config)
class Config:
    # הגדרות AI
    AI_PROVIDER = os.getenv("AI_PROVIDER", "codex")  # codex, openai, mock
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # הגדרות אחסון
    SESSION_STORE_TYPE = os.getenv("SESSION_STORE_TYPE", "json")  # memory, json, redis
    SESSION_FILE_PATH = os.getenv("SESSION_FILE_PATH", "ai_sessions.json")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # הגדרות Flow
    FLOW_TIMEOUT = int(os.getenv("FLOW_TIMEOUT", "60000"))
    MAX_RECORDING_SECONDS = int(os.getenv("MAX_RECORDING_SECONDS", "15"))

config = Config()

# יצירת Flow
flow = Flow(timeout=config.FLOW_TIMEOUT, print_log=True)

# יצירת Session Store
def create_session_store():
    if config.SESSION_STORE_TYPE == "memory":
        from yemot_ai import MemorySessionStore
        return MemorySessionStore()
    elif config.SESSION_STORE_TYPE == "json":
        return JSONSessionStore(config.SESSION_FILE_PATH)
    elif config.SESSION_STORE_TYPE == "redis":
        try:
            from yemot_ai.session_store import RedisSessionStore
            return RedisSessionStore()
        except ImportError:
            logger.warning("Redis לא זמין, עובר לאחסון JSON")
            return JSONSessionStore(config.SESSION_FILE_PATH)
    else:
        raise ValueError(f"סוג אחסון לא נתמך: {config.SESSION_STORE_TYPE}")

session_store = create_session_store()

# יצירת AI Manager
def create_ai_manager():
    if config.AI_PROVIDER == "openai":
        if not config.OPENAI_API_KEY:
            raise ValueError("נדרש OPENAI_API_KEY למשתמש OpenAI")
        return AI.create_openai_ai(
            api_key=config.OPENAI_API_KEY,
            model=config.OPENAI_MODEL,
            session_store=session_store
        )
    elif config.AI_PROVIDER == "codex":
        return AI.create_codex_ai(session_store=session_store)
    elif config.AI_PROVIDER == "mock":
        return AI.create_mock_ai(session_store=session_store)
    else:
        raise ValueError(f"ספק AI לא נתמך: {config.AI_PROVIDER}")

ai_manager = create_ai_manager()

logger.info(f"מערכת הופעלה עם: AI={config.AI_PROVIDER}, Store={config.SESSION_STORE_TYPE}")


# =============================================================================
# Flow Handlers
# =============================================================================

@flow.get("")
def welcome(call):
    """שלוחה ראשית מתקדמת."""
    call.play_message([
        ("text", "ברוכים הבאים למערכת הסיוע החכמה המתקדמת!"),
        ("text", "אנחנו משתמשים בטכנולוגיות AI מתקדמות כדי לספק לכם שירות מעולה."),
    ])
    
    # תפריט עם אפשרויות מרובות
    call.play_message([
        ("text", "הקש 1 לשיחה עם הסוכן החכם"),
        ("text", "הקש 2 למידע על השירותים שלנו"), 
        ("text", "הקש 3 לשאלות נפוצות"),
        ("text", "הקש 9 להשארת הודעה"),
        ("text", "הקש 0 לסיום")
    ])
    
    call.read([("text", "אנא בחר אפשרות")], max_digits=1)
    
    choice = call.params.get("Digits", "")
    
    if choice == "1":
        call.goto("/ai_intro")
    elif choice == "2":  
        call.goto("/services_info")
    elif choice == "3":
        call.goto("/faq")
    elif choice == "9":
        call.goto("/leave_message")
    elif choice == "0":
        call.play_message([("text", "תודה ויום טוב!")])
        call.hangup()
    else:
        call.play_message([("text", "בחירה לא תקינה")])
        call.goto("")


@flow.get("services_info")
def services_info(call):
    """מידע על השירותים."""
    call.play_message([
        ("text", "אנחנו מציעים מגוון שירותים באמצעות בינה מלאכותית:"),
        ("text", "יעוץ וסיוע בנושאים שונים, מענה על שאלות, ועוד."),
        ("text", "הסוכן שלנו זמין 24 שעות ביממה ויכול לעזור במגוון רחב של נושאים.")
    ])
    
    call.read([("text", "הקש כוכבית לחזרה לתפריט")], max_digits=1)
    call.goto("")


@flow.get("faq") 
def faq(call):
    """שאלות נפוצות."""
    call.play_message([
        ("text", "שאלות נפוצות:"),
        ("text", "האם השירות בחינם? כן, השירות ניתן ללא עלות."),
        ("text", "כמה זמן לוקח לקבל מענה? בדרך כלל כמה שניות."),
        ("text", "האם השיחות מוקלטות? לא, אנחנו לא שומרים הקלטות.")
    ])
    
    call.read([("text", "הקש כוכבית לחזרה")], max_digits=1) 
    call.goto("")


@flow.get("leave_message")
def leave_message(call):
    """השארת הודעה."""
    call.play_message([
        ("text", "תוכל להשאיר הודעה של עד 30 שניות."),
        ("text", "דבר אחרי הצפצוף והודעתך תישלח לצוות שלנו.")
    ])
    
    call.record(max_seconds=30, silence_timeout=3)
    
    call.play_message([
        ("text", "תודה על ההודעה! אנחנו ניצור איתך קשר בהקדם.")
    ])
    
    call.hangup()


@flow.get("ai_intro")
def ai_intro(call):
    """מבוא לשיחת AI."""
    call_id = call.params.get("ApiCallId")
    
    if ai_manager.has_active_conversation(call_id):
        call.play_message([
            ("text", "ברוך שובך! נמשיך את השיחה מהמקום שבו עצרנו.")
        ])
    else:
        call.play_message([
            ("text", f"מעולה! אתה עומד לשוחח עם הסוכן החכם שלנו המופעל על ידי {config.AI_PROVIDER}."),
            ("text", "הסוכן יכול לעזור לך עם מגוון רחב של נושאים ושאלות."),
            ("text", "דבר בבירור ובקצב נוח. אל תמהר.")
        ])
    
    call.play_message([
        ("text", "כמה עצות חשובות:"),
        ("text", "דבר בבירור אחרי הצפצוף"),
        ("text", "המתן לתשובה מלאה לפני שתמשיך"),
        ("text", "אמור 'תפריט ראשי' כדי לחזור לתפריט"),
        ("text", "אמור 'סיום שיחה' כדי לסיים")
    ])
    
    call.goto("/ai_conversation")


@flow.get("ai_conversation")
def ai_conversation(call):
    """שיחת AI מתקדמת עם טיפול משופר בשגיאות."""
    call_id = call.params.get("ApiCallId")
    user_text = call.params.get("RecordingText")
    
    if not user_text:
        call.play_message([("text", "דבר עכשיו")])
        call.record(
            max_seconds=config.MAX_RECORDING_SECONDS,
            silence_timeout=3,
            speech_timeout=1
        )
        return
    
    # נרמול הטקסט
    user_text = user_text.strip()
    user_text_lower = user_text.lower()
    
    # פקודות מיוחדות
    if any(phrase in user_text_lower for phrase in ["תפריט ראשי", "תפריט", "חזרה"]):
        call.play_message([("text", "חוזר לתפריט הראשי")])
        call.goto("")
        return
        
    if any(phrase in user_text_lower for phrase in ["סיום שיחה", "סיום", "להתראות", "ביי"]):
        call.play_message([("text", "תודה על השיחה הנעימה! יום טוב!")])
        ai_manager.end_conversation(call_id)
        call.hangup()
        return
    
    if any(phrase in user_text_lower for phrase in ["עזרה", "הוראות", "איך"]):
        call.play_message([
            ("text", "אני כאן כדי לעזור! תוכל לשאול אותי כל שאלה."),
            ("text", "לדוגמה: שאל אותי על מזג האוויר, בקש עצות, או פשוט שוחח איתי."),
            ("text", "מה תרצה לדעת?")
        ])
        call.record(max_seconds=config.MAX_RECORDING_SECONDS, silence_timeout=3)
        return
    
    # שליחה לסוכן AI
    try:
        logger.info(f"[{call_id[:8]}] שולח: {user_text[:100]}")
        
        ai_response = ai_manager.reply(call_id, user_text)
        
        logger.info(f"[{call_id[:8]}] קיבל: {ai_response[:100]}")
        
        # השמעת תשובה עם חלוקה לחלקים אם צריך
        if len(ai_response) > 300:
            # חלוקה לחלקים קצרים יותר לקריאות טובה יותר
            parts = _split_text_to_parts(ai_response, 250)
            for part in parts:
                call.play_message([("text", part)])
        else:
            call.play_message([("text", ai_response)])
        
        # המשך השיחה
        call.play_message([("text", "יש לך עוד שאלה? דבר אחרי הצפצוף.")])
        call.record(max_seconds=config.MAX_RECORDING_SECONDS, silence_timeout=4)
        
    except Exception as e:
        logger.error(f"[{call_id[:8]}] שגיאת AI: {e}")
        
        # הודעת שגיאה ידידותית
        call.play_message([
            ("text", "מצטער, יש לי בעיה זמנית."),
            ("text", "בוא ננסה שוב, או שתוכל לחזור לתפריט הראשי.")
        ])
        
        call.read([("text", "הקש 1 לנסות שוב, או כוכבית לתפריט")], max_digits=1)
        
        choice = call.params.get("Digits", "")
        if choice == "1":
            call.goto("/ai_conversation")
        else:
            call.goto("")


def _split_text_to_parts(text: str, max_length: int = 250) -> list:
    """מחלק טקסט ארוך לחלקים קצרים יותר."""
    if len(text) <= max_length:
        return [text]
    
    parts = []
    sentences = text.split('. ')
    current_part = ""
    
    for sentence in sentences:
        if len(current_part + sentence) <= max_length:
            current_part += sentence + ". "
        else:
            if current_part:
                parts.append(current_part.strip())
                current_part = sentence + ". "
            else:
                # משפט יחיד ארוך מדי - חותכים באמצע
                parts.append(sentence[:max_length])
                current_part = sentence[max_length:] + ". "
    
    if current_part:
        parts.append(current_part.strip())
    
    return parts


# =============================================================================
# FastAPI Routes  
# =============================================================================

@app.post("/yemot")
@app.get("/yemot") 
async def yemot_handler(request: Request):
    """נקודת כניסה לבקשות ימות המשיח."""
    form_data = await request.form()
    params = dict(form_data)
    
    try:
        xml_response = flow.handle_request(params)
        handle_yemot_hangup(ai_manager, params)
        
        return Response(
            content=xml_response,
            media_type="application/xml",
            headers={"Content-Type": "text/xml; charset=utf-8"}
        )
        
    except Exception as e:
        logger.error(f"שגיאה בעיבוד ימות: {e}")
        
        error_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say>שגיאה במערכת, אנא נסה מאוחר יותר</Say>
            <Hangup/>
        </Response>'''
        
        return Response(content=error_xml, media_type="application/xml")


@app.get("/")
async def root():
    """דף בית."""
    return {
        "message": "Yemot AI Advanced Server", 
        "version": "1.0.0",
        "ai_provider": config.AI_PROVIDER,
        "session_store": config.SESSION_STORE_TYPE
    }


@app.get("/health")
async def health_check():
    """בדיקת תקינות מתקדמת."""
    try:
        session_info = ai_manager.get_session_info("health_check")
        
        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",  # יש להחליף בזמן אמיתי
            "config": {
                "ai_provider": config.AI_PROVIDER,
                "session_store": config.SESSION_STORE_TYPE,
                "flow_timeout": config.FLOW_TIMEOUT
            },
            "ai_info": session_info
        }
        
    except Exception as e:
        logger.error(f"שגיאה בבדיקת תקינות: {e}")
        raise HTTPException(status_code=500, detail=f"שגיאה: {e}")


@app.get("/admin/sessions")
async def get_sessions():
    """מידע על סשנים פעילים."""
    try:
        if hasattr(ai_manager.session_store, 'get_all_sessions'):
            sessions = ai_manager.session_store.get_all_sessions()
            return {
                "total_sessions": len(sessions),
                "sessions": sessions
            }
        else:
            return {"message": "אין אפשרות להציג סשנים עם סוג אחסון זה"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/admin/sessions")
async def clear_sessions():
    """ניקוי כל הסשנים."""
    try:
        ai_manager.clear_all_sessions()
        return {"message": "כל הסשנים נוקו"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/config")
async def get_config():
    """הצגת תצורה נוכחית.""" 
    return {
        "ai_provider": config.AI_PROVIDER,
        "session_store_type": config.SESSION_STORE_TYPE, 
        "flow_timeout": config.FLOW_TIMEOUT,
        "max_recording_seconds": config.MAX_RECORDING_SECONDS,
        "session_file_path": config.SESSION_FILE_PATH if config.SESSION_STORE_TYPE == "json" else None
    }


if __name__ == "__main__":
    import uvicorn
    
    print("מפעיל שרת FastAPI מתקדם...")
    print(f"AI Provider: {config.AI_PROVIDER}")
    print(f"Session Store: {config.SESSION_STORE_TYPE}")
    print("נקודות כניסה:")
    print("  Yemot: http://localhost:8000/yemot")  
    print("  Health: http://localhost:8000/health")
    print("  Admin: http://localhost:8000/admin/sessions")
    
    uvicorn.run(
        "fastapi_advanced:app",  # החלף בשם הקובץ
        host="0.0.0.0",
        port=8000,
        reload=True,  # להסיר בפרודקשן
        log_level="info"
    )