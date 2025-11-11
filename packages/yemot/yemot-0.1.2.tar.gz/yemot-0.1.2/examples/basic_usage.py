"""דוגמת שימוש בסיסית בלקוח yemot."""

from yemot import Client, System, Campaign


def main() -> None:
    """תסריט הדגמה קצר להפעלה ידנית או כנקודת פתיחה לקוד שלכם."""

    # החליפו את המשתמש והסיסמה בפרטי המערכת שלכם.
    client = Client(username="0xxxxxxxxx", password="xxxxxx")

    # שליפת פרטי מערכת כלליים.
    system = System(client)
    system_info = system.system_info()
    print("פרטי מערכת:", system_info)

    # טעינת נתוני קמפיינים קיימים.
    campaign = Campaign(client)
    templates = campaign.get_templates()
    print("כמות תבניות:", len(templates.get("templates", [])))


if __name__ == "__main__":
    main()
