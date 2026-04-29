"""ConfigManager — loads, validates, and hot-reloads AppConfig from a YAML file."""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Optional

import yaml
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from app.config import AppConfig

logger = logging.getLogger(__name__)

_VALID_FUSION_STRATEGIES = {"rrf", "weighted_sum"}
_VALID_WEB_SEARCH_PROVIDERS = {"duckduckgo", "google_cse", "bing"}
_VALID_LANGUAGES = {"ro", "en"}


def _validate(cfg: AppConfig) -> list[str]:
    """Return a list of validation error messages; empty list means valid."""
    errors: list[str] = []

    # Weights must be in [0.0, 1.0]
    if not (0.0 <= cfg.semantic_weight <= 1.0):
        errors.append(
            f"semantic_weight must be in [0.0, 1.0], got {cfg.semantic_weight}"
        )
    if not (0.0 <= cfg.keyword_weight <= 1.0):
        errors.append(
            f"keyword_weight must be in [0.0, 1.0], got {cfg.keyword_weight}"
        )

    # Top-K values must be >= 1
    for name, value in [
        ("article_top_k", cfg.article_top_k),
        ("web_top_k", cfg.web_top_k),
        ("semantic_top_k", cfg.semantic_top_k),
        ("keyword_top_k", cfg.keyword_top_k),
    ]:
        if value < 1:
            errors.append(f"{name} must be >= 1, got {value}")

    # Fusion strategy
    if cfg.fusion_strategy not in _VALID_FUSION_STRATEGIES:
        errors.append(
            f"fusion_strategy must be one of {_VALID_FUSION_STRATEGIES}, "
            f"got '{cfg.fusion_strategy}'"
        )

    # Web search provider
    if cfg.web_search_provider not in _VALID_WEB_SEARCH_PROVIDERS:
        errors.append(
            f"web_search_provider must be one of {_VALID_WEB_SEARCH_PROVIDERS}, "
            f"got '{cfg.web_search_provider}'"
        )

    # Default language
    if cfg.default_language not in _VALID_LANGUAGES:
        errors.append(
            f"default_language must be one of {_VALID_LANGUAGES}, "
            f"got '{cfg.default_language}'"
        )

    # restrict_language (None is allowed)
    if cfg.restrict_language is not None and cfg.restrict_language not in _VALID_LANGUAGES:
        errors.append(
            f"restrict_language must be None or one of {_VALID_LANGUAGES}, "
            f"got '{cfg.restrict_language}'"
        )

    return errors


def _build_config(data: dict) -> AppConfig:
    """Construct an AppConfig from a raw YAML dict, ignoring unknown keys."""
    defaults = AppConfig()
    kwargs: dict = {}

    field_names = {f.name for f in AppConfig.__dataclass_fields__.values()}  # type: ignore[attr-defined]
    for key, value in data.items():
        if key in field_names:
            kwargs[key] = value

    return AppConfig(**kwargs)


class _ConfigFileHandler(FileSystemEventHandler):
    """Watchdog event handler that triggers a config reload on file modification."""

    def __init__(self, manager: "ConfigManager") -> None:
        super().__init__()
        self._manager = manager

    def on_modified(self, event) -> None:  # type: ignore[override]
        if not event.is_directory and Path(event.src_path).resolve() == self._manager._config_path.resolve():
            logger.info("Config file changed, reloading…")
            self._manager.reload()


class ConfigManager:
    """
    Reads a YAML config file, validates all fields, and hot-reloads on change.

    Usage::

        manager = ConfigManager("config.yaml")
        cfg = manager.get()          # AppConfig snapshot
        manager.reload()             # manual reload
        manager.start_watching()     # begin watchdog file watcher
        manager.stop_watching()      # stop watchdog file watcher
    """

    def __init__(self, config_path: str = "config.yaml") -> None:
        self._config_path = Path(config_path)
        self._lock = threading.RLock()
        self._current: AppConfig = AppConfig()  # safe default until first load
        self._observer: Optional[Observer] = None

        # Perform initial load; if it fails, keep the dataclass defaults
        self.reload()

    # ── Public API ────────────────────────────────────────────────────────────

    def get(self) -> AppConfig:
        """Return the current validated config snapshot (thread-safe)."""
        with self._lock:
            return self._current

    def reload(self) -> None:
        """Re-read the config file and validate; retain previous config on error."""
        try:
            raw = self._read_yaml()
        except Exception as exc:
            logger.warning("Failed to read config file '%s': %s", self._config_path, exc)
            return

        try:
            candidate = _build_config(raw)
        except Exception as exc:
            logger.warning("Failed to parse config values: %s", exc)
            return

        errors = _validate(candidate)
        if errors:
            for err in errors:
                logger.warning("Invalid config value — retaining previous config: %s", err)
            return

        with self._lock:
            self._current = candidate
            logger.info("Config reloaded successfully from '%s'", self._config_path)

    def start_watching(self) -> None:
        """Start the watchdog observer to hot-reload on file changes."""
        if self._observer is not None:
            return  # already watching

        handler = _ConfigFileHandler(self)
        observer = Observer()
        watch_dir = str(self._config_path.parent.resolve())
        observer.schedule(handler, watch_dir, recursive=False)
        observer.start()
        self._observer = observer
        logger.info("Watching '%s' for config changes", self._config_path)

    def stop_watching(self) -> None:
        """Stop the watchdog observer."""
        if self._observer is not None:
            self._observer.stop()
            self._observer.join()
            self._observer = None

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _read_yaml(self) -> dict:
        """Read and parse the YAML config file; return an empty dict if missing."""
        if not self._config_path.exists():
            logger.warning(
                "Config file '%s' not found; using AppConfig defaults", self._config_path
            )
            return {}
        with self._config_path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        return data if isinstance(data, dict) else {}
