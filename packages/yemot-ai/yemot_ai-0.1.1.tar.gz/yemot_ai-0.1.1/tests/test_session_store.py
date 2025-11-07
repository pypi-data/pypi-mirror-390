"""
טסטים בסיסיים למחלקות SessionStore.
"""

import pytest
import tempfile
import os
from yemot_ai.session_store import MemorySessionStore, JSONSessionStore


class TestMemorySessionStore:
    """טסטים עבור MemorySessionStore."""
    
    def setup_method(self):
        """הכנה לכל טסט."""
        self.store = MemorySessionStore()
    
    def test_get_set_basic(self):
        """בדיקה בסיסית של get ו-set."""
        call_id = "test_call_123"
        session_id = "test_session_456"
        
        # בהתחלה אין סשן
        assert self.store.get(call_id) is None
        assert not self.store.exists(call_id)
        
        # שמירה
        self.store.set(call_id, session_id)
        
        # אחזור
        assert self.store.get(call_id) == session_id
        assert self.store.exists(call_id)
    
    def test_clear(self):
        """בדיקת ניקוי סשן."""
        call_id = "test_call"
        session_id = "test_session"
        
        # שמירה ובדיקה
        self.store.set(call_id, session_id)
        assert self.store.exists(call_id)
        
        # ניקוי ובדיקה
        self.store.clear(call_id)
        assert not self.store.exists(call_id)
        assert self.store.get(call_id) is None
    
    def test_clear_nonexistent(self):
        """בדיקה שניקוי סשן לא קיים לא גורם לשגיאה."""
        self.store.clear("nonexistent_call")
        # לא אמור לזרוק שגיאה
    
    def test_multiple_sessions(self):
        """בדיקת ניהול מספר סשנים."""
        sessions = {
            "call_1": "session_1",
            "call_2": "session_2", 
            "call_3": "session_3"
        }
        
        # שמירת כמה סשנים
        for call_id, session_id in sessions.items():
            self.store.set(call_id, session_id)
        
        # בדיקה שכולם שמורים
        for call_id, session_id in sessions.items():
            assert self.store.get(call_id) == session_id
            assert self.store.exists(call_id)
        
        # בדיקת get_all_sessions
        all_sessions = self.store.get_all_sessions()
        assert len(all_sessions) == 3
        assert all_sessions == sessions
    
    def test_clear_all(self):
        """בדיקת ניקוי כל הסשנים."""
        # שמירת כמה סשנים
        self.store.set("call_1", "session_1")
        self.store.set("call_2", "session_2")
        
        assert len(self.store.get_all_sessions()) == 2
        
        # ניקוי הכל
        self.store.clear_all()
        
        assert len(self.store.get_all_sessions()) == 0
        assert not self.store.exists("call_1")
        assert not self.store.exists("call_2")
    
    def test_update_session(self):
        """בדיקה שעדכון סשן קיים עובד."""
        call_id = "test_call"
        
        self.store.set(call_id, "session_1")
        assert self.store.get(call_id) == "session_1"
        
        self.store.set(call_id, "session_2")
        assert self.store.get(call_id) == "session_2"


class TestJSONSessionStore:
    """טסטים עבור JSONSessionStore."""
    
    def setup_method(self):
        """הכנה לכל טסט."""
        # יצירת קובץ זמני
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.file_path = self.temp_file.name
        
        self.store = JSONSessionStore(self.file_path)
    
    def teardown_method(self):
        """ניקוי אחרי כל טסט."""
        # מחיקת הקובץ הזמני
        try:
            os.unlink(self.file_path)
        except FileNotFoundError:
            pass
    
    def test_get_set_basic(self):
        """בדיקה בסיסית של get ו-set."""
        call_id = "test_call_123"
        session_id = "test_session_456"
        
        # בהתחלה אין סשן
        assert self.store.get(call_id) is None
        assert not self.store.exists(call_id)
        
        # שמירה
        self.store.set(call_id, session_id)
        
        # אחזור
        assert self.store.get(call_id) == session_id
        assert self.store.exists(call_id)
        
        # בדיקה שהקובץ נוצר
        assert os.path.exists(self.file_path)
    
    def test_persistence(self):
        """בדיקה שהנתונים נשמרים בקובץ."""
        call_id = "persistent_call"
        session_id = "persistent_session"
        
        # שמירה בstore הראשון
        self.store.set(call_id, session_id)
        
        # יצירת store חדש עם אותו קובץ
        new_store = JSONSessionStore(self.file_path)
        
        # בדיקה שהנתונים נשמרו
        assert new_store.get(call_id) == session_id
        assert new_store.exists(call_id)
    
    def test_clear(self):
        """בדיקת ניקוי סשן."""
        call_id = "test_call"
        session_id = "test_session"
        
        # שמירה ובדיקה
        self.store.set(call_id, session_id)
        assert self.store.exists(call_id)
        
        # ניקוי ובדיקה
        self.store.clear(call_id)
        assert not self.store.exists(call_id)
        assert self.store.get(call_id) is None
    
    def test_multiple_sessions(self):
        """בדיקת ניהול מספר סשנים."""
        sessions = {
            "call_1": "session_1",
            "call_2": "session_2",
            "call_3": "session_3"
        }
        
        # שמירת כמה סשנים
        for call_id, session_id in sessions.items():
            self.store.set(call_id, session_id)
        
        # בדיקה שכולם שמורים
        for call_id, session_id in sessions.items():
            assert self.store.get(call_id) == session_id
        
        # בדיקת get_all_sessions
        all_sessions = self.store.get_all_sessions()
        assert len(all_sessions) == 3
        assert all_sessions == sessions
    
    def test_clear_all(self):
        """בדיקת ניקוי כל הסשנים.""" 
        # שמירת כמה סשנים
        self.store.set("call_1", "session_1")
        self.store.set("call_2", "session_2")
        
        assert len(self.store.get_all_sessions()) == 2
        
        # ניקוי הכל
        self.store.clear_all()
        
        assert len(self.store.get_all_sessions()) == 0
        assert not self.store.exists("call_1")
        assert not self.store.exists("call_2")
    
    def test_corrupted_file_handling(self):
        """בדיקת טיפול בקובץ פגום."""
        # כתיבת תוכן לא תקין לקובץ
        with open(self.file_path, 'w') as f:
            f.write("invalid json content")
        
        # יצירת store חדש - אמור להתמודד עם הקובץ הפגום
        store = JSONSessionStore(self.file_path)
        
        # אמור להחזיר None עבור מפתח לא קיים (כאילו הקובץ ריק)
        assert store.get("any_key") is None
        
        # אמור לאפשר שמירה חדשה
        store.set("new_call", "new_session")
        assert store.get("new_call") == "new_session"
    
    def test_nonexistent_file(self):
        """בדיקת עבודה כשהקובץ לא קיים."""
        # מחיקת הקובץ
        os.unlink(self.file_path)
        
        # יצירת store חדש
        store = JSONSessionStore(self.file_path)
        
        # אמור לעבוד כרגיל
        assert store.get("any_key") is None
        
        store.set("test_call", "test_session")
        assert store.get("test_call") == "test_session"


class TestSessionStoreInterface:
    """טסטים כלליים לממשק SessionStore."""
    
    @pytest.mark.parametrize("store_class", [MemorySessionStore, JSONSessionStore])
    def test_interface_consistency(self, store_class):
        """בדיקה שכל המימושים מקיימים את אותו ממשק."""
        if store_class == JSONSessionStore:
            # יצירת קובץ זמני
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
            temp_file.close()
            store = store_class(temp_file.name)
            temp_path = temp_file.name
        else:
            store = store_class()
            temp_path = None
        
        try:
            # בדיקה שכל המתודות קיימות
            assert hasattr(store, 'get')
            assert hasattr(store, 'set')
            assert hasattr(store, 'clear')
            assert hasattr(store, 'clear_all')
            assert hasattr(store, 'exists')
            
            # בדיקה שהמתודות עובדות
            call_id = "interface_test"
            session_id = "interface_session"
            
            store.set(call_id, session_id)
            assert store.get(call_id) == session_id
            assert store.exists(call_id)
            
            store.clear(call_id)
            assert not store.exists(call_id)
            
            store.clear_all()  # לא אמור לזרוק שגיאה
        
        finally:
            # ניקוי קובץ זמני אם נוצר
            if temp_path:
                try:
                    os.unlink(temp_path)
                except FileNotFoundError:
                    pass