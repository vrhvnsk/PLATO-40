
import csv
from functools import lru_cache
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent.parent / "data" / "adaption" / "guest_message_templates.csv"

LANGUAGES = {
    "en": "en", "english": "en",
    "de": "de", "german": "de",
    "fr": "fr", "french": "fr",
    "it": "it", "italian": "it",
    "es": "es", "spanish": "es",
    "nl": "nl", "dutch": "nl",
}

FALLBACK = (
    "Your room is not confirmed ready yet. "
    "We will update you once housekeeping verifies readiness."
)


@lru_cache(maxsize=1)
def load_templates():
    templates = {}
    if not TEMPLATES.is_file():
        return templates

    with TEMPLATES.open(encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            scenario = (row.get("scenario") or "").strip().lower()
            language = (row.get("language") or "").strip().lower()
            message = (row.get("text") or "").strip()

            language = LANGUAGES.get(language, language)

            if scenario and language and message:
                templates[(scenario, language)] = message

    return templates


def propose_guest_message(language, scenario="early_checkin"):
    code = LANGUAGES.get(str(language).strip().lower(), "en")
    templates = load_templates()

    message = (
        templates.get((scenario, code))
        or templates.get((scenario, "en"))
        or FALLBACK
    )

    return f"PROPOSED ({code}; NOT SENT): {message}"
