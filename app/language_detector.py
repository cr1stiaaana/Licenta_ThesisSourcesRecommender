"""Language detection for the Hybrid Thesis Recommender.

Uses an ensemble of langdetect and langid to identify whether a query is
Romanian ("ro") or English ("en"). Falls back to "en" on any disagreement
or exception.
"""

from __future__ import annotations

import logging
from typing import Literal

logger = logging.getLogger(__name__)


class LanguageDetector:
    """Detects whether text is Romanian or English.

    Uses langdetect and langid as an ensemble: both libraries must agree
    on a supported language ("ro" or "en") for that result to be returned.
    Any disagreement, unsupported language, or exception causes a fallback
    to "en".
    """

    _SUPPORTED: frozenset[str] = frozenset({"ro", "en"})

    def detect(self, text: str) -> Literal["ro", "en"]:
        """Return 'ro' or 'en' for the given text.

        Never raises an exception — always returns a valid language code.

        Args:
            text: The text to classify (e.g. a thesis title).

        Returns:
            "ro" if both libraries agree the text is Romanian,
            "en" otherwise (including on any failure or disagreement).
        """
        langdetect_result: str | None = None
        langid_result: str | None = None

        # --- langdetect ---
        try:
            import langdetect  # type: ignore[import-untyped]

            langdetect_result = langdetect.detect(text)
        except Exception as exc:  # noqa: BLE001
            logger.debug("langdetect raised an exception: %s — falling back to 'en'", exc)
            return "en"

        # --- langid ---
        try:
            import langid  # type: ignore[import-untyped]

            langid_result = langid.classify(text)[0]
        except Exception as exc:  # noqa: BLE001
            logger.debug("langid raised an exception: %s — falling back to 'en'", exc)
            return "en"

        # --- ensemble decision ---
        if langdetect_result == langid_result and langdetect_result in self._SUPPORTED:
            return langdetect_result  # type: ignore[return-value]

        logger.debug(
            "Language detection disagreement or unsupported result "
            "(langdetect=%r, langid=%r) — falling back to 'en'",
            langdetect_result,
            langid_result,
        )
        return "en"
