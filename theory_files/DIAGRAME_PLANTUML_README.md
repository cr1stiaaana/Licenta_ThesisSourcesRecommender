# PlantUML Diagrams - Hybrid Thesis Recommender

**Locație:** `theory_files/plantuml_diagrams/`

## Diagrame Disponibile

### Versiuni Complete (Detaliate)
1. **component-diagram.puml** - Arhitectura componentelor (simplificată pentru A4)
2. **class-diagram.puml** - Diagrama claselor complete (foarte detaliată)
3. **sequence-diagram-recommend.puml** - Fluxul complet de recomandare
4. **sequence-diagram-feedback.puml** - Fluxul de feedback
5. **deployment-diagram.puml** - Arhitectura de deployment
6. **activity-diagram-ingestion.puml** - Pipeline-ul de ingestion
7. **state-diagram-query.puml** - State machine pentru query

### Versiuni Simplificate (Optimizate pentru A4)
1. **class-diagram-simple.puml** - Clasele principale
2. **sequence-diagram-simple.puml** - Fluxul de recomandare simplificat
3. **deployment-diagram-simple.puml** - Deployment simplificat
4. **activity-diagram-simple.puml** - Ingestion simplificat
5. **state-diagram-simple.puml** - State machine simplificat

## Cum să Generezi Diagramele

### Opțiunea 1: Online (PlantUML Web Server)

1. Deschide [PlantUML Online Editor](http://www.plantuml.com/plantuml/uml/)
2. Copiază conținutul fișierului `.puml`
3. Lipește în editor
4. Descarcă ca PNG sau SVG

### Opțiunea 2: Visual Studio Code

1. Instalează extensia **PlantUML** de jebbs
2. Instalează **Graphviz** (necesar pentru rendering):
   - Windows: `choco install graphviz` sau descarcă de pe [graphviz.org](https://graphviz.org/download/)
   - Mac: `brew install graphviz`
   - Linux: `sudo apt-get install graphviz`
3. Deschide fișierul `.puml` în VS Code
4. Apasă `Alt+D` pentru preview
5. Click dreapta → "Export Current Diagram" → Alege formatul (PNG, SVG, PDF)

### Opțiunea 3: Command Line

```bash
# Instalează PlantUML
# Windows (cu Chocolatey)
choco install plantuml

# Mac (cu Homebrew)
brew install plantuml

# Linux
sudo apt-get install plantuml

# Navighează la directorul cu diagrame
cd theory_files/plantuml_diagrams

# Generează diagrama
plantuml component-diagram.puml

# Generează toate diagramele
plantuml *.puml

# Generează ca SVG (scalabil)
plantuml -tsvg component-diagram.puml

# Generează ca PDF
plantuml -tpdf component-diagram.puml
```

### Opțiunea 4: Docker

```bash
# Navighează la directorul cu diagrame
cd theory_files/plantuml_diagrams

# Rulează PlantUML în Docker
docker run --rm -v $(pwd):/data plantuml/plantuml:latest -tpng /data/*.puml

# Pentru SVG
docker run --rm -v $(pwd):/data plantuml/plantuml:latest -tsvg /data/*.puml
```

## Recomandări pentru Imprimare pe A4

### Versiuni Simplificate (Recomandate)
- **class-diagram-simple.puml** - Se încadrează perfect pe A4 portrait
- **sequence-diagram-simple.puml** - Se încadrează pe A4 portrait
- **deployment-diagram-simple.puml** - Se încadrează pe A4 portrait
- **activity-diagram-simple.puml** - Se încadrează pe A4 portrait
- **state-diagram-simple.puml** - Se încadrează pe A4 portrait

### Versiuni Complete
- **component-diagram.puml** - Optimizat pentru A4 portrait
- **sequence-diagram-recommend.puml** - Mai bine pe A4 landscape
- **sequence-diagram-feedback.puml** - Se încadrează pe A4 portrait
- **deployment-diagram.puml** - Mai bine pe A4 landscape
- **activity-diagram-ingestion.puml** - Se încadrează pe A4 portrait
- **state-diagram-query.puml** - Mai bine pe A4 landscape
- **class-diagram.puml** - Foarte detaliat, mai bine pe A3 sau 2 pagini A4

## Setări de Export pentru A4

### Pentru PNG (Imprimare)
```bash
# Navighează la directorul cu diagrame
cd theory_files/plantuml_diagrams

# DPI înalt pentru imprimare
plantuml -DPLANTUML_LIMIT_SIZE=8192 -tpng class-diagram-simple.puml
```

### Pentru PDF (Cel mai bun pentru imprimare)
```bash
cd theory_files/plantuml_diagrams
plantuml -tpdf class-diagram-simple.puml
```

### Pentru SVG (Scalabil, perfect pentru documentație)
```bash
cd theory_files/plantuml_diagrams
plantuml -tsvg class-diagram-simple.puml
```

## Personalizare

Poți ajusta dimensiunea fontului în fiecare fișier `.puml`:

```plantuml
skinparam defaultFontSize 9   ' Mai mic pentru mai mult conținut
skinparam defaultFontSize 11  ' Mai mare pentru lizibilitate
```

Poți ajusta spațierea:

```plantuml
skinparam nodesep 10   ' Spațiu între noduri
skinparam ranksep 20   ' Spațiu între niveluri
```

## Includere în LaTeX

```latex
\usepackage{graphicx}

% Pentru PNG
\includegraphics[width=\textwidth]{theory_files/plantuml_diagrams/component-diagram.png}

% Pentru PDF
\includegraphics[width=\textwidth]{theory_files/plantuml_diagrams/component-diagram.pdf}

% Pentru SVG (necesită svg package)
\usepackage{svg}
\includesvg[width=\textwidth]{theory_files/plantuml_diagrams/component-diagram}
```

## Includere în Word

1. Generează ca PNG sau SVG
2. Insert → Pictures → Selectează fișierul
3. Ajustează dimensiunea la lățimea paginii

## Troubleshooting

### Diagrama este prea mare
- Folosește versiunea simplificată (`*-simple.puml`)
- Reduce `defaultFontSize` la 8 sau 9
- Exportă ca PDF și printează landscape

### Textul este prea mic
- Crește `defaultFontSize` la 11 sau 12
- Exportă ca SVG pentru scalare fără pierdere de calitate

### Graphviz nu este găsit
```bash
# Verifică instalarea
dot -V

# Setează path-ul în VS Code settings.json
"plantuml.java": "java",
"plantuml.commandArgs": ["-DGRAPHVIZ_DOT=C:\\Program Files\\Graphviz\\bin\\dot.exe"]
```

## Diagrame Recomandate pentru Licență

Pentru o lucrare de licență, recomand următoarele diagrame în această ordine:

1. **component-diagram.puml** - Prezentare generală a arhitecturii
2. **sequence-diagram-simple.puml** - Fluxul principal de recomandare
3. **class-diagram-simple.puml** - Modelul de date
4. **deployment-diagram-simple.puml** - Arhitectura de deployment
5. **activity-diagram-simple.puml** - Pipeline-ul de ingestion (opțional)
6. **state-diagram-simple.puml** - State machine (opțional)

Toate versiunile simplificate se încadrează perfect pe A4 portrait!

## Resurse Utile

- [PlantUML Official Documentation](https://plantuml.com/)
- [PlantUML Cheat Sheet](https://ogom.github.io/draw_uml/plantuml/)
- [Real World PlantUML Examples](https://real-world-plantuml.com/)
- [PlantUML Themes](https://github.com/plantuml/plantuml/tree/master/themes)

