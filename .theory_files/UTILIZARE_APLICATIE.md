# Ghid de Utilizare — Hybrid Thesis Recommender

## 1. Pornirea Aplicației

### 1.1 Cerințe Prealabile

- Python 3.10+ instalat
- Dependențele instalate: `pip install -r requirements.txt`
- Modelul de embeddings se descarcă automat la prima rulare (~420MB)

### 1.2 Pornire Server

```bash
# Pornire standard (http://localhost:5000)
python -m app.main serve

# Cu debug mode (auto-reload la modificări cod)
python -m app.main serve --debug

# Pe alt port / accesibil din rețea
python -m app.main serve --host 0.0.0.0 --port 8080
```

### 1.3 Accesare

Deschide un browser la adresa: **http://localhost:5000**

---

## 2. Căutare de Recomandări

### 2.1 Pasul 1: Introducerea Query-ului

În panoul din stânga, completează:

| Câmp | Obligatoriu | Descriere |
|------|:-----------:|-----------|
| **Titlul tezei** | ✅ | Titlul complet sau parțial (3-500 caractere) |
| **Rezumat** | ❌ | Abstractul tezei — îmbunătățește precizia |
| **Cuvinte cheie** | ❌ | Termeni separați prin virgulă |

**Exemple de query-uri:**
- `"Rețele neuronale pentru procesarea limbajului natural"`
- `"Hybrid recommender systems using deep learning"`
- `"Securitatea aplicațiilor web bazate pe microservicii"`

### 2.2 Pasul 2: Lansarea Căutării

- Click pe butonul **🔍 Caută**
- Apare un spinner de încărcare (1-3 secunde)
- Butonul se dezactivează pentru a preveni cereri duplicate

### 2.3 Pasul 3: Vizualizarea Rezultatelor

Rezultatele apar în panoul din dreapta, organizate pe **două tab-uri**:

#### Tab "Resurse Web"
- Pagini web relevante (bloguri, documentație, tutoriale)
- Surse: DuckDuckGo, Semantic Scholar, arXiv
- Fiecare card conține: titlu (link clickabil), snippet, scor, keywords

#### Tab "Articole"
- Articole academice din corpusul local
- Surse: baza de date indexată + API-uri academice
- Fiecare card conține: titlu, autori, an, abstract, DOI, scor

### 2.4 Pasul 4: Paginare

- Inițial se afișează **5 rezultate** per tab
- Click **"Încarcă mai multe"** pentru următoarele 5
- Paginarea e independentă per tab (poți încărca mai multe articole fără a afecta web)
- Când nu mai sunt rezultate: mesaj "Nu mai sunt articole/resurse de afișat"

---

## 3. Interpretarea Rezultatelor

### 3.1 Scorul de Relevanță

Fiecare rezultat are un **badge de scor** colorat:

| Culoare | Interval | Semnificație |
|---------|----------|-------------|
| 🟢 Verde | 0.7 – 1.0 | Foarte relevant |
| 🟠 Portocaliu | 0.4 – 0.7 | Moderat relevant |
| ⚪ Gri | 0.0 – 0.4 | Slab relevant |

Scorul combină:
- Similaritate semantică (înțelegerea sensului)
- Potrivire keywords (termeni exacți)
- Poziție în rezultatele web search

### 3.2 Badge-ul de Avertizare (⚠)

Dacă un rezultat are badge-ul **"⚠ Verificați conținutul"** (sau "⚠ Verify content"):
- Titlul pare relevant, dar conținutul (abstract/snippet) nu confirmă relevanța
- Posibil clickbait sau titlu înșelător
- Recomandare: verifică manual sursa înainte de a o cita

### 3.3 Tipul Resursei

| Badge | Semnificație |
|-------|-------------|
| **ARTICLE** (albastru) | Articol academic (din corpus sau API-uri) |
| **WEB** (verde) | Resursă web (blog, documentație, tutorial) |

---

## 4. Evaluarea Rezultatelor (Rating)

### 4.1 Cum Evaluezi

1. Sub fiecare card, vezi 5 stele (☆☆☆☆☆)
2. Hover pe o stea → se colorează progresiv
3. Click pe steaua dorită (1 = slab, 5 = excelent)
4. Rating-ul se salvează automat (fără buton extra)

### 4.2 Ce Înseamnă Stelele

| Stele | Semnificație |
|-------|-------------|
| ⭐ | Irelevant pentru teza mea |
| ⭐⭐ | Puțin relevant, nu ajută direct |
| ⭐⭐⭐ | Moderat util, informații de fundal |
| ⭐⭐⭐⭐ | Foarte util, voi cita/folosi |
| ⭐⭐⭐⭐⭐ | Esențial pentru teza mea |

### 4.3 Impactul Rating-urilor

- Rating-urile tale influențează recomandările viitoare
- Articolele cu media ≥ 4.0 primesc un boost subtil în ranking
- Alți utilizatori văd media și numărul de evaluări

---

## 5. Salvarea Articolelor

### 5.1 Salvare

- Pe fiecare card, click **"💾 Salvează"**
- Butonul devine verde ("Salvat ✓")
- Articolul e adăugat la colecția ta

### 5.2 Vizualizare Salvate

- Click pe butonul **"Vezi salvate"** din header
- Se deschide un modal cu toate articolele/resursele salvate
- Fiecare item poate fi eliminat din colecție

### 5.3 Persistență

- **Fără cont**: salvările sunt în browser (localStorage) — se pierd la ștergerea datelor
- **Cu cont**: salvările sunt pe server — accesibile de pe orice dispozitiv

---

## 6. Autentificare (Opțional)

### 6.1 Înregistrare

1. Click **"Autentificare"** din header
2. Click **"Înregistrează-te"**
3. Completează: username (min 3 chars), email, parolă (min 6 chars)
4. Click **"Înregistrare"**
5. Ești logat automat

### 6.2 Autentificare

1. Click **"Autentificare"** din header
2. Introdu username + parolă
3. Click **"Autentificare"**
4. Username-ul apare în header

### 6.3 Beneficii Cont

| Feature | Fără cont | Cu cont |
|---------|:---------:|:-------:|
| Căutare recomandări | ✅ | ✅ |
| Rating articole | ✅ (session) | ✅ (persistent) |
| Salvare articole | ✅ (localStorage) | ✅ (server) |
| Sincronizare dispozitive | ❌ | ✅ |
| Istoric rating-uri | ❌ | ✅ |

### 6.4 Deconectare

- Click **"Deconectare"** din header
- Sesiunea se șterge, revii la modul guest

---

## 7. Schimbarea Limbii

### 7.1 Toggle Manual

- În header: click pe **RO** sau **EN**
- Toate textele UI se actualizează instant (fără reload)
- Preferința se salvează pentru vizitele viitoare

### 7.2 Detectare Automată

- La căutare, sistemul detectează limba query-ului
- Mesajele de eroare și notice-urile vin în limba detectată
- Rezultatele conțin articole în ambele limbi (cross-lingual)

### 7.3 Ce Se Schimbă

| Element | RO | EN |
|---------|----|----|
| Titlu formular | "Introduceți titlul tezei" | "Enter your thesis title" |
| Buton căutare | "Caută" | "Search" |
| Tab-uri | "Articole" / "Resurse Web" | "Articles" / "Web Resources" |
| Mesaje eroare | "Query-ul trebuie să aibă..." | "Query must be between..." |
| Rating label | "Utilitate" | "Usefulness" |
| Avertisment calitate | "⚠ Verificați conținutul" | "⚠ Verify content" |

---

## 8. Dark Mode

### 8.1 Activare

- Click pe iconița **🌙** din header
- Interfața trece instant pe fundal întunecat
- Iconița devine **☀** (click din nou pentru light mode)

### 8.2 Persistență

- Preferința se salvează în browser
- La următoarea vizită, tema se aplică automat

---

## 9. Pagina "Despre"

- Click pe butonul **"Despre"** din header
- Se deschide un modal cu:
  - Descrierea sistemului
  - Caracteristici principale (5 features)
  - Cum funcționează (4 pași)

---

## 10. Scenarii de Utilizare

### 10.1 Student la Început de Licență

**Scop**: Găsirea surselor inițiale pentru o temă nouă.

1. Introdu titlul tezei (chiar dacă e preliminar)
2. Verifică tab-ul **Resurse Web** — tutoriale, documentație, overview-uri
3. Verifică tab-ul **Articole** — papers fundamentale
4. Salvează cele mai relevante
5. Reformulează titlul și caută din nou pentru acoperire mai bună

### 10.2 Cercetător cu Temă Definită

**Scop**: Găsirea literaturii specifice și a lucrărilor recente.

1. Introdu titlul exact + abstract + keywords
2. Focus pe tab-ul **Articole** — papers cu DOI citabile
3. Evaluează cu stele (ajută la recomandări viitoare)
4. Folosește "Încarcă mai multe" pentru a explora mai adânc
5. Verifică badge-urile de avertizare — evită surse dubioase

### 10.3 Căutare Bilingvă

**Scop**: Găsirea surselor atât în română cât și în engleză.

1. Caută în română: "Sisteme de recomandare hibride"
2. Sistemul returnează articole în AMBELE limbi (cross-lingual)
3. Caută și în engleză: "Hybrid recommender systems"
4. Compară rezultatele — unele articole apar în ambele căutări

### 10.4 Verificarea Calității Surselor

**Scop**: Filtrarea surselor de calitate scăzută.

1. Caută normal
2. Observă badge-urile **⚠ Verificați conținutul**
3. Aceste surse au titlu relevant dar conținut posibil înșelător
4. Verifică manual URL-ul înainte de a cita
5. Sursele din domenii blocate (content farms) sunt deja excluse automat

---

## 11. Troubleshooting

### 11.1 Probleme Comune

| Problemă | Cauză | Soluție |
|----------|-------|---------|
| "Nu au fost găsite articole" | Corpus mic sau query prea specific | Reformulează mai general |
| "Nu au fost găsite resurse web" | DuckDuckGo rate limited | Așteaptă câteva minute |
| Spinner infinit | Timeout pe retriever | Reîncarcă pagina |
| Notice "Semantic retrieval unavailable" | Model nu s-a încărcat | Repornește serverul |
| Notice "Web retrieval unavailable" | Fără internet | Verifică conexiunea |
| Rating nu se salvează | Feedback store indisponibil | Verifică `data/feedback.db` |

### 11.2 Sfaturi pentru Rezultate Mai Bune

- **Titlu specific** > titlu generic ("Neural networks for Romanian NER" > "Neural networks")
- **Adaugă abstract** — crește dramatic precizia semantică
- **Adaugă keywords** — ajută BM25 să prindă termeni exacți
- **Caută în ambele limbi** — corpusul e majoritar EN, dar cross-lingual funcționează
- **Evaluează rezultatele** — feedback-ul îmbunătățește recomandările viitoare

---

## 12. Comenzi Rapide

| Acțiune | Cum |
|---------|-----|
| Căutare | Enter în câmpul titlu |
| Schimbare tab | Click pe "Articole" / "Resurse Web" |
| Schimbare limbă | Click RO / EN în header |
| Dark mode | Click 🌙 în header |
| Salvare articol | Click "💾 Salvează" pe card |
| Rating | Click pe steaua dorită |
| Vezi salvate | Click "Vezi salvate" în header |
| Despre | Click "Despre" în header |
