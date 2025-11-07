# Contributing to yemot-ai

🙏 תודה על העניין בתרומה לפרויקט yemot-ai! 

אנו מזמינים תרומות מכל סוג: תיקוני באגים, תכונות חדשות, שיפור תיעוד, הצעות לשיפור, ועוד.

## 🚀 איך לתרום

### 1. הכנת הסביבה

```bash
# Fork הפרויקט ב-GitHub ושכפל את ה-fork שלך
git clone https://github.com/YOUR_USERNAME/yemot-ai.git
cd yemot-ai

# יצירת סביבה וירטואלית
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# התקנת הפרויקט במצב פיתוח
pip install -e ".[dev]"

# הרצת טסטים לוודא שהכל עובד
pytest
```

### 2. יצירת Branch חדש

```bash
git checkout -b feature/your-feature-name
# או
git checkout -b fix/your-bug-fix
```

### 3. ביצוע השינויים

- עקוב אחרי הקונבנציות הקיימות
- כתוב טסטים לקוד חדש
- עדכן תיעוד אם נדרש
- ודא שהטסטים עוברים

### 4. שליחת Pull Request

```bash
git add .
git commit -m "תיאור השינוי בעברית או אנגלית"
git push origin feature/your-feature-name
```

פתח Pull Request ב-GitHub עם תיאור מפורט של השינויים.

## 📋 סוגי תרומות מבוקשות

### 🐛 תיקוני באגים
- תיאור הבעיה וצעדי שחזור
- תיקון הקוד
- טסט שמוודא שהבאג תוקן

### ✨ תכונות חדשות
- הסבר מה התכונה עושה ולמה היא נחוצה
- מימוש התכונה עם טסטים
- עדכון התיעוד

### 📚 שיפור תיעוד
- תיקון שגיאות בתיעוד
- הוספת דוגמאות
- שיפור ההסברים

### 🧪 ספקי AI חדשים
- ספק AI חדש (Anthropic, Azure OpenAI, וכו')
- מימוש הממשק `AIProvider`
- טסטים מקיפים

### 🔧 שיפורי תשתית
- שיפור ביצועים
- קוד נקי יותר
- אבטחה משופרת

## 📏 קונבנציות קוד

### סגנון Python
```bash
# פרמוט קוד
black yemot_ai/ tests/ examples/

# בדיקת איכות קוד  
flake8 yemot_ai/ tests/

# בדיקת type hints (אופציונלי)
mypy yemot_ai/
```

### שמות ומשתנים
- שמות מחלקות: `PascalCase`
- שמות פונקציות ומשתנים: `snake_case`
- קבועים: `UPPER_CASE`
- שמות קבצים: `snake_case.py`

### תיעוד
```python
def example_function(param1: str, param2: int) -> str:
    """
    תיאור הפונקציה בעברית או אנגלית.
    
    Args:
        param1: תיאור הפרמטר הראשון
        param2: תיאור הפרמטר השני
        
    Returns:
        תיאור מה שהפונקציה מחזירה
        
    Raises:
        ValueError: מתי זורקת שגיאה זו
    """
    pass
```

### טסטים
```python
class TestMyFeature:
    """טסטים לתכונה שלי."""
    
    def setup_method(self):
        """הכנה לכל טסט."""
        pass
    
    def test_basic_functionality(self):
        """בדיקה בסיסית של הפונקציונליות."""
        assert True  # הטסט שלך כאן
    
    def test_edge_cases(self):
        """בדיקת מקרי קצה.""" 
        pass
    
    def test_error_handling(self):
        """בדיקת טיפול בשגיאות."""
        pass
```

## 🧪 הרצת טסטים

```bash
# כל הטסטים
pytest

# עם כיסוי
pytest --cov=yemot_ai --cov-report=html

# טסט ספציפי
pytest tests/test_core.py::TestYemotAI::test_reply_basic

# רק טסטים שנכשלו
pytest --lf

# רק טסטים חדשים
pytest --tb=short
```

## 📝 דרישות לPull Request

### ✅ רשימת בדיקה
- [ ] הקוד עוקב אחרי הקונבנציות
- [ ] כל הטסטים עוברים (`pytest`)
- [ ] הקוד מפורמט נכון (`black`)
- [ ] אין שגיאות lint (`flake8`)
- [ ] טסטים חדשים לתכונות חדשות
- [ ] תיעוד מעודכן אם נדרש
- [ ] CHANGELOG.md מעודכן לשינויים חשובים

### 💬 תיאור Pull Request
כלול בתיאור:
- מה השינוי עושה
- למה השינוי נחוץ
- איך בדקת שזה עובד
- האם זה שובר תאימות לאחור

## 🏗️ הוספת ספק AI חדש

### 1. צור מחלקה חדשה

```python
# yemot_ai/providers.py
class MyAIProvider(AIProvider):
    """ספק AI חדש שלי."""
    
    def __init__(self, session_store: SessionStore, **kwargs):
        super().__init__(session_store)
        # ההגדרות שלך
    
    def start_session(self, call_id: str, user_text: str) -> str:
        """התחלת סשן חדש."""
        # המימוש שלך
        pass
    
    def continue_session(self, call_id: str, user_text: str) -> str:
        """המשך סשן קיים."""
        # המימוש שלך
        pass
```

### 2. הוסף לבחירה ב-YemotAI

```python
# yemot_ai/core.py
def _create_provider(self, provider_type: str, **kwargs) -> AIProvider:
    # ... קוד קיים
    elif provider_type == "my_ai":
        return MyAIProvider(
            session_store=self.session_store,
            **kwargs
        )
```

### 3. כתוב טסטים

```python
# tests/test_my_provider.py
class TestMyAIProvider:
    def test_start_session(self):
        # בדיקת התחלת סשן
        pass
    
    def test_continue_session(self):
        # בדיקת המשך סשן
        pass
```

### 4. עדכן תיעוד

עדכן את ה-README ו-CHANGELOG עם הספק החדש.

## 🎯 איך לדווח על באגים

### 🔍 לפני הדיווח
1. בדוק שהבאג לא דווח כבר ב-[Issues](https://github.com/your-username/yemot-ai/issues)
2. נסה לשחזר בסביבה נקייה
3. בדוק עם הגירסה העדכנית ביותר

### 📋 תבנית דיווח
```markdown
## תיאור הבעיה
תיאור קצר וברור של מה שלא עובד.

## צעדי שחזור
1. עשה כך
2. אז עשה כך
3. ראה שגיאה

## התנהגות צפויה
מה אתה מצפה שיקרה.

## התנהגות בפועל
מה קרה בפועל.

## סביבה
- OS: [למשל Windows 10]
- Python: [למשל 3.9.0]
- yemot-ai: [למשל 0.1.0]
- yemot-flow: [למשל 1.2.3]

## קוד לשחזור
```python
# קוד מינימלי שמשחזר את הבעיה
```

## הודעת שגיאה מלאה
```
הדבק כאן את הודעת השגיאה המלאה
```
```

## 💡 הצעות לתכונות

### 📋 תבנית הצעה
```markdown
## תיאור התכונה
תיאור ברור של מה אתה רוצה שיקרה.

## בעיה שזה פותר
הסבר איזו בעיה התכונה פותרת.

## פתרונות אלטרנטיביים
תיאור של פתרונות אחרים ששקלת.

## דוגמת שימוש
```python
# איך אתה מדמיין שהתכונה תעבוד
ai.new_feature(param1, param2)
```
```

## 🌟 רעיונות לתכונות עתידיות

- **ספקי AI נוספים**: Anthropic Claude, Cohere, Hugging Face
- **אחסון מתקדם**: PostgreSQL, MongoDB, DynamoDB
- **תכונות מתקדמות**: Streaming, Voice cloning, Context window management
- **ניטור**: Metrics, Logging, Health checks מובנים
- **אבטחה**: Rate limiting, Authentication, Input sanitization
- **UI**: Dashboard לניהול סשנים וניטור

## 📞 יצירת קשר

- 🐛 באגים: [GitHub Issues](https://github.com/your-username/yemot-ai/issues)
- 💡 רעיונות: [GitHub Discussions](https://github.com/your-username/yemot-ai/discussions)
- ❓ שאלות: [GitHub Discussions](https://github.com/your-username/yemot-ai/discussions)
- 📧 פרטי: heskisharf@gmail.com

## ⚡ טיפים למפתחים

### איך לעבוד בקבצים מקומיים
```bash
# עריכה והרצה מקומית ללא התקנה
export PYTHONPATH="${PWD}:${PYTHONPATH}"
python examples/simple_demo.py
```

### דיבוג עם VSCode
צור `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        }
    ]
}
```

### Git hooks מועילים
```bash
# pre-commit hook שמריץ black ו-flake8
# .git/hooks/pre-commit
#!/bin/sh
black --check yemot_ai/ tests/ examples/
flake8 yemot_ai/ tests/
pytest tests/ -x
```

---

**תודה על התרומה לקהילה! 🚀**