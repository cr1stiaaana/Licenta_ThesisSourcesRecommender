# Index Diagrame - Hybrid Thesis Recommender

## 📊 Diagrame Mermaid (în documentație)

Locație: `theory_files/ARHITECTURA_SISTEM.md` și `theory_files/DIAGRAME_TEHNOLOGII.md`

### Arhitectura Sistem
1. **Diagrama Arhitecturală Generală** - Vedere de ansamblu cu toate straturile
2. **Arhitectura pe Straturi** - Layered architecture (7 straturi)
3. **Arhitectura Componentelor** - Componente detaliate
4. **Fluxul de Date** - Secvența unei cereri de recomandare
5. **Fluxul Feedback-ului** - Procesul de rating
6. **Schema Bazei de Date** - ER diagram
7. **Arhitectura de Deployment** - Deployment actual și planificat
8. **Arhitectura de Securitate** - Layere de securitate
9. **Arhitectura de Scalabilitate** - Scaling strategy
10. **Arhitectura de Configurare** - Config management
11. **Metrici și Monitorizare** - Monitoring architecture

### Tehnologii
1. **Stack Tehnologic** - Vedere de ansamblu
2. **Flux de Date Request/Response** - Pipeline complet
3. **Arhitectura Modulară** - Structura directoarelor
4. **Pipeline de Procesare Query** - Query processing
5. **Spec-Driven Development Workflow** - Metodologie
6. **Tehnologii ML/AI Pipeline** - ML workflow
7. **Deployment Architecture** - Deployment planificat
8. **Metrici de Performanță** - Performance metrics

---

## 🎨 Diagrame PlantUML (fișiere separate)

Locație: `theory_files/plantuml_diagrams/*.puml`

### Versiuni Simplificate (✅ Recomandate pentru A4)

| Fișier | Descriere | Format Recomandat | Pagini |
|--------|-----------|-------------------|--------|
| `class-diagram-simple.puml` | Clasele principale și relațiile | A4 Portrait | 1 |
| `sequence-diagram-simple.puml` | Fluxul de recomandare simplificat | A4 Portrait | 1 |
| `deployment-diagram-simple.puml` | Arhitectura de deployment | A4 Portrait | 1 |
| `activity-diagram-simple.puml` | Pipeline ingestion simplificat | A4 Portrait | 1 |
| `state-diagram-simple.puml` | State machine simplificat | A4 Portrait | 1 |

### Versiuni Complete (Detaliate)

| Fișier | Descriere | Format Recomandat | Pagini |
|--------|-----------|-------------------|--------|
| `component-diagram.puml` | Arhitectura componentelor (optimizat) | A4 Portrait | 1 |
| `class-diagram.puml` | Toate clasele și metodele | A4 Landscape / A3 | 1-2 |
| `sequence-diagram-recommend.puml` | Fluxul complet de recomandare | A4 Landscape | 1-2 |
| `sequence-diagram-feedback.puml` | Fluxul de feedback detaliat | A4 Portrait | 1 |
| `deployment-diagram.puml` | Deployment cu toate detaliile | A4 Landscape | 1 |
| `activity-diagram-ingestion.puml` | Pipeline ingestion complet | A4 Portrait | 1 |
| `state-diagram-query.puml` | State machine detaliat | A4 Landscape | 1-2 |

---

## 📋 Recomandări pentru Lucrarea de Licență

### Set Minim (5 diagrame)

Pentru o prezentare completă dar concisă:

1. **Arhitectura Generală** 
   - Mermaid: "Diagrama Arhitecturală Generală" din `ARHITECTURA_SISTEM.md`
   - SAU PlantUML: `component-diagram.puml`

2. **Fluxul Principal**
   - PlantUML: `sequence-diagram-simple.puml`

3. **Modelul de Date**
   - PlantUML: `class-diagram-simple.puml`

4. **Deployment**
   - PlantUML: `deployment-diagram-simple.puml`

5. **Baza de Date**
   - Mermaid: "Schema Bazei de Date" din `ARHITECTURA_SISTEM.md`

### Set Complet (10 diagrame)

Pentru o documentație exhaustivă:

1. **Arhitectura Generală** - `component-diagram.puml`
2. **Arhitectura pe Straturi** - Mermaid din `ARHITECTURA_SISTEM.md`
3. **Fluxul de Recomandare** - `sequence-diagram-simple.puml`
4. **Fluxul de Feedback** - `sequence-diagram-feedback.puml`
5. **Modelul de Date** - `class-diagram-simple.puml`
6. **Schema Bazei de Date** - Mermaid din `ARHITECTURA_SISTEM.md`
7. **Deployment** - `deployment-diagram-simple.puml`
8. **Pipeline Ingestion** - `activity-diagram-simple.puml`
9. **State Machine** - `state-diagram-simple.puml`
10. **Stack Tehnologic** - Mermaid din `DIAGRAME_TEHNOLOGII.md`

---

## 🛠️ Cum să Generezi Diagramele

### Mermaid (din documentație)

**Opțiunea 1: Copy-Paste în Mermaid Live Editor**
1. Deschide [Mermaid Live Editor](https://mermaid.live/)
2. Copiază codul Mermaid din fișierele `.md`
3. Descarcă ca PNG/SVG

**Opțiunea 2: VS Code cu Mermaid Preview**
1. Instalează extensia "Markdown Preview Mermaid Support"
2. Deschide fișierul `.md`
3. Preview Markdown (Ctrl+Shift+V)
4. Click dreapta pe diagramă → Save as PNG

**Opțiunea 3: Mermaid CLI**
```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i diagram.mmd -o diagram.png
```

### PlantUML

**Opțiunea 1: Online (Fără Instalare)**
1. Deschide [PlantUML Online](http://www.plantuml.com/plantuml/uml/)
2. Copiază conținutul fișierului `.puml`
3. Descarcă ca PNG/SVG/PDF

**Opțiunea 2: VS Code**
1. Instalează extensia "PlantUML" de jebbs
2. Instalează Graphviz: `choco install graphviz` (Windows) sau `brew install graphviz` (Mac)
3. Deschide fișierul `.puml`
4. Alt+D pentru preview
5. Click dreapta → Export Current Diagram

**Opțiunea 3: Command Line**
```bash
# Instalează PlantUML
choco install plantuml  # Windows
brew install plantuml   # Mac

# Generează toate diagramele simplificate ca PDF
plantuml -tpdf theory_files/*-simple.puml

# Generează toate ca PNG
plantuml theory_files/*.puml

# Generează toate ca SVG (scalabil)
plantuml -tsvg theory_files/*.puml
```

---

## 📐 Setări de Imprimare

### Pentru A4 Portrait (21cm x 29.7cm)
- Folosește versiunile simplificate (`*-simple.puml`)
- Export ca PDF pentru cea mai bună calitate
- DPI recomandat pentru PNG: 300

### Pentru A4 Landscape (29.7cm x 21cm)
- Folosește versiunile complete pentru diagrame complexe
- `sequence-diagram-recommend.puml`
- `deployment-diagram.puml`
- `state-diagram-query.puml`

### Pentru A3 (29.7cm x 42cm)
- `class-diagram.puml` (versiunea completă)

---

## 🎯 Comparație Mermaid vs PlantUML

| Aspect | Mermaid | PlantUML |
|--------|---------|----------|
| **Instalare** | Nu necesită (online) | Necesită Java + Graphviz |
| **Sintaxă** | Mai simplă | Mai complexă |
| **Flexibilitate** | Limitată | Foarte flexibilă |
| **Calitate Export** | Bună (PNG/SVG) | Excelentă (PNG/SVG/PDF) |
| **Integrare Markdown** | Nativă (GitHub, GitLab) | Necesită plugin |
| **Tipuri Diagrame** | 10+ tipuri | 20+ tipuri |
| **Personalizare** | Limitată | Extinsă |
| **Recomandare** | Pentru documentație online | Pentru imprimare/licență |

---

## 💡 Tips & Tricks

### Pentru Imprimare de Calitate
1. Exportă PlantUML ca PDF (nu PNG)
2. Folosește versiunile simplificate pentru A4
3. Verifică preview-ul înainte de imprimare

### Pentru Documentație Online
1. Folosește Mermaid în fișierele Markdown
2. GitHub/GitLab le vor randa automat
3. Pentru prezentări, exportă ca SVG

### Pentru Prezentări PowerPoint
1. Exportă ca SVG pentru scalare fără pierdere
2. Sau exportă ca PNG cu DPI 300
3. Inserează în slide-uri

### Pentru LaTeX
```latex
% Pentru PDF
\includegraphics[width=\textwidth]{theory_files/plantuml_diagrams/component-diagram.pdf}

% Pentru SVG (necesită svg package)
\usepackage{svg}
\includesvg[width=\textwidth]{theory_files/plantuml_diagrams/component-diagram}
```

---

## 📚 Resurse Utile

### Mermaid
- [Mermaid Documentation](https://mermaid.js.org/)
- [Mermaid Live Editor](https://mermaid.live/)
- [Mermaid Cheat Sheet](https://jojozhuang.github.io/tutorial/mermaid-cheat-sheet/)

### PlantUML
- [PlantUML Documentation](https://plantuml.com/)
- [PlantUML Online Editor](http://www.plantuml.com/plantuml/uml/)
- [PlantUML Cheat Sheet](https://ogom.github.io/draw_uml/plantuml/)
- [Real World PlantUML](https://real-world-plantuml.com/)

### Graphviz (necesar pentru PlantUML)
- [Graphviz Download](https://graphviz.org/download/)
- [Graphviz Documentation](https://graphviz.org/documentation/)

---

## ✅ Checklist pentru Licență

- [ ] Generează toate diagramele simplificate ca PDF
- [ ] Verifică că toate diagramele se încadrează pe A4
- [ ] Exportă schema bazei de date din Mermaid
- [ ] Exportă stack tehnologic din Mermaid
- [ ] Testează imprimarea pe hârtie
- [ ] Verifică lizibilitatea textului
- [ ] Numerotează figurile în documentație
- [ ] Adaugă caption-uri descriptive
- [ ] Referențiază diagramele în text
- [ ] Verifică consistența stilului

