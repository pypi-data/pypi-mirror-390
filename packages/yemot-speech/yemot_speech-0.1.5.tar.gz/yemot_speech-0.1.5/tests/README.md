# טסטים yemot-speech / yemot-speech Tests

תיקייה זו מכילה טסטים עבור ספריית yemot-speech.
This directory contains tests for the yemot-speech library.

## קבצים / Files

### 🧪 `test_basic.py`
טסטים בסיסיים לפונקציונליות ליבה
Basic tests for core functionality

```bash
cd tests
python test_basic.py
```

### ✅ `check_install.py`
בדיקת התקנה ותלויות
Installation and dependencies check

```bash
cd tests
python check_install.py
```

## הרצת טסטים / Running Tests

### בדיקה בסיסית / Basic Check
```bash
# מהשורש של הפרוייקט / From project root
python tests/test_basic.py
python tests/check_install.py
```

### עם pytest (אם מותקן)
```bash
# התקן pytest / Install pytest
pip install pytest

# הרץ טסטים / Run tests
pytest tests/
```

### בדיקה מלאה / Complete Check
```bash
# בדוק התקנה / Check installation
python tests/check_install.py

# הרץ טסטים בסיסיים / Run basic tests
python tests/test_basic.py

# הרץ דמו מלא / Run full demo
python examples/demo_full.py
```

## מה הטסטים בודקים / What Tests Check

### ✅ טסטים בסיסיים:
- ייבוא מודולים / Module imports
- רישום ספקים / Provider registration  
- פונקציונליות STT / STT functionality
- פונקציונליות TTS / TTS functionality
- ניהול קבצים / File handling

### ✅ בדיקת התקנה:
- תלויות זמינות / Available dependencies
- ספקים זמינים / Available providers
- המלצות להתקנה / Installation recommendations
- טסט פונקציונליות מלא / Full functionality test

## דרישות / Requirements

הטסטים עובדים ללא תלויות חיצוניות נוספות.
Tests work without additional external dependencies.

עבור טסטים מתקדמים עם ספקים אמיתיים:
For advanced tests with real providers:

```bash
pip install yemot-speech[all]  # כל הספקים / All providers
pip install pytest           # טסטים מתקדמים / Advanced testing
```

## הוספת טסטים / Adding Tests

לפיתוח נוסף:
For further development:

1. צור קובץ טסט חדש ב-`tests/`
2. ייבא `yemot_speech` עם path fixing
3. השתמש במחלקות בסיס לטסטי דמו
4. בדוק גם STT וגם TTS
5. הוסף תיעוד עברי ואנגלי

```python
# Template for new test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from yemot_speech import STT, TTS
# Your test code here...
```