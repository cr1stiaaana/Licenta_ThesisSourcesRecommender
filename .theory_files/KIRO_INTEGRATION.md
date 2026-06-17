# Integrarea Kiro în Proiect

## 1. Ce este Kiro

Kiro este un mediu de dezvoltare asistat de AI (AI-Powered Development Environment) care oferă:
- **Spec-Driven Development** — dezvoltare ghidată de specificații structurate
- **Steering Files** — reguli și context persistent care ghidează agentul AI în fiecare interacțiune
- **MCP (Model Context Protocol)** — integrare cu servere externe pentru acces la baze de date, fetch web, și alte tool-uri
- **Hooks** — automatizări care se declanșează la evenimente din IDE (editare fișiere, submit prompt, etc.)
- **Powers** — extensii modulare care adaugă capabilități suplimentare (documentație, tool-uri, workflow-uri)

## 2. Structura Directorului `.kiro/`

```
.kiro/
├── settings/
│   └── mcp.json              # Configurare servere MCP
├── specs/
│   └── hybrid-thesis-recommender/
│       ├── .config.kiro      # Configurare spec
│       ├── requirements.md   # Cerințe funcționale detaliate
│       ├── design.md         # Document de design tehnic
│       └── tasks.md          # Plan de implementare cu task-uri
└── steering/
    ├── product.md            # Context despre produs (always included)
    ├── structure.md          # Structura proiectului (always included)
    └── tech.md               # Stack tehnologic și comenzi (always included)
```

## 3. Steering Files — Context Persistent

Steering files sunt fișiere Markdown din `.kiro/steering/` care furnizează context și instrucțiuni agentului AI la fiecare interacțiune. Ele funcționează ca o „memorie de lungă durată" a proiectului.

### 3.1 Tipuri de Incluziune

| Tip | Comportament |
|-----|-------------|
| **Always** (implicit) | Inclus automat în fiecare conversație |
| **fileMatch** | Inclus doar când un fișier care se potrivește pattern-ului este citit |
| **manual** | Inclus doar când utilizatorul îl referențiază explicit cu `#` |

### 3.2 Fișiere Steering din Proiect

#### `product.md` — Descriere Produs
Conține:
- Funcționalitatea de bază a sistemului
- Features cheie (hybrid retrieval, web search, quality verification, feedback, i18n)
- Scop: Kiro înțelege *ce* construiește

#### `structure.md` — Structura Proiectului
Conține:
- Layout-ul directoarelor cu explicații
- Patternuri arhitecturale (modular design, dependency injection, application factory)
- Fluxul de date (Query → Retrieval → Ranking → Verification → Response)
- Convenții de cod (naming, imports, error handling, testing)
- Scop: Kiro înțelege *cum* este organizat codul

#### `tech.md` — Stack Tehnologic
Conține:
- Limbaje și versiuni (Python 3.10+, Flask 3.1.1, etc.)
- Comenzi de dezvoltare (start server, run tests, ingest data)
- Configurare (`config.yaml`)
- Dependențe
- Scop: Kiro știe *cu ce* lucrează și cum să ruleze proiectul

### 3.3 Beneficii

- **Consistență**: Agentul respectă convențiile proiectului fără a fi instruit de fiecare dată
- **Eficiență**: Nu trebuie repetat contextul la fiecare conversație
- **Colaborare**: Orice membru al echipei beneficiază de aceleași reguli
- **Evoluție**: Se actualizează pe măsură ce proiectul crește

## 4. Spec-Driven Development (SDD)

Specs sunt documente structurate care ghidează implementarea de la cerințe la cod funcțional.

### 4.1 Fluxul SDD

```
Requirements → Design → Tasks → Implementation → Validation
```

### 4.2 Niveluri de Specificații

#### `requirements.md` — Cerințe Funcționale
- **12 cerințe** detaliate cu user stories și acceptance criteria
- Format: "THE System SHALL..." pentru cerințe obligatorii
- Glosar cu termeni definiți (Query, Article, Embedding, Hybrid_Ranker, etc.)
- Cerințe acoperite: input validation, semantic retrieval, keyword retrieval, hybrid ranking, output format, content quality, web retrieval, ingestion, configuration, error handling, multilingual support, web UI, feedback

#### `design.md` — Design Tehnic
- Diagrame Mermaid (sequence diagram, component diagram, flowchart)
- Algoritmi detaliați (BM25, RRF, cosine similarity, content verification)
- Interfețe Python pentru fiecare componentă
- Modele de date (dataclasses)
- Decizii tehnologice cu justificări

#### `tasks.md` — Plan de Implementare
- **19 task-uri** ordonate cronologic cu dependențe
- Fiecare task referențiază cerințele pe care le implementează
- Checkpoints la task-urile 7, 11, 14, 19 pentru validare incrementală
- Task-uri opționale marcate cu `*` (teste unitare, property tests)
- Status tracking: `[x]` completat, `[ ]` în așteptare, `[-]` parțial

### 4.3 Trasabilitate

Fiecare task din `tasks.md` referențiază cerințele din `requirements.md`:
```
- [x] 5.1 Implement SemanticRetriever
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 10.3, 10.4, 10.5_
```

Aceasta asigură:
- Nicio cerință nu rămâne neimplementată
- Fiecare linie de cod are o justificare
- Testele validează cerințe specifice

## 5. MCP (Model Context Protocol)

MCP permite agentului AI să interacționeze cu servere externe direct din conversație.

### 5.1 Configurare (`mcp.json`)

```json
{
  "mcpServers": {
    "sqlite": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db-path", "data/articles.db"],
      "disabled": false,
      "autoApprove": ["read_query", "list_tables", "describe_table"]
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"],
      "disabled": false,
      "autoApprove": ["fetch"]
    }
  }
}
```

### 5.2 Servere MCP Configurate

| Server | Scop | Tool-uri |
|--------|------|----------|
| **sqlite** | Acces direct la baza de date `articles.db` | `read_query`, `write_query`, `list_tables`, `describe_table` |
| **fetch** | Fetch conținut de pe web (URL-uri) | `fetch` |

### 5.3 Utilizare Practică

- **SQLite MCP**: Kiro poate interoga direct baza de date pentru a inspecta articole, verifica schema, sau analiza date fără a scrie scripturi separate
- **Fetch MCP**: Kiro poate accesa documentație online, API-uri, sau pagini web pentru a obține informații actualizate

### 5.4 Auto-Approve

Tool-urile din `autoApprove` sunt executate fără confirmare explicită de la utilizator, accelerând workflow-ul pentru operații sigure (read-only).

## 6. Hooks — Automatizări IDE

Hooks sunt acțiuni automate declanșate de evenimente din IDE.

### 6.1 Tipuri de Evenimente

| Eveniment | Declanșare |
|-----------|-----------|
| `fileEdited` | Când un fișier este salvat |
| `fileCreated` | Când un fișier nou este creat |
| `fileDeleted` | Când un fișier este șters |
| `promptSubmit` | Când un mesaj este trimis agentului |
| `agentStop` | Când agentul termină execuția |
| `preToolUse` | Înainte de executarea unui tool |
| `postToolUse` | După executarea unui tool |
| `preTaskExecution` | Înainte de începerea unui task din spec |
| `postTaskExecution` | După completarea unui task din spec |
| `userTriggered` | Manual, la apăsarea unui buton |

### 6.2 Acțiuni Disponibile

| Acțiune | Descriere |
|---------|-----------|
| `askAgent` | Trimite un prompt agentului AI |
| `runCommand` | Execută o comandă shell |

### 6.3 Exemplu: Lint la Salvare

```json
{
  "name": "Lint on Save",
  "version": "1.0.0",
  "when": {
    "type": "fileEdited",
    "patterns": ["*.py"]
  },
  "then": {
    "type": "runCommand",
    "command": "flake8 app/ --select=E9,F63,F7,F82"
  }
}
```

### 6.4 Exemplu: Teste după Task

```json
{
  "name": "Run Tests After Task",
  "version": "1.0.0",
  "when": {
    "type": "postTaskExecution"
  },
  "then": {
    "type": "runCommand",
    "command": "pytest tests/ -v --tb=short"
  }
}
```

## 7. Powers — Extensii Modulare

Powers sunt pachete care adaugă capabilități suplimentare agentului.

### 7.1 Componente unui Power

| Componentă | Rol |
|------------|-----|
| **POWER.md** | Documentație și instrucțiuni |
| **MCP Servers** | Tool-uri externe accesibile agentului |
| **Steering Files** | Ghiduri de workflow specifice |

### 7.2 Cazuri de Utilizare Relevante

- **Generare diagrame**: PlantUML/Mermaid automat din cod
- **Fetch articole academice**: Acces la Semantic Scholar, arXiv
- **Documentație AWS**: Pentru deployment cloud
- **Build a Power**: Creare powers custom pentru proiect

### 7.3 Instalare

Powers se instalează din panoul dedicat din Kiro (Command Palette → Powers).

## 8. Workflow Complet de Dezvoltare cu Kiro

### 8.1 Inițializare Proiect

```
1. Creare steering files (product.md, structure.md, tech.md)
2. Configurare MCP servers (mcp.json)
3. Definire spec (requirements → design → tasks)
```

### 8.2 Dezvoltare Iterativă

```
1. Selectare task din tasks.md
2. Kiro citește steering files → înțelege contextul
3. Kiro citește design.md → înțelege arhitectura
4. Implementare cod conform specificațiilor
5. Validare (teste, build)
6. Marcare task ca completat [x]
7. Checkpoint → validare integrare
```

### 8.3 Moduri de Autonomie

| Mod | Comportament |
|-----|-------------|
| **Autopilot** | Kiro lucrează autonom, utilizatorul revizuiește la final |
| **Supervised** | Kiro cere aprobare după fiecare modificare |

### 8.4 Sesiuni

| Tip | Scop |
|-----|------|
| **Vibe** | Conversație liberă, Q&A, explorare |
| **Spec** | Dezvoltare structurată pe baza specificațiilor |

## 9. Avantaje ale Integrării Kiro

### Pentru Dezvoltare
- **Consistență**: Steering files asigură respectarea convențiilor
- **Trasabilitate**: Fiecare linie de cod este legată de o cerință
- **Productivitate**: Generare cod, teste, documentație automat
- **Calitate**: Validare continuă prin hooks și checkpoints

### Pentru Documentare (Licență)
- **Specs ca documentație**: `requirements.md` și `design.md` pot fi incluse direct în lucrare
- **Diagrame automate**: Mermaid/PlantUML generate din design
- **Istoric decizii**: Specificațiile captează *de ce* s-au făcut anumite alegeri
- **Reproducibilitate**: Oricine poate reconstrui proiectul urmând `tasks.md`

### Pentru Mentenanță
- **Onboarding rapid**: Steering files explică proiectul noilor contribuitori
- **Hot-reload config**: Modificări fără restart
- **MCP access**: Inspecție directă a datelor fără scripturi ad-hoc

## 10. Comparație cu Dezvoltarea Tradițională

| Aspect | Tradițional | Cu Kiro |
|--------|-------------|---------|
| Context proiect | În capul dezvoltatorului | Steering files (persistent) |
| Cerințe | Document Word/PDF separat | `requirements.md` integrat |
| Design | Diagrame separate | `design.md` cu cod Mermaid |
| Implementare | Manual, de la zero | Ghidată de tasks.md |
| Validare | Manuală, ad-hoc | Hooks automate |
| Acces date | Scripturi separate | MCP direct din IDE |
| Documentație | Scrisă post-factum | Generată din specs |

## 11. Referințe

- [Kiro Documentation](https://kiro.dev/docs)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Spec-Driven Development](https://kiro.dev/docs/specs)
- Fișiere locale: `.kiro/steering/`, `.kiro/specs/`, `.kiro/settings/mcp.json`
