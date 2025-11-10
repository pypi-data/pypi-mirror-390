# 🔗 שילוב yemot-speech עם Yemot - Integration Guide

מדריך לשילוב ספריית yemot-speech עם הפרויקט Yemot לעיבוד קבצי שמע ממערכת ימות המשיח.

## 🎯 מה השילוב מאפשר?

### 📥 **הורדה ועיבוד קבצי שמע**
- הורדת קבצי שמע ממערכת ימות המשיח
- המרת השמע לטקסט באמצעות STT
- ניתוח תוכן ההודעות הקוליות

### 📤 **יצירה והעלאה של קבצי שמע**
- יצירת הודעות קוליות מטקסט
- העלאת קבצי שמע למערכת ימות המשיח
- אוטומציה מלאה של תהליכי השמע

### 🎪 **ניהול קמפיינים קוליים**
- יצירת הודעות קמפיין אוטומטיות
- ניתוח תגובות משתמשים
- מעקב ודיווח על ביצועי קמפיינים

## 🛠️ התקנה

### דרישות בסיס:
```bash
# התקן את שתי הספריות
pip install yemot
pip install yemot-speech[openai]  # או ספק אחר

# לכל הספקים
pip install yemot-speech[all]
```

### הגדרת API Keys:
```python
# לOpenAI Whisper & TTS
OPENAI_API_KEY = "your-openai-key"

# לGoogle Cloud Speech & TTS  
GOOGLE_CREDENTIALS = "path/to/google-credentials.json"

# למערכת ימות המשיח
YEMOT_USERNAME = "0500000000"  # מספר המערכת
YEMOT_PASSWORD = "123456"      # סיסמת המערכת
```

## 🚀 דוגמאות שימוש

### דוגמה בסיסית - שילוב הספריות:
```python
from yemot import Client, System, Campaign
from yemot_speech import STT, TTS

# חיבור לימות המשיח
yemot_client = Client(username='0500000000', password='123456')
system = System(yemot_client)

# אתחול שירותי דיבור
stt = STT(provider='openai', api_key='your-key')
tts = TTS(provider='gtts', language='he')

print("✅ Both systems connected and ready!")
```

### הורדה והמרה של קובץ שמע:
```python
# הורדת קובץ שמע ממערכת ימות
audio_path = "ivr2:recordings/call_001.wav"
download_result = system.download_file(audio_path)

# שמירה מקומית והמרה לטקסט
with open("temp_audio.wav", "wb") as f:
    f.write(download_result['data'])  # תלוי בפורמט התגובה

# המרת השמע לטקסט
transcription = stt.transcribe("temp_audio.wav", language='he')
print(f"תמלול: {transcription}")
```

### יצירת הודעת קמפיין והעלאתה:
```python
# יצירת הודעת קמפיין
campaign_message = """
שלום וברכה! זוהי הזמנה לשיעור מיוחד מחר בשעה 20:00.
לאישור השתתפות לחצו 1, לביטול לחצו 2.
תודה רבה!
"""

# המרה לשמע
tts.save_audio(campaign_message, "campaign_message.wav")

# העלאה למערכת ימות
campaign = Campaign(yemot_client)
upload_result = campaign.upload_template_file(
    file="campaign_message.wav",
    name="12345",  # מזהה התבנית
    type="VOICE",
    convertAudio="1"
)

print(f"✅ הודעה הועלתה בהצלחה: {upload_result}")
```

## 📁 קבצי דוגמאות

### 🔗 `yemot_integration.py`
מחלקה מלאה לשילוב עם כל הפונקציונליות:
- הורדת קבצי שמע והמרה לטקסט
- יצירת קבצי שמע והעלאתם
- עיבוד קמפיינים קוליים
- ניתוח תגובות ומשוב

```bash
python examples/yemot_integration.py
```

### 🎯 `yemot_use_cases.py` 
מקרי שימוש נפוצים:
- תמלול הודעות קוליות
- יצירת הודעות אוטומטיות 
- עיבוד תפריטים אינטראקטיביים
- ניתוח משוב קמפיינים

```bash
python examples/yemot_use_cases.py
```

## 🎛️ מקרי שימוש נפוצים

### 1️⃣ **מערכת הודעות קוליות**
```python
# המרת הודעות קוליות לטקסט לצורך ניהול ומעקב
voicemail_files = system.get_voicemail_list()
for file in voicemail_files:
    text = stt.transcribe(file)
    # שמירת התמלול במאגר הנתונים
    save_transcription(file, text)
```

### 2️⃣ **הודעות אוטומטיות**
```python
# יצירת הודעות זמנים יומיות
daily_zmanim = get_daily_zmanim()  # קבלת זמנים מAPI
message = f"זמני התפילות היום: שחרית {daily_zmanim['shacharit']}, מנחה {daily_zmanim['mincha']}"

tts.save_audio(message, "daily_zmanim.wav")
system.upload_file("daily_zmanim.wav", "ivr2:daily/zmanim.wav")
```

### 3️⃣ **תפריטים חכמים**
```python
# עיבוד תשובות חופשיות בתפריט
user_response = "אני רוצה לדעת מתי השיעור השבועי"
intent = analyze_intent(user_response)  # זיהוי כוונה

if intent == "shiur_times":
    response = "השיעור השבועי מתקיים בימי ראשון בשעה 20:30"
    tts.save_audio(response, "shiur_response.wav")
```

### 4️⃣ **ניתוח קמפיינים**
```python
# ניתוח תגובות לקמפיין
campaign_responses = get_campaign_responses(template_id=12345)
analysis_results = []

for response_audio in campaign_responses:
    text = stt.transcribe(response_audio)
    sentiment = analyze_sentiment(text)  # חיובי/שלילי/נייטרל
    analysis_results.append({
        'text': text,
        'sentiment': sentiment
    })

# יצירת דוח מסכם
create_campaign_report(analysis_results)
```

## 🏛️ אופטימיזציה למערכות ימות המשיח

### הגדרות מומלצות לשיחות טלפון:
```python
# STT מותאם לאיכות טלפון
stt = STT(
    provider='google',
    credentials_path='credentials.json'
)

# המרה עם הגדרות טלפון
text = stt.transcribe(
    audio_file,
    encoding='MULAW',      # קידוד נפוץ בטלפוניה
    sample_rate=8000,      # תדירות טלפון סטנדרטית
    language_code='he-IL'  # עברית ישראלית
)
```

### TTS מותאם לעברית:
```python
# הגדרות אופטימליות לעברית
tts = TTS(
    provider='gtts',
    language='he',
    slow=False  # מהירות טבעית
)

# או עם Azure לאיכות גבוהה
tts = TTS(
    provider='azure',
    subscription_key='your-key',
    region='eastus',
    voice_name='he-IL-AvigailNeural'  # קול עברי איכותי
)
```

## ⚡ אוטומציה מתקדמת

### זרימת עבודה מלאה:
```python
class YemotAutomation:
    def __init__(self):
        self.yemot = Client(username="...", password="...")
        self.stt = STT(provider='openai', api_key="...")
        self.tts = TTS(provider='gtts', language='he')
    
    def process_daily_workflow(self):
        # 1. עיבוד הודעות חדשות
        new_messages = self.download_new_messages()
        transcriptions = [self.stt.transcribe(msg) for msg in new_messages]
        
        # 2. יצירת דוח יומי
        daily_report = self.create_daily_report(transcriptions)
        
        # 3. יצירת הודעות תגובה
        response_audio = self.tts.save_audio(daily_report, "daily_report.wav")
        
        # 4. העלאת ההודעות למערכת
        self.upload_to_yemot(response_audio, "ivr2:reports/daily.wav")
```

## 🔧 פתרון בעיות נפוצות

### בעיות חיבור לימות המשיח:
```python
try:
    client = Client(username=username, password=password)
    print("✅ Connected to Yemot successfully")
except Exception as e:
    print(f"❌ Yemot connection failed: {e}")
    # בדוק username, password, חיבור אינטרנט
```

### בעיות איכות שמע:
```python
# שיפור איכות STT
stt = STT(
    provider='openai',
    api_key=key,
    model='whisper-1'  # מודל מתקדם יותר
)

# בדיקת איכות קובץ שמע
audio_info = analyze_audio_quality(audio_file)
if audio_info['quality'] < 0.5:
    print("⚠️ Audio quality low - consider noise reduction")
```

### אופטימיזציה לביצועים:
```python
# עיבוד במקביל
from concurrent.futures import ThreadPoolExecutor

def process_multiple_files(audio_files):
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(stt.transcribe, audio_files))
    return results
```

## 📞 תמיכה ועזרה

- **תיעוד Yemot**: https://github.com/davidTheDeveloperY/Yemot
- **תיעוד yemot-speech**: ראה README.md הראשי  
- **דוגמאות נוספות**: בתיקיית examples/
- **בעיות**: פתח issue ב-GitHub

---

**💡 טיפ**: התחל עם הדוגמאות הבסיסיות ובנה בהדרגה את המערכת שלך. השילוב מאפשר אוטומציה מלאה של תהליכי השמע במערכת ימות המשיח!