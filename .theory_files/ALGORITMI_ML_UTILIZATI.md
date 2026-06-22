# Algoritmii de Machine Learning Utilizați în Proiect

## 1. Contextul Utilizării ML în Sistem

Sistemul de recomandare dezvoltat nu antrenează modele de la zero, ci utilizează modele pre-antrenate și algoritmi clasici de regăsire a informației pentru a transforma textul unei interogări în recomandări relevante. Această abordare, denumită transfer learning, permite exploatarea cunoștințelor lingvistice acumulate de modele antrenate pe miliarde de texte, fără a necesita un corpus propriu de antrenare de dimensiuni similare.

Algoritmii ML intervin în trei puncte ale pipeline-ului:
1. **Reprezentarea semantică** — transformarea textului în vectori numerici (embeddings)
2. **Căutarea prin similaritate** — identificarea celor mai apropiați vectori din index
3. **Detecția calității** — compararea semantică între titlu și conținut pentru identificarea surselor înșelătoare

---

## 2. Sentence-Transformers: Modelul de Embeddings

### 2.1 Ce face

Modelul `paraphrase-multilingual-mpnet-base-v2` este o rețea neuronală de tip Transformer, antrenată prin tehnica de învățare contrastivă, care transformă orice text (propoziție, paragraf, titlu de articol) într-un vector dens de 768 de numere reale. Acest vector captează sensul semantic al textului — două texte cu semnificație similară vor produce vectori apropiați în spațiul vectorial, indiferent de limba în care sunt formulate.

### 2.2 Arhitectura

Modelul este bazat pe arhitectura MPNet (Masked and Permuted Pre-training for Language Understanding), care combină avantajele BERT (atenție bidirecțională) cu cele ale XLNet (permutation language modeling). Structura include:

- **Tokenizer** — descompune textul în sub-cuvinte (WordPiece) dintr-un vocabular de ~250.000 de tokeni, acoperind 50+ limbi
- **12 straturi Transformer** — fiecare strat aplică mecanismul de self-attention, care permite fiecărui token să „vadă" contextul tuturor celorlalte tokeni din propoziție
- **Pooling layer** — agregă reprezentările tuturor tokenilor într-un singur vector de 768 dimensiuni (mean pooling)
- **Normalizare L2** — vectorul final este normalizat la lungime unitară pentru a permite calculul direct al similarității cosinus prin produs scalar

### 2.3 Antrenarea (pre-training + fine-tuning)

Modelul a parcurs două faze de antrenare, ambele realizate de echipa sentence-transformers, nu de dezvoltatorul acestui proiect:

**Faza 1 — Pre-training (MPNet base):** Antrenare pe corpusuri masive de text (Wikipedia, BookCorpus) prin predicția cuvintelor mascate. Rezultatul: un model care „înțelege" structura limbii.

**Faza 2 — Fine-tuning contrastiv:** Antrenare pe perechi de propoziții (parafrazări) din multiple limbi. Modelul învață să producă vectori apropiați pentru texte cu același sens și vectori depărtați pentru texte cu sens diferit. Această fază este cea care face modelul util pentru căutarea semantică.

### 2.4 Utilizare în proiect

În codul aplicației, modelul este folosit în două locuri:

```python
# 1. Encodarea interogării utilizatorului (SemanticRetriever)
query_vector = model.encode("neural networks for NLP")  # → vector 768D

# 2. Verificarea calității (ContentVerifier)
title_vector = model.encode("Attention Is All You Need")
abstract_vector = model.encode("This paper proposes...")
mismatch = cosine_sim(query, title) - cosine_sim(query, abstract)
```

### 2.5 Proprietatea cross-linguală

O proprietate esențială pentru proiect este suportul multilingv. Deoarece modelul a fost antrenat pe perechi de texte din 50+ limbi, vectorii produși sunt aliniați lingvistic — o interogare în română („rețele neuronale") va fi apropiată vectorial de un articol în engleză ("neural networks") fără traducere explicită. Această proprietate elimină necesitatea unui sistem de traducere separat și permite căutarea bilingvă transparentă.

---

## 3. FAISS: Căutarea prin Similaritate Vectorială

### 3.1 Ce face

FAISS (Facebook AI Similarity Search) este o bibliotecă optimizată pentru găsirea celor mai apropiați vecini (nearest neighbors) într-un spațiu vectorial de înaltă dimensionalitate. Primește un vector de interogare și returnează cele mai similare K vectori din index, împreună cu scorurile de similaritate.

### 3.2 Algoritmul utilizat: IndexFlatIP (Brut Force cu Inner Product)

Proiectul folosește `IndexFlatIP` — căutare exactă prin produs scalar (inner product). Deoarece vectorii sunt normalizați L2, produsul scalar devine echivalent cu similaritatea cosinus:

$$\text{cosine\_sim}(a, b) = \frac{a \cdot b}{||a|| \cdot ||b||} = a \cdot b \quad \text{(dacă } ||a|| = ||b|| = 1\text{)}$$

Algoritmul compară vectorul interogării cu fiecare vector din index, calculând produsul scalar, și returnează Top-K rezultate sortate descrescător.

### 3.3 Complexitate

- **Timp:** O(n × d) unde n = număr articole, d = 768 dimensiuni
- **Spațiu:** O(n × d × 4 bytes) = 3KB per articol (float32)
- **La 33 articole:** <0.1ms — neglijabil
- **La 1.000.000 articole:** ~500ms — ar necesita trecerea la IndexIVFFlat (căutare aproximativă)

### 3.4 De ce FAISS și nu o bază de date vectorială

Alegerea FAISS față de alternative (ChromaDB, Pinecone, Qdrant) a fost motivată de:
- Zero dependențe externe — rulează local, fără server separat
- Performanță optimă pentru corpusuri mici-medii (<100.000 articole)
- Integrare nativă cu numpy și sentence-transformers
- Fără costuri de operare (alternativele cloud au pricing per query)

---

## 4. BM25: Regăsirea Lexicală

### 4.1 Ce face

BM25 (Best Matching 25) este un algoritm probabilistic de regăsire a informației care calculează relevanța unui document față de o interogare pe baza potrivirii exacte a cuvintelor. Spre deosebire de căutarea semantică care operează pe sens, BM25 operează pe termeni — dacă cuvântul „FAISS" apare în interogare și în document, BM25 îl consideră relevant.

### 4.2 Formula de scoring

Pentru fiecare termen q_i din interogare și document D:

$$\text{score}(D, Q) = \sum_{i=1}^{n} \text{IDF}(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot (1 - b + b \cdot \frac{|D|}{\text{avgdl}})}$$

Unde:
- **f(q_i, D)** = frecvența termenului q_i în documentul D
- **IDF(q_i)** = Inverse Document Frequency — penalizează cuvintele prea comune (ex: „the", „de")
- **|D|** = lungimea documentului (în cuvinte)
- **avgdl** = lungimea medie a documentelor din corpus
- **k_1 = 1.5** = controlează saturația frecvenței (după câte apariții ale unui termen beneficiul scade)
- **b = 0.75** = controlează normalizarea pe lungime (documentele lungi nu sunt favorizate automat)

### 4.3 Cum funcționează în proiect

1. **La ingestie:** Se tokenizează toate articolele din corpus (titlu + abstract + keywords) și se construiește un index inversat (termen → lista documentelor care îl conțin)
2. **La interogare:** Se tokenizează query-ul, se calculează scorul BM25 pentru fiecare document din corpus, se returnează Top-K
3. **Indexul e serializat:** Salvat ca fișier pickle (`bm25.pkl`) pentru a nu fi recalculat la fiecare pornire a serverului

### 4.4 Complementaritate cu căutarea semantică

BM25 și căutarea semantică acoperă cazuri diferite:

| Scenariu | BM25 | Semantic |
|----------|------|----------|
| Termenul exact „FAISS" apare în articol | ✅ Găsește | ❌ Poate rata |
| Interogare „rețele neuronale" → articol „neural networks" | ❌ Nu găsește (limbi diferite) | ✅ Găsește (cross-lingual) |
| Concept similar dar terminologie diferită | ❌ Nu găsește | ✅ Găsește |
| Cuvânt-cheie foarte specific (ex: „BM25Okapi") | ✅ Găsește exact | ⚠️ Poate confunda cu concepte similare |

Această complementaritate este motivul pentru care sistemul folosește ambele metode simultan, fuzionate prin RRF.

---

## 5. Reciprocal Rank Fusion (RRF): Algoritmul de Fuziune

### 5.1 Ce face

RRF este un algoritm de fuziune tardivă (late fusion) care combină mai multe liste de rezultate ordonate într-o singură listă unificată. Nu necesită calibrarea scorurilor între surse diferite — funcționează exclusiv pe baza rangurilor.

### 5.2 Formula

$$\text{RRF}(d) = \sum_{r \in R} \frac{w_r}{k + \text{rank}_r(d)}$$

Unde:
- **d** = un document
- **R** = setul de liste de rezultate (semantic, keyword, academic)
- **w_r** = ponderea listei r (semantic_weight = 0.6, keyword_weight = 0.4)
- **k = 60** = constantă de amortizare (standard în literatură)
- **rank_r(d)** = poziția documentului d în lista r (1-indexed)

### 5.3 De ce RRF și nu suma ponderată a scorurilor

Suma ponderată directă a scorurilor (weighted sum) are o problemă fundamentală: scorurile din surse diferite nu sunt comparabile. Un scor BM25 de 15.3 nu are aceeași semnificație cu un scor cosinus de 0.87. Ar necesita o etapă de normalizare care introduce parametri suplimentari și poate distorsiona rezultatele.

RRF elimină această problemă prin operarea exclusiv pe ranguri, nu pe scoruri. Un document pe locul 1 în ambele liste va primi un scor RRF mai mare decât unul pe locul 1 într-o singură listă și locul 20 în cealaltă, indiferent de valorile absolute ale scorurilor originale.

### 5.4 Proprietatea scale-free

RRF este scale-free: nu depinde de distribuția sau magnitudinea scorurilor individuale. Aceasta este proprietatea critică care permite fuzionarea rezultatelor din surse eterogene (FAISS cu scoruri [0,1], BM25 cu scoruri [0, 50], API-uri academice cu scoruri arbitrare) fără calibrare prealabilă.

---

## 6. Detectarea Calității prin Similaritate Cosinus

### 6.1 Ce face

ContentVerifier folosește modelul de embeddings pentru a detecta articolele de tip clickbait — articole al căror titlu sugerează un conținut pe care abstractul nu îl confirmă.

### 6.2 Algoritmul

1. Encodează interogarea → query_embedding
2. Pentru fiecare articol:
   - Encodează titlul → title_embedding
   - Encodează abstractul → content_embedding
   - Calculează title_sim = cosine_similarity(query_embedding, title_embedding)
   - Calculează content_sim = cosine_similarity(query_embedding, content_embedding)
   - mismatch = title_sim - content_sim
3. Dacă mismatch > threshold (0.3):
   - Scorul articolului este penalizat: quality_score = score × (1 - mismatch)
   - Se adaugă un avertisment localizat („⚠ Verificați conținutul")
4. Dacă quality_score < min_score → articolul este exclus complet

### 6.3 Intuiția

Un articol de calitate bună are titlul aliniat cu conținutul. Dacă titlul este foarte similar cu interogarea (title_sim mare) dar abstractul nu este (content_sim mic), înseamnă că titlul „promite" ceva ce conținutul nu livrează — indicator de clickbait sau conținut irelevant.

---

## 7. Detectarea Limbii (langdetect + langid)

### 7.1 Ce face

Modulul LanguageDetector determină automat dacă interogarea utilizatorului este în română sau engleză, pentru a adapta mesajele din interfață și, opțional, strategia de căutare web.

### 7.2 Algoritmul (langdetect)

Biblioteca langdetect folosește un clasificator Naive Bayes antrenat pe profiluri de n-grame de caractere. Pentru fiecare limbă, există un profil statistic al secvențelor de 1-3 caractere cele mai frecvente. Textul de intrare este descompus în n-grame, iar probabilitatea fiecărei limbi este calculată bayesian.

Exemplu: secvențele „ții", „ șt", „ează" au probabilitate ridicată în profilul limbii române, deci un text cu aceste secvențe va fi clasificat ca „ro".

### 7.3 Fallback

Dacă textul e prea scurt sau ambiguu (ex: un singur cuvânt tehnic în engleză), langdetect poate returna rezultate inconsistente. De aceea, sistemul folosește și langid ca a doua opinie și aplică un fallback la limba engleză dacă detectarea eșuează.

---

## 8. Rezumat: Unde Intervine ML în Pipeline

| Etapa | Algoritm ML | Input | Output | Latență |
|-------|-------------|-------|--------|---------|
| Detectare limbă | Naive Bayes (n-grame) | Text interogare | „ro" sau „en" | ~5ms |
| Encodare interogare | Transformer (MPNet) | Text interogare | Vector 768D | ~50ms |
| Căutare semantică | FAISS (Inner Product) | Vector query + Index | Top-K articole + scoruri | <0.1ms |
| Căutare lexicală | BM25 (probabilistic) | Tokeni query + Index inversat | Top-K articole + scoruri | ~0.5ms |
| Fuziune rezultate | RRF (rank-based) | Liste ordonate | Listă unificată | ~0.1ms |
| Verificare calitate | Cosine Similarity pe embeddings | Embeddings titlu + abstract | Mismatch score + warnings | ~189ms |

Toate componentele ML operează la inferență (nu antrenare) — modelele sunt pre-antrenate, indexurile sunt pre-calculați, iar la runtime se execută doar forward pass și operații vectoriale.
