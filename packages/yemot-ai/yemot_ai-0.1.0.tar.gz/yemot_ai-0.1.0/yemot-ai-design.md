
# תכנון חבילת `yemot-ai` לחיבור סוכני AI למערכות ימות המשיח

> **מטרה:** לבנות חבילת Python (`yemot-ai`) שמשמשת כ־wrapper מעל `yemot-flow` ומחברת שיחות טלפון של **ימות המשיח** אל סוכן AI.  
> בגישה הנוכחית מתמקדים ב־**CLI של Codex** (גרסה 0.55.0), תוך שימוש ב־`codex exec` ליצירת שיחות חדשות וב־`codex exec resume <session-id> "<prompt>"` להמשך שיחות — **מבלי** לשלוח היסטוריית הקשר ידנית.

---

## תוכן העניינים
1. [סקירה מהירה](#סקירה-מהירה)
2. [הבנת `yemot-flow` (זרימת IVR ו־Handlers)](#הבנת-yemot-flow-זרימת-ivr-והandlers)
3. [Codex CLI — ניהול סשנים: `exec` ו־`resume` (פתרון תקיעת subprocess)](#codex-cli--ניהול-סשנים-exec-וresume-פתרון-תקיעת-subprocess)
4. [מיפוי בין ApiCallId ↔ Codex Session ID](#מיפוי-בין-apicallid--codex-session-id)
5. [ארכיטקטורת חבילה מומלצת](#ארכיטקטורת-חבילה-מומלצת)
6. [דוגמת קוד מלאה: Flask + `yemot-flow` + Codex CLI](#דוגמת-קוד-מלאה-flask--yemot-flow--codex-cli)
7. [ניהול תקלות, ניקוי, וטיפים לפרודקשן](#ניהול-תקלות-ניקוי-וטיפים-לפרודקשן)
8. [נספח: API מוצע למפתחים (`YemotAI`)](#נספח-api-מוצע-למפתחים-yemotai)

---

## סקירה מהירה

- **לא שולחים context ידנית.** מנצלים את יכולת ה־**resume** של Codex: כל שיחה (Session) נשמרת בצד ה־CLI, ואנו מצרפים רק את ההודעה החדשה בכל פנייה.  
- **שיחה חדשה:** `codex exec --json "<prompt>"` → שולפים `session_id` מה־JSONL ומחזירים את תשובת הסוכן.  
- **המשך שיחה:** `codex exec resume <session-id> "<prompt>"` → שולח את ההודעה החדשה ומחזיר תשובה *בלי* מצב אינטראקטיבי.  
- **מיפוי סשנים:** שומרים `ApiCallId -> session_id` במבנה פשוט: מילון בזיכרון או JSON מקומי (בשלב ראשון).  
- **עטיפה מעל `yemot-flow`:** מספקים פונקציה/מחלקה שמסתירה את כל ניהול ה־session, כדי שה־Handler יתמקד בלוגיקת השיחה.

---

## הבנת `yemot-flow` (זרימת IVR ו־Handlers)

`yemot-flow` מנהלת **שיחה טלפונית מבוססת אירועים** בצורה שנראית כמו קוד רציף. מגדירים **Handlers** (ל״שלוחות״) בעזרת דקורטורים, ומשתמשים במתודות כמו `play_message`, `read`, `record`, `goto` כדי להנחות את השיחה.

דוגמה מינימלית (רעיון כללי; קוד ייעודי בהמשך):
```python
from yemot_flow import Flow

flow = Flow(timeout=30000, print_log=True)

@flow.get("")  # שלוחה ראשית
def welcome(call):
    call.play_message([("text", "שלום! לחץ 1 לשיחה עם סוכן ה-AI, או 2 לסיום.")])
    call.read([("text", "הקש בחירה")], max_digits=1)
    if call.params.get("Digits") == "1":
        call.goto("/ai_agent")
    else:
        call.hangup()
```

הקריאות לפונקציות ״חיצוניות״ (כמו מודל AI) יכולות להתבצע בגוף ה־handler; אם הן איטיות, אפשר לשקול ריצה אסינכרונית, אך לשלב ראשון גישה סינכרונית עובדת מצוין.

---

## Codex CLI — ניהול סשנים: `exec` ו־`resume` (פתרון תקיעת subprocess)

### יצירת שיחה חדשה וקבלת **Session ID**
הדרך הבטוחה לחלץ `session_id` היא להריץ ב־JSONL:
```bash
codex exec --json "שלום, זו ההודעה הראשונה שלי."
```
- הפלט הוא **שורות JSON** (אירועים). באירוע ההתחלתי אפשר לחלץ מזהה Thread/Session.
- בנוסף יופיע אירוע עם הודעת הסוכן שמכיל את הטקסט של התשובה.

דוגמת ניתוח ב־Python:
```python
import subprocess, json

def codex_start_session(user_text):
    result = subprocess.run(
        ["codex", "exec", "--json", user_text],
        capture_output=True, text=True, check=True
    )
    session_id, answer = None, None
    for line in result.stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        # דוגמאות לשמות שדות/אירועים - יתכן שינויי גרסה קלים
        if event.get("type") in {"thread.started", "session.started"}:
            session_id = event.get("thread_id") or event.get("session_id")
        if (
            event.get("type") in {"item.completed", "message.completed"}
            and (event.get("item") or {}).get("type") in {"agent_message", "assistant_message"}
        ):
            answer = (event.get("item") or {}).get("text") or event.get("message", {}).get("text")
    return session_id, answer
```

### המשך שיחה קיימת — ללא מצב אינטראקטיבי
**בעיה נפוצה:** `codex resume <session-id>` לבדו נכנס למצב אינטראקטיבי ומיתקע ב־subprocess.  
**פתרון:** להשתמש ב־`codex exec resume <session-id> "<prompt>"` — הפקודה שולחת הודעה, מריצה ומחזירה תשובה **מיד**, בלי TUI.

```python
def codex_resume(session_id, user_text):
    result = subprocess.run(
        ["codex", "exec", "resume", session_id, user_text],
        capture_output=True, text=True, check=True
    )
    return result.stdout.strip()
```

> טיפ: אם תרצה פלט מובנה גם ב־resume, אפשר גרסה עם `--json` ולנתח כמו ב־start. לרוב לא צריך — הפלט ה״רגיל״ הוא תשובת הסוכן.

---

## מיפוי בין `ApiCallId` ↔ Codex Session ID

בשלב ראשון נשתמש ב־**מילון בזיכרון** או ב־**קובץ JSON מקומי**:

- מפתח (key): `ApiCallId` של ימות.
- ערך (value): `session_id` של Codex.
- מנקים את המיפוי בסיום השיחה (למשל אם `hangup=yes`).

דוגמה פשוטה (בזיכרון):
```python
SESSIONS = {}  # { ApiCallId: session_id }

def get_session_for_call(call_id):
    return SESSIONS.get(call_id)

def set_session_for_call(call_id, session_id):
    SESSIONS[call_id] = session_id

def clear_session_for_call(call_id):
    SESSIONS.pop(call_id, None)
```

גרסת קובץ JSON (פשוטה; ללא נעילה בין־תהליכית):
```python
import json, os, threading
STORE_PATH = "yemot_ai_sessions.json"
_LOCK = threading.Lock()

def _load_store():
    if not os.path.exists(STORE_PATH):
        return {}
    with open(STORE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_store(data):
    with open(STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_session_for_call(call_id):
    with _LOCK:
        data = _load_store()
        return data.get(call_id)

def set_session_for_call(call_id, session_id):
    with _LOCK:
        data = _load_store()
        data[call_id] = session_id
        _save_store(data)

def clear_session_for_call(call_id):
    with _LOCK:
        data = _load_store()
        if call_id in data:
            del data[call_id]
            _save_store(data)
```

---

## ארכיטקטורת חבילה מומלצת

**שכבות:**
1. **SessionStore** — אחסון למיפוי `ApiCallId`→`session_id` (Memory/JSON/Redis בעתיד).
2. **AI Providers** — מימושים ברי החלפה:
   - `CodexCLIProvider` (CLI-only) — `start_session()`, `continue_session()`.
   - `OpenAIProvider`/`AnthropicProvider` (API) — אופציונלי לעתיד.
3. **YemotAI / AIManager** — מעטפת אחידה שמסתירה את ניהול הסשנים והמימוש (CLI/API).
4. **Integration עם `yemot-flow`** — פונקציה/מחלקה לשימוש קל בתוך Handlers.

דוגמת ממשק (רעיוני):
```python
class AIProvider:
    def start_session(self, call_id: str, user_text: str) -> str:
        raise NotImplementedError
    def continue_session(self, call_id: str, user_text: str) -> str:
        raise NotImplementedError

class CodexCLIProvider(AIProvider):
    def __init__(self, store):
        self.store = store
    def start_session(self, call_id, user_text):
        session_id, answer = codex_start_session(user_text)
        if not session_id:
            raise RuntimeError("No session_id returned from codex exec --json")
        self.store.set(call_id, session_id)
        return answer
    def continue_session(self, call_id, user_text):
        session_id = self.store.get(call_id)
        if not session_id:
            return self.start_session(call_id, user_text)
        return codex_resume(session_id, user_text)

class YemotAI:
    def __init__(self, provider: AIProvider):
        self.provider = provider
    def reply(self, call_id: str, user_text: str) -> str:
        # אם יש סשן קיים → continue; אחרת → start
        if self.provider.store.get(call_id):
            return self.provider.continue_session(call_id, user_text)
        return self.provider.start_session(call_id, user_text)
```

---

## דוגמת קוד מלאה: Flask + `yemot-flow` + Codex CLI

> **הערה:** הדוגמה מניחה שיש לך דרך להפיק טקסט מהמשתמש (ASR). בדמו זה נניח שהטקסט מגיע בפרמטר `RecordingText`. בפועל תשלב/י מנגנון STT משלך, או מעבר ל־DTMF אם הרעיון הוא תפריטים.

```python
from flask import Flask, request, Response
from yemot_flow import Flow
import subprocess, json

app = Flask(__name__)
flow = Flow(timeout=45000, print_log=True)

# --- Store בסיסי בזיכרון ---
SESSIONS = {}  # ApiCallId -> codex session_id

def codex_start_session(user_text):
    result = subprocess.run(
        ["codex", "exec", "--json", user_text],
        capture_output=True, text=True, check=True
    )
    session_id, answer = None, ""
    for line in result.stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") in {"thread.started", "session.started"}:
            session_id = event.get("thread_id") or event.get("session_id")
        if (
            event.get("type") in {"item.completed", "message.completed"}
            and (event.get("item") or {}).get("type") in {"agent_message", "assistant_message"}
        ):
            answer = (event.get("item") or {}).get("text") or event.get("message", {}).get("text", "")
    return session_id, answer

def codex_resume(session_id, user_text):
    result = subprocess.run(
        ["codex", "exec", "resume", session_id, user_text],
        capture_output=True, text=True, check=True
    )
    return result.stdout.strip()

@flow.get("ai_agent")
def ai_agent_handler(call):
    call_id = call.params.get("ApiCallId")
    user_text = call.params.get("RecordingText")  # דוגמא: טקסט מזוהה
    if not user_text:
        call.play_message([("text", "אתה מדבר עם סוכן ה-AI. אמור את בקשתך אחרי הצפצוף.")])
        # בדמו: מבקש הקלטה כדי שבקריאה הבאה יופיע RecordingText
        call.record(max_seconds=7, silence_timeout=2, speech_timeout=2)
        return

    if call_id in SESSIONS:
        answer = codex_resume(SESSIONS[call_id], user_text)
    else:
        session_id, answer = codex_start_session(user_text)
        if session_id:
            SESSIONS[call_id] = session_id

    call.play_message([("text", answer or "לא הצלחתי להבין, נסה שוב בבקשה.")])
    # לולאה: בקש הודעה נוספת מאותו מתקשר כדי להמשיך את ה־resume
    call.record(max_seconds=7, silence_timeout=2, speech_timeout=2)

@app.route("/yemot", methods=["POST"])
def yemot_entrypoint():
    params = request.values.to_dict()
    xml = flow.handle_request(params)
    # ניקוי סשן בסיום שיחה
    if params.get("hangup") == "yes":
        call_id = params.get("ApiCallId")
        if call_id:
            SESSIONS.pop(call_id, None)
    return Response(xml, mimetype="text/xml")
```

**מה קורה כאן?**
- קריאה ראשונה בלי `RecordingText` → מנגישים הודעת פתיחה ומבקשים הקלטה (`record`).  
- בקריאה העוקבת יש `RecordingText`:  
  - אם יש סשן קיים ל־`ApiCallId` → `codex exec resume <session> "<text>"`.  
  - אחרת → `codex exec --json "<text>"` ומחלצים `session_id` + תשובה.  
- את התשובה משמיעים למתקשר ושוב מבקשים הקלטה — כך נוצר **דיאלוג רציף** מבלי להעביר היסטוריה.  
- בסיום (`hangup=yes`) מוחקים את המיפוי.

---

## ניהול תקלות, ניקוי, וטיפים לפרודקשן

- **בדיקת קודים:** תמיד בדוק/י `returncode` של `subprocess.run` (`check=True` כבר זורק חריגה). עטפו ב־`try/except` להשמעת הודעת fallback.  
- **זמני המתנה:** הגדל/י `timeout` ב־`Flow` (למשל 45 שניות) כדי לאפשר חביון רשת סביר ל־Codex.  
- **ניקוי סשנים:** הסר/י `ApiCallId` מהמפה ב־`hangup`. שקול/י גם Thread שמוחק סשנים ״ישנים״.  
- **תלות ב־CLI:** ודא/י שה־CLI זמין ב־PATH של התהליך שרץ תחת ה־WSGI/ASGI.  
- **הרחבה עתידית:** ספק אחסון משותף (Redis) אם יש מספר workers. הוסף/י Provider ל־OpenAI/Anthropic API עם ממשק זהה.  
- **אבטחה:** אם מאפשרים ל־Codex להריץ כלים, ודא/י sandbox מתאים. עבור עוזר שיחה בלבד, העבר/י הנחיה (system prompt) שתמנע ביצועי־יתר.  

---

## נספח: API מוצע למפתחים (`YemotAI`)

```python
class SessionStore:
    def __init__(self):
        self._map = {}
    def get(self, call_id):
        return self._map.get(call_id)
    def set(self, call_id, session_id):
        self._map[call_id] = session_id
    def clear(self, call_id):
        self._map.pop(call_id, None)

class CodexCLIProvider:
    def __init__(self, store: SessionStore):
        self.store = store
    def start_session(self, call_id, text):
        s, ans = codex_start_session(text)
        if not s:
            raise RuntimeError("codex did not return session_id")
        self.store.set(call_id, s)
        return ans
    def continue_session(self, call_id, text):
        sid = self.store.get(call_id)
        if not sid:
            return self.start_session(call_id, text)
        return codex_resume(sid, text)

class YemotAI:
    def __init__(self, provider):
        self.provider = provider
    def reply(self, call_id, text):
        if self.provider.store.get(call_id):
            return self.provider.continue_session(call_id, text)
        return self.provider.start_session(call_id, text)
```

שימוש ב־Handler:
```python
store = SessionStore()
provider = CodexCLIProvider(store)
ai = YemotAI(provider)

@flow.get("assistant")
def assistant(call):
    call_id = call.params.get("ApiCallId")
    text = call.params.get("RecordingText") or ""
    if not text:
        call.play_message([("text", "דבר אחרי הצפצוף")])
        call.record(max_seconds=7, silence_timeout=2, speech_timeout=2)
        return
    answer = ai.reply(call_id, text)
    call.play_message([("text", answer)])
    call.record(max_seconds=7, silence_timeout=2, speech_timeout=2)
```

---

**זהו.** עם המבנה הזה, `yemot-ai` מספק חוויית פיתוח נקייה: המפתח מקבל פונקציה אחת (`reply`) שמנהלת סשנים אוטומטית ומנצלת את `codex exec resume` לצבירת הקשר — בלי להעביר היסטוריה ידנית.
