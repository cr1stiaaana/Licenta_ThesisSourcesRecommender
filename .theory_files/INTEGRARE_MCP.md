# Integrarea MCP în Studiul de Caz

Pe baza mecanismelor descrise anterior, în cadrul dezvoltării sistemului de recomandare au fost configurate două servere MCP care au facilitat procesul de debugging, inspecție a datelor și acces la documentație externă. Această secțiune prezintă configurarea concretă, utilizarea practică și concluziile rezultate din integrarea protocolului în fluxul de lucru al proiectului.

## Configurarea Serverelor

Serverele MCP sunt definite în fișierul `.kiro/settings/mcp.json`, care specifică modul de pornire, parametrii de conectare și politica de aprobare pentru fiecare server:

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

**De ce `uvx` ca executor:** `uvx` este echivalentul `npx` din ecosistemul Node.js, dar pentru Python. Descarcă și rulează un pachet Python fără a-l instala permanent pe sistem. La prima utilizare, descarcă serverul MCP din registrul PyPI; la utilizările ulterioare, îl execută direct din cache. Această abordare elimină necesitatea instalării manuale a serverelor MCP și evită conflictele cu dependențele proiectului.

**Politica de auto-aprobare selectivă:** Fiecare server declară o listă de tool-uri (`autoApprove`) care pot fi executate fără confirmare din partea utilizatorului. Principiul aplicat este separarea între operații de citire (sigure) și operații de scriere (potențial distructive):

| Categorie | Tool-uri | Auto-aprobat | Motivație |
|-----------|----------|:------------:|-----------|
| Citire date | `read_query`, `list_tables`, `describe_table` | ✅ Da | Nu pot modifica sau corupe baza de date |
| Scriere date | `write_query`, `create_table` | ❌ Nu | Pot altera ireversibil conținutul bazei de date |
| Acces web | `fetch` | ✅ Da | Operație read-only, fără efecte secundare |

Acest model asigură un echilibru între eficiență (nu se cere confirmare pentru fiecare SELECT) și siguranță (o operație DELETE necesită întotdeauna aprobarea explicită a dezvoltatorului).

## Serverul SQLite

**Scopul:** Accesul direct la baza de date `articles.db` din cadrul conversației cu asistentul AI, fără a scrie și rula scripturi Python intermediare.

Serverul expune operațiile SQL standard prin intermediul a cinci tool-uri:

| Tool | Operație | Descriere |
|------|----------|-----------|
| `read_query` | SELECT | Execută o interogare de citire și returnează rezultatele ca JSON |
| `write_query` | INSERT, UPDATE, DELETE | Execută o operație de modificare a datelor |
| `list_tables` | Metadata | Listează toate tabelele existente în baza de date |
| `describe_table` | Metadata | Returnează schema unei tabele (coloane, tipuri de date, constrângeri) |
| `create_table` | DDL | Creează o tabelă nouă conform unei instrucțiuni SQL |

**Exemple concrete de utilizare în timpul dezvoltării:**

*Verificarea ingestiei:* După rularea scripturilor de populare a corpusului (`populate_article_store.py`), serverul SQLite a fost folosit pentru a confirma că articolele au fost inserate corect — verificarea numărului total (`SELECT COUNT(*) FROM articles`), prezența câmpurilor obligatorii (titlu, autori, DOI), și absența duplicatelor.

*Debugging retrieval:* Când rezultatele căutării semantice nu corespundeau așteptărilor, serverul a permis inspectarea directă a metadatelor articolelor din baza de date pentru a identifica dacă problema era în date (articolul lipsea sau avea metadata incompletă) sau în algoritmul de retrieval.

*Analiza feedback-ului:* Interogarea tabelei de rating-uri pentru a verifica funcționarea corectă a operațiilor upsert — confirmarea că un al doilea rating de la același utilizator actualizează înregistrarea existentă în loc să creeze un duplicat.

*Generarea statisticilor:* Extragerea de informații agregate (distribuția articolelor pe ani, limbi, număr de rating-uri) pentru includerea în documentația proiectului.

## Serverul Fetch

**Scopul:** Accesul la conținut web (documentație, API-uri, pagini de referință) direct din conversație, fără a deschide un browser separat și a pierde contextul de lucru.

Serverul expune un singur tool (`fetch`) care descarcă conținutul unui URL și îl returnează ca text procesabil de asistentul AI.

**Exemple concrete de utilizare în timpul dezvoltării:**

*Consultarea documentației:* Accesarea paginilor de documentație ale bibliotecilor utilizate (sentence-transformers, FAISS, schemathesis, Flask) pentru a verifica semnăturile funcțiilor, parametrii disponibili, și exemplele de utilizare — fără a întrerupe fluxul de lucru.

*Verificarea versiunilor:* Consultarea registrului PyPI pentru a confirma versiunile cele mai recente ale dependențelor și compatibilitatea dintre ele.

*Cercetarea soluțiilor:* Accesarea răspunsurilor relevante de pe GitHub Issues sau documentație oficială pentru rezolvarea erorilor specifice întâmpinate în timpul dezvoltării (ex: configurarea corectă a FAISS IndexFlatIP, parametrii schemathesis).

## Beneficii Observate în Practică

**Flux de lucru neîntrerupt:** Fără MCP, inspectarea bazei de date presupunea: deschiderea terminalului → scrierea unui script Python → rularea → copierea rezultatului → revenirea la conversație. Cu MCP, întregul proces se reduce la o singură întrebare în conversație, iar rezultatul este disponibil imediat în context.

**Interpretare automată a rezultatelor:** Asistentul AI nu returnează doar datele brute ale interogării, ci le interpretează și răspunde la întrebarea reală a dezvoltatorului. De exemplu, la întrebarea „de ce nu apare articolul X în rezultate?", asistentul execută SELECT-ul, analizează rezultatul, și poate identifica singur cauza (ex: articolul lipsește din baza de date, sau are un câmp NULL care îl exclude din index).

**Auditabilitate:** Fiecare apel MCP este vizibil în istoricul conversației — se poate vedea exact ce query SQL a fost executat, ce parametri s-au folosit, și ce rezultat a fost returnat. Aceasta oferă transparență completă asupra operațiilor efectuate și facilitează reproducerea pașilor în cazul unui debugging complex.

**Reducerea erorilor:** Tool-urile MCP sunt standardizate și testate. Spre deosebire de scripturile ad-hoc scrise rapid pentru o singură utilizare, care pot conține erori de sintaxă sau logică, apelurile MCP execută operații bine definite cu gestionare corectă a erorilor.

## Limitări Identificate

**Lipsa unui server MCP pentru FAISS:** Nu există un server MCP standardizat pentru interogarea indexului vectorial FAISS. Aceasta înseamnă că inspectarea directă a vectorilor (vizualizarea embedding-urilor, verificarea similaritatii cosinus între doi vectori) necesită în continuare scripturi Python dedicate. Serverul SQLite acoperă doar metadatele articolelor, nu și reprezentările lor vectoriale.

**Dependența de `uvx`:** Funcționarea serverelor MCP necesită instalarea prealabilă a tool-ului `uv` (managerul de pachete Python). Pe o mașină nouă, aceasta reprezintă un pas suplimentar de configurare. Totuși, instalarea este unică și nu afectează funcționarea aplicației în sine.

**Fără persistență între sesiuni:** Serverele MCP nu mențin un istoric al interogărilor sau al rezultatelor anterioare. La începerea unei noi sesiuni de lucru, contextul descoperit anterior (ex: „articolul Y are DOI-ul Z") nu este disponibil automat — trebuie fie re-interogat, fie documentat explicit în steering files.

**Latență minimă:** Fiecare apel MCP adaugă aproximativ 100-500ms (pornirea procesului server + executarea operației + serializarea rezultatului). Pentru interogări simple aceasta este neglijabilă, dar pentru secvențe lungi de interogări succesive devine perceptibilă. În practică, serverul rămâne activ între apeluri, reducând latența la apelurile ulterioare.
