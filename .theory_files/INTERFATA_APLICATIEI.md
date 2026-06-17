# Capitolul: Interfața Aplicației

## 1. Prezentare Generală

Interfața web a sistemului Hybrid Thesis Recommender este implementată fără framework frontend — folosind **HTML5 semantic**, **CSS3 cu variabile custom** (theming), și **TypeScript strict** compilat în JavaScript ES2020. Aplicația este servită de Flask din același origin ca API-ul REST.

### Principii de Design

- **Fără framework** — control complet, zero overhead, fără build complex
- **Responsive** — funcționează pe desktop și mobile (CSS Grid + media queries)
- **Accesibilitate** — ARIA labels, keyboard navigation, semantic HTML
- **Bilingv** — interfață completă în română și engleză, switch instant
- **Dark mode** — temă întunecată cu persistență preferință
- **Progressive enhancement** — funcționează fără JavaScript pentru structură de bază

---

## 2. Arhitectura Frontend

### 2.1 Structura Fișierelor

```
static/
├── index.html          # Pagina principală (HTML5 semantic)
├── style.css           # Stiluri cu CSS custom properties
├── tsc logo.png        # Logo aplicație
├── src/                # Surse TypeScript
│   ├── types.ts        # Interfețe și tipuri (bazate pe OpenAPI spec)
│   ├── api.ts          # Client API (fetch wrapper-e tipizate)
│   └── app.ts          # Logica aplicației (DOM, events, state)
└── dist/               # JavaScript compilat (ES2020 modules)
    ├── api.js
    ├── app.js
    └── types.js
```

### 2.2 Fluxul de Date

```
User Action (click, submit, toggle)
        │
        ▼
┌─────────────────────┐
│  app.ts             │  Event handlers, DOM manipulation
│  (Application Logic)│  State management (SessionStorage)
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  api.ts             │  fetch() calls tipizate
│  (API Client)       │  Error handling, fallback localStorage
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Flask Backend      │  POST /recommend, POST /feedback, etc.
│  (Same Origin)      │
└─────────┬───────────┘
          │
          ▼
    JSON Response → DOM Update (render cards, badges, ratings)
```

---

## 3. Layout și Componente UI

### 3.1 Layout Two-Column

```
┌──────────────────────────────────────────────────────────────────┐
│  HEADER: Logo | Titlu | Despre | Salvate | Auth | RO|EN | 🌙    │
├────────────────────┬─────────────────────────────────────────────┤
│                    │                                             │
│  LEFT COLUMN       │  RIGHT COLUMN                              │
│  (sticky)          │                                             │
│                    │  ┌─────────────────────────────────────┐   │
│  ┌──────────────┐  │  │  TABS: [Resurse Web] [Articole]    │   │
│  │ Titlu teză * │  │  └─────────────────────────────────────┘   │
│  │              │  │                                             │
│  │ Rezumat      │  │  ┌─────────────────────────────────────┐   │
│  │ (opțional)   │  │  │  Result Card                        │   │
│  │              │  │  │  ┌─ Title ──────── Score Badge ──┐  │   │
│  │ Cuvinte cheie│  │  │  │  Authors | Year | DOI         │  │   │
│  │ (opțional)   │  │  │  │  Abstract snippet...          │  │   │
│  │              │  │  │  │  [Keywords] [Tags]             │  │   │
│  │ [🔍 Caută]   │  │  │  │  ⭐⭐⭐⭐☆  (4.2 avg, 12 ratings)│  │   │
│  └──────────────┘  │  │  │  [💾 Salvează]                 │  │   │
│                    │  │  └────────────────────────────────┘  │   │
│                    │  │                                       │   │
│                    │  │  ... more cards ...                   │   │
│                    │  │                                       │   │
│                    │  │  [Încarcă mai multe]                  │   │
│                    │  └─────────────────────────────────────────┘   │
│                    │                                             │
├────────────────────┴─────────────────────────────────────────────┤
│  FOOTER: Thesis Sources Recommender — UPB                        │
└──────────────────────────────────────────────────────────────────┘
```

### 3.2 Componente Principale

| Componentă | Descriere |
|------------|-----------|
| **Header** | Logo, titlu, butoane acțiuni (About, Saved, Auth, Lang, Theme) |
| **Form Section** | Input titlu (obligatoriu), textarea abstract, input keywords |
| **Tabs** | Navigare între "Resurse Web" și "Articole" cu contoare |
| **Result Cards** | Carduri cu metadata, scor, rating, save |
| **Loading Spinner** | Indicator vizual în timpul request-ului |
| **Error Container** | Mesaje de eroare inline (fără redirect) |
| **Notices** | Avertismente sistem (retriever indisponibil) |
| **Modals** | About, Saved Items, Authentication (Login/Register) |
| **Pagination** | "Încarcă mai multe" per tab (offset-based) |

---

## 4. Sistem de Teme (Theming)

### 4.1 CSS Custom Properties

Întreaga interfață folosește **variabile CSS** pentru culori, umbre, raze, fonturi:

```css
:root {
  --color-bg:           #f4f4f4;
  --color-surface:      #ffffff;
  --color-primary:      #c7410e;
  --color-text:         #242729;
  --color-text-muted:   #6a737c;
  --color-star-filled:  #c7410e;
  --color-error:        #d1383d;
  /* ... 40+ variabile */
}

[data-theme="dark"] {
  --color-bg:           #1c1c1c;
  --color-surface:      #2d2d2d;
  --color-primary:      #f48024;
  --color-text:         #e4e6e8;
  /* ... override-uri dark mode */
}
```

### 4.2 Schimbare Temă

- Toggle via butonul 🌙/☀ din header
- Persistență în `localStorage` (cheia `theme`)
- Aplicare: `document.documentElement.setAttribute('data-theme', 'dark')`
- Tranziție smooth: `transition: 150ms ease` pe toate proprietățile

### 4.3 Paletă de Culori

| Scop | Light Mode | Dark Mode |
|------|-----------|-----------|
| Background | `#f4f4f4` | `#1c1c1c` |
| Surface (cards) | `#ffffff` | `#2d2d2d` |
| Primary (accent) | `#c7410e` (roșu-portocaliu) | `#f48024` (portocaliu) |
| Text | `#242729` | `#e4e6e8` |
| Text muted | `#6a737c` | `#9fa6ad` |
| Success | `#5eba7d` | `#5eba7d` |
| Error | `#d1383d` | `#e74c3c` |

---

## 5. Internaționalizare (i18n)

### 5.1 Mecanism

Toate textele UI au atributul `data-i18n`:

```html
<h2 data-i18n="form_heading">Introduceți titlul tezei</h2>
<button data-i18n="btn_submit">Caută</button>
```

La schimbarea limbii, JavaScript parcurge toate elementele cu `data-i18n` și le actualizează textul din dicționarul de traduceri.

### 5.2 Limbi Suportate

| Cheie | Română | English |
|-------|--------|---------|
| `form_heading` | Introduceți titlul tezei | Enter your thesis title |
| `btn_submit` | Caută | Search |
| `heading_articles` | Articole | Articles |
| `heading_web` | Resurse Web | Web Resources |
| `no_articles` | Nu au fost găsite articole... | No sufficiently relevant articles... |
| `label_usefulness` | Utilitate | Usefulness |
| `btn_save` | Salvează | Save |
| `btn_load_more` | Încarcă mai multe | Load more |

Total: **50+ chei de traducere** acoperind toate textele vizibile.

### 5.3 Detectare Automată

- La prima vizită: limba se setează pe baza răspunsului API (`query_language`)
- Toggle manual: RO | EN în header
- Persistență: `localStorage`
- Schimbare instant (fără reload pagină)

---

## 6. Carduri de Rezultate

### 6.1 Card Articol

```
┌─────────────────────────────────────────────────────────────┐
│  Attention Is All You Need                                  │
│  ┌────────┐ ┌──────────────┐ ┌──────────────────────────┐  │
│  │ARTICLE │ │ Score: 0.87  │ │ ⚠ Verificați conținutul  │  │
│  └────────┘ └──────────────┘ └──────────────────────────┘  │
│                                                             │
│  Vaswani, A. • Shazeer, N. • 2017 • DOI: 10.48550/...     │
│                                                             │
│  The dominant sequence transduction models are based on     │
│  complex recurrent or convolutional neural networks...      │
│                                                             │
│  [transformers] [attention] [neural networks]               │
│                                                             │
│  ⭐⭐⭐⭐☆  Utilitate    4.2 medie (12 evaluări)             │
│  [💾 Salvează]                                              │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Card Resursă Web

```
┌─────────────────────────────────────────────────────────────┐
│  Introduction to Transformer Architecture                    │
│  ┌─────┐ ┌──────────────┐                                  │
│  │ WEB │ │ Score: 0.95  │                                  │
│  └─────┘ └──────────────┘                                  │
│                                                             │
│  https://example.com/transformers-guide                     │
│                                                             │
│  A comprehensive guide to understanding the transformer     │
│  architecture and its applications in NLP...                │
│                                                             │
│  [deep learning] [NLP] [architecture]                       │
│                                                             │
│  ⭐⭐⭐⭐⭐  Utilitate    4.8 medie (5 evaluări)              │
│  [💾 Salvează]                                              │
└─────────────────────────────────────────────────────────────┘
```

### 6.3 Elemente Card

| Element | Descriere |
|---------|-----------|
| **Titlu** | Link clickabil (DOI/URL dacă disponibil) |
| **Badge tip** | "ARTICLE" (albastru) sau "WEB" (verde) |
| **Badge scor** | Colorat: verde (>0.7), portocaliu (0.4-0.7), gri (<0.4) |
| **Badge warning** | Galben/amber, apare doar dacă `quality_warning` e setat |
| **Meta** | Autori, an, DOI (articole) sau URL (web) |
| **Snippet** | Abstract trunchiat (300 chars) sau snippet pagină |
| **Keywords** | Tag-uri cu fundal gri |
| **Rating** | 5 stele interactive + media + count |
| **Save** | Buton salvare (toggle saved/unsaved) |

---

## 7. Sistem de Rating

### 7.1 Interacțiune

1. User hover pe stele → highlight vizual (stele se colorează progresiv)
2. User click pe steaua N → trimite rating N la backend
3. `POST /feedback` asincron (fără reload)
4. Confirmarea apare inline ("Rating salvat")
5. Media și count se actualizează

### 7.2 Persistență

- **User autentificat**: rating salvat pe server (legat de user_id)
- **User guest**: rating salvat pe server (legat de session_id din SessionStorage)
- La re-render card: `GET /feedback/{item_id}?session_id=...` pre-populează steaua

### 7.3 Feedback Signal

Rating-urile influențează recomandările viitoare:
- Articole cu media ≥ 4.0 primesc boost în ranking
- Efect subtil (boost 0.1) — nu domină semnalul de retrieval

---

## 8. Paginare

### 8.1 Mecanism

Paginare **offset-based** independentă per tab:

```typescript
// State per tab
displayedArticles: number;     // câte articole sunt afișate
displayedWebResources: number; // câte resurse web sunt afișate
hasMoreArticles: boolean;
hasMoreWebResources: boolean;
```

### 8.2 Flux

1. Prima cerere: `POST /recommend {title, offset: 0, type: "both"}`
2. Se afișează primele 5 rezultate per tab
3. Click "Încarcă mai multe" → `POST /recommend {title, offset: 5, type: "articles"}`
4. Rezultatele noi se adaugă la lista existentă
5. Când nu mai sunt rezultate → mesaj "Nu mai sunt articole de afișat"

### 8.3 Independență Tab-uri

- Articolele și resursele web au offset-uri separate
- Click "Load more" pe tab-ul Web nu afectează tab-ul Articles
- Parametrul `type` controlează ce se cere: `"articles"`, `"web"`, sau `"both"`

---

## 9. Autentificare

### 9.1 Fluxuri

| Acțiune | Endpoint | Rezultat |
|---------|----------|----------|
| Register | `POST /auth/register` | Creare cont + auto-login |
| Login | `POST /auth/login` | Setare session cookie |
| Logout | `POST /auth/logout` | Ștergere session |
| Check | `GET /auth/me` | Verificare dacă e logat |

### 9.2 UI

- **Neautentificat**: buton "Autentificare" → modal Login/Register
- **Autentificat**: afișare username + buton "Deconectare"
- **Migrare date**: la login, articolele salvate din localStorage se migrează pe server

### 9.3 Fallback Guest

Utilizatorii neautentificați pot:
- Căuta și primi recomandări ✅
- Da rating-uri (legate de session_id) ✅
- Salva articole (în localStorage) ✅
- Nu pot: sincroniza între dispozitive ❌

---

## 10. Accesibilitate

### 10.1 Implementări

| Feature | Implementare |
|---------|-------------|
| **Semantic HTML** | `<header>`, `<main>`, `<aside>`, `<section>`, `<footer>` |
| **ARIA labels** | `aria-label`, `aria-labelledby`, `aria-describedby` pe toate controalele |
| **ARIA roles** | `role="tablist"`, `role="tab"`, `role="tabpanel"`, `role="dialog"` |
| **ARIA live** | `aria-live="assertive"` pe erori, `aria-live="polite"` pe loading |
| **Keyboard nav** | Tab order logic, focus visible pe toate elementele interactive |
| **Focus management** | Focus trap în modale, return focus la închidere |
| **Color contrast** | Raport minim 4.5:1 pentru text normal |
| **Required fields** | `aria-required="true"` + indicator vizual `*` |

### 10.2 Exemple

```html
<button id="submit-btn" type="submit" aria-label="Caută recomandări">
<div id="error-container" role="alert" aria-live="assertive" hidden>
<section id="panel-articles" role="tabpanel" aria-labelledby="tab-articles">
<input aria-required="true" aria-describedby="title-hint">
```

---

## 11. Responsive Design

### 11.1 Breakpoints

| Breakpoint | Layout |
|-----------|--------|
| > 1024px | Two-column (form sticky left, results right) |
| ≤ 1024px | Single column (form top, results below) |
| ≤ 600px | Compact (padding redus, cards full-width) |

### 11.2 CSS Grid

```css
.two-column-layout {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 2rem;
}

@media (max-width: 1024px) {
  .two-column-layout {
    grid-template-columns: 1fr;
  }
}
```

---

## 12. State Management

### 12.1 Fără Framework — Vanilla Approach

State-ul aplicației este gestionat manual:

```typescript
interface AppState {
  currentQuery: string;
  allArticles: Article[];
  allWebResources: WebResource[];
  displayedArticles: number;
  displayedWebResources: number;
  hasMoreArticles: boolean;
  hasMoreWebResources: boolean;
  currentLang: Language;
  timestamp: number;
}
```

### 12.2 Persistență

| Date | Storage | Expirare |
|------|---------|----------|
| Tema (light/dark) | localStorage | Permanent |
| Limba (ro/en) | localStorage | Permanent |
| Session ID | sessionStorage | Tab close |
| Rezultate curente | sessionStorage | 1 oră |
| Articole salvate (guest) | localStorage | Permanent |
| Articole salvate (auth) | Server (SQLite) | Permanent |

---

## 13. TypeScript — Type Safety

### 13.1 De ce TypeScript fără Framework

- **Type safety**: Erori detectate la compilare, nu la runtime
- **IntelliSense**: Autocomplete în IDE pentru toate structurile
- **Refactoring sigur**: Redenumire proprietăți propagată automat
- **Documentație implicită**: Interfețele servesc ca documentație
- **Zero overhead**: Compilat în JS vanilla, niciun runtime extra

### 13.2 Tipuri Definite (`types.ts`)

Toate structurile de date sunt tipizate conform OpenAPI spec:

```typescript
export interface Article {
  resource_type: 'article';
  title: string;
  authors: string[];
  year: number | null;
  abstract_snippet: string | null;
  score: number;
  quality_warning: string | null;
  item_id: string;
}

export interface RecommendResponse {
  query_language: 'ro' | 'en';
  articles: Article[];
  web_resources: WebResource[];
  notices: string[];
  error: string | null;
}
```

### 13.3 API Client Tipizat (`api.ts`)

Fiecare funcție API are tipuri stricte pe input și output:

```typescript
export async function fetchRecommendations(
  request: RecommendRequest
): Promise<RecommendResponse> { ... }

export async function submitFeedback(
  request: FeedbackRequest
): Promise<FeedbackResponse> { ... }
```

### 13.4 Compilare

```bash
# TypeScript → JavaScript (ES2020 modules)
npx tsc --strict --target ES2020 --module ES2020 --outDir static/dist static/src/*.ts
```

---

## 14. Performanță Frontend

| Optimizare | Detaliu |
|-----------|---------|
| **No framework** | 0KB overhead de framework (React ~40KB, Vue ~30KB) |
| **CSS variables** | Schimbare temă fără re-render (doar CSS repaint) |
| **Lazy pagination** | Doar 5 carduri inițial, rest la cerere |
| **Async feedback** | Rating-uri trimise fără blocare UI |
| **Event delegation** | Un singur listener pe container, nu pe fiecare card |
| **SessionStorage state** | Rezultate cache-uite 1h (evită re-fetch la navigare) |
| **ES modules** | Încărcare paralelă `api.js` + `app.js` |
