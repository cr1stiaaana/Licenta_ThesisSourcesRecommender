# PlantUML Diagrams

Acest director conține toate diagramele PlantUML pentru Hybrid Thesis Recommender în două limbi.

## 🌍 Limbi Disponibile

- **🇬🇧 Engleză** (subdirectorul `en/`): Versiuni originale în engleză
- **🇷🇴 Română** (subdirectorul `ro/`): Toate diagramele traduse în română

## 📁 Structură

```
plantuml_diagrams/
├── README.md                           # Acest fișier
├── en/                                 # Versiuni în engleză
│   ├── README.md                       # Ghid pentru versiunile EN
│   ├── *-simple.puml                   # 5 diagrame simplificate (EN)
│   └── *.puml                          # 7 diagrame complete (EN)
└── ro/                                 # Versiuni în română
    ├── README.md                       # Ghid pentru versiunile RO
    ├── *-simple.puml                   # 5 diagrame simplificate (RO)
    └── *.puml                          # Diagrame complete (RO)
```

## 📁 Conținut

### Versiuni Simplificate (✅ Recomandate pentru A4)

| Fișier (EN) | Fișier (RO) | Descriere |
|-------------|-------------|-----------|
| `architecture-overview.puml` | `ro/architecture-overview.puml` | **Arhitectură generală** ⭐ |
| `frontend-backend.puml` | `ro/frontend-backend.puml` | **Interacțiune Frontend-Backend** ⭐ |
| `backend-layers.puml` | `ro/backend-layers.puml` | **Straturi Backend (7 straturi)** ⭐ |
| `class-diagram-simple.puml` | `ro/class-diagram-simple.puml` | Clasele principale |
| `sequence-diagram-simple.puml` | `ro/sequence-diagram-simple.puml` | Flux recomandare |
| `deployment-diagram-simple.puml` | `ro/deployment-diagram-simple.puml` | Deployment |
| `activity-diagram-simple.puml` | `ro/activity-diagram-simple.puml` | Pipeline ingestion |
| `state-diagram-simple.puml` | `ro/state-diagram-simple.puml` | Mașină de stări |

### Versiuni Complete (Detaliate)

| Fișier (EN) | Fișier (RO) | Descriere |
|-------------|-------------|-----------|
| `component-diagram.puml` | `ro/component-diagram.puml` | Arhitectura componentelor |
| `class-diagram.puml` | - | Toate clasele (doar EN) |
| `sequence-diagram-recommend.puml` | `ro/sequence-diagram-recommend.puml` | Flux complet |
| `sequence-diagram-feedback.puml` | `ro/sequence-diagram-feedback.puml` | Flux feedback |
| `deployment-diagram.puml` | - | Deployment detaliat (doar EN) |
| `activity-diagram-ingestion.puml` | - | Ingestion complet (doar EN) |
| `state-diagram-query.puml` | - | State machine detaliat (doar EN) |

## 🚀 Cum să Generezi Diagramele

### Metoda 1: Online (Fără Instalare) ⭐ Recomandat

1. Deschide [PlantUML Online Editor](http://www.plantuml.com/plantuml/uml/)
2. Deschide fișierul `.puml` dorit (EN sau RO)
3. Copiază tot conținutul (Ctrl+A, Ctrl+C)
4. Lipește în editor (Ctrl+V)
5. Descarcă ca PNG/SVG/PDF

### Metoda 2: Command Line

```bash
# Instalează PlantUML și Graphviz
choco install plantuml graphviz  # Windows
brew install plantuml graphviz   # Mac
sudo apt-get install plantuml graphviz  # Linux

# Pentru versiunile în engleză
cd theory_files/plantuml_diagrams
plantuml -tpdf *-simple.puml

# Pentru versiunile în română
cd theory_files/plantuml_diagrams/ro
plantuml -tpdf *-simple.puml
```

### Metoda 3: Visual Studio Code

1. Instalează extensia "PlantUML" de jebbs
2. Instalează Graphviz
3. Deschide orice fișier `.puml`
4. Apasă `Alt+D` pentru preview
5. Click dreapta → "Export Current Diagram"

## 📋 Recomandări pentru Licență

### Pentru Licență în Română 🇷🇴

Folosește diagramele din subdirectorul `ro/`:

**Set Complet (Recomandat):**
1. **ro/architecture-overview.puml** ⭐ - Arhitectura generală
2. **ro/frontend-backend.puml** ⭐ - Interacțiune Frontend-Backend
3. **ro/backend-layers.puml** ⭐ - Straturi Backend (7 straturi)
4. **ro/sequence-diagram-simple.puml** - Fluxul principal
5. **ro/class-diagram-simple.puml** - Modelul de date
6. Schema bazei de date din `../ARHITECTURA_SISTEM.md` (Mermaid)

**Set Minim:**
1. **ro/architecture-overview.puml** - Arhitectura generală
2. **ro/backend-layers.puml** - Straturi Backend
3. **ro/sequence-diagram-simple.puml** - Fluxul principal

### Pentru Licență în Engleză 🇬🇧

Folosește diagramele din subdirectorul `en/`:

**Complete Set (Recommended):**
1. **en/architecture-overview.puml** ⭐ - System architecture
2. **en/frontend-backend.puml** ⭐ - Frontend-Backend interaction
3. **en/backend-layers.puml** ⭐ - Backend layers (7 layers)
4. **en/sequence-diagram-simple.puml** - Main flow
5. **en/class-diagram-simple.puml** - Data model
6. Database schema from `../ARHITECTURA_SISTEM.md` (Mermaid)

**Minimal Set:**
1. **en/architecture-overview.puml** - System architecture
2. **en/backend-layers.puml** - Backend layers
3. **en/sequence-diagram-simple.puml** - Main flow

Toate versiunile simplificate se încadrează perfect pe A4 portrait!

## 📐 Setări de Imprimare

- **A4 Portrait:** Toate diagramele `*-simple.puml`
- **A4 Landscape:** `sequence-diagram-recommend.puml`
- **Format recomandat:** PDF pentru cea mai bună calitate

## 💡 Tips

- Exportă ca **PDF** pentru imprimare de calitate
- Exportă ca **SVG** pentru scalare fără pierdere în prezentări
- Exportă ca **PNG** pentru documentație online
- Folosește versiunile simplificate pentru A4
- Alege limba potrivită pentru lucrarea ta (RO sau EN)

## 📚 Documentație Completă

Vezi fișierele din directorul părinte:
- `../DIAGRAME_PLANTUML_README.md` - Instrucțiuni complete
- `../QUICK_START.md` - Ghid rapid
- `../DIAGRAME_INDEX.md` - Index complet cu toate diagramele
- `ro/README.md` - Ghid specific pentru versiunile în română

## 🔗 Resurse

- [PlantUML Documentation](https://plantuml.com/)
- [PlantUML Online Editor](http://www.plantuml.com/plantuml/uml/)
- [Graphviz Download](https://graphviz.org/download/)

## ✅ Checklist

- [ ] Am ales limba potrivită (RO sau EN)
- [ ] Am generat diagramele simplificate ca PDF
- [ ] Am verificat că se încadrează pe A4
- [ ] Am testat imprimarea
- [ ] Textul este lizibil

