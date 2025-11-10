# Yemot Speech

ספריית Python להמרת שמע לטקסט (STT) וטקסט לשמע (TTS) עבור מערכות ימות המשיח.
Python library for Speech-to-Text (STT) and Text-to-Speech (TTS) for Yemot HaMashiach systems.

## ✨ תכונות עיקריות / Features

- 🎯 **ממשק אחיד** - API פשוט ואחיד לכל ספקי ה-STT וה-TTS
- 🌐 **תמיכה בספקים מרובים** - OpenAI, Google Cloud, Amazon, Azure, מודלים מקומיים
- 🎤 **Speech-to-Text** - המרת שמע לטקסט עם ספקים שונים
- 🔊 **Text-to-Speech** - המרת טקסט לשמע עם קולות איכותיים
- 🇮🇱 **אופטימיזציה לעברית** - הגדרות מותאמות לעברית ומערכות ימות המשיח
- 📞 **תמיכה בשיחות טלפון** - הגדרות מותאמות לקבצי שמע מטלפוניה
- 🔧 **גמישות מלאה** - תמיכה בקבצים, bytes, וזרמי נתונים
- 🏃‍♂️ **קל לשימוש** - התחל עם שורה אחת של קוד

## 🚀 התקנה / Installation

### התקנה בסיסית / Basic Installation
```bash
pip install yemot-speech
# or
uv add yemot-speech
```

### התקנה עם ספקים ספציפיים / Installation with Specific Providers

```bash
# התקנה עם OpenAI Whisper
pip install yemot-speech[openai]
uv add yemot-speech[openai]

# התקנה עם Google Cloud Speech
pip install yemot-speech[google]
uv add yemot-speech[google]

# התקנה עם Amazon Transcribe
pip install yemot-speech[amazon]
uv add yemot-speech[amazon]

# עבור מודלים מקומיים
pip install yemot-speech[local]
uv add yemot-speech[local]

# עבור Text-to-Speech (המרת טקסט לשמע)
pip install yemot-speech[tts]
uv add yemot-speech[tts]

# עבור TTS ספציפי
pip install yemot-speech[tts-openai]    # OpenAI TTS
pip install yemot-speech[tts-amazon]    # Amazon Polly
pip install yemot-speech[tts-azure]     # Azure Cognitive Services

# התקנה עם כל הספקים
pip install yemot-speech[all]
uv add yemot-speech[all]

# התקנה עם מספר ספקים ספציפיים
pip install yemot-speech[openai,google]
uv add yemot-speech[openai,google]
```

### התקנת תלויות בנפרד / Manual Dependencies Installation

```bash
# עבור OpenAI Whisper
pip install openai>=1.0.0

# עבור Google Cloud Speech
pip install google-cloud-speech>=2.0.0

# עבור Amazon Transcribe
pip install boto3>=1.26.0

# עבור מודלים מקומיים
pip install openai-whisper>=20230314 SpeechRecognition>=3.10.0
```

## 📖 שימוש בסיסי / Basic Usage

### 🎯 שימוש מהיר / Quick Usage

#### STT - המרת שמע לטקסט / Speech-to-Text
```python
from yemot_speech import transcribe

# המרה מהירה עם OpenAI
text = transcribe(
    'audio.wav',
    provider='openai',
    api_key='your-api-key',
    language='he'
)
print(text)
```

#### TTS - המרת טקסט לשמע / Text-to-Speech
```python
from yemot_speech import synthesize, speak

# יצירת קובץ שמע
audio_file = synthesize(
    'שלום עליכם! ברוכים הבאים למערכת ימות המשיח',
    provider='gtts',
    output_file='greeting.mp3'
)

# השמעה ישירה
speak('שלום וברכה לכולם', provider='gtts')
```

### 🔧 שימוש מתקדם / Advanced Usage

```python
from yemot_speech import STT

# יצירת אובייקט STT
stt = STT(
    provider='openai',
    api_key='your-openai-api-key'
)

# המרת קובץ שמע
text = stt.transcribe('path/to/audio.wav', language='he')
print(f"Transcribed: {text}")

# המרת bytes
with open('audio.wav', 'rb') as f:
    audio_bytes = f.read()
text = stt.transcribe_bytes(audio_bytes, language='he')
```

## 🛠️ ספקי STT זמינים / Available STT Providers

### 1. OpenAI Whisper (מומלץ / Recommended)

```python
stt = STT(
    provider='openai',
    api_key='your-api-key',
    model='whisper-1'
)

# עם הגדרות מתקדמות
text = stt.transcribe(
    'audio.wav',
    language='he',
    temperature=0.2,
    prompt='שיחה טלפונית בעברית'
)
```

### 2. Google Cloud Speech

```python
stt = STT(
    provider='google',
    credentials_path='path/to/credentials.json',
    language_code='he-IL'
)

# עבור שיחות טלפון
text = stt.transcribe(
    'call.wav',
    encoding='MULAW',
    sample_rate=8000,
    model='phone_call'
)
```

### 3. Amazon Transcribe

```python
stt = STT(
    provider='amazon',
    aws_access_key_id='your-key-id',
    aws_secret_access_key='your-secret-key',
    region_name='us-east-1',
    bucket_name='your-s3-bucket'
)

text = stt.transcribe(
    'audio.wav',
    language_code='he-IL',
    enable_speaker_identification=True
)
```

### 4. מודל מקומי / Local Models

```python
# שימוש ב-Whisper מקומי
stt = STT(
    provider='local',
    engine='whisper',
    model_name='medium'
)

text = stt.transcribe('audio.wav', language='hebrew')
```

## 📞 שימוש עם מערכות ימות המשיח / Yemot HaMashiach Integration

### המרת שיחות טלפון / Phone Call Transcription

```python
from yemot_speech import STT

# הגדרה אופטימלית לשיחות ימות המשיח
stt = STT(
    provider='google',
    credentials_path='credentials.json',
    language_code='he-IL'
)

# המרת קובץ שיחה (בדרך כלל WAV או μ-law)
def transcribe_yemot_call(audio_file_path):
    text = stt.transcribe(
        audio_file_path,
        encoding='MULAW',  # או 'LINEAR16' לפי סוג הקובץ
        sample_rate=8000,   # תדירות נפוצה בטלפוניה
        language_code='he-IL',
        enable_automatic_punctuation=True,
        model='phone_call'
    )
    return text

# דוגמה
result = transcribe_yemot_call('yemot_recording.wav')
print(f"תוכן השיחה: {result}")
```

### עיבוד מקובלי קבצים / Batch Processing

```python
import os
from yemot_speech import STT

def process_yemot_recordings(directory_path):
    stt = STT(provider='openai', api_key='your-key')
    
    results = {}
    for filename in os.listdir(directory_path):
        if filename.endswith(('.wav', '.mp3', '.m4a')):
            file_path = os.path.join(directory_path, filename)
            try:
                text = stt.transcribe(file_path, language='he')
                results[filename] = text
                print(f"✅ {filename}: {text[:50]}...")
            except Exception as e:
                print(f"❌ {filename}: Error - {e}")
    
    return results

# עיבוד כל הקבצים בתיקייה
recordings = process_yemot_recordings('/path/to/yemot/recordings')
```

## 🔍 מידע על ספקים / Provider Information

```python
from yemot_speech import STT

# בדיקת ספקים זמינים
available_providers = STT.get_available_providers()
print(f"Available providers: {available_providers}")

# מידע על ספק נוכחי
stt = STT(provider='openai', api_key='test')
info = stt.get_provider_info()
print(f"Provider info: {info}")
```

## ⚙️ הגדרות מתקדמות / Advanced Configuration

### הגדרה מותאמת לעברית / Hebrew-Optimized Settings

```python
# עבור OpenAI - הגדרות אופטימליות לעברית
stt_openai = STT(
    provider='openai',
    api_key='your-key'
)

hebrew_text = stt_openai.transcribe(
    'hebrew_audio.wav',
    language='he',
    temperature=0.1,  # יציבות גבוהה יותר
    prompt='תוכן בעברית, כולל מושגים דתיים ותורניים'
)

# עבור Google Cloud - הגדרות משופרות
stt_google = STT(
    provider='google',
    credentials_path='credentials.json'
)

hebrew_text = stt_google.transcribe(
    'hebrew_audio.wav',
    language_code='he-IL',
    enable_automatic_punctuation=True,
    model='latest_long',  # מודל משופר
    use_enhanced=True     # דיוק גבוה יותר
)
```

### טיפול בשגיאות / Error Handling

```python
from yemot_speech import STT

def safe_transcribe(audio_file, providers=['openai', 'google', 'local']):
    """ניסיון עם מספר ספקים עד להצלחה"""
    
    for provider in providers:
        try:
            if provider == 'openai':
                stt = STT(provider='openai', api_key='your-key')
            elif provider == 'google':
                stt = STT(provider='google', credentials_path='creds.json')
            elif provider == 'local':
                stt = STT(provider='local', engine='whisper', model_name='base')
            
            return stt.transcribe(audio_file, language='he')
            
        except Exception as e:
            print(f"Provider {provider} failed: {e}")
            continue
    
    raise Exception("All providers failed")

# שימוש
try:
    result = safe_transcribe('audio.wav')
    print(f"Success: {result}")
except Exception as e:
    print(f"All transcription attempts failed: {e}")
```

## 📁 מבנה הפרוייקט / Project Structure

```
yemot-speech/
├── src/yemot_speech/
│   ├── __init__.py          # API ראשי
│   ├── stt.py              # מחלקה מרכזת STT
│   ├── tts.py              # מחלקה מרכזת TTS
│   ├── base.py             # מחלקות בסיס
│   └── providors/          # ספקי STT ו-TTS
│       ├── openai.py       # OpenAI Whisper (STT)
│       ├── openai_tts.py   # OpenAI TTS
│       ├── google.py       # Google Cloud Speech (STT)
│       ├── gtts.py         # Google TTS
│       ├── amazon.py       # Amazon Transcribe (STT)
│       ├── amazon_tts.py   # Amazon Polly (TTS)
│       ├── azure_tts.py    # Azure Cognitive Services (TTS)
│       └── local.py        # מודלים מקומיים
├── demo_full.py           # דמו מלא עם STT ו-TTS
├── examples.py            # דוגמאות מפורטות
├── check_install.py       # בדיקת התקנה
├── test_basic.py          # טסטים בסיסיים
├── pyproject.toml        # הגדרות פרוייקט
└── README.md             # תיעוד זה
```

## 🎯 סיכום מהיר / Quick Summary

### STT - Speech to Text
```python
from yemot_speech import STT
stt = STT(provider='openai', api_key='key')
text = stt.transcribe('audio.wav', language='he')
```

### TTS - Text to Speech  
```python
from yemot_speech import TTS
tts = TTS(provider='gtts', language='he')
audio = tts.synthesize('שלום עליכם!')
tts.save_audio('שלום עליכם!', 'greeting.mp3')
```

### פונקציות מהירות / Quick Functions
```python
from yemot_speech import transcribe, synthesize, speak

# STT
text = transcribe('audio.wav', provider='openai', api_key='key')

# TTS
audio = synthesize('שלום וברכה', provider='gtts', output_file='greeting.mp3')
speak('שלום לכולם', provider='gtts')  # השמעה ישירה
```

## 🤝 תרומה לפרוייקט / Contributing

### התקנה לפיתוח / Development Installation
```bash
# Clone the repository
git clone https://github.com/your-username/yemot-speech
cd yemot-speech

# Install for development
pip install -e .[dev,all]
# or with uv
uv add -e .[dev,all]

# Run tests
python test_basic.py

# Check installation
python check_install.py
```

### בנייה ופרסום / Building and Publishing
```bash
# Make the build script executable
chmod +x build_and_publish.sh

# Build the package
./build_and_publish.sh

# Or manually:
python -m build
python -m twine upload dist/*
```

### דוגמאות נוספות / More Examples
```bash
# Run the demo
python demo.py

# Check what providers are available
python -c "from yemot_speech import STT; print(STT.get_available_providers())"
```

נשמח לתרומות! אנא פתח Issue או Pull Request.

## 📄 רישיון / License

MIT License

## 🆘 תמיכה / Support

לשאלות ותמיכה:
- פתח Issue ב-GitHub
- שלח מייל למפתחים

---

### 💡 טיפים להתקנה / Installation Tips

#### עבור משתמשי uv (מהיר יותר) / For uv users (faster)
```bash
# התקנה מהירה עם uv
uv add yemot-speech[openai]
uv add yemot-speech[google,local]  # מספר ספקים
uv add yemot-speech[all]           # כל הספקים
```

#### עבור פרוייקטים קיימים / For existing projects
```bash
# הוסף לפרוייקט קיים
pip install yemot-speech[openai] --upgrade
uv add yemot-speech[openai]

# בדוק שהתקנה עבדה
python -c "from yemot_speech import STT; print('✅ Installation successful!')"
```

#### בעיות התקנה נפוצות / Common Installation Issues
```bash
# אם יש בעיות עם Google Cloud
pip install google-cloud-speech --upgrade

# אם יש בעיות עם Whisper מקומי
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install openai-whisper

# עבור Apple Silicon (M1/M2)
pip install yemot-speech[local] --no-deps
pip install openai-whisper torch
```

## 📦 התקנה מהירה ושימוש / Quick Start

### 1. התקן עם הספק המועדף / Install with your preferred provider

```bash
# לשימוש עם OpenAI (מומלץ)
pip install yemot-speech[openai]

# לשימוש עם Google Cloud
pip install yemot-speech[google] 

# לשימוש עם מודל מקומי (ללא API keys)
pip install yemot-speech[local]
```

### 2. השתמש בקוד / Use in your code

```python
from yemot_speech import STT

# עם OpenAI
stt = STT(provider='openai', api_key='your-api-key')
text = stt.transcribe('audio.wav', language='he')

# עם Google Cloud  
stt = STT(provider='google', credentials_path='creds.json')
text = stt.transcribe('audio.wav', language_code='he-IL')

# עבור מודל מקומי (ללא API)
stt = STT(provider='local', engine='whisper', model_name='base')
text = stt.transcribe('audio.wav', language='hebrew')
```

## 🔊 ספקי TTS זמינים / Available TTS Providers

### 1. Google TTS (gTTS) - מומלץ / Recommended

```python
from yemot_speech import TTS

tts = TTS(provider='gtts', language='he')

# יצירת שמע
audio_bytes = tts.synthesize('שלום עליכם!')

# שמירה לקובץ
tts.save_audio('שלום עליכם!', 'greeting.mp3')

# השמעה ישירה (דורש pygame)
tts.play_audio('שלום עליכם!')
```

### 2. OpenAI TTS

```python
tts = TTS(
    provider='openai',
    api_key='your-api-key',
    voice='nova'  # עובד טוב עם עברית
)

# יצירת שמע באיכות גבוהה
audio_bytes = tts.synthesize(
    'שלום וברכה לכולם',
    voice='nova',
    speed=1.0
)
```

### 3. Azure Cognitive Services TTS

```python
tts = TTS(
    provider='azure',
    subscription_key='your-azure-key',
    region='eastus'
)

# עם קול עברי
audio_bytes = tts.synthesize(
    'ברוכים הבאים',
    voice_name='he-IL-AvigailNeural'
)

# עם SSML למרכות מתקדמות
tts.synthesize_ssml('''
<speak version="1.0" xml:lang="he-IL">
    <voice name="he-IL-AvigailNeural">
        <prosody rate="slow">שלום וברכה</prosody>
    </voice>
</speak>
''', 'greeting.wav')
```

### 4. Amazon Polly TTS

```python
tts = TTS(
    provider='amazon',
    aws_access_key_id='your-key-id',
    aws_secret_access_key='your-secret-key'
)

# עם קול עברי (אם זמין)
audio_bytes = tts.synthesize(
    'שלום עליכם',
    voice_id='Ayelet',  # קול עברי
    language_code='he-IL'
)
```

### 3. עבור פיתוח וקוד בדיקה / For development and testing

```bash
# התקן עם כל הספקים
pip install yemot-speech[all]
```

## 📚 דוגמאות שימוש / Usage Examples

הפרויקט כולל דוגמאות מפורטות ומאורגנות בתיקיית `examples/`:

### 🎯 דוגמאות בסיסיות:
- **`stt_basic.py`** - דוגמאות STT בסיסיות עם ספקים שונים
- **`tts_basic.py`** - דוגמאות TTS בסיסיות עם ספקים שונים
- **`demo.py`** - דמו מהיר לספריה
- **`demo_full.py`** - דמו מלא עם כל התכונות

### 🏛️ מיוחד לימות המשיח:
- **`yemot_voice_system.py`** - מערכות קוליות מלאות (תפריטים, הודעות, שגיאות)
- **`stt_advanced.py`** - עיבוד שיחות טלפון ותפריטים אינטראקטיביים

### 🔄 זרימות עבודה:
- **`combined_workflows.py`** - שילוב STT+TTS בזרימות מלאות

### 🔗 שילוב עם Yemot:
- **`yemot_integration.py`** - שילוב מלא עם הפרויקט [Yemot](https://github.com/davidTheDeveloperY/Yemot)
- **`yemot_use_cases.py`** - מקרי שימוש נפוצים עם מערכת ימות המשיח
- **`YEMOT_INTEGRATION.md`** - מדריך מפורט לשילוב עם Yemot

### הרצת הדוגמאות:
```bash
# דוגמאות בסיסיות
python examples/stt_basic.py
python examples/tts_basic.py

# מערכות ימות המשיח
python examples/yemot_voice_system.py

# שילוב עם Yemot (דורש: pip install yemot)
python examples/yemot_integration.py
python examples/yemot_use_cases.py

# דמואים מלאים
python examples/demo_full.py
```

**הערה:** הדוגמאות עובדות גם ללא API keys (במצב דמו) להדגמה.

---

**Made with ❤️ for the Yemot HaMashiach community**
