"""
Seed the languages table with supported languages.

Safe to run multiple times.
"""

from app.db.session import SessionLocal
from app.models.language import Language


LANGUAGES = [
    ("en", "English", "English", True),
    ("ja", "Japanese", "日本語", True),
    ("de", "German", "Deutsch", True),
    ("fr", "French", "Français", True),
    ("es", "Spanish", "Español", True),
    ("hi", "Hindi", "हिन्दी", True),
    ("ko", "Korean", "한국어", False),
    ("zh-Hans", "Chinese (Simplified)", "简体中文", False),
    ("zh-Hant", "Chinese (Traditional)", "繁體中文", False),
    ("it", "Italian", "Italiano", False),
    ("pt", "Portuguese", "Português", False),
    ("ru", "Russian", "Русский", False),
    ("ar", "Arabic", "العربية", False),
    ("tr", "Turkish", "Türkçe", False),
    ("nl", "Dutch", "Nederlands", False),
    ("pl", "Polish", "Polski", False),
    ("sv", "Swedish", "Svenska", False),
    ("no", "Norwegian", "Norsk", False),
    ("da", "Danish", "Dansk", False),
    ("fi", "Finnish", "Suomi", False),
    ("el", "Greek", "Ελληνικά", False),
    ("he", "Hebrew", "עברית", False),
    ("th", "Thai", "ไทย", False),
    ("vi", "Vietnamese", "Tiếng Việt", False),
    ("id", "Indonesian", "Bahasa Indonesia", False),
    ("ms", "Malay", "Bahasa Melayu", False),
    ("ta", "Tamil", "தமிழ்", False),
    ("te", "Telugu", "తెలుగు", False),
    ("bn", "Bengali", "বাংলা", False),
    ("pa", "Punjabi", "ਪੰਜਾਬੀ", False),
    ("ur", "Urdu", "اردو", False),
    ("mr", "Marathi", "मराठी", False),
    ("gu", "Gujarati", "ગુજરાતી", False),
    ("kn", "Kannada", "ಕನ್ನಡ", False),
    ("ml", "Malayalam", "മലയാളം", False),
    ("ne", "Nepali", "नेपाली", False),
    ("si", "Sinhala", "සිංහල", False),
    ("fa", "Persian", "فارسی", False),
    ("uk", "Ukrainian", "Українська", False),
    ("cs", "Czech", "Čeština", False),
    ("sk", "Slovak", "Slovenčina", False),
    ("ro", "Romanian", "Română", False),
    ("hu", "Hungarian", "Magyar", False),
    ("bg", "Bulgarian", "Български", False),
    ("hr", "Croatian", "Hrvatski", False),
    ("sr", "Serbian", "Српски", False),
    ("lt", "Lithuanian", "Lietuvių", False),
    ("lv", "Latvian", "Latviešu", False),
    ("et", "Estonian", "Eesti", False),
    ("fil", "Filipino", "Filipino", False),
    ("sw", "Swahili", "Kiswahili", False),
]


def main():
    db = SessionLocal()

    inserted = 0
    skipped = 0

    try:
        for code, name, native_name, ui_supported in LANGUAGES:
            exists = (
                db.query(Language)
                .filter(Language.code == code)
                .first()
            )

            if exists:
                skipped += 1
                continue

            db.add(
                Language(
                    code=code,
                    name=name,
                    native_name=native_name,
                    is_learnable=True,
                    is_ui_supported=ui_supported,
                    is_active=True,
                )
            )

            inserted += 1

        db.commit()

        print("=" * 50)
        print("Language seeding completed")
        print(f"Inserted : {inserted}")
        print(f"Skipped  : {skipped}")
        print("=" * 50)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()