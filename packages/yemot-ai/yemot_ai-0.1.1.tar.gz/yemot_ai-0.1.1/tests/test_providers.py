"""
טסטים לספקי AI (AI Providers).
"""

import pytest
from unittest.mock import Mock, patch
from yemot_ai.session_store import MemorySessionStore
from yemot_ai.providers import MockAIProvider, AIProvider


class TestMockAIProvider:
    """טסטים עבור MockAIProvider."""
    
    def setup_method(self):
        """הכנה לכל טסט."""
        self.session_store = MemorySessionStore()
        self.provider = MockAIProvider(self.session_store)
    
    def test_start_session(self):
        """בדיקת התחלת סשן."""
        call_id = "test_call"
        user_text = "שלום"
        
        response = self.provider.start_session(call_id, user_text)
        
        # בדיקה שחזרה תשובה
        assert isinstance(response, str)
        assert len(response) > 0
        
        # בדיקה שהסשן נשמר
        assert self.provider.has_active_session(call_id)
        assert self.session_store.exists(call_id)
    
    def test_continue_session(self):
        """בדיקת המשך סשן."""
        call_id = "test_call"
        
        # התחלת סשן
        response1 = self.provider.start_session(call_id, "הודעה 1")
        
        # המשך סשן
        response2 = self.provider.continue_session(call_id, "הודעה 2")
        
        # בדיקה שקיבלנו תשובות שונות (לפי הרשימה המחזורית)
        assert isinstance(response2, str)
        assert len(response2) > 0
        # בהנחה שיש יותר מתשובה אחת ברשימה, התשובות יהיו שונות
        if len(self.provider.responses) > 1:
            assert response1 != response2
    
    def test_continue_session_without_start(self):
        """בדיקה שcontinue_session יוצר סשן חדש אם לא קיים."""
        call_id = "new_call"
        
        # קריאה ל-continue ללא start
        response = self.provider.continue_session(call_id, "הודעה")
        
        # אמור לעבוד כאילו זה start_session
        assert isinstance(response, str)
        assert self.provider.has_active_session(call_id)
    
    def test_custom_responses(self):
        """בדיקת תשובות מותאמות אישית."""
        custom_responses = ["תשובה 1", "תשובה 2", "תשובה 3"]
        provider = MockAIProvider(self.session_store, responses=custom_responses)
        
        call_id = "custom_test"
        
        # בדיקה שהתשובות מגיעות לפי הסדר
        response1 = provider.start_session(call_id, "הודעה 1")
        assert response1 == "תשובה 1"
        
        response2 = provider.continue_session(call_id, "הודעה 2") 
        assert response2 == "תשובה 2"
        
        response3 = provider.continue_session(call_id, "הודעה 3")
        assert response3 == "תשובה 3"
        
        # בדיקה שחוזר להתחלה (מחזורי)
        response4 = provider.continue_session(call_id, "הודעה 4")
        assert response4 == "תשובה 1"
    
    def test_cleanup_session(self):
        """בדיקת ניקוי סשן."""
        call_id = "cleanup_test"
        
        # יצירת סשן
        self.provider.start_session(call_id, "הודעה")
        assert self.provider.has_active_session(call_id)
        
        # ניקוי
        self.provider.cleanup_session(call_id)
        assert not self.provider.has_active_session(call_id)
    
    def test_multiple_calls(self):
        """בדיקת מספר שיחות במקביל."""
        call1 = "call_1"
        call2 = "call_2"
        
        # התחלת שתי שיחות
        response1_1 = self.provider.start_session(call1, "הודעה 1 מקול 1")
        response2_1 = self.provider.start_session(call2, "הודעה 1 מקול 2")
        
        # המשך שתי שיחות
        response1_2 = self.provider.continue_session(call1, "הודעה 2 מקול 1")
        response2_2 = self.provider.continue_session(call2, "הודעה 2 מקול 2")
        
        # בדיקה שכל שיחה מתנהלת בנפרד
        assert self.provider.has_active_session(call1)
        assert self.provider.has_active_session(call2)
        
        # התשובות אמורות להיות עצמאיות
        assert isinstance(response1_1, str)
        assert isinstance(response1_2, str)
        assert isinstance(response2_1, str)
        assert isinstance(response2_2, str)


class TestAIProviderInterface:
    """טסטים כלליים לממשק AIProvider."""
    
    def test_abstract_methods(self):
        """בדיקה שלא ניתן ליצור מופע של המחלקה האבסטרקטית."""
        session_store = MemorySessionStore()
        
        # נסיון ליצור מופע של AIProvider אמור לזרוק שגיאה
        with pytest.raises(TypeError):
            AIProvider(session_store)
    
    def test_has_active_session(self):
        """בדיקת מתודת has_active_session."""
        session_store = MemorySessionStore()
        provider = MockAIProvider(session_store)
        
        call_id = "test_session_check"
        
        # בהתחלה אין סשן
        assert not provider.has_active_session(call_id)
        
        # אחרי יצירת סשן
        provider.start_session(call_id, "הודעה")
        assert provider.has_active_session(call_id)
        
        # אחרי ניקוי
        provider.cleanup_session(call_id)
        assert not provider.has_active_session(call_id)


class TestCodexCLIProvider:
    """טסטים עבור CodexCLIProvider (מדומים)."""
    
    def setup_method(self):
        """הכנה לכל טסט."""
        self.session_store = MemorySessionStore()
        
        # ייבוא מקומי כדי למנוע שגיאות אם הקובץ לא נטען
        from yemot_ai.providers import CodexCLIProvider
        self.provider_class = CodexCLIProvider
    
    @patch('subprocess.run')
    def test_start_session_success(self, mock_subprocess):
        """בדיקת התחלת סשן מוצלחת (מדומה)."""
        # הכנת mock לתשובה של subprocess.run
        mock_result = Mock()
        mock_result.stdout = '''
{"type": "thread.started", "thread_id": "test_session_123"}
{"type": "item.completed", "item": {"type": "agent_message", "text": "Hello! How can I help you?"}}
'''
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        provider = self.provider_class(self.session_store)
        call_id = "test_call"
        user_text = "Hello"
        
        response = provider.start_session(call_id, user_text)
        
        # בדיקות
        assert response == "Hello! How can I help you?"
        assert provider.has_active_session(call_id)
        
        # בדיקה שהפקודה נקראה נכון
        mock_subprocess.assert_called_once()
        args = mock_subprocess.call_args[0][0]
        assert "codex" in args
        assert "exec" in args
        assert "--json" in args
        assert user_text in args
    
    @patch('subprocess.run')
    def test_continue_session_success(self, mock_subprocess):
        """בדיקת המשך סשן מוצלח (מדומה)."""
        # הכנת סשן קיים
        call_id = "test_call"
        session_id = "existing_session_456"
        self.session_store.set(call_id, session_id)
        
        # הכנת mock לתשובה
        mock_result = Mock()
        mock_result.stdout = "This is the AI response"
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        provider = self.provider_class(self.session_store)
        user_text = "Continue conversation"
        
        response = provider.continue_session(call_id, user_text)
        
        # בדיקות
        assert response == "This is the AI response"
        
        # בדיקה שהפקודה נקראה עם resume
        args = mock_subprocess.call_args[0][0]
        assert "codex" in args
        assert "exec" in args
        assert "resume" in args
        assert session_id in args
        assert user_text in args
    
    @patch('subprocess.run')
    def test_subprocess_error_handling(self, mock_subprocess):
        """בדיקת טיפול בשגיאות subprocess."""
        from subprocess import CalledProcessError
        
        # הכנת mock שזורק שגיאה
        mock_subprocess.side_effect = CalledProcessError(
            returncode=1, 
            cmd=["codex"], 
            stderr="Command failed"
        )
        
        provider = self.provider_class(self.session_store)
        call_id = "error_call"
        user_text = "Test message"
        
        # בדיקה שנזרקת RuntimeError
        with pytest.raises(RuntimeError) as exc_info:
            provider.start_session(call_id, user_text)
        
        assert "נכשלה" in str(exc_info.value)
    
    @patch('subprocess.run')
    def test_missing_session_id(self, mock_subprocess):
        """בדיקת טיפול במקרה שלא מתקבל session_id."""
        # הכנת mock ללא session_id
        mock_result = Mock()
        mock_result.stdout = '{"type": "unknown", "data": "no session id"}'
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        provider = self.provider_class(self.session_store)
        call_id = "no_session_call"
        user_text = "Test"
        
        # בדיקה שנזרקת RuntimeError
        with pytest.raises(RuntimeError) as exc_info:
            provider.start_session(call_id, user_text)
        
        assert "session ID" in str(exc_info.value)


# הוספת __init__.py ריק לתיקיית tests אם לא קיים
def test_imports():
    """בדיקה בסיסית שהייבואים עובדים."""
    from yemot_ai.providers import AIProvider, MockAIProvider
    from yemot_ai.session_store import SessionStore, MemorySessionStore
    
    # בדיקה שהמחלקות קיימות
    assert AIProvider is not None
    assert MockAIProvider is not None
    assert SessionStore is not None
    assert MemorySessionStore is not None