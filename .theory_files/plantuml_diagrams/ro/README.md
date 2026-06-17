# Diagrame PlantUML în Română

Acest director conține versiunile în limba română ale tuturor diagramelor PlantUML.

## 📁 Conținut

### Versiuni Simplificate (✅ Recomandate pentru A4)

| Fișier | Descriere |
|--------|-----------|
| `architecture-overview.puml` | **Arhitectura generală a sistemului** ⭐ |
| `frontend-backend.puml` | **Interacțiune Frontend-Backend** ⭐ |
| `backend-layers.puml` | **Straturi Backend (7 straturi)** ⭐ |
| `class-diagram-simple.puml` | Clasele principale și relațiile |
| `sequence-diagram-simple.puml` | Fluxul de recomandare simplificat |
| `deployment-diagram-simple.puml` | Arhitectura de deployment |
| `activity-diagram-simple.puml` | Pipeline ingestion simplificat |
| `state-diagram-simple.puml` | Mașină de stări simplificată |

### Versiuni Complete (Detaliate)

| Fișier | Descriere |
|--------|-----------|
| `component-diagram.puml` | Arhitectura componentelor |
| `sequence-diagram-recommend.puml` | Fluxul complet de recomandare |
| `sequence-diagram-feedback.puml` | Fluxul de feedback detaliat |

## 🚀 Cum să Generezi Diagramele

### Metoda 1: Online (Fără Instalare)

1. Deschide [PlantUML Online Editor](http://www.plantuml.com/plantuml/uml/)
2. Deschide unul din fișierele `.puml` din acest director
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
cd theory_files/plantuml_diagrams/ro

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
2. Instalează Graphviz
3. Deschide orice fișier `.puml` din acest director
4. Apasă `Alt+D` pentru preview
5. Click dreapta → "Export Current Diagram"

## 📋 Recomandări pentru Licență

Pentru o lucrare de licență pe A4, folosește aceste diagrame în română:

1. **architecture-overview.puml** ⭐ - Arhitectura generală (OBLIGATORIU)
2. **sequence-diagram-simple.puml** - Fluxul principal
3. **class-diagram-simple.puml** - Modelul de date
4. **deployment-diagram-simple.puml** - Deployment
5. Schema bazei de date din `../../ARHITECTURA_SISTEM.md` (Mermaid)

**Notă:** Diagrama `architecture-overview.puml` oferă o vedere de ansamblu completă a sistemului și este ideală pentru capitolul de arhitectură!

Toate versiunile simplificate se încadrează perfect pe A4 portrait!

## 🌍 Versiuni Disponibile

- **Română** (acest director): Toate textele în limba română
- **Engleză** (directorul părinte): Versiuni originale în engleză

## 📐 Setări de Imprimare

- **A4 Portrait:** Toate diagramele `*-simple.puml`
- **A4 Landscape:** `sequence-diagram-recommend.puml`
- **Format recomandat:** PDF pentru cea mai bună calitate

## 💡 Tips

- Exportă ca **PDF** pentru imprimare de calitate
- Exportă ca **SVG** pentru scalare fără pierdere
- Exportă ca **PNG** pentru documentație online
- Toate diagramele sunt optimizate pentru A4

## 📚 Documentație

Vezi documentația completă în directorul părinte:
- `../../DIAGRAME_PLANTUML_README.md` - Instrucțiuni complete
- `../../QUICK_START.md` - Ghid rapid
- `../../DIAGRAME_INDEX.md` - Index complet

## 🔗 Resurse

- [PlantUML Documentation](https://plantuml.com/)
- [PlantUML Online Editor](http://www.plantuml.com/plantuml/uml/)
- [Graphviz Download](https://graphviz.org/download/)

