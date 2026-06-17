"""Performance Benchmark for the Hybrid Thesis Recommender.

Measures latency and throughput of each component individually and end-to-end.
Outputs a structured performance report.

Usage:
    python benchmark_performance.py [--iterations 10] [--skip-web]

Requirements: Running system with data populated (articles.db, faiss.index, bm25.pkl).
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import statistics
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Benchmark result model
# ---------------------------------------------------------------------------

@dataclass
class BenchmarkResult:
    """Stores timing results for a single benchmark."""
    name: str
    times_ms: list[float] = field(default_factory=list)

    @property
    def mean_ms(self) -> float:
        return statistics.mean(self.times_ms) if self.times_ms else 0.0

    @property
    def median_ms(self) -> float:
        return statistics.median(self.times_ms) if self.times_ms else 0.0

    @property
    def min_ms(self) -> float:
        return min(self.times_ms) if self.times_ms else 0.0

    @property
    def max_ms(self) -> float:
        return max(self.times_ms) if self.times_ms else 0.0

    @property
    def stdev_ms(self) -> float:
        return statistics.stdev(self.times_ms) if len(self.times_ms) >= 2 else 0.0

    @property
    def p95_ms(self) -> float:
        if not self.times_ms:
            return 0.0
        sorted_times = sorted(self.times_ms)
        idx = int(len(sorted_times) * 0.95)
        return sorted_times[min(idx, len(sorted_times) - 1)]


# ---------------------------------------------------------------------------
# Benchmark runner
# ---------------------------------------------------------------------------

class PerformanceBenchmark:
    """Runs performance benchmarks on all system components."""

    QUERIES = [
        "neural networks for natural language processing",
        "machine learning in healthcare diagnosis",
        "blockchain technology applications in supply chain",
        "deep reinforcement learning for robotics",
        "quantum computing algorithms",
        "rețele neuronale convoluționale pentru clasificarea imaginilor",
        "inteligență artificială în educație",
        "securitate cibernetică și criptografie post-cuantică",
    ]

    def __init__(self, iterations: int = 10, skip_web: bool = False) -> None:
        self.iterations = iterations
        self.skip_web = skip_web
        self.results: list[BenchmarkResult] = []

        # Initialize components
        print("=" * 70)
        print("PERFORMANCE BENCHMARK — Hybrid Thesis Recommender")
        print("=" * 70)
        print(f"\nIterations per test: {iterations}")
        print(f"Test queries: {len(self.QUERIES)}")
        print(f"Skip web search: {skip_web}")
        print("\n" + "-" * 70)
        print("Initializing components...")

        from app.config_manager import ConfigManager
        from app.article_store import ArticleStore

        self.config_manager = ConfigManager("config.yaml")
        self.config = self.config_manager.get()

        self.article_store = ArticleStore(
            vector_store_path=self.config.vector_store_path,
            metadata_db_path=self.config.metadata_db_path,
        )

        # Track component initialization times
        self._init_components()
        print("-" * 70 + "\n")

    def _init_components(self) -> None:
        """Initialize all retriever components and measure startup time."""
        from app.retrievers.semantic import SemanticRetriever, SemanticRetrieverError
        from app.retrievers.keyword import KeywordRetriever, KeywordRetrieverError
        from app.retrievers.web import WebRetriever
        from app.retrievers.academic_web import AcademicWebRetriever
        from app.rankers.hybrid import HybridRanker
        from app.feedback.store import FeedbackStore
        from app.verifiers.content import ContentVerifier
        from app.language_detector import LanguageDetector

        # Semantic Retriever (includes model loading)
        t0 = time.perf_counter()
        try:
            self.semantic_retriever = SemanticRetriever(self.article_store, self.config)
            self.semantic_init_ms = (time.perf_counter() - t0) * 1000
            print(f"  ✓ SemanticRetriever initialized ({self.semantic_init_ms:.0f}ms)")
        except SemanticRetrieverError as e:
            self.semantic_retriever = None
            self.semantic_init_ms = 0
            print(f"  ✗ SemanticRetriever failed: {e}")

        # Keyword Retriever
        t0 = time.perf_counter()
        try:
            self.keyword_retriever = KeywordRetriever(self.article_store, self.config)
            kw_init_ms = (time.perf_counter() - t0) * 1000
            print(f"  ✓ KeywordRetriever initialized ({kw_init_ms:.0f}ms)")
        except KeywordRetrieverError as e:
            self.keyword_retriever = None
            print(f"  ✗ KeywordRetriever failed: {e}")

        # Web Retriever
        self.web_retriever = WebRetriever(self.config)
        print("  ✓ WebRetriever initialized")

        # Academic Web Retriever
        self.academic_retriever = AcademicWebRetriever(
            timeout=self.config.component_timeout_seconds
        )
        print("  ✓ AcademicWebRetriever initialized")

        # Feedback Store
        self.feedback_store = FeedbackStore(self.config.feedback_store_path)
        print("  ✓ FeedbackStore initialized")

        # Hybrid Ranker
        self.hybrid_ranker = HybridRanker(self.config, feedback_store=self.feedback_store)
        print("  ✓ HybridRanker initialized")

        # Content Verifier
        if self.semantic_retriever:
            self.content_verifier = ContentVerifier(self.semantic_retriever)
            print("  ✓ ContentVerifier initialized")
        else:
            self.content_verifier = None

        # Language Detector
        self.language_detector = LanguageDetector()
        print("  ✓ LanguageDetector initialized")

    def _time_fn(self, fn, *args, **kwargs) -> tuple[float, any]:
        """Time a function call, return (time_ms, result)."""
        t0 = time.perf_counter()
        result = fn(*args, **kwargs)
        elapsed = (time.perf_counter() - t0) * 1000
        return elapsed, result

    # ─────────────────────────────────────────────────────────────────────────
    # Individual component benchmarks
    # ─────────────────────────────────────────────────────────────────────────

    def bench_language_detection(self) -> BenchmarkResult:
        """Benchmark language detection speed."""
        result = BenchmarkResult(name="Language Detection")
        for query in self.QUERIES:
            for _ in range(self.iterations):
                ms, _ = self._time_fn(self.language_detector.detect, query)
                result.times_ms.append(ms)
        return result

    def bench_encoding(self) -> BenchmarkResult | None:
        """Benchmark sentence-transformer encoding."""
        if not self.semantic_retriever:
            return None
        result = BenchmarkResult(name="Embedding Encode")
        for query in self.QUERIES:
            for _ in range(self.iterations):
                ms, _ = self._time_fn(self.semantic_retriever.encode, query)
                result.times_ms.append(ms)
        return result

    def bench_faiss_search(self) -> BenchmarkResult | None:
        """Benchmark FAISS vector search (excluding encoding)."""
        if not self.semantic_retriever:
            return None
        import numpy as np
        result = BenchmarkResult(name="FAISS Search (index only)")

        # Pre-encode queries
        vectors = [self.semantic_retriever.encode(q) for q in self.QUERIES]

        for vec in vectors:
            for _ in range(self.iterations):
                t0 = time.perf_counter()
                self.article_store._index.search(
                    vec.reshape(1, -1).astype("float32"),
                    self.config.semantic_top_k,
                )
                result.times_ms.append((time.perf_counter() - t0) * 1000)
        return result

    def bench_semantic_retriever(self) -> BenchmarkResult | None:
        """Benchmark full semantic retrieval (encode + FAISS + metadata)."""
        if not self.semantic_retriever:
            return None
        from app.models import Query
        result = BenchmarkResult(name="Semantic Retriever (full)")
        for query_text in self.QUERIES:
            query = Query(title=query_text, abstract=None, keywords=[])
            for _ in range(self.iterations):
                ms, _ = self._time_fn(
                    self.semantic_retriever.retrieve, query, self.config.semantic_top_k
                )
                result.times_ms.append(ms)
        return result

    def bench_keyword_retriever(self) -> BenchmarkResult | None:
        """Benchmark BM25 keyword retrieval."""
        if not self.keyword_retriever:
            return None
        from app.models import Query
        result = BenchmarkResult(name="Keyword Retriever (BM25)")
        for query_text in self.QUERIES:
            query = Query(title=query_text, abstract=None, keywords=[])
            for _ in range(self.iterations):
                ms, _ = self._time_fn(
                    self.keyword_retriever.retrieve, query, self.config.keyword_top_k
                )
                result.times_ms.append(ms)
        return result

    def bench_web_search(self) -> BenchmarkResult | None:
        """Benchmark web search (DuckDuckGo)."""
        if self.skip_web:
            return None
        from app.models import Query
        result = BenchmarkResult(name="Web Search (DuckDuckGo)")
        # Only use 3 queries and fewer iterations for web (rate limiting)
        for query_text in self.QUERIES[:3]:
            query = Query(title=query_text, abstract=None, keywords=[])
            for _ in range(min(3, self.iterations)):
                ms, _ = self._time_fn(
                    self.web_retriever.retrieve, query, "en"
                )
                result.times_ms.append(ms)
                time.sleep(1)  # Rate limiting
        return result

    def bench_academic_search(self) -> BenchmarkResult | None:
        """Benchmark academic API search (Semantic Scholar + arXiv)."""
        if self.skip_web:
            return None
        from app.models import Query
        result = BenchmarkResult(name="Academic Search (Semantic Scholar + arXiv)")
        for query_text in self.QUERIES[:3]:
            query = Query(title=query_text, abstract=None, keywords=[])
            for _ in range(min(3, self.iterations)):
                ms, _ = self._time_fn(
                    self.academic_retriever.retrieve, query, self.config.article_top_k
                )
                result.times_ms.append(ms)
                time.sleep(0.5)
        return result

    def bench_hybrid_ranker(self) -> BenchmarkResult | None:
        """Benchmark hybrid fusion (RRF/weighted sum)."""
        if not self.semantic_retriever or not self.keyword_retriever:
            return None
        from app.models import Query, RetrievalResult
        result = BenchmarkResult(name="Hybrid Ranker (RRF fusion)")

        # Pre-compute retrieval results
        for query_text in self.QUERIES:
            query = Query(title=query_text, abstract=None, keywords=[])
            sem = self.semantic_retriever.retrieve(query, self.config.semantic_top_k)
            kw = self.keyword_retriever.retrieve(query, self.config.keyword_top_k)

            for _ in range(self.iterations):
                ms, _ = self._time_fn(
                    self.hybrid_ranker.fuse_articles,
                    semantic=sem,
                    keyword=kw,
                    top_k=self.config.article_top_k,
                    semantic_weight=self.config.semantic_weight,
                    keyword_weight=self.config.keyword_weight,
                )
                result.times_ms.append(ms)
        return result

    def bench_content_verifier(self) -> BenchmarkResult | None:
        """Benchmark content verification (quality checking)."""
        if not self.content_verifier or not self.semantic_retriever:
            return None
        from app.models import ArticleRecommendation, WebResourceRecommendation
        import numpy as np
        result = BenchmarkResult(name="Content Verifier")

        # Create sample recommendations to verify
        sample_articles = [
            ArticleRecommendation(
                title="Attention Is All You Need",
                authors=["Vaswani, A."],
                year=2017,
                abstract_snippet="The dominant sequence transduction models...",
                doi="10.48550/arXiv.1706.03762",
                url="https://arxiv.org/abs/1706.03762",
                score=0.9,
                quality_warning=None,
                item_id="doi:10.48550/arXiv.1706.03762",
            )
        ]
        sample_web = [
            WebResourceRecommendation(
                title="Introduction to Neural Networks",
                url="https://example.com/nn",
                snippet="A comprehensive guide to neural networks and deep learning",
                web_score=0.8,
                keywords=["neural networks"],
                quality_warning=None,
                item_id="url:https://example.com/nn",
            )
        ]

        for query_text in self.QUERIES[:4]:
            query_embedding = self.semantic_retriever.encode(query_text)
            for _ in range(self.iterations):
                ms, _ = self._time_fn(
                    self.content_verifier.verify,
                    sample_articles.copy(),
                    sample_web.copy(),
                    query_embedding,
                    "en",
                    self.config,
                )
                result.times_ms.append(ms)
        return result

    def bench_end_to_end_local(self) -> BenchmarkResult | None:
        """Benchmark full pipeline (local only, no web)."""
        if not self.semantic_retriever or not self.keyword_retriever:
            return None
        from app.models import Query, RetrievalResult, WebRetrievalResult
        result = BenchmarkResult(name="End-to-End (local only, no web)")

        for query_text in self.QUERIES:
            for _ in range(self.iterations):
                t0 = time.perf_counter()

                # Language detection
                lang = self.language_detector.detect(query_text)
                query = Query(title=query_text, abstract=None, keywords=[])

                # Parallel retrieval (local only)
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    sem_future = executor.submit(
                        self.semantic_retriever.retrieve, query, self.config.semantic_top_k
                    )
                    kw_future = executor.submit(
                        self.keyword_retriever.retrieve, query, self.config.keyword_top_k
                    )
                    sem_result = sem_future.result(timeout=10)
                    kw_result = kw_future.result(timeout=10)

                # Fusion
                articles = self.hybrid_ranker.fuse_articles(
                    semantic=sem_result,
                    keyword=kw_result,
                    top_k=self.config.article_top_k,
                    semantic_weight=self.config.semantic_weight,
                    keyword_weight=self.config.keyword_weight,
                )

                # Content verification
                if self.content_verifier:
                    query_embedding = self.semantic_retriever.encode(query_text)
                    articles, _ = self.content_verifier.verify(
                        articles, [], query_embedding, lang, self.config
                    )

                elapsed = (time.perf_counter() - t0) * 1000
                result.times_ms.append(elapsed)
        return result

    def bench_end_to_end_full(self) -> BenchmarkResult | None:
        """Benchmark full pipeline including web search."""
        if self.skip_web or not self.semantic_retriever:
            return None
        from app.models import Query, RetrievalResult, WebRetrievalResult
        result = BenchmarkResult(name="End-to-End (with web search)")

        for query_text in self.QUERIES[:3]:  # Fewer iterations for web
            t0 = time.perf_counter()

            lang = self.language_detector.detect(query_text)
            query = Query(title=query_text, abstract=None, keywords=[])

            # Parallel retrieval (all sources)
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = {}
                futures["semantic"] = executor.submit(
                    self.semantic_retriever.retrieve, query, self.config.semantic_top_k
                )
                if self.keyword_retriever:
                    futures["keyword"] = executor.submit(
                        self.keyword_retriever.retrieve, query, self.config.keyword_top_k
                    )
                futures["web"] = executor.submit(
                    self.web_retriever.retrieve, query, lang
                )
                futures["academic"] = executor.submit(
                    self.academic_retriever.retrieve, query, self.config.article_top_k
                )

                sem_result = futures["semantic"].result(timeout=18)
                kw_result = futures.get("keyword", futures["semantic"]).result(timeout=18)
                web_result = futures["web"].result(timeout=18)
                acad_result = futures["academic"].result(timeout=18)

            # Merge academic into semantic
            if acad_result and acad_result.items:
                sem_result.items.extend(acad_result.items)

            # Fusion
            articles = self.hybrid_ranker.fuse_articles(
                semantic=sem_result,
                keyword=kw_result,
                top_k=self.config.article_top_k,
                semantic_weight=self.config.semantic_weight,
                keyword_weight=self.config.keyword_weight,
            )

            web_resources = self.hybrid_ranker.rank_web_resources(
                web_result, self.config.web_top_k
            )

            # Content verification
            if self.content_verifier:
                query_embedding = self.semantic_retriever.encode(query_text)
                articles, web_resources = self.content_verifier.verify(
                    articles, web_resources, query_embedding, lang, self.config
                )

            elapsed = (time.perf_counter() - t0) * 1000
            result.times_ms.append(elapsed)
            time.sleep(1)  # Rate limiting

        return result

    # ─────────────────────────────────────────────────────────────────────────
    # Memory profiling
    # ─────────────────────────────────────────────────────────────────────────

    def measure_memory(self) -> dict[str, float]:
        """Measure memory usage of key components (in MB)."""
        import sys

        memory = {}

        # FAISS index size
        n_vectors = self.article_store._index.ntotal
        memory["faiss_index"] = (n_vectors * 768 * 4) / (1024 * 1024)  # float32
        memory["faiss_vectors"] = n_vectors

        # BM25 index (approximate from file size)
        bm25_path = Path(self.config.bm25_index_path)
        if bm25_path.exists():
            memory["bm25_index_file_mb"] = bm25_path.stat().st_size / (1024 * 1024)

        # SQLite DB sizes
        articles_db = Path(self.config.metadata_db_path)
        if articles_db.exists():
            memory["articles_db_mb"] = articles_db.stat().st_size / (1024 * 1024)

        feedback_db = Path(self.config.feedback_store_path)
        if feedback_db.exists():
            memory["feedback_db_mb"] = feedback_db.stat().st_size / (1024 * 1024)

        # Embedding model (approximate)
        memory["embedding_model_mb"] = 420  # paraphrase-multilingual-mpnet-base-v2

        # Process memory
        try:
            import psutil
            process = psutil.Process()
            mem_info = process.memory_info()
            memory["process_rss_mb"] = mem_info.rss / (1024 * 1024)
            memory["process_vms_mb"] = mem_info.vms / (1024 * 1024)
        except ImportError:
            memory["process_rss_mb"] = -1
            memory["process_vms_mb"] = -1

        return memory

    # ─────────────────────────────────────────────────────────────────────────
    # Run all benchmarks
    # ─────────────────────────────────────────────────────────────────────────

    def run_all(self) -> None:
        """Execute all benchmarks and print the report."""
        benchmarks = [
            ("Language Detection", self.bench_language_detection),
            ("Embedding Encode", self.bench_encoding),
            ("FAISS Search", self.bench_faiss_search),
            ("Semantic Retriever", self.bench_semantic_retriever),
            ("Keyword Retriever", self.bench_keyword_retriever),
            ("Hybrid Ranker", self.bench_hybrid_ranker),
            ("Content Verifier", self.bench_content_verifier),
            ("Web Search", self.bench_web_search),
            ("Academic Search", self.bench_academic_search),
            ("End-to-End (local)", self.bench_end_to_end_local),
            ("End-to-End (full)", self.bench_end_to_end_full),
        ]

        for name, bench_fn in benchmarks:
            print(f"\n▶ Running: {name}...")
            try:
                result = bench_fn()
                if result:
                    self.results.append(result)
                    print(f"  ✓ {result.mean_ms:.1f}ms mean | "
                          f"{result.median_ms:.1f}ms median | "
                          f"{result.p95_ms:.1f}ms p95 | "
                          f"({len(result.times_ms)} samples)")
                else:
                    print(f"  ⊘ Skipped (component unavailable)")
            except Exception as e:
                print(f"  ✗ Failed: {e}")

        # Memory
        print(f"\n▶ Measuring memory usage...")
        memory = self.measure_memory()

        # Print final report
        self._print_report(memory)

    def _print_report(self, memory: dict[str, float]) -> None:
        """Print a formatted performance report."""
        print("\n")
        print("=" * 70)
        print("PERFORMANCE REPORT")
        print("=" * 70)

        # Latency table
        print("\n┌─────────────────────────────────────┬────────┬────────┬────────┬────────┬────────┐")
        print("│ Component                           │ Mean   │ Median │ P95    │ Min    │ Max    │")
        print("├─────────────────────────────────────┼────────┼────────┼────────┼────────┼────────┤")
        for r in self.results:
            name = r.name[:37].ljust(37)
            print(f"│ {name} │ {r.mean_ms:5.1f}ms│ {r.median_ms:5.1f}ms│ "
                  f"{r.p95_ms:5.1f}ms│ {r.min_ms:5.1f}ms│ {r.max_ms:5.1f}ms│")
        print("└─────────────────────────────────────┴────────┴────────┴────────┴────────┴────────┘")

        # Memory table
        print("\n┌─────────────────────────────────────┬──────────────┐")
        print("│ Resource                            │ Size         │")
        print("├─────────────────────────────────────┼──────────────┤")
        print(f"│ FAISS Index ({memory.get('faiss_vectors', 0):.0f} vectors)        │ {memory.get('faiss_index', 0):8.2f} MB  │")
        print(f"│ BM25 Index (file)                   │ {memory.get('bm25_index_file_mb', 0):8.2f} MB  │")
        print(f"│ Articles DB                         │ {memory.get('articles_db_mb', 0):8.2f} MB  │")
        print(f"│ Feedback DB                         │ {memory.get('feedback_db_mb', 0):8.2f} MB  │")
        print(f"│ Embedding Model (approx)            │ {memory.get('embedding_model_mb', 0):8.0f} MB  │")
        if memory.get("process_rss_mb", -1) > 0:
            print(f"│ Process RSS                         │ {memory['process_rss_mb']:8.1f} MB  │")
            print(f"│ Process VMS                         │ {memory['process_vms_mb']:8.1f} MB  │")
        print("└─────────────────────────────────────┴──────────────┘")

        # Model initialization
        print(f"\n⏱  Model initialization time: {self.semantic_init_ms:.0f}ms")

        # Summary
        print("\n── Summary ──")
        local_results = [r for r in self.results if r.name == "End-to-End (local only, no web)"]
        full_results = [r for r in self.results if r.name == "End-to-End (with web search)"]
        if local_results:
            print(f"  • End-to-end (local only): {local_results[0].mean_ms:.0f}ms mean, "
                  f"{local_results[0].p95_ms:.0f}ms p95")
        if full_results:
            print(f"  • End-to-end (with web):   {full_results[0].mean_ms:.0f}ms mean, "
                  f"{full_results[0].p95_ms:.0f}ms p95")

        # Bottleneck analysis
        print("\n── Bottleneck Analysis ──")
        sorted_results = sorted(self.results, key=lambda r: r.mean_ms, reverse=True)
        for i, r in enumerate(sorted_results[:3], 1):
            print(f"  {i}. {r.name}: {r.mean_ms:.1f}ms mean")

        # Export JSON
        self._export_json(memory)

    def _export_json(self, memory: dict[str, float]) -> None:
        """Export results as JSON for programmatic consumption."""
        report = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "config": {
                "iterations": self.iterations,
                "queries": len(self.QUERIES),
                "semantic_top_k": self.config.semantic_top_k,
                "keyword_top_k": self.config.keyword_top_k,
                "article_top_k": self.config.article_top_k,
                "fusion_strategy": self.config.fusion_strategy,
            },
            "latency": {
                r.name: {
                    "mean_ms": round(r.mean_ms, 2),
                    "median_ms": round(r.median_ms, 2),
                    "p95_ms": round(r.p95_ms, 2),
                    "min_ms": round(r.min_ms, 2),
                    "max_ms": round(r.max_ms, 2),
                    "stdev_ms": round(r.stdev_ms, 2),
                    "samples": len(r.times_ms),
                }
                for r in self.results
            },
            "memory": memory,
            "initialization_ms": round(self.semantic_init_ms, 1),
        }

        output_path = Path("data/benchmark_results.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n📄 Results exported to: {output_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Performance benchmark for Hybrid Thesis Recommender")
    parser.add_argument("--iterations", type=int, default=10,
                        help="Number of iterations per test (default: 10)")
    parser.add_argument("--skip-web", action="store_true",
                        help="Skip web search benchmarks (avoid rate limiting)")
    args = parser.parse_args()

    benchmark = PerformanceBenchmark(
        iterations=args.iterations,
        skip_web=args.skip_web,
    )
    benchmark.run_all()


if __name__ == "__main__":
    main()
