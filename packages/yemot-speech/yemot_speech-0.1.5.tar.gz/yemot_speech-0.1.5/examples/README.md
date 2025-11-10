# 📚 דוגמאות yemot-speech / yemot-speech Examples

תיקייה זו מכילה דוגמאות מעשיות ומפורטות לשימוש בספריית yemot-speech.
This directory contains practical and detailed examples for the yemot-speech library.

## 🗂️ קבצי דוגמאות / Example Files

### 🎤 STT (Speech-to-Text) Examples
- **`stt_basic.py`** - דוגמאות בסיסיות ל-STT עם ספקים שונים
- **`stt_advanced.py`** - דוגמאות מתקדמות למערכות ימות המשיח

### 🔊 TTS (Text-to-Speech) Examples  
- **`tts_basic.py`** - דוגמאות בסיסיות ל-TTS עם ספקים שונים

### 🏛️ Yemot HaMashiach Systems
- **`yemot_voice_system.py`** - מערכות קוליות מלאות לימות המשיח
- **`combined_workflows.py`** - שילוב STT+TTS בזרימות עבודה מלאות

### 🔗 שילוב עם Yemot:
- **`yemot_integration.py`** - שילוב מלא עם הפרויקט [Yemot](https://github.com/davidTheDeveloperY/Yemot)
- **`yemot_use_cases.py`** - מקרי שימוש נפוצים עם מערכת ימות המשיח
- **`YEMOT_INTEGRATION.md`** - מדריך מפורט לשילוב עם Yemot

### 🎯 General Demos
- **`demo.py`** - דמו בסיסי להדגמת הספריה
- **`demo_full.py`** - דמו מלא עם כל התכונות
- **`examples.py`** - דוגמאות המקוריות (מקיף אבל ארוך)

## 🚀 שימוש מהיר / Quick Usage

### דוגמאות בסיסיות:
```bash
# STT בסיסי
python stt_basic.py

# TTS בסיסי  
python tts_basic.py
```

### דוגמאות מתקדמות:
```bash
# מערכות ימות המשיח
python yemot_voice_system.py

# זרימות עבודה משולבות
python combined_workflows.py

# STT מתקדם
python stt_advanced.py

# שילוב עם Yemot (דורש: pip install yemot)
python yemot_integration.py
python yemot_use_cases.py
```

### דמואים כלליים:
```bash
# דמו בסיסי
python demo.py

# דמו מלא
python demo_full.py
```

## 📋 דרישות / Requirements

לפני הרצת הדוגמאות, וודא שהתקנת את הספרייה:
Before running examples, make sure you have installed the library:

```bash
# התקנה בסיסית / Basic installation
pip install yemot-speech

# עם ספקים ספציפיים / With specific providers
pip install yemot-speech[openai]
pip install yemot-speech[tts] 
pip install yemot-speech[all]
```

## 🔧 הגדרה לשימוש אמיתי / Setup for Real Usage

1. **הגדר API Keys:**
   ```python
   # עדכן בקוד
   api_key = 'your-real-api-key'
   ```

2. **הכן קבצי שמע:**
   ```python
   # עדכן נתיבי קבצים
   audio_file = 'path/to/your/audio.wav'
   ```

3. **בחר ספקים:**
   - OpenAI: `pip install yemot-speech[openai]`
   - Google: `pip install yemot-speech[google]`
   - Amazon: `pip install yemot-speech[amazon]`
   - Azure: `pip install yemot-speech[azure]`

## 💡 דוגמאות מהירות / Quick Examples

### STT - המרת שמע לטקסט
```python
from yemot_speech import STT
stt = STT(provider='openai', api_key='your-key')
text = stt.transcribe('audio.wav', language='he')
```

### TTS - המרת טקסט לשמע
```python
from yemot_speech import TTS
tts = TTS(provider='gtts', language='he')
tts.save_audio('שלום עליכם!', 'greeting.mp3')
```

### Combined STT+TTS Workflow
```python
from yemot_speech import STT, TTS

# Setup
stt = STT(provider='openai', api_key='key')
tts = TTS(provider='gtts', language='he')

# Process: Audio → Text → Response → Audio
user_text = stt.transcribe('user_question.wav')
response = process_request(user_text)  # Your logic
tts.save_audio(response, 'system_response.mp3')
```

## 🎯 מיוחד לעברית ולימות המשיח / Hebrew & Yemot Specialties

כל הדוגמאות כוללות:
All examples include:

- ✅ תמיכה מלאה בעברית / Full Hebrew support
- ✅ דוגמאות טקסט בעברית / Hebrew text examples  
- ✅ הגדרות מותאמות למערכות ימות המשיח / Yemot-optimized settings
- ✅ תפריטים קוליים בעברית / Hebrew voice menus
- ✅ הודעות מערכת מלאות / Complete system messages

**הערה:** הדוגמאות עובדות עם ספק דמו גם ללא API keys.
**Note:** Examples work with demo provider even without API keys.