"""Entry point for the Hybrid Thesis Recommender.

Usage
-----
Run the development server::

    python -m app.main

Ingest an article corpus::

    python -m app.main ingest --file data/articles.json --format json
    python -m app.main ingest --file data/articles.csv  --format csv
    python -m app.main ingest --file data/refs.bib      --format bibtex

Requirements: 7.1, 11.1
"""

from __future__ import annotations

import argparse
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Sub-command: serve (default)
# ---------------------------------------------------------------------------

def _cmd_serve(args: argparse.Namespace) -> None:
    """Instantiate all components and start the Flask development server."""
    from app.config_manager import ConfigManager
    from app.api import create_app

    config_path: str = args.config
    host: str = args.host
    port: int = args.port
    debug: bool = args.debug

    logger.info("Loading configuration from '%s'.", config_path)
    config_manager = ConfigManager(config_path)
    config_manager.start_watching()

    logger.info("Building Flask application…")
    app = create_app(config_manager)

    logger.info("Starting development server on %s:%d (debug=%s).", host, port, debug)
    try:
        app.run(host=host, port=port, debug=debug, use_reloader=False)
    finally:
        config_manager.stop_watching()


# ---------------------------------------------------------------------------
# Sub-command: ingest
# ---------------------------------------------------------------------------

def _cmd_ingest(args: argparse.Namespace) -> None:
    """Ingest an article file into the ArticleStore."""
    from app.article_store import ArticleStore
    from app.config_manager import ConfigManager
    from app.ingestion.pipeline import IngestionPipeline
    from app.language_detector import LanguageDetector

    config_path: str = args.config
    file_path: str = args.file
    fmt: str = args.format

    logger.info("Loading configuration from '%s'.", config_path)
    config_manager = ConfigManager(config_path)
    cfg = config_manager.get()

    logger.info("Initializing ArticleStore…")
    article_store = ArticleStore(
        vector_store_path=cfg.vector_store_path,
        metadata_db_path=cfg.metadata_db_path,
    )

    language_detector = LanguageDetector()

    pipeline = IngestionPipeline(
        article_store=article_store,
        config=cfg,
        language_detector=language_detector,
    )

    logger.info("Ingesting '%s' (format=%s)…", file_path, fmt)
    report = pipeline.ingest_file(path=file_path, format=fmt)

    print(
        f"\nIngestion complete:\n"
        f"  Ingested : {report.ingested}\n"
        f"  Skipped  : {report.skipped}\n"
        f"  Failed   : {report.failed}"
    )

    if report.errors:
        print("\nErrors:")
        for err in report.errors:
            print(f"  - {err}")

    if report.failed > 0:
        sys.exit(1)


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hybrid-thesis-recommender",
        description="Hybrid Thesis Recommender — Flask backend and ingestion CLI.",
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        metavar="PATH",
        help="Path to the YAML configuration file (default: config.yaml).",
    )

    subparsers = parser.add_subparsers(dest="command")

    # ── serve ────────────────────────────────────────────────────────────────
    serve_parser = subparsers.add_parser(
        "serve",
        help="Start the Flask development server (default command).",
    )
    serve_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind the server to (default: 127.0.0.1).",
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to listen on (default: 5000).",
    )
    serve_parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable Flask debug mode.",
    )

    # ── ingest ───────────────────────────────────────────────────────────────
    ingest_parser = subparsers.add_parser(
        "ingest",
        help="Ingest an article corpus file into the ArticleStore.",
    )
    ingest_parser.add_argument(
        "--file",
        required=True,
        metavar="PATH",
        help="Path to the input file (JSON, CSV, or BibTeX).",
    )
    ingest_parser.add_argument(
        "--format",
        required=True,
        choices=["json", "csv", "bibtex"],
        help="Format of the input file.",
    )

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Default to 'serve' when no sub-command is given
    if args.command is None or args.command == "serve":
        # Populate serve defaults if the sub-command was omitted entirely
        if args.command is None:
            args.host = getattr(args, "host", "127.0.0.1")
            args.port = getattr(args, "port", 5000)
            args.debug = getattr(args, "debug", False)
        _cmd_serve(args)
    elif args.command == "ingest":
        _cmd_ingest(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
