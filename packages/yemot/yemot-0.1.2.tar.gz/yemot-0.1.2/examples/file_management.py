"""ניהול קבצי IVR באמצעות המודול System."""

from pathlib import Path

from yemot import Client, System, YemotError


def main() -> None:
    """מדגים העלאה, הורדה והמרה בסיסית של קבצים."""
    client = Client(username="0xxxxxxxxx", password="xxxxxx")
    system = System(client)

    source_path = Path("example_message.mp3")
    if not source_path.exists():
        source_path.write_bytes(b"Fake MP3 data - replace with a real recording.")
        print("נוצר קובץ דמה example_message.mp3 - מומלץ להחליף בהקלטה אמיתית.")

    try:
        system.upload_file(
            file_path=str(source_path),
            path="ivr2:1/000.wav",
            convert_audio=True,
        )
        print("הקובץ הועלה לנתיב ivr2:1/000.wav")

        downloaded = system.download_file(path="ivr2:1/000.wav")
        Path("downloaded_demo.wav").write_bytes(downloaded)
        print("הקובץ הורד ונשמר בשם downloaded_demo.wav")
    except YemotError as exc:
        print("שגיאת API:", exc)


if __name__ == "__main__":
    main()
