# Changelog - yemot-ai

כל השינויים החשובים בפרויקט yemot-ai יתועדו בקובץ זה.

הפורמט מבוסס על [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
והפרויקט עוקב אחרי [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### תכונות מתוכננות
- תמיכה ב-Anthropic Claude API
- תמיכה ב-Azure OpenAI Service
- Cache מתקדם לתשובות AI
- Webhooks לעדכונים על סטטוס סשנים
- תמיכה ב-Streaming responses
- תמיכה ב-Voice cloning
- Dashboard ניהול גרפי

### שיפורים מתוכננים
- ביצועים משופרים עבור אחסון Redis
- תמיכה ב-async/await מלאה
- מדדי ביצועים (metrics) ו-monitoring
- תמיכה ב-load balancing בין מספר AI providers

## [0.1.0] - 2024-01-15

### ✅ נוסף (Added)
- **מחלקות ליבה**:
  - `YemotAI` - המחלקה הראשית לניהול AI
  - `SessionStore` - ממשק אחסון סשנים
  - `AIProvider` - ממשק לספקי AI

- **ספקי AI**:
  - `CodexCLIProvider` - תמיכה ב-Codex CLI של OpenAI
  - `OpenAIProvider` - תמיכה ב-OpenAI ChatCompletion API
  - `MockAIProvider` - ספק מדומה לבדיקות ופיתוח

- **סוגי אחסון**:
  - `MemorySessionStore` - אחסון בזיכרון
  - `JSONSessionStore` - אחסון בקובץ JSON מקומי
  - `RedisSessionStore` - אחסון ב-Redis (אופציונלי)

- **תכונות עיקריות**:
  - ניהול סשנים אוטומטי עם שמירת הקשר השיחה
  - תמיכה במספר שיחות במקביל
  - טיפול חכם בשגיאות עם הודעות ידידותיות
  - ממשק פשוט עם מתודת `reply()` יחידה
  - ניקוי סשנים אוטומטי בסיום שיחות

- **אינטגרציה**:
  - פונקציית `handle_yemot_hangup()` לניקוי אוטומטי
  - תמיכה מלאה ב-`yemot-flow`
  - דוגמאות עבודה עם Flask ו-FastAPI

- **דוגמאות ותיעוד**:
  - `examples/flask_basic.py` - דוגמה בסיסית עם Flask
  - `examples/fastapi_advanced.py` - דוגמה מתקדמת עם FastAPI
  - `examples/simple_demo.py` - הדגמה ללא תלויות חיצוניות
  - README מפורט עם דוגמאות שימוש
  - תיעוד API מקיף

- **טסטים**:
  - טסטים מקיפים עבור כל המודולים
  - כיסוי טסטים > 90%
  - טסטי אינטגרציה לזרימות עבודה מלאות
  - Mock objects לבדיקת פונקציונליות ללא תלויות

### 🛠️ תשתית (Infrastructure)
- הגדרת פרויקט עם `setup.py` ו-`requirements.txt`
- מבנה תיקיות מאורגן עם הפרדה בין core, providers, ו-tests
- CI/CD מוכן עם GitHub Actions (בתיכנון)
- תמיכה ב-Python 3.8+

### 📖 תיעוד (Documentation)
- README מפורט בעברית עם דוגמאות שימוש
- תיעוד API מלא לכל המחלקות והמתודות
- דוגמאות קוד מעשיות ובדוקות
- הוראות התקנה ופריסה לפרודקשן
- מדריך תרומה לפרויקט

### 🔧 הגדרות (Configuration)
- תמיכה במשתני סביבה לכל ההגדרות
- תצורות מוכנות מראש לסביבות שונות
- גמישות בבחירת ספק AI וסוג אחסון
- הגדרות timeout ו-retry מתאימות

## הערות פיתוח

### ארכיטקטורה
הפרויקט בנוי על עקרונות של:
- **Separation of Concerns** - הפרדה ברורה בין שכבות
- **Dependency Injection** - ניתן להחליף כל רכיב בקלות
- **Interface-based Design** - כל רכיב מממש ממשק ברור
- **Testability** - כל רכיב ניתן לבדיקה עצמאית

### החלטות עיצוב
- **פשטות מעל גמישות יתרה** - ממשק פשוט למשתמש הסופי
- **אמינות מעל ביצועים** - הקפדה על טיפול בשגיאות
- **תאימות לאחור** - שמירה על יציבות API בין גירסאות
- **תמיכה בקהילה הישראלית** - תיעוד ושמות בעברית

### מגבלות ידועות בגירסה זו
- תמיכה בספק אחד בלבד בכל מופע YemotAI
- אחסון Redis דורש התקנה נוספת
- Codex CLI דורש הגדרה חיצונית
- לא תמיכה ב-streaming responses

### תודות
- קהילת המפתחים של ימות המשיח
- תורמי פרויקט yemot-flow
- צוות OpenAI על הכלים המעולים

---

## פורמט החלוקה

### [גירסה] - תאריך
- **Added** - תכונות חדשות
- **Changed** - שינויים בתכונות קיימות  
- **Deprecated** - תכונות שיוסרו בעתיד
- **Removed** - תכונות שהוסרו
- **Fixed** - תיקוני באגים
- **Security** - תיקוני אבטחה