# PlantUML Diagrams

Acest director conține toate diagramele PlantUML pentru Hybrid Thesis Recommender.

## 📁 Conținut

### Versiuni Simplificate (✅ Recomandate pentru A4)

| Fișier | Descriere |
|--------|-----------|
| `class-diagram-simple.puml` | Clasele principale și relațiile |
| `sequence-diagram-simple.puml` | Fluxul de recomandare simplificat |
| `deployment-diagram-simple.puml` | Arhitectura de deployment |
| `activity-diagram-simple.puml` | Pipeline ingestion simplificat |
| `state-diagram-simple.puml` | State machine simplificat |

### Versiuni Complete (Detaliate)

| Fișier | Descriere |
|--------|-----------|
| `component-diagram.puml` | Arhitectura componentelor (optimizat pentru A4) |
| `class-diagram.puml` | Toate clasele și metodele |
| `sequence-diagram-recommend.puml` | Fluxul complet de recomandare |
| `sequence-diagram-feedback.puml` | Fluxul de feedback detaliat |
| `deployment-diagram.puml` | Deployment cu toate detaliile |
| `activity-diagram-ingestion.puml` | Pipeline ingestion complet |
| `state-diagram-query.puml` | State machine detaliat |

## 🚀 Cum să Generezi Diagramele

### Metoda 1: Online (Fără Instalare)

1. Deschide [PlantUML Online Editor](http://www.plantuml.com/plantuml/uml/)
2. Deschide unul din fișierele `.puml`
3. Copiază tot conținutul (Ctrl+A, Ctrl+C)
4. Lipește în editor (Ctrl+V)
5. Descarcă ca PNG/SVG/PDF

### Metoda 2: Command Line

```bash
# Instalează PlantUML și Graphviz
choco install plantuml graphviz  # Windows
brew install plantuml graphviz   # Mac
sudo apt-get install plantuml graphviz  # Linux

# Navighează la acest director
cd theory_files/plantuml_diagrams

# Generează toate ca PNG
plantuml *.puml

# Generează versiunile simplificate ca PDF (recomandat)
plantuml -tpdf *-simple.puml

# Generează toate ca PDF
plantuml -tpdf *.puml

# Generează ca SVG (scalabil)
plantuml -tsvg *.puml
```

### Metoda 3: Visual Studio Code

1. Instalează extensia "PlantUML" de jebbs
2. Instalează Graphviz (vezi mai sus)
3. Deschide orice fișier `.puml`
4. Apasă `Alt+D` pentru preview
5. Click dreapta → "Export Current Diagram"

## 📋 Recomandări pentru Licență

Pentru o lucrare de licență pe A4, folosește aceste 5 diagrame:

1. **component-diagram.puml** - Arhitectura generală
2. **sequence-diagram-simple.puml** - Fluxul principal
3. **class-diagram-simple.puml** - Modelul de date
4. **deployment-diagram-simple.puml** - Deployment
5. Schema bazei de date din `../ARHITECTURA_SISTEM.md` (Mermaid)

Toate versiunile simplificate se încadrează perfect pe A4 portrait!

## 📐 Setări de Imprimare

- **A4 Portrait:** Toate diagramele `*-simple.puml`
- **A4 Landscape:** `sequence-diagram-recommend.puml`, `deployment-diagram.puml`, `state-diagram-query.puml`
- **A3:** `class-diagram.puml` (versiunea completă)

## 💡 Tips

- Exportă ca **PDF** pentru cea mai bună calitate de imprimare
- Exportă ca **SVG** pentru scalare fără pierdere în prezentări
- Exportă ca **PNG** pentru documentație online

## 📚 Documentație Completă

Vezi fișierele din directorul părinte:
- `../DIAGRAME_PLANTUML_README.md` - Instrucțiuni complete
- `../QUICK_START.md` - Ghid rapid
- `../DIAGRAME_INDEX.md` - Index complet cu toate diagramele

## 🔗 Resurse

- [PlantUML Documentation](https://plantuml.com/)
- [PlantUML Online Editor](http://www.plantuml.com/plantuml/uml/)
- [Graphviz Download](https://graphviz.org/download/)

