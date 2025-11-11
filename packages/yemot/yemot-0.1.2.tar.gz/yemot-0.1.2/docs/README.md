# תיעוד ספריית `yemot`

## מבוא
`yemot` היא ספריית Python המאפשרת עבודה נוחה מול שירות ה־API של ימות המשיח (Call2All). הספרייה מנתקת אתכם מהצורך לבנות ידנית בקשות HTTP, לטפל בחידוש טוקנים או להמיר ערכים, ומספקת ממשק עקבי וברור לכל התרחישים הנפוצים.

## התקנה
### התקנה באמצעות `pip`
```bash
pip install yemot
```

להתקנת גרסת פיתוח:
```bash
pip install -e .
```

### התקנה באמצעות `uv`
`uv` היא מנהלת חבילות וסביבות מהירה במיוחד הכתובה ב-Rust. כך מומלץ לפעול:

```bash
uv venv
source .venv/bin/activate        # בלינוקס וב-macOS
# ב-Windows PowerShell: .venv\Scripts\Activate.ps1

uv pip install yemot              # התקנה מ-PyPI
# התקנת גרסת פיתוח (Editable):
uv pip install -e .

uv run python examples/basic_usage.py  # הרצת דוגמה
uv run pytest                        # הרצת בדיקות
```

## מבנה הפרויקט
- `src/yemot` – מימוש הספרייה עצמה.
- `examples` – דוגמאות קוד שימושיות.
  - `basic_usage.py` – התחברות ושליפת פרטי מערכת.
  - `file_management.py` – העלאה, המרה והורדה של קבצי שמע.
  - `run_campaign.py` – ניהול תבניות וקמפיינים קוליים.
  - `error_handling.py` – תרחישים לטיפול בחריגות נפוצות.
- `tests` – בדיקות יחידה ואינטגרציה.
- `docs` – קבצי תיעוד בעברית.

## שימוש מהיר
```python
from yemot import Client, System

client = Client(username="0xxxxxxxxx", password="xxxxxx")
system = System(client)
system_info = system.system_info()
print(system_info["name"], system_info["units"])
```

הספרייה מטפלת באופן אוטומטי בחידוש טוקן, בזיהוי תקלות API ובהמרת ערכי True/False לפורמטים שהשירות מצפה לקבל.

## רכיבי הליבה
### `Client`
- אחראי על תהליך ההתחברות (`login`) והחזקת טוקן תקין.
- מבצע חידוש טוקן אוטומטי כאשר מתקבלת שגיאת אימות.
- מספק מתודות `get`, `post`, `post_file`, `download` לעבודה גנרית מול ה־API.
- זורק חריגות ייעודיות (`YemotError`, `AuthenticationError`, `MFARequiredError`) עם פרטים ברורים.

### `System`
- `system_info()` – שליפת פרטי לקוח, יחידות ותוקף הטוקן.
- `set_system_info(...)` – עדכון פרטי קשר ופרטי חשבונית.
- `get_transactions(from_id=None, limit=100, filter_=None)` – דוח תנועות יחידות לפי פילטרים.
- `transfer_units(amount, destination)` – העברת יחידות בין מערכות בתוך הארגון.
- `upload_file(...)` ו-`download_file(path)` – העלאה והורדה של קבצי IVR.

### `Campaign`
- `get_templates()` – קבלת רשימת תבניות קיימות.
- `update_template(...)` – עדכון מאפיינים כגון תיאור, מדיניות חיוג ומספר קווים פעילים.
- `create_template(description)` / `delete_template(template_id)` – מחזור חיים מלא של תבניות קמפיין.
- `update_template_entry(...)` – הוספה או עדכון של אנשי קשר לרשימת התפוצה.
- `upload_template_file(...)` ו-`download_template_file(...)` – ניהול קבצי שמע לתבנית.

## עבודה עם קבצים
```python
from pathlib import Path
from yemot import Client, System

client = Client(username="0xxxxxxxxx", password="xxxxxx")
system = System(client)

source_path = Path("/tmp/message.mp3")
system.upload_file(
    file_path=str(source_path),
    path="ivr2:1/000.wav",
    convert_audio=True,
)

binary_data = system.download_file(path="ivr2:1/000.wav")
Path("downloaded.wav").write_bytes(binary_data)
```

## ניהול קמפיין
```python
from yemot import Client, Campaign

client = Client(username="0xxxxxxxxx", password="xxxxxx")
campaign = Campaign(client)

templates = campaign.get_templates()["templates"]
if not templates:
    raise SystemExit("אין תבניות פעילות במערכת")

template_id = templates[0]["templateId"]

campaign.update_template(
    template_id,
    description="קמפיין עדכון מערכת",
    max_active_channels=50,
    vm_detect=True,
    redial_policy="FAILED",
)

campaign.update_template_entry(
    template_id,
    phone="0501234567",
    name="לקוח לדוגמה",
    more_info="קיבוץ",
)
```

## טיפול בשגיאות ואימות דו-שלבי
```python
from yemot import Client, AuthenticationError, MFARequiredError

try:
    client = Client(username="0xxxxxxxxx", password="xxxxxx")
except MFARequiredError:
    print("נדרש להשלים תהליך אימות דו-שלבי דרך ממשק הניהול")
except AuthenticationError as exc:
    print("שגיאת התחברות:", exc)
```

הספרייה מטפלת באופן אוטומטי בחידוש טוקן, בזיהוי תקלות API ובהמרת ערכי True/False לפורמטים שהשירות מצפה לקבל.

## תלויות
- `requests`

## משאבים נוספים
- [פורום המפתחים של ימות המשיח](https://f2.freeivr.co.il/topic/55/api-%D7%92%D7%99%D7%A9%D7%AA-%D7%9E%D7%A4%D7%AA%D7%97%D7%99%D7%9D-%D7%9C%D7%9E%D7%A2%D7%A8%D7%9B%D7%95%D7%AA)

## רישיון
הפרויקט מופץ ברישיון MIT (ראה `LICENSE` במידה וקיים בקוד המקור).
