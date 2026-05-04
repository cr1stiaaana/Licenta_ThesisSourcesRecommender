# Niveluri de Specificații în Spec-Driven Development

## Cuprins

1. [Introducere](#introducere)
2. [Tipuri de Specificații în SDD](#tipuri-de-specificatii-in-sdd)
3. [Feature Specifications - Requirements-First Workflow](#feature-specifications---requirements-first-workflow)
4. [Nivelurile de Abstractizare](#nivelurile-de-abstractizare)
5. [Exemplu Complet: Hybrid Ranking System](#exemplu-complet-hybrid-ranking-system)
6. [Trasabilitate între Niveluri](#trasabilitate-intre-niveluri)
7. [Property-Based Testing Integration](#property-based-testing-integration)
8. [Beneficiile Requirements-First](#beneficiile-requirements-first)
9. [Comparație: Requirements-First vs Design-First](#comparatie-requirements-first-vs-design-first)

---

## Introducere

În dezvoltarea software modernă, **specificațiile** joacă un rol crucial în transformarea ideilor abstracte în cod funcțional. **Spec-Driven Development (SDD)** introduce o metodologie structurată pentru crearea și gestionarea specificațiilor la multiple niveluri de abstractizare, asigurând că fiecare decizie de design și implementare este trasabilă până la cerințele inițiale.

Acest capitol explorează **nivelurile de specificații** folosite în SDD, cu focus pe **Feature Specifications** și **Requirements-First workflow** - abordarea folosită în dezvoltarea sistemului Hybrid Thesis Recommender.

### Ierarhia Specificațiilor

Specificațiile în SDD sunt organizate ierarhic, de la abstract la concret:

```
Business Requirements (Ce vrem să realizăm?)
        ↓
Functional Specifications (Ce trebuie să facă sistemul?)
        ↓
Technical Design (Cum implementăm funcționalitatea?)
        ↓
Implementation Tasks (Pași concreți de implementare)
        ↓
Code + Tests (Cod executabil + verificare)
```

---

## Tipuri de Specificații în SDD

SDD definește două tipuri principale de specificații:

### 1. Feature Specifications (Specificații de Funcționalitate)

Folosite pentru **dezvoltarea de funcționalități noi** care nu există încă în sistem.

**Workflow-uri disponibile:**
- **Requirements-First**: Cerințe → Design → Tasks (folosit în Hybrid Thesis Recommender)
- **Design-First**: Design → Cerințe → Tasks

### 2. Bugfix Specifications

Folosite pentru **corectarea defectelor** în funcționalități existente.

**Workflow:** Bugfix Requirements → Design → Tasks

---

## Feature Specifications - Requirements-First Workflow

Requirements-First este abordarea în care **cerințele de business și funcționale** sunt definite **înainte** de design-ul tehnic. Acest workflow este ideal când:
- Ai cerințe clare de la stakeholders
- Funcționalitatea este nouă și nu există soluție tehnică predefinită
- Vrei să validezi cerințele înainte de a investi în design tehnic

### Structura unui Feature Spec

Un Feature Spec în Requirements-First constă din **3 fișiere principale**:

```
.kiro/specs/{feature-name}/
├── requirements.md    # Nivel înalt: User stories, acceptance criteria, properties
├── design.md          # Nivel tehnic: Algoritmi, arhitectură, API contracts
└── tasks.md           # Nivel implementare: Task breakdown, checklist
```

---

## Nivelurile de Abstractizare

### Nivel 1: Requirements.md (Nivel Înalt - Business + Funcțional)

**Scop:** Definește **CE** trebuie să facă sistemul din perspectiva utilizatorului și a business-ului.

**Conținut:**
- **User Stories**: Descrieri în limbaj natural ale nevoilor utilizatorilor
- **Acceptance Criteria**: Condiții măsurabile de succes
- **Correctness Properties**: Proprietăți formale de corectitudine (pentru Property-Based Testing)
- **Non-Functional Requirements**: Performanță, securitate, scalabilitate

**Audience:** Product owners, stakeholders, dezvoltatori

**Exemplu real din Hybrid Thesis Recommender:**

```markdown
### Requirement 4: Hybrid Ranking and Fusion

**User Story:** As a User, I want the best results from both semantic 
and keyword retrieval combined into a single ranked list, so that I get 
comprehensive and relevant recommendations.

#### Acceptance Criteria

1. WHEN results are available from both the Semantic_Retriever and the 
   Keyword_Retriever, THE Hybrid_Ranker SHALL merge the two result sets 
   using a weighted fusion strategy (such as Reciprocal Rank Fusion or 
   a configurable weighted sum of Scores).

2. THE Hybrid_Ranker SHALL produce a single ranked list of unique Articles 
   ordered by descending combined Score.

3. WHERE only one retriever returns results (due to fallback or empty results), 
   THE Hybrid_Ranker SHALL rank and return the available results without error.

4. THE Hybrid_Ranker SHALL deduplicate Articles that appear in both result sets, 
   retaining the higher combined Score.

5. THE System SHALL return at most Top-K Recommendations, where Top-K is 
   configurable and defaults to 10.

#### Correctness Properties

- P1: ∀ result ∈ results: 0 ≤ result.score ≤ 1
- P2: results are sorted: ∀ i < j: results[i].score ≥ results[j].score
- P3: No duplicates: ∀ i ≠ j: results[i].id ≠ results[j].id
- P4: |results| ≤ Top-K
```

**Caracteristici cheie:**
- ✅ Limbaj natural, ușor de înțeles
- ✅ Criterii măsurabile (SHALL, WHEN, WHERE)
- ✅ Proprietăți formale pentru testare automată
- ✅ Fără detalii de implementare

---

### Nivel 2: Design.md (Nivel Mediu-Scăzut - Tehnic)

**Scop:** Definește **CUM** va fi implementată funcționalitatea din punct de vedere tehnic.

**Conținut:**
- **Arhitectură tehnică**: Componente, module, clase
- **Algoritmi specifici**: Pseudocod, formule matematice
- **Structuri de date**: Formate, scheme
- **API Contracts**: Semnături de funcții, endpoint-uri
- **Diagrame**: Sequence diagrams, class diagrams, flowcharts
- **Considerații de implementare**: Edge cases, optimizări

**Audience:** Dezvoltatori, arhitecți software

**Exemplu real din Hybrid Thesis Recommender:**

```markdown
### Algorithm: Reciprocal Rank Fusion (RRF)

For each article appearing in multiple result lists:
  RRF_score = Σ (weight_source / (k + rank_in_source))
  where k = 60 (constant)

**Rationale:** RRF is robust to score scale differences between retrievers 
and naturally down-ranks items that appear only in low-ranked positions.

### Class Design

```python
class HybridRanker:
    def __init__(self, config: AppConfig):
        self.method = config.ranking_method  # "rrf" or "weighted_sum"
        self.weights = config.retriever_weights
        self.k = 60  # RRF constant
    
    def rank(self, results: Dict[str, List[Article]]) -> List[Article]:
        """Fuse and rank results from multiple retrievers."""
        if self.method == "rrf":
            return self._rrf_fusion(results)
        else:
            return self._weighted_sum(results)
    
    def _rrf_fusion(self, results: Dict[str, List[Article]]) -> List[Article]:
        """Apply Reciprocal Rank Fusion algorithm."""
        # Implementation details...
    
    def _deduplicate(self, articles: List[Article]) -> List[Article]:
        """Remove duplicates based on DOI or normalized title."""
        # Implementation details...
```

### Data Flow

```
Semantic Retriever → Raw Results (scored 0.0-1.0)
        ↓
Keyword Retriever → Raw Results (BM25 scores normalized)
        ↓
    Hybrid Ranker → Fused Results (RRF scores)
        ↓
    Deduplicator → Unique Results
        ↓
Content Verifier → Verified Results (with quality warnings)
        ↓
    Response → JSON to client
```

### API Contract

```python
def hybrid_rank(
    semantic_results: List[Article],
    keyword_results: List[Article],
    method: Literal["rrf", "weighted_sum"] = "rrf",
    top_k: int = 10
) -> List[Article]:
    """
    Fuse and rank results from multiple retrievers.
    
    Args:
        semantic_results: Articles from semantic retriever with scores
        keyword_results: Articles from keyword retriever with scores
        method: Fusion method ("rrf" or "weighted_sum")
        top_k: Maximum number of results to return
    
    Returns:
        Ranked list of unique articles, limited to top_k
    
    Ensures:
        - All scores in [0.0, 1.0]
        - Results sorted by descending score
        - No duplicate articles
        - len(result) <= top_k
    """
```
```

**Caracteristici cheie:**
- ✅ Algoritmi specifici cu formule matematice
- ✅ Structuri de date și clase
- ✅ Diagrame tehnice (sequence, flowchart)
- ✅ Pre/post-condiții pentru funcții
- ✅ Considerații de implementare

---

### Nivel 3: Tasks.md (Nivel Implementare)

**Scop:** Descompune design-ul tehnic în **pași concreți de implementare**.

**Conținut:**
- **Task breakdown**: Liste de task-uri cu sub-task-uri
- **Dependențe**: Ordinea de execuție
- **Checklist**: Progres tracking
- **Testing tasks**: Unit tests, property tests, integration tests

**Audience:** Dezvoltatori care implementează

**Exemplu real din Hybrid Thesis Recommender:**

```markdown
# Implementation Tasks

## Task 1: Implement HybridRanker Class

- [ ] 1.1 Create HybridRanker class structure
  - [ ] 1.1.1 Define __init__ with config parameter
  - [ ] 1.1.2 Add method selection logic (rrf vs weighted_sum)
  - [ ] 1.1.3 Store weights and k constant

- [ ] 1.2 Implement RRF fusion method
  - [ ] 1.2.1 Create _rrf_fusion() method
  - [ ] 1.2.2 Aggregate articles from all sources
  - [ ] 1.2.3 Compute RRF score for each article
  - [ ] 1.2.4 Sort by descending RRF score

- [ ] 1.3 Implement weighted sum method
  - [ ] 1.3.1 Create _weighted_sum() method
  - [ ] 1.3.2 Normalize scores from each retriever
  - [ ] 1.3.3 Apply configurable weights
  - [ ] 1.3.4 Compute final weighted score

- [ ] 1.4 Implement deduplication
  - [ ] 1.4.1 Create _deduplicate() method
  - [ ] 1.4.2 Check for duplicate DOIs
  - [ ] 1.4.3 Check for duplicate normalized titles
  - [ ] 1.4.4 Retain article with higher score

- [ ] 1.5 Apply Top-K cutoff
  - [ ] 1.5.1 Limit results to top_k parameter
  - [ ] 1.5.2 Ensure default value of 10

## Task 2: Write Property-Based Tests

- [ ] 2.1 Test score bounds property
  - [ ] 2.1.1 Generate random article lists with Hypothesis
  - [ ] 2.1.2 Assert all scores in [0.0, 1.0]
  - [ ] 2.1.3 Test with empty inputs
  - [ ] 2.1.4 Test with single-source inputs

- [ ] 2.2 Test sorting order property
  - [ ] 2.2.1 Generate random article lists
  - [ ] 2.2.2 Assert results[i].score >= results[i+1].score
  - [ ] 2.2.3 Test with duplicate scores

- [ ] 2.3 Test no duplicates property
  - [ ] 2.3.1 Generate lists with intentional duplicates
  - [ ] 2.3.2 Assert all article IDs are unique
  - [ ] 2.3.3 Test DOI-based deduplication
  - [ ] 2.3.4 Test title-based deduplication

- [ ] 2.4 Test Top-K limit property
  - [ ] 2.4.1 Generate large result sets
  - [ ] 2.4.2 Assert len(results) <= top_k
  - [ ] 2.4.3 Test with top_k = 0, 1, 10, 100

## Task 3: Integration Testing

- [ ] 3.1 Test with real retrievers
  - [ ] 3.1.1 Mock Semantic_Retriever
  - [ ] 3.1.2 Mock Keyword_Retriever
  - [ ] 3.1.3 Test full pipeline
  - [ ] 3.1.4 Verify response format

- [ ] 3.2 Test fallback scenarios
  - [ ] 3.2.1 Test semantic-only fallback
  - [ ] 3.2.2 Test keyword-only fallback
  - [ ] 3.2.3 Test empty results handling
```

**Caracteristici cheie:**
- ✅ Task-uri granulare, acționabile
- ✅ Sub-task-uri cu dependențe clare
- ✅ Checkbox-uri pentru tracking progres
- ✅ Include testing tasks
- ✅ Mapare directă la design.md

---

## Exemplu Complet: Hybrid Ranking System

Să urmărim un feature complet prin toate cele 3 niveluri:

### 📋 requirements.md (Extras)

```markdown
## Requirement 4: Hybrid Ranking and Fusion

**User Story:** As a User, I want the best results from both semantic 
and keyword retrieval combined into a single ranked list.

**Acceptance Criteria:**
- AC1: System merges semantic + keyword results using RRF or weighted sum
- AC2: Results are deduplicated by DOI or title
- AC3: Final list is sorted by descending score
- AC4: Response time < 2 seconds
- AC5: Maximum Top-K results returned (default: 10)

**Correctness Properties:**
- P1: Score bounds: ∀ r ∈ results: 0 ≤ r.score ≤ 1
- P2: Sorted order: ∀ i < j: results[i].score ≥ results[j].score
- P3: No duplicates: ∀ i ≠ j: results[i].id ≠ results[j].id
- P4: Top-K limit: |results| ≤ Top-K

**Non-Functional Requirements:**
- NFR1: Ranking must complete in < 100ms for 100 articles
- NFR2: Memory usage < 50MB for ranking operation
- NFR3: Configurable weights without code changes
```

### 🏗️ design.md (Extras)

```markdown
## Design: Hybrid Ranking System

### Algorithm Selection

**Reciprocal Rank Fusion (RRF)** chosen for:
- Robustness to score scale differences
- No need for score normalization
- Well-studied in IR literature

**Formula:**
```
RRF_score(article) = Σ (weight_source / (k + rank_in_source))
where:
  - k = 60 (standard RRF constant)
  - weight_source = configurable per retriever
  - rank_in_source = position in that retriever's results (1-indexed)
```

### Component Architecture

```
┌─────────────────────────────────────┐
│       HybridRanker                  │
├─────────────────────────────────────┤
│ + rank(results, method, top_k)      │
│ - _rrf_fusion(results)              │
│ - _weighted_sum(results)            │
│ - _deduplicate(articles)            │
│ - _apply_top_k(articles, k)         │
└─────────────────────────────────────┘
```

### Data Structures

```python
@dataclass
class Article:
    id: str
    title: str
    abstract: str
    score: float  # Always in [0.0, 1.0]
    source: str   # "semantic" | "keyword" | "web"
    doi: Optional[str] = None
    
@dataclass
class RankedResults:
    articles: List[Article]
    method_used: str
    total_time_ms: float
    fallback_notices: List[str]
```

### Deduplication Strategy

1. **Primary key**: DOI (if available)
2. **Secondary key**: Normalized title (lowercase, remove punctuation)
3. **Conflict resolution**: Keep article with higher score

### Edge Cases

- **Empty input**: Return empty list
- **Single source**: Pass through without fusion
- **All duplicates**: Return single copy with max score
- **Tie scores**: Preserve original order (stable sort)
```

### ✅ tasks.md (Extras)

```markdown
## Implementation Tasks

- [x] 1. Implement HybridRanker class
  - [x] 1.1 Class structure with config
  - [x] 1.2 RRF fusion method
  - [x] 1.3 Weighted sum method
  - [x] 1.4 Deduplication logic
  - [x] 1.5 Top-K cutoff

- [x] 2. Write property-based tests
  - [x] 2.1 Property: score bounds [0,1]
  - [x] 2.2 Property: sorted order
  - [x] 2.3 Property: no duplicates
  - [x] 2.4 Property: Top-K limit

- [x] 3. Integration tests
  - [x] 3.1 Test with real retrievers
  - [x] 3.2 Test fallback scenarios
  - [x] 3.3 Test performance (< 100ms)

- [x] 4. Documentation
  - [x] 4.1 API documentation
  - [x] 4.2 Algorithm explanation
  - [x] 4.3 Configuration guide
```

---

## Trasabilitate între Niveluri

Unul dintre beneficiile majore ale SDD este **trasabilitatea completă** de la cerință la cod.

### Tabel de Trasabilitate

| User Story | Acceptance Criteria | Property | Design Component | Implementation | Test |
|------------|-------------------|----------|------------------|----------------|------|
| US4: Combined results | AC1: RRF fusion | P1: Score ∈ [0,1] | `HybridRanker._rrf_fusion()` | `app/rankers/hybrid.py:45` | `test_score_bounds()` |
| US4: Combined results | AC2: Deduplicate | P3: Unique IDs | `HybridRanker._deduplicate()` | `app/rankers/hybrid.py:78` | `test_no_duplicates()` |
| US4: Combined results | AC3: Sorted | P2: Descending order | `HybridRanker.rank()` | `app/rankers/hybrid.py:32` | `test_sorted_order()` |
| US4: Combined results | AC5: Top-K limit | P4: |results| ≤ K | `HybridRanker._apply_top_k()` | `app/rankers/hybrid.py:95` | `test_top_k_limit()` |

### Mapare Completă

```
requirements.md
    │
    ├─ User Story 4: "Combined results"
    │       │
    │       ├─ Acceptance Criteria AC1: "RRF fusion"
    │       │       │
    │       │       └─ design.md
    │       │               │
    │       │               ├─ Algorithm: "RRF formula"
    │       │               ├─ Component: "HybridRanker._rrf_fusion()"
    │       │               │
    │       │               └─ tasks.md
    │       │                       │
    │       │                       ├─ Task 1.2: "Implement RRF fusion"
    │       │                       │       │
    │       │                       │       └─ Code: app/rankers/hybrid.py:45
    │       │                       │
    │       │                       └─ Task 2.1: "Test score bounds"
    │       │                               │
    │       │                               └─ Test: tests/test_ranker.py:test_score_bounds()
    │       │
    │       └─ Property P1: "Score ∈ [0,1]"
    │               │
    │               └─ Verified by: test_score_bounds() using Hypothesis
```

---

## Property-Based Testing Integration

Un aspect unic al SDD este integrarea **Property-Based Testing (PBT)** direct în requirements.

### De la Property la Test

**În requirements.md:**
```markdown
**Correctness Properties:**
- P1: ∀ result ∈ results: 0 ≤ result.score ≤ 1
- P2: results are sorted: ∀ i < j: results[i].score ≥ results[j].score
- P3: No duplicates: ∀ i ≠ j: results[i].id ≠ results[j].id
```

**În tasks.md:**
```markdown
- [ ] 2.1 Test score bounds property
  - [ ] 2.1.1 Generate random article lists with Hypothesis
  - [ ] 2.1.2 Assert all scores in [0.0, 1.0]
```

**În cod (tests/test_ranker.py):**
```python
from hypothesis import given, strategies as st
import pytest

@given(
    semantic_results=st.lists(
        st.builds(Article, 
                  score=st.floats(min_value=0.0, max_value=1.0)),
        max_size=50
    ),
    keyword_results=st.lists(
        st.builds(Article, 
                  score=st.floats(min_value=0.0, max_value=1.0)),
        max_size=50
    )
)
def test_score_bounds_property(semantic_results, keyword_results, ranker):
    """Property P1: All scores must be in [0.0, 1.0]"""
    results = ranker.rank({
        "semantic": semantic_results,
        "keyword": keyword_results
    })
    
    for article in results:
        assert 0.0 <= article.score <= 1.0, \
            f"Score {article.score} out of bounds for article {article.id}"

@given(
    results=st.lists(
        st.builds(Article, score=st.floats(min_value=0.0, max_value=1.0)),
        min_size=2,
        max_size=100
    )
)
def test_sorted_order_property(results, ranker):
    """Property P2: Results must be sorted by descending score"""
    ranked = ranker.rank({"semantic": results})
    
    for i in range(len(ranked) - 1):
        assert ranked[i].score >= ranked[i+1].score, \
            f"Results not sorted at index {i}: {ranked[i].score} < {ranked[i+1].score}"
```

### Beneficii PBT în SDD

- ✅ **Specificații executabile**: Properties din requirements devin teste automate
- ✅ **Acoperire exhaustivă**: Hypothesis generează sute de cazuri de test
- ✅ **Detectare edge cases**: Găsește bug-uri pe care testele manuale le ratează
- ✅ **Documentație vie**: Testele demonstrează proprietățile sistemului
- ✅ **Regresie prevention**: Properties rămân valide pe toată durata de viață

---

## Beneficiile Requirements-First

### 1. Validare Timpurie

**Înainte de a scrie cod**, stakeholders pot valida că cerințele sunt corecte:
- User stories sunt clare și complete?
- Acceptance criteria sunt măsurabile?
- Properties acoperă toate invarianții?

### 2. Trasabilitate Completă

Fiecare linie de cod poate fi trasată înapoi la o cerință de business:
```
Cod → Task → Design → Acceptance Criteria → User Story
```

### 3. Documentație Automată

Spec-urile servesc ca documentație:
- **requirements.md**: Documentație pentru stakeholders
- **design.md**: Documentație tehnică pentru dezvoltatori
- **tasks.md**: Ghid de implementare

### 4. Testare Sistematică

Properties din requirements devin teste automate:
- Property-based tests cu Hypothesis
- Unit tests pentru fiecare component
- Integration tests pentru fluxuri complete

### 5. Mentenanță Ușoară

Când cerințele se schimbă:
1. Actualizezi requirements.md
2. Actualizezi design.md
3. Actualizezi tasks.md
4. Implementezi modificările
5. Testele PBT validează că properties sunt încă respectate

---

## Comparație: Requirements-First vs Design-First

| Aspect | Requirements-First | Design-First |
|--------|-------------------|--------------|
| **Punct de start** | User stories, business needs | Soluție tehnică existentă |
| **Flux** | Requirements → Design → Tasks | Design → Requirements → Tasks |
| **Când folosești** | Feature nou, cerințe clare de la stakeholders | Refactoring, soluție tehnică cunoscută |
| **Avantaj principal** | Validare business timpurie, trasabilitate clară | Rapid pentru soluții tehnice cunoscute |
| **Dezavantaj** | Mai mult timp inițial pentru requirements | Risc de a implementa soluția greșită |
| **Ideal pentru** | Proiecte noi, features complexe | Migrări tehnice, optimizări |
| **Exemplu** | Hybrid Ranking System (nou feature) | Migrare de la BM25 la Elasticsearch |

### Când să folosești Requirements-First?

✅ **DA** - Folosește Requirements-First când:
- Construiești un feature complet nou
- Ai stakeholders care trebuie să valideze cerințele
- Cerințele de business sunt clare, dar soluția tehnică nu
- Vrei trasabilitate completă de la business la cod
- Proiectul este complex și necesită documentație detaliată

❌ **NU** - Nu folosi Requirements-First când:
- Faci refactoring tehnic fără schimbări funcționale
- Soluția tehnică este evidentă și bine cunoscută
- Timpul este critic și cerințele sunt triviale
- Lucrezi solo pe un prototip rapid

---

## Concluzie

**Nivelurile de specificații în SDD** oferă o structură clară pentru transformarea ideilor abstracte în cod funcțional:

1. **requirements.md**: CE vrem (business + funcțional)
2. **design.md**: CUM implementăm (tehnic)
3. **tasks.md**: PAȘI concreți (implementare)
4. **Cod + Tests**: Execuție + verificare

**Requirements-First workflow** asigură că:
- ✅ Cerințele sunt validate înainte de implementare
- ✅ Fiecare linie de cod este trasabilă la o cerință
- ✅ Properties de corectitudine sunt testate automat
- ✅ Documentația este întotdeauna actualizată
- ✅ Mentenanța este simplificată

În **Hybrid Thesis Recommender**, această abordare a permis dezvoltarea sistematică a tuturor feature-urilor majore (Hybrid Ranking, Content Verification, Feedback System, Multilingual Support) cu trasabilitate completă și acoperire exhaustivă cu teste.

---

## Referințe

- Spec-Driven Development Methodology: `theory_files/SPEC_DRIVEN_DEVELOPMENT.md`
- Hybrid Thesis Recommender Spec: `.kiro/specs/hybrid-thesis-recommender/`
- Property-Based Testing cu Hypothesis: https://hypothesis.readthedocs.io/
- Reciprocal Rank Fusion: Cormack, G. V., Clarke, C. L., & Buettcher, S. (2009)
