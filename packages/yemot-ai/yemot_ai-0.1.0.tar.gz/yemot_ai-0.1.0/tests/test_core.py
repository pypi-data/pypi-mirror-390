"""
טסטים למחלקה הראשית AI.
"""

import pytest
from yemot_ai import AI, MemorySessionStore, MockAIProvider


class TestAI:
    """טסטים עבור AI."""
    
    def test_create_with_mock_provider(self):
        """יצירת AI עם ספק מדומה."""
        ai = AI(provider_type="mock")
        
        assert ai is not None
        assert isinstance(ai.provider, MockAIProvider)
        assert isinstance(ai.session_store, MemorySessionStore)
    
    def test_create_with_custom_responses(self):
        """יצירת AI עם תשובות מותאמות אישית."""
        custom_responses = ["תשובה מותאמת 1", "תשובה מותאמת 2"]
        ai = AI(provider_type="mock", responses=custom_responses)
        
        # בדיקה שהתשובות המותאמות נשמרו
        assert ai.provider.responses == custom_responses
    
    def test_create_with_custom_session_store(self):
        """יצירת AI עם SessionStore מותאם אישית."""
        custom_store = MemorySessionStore()
        ai = AI(provider_type="mock", session_store=custom_store)
        
        assert ai.session_store is custom_store
    
    def test_create_codex_ai_classmethod(self):
        """בדיקת class method ליצירת Codex AI."""
        ai = AI.create_codex_ai()
        
        assert ai is not None
        # הספק אמור להיות CodexCLIProvider (אבל לא נבדוק זאת כי זה דורש Codex)
        assert hasattr(ai.provider, 'start_session')
        assert hasattr(ai.provider, 'continue_session')
    
    def test_create_mock_ai_classmethod(self):
        """בדיקת class method ליצירת Mock AI."""
        custom_responses = ["בדיקה 1", "בדיקה 2"] 
        ai = AI.create_mock_ai(responses=custom_responses)
        
        assert isinstance(ai.provider, MockAIProvider)
        assert ai.provider.responses == custom_responses
    
    def test_reply_basic(self):
        """בדיקה בסיסית של reply."""
        ai = AI.create_mock_ai()
        call_id = "test_call_123"
        user_text = "שלום, איך אתה?"
        
        response = ai.reply(call_id, user_text)
        
        assert isinstance(response, str)
        assert len(response) > 0
        
        # בדיקה שהסשן נוצר
        assert ai.has_active_conversation(call_id)
    
    def test_reply_continuation(self):
        """בדיקת המשך שיחה."""
        ai = AI.create_mock_ai()
        call_id = "test_call"
        
        # הודעה ראשונה
        response1 = ai.reply(call_id, "הודעה ראשונה")
        
        # הודעה שנייה (המשך)
        response2 = ai.reply(call_id, "הודעה שנייה")
        
        # בדיקה שקיבלנו תשובות
        assert isinstance(response1, str)
        assert isinstance(response2, str)
        
        # הסשן אמור להיות פעיל
        assert ai.has_active_conversation(call_id)
    
    def test_reply_invalid_parameters(self):
        """בדיקת טיפול בפרמטרים לא תקינים."""
        ai = AI.create_mock_ai()
        
        # call_id ריק
        with pytest.raises(ValueError) as exc_info:
            ai.reply("", "טקסט תקין")
        assert "call_id" in str(exc_info.value)
        
        # user_text ריק
        with pytest.raises(ValueError) as exc_info:
            ai.reply("call_id_valid", "")
        assert "user_text" in str(exc_info.value)
        
        # user_text עם רק רווחים
        with pytest.raises(ValueError) as exc_info:
            ai.reply("call_id_valid", "   ")
        assert "user_text" in str(exc_info.value)
    
    def test_end_conversation(self):
        """בדיקת סיום שיחה."""
        ai = AI.create_mock_ai()
        call_id = "conversation_to_end"
        
        # התחלת שיחה
        ai.reply(call_id, "התחלת שיחה")
        assert ai.has_active_conversation(call_id)
        
        # סיום שיחה
        ai.end_conversation(call_id)
        assert not ai.has_active_conversation(call_id)
    
    def test_end_conversation_nonexistent(self):
        """בדיקה שסיום שיחה לא קיימת לא גורם לשגיאה."""
        ai = AI.create_mock_ai()
        
        # לא אמור לזרוק שגיאה
        ai.end_conversation("nonexistent_call")
        ai.end_conversation("")  # גם call_id ריק
    
    def test_has_active_conversation(self):
        """בדיקת has_active_conversation."""
        ai = AI.create_mock_ai()
        call_id = "active_test"
        
        # בהתחלה אין שיחה
        assert not ai.has_active_conversation(call_id)
        assert not ai.has_active_conversation("")  # call_id ריק
        
        # אחרי התחלת שיחה
        ai.reply(call_id, "התחלת שיחה")
        assert ai.has_active_conversation(call_id)
        
        # אחרי סיום שיחה
        ai.end_conversation(call_id)
        assert not ai.has_active_conversation(call_id)
    
    def test_get_session_info(self):
        """בדיקת get_session_info."""
        ai = AI.create_mock_ai()
        call_id = "info_test"
        
        # בדיקת מידע ללא סשן
        info = ai.get_session_info(call_id)
        assert isinstance(info, dict)
        assert info["call_id"] == call_id
        assert info["has_active_session"] == False
        assert "provider_type" in info
        assert "session_store_type" in info
        
        # יצירת סשן ובדיקת מידע
        ai.reply(call_id, "יצירת סשן")
        info_with_session = ai.get_session_info(call_id)
        assert info_with_session["has_active_session"] == True
    
    def test_clear_all_sessions(self):
        """בדיקת clear_all_sessions."""
        ai = AI.create_mock_ai()
        
        # יצירת מספר סשנים
        ai.reply("call_1", "הודעה 1")
        ai.reply("call_2", "הודעה 2")
        ai.reply("call_3", "הודעה 3")
        
        # בדיקה שהסשנים קיימים
        assert ai.has_active_conversation("call_1")
        assert ai.has_active_conversation("call_2")
        assert ai.has_active_conversation("call_3")
        
        # ניקוי כל הסשנים
        ai.clear_all_sessions()
        
        # בדיקה שכל הסשנים נוקו
        assert not ai.has_active_conversation("call_1")
        assert not ai.has_active_conversation("call_2") 
        assert not ai.has_active_conversation("call_3")
    
    def test_multiple_concurrent_conversations(self):
        """בדיקת מספר שיחות במקביל."""
        ai = AI.create_mock_ai()
        
        calls = ["call_1", "call_2", "call_3"]
        
        # התחלת מספר שיחות
        responses = {}
        for call_id in calls:
            response = ai.reply(call_id, f"הודעה מ-{call_id}")
            responses[call_id] = response
            assert ai.has_active_conversation(call_id)
        
        # המשך כל השיחות
        for call_id in calls:
            response = ai.reply(call_id, f"המשך מ-{call_id}")
            assert isinstance(response, str)
            assert ai.has_active_conversation(call_id)
        
        # סיום חלק מהשיחות
        ai.end_conversation("call_2")
        assert not ai.has_active_conversation("call_2")
        assert ai.has_active_conversation("call_1")
        assert ai.has_active_conversation("call_3")
    
    def test_unsupported_provider_type(self):
        """בדיקת טיפול בספק לא נתמך."""
        with pytest.raises(ValueError) as exc_info:
            AI(provider_type="unsupported_provider")
        
        assert "לא נתמך" in str(exc_info.value)
    
    def test_openai_without_api_key(self):
        """בדיקה שOpenAI דורש API key."""
        with pytest.raises(ValueError) as exc_info:
            AI(provider_type="openai")
        
        assert "api_key" in str(exc_info.value)


class TestAIIntegration:
    """טסטים אינטגרטיביים עבור AI."""
    
    def test_full_conversation_flow(self):
        """בדיקת זרימת שיחה מלאה."""
        ai = AI.create_mock_ai(responses=[
            "שלום! איך אפשר לעזור?",
            "מעניין, ספר לי עוד.",
            "אני מבין. יש לך עוד שאלות?",
            "תודה על השיחה!"
        ])
        
        call_id = "full_conversation"
        
        # שיחה מלאה
        r1 = ai.reply(call_id, "שלום")
        assert "שלום" in r1
        
        r2 = ai.reply(call_id, "יש לי שאלה")
        assert "מעניין" in r2
        
        r3 = ai.reply(call_id, "תוכל לעזור לי?")
        assert "מבין" in r3
        
        r4 = ai.reply(call_id, "תודה רבה")
        assert "תודה" in r4
        
        # סיום השיחה
        ai.end_conversation(call_id)
        assert not ai.has_active_conversation(call_id)
    
    def test_reconnection_after_cleanup(self):
        """בדיקת התחברות מחדש אחרי ניקוי."""
        ai = AI.create_mock_ai()
        call_id = "reconnection_test"
        
        # שיחה ראשונה
        r1 = ai.reply(call_id, "שיחה ראשונה")
        assert ai.has_active_conversation(call_id)
        
        # ניקוי
        ai.end_conversation(call_id)
        assert not ai.has_active_conversation(call_id)
        
        # שיחה חדשה עם אותו call_id
        r2 = ai.reply(call_id, "שיחה חדשה")
        assert ai.has_active_conversation(call_id)
        assert isinstance(r2, str)


# פונקציות עזר
from yemot_ai.core import create_ai_manager, handle_yemot_hangup


class TestHelperFunctions:
    """טסטים לפונקציות העזר."""
    
    def test_create_ai_manager(self):
        """בדיקת create_ai_manager."""
        ai = create_ai_manager("mock")
        assert isinstance(ai, AI)
    
    def test_handle_yemot_hangup_with_hangup(self):
        """בדיקת handle_yemot_hangup עם hangup=yes."""
        ai = AI.create_mock_ai()
        call_id = "hangup_test"
        
        # יצירת סשן
        ai.reply(call_id, "התחלת שיחה")
        assert ai.has_active_conversation(call_id)
        
        # סימולציית hangup
        params = {"hangup": "yes", "ApiCallId": call_id}
        handle_yemot_hangup(ai, params)
        
        # בדיקה שהסשן נוקה
        assert not ai.has_active_conversation(call_id)
    
    def test_handle_yemot_hangup_without_hangup(self):
        """בדיקת handle_yemot_hangup ללא hangup."""
        ai = AI.create_mock_ai()
        call_id = "no_hangup_test"
        
        # יצירת סשן
        ai.reply(call_id, "התחלת שיחה")
        assert ai.has_active_conversation(call_id)
        
        # סימולציית בקשה ללא hangup
        params = {"ApiCallId": call_id}
        handle_yemot_hangup(ai, params)
        
        # בדיקה שהסשן נשאר
        assert ai.has_active_conversation(call_id)
    
    def test_handle_yemot_hangup_missing_call_id(self):
        """בדיקת handle_yemot_hangup ללא ApiCallId."""
        ai = AI.create_mock_ai()
        
        # לא אמור לזרוק שגיאה
        params = {"hangup": "yes"}
        handle_yemot_hangup(ai, params)