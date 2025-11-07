"""
דוגמה פשוטה לשימוש ב-yemot-ai ללא תלותות חיצוניות.

דוגמה זו מראה איך להשתמש במחלקות של yemot-ai באופן עצמאי,
בלי תלות ב-yemot-flow או Flask. מתאים לבדיקות וללימוד.
"""

import sys
import os

# הוספת הנתיב לחבילה (רק לדוגמה - בפרודקשן יש להתקין את החבילה)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from yemot_ai import AI, MemorySessionStore, MockAIProvider


def demo_basic_usage():
    """דוגמה בסיסית לשימוש ב-AI."""
    print("=== דוגמה בסיסית ===")
    
    # יצירת מנהל AI מדומה (לא דורש Codex CLI)
    ai = AI.create_mock_ai()
    
    # סימולציה של שיחה
    call_id = "demo_call_123"
    
    print(f"התחלת שיחה: {call_id}")
    
    # הודעה ראשונה
    response1 = ai.reply(call_id, "שלום, אני רוצה עזרה")
    print(f"משתמש: שלום, אני רוצה עזרה")
    print(f"AI: {response1}")
    
    # הודעה שנייה
    response2 = ai.reply(call_id, "איך אתה יכול לעזור לי?")
    print(f"משתמש: איך אתה יכול לעזור לי?")
    print(f"AI: {response2}")
    
    # הודעה שלישית
    response3 = ai.reply(call_id, "תודה רבה!")
    print(f"משתמש: תודה רבה!")
    print(f"AI: {response3}")
    
    # סיום השיחה
    ai.end_conversation(call_id)
    print("השיחה הסתיימה")
    print()


def demo_multiple_conversations():
    """דוגמה למספר שיחות במקביל."""
    print("=== דוגמה למספר שיחות ===")
    
    # יצירת מנהל AI עם תשובות מותאמות אישית
    custom_responses = [
        "שלום! איך אפשר לעזור?",
        "מעניין, ספר לי עוד.",
        "אני מבין את השאלה שלך.",
        "זה באמת נושא חשוב.",
        "יש לי עוד רעיונות בנושא.",
        "האם זה עונה על השאלה?"
    ]
    
    ai = AI.create_mock_ai(responses=custom_responses)
    
    # שתי שיחות במקביל
    call1 = "call_001" 
    call2 = "call_002"
    
    print("שיחה 1:")
    r1_1 = ai.reply(call1, "שאלה ראשונה")
    print(f"  {r1_1}")
    
    print("שיחה 2:")  
    r2_1 = ai.reply(call2, "שאלה אחרת לגמרי")
    print(f"  {r2_1}")
    
    print("המשך שיחה 1:")
    r1_2 = ai.reply(call1, "המשך של השאלה הראשונה") 
    print(f"  {r1_2}")
    
    print("המשך שיחה 2:")
    r2_2 = ai.reply(call2, "המשך של השאלה השנייה")
    print(f"  {r2_2}")
    
    # בדיקת מצב סשנים
    print(f"שיחה 1 פעילה: {ai.has_active_conversation(call1)}")
    print(f"שיחה 2 פעילה: {ai.has_active_conversation(call2)}")
    
    # ניקוי
    ai.end_conversation(call1)
    ai.end_conversation(call2)
    
    print(f"אחרי ניקוי - שיחה 1 פעילה: {ai.has_active_conversation(call1)}")
    print()


def demo_session_stores():
    """דוגמה לסוגי אחסון שונים.""" 
    print("=== דוגמה לסוגי אחסון ===")
    
    # אחסון בזיכרון
    memory_store = MemorySessionStore()
    ai_memory = AI(provider_type="mock", session_store=memory_store)
    
    # אחסון ב-JSON
    from yemot_ai import JSONSessionStore
    json_store = JSONSessionStore("demo_sessions.json")
    ai_json = AI(provider_type="mock", session_store=json_store)
    
    call_id = "store_test"
    
    # בדיקה עם אחסון בזיכרון
    print("בדיקה עם אחסון בזיכרון:")
    r1 = ai_memory.reply(call_id, "בדיקה 1")
    print(f"  {r1}")
    print(f"  יש סשן: {ai_memory.has_active_conversation(call_id)}")
    
    # בדיקה עם אחסון JSON
    print("בדיקה עם אחסון JSON:")
    r2 = ai_json.reply(call_id, "בדיקה 2") 
    print(f"  {r2}")
    print(f"  יש סשן: {ai_json.has_active_conversation(call_id)}")
    
    # הצגת תוכן האחסון
    if hasattr(memory_store, 'get_all_sessions'):
        print(f"  זיכרון: {memory_store.get_all_sessions()}")
        
    if hasattr(json_store, 'get_all_sessions'):
        print(f"  JSON: {json_store.get_all_sessions()}")
    
    # ניקוי
    ai_memory.clear_all_sessions()
    ai_json.clear_all_sessions()
    
    # ניקוי קובץ הדמו
    try:
        os.remove("demo_sessions.json")
    except FileNotFoundError:
        pass
    
    print()


def demo_error_handling():
    """דוגמה לטיפול בשגיאות."""
    print("=== דוגמה לטיפול בשגיאות ===")
    
    ai = AI.create_mock_ai()
    
    # בדיקת שגיאות בפרמטרים
    try:
        ai.reply("", "טקסט תקין")
        print("שגיאה: אמור היה לזרוק שגיאה על call_id ריק")
    except ValueError as e:
        print(f"✓ תפס שגיאה כצפוי: {e}")
    
    try:
        ai.reply("call_id_valid", "")
        print("שגיאה: אמור היה לזרוק שגיאה על טקסט ריק")
    except ValueError as e:
        print(f"✓ תפס שגיאה כצפוי: {e}")
    
    # בדיקת מידע על סשן
    call_id = "error_test"
    info = ai.get_session_info(call_id)
    print(f"מידע על סשן: {info}")
    
    print()


def demo_codex_simulation():
    """
    סימולציה של שימוש ב-Codex CLI (בלי להריץ את זה בפועל).
    
    הערה: לשימוש אמיתי ב-Codex CLI יש לוודא שהוא מותקן ונגיש.
    """
    print("=== סימולציית Codex CLI ===")
    
    print("לשימוש אמיתי ב-Codex CLI:")
    print("1. התקן את Codex CLI")
    print("2. ודא שהוא נגיש ב-PATH")
    print("3. השתמש בקוד הבא:")
    
    code_example = '''
# יצירת מנהל AI עם Codex CLI
ai = AI.create_codex_ai()

# שימוש רגיל
call_id = "real_call_123" 
response = ai.reply(call_id, "שלום, איך אתה?")
print(f"תשובת Codex: {response}")
'''
    
    print(code_example)
    print("הערה: הדוגמה הזו דורשת Codex CLI פעיל.")
    print()


def main():
    """הרצת כל הדוגמאות."""
    print("🤖 דוגמאות לשימוש ב-yemot-ai")
    print("=" * 50)
    
    try:
        demo_basic_usage()
        demo_multiple_conversations()
        demo_session_stores()
        demo_error_handling()
        demo_codex_simulation()
        
        print("✅ כל הדוגמאות הרוצו בהצלחה!")
        
    except Exception as e:
        print(f"❌ שגיאה בהרצת הדוגמאות: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()