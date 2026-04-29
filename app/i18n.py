"""Localization helper for the Hybrid Thesis Recommender.

Provides a simple message table and a `t()` function to retrieve
translated strings for supported languages ("ro", "en").
"""

_MESSAGES: dict[str, dict[str, str]] = {
    "no_articles": {
        "ro": "Nu au fost găsite articole suficient de relevante.",
        "en": "No sufficiently relevant articles were found.",
    },
    "no_web_resources": {
        "ro": "Nu au fost găsite resurse web suficient de relevante.",
        "en": "No sufficiently relevant web resources were found.",
    },
    "semantic_unavailable": {
        "ro": "Recuperarea semantică nu este disponibilă.",
        "en": "Semantic retrieval is unavailable.",
    },
    "keyword_unavailable": {
        "ro": "Recuperarea prin cuvinte cheie nu este disponibilă.",
        "en": "Keyword retrieval is unavailable.",
    },
    "web_unavailable": {
        "ro": "Căutarea web nu este disponibilă.",
        "en": "Web search is unavailable.",
    },
    "quality_warning": {
        "ro": "⚠ Verificați conținutul",
        "en": "⚠ Verify content",
    },
    "rating_saved": {
        "ro": "Evaluare salvată.",
        "en": "Rating saved.",
    },
    "rating_invalid": {
        "ro": "Evaluarea trebuie să fie un număr întreg între 1 și 5.",
        "en": "Rating must be an integer between 1 and 5.",
    },
    "query_invalid": {
        "ro": "Titlul trebuie să aibă între 3 și 500 de caractere.",
        "en": "Title must be between 3 and 500 characters.",
    },
}


def t(key: str, language: str) -> str:
    """Return the localised message for *key* in *language*.

    Falls back to ``"en"`` for unknown languages.
    Returns *key* itself when the key is not present in the message table.
    """
    entry = _MESSAGES.get(key)
    if entry is None:
        return key
    return entry.get(language) or entry.get("en") or key
