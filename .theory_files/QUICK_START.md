# Quick Start - Generare Diagrame PlantUML

**Locație diagrame:** `theory_files/plantuml_diagrams/`

## 🚀 Metoda Rapidă (Fără Instalare)

### Online - PlantUML Web Server

1. Deschide [PlantUML Online Editor](http://www.plantuml.com/plantuml/uml/)
2. Deschide unul din fișierele `.puml` din acest director
3. Copiază tot conținutul (Ctrl+A, Ctrl+C)
4. Lipește în editor-ul online (Ctrl+V)
5. Descarcă diagrama:
   - Click pe "PNG" pentru imagine
   - Click pe "SVG" pentru vector scalabil
   - Click pe "PDF" pentru imprimare

**Recomandare:** Începe cu versiunile simplificate (`*-simple.puml`)

---

## 💻 Metoda cu Command Line

### Windows

1. **Instalează dependențele:**
   ```cmd
   choco install plantuml graphviz
   ```

2. **Generează diagramele:**
   ```cmd
   cd theory_files\plantuml_diagrams
   plantuml *.puml
   ```

3. **Pentru PDF (recomandat):**
   ```cmd
   plantuml -tpdf *-simple.puml
   ```

### Mac / Linux

1. **Instalează dependențele:**
   ```bash
   # Mac
   brew install plantuml graphviz
   
   # Linux
   sudo apt-get install plantuml graphviz
   ```

2. **Generează diagramele:**
   ```bash
   cd theory_files/plantuml_diagrams
   plantuml *.puml
   ```

3. **Pentru PDF (recomandat):**
   ```bash
   plantuml -tpdf *-simple.puml
   ```

---

## 🎨 Visual Studio Code (Recomandat)

### Setup Inițial

1. **Instalează extensia PlantUML:**
   - Deschide VS Code
   - Apasă Ctrl+Shift+X
   - Caută "PlantUML" (de jebbs)
   - Click "Install"

2. **Instalează Graphviz:**
   - Windows: `choco install graphviz`
   - Mac: `brew install graphviz`
   - Linux: `sudo apt-get install graphviz`

### Generare Diagrame

1. Deschide orice fișier `.puml` în VS Code
2. Apasă `Alt+D` pentru preview
3. Click dreapta în preview → "Export Current Diagram"
4. Alege formatul:
   - **PDF** - Pentru imprimare (recomandat)
   - **PNG** - Pentru documentație
   - **SVG** - Pentru scalare

---

## 📋 Diagrame Recomandate pentru Licență

### Set Minim (5 diagrame) - ~15 minute

Generează doar acestea pentru o prezentare completă:

1. **component-diagram.puml** → `component-diagram.pdf`
2. **sequence-diagram-simple.puml** → `sequence-diagram-simple.pdf`
3. **class-diagram-simple.puml** → `class-diagram-simple.pdf`
4. **deployment-diagram-simple.puml** → `deployment-diagram-simple.pdf`
5. Schema bazei de date din `ARHITECTURA_SISTEM.md` (Mermaid)

### Cum să Generezi Doar Acestea

**Online:**
```
1. Deschide http://www.plantuml.com/plantuml/uml/
2. Copiază conținutul din component-diagram.puml
3. Descarcă ca PDF
4. Repetă pentru celelalte 3 fișiere
```

**Command Line:**
```bash
cd theory_files/plantuml_diagrams
plantuml -tpdf component-diagram.puml
plantuml -tpdf sequence-diagram-simple.puml
plantuml -tpdf class-diagram-simple.puml
plantuml -tpdf deployment-diagram-simple.puml
```

---

## 🔧 Troubleshooting

### "plantuml: command not found"

**Windows:**
```cmd
choco install plantuml
```

**Mac:**
```bash
brew install plantuml
```

**Linux:**
```bash
sudo apt-get install plantuml
```

### "Graphviz not found"

**Windows:**
```cmd
choco install graphviz
```

**Mac:**
```bash
brew install graphviz
```

**Linux:**
```bash
sudo apt-get install graphviz
```

### Diagrama este prea mare pentru A4

- Folosește versiunea simplificată (`*-simple.puml`)
- Sau printează în landscape (orizontal)
- Sau reduce fontul în fișierul `.puml`:
  ```plantuml
  skinparam defaultFontSize 8
  ```

### Textul este prea mic

- Crește fontul în fișierul `.puml`:
  ```plantuml
  skinparam defaultFontSize 11
  ```
- Sau exportă ca SVG și scalează în Word/PowerPoint

---

## 📐 Setări de Imprimare

### Pentru A4 Portrait (Recomandat)

Toate diagramele `*-simple.puml` sunt optimizate pentru A4 portrait:
- `class-diagram-simple.puml` ✅
- `sequence-diagram-simple.puml` ✅
- `deployment-diagram-simple.puml` ✅
- `activity-diagram-simple.puml` ✅
- `state-diagram-simple.puml` ✅

### Pentru A4 Landscape

Diagramele complete mai complexe:
- `sequence-diagram-recommend.puml`
- `deployment-diagram.puml`
- `state-diagram-query.puml`

---

## 💡 Tips

### Calitate Maximă pentru Imprimare
```bash
# Generează ca PDF (cel mai bun pentru imprimare)
plantuml -tpdf diagram.puml

# Sau PNG cu DPI înalt
plantuml -DPLANTUML_LIMIT_SIZE=8192 diagram.puml
```

### Pentru Prezentări PowerPoint
```bash
# Generează ca SVG (scalabil fără pierdere)
plantuml -tsvg diagram.puml
```

### Pentru LaTeX
```bash
# Generează ca PDF
plantuml -tpdf diagram.puml

# Apoi în LaTeX:
# \includegraphics[width=\textwidth]{diagram.pdf}
```

---

## ⏱️ Timp Estimat

| Metodă | Timp Setup | Timp Generare | Total |
|--------|------------|---------------|-------|
| Online (fără instalare) | 0 min | 2 min/diagramă | ~10 min pentru 5 |
| Command line | 5 min | 1 min | ~6 min pentru toate |
| VS Code | 10 min | 30 sec/diagramă | ~13 min pentru toate |

---

## 📞 Ajutor

Dacă întâmpini probleme:

1. Verifică că ai instalat Graphviz: `dot -V`
2. Verifică că ai instalat PlantUML: `plantuml -version`
3. Încearcă metoda online (nu necesită instalare)
4. Consultă `DIAGRAME_PLANTUML_README.md` pentru detalii complete

---

## ✅ Checklist

- [ ] Am instalat PlantUML și Graphviz (sau folosesc online)
- [ ] Am generat cele 5 diagrame recomandate
- [ ] Am verificat că se încadrează pe A4
- [ ] Am exportat ca PDF pentru imprimare
- [ ] Am testat imprimarea pe hârtie
- [ ] Textul este lizibil la dimensiunea A4

**Gata! Diagramele sunt pregătite pentru licență! 🎉**

