# Theory Files - Hybrid Thesis Recommender

Acest director conține toată documentația tehnică și diagramele pentru lucrarea de licență.

## 📚 Documentație Disponibilă

### Arhitectură și Design

| Fișier | Descriere |
|--------|-----------|
| `ARHITECTURA_SISTEM.md` | Arhitectura completă a sistemului cu diagrame Mermaid |
| `DIAGRAME_TEHNOLOGII.md` | Stack tehnologic și vizualizări |
| `API_DOCUMENTATION.md` | Documentația API-ului REST |
| `AUTH_IMPLEMENTATION.md` | Implementarea autentificării |

### Metodologie

| Fișier | Descriere |
|--------|-----------|
| `SPEC_DRIVEN_DEVELOPMENT.md` | Metodologia Spec-Driven Development |
| `NIVELURI_SPECIFICATII.md` | **Niveluri de Specificații în SDD (Requirements-First)** ⭐ |
| `CAPITOL_TEHNOLOGII.md` | Capitolul despre tehnologii pentru licență |

### Diagrame PlantUML

| Director/Fișier | Descriere |
|-----------------|-----------|
| `plantuml_diagrams/` | **Toate diagramele PlantUML** (12 fișiere .puml) |
| `DIAGRAME_PLANTUML_README.md` | Instrucțiuni complete pentru PlantUML |
| `DIAGRAME_INDEX.md` | Index complet cu toate diagramele (Mermaid + PlantUML) |
| `QUICK_START.md` | Ghid rapid pentru generarea diagramelor |

### Altele

| Fișier | Descriere |
|--------|-----------|
| `FIXES_SUMMARY.md` | Rezumatul bug-urilor rezolvate |

## 🎨 Diagrame Disponibile

### Diagrame Mermaid (în documentație)

Locație: `ARHITECTURA_SISTEM.md` și `DIAGRAME_TEHNOLOGII.md`

- Diagrama Arhitecturală Generală
- Arhitectura pe Straturi (7 straturi)
- Fluxul de Date (Request/Response)
- Schema Bazei de Date (ER diagram)
- Arhitectura de Deployment
- Stack Tehnologic
- Pipeline de Procesare Query
- Metrici de Performanță

### Diagrame PlantUML (fișiere separate)

Locație: `plantuml_diagrams/*.puml`

**Versiuni Simplificate (✅ Recomandate pentru A4):**
- `class-diagram-simple.puml`
- `sequence-diagram-simple.puml`
- `deployment-diagram-simple.puml`
- `activity-diagram-simple.puml`
- `state-diagram-simple.puml`

**Versiuni Complete:**
- `component-diagram.puml`
- `class-diagram.puml`
- `sequence-diagram-recommend.puml`
- `sequence-diagram-feedback.puml`
- `deployment-diagram.puml`
- `activity-diagram-ingestion.puml`
- `state-diagram-query.puml`

## 🚀 Quick Start

### Pentru a Genera Diagramele PlantUML

**Metoda 1: Online (Fără Instalare)**
1. Deschide [PlantUML Online](http://www.plantuml.com/plantuml/uml/)
2. Copiază conținutul din `plantuml_diagrams/*.puml`
3. Descarcă ca PNG/SVG/PDF

**Metoda 2: Command Line**
```bash
# Instalează PlantUML
choco install plantuml graphviz  # Windows
brew install plantuml graphviz   # Mac

# Generează diagramele
cd plantuml_diagrams
plantuml -tpdf *-simple.puml
```

**Metoda 3: VS Code**
1. Instalează extensia "PlantUML"
2. Deschide fișierul `.puml`
3. Alt+D pentru preview
4. Export as PDF

### Pentru a Vizualiza Diagramele Mermaid

**Metoda 1: GitHub/GitLab**
- Diagramele Mermaid se randează automat în fișierele `.md`

**Metoda 2: Mermaid Live Editor**
1. Deschide [Mermaid Live](https://mermaid.live/)
2. Copiază codul Mermaid din documentație
3. Descarcă ca PNG/SVG

**Metoda 3: VS Code**
1. Instalează "Markdown Preview Mermaid Support"
2. Deschide fișierul `.md`
3. Preview Markdown (Ctrl+Shift+V)

## 📋 Recomandări pentru Licență

### Set Minim (5 diagrame)

1. **Arhitectura Generală** - `plantuml_diagrams/component-diagram.puml`
2. **Fluxul Principal** - `plantuml_diagrams/sequence-diagram-simple.puml`
3. **Modelul de Date** - `plantuml_diagrams/class-diagram-simple.puml`
4. **Deployment** - `plantuml_diagrams/deployment-diagram-simple.puml`
5. **Schema BD** - Mermaid din `ARHITECTURA_SISTEM.md`

### Capitole Recomandate

1. **Introducere**
   - Context și motivație
   - Obiective

2. **Tehnologii Utilizate**
   - Vezi `CAPITOL_TEHNOLOGII.md`
   - Stack tehnologic din `DIAGRAME_TEHNOLOGII.md`

3. **Arhitectura Sistemului**
   - Vezi `ARHITECTURA_SISTEM.md`
   - Diagrame din `plantuml_diagrams/`

4. **Implementare**
   - API Documentation: `API_DOCUMENTATION.md`
   - Autentificare: `AUTH_IMPLEMENTATION.md`
   - Metodologie: `SPEC_DRIVEN_DEVELOPMENT.md`

5. **Testare și Validare**
   - Vezi `FIXES_SUMMARY.md`

6. **Concluzii**
   - Rezultate obținute
   - Dezvoltări viitoare

## 📐 Formatare pentru A4

Toate diagramele simplificate (`*-simple.puml`) sunt optimizate pentru A4 portrait.

Pentru imprimare de calitate:
- Exportă PlantUML ca **PDF** (nu PNG)
- Folosește versiunile simplificate
- Verifică preview-ul înainte de imprimare

## 📚 Documentație Completă

Pentru instrucțiuni detaliate, consultă:
- `DIAGRAME_PLANTUML_README.md` - Ghid complet PlantUML
- `QUICK_START.md` - Ghid rapid
- `DIAGRAME_INDEX.md` - Index complet
- `plantuml_diagrams/README.md` - README pentru diagrame

## 🔗 Resurse Externe

### PlantUML
- [PlantUML Documentation](https://plantuml.com/)
- [PlantUML Online Editor](http://www.plantuml.com/plantuml/uml/)
- [Graphviz Download](https://graphviz.org/download/)

### Mermaid
- [Mermaid Documentation](https://mermaid.js.org/)
- [Mermaid Live Editor](https://mermaid.live/)

## ✅ Checklist pentru Licență

- [ ] Am citit `ARHITECTURA_SISTEM.md`
- [ ] Am generat diagramele PlantUML recomandate
- [ ] Am exportat diagramele ca PDF
- [ ] Am verificat că se încadrează pe A4
- [ ] Am testat imprimarea
- [ ] Am inclus diagramele în documentație
- [ ] Am adăugat caption-uri și referințe
- [ ] Am verificat consistența stilului

---

**Notă:** Toate fișierele sunt în format Markdown și pot fi vizualizate direct pe GitHub/GitLab sau convertite în PDF/Word pentru licență.

