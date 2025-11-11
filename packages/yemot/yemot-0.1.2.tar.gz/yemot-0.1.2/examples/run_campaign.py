"""דוגמה לניהול תבניות וקמפיינים קוליים."""

from typing import Any, Dict

from yemot import Campaign, Client, YemotError


def _ensure_template(campaign: Campaign) -> int:
    """מאזן בין שליפת תבנית קיימת ליצירת חדשה לצורכי הדגמה."""
    templates: Dict[str, Any] = campaign.get_templates()
    existing = templates.get("templates", [])
    if existing:
        return int(existing[0]["templateId"])

    created = campaign.create_template("תבנית API חדשה")
    template_id = int(created.get("templateId", 0))
    if not template_id:
        raise RuntimeError("יצירת תבנית נכשלה")
    return template_id


def main() -> None:
    """מריץ זרימה בסיסית של ניהול קמפיין."""
    client = Client(username="0xxxxxxxxx", password="xxxxxx")
    campaign = Campaign(client)

    try:
        template_id = _ensure_template(campaign)

        campaign.update_template(
            template_id,
            description="קמפיין עדכון מערכת",
            max_active_channels=50,
            vm_detect=True,
            redial_policy="FAILED",
        )
        print(f"תבנית {template_id} עודכנה בהצלחה")

        campaign.update_template_entry(
            template_id,
            phone="0501234567",
            name="לקוח לדוגמה",
            more_info="First batch",
        )
        print("נוסף איש קשר חדש לקמפיין")

        campaign.upload_template_file(
            file_path="downloaded_demo.wav",
            template_name=str(template_id),
            file_type="VOICE",
            convert_audio=True,
        )
        print("הודעת הקמפיין הועלתה בהצלחה")

    except YemotError as exc:
        print("שגיאת API:", exc)


if __name__ == "__main__":
    main()
