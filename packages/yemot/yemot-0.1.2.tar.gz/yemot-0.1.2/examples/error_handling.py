"""תרחישי טיפול בחריגות נפוצות עבור ספריית yemot."""

from yemot import (
    AuthenticationError,
    Client,
    MFARequiredError,
    System,
    YemotError,
)


def main() -> None:
    """מדגים תגובה לשגיאות התחברות וקריאות API."""
    try:
        client = Client(username="0xxxxxxxxx", password="xxxxxx")
    except MFARequiredError:
        print("נדרש להשלים אימות דו-שלבי לפני שימוש ב-API.")
        return
    except AuthenticationError as exc:
        print("פרטי ההתחברות שגויים:", exc)
        return

    system = System(client)
    try:
        info = system.system_info()
    except YemotError as exc:
        print("נכשלה שליפת פרטי המערכת:", exc)
        return

    print("התחברות מוצלחת. שם המערכת:", info.get("name"))


if __name__ == "__main__":
    main()
