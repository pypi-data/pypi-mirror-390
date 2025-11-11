"""בדיקות בסיסיות עבור חבילת yemot."""


def test_package_import() -> None:
    """מוודא שניתן לייבא את המודולים המרכזיים ללא חריגה."""
    from yemot import Client, System, Campaign  # noqa: F401
